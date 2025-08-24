# codex kickoff brief (0→1 mvp)

> tl;dr for Codex Cloud
>
> - Step 1 (this PR): Create and run a minimal hello-world pytest (tests/test_smoke.py).
> - Step 2 (next PR): Explore `data_samples/` only. No API, no Docker, no VM.
> - Produce a short report: file counts, schema keys, sample counts, timestamp ranges, anomalies.
> - Optionally emit 1–2 simple plots from samples (e.g., value over time) to a local `out/` folder.
> - Add minimal, tolerant tests for the loader/summarizer. Defer endpoints and transforms.
> - Ignore API/VM/600s-in-zone-2 sections below (legacy; kept for later).


> objective: in codex cloud, start data-first: read the provided sample files under `data_samples/`,
> understand their shape, summarize them, and (optionally) render simple plots. no api, no vm,
> no docker for mvp. endpoints and transforms are later milestones.

## what to build (deliverables — data-first mvp)

* docs and utilities only, focused on understanding `data_samples/`:

```
README.md               # codex usage + prompts
AGENTS.md               # first tasks for codex

tools/
  loader.py             # load and iterate sample files (shape‑tolerant)
  summarize.py          # compute basic stats: counts, keys, ts ranges, missing

tests/
  test_smoke.py         # hello‑world
  test_loader_basic.py  # minimal loader/summarizer assertions (no strict schema)

out/                    # codex may write simple plots/reports here (gitignored later)
```

## endpoints & security (mvp)

Deferred. No endpoints in the first iteration. Operate on `data_samples/` only.

## fixture schema (hr-only for mvp)

```json
{
  "type": "heart_rate",
  "source": "hae",
  "device": "applewatch_ultra_2",
  "samples": [
    {"ts": 1724512345, "bpm": 132},
    {"ts": 1724512350, "bpm": 133}
  ]
}
```

* note: initial run may use a synthetic file; later you will paste a trimmed, realistic segment from yesterday’s iphone export here.

## transform rules

Deferred. Avoid prescriptive mapping. Let Codex infer structure from samples and
draft a proposal later.

## compose (mvp)

Deferred. No docker/VM required for the first iteration.

**.env.example**

Deferred. Not needed for data-first iteration.

**makefile**

Optional later. For now, `pytest -q` is sufficient.

## tests (what must pass in codex)

* smoke: `tests/test_smoke.py` passes.
* loader/summarizer: can enumerate files in `data_samples/`, parse JSON records leniently,
  and return simple counts/ranges without failing on unexpected keys.

## codex prompt (copy/paste to start)

> Step 1: add `tests/test_smoke.py` with a single passing assertion and run `pytest -q`.
> Step 2: write `tools/loader.py` and `tools/summarize.py` to iterate `data_samples/` and
> produce a short printed summary (counts, keys, ts ranges) and optionally save 1–2 plots
> into `out/`. Add `tests/test_loader_basic.py` with minimal, tolerant checks. Do not add
> any API, Docker, or VM. Keep PR small.

## real-data fixtures (later today)

* use health auto export on iphone → json export for **last week**.
* extract **one 10‑minute hr block** at \~z2 intensity into `tests/fixtures/realish/hr_z2_10min.json` following the schema above (no need to strip pii if repo is private).
* re-run `make test` in codex; adjust mapping if sample sits on zone boundary.

## footnote (future only; do not build now)

* read‑only live peek later via tiny gateway behind cloudflare tunnel; keep agents on fixtures by default.

---

# fitness ingest stack — prd + runbook (pi + agents)

> start **painfully simple**: prove we can ingest a few heart‑rate (hr) samples end‑to‑end in a sandbox, then ship to the pi. agents are ephemeral; vm is the source of truth.

---

## 0) scope & goals (mvp first)

* **mvp ingest**: a **couple recent hr readings** only.
* use **health auto export (hae)** to see real sample shape; confirm our fixture schema matches reality.
* transform → **victoria‑metrics (vm)** as gauges/counters we’ll expand later.
* no mysql. keep **raw ndjson** for audit/replay.
* **low‑pain networking**: cloudflare tunnel (for real phone → pi later). sandbox uses **localhost** only.
* **codex cloud agent** for dev/tests; github actions **optional later** (skip rn).
* grafana nice‑to‑have after mvp (we’ll still list starter queries).
* optional later: trmnl e‑ink pngs off the same vm data.

