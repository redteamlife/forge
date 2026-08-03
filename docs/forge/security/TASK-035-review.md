# Security Review: minimum-cadence output + required-read loading (TASK-035)

Required because an output-policy change could accidentally suppress a security
blocker.

## Change surface

Wording/loading only: the minimum-cadence rule in `checkpoint-output.md`, the
execute-task required-read step + inline fallback, the surface generator, and six
static surfaces. No executable behavior beyond the generator emitting an extra
instruction line. No network, credentials, or repository-control change.

## Findings

- **Blockers are explicitly preserved, not suppressed.** Every layer names
  blockers/escalations as REQUIRED output: the protocol's per-checkpoint stopped
  states, the execute-task fallback ("blockers state check+evidence+need"), and
  the surface line ("emit … blockers …"). The compact rule silences routine
  *narration*, never a blocker, gate failure, `escalated`, or `handoff-required`.
- **Gate/stop logic unchanged.** execute-task's Hard Stops and the `gates:`
  recording are untouched; a failed security gate still stops the loop
  regardless of `progress_policy`.
- **`detailed` cannot weaken security either** — it only adds narration.
- **Generator adds a fixed instruction line**, no project-controlled text
  evaluated; no injection surface.

## Residual risk

None material. Verbosity is not a security control; no gate, review, or stop can
be skipped by any `progress_policy` value.

## Outcome

security: pass.
