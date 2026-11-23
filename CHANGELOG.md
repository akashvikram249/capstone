# Changelog

## US-102 dashboard capstone

- Replace the OpenAPI documentation generator with the Caseflow test management dashboard.
- Add Java 17 HTTP server and simulated asynchronous test runner.
- Add browser UI for case management, search/filter, run status, and execution reports.
- Store case and report data in local storage and use a demo-only login gate.
- Add Maven tests, GitHub Actions CI, and Copilot workflow helpers.
- Add an eight-phase Copilot SDLC pipeline with a coordinating orchestrator and phase-specific agents, prompts, and skills.

## US-105 — Run statistics endpoint

- GET /api/stats returns run statistics as JSON {"totalRuns":N,"inProgress":N,"passed":N,"failed":N}; counts runs started since the server began (in memory); non-GET methods return 405 with Allow: GET.
