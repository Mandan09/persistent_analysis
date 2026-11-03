from persistence.generate import generate


# Same seed must give identical tables.
def test_reproducible():
    a, b = generate(500, seed=1), generate(500, seed=1)
    assert all(x.equals(y) for x, y in zip(a, b))


# Every fill falls inside the patient's insurance period and has a valid supply.
def test_fills_within_enrolment():
    fills, enrol, _ = generate(500)
    m = fills.merge(enrol, on="patient_id")
    assert ((m.fill_date >= m.start) & (m.fill_date <= m.end)).all()
    assert fills.days_supply.isin([30, 90]).all()


# Some patients get a prescription but never fill it.
def test_abandoners_exist():
    fills, _, rx = generate(500)
    assert (~rx.patient_id.isin(fills.patient_id)).any()
