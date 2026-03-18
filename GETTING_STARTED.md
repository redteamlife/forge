# Getting Started with FORGE

FORGE gives your AI coding assistant a structured contract to work from - a task list, a rules file, and a required commit format. The AI reads the documents, does one task, commits, and stops. You stay in control of every increment.

**No CI pipeline, no hooks, no GitHub Actions required to get started.** The minimum setup is three files.

---

## Before You Begin

**What you need:**

- An AI assistant that can read files in your project (Claude Code, Codex, Cursor, GitHub Copilot Workspace, a local LLM, or similar)
- A project directory with git initialized (`git init` if starting fresh)
- This repository cloned locally, or just the `templates/` folder copied somewhere

**That's it.** No special tooling, no pipeline setup.

---

## Choose Your Starting Mode

Pick a mode before generating docs so you know what to expect. If you're unsure, start at Lightweight.

| Mode | What you get | When to use it |
| --- | --- | --- |
| **Lightweight** | 3 required files. Task tracking, commit discipline, hard stops. | Starting out, personal projects, low-risk work |
| **Mid** | 8 files. Adds architecture constraints, security checklists, evaluation gates. | Most development work |
| **Strict** | 11 files. Adds formal reviews, exploration docs, roadmap. | Team projects, audit requirements |
| **Full Discipline** | 12 files + org policy. Full deterministic workflow. | Regulated environments, enterprise |

> **Recommendation:** Start at Lightweight. You can switch modes at any time by updating `docs/forge/AI.md` and adding the documents for the new mode.

---

## Step 1: Copy the templates into your project

```bash
cp -r /path/to/forge/templates /path/to/your-project/templates
```

Your project should now look like:

```text
your-project/
├── templates/
│   ├── GENERATE_PROJECT_DOCS.md
│   ├── AI.template.md
│   ├── FORGE.template.md
│   └── ... (other templates)
└── (your existing code)
```

---

## Step 2: Generate your FORGE documents

Open your project in your AI assistant. Give it this prompt, replacing the last line with your actual project:

> Read `templates/GENERATE_PROJECT_DOCS.md`, then generate FORGE documentation in Lightweight mode for the following project:
>
> [describe your project in 2-4 sentences]

The AI will write your governance documents into `docs/forge/`.

### What gets generated

**Lightweight mode - the only three files that matter to start:**

| File | What it does |
| --- | --- |
| `docs/forge/AI.md` | Your configuration - mode, execution style, project constraints |
| `docs/forge/FORGE.md` | The rules file - the AI reads this before every session |
| `docs/forge/TASKS.yaml` | Your task list - the AI works through this one task at a time |

**Mid mode and above also generate:**

| File | What it does |
| --- | --- |
| `ARCHITECTURE.md` | System design constraints the AI must respect |
| `EVALUATION.md` | Definition of done and gate requirements |
| `MEMORY.md` | Patterns and lessons captured across sessions |
| `TEST_STRATEGY.md` | Testing expectations |
| `SECURITY_CHECKLISTS.md` | Task-type-specific security review checklists |
| `REVIEW_GUIDE.md` | Code and security review criteria |
| `ROADMAP.md` | Delivery phases and scope boundaries |
| `ARCHITECTURE_EXPLORATION.md` | Pre-decision trade-off analysis |

You can delete the `templates/` folder after generation if you want a cleaner project structure. You won't need it again unless you add new docs.

---

## Step 3: Review the generated documents

### Check AI.md

Open `docs/forge/AI.md`. At the top you'll see the config block:

```text
forge_version: 0.1.1
FORGE_mode: Lightweight
execution_mode: manual
```

Make sure `FORGE_mode` matches the mode you asked for. If the AI generated Mid but you wanted Lightweight, just change the value and delete the extra files.

`execution_mode: manual` means the AI does one task per session and stops. That's the right default to start.

### Check and edit TASKS.yaml

Open `docs/forge/TASKS.yaml`. This is where your work lives. The AI generated a first pass based on your project description - review it and adjust.

**Good tasks are specific and bounded.** One thing, completable without touching unrelated parts of the codebase.

Example of a well-written task list:

```yaml
tasks:
  - id: setup-db-schema
    description: Create the initial database schema with users and sessions tables using the ORM defined in ARCHITECTURE.md
    status: incomplete

  - id: add-user-registration
    description: Implement the POST /auth/register endpoint with email and password validation, hashing the password before storage
    status: incomplete

  - id: add-user-login
    description: Implement the POST /auth/login endpoint returning a JWT token on success
    status: incomplete

  - id: write-auth-tests
    description: Write unit tests for registration and login covering success, duplicate email, and invalid credential cases
    status: incomplete
```

Tasks with `status: incomplete` are eligible for the AI to pick up. You can add, edit, reorder, or delete tasks at any time.

---

## Step 4: Start a session

Tell your AI assistant:

> Read `docs/forge/FORGE.md` and begin working.

The AI will:

1. Read `FORGE.md` (the rules)
2. Read `AI.md` (the configuration)
3. Read `MEMORY.md` if present (lessons from past sessions)
4. Pick the first incomplete task from `TASKS.yaml`
5. Implement only that task
6. Review its own work and check for security concerns
7. Mark the task complete in `TASKS.yaml`
8. Commit with a structured message
9. Stop

---

## What a Session Produces

After a successful session you'll have a commit that looks like this:

```text
feat(auth): add JWT token validation

Implements token validation per trust boundary constraints.
Tokens are validated on every protected route before handler execution.

FORGE-mode: Lightweight
FORGE-task: add-user-login
FORGE-gate: pass
```

