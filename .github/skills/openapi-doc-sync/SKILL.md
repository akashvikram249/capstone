---
name: openapi-doc-sync
description: "Synchronize and verify generated API documentation after OpenAPI spec changes. Use when editing openapi.yaml/openapi.json, refreshing docs/api.md, or debugging a stale-documentation check."
argument-hint: "OpenAPI file to synchronize (optional)"
---

# OpenAPI Documentation Synchronization

Use this workflow when an OpenAPI contract changes or the API reference check fails.

1. Read [requirements.md](../../../requirements.md), especially the acceptance criteria.
2. Review the contract changes and confirm the file is OpenAPI 3.0.x or 3.1.x.
3. Generate the reference with `python scripts/sync_openapi_docs.py`. If the repository contains both root-level supported inputs, pass the intended file with `--spec`.
4. Run `python -m unittest discover -s tests -v`.
5. Run `python scripts/sync_openapi_docs.py --check` to verify `docs/api.md` without modifying it.
6. Report test results and any unsupported fields or external references. Do not bypass validation or manually edit generated output.
