from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator, Dict, Any


def iter_background_metrics(base_path: Path) -> Iterator[Dict[str, Any]]:
    """Yield background metric records from sample files.

    Each record includes ``name``, ``units``, ``date`` and ``qty`` when
    available. Files are read in sorted order to keep iteration stable.
    """
    metrics_dir = base_path / "Background Health Metrics"
    for path in sorted(metrics_dir.glob("*.json")):
        with path.open() as f:
            payload = json.load(f)
        for metric in payload.get("data", {}).get("metrics", []):
            name = metric.get("name")
            units = metric.get("units")
            for entry in metric.get("data", []):
                record = {"name": name, "units": units}
                record.update(entry)
                yield record


def iter_workout_heart_rate(base_path: Path) -> Iterator[Dict[str, Any]]:
    """Yield heart-rate samples from workout files."""
    workouts_dir = base_path / "Workout Data"
    for path in sorted(workouts_dir.glob("*.json")):
        with path.open() as f:
            payload = json.load(f)
        for workout in payload.get("data", {}).get("workouts", []):
            wid = workout.get("id")
            for hr in workout.get("heartRateData", []):
                record = {"workout_id": wid}
                record.update(hr)
                yield record
