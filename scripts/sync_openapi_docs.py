#!/usr/bin/env python3
"""Validate an OpenAPI document and generate its Markdown API reference."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml
from openapi_spec_validator import validate
from openapi_spec_validator.exceptions import OpenAPIError
from openapi_spec_validator.validation.exceptions import OpenAPIValidationError
from referencing.exceptions import Unresolvable


HTTP_METHODS = {
    "delete",
    "get",
    "head",
    "options",
    "patch",
    "post",
    "put",
    "trace",
}
SPEC_NAMES = ("openapi.yaml", "openapi.json")
OPENAPI_VERSION = re.compile(r"^3\.(?:0|1)\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


class SyncError(Exception):
    """An expected input, validation, or documentation consistency error."""


def discover_spec(root: Path, explicit_spec: str | None) -> Path:
    if explicit_spec is not None:
        path = Path(explicit_spec)
        if not path.is_absolute():
            path = root / path
        if path.suffix.lower() not in {".yaml", ".json"}:
            raise SyncError(f"Unsupported specification format: {path}. Use .yaml or .json.")
        if not path.is_file():
            raise SyncError(f"OpenAPI specification not found: {path}")
        return path

    candidates = [root / name for name in SPEC_NAMES if (root / name).is_file()]
    if not candidates:
        expected = " or ".join(SPEC_NAMES)
        raise SyncError(f"No OpenAPI specification found in {root}. Expected {expected}.")
    if len(candidates) > 1:
        names = ", ".join(str(path) for path in candidates)
        raise SyncError(f"Multiple OpenAPI specifications found: {names}. Pass --spec to choose one.")
    return candidates[0]


def reject_external_references(value: Any, spec_path: Path) -> None:
    if isinstance(value, dict):
        reference = value.get("$ref")
        if isinstance(reference, str) and not reference.startswith("#"):
            raise SyncError(
                f"External OpenAPI references in {spec_path} are not supported. "
                "Use local #/... references."
            )
        for nested_value in value.values():
            reject_external_references(nested_value, spec_path)
    elif isinstance(value, list):
        for nested_value in value:
            reject_external_references(nested_value, spec_path)


def validate_mapping_keys(value: Any, spec_path: Path) -> None:
    if isinstance(value, dict):
        for key, nested_value in value.items():
            if not isinstance(key, str):
                raise SyncError(
                    f"OpenAPI object keys must be strings in {spec_path}; "
                    "quote numeric YAML response codes, for example '200'."
                )
            validate_mapping_keys(nested_value, spec_path)
    elif isinstance(value, list):
        for nested_value in value:
            validate_mapping_keys(nested_value, spec_path)


def load_and_validate(spec_path: Path) -> dict[str, Any]:
    try:
        text = spec_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise SyncError(
            f"OpenAPI specification is not valid UTF-8: {spec_path} (byte offset {error.start})."
        ) from error
    except OSError as error:
        raise SyncError(f"Cannot read OpenAPI specification {spec_path}: {error}") from error

    if not text.strip():
        raise SyncError(f"OpenAPI specification is empty: {spec_path}")

    if spec_path.suffix.lower() == ".json":
        try:
            spec = json.loads(text)
        except json.JSONDecodeError as error:
            raise SyncError(
                f"Cannot parse JSON specification {spec_path} at line {error.lineno}, "
                f"column {error.colno}."
            ) from error
    else:
        try:
            spec = yaml.safe_load(text)
        except yaml.YAMLError as error:
            mark = getattr(error, "problem_mark", None)
            if mark is None:
                location = ""
            else:
                location = f" at line {mark.line + 1}, column {mark.column + 1}"
            raise SyncError(f"Cannot parse YAML specification {spec_path}{location}.") from error

    if not isinstance(spec, dict):
        raise SyncError(f"OpenAPI specification must contain a YAML or JSON object: {spec_path}")

    validate_mapping_keys(spec, spec_path)
    version = spec.get("openapi")
    if not isinstance(version, str) or not OPENAPI_VERSION.fullmatch(version):
        raise SyncError(
            f"Unsupported or missing OpenAPI version in {spec_path}. "
            "Supported versions are 3.0.x and 3.1.x."
        )

    reject_external_references(spec, spec_path)
    try:
        validate(spec)
    except OpenAPIValidationError as error:
        location = ".".join(str(part) for part in error.absolute_path) or "document root"
        rule = getattr(error, "validator", "structure")
        raise SyncError(
            f"OpenAPI validation failed for {spec_path} at {location} (rule: {rule}). "
            "Check required fields and value types."
        ) from error
    except Unresolvable as error:
        raise SyncError(
            f"OpenAPI validation failed for {spec_path}: a local $ref target could not be resolved."
        ) from error
    except OpenAPIError as error:
        raise SyncError(
            f"OpenAPI validation failed for {spec_path} ({type(error).__name__})."
        ) from error

    return spec


def markdown_text(value: Any) -> str:
    return str(value).replace("|", r"\|").replace("\r", " ").replace("\n", " ").strip()


def schema_block(schema: Any) -> str:
    if schema is None:
        return "_No schema specified._"
    rendered = json.dumps(schema, indent=2, ensure_ascii=False, sort_keys=True)
    longest_backtick_run = max((len(run) for run in re.findall(r"`+", rendered)), default=0)
    fence = "`" * max(3, longest_backtick_run + 1)
    return f"{fence}json\n{rendered}\n{fence}"


def render_parameters(parameters: Any) -> list[str]:
    if not parameters:
        return ["_No parameters._"]

    lines = [
        "| Name | In | Required | Schema |",
        "|---|---|---:|---|",
    ]
    for parameter in parameters:
        if not isinstance(parameter, dict):
            lines.append(f"| Reference | — | — | `{markdown_text(parameter)}` |")
            continue
        if "$ref" in parameter:
            lines.append(f"| Reference | — | — | `{markdown_text(parameter['$ref'])}` |")
            continue
        schema = parameter.get("schema")
        schema_text = json.dumps(schema, ensure_ascii=False, sort_keys=True) if schema is not None else "—"
        lines.append(
            "| "
            + " | ".join(
                (
                    markdown_text(parameter.get("name", "—")),
                    markdown_text(parameter.get("in", "—")),
                    "Yes" if parameter.get("required", False) else "No",
                    f"`{markdown_text(schema_text)}`",
                )
            )
            + " |"
        )
    return lines


def render_request_body(request_body: Any) -> list[str]:
    if not isinstance(request_body, dict):
        return ["_No request body._"]
    if "$ref" in request_body:
        return [f"Reference: `{markdown_text(request_body['$ref'])}`"]

    lines = [f"**Required:** {'Yes' if request_body.get('required', False) else 'No'}", ""]
    if request_body.get("description"):
        lines.append(markdown_text(request_body["description"]))
    content = request_body.get("content", {})
    if not isinstance(content, dict) or not content:
        lines.append("_No request schema specified._")
        return lines
    for media_type, details in sorted(content.items()):
        schema = details.get("schema") if isinstance(details, dict) else None
        lines.extend((f"**{markdown_text(media_type)}**", schema_block(schema), ""))
    return lines


def render_responses(responses: Any) -> list[str]:
    if not isinstance(responses, dict) or not responses:
        return ["_No responses specified._"]

    lines: list[str] = []
    for status, response in sorted(responses.items(), key=lambda item: str(item[0])):
        if isinstance(response, dict) and "$ref" in response:
            lines.append(f"**{markdown_text(status)}** — Reference: `{markdown_text(response['$ref'])}`")
            lines.append("")
            continue
        lines.append(f"**{markdown_text(status)}** — {markdown_text(response.get('description', ''))}")
        content = response.get("content", {}) if isinstance(response, dict) else {}
        if not isinstance(content, dict) or not content:
            lines.append("")
            continue
        for media_type, details in sorted(content.items()):
            schema = details.get("schema") if isinstance(details, dict) else None
            lines.extend((f"- `{markdown_text(media_type)}` response schema:", schema_block(schema), ""))
    return lines


def render_spec(spec: dict[str, Any]) -> str:
    info = spec.get("info", {})
    title = markdown_text(info.get("title", "API Reference"))
    version = markdown_text(info.get("version", ""))
    lines = [f"# {title}", ""]
    if version:
        lines.extend((f"**API version:** {version}", ""))
    if info.get("description"):
        lines.extend((markdown_text(info["description"]), ""))
    lines.extend(("<!-- Generated by scripts/sync_openapi_docs.py; do not edit by hand. -->", ""))

    paths = spec.get("paths", {})
    for path, path_item in sorted(paths.items()):
        if not isinstance(path_item, dict):
            continue
        path_parameters = path_item.get("parameters", [])
        for method, operation in sorted(path_item.items()):
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            parameters = [*path_parameters, *operation.get("parameters", [])]
            lines.extend((f"## `{method.upper()} {path}`", ""))
            if operation.get("summary"):
                lines.extend((markdown_text(operation["summary"]), ""))
            if operation.get("description"):
                lines.extend((markdown_text(operation["description"]), ""))
            if operation.get("operationId"):
                lines.extend((f"**Operation ID:** `{markdown_text(operation['operationId'])}`", ""))
            lines.extend(("### Parameters", "", *render_parameters(parameters), ""))
            lines.extend(("### Request body", "", *render_request_body(operation.get("requestBody")), ""))
            lines.extend(("### Responses", "", *render_responses(operation.get("responses")), ""))

    components = spec.get("components", {})
    component_sections = (
        ("schemas", "Schemas"),
        ("parameters", "Parameters"),
        ("requestBodies", "Request bodies"),
        ("responses", "Responses"),
    )
    for component_key, heading in component_sections:
        component_values = components.get(component_key, {})
        if component_values:
            lines.extend((f"## {heading}", ""))
            for name, component in sorted(component_values.items()):
                lines.extend((f"### `{markdown_text(name)}`", "", schema_block(component), ""))

    return "\n".join(lines).rstrip() + "\n"


def write_atomically(output_path: Path, content: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            temporary_file.write(content)
        os.replace(temporary_path, output_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def synchronize(root: Path, spec_arg: str | None, output_arg: str, check: bool) -> str:
    spec_path = discover_spec(root, spec_arg)
    spec = load_and_validate(spec_path)
    content = render_spec(spec)
    output_path = Path(output_arg)
    if not output_path.is_absolute():
        output_path = root / output_path
    if output_path.resolve() == spec_path.resolve():
        raise SyncError("Generated documentation path must not overwrite the OpenAPI specification.")

    if check:
        try:
            existing = output_path.read_text(encoding="utf-8")
        except FileNotFoundError as error:
            raise SyncError(
                f"Generated documentation is missing: {output_path}. "
                "Run python scripts/sync_openapi_docs.py and commit the result."
            ) from error
        except OSError as error:
            raise SyncError(f"Cannot read generated documentation {output_path}: {error}") from error
        if existing != content:
            raise SyncError(
                f"Generated documentation is stale: {output_path}. "
                "Run python scripts/sync_openapi_docs.py and commit the result."
            )
        return f"Documentation is up to date: {output_path}"

    try:
        write_atomically(output_path, content)
    except OSError as error:
        raise SyncError(f"Cannot write generated documentation {output_path}: {error}") from error
    return f"Generated documentation: {output_path}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate an OpenAPI 3.0/3.1 specification and synchronize its Markdown reference."
    )
    parser.add_argument("--spec", help="Path to openapi.yaml or openapi.json (auto-discovered by default).")
    parser.add_argument("--output", default="docs/api.md", help="Generated Markdown path (default: docs/api.md).")
    parser.add_argument("--check", action="store_true", help="Check for stale documentation without writing.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help=argparse.SUPPRESS,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        print(synchronize(args.repo_root.resolve(), args.spec, args.output, args.check))
    except SyncError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
