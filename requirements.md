# Requirements

## User story

**US-102: Create and Manage UI Test Cases Through a Dashboard**

As a QA Automation Engineer, I want a web-based dashboard to create, view, edit, delete, and execute UI automation test cases, so that I can manage test scenarios efficiently, monitor execution results, and identify failures without manually reviewing test logs.

## Scope decisions

- Implement a Java 17 web server and a browser dashboard using plain HTML, CSS, and JavaScript.
- Keep test cases, the demo login name, and execution reports in the browser's local storage.
- Use a simple demo login gate only; there are no real accounts, passwords, or server-side authentication.
- The Run Test action uses a server-side simulator that returns Pass or Fail after a short delay. It does not launch a browser or run Playwright/Selenium.
- Seed sample test cases when this browser has no saved cases.

## Functional requirements

### FR-1: View, search, and filter test cases

After entering the demo dashboard, show a table with test ID/name, module, priority, test status, and last result. Allow search by relevant test fields and filtering by module, priority, and status.

### FR-2: Create test cases

Allow a user to create a case with a unique ID, name, module, priority, steps, and expected result. Validate required values and reject duplicate IDs without losing the form data. Confirm successful creation.

### FR-3: Edit and delete test cases

Allow saved case details to be edited and shown in the list. Ask for confirmation before deleting a case. Keep existing execution history available after a case is deleted.

### FR-4: Execute test cases

Let a user run a saved case and immediately show In Progress, followed by Passed or Failed. Demo-only outcome selection makes both results demonstrable; the simulator does not execute the written steps.

### FR-5: View execution reports

Show report status, duration, timestamp, associated case, and failure details when a run fails. Persist reports locally in the browser.

## Non-functional requirements

- Use Java 17 and Maven, without a database or frontend framework.
- Escape user-entered values before rendering them as HTML.
- Limit request size and validate values at the Java runner endpoint.
- Keep browser storage local to the current browser profile; it is not shared or backed up.
- Show actionable errors for storage or runner failures.
- Keep demo authentication and simulated execution clearly labeled as non-production.

## Acceptance criteria

- **AC-01 — View test cases:** The dashboard lists test name, module, priority, status, and last result; search and filters work.
- **AC-02 — Create a test case:** Mandatory fields are validated, duplicate IDs are rejected, and successful saves are confirmed.
- **AC-03 — Edit/delete:** Edits appear in the dashboard and deletion requires confirmation.
- **AC-04 — Execute:** Running a saved case shows In Progress followed by Passed or Failed.
- **AC-05 — Reports:** Completed reports show status, duration, timestamp, and failure details when applicable.

## Out of scope

- Production authentication, roles, access control, and multi-user data.
- Running real browser automation or connecting to an external test framework.
- Server/database persistence, audit retention, or cross-device synchronization.

## US-103: Filter Test Reports by Status

### User story

As a QA engineer, I want to filter test reports by status so I can find failed runs quickly.

**Source:** User-provided story in Copilot chat. No JIRA, Confluence, or document link was provided.

### Context and confirmed decisions

- The reports page displays completed reports stored in browser local storage.
- Current report statuses are Passed and Failed.
- The status filter provides All, Passed, and Failed options, with All selected by default.
- The selected filter is transient and is not saved to browser storage; a full page reload returns it to All.

### Functional requirements

#### FR-6: Filter execution reports by status

Provide a labeled status filter on the reports page. Selecting All shows every report; selecting Passed or Failed shows only reports with that status. Filtering updates the displayed report rows without a page reload, preserves their existing order, and does not modify or delete stored reports. When no reports match the selected status, show an explicit no-matching-reports message.

### Non-functional requirements

- Apply filtering in the browser to the report data already loaded by the dashboard; no server or persistence changes are required.
- Keep the filter operable and understandable using the dashboard's existing form-control and empty-state patterns.
- Announce the updated visible-result count and no-match state to assistive technology through a polite live region without moving focus.

### Acceptance criteria

- **AC-06 — Filter reports by status:** The reports page offers All, Passed, and Failed; All is selected by default and shows all reports.
- **AC-07 — Show matching reports:** Selecting Passed or Failed immediately displays only reports with the selected status, preserving the existing report order and report-detail actions.
- **AC-08 — Preserve report data:** Changing or resetting the filter does not change or remove reports in browser storage; after a full page reload the filter defaults to All.
- **AC-09 — Empty filter result:** If no reports match a selected status, the reports page displays a clear no-matching-reports message.
- **AC-10 — Announce filter results:** A polite live region announces the visible-result count after a filter change and announces when no reports match; focus remains on the filter.
- **AC-11 — Handle invalid report data safely:** If the stored report value is valid JSON but not an array, the dashboard shows an actionable report-data error, does not crash, and does not overwrite or delete the stored value.

### Out of scope

- Filtering by date, case, module, or other report attributes.
- Persisting the selected filter across page reloads.
- Changing how reports are generated, stored, or retained.
- Automatically repairing or deleting structurally invalid report data.
