# FORGE Codex Reinforcement (optional)

Codex narrates more by default than some harnesses, and portable skill wording
cannot fully override a host's system-level behavior. These optional, Codex-native
controls reinforce FORGE's output discipline — most importantly across
compaction, which a once-loaded reference cannot survive.

## SessionStart hook (recommended)

`.codex/hooks.json` + `.codex/hooks/forge_session_context.py` re-inject FORGE's
governance + output-discipline rule as developer context on `startup`, `resume`,
`clear`, and `compact`. The `compact` match is the key win: the rule re-applies
after Codex auto-compacts a long session.

Install / upgrade (merge-safe — preserves unrelated hooks, replaces only the
FORGE entry, fails closed on malformed JSON):

```
python3 <skill-root>/assets/scripts/forge_install_codex_hook.py <repo> --apply
```

A hook is not active until you **trust the project** in Codex. The script reads
`progress_policy` with a fixed-enum parse only, emits no secrets, and never
mutates the repository.

## Opt-in low-verbosity profile (user-owned)

For consistently compact Codex output, add a profile to your OWN
`~/.codex/config.toml` (FORGE never writes there):

```toml
[profiles.forge]
model_verbosity = "low"
model_reasoning_summary = "none"
hide_agent_reasoning = true
```

Honest limits: `model_verbosity = "low"` shortens output but does not guarantee
silence or override a higher-priority instruction; the reasoning flags cut
reasoning/log noise, not ordinary commentary. This is the strongest single lever
for narration on Codex, but it is your config to set, not something FORGE
installs.
