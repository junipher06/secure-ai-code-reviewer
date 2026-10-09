# Secure AI Code Reviewer

A Section 2 course project for **Junipher06/secure-ai-code-reviewer**, intended to be PUBLIC for GitHub Free branch protection. It reads a pull request diff through GitHub's API, checks deterministic rules, asks Groq for a structured review, and reports PASS or FAIL. It never applies the suggested tests or edits, pushes, or merges PR code.

**Current state:** local implementation; public empty repository and owner account verified on 9 October 2026. Live Groq responses, hosted checks/comments, collaborator access, and branch protection still await verification. All demo code and responses are explicitly synthetic. No real API key or `.env` was created.

## Understand the flow

1. GitHub starts the workflow when a PR opens or changes.
2. **AI Review** checks out the trusted base commit, fetches the PR diff as data through the API, and applies policy checks. Prohibited patterns fail before sending the diff to Groq.
3. If deterministic checks permit it, Groq returns JSON. The app validates both its structure and its meaning: findings must refer to visible diff lines, and PASS cannot coexist with blocking findings.
4. Sensitive paths and HIGH risk reviews need a configured CODEOWNER's approval of the current PR commit. Sensitive paths additionally require a matching CODEOWNER.
5. **CI Checks** runs lint, type checks, unit tests, and a static security scan in a separate job. It executes PR code but has no Groq secret and read-only GitHub permissions.
6. **AI Review Gate** fails if either job fails, is cancelled, or is skipped. Branch protection is needed to make that failing check prevent merging.

The model receives no tools. PR instructions are untrusted text, never authority. Strict output validation limits what the response can do; it does not guarantee that every finding is correct.

## Files explained

- `pyproject.toml`: Python package metadata, bounded dependencies, and check settings.
- `.gitignore`: excludes local environments, keys in `.env`, caches, and build products.
- `.env.example`: blank `GROQ_API_KEY` placeholder; documentation only.
- `src/reviewer/__init__.py`: marks the Python package.
- `src/reviewer/errors.py`: safe, understandable failure messages.
- `src/reviewer/diff.py`: parses file paths, added code, and visible line numbers without executing code.
- `src/reviewer/github.py`: fetches PR data, diffs, reviews, and posts the report through fixed GitHub API endpoints.
- `src/reviewer/policy.py`: checks risky patterns, test expectations, sensitive paths, and current human approvals.
- `src/reviewer/groq_review.py`: calls Groq and validates the structured response; missing keys, failed requests, and invalid output fail closed.
- `src/reviewer/report.py`: formats the review and escapes untrusted text/redacts recognizable credential patterns.
- `src/reviewer/cli.py`: coordinates offline demos and live reviews; exit 0 means PASS, exit 1 means FAIL.
- `.agent/policy.json`: centralized model name, required checks, sensitive paths, reviewers, risky patterns, and test expectations.
- `.agent/review.schema.json`: strict response schema; unknown fields are rejected.
- `.agent/reviewer_prompt.md`: tells the model its limited review role and to treat diff instructions as untrusted.
- `.github/workflows/ai-review.yml`: separate review, CI, and final gate jobs.
- `.github/CODEOWNERS`: placeholder ownership example; replace it before sensitive changes can pass.
- `tests/fixtures/safe.diff`: synthetic source change with accompanying tests.
- `tests/fixtures/unsafe.diff`: synthetic `eval` change without tests.
- `tests/fixtures/model-pass.json`: synthetic model response used only for offline testing.
- `tests/fixtures/README.md`: explains the fixtures' synthetic status.
- `tests/test_reviewer.py`: policy, approval, schema, API-failure, reporting, and offline demo tests.
- `tests/test_github.py`: mocked API collection, race, pagination, and completeness tests.
- `tests/test_workflow.py`: checks workflow triggers, permissions, secret separation, and the required gate.
- `COURSE_CHECKLIST.md`: maps instructor requirements to implementation and pending setup.
- `VALIDATION.md`: records the local checks and remaining integration work.

## Local setup and checks (PowerShell)

