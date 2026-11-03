import pandas as pd

from persistence.cohort import build_cohort, days, days_on_therapy

D0 = pd.Timestamp("2022-01-01")


# Runs R4 on hand-written fills given as (day, supply) pairs.
def run(fills, follow=400, gap=60):
    f = pd.DataFrame({"fill_date": [D0 + days(d) for d, _ in fills], "days_supply": [s for _, s in fills]})
    return days_on_therapy(f, D0, D0 + days(follow), gap)


# Aman refills every month and is still on therapy when follow-up ends.
def test_steady_patient_is_censored():
    assert run([(d, 30) for d in range(0, 360, 30)]) == (400, False)


# Gita stops after two fills; she stopped when her supply ran out on day 60.
def test_stopper():
    assert run([(0, 30), (30, 30)]) == (60, True)


# Sita's break is exactly 60 days: allowed under the 60-day rule, not under 59.
def test_gap_boundary():
    fills = [(0, 30), (30, 30)] + [(d, 30) for d in range(120, 360, 30)]
    assert run(fills, gap=60)[1] is False
    assert run(fills, gap=59) == (60, True)


# Farhan's 45-day break passes at 60 days but counts as stopping at 30.
def test_gap_length_changes_answer():
    fills = [(0, 30), (30, 30), (60, 30)] + [(d, 30) for d in range(135, 360, 30)]
    assert run(fills, gap=60)[1] is False
    assert run(fills, gap=30) == (90, True)


# Ravi's 90-day fills are 90 days apart but leave no gap.
def test_ninety_day_fills():
    assert run([(d, 90) for d in (0, 90, 180, 270)])[1] is False


# An early refill carries the leftover supply forward.
def test_early_refill_carries_over():
    assert run([(0, 30), (20, 30)]) == (60, True)


# Isha's insurance ends on day 70: unknown, so censored rather than stopped.
def test_insurance_end_is_censored():
    assert run([(0, 30), (30, 30)], follow=70) == (70, False)


# R2 drops patients without a year of history; R3 drops those without a year of follow-up.
def test_enrolment_rules():
    fills = pd.DataFrame({"patient_id": [1, 2, 3], "fill_date": [D0] * 3, "days_supply": [30] * 3})
    enrol = pd.DataFrame({"patient_id": [1, 2, 3],
                          "start": [D0 - days(400), D0 - days(100), D0 - days(400)],
                          "end": [D0 + days(400), D0 + days(400), D0 + days(100)]})
    cohort, funnel = build_cohort(fills, enrol)
    assert list(cohort.patient_id) == [1]
    assert [n for _, n in funnel] == [3, 3, 2, 1]
