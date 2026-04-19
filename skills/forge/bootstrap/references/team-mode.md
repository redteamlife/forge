# Bootstrap Team Mode

Team mode exists to keep concurrent developers and agents from colliding.

At bootstrap time:

- define branch naming and PR policy in `docs/forge/TEAM.md`
- require task claiming before implementation
- require `file_scope` for executable tasks
- define the integration closeout contract so `implemented`, `integrated`, and `complete` are not conflated
- enable `ci_enforcement` in `docs/forge/AI.md`
