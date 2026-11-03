# How the six-month persistence number is calculated

This is the plain-language write-up of the method that was never written down. Every section has an ID in brackets so the assistant and the slides can point back to it.

## [D1] Data

Synthetic pharmacy claims for 5,000 patients on one treatment-resistant depression drug, covering 2021 to 2024. Each claim records the patient, the date the prescription was filled and how many days of medicine it covered (30 or 90). A separate table records when each patient's insurance started and ended. A third table records prescriptions written by doctors, including ones that were never filled. The data is synthetic, so it shows how the rules behave, not the brand's real numbers.

## [R1] Index date: the first fill

A patient's analysis starts on the date of their first fill of the drug that we can see in the claims. Everything after is measured from this day.

## [R2] Look-back: 12 months of insurance before the first fill

A patient is only kept if their insurance covered the 12 months before the first fill. If we can see a year of history with no fills, we can be fairly sure this is a new patient and not someone who was already on the drug before their records start. Patients already on the drug tend to stay on it, so letting them in would push the number up.

## [R3] Look-forward: 12 months of insurance after the first fill

A patient is only kept if their insurance covered the 12 months after the first fill. This guarantees we can see their whole first year. The cost is that it keeps only patients with stable insurance, who also tend to be more stable on treatment, so it can push the number up. In this data it removes about half of the patients who pass R2.

## [R4] Persistence: still filling at 6 months with no gap over 60 days

We track how many days of medicine each patient has on hand. An early refill adds its supply on top of what is left, and a 90-day fill covers 90 days, so neither creates a gap. If the time between running out and the next fill is more than 60 days, the patient is counted as having stopped on the day their medicine ran out. A gap of exactly 60 days is allowed. A patient is persistent at 6 months (182 days) if they had not stopped by then.

## [C1] Time-to-discontinuation curve (Kaplan-Meier)

Instead of one number at 6 months, the curve shows the share still on therapy on every day of the first year. If a patient's insurance ends before we see them stop, we do not count them as stopped: we stop following them from that day (this is called censoring). That keeps patients with short records from dragging the number down unfairly.

## [N1] Naive share

The naive share counts anyone whose follow-up ended before 6 months as not persistent. It is shown next to the Kaplan-Meier number to show how much censoring matters when the look-forward rule is relaxed.

## [S1] Sensitivity analysis

The analysis is rerun for every combination of allowed gap (30, 60 or 90 days), look-back (6, 12 or 24 months) and look-forward (none, 6 or 12 months). The original method is gap 60, look-back 12 months and look-forward 12 months. Each run has an ID like S-60-365-365 (gap, look-back days, look-forward days).

## [F1] Why the field team sees patients stop sooner

Three things separate the field team's view from the claims number. First, the field team likely thinks of a month without medicine as stopping, which is closer to a 30-day gap than a 60-day one. Second, the look-forward rule keeps only patients with stable insurance. Third, some patients are prescribed the drug but never fill it; doctors and reps see them, but pharmacy claims never do. The explorer can count these never-filled patients as stopping on day 0.

## [L1] What this data cannot see

Free samples given before the first fill, medicine paid for in cash, medicine given in hospital, and whether a patient actually took the medicine they bought. Deaths are not recorded separately. None of these are in pharmacy claims.
