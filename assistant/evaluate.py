"""Stress-tests the assistant with the question set and prints a score per category."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

from assistant.agent import ask


# True if the reply does what the case expects.
def grade(case, reply):
    cited = bool(set(case["cite"]) & set(reply.citations)) if "cite" in case else bool(reply.citations)
    if case["expect"] == "decline":
        return reply.declined
    if case["expect"] == "either":
        return reply.declined or cited
    numbers = [[n] if isinstance(n, str) else n for n in case.get("numbers", [])]
    return not reply.declined and cited and all(any(n in reply.answer for n in options) for options in numbers)


# Plays any earlier turns of the chat first, then asks the case's question.
def run(case):
    history = []
    for q in case.get("history", []):
        history.append((q, ask(q, history).answer))
    return case, ask(case["q"], history)


# Runs every case in parallel and prints failures plus a score per category.
def main():
    groups = yaml.safe_load((Path(__file__).parent / "questions.yaml").read_text())
    cases = [{**c, "type": t} for t, items in groups.items() for c in items]
    with ThreadPoolExecutor(8) as pool:
        results = list(pool.map(run, cases))
    total, passed = Counter(), Counter()
    for case, reply in results:
        ok = grade(case, reply)
        total[case["type"]] += 1
        passed[case["type"]] += ok
        if not ok:
            print(f"FAIL [{case['type']}] {case['q']}\n     -> {reply.answer[:200]} {reply.citations}")
    print()
    for t in total:
        print(f"{t:14} {passed[t]}/{total[t]}")
    print(f"\nTotal {sum(passed.values())}/{sum(total.values())}")


if __name__ == "__main__":
    main()
