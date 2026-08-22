#!/usr/bin/env python3
"""The four held edits, now that the triggering-unit token exists.

1. ch_cro_baron_fight's failure branch wrote nothing, so a 70% roll advanced
   q_croppers past ordinal 3 with nothing downstream deliverable. It now records
   the loss and closes the quest.
2. All eleven ADJUST_BASE_STRENGTH effects targeted "active", which resolves to
   a player id while the handler wants a unit uid -- so every one was skipped,
   including all four -99 destroy sentinels. Retargeted to "triggering-unit".
3/4. Both q_tempest contests had an empty onLose. A failed siege now costs the
   column that fought it, and each failure routes to a short aftermath.

Token spelling: targeting.js aliases "triggering-unit" -> "triggering_unit".
The corpus authors the hyphenated schema forms throughout ("active", not
"active_player"), so the hyphenated one is used here for consistency and for the
editor validator, which checks schema names.

The two new aftermath beats are deliberately short. They exist to close routes
that previously could not close; they are consequence wiring and want a proper
authoring pass later, recorded in docs/import/deferred-legibility-pass.md.
"""
import json
import sys
from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent / "remnant_content_consolidated_rev2.json"

UNIT = "triggering-unit"
EXHAUSTION = {"q_carto", "q_debt", "q_herd", "q_rail", "q_salvage", "q_weather"}

HAS = lambda f: {"has_flag": {"player": "active", "flag": f}}
NOT = lambda f: {"not": HAS(f)}

FAILED_TEXT = (
    "The wall holds. Tempest spends three more weeks in front of it and then spends the winter "
    "explaining why, and the part of that explanation which involves you is short and not "
    "flattering. You get your people back, or the ones who are coming back."
)

TURNED_LOST_TEXT = (
    "Tempest takes the capital anyway, and takes it knowing exactly where you were standing when "
    "they did. Corrow pays what she promised, which is the last thing the coalition does as a "
    "coalition. Nobody has to tell you what your name is worth on the lakes now."
)


def walk(node, fn):
    """Apply fn to every dict in the tree, depth first."""
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


def prose(data, skip_b=(), skip_c=()):
    return (
        {b["id"]: b.get("text") for b in data["quest_beats"] if b["id"] not in skip_b},
        {c["id"]: (c.get("label"), c.get("outcomeText")) for c in data["choices"]
         if c["id"] not in skip_c},
    )