The `FORGE-mode`, `FORGE-task`, and `FORGE-gate` lines are git trailers - metadata attached to the commit. They make every task traceable: you can look at any commit and know exactly which task it corresponds to, what mode was active, and whether all gates passed.

The AI generates this format automatically. You do not write it manually.

---

## The Daily Loop

In `manual` mode, the AI completes one task per session and stops. This keeps you in control.

```text
1. Open your project in your AI assistant
2. Say: Read docs/forge/FORGE.md and begin working.
3. AI picks the next task, implements it, and commits
4. Review the commit
5. Repeat for the next task
```

When all tasks are done, add new tasks to `TASKS.yaml` and continue.

---

## When the AI Stops Without Finishing

FORGE uses **hard stops** - the AI halts and tells you exactly what blocked it rather than guessing or continuing past a problem. This is the governance model working correctly.

**Common reasons for a hard stop and how to fix them:**

| What the AI reports | What to do |
| --- | --- |
| Task description is ambiguous | Rewrite the task in `TASKS.yaml` to be more specific |
| Task scope conflicts with architecture | Update `ARCHITECTURE.md` or clarify the task boundary |
| A required document is missing | Generate the missing document or switch to a lower mode |
| Security concern identified | Review the concern, update the task or architecture doc, restart |
| No eligible tasks remain | Add new tasks to `TASKS.yaml` |

After fixing the issue, start a new session with the same prompt. The AI will pick up from the next eligible task.

---

## Switching Modes

To move from Lightweight to Mid (or any higher mode):

1. Open `docs/forge/AI.md` and change `FORGE_mode: Lightweight` to `FORGE_mode: Mid`
2. Tell your AI: *Read `templates/GENERATE_PROJECT_DOCS.md` and generate the Mid-mode documents that are currently missing from `docs/forge/`*
3. Review the new documents - especially `ARCHITECTURE.md`, which defines the constraints the AI will enforce

The AI will only generate the files that are missing. Existing files are left alone.

---

## Next Steps

Once you're comfortable with the basic loop:

- [Modes](philosophy/modes.md) - what each mode adds and when to level up
- [Maturity Model](philosophy/maturity-model.md) - the full progression from ad hoc prompting to full discipline
- [Execution Model](philosophy/execution-model.md) - the reasoning behind how FORGE works

---

## Optional: CI Pipeline Enforcement

The `ci/` directory in this repository contains scripts and a GitHub Actions workflow that validate FORGE outputs on every pull request - commit format, task completion, evidence artifacts, file scope, and doc completeness. These run independently of the AI and block merges on validation failure.

This is entirely optional. FORGE works without it. It becomes most useful when:

- You're working in a team and want machine-enforced consistency
- You're at Mid mode or above where missed review steps have real consequences
- You want commit format enforced before code reaches a shared branch

**To set up CI enforcement:**

1. Copy `ci/` into your project root

2. Install the commit hook:

   ```bash
   cp ci/hooks/commit-msg .git/hooks/commit-msg
   chmod +x .git/hooks/commit-msg
   ```

3. Copy the workflow to your GitHub Actions directory:

   ```bash
   mkdir -p .github/workflows
   cp ci/workflows/forge-governance.yml .github/workflows/
   ```

4. Set `ci_enforcement: enabled` in `docs/forge/AI.md`
5. Add `FORGE Governance Checks` as a required status check in your repository's branch protection settings

Full setup details are in [ci/README.md](ci/README.md).

---

## Building and Releasing Tools with FORGE

If you are using FORGE to develop a releasable tool — a CLI, web tool, or script — the tool development workflow gives you a structured way to keep internal planning and governance docs private while publishing clean artifacts publicly.

The workflow supports two visibility models:

- **Open source** — source code is published to a separate public repository
- **Closed source** — compiled binaries are published as GitHub Release assets; source never leaves the private dev repo

For open-source tools, FORGE now supports two publish strategies:

- **`preserve-history`** — recommended default; keeps public repo history intact so outside PRs can be merged normally
- **`snapshot-force-push`** — maintainer-only release mirror mode; replaces public `main` from the private release snapshot

Open-source scaffolds also include:

- `public_sync.required` — blocks publish if accepted public changes have not been imported
- `public_sync.last_imported_public_commit` — updated when you pull merged public work into private dev
- `sync_map` — defines how public paths map back into private repo paths during intake

**To scaffold a new tool project:**

```bash
# Linux / macOS
./scripts/forge-tool-init.sh ToolName

# Windows (PowerShell)
.\scripts\forge-tool-init.ps1 -ToolName ToolName
```

The script creates a `ToolName-dev/` directory with the full FORGE document set, a `forge.yaml` configuration file, a `release/` staging area, and helper scripts for both publishing and pulling accepted public PRs back into private development. It optionally creates both GitHub repositories and configures remotes.

**To publish a release:**

```bash
# Linux / macOS
./scripts/forge-publish.sh

# Windows (PowerShell)
.\scripts\forge-publish.ps1
```

For closed-source tools, pass a `--tag` / `-Tag` argument (e.g. `--tag v1.0.0`). Binaries are uploaded as GitHub Release assets via the `gh` CLI — nothing is committed to the public repo.

For open-source tools using the default `preserve-history` strategy, accepted public PRs can be imported into the private dev repo with:

```bash
./scripts/forge-sync-public.sh --pr 123
```

Or on Windows:

```powershell
.\scripts\forge-sync-public.ps1 -Pr 123
```

The full workflow reference is in `docs/forge/TOOL_WORKFLOW.md` inside each scaffolded project, and the `forge.yaml` configuration schema is in `templates/forge.yaml.template`.
