---
name: plan-feature-tests
description: Create, review, or execute resource-bounded, traceable feature QA plans and reports from specs, acceptance criteria, screenshots, API contracts, implementation diffs, or existing checklists. Use when an AI coding agent is asked to help test a feature, review test completeness, run an approved plan, resume partial QA, or report PASS/FAIL/BLOCKED results with safe mocks, cleanup, usage warnings, and build-time limits.
---

# Plan Feature Tests

## Purpose

Turn feature requirements into a traceable, executable QA plan. Use a bounded completeness loop before execution, stop for material resource gates, and produce a concise report that accounts for every frozen test ID.

## Host Capabilities and Portability

- The core workflow is model-neutral. Skill discovery, invocation syntax, tool names, and permissions belong to the host. `agents/openai.yaml` is optional Codex UI metadata; other hosts do not need it or the `$plan-feature-tests` invocation syntax.
- Resolve `references/` and `scripts/` relative to the directory containing this `SKILL.md`, not the project working directory. Transfer the complete skill directory. Use the resolved absolute script path and an available Python 3 interpreter for validation; quote paths containing spaces.
- Before planning or execution, record applicable capabilities as Available, Unavailable, or Not Required: source/file access, artifact writing, Python 3, Git or another source-version mechanism, command monitoring and safe interruption, device/browser access, and readable usage telemetry. Record the actual tool or limitation in `資源預算與門檻` or the report premises.
- With supplied source text but no workspace access, continue only the planning/review that the supplied evidence supports. Do not claim to have inspected inaccessible code, calculated unavailable fingerprints, or executed commands. Request missing sources for affected scope. Without Git, use supplied versions or content hashes and disclose the unavailable branch/dirty-tree baseline.
- If Python, required resources, or file access is unavailable, label the artifact `VALIDATION_NOT_RUN`, explain the missing capability, and provide the validation command for a capable host. Do not claim validated handoff or execute from an unvalidated plan. This artifact-level label does not replace test-case statuses or imply that requirements are resolved.
- Before launching a build, ensure the host can monitor progress and enforce the approved deadline safely. Otherwise leave affected cases `NOT_RUN` and resolve the execution arrangement with the user; do not launch an unmonitorable build. Missing runtime/device capability cannot be replaced by static PASS evidence.
- Preserve exact template headings, column names, IDs, and status tokens required by the validator. Narrative may follow the user's language; do not translate or rename the schema.

## Select the Mode

- Use `PLAN` when asked to create a plan or generically asked to test without an approved plan. Create the plan, run the completeness loop, and keep every case `NOT_RUN`; do not execute yet.
- Use `REVIEW` when inspecting an existing plan or when source changes or newly discovered behavior may invalidate a frozen plan.
- Use `EXECUTE` only when the user explicitly approves execution or names an already approved plan. Do not re-propose unchanged premises.
- Use `RESUME` for partial execution. Preserve results and run only `NOT_RUN` or explicitly requested cases after verifying that the frozen source fingerprint is unchanged.
- For a narrowly named rerun such as one test ID or one command, verify the frozen plan and source fingerprint, then run only that scope. Do not restart the full completeness loop unless the source or scope changed.

## Read the Required Resources

- Read `references/test-plan-template.md` before creating a plan or report.
- Read `references/spec-completeness-checklist.md` when UI, API, state, interaction, accessibility, or design requirements are in scope.
- Run `scripts/validate_test_plan.py` for every saved Markdown plan or report before validated handoff; follow the capability fallback above when it cannot run.

## Inspect Project Context

1. Read applicable repository instructions and project-local task or lesson files before inspecting code or changing state.
2. Record the current branch/commit, source versions, dirty-tree baseline, and affected modules. Preserve unrelated user changes.
3. Inventory the input size before broad reads. Use the resource gates below before expanding beyond the initial scope.
4. Prefer an existing structural index such as CodeGraph. Inspect actual entry points, callers, callbacks, shared state, and runtime control paths instead of inferring behavior from names or stale documentation.
5. Create a stable source ledger with IDs, locations or versions, scope, status, and a fingerprint suitable for later freshness checks.

## Apply the Specification Gate

1. Read the complete feature spec or checklist once and capture it in the source ledger.
2. Identify goals, entry points, affected modules, user flows, API contracts, UI states, business rules, acceptance criteria, exclusions, and suggested verification.
3. Compare the spec, design, confirmed user decisions, current code, and historical reports when available.
4. Use `references/spec-completeness-checklist.md` to inspect every applicable screen, component, state, API contract, and data source.
5. Mark missing, conflicting, or ambiguous requirements as `Needs Confirmation`. State the affected test cases and impact. Never invent unspecified values.
6. Resolve source-of-truth differences before execution. Record the selected source as a premise; treat historical reports only as background evidence unless the user explicitly accepts them.

