# Design v2: Workflow Stickiness (layered activation, mode-aware loop, moment routing)

Status: accepted after external review (v1 critique: fail pending revisions; all
blocking findings incorporated below). Implemented by TASK-012..017, target 1.9.0.

## Problem (unchanged from v1)

After `forge-bootstrap`, governed behavior decays: gates (critique,
security-review, evaluation, memory) never run unless explicitly requested, and
users must keep saying "use forge skills to ...". Root causes: the execution loop
does not close (execute-task never invokes the gates), agent surfaces route to
files not moments, alias descriptions trigger only on the word "FORGE",
`execution_mode` semantics are undefined, and memory handling drifted from
`philosophy/execution-model.md`.

## Architecture: stickiness as a layered system (from review)

```text
repo activation surface        (always in context; consented via config)
        v
single moment router           (intent -> one owning skill)
        v
mode-aware checkpoint loop     (gates run per profile; outcomes recorded)
        v
deterministic enforcement      (machine-readable gate state + helper script,
                                git hooks, CI; harness adapters optional)
```

## Decisions

### D1. Close the loop inside `forge-execute-task` — mode-aware

Checkpoint: select/claim -> memory read (index + relevant topic, before the
alignment check) -> implement -> checks -> **review gates via the `forge-review`
composite** (single owner of gate ordering; runs critique, then security review
when the change surface or `security_profile` requires it, then evaluation) ->
memory write when a reusable lesson exists -> update task state -> commit ->
stop or continue per `execution_mode`.

Mode/artifact awareness (v2 change — v1 would have hard-stopped Lightweight
repos, including this one):

- critique: always (needs no project files).
- security review: driven by change surface and `security_profile`, as the
  security-review skill already defines; `n/a` is a recorded outcome, not a skip.
- evaluation: full gate when `docs/forge/EVALUATION.md` exists; otherwise record
  the outcome in the task's `gates:` block only.
- memory: read/write only when memory docs exist; never a mandatory entry —
  `no relevant lesson` is a first-class outcome (prevents operational sludge).

Recorded outcome vocabulary (machine-readable, in the task file):

```yaml
gates:
  critique: pass | fail
  security: pass | n/a | escalated
  evaluation: pass | handoff-required | fail
  memory: entry | no-relevant-lesson | store-unavailable
```

### D2. Agent surfaces become moment->skill maps (routing corrected)

Generated router and narrative governance section carry:

- plan / break down / add or reshape work -> `forge-plan`
- implement / build / fix / continue -> `forge-build` (public route; delegates
  to the `forge-execute-task` primitive — one owner, resolving the v1
  double-ownership error)
- review / "is this done" -> `forge-review`
- commit current task -> `forge-execute-task` closeout (v1 wrongly sent commits
  to forge-ship)
- merge / release / promote / close out -> `forge-ship`
- record or recall lessons -> `forge-memory`

The activation line is emitted only when the repo consents via D6.

### D3. De-meta alias descriptions

Alias descriptions trigger on the user's words plus the repo signal
(`docs/forge/` present or FORGE named), not on the word "FORGE" alone.
`forge-build` owns implement/build/fix wording; `forge-execute-task`'s
description names it as the primitive that build routes to (collision-avoidance
between root, aliases, and primitives). Trigger evaluation: measured runs with
the existing Claude-oriented optimizer harness; other harnesses get manual
description review against their documented matching behavior (building a
cross-harness eval rig is out of scope).

### D4. Execution modes: define the vocabulary we already ship (v2 redesign)

v1's `manual | continuous` is dropped — the pack already ships
`execution_mode: auto` (org policy `auto_mode_permitted`) and bounded batch
(`batch_size`, modes philosophy). Semantics defined in a new
`references/execution-modes.md`:

