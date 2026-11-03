"""Runs the question set against the assistant and prints a score."""
from pathlib import Path

import yaml

from assistant.agent import ask


# True if the reply does what the question expects.
def grade(case, reply):
    if case["expect"] == "decline":
        return reply.declined
    return (not reply.declined and bool(set(case["cite"]) & set(reply.citations))
            and all(s in reply.answer for s in case.get("contains", [])))


# Asks every question and prints pass or fail with the citations used.
def main():
    cases = yaml.safe_load((Path(__file__).parent / "questions.yaml").read_text())
    passed = 0
    for case in cases:
        reply = ask(case["q"])
        ok = grade(case, reply)
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  {case['expect']:7} {case['q']}  {reply.citations}")
    print(f"\n{passed}/{len(cases)} passed")


if __name__ == "__main__":
    main()
