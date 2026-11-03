"""Kaplan-Meier time-to-discontinuation for a cohort."""
from lifelines import KaplanMeierFitter


# Fits Kaplan-Meier on days_on; patients whose follow-up ended early are censored, not counted as stopped.
def fit(cohort):
    return KaplanMeierFitter().fit(cohort.days_on, event_observed=cohort.stopped)


# Share still on therapy at a given day.
def share_at(cohort, day=182):
    return float(fit(cohort).predict(day))


# Curve as (day, share) points from day 0 to `until`, ready for a chart.
def curve(cohort, until=365, step=7):
    days = list(range(0, until + 1, step))
    return list(zip(days, fit(cohort).survival_function_at_times(days).round(4).tolist()))
