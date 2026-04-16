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
- Run `bash verify-install.sh --agent claude` after install
- Copy `skills/forge/assets/agent-surfaces/` into your repo if you want editor-specific onboarding files
- Treat `skills/forge/assets/agent-surfaces/` as the canonical source for reusable agent/editor surfaces

## First Use

Most people will use FORGE in a very simple loop:

1. Tell the agent what the project is.
2. Let FORGE bootstrap `docs/forge/`.
3. Review the generated docs.
4. Tell the agent to start working tasks.
5. Step in only when FORGE surfaces a real blocker or decision.

### Example: bootstrap a new project

```text
Use the forge skill to bootstrap this repo for a new project. This project is for an interactive web site that will be the main hub for RedTeam.Life information. We will have a team of people and agents working on it.
```

If your editor surfaces installed skills as slash commands, the subskills are grouped under the `forge-` prefix, for example `/forge-bootstrap` and `/forge-execute-task`.

That should generate a lean but team-ready `docs/forge/` set.

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

In solo mode:

- the agent should finish one task
- update `TASKS.yaml`
- create a Conventional Commit
- stop before moving to the next task unless you explicitly allow continued execution

In team mode:

- task claims should be coordinated
- feature work should stay on task branches
- integration should happen before release promotion
- CI and setup details should be tracked in `docs/forge/SETUP.md`

FORGE is meant to feel like a trustworthy workflow layer, not a pile of ceremony.

## Optional Enforcement

If you want CI and hook enforcement, copy the `ci/` layer into the target repo and follow [ci/README.md](./ci/README.md).

## Agent Surfaces

Reusable agent/editor surfaces live in `skills/forge/assets/agent-surfaces/`.

- Copy from there into downstream repos when you want `AGENTS.md`, Copilot instructions, Codex hooks, Cursor rules, or Windsurf rules.
- Root `.github/workflows/` files in this repo are repository-specific and stay at the root.

## Updating Existing Projects

If a repo was already bootstrapped with an earlier version of FORGE, do not start over by default.

- Update only the affected `docs/forge/` files.
- Preserve project-specific content already written by the team.
- See [MIGRATION.md](./MIGRATION.md) for the coordination-branch migration path.
