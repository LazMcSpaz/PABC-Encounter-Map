#!/usr/bin/env python3
"""Declare subjectFaction on six quests, and make the Tempest siege a real deadline.

Field specs read from src/game/quests.js and src/game/deferred.js -- the engine
contract does not document any of the four yet, the same lag that applied to the
triggering-unit token.

1. subjectFaction is a QUEST-level field, checked in offerQuests: a quest
   declaring one is never offered to that faction and is offered to everyone
   else. The six values come from reading the beat prose, not the ids or gates.

2. The deadline fields sit beside delayRounds and effects inside a
   QUEUE_DEFERRED's params:
       label            player-facing HUD text
       visible          show a countdown to the queuer
       satisfiedIfFlag  the condition being raced
       onMissed         what runs instead when it is not met
   `effects` becomes the MET branch. The three rider packets now race the
   player to the wall: met records that they made it, missed sets
   tempest_siege_over, which is what routes qb_tem_4_paid and qb_tem_4_none.
   Dropping tempest_siege_over from the met branch is safe and tightens the
   gates -- both of those beats already require NOT fought_for / NOT
   fought_against / NOT walked_away, so an arriver could never match them.

   tempest_reached_the_wall is added to all three qb_tem_wall choices, so the
   deadline means exactly what it says rather than relying on the aftermath
   gates to sort it out afterwards.

The redundant `ne active lakers` opener gates on q_works and q_runner are left
in place deliberately -- see the report; removing them is a separate call.
"""
import json
import sys
from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent / "remnant_content_consolidated_rev2.json"

SUBJECTS = {
    "q_caravan": "versari",
    "q_massacre": "goldgrass",
    "q_works": "lakers",
    "q_runner": "lakers",
    "q_croppers": "plainers",
    "q_baron": "plainers",
}
FACTIONS = {"versari", "goldgrass", "lakers", "plainers"}

DEADLINE_PACKETS = ["ef_tem_s5_deadline", "ef_tem_s10_deadline", "ef_tem_sn_deadline"]
WALL_CHOICES = ["ch_tem_wall_start", "ch_tem_wall_turn", "ch_tem_wall_leave"]
REACHED = "tempest_reached_the_wall"

def sf(flag):
    return {"type": "SET_PLAYER_FLAG",
            "params": {"flag": flag, "value": True, "duration": "permanent",
                       "target": "active"}}

def main():
    raw = CONTENT.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert json.dumps(data, indent=1, ensure_ascii=False) == raw, \
        "round-trip is not byte-identical; refusing to write"

    quests, effects, choices = data["quests"], data["effects"], data["choices"]
    before = {k: len(v) for k, v in data.items() if isinstance(v, list)}
    before_prose = ({b["id"]: b.get("text") for b in data["quest_beats"]},
                    {c["id"]: (c.get("label"), c.get("outcomeText")) for c in choices})

    if any(q.get("subjectFaction") for q in quests):
        print("already applied; nothing to do")
        return 0

    # ---- 1. subjectFaction --------------------------------------------
    by_id = {q["id"]: q for q in quests}
    for qid, fid in SUBJECTS.items():
        assert qid in by_id, "no such quest %s" % qid
        assert fid in FACTIONS, "unknown faction %s" % fid
        assert "subjectFaction" not in by_id[qid]
        by_id[qid]["subjectFaction"] = fid

    # ---- 2. the wall records arrival ----------------------------------
    e_anchor = max(i for i, e in enumerate(effects) if e["parentId"].startswith("ch_tem")) + 1
    new_e = []
    for cid in WALL_CHOICES:
        assert any(c["id"] == cid for c in choices), "no such choice %s" % cid
        nxt = max(e["ordinal"] for e in effects if e["parentId"] == cid) + 1
        new_e.append({"id": "ef_%s_reached" % cid[3:], "parentKind": "choice",
                      "parentId": cid, "ordinal": nxt, "type": "SET_PLAYER_FLAG",
                      "paramsJson": {"flag": REACHED, "value": True,
                                     "duration": "permanent", "target": "active"}})
    effects[e_anchor:e_anchor] = new_e

    # ---- 3. the rider packets become deadlines ------------------------
    for eid in DEADLINE_PACKETS:
        e = next(x for x in effects if x["id"] == eid)
        p = e["paramsJson"]
        assert e["type"] == "QUEUE_DEFERRED" and p["delayRounds"] == 4, p
        assert [x["params"]["flag"] for x in p["effects"]] == ["tempest_siege_over"], p
        p["effects"] = [sf("tempest_reached_in_time")]
        p["label"] = "The siege at the Laker capital"
        p["visible"] = True
        p["satisfiedIfFlag"] = REACHED
        p["onMissed"] = [sf("tempest_siege_over")]

    return _verify(data, before, before_prose)


