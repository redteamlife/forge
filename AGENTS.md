@./skills/forge/SKILL.md

This repository contains the canonical FORGE skill-pack implementation under `skills/forge/`.

When working on the skill pack itself:

- prefer updating the canonical files in `skills/forge/`
- keep install docs and scripts at the repo root aligned with the canonical skill content
- preserve explicit activation; do not turn FORGE into an always-on behavior by default
- keep working responses terse and implementation-focused; avoid conversational filler and repeated context recap
- keep workflow and CI references aligned with `.github/workflows/verify-forge-skills.yml`
