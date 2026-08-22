"""
audit_choices.py - audit choice labels for decision-context sufficiency.

Standard (from the user):
  The player must understand WHAT THEY ARE CHOOSING TO DO.
  The player must NOT learn WHAT THE OUTCOME WILL BE.
  There is no length target. A clear three-word choice is already correct.

So this does NOT flag "short". It flags "unclear". Those are different, and
conflating them is the failure mode this audit exists to avoid.

Usage:  python scripts/audit_choices.py <consolidated.json> [--json out.json]
"""
import json, sys, re, collections, difflib

# Verbs that name a posture but not an action. Fine WITH an object, thin alone.
BARE_VERBS = {
    "accept", "refuse", "decline", "agree", "disagree", "comply", "resist",
    "investigate", "explore", "search", "look", "wait", "leave", "stay", "go",
    "help", "assist", "ignore", "continue", "proceed", "stop", "attack",
    "fight", "flee", "run", "hide", "talk", "speak", "listen", "ask", "tell",
    "trade", "negotiate", "bargain", "take", "give", "keep", "drop", "open",
    "close", "enter", "exit", "push", "pull", "yes", "no", "nothing", "insist",
    "press", "relent", "withdraw", "advance", "retreat", "intervene", "abstain",
}
# Pronouns with no antecedent inside the label itself.
DEICTIC = {"it", "them", "him", "her", "this", "that", "those", "these", "one"}

HEDGE = {"something", "somehow", "someone", "anything", "whatever", "maybe"}

# label-intent vs effect-direction, for the MISLEADING check
# Word-boundary regex, NOT substring. The substring version matched "pay" inside
# "payment", "share" inside "Take the share", "offer" inside "what she offers" -
# every one a false positive. Kept as a regex so that stays fixed.
REFUSAL_RE = r"\b(refuse[sd]?|decline[sd]?|reject|walk away|say nothing|turn down|abstain|ignore|leave|leaves|withdraw|back out)\b"

# The GENEROSITY and AGGRESSION detectors were REMOVED, not fixed. Both rested on
# "gave something away but score went up = misleading", which is simply wrong in
# this fiction: generosity is *rewarded* with standing and honor, so the premise
# inverts the real design. They produced 12 false positives and zero true ones.
# Faction-mismatch (below) survives because it compares data to data.

# Contrastive pairs. Sibling labels differing by one of these are MAXIMALLY
# distinct, however similar their strings - "Give her the pledge" / "Refuse the
# pledge" scores 0.64. Exempt them or the check inverts.
CONTRAST = [("give", "refuse"), ("grant", "refuse"), ("honor", "refuse"),
            ("press", "withdraw"), ("accept", "refuse"), ("send", "decline"),
            ("take", "leave"), ("comply", "override"), ("open", "close"),
            ("pay", "refuse"), ("help", "leave")]


def words(s):
    return re.findall(r"[a-z']+", (s or "").lower())


def norm(s):
    w = [x for x in words(s) if x not in {"the", "a", "an", "to", "of", "and", "for"}]
    return " ".join(w)


def params(e):
    p = e.get("paramsJson", e.get("params")) or {}
    if isinstance(p, str):
        try:
            p = json.loads(p)
        except ValueError:
            return {}
    return p if isinstance(p, dict) else {}


# Tuned against the real corpus, not guessed. Sweep over all 383 choices' sibling
# pairs:  >=0.60 -> 14 pairs | >=0.65 -> 8 | >=0.70 -> 3 | >=0.72 -> 2 | >=0.80 -> 1
# Below 0.70 the check INVERTS: opposite-meaning pairs that share a noun score
# 0.61-0.67 ("Honor the tally"/"Refuse the tally" = 0.61; "Give her the pledge"/
# "Refuse the pledge" = 0.64), so loosening adds only false positives. 0.70 keeps
# all three genuine hits; 0.72 would drop a real one (we_petition at 0.71).
SIBLING_THRESHOLD = 0.70

NEST = ("effects", "onSuccess", "onFail", "onWin", "onLose")


def walk(effects):
    for e in effects or []:
        if not isinstance(e, dict) or not e.get("type"):
            continue
        yield e
        p = params(e)
        for k in NEST:
            if isinstance(p.get(k), list):
                yield from walk(p[k])
        for o in p.get("options") or []:
            if isinstance(o, dict) and isinstance(o.get("effects"), list):
                yield from walk(o["effects"])


def resource_delta(effs):
    """Net signed movement in player-facing value. Crude but directional."""
    d = 0
    for e in effs:
        p = params(e)
        a = p.get("amount")
        if not isinstance(a, (int, float)):
            continue
        if e["type"] in ("ADJUST_RESOURCE", "ADJUST_TRACK", "ADJUST_STANDING",
                         "ADJUST_HONOR"):
            d += a
        elif e["type"] == "ADJUST_MENACE":
            d -= a
    return d


