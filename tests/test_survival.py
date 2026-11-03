import pandas as pd

from persistence.cohort import persistent_share
from persistence.survival import curve, share_at


# A stays on, B stops on day 100, C's insurance ends on day 50.
COHORT = pd.DataFrame({"days_on": [400, 100, 50], "stopped": [False, True, False]})


# Censored C is dropped from the risk set instead of counted as stopped: 1/2, not 1/3.
def test_censoring_differs_from_naive_share():
    assert round(persistent_share(COHORT), 3) == 0.333
    assert share_at(COHORT, 182) == 0.5


# The curve starts at 100% and never goes up.
def test_curve_shape():
    shares = [s for _, s in curve(COHORT)]
    assert shares[0] == 1.0
    assert all(a >= b for a, b in zip(shares, shares[1:]))
