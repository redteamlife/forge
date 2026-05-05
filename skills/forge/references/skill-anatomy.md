# FORGE Skill Anatomy

Use this reference when creating or revising FORGE skills.

FORGE skills should be compact workflows with activation rules, stop
conditions, rationalization guards, and evidence exits. Avoid long essays that
agents can admire and then ignore.

## Standard Sections

Use these sections for operational skills when they fit the skill's scope:

- `Use When`: explicit triggers.
- `Do Not Use When`: boundaries and better routes.
- `Required Inputs`: minimal files, commands, or context to read.
- `Workflow`: ordered actions.
- `Hard Stops`: conditions that block forward motion.
- `Rationalizations To Reject`: common excuses agents must not use.
- `Evidence Required`: artifacts or checks that prove completion.
- `Output Shape`: concise response format.

Small routing skills may omit sections that add no value, but core operational
skills should include hard stops, evidence, and rationalization guards.

## Trigger Rules

Good triggers are concrete:

- user explicitly names the skill or lifecycle phase
- project-local config declares the workflow
- a task's type, files, or metadata require the workflow

Avoid vague triggers such as "when helpful" or "when appropriate" unless they
are paired with examples and non-examples.

## Workflow Rules

Workflows should:

- start from the authoritative project state
- read only the docs needed for the current step
- preserve one-task checkpoints
- prefer structured files over chat-only state
- name when to stop instead of improvising around missing data
- end with evidence, not confidence

## Rationalization Guards

Agents often skip governance by sounding reasonable. Capture the common excuses
and the required FORGE response.

Example:

| Rationalization | FORGE response |
|---|---|
| "This is too small for a task." | Small tasks still need bounded scope and commit hygiene. |
| "I will update docs later." | Triggered docs update in the same change set. |
| "CI passed, so review is done." | CI is evidence, not critique or evaluation. |

Keep tables short. Prefer the few excuses that actually cause drift.

## Evidence Rules

Evidence must be observable:

- changed files
- test, build, lint, or validation commands
- task-state transitions
- issue, PR, or MR links
- `EVALUATION.md` entries
- contract docs, XPDs, ADRs, or application docs
- explicit human approval when required

Do not accept "looks good" as evidence.

## Output Rules

Output should be small and decision-oriented:

- gate result first
- changed artifacts second
- blockers as facts plus the decision needed
- no duplicated file contents unless the user asked

Use the main FORGE token-discipline rules unless a skill explicitly needs a
different response shape.
