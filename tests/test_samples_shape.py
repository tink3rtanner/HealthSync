import glob
import json


def test_background_metrics_structure():
    for path in glob.glob("data_samples/Background Health Metrics/*.json"):
        with open(path) as f:
            payload = json.load(f)
        assert "data" in payload and "metrics" in payload["data"]
        metrics = payload["data"]["metrics"]
        assert metrics, path
        for metric in metrics:
            assert {"name", "units", "data"} <= metric.keys()
            for sample in metric["data"]:
                assert any(
                    key in sample for key in ("qty", "Avg", "value")
                )
                assert any(
                    key in sample for key in ("date", "start", "startDate")
                )


def test_workout_data_structure():
    path = "data_samples/Workout Data/HealthAutoExport-2025-34.json"
    with open(path) as f:
        payload = json.load(f)
    workouts = payload["data"]["workouts"]
    assert len(workouts) == 4
    for workout in workouts:
        assert "id" in workout
        assert workout.get("heartRateData"), workout["id"]
