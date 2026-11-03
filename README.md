# Persistence analysis, rebuilt

A brand team was told that 68% of patients on a treatment-resistant depression drug are still on it after six months. The person who built that number left without writing down how, and the field team says patients stop much sooner. This repo rebuilds the analysis so anyone can see where the number comes from and what moves it.

It has four parts:

- **The rules as code.** The original cohort rules are written in Python and tested. Run on 5,000 synthetic patients, they give 70.1%, close to the reported 68%.
- **A curve instead of one number.** A Kaplan-Meier curve shows how many patients are still on therapy on each day of the first year. Patients whose insurance ends early are handled properly instead of being counted as stopped.
- **An explorer.** One web page with sliders for the rules. Move a slider and the curve, the headline number and the patient counts update.
- **An assistant.** You can ask it about the method in English or Hinglish. It answers only from the written method and the results, shows its sources, and declines anything else.

**What it shows:** the rule for how long a break between refills is allowed moves the number most. Allow 60 days and it is 70%. Allow 30 and it falls to 58%. Add the patients who were prescribed the drug but never filled it, and it lands near 48%. The 68% and the field team's view are both reasonable; they count different patients with different rules.

## Getting started

You need a Gemini API key for the assistant. Everything else runs without one.

### With Docker

```bash
cp .env.example .env        # put your GEMINI_API_KEY in .env
docker compose up --build
```

Open http://localhost:8000 for the explorer, or http://localhost:8000/deck for the 8-slide deck (use ← →). The build generates the data, runs the analysis and builds the page, so there is nothing else to set up. There is no database: the data is CSV files and the results are one JSON file, all rebuilt from a fixed seed.

### Without Docker

You need [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env                       # put your GEMINI_API_KEY in .env
uv run python -m persistence.generate      # synthetic data into data/
uv run python -m persistence.sensitivity   # every rule setting into data/results.json
uv run python -m explorer.build            # explorer/explorer.html
uv run uvicorn assistant.server:app        # http://127.0.0.1:8000
```

`explorer/explorer.html` also opens on its own by double-clicking it. Everything works except the assistant, which needs the server.

### Tests and evaluation

```bash
uv run pytest                           # 14 tests for the data, rules, curve and grid
uv run python -m assistant.evaluate     # 97 questions for the assistant (uses the API)
```

## Using the explorer

- **Longest break allowed:** a longer gap between refills counts as stopping. The original method uses 60 days.
- **Insurance needed after first fill:** keeps only patients we can follow for that long. The original uses 12 months.
- **Insurance needed before first fill:** shows the patient is new to the drug. The original uses 12 months.
- **Count patients who never filled:** adds the people doctors prescribed the drug to but who never picked it up. This is closer to what the field team sees.

The grey dashed line is always the original method, so you can see how far your setting has moved from it. **Ask about the method**, bottom right, opens the assistant. Click a numbered badge in an answer to read the exact rule or result it came from.

## How it is put together

```
persistence/   generate.py     synthetic fills, insurance periods, prescriptions
               cohort.py       the four rules and the patient funnel
               survival.py     Kaplan-Meier curve
               sensitivity.py  105 rule settings into data/results.json
explorer/      template.html   the page; build.py bakes the results into explorer.html and the deck
deck/          template.html   8-slide interactive deck, built to deck.html
assistant/     agent.py        prompt, sources, citation checks, model fallback
               server.py       serves the page and the streaming /ask endpoint
               questions.yaml  evaluation questions; evaluate.py runs them
tests/         unit tests
METHODOLOGY.md the method in plain language; the assistant cites it
SOLUTION.md    the full write-up: decisions, evaluation, limitations
```

## Decisions worth knowing

- **All numbers come from tested Python.** The page and the assistant only show precomputed results, so they can't drift from the tested code.
- **Breaks are measured from the day the medicine runs out,** not from the fill date. That way 90-day fills and early refills aren't mistaken for gaps.
- **The assistant can't make up a source.** Code drops any citation that doesn't exist and turns an answer with no real source into a decline.
- **The model is cheap on purpose.** It uses Gemini Flash with low reasoning, through LiteLLM, with Flash-Lite as a fallback. That costs about $0.009 per question, a third of the first version, and still answers all 97 test questions correctly. To change models, set `ASSISTANT_MODELS` in `.env`.

## Limits

- **The data is synthetic.** I tuned its settings by hand so the original rules land near 68%. Read the results as how the rules behave, not as the brand's real persistence.
- **The cohort is small.** With 739 patients the six-month number has roughly ±3 points of noise, so small effects, such as the look-back rule's, can't be told apart from noise.
- **The server is for local use only.** It has no login or rate limiting. Real patient data would need both, plus de-identified data and an enterprise LLM endpoint.

The details are in [SOLUTION.md](SOLUTION.md).
