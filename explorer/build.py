"""Builds explorer.html with results.json baked in, so it opens without a server."""
from pathlib import Path

HERE = Path(__file__).parent


# Injects the results into the template and writes explorer.html.
def build(results="data/results.json"):
    html = (HERE / "template.html").read_text().replace("__RESULTS__", Path(results).read_text())
    (HERE / "explorer.html").write_text(html)


if __name__ == "__main__":
    build()
