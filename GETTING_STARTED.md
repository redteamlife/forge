# Getting Started with FORGE

FORGE gives your AI coding assistant a structured contract to work from - defining which task to work on, what the boundaries are, when to stop, and how to commit. Instead of open-ended conversations, your AI follows a documented workflow you control.

## What You Need

- **An AI coding assistant** that can read files in your project directory. FORGE is designed for tools like [Claude Code](https://claude.ai/code) but works with any AI assistant that has file access (Codex, Cursor, GitHub Copilot Workspace, etc.).
- **A project directory.** Can be an existing project or a new one. Git is required for commit discipline, but you can set it up during the process.
- **This repository cloned locally**, or just the `templates/` and `ci/` directories copied somewhere accessible.

---

## Step 1: Copy `templates/` into your project

Copy the `templates/` folder from this repository into the root of your project:

```bash
cp -r /path/to/forge/templates /path/to/your-project/templates
```

Your project should now look something like:

```text
your-project/
├── templates/
│   ├── AI.template.md
│   ├── FORGE.template.md
│   ├── GENERATE_PROJECT_DOCS.md
│   └── ... (other templates)
└── (your existing code)
```

---

## Step 2: Generate your FORGE documents

Open your project in your AI coding assistant. Give the AI this prompt - replacing the last line with your actual project description:

> Read `templates/GENERATE_PROJECT_DOCS.md`, then generate FORGE documentation for the following project:
>
> [describe your project in 2–4 sentences]

The AI will read the templates and write a set of governance documents into `docs/forge/` in your project:

| File | Purpose |
| --- | --- |
| `AI.md` | Your execution configuration - mode, execution style, constraints |
| `FORGE.md` | The execution engine the AI follows on every session |
| `TASKS.yaml` | The list of tasks the AI will work through |
| `ARCHITECTURE.md` | System design constraints the AI must respect |
| `EVALUATION.md` | Definition of done and gate requirements |
| `MEMORY.md` | Patterns and lessons captured across sessions |
| `TEST_STRATEGY.md` | Testing expectations per mode |
| `REVIEW_GUIDE.md` | Review criteria for code and security |
| `ROADMAP.md` | Delivery phases and scope boundaries |
| `ARCHITECTURE_EXPLORATION.md` | Pre-decision trade-off analysis |

---

## Step 3: Review and tune the generated documents

### Check your mode

Open `docs/forge/AI.md` and look at the `FORGE-config` block at the top:

```text
FORGE_mode: Lightweight
execution_mode: manual
```

**If you are just starting out, use `Lightweight` mode.** It requires only three documents and has minimal overhead. You can always move up as your project matures.

| Mode | Use when |
| --- | --- |
| Lightweight | Learning FORGE, personal projects, low-risk changes |
| Mid | Most development work. Adds architecture alignment and security review |
| Strict | Security-sensitive systems, team projects with audit requirements |
| Full Discipline | Regulated environments, enterprise contexts |

### Check your tasks

Open `docs/forge/TASKS.yaml`. This is where your project work lives. Each task is one unit of work the AI will implement in a single session.

Good tasks are:
- **Specific** - "Add input validation to the login endpoint" not "improve security"
- **Bounded** - one thing, completable without touching unrelated code
- **Ordered** - sequenced so earlier tasks don't block later ones

Example of a well-written `TASKS.yaml`:

```yaml
tasks:
  - id: setup-db-schema
    description: Create the initial database schema with users and sessions tables using the ORM defined in ARCHITECTURE.md
    status: incomplete

  - id: add-user-registration
    description: Implement the POST /auth/register endpoint with email and password, hashing the password before storage
    status: incomplete

  - id: add-user-login
    description: Implement the POST /auth/login endpoint returning a JWT token on success
    status: incomplete

  - id: add-input-validation
    description: Add server-side input validation to all auth endpoints - reject malformed emails, enforce password minimum length
    status: incomplete

  - id: write-auth-tests
    description: Write unit tests for the registration and login logic covering success, duplicate email, and invalid credential cases
    status: incomplete
```

You can edit, add, or reorder tasks at any time. Tasks with `status: incomplete` are eligible for the AI to pick up.

---

## Step 4: Start a governed session

Give your AI coding assistant this prompt:

> Read `docs/forge/FORGE.md` and begin working.

That's it. The AI will:

1. Read your governance documents
2. Check `MEMORY.md` for relevant lessons from previous sessions
3. Pick the first incomplete task from `TASKS.yaml`
4. Check the task against your architecture constraints
5. Implement only that task - nothing more
6. Run a self-critique and security review
7. Update `TASKS.yaml` to mark the task complete
8. Commit with a structured message and stop

---

## The Daily Loop

In `manual` mode (the default), the AI completes one task per session and stops. This keeps you in control of each increment.

```
1. Open your project in your AI assistant
2. Say: Read docs/forge/FORGE.md and begin working.
3. AI picks next task → implements → critiques → commits → stops
4. Review the commit
5. Repeat
```

**Execution modes:**

| Mode | Behavior |
| --- | --- |
| `manual` | One task per session. You reinvoke each time. |
| `batch` | Up to `batch_size` tasks per session, then stops. |
| `auto` | Runs until all tasks are complete or a hard stop occurs. |

To change modes, update `execution_mode` in `docs/forge/AI.md`.

---

## When the AI Stops Without Finishing

FORGE uses **hard stops** - the AI halts and reports a blocking condition rather than guessing or drifting. Common reasons:

- A task description is ambiguous
- A required document is missing or inconsistent
- The task conflicts with documented architecture
- A security concern was identified

When this happens, the AI tells you exactly what blocked it. Resolve the issue - usually by clarifying a document or rewriting a task - then start a new session.

Hard stops are not failures. They are the governance model working correctly.

---

## Commit Format

FORGE commits follow [Conventional Commits](https://www.conventionalcommits.org) with FORGE metadata as git trailers:

```text
feat(auth): add JWT token validation

Implements token validation per ARCHITECTURE.md trust boundary constraints.

FORGE-mode: Lightweight
FORGE-task: add-user-login
FORGE-gate: pass
```

The AI generates this format automatically. You do not need to write it manually.

---

## Next Steps

Once you're comfortable with the basic loop:

- Read [Modes](philosophy/modes.md) to understand when to level up your governance
- Read [Maturity Model](philosophy/maturity-model.md) to understand the full progression
- Read [Execution Model](philosophy/execution-model.md) for the reasoning behind FORGE's design decisions
- When you're ready for pipeline enforcement (CI checks, commit hooks, branch protection), see [ci/README.md](ci/README.md)
