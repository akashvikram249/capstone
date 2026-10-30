---
description: "Update the generated API reference after changing an OpenAPI contract"
name: "Synchronize OpenAPI Documentation"
agent: "agent"
---

Review the changed OpenAPI contract and the generation rules in [requirements.md](../../requirements.md). Run `python scripts/sync_openapi_docs.py` to update `docs/api.md`, then run:

1. `python -m unittest discover -s tests -v`
2. `python scripts/sync_openapi_docs.py --check`

Fix failures caused by this change. Do not edit the generated reference by hand, weaken validation, add secrets, or make CI push commits. Summarize changed contract fields and test results.
