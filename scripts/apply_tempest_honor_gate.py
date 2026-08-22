#!/usr/bin/env python3
"""Raise the q_tempest opening gate from honour <= 2 to honour <= 3.

Players start at honour 4, so a <= 2 gate needed two dishonourable acts before
qb_tem_1 would deliver at all; the other four beats of q_tempest were blocked by
consequence, since a quest whose opener never places can never start. Ruled
value change: 2 -> 3.

The gate occurs in exactly one place in the corpus. This script asserts that
rather than assuming it, and refuses to write if it finds any other occurrence.

Touches one integer. No prose, no effect, no table count changes. Written back
with the source file's 1-space indent and no trailing newline.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "remnant_content_consolidated_rev2.json"

BEAT = "qb_tem_1"
OLD, NEW = 2, 3


def honor_clauses(node, path="", found=None):
    """Every {op, left:{score:{kind:honor}}, right:N} clause anywhere in the tree."""
    if found is None:
        found = []
    if isinstance(node, dict):
        left = node.get("left")
        if (
            isinstance(left, dict)
            and isinstance(left.get("score"), dict)
            and left["score"].get("kind") == "honor"
        ):
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
    assert len(corpus) == 1, \
        "expected exactly 1 honour clause in the corpus, found %d: %s" % (
            len(corpus), [p for p, _ in corpus])

    beat = next(b for b in data["quest_beats"] if b["id"] == BEAT)
    clauses = honor_clauses(beat.get("deliverCondition"))
    assert len(clauses) == 1, "expected 1 honour clause on %s, found %d" % (BEAT, len(clauses))

    _, clause = clauses[0]
    if clause["right"] == NEW:
        print("already applied (%s honour gate is <= %d); nothing to do" % (BEAT, NEW))
        return 0
    assert clause["op"] == "lte", "expected op 'lte', found %r" % clause["op"]
    assert clause["right"] == OLD, "expected right == %d, found %r" % (OLD, clause["right"])

    before_counts = {k: len(v) for k, v in data.items() if isinstance(v, list)}
    clause["right"] = NEW
    after_counts = {k: len(v) for k, v in data.items() if isinstance(v, list)}
    assert before_counts == after_counts, "table counts moved; refusing to write"

    CONTENT.write_text(
        json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n"
    )
    print("%s honour gate: <= %d -> <= %d" % (BEAT, OLD, NEW))
    return 0


if __name__ == "__main__":
    sys.exit(main())