def main():
    raw = CONTENT.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert json.dumps(data, indent=1, ensure_ascii=False) == raw, \
        "round-trip is not byte-identical; refusing to write"

    beats, choices, effects = data["quest_beats"], data["choices"], data["effects"]
    if any(b["id"] == "qb_tem_4_failed" for b in beats):
        print("already applied; nothing to do")
        return 0

    before = {k: len(v) for k, v in data.items() if isinstance(v, list)}
    NEW_B = {"qb_tem_4_failed", "qb_tem_4_turned_lost"}
    NEW_C = {"ch_tem_failed_ack", "ch_tem_turned_lost_ack"}
    before_prose = prose(data, NEW_B, NEW_C)

    # ---- 2. retarget every ADJUST_BASE_STRENGTH ------------------------
    hits = []

    def retarget(node):
        if node.get("type") == "ADJUST_BASE_STRENGTH":
            p = node.get("params") or node.get("paramsJson") or {}
            assert p.get("target") == "active", "unexpected target %r" % p.get("target")
            p["target"] = UNIT
            hits.append(p.get("amount"))

    walk(effects, retarget)
    assert len(hits) == 11, "expected 11 ADJUST_BASE_STRENGTH, retargeted %d" % len(hits)
    assert sorted(hits) == [-99, -99, -99, -99, -2, -2, -2, -2, -1, 1, 2], sorted(hits)

    # ---- 1. the Baron's failure branch ---------------------------------
    baron = next(e for e in effects if e["id"] == "ef_cro_bar_fight")
    fail = baron["paramsJson"]["onFail"]
    assert len(fail) == 1 and fail[0]["type"] == "ADJUST_BASE_STRENGTH", fail
    fail.append({"type": "SET_PLAYER_FLAG",
                 "params": {"flag": "cro_relic_lost", "value": True,
                            "duration": "permanent", "target": "active"}})
    fail.append({"type": "COMPLETE_QUEST", "params": {"questId": "q_croppers"}})

    # ---- 3/4. the two q_tempest failure branches -----------------------
    ws = next(e for e in effects if e["id"] == "ef_tem_ws_contest")
    wt = next(e for e in effects if e["id"] == "ef_tem_wt_contest")
    for eff, flagname in ((ws, "tempest_siege_failed"), (wt, "tempest_turn_failed")):
        assert eff["paramsJson"]["onLose"] == [], "onLose already populated on %s" % eff["id"]
        eff["paramsJson"]["onLose"] = [
            {"type": "ADJUST_BASE_STRENGTH", "params": {"amount": -99, "target": UNIT}},
            {"type": "SET_PLAYER_FLAG",
             "params": {"flag": flagname, "value": True,
                        "duration": "permanent", "target": "active"}},
        ]

    # the winning aftermaths must now require the win
    blood = next(b for b in beats if b["id"] == "qb_tem_4_blood")
    assert blood["deliverCondition"] == HAS("tempest_fought_for")
    blood["deliverCondition"] = {"all": [HAS("tempest_fought_for"), HAS("tempest_victory")]}
    turned = next(b for b in beats if b["id"] == "qb_tem_4_turned")
    assert turned["deliverCondition"] == HAS("tempest_fought_against")
    turned["deliverCondition"] = {"all": [HAS("tempest_fought_against"), HAS("tempest_broken")]}

    # ---- the two short aftermaths --------------------------------------
    anchor = next(i for i, b in enumerate(beats) if b["id"] == "qb_tem_betray")
    beats[anchor:anchor] = [
        {"id": "qb_tem_4_failed", "questId": "q_tempest", "ordinal": 0,
         "deliver": "conditional",
         "deliverCondition": {"all": [HAS("tempest_fought_for"), HAS("tempest_siege_failed")]},
         "text": FAILED_TEXT,
         "art": "A siege line in winter, the wall behind it undamaged."},
        {"id": "qb_tem_4_turned_lost", "questId": "q_tempest", "ordinal": 0,
         "deliver": "conditional",
         "deliverCondition": {"all": [HAS("tempest_fought_against"),
                                      HAS("tempest_turn_failed")]},
         "text": TURNED_LOST_TEXT,
         "art": "A payment counted out in a hurry, by people packing to leave."},
    ]
    # renumber the whole quest in array order
    tem = [b for b in beats if b["questId"] == "q_tempest"]
    for n, b in enumerate(tem):
        b["ordinal"] = n

    c_anchor = max(i for i, c in enumerate(choices) if c["parentId"].startswith("qb_tem")) + 1
    choices[c_anchor:c_anchor] = [
        {"id": "ch_tem_failed_ack", "parentKind": "beat", "parentId": "qb_tem_4_failed",
         "ordinal": 0, "label": "Count them",
         "outcomeText": "You count them yourself, because it is the one part of this nobody "
                        "else should do for you."},
        {"id": "ch_tem_turned_lost_ack", "parentKind": "beat",
         "parentId": "qb_tem_4_turned_lost", "ordinal": 0, "label": "Take the payment",
         "outcomeText": "You take it. There is nothing else left on the table and both of you "
                        "know exactly what it is you are being paid for."},
    ]

    e_anchor = max(i for i, e in enumerate(effects) if e["parentId"].startswith("ch_tem")) + 1
    def std(fid, cid, o, amt):
        return {"id": fid, "parentKind": "choice", "parentId": cid, "ordinal": o,
                "type": "ADJUST_STANDING",
                "paramsJson": {"faction": "lakers", "player": "active", "amount": amt}}
    def done(fid, cid, o):
        return {"id": fid, "parentKind": "choice", "parentId": cid, "ordinal": o,
                "type": "COMPLETE_QUEST", "paramsJson": {"questId": "q_tempest"}}
    effects[e_anchor:e_anchor] = [
        std("ef_tem_fl_std", "ch_tem_failed_ack", 0, 1),
        done("ef_tem_fl_end", "ch_tem_failed_ack", 1),
        std("ef_tem_tl_std", "ch_tem_turned_lost_ack", 0, -6),
        done("ef_tem_tl_end", "ch_tem_turned_lost_ack", 1),
    ]

    data["quest_beat_prereqs"] += [
        {"beatId": "qb_tem_4_failed", "prereqBeatId": "qb_tem_wall"},
        {"beatId": "qb_tem_4_turned_lost", "prereqBeatId": "qb_tem_wall"},
    ]
    return _verify(data, before, before_prose, NEW_B, NEW_C)


