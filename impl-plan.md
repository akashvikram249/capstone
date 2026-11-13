# Implementation Plan

| Priority | Task | Dependencies | Status |
|---:|---|---|---|
| 1 | Capture US-102 scope, behavior, and demo boundaries in requirements. | None | Complete |
| 2 | Approve the Java server, browser storage, runner API, and security limits. | 1 | Complete |
| 3 | Implement Java HTTP server and simulated asynchronous execution service. | 2 | Complete |
| 4 | Implement dashboard login gate, case CRUD, search/filter, and browser persistence. | 2 | Complete |
| 5 | Implement execution polling, status indicators, and report history. | 3, 4 | Complete |
| 6 | Add tests, CI workflow, Copilot customizations, documentation, and PR template. | 3, 4, 5 | Complete |
| 7 | Run Maven tests, start server, and verify UI/API behavior against AC-01–AC-05. | 6 | Complete |

## Blocked work

Production authentication, database persistence, and real browser automation are outside the approved demo scope.

## US-103 — Filter test reports by status

The tasks below cover approved AC-06–AC-11 and the accepted design-review decisions. They change only the existing browser report view; they do not add server behavior, persistence, or test tooling. The user approved this plan, authorizing Phase 5 implementation. Browser acceptance remains a manual check because the repository has no browser test harness.

| Priority | Task | Actual prerequisites | Completion criteria and focused verification | Status |
|---:|---|---|---|---|
| 1 | Guard report loading and rendering against valid-JSON, non-array stored values; show an actionable report-data error while leaving the stored value untouched. Ensure report-dependent rendering does not invoke array methods on invalid data. | None | In a browser, store valid JSON such as `null` or an object under the report-storage key, then load the dashboard. The dashboard does not crash, the reports view identifies the report-data problem and gives an actionable next step, and the original stored value remains byte-for-byte unchanged. | Complete — malformed shape displayed an error; stored value preserved |
| 2 | Add a visibly labeled native All/Passed/Failed status control to the reports page, with All selected by default and the selection kept only in the current page state. Reuse existing control styling. | None | Confirm the label is associated with the control, all three choices are available, All is initially selected, keyboard operation works, and changing the control does not write the selected value to browser storage. | Complete — label/options/default, keyboard selection, and reload reset checked |
| 3 | Connect the status control to an in-memory report projection and render its results. Preserve original ordering and report-detail actions, do not mutate or persist/delete the source reports, and distinguish the no-reports-yet state from an explicit no-matching-reports state. | 1, 2 | With report fixtures in browser storage, verify All shows every report and Passed/Failed show only matching rows in original relative order; report detail still opens by report ID; an unmatched selection shows a clear no-matching-reports message; changing back to All restores rows; stored reports remain unchanged. | Complete — filters, order, details, empty states, reload, and storage preservation checked |
| 4 | Add/update the polite live region for filter-result announcements without moving focus. | 3 | Change the filter and verify assistive technology is informed of the visible-result count or the no-match state; keyboard focus remains on the status control. Confirm the announcement reflects the rendered projection. | Complete — polite live-region attributes/text and retained focus checked; screen-reader speech not independently tested |
| 5 | Perform focused manual browser acceptance verification for AC-06–AC-11; record the outcomes against this checklist without introducing browser-test tooling. | 1, 2, 3, 4 | Checklist: (a) All is the initial selection and shows every report; (b) Passed and Failed update immediately, retain relative order, and keep detail actions working; (c) empty report storage retains the existing no-reports message and a nonmatching status shows a distinct no-match message; (d) filter changes leave report storage unchanged and a full reload resets to All; (e) polite count/no-match announcements occur without focus movement; (f) valid-JSON non-array report storage produces the actionable error without a crash or storage modification. Record pass/fail and any observed issue for every item. | Complete — integrated-browser checks passed; temporary fixtures/session cleared |
| 6 | Run the existing Maven test suite as regression verification; add no tests or dependencies for this feature. | 1, 2, 3, 4 | `mvn test` completes successfully; capture the command outcome and any failures for review. | Complete — `mvn test`: 7 tests passed, 0 failures/errors/skips |
| 7 | Review the completed US-103 changes against requirements, approved architecture, design-review decisions, and repository conventions. | 1, 2, 3, 4 | Review confirms AC-06–AC-11 coverage, safe escaped report rendering, non-destructive local-storage handling, no persistence/API changes, accessible announcements, and no unrelated edits; resolve or explicitly report findings. | Complete — checklist review completed; the report-storage failure finding was fixed and rechecked |
| 8 | Complete final verification and report readiness for human acceptance. | 5, 6, 7 | Confirm manual and automated evidence is recorded, review findings are resolved or clearly listed, and report readiness accurately describes remaining limitations and approval gates. | Complete — Maven verification, JavaScript syntax, and targeted browser checks passed |

### US-103 blockers

- The user-approved plan authorizes Phase 5 implementation; no additional design or tooling blocker is identified for the approved scope.
- Manual browser acceptance covered report-status subsets and order, report details, empty states, storage preservation, reload default, live-region attributes/text, focus retention, invalid-data handling, and keyboard letter selection. A targeted storage-write failure check also confirmed the report remains out of in-memory state, local storage is unchanged, and the storage error is shown.
- Latest verification: `mvn --batch-mode verify` passed (7 tests, 0 failures/errors/skips); `node --check src/main/resources/static/app.js` passed. Actual screen-reader speech was not independently tested.
- Dependency inventory found only test-scope JUnit dependencies; no automated CVE scan was run. See the implementation review in `design-review.md`.
- The story source is the user's Copilot chat message; no external JIRA, Confluence, or document source was supplied. No commit, push, deployment, or PR was authorized.
