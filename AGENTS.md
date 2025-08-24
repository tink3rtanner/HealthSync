# project playbook for codex (minimum)

## goal
- mvp (data-first): explore `data_samples/`, summarize structure, and optionally plot simple views. No API/VM.

## inputs
- primary brief: `bootstrap.md` (section “2) 0→1 bootstrap” defines files and expectations).

## constraints
- no grafana, no cloudflared, no gateways in mvp.
- localhost-only networking in compose.
- keep diffs small; open a PR; keep tests green.
- treat agents as ephemeral; fixtures drive tests.

## environment
- copy `.env.example` → `.env` when tests need it.

## commands (expected once scaffold exists)
- pytest -q

## first task for codex (copy/paste prompt)
```
Task 1 (smoke): Create and run a minimal "hello world" test to validate the
sandbox. Do not scaffold the full project yet.

Steps:
1) Create tests/test_smoke.py with one passing test (e.g., assert "hello" in
   "hello world").
2) Run `pytest -q` and include the output. Keep the PR as small as possible.

After the smoke test passes, read bootstrap.md (data-first version) and write a
short plan summarizing how you will load and summarize `data_samples/`, and what
minimal tests/plots you will add. Open a follow-up task/PR to implement that next.
```

## non-goals (for this PR)
- workouts, sleep, vo2max, dashboards, tunnels.

## review checklist
- unit test asserts z2 sums to 600s and last HR gauge equals last sample.
- e2e script asserts z2 == 600 via VM query.