def audit(path, jsonout=None):
    src = json.load(open(path, encoding="utf-8"))
    choices = src.get("choices") or []
    all_eff = src.get("effects") or []

    by_choice = collections.defaultdict(list)
    for e in all_eff:
        if e.get("parentKind") in ("choice", "choices"):
            by_choice[e.get("parentId")].append(e)

    by_parent = collections.defaultdict(list)
    for c in choices:
        by_parent[c.get("parentId")].append(c)

    findings = []

    for c in choices:
        cid = c.get("id")
        label = (c.get("label") or "").strip()
        w = words(label)
        flags = []

        if not label:
            flags.append(("EMPTY", "no label at all"))

        # --- thin: a bare posture verb with no object ---
        content = [x for x in w if x not in {"the", "a", "an", "to", "of", "it",
                                             "them", "and", "for", "with", "on"}]
        if w and w[0] in BARE_VERBS and len(content) <= 1:
            flags.append(("BARE_VERB",
                          "'%s' names a posture but no object - accept/refuse WHAT?" % w[0]))

        # --- deictic with no antecedent in the label ---
        nouny = [x for x in w if x not in BARE_VERBS and x not in DEICTIC
                 and x not in {"the", "a", "an", "to", "of", "and", "for", "with", "on"}]
        if any(x in DEICTIC for x in w) and not nouny:
            flags.append(("DEICTIC", "refers to 'it/them/this' with no noun in the label"))

        if any(x in HEDGE for x in w):
            flags.append(("HEDGE", "hedging word ('something'/'somehow') hides the action"))

        # --- missing object: verb-initial, no noun-ish token ---
        if w and w[0] in BARE_VERBS and len(w) > 1 and not nouny:
            flags.append(("NO_OBJECT", "verb has no object"))

        findings.append({"id": cid, "parentKind": c.get("parentKind"),
                         "parentId": c.get("parentId"), "ordinal": c.get("ordinal"),
                         "label": label, "flags": flags,
                         "n_effects": len(by_choice.get(cid, []))})

    # --- sibling near-duplicates: the worst class ---
    fmap = {f["id"]: f for f in findings}
    for pid, sibs in by_parent.items():
        for i in range(len(sibs)):
            for j in range(i + 1, len(sibs)):
                a, b = sibs[i], sibs[j]
                la, lb = norm(a.get("label")), norm(b.get("label"))
                if not la or not lb:
                    continue
                r = difflib.SequenceMatcher(None, la, lb).ratio()
                sa, sb = set(la.split()), set(lb.split())
                diff_tokens = sa ^ sb
                if any(x in diff_tokens and y in diff_tokens
                       for x, y in CONTRAST):
                    continue          # opposite actions - distinct by design
                if r >= SIBLING_THRESHOLD:
                    msg = "reads almost identically to %s ('%s') - similarity %.2f" % (
                        b.get("id"), b.get("label"), r)
                    fmap[a["id"]]["flags"].append(("SIBLING_DUP", msg))
                    fmap[b["id"]]["flags"].append(
                        ("SIBLING_DUP", "reads almost identically to %s ('%s') - similarity %.2f"
                         % (a.get("id"), a.get("label"), r)))

    # --- MISLEADING: label intent contradicts effect direction ---
    for f in findings:
        cid, label = f["id"], f["label"].lower()
        effs = list(walk(by_choice.get(cid, [])))
        if not effs:
            continue
        delta = resource_delta(effs)
        types = {e["type"] for e in effs}

        if re.search(REFUSAL_RE, label) and delta > 0:
            f["flags"].append(("MISLEADING_CANDIDATE",
                               "refusal-shaped label, net outcome +%d - REQUIRES HUMAN READ" % delta))

        # faction named in label vs faction actually adjusted
        named = {fid for fid in ("versari", "goldgrass", "lakers", "plainers")
                 if fid in label}
        touched = {params(e).get("faction") for e in effs
                   if e["type"] == "ADJUST_STANDING"}
        touched = {t for t in touched if isinstance(t, str)}
        if named and touched and not (named & touched):
            f["flags"].append(("MISLEADING",
                               "label names %s but standing moves for %s"
                               % (sorted(named), sorted(touched))))

    flagged = [f for f in findings if f["flags"]]
    counts = collections.Counter(k for f in flagged for k, _ in f["flags"])

    print("=== CHOICE AUDIT ===")
    print("  %d choices, %d flagged (%.1f%%), %d clean"
          % (len(findings), len(flagged),
             100.0 * len(flagged) / max(1, len(findings)),
             len(findings) - len(flagged)))
    print("\n  by category:")
    for k, n in counts.most_common():
        print("    %-14s %4d" % (k, n))

    print("\n  length distribution (NOT a defect - context only):")
    ld = collections.Counter(len(words(f["label"])) for f in findings)
    for k in sorted(ld):
        print("    %2d word%s : %4d" % (k, " " if k == 1 else "s", ld[k]))

    order = ["MISLEADING", "MISLEADING_CANDIDATE", "SIBLING_DUP", "EMPTY", "BARE_VERB", "DEICTIC",
             "NO_OBJECT", "HEDGE"]
    for cat in order:
        rows = [f for f in flagged if any(k == cat for k, _ in f["flags"])]
        if not rows:
            continue
        print("\n\n--- %s (%d) ---" % (cat, len(rows)))
        for f in rows:
            why = "; ".join(m for k, m in f["flags"] if k == cat)
            print("  [%s] parent=%s ord=%s" % (f["id"], f["parentId"], f["ordinal"]))
            print("      label: %r" % f["label"])
            print("      why  : %s" % why)

    if jsonout:
        json.dump(findings, open(jsonout, "w", encoding="utf-8"), indent=2)
        print("\n  wrote %s" % jsonout)
    return findings


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = None
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
    audit(args[0], out)