non‑goals (mvp): workouts, sleep, vo2max — we’ll add after hr is green.

---

## 1) architecture (mvp)

**sandbox path (now)**: sample files → loader → summaries/plots → tests

**later path**: phone/export → api → raw → transforms → vm/grafana

**compose services (mvp)**

* `api`: fastapi receiver + minimal transformer (hr → zone seconds + optional hr gauge)
* `victoria-metrics` (vm): time‑series db
* (later) `grafana`
* (later) `cloudflared` tunnel (for the pi only)

all containers on a private docker network; host ports bound to `127.0.0.1`.

---

## 2) 0→1 bootstrap (exact handoff an agent can execute)

**goal:** create a repo Codex can run immediately to explore `data_samples/` and produce
basic summaries/plots with passing smoke tests.

**files to scaffold**

```
README.md
AGENTS.md
Makefile
.env.example

docker-compose.yml

api/
  requirements.txt
  main.py            # POST /hook/{secret} (auth), write raw ndjson, transform->vm
  transform.py       # json -> influx line protocol lines (hr + zone)

scripts/
  wait_ready.sh
  post_fixture.sh
  assert_vm.sh

tests/
  fixtures/hae/hr_z2_10min.json
  test_transform.py
```

**env example**

```
AUTH_TOKEN=changeme
SECRET_PATH=devhook
HR_MAX=200
RHR=60
ZONES_MODE=max   # or karvonen later
```

**compose (mvp)**

```yaml
version: "3.9"
services:
  api:
    build: ./api
    environment:
      - AUTH_TOKEN=${AUTH_TOKEN}
      - SECRET_PATH=${SECRET_PATH}
      - HR_MAX=${HR_MAX}
      - RHR=${RHR}
      - ZONES_MODE=${ZONES_MODE}
    ports: ["127.0.0.1:18000:8000"]
    volumes: [ "raw:/data/raw" ]
    restart: unless-stopped
  vm:
    image: victoriametrics/victoria-metrics
    command: -retentionPeriod=5y
    ports: ["127.0.0.1:18428:8428"]
    restart: unless-stopped
volumes: { raw: {} }
```

**makefile (mvp)**

```
up: ; docker compose up -d
 down: ; docker compose down -v
 test: ; pytest -q --cov=api --cov-report=term-missing
 seed: ; ./scripts/post_fixture.sh
```

**zero‑to‑one with codex (no local ide needed)**

* create a **blank github repo**.
* open chatgpt → codex → “open repository” → select repo.
* prompt codex: **“scaffold the files listed in section 2 of the prd, implement a minimal fastapi /hook that writes ndjson and converts hr fixtures to vm influx line protocol, plus unit + e2e tests; run make up && make test; fix red tests.”**
* codex will create files, run compose/tests in its sandbox, and open a pr. you can review/merge. (you *can* also do this locally in vscode; not required.)

---

## 3) fixtures (mvp realism)

* start with **synthetic hr**: 10 minutes at \~65% HRmax → expect **600s** in z2.
* schema (keep tight):

```json
{
  "type": "heart_rate",
  "sourceBundleId": "dev.fixture",
  "device": "applewatch_ultra_2",
  "samples": [
    {"ts": 1724512345, "bpm": 132},
    {"ts": 1724512350, "bpm": 133}
  ]
}
```

* assertions (e2e):

  * `increase(zone_seconds_total{zone="z2"}[1h]) == 600`
  * optional: last hr gauge equals last sample bpm

**later** (after mvp): record one hae export, scrub ids, clamp to a fixed anchor date, and add as a “realish” fixture.

---

## 4) transform rules (mvp)

* compute `dt` between consecutive hr samples (cap per‑sample `dt` to e.g. 10s to avoid long gaps inflating zone time).
* map bpm→zone using `%max` (or karvonen later).
* bump `zone_seconds_total{zone}` by `dt` via influx line protocol to vm.
* optionally write `heart_rate_bpm` gauge at each sample ts.

**influx line examples**

```
zone_seconds_total,zone=z2,user=me value=5i 1724512345000000000
heart_rate_bpm,user=me value=133 1724512350000000000
```

---

## 5) testing (tdd, minimal)

**unit (transform)**

* input: `tests/fixtures/hae/hr_z2_10min.json`
* assert: emitted lines sum to 600s in z2; last hr gauge equals fixture tail.

