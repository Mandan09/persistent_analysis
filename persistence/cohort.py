"""Exhibit 1 cohort rules (R1-R4) and the six-month persistence measure."""
from dataclasses import dataclass

import pandas as pd


# The choices that define the cohort; defaults match the original method.
@dataclass(frozen=True)
class Rules:
    gap: int = 60
    lookback: int = 365
    lookforward: int = 365
    horizon: int = 182


# A whole number of days as a Timedelta.
def days(n):
    return pd.Timedelta(int(n), unit="D")


# Days as a readable month count: 365 -> "12 months".
def months(n):
    return f"{round(n / 30.4)} months"


# R1: each patient's index date is their first observed fill.
def index_dates(fills):
    return fills.groupby("patient_id").fill_date.min().rename("index_date")


# R4: days until supply ran out before a gap longer than `gap`; stopped=False means still on therapy when follow-up ended.
def days_on_therapy(fills, index, follow_end, gap):
    covered = index
    for day, supply in zip(fills.fill_date, fills.days_supply):
        if (day - covered).days > gap:
            return (covered - index).days, True
        covered = max(covered, day) + days(supply)
    if (follow_end - covered).days > gap:
        return (covered - index).days, True
    return (follow_end - index).days, False


# Applies R1-R3, measures R4 for everyone kept, and returns the cohort plus patient counts after each rule.
def build_cohort(fills, enrolment, rules=Rules()):
    fills = fills.sort_values(["patient_id", "fill_date"])
    funnel = [("All patients", len(enrolment))]
    df = enrolment.join(index_dates(fills), on="patient_id", how="inner")
    funnel.append(("Filled the drug at least once", len(df)))
    df = df[df.start <= df.index_date - days(rules.lookback)]
    funnel.append((f"Insured {months(rules.lookback)} before first fill", len(df)))
    df = df[df.end >= df.index_date + days(rules.lookforward)]
    funnel.append((f"Insured {months(rules.lookforward)} after first fill" if rules.lookforward
                   else "No insurance needed after first fill", len(df)))
    by_patient = dict(tuple(fills.groupby("patient_id")))
    out = [days_on_therapy(by_patient[r.patient_id], r.index_date, r.end, rules.gap) for r in df.itertuples()]
    df = df.assign(days_on=[o[0] for o in out], stopped=[o[1] for o in out])
    return df.reset_index(drop=True), funnel


# R4 headline: share still on therapy at the horizon; anyone whose follow-up ended earlier counts as not persistent.
def persistent_share(cohort, horizon=182):
    return (cohort.days_on >= horizon).mean()
