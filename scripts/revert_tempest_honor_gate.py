#!/usr/bin/env python3
"""Revert the q_tempest opening gate from honour <= 3 back to <= 2.

apply_tempest_honor_gate.py raised it on the strength of a measurement showing
honour never dropped that low. The measurement was wrong: neither harness
imported ai.js, so no seat in any run had actually played -- no economy, builds,
research, diplomacy or contests -- which is why honour never moved.

With the AI playing, 18 of 24 seat-campaigns dip to honour <= 2 and 13 bottom
out at -12, and all five q_tempest beats reach at the unchanged gate on 6/6
boards and 4/4 seats by rounds 9-16. The raise bought two seat-campaigns and was
a content change made on a broken instrument. Putting it back.

The gate occurs in exactly one place in the corpus; asserted, not assumed.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "remnant_content_consolidated_rev2.json"

BEAT = "qb_tem_1"
FROM, TO = 3, 2


def honor_clauses(node, path="", found=None):
    if found is None:
        found = []
    if isinstance(node, dict):
        left = node.get("left")
        if (isinstance(left, dict) and isinstance(left.get("score"), dict)
                and left["score"].get("kind") == "honor"):
            found.append((path, node))
        for k, v in node.items():
            honor_clauses(v, path + "/" + str(k), found)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            honor_clauses(v, path + "/%d" % i, found)
    return found


def main():
    raw = CONTENT.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert json.dumps(data, indent=1, ensure_ascii=False) == raw, \
        "round-trip is not byte-identical; refusing to write"

    corpus = honor_clauses(data)
    assert len(corpus) == 1, "expected exactly 1 honour clause, found %d" % len(corpus)

    beat = next(b for b in data["quest_beats"] if b["id"] == BEAT)
    clauses = honor_clauses(beat.get("deliverCondition"))
    assert len(clauses) == 1, "expected 1 honour clause on %s" % BEAT
    _, clause = clauses[0]

    if clause["right"] == TO:
        print("already reverted (%s honour gate is <= %d); nothing to do" % (BEAT, TO))
        return 0
    assert clause["op"] == "lte" and clause["right"] == FROM, \
        "expected lte %d, found %s %r" % (FROM, clause["op"], clause["right"])

    before = {k: len(v) for k, v in data.items() if isinstance(v, list)}
    clause["right"] = TO
    assert before == {k: len(v) for k, v in data.items() if isinstance(v, list)}

    CONTENT.write_text(
        json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n"
    )
    print("%s honour gate: <= %d -> <= %d (reverted)" % (BEAT, FROM, TO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
