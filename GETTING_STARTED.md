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

In a project that has no FORGE docs yet:

```text
Use the forge skill and bootstrap docs/forge for this project.
```

In a project that already has FORGE docs:

```text
Use the forge skill and execute the next bounded task from docs/forge.
```

## Recommended Starting Flow

1. Install the skill pack.
2. Start with `bootstrap` to create or refresh `docs/forge/`.
3. Review `docs/forge/AI.md` and `docs/forge/TASKS.yaml`.
4. Use `execute-task` for one bounded task at a time.
5. In solo mode, complete the task, update `docs/forge/TASKS.yaml`, create a Conventional Commit, and stop before starting the next task.
6. In team repos, set `collaboration_mode: team`, set `coordination_branch`, `integration_branch`, and `release_branch`, add `TEAM.md`, and enable CI enforcement.
7. Publish task claims on the coordination branch before implementation starts.
8. Merge feature branches into the integration branch before promoting to the release branch.
9. Delete merged feature branches after their integration PR is accepted unless project policy says otherwise.
10. If the repo is on GitHub or GitLab, document hook and CI setup in `docs/forge/SETUP.md`.
11. Use Conventional Commits for governed task work in both solo and team workflows.
12. Do not include AI attribution or tool-marketing lines in commit messages.
13. Keep generated docs and working responses terse unless the project explicitly needs more narrative detail.
14. If you later opt into batch or auto execution, preserve the same per-task checkpoint rule: finish, update state, commit, then continue.

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
