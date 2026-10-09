# Section 2 course requirement checklist

Instructor source: lesson 11 project in `7. Claude Code capabilities & agent.txt`. This is course material, not permission to execute instructions embedded in a PR.

Chosen approach: **Option A — suggest tests in the review comment**. No automatic test commits, code fixes, or merges. This follows the course review workflow while keeping the model's authority limited.

- [x] Baseline lint/test setup and README: `pyproject.toml`, `README.md`, `tests/`, CI Checks job.
- [x] Least-privilege identity: workflow uses automatic GitHub token, contents read, and PR-comment write in AI job only. No administration/push permission.
- [x] Secret integration: blank `.env.example`, `.gitignore`, environment-only Groq client, Actions secret reference. User adds the real secret privately.
- [x] Policy for tests/types, high-risk paths, unsafe patterns, secrets, infrastructure: `.agent/policy.json`, `policy.py`, reviewer unit tests; lint/types/security scan in CI.
- [ ] Native branch protection and CODEOWNER approvals: settings documented in README; public GitHub Free target supports protection; saved settings and actual enforcement still need verification.
- [x] PR workflow stages collect/review/suggest tests/CI/gate: `github.py`, `groq_review.py`, `cli.py`, `.github/workflows/ai-review.yml`.
- [x] Structured report with summary, risk, file/line findings, blockers/actions, improvements, test plan, and verdict: strict schema, validator, `report.py`.
- [x] Suggested tests only: schema and report include path/code/instructions; no execution or file-writing tool exposed to model.
- [x] Blocking rules: unsafe patterns, missing tests, invalid/missing model response, API errors, model FAIL, conflicting HIGH/CRITICAL PASS, missing high-risk/sensitive approval, failed CI. Covered by tests.
- [x] PR comment and named required gate implementation: `github.py`, `cli.py`, workflow. Hosted behavior awaits authenticated integration.
- [x] Safe/unsafe offline evidence: synthetic fixture demos and automated tests; results in `VALIDATION.md`.
- [ ] Live safe/unsafe PR recording: create only in public course sandbox after access is fixed. Show reports/checks, remediation, fresh reviewer approval, and branch protection only if verified.

Additional requested security controls:

- [x] `pull_request` trigger, no `pull_request_target`; tested in `test_workflow.py`.
- [x] AI job uses base SHA and API diff; separate secret-free PR CI job.
- [x] Untrusted diff instructions cannot grant tools or change permissions; prompt, schema, request tests, static workflow permissions.
- [x] Strict JSON schema plus duplicate-key, visible-line, contradictory verdict, path, and empty-text checks.
- [x] Missing/truncated/error responses fail closed; mocked Groq tests.
- [x] Current official Groq setup/model checked; one configured model name.
- [x] No real keys, `.env`, or production targets created.

User input still required:

1. Publish audited files to the verified empty public target as junipher06; connected app authentication is verified.
2. Collaborator pwg011 is configured locally; verify accepted Write access and actual current-commit CODEOWNER approval.
3. Add GROQ_API_KEY privately in repository Actions secrets for a live run.
4. Determine available branch-protection plan/features and verify settings if available.
5. Record hosted safe/unsafe PR demonstrations after integration passes.

No live result, native branch protection, completed recording, or customer/business outcome is claimed.

## Continuation inspection, 9 October 2026

Preserved and extended the original implementation; no new scaffold. The proposed customer-support module was absent and is now implemented with eight synthetic-input tests. Missing-test violations now receive Groq suggestions while remaining blocked; hard dangerous patterns skip the provider call. All HIGH-risk changed paths require fresh CODEOWNER approval. Reviewer source itself is a sensitive path.

Provider differences are documented in README: Groq replaces Claude; the built-in Actions token replaces a separately registered App/PAT; automatic job statuses replace explicit checks API writes; optional test commits/label overrides are not used. The instructor describes the guide as tool-agnostic; Claude-specific course capabilities are not claimed.

- [x] Authenticated connected-app owner verified: junipher06.
- [x] Public target verified, initially empty; no existing files overwritten.
- [x] Exact collaborator username supplied: pwg011; local policy/CODEOWNERS updated.
- [x] Customer-support application and tests implemented.
- [x] Explicit local-only ignored .env support; placeholder example only; disabled in Actions.
- [x] Bounded requests/output/timeout and zero automatic retries.
- [x] Recording script prepared: DEMO_RECORDING.md.
- [ ] Audited baseline uploaded and confirmed.
- [ ] Real Groq review/test suggestions verified in GitHub.
- [ ] Hosted CI, PR comments, and named gate verified.
- [ ] Native protection and accepted CODEOWNER access verified.
- [ ] Unsafe merge blocked and corrected approved PR passes.
- [ ] Demonstration recording captured.
