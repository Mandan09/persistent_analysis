import itertools

from persistence.sensitivity import GAPS, LOOKBACKS, LOOKFORWARDS, one_at_a_time


# Picks exactly the rows where one rule moves and the other two stay at the original values.
def test_one_at_a_time_rows():
    runs = [{"gap": g, "lookback": b, "lookforward": f, "km_6m": 0.5}
            for g, b, f in itertools.product(GAPS, LOOKBACKS, LOOKFORWARDS)]
    rows = one_at_a_time(runs)
    assert len(rows) == len(GAPS) + len(LOOKBACKS) + len(LOOKFORWARDS)
    assert {(r["rule"], r["value"]) for r in rows if r["rule"] == "gap"} == {("gap", g) for g in GAPS}