Run these commands **inside this project folder**:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy src
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m bandit -r src -ll
.\.venv\Scripts\python.exe -m reviewer.cli --demo safe
.\.venv\Scripts\python.exe -m reviewer.cli --demo unsafe
```

The safe demonstration should exit **0**. The unsafe demonstration should exit **1**, explaining the dangerous pattern and missing tests. Both use a synthetic model response and make no Groq call. An unsafe demo failure is the intended result.

On macOS/Linux use `.venv/bin/python` instead. Python 3.11 or newer is required. Dependencies have bounded versions; the first installation needs internet access. The tests mock network clients and require no API key.

## Groq setup: no paid API is required for offline work

Create/sign into [Groq Console](https://console.groq.com/) when ready for a live demo. Check the account's current free-tier availability and limits yourself; free access is not promised indefinitely. Rate limits, unavailable models, and quota errors fail the review, rather than silently passing it.

The model is configured only in `.agent/policy.json`: `openai/gpt-oss-20b`. Official SDK, model, and strict structured-output documentation were checked on 9 October 2026:

- [SDK quickstart](https://console.groq.com/docs/quickstart)
- [Supported models](https://console.groq.com/docs/models)
- [Structured outputs](https://console.groq.com/docs/structured-outputs)

The code uses `from groq import Groq` and `response_format` with `json_schema` and `strict: true`. Live compatibility still needs an actual authenticated run.

For local live execution set **GROQ_API_KEY** privately in your operating system/process environment. Do not paste it into chat, source, YAML, logs, or screenshots. Optional local live testing can use an ignored `.env` file you create privately, matching the blank `.env.example`. Pass `--env-file .env` explicitly. It accepts only GROQ_API_KEY and GITHUB_TOKEN, preserves existing environment values, and is disabled in GitHub Actions. Never commit the real file. No real .env is supplied.

For Actions, you enter the key yourself:

1. Open this repository on GitHub.
2. Go to **Settings → Secrets and variables → Actions**.
3. Choose **New repository secret**.
4. Name it **GROQ_API_KEY**, enter the value privately, and save.

The workflow references `${{ secrets.GROQ_API_KEY }}` only in the AI review step and never prints it. GitHub supplies `GITHUB_TOKEN` automatically; do not create a token for the workflow.

## GitHub authentication and public sandbox

Access is through the connected GitHub app, not GitHub CLI. Its **Jenna** account connection was selected and verified as **junipher06** (the earlier Primary connection was pwg011). The owner created the public repository; the connector confirmed it is empty. No account passwords or tokens were obtained or displayed.

Repository: https://github.com/junipher06/secure-ai-code-reviewer

This folder has an isolated local Git repository. Publication uses the authenticated GitHub app's content/Git APIs; no local GitHub token is needed. Only the audited files listed in VALIDATION.md may be uploaded. Existing remote files must be inspected and preserved; never force-push over them. Course documents, parent workspace files, .venv, .env, and caches are excluded.

For optional terminal work, install GitHub CLI and use `gh auth login --hostname github.com --web --git-protocol https`, then verify `gh api user --jq .login` returns junipher06. The CLI's login is separate from the app connection. Do not use `gh auth token` or display credentials.

## Human reviewer and CODEOWNERS

You supplied **pwg011** as the collaborator. CODEOWNERS and trusted_reviewers are configured accordingly. Invite pwg011 under repository **Settings → Collaborators** with Write access and have them accept. Administrator access is unnecessary. Accepted access and a real approval still need verification.

The example CODEOWNERS assigns all files to that person. The Python gate supports simple glob paths and explicit individual usernames, not GitHub teams or the full CODEOWNERS pattern language. A sensitive path with a placeholder, missing owner, or missing current approval fails closed. A PR author cannot approve their own change for this gate. Earlier approval does not count for a newer commit, and a later dismissal/change request supersedes approval.

Because the workflow triggers only on `pull_request`, after the collaborator approves the current commit choose **Actions → the PR run → Re-run all jobs**. Approval alone does not automatically rerun this workflow.

## Branch protection: setup still required

**Branch protection is not enabled or verified.** The target is now public, as requested. [GitHub's official documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) supports protected branches on public repositories with GitHub Free. A failing check alone does not prevent merging until the saved protection rule is verified.

If protection is available, configure the default branch under **Settings → Branches → Add branch protection rule** (or corresponding ruleset):

- Require a pull request and at least one approving review.
- Require review from CODEOWNERS and dismiss stale approvals on new commits.
- Require status checks **CI Checks**, **AI Review**, and **AI Review Gate**.
- Require the branch to be up to date before merging and resolve review conversations.
- Disable force pushes/deletions and avoid administrator bypasses.

Run a PR once so check names appear in settings. Verify the saved rule and a blocked unsafe PR before claiming merge enforcement. The application has no repository-administration permission to configure this for you.

## Security limits and trust

Deterministic rules flag added `eval`, disabled TLS checks, shell execution, likely hardcoded credentials, and destructive infrastructure commands. Source changes need added/updated test lines. These are conservative heuristics: false positives and missed vulnerabilities are possible, and test presence does not prove coverage. Binary-only, omitted, oversized, unsupported diffs and invalid responses fail closed for manual review. Do not truncate a diff to get a PASS.

The AI job reads trusted base files and never checks out PR head code. Its only write permission is PR comments. The CI job gets no Groq secret. No job may push commits, administer the repository, or merge. Model test suggestions are displayed as text and never executed or written to files.

Review the workflow itself before running same-repository PRs: a collaborator with write access can propose a modified workflow that requests secrets. CODEOWNERS protects merging when enforced; it does not itself stop a malicious workflow from running. Treat write-access collaborators as trusted, use GitHub-hosted runners, and never approve a suspicious fork workflow run just to obtain a passing result. Fork PR secret/comment restrictions can cause a deliberate fail-closed result.

Groq receives eligible code diffs, so use synthetic course code, not production or confidential customer data. Redaction is best effort, not a complete secret detector. No production repository is a test target.

## Course demonstration

First use the offline commands above. After GitHub, Groq, and reviewer setup are complete, create small synthetic PRs: one with unsafe `eval` and missing tests, then a corrected implementation with tests. Demonstrate failing/passing checks and fresh human approval where required. Record the workflow runs and reports, excluding secret screens. The offline demo is not evidence that hosted integration works. Follow `COURSE_CHECKLIST.md` for the remaining evidence.

## Synthetic customer-support application

The original local reviewer did not include the proposed support module. It now has `customer_support.routing.route_ticket`, which returns general/billing/technical queues, and `customer_support.security_rules.needs_human_review`, which escalates security messages. It never sends messages, stores customer records, or calls another service. Run `python -m customer_support.routing` after installation for a synthetic example. Eight tests cover priority, case, empty input, and input bounds.

Use this module for the real PR demonstration: an added security-routing feature without tests should fail and receive suggested tests; adding reviewed test code should pass model/CI checks while still requiring pwg011's fresh approval. See DEMO_RECORDING.md. Suggestions must include imports and unittest cases, but their usefulness must be assessed during the real run; schema validity is not proof of correctness.

## Groq substitution and free-tier bounds

The lesson 11 guide describes the project as tool-agnostic but shows Claude/ANTHROPIC_API_KEY examples. This implementation substitutes Groq/GROQ_API_KEY and a configured strict-output model. It is not a Claude Code integration, Claude multi-agent demonstration, or evidence that Claude-specific features were used. If the assessor explicitly requires Claude credentials or Claude Code execution, that item remains unsatisfied by this free implementation and needs clarification; no such mandatory provider statement appears in the supplied project guide.

The built-in GitHub Actions installation token replaces a separately registered bot/App token. GitHub creates job checks automatically, so no checks:write permission is needed. This retains minimum permissions without the optional ability to commit generated tests. Collect/review run in one trusted job; test generation is advisory only (course Option A). Optional label bypasses are omitted: destructive patterns are always blocked.

Policy bounds: 8,000-byte complete diff, 24,000-byte serialized request, 2,048 maximum completion tokens, 45-second Groq timeout, zero automatic retries. Size is a conservative budget guard, not a token-count guarantee. Consult your account's actual [Groq limits](https://console.groq.com/docs/rate-limits); quota errors fail closed and require a later deliberate rerun. Do not truncate a PR to evade the bounds. Python import conventions and the test command are included as trusted context for useful test suggestions. No source changes are applied by the model.
