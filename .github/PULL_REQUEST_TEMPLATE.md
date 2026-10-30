## Summary

This project adds a validated OpenAPI-to-Markdown synchronization tool and a read-only GitHub Actions check. It keeps `docs/api.md` aligned with OpenAPI 3.0.x/3.1.x contracts and catches stale output before merge.

## Changes Made

- `requirements.md` — agreed user story, functional and non-functional requirements, and acceptance criteria.
- `architecture.md`, `design-review.md`, `impl-plan.md` — approved component design, review decisions, and dependency-ordered delivery plan.
- `scripts/sync_openapi_docs.py` — parsing, validation, deterministic Markdown rendering, safe errors, check mode, and atomic writes.
- `requirements.txt` — YAML, OpenAPI validation, and local-reference dependencies.
- `openapi.yaml`, `docs/api.md` — demonstration contract and its generated reference.
- `tests/test_sync_openapi_docs.py` — generation, JSON/YAML, invalid input, stale output, missing input, reference, and error-output coverage.
- `.github/workflows/openapi-docs.yml` — pull request tests, dependency audit, and documentation consistency check with read-only permissions.
- `README.md`, `CHANGELOG.md`, `.gitignore` — setup and usage, release notes, and local Python artifact exclusions.
- `.github/copilot-instructions.md`, `.github/agents/openapi-doc-reviewer.agent.md`, `.github/prompts/sync-openapi-docs.prompt.md`, `.github/skills/openapi-doc-sync/SKILL.md` — team-shared Copilot guidance and repeatable workflows.
- `.github/PULL_REQUEST_TEMPLATE.md` — this summary, evidence, limitations, and reviewer checklist.

## Test Evidence

- `python -m unittest discover -s tests -v` — 11 tests passed.
- `python scripts/sync_openapi_docs.py --check` — generated documentation is up to date.
- `python -m pip_audit -r requirements.txt` — no known vulnerabilities found.

## Known Limitations

- This delivery is a local repository; it has not been published to GitHub and no remote pull request has been opened.
- CI detects stale documentation but does not commit generated files; contributors must regenerate and commit `docs/api.md`.
- External `$ref` targets are rejected; use local references.

## Reviewer Checklist

- [ ] Confirm requirements and acceptance criteria match the intended synchronization behavior.
- [ ] Confirm supported OpenAPI versions, parsing, and validation errors are correct and actionable.
- [ ] Confirm generated output covers paths, methods, parameters, request bodies, schemas, and response codes.
- [ ] Confirm malformed or missing input cannot modify existing documentation.
- [ ] Confirm tests, documentation check, and dependency audit pass.
- [ ] Confirm workflow permissions remain read-only and no secrets are exposed.