## Run the Bounded Completeness Loop

Run at least two rounds and at most three rounds for every new or materially changed feature plan:

1. `Round 1 — Spec-first`: build the requirement, exclusion, screen/state, API, code-path, test-support, evidence, and cleanup inventories; generate the first case set.
2. `Round 2 — Code/Failure-first`: independently inspect implementation entry points, callers, callbacks, lifecycle, cancellation, retries, concurrency, boundaries, security, regressions, and hidden flows. Compare those findings with the first case set.
3. Finish Round 2 as `READY_TO_FREEZE` only when it adds zero requirements and zero cases and the total unresolved gap count is zero.
4. If Round 2 changes the plan, repair it and run `Round 3 — Delta audit` against only the changed sources, new requirements, new cases, and unresolved gaps.
5. Finish Round 3 as `READY_TO_FREEZE` only when it adds no new requirement or case and has zero unresolved gaps.
6. If Round 3 still finds new scope, stop as `LOOP_LIMIT_REACHED`. If requirements remain ambiguous, stop as `NEEDS_CONFIRMATION`. If source versions keep changing, stop as `SCOPE_UNSTABLE`.
7. Never start Round 4 without explicit user approval. Do not call a non-ready plan complete or execute its affected cases.

Record every round in `Completeness Loop` with the source fingerprint, review perspective, new requirement count, new case count, unresolved gap count, and result. Freeze the exact source fingerprint, plan version, and test-ID set only after `READY_TO_FREEZE`.

Read the full source only in Round 1. In later rounds, verify fingerprints and focus reads on deltas, unresolved areas, and relevant entry points or call paths not yet inspected, within the file-read gate. Do not reread unchanged sources already covered. The independent review perspective does not require a separate agent. After context compaction, reload the source ledger, loop record, frozen case set, and open gaps instead of rebuilding the whole plan from memory.

If execution discovers a new path, requirement, or source change, pause the affected scope and return to `REVIEW`. Update the plan, rerun the bounded loop, obtain confirmation for any material scope or support change, then `RESUME`.

## Enforce Resource and Time Gates

Record the gates in `資源預算與門檻` before execution.

### Usage gate

- Record the starting weekly remaining percentage and timestamp only when the active host exposes readable telemetry for that weekly usage window. Record the provider, window, and reset time when available; do not compare different providers or quota windows.
- Stop before the next large stage whenever weekly remaining usage drops by another 5 percentage points from the recorded baseline or last confirmed checkpoint. Report completed work, remaining scope, the next stage, and ask whether to continue.
- If one stage crosses multiple 5-point thresholds, report all crossed thresholds but request one decision at the current checkpoint.
- Reset the baseline when the usage window resets.
- If telemetry is unavailable, record `Unavailable`, tell the user exact weekly 5-point tracking is not possible, and never substitute context usage, tool output, elapsed time, or an estimate as weekly usage. Use user-provided usage snapshots when supplied (`/status` or `/usage` are host-specific examples, not portable commands). A daily/session quota or explicit task token budget may be tracked separately with its own agreed gate; it must not be presented as weekly usage. Unavailable weekly telemetry alone does not block work under the other resource gates.

### Local command gates

- Start local builds in a monitored session with the command, target, start time, last progress time, and deadline recorded.
- Treat two minutes without observable progress as a stall warning. At five minutes total runtime or five minutes without progress, stop the build safely when it is interruptible, retain only the concise progress or failure summary, and ask whether to extend. Never silently extend the deadline.
- If a build is known to require more than five minutes, obtain a longer allowance before starting it. Each approved extension creates a new explicit deadline.
- Attempt the same build, test, device flow, or unchanged failing command at most twice. Ask before a third attempt. Treat inconsistent behavior after controlled reruns as `❌ FAIL` and label it flaky.
- Ask before expanding to more than 20 newly read files. Cap a single tool result at about 8,000 output tokens and switch to summaries, focused ranges, or failure snippets.
- During runtime/device execution, checkpoint after 10 cases or 15 minutes, whichever comes first. Keep raw logs out of the conversation and report only filtered evidence.

Waiting for a build does not justify streaming its full log. Poll at concise intervals, preserve no more evidence than needed, and remove temporary raw output during cleanup.

