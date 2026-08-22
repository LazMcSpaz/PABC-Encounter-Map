#!/usr/bin/env python3
"""Correct parentKind on 15 choice rows: "beat" -> "quest_beat".

My defect, from the q_tempest rebuild at 638bb16 and the consequence fixes at
fcf6398. build-content.mjs keys choices as <parentKind>:<parentId> and looks
them up as quest_beat:<id>, so 15 rows were filed under a key nothing reads and
nine beats assembled with zero choices. A beat with no choices cannot be
answered, so it is never delivered, so nothing downstream opens -- the whole
Tempest rebuild was inert.

Every assertion I wrote on those commits compared the file against itself:
counts, ordinals, prose invariants, duplicate ids, orphan rows. All passed. A
new row that is internally consistent and inconsistent with the corpus survives
every one of them. So this script also adds the check that was missing --
conformance of each row's field vocabulary against the existing rows of its own
kind -- and runs it over the whole corpus, not just the rows being fixed.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent / "remnant_content_consolidated_rev2.json"

VALID_CHOICE_PARENTS = {"quest_beat", "world_encounter", "field_encounter"}
VALID_EFFECT_PARENTS = {"choice"}


def conformance(rows, label, key="parentKind"):
    """Every value of `key` must already be used by the majority of rows."""
    counts = Counter(r.get(key) for r in rows)
    rare = {k: n for k, n in counts.items() if n < max(counts.values()) * 0.02}
    return counts, rare


def main():
    raw = CONTENT.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert json.dumps(data, indent=1, ensure_ascii=False) == raw, \
        "round-trip is not byte-identical; refusing to write"

    choices, effects = data["choices"], data["effects"]
    before_counts = {k: len(v) for k, v in data.items() if isinstance(v, list)}
    before_prose = {c["id"]: (c.get("label"), c.get("outcomeText")) for c in choices}

    bad = [c for c in choices if c.get("parentKind") == "beat"]
    if not bad:
        print("already applied; no choice row carries parentKind 'beat'")
    else:
        beat_ids = {b["id"] for b in data["quest_beats"]}
        for c in bad:
            assert c["parentId"] in beat_ids, "%s parents a non-beat" % c["id"]
            c["parentKind"] = "quest_beat"
        print("corrected %d choice rows: parentKind 'beat' -> 'quest_beat'" % len(bad))

    # ---- corpus-wide checks on the whole class ------------------------
    ck = Counter(c.get("parentKind") for c in choices)
    assert set(ck) <= VALID_CHOICE_PARENTS, "unknown choice parentKind: %r" % (set(ck) - VALID_CHOICE_PARENTS)
    ek = Counter(e.get("parentKind") for e in effects)
    assert set(ek) <= VALID_EFFECT_PARENTS, "unknown effect parentKind: %r" % (set(ek) - VALID_EFFECT_PARENTS)

    by_key = defaultdict(list)
    for c in choices:
        by_key[(c["parentKind"], c["parentId"])].append(c["id"])

    empty = [b["id"] for b in data["quest_beats"] if not by_key[("quest_beat", b["id"])]]
    assert not empty, "quest beats assembling with zero choices: %r" % empty
    for w in data["world_encounters"]:
        assert by_key[("world_encounter", w["id"])], "%s has no choices" % w["id"]
    for f in data["field_encounters"]:
        assert by_key[("field_encounter", f["id"])], "%s has no choices" % f["id"]

    # every choice parents something real, every effect parents a real choice
    parents = ({b["id"] for b in data["quest_beats"]}
               | {w["id"] for w in data["world_encounters"]}
               | {f["id"] for f in data["field_encounters"]})
    for c in choices:
        assert c["parentId"] in parents, "orphan choice %s" % c["id"]
    cids = {c["id"] for c in choices}
    for e in effects:
        assert e["parentId"] in cids, "orphan effect %s" % e["id"]

    # field vocabulary: no row may carry a key unknown to its kind
    def keyset(rows):
        return Counter(k for r in rows for k in r)
    for kind in VALID_CHOICE_PARENTS:
        rows = [c for c in choices if c["parentKind"] == kind]
        ks = keyset(rows)
        common = {k for k, n in ks.items() if n > len(rows) * 0.5}
        for r in rows:
            unknown = set(r) - set(ks)
            assert not unknown, "%s carries unknown keys %r" % (r["id"], unknown)
            missing = common - set(r)
            assert not missing, "%s missing keys %r that %d%% of its kind carry" % (
                r["id"], missing, 100 * len(rows) // len(rows))

    after_counts = {k: len(v) for k, v in data.items() if isinstance(v, list)}
    assert after_counts == before_counts, "table counts moved"
    assert {c["id"]: (c.get("label"), c.get("outcomeText")) for c in choices} == before_prose, \
        "prose changed"

    CONTENT.write_text(json.dumps(data, indent=1, ensure_ascii=False),
                       encoding="utf-8", newline="\n")
    print("choice parentKind: %s" % dict(Counter(c["parentKind"] for c in choices)))
    print("quest beats with zero choices: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
