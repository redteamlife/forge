# FORGE Execution Engine

This document is the execution authority. If any instruction conflicts with this document, this document governs.

FORGE documents are co-located under `docs/forge/` in the project root unless explicitly overridden by project policy.

---

## Invariants

These rules apply unconditionally at every moment of execution, regardless of step, mode, or context. Check all invariants before starting and verify you are not violating any of them before each action.

**I1 - Branch:** Never execute on `main` or a detached HEAD unless project policy explicitly permits detached HEAD.

**I2 - Required documents:** Never proceed without all documents required by the active mode present and consistent.

**I3 - One task:** Never implement more than the single selected task per invocation. Never begin a second task before all gates for the current task are satisfied and committed.

**I4 - File scope:** Never modify files outside the task's declared `file_scope`. If no `file_scope` is declared, limit changes to what the task explicitly requires.

**I5 - Commit discipline:** Never commit without passing critique, security review, and evaluation gate. Never commit without the required FORGE trailers. Never bundle unrelated task work in a single commit.

**I6 - Hard stops are unconditional:** When a hard stop condition is met, stop immediately. Do not attempt to work around it. Record the blocking condition and escalate.

If you cannot verify that all invariants are satisfied, stop and escalate before proceeding.

---

## 1. Definitions

- `FORGE_mode`: governance level declared in `AI.md` - `Lightweight` | `Mid` | `Strict` | `Full Discipline`
- `execution_mode`: `manual` | `batch` | `auto`
- `batch_size`: positive integer; required when `execution_mode: batch`
- `eligible task`: a task with `status: incomplete` and sufficient documentation to execute

## 2. Configuration and Mode Detection

Parse the `FORGE-config` block in `AI.md`. Extract and validate:

- `forge_version` - records which version of the FORGE framework this project uses; informational, no hard validation required
- `FORGE_mode` - must be one of the four valid values
- `execution_mode` - must be `manual`, `batch`, or `auto`
- `batch_size` - must be a positive integer if `execution_mode: batch`

Execution behavior:

- `manual`: one task per invocation
- `batch`: up to `batch_size` tasks sequentially per invocation
- `auto`: iterates without reinvocation until no eligible tasks remain or a hard stop occurs

## 3. Branch Discipline

Execution must not proceed on `main` or detached HEAD unless project policy explicitly permits detached HEAD.

If branch validation fails, hard stop before task selection.

## 4. Required Document Validation

Validate document **presence** before task selection. Defer reading document **content** until the workflow step that first requires it.

**All modes:** `AI.md`, `FORGE.md`, `TASKS.yaml`

**Mid and above:** `ARCHITECTURE.md`, `TEST_STRATEGY.md`, `EVALUATION.md`, `MEMORY.md`, `SECURITY_CHECKLISTS.md`

**Strict and above:** `ARCHITECTURE_EXPLORATION.md`, `REVIEW_GUIDE.md`, `ROADMAP.md`

**Full Discipline:** All Strict documents required and current.

If any required document is missing or documents are materially inconsistent, hard stop and escalate.

## 5. Task Selection

Parse `TASKS.yaml`. Eligible tasks must have a non-empty `id`, non-empty `description`, and `status: incomplete`.

`acceptance_criteria` and `scope_boundary` do not affect eligibility in Lightweight or Mid mode. In Strict mode they are encouraged. In Full Discipline mode they are required for eligibility.

`file_scope` declares which directories or files a task is allowed to modify. It is optional but encouraged in Mid+ and required in Full Discipline. When declared, it is enforced by the CI pipeline via `validate-file-scope.sh`. The implementing agent must not modify files outside declared `file_scope`.

Select tasks in file order unless project policy defines a deterministic alternative. If no eligible tasks exist, stop with `no_remaining_tasks`.

## 6. Execution Mode Behavior

**Manual:** Select one eligible task. Require reinvocation for any additional task.

**Batch:** Select up to `batch_size` eligible tasks. Execute sequentially. Apply full per-task workflow. Stop immediately on any hard stop.

**Auto** _(Strict+)_**:** Enforce single-task bounded execution internally. Iterate without reinvocation only while all gates pass. Stop immediately on any failed gate, escalation, or policy conflict.

## 7. Single-Task Implementation Workflow

### Step 7.0 - Memory Query

If `MEMORY.md` is present, read it now. Search for patterns, failures, or lessons relevant to the active task's component, domain, or change type. Note how any relevant entries inform approach or constraints. Skip if `MEMORY.md` is absent and not required by the active mode.

This step applies at all modes whenever `MEMORY.md` exists.

### Step 7.1 - Pre-Implementation Alignment Check

- Confirm task scope is consistent with `AI.md`
- Confirm architectural alignment with `ARCHITECTURE.md` _(Mid+)_
- If architectural uncertainty exists and mode requires exploration, record in `ARCHITECTURE_EXPLORATION.md` _(Strict+)_
- If misaligned, hard stop and escalate

### Step 7.2 - Implement Only the Selected Task

Limit changes to what the active task requires. Do not include unrelated work. Do not begin a second task before all gates for the current task are satisfied.

If the task declares `file_scope`, do not modify any files outside the listed paths. The CI pipeline will reject commits that violate declared scope.

### Step 7.3 - Update Task-Related Documentation

Record required architectural or test strategy changes. Preserve deterministic structure and formatting.

## 8. Critique Pass

Perform a self-critique before any completion decision.

