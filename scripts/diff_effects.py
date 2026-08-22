"""
diff_effects.py - re-derive docs/import/effect-diff.md from the real file.

Every content-side number in effect-diff.md is currently RELAYED, not parsed.
This script replaces all of them.

Usage:  python scripts/diff_effects.py remnant_content_consolidated_rev2.json

Engine vocabulary below is transcribed from
PABC/docs/encounter-import/engine-contract.md @ main d623ae0.
"""
import json, sys, collections

EDITOR_23 = {
    # Group A - core (13)
    "ADJUST_RESOURCE", "MODIFY_STAT", "GRANT_ACTIONS", "MOVE_CARD", "SET_FLAG",
    "TRANSFER", "CONVERT", "SPAWN", "PEEK", "FORCE_CHOICE", "SURCHARGE",
    "REDIRECT", "CANCEL",
    # Group B - encounter/quest (9)
    "ADJUST_TRACK", "ADJUST_STANDING", "SET_PLAYER_FLAG", "QUEUE_DEFERRED",
    "START_QUEST", "ADVANCE_QUEST", "COMPLETE_QUEST", "PLACE_ENCOUNTER",
    "DELIVER_ENCOUNTER",
    # Group C - attrition (1)
    "ADJUST_BASE_STRENGTH",
}
ENGINE_ONLY_19 = {
    "GRANT_CHIP", "DISABLE_CHIP", "STRIP_CHIP",
    "REVEAL_REGION", "GRANT_VISION", "PLANT_FALSE_INTEL",
    "ADJUST_MENACE", "ADJUST_HONOR", "DECLARE_WAR", "MAKE_PEACE", "FORM_PACT",
    "BREAK_PACT", "CALL_PACT", "DENOUNCE", "MEDIATE", "VASSALIZE",
    "RELEASE_VASSAL", "RESOLVE_DEAL", "PROPOSE_DEAL",
}
ENGINE_42 = EDITOR_23 | ENGINE_ONLY_19
INERT = {"PEEK": "empty handler body", "SURCHARGE": "state.surcharges never read",
         "SPAWN": "empty handler body", "SET_FLAG": "entity.flags never read"}

DEAD_TOKENS = {"random", "most-raided", "least-engaged"}
DEAD_PREFIXES = ("lowest-standing-with:", "highest-standing-with:", "controller-of:")
LIVE_TOKENS = {"active", "each", "triggering-player", "chosen-by-active", "claimant",
               "versari", "goldgrass", "lakers", "plainers",
               "self", "controller", "active_player", "triggering_player",
               "all_players", "each_opponent", "random_opponent", "chosen_opponent",
               "defending_unit", "stationed_unit", "entity"}

NEST_KEYS = ("effects", "onSuccess", "onFail", "onWin", "onLose")
TOKEN_FIELDS = ("target", "recipient", "player", "claimant", "chooser", "actor")


def params(e):
    p = e.get("paramsJson", e.get("params")) or {}
    if isinstance(p, str):
        try:
            p = json.loads(p)
        except ValueError:
            return {}
    return p if isinstance(p, dict) else {}


def walk(effects, depth=0):
    for e in effects or []:
        if not isinstance(e, dict) or not e.get("type"):
            continue
        yield e, depth
        p = params(e)
        for k in NEST_KEYS:
            if isinstance(p.get(k), list):
                yield from walk(p[k], depth + 1)
        for opt in p.get("options") or []:
            if isinstance(opt, dict) and isinstance(opt.get("effects"), list):
                yield from walk(opt["effects"], depth + 1)


def token_status(tok):
    if not isinstance(tok, str):
        return "non-string"
    if tok in DEAD_TOKENS or tok.startswith(DEAD_PREFIXES):
        return "DEAD"
    if tok in LIVE_TOKENS:
        return "ok"
    return "UNKNOWN"


