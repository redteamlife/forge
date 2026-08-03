# Security Review: Codex SessionStart hook (TASK-037)

Required because it ships an executable hook.

## Change surface
A SessionStart hook (`.codex/hooks.json` + `forge_session_context.py`) and a
merge-safe installer. The hook runs on session start/resume/clear/compact and
prints developer context.

## Findings
- **No repo mutation, no secrets, no network.** The context script only reads
  docs/forge/AI.md and prints a fixed governance/output line. `pass`.
- **Fixed-enum parse.** `progress_policy` is matched against a regex enum; no
  project-controlled text is executed or interpolated into a shell. `pass`.
- **Merge-safe install.** Installer preserves unrelated hooks, replaces only the
  FORGE entry (canonical command path; legacy inline-echo by signature), and
  fails closed on malformed JSON. `pass`.
- **Trust boundary respected.** A hook is inert until the user trusts the project
  in Codex; the installer only writes the file, never activates it. `pass`.
- Cannot suppress a blocker — it only adds context; it changes no gate logic.

## Residual risk
The hook executes `python3` on session events once trusted; the shipped script
is inert (read + print). A user who edits the script assumes responsibility.
security: pass.
