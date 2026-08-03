# Security Review: forge_upgrade.py (TASK-036)

Required because it mutates existing project files.

## Change surface
A stdlib-only upgrader. Mutates only with --apply, backs up AI.md before editing,
patches only the FORGE-config block (regex-bounded), and regenerates surfaces
only when they match the stock-router signature.

## Findings
- Fail-safe default: dry-run unless --apply. `pass`.
- No destructive regen of customized/narrative surfaces (signature-gated); they
  are reported for manual edit, never overwritten. `pass`.
- AI.md backed up to .md.bak before any write; patch limited to the config block,
  never prose. `pass`.
- Unknown legacy `response_style` value halts (exit 1) for human decision rather
  than guessing. `pass`.
- No network, no credentials, no execution of project-controlled text. `pass`.

## Residual risk
A stock-router repo that hand-edited its router below the first heading would be
regenerated; acceptable — the signature is the documented contract, and AI.md is
backed up. security: pass.