**e2e (compose sandbox)**

1. `docker compose up -d`
2. `scripts/wait_ready.sh` checks `http://localhost:18000/ping` and `http://localhost:18428/health`
3. `scripts/post_fixture.sh` posts fixture to `/hook/{SECRET_PATH}` with bearer
4. `scripts/assert_vm.sh` queries vm api and asserts z2==600

all of this runs **inside codex** or locally; no lan, no tunnel.

---

## 6) grafana (after mvp)

* add datasource `victoria-metrics` at `http://vm:8428`.
* starter panels:

  * weekly zone time (hrs, stacked): `sum by (zone)(increase(zone_seconds_total[1w]))/3600`
  * z2+ hours: `sum(increase(zone_seconds_total{zone=~"z2|z3|z4|z5"}[1w]))/3600`
  * hr trend (last 24h): `heart_rate_bpm`

---

## 7) trmnl e‑ink (later, but planned)

* **bespoke renderer**: query vm (`/api/v1/query_range`) and draw stark b/w png sized to your trmnl resolution; host it behind your tunnel; point trmnl’s image plugin at that url.
* keep typography huge (numerics) + minimal sparklines; e‑ink loves contrast.

---

## 8) networking (prod only)

* add `cloudflared` service; map public hostname → `http://api:8000`.
* keep host binds to `127.0.0.1`; the tunnel is the only ingress.

---

## 9) deployment to the pi (after sandbox is green)

1. `ssh` to the pi; install docker + compose; enable cgroup memory if needed.
2. clone repo to `/opt/fitness-stack`.
3. create real `.env` with long `AUTH_TOKEN`, `SECRET_PATH`, zones config, tunnel token.
4. `docker compose up -d`.
5. point **hae** to `https://<your-tunnel>/hook/${SECRET_PATH}` with bearer header; cadence 5–10 min.
6. verify vm has points; then wire grafana and (later) trmnl renderer.

---

## 10) security & ops (even in mvp)

* bearer token + secret path; reject without both.
* write **raw ndjson first**, then transform → vm (replayable).
* idempotency: dedupe key = sha256(`type|start|end|value|source|device`).
* caps: mem/cpu per container; bind only to loopback on host; tunnel for public.
* retention: vm `-retentionPeriod=5y` (tune later). back up volumes (`raw`, vm, grafana if used).

---

## 11) agents.md (what codex follows)

```
# project playbook for agents

## goals
- mvp: ingest hr fixture -> vm (zone_seconds_total + heart_rate_bpm), assert z2=600

## commands
- make up / make down / make test / make seed

## env
- copy .env.example -> .env (tests only)

## tests
- unit: tests/test_transform.py
- e2e: compose up -> wait_ready -> post_fixture -> assert_vm

## prs
- keep diffs small; maintain tests green; expand fixtures incrementally (workouts, sleep) after mvp
```

---

## 12) faq (quick hits)

* **do i need github actions now?** no. use codex only. add gha later if you want scheduled builds or multi‑arch pushes.
* **what’s e2e again?** bring up compose in a sandbox, post a fixture to your api, and assert vm numbers — no lan, no phone.
* **can i dev locally?** yes, vscode works fine; but codex can scaffold+run the whole thing if you don’t want local setup yet.
* **how do agents “remember”?** they don’t. vm on the pi is persistent; agents are stateless per task; they use fixtures.

---

**done (mvp‑first version).** next milestone after hr: add workouts (count/distance) and sleep (stage seconds), then grafana and trmnl pngs.


# codex kickoff brief (0→1 mvp)

> objective: in a codex cloud sandbox, ingest **a few recent hr samples** via `/hook`, transform to vm metrics, and assert z2==600 using a fixture derived from your iphone export. no grafana, no tunnel, no gateway yet.

## what to build (deliverables)

* repo scaffold runnable in codex sandbox:

```
README.md
AGENTS.md
Makefile
.env.example

docker-compose.yml

api/
  requirements.txt
  main.py            # fastapi: POST /hook/{secret} (bearer auth) + /ping
  transform.py       # hr json -> influx line protocol lines

scripts/
  wait_ready.sh      # poll api/vm until ready
  post_fixture.sh    # post tests/fixtures/... to /hook with bearer
  assert_vm.sh       # query vm api and assert numeric results (jq)

tests/
  fixtures/realish/hr_z2_10min.json  # you will paste from iphone export (trimmed)
  test_transform.py
```