## Use the Pre-Test Confirmation Gate

Produce a numbered `測試前確認清單` before execution when any of these apply:

- The spec, design, confirmed decisions, and current code disagree.
- A UI detail, text, state, API field, mock response, environment, account, device, evidence rule, cleanup rule, or resource budget is ambiguous.
- Testing requires temporary files, mock servers, fake data, debug hooks, APK install/uninstall, device/network changes, login changes, or backend data mutation.
- A case cannot be tested safely without credentials, backend controls, device access, production-impacting behavior, or a resource-gate extension.

Ask the user to confirm these items before executing affected cases. Keep confirmed exclusions in `不納入範圍`. Use `⚠️ BLOCKED` only for execution barriers that remain after confirmation; do not hide unresolved product requirements as runtime blockers.

## Build the Test Model

Assign priorities by user and system impact:

- `P0`: build failure, crash, money/account/security impact, wrong request or business decision, data loss.
- `P1`: incorrect state, text, navigation, validation, error handling, lifecycle, retry, concurrency, or accessibility behavior.
- `P2`: minor visual consistency, non-critical logs, or low-impact cleanup.

Create only applicable coverage across `Build`, `Code`, `API`, `Logic`, `UI Text`, `UI Layout`, `State`, `Accessibility`, `Regression`, and `Test Support`.

For every test case, define a stable test ID, mapped requirement ID, priority, type, case-specific precondition, action/check, observable expected result, validation level, controlled support, cleanup reference, narrow Token/Log method, and status.

Map requirements and cases in both directions: every in-scope requirement must map to at least one case or a confirmed exclusion, and every case must map to an existing requirement. Do not freeze a plan without this accounting.

## Design Safe Test Support

- Define controllable support before execution for API errors, retry, timeout, cache, offline, empty/null data, encryption/public-key handling, edge cases, and destructive-risk flows.
- Prefer test source sets, debug-only variants, dependency injection, local mock servers, disposable fixtures, and non-production accounts.
- Keep support isolated from production behavior and name every file, dependency, package, backend record, and device setting that the run will create or change.
- Define cleanup and post-cleanup verification for every support or cleanup ID. Do not leave orphan references in the plan.

## Execute the Frozen Plan

1. Re-read the frozen ledger, plan, project instructions, confirmed premises, resource gates, and dirty-tree baseline. Verify the source fingerprint.
2. Run low-risk checks first, then the smallest safe module, variant, class, method, device flow, or request scope.
3. Add confirmed support only after the confirmation gate and record it in the cleanup ledger immediately.
4. Use runtime screenshots or device/browser interaction when the required evidence level is `Runtime/Device`.
5. Record each frozen case exactly once as `✅ PASS`, `❌ FAIL`, `⚠️ BLOCKED`, or `NOT_RUN`. Runtime, network, lifecycle, and state-transition behavior cannot pass from static inspection alone.
6. Redact credentials, tokens, cookies, personal data, account identifiers, and secrets.
7. Remove only current-run artifacts, restore device/network/login state, and compare the final state with the baseline.
8. Update the report after cleanup so it does not reference deleted evidence.

## Report Results

- Lead with a short conclusion and one compact result table.
- Preserve every frozen test ID. Count underlying cases, not grouped display rows.
- Use `通過率 = PASS / (PASS + FAIL)` and `N/A` when no case executed.
- Use `執行覆蓋 = (PASS + FAIL) / total frozen in-scope cases`; report `BLOCKED` and `NOT_RUN` separately.
- Include resource-gate events only when triggered. Keep raw logs, videos, and duplicate screenshots out of the body.
- Add `清理結果` only when support, temporary files, packages, backend data, device settings, screenshots, or raw logs changed.

## Validate Before Handoff

Resolve the script path from the Skill root and invoke it with Python 3 for both commands below. If unavailable, apply `VALIDATION_NOT_RUN` as defined above.

1. Run `python3 "<skill-root>/scripts/validate_test_plan.py" <plan> --kind plan --require-not-run` for a fresh plan.
2. Run `python3 "<skill-root>/scripts/validate_test_plan.py" <report> --kind report --plan <plan>` for an execution report.
3. Run the narrowest build or syntax checks for added test support within the resource gates.
4. Verify no temporary artifacts, secrets, stale evidence links, duplicate IDs, unmapped requirements, orphan support/cleanup references, unrelated changes, or unaccounted frozen cases remain.
5. Keep unresolved requirements in `Needs Confirmation`; never convert them into assumed PASS criteria.
