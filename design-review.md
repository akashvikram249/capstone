# Design Review

## Outcome

Approved as a **local demo capstone**, not as a production test management system.

## Findings and decisions

| Risk / question | Decision |
|---|---|
| User requested a Java implementation but local browser persistence. | Use a Java 17 server for static files and the runner API, with browser local storage for cases and reports. |
| AC-04 says execute a UI automation test, but no real test harness was selected. | Use a clearly labeled simulator to demonstrate In Progress, Passed, and Failed. Document that it does not run browser automation. |
| AC-01 assumes a logged-in user. | Provide a demo-only login gate with no real credentials or security claim. |
| Duplicate IDs and required fields must be reliable. | Validate trimmed mandatory fields and unique IDs (case-insensitive) in the dashboard before saving. |
| User-entered content could be unsafe when displayed. | Escape all dynamic values before inserting into dashboard HTML. |
| Runs are asynchronous and need history. | Java returns a run ID and updates status; the browser polls and stores completed reports locally. |
| Deletion should not erase evidence. | Case deletion preserves existing execution reports. |

## Review checklist

- [x] Correctness: map each user-story criterion to a visible dashboard behavior.
- [x] Security: explicitly limit demo login; escape user content; bound and validate runner requests.
- [x] Error handling: handle duplicate IDs, validation errors, missing runs, and server failures.
- [x] Tests: cover runner state transitions and HTTP endpoint success/error behavior; verify client interactions with a manual browser checklist because no browser test harness exists.
- [x] Simplicity: use JDK HTTP server and plain browser assets instead of unnecessary frameworks or database.
- [x] Transparency: label execution and login as demo-only; explain local-storage limits.

## Residual limitations

- Browser local storage is per browser profile and can be cleared by the user.
- Demo login does not authenticate a user.
- Demo runner does not launch a browser or evaluate the test steps.

## US-103 — Filter test reports by status

### Review scope and approval status

Reviewed the approved US-103 requirements (AC-06 through AC-11) together with the US-103 architecture addition and the current report renderer, storage helpers, report-detail event handling, and available tests. This section supplements the US-102 review above; it does not change or revoke its outcome.

**Status: Approved for implementation under the user-approved US-103 plan.** The normal-path design covers the stated criteria and preserves the existing client-side report ownership boundary. The user accepted the three review recommendations below; the requirements and architecture artifacts record those decisions.

### Severity-ranked findings

| ID / severity | Classification and evidence | Impact | Recommendation |
|---|---|---|---|
| US103-F1 — **P2 (Medium)** | **Confirmed existing data-validation defect / integration risk.** `app.js` `readStorage` parses JSON but does not check the parsed value's shape; `renderReports` assumes `state.reports` has array methods (`.length` and `.map`). The proposed filter similarly depends on an array. Valid JSON such as `null` or an object in the report-storage key therefore bypasses the current parse-error fallback and can throw during rendering, preventing the reports page from displaying its empty/error state. | A browser-local storage value that is syntactically valid but not an array can break both the current report view and the planned All/status-filter views. This is not a defect in the specified filtering algorithm for valid report data. | **Accepted:** validate the loaded report value before array operations, display an actionable error, and leave the stored value untouched. The error is distinct from empty-report and no-match states. |
| US103-F2 — **P2 (Medium)** | **Verification risk.** The architecture explicitly notes that there is no browser JavaScript test harness. The available `DashboardServerTest` covers Java HTTP/static delivery, not selection changes, DOM rendering, storage preservation, or report-detail actions. | The central behavior for AC-06–AC-11 could regress without any automated test failing; server tests cannot demonstrate client-side filtering or data immutability. | **Accepted:** use a documented manual browser acceptance checklist covering default/All, each subset and stable order, details action, both empty states, reload-to-All, result announcements, unchanged stored data, and invalid-data handling, together with `mvn test`. Do not add test tooling or dependencies for this feature. |
| US103-F3 — **P3 (Low)** | **Accessibility risk / assumption.** The architecture selects a native control with a visible label, which provides standard keyboard operation. However, the current report count is an ordinary `<span>` and the report container has no live-region semantics; the architecture did not specify how a screen-reader user is informed that the result list changed after selection. | A user operating the filter with assistive technology may hear the changed select value without a clear announcement of the updated match count or no-match result. | **Accepted:** add a scoped polite live region that announces the visible result count or no-match state without moving focus. |

