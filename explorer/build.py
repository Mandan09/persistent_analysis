"""Builds explorer.html and the deck with results.json baked in, so they open without a server."""
from pathlib import Path

ROOT = Path(__file__).parent.parent
PAGES = {"explorer/template.html": "explorer/explorer.html", "deck/template.html": "deck/deck.html"}


# Injects the results into each template and writes the finished page.
def build(results="data/results.json"):
    data = Path(results).read_text()
    for src, out in PAGES.items():
        (ROOT / out).write_text((ROOT / src).read_text().replace("__RESULTS__", data))


if __name__ == "__main__":
    build()
