# FORGE Context Budget

```yaml
context_profile: lite

default_session_reads:
  - docs/forge/AI.md
  - selected task only

never_auto_read:
  - docs/forge/SECURITY_CHECKLISTS.md
  - docs/forge/security-checklists/*
  - docs/forge/MEMORY.md
  - docs/forge/MEMORY.index.yaml
  - docs/forge/memory/*
  - docs/forge/TEAM.md
  - docs/forge/ARCHITECTURE.md
  - docs/forge/SETUP.md
  - docs/forge/EVALUATION.md

read_when:
  TEAM.md: "team-full mode, task ownership conflict, branch claiming ambiguity, or reviewer/persona routing"
  ARCHITECTURE.md: "task touches design boundaries, persistence, interfaces, deployment, data flow, or cross-module behavior"
  SECURITY_CHECKLISTS.md: "explicit security review, authn/authz work, input validation, secrets, crypto, deserialization, SSRF, injection, or supply-chain risk"
  MEMORY.md: "fallback only; prefer MEMORY.index.yaml plus a specific memory topic file"
  MEMORY.index.yaml: "when prior context is needed; then read only the relevant memory topic file"
  EVALUATION.md: "evaluation/reflection tasks only"
  SETUP.md: "environment setup or onboarding tasks only"

hard_rules:
  - "Do not load all docs/forge files at startup."
  - "Do not read every task to select work; use the task index."
  - "Do not load full checklists unless performing a security review."
  - "Prefer selected snippets over whole files when possible."

budgets:
  lite:
    default_context_tokens_warn: 2500
    default_context_tokens_fail: 5000
  standard:
    default_context_tokens_warn: 5000
    default_context_tokens_fail: 10000
  full:
    default_context_tokens_warn: 15000
    default_context_tokens_fail: 30000
```
