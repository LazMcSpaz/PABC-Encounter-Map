#!/usr/bin/env python3
"""Rebuild q_tempest around the siege of the Laker capital.

Approved authoring pass. The quest previously asked for a commitment twice --
once at qb_tem_2 as a fixed twelve-load cost, again at qb_tem_3 -- and then
resolved every route, including sending nothing, on one shared 60% ROLL paying
an identical reward. Seven of its eight state flags were written and read by
nothing.

New shape:
  qb_tem_1  envoy at the gate                       (unchanged)
  qb_tem_2  the pitch; the two "yes" choices merge into one alliance decision
  qb_tem_3  the rider: word, a deadline, and how much scrap you send ahead
  qb_tem_road  NEW  the coalition intercepts you on the road, discovered
  qb_tem_wall  NEW  the capital, discovered; one last out, then the contest
  qb_tem_4_blood / _turned / _paid / _none  NEW  four aftermaths
  qb_tem_betray                                     (unchanged, renumbered)

Whether you march is answered by the board rather than a menu, which is why the
old commit FORCE_CHOICE is retired and why qb_tem_road needs no "did you bring
columns" flag: a player who never leaves home never lands on the road hex.

Deletes 4 choices, 1 beat and 13 effects; adds 6 beats, 13 choices and 45 effects.
No existing prose is edited except qb_tem_3's beat text and ch_tem_direct's
label, both of which are named below. Written back with the source file's
1-space indent and no trailing newline.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "remnant_content_consolidated_rev2.json"

DROP_CHOICES = ["ch_tem_material", "ch_tem_commit", "ch_tem_withhold", "ch_tem_result"]
DROP_BEAT = "qb_tem_4"
EXHAUSTION = {"q_carto", "q_debt", "q_herd", "q_rail", "q_salvage", "q_weather"}

CAPITAL_FILTER = [
    {"type": "location", "factionAffiliation": "lakers", "hasChip": "capital"},
    {"type": "location", "factionAffiliation": "lakers", "strategicValue": "veryHigh"},
    {"type": "location", "factionAffiliation": "lakers"},
]
ROAD_FILTER = [
    {"type": "any", "hasRoad": True, "notControlledBy": "active"},
    {"type": "any", "hasRoad": True},
]

RIDER_TEXT = (
    "A Tempest rider comes in at night on a horse that has been ridden badly, and does not "
    "apologise for either. The clan is moving on the Laker capital, and the lines will close "
    "around it inside the month. He does not ask you for a decision. He tells you where it is "
    "and when it starts, and that a wagon which gets there before the lines close is worth two "
    "that arrive after. Whether you come yourself is a separate question, and he does not ask "
    "it. Then he sleeps four hours in your stable and rides back."
)

ROAD_TEXT = (
    "They meet your column on the road in the middle of the day. No rider, no night, no apology "
    "for the hour. Ilsa Corrow speaks for four of the five clans and brings enough escort to "
    "make it clear she is not hiding.\n\n"
    "She wants you to turn on Tempest at the battle. She says so in the first minute, before "
    "anything else, so that the rest of it can be honest.\n\n"
    "Her reason is this. Clan Tempest rules by an old right that only works while every other "
    "clan stays small. Ninety years of it has kept the lakes fighting each other, and Tempest "
    "has never once tried to stop that, because the fighting is what keeps them first. The "
    "coalition closed the capital to break the pattern. If Tempest takes the seat back, nothing "
    "changes for another ninety years.\n\n"
    "The offer is scrap, paid on the day, and an alliance with the coalition afterwards. She "
    "names both and then stops talking.\n\n"
    "What she cannot offer is the one thing Tempest already has. They asked first, and you said "
    "yes."
)

WALL_TEXT = (
    "The Laker capital is bigger than anything the rider said about it. It stands on rising "
    "ground behind two walls with the lake at its back, and the coalition has had ninety years "
    "and five clans' revenues to make it what it is. Whoever holds it rules the lakes \u2014 which "
    "is why Tempest has come for it, and why it is defended the way it is.\n\n"
    "Your columns are up on the left of the line by midday. A Tempest captain \u2014 grey, "
    "unhurried, missing most of one ear \u2014 walks the length of your front, looks at what you "
    "have brought, and asks whether you are certain. He is not offering you a way out. He has "
    "seen people get this close and realise they had imagined something smaller. He asks once. "
    "Then he waits, and the waiting is the courtesy."
)

BLOOD_TEXT = (
    "The wall goes in the third week, and the counting starts before the dust has settled. "
    "Tempest pays what it owes in front of its own people, which among Lakers is the whole of "
    "the ceremony. Your dead are counted separately, by your own, in a tent that smells of "
    "other men's smoke.\n\n"
    "Nobody in the tent says out loud how much of the coalition is left. Everyone in it knows, "
    "and the number is smaller than it was a season ago."
)

TURNED_TEXT = (
    "Tempest breaks on the ground it came to take, and it breaks partly because of where your "
    "people were standing. The coalition pays what Corrow said it would, on time and in "
    "daylight and in front of witnesses. They want it on the record that they paid you.\n\n"
    "Somewhere south of here a clan that is now considerably smaller than it was knows the name "
    "of everyone who stood on that line."
)

PAID_TEXT = "The siege ends the way sieges end, and the accounting begins immediately."

NONE_TEXT = (
    "Word of how the siege ended reaches you the way news reaches a man who was not there: "
    "late, secondhand, and from somebody who assumes he has no particular interest in it."
)


def flag(fid, name, value=True):
    return {"id": fid, "type": "SET_PLAYER_FLAG",
            "paramsJson": {"flag": name, "value": value,
                           "duration": "permanent", "target": "active"}}


def simple(fid, etype, params):
    return {"id": fid, "type": etype, "paramsJson": params}


def res(fid, amount):
    return simple(fid, "ADJUST_RESOURCE",
                  {"resource": "Resource", "amount": amount, "target": "active"})


def std(fid, amount):
    return simple(fid, "ADJUST_STANDING",
                  {"faction": "lakers", "player": "active", "amount": amount})


def hon(fid, amount):
    return simple(fid, "ADJUST_HONOR", {"amount": amount, "target": "active"})


def adv(fid, beat):
    return simple(fid, "ADVANCE_QUEST", {"questId": "q_tempest", "beatId": beat})


def done(fid):
    return simple(fid, "COMPLETE_QUEST", {"questId": "q_tempest"})


def deadline(fid):
    return simple(fid, "QUEUE_DEFERRED", {
        "delayRounds": 4,
        "effects": [{"type": "SET_PLAYER_FLAG",
                     "params": {"flag": "tempest_siege_over", "value": True,
                                "duration": "permanent", "target": "active"}}]})


HAS = lambda f: {"has_flag": {"player": "active", "flag": f}}
NOT = lambda f: {"not": HAS(f)}

# beat id -> (ordinal, deliver, gate, placementFilter, text, art)
NEW_BEATS = [
    ("qb_tem_road", 3, "discovered",
     {"all": [HAS("tempest_allied"), HAS("tempest_call_due"), NOT("turned_on_tempest"),
              NOT("tempest_siege_over")]},
     ROAD_FILTER, ROAD_TEXT,
     "A well-escorted delegation halting a marching column on an open road at midday."),
    ("qb_tem_wall", 4, "discovered",
     {"all": [HAS("tempest_allied"), HAS("tempest_call_due"), NOT("tempest_siege_over")]},
     CAPITAL_FILTER, WALL_TEXT,
     "Siege lines before a double-walled city on rising ground, a lake behind it."),
    ("qb_tem_4_blood", 5, "conditional", HAS("tempest_fought_for"), None, BLOOD_TEXT,
     "A command tent after a storming; two sets of ledgers on the same table."),
    ("qb_tem_4_turned", 6, "conditional", HAS("tempest_fought_against"), None, TURNED_TEXT,
     "Coalition clerks paying out in daylight, in the open, in front of witnesses."),
    ("qb_tem_4_paid", 7, "conditional",
     {"all": [HAS("tempest_siege_over"), NOT("tempest_fought_for"),
              NOT("tempest_fought_against"), NOT("tempest_walked_away"),
              {"any": [HAS("tempest_scrap_1"), HAS("tempest_scrap_2")]}]},
     None, PAID_TEXT, "A long list being read aloud from a board; a clerk not looking up."),
    ("qb_tem_4_none", 8, "conditional",
     {"all": [HAS("tempest_siege_over"), NOT("tempest_fought_for"),
              NOT("tempest_fought_against"), NOT("tempest_walked_away"),
              NOT("tempest_scrap_1"), NOT("tempest_scrap_2")]},
     None, NONE_TEXT, "A distant column of smoke seen from a long way off, from safety."),
]

# (choice id, beat, ordinal, label, condition, outcomeText, [effects])
NEW_CHOICES = [
    ("ch_tem_scrap5", "qb_tem_3", 0, "Send five scrap ahead", None,
     "Five scrap goes east with his escort. Tempest will spend it on men before you get there. "
     "He accepts it as what it is and files away what it isn't.",
     [res("ef_tem_s5_cost", -5), flag("ef_tem_s5_flag", "tempest_scrap_1"),
      std("ef_tem_s5_std", 1), deadline("ef_tem_s5_deadline"),
      adv("ef_tem_s5_adv", "qb_tem_3")]),
    ("ch_tem_scrap10", "qb_tem_3", 1, "Send ten scrap ahead", None,
     "Ten scrap goes east with his escort. That is twice what he asked for and he does not "
     "remark on it. Tempest will have two companies standing because of it before the digging "
     "is done.",
     [res("ef_tem_s10_cost", -10), flag("ef_tem_s10_flag", "tempest_scrap_2"),
      std("ef_tem_s10_std", 2), deadline("ef_tem_s10_deadline"),
      adv("ef_tem_s10_adv", "qb_tem_3")]),
    ("ch_tem_sendnone", "qb_tem_3", 2, "Send nothing ahead", None,
     "You send the rider back with your compliments and nothing else. What you do about the "
     "wall itself is still in front of you.",
     [flag("ef_tem_sn_flag", "tempest_sent_nothing"), deadline("ef_tem_sn_deadline"),
      adv("ef_tem_sn_adv", "qb_tem_3")]),

    ("ch_tem_road_take", "qb_tem_road", 0, "Take her terms", None,
     "You settle it in an hour, on a road. She does not shake your hand at the end. There is no "
     "document, no seal and no witness, which is exactly what both of you want.",
     [flag("ef_tem_rt_flag", "turned_on_tempest"),
      flag("ef_tem_rt_ally", "laker_coalition_ally"), hon("ef_tem_rt_hon", -3),
      adv("ef_tem_rt_adv", "qb_tem_road")]),
    ("ch_tem_road_refuse", "qb_tem_road", 1, "Send her away", None,
     "She goes without arguing, which is worse than arguing. Nobody will ever know she came, "
     "and that includes the people you are about to fight for.",
     [flag("ef_tem_rr_flag", "refused_the_coalition"), hon("ef_tem_rr_hon", 1),
      adv("ef_tem_rr_adv", "qb_tem_road")]),
    ("ch_tem_road_tell", "qb_tem_road", 2, "Send her away, and tell Tempest she came", None,
     "The captain hears it out, asks two questions about the size of her escort and none about "
     "her offer, and thanks you so briefly that it takes a moment to recognise as thanks. It "
     "will be remembered a great deal longer than it was said.",
     [flag("ef_tem_rl_flag", "told_tempest_of_the_offer"),
      flag("ef_tem_rl_ref", "refused_the_coalition"), hon("ef_tem_rl_hon", 1),
      adv("ef_tem_rl_adv", "qb_tem_road")]),
]

NEW_CHOICES += [
    ("ch_tem_wall_start", "qb_tem_wall", 0, "Tell him to start", NOT("turned_on_tempest"),
     "He nods the way a man nods at a receipt and goes back down the line without hurrying, and "
     "somewhere behind him a horn goes.",
     [flag("ef_tem_ws_flag", "tempest_fought_for"),
      {"id": "ef_tem_ws_contest", "type": "CONTEST",
       "_note": "opponentStrength provisional: capital garrison plus defenders. Must be "
                "re-measured now that allies and vassals defend as well as attack.",
       "paramsJson": {"opponentStrength": 12, "target": "active",
                      "onWin": [{"type": "SET_PLAYER_FLAG",
                                 "params": {"flag": "tempest_victory", "value": True,
                                            "duration": "permanent", "target": "active"}}],
                      "onLose": []}},
      adv("ef_tem_ws_adv", "qb_tem_wall")]),
    ("ch_tem_wall_turn", "qb_tem_wall", 1, "Tell him to start, and wait", HAS("turned_on_tempest"),
     "He nods the way a man nods at a receipt and goes back down the line without hurrying. You "
     "watch him all the way, which you did not intend to do.",
     [flag("ef_tem_wt_flag", "tempest_fought_against"),
      {"id": "ef_tem_wt_contest", "type": "CONTEST",
       "_note": "You fight alongside the garrison against Tempest. Any Tempest units your "
                "scrap paid for are on the other side. opponentStrength provisional.",
       "paramsJson": {"opponentStrength": 8, "target": "active",
                      "onWin": [{"type": "SET_PLAYER_FLAG",
                                 "params": {"flag": "tempest_broken", "value": True,
                                            "duration": "permanent", "target": "active"}}],
                      "onLose": []}},
      adv("ef_tem_wt_adv", "qb_tem_wall")]),
    ("ch_tem_wall_leave", "qb_tem_wall", 2, "Turn your columns around", None,
     "You take your people back off the line in good order and in full view, which is the only "
     "way it can be done. The captain does not argue and does not watch you go. By the time you "
     "make camp that night it is already a thing that is known.",
     [flag("ef_tem_wl_flag", "tempest_walked_away"), std("ef_tem_wl_std", -8),
      hon("ef_tem_wl_hon", -2), done("ef_tem_wl_end")]),

    ("ch_tem_blood_ack", "qb_tem_4_blood", 0, "Bury yours first", None,
     "They pay in full and they pay ahead of their own clans, and nobody objects out loud. It "
     "is not gratitude. It is a debt being closed where everyone can see it closed.",
     [std("ef_tem_bl_std", 6), res("ef_tem_bl_res", 10), done("ef_tem_bl_end")]),
    ("ch_tem_turned_ack", "qb_tem_4_turned", 0, "Take the payment", None,
     "You take it. It spends exactly as well as any other money, which is the thing nobody "
     "warns you about.",
     [res("ef_tem_tn_res", 12), std("ef_tem_tn_std", 6), done("ef_tem_tn_end")]),
    ("ch_tem_paid_ack", "qb_tem_4_paid", 0, "Settle accounts", None,
     "Tempest is precise about what it owes and equally precise about what it doesn't. Your "
     "scrap is on the list. It is on it beneath every clan that sent men, and the clerk reading "
     "it does not look up.",
     [std("ef_tem_pd_std", 2), res("ef_tem_pd_res", 3), done("ef_tem_pd_end")]),
    ("ch_tem_none_ack", "qb_tem_4_none", 0, "Let it go", None,
     "You let it go. There was never a version of this in which they came and told you "
     "themselves.",
     [std("ef_tem_nn_std", -3), done("ef_tem_nn_end")]),
]


def prose_snapshot(data, skip_beats=(), skip_choices=()):
    return (
        {b["id"]: b.get("text") for b in data["quest_beats"] if b["id"] not in skip_beats},
        {c["id"]: (c.get("label"), c.get("outcomeText")) for c in data["choices"]
         if c["id"] not in skip_choices},
    )


def main():
    raw = CONTENT.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert json.dumps(data, indent=1, ensure_ascii=False) == raw, \
        "round-trip is not byte-identical; refusing to write"

    beats, choices, effects = data["quest_beats"], data["choices"], data["effects"]
    if any(b["id"] == "qb_tem_wall" for b in beats):
        print("already applied (qb_tem_wall exists); nothing to do")
        return 0

    before = {k: len(v) for k, v in data.items() if isinstance(v, list)}
    touched_beats = {"qb_tem_3"}
    touched_choices = {"ch_tem_direct"} | set(DROP_CHOICES)
    before_prose = prose_snapshot(data, touched_beats | {DROP_BEAT}, touched_choices)

    # --- deletions -----------------------------------------------------
    drop_eff = [e["id"] for e in effects if e["parentId"] in DROP_CHOICES]
    assert len(drop_eff) == 13, "expected 13 effects to drop, found %d" % len(drop_eff)
    data["effects"] = effects = [e for e in effects if e["parentId"] not in DROP_CHOICES]
    data["choices"] = choices = [c for c in choices if c["id"] not in DROP_CHOICES]
    beat4_i = next(i for i, b in enumerate(beats) if b["id"] == DROP_BEAT)
    beats.pop(beat4_i)

    # qb_tem_4's prereq row dies with it; the branch heads inherit the chain
    pre = data["quest_beat_prereqs"]
    old_row = {"beatId": DROP_BEAT, "prereqBeatId": "qb_tem_3"}
    assert old_row in pre, "expected prereq %r" % old_row
    at = pre.index(old_row)
    pre[at:at + 1] = [
        {"beatId": "qb_tem_road", "prereqBeatId": "qb_tem_3"},
        {"beatId": "qb_tem_wall", "prereqBeatId": "qb_tem_3"},
        {"beatId": "qb_tem_4_blood", "prereqBeatId": "qb_tem_wall"},
        {"beatId": "qb_tem_4_turned", "prereqBeatId": "qb_tem_wall"},
        {"beatId": "qb_tem_4_paid", "prereqBeatId": "qb_tem_3"},
        {"beatId": "qb_tem_4_none", "prereqBeatId": "qb_tem_3"},
    ]

    # --- modifications -------------------------------------------------
    direct = next(c for c in choices if c["id"] == "ch_tem_direct")
    assert direct["label"] == "Offer him your soldiers"
    direct["label"] = "Take his terms"
    dflag = next(e for e in effects if e["id"] == "ef_tem_dir_flag")
    assert dflag["paramsJson"]["flag"] == "tempest_direct_support"
    dflag["paramsJson"]["flag"] = "tempest_allied"
    rider = next(b for b in beats if b["id"] == "qb_tem_3")
    rider["text"] = RIDER_TEXT
    return _finish(data, beats, choices, effects, before, before_prose,
                   touched_beats, touched_choices, raw)


def _finish(data, beats, choices, effects, before, before_prose,
            touched_beats, touched_choices, raw):
    # --- new beats, inserted inside the q_tempest run to keep grouping ---
    anchor = next(i for i, b in enumerate(beats) if b["id"] == "qb_tem_betray")
    rows = []
    for bid, ordinal, deliver, gate, pf, text, art in NEW_BEATS:
        row = {"id": bid, "questId": "q_tempest", "ordinal": ordinal, "deliver": deliver}
        if pf is not None:
            row["placementFilter"] = pf
        row["deliverCondition"] = gate
        row["text"] = text
        row["art"] = art
        rows.append(row)
    beats[anchor:anchor] = rows
    next(b for b in beats if b["id"] == "qb_tem_betray")["ordinal"] = 9

    # --- new choices and their effects ---
    c_anchor = max(i for i, c in enumerate(choices)
                   if c["parentId"].startswith("qb_tem")) + 1
    e_anchor = max(i for i, e in enumerate(effects)
                   if e["parentId"].startswith("ch_tem")) + 1
    new_c, new_e = [], []
    for cid, beat, ordinal, label, cond, out, evs in NEW_CHOICES:
        row = {"id": cid, "parentKind": "beat", "parentId": beat, "ordinal": ordinal,
               "label": label}
        if cond is not None:
            row["condition"] = cond
        row["outcomeText"] = out
        new_c.append(row)
        for n, ev in enumerate(evs):
            e = {"id": ev["id"], "parentKind": "choice", "parentId": cid, "ordinal": n,
                 "type": ev["type"], "paramsJson": ev["paramsJson"]}
            if "_note" in ev:
                e["_note"] = ev["_note"]
            new_e.append(e)
    choices[c_anchor:c_anchor] = new_c
    effects[e_anchor:e_anchor] = new_e

    # --- assertions ----------------------------------------------------
    after = {k: len(v) for k, v in data.items() if isinstance(v, list)}
    assert after["quest_beats"] == before["quest_beats"] + 5, after
    assert after["choices"] == before["choices"] + 9, after
    assert after["effects"] == before["effects"] + 32, after  # 45 added, 13 dropped
    assert after["quest_beat_prereqs"] == before["quest_beat_prereqs"] + 5, after
    for k in ("quests", "world_encounters", "field_encounters"):
        assert after[k] == before[k], "%s moved" % k

    added_b = {b[0] for b in NEW_BEATS}
    added_c = {c[0] for c in NEW_CHOICES}
    assert prose_snapshot(data, touched_beats | {DROP_BEAT} | added_b,
                          touched_choices | added_c) == before_prose, \
        "untouched prose changed"

    ids = [b["id"] for b in beats]
    assert len(ids) == len(set(ids)), "duplicate beat id"
    cids = [c["id"] for c in choices]
    assert len(cids) == len(set(cids)), "duplicate choice id"
    eids = [e["id"] for e in effects]
    assert len(eids) == len(set(eids)), "duplicate effect id"

    tem = sorted([b for b in beats if b["questId"] == "q_tempest"], key=lambda b: b["ordinal"])
    assert [b["ordinal"] for b in tem] == list(range(10)), \
        "q_tempest ordinals: %r" % [b["ordinal"] for b in tem]

    seen, prev, ok = set(), None, True
    for b in beats:
        if b["questId"] != prev:
            if b["questId"] in seen:
                ok = False
            seen.add(b["questId"])
            prev = b["questId"]
    assert ok and len(seen) == 35, "quest_beats no longer grouped into 35 runs"

    beat_ids = {b["id"] for b in beats}
    for c in choices:
        assert c["parentId"] in beat_ids or c["parentKind"] != "beat", \
            "orphan choice %s" % c["id"]
    for p in data["quest_beat_prereqs"]:
        assert p["beatId"] in beat_ids and p["prereqBeatId"] in beat_ids, "dangling prereq"
    choice_ids = set(cids)
    for e in effects:
        if e["parentKind"] == "choice":
            assert e["parentId"] in choice_ids, "orphan effect %s" % e["id"]

    for q in EXHAUSTION:
        n = sum(1 for e in effects
                if e["type"] == "COMPLETE_QUEST" and e["paramsJson"]["questId"] == q)
        assert n == 0, "%s gained a COMPLETE_QUEST" % q

    # every q_tempest terminal route can close the quest
    closers = {e["parentId"] for e in effects
               if e["type"] == "COMPLETE_QUEST" and e["paramsJson"]["questId"] == "q_tempest"}
    for cid in ("ch_tem_dismiss", "ch_tem_reject", "ch_tem_wall_leave", "ch_tem_blood_ack",
                "ch_tem_turned_ack", "ch_tem_paid_ack", "ch_tem_none_ack",
                "ch_tem_betray_ack"):
        assert cid in closers, "%s does not complete q_tempest" % cid

    # no flag written by the new content is left unread unless it is a hook
    HOOKS = {"tempest_victory", "tempest_broken", "laker_coalition_ally",
             "refused_the_coalition", "told_tempest_of_the_offer", "tempest_sent_nothing",
             "tempest_walked_away", "seen_tempest_envoy"}
    gates = json.dumps([b.get("deliverCondition") for b in beats]
                       + [c.get("condition") for c in choices])
    for e in effects:
        if e["type"] == "SET_PLAYER_FLAG" and e["parentId"].startswith("ch_tem"):
            f = e["paramsJson"]["flag"]
            assert f in HOOKS or ('"%s"' % f) in gates, "flag %s is written and never read" % f

    assert "loads" not in json.dumps([b for b in beats if b["questId"] == "q_tempest"]), \
        "'loads' still present in a q_tempest beat"

    CONTENT.write_text(
        json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n"
    )
    print("q_tempest rebuilt: beats %d -> %d, choices %d -> %d, effects %d -> %d"
          % (before["quest_beats"], after["quest_beats"], before["choices"], after["choices"],
             before["effects"], after["effects"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
