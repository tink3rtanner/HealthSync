from pathlib import Path
from tools import scanners

BASE = Path("data_samples")


def test_background_metric_names():
    records = list(scanners.iter_background_metrics(BASE))
    names = {r["name"] for r in records}
    assert len(records) > 0
    assert names == {
        'apple_exercise_time',
        'heart_rate',
        'heart_rate_variability',
        'resting_heart_rate',
        'running_speed',
        'sleep_analysis',
        'swimming_distance',
        'walking_heart_rate_average',
        'walking_running_distance',
    }


def test_workout_heart_rate_counts():
    records = list(scanners.iter_workout_heart_rate(BASE))
    counts = {}
    for r in records:
        counts.setdefault(r['workout_id'], 0)
        counts[r['workout_id']] += 1
    assert sorted(counts.values()) == [47, 76, 93, 128]
