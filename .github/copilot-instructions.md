# Project Guidelines

- Read [requirements.md](../requirements.md), [architecture.md](../architecture.md), and [design-review.md](../design-review.md) before changing dashboard behavior.
- Keep the demo limitations clear: login is not authentication, local storage is browser-only, and test execution is simulated.
- Escape user-controlled strings before inserting them into HTML. Validate runner inputs and keep the request size bounded.
- Run `mvn test` after Java or dashboard changes.
- Preserve test reports when deleting test cases; maintain unique test case IDs.
- GitHub Actions must remain read-only and use Java 17.
