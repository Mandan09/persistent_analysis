"""Runs every rule combination and saves results.json for the explorer and the assistant."""
import itertools
import json
from pathlib import Path

from persistence.cohort import Rules, build_cohort, persistent_share
from persistence.generate import load
from persistence.survival import curve, share_at

GAPS, LOOKBACKS, LOOKFORWARDS = (30, 60, 90), (182, 365, 730), (0, 182, 365)
KEYS = ("gap", "lookback", "lookforward")
MONTHS = {1: 30, 3: 91, 6: 182, 9: 274, 12: 365}


# Runs one rule setting: funnel, six-month counts, Kaplan-Meier at each milestone month, and the curve.
def run(fills, enrolment, rules):
    cohort, funnel = build_cohort(fills, enrolment, rules)
    early = cohort.days_on < rules.horizon
    return {"gap": rules.gap, "lookback": rules.lookback, "lookforward": rules.lookforward,
            "patients": len(cohort), "funnel": funnel,
            "on_6m": int((~early).sum()), "stopped_6m": int((early & cohort.stopped).sum()),
            "censored_6m": int((early & ~cohort.stopped).sum()),
            "naive_6m": round(persistent_share(cohort), 4), "km_6m": round(share_at(cohort), 4),
            "km_months": {m: round(share_at(cohort, d), 4) for m, d in MONTHS.items()},
            "curve": curve(cohort)}


# Every combination of gap, look-back and look-forward.
def grid(fills, enrolment):
    return [run(fills, enrolment, Rules(gap=g, lookback=b, lookforward=f))
            for g, b, f in itertools.product(GAPS, LOOKBACKS, LOOKFORWARDS)]


# Rows where only one rule differs from the original, to show how far each rule moves the number.
def one_at_a_time(results):
    base = Rules()
    return [{"rule": k, "value": r[k], "km_6m": r["km_6m"]} for k in KEYS for r in results
            if all(r[o] == getattr(base, o) for o in KEYS if o != k)]


# Builds the full results file, including dataset counts and how many prescriptions were never filled.
def save(folder="data"):
    fills, enrolment, rx = load(folder)
    results = grid(fills, enrolment)
    never = ~rx.patient_id.isin(fills.patient_id)
    out = {"original": {k: getattr(Rules(), k) for k in KEYS},
           "dataset": {"patients": len(enrolment), "fills": len(fills), "prescriptions": len(rx),
                       "never_filled": int(never.sum())},
           "never_filled_share": round(float(never.mean()), 4),
           "one_at_a_time": one_at_a_time(results), "runs": results}
    Path(folder, "results.json").write_text(json.dumps(out))
    return out


if __name__ == "__main__":
    for row in save()["one_at_a_time"]:
        print(f"{row['rule']:12} {row['value']:4}  {row['km_6m'] * 100:5.1f}%")
