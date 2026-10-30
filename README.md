# Caseflow — UI Test Case Management Dashboard

A Java 17 capstone demo for managing UI test cases and viewing execution results.

## What it does

- Shows test cases by name, module, priority, status, and last result.
- Searches cases and filters by module, priority, and status.
- Creates and edits test cases with required-field validation and unique IDs.
- Confirms before deletion and keeps existing run reports.
- Simulates asynchronous test runs that finish Passed or Failed.
- Stores cases and reports in browser local storage.
- Shows reports with status, duration, execution time, and simulated failure details.

## Important demo limitations

- The sign-in screen is a demo gate, not real authentication. Any non-empty name works.
- The runner is simulated. It does not launch a browser or run Selenium/Playwright tests.
- Cases and reports live only in the current browser profile. Clearing browser data removes them.
- Selecting Pass/Fail is only for demonstrating the two report outcomes.

## Requirements

- Java 17
- Maven 3.8+

## Run locally

```sh
mvn test
mvn exec:java
```

Open [http://localhost:8080](http://localhost:8080), enter any display name, and start exploring. Override the port with `mvn exec:java -Dexec.args="8090"` or set `PORT`.

## Test

```sh
mvn test
```

The tests cover execution state transitions, server endpoints, validation errors, missing runs, and static page delivery. GitHub Actions runs `mvn verify` for pushes to `main` and pull requests.

## Project guide

- [requirements.md](requirements.md) — user story and acceptance criteria
- [architecture.md](architecture.md) — components, data flow, API, and scope boundaries
- [design-review.md](design-review.md) — reviewed decisions and limitations
- [impl-plan.md](impl-plan.md) — dependency-ordered delivery plan
- [CHANGELOG.md](CHANGELOG.md) — project changes
- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md) — PR description and reviewer checklist

## Copilot helpers

The `.github` folder includes project instructions, a dashboard reviewer agent, an implementation/review prompt, and an on-demand dashboard skill.
