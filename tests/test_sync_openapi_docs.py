import json
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

from scripts.sync_openapi_docs import SyncError, discover_spec, load_and_validate, main, synchronize


VALID_SPEC = """\
openapi: 3.0.3
info:
  title: Sample Service
  version: 1.0.0
paths:
  /items/{itemId}:
    get:
      operationId: getItem
      summary: Get an item
      parameters:
        - name: itemId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: The requested item
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
  /items:
    post:
      summary: Create an item
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - name
              properties:
                name:
                  type: string
      responses:
        '201':
          description: The item was created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Item'
components:
  schemas:
    Item:
      type: object
      required:
        - id
      properties:
        id:
          type: string
"""


class SyncOpenApiDocsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.spec_path = self.root / "openapi.yaml"
        self.output_path = self.root / "docs" / "api.md"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_generates_reference_with_operations_parameters_and_responses(self) -> None:
        self.spec_path.write_text(VALID_SPEC, encoding="utf-8")

        message = synchronize(self.root, None, "docs/api.md", check=False)
        generated = self.output_path.read_text(encoding="utf-8")

        self.assertIn("Generated documentation:", message)
        self.assertIn("## `GET /items/{itemId}`", generated)
        self.assertIn("| itemId | path | Yes |", generated)
        self.assertIn("**200** — The requested item", generated)
        self.assertIn('"type": "object"', generated)
        self.assertIn("## `POST /items`", generated)
        self.assertIn("### Request body", generated)
        self.assertIn("**Required:** Yes", generated)
        self.assertIn("**application/json**", generated)
        self.assertIn("**201** — The item was created", generated)
        self.assertIn("#/components/schemas/Item", generated)
        self.assertIn("## Schemas", generated)

    def test_check_mode_detects_stale_docs_without_modifying_them(self) -> None:
        self.spec_path.write_text(VALID_SPEC, encoding="utf-8")
        self.output_path.parent.mkdir()
        self.output_path.write_text("stale reference\n", encoding="utf-8")

        with self.assertRaisesRegex(SyncError, "is stale"):
            synchronize(self.root, None, "docs/api.md", check=True)

        self.assertEqual(self.output_path.read_text(encoding="utf-8"), "stale reference\n")

    def test_check_mode_detects_missing_docs_without_creating_them(self) -> None:
        self.spec_path.write_text(VALID_SPEC, encoding="utf-8")

        with self.assertRaisesRegex(SyncError, "is missing"):
            synchronize(self.root, None, "docs/api.md", check=True)

        self.assertFalse(self.output_path.exists())

    def test_output_cannot_overwrite_the_specification(self) -> None:
        self.spec_path.write_text(VALID_SPEC, encoding="utf-8")

        with self.assertRaisesRegex(SyncError, "must not overwrite"):
            synchronize(self.root, None, "openapi.yaml", check=False)

        self.assertEqual(self.spec_path.read_text(encoding="utf-8"), VALID_SPEC)

    def test_invalid_specs_do_not_modify_existing_documentation(self) -> None:
        invalid_specs = (
            "",
            "openapi: [",
            "openapi: 2.0.0\ninfo: {}\npaths: {}\n",
            "openapi: 3.0.3\ninfo: {}\npaths: {}\n",
            VALID_SPEC.replace("'200':", "200:"),
            VALID_SPEC.replace("    Item:", "    MissingItem:"),
            (
                "openapi: 3.0.3\ninfo:\n  title: Remote ref\n  version: 1.0.0\n"
                "paths:\n  /items:\n    get:\n      responses:\n        '200':\n"
                "          $ref: https://example.com/response.yaml\n"
            ),
        )
        self.output_path.parent.mkdir()
        self.output_path.write_text("keep this content\n", encoding="utf-8")

        for invalid_spec in invalid_specs:
            with self.subTest(invalid_spec=invalid_spec):
                self.spec_path.write_text(invalid_spec, encoding="utf-8")
                with self.assertRaises(SyncError):
                    synchronize(self.root, None, "docs/api.md", check=False)
                self.assertEqual(self.output_path.read_text(encoding="utf-8"), "keep this content\n")

    def test_external_references_are_rejected_without_fetching(self) -> None:
        self.spec_path.write_text(
            "openapi: 3.0.3\ninfo:\n  title: Remote ref\n  version: 1.0.0\n"
            "paths:\n  /items:\n    get:\n      responses:\n        '200':\n"
            "          $ref: https://example.com/response.yaml\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(SyncError, "External OpenAPI reference"):
            load_and_validate(self.spec_path)

    def test_json_spec_can_be_selected_explicitly(self) -> None:
        json_path = self.root / "contract.json"
        json_path.write_text(
            json.dumps(
                {
                    "openapi": "3.1.0",
                    "info": {"title": "JSON API", "version": "1.0.0"},
                    "paths": {"/health": {"get": {"responses": {"200": {"description": "Healthy"}}}}},
                }
            ),
            encoding="utf-8",
        )

        spec = load_and_validate(discover_spec(self.root, str(json_path)))
        message = synchronize(self.root, str(json_path), "docs/api.md", check=False)

        self.assertEqual(spec["info"]["title"], "JSON API")
        self.assertIn("Generated documentation:", message)
        self.assertIn("## `GET /health`", self.output_path.read_text(encoding="utf-8"))

    def test_malformed_json_does_not_modify_existing_documentation(self) -> None:
        json_path = self.root / "openapi.json"
        json_path.write_text('{"openapi": ', encoding="utf-8")
        self.output_path.parent.mkdir()
        self.output_path.write_text("keep this content\n", encoding="utf-8")

        with self.assertRaisesRegex(SyncError, "Cannot parse JSON specification"):
            synchronize(self.root, "openapi.json", "docs/api.md", check=False)

        self.assertEqual(self.output_path.read_text(encoding="utf-8"), "keep this content\n")

    def test_auto_discovery_fails_for_missing_or_ambiguous_spec(self) -> None:
        with self.assertRaisesRegex(SyncError, "No OpenAPI specification found"):
            discover_spec(self.root, None)

        self.spec_path.write_text(VALID_SPEC, encoding="utf-8")
        (self.root / "openapi.json").write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(SyncError, "Multiple OpenAPI specifications found"):
            discover_spec(self.root, None)

    def test_cli_returns_nonzero_for_missing_spec(self) -> None:
        with redirect_stderr(StringIO()):
            self.assertEqual(main(["--repo-root", str(self.root)]), 1)

    def test_validation_errors_do_not_echo_spec_values(self) -> None:
        secret_marker = "example-sensitive-value"
        self.spec_path.write_text(
            f"openapi: 3.0.3\ninfo:\n  version: 1.0.0\n  description: {secret_marker}\npaths: {{}}\n",
            encoding="utf-8",
        )
        error_output = StringIO()

        with redirect_stderr(error_output):
            self.assertEqual(main(["--repo-root", str(self.root)]), 1)

        self.assertNotIn(secret_marker, error_output.getvalue())


if __name__ == "__main__":
    unittest.main()
