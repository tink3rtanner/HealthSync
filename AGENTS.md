# project playbook for codex (minimum)

## goal
- mvp (data-first): explore `data_samples/`, summarize structure, and optionally plot simple views. No API/VM.

## inputs
- primary brief: `bootstrap.md` (section “2) 0→1 bootstrap” defines files and expectations).
- stepwise roadmap: `bootstrap_plan_incremental.md` (current working plan).

## constraints
- no grafana, no cloudflared, no gateways in mvp.
- localhost-only networking in compose.
- keep diffs small; open a PR; keep tests green.
- treat agents as ephemeral; fixtures drive tests.

## environment
- copy `.env.example` → `.env` when tests need it.

## commands
- run `pytest -q` after changes to keep tests green.

## first task for codex (copy/paste prompt)
```
Task 1 (smoke): Create and run a minimal "hello world" test to validate the
sandbox. Do not scaffold the full project yet.

Steps:
1) Create tests/test_smoke.py with one passing test (e.g., assert "hello" in
   "hello world").
2) Run `pytest -q` and include the output. Keep the PR as small as possible.

After the smoke test passes, follow `bootstrap_plan_incremental.md` to load and
summarize `data_samples/` and add minimal tests/plots. Keep the PR as small as
possible.
```

## non-goals (for this PR)
- workouts, sleep, vo2max, dashboards, tunnels.

## review checklist
- unit test ensures the last HR gauge equals the final sample.
- e2e script verifies transformed metrics round-trip through Victoria Metrics.

