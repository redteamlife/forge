# Bootstrap Scaffolding Helpers

Use this reference only when running `forge-bootstrap` and the project is
asking for one of these optional scaffolds. None of them are required.

## Narrative Agent Surface

Catapult-style "humane front door". Recommended default for `solo-governed`
and `team-full` profiles. Keeps `CLAUDE.md` as a router so `lite` context
discipline is preserved.

Ask the user for:

- project name (one phrase)
- project goal (one or two sentences)
- tech stack (3–6 bullets)
- repo layout (the top three to five directories)
- role split (only for team mode; one line per lane plus the integration seam)

Then run:

```
python <skill-root>/assets/scripts/forge_generate_agent_surfaces.py <repo> \
  --narrative --narrative-target agents \
  --project-name "..." --project-goal "..." \
  --tech-stack "..." --repo-layout "..." --role-split "..." \
  --scoped-rules
```

`--scoped-rules` emits `.cursor/rules/{project-conventions,security,...}.mdc`.
Stack rules are picked from auto-detected markers (`pyproject.toml`,
`package.json`, `go.mod`); override with `--stacks python,ts,go`.

Constraints:

- narrative `AGENTS.md` must not include `@docs/forge/*` references in lite
  mode; the script enforces this
- if the user pushes back on narrative, fall back to the router form

## Contract-First Scaffold

Use only when `repo_flavor: contract-first` is selected.

```
python <skill-root>/assets/scripts/forge_scaffold_contract.py <repo> \
  --kind {openapi|protobuf|graphql} --project-name "..."
```

OpenAPI mode also drops:

- `docs/forge/contracts/Makefile.snippet` (merge into project Makefile)
- `.github/workflows/check-openapi-drift.yml` (CI drift gate)

After scaffolding:

- record the contract file in `docs/forge/ARCHITECTURE.md` under
  "Contract Artifacts"
- declare `contract_files` on any task that touches the contract
- replace the `your-app dump-openapi` placeholder in the Makefile snippet
  with the real command for the chosen framework

## Quality CI Workflow

Use only when `team-full` + `ci_enforcement: enabled`.

Copy `<skill-root>/assets/ci/workflows/forge-quality.yml` to
`.github/workflows/forge-quality.yml` and replace the placeholder
lint/test/contract-drift commands with the project's real commands.

The `contract-drift` job should be removed when the repo has no shared
interface contract.
