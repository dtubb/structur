# structur — Agent Constitution

## Agent Config

```
TASK_TRACKING: local
AUTONOMOUS_COMMITS: true
UPCOMING_BRANCH: codex/upcoming
```

## Purpose

Working constitution for agent operations in this repository.

## Autonomous Loop Policy

- `main` is the stable source-of-truth branch.
- `codex/upcoming` is the active integration lane for autonomous runs.
- Use short-lived issue branches only when isolation is needed, then merge back quickly.
- Do not keep long-lived `release/*` branches for `0.0.x`.
- Before loading full context, check repo-level `BLOCK.md`.
- If the first non-empty line starts with `BLOCKED`, stop immediately.
- When blocked: do not triage tasks, do not spawn agents, do not modify files; report `STATUS: BLOCKED` and the first blocking line.
- Use global `session-start`, `session-start-auto`, `session-start-team`, and `session-end` skills by default. Project-local overrides require explicit justification.

## Rules

1. Keep changes small and scoped.
2. Prefer documented workflow over ad-hoc branching.
3. Record durable operational decisions in MEMORY/STATE docs when present.
