# HealthSync — Codex Cloud minimal kickoff

This repository is intentionally minimal so OpenAI Codex Cloud can scaffold the MVP.

## How to run with Codex Cloud
1. Open ChatGPT → Codex → Open Repository → select this repo.
2. Use the prompt below as the first instruction. Codex will open a PR.

## First prompt for Codex
```
First, create and run a minimal "hello world" test to validate the sandbox.
Add tests/test_smoke.py with one passing test (e.g., assert "hello" in
"hello world") and run `pytest -q`, sharing the output.

After that smoke passes, read bootstrap.md and propose a brief plan for
scaffolding the MVP from section “2) 0→1 bootstrap” and how you'll test it.
Open a follow-up task/PR for implementation.
```

See also: `AGENTS.md` for guardrails.
