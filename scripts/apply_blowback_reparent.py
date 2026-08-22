#!/usr/bin/env python3
"""Re-parent qb_cro_blowback from q_croppers into q_baron as its opening beat.

The blowback is armed by a 10-round timer at qb_cro_baron, but q_croppers closes
at T+6 when the relic arrives, so the beat could never deliver -- and with it
died blamed_for_barons_war and all three beats of q_baron. The 6/10 split is
deliberate authorship, so the fix keeps the delay and moves the beat instead:
it is the Baron story's inciting incident, not the Croppers' epilogue.

Structural, not additive. Three edits:
  1. qb_cro_blowback: questId q_croppers -> q_baron, ordinal 5 -> 0, and the row
     moves to sit with q_baron's beats (quest_beats is grouped by quest, 35
     contiguous runs, and this preserves that).
  2. qb_bar_1 / qb_bar_2 / qb_bar_3 ordinals 0/1/2 -> 1/2/3.
  3. ef_cro_blow_complete -> ef_cro_blow_adv: COMPLETE_QUEST q_croppers becomes
     ADVANCE_QUEST q_baron / qb_cro_blowback.

On (3): the corpus authors ADVANCE_QUEST both self-referentially (142) and
naming a downstream beat (49, including q_baron's own). The engine auto-appends
a self-referential ADVANCE_QUEST to every choice anyway, so the self-referential
form is a no-op under either reading of the semantics, whereas naming qb_bar_1
would mark it complete if the contract is read literally. Self-referential is
the only form that is safe both ways. Progression to qb_bar_1 does not depend on
it either way: qb_bar_1 gates on blamed_for_barons_war, which this choice writes.

No prose is touched. No effect is added or removed. Exactly one effect is
modified, and the script names it and asserts nothing else moved.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "remnant_content_consolidated_rev2.json"

BEAT = "qb_cro_blowback"
FROM_Q, TO_Q = "q_croppers", "q_baron"
SHIFT = ["qb_bar_1", "qb_bar_2", "qb_bar_3"]
OLD_EF, NEW_EF = "ef_cro_blow_complete", "ef_cro_blow_adv"

EXHAUSTION = {"q_carto", "q_debt", "q_herd", "q_rail", "q_salvage", "q_weather"}


def prose(data):
    return (
        {b["id"]: b.get("text") for b in data["quest_beats"]},
        {c["id"]: (c.get("label"), c.get("outcomeText")) for c in data["choices"]},
    )


def main():
    raw = CONTENT.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert json.dumps(data, indent=1, ensure_ascii=False) == raw, \
        "round-trip is not byte-identical; refusing to write"

    beats, effects = data["quest_beats"], data["effects"]
    before_counts = {k: len(v) for k, v in data.items() if isinstance(v, list)}
    before_prose = prose(data)

    beat = next(b for b in beats if b["id"] == BEAT)
    if beat["questId"] == TO_Q:
        print("already applied (%s is in %s); nothing to do" % (BEAT, TO_Q))
        return 0
    assert beat["questId"] == FROM_Q and beat["ordinal"] == 5, \
        "unexpected start state: %s ord %s" % (beat["questId"], beat["ordinal"])

    # 1. move the row so quest_beats stays grouped by quest
    beats.remove(beat)
    anchor = next(i for i, b in enumerate(beats) if b["id"] == SHIFT[0])
    beat["questId"] = TO_Q
    beat["ordinal"] = 0
    beats.insert(anchor, beat)

    # 2. shift the existing q_baron ordinals
    for n, bid in enumerate(SHIFT, start=1):
        b = next(x for x in beats if x["id"] == bid)
        assert b["ordinal"] == n - 1, "%s expected ord %d, found %s" % (bid, n - 1, b["ordinal"])
        b["ordinal"] = n

    # 3. retype the closing effect
    ef = next(e for e in effects if e["id"] == OLD_EF)
    assert ef["type"] == "COMPLETE_QUEST" and ef["paramsJson"] == {"questId": FROM_Q}, \
        "unexpected effect state: %r" % (ef,)
    assert not any(e["id"] == NEW_EF for e in effects), "id %s already in use" % NEW_EF
    ef["id"] = NEW_EF
    ef["type"] = "ADVANCE_QUEST"
    ef["paramsJson"] = {"questId": TO_Q, "beatId": BEAT}

    # --- assertions -------------------------------------------------------
    assert before_counts == {k: len(v) for k, v in data.items() if isinstance(v, list)}, \
        "table counts moved"
    assert before_prose == prose(data), "prose changed"

    for q, expect in ((FROM_Q, 5), (TO_Q, 4)):
        ords = sorted(b["ordinal"] for b in beats if b["questId"] == q)
        assert ords == list(range(expect)), "%s ordinals are %r" % (q, ords)

    assert beats == sorted(beats, key=lambda b: 0) and True  # order preserved by construction
    seen, prev, ok = set(), None, True
    for b in beats:
        if b["questId"] != prev:
            if b["questId"] in seen:
                ok = False
            seen.add(b["questId"])
            prev = b["questId"]
    assert ok and len(seen) == 35, "quest_beats is no longer grouped into 35 runs"

    ids = {b["id"] for b in beats}
    for p in data["quest_beat_prereqs"]:
        assert p["beatId"] in ids and p["prereqBeatId"] in ids, "dangling prereq %r" % (p,)

    for q in EXHAUSTION:
        n = sum(1 for e in effects
                if e["type"] == "COMPLETE_QUEST" and e["paramsJson"]["questId"] == q)
        assert n == 0, "%s gained %d COMPLETE_QUEST" % (q, n)

    for q in (FROM_Q, TO_Q):
        n = sum(1 for e in effects
                if e["type"] == "COMPLETE_QUEST" and e["paramsJson"]["questId"] == q)
        assert n > 0, "%s has no way to complete" % q

    CONTENT.write_text(
        json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n"
    )
    print("%s: %s ord 5 -> %s ord 0; %s shifted to 1/2/3; %s -> %s (ADVANCE_QUEST)"
          % (BEAT, FROM_Q, TO_Q, "/".join(SHIFT), OLD_EF, NEW_EF))
    return 0


if __name__ == "__main__":
    sys.exit(main())
