# Changelog

## US-102 dashboard capstone

- Replace the OpenAPI documentation generator with the Caseflow test management dashboard.
- Add Java 17 HTTP server and simulated asynchronous test runner.
- Add browser UI for case management, search/filter, run status, and execution reports.
- Store case and report data in local storage and use a demo-only login gate.
- Add Maven tests, GitHub Actions CI, and Copilot workflow helpers.
- Add an eight-phase Copilot SDLC pipeline with a coordinating orchestrator and phase-specific agents, prompts, and skills.

### Known limitations (US-102)

- The browser-side logic (search/filter, create/edit/delete, report display) has no automated tests; it is verified manually. Server behavior is covered by `DashboardServerTest` and `ExecutionServiceTest`.
- Editing a test case's ID does not update the `caseId` stored on existing execution reports; historical reports keep the original ID.
- Authentication and test execution are demo-only and not suitable for production.
