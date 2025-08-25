from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Iterable
import json

try:  # optional dependency
    import requests  # type: ignore
    HAVE_REQUESTS = True
except Exception:  # pragma: no cover - network-restricted envs
    HAVE_REQUESTS = False
import urllib.request
import urllib.parse

from . import scanners

DT_FORMAT = "%Y-%m-%d %H:%M:%S %z"


def _parse_ts(value: str) -> int:
    """Return timestamp in nanoseconds for VictoriaMetrics."""
    return int(datetime.strptime(value, DT_FORMAT).timestamp() * 1_000_000_000)


def records(base_path: Path) -> Iterable[str]:
    """Generate line-protocol lines for all samples under ``base_path``."""
    for rec in scanners.iter_background_metrics(base_path):
        date = rec.get("date") or rec.get("start") or rec.get("startDate")
        qty = rec.get("qty") or rec.get("Avg")
        if date is None or qty is None:
            continue
        ts = _parse_ts(date)
        name = rec.get("name", "unknown").replace(" ", "_")
        yield f"background_metric,name={name} qty={float(qty)} {ts}"

    for rec in scanners.iter_workout_heart_rate(base_path):
        date = rec.get("date")
        qty = rec.get("qty") or rec.get("Avg")
        wid = rec.get("workout_id", "unknown")
        if date is None or qty is None:
            continue
        ts = _parse_ts(date)
        yield f"workout_heart_rate,workout_id={wid} qty={float(qty)} {ts}"


def send_to_vm(base_path: Path, base_url: str = "http://localhost:8428") -> None:
    """Send all sample records to VictoriaMetrics using line protocol."""
    data = "\n".join(records(base_path))
    if HAVE_REQUESTS:
        resp = requests.post(f"{base_url}/write", data=data)
        resp.raise_for_status()
    else:  # pragma: no cover - exercised when requests missing
        req = urllib.request.Request(
            f"{base_url}/write", data=data.encode("utf-8"), method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            resp.read()  # ensure request is made


def read_metric(base_url: str, metric: str) -> float:
    """Return the latest value for ``metric`` from VictoriaMetrics."""
    if HAVE_REQUESTS:
        resp = requests.get(f"{base_url}/api/v1/query", params={"query": metric})
        resp.raise_for_status()
        data = resp.json()
    else:  # pragma: no cover - exercised when requests missing
        url = f"{base_url}/api/v1/query?" + urllib.parse.urlencode({"query": metric})
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    results = data.get("data", {}).get("result", [])
    if not results:
        return float("nan")
    return float(results[0]["value"][1])


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Send samples to VictoriaMetrics")
    parser.add_argument("--base-url", default="http://localhost:8428")
    parser.add_argument("--data-path", default="data_samples")
    args = parser.parse_args(argv)
    send_to_vm(Path(args.data_path), args.base_url)


if __name__ == "__main__":
    main()