## endpoints & security (mvp)

* `POST /hook/{secret}` → expects body schema below; header `authorization: Bearer <token>`.
* `GET /ping` → returns 200 empty body.
* write body to `/data/raw/YYYY-MM-DD.ndjson` (append), then transform and POST to vm `/_/write` (influx line protocol). bind host ports to `127.0.0.1`.

## fixture schema (hr-only for mvp)

```json
{
  "type": "heart_rate",
  "source": "hae",
  "device": "applewatch_ultra_2",
  "samples": [
    {"ts": 1724512345, "bpm": 132},
    {"ts": 1724512350, "bpm": 133}
  ]
}
```

* note: initial run may use a synthetic file; later you will paste a trimmed, realistic segment from yesterday’s iphone export here.

## transform rules (hr → metrics)

* sort by `ts` asc.
* dedup: drop sample if `(ts,bpm)` equals previous or `ts` ≤ previous.
* `dt = min(ts_i - ts_{i-1}, 10)` seconds (cap gaps at 10s).
* zone mapping (%hrmax for mvp):

  * z1: <60%, z2: 60–70, z3: 70–80, z4: 80–90, z5: ≥90 (configurable via env later).
* bump `zone_seconds_total{zone}` by `dt` (counter); optionally emit `heart_rate_bpm` gauge at `ts`.
* influx line protocol examples:

```
zone_seconds_total,zone=z2,user=me value=5i 1724512345000000000
heart_rate_bpm,user=me value=133 1724512350000000000
```

## compose (mvp)

```yaml
version: "3.9"
services:
  api:
    build: ./api
    environment:
      - AUTH_TOKEN=${AUTH_TOKEN}
      - SECRET_PATH=${SECRET_PATH}
      - HR_MAX=${HR_MAX}
      - RHR=${RHR}
      - ZONES_MODE=${ZONES_MODE}
    ports: ["127.0.0.1:18000:8000"]
    volumes: [ "raw:/data/raw" ]
    restart: unless-stopped
  vm:
    image: victoriametrics/victoria-metrics
    command: -retentionPeriod=5y
    ports: ["127.0.0.1:18428:8428"]
    restart: unless-stopped
volumes: { raw: {} }
```

**.env.example**

```
AUTH_TOKEN=changeme
SECRET_PATH=devhook
HR_MAX=200
RHR=60
ZONES_MODE=max
```

**makefile**

```
up: ; docker compose up -d
 down: ; docker compose down -v
 test: ; pytest -q --cov=api --cov-report=term-missing
 seed: ; ./scripts/post_fixture.sh
```

## tests (what must pass in codex)

* **unit (transformer):** given `tests/fixtures/realish/hr_z2_10min.json`, emitted lines must sum to **600s** in z2; last hr gauge equals last sample bpm.
* **e2e (compose sandbox):**

  1. `docker compose up -d`
  2. `scripts/wait_ready.sh` checks `http://localhost:18000/ping` and `http://localhost:18428/health`
  3. `scripts/post_fixture.sh` posts fixture (with bearer + secret)
  4. `scripts/assert_vm.sh` queries vm: `increase(zone_seconds_total{zone="z2"}[1h]) == 600`

## codex prompt (copy/paste to start)

> scaffold the repo exactly as specified in the "codex kickoff brief (0→1 mvp)" section of the prd. implement fastapi /hook with bearer+secret, raw ndjson append, and hr→influx transform per rules. add unit + e2e tests and the three shell scripts. run `make up && make test` in the sandbox and iterate until green. do not add grafana or cloudflare yet.

## real-data fixtures (later today)

* use health auto export on iphone → json export for **last week**.
* extract **one 10‑minute hr block** at \~z2 intensity into `tests/fixtures/realish/hr_z2_10min.json` following the schema above (no need to strip pii if repo is private).
* re-run `make test` in codex; adjust mapping if sample sits on zone boundary.

## footnote (future only; do not build now)

* read‑only live peek later via tiny gateway behind cloudflare tunnel; keep agents on fixtures by default.

---

# fitness ingest stack — prd + runbook (pi + agents)

