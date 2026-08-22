"""
apply_placement_filters.py - re-site the terrain-blocked quest openers.

Approved plan; run once the engine agent's hit-rate measurements confirm.
See docs/import/terrain-relocation.md and qb_mas_compound-adjacency.md.

    python scripts/apply_placement_filters.py <consolidated.json> [--write]

Writes with the source file's own formatting (1-space indent, no trailing
newline) so the diff stays reviewable.
"""
import json, sys, copy

EDITS = {
    # terrain-blocked openers. terrain: is dead engine-side and permanently so.
    "qb_wks_1":  ({"hasRoad": True},
                  'rubble was a proxy for "where salvage is"; qb_wks_3 names "a board at the road end"'),
    "qb_gls_1":  ({"type": "terrain", "hasRoad": False},
                  'rubble contradicted the text - "it is not a crater... no spoil anywhere"'),
    "qb_gls_2":  ({"type": "terrain", "hasRoad": False}, "same field as qb_gls_1"),
    "qb_fd_1":   ({"hasRoad": True},
                  "a ford is where a road crosses water; wetland was never right"),
    "qb_fd_2":   ({"hasRoad": True}, "same crossing as qb_fd_1"),
    "qb_cro_1":  ({"type": "terrain", "hasRoad": False},
                  'text says "in a hollow... well away from any road"'),
    "qb_rd_1":   ({"hasRoad": True}, "the quest is about a road"),
    "qb_rd_2":   ({"hasRoad": True}, "same grade as qb_rd_1"),
    # adjacency drop - anchor contradicted the fiction and could not pin anyway
    "qb_mas_compound": ({"type": "location", "factionAffiliation": "plainers"},
                        "matches qb_mas_revenge, the same compound, already unanchored"),
}


def main(path, write):
    doc = json.load(open(path, encoding="utf-8"))
    beats = {b["id"]: b for b in doc["quest_beats"]}
    missing = [k for k in EDITS if k not in beats]
    if missing:
        print("ERROR - beat ids not found: %s" % missing); return 2

    before_text = {b["id"]: b.get("text") for b in doc["quest_beats"]}
    before_choice = {c["id"]: (c.get("label"), c.get("outcomeText")) for c in doc["choices"]}

    for bid, (newf, why) in EDITS.items():
        b = beats[bid]
        print("\n%s  (%s)" % (bid, b.get("questId")))
        print("  why   : %s" % why)
        print("  before: %s" % json.dumps(b.get("placementFilter")))
        print("  after : %s" % json.dumps(newf))
        b["placementFilter"] = newf

    # the whole point of this plan was zero prose change - prove it
    prose_changed = [b["id"] for b in doc["quest_beats"] if b.get("text") != before_text[b["id"]]]
    choice_changed = [c["id"] for c in doc["choices"]
                      if (c.get("label"), c.get("outcomeText")) != before_choice[c["id"]]]
    print("\nPROSE CHECK  beat texts changed: %d  choice label/outcome changed: %d"
          % (len(prose_changed), len(choice_changed)))
    if prose_changed or choice_changed:
        print("  *** UNEXPECTED *** %s %s" % (prose_changed, choice_changed)); return 3

    blob = json.dumps(doc)
    for dead in ('"terrain":', '"hasAbility"'):
        print("residual %-16s %d" % (dead, blob.count(dead)))

    if write:
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, indent=1, ensure_ascii=False)
        print("\nWROTE %s" % path)
    else:
        print("\nDry run. Pass --write to apply.")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.exit(main(args[0], "--write" in sys.argv))