- Was task scope exceeded?
- Are assumptions documented?
- Are edge cases or failure modes unaddressed?
- Does the change conflict with architecture or constraints?
- Is documentation updated where required?

Resolve blocking issues within task bounds or escalate. Do not proceed with known unresolved blockers.

## 9. Security Review Pass

Perform a security-focused review using `SECURITY_CHECKLISTS.md`. Select the checklist matching the task's `task_type` field and apply it alongside the General checklist. If no `task_type` is declared, apply the General checklist only.

Every checklist item must receive an explicit outcome (`pass`, `n/a`, or an escalation note). Free-form narrative does not satisfy the security review. Record completed checklist results in `EVALUATION.md`.

Core areas the checklists cover:

- Trust boundary impact
- Sensitive data handling
- New permissions, access paths, or privileged behaviors
- Input validation and output filtering
- Integration and dependency risks

If any checklist item raises an unresolved concern, hard stop and escalate before proceeding to the evaluation gate.

## 10. Evaluation Gate

Read `EVALUATION.md` and `TEST_STRATEGY.md` now _(Mid+)_. Apply their requirements before completion.

- Definition of Done satisfied for the task
- Required tests or validations completed per active mode
- Required review evidence recorded
- Release-readiness checks completed where applicable

If gate fails: keep task `incomplete`, record failure reason, stop or continue per `execution_mode` hard stop rules.

## 11. Memory Update

Update `MEMORY.md` after each task attempt.

**On success:** record useful patterns, risks avoided, review or testing lessons.

**On failure or escalation:** record failure mode, guardrail or documentation gap, recommended refinement.

Updates must be concise, factual, and attributable to the task.

## 12. Commit-Per-Task Enforcement

Commit preconditions: critique pass, security review pass, evaluation gate pass, `TASKS.yaml` status updated, required documentation and memory updates recorded.

Commits must follow [Conventional Commits](https://www.conventionalcommits.org) format with FORGE metadata recorded as git trailers in the commit footer.

Subject line format:

```text
<type>[optional scope]: <description>
```

Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `build`, `ci`, `perf`, `revert`

Required trailers:

```text
FORGE-mode: <Lightweight|Mid|Strict|Full Discipline>
FORGE-task: <task-id>
FORGE-gate: pass
```

Full example:

```text
feat(auth): add JWT token validation

Implements token validation per ARCHITECTURE.md trust boundary constraints.

FORGE-mode: Mid
FORGE-task: AUTH-003
FORGE-gate: pass
```

- `FORGE-mode` must match `FORGE_mode` declared in `AI.md`
- `FORGE-task` must match the task `id` in `TASKS.yaml`
- `FORGE-gate` records the evaluation gate outcome
- Trailers must appear in the commit footer, separated from the body by a blank line
- Do not add any trailers beyond the three above - no `Co-authored-by`, no `Signed-off-by`, no AI attribution, no tool-generated footers of any kind

If multiple tasks are combined in one commit, unrelated files are included, or any unauthorized trailers are present, hard stop and correct before proceeding.

## 13. Task Status

Mark `complete` only after evaluation gate pass and commit. Keep `incomplete` on any gate failure or escalation. Record blocking information per mode requirements.

## 14. Hard Stop Rules

Stop immediately when any of the following occurs:

- Running on `main`
- Invalid or missing `FORGE-config` values
- Missing required documents for active mode
- Material inconsistency across required documents
- Task ambiguity prevents bounded implementation
- Architecture misalignment without approved resolution
- Failed security review with unresolved concerns
- Failed evaluation gate without approved remediation path
- Commit policy cannot be satisfied
- Any policy or organizational constraint conflict

Record the blocking reason. Do not continue to another task. Escalate per project policy.

## 15. Escalation Rules

Escalate when execution cannot proceed safely or deterministically.

Triggers: scope ambiguity or conflicting requirements, missing approvals or policy decisions, security or compliance uncertainty, architecture change beyond task authority, batch coupling that invalidates independent execution, repeated failure pattern indicating guardrail weakness.

Record: task id, blocking condition, impacted documents or systems, recommended resolution path, whether execution stopped before or after implementation attempt.

## 16. Completion Condition

- `manual`: one task completes the full workflow and is committed, or a hard stop occurs
- `batch`: each selected task completes and is committed, or execution stops on the first hard stop
- `auto`: no eligible tasks remain, or execution stops on the first hard stop or escalation

No task is complete until all required gates pass and commit-per-task enforcement is satisfied.

## 17. Pipeline Enforcement

When `ci_enforcement: enabled` is declared in `AI.md`, external pipeline checks validate workflow outputs independently of agent behavior. These checks run on every pull request and cannot be bypassed without disabling branch protection.

Pipeline checks validate:

- Commit message format - every non-merge commit must follow Conventional Commits with `FORGE-mode`, `FORGE-task`, and `FORGE-gate` trailers
- Task state - every task ID referenced in a commit must have `status: complete` in `TASKS.yaml`
- Evidence artifacts - `EVALUATION.md` and `MEMORY.md` must be modified in the same PR

Pipeline enforcement does not replace agent workflow steps. It validates their outputs. A commit that passes agent workflow but fails a pipeline check is not mergeable.

CI gate outcomes in the pipeline run log constitute valid evaluation evidence. The run ID and result may be recorded in `EVALUATION.md` as evidence of gate completion.

Setup instructions are in `ci/README.md` in the FORGE repository.
