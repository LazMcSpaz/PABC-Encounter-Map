#!/usr/bin/env python3
"""Apply docs/import/stalled-branch-closures.md.

Nine terminal choices across q_signal, q_croppers and q_caravan resolve but never
close their quest. Each gains a COMPLETE_QUEST. Five of them also gain a new
SET_PLAYER_FLAG continuation hook; the other four reuse a flag their choice
already writes, so no second write is added.

9 COMPLETE_QUEST + 5 SET_PLAYER_FLAG = 14 effects. 1133 -> 1147.

Appends only. No existing effect is removed, reordered or renumbered, and no
beat text, choice label or outcomeText is touched. Written back with the source
file's own 1-space indent and no trailing newline.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "remnant_content_consolidated_rev2.json"

# choiceId -> (questId, new flag or None, effect id stem)
CLOSURES = [
    ("ch_sig_ignore",       "q_signal",   None,                     "ef_sig_ignore"),
    ("ch_sig_out_free",     "q_signal",   None,                     "ef_sig_free"),
    ("ch_cro_blowback_ack", "q_croppers", None,                     "ef_cro_blow"),
    ("ch_car_bm_pay",       "q_caravan",  "car_blackmail_paid",     "ef_car_bm_pay"),
    ("ch_car_bm_refuse",    "q_caravan",  "car_blackmail_refused",  "ef_car_bm_ref"),
    ("ch_car_bm_public",    "q_caravan",  "car_witness_hanged",     "ef_car_bm_pub"),
    ("ch_car_bm_quiet",     "q_caravan",  "car_witness_vanished",   "ef_car_bm_qui"),
    ("ch_car_req_pay",      "q_caravan",  None,                     "ef_car_req_pay"),
    ("ch_car_req_refuse",   "q_caravan",  "car_supply_declined",    "ef_car_req_ref"),
]

# Placement-driven quests that already complete by exhausting their beats.
# A COMPLETE_QUEST here would close them early. Guarded, not assumed.
EXHAUSTION_QUESTS = {"q_carto", "q_debt", "q_herd", "q_rail", "q_salvage", "q_weather"}


def main():
    raw = CONTENT.read_text(encoding="utf-8")
    data = json.loads(raw)
    effects = data["effects"]

    assert json.dumps(data, indent=1, ensure_ascii=False) == raw, \
        "round-trip is not byte-identical; refusing to write"

    before = len(effects)
    if before == 1147:
        print("already applied (effects == 1147); nothing to do")
        return 0
    assert before == 1133, f"expected 1133 effects, found {before}"

    by_choice = {}
    for i, e in enumerate(effects):
        if e.get("parentKind") == "choice":
            by_choice.setdefault(e["parentId"], []).append(i)

    existing_ids = {e["id"] for e in effects}
    additions = []  # (insert_after_index, [new effect, ...])

    for choice_id, quest_id, new_flag, stem in CLOSURES:
        assert quest_id not in EXHAUSTION_QUESTS, \
            f"{quest_id} completes by exhaustion; refusing to add COMPLETE_QUEST"
        idxs = by_choice.get(choice_id)
        assert idxs, f"choice {choice_id} has no effects"

        last = idxs[-1]
        ordinal = max(effects[i]["ordinal"] for i in idxs) + 1
        rows = []

        if new_flag is not None:
            assert not any(
                e["type"] == "SET_PLAYER_FLAG"
                and e["paramsJson"].get("flag") == new_flag
                for e in effects
            ), f"flag {new_flag} is already written somewhere"
            rows.append({
                "id": f"{stem}_{new_flag.rsplit('_', 1)[-1]}flag",
                "parentKind": "choice",
                "parentId": choice_id,
                "ordinal": ordinal,
                "type": "SET_PLAYER_FLAG",
                "paramsJson": {
                    "flag": new_flag,
                    "value": True,
                    "duration": "permanent",
                    "target": "active",
                },
            })
            ordinal += 1

        rows.append({
            "id": f"{stem}_complete",
            "parentKind": "choice",
            "parentId": choice_id,
            "ordinal": ordinal,
            "type": "COMPLETE_QUEST",
            "paramsJson": {"questId": quest_id},
        })

        for r in rows:
            assert r["id"] not in existing_ids, f"duplicate effect id {r['id']}"
            existing_ids.add(r["id"])
        additions.append((last, rows))

    # Splice from the back so earlier indices stay valid.
    for last, rows in sorted(additions, key=lambda a: a[0], reverse=True):
        effects[last + 1:last + 1] = rows

    after = len(effects)
    assert after == 1147, f"expected 1147 effects after write, got {after}"

    CONTENT.write_text(
        json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n"
    )
    print(f"effects {before} -> {after} (+{after - before})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