def _verify(data, before, before_prose):
    quests, effects, choices = data["quests"], data["effects"], data["choices"]
    after = {k: len(v) for k, v in data.items() if isinstance(v, list)}
    assert after["effects"] == before["effects"] + 3, after
    for k in ("quests", "quest_beats", "quest_beat_prereqs", "choices",
              "world_encounters", "field_encounters"):
        assert after[k] == before[k], "%s moved" % k
    assert ({b["id"]: b.get("text") for b in data["quest_beats"]},
            {c["id"]: (c.get("label"), c.get("outcomeText")) for c in choices}) == before_prose, \
        "prose changed"

    # exactly the six, and only valid faction ids
    declared = {q["id"]: q["subjectFaction"] for q in quests if q.get("subjectFaction")}
    assert declared == SUBJECTS, declared
    assert set(declared.values()) <= FACTIONS

    # row-shape conformance: quests either carry the field or do not, no other key moved
    keys = {frozenset(q) for q in quests}
    assert keys <= {frozenset(["id", "mode", "title"]),
                    frozenset(["id", "mode", "title", "subjectFaction"])}, keys

    # the deadline packets are well formed and agree with each other
    for eid in DEADLINE_PACKETS:
        p = next(x for x in effects if x["id"] == eid)["paramsJson"]
        for k in ("label", "visible", "satisfiedIfFlag", "onMissed"):
            assert k in p, "%s missing %s" % (eid, k)
        assert p["visible"] is True
        assert p["satisfiedIfFlag"] == REACHED
        assert [x["params"]["flag"] for x in p["onMissed"]] == ["tempest_siege_over"]
        assert [x["params"]["flag"] for x in p["effects"]] == ["tempest_reached_in_time"]
    labels = {next(x for x in effects if x["id"] == e)["paramsJson"]["label"]
              for e in DEADLINE_PACKETS}
    assert len(labels) == 1, "the three packets disagree about the label: %r" % labels

    # the raced flag is actually written, by every wall choice
    writers = {e["parentId"] for e in effects
               if e["type"] == "SET_PLAYER_FLAG" and e["paramsJson"]["flag"] == REACHED}
    assert writers == set(WALL_CHOICES), writers

    # nothing still routes to tempest_siege_over on a met branch
    for eid in DEADLINE_PACKETS:
        p = next(x for x in effects if x["id"] == eid)["paramsJson"]
        assert "tempest_siege_over" not in json.dumps(p["effects"])

    # the two beats that consume tempest_siege_over still exclude arrivers
    for bid in ("qb_tem_4_paid", "qb_tem_4_none"):
        g = json.dumps(next(b for b in data["quest_beats"] if b["id"] == bid)["deliverCondition"])
        assert "tempest_siege_over" in g, bid
        for f in ("tempest_fought_for", "tempest_fought_against", "tempest_walked_away"):
            assert f in g, "%s no longer excludes %s" % (bid, f)

    # unchanged global invariants
    ids = [e["id"] for e in effects]
    assert len(ids) == len(set(ids)), "duplicate effect id"
    cids = {c["id"] for c in choices}
    for e in effects:
        assert e["parentKind"] == "choice" and e["parentId"] in cids, "orphan effect %s" % e["id"]
    for q in ("q_carto", "q_debt", "q_herd", "q_rail", "q_salvage", "q_weather"):
        n = sum(1 for e in effects
                if e["type"] == "COMPLETE_QUEST" and e["paramsJson"]["questId"] == q)
        assert n == 0, "%s gained a COMPLETE_QUEST" % q

    CONTENT.write_text(json.dumps(data, indent=1, ensure_ascii=False),
                       encoding="utf-8", newline="\n")
    print("subjectFaction declared on %d quests: %s" % (len(declared), sorted(declared.items())))
    print("3 rider packets are now visible deadlines racing %s" % REACHED)
    print("effects %d -> %d" % (before["effects"], after["effects"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