> start **painfully simple**: prove we can ingest a few heart‑rate (hr) samples end‑to‑end in a sandbox, then ship to the pi. agents are ephemeral; vm is the source of truth.

---

## 0) scope & goals (mvp first)

* **mvp ingest**: a **couple recent hr readings** only.
* use **health auto export (hae)** to see real sample shape; confirm our fixture schema matches reality.
* transform → **victoria‑metrics (vm)** as gauges/counters we’ll expand later.
* no mysql. keep **raw ndjson** for audit/replay.
* **low‑pain networking**: cloudflare tunnel (for real phone → pi later). sandbox uses **localhost** only.
* **codex cloud agent** for dev/tests; github actions **optional later** (skip rn).
* grafana nice‑to‑have after mvp (we’ll still list starter queries).
* optional later: trmnl e‑ink pngs off the same vm data.

non‑goals (mvp): workouts, sleep, vo2max — we’ll add after hr is green.

---

## 1) architecture (mvp)

**sandbox path**: fixture → `api` → raw ndjson → vm → assertions

**prod path** (after mvp): phone (hae) → cloudflare tunnel → `api` → raw → transform → vm → grafana (+ optional trmnl renderer)

**compose services (mvp)**

* `api`: fastapi receiver + minimal transformer (hr → zone seconds + optional hr gauge)
* `victoria-metrics` (vm): time‑series db
* (later) `grafana`
* (later) `cloudflared` tunnel (for the pi only)

all containers on a private docker network; host ports bound to `127.0.0.1`.

---

## 2) 0→1 bootstrap (exact handoff an agent can execute)

**goal:** create a repo that codex can run immediately (unit + e2e) with synthetic hr.

**files to scaffold**

```
README.md
AGENTS.md
Makefile
.env.example

docker-compose.yml

api/
  requirements.txt
  main.py            # POST /hook/{secret} (auth), write raw ndjson, transform->vm
  transform.py       # json -> influx line protocol lines (hr + zone)

scripts/
  wait_ready.sh
  post_fixture.sh
  assert_vm.sh

tests/
  fixtures/hae/hr_z2_10min.json
  test_transform.py
```

**env example**

```
AUTH_TOKEN=changeme
SECRET_PATH=devhook
HR_MAX=200
RHR=60
ZONES_MODE=max   # or karvonen later
```

**compose (mvp)**

```yaml
version: "3.9"
services:
  api:
    build: ./api
    environment:
      - AUTH_TOKEN=${AUTH_TOKEN}
      - SECRET_PATH=${SECRET_PATH}
      - HR_MAX=${HR_MAX}
      - RHR=${RHR}
      - ZONES_MODE=${ZONES_MODE}
    ports: ["127.0.0.1:18000:8000"]
    volumes: [ "raw:/data/raw" ]
    restart: unless-stopped
  vm:
    image: victoriametrics/victoria-metrics
    command: -retentionPeriod=5y
    ports: ["127.0.0.1:18428:8428"]
    restart: unless-stopped
volumes: { raw: {} }
```

**makefile (mvp)**

```
up: ; docker compose up -d
 down: ; docker compose down -v
 test: ; pytest -q --cov=api --cov-report=term-missing
 seed: ; ./scripts/post_fixture.sh
```

**zero‑to‑one with codex (no local ide needed)**

* create a **blank github repo**.
* open chatgpt → codex → “open repository” → select repo.
* prompt codex: **“scaffold the files listed in section 2 of the prd, implement a minimal fastapi /hook that writes ndjson and converts hr fixtures to vm influx line protocol, plus unit + e2e tests; run make up && make test; fix red tests.”**
* codex will create files, run compose/tests in its sandbox, and open a pr. you can review/merge. (you *can* also do this locally in vscode; not required.)

---

## 3) fixtures (mvp realism)

* start with **synthetic hr**: 10 minutes at \~65% HRmax → expect **600s** in z2.
* schema (keep tight):

```json
{
  "type": "heart_rate",
  "sourceBundleId": "dev.fixture",
  "device": "applewatch_ultra_2",
  "samples": [
    {"ts": 1724512345, "bpm": 132},
    {"ts": 1724512350, "bpm": 133}
  ]
}
```

* assertions (e2e):

  * `increase(zone_seconds_total{zone="z2"}[1h]) == 600`
  * optional: last hr gauge equals last sample bpm

