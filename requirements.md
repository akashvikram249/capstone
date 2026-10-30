# Requirements

## User story

**US-101: Automatically Synchronize API Documentation with OpenAPI Specifications**

As a backend developer, I want API documentation to be automatically generated or updated whenever the OpenAPI specification changes in a GitHub repository, so that API documentation remains accurate, consistent with the implementation contract, and up to date without requiring manual editing.

The business problem is that API endpoints, request fields, response schemas, and error codes are often changed without corresponding documentation updates. This creates stale API references, integration failures, and additional QA effort.

## Scope and decisions

- The deliverable is a local, standalone repository containing a reusable documentation generator and GitHub Actions verification workflow.
- The repository includes a small sample OpenAPI specification to demonstrate the feature.
- Generated documentation is `docs/api.md`.
- The generator updates documentation when run normally. Pull request CI runs it in check mode and fails if the checked-in documentation is stale; CI does not push commits.
- Root-level `openapi.yaml` and `openapi.json` are supported. If both are present without an explicit input, the generator reports an ambiguity.

## Functional requirements

### FR-1: Detect OpenAPI changes

When a pull request adds or modifies root-level `openapi.yaml` or `openapi.json`, the GitHub Actions workflow runs documentation validation and consistency checks.

### FR-2: Validate before generation

The generator parses YAML or JSON, accepts supported OpenAPI 3.0.x and 3.1.x specifications, and validates the required OpenAPI structure before rendering output. Unsupported versions, invalid syntax, invalid structure, empty files, and missing or ambiguous inputs produce actionable errors and a non-zero exit status.

### FR-3: Generate API reference

For a valid specification, the generator creates or updates `docs/api.md` with endpoint paths and HTTP methods, operation descriptions, parameters, request bodies, response status codes, and response schemas.

### FR-4: Preserve output on failure

If the specification is missing, empty, malformed, unsupported, or structurally invalid, generation fails without modifying existing documentation.

### FR-5: Verify changes in CI

For relevant pull requests, GitHub Actions runs automated tests, validates the specification, checks that generated documentation matches the committed output, and reports success or failure through the workflow check. Any required check failure fails the workflow.

### FR-6: Local synchronization

A documented local command generates or updates `docs/api.md`. A check mode verifies the output without changing files and returns a non-zero status when the document is stale.

## Non-functional requirements

- Generation is deterministic: the same valid input produces byte-for-byte identical Markdown.
- The tool makes no network requests and does not print secrets.
- Invalid input is reported explicitly; errors are not converted into successful or empty output.
- Output replacement is atomic after validation and rendering succeed.
- The implementation and tests run on Python 3.11 or newer.
- The GitHub Actions workflow uses read-only repository permissions.

## Acceptance criteria

- **AC-01 — Detect OpenAPI changes:** A pull request adding or modifying `openapi.yaml` or `openapi.json` triggers the documentation workflow.
- **AC-02 — Validate the specification:** Syntax, supported OpenAPI version, and required structure are validated before generation. Invalid input reports a useful error.
- **AC-03 — Generate and synchronize documentation:** Valid input generates or updates `docs/api.md` with paths, methods, parameters, request bodies, response schemas, and status codes.
- **AC-04 — Handle errors safely:** Missing, empty, malformed, unsupported, or invalid specifications fail with an actionable message and non-zero status without changing existing documentation.
- **AC-05 — Automate verification:** Pull request CI runs validation, automated tests, and documentation consistency checks, and fails when any required check fails.

## Out of scope

- Committing or pushing generated documentation from CI.
- Publishing or hosting the generated API reference.
- Fetching external `$ref` documents or resolving network URLs.
- Supporting OpenAPI 2.0 or formats other than YAML and JSON.
