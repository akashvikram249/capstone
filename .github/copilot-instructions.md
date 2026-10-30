# Project Guidelines

- Read [requirements.md](../requirements.md) and [architecture.md](../architecture.md) before changing sync behavior.
- Keep the OpenAPI generator deterministic; validate input fully before touching generated output.
- Preserve `docs/api.md` as generated output. Regenerate it with `python scripts/sync_openapi_docs.py`.
- Run `python -m unittest discover -s tests -v` and `python scripts/sync_openapi_docs.py --check` after relevant changes.
- Keep GitHub Actions read-only; CI detects stale docs and must not commit or push.
- Add regression tests for invalid input and output-preservation behavior when changing validation or writing.
