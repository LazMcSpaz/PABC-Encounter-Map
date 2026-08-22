"""
effect_census.py — the inventory that docs/import/content-inventory.md is
blocked on. Run it against the consolidated encounter-builder export as soon as
that file exists.

Usage:  python scripts/effect_census.py <consolidated.json>

Counts effect types RECURSIVELY (params.effects / onSuccess / onFail / onWin /
onLose / options[].effects), because a flat count of top-level rows undercounts.
Recursion set taken from index.html's walkEffects().
"""
import json, sys, collections

NEST_KEYS = ("effects", "onSuccess", "onFail", "onWin", "onLose")


def params(e):
    p = e.get("paramsJson") or e.get("params") or {}
    if isinstance(p, str):
        try:
            p = json.loads(p)
        except ValueError:
            p = {}
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


def main(path):
    src = json.load(open(path, encoding="utf-8"))

    types = collections.Counter()
    fields = collections.defaultdict(collections.Counter)
    values = collections.defaultdict(lambda: collections.defaultdict(set))
    depths = collections.defaultdict(collections.Counter)

    for e, d in walk(src.get("effects", [])):
        t = e["type"]
        types[t] += 1
        depths[t][d] += 1
        for k, v in params(e).items():
            fields[t][k] += 1
            if isinstance(v, (str, int, float, bool)) or v is None:
                values[t][k].add(v)

    print(f"{sum(types.values())} effect instances, {len(types)} distinct types\n")
    for t, n in types.most_common():
        nest = ", ".join(f"depth{d}×{c}" for d, c in sorted(depths[t].items()))
        print(f"{t}  ×{n}   ({nest})")
        for k, c in fields[t].most_common():
            vs = values[t][k]
            sample = ""
            if vs:
                shown = sorted(vs, key=lambda x: (x is None, str(x)))[:8]
                sample = "  e.g. " + ", ".join(repr(x) for x in shown)
                if len(vs) > 8:
                    sample += f", … ({len(vs)} distinct)"
            print(f"    {k}: {c}/{n}{sample}")
        print()

    for table in ("world_encounters", "field_encounters", "quests",
                  "quest_beats", "quest_beat_prereqs", "choices", "effects"):
        rows = src.get(table)
        print(f"{table}: {len(rows) if isinstance(rows, list) else 'ABSENT'}")


if __name__ == "__main__":
    main(sys.argv[1])
