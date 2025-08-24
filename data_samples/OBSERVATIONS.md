# Data Sample Observations

## Background Health Metrics
- Seven JSON files dated 2025-08-18 through 2025-08-24.
- Nine metric names observed: `apple_exercise_time`, `heart_rate`, `heart_rate_variability`, `resting_heart_rate`, `running_speed`, `sleep_analysis`, `swimming_distance`, `walking_heart_rate_average`, `walking_running_distance`.
- Entries include numeric `qty`, `source`, and timestamps such as `date`, `start`/`end`, or `startDate`/`endDate`.
- Overall timestamp range: 2025-08-17 23:07:33+01:00 to 2025-08-24 19:27:18+01:00.

## Workout Data
- One JSON file containing four workouts.
- Each workout has an `id`, `start` and `end` times, and arrays like `heartRateData`, `activeEnergy`, and `walkingAndRunningDistance`.
- Heart rate sample counts per workout: 128, 93, 76, and 47.
- Timestamps follow the `%Y-%m-%d %H:%M:%S %z` format.

## Common Fields
- Most samples include `qty`, `units`, and `source` fields.
- Timestamps may appear under `date`, `start`, `end`, `startDate`, or `endDate`.

## Reading & Validation Tips
- Load files with Python's `json` module and iterate over `data["metrics"]` or `data["workouts"]`.
- Ensure each sample has a `qty` and at least one timestamp field.
- Parse timestamps using `datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")`.
