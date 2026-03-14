# Security Checklists

## Purpose

Provide concrete, task-type-specific security checklists for the security review pass (FORGE.md Step 9).

The agent selects the checklist matching the active task's `task_type` field and answers every item. Each item must receive an explicit outcome: `pass`, `n/a`, or an escalation note if a concern is identified. Free-form narrative does not satisfy the checklist.

If no `task_type` is declared, apply the General checklist.

If a checklist item raises an unresolved concern, hard stop and escalate before proceeding to the evaluation gate.

---

## General (all task types)

Apply this checklist in addition to any type-specific checklist below.

- [ ] Does this change introduce new external inputs (user data, API params, file paths, env vars)?
- [ ] Are all new external inputs validated and sanitized before use?
- [ ] Does this change touch or expose credentials, tokens, secrets, or PII?
- [ ] Are sensitive values excluded from logs, error messages, and responses?
- [ ] Does this change modify file system paths, shell commands, or subprocess calls?
- [ ] Are new dependencies introduced, and have they been reviewed for known vulnerabilities?
- [ ] Does this change affect error handling in a way that could expose internal state?

---

## feature

Apply in addition to General.

- [ ] Are new capabilities gated behind appropriate authentication and authorization checks?
- [ ] Does the feature introduce new trust boundaries or cross existing ones?
- [ ] Are new API endpoints or data flows documented in ARCHITECTURE.md?
- [ ] Does the feature introduce new persistent state, and is that state access-controlled?
- [ ] Have rate limiting and abuse scenarios been considered for any new user-facing surface?

---

## fix

Apply in addition to General.

- [ ] Does the fix address the root cause or only the symptom?
- [ ] Could the fix introduce a regression in a security-sensitive code path?
- [ ] Does the fix change behavior that other components depend on (trust boundary impact)?
- [ ] If the original issue was security-related, is the fix reviewed against the full attack surface?

---

## refactor

Apply in addition to General.

- [ ] Does the refactor preserve all existing security invariants (auth checks, validation, access control)?
- [ ] Were any security-relevant conditions simplified, reordered, or removed?
- [ ] Does the refactor change error handling behavior in security-sensitive paths?
- [ ] Are tests in place that would catch a security regression introduced by this refactor?

---

## security

Apply in addition to General. This task type requires the most thorough review.

- [ ] Is the threat model for this change explicitly documented?
- [ ] Have all attack vectors relevant to this change been enumerated?
- [ ] Has the change been verified against the specific vulnerability class it targets?
- [ ] Are tests written that demonstrate the vulnerability is closed (not just that the fix compiles)?
- [ ] Have adjacent or related code paths been reviewed for the same vulnerability class?
- [ ] Does this change require external review, pen testing, or a second agent review pass?

---

## api_change

Apply in addition to General.

- [ ] Is authentication required on all new or modified endpoints?
- [ ] Are authorization checks (role, permission, ownership) applied at the correct layer?
- [ ] Are all request inputs validated for type, length, format, and allowed values?
- [ ] Are responses filtered to exclude fields the caller should not receive?
- [ ] Are error responses generic enough to avoid leaking internal detail?
- [ ] Is rate limiting applied to new endpoints?
- [ ] Are new endpoints documented in ARCHITECTURE.md?

---

## data_model_change

Apply in addition to General.

- [ ] Are any new fields sensitive (PII, credentials, financial data)? If so, are they encrypted at rest?
- [ ] Are access controls applied to new fields at the query or application layer?
- [ ] Does the migration preserve data integrity under partial failure?
- [ ] Is the migration reversible, and has a rollback plan been documented?
- [ ] Are indexes or constraints introduced in a way that could cause downtime?
- [ ] Are new fields excluded from logs and error output?

---

## auth_change

Apply in addition to General. This task type requires the most thorough review.

- [ ] Does the change affect session creation, validation, or expiry?
- [ ] Are token or credential storage mechanisms reviewed (no plaintext, appropriate hashing)?
- [ ] Is token lifetime appropriate for the risk level of the protected resource?
- [ ] Are revocation and logout paths fully handled?
- [ ] Could the change allow privilege escalation (horizontal or vertical)?
- [ ] Are brute-force and replay attack vectors addressed?
- [ ] Has the change been tested against the full authentication flow end to end?

---

## docs

Apply in addition to General.

- [ ] Does the documentation expose internal implementation details, credentials, or environment specifics?
- [ ] Are code examples in documentation safe to copy and run (no hardcoded secrets, no unsafe patterns)?

---

## config

Apply in addition to General.

- [ ] Are default values safe for production use?
- [ ] Are secrets or credentials sourced from environment variables or a secrets manager, not config files?
- [ ] Is the config file excluded from version control if it can contain sensitive values?
- [ ] Does the config change affect security-relevant behavior (timeouts, retries, TLS, auth)?

---

## Recording Checklist Results

Record the completed checklist in `EVALUATION.md` as part of the security review evidence. Format:

```
## Security Review - <task-id>

task_type: <type>
checklists applied: General, <type>

| Item | Outcome |
|------|---------|
| <checklist item text> | pass / n/a / ESCALATED |

Unresolved concerns: none / <description>
```

A security review is only complete when every item has an explicit outcome and unresolved concerns are none or formally escalated.
