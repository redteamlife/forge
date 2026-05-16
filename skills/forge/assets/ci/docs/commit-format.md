# FORGE Commit Format

FORGE commits use Conventional Commits with FORGE metadata as git trailers.

```text
<type>[optional scope]: <description>

FORGE-mode: <Lightweight|Mid|Strict|Full Discipline>
FORGE-task: <task-id>
FORGE-gate: pass
```

Valid types:

- `feat`
- `fix`
- `docs`
- `style`
- `refactor`
- `test`
- `chore`
- `build`
- `ci`
- `perf`
- `revert`

Trailers must appear in the commit footer, separated from any body text by a blank line.

Do not include AI attribution, assistant branding, or tool-marketing trailers.
