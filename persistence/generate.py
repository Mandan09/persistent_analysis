"""Synthetic pharmacy claims, enrolment and prescriptions for one CNS drug."""
from pathlib import Path

import numpy as np
import pandas as pd

DATA_START, DATA_END = pd.Timestamp("2021-01-01"), pd.Timestamp("2024-12-31")
SPAN = (DATA_END - DATA_START).days


# Simulates one patient as day offsets from DATA_START; None if they never appear in our data.
def _patient(rng):
    unstable = rng.random() < 0.35
    start = int(rng.integers(-700, SPAN - 180))
    joined_late = rng.random() < 0.2
    enrol_from = start + int(rng.integers(-300, 200)) if joined_late else start - int(rng.integers(0, 1500))
    enrol_to = start + int(rng.exponential(400 if unstable else 1500))
    enrolment = (max(enrol_from, 0), min(enrol_to, SPAN))
    if enrolment[0] >= enrolment[1]:
        return None
    if rng.random() < 0.12:
        return start, enrolment, []
    stop = start + rng.weibull(0.7) * (120 if unstable else 600)
    supply = 90 if rng.random() < 0.15 else 30
    pause_at = start + rng.uniform(0, stop - start) if rng.random() < 0.15 else None
    fills, day = [], start
    while day < stop:
        fills.append((day, supply))
        day += supply + int(rng.integers(-5, 11))
        if pause_at is not None and day > pause_at:
            day, pause_at = day + int(rng.integers(20, 90)), None
    return start, enrolment, [f for f in fills if enrolment[0] <= f[0] <= enrolment[1]]


# Turns day-offset columns into real dates.
def _dates(df, *cols):
    for c in cols:
        df[c] = DATA_START + pd.to_timedelta(df[c], unit="D")
    return df


# Builds fills, enrolment and prescriptions for n patients; same seed gives the same data.
def generate(n=5000, seed=7):
    rng = np.random.default_rng(seed)
    fills, enrol, rx = [], [], []
    while len(enrol) < n:
        p = _patient(rng)
        if p is None:
            continue
        pid, (start, (a, b), pfills) = len(enrol) + 1, p
        enrol.append((pid, a, b))
        if 0 <= start <= SPAN:
            rx.append((pid, start))
        fills += [(pid, d, s) for d, s in pfills]
    return (
        _dates(pd.DataFrame(fills, columns=["patient_id", "fill_date", "days_supply"]), "fill_date"),
        _dates(pd.DataFrame(enrol, columns=["patient_id", "start", "end"]), "start", "end"),
        _dates(pd.DataFrame(rx, columns=["patient_id", "written_date"]), "written_date"),
    )


# Writes fills.csv, enrolment.csv and prescriptions.csv into out.
def save(out="data", **kw):
    Path(out).mkdir(exist_ok=True)
    for name, df in zip(("fills", "enrolment", "prescriptions"), generate(**kw)):
        df.to_csv(Path(out) / f"{name}.csv", index=False)


if __name__ == "__main__":
    save()
