# Automated API Documentation Sync

Generate and verify a Markdown API reference from a root-level OpenAPI 3.0.x or 3.1.x contract.

## Requirements

- Python 3.11 or newer
- pip

## Install

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Generate documentation

Place `openapi.yaml` or `openapi.json` in the repository root, then run:

```sh
python scripts/sync_openapi_docs.py
```

The command validates the specification and creates or updates [`docs/api.md`](docs/api.md). If both supported filenames are present, choose one explicitly:

```sh
python scripts/sync_openapi_docs.py --spec openapi.json
```

To check that the committed documentation is current without changing files:

```sh
python scripts/sync_openapi_docs.py --check
```

When the check reports stale documentation, regenerate the file and commit it with the OpenAPI change.

## Tests

```sh
python -m unittest discover -s tests -v
```

The GitHub Actions workflow runs tests, a dependency audit, and the documentation check for relevant pull requests. It has read-only repository permissions and never commits generated files.

## Copilot workflow helpers

Workspace instructions, a focused API documentation review agent, a synchronization prompt, and an on-demand synchronization skill are under `.github/`. There is no agent lifecycle hook: generation and CI checks are explicit commands, and the GitHub Actions workflow is the appropriate deterministic enforcement point.
