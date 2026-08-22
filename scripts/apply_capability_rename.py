"""
apply_capability_rename.py - replace the four dead capability gates.

BLOCKED until Q1-Q4 in docs/import/HANDOVER-peek-scope-and-capability-rename.md
are answered. Fill the four constants below, then:

    python scripts/apply_capability_rename.py <consolidated.json> [--write]

Without --write it prints a diff and changes nothing.

Why these four: the corpus reads techLevel/intrigue/recon and never writes them,
so they are engine-side tree/chip state. techLevel in particular is 1 for every
player from turn one (engine-contract A2), so that gate currently FAILS OPEN.
"""
import json, sys, copy

# ---------------------------------------------------------------- FILL THESE IN
# Q2: the actual chip ids for lab tiers, from the engine side.
LAB_CHIP_IDS = ["labs", "advanced-lab"]   # A8: the only two; both kind:"location"
# Q1: which holder value scopes to locations on a single hex.
LAB_HOLDER = "location-on-hex"   # A8: single-hex scope. NOT active-player-locations
                                 # (territory-wide) - the user's ruling is that the
                                 # lab must be AT the hex being studied.
# Q1: the list key - "chipIds", or "chipId" accepting an array.
CHIP_LIST_KEY = "chipId"     # A8: the key is chipId and it accepts an array.
                             # There is no chipIds.
# Q3: branch identifier for the espionage/intrigue tree.
INTRIGUE_PATH   = "intelligence"   # A8: paths are military|logistics|economy|intelligence
INTRIGUE_BRANCH = "b"              # A8: intelligence a=Vision, b=Espionage.
                                   # branch excludes the entry node by design.
# Q4: branch identifier for recon -- OR switch to the chip form, see the handover.
# recon is a BRANCH distinction, not a depth one. count_tech{path:"intelligence"}
# counts nodes on the path, so entry + Vision-1 scores 2 - two levels of pure
# scouting satisfying a "run an operation abroad" gate it has nothing to do with.
# So: 1 => any investment in Intelligence; 2 => the Espionage fork specifically.
RECON_PATH        = "intelligence"
RECON_FORK_BRANCH = "b"          # Espionage
RECON_BRANCH = "RESOLVED"        # sentinel: no longer blocking
RECON_AS_CHIPS = False       # True => use count_chips on a recon-team chip instead
RECON_CHIP_IDS = None        # e.g. ["recon-team"]
# ------------------------------------------------------------------------------


def lab_predicate():
    """Bunker: a lab AT THE ENCOUNTER'S HEX. The user's ruling is explicit --
    'the lab needs to be in that place to study that place' -- so this must not
    default to territory-wide."""
    return {"has_chip": {"holder": LAB_HOLDER,
                         CHIP_LIST_KEY: LAB_CHIP_IDS,
                         "player": "active",
                         "hex": "encounter-hex"}}


def intrigue_predicate():
    return {"has_tech": {"path": INTRIGUE_PATH, "branch": INTRIGUE_BRANCH,
                         "player": "active"}}


def recon_predicate(tier):
    """tier 1 = any investment in Intelligence; tier 2 = the Espionage fork.
    Deliberately NOT count_tech >= N - see the note on RECON_PATH."""
    q = {"path": RECON_PATH, "player": "active"}
    if tier == 2:
        q = {"path": RECON_PATH, "branch": RECON_FORK_BRANCH, "player": "active"}
    return {"has_tech": q}


# choiceId -> (description, builder). Thresholds preserved from the original.
EDITS = {
    "ch_bunker_lab": ("techLevel>=1 -> lab chip at encounter hex", lambda old: {
        # keep the Versari disjunct: it is a faction check and now works post-Val
        "any": [lab_predicate(),
                {"op": "eq", "left": "active", "right": "versari"}]}),
    "ch_sig_intrigue": ("intrigue>=2 -> has_tech espionage",
                        lambda old: intrigue_predicate()),
    "ch_cro_observe": ("recon>=1 -> has_tech any Intelligence",
                       lambda old: recon_predicate(1)),
    "ch_car_spy": ("recon>=2 -> has_tech Espionage fork",
                   lambda old: recon_predicate(2)),
}


def main(path, write):
    edits = dict(EDITS)
    if (not RECON_AS_CHIPS and RECON_BRANCH is None) or (RECON_AS_CHIPS and RECON_CHIP_IDS is None):
        for k in ("ch_cro_observe", "ch_car_spy"):
            edits.pop(k, None)
        print("NOTE: recon branch id not yet supplied - HOLDING ch_cro_observe and")
        print("      ch_car_spy. Applying the lab and intrigue gates only.\n")
    for n, v in (("LAB_CHIP_IDS", LAB_CHIP_IDS), ("LAB_HOLDER", LAB_HOLDER),
                 ("CHIP_LIST_KEY", CHIP_LIST_KEY), ("INTRIGUE_BRANCH", INTRIGUE_BRANCH)):
        if v is None:
            print("BLOCKED - %s unset" % n); return 1

    doc = json.load(open(path, encoding="utf-8"))
    by_id = {c["id"]: c for c in doc["choices"]}
    missing = [k for k in EDITS if k not in by_id]
    if missing:
        print("ERROR - choice ids not found: %s" % missing)
        return 2

    for cid, (desc, build) in edits.items():
        c = by_id[cid]
        before = copy.deepcopy(c.get("condition"))
        after = build(before)
        print("\n%s  (%s)" % (cid, desc))
        print("  label : %r" % c.get("label"))
        print("  before: %s" % json.dumps(before))
        print("  after : %s" % json.dumps(after))
        c["condition"] = after

    # nothing else in the corpus may reference these three paths afterwards
    blob = json.dumps(doc)
    for dead in ("players.active.techLevel", "players.active.intrigue",
                 "players.active.recon"):
        pass
    for dead in ("players.active.techLevel", "players.active.intrigue",
                 "players.active.recon"):
        n = blob.count(dead)
        print("\nresidual %-28s %d %s" % (dead, n, "OK" if n == 0 else "*** STILL PRESENT ***"))

    if write:
        # Match the source file's own formatting exactly: 1-space indent, UTF-8
        # literals, trailing newline. Anything else turns a two-line change into a
        # 21,000-line diff nobody can review.
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, indent=1, ensure_ascii=False)
            # Source file has no trailing newline; matching it keeps the diff to
            # the semantic change alone.
        print("\nWROTE %s" % path)
    else:
        print("\nDry run. Pass --write to apply.")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.exit(main(args[0], "--write" in sys.argv))
