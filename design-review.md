# Design Review

## Review outcome

**Approved with the decisions and mitigations below.** The design is intentionally limited to a local generator and a read-only GitHub Actions check.

## Findings and decisions

| Area | Finding / risk | Decision |
|---|---|---|
| Synchronization semantics | PR check mode does not automatically commit regenerated documentation. | The generator has write mode for contributor use and check mode for CI. CI fails on stale output but never pushes. The workflow and README state this clearly. |
| Input selection | Two accepted root-level filenames could make implicit selection ambiguous. | Auto-discovery requires exactly one supported filename; users can pass `--spec` explicitly. |
| Validation | Syntax checks alone would allow structurally invalid contracts. | Parse first, restrict versions to OpenAPI 3.0.x/3.1.x, then use `openapi-spec-validator` before rendering. |
| Failure safety | A parse or validation failure must not truncate an existing reference. | Render in memory only after successful validation and atomically replace output only after rendering succeeds. Check mode is read-only. |
| Schema references | External references can require network access or produce non-reproducible content. | Do not fetch references. Render reference identifiers as provided; document external-reference resolution as out of scope. |
| Workflow permissions | A workflow that writes generated files would need broader permissions and creates token/loop risks. | Use `contents: read`; report drift as a failed check and require a normal reviewed commit. |
| Dependency safety | The generator depends on third-party parsing and validation libraries. | Keep direct dependencies explicit and run `pip-audit` in CI. |
| Agent lifecycle hooks | Hooks can run commands automatically during agent actions, but no universal command needs to run for every interaction. | Do not add a lifecycle hook; use the explicit prompt/skill and PR workflow instead of surprising side effects. |

## Review checklist

- [x] Correctness: output fields map to the agreed acceptance criteria.
- [x] Security: safe YAML parsing, no secrets, no network resolution, read-only workflow.
- [x] Error handling: failures are actionable and non-zero; invalid input does not modify output.
- [x] Test coverage: happy path, missing/empty/invalid specs, stale docs, and output preservation are planned.
- [x] Code clarity and DRY: parsing, validation, rendering, and writing are separate focused functions in one small CLI module.
- [x] Dependency safety: direct dependencies are declared and audited in CI.

## Residual limitations

- CI checks only root-level `openapi.yaml` and `openapi.json` by default; callers can explicitly provide another path locally.
- External `$ref` targets are displayed but not dereferenced.
- Generated Markdown is an API reference, not a hosted interactive explorer.
