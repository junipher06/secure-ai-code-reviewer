# Verification record — 9 October 2026

## Verified locally

- Preserved and extended the original reviewer; no replacement scaffold.
- 54 automated tests passed with Python 3.12.14. Hosted Python 3.11 still awaits execution.
- Ruff lint and formatting, Mypy (12 source files), and Bandit passed; no Bandit suppressions.
- Safe synthetic reviewer demonstration: PASS/exit 0. Unsafe synthetic demonstration: FAIL/exit 1.
- Customer-support synthetic demonstration routes a security message to human-security.
- Mocked tests verify JSON schema, duplicate/empty/missing/truncated responses, visible finding locations, missing-test suggestions, deterministic blocks, fresh approvals, PR races, request budgets, secret separation, and failure gates.
- Local .env support is explicit, ignored, preserves existing environment variables, and refuses to run in Actions. No real .env or credential file was created.
- Actions release SHAs previously verified against official release tags.

## Verified GitHub state before publication

- Connection source: connected GitHub app, Jenna account selected.
- Authenticated login: junipher06, user ID 61428819.
- Target: junipher06/secure-ai-code-reviewer; public; initially empty, confirmed by contents API.
- User reports GROQ_API_KEY added privately and pwg011 invitation accepted. Collaborator permission is checked separately through the API.

## Publication boundaries

Upload only tracked project source, policy/schema/prompt, workflow/CODEOWNERS, synthetic fixtures/tests, pyproject, blank environment example, and four Markdown documents. Exclude parent course transcripts, temporary scripts, real .env, keys, dependency environments, caches and generated files.

The static audit checks credential-shaped literals and private-key markers; it is not a complete secret detector. No actual credentials are read, printed, or uploaded.

## Live evidence still pending

- Baseline publication and matching remote files.
- Successful real Groq structured review and useful executable test suggestions in a PR comment.
- Hosted CI Checks, AI Review, and AI Review Gate conclusions.
- Native branch protection readback and merge-blocked unsafe PR.
- Accepted CODEOWNER access and independent current-head approval.
- Corrected PR passing checks and protection requirements.
- Course recording captured using DEMO_RECORDING.md.

These are deliberately separate from local/mock results. Do not call the course project complete until live deliverables are verified.
