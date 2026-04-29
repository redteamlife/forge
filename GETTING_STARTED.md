# Getting Started with FORGE

FORGE is meant to be installed and used as a reusable skill pack rather than a template generator.

## Install

macOS / Linux:

```bash
bash install.sh
bash install.sh --agent claude --link
bash install.sh --agent codex --agent cursor --copy
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Agent claude,codex -Mode copy
```

Vercel skills CLI:

```bash
npx skills add https://github.com/redteamlife/forge.git
```

Compatibility note:

- Via `npx skills add`, FORGE is meant to work within Vercel's broader skills ecosystem, which Vercel documents as supporting 18+ agents including Claude Code, GitHub Copilot, Cursor, Cline, and many others.
- The manual install scripts in this repo provide explicit install targets for shared `~/.agents/skills`, Claude Code, Codex, Cursor, and Windsurf.

Optional:

- Set `FORGE_SKILL_TARGET` to install somewhere other than `~/.agents/skills`
- Use `--agent shared|claude|codex|cursor|windsurf` or `-Agent ...` to install to native agent paths
- Use `--link` / `-Mode link` to symlink instead of copying
- Use `--force` or `-Force` to replace an existing install
- Install scripts run verification automatically; `bash verify-install.sh --agent claude` is still available when you want a separate check
- Copy `skills/forge/assets/agent-surfaces/` into your repo if you want editor-specific onboarding files
- Treat `skills/forge/assets/agent-surfaces/` as the canonical source for reusable agent/editor surfaces

## Local Hooks

`solo-governed` and `team-full` bootstraps install the FORGE git hooks
automatically. To install or upgrade hooks on an existing repo, run from
the FORGE install directory against the target repo:

```bash
bash scripts/install-forge-hooks.sh
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-forge-hooks.ps1
```

The installer is idempotent and backs up any non-FORGE hook found at the
same path to `<name>.bak`. Solo-simple bootstraps leave hooks manual unless
you ask for them.

## First Use

FORGE now works best when you choose an explicit bootstrap profile up front:

1. `solo-simple`
2. `solo-governed`
3. `team-full`

Bootstrap also asks where tasks should be tracked:

- `local`: `docs/forge/TASKS.yaml`
- `github`: GitHub Issues, preferred when the repo has a GitHub remote and `gh` is authenticated
- `gitlab`: GitLab Issues, preferred when the repo has a GitLab remote and `glab` is authenticated
- `external`: Jira, Linear, or another tracker managed through MCP, CLI, or human workflow

FORGE may also record an optional `repo_flavor` hint, only when the repo shape changes generated docs:

- `contract-first`: shared OpenAPI, protobuf, schema, or generated-client files are part of the task boundary
- `tooling`: private/public tool release workflow

FORGE may also enable `application_docs: true` to generate a human-facing `docs/` tree (overview, architecture, threat model, developer guide, interfaces, deployment, runbook, ADRs) parallel to `docs/forge/`. Default is `false`.

FORGE may also record a `security_profile`:

- `baseline`: task-local checklist review
- `repo-fortress`: branch protection, CODEOWNERS, security policy, and risk visibility
- `ci-security`: repo-fortress plus SAST, secret scanning, dependency/SCA, and findings visibility
- `full-devsecops`: CI security plus CD pre-flight, DAST, SBOM, provenance, and cleanup evidence

### Solo-simple

Use this when you want the lightest useful FORGE loop:

1. Tell the agent what the project is.
2. Ask FORGE to bootstrap in `solo-simple`.
3. Review `docs/forge/AI.md` and `docs/forge/TASKS.yaml`.
4. Tell the agent to start working tasks.

Example:

```text
Use the forge skill to bootstrap this repo in solo-simple mode for a new project. This is a small internal utility and I am the only operator.
```

### Solo-governed

Use this when you are the only operator but still want branch discipline and human-controlled merges:

1. Ask FORGE to bootstrap in `solo-governed`.
2. Review `docs/forge/AI.md`, especially `solo_branch_flow: task-branches`, and make sure the protected `release_branch` is still the real release branch such as `main`.
3. Let the agent implement one task per task branch.
4. Review and merge yourself, or explicitly tell the agent when a merge is allowed.

Example:

```text
Use the forge skill to bootstrap this repo in solo-governed mode. I want one task branch per governed task, and the agent must never merge into main unless I say so explicitly.
```

### Team-full

Use this when multiple people or agents will share the repo and you want the full FORGE experience:

1. Ask FORGE to bootstrap in `team-full`.
2. Generate the full team-ready `docs/forge/` set.
3. Let FORGE ask whether it should also copy the repo agent-surface files and `ci/` scaffolding now, or leave those steps manual.
4. If you choose the automated path, let it copy those repo-local assets.
5. Configure branch protection and required checks.

Example:

```text
Use the forge skill to bootstrap this repo in team-full mode for a SaaS web app. We want repo agent surfaces, CI enforcement scaffolding, and team coordination from the start.
```

Expected follow-up:

- FORGE bootstraps the full team-ready docs first
- then it asks whether you want it to copy repo agent surfaces and CI scaffolding now, or leave those steps manual

If your editor surfaces installed skills as slash commands, the subskills are grouped under the `forge-` prefix, for example `/forge-bootstrap` and `/forge-execute-task`.

### Example: start working

After you review the generated docs, tell the agent:

```text
Use the forge skill to start working on tasks.
```

If you want the agent to keep going until it hits a real blocking decision:

```text
Use the forge skill to start working on tasks, do not stop until done.
```

FORGE should keep moving while preserving per-task checkpoints, commits, and hard stops.

## What To Review After Bootstrap

You do not need to read every generated file line by line before starting. Usually the highest-value review is:

- `docs/forge/AI.md` for project mode and team settings
- `docs/forge/TASKS.yaml` for whether the initial task list makes sense
- `docs/forge/ARCHITECTURE.md` if framework, deployment, or content choices are important early
- `docs/forge/TEAM.md` if multiple people or agents will be working in parallel

Once those look sane, you can start letting the skill drive task execution.

## How FORGE Behaves

In `solo-simple`:

- the agent should finish one task
- update `TASKS.yaml`
- create a Conventional Commit
- stop before moving to the next task unless you explicitly allow continued execution

In `solo-governed`:

- the agent should work from a task branch for each governed task
- the agent should not merge into `release_branch` unless you explicitly instruct it
- the human can review and merge, or explicitly tell the agent when to do so
- `docs/forge/SETUP.md` is useful when you want the branch and review handoff recorded

In `team-full`:

- task claims should be coordinated
- GitHub/GitLab repos should prefer issue assignment and labels as the coordination ledger
- feature work should stay on task branches
- integration should happen before release promotion
- CI and setup details should be tracked in `docs/forge/SETUP.md`
- contract files should be updated with the task that changes API, schema, generated client, or integration-boundary behavior
- enabled security scans, SBOM, DAST, and repository hardening controls should be recorded as setup evidence

FORGE is meant to feel like a trustworthy workflow layer, not a pile of ceremony.

## Full Team Setup

If you want the full team experience, ask FORGE to set up all repo-local pieces it can:

- the full team-ready `docs/forge/` set
- then an explicit follow-up choice about copying repo agent-surface files from `skills/forge/assets/agent-surfaces/`
- and an explicit follow-up choice about copying the `ci/` enforcement layer
- issue-backed task coordination when `task_source` is `github` or `gitlab`
- optional agent-specific surfaces such as `AGENTS.md`, `CLAUDE.md`, Cursor rules, Copilot instructions, Codex hooks, or Windsurf rules

Then finish the external platform steps yourself:

- branch protection
- required checks
- merge policy
- any provider-specific secrets or admin settings

## Agent Surfaces

Reusable agent/editor surfaces live in `skills/forge/assets/agent-surfaces/`.

- Copy from there into downstream repos when you want `AGENTS.md`, Copilot instructions, Codex hooks, Cursor rules, or Windsurf rules.
- Those surfaces are the repo-level reminder layer: they tell agents to use FORGE for governed work or stop and ask for installation if the skill is unavailable.
- Root `.github/workflows/` files in this repo are repository-specific and stay at the root.

## Updating Existing Projects

If a repo was already bootstrapped with an earlier version of FORGE, do not start over by default.

- Update only the affected `docs/forge/` files.
- Preserve project-specific content already written by the team.
- See [MIGRATION.md](./MIGRATION.md) for the coordination-branch migration path.
