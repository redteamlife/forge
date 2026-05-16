---
name: forge-security-review
description: Apply FORGE checklist-based security review to a task. Use when selecting a task-specific security checklist, reviewing trust-boundary and sensitive-data impact, and producing explicit pass, n-a, or escalated outcomes for each item.
---

# FORGE Security Review

Use this skill after implementation and before completion.

## Use When

- implementation changes security-relevant behavior or project policy requires review
- the change touches auth, data, APIs, frontend surfaces, storage, infra, CI, CD, dependencies, build artifacts, or deployment
- `forge-review` routes here between critique and evaluation

## Do Not Use When

- the user wants general code review rather than security checklist review
- project-local checklist inputs are required but missing
- the change surface cannot be identified

## Workflow

1. Read `docs/forge/CONTEXT.md` if present, then `docs/forge/AI.md`.
2. Read the selected task from `docs/forge/TASKS.index.yaml`, `docs/forge/tasks/`, `docs/forge/TASKS.yaml`, or the configured issue tracker.
3. Select checklist inputs:
   - prefer relevant files in `docs/forge/security-checklists/`
   - if relevance is unclear, start with `docs/forge/security-checklists/general.md`
   - fall back to relevant sections of `docs/forge/SECURITY_CHECKLISTS.md`
4. Apply only the sections relevant to the active change surface.
5. If the change adds or modifies automation for GitHub, GitLab, Jira, Linear, or another tracker, review token scope and assignee semantics.
6. If the change touches repository settings, CI, CD, dependency management, build artifacts, or deployment, apply the matching DevSecOps checklist sections.
7. Require an explicit outcome for every item: `pass`, `n/a`, or escalated.
8. If any unresolved concern remains, stop before evaluation.

## Hard Stops

Stop when:

- neither split checklists nor the compatibility checklist wrapper are available when checklist review is required
- the change surface is unclear
- any checklist item remains unresolved
- a declared security profile lacks setup evidence for claimed controls
- token scope, secret handling, trust boundary, or sensitive-data concerns cannot be resolved

## Rationalizations To Reject

| Rationalization | FORGE response |
|---|---|
| "This is not a security task." | Security review follows touched surfaces, not task labels alone. |
| "No auth changed, so security is n/a." | Data, APIs, frontend, CI, dependencies, and deployment can all be security surfaces. |
| "The scanner will catch it." | Automated scans are evidence, not a substitute for checklist outcomes. |
| "We probably have branch protection." | Claimed controls need setup evidence. |

## Evidence Required

- selected checklist sections
- `pass`, `n/a`, or escalated result for every applicable item
- unresolved findings, if any
- recorded setup evidence for claimed DevSecOps controls

## Notes

- Free-form narrative is not enough by itself.
- Prefer recording results in `docs/forge/EVALUATION.md`.
- Keep the review crisp and machine-checkable where possible.
- Do not load every checklist by default.
- Prefer read-only project or service tokens for issue-state verification.
- Use a human account or user-scoped token for assignment when claim ownership must represent the engineer.
- Do not treat a bot-assigned issue as human ownership unless project policy explicitly allows it.
- Do not claim SAST, DAST, SCA, SBOM, branch protection, CODEOWNERS, or security-policy coverage exists unless setup evidence is recorded.
- If a project declares `security_profile: ci-security` or `full-devsecops`, missing configured checks are findings, not silent `n/a` results.
- If split checklists and the compatibility wrapper are both missing for a workflow that expects checklist review, stop and ask for one to be created.
- Shared baseline assets live under `assets/security-checklists/` in the installed skill pack; bootstrap may compose a smaller project-local checklist from those assets.
