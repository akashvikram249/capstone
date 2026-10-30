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
- [x] Tests: cover runner state transitions and HTTP endpoint success/error behavior; verify client interactions.
- [x] Simplicity: use JDK HTTP server and plain browser assets instead of unnecessary frameworks or database.
- [x] Transparency: label execution and login as demo-only; explain local-storage limits.

## Residual limitations

- Browser local storage is per browser profile and can be cleared by the user.
- Demo login does not authenticate a user.
- Demo runner does not launch a browser or evaluate the test steps.
