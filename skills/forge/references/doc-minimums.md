# FORGE Doc Minimums

This reference trims the original FORGE documentation model down to the smallest set that still works well with skills.

## Lightweight Skill-Based Default

Required:

- `docs/forge/AI.md`
- `docs/forge/TASKS.yaml`

Recommended:

- `docs/forge/ARCHITECTURE.md` when architecture constraints matter
- `docs/forge/EVALUATION.md` when explicit gates matter
- `docs/forge/MEMORY.md` when tasks recur across sessions
- `docs/forge/TEAM.md` when more than one developer or agent may execute in the same repo
- `docs/forge/SECURITY_CHECKLISTS.md` when security review should be checklist-driven
- `docs/forge/SETUP.md` when enforcement setup needs to be handed off clearly to humans

Optional:

- `docs/forge/REVIEW_GUIDE.md`
- `docs/forge/ROADMAP.md`
- `docs/forge/ARCHITECTURE_EXPLORATION.md`

## Rule Of Thumb

Only keep a repo-local file if:

- it contains project-specific facts
- it needs to be updated over time
- another tool or CI check will read it

If the content is stable FORGE procedure, it belongs in the skill pack instead.

Token rule of thumb:

- keep repo-local docs factual and compact
- avoid writing long narrative guidance into project docs when short structured fields will do

## Multi-Developer Team Mode

When a project is shared by multiple developers, multiple IDE agents, or both, treat this as the minimum practical set:

- `docs/forge/AI.md`
- `docs/forge/TASKS.yaml`
- `docs/forge/TEAM.md`
- `docs/forge/ARCHITECTURE.md`
- `docs/forge/EVALUATION.md`
- `docs/forge/MEMORY.md`
- `docs/forge/SECURITY_CHECKLISTS.md`
- `docs/forge/SETUP.md`

Additional expectations:

- `ci_enforcement` should be enabled
- task `file_scope` should be required for any task that will be implemented by an agent
- task claims should be recorded before code changes begin
