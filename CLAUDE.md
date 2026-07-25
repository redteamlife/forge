# FORGE Skill-Pack Repository

This repository contains the canonical FORGE skill-pack implementation under `skills/forge/`.

When working on the skill pack itself:

- use installed FORGE skills explicitly for governed work; do not auto-load the whole skill pack
- read `skills/forge/SKILL.md` only when root routing guidance is needed
- read specific subskill files such as `skills/forge/bootstrap/SKILL.md` or `skills/forge/execute-task/SKILL.md` only for the current task
- prefer updating the canonical files in `skills/forge/`
- keep install docs and scripts at the repo root aligned with the canonical skill content
- preserve explicit activation; do not turn FORGE into an always-on behavior by default
- keep working responses terse and implementation-focused; avoid conversational filler and repeated context recap
- keep workflow and CI references aligned with `.github/workflows/verify-forge-skills.yml`
- repo governance lives on `dev` only: `docs/forge/` must never reach `main`; promote via `scripts/forge-promote.sh` (squash + strip), enforced by `.github/workflows/main-branch-guard.yml`
