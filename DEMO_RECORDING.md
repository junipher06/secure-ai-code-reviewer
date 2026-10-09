# Course demonstration recording plan

This is a script for a future recording, not evidence that these actions have occurred. Use only synthetic messages in the public course sandbox.

## Before recording

1. Verify connected app username junipher06 and public target repository.
2. User adds GROQ_API_KEY privately in Settings → Secrets and variables → Actions. Never record the value or its entry screen.
3. User invites pwg011 with Write access; pwg011 accepts. Verify collaborator permission before claiming approval is enforceable.
4. Enable main branch protection after baseline publication: require PR, one approval, CODEOWNER review, dismiss stale approvals, strict up-to-date checks CI Checks / AI Review / AI Review Gate, conversation resolution, no force pushes/deletion, enforce for administrators/no bypass.
5. Read back the actual saved rule. The reviewer workflow cannot administer protection. Owner setup is separate from the agent's permissions.

## Recording sequence

Explain: “The model suggests; deterministic checks, automated tests, and human approval control merging.”

1. Show the application and passing local tests. Say these are local results, not hosted results.
2. Create a branch `codex/demo-missing-tests` from main. Add a security keyword such as pin reset to `src/customer_support/security_rules.py`, without accompanying tests. Label the PR as a synthetic course demonstration.
3. Open the PR. Show the AI comment with summary/risk/located findings/blockers/test plan/verdict and useful suggested unittest code. Missing tests must keep AI Review Gate failed even if the model mistakenly says PASS. Record the actual Groq response only after confirming no credentials or private data appear in it.
4. Show the merge box and verified protection: merging must be blocked. A failed job alone is insufficient evidence.
5. Developer reviews/adapts the suggested tests, adds cases for pin reset and unaffected routing, then commits the fix. The model does not apply tests or production changes.
6. Show new hosted CI and AI results. If a model/API/schema error occurs, explain the failure and fix/rerun deliberately; do not label it PASS.
7. Show the sensitive-path block before human approval. Have pwg011 independently review and approve the current commit from their own account. Do not impersonate or submit their approval with their connected account on their behalf.
8. Because triggers are pull_request only, manually rerun all jobs after approval. Show AI Review Gate passing and native approval/CODEOWNER requirements satisfied. New commits invalidate the old approval.
9. Show the final merge eligibility and actual branch protection readback. Merging the demo is optional and requires an explicit decision.

Optional extra: a synthetic added eval expression is deterministically blocked before Groq receives it. Do not execute that expression. This extra demonstration does not count as a real Groq review.

## Evidence to capture

- PR URL, head commit SHA, workflow run URL and attempt number.
- AI comment URL containing the real structured review/test suggestion.
- CI Checks, AI Review, AI Review Gate conclusions for unsafe and corrected states.
- Actual native branch-protection/ruleset settings and merge-blocked state.
- pwg011 approval at the corrected head SHA; no stale/self approval.
- Short narration distinguishing local tests, mocked API tests, real Groq review, hosted checks, and native merge enforcement.

Record only repository/code/check pages. Exclude secret screens, authentication prompts, environment variables, access tokens, emails, and private course transcripts. A recording is complete only after these live artifacts exist.