### Decisions and trade-offs

- **Supported normal path:** retain a transient, in-memory projection of the report array; All is the initial filter; Passed and Failed preserve source order; filtering does not request the server or write/delete reports; reloading returns the filter to All. These choices directly satisfy AC-06–AC-08 and preserve the stated local-storage boundary.
- **Empty states:** keep “No execution reports yet” distinct from the explicit no-matching-reports state required by AC-09. A no-match result is ordinary filtering, not a storage/runner error.
- **Report details and rendering:** keep actions resolved by original report ID against the full report collection, and continue escaping report-derived values before HTML insertion. The existing document-level delegated click handler and `showReport` lookup provide a compatible pattern, provided the filtered renderer does not replace the source collection.
- **Invalid report data:** guard against a parsed non-array report value, surface an actionable error, and preserve the stored value without automatic repair or deletion.
- **Accessibility:** announce the filtered result count and no-match state in a polite live region while retaining focus on the native filter.
- **Verification:** use a documented manual browser acceptance checklist for client behavior and run `mvn test` for Java regressions; no new test tooling or dependency is added.
- **Count semantics:** architecture says the count reflects visible rows. This is consistent with the displayed projection; requirements do not independently prescribe count semantics.
- **Privacy/security:** the planned filter uses only already-loaded local report data and sends neither report content nor filter choice to the server. No new trust boundary or persistence surface is proposed.
- **Scope and simplicity:** the native select and existing empty-state styling are proportionate to this two-status filter. No custom control, backend endpoint, or persisted preference is justified by the requirements.

### Approval status

The three recommendations are reflected in `requirements.md` (AC-10 and AC-11), `architecture.md`, and this review. The user approved the design and implementation plan for Phase 5. This approval does not authorize scope expansion or later SDLC phases.

### US-103 implementation review

The completed report-filter diff was checked against AC-06–AC-11, the approved architecture and design decisions, report rendering and storage call sites, available tests, Maven dependencies, and the CI workflow.

| Review area | Result |
|---|---|
| Correctness | The All/Passed/Failed view preserves source order and report-detail IDs, distinguishes the empty states, and leaves filter selection transient. |
| Security | Report fields continue through HTML escaping; filtering makes no server request and adds no trust boundary. The demo-login and local-storage limitations remain documented. |
| Error handling | Valid-JSON, non-array report data is handled without overwriting it. One additional finding below was fixed: failed report-storage writes could previously be followed by a success toast. |
| Test coverage | Java tests cover runner and HTTP behavior; they do not automate dashboard JavaScript. Manual browser checks covered the report acceptance checklist and a simulated storage-write failure. |
| Clarity / DRY | The report projection and persistence path use the existing renderer and storage helper; no review-worthy duplication was found. |
| Dependency safety | `mvn --batch-mode dependency:tree` showed JUnit Jupiter 5.11.4 and its transitive dependencies in test scope, with no production dependency declared. This is an inventory only; no CVE database or automated vulnerability scanner was run, so no vulnerability-free claim is made. |
| CI configuration | `.github/workflows/ci.yml` grants only `contents: read` and configures Java 17. |

#### Finding and disposition

**US103-CR1 — P2 (Medium), resolved.** `recordReport` previously returned success even when `saveStorage` failed, and updated the in-memory report list before persistence succeeded. A run could therefore show a success-shaped message and later render an unsaved report. The fix now persists a candidate list first, updates state and rerenders only after a successful write, and leaves the existing storage-error toast visible on failure. A targeted browser check simulated a report-storage quota error and confirmed a false result, unchanged in-memory and stored reports, and the storage error message.

**Review outcome:** no unresolved code-review findings. Limits remain: the browser UI has no automated JavaScript test harness; actual screen-reader speech and a dependency CVE scan were not performed.