def _verify(data, before, before_prose, NEW_B, NEW_C):
    beats, choices, effects = data["quest_beats"], data["choices"], data["effects"]
    after = {k: len(v) for k, v in data.items() if isinstance(v, list)}

    assert after["quest_beats"] == before["quest_beats"] + 2, after
    assert after["choices"] == before["choices"] + 2, after
    assert after["effects"] == before["effects"] + 4, after
    assert after["quest_beat_prereqs"] == before["quest_beat_prereqs"] + 2, after
    for k in ("quests", "world_encounters", "field_encounters"):
        assert after[k] == before[k], "%s moved" % k

    assert prose(data, NEW_B, NEW_C) == before_prose, "existing prose changed"

    # no ADJUST_BASE_STRENGTH still points at a player
    left = []
    walk(effects, lambda n: left.append(n) if n.get("type") == "ADJUST_BASE_STRENGTH"
         and (n.get("params") or n.get("paramsJson") or {}).get("target") != UNIT else None)
    assert not left, "%d ADJUST_BASE_STRENGTH still mis-targeted" % len(left)

    # the Baron can no longer strand
    baron = next(e for e in effects if e["id"] == "ef_cro_bar_fight")
    for branch in ("onSuccess", "onFail"):
        kinds = [x["type"] for x in baron["paramsJson"][branch]]
        assert "SET_PLAYER_FLAG" in kinds, "%s writes no flag" % branch
    assert any(x["type"] == "COMPLETE_QUEST" for x in baron["paramsJson"]["onFail"]), \
        "Baron onFail cannot close q_croppers"

    # both q_tempest contests have a populated onLose
    for eid in ("ef_tem_ws_contest", "ef_tem_wt_contest"):
        e = next(x for x in effects if x["id"] == eid)
        assert e["paramsJson"]["onLose"], "%s onLose still empty" % eid

    # every win/lose pair of q_tempest gates is mutually exclusive and covered
    gates = {b["id"]: json.dumps(b.get("deliverCondition"))
             for b in beats if b["questId"] == "q_tempest"}
    for won, lost, flag in (("qb_tem_4_blood", "qb_tem_4_failed", "tempest_victory"),
                            ("qb_tem_4_turned", "qb_tem_4_turned_lost", "tempest_broken")):
        assert flag in gates[won], "%s does not require %s" % (won, flag)
        assert flag not in gates[lost], "%s wrongly requires %s" % (lost, flag)

    ids = [b["id"] for b in beats]
    assert len(ids) == len(set(ids))
    cids = [c["id"] for c in choices]
    assert len(cids) == len(set(cids))
    eids = [e["id"] for e in effects]
    assert len(eids) == len(set(eids))

    tem = sorted([b for b in beats if b["questId"] == "q_tempest"], key=lambda b: b["ordinal"])
    assert [b["ordinal"] for b in tem] == list(range(12)), [b["ordinal"] for b in tem]

    seen, prev, ok = set(), None, True
    for b in beats:
        if b["questId"] != prev:
            if b["questId"] in seen:
                ok = False
            seen.add(b["questId"])
            prev = b["questId"]
    assert ok and len(seen) == 35, "quest_beats no longer grouped into 35 runs"

    beat_ids = set(ids)
    for p in data["quest_beat_prereqs"]:
        assert p["beatId"] in beat_ids and p["prereqBeatId"] in beat_ids, "dangling prereq"
    for c in choices:
        assert c["parentId"] in beat_ids or c["parentKind"] != "beat", "orphan choice"
    choice_ids = set(cids)
    for e in effects:
        if e["parentKind"] == "choice":
            assert e["parentId"] in choice_ids, "orphan effect %s" % e["id"]

    for q in EXHAUSTION:
        n = sum(1 for e in effects
                if e["type"] == "COMPLETE_QUEST" and e["paramsJson"]["questId"] == q)
        assert n == 0, "%s gained a COMPLETE_QUEST" % q

    CONTENT.write_text(json.dumps(data, indent=1, ensure_ascii=False),
                       encoding="utf-8", newline="\n")
    print("retargeted 11 ADJUST_BASE_STRENGTH to %s" % UNIT)
    print("Baron onFail: records cro_relic_lost and closes q_croppers")
    print("q_tempest: both contests have an onLose; 2 aftermath beats added")
    print("beats %d -> %d, choices %d -> %d, effects %d -> %d, prereqs %d -> %d"
          % (before["quest_beats"], after["quest_beats"], before["choices"], after["choices"],
             before["effects"], after["effects"], before["quest_beat_prereqs"],
             after["quest_beat_prereqs"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