def main(path):
    src = json.load(open(path, encoding="utf-8"))

    print("=== TABLES ===")
    for t in ("world_encounters", "field_encounters", "quests", "quest_beats",
              "quest_beat_prereqs", "choices", "effects"):
        rows = src.get(t)
        print("  %-22s %s" % (t, len(rows) if isinstance(rows, list) else "ABSENT"))

    top = collections.Counter()
    nested = collections.Counter()
    for e, d in walk(src.get("effects", [])):
        (top if d == 0 else nested)[e["type"]] += 1

    print("\n=== EFFECT CENSUS ===")
    print("  top-level %d | nested %d | total %d | distinct %d"
          % (sum(top.values()), sum(nested.values()),
             sum(top.values()) + sum(nested.values()),
             len(set(top) | set(nested))))

    buckets = collections.defaultdict(list)
    for t in sorted(set(top) | set(nested), key=lambda x: -(top[x] + nested[x])):
        n = top[t] + nested[t]
        if t not in ENGINE_42:
            b = "3-THROWS"
        elif t in INERT:
            b = "1b-INERT"
        elif t in ENGINE_ONLY_19:
            b = "2-EDITOR-REJECTS"
        else:
            b = "1-OK"
        buckets[b].append((t, top[t], nested[t], n))

    for b in ("1-OK", "1b-INERT", "2-EDITOR-REJECTS", "3-THROWS"):
        rows = buckets.get(b, [])
        print("\n--- %s : %d instances, %d types ---" % (b, sum(r[3] for r in rows), len(rows)))
        for t, tp, ns, n in rows:
            extra = "  <- " + INERT[t] if t in INERT else ""
            print("    %-24s %5d  (top %d, nested %d)%s" % (t, n, tp, ns, extra))

    print("\n=== RECIPIENT TOKENS  (highest-risk item) ===")
    tokens = collections.Counter()
    by_type = collections.defaultdict(collections.Counter)
    for e, _ in walk(src.get("effects", [])):
        p = params(e)
        for f in TOKEN_FIELDS:
            if f in p and isinstance(p[f], str):
                tokens[p[f]] += 1
                by_type[p[f]][e["type"]] += 1
    for tok, n in tokens.most_common():
        st = token_status(tok)
        mark = {"DEAD": " *** SILENT NO-OP ***", "UNKNOWN": " ??? not in either vocabulary"}.get(st, "")
        print("  %-34s %5d  [%s]%s" % (repr(tok), n, st, mark))
        if st != "ok":
            print("        used by: " + ", ".join("%s x%d" % kv for kv in by_type[tok].most_common()))
    dead = sum(n for t, n in tokens.items() if token_status(t) == "DEAD")
    print("\n  %d instances carry a dead token." % dead)

    print("\n=== SEMANTIC COLLISIONS ===")
    beats = src.get("quest_beats") or []
    cond = [b for b in beats if b.get("deliver") == "conditional"]
    print("  quest_beats deliver=conditional : %d  (deliverCondition never read -> all fire unconditionally)"
          % len(cond))
    print("  explicit ADVANCE_QUEST rows     : %d  (engine may auto-append per choice -> double-advance)"
          % (top["ADVANCE_QUEST"] + nested["ADVANCE_QUEST"]))

    we = src.get("world_encounters") or []
    tw = [r for r in we if "triggerWeight" in r]
    print("  world_encounters w/ triggerWeight: %d / %d  (importer rejects: unknown column)" % (len(tw), len(we)))

    per_parent = collections.Counter(c.get("parentId") for c in src.get("choices") or [])
    over = {k: v for k, v in per_parent.items() if v > 3}
    print("  parents with >3 choices          : %d  (validator caps at 3)" % len(over))
    for k, v in sorted(over.items(), key=lambda x: -x[1])[:10]:
        print("      %s: %d" % (k, v))

    shapes = collections.Counter()
    for e in src.get("effects") or []:
        shapes["paramsJson" if "paramsJson" in e else ("params" if "params" in e else "NEITHER")] += 1
    print("  effect param key                 : %s" % dict(shapes))

    print("\n=== COUNT_FLAGS (not in engine DSL -> evaluates false) ===")
    blob = json.dumps(src)
    print("  count_flags occurrences: %d" % blob.count("count_flags"))


if __name__ == "__main__":
    main(sys.argv[1])
