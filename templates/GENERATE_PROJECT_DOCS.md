# FORGE Documentation Generator

You are generating a new FORGE project documentation set.

This instruction file is intentionally located in `./templates/` so teams can copy a single folder into a new repository, generate docs, and optionally remove `./templates/` afterward.

This repository contains canonical documentation templates in:

./templates/

These templates define the required structure, sections, formatting, and governance model for FORGE projects.

Your job is to:

- Read all template files (`*.template.md`, `*.template.yaml`) in `./templates/`
- Preserve their structure exactly
- Replace placeholder content with project-specific content
- Output completed files into ./docs/forge/
- Do not generate application code
- Do not modify files inside ./templates/

---

## Authoritative Template Source

All schema definitions live in:

./templates/

You must:

- Preserve all headings exactly
- Preserve section ordering
- Preserve required configuration blocks
- Preserve file naming (remove ".template" suffix)
- Not remove required sections
- Not add new structural sections unless absolutely required

If a section does not apply, explain why it does not apply.
Do not delete it.

---

## Output Location

Write completed documentation files to:

./docs/forge/

Create this directory if it does not already exist.

Use the same filename as the template, but remove ".template" from the name.

Example:

AI.template.md → ./docs/forge/AI.md
TASKS.template.yaml → ./docs/forge/TASKS.yaml

Do not overwrite template files.

---

## Required Files

You must generate all template files:

- AI.md
- FORGE.md
- ROADMAP.md
- TASKS.yaml
- ARCHITECTURE_EXPLORATION.md
- ARCHITECTURE.md
- REVIEW_GUIDE.md
- TEST_STRATEGY.md
- EVALUATION.md
- MEMORY.md
- SECURITY_CHECKLISTS.md

If FORGE mode is Lightweight, architectural documents may remain minimal but must still exist.

### Optional: TOOL_WORKFLOW.md

If a `forge.yaml` file is present in the project root, this project is using the FORGE tool development workflow. In that case, also generate `TOOL_WORKFLOW.md` from `TOOL_WORKFLOW.template.md`. Replace the `[DEV_REPO]` and `[PUBLIC_REPO]` placeholders with the values from `forge.yaml` under `repos.dev` and `repos.public`. If `forge.yaml` is not present, omit this file.

---

## FORGE Configuration Block

In AI.md, you must include a valid configuration block:

```FORGE-config
forge_version: 0.1.1
FORGE_mode: <Lightweight | Mid | Strict | Full Discipline>
execution_mode: <manual | batch | auto>
batch_size: <integer if execution_mode = batch>
```

Rules:

- Default execution_mode = manual unless specified.
- batch_size required only if execution_mode = batch.

Do not alter block format.

---

## TASKS.yaml Requirements

TASKS.yaml must:

- Contain actionable, atomic tasks
- Avoid vague descriptions
- Avoid large, compound tasks
- Follow strict YAML formatting
- Use status: incomplete for all initial tasks
- Include `acceptance_criteria` and `scope_boundary` per task when FORGE_mode is Strict or Full Discipline
- Include `task_type` per task when FORGE_mode is Mid or above (selects the appropriate security checklist)
- Include `file_scope` per task when FORGE_mode is Mid or above; required for Full Discipline
- Include `complexity` per task when task risk warrants it

No placeholder tasks.

---

## Mode-Scoped FORGE.md Generation

When generating FORGE.md, produce only the content applicable to the declared FORGE_mode. Do not include rules, sections, or requirements for modes above the declared level. This reduces agent token cost at runtime.

- Sections and bullets marked _(Mid+)_ must be omitted from Lightweight output.
- Sections and bullets marked _(Strict+)_ must be omitted from Lightweight and Mid output.
- Auto mode content must be omitted from Lightweight output. For Mid output, include auto execution behavior only when `execution_mode: auto` is declared; omit it when `execution_mode` is `manual` or `batch`.

The hard stop rules, escalation rules, commit format, branch discipline, and completion conditions apply at all modes and must always be included.

---

## Architecture Expectations

If FORGE_mode is:

Lightweight:

- ARCHITECTURE.md may be minimal
- ARCHITECTURE_EXPLORATION.md may summarize trade-offs briefly

Mid:

- ARCHITECTURE.md required
- ARCHITECTURE_EXPLORATION.md required

Strict:

- Full architectural analysis required
- Explicit trust boundaries required

Full Discipline:

- Multi-layer architecture assumed
- Deployment considerations required
- Evaluation gates strict

You must align documentation depth with declared FORGE_mode.

---

## Constraints

You must NOT:

- Generate source code
- Generate Docker files
- Generate example implementations
- Modify templates
- Invent new template files
- Skip required sections
- Introduce marketing language
- Add emojis
- Produce hype language

Professional engineering tone only.

---

## CI Enforcement Setup (Optional)

After generating documentation, pipeline enforcement can be enabled to validate FORGE workflow outputs externally.

To enable:

1. Copy `ci/` from the FORGE repository into the project root.
2. Install the commit hook:

   ```bash
   cp ci/hooks/commit-msg .git/hooks/commit-msg && chmod +x .git/hooks/commit-msg
   ```

3. Copy the workflow:

   ```bash
   cp ci/workflows/forge-governance.yml .github/workflows/forge-governance.yml
   ```

4. Set `ci_enforcement: enabled` in `docs/forge/AI.md`.
5. Add `FORGE Governance Checks` as a required status check in branch protection settings.

Refer to `ci/README.md` for full setup instructions and org-level policy configuration.

CI enforcement is independent of FORGE mode. It can be enabled at any mode but is most impactful at Mid and above where evidence artifact requirements apply.

---

## Input Idea

The user will provide a project idea below.

You must transform that idea into a full FORGE documentation set using the templates.

---

## Begin

Read all template files in `./templates/` completely before generating any output.

Then generate all completed documentation files into ./docs/forge/
