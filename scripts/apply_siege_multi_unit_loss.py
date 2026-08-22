#!/usr/bin/env python3
"""A failed storming of the Laker capital costs every column committed, not one.

The two qb_tem_wall storming choices carry a CONTEST whose onLose destroys a
unit. Both read `triggering-unit`, which resolves to exactly one unit -- so a
lost siege cost a single column however many the player marched, which is not
what the scene describes. Retargeted to `units-on-hex`, which resolves to every
unit the recipient has on the beat's hex.

Only these two. The other eleven ADJUST_BASE_STRENGTH effects are single-unit
consequences by design: the Baron's estate costs the column that went in, not
the army. The siege is the only multi-column commitment in the corpus.

Note for later: the engine's fallback when there is no hex context is a single
unit, matching `triggering-unit`, so an effect cannot become army-wide on a
technicality. Both beats here are `discovered`, so a unit is always standing on
the hex when they fire -- but anything applying this token to a `conditional`
beat, which resolves at round end with nobody standing anywhere, gets the
single-unit fallback rather than what it looks like it asked for.
"""
import json
import sys
from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent / "remnant_content_consolidated_rev2.json"

TARGETS = ["ef_tem_ws_contest", "ef_tem_wt_contest"]
OLD, NEW = "triggering-unit", "units-on-hex"


def all_abs(effects):
    """(effect id, amount, target) for every ADJUST_BASE_STRENGTH, however nested."""
    found = []

    def walk(node, eid):
        if isinstance(node, dict):
            if node.get("type") == "ADJUST_BASE_STRENGTH":
                p = node.get("params") or node.get("paramsJson") or {}
                found.append((eid, p.get("amount"), p.get("target")))
            for v in node.values():
                walk(v, eid)
        elif isinstance(node, list):
            for v in node:
                walk(v, eid)

    for e in effects:
        walk(e, e["id"])
    return sorted(found)


def main():
    raw = CONTENT.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert json.dumps(data, indent=1, ensure_ascii=False) == raw, \
        "round-trip is not byte-identical; refusing to write"

    effects = data["effects"]
    before_counts = {k: len(v) for k, v in data.items() if isinstance(v, list)}
    before_prose = ({b["id"]: b.get("text") for b in data["quest_beats"]},
                    {c["id"]: (c.get("label"), c.get("outcomeText")) for c in data["choices"]})
    before_abs = all_abs(effects)
    assert len(before_abs) == 13, "expected 13 ADJUST_BASE_STRENGTH, found %d" % len(before_abs)

    done = 0
    for eid in TARGETS:
        e = next(x for x in effects if x["id"] == eid)
        assert e["type"] == "CONTEST", "%s is %s" % (eid, e["type"])
        lose = e["paramsJson"]["onLose"]
        hits = [x for x in lose if x.get("type") == "ADJUST_BASE_STRENGTH"]
        assert len(hits) == 1, "%s has %d strength effects in onLose" % (eid, len(hits))
        p = hits[0]["params"]
        if p["target"] == NEW:
            continue
        assert p["target"] == OLD, "%s target is %r, not %r" % (eid, p["target"], OLD)
        assert p["amount"] == -99, "%s amount is %r" % (eid, p["amount"])
        p["target"] = NEW
        done += 1
    if not done:
        print("already applied; nothing to do")
        return 0

    # --- assertions -----------------------------------------------------
    after_abs = all_abs(effects)
    assert len(after_abs) == 13, "count moved"
    changed = [a for a, b in zip(before_abs, after_abs) if a != b]
    moved = {a[0] for a, b in zip(before_abs, after_abs) if a != b}
    assert moved == set(TARGETS), "changed the wrong effects: %r" % moved
    assert len(changed) == 2, "expected 2 changed rows, got %d" % len(changed)

    for eid, amount, target in after_abs:
        if eid in TARGETS:
            assert target == NEW, "%s did not take %s" % (eid, NEW)
        else:
            assert target == OLD, "%s drifted to %r" % (eid, target)

    # win branches, flags and routing untouched
    for eid, flag in ((TARGETS[0], "tempest_siege_failed"), (TARGETS[1], "tempest_turn_failed")):
        p = next(x for x in effects if x["id"] == eid)["paramsJson"]
        assert [x["params"]["flag"] for x in p["onLose"]
                if x["type"] == "SET_PLAYER_FLAG"] == [flag], eid
        assert p["onWin"], "%s lost its win branch" % eid

    assert {k: len(v) for k, v in data.items() if isinstance(v, list)} == before_counts, \
        "table counts moved"
    assert ({b["id"]: b.get("text") for b in data["quest_beats"]},
            {c["id"]: (c.get("label"), c.get("outcomeText")) for c in data["choices"]}) \
        == before_prose, "prose changed"

    CONTENT.write_text(json.dumps(data, indent=1, ensure_ascii=False),
                       encoding="utf-8", newline="\n")
    print("retargeted %d siege onLose effects: %s -> %s" % (done, OLD, NEW))
    print("the other 11 ADJUST_BASE_STRENGTH still read %s" % OLD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
