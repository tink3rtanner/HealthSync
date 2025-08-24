# bootstrap plan (incremental)

This document refines `bootstrap.md` into small, ordered steps for the data-first MVP.

## 1. Validate the sandbox
- Ensure Python tests run: `pytest -q`.
- Copy `.env.example` to `.env` only when tests require it.

## 2. Explore `data_samples/`
- List available files and note counts per type.
- Inspect JSON shapes and keys; capture timestamp ranges and any missing fields.
- Record observations in a short summary.

## 3. Build minimal tooling
- `tools/loader.py`: tolerant iterator over sample files.
- `tools/summarize.py`: report counts, keys, and timestamp ranges; optionally emit basic plots to `out/`.

## 4. Add tests
- Keep `tests/test_smoke.py` passing.
- Add `tests/test_loader_basic.py` verifying loader iterates files and summary includes counts and time range.
- Run `pytest -q` to confirm all tests pass.
- Future unit test: heart‑rate fixture's last gauge equals the final sample; zone totals may vary.

## 5. Next milestones
1. Implement transform -> Victoria Metrics.
2. Develop e2e script verifying metrics round-trip through Victoria Metrics.
3. Once data flow is validated locally, prepare Raspberry Pi deployment and networking.

`bootstrap.md` remains for historical context.