**later** (after mvp): record one hae export, scrub ids, clamp to a fixed anchor date, and add as a “realish” fixture.

---

## 4) transform rules (mvp)

* compute `dt` between consecutive hr samples (cap per‑sample `dt` to e.g. 10s to avoid long gaps inflating zone time).
* map bpm→zone using `%max` (or karvonen later).
* bump `zone_seconds_total{zone}` by `dt` via influx line protocol to vm.
* optionally write `heart_rate_bpm` gauge at each sample ts.

**influx line examples**

```
zone_seconds_total,zone=z2,user=me value=5i 1724512345000000000
heart_rate_bpm,user=me value=133 1724512350000000000
```

---

## 5) testing (tdd, minimal)

**unit (transform)**

* input: `tests/fixtures/hae/hr_z2_10min.json`
* assert: emitted lines sum to 600s in z2; last hr gauge equals fixture tail.

**e2e (compose sandbox)**

1. `docker compose up -d`
2. `scripts/wait_ready.sh` checks `http://localhost:18000/ping` and `http://localhost:18428/health`
3. `scripts/post_fixture.sh` posts fixture to `/hook/{SECRET_PATH}` with bearer
4. `scripts/assert_vm.sh` queries vm api and asserts z2==600

all of this runs **inside codex** or locally; no lan, no tunnel.

---

## 6) grafana (after mvp)

* add datasource `victoria-metrics` at `http://vm:8428`.
* starter panels:

  * weekly zone time (hrs, stacked): `sum by (zone)(increase(zone_seconds_total[1w]))/3600`
  * z2+ hours: `sum(increase(zone_seconds_total{zone=~"z2|z3|z4|z5"}[1w]))/3600`
  * hr trend (last 24h): `heart_rate_bpm`

---

## 7) trmnl e‑ink (later, but planned)

* **bespoke renderer**: query vm (`/api/v1/query_range`) and draw stark b/w png sized to your trmnl resolution; host it behind your tunnel; point trmnl’s image plugin at that url.
* keep typography huge (numerics) + minimal sparklines; e‑ink loves contrast.

---

## 8) networking (prod only)

* add `cloudflared` service; map public hostname → `http://api:8000`.
* keep host binds to `127.0.0.1`; the tunnel is the only ingress.

---

## 9) deployment to the pi (after sandbox is green)

1. `ssh` to the pi; install docker + compose; enable cgroup memory if needed.
2. clone repo to `/opt/fitness-stack`.
3. create real `.env` with long `AUTH_TOKEN`, `SECRET_PATH`, zones config, tunnel token.
4. `docker compose up -d`.
5. point **hae** to `https://<your-tunnel>/hook/${SECRET_PATH}` with bearer header; cadence 5–10 min.
6. verify vm has points; then wire grafana and (later) trmnl renderer.

---

## 10) security & ops (even in mvp)

* bearer token + secret path; reject without both.
* write **raw ndjson first**, then transform → vm (replayable).
* idempotency: dedupe key = sha256(`type|start|end|value|source|device`).
* caps: mem/cpu per container; bind only to loopback on host; tunnel for public.
* retention: vm `-retentionPeriod=5y` (tune later). back up volumes (`raw`, vm, grafana if used).

---

## 11) agents.md (what codex follows)

```
# project playbook for agents

## goals
- mvp: ingest hr fixture -> vm (zone_seconds_total + heart_rate_bpm), assert z2=600

## commands
- make up / make down / make test / make seed

## env
- copy .env.example -> .env (tests only)

## tests
- unit: tests/test_transform.py
- e2e: compose up -> wait_ready -> post_fixture -> assert_vm

## prs
- keep diffs small; maintain tests green; expand fixtures incrementally (workouts, sleep) after mvp
```

---

## 12) faq (quick hits)

* **do i need github actions now?** no. use codex only. add gha later if you want scheduled builds or multi‑arch pushes.
* **what’s e2e again?** bring up compose in a sandbox, post a fixture to your api, and assert vm numbers — no lan, no phone.
* **can i dev locally?** yes, vscode works fine; but codex can scaffold+run the whole thing if you don’t want local setup yet.
* **how do agents “remember”?** they don’t. vm on the pi is persistent; agents are stateless per task; they use fixtures.

---

**done (mvp‑first version).** next milestone after hr: add workouts (count/distance) and sleep (stage seconds), then grafana and trmnl pngs.