- `manual` (default, all profiles): stop after each completed checkpoint.
- `batch`: continue up to `batch_size` checkpoints. Requires: task independence
  (no shared `file_scope`/`contract_files`), and a branch rule — solo-governed
  merges or hands off each task branch before starting the next unless
  `solo_branch_flow: direct`; team mode re-claims and reconciles per task.
- `auto`: batch without a fixed count; permitted only when org policy allows
  (`auto_mode_permitted`) and never with `requires_independent_review` tasks —
  those are an unconditional stop in every mode.

All modes: full gates per checkpoint (mode changes pacing and topology rules,
never rigor); stop on hard stops, ledger exhaustion, un-integrated dependents,
or claim conflicts. "Do not stop until done" is a per-run override interpreted
as `batch` with the run's stated bound, not a persistent config change.
Validator gains value checking for `execution_mode` (`manual|batch|auto`).

### D5. Deterministic enforcement core; adapters optional (v2 redesign)

- Machine-readable gate state: the `gates:` block (D1) in per-task files;
  templates document it; the task schema accepts it.
- New helper `assets/scripts/forge_next_gate.py`: reads `AI.md` + one task file,
  prints the next required gate (or `checkpoint-complete`) given the profile and
  recorded outcomes. Small models and non-skill harnesses get a deterministic
  conductor instead of probabilistic four-skill chaining.
- Git `pre-commit` remains the local enforcement layer and closes the v1 bypass:
  it now also warns on commits that touch `governed_paths` (D6) with no
  task-state change at all (warn, not block — code-only WIP commits are legal).
- Harness adapters are thin optional fragments invoking the same helper; ship
  the Claude Code one (`.claude/settings.json` PreToolUse example, verifiable
  today) and document the adapter pattern for Codex/Cursor/Qwen Code rather than
  shipping unverified fragments. CI stays the durable backstop.

### D6. Activation is consented config, not repo-presence (from review)

New FORGE-config fields:

```yaml
activation_mode: explicit | repo-default
# governed_paths: src/, services/payments/   # optional; monorepo scoping
```

- `explicit` (default for existing repos and migrations): surfaces route when
  asked; today's behavior, and the root skill's "never always-on" rule holds.
- `repo-default`: surfaces carry the activation line ("implementation work in
  this repo routes through FORGE skills, even when the request does not mention
  FORGE"), scoped to `governed_paths` when set.
- New bootstraps ask once (governed profiles recommend `repo-default`).
  Surface regeneration NEVER changes `activation_mode` — existing repos keep
  their behavior unless the human edits the config.
- Root skill rule amended to defer to `activation_mode` instead of a blanket
  "never always-on".

### D7. Hook-docs reconciliation (pre-existing contradiction, fixed first)

GETTING_STARTED.md and the 1.6.0 changelog say governed profiles install git
hooks automatically; bootstrap SKILL.md says "when the user wants local
enforcement". Resolution: governed profiles install hooks by default with an
explicit opt-out at bootstrap; docs aligned in both directions.

## Implementation plan

1. TASK-012: D7 hook-docs reconciliation (standalone quick fix).
2. TASK-013: D1 loop closure + memory drift fix + `gates:` block in templates/
   schema + execute-task budget management.
3. TASK-014: D4 `references/execution-modes.md` + validator value check + org
   policy/philosophy/README alignment.
4. TASK-015: D6 config + D2 surface generator/narrative rewrite + root-skill
   amendment + fixtures.
5. TASK-016: D3 description rewrites + collision review; optimizer eval runs
   recorded as evidence where run.
6. TASK-017: D5 `forge_next_gate.py` + pre-commit governed-paths warn + Claude
   adapter fragment + ci-setup/agent-flavors docs.

Scope includes (from review): root skill, `agent-flavors.md`, migration docs,
mode philosophy, org policy template, and verification fixtures. Checkpoint
context cost is measured (gate skills + evidence reads), not only surface size.

## Non-goals

- No always-on behavior without `activation_mode: repo-default` consent.
- No new subskills; no unverified harness fragments; no cross-harness eval rig.
