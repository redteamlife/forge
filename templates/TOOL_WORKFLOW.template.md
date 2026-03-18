# Tool Development Workflow

This document defines the development and release workflow for this project. It supplements the standard FORGE governance documents with the dual-repo model, release procedures, and contribution back-merge policy specific to tool development.

---

## Dual-Repo Model

This project uses two repositories:

| Repository | Visibility | Contains |
| --- | --- | --- |
| `[DEV_REPO]` | Private | FORGE governance docs, source code, architecture, planning artifacts |
| `[PUBLIC_REPO]` | Public | Published source (open-source) or release assets (closed-source) |

All governed development work occurs in the private dev repo. For open-source tools using history-preserving publish, the public repo is also a normal collaboration surface where outside contributors can open pull requests.

---

## forge.yaml

The project root contains a `forge.yaml` file that configures the release tooling. Key fields:

- `project` — tool name
- `visibility` — `open-source` or `closed-source`
- `publish_strategy` — `preserve-history` or `snapshot-force-push` (open-source only)
- `public_sync.required` — blocks publish when merged public changes have not been imported into private dev
- `public_sync.last_imported_public_commit` — last merged public commit intentionally imported into private dev
- `sync_map` — maps public repo paths back into private repo paths during public PR intake
- `src_dir` — source directory (open-source: copied to release)
- `release_dir` — staging directory populated before publishing
- `build_output` — compiled binary paths (closed-source only)
- `repos.dev` — private dev repo name
- `repos.public` — public release repo name

Do not add release configuration to `docs/forge/AI.md`. That file governs AI execution only.

---

## Development Workflow

All development, planning, and AI-assisted work occurs inside the private dev repo following standard FORGE governance:

1. Work on a feature branch, never on `main`.
2. AI agent selects tasks from `docs/forge/TASKS.yaml` per `FORGE.md`.
3. All gates (critique, security review, evaluation) must pass before commit.
4. Commits follow Conventional Commits format with FORGE trailers.
5. `docs/forge/MEMORY.md` is updated after each task.

The public repo is not touched during development.

The exception is public contribution intake: merged public PRs are imported back into the private dev repo through the sync workflow described below.

---

## Release Workflow

Publishing is performed from the private dev repo using the provided scripts.

### Prerequisites

- `forge.yaml` is present and fully populated at the project root.
- For closed-source: binaries listed in `build_output` have been compiled and exist at their declared paths.
- For open-source and closed-source GitHub Release creation: the `gh` CLI is installed and authenticated.
- A git remote named `public` is configured pointing to the public repository.

### Open Source Release

Run from the project root:

```bash
./scripts/forge-publish.sh
```

Or on Windows:

```powershell
.\scripts\forge-publish.ps1
```

What happens:

1. Script validates `forge.yaml`.
2. Source artifacts from `src_dir` are copied to `release_dir`.
3. Publish behavior follows `publish_strategy`.

If `publish_strategy: preserve-history`:

1. The script fetches the public repo's `main`.
2. The release content is applied on top of existing public history.
3. A normal commit is created only if the published tree changed.
4. The update is pushed normally to public `main`.

If `publish_strategy: snapshot-force-push`:

1. A fresh release-only repository is created from `release_dir`.
2. Public `main` is replaced from that release snapshot.

In both cases, the public repo receives only the contents of `release_dir`. FORGE governance documents, architecture notes, and internal planning artifacts are never included.

### Closed Source Release

Run from the project root:

```bash
./scripts/forge-publish.sh
```

Or on Windows:

```powershell
.\scripts\forge-publish.ps1
```

What happens:

1. Script validates `forge.yaml` and verifies each `build_output` path exists.
2. A GitHub Release is created on the **public** repo via `gh release create <tag>`.
3. Each binary listed in `build_output` is uploaded as a release asset via `gh release upload`.
4. Source code is never pushed to the public repo.

The release tag is taken from a `--tag` argument or prompted interactively if not provided.

---

## Public Contribution Intake (Open Source Only)

External contributors submit pull requests to the public repo. After review and merge, changes must be brought back into the dev repo.

### Procedure

1. Ensure the `public` remote is configured in the dev repo:

   ```bash
   git remote -v
   # public  https://github.com/[ORG]/[PUBLIC_REPO].git (fetch)
   ```

2. Import the accepted pull request from the private dev repo:

   ```bash
   ./scripts/forge-sync-public.sh --pr 123
   ```

   Or on Windows:

   ```powershell
   .\scripts\forge-sync-public.ps1 -Pr 123
   ```

3. The sync script fetches `public`, verifies that the PR is merged, resolves the merge commit, maps changed public paths through `sync_map`, and applies the imported change into the current private dev branch.

4. The script also appends an intake task stub to `docs/forge/TASKS.yaml` when that file exists and updates `public_sync.last_imported_public_commit` in `forge.yaml`.

5. Review, test, and complete the intake task like any other governed change. If the imported change affects architecture or security posture, update the corresponding docs before the next publish.

### Eligibility Policy

Only changes that were reviewed and merged via the public repo's pull request workflow are eligible for back-merge. Do not directly cherry-pick or manually apply unreviewed external commits.

---

## Commit Policy Across Repos

Both repos enforce FORGE commit format where applicable:

- Dev repo: all commits must follow Conventional Commits with FORGE trailers.
- Public repo: commits generated by `forge-publish` use a standardized release commit message. Public contributor commits remain in public history when `publish_strategy: preserve-history` is used.

---

## Directory Structure Reference

### Private Dev Repo

```text
ToolName-dev/
├── src/                    source code
├── docs/
│   └── forge/              FORGE governance documents
│       ├── AI.md
│       ├── FORGE.md
│       ├── TASKS.yaml
│       ├── TOOL_WORKFLOW.md
│       └── ...
├── release/                staging directory (populated by forge-publish)
├── scripts/
│   ├── forge-tool-init.sh
│   ├── forge-tool-init.ps1
│   ├── forge-publish.sh
│   ├── forge-publish.ps1
│   ├── forge-sync-public.sh
│   └── forge-sync-public.ps1
└── forge.yaml
```

### Public Repo — Open Source

```text
ToolName/
├── [source artifacts from src/]
├── README.md
└── LICENSE
```

### Public Repo — Closed Source

GitHub Releases tab contains versioned binary assets. The repository itself contains only:

```text
ToolName/
├── README.md
└── LICENSE
```
