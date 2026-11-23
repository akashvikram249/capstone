# Changelog

## US-106 run statistics endpoint

- Add `GET /api/stats`, which returns `{"totalRuns":N,"inProgress":N,"passed":N,"failed":N}` for the runs the server has started.
- `totalRuns` equals `inProgress + passed + failed`; a fresh server returns all zeros, and counts reset when the server restarts.
- Non-GET methods (including HEAD) return 405 with `Allow: GET`.
- Backend-only: no change to the browser UI, local storage, or `POST /api/runs`.
- Add JUnit tests for the empty state, in-progress, pass/fail counts, and the 405 case.

## US-102 dashboard capstone

- Replace the OpenAPI documentation generator with the Caseflow test management dashboard.
- Add Java 17 HTTP server and simulated asynchronous test runner.
- Add browser UI for case management, search/filter, run status, and execution reports.
- Store case and report data in local storage and use a demo-only login gate.
- Add Maven tests, GitHub Actions CI, and Copilot workflow helpers.
- Add an eight-phase Copilot SDLC pipeline with a coordinating orchestrator and phase-specific agents, prompts, and skills.
