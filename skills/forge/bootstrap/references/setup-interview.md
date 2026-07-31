# Bootstrap Setup Interview

Present these choices to the user as menus — each option with a one-line
description and the recommended default marked `(default)`. Do not ask
open-ended questions; the user may not know what is available. Use the harness's
structured multiple-choice UI when it has one; otherwise render each as a short
labeled list and take the user's pick.

Detect first, then ask only what you could not infer or must confirm: language
and test runner (from repo files), a GitHub/GitLab remote (suggests
`task_source`), existing CI, and monorepo shape. Show detected values as the
proposed default.

Skip the interview only when the user supplied the configuration explicitly or
asked for sensible defaults. When skipping, state the defaults you applied.

## 1. Bootstrap profile

- `solo-simple` — one operator, smallest governance, direct commits.
- `solo-governed` (default) — one operator with task branches and
  human-controlled merges to the release branch.
- `team-full` — multiple developers/agents: claims, branch policy, reviewer
  routing, coordination docs.

## 2. Context profile

- `lite` (default) — no doc auto-loading; agents read `AI.md`, `CONTEXT.md`, the
  task index, and one task. Best for enterprise/API/CI/uncertain environments.
- `standard` — may auto-include `AI.md` only.
- `full` — may auto-include several docs; high-context, for local/dev sessions.

## 3. Task source

- `local` (default) — tasks live in `docs/forge/TASKS.index.yaml` + `tasks/`.
- `github` — GitHub Issues are authoritative (needs `gh`).
- `gitlab` — GitLab Issues are authoritative (needs `glab`).
- `external` — Jira/Linear/other via MCP, CLI, or human workflow.

## 4. Security profile

- `baseline` (default) — task-local checklist review.
- `repo-fortress` — branch protection, CODEOWNERS, SECURITY.md, Scorecard.
- `ci-security` — adds SAST, secret scanning, dependency/SCA scanning.
- `full-devsecops` — adds CD pre-flight, DAST, SBOM, provenance.

## 5. Activation mode

- `explicit` (default) — FORGE skills route when the user asks.
- `repo-default` — generated surfaces route all implementation work through
  FORGE even when the request does not mention it; optionally scope with
  `governed_paths` in monorepos. Recommended when you want the workflow to stay
  sticky without re-prompting.

## 6. Application docs

- `false` (default) — governance docs only.
- `true` — also generate a human-facing `docs/` handbook (overview,
  architecture, developer guide, and profile-appropriate additions).

## 7. Clean-main (governed profiles only)

- No (default) — governance files may live on the release branch.
- Yes — the release branch stays free of `docs/forge/`; promotion strips it via
  `forge-promote.sh`. Sets `integration_branch` and `dev_only_paths`. See
  `references/doc-minimums.md`.

## 8. Repo flavor (optional; only when it changes behavior)

- none (default).
- `contract-first` — OpenAPI/protobuf/GraphQL or other shared-interface files
  drive changes; scaffolds a contract surface.
- `tooling` — private-dev/public-release tool workflow.

## Confirm before generating

Echo the selected configuration back as the `FORGE-config` block that will be
written to `docs/forge/AI.md`, and confirm before generating docs. Hooks and
CI/team/cross-project setup still require explicit authorization.
