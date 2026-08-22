# Capability gating — full sweep

*"Does the player have X"* across buildings, researched technology, and upgrade
chips. **All [VERIFIED-PARSED].** Companion to `dsl-val-defect.md`, which explains
why none of it currently fires.

---

## 1. Headline

**The corpus contains exactly four capability gates. All four are dead. There are
zero chip gates and zero building gates.**

| Axis | Gates in corpus | Working |
|---|---:|---:|
| Technology / skill-tree investment | **4** | **0** |
| Upgrade chips installed | **0** | — |
| Buildings owned | **0** | — |

---

## 2. The four gates — one consistent encoding

Every capability gate in the file uses the same form:
**`{op: "gte", left: "players.active.<stat>", right: <int>}`**

| Choice | Stat | Threshold | The option gated |
|---|---|---:|---|
| `ch_bunker_lab` "Study it properly" | `techLevel` | 1 | the 15% safe route into the bunker |
| `ch_sig_intrigue` "Get him out quietly" | `intrigue` | 2 | extraction with no shot fired |
| `ch_car_spy` "Offer to find out why" | `recon` | 2 | offering intelligence instead of grain |
| `ch_cro_observe` "Watch from the ridge" | `recon` | 1 | scouting instead of riding in |

**The authors did not reach for different encodings in different places.** One
form, three stats, four sites. That consistency is worth stating plainly: this is
not a mess to be reconciled, it is a single small vocabulary that has never been
wired up.

Complete list of dot-paths in the entire corpus — there are only three:

```
players.active.recon      x2
players.active.techLevel  x1
players.active.intrigue   x1
```

## 3. Two shapes, and the espionage case is the second one

The engine agent should know it is building **a tree-category query with a
threshold, not a membership test.** Both shapes are present:

- **Global aggregate** — `techLevel >= 1`. Overall technological development.
- **Branch aggregate** — `intrigue >= 2`, `recon >= 1|2`. **Investment in a
  branch of the tree, not possession of a specific leaf.**

The user's description of the espionage case — *"checks if you've invested any
tech into the intrigue or espionage skill tree"* — is exactly the second shape,
and `intrigue >= 2` is exactly how the author wrote it. **Content and stated
intent agree.**

Note the thresholds are small (1 and 2) and graded: `recon` gates at 1 for the
cheap option (scouting) and 2 for the expensive one (running an intelligence
operation for a foreign power). That is a deliberate two-tier read of one branch,
and it only works if the query returns *how much* has been invested, not whether
anything has.

## 4. The earn side exists and is healthy

The capability loop is only half-broken. Tech is **granted** 25 times across the
corpus, in amounts −1 to +4:

```
+1 ch_bunker_lab · +1 ch_bunker_rough · +1 ch_bunker_technician · +2 ch_sig_out_free
+2 ch_app3r_ack · +2 ch_app3r_refuse · +3 ch_wir1_hire · +4 ch_wir1_take
+2 ch_gls2_study · +2 ch_wir2_paid · +3 ch_wir2_offer  … 25 total
```

So the content pays out tech generously and then checks it four times, and all
four checks fail. **Players have been accumulating a currency that has never once
opened a door.**

Note `ch_bunker_lab` both requires `techLevel >= 1` and grants `Tech +1` — the
safe route pays forward into the next gate. That loop is intact in the writing.

## 5. Chips and buildings — nothing to sweep, and one thing to raise

Exhaustive search of the whole 548 KB file:

```
"chipId" 0 · "chip" 0 · GRANT_CHIP 0 · has_chip 0
"building" 0 · "buildingId" 0 · "structure" 0 · "techId" 0 · "upgrade" 0
```

**No capability gate in this corpus references a chip or a building.** So there
are no dangling chip/building ids to correct — the requested check for predicates
naming nonexistent content returns **empty on those axes**, because those axes are
unused.

Two consequences worth the user's attention:

1. **`has_chip` is implemented in the engine today and no content uses it.**
   [FROM-CONTRACT] it supports `holder ∈ active-player-units |
   active-player-locations | any-unit-on-hex | any-location-on-hex`. If
   chip-based gating is wanted, the engine side already exists and the *content*
   is what is missing.
2. **"Has a lab built" cannot currently be expressed at all.** [FROM-CONTRACT]
   the implemented condition forms are `has_flag`, `count_flags`, `all`, `any`,
   `not`, `op`, `score`, `quest_active`, `quest_completed`, `controls_count`,
   `control_duration`, `has_chip`, `unit_count`, `zoc_contains`. **There is no
   building predicate.** The author's `techLevel >= 1` is the nearest available
   proxy, and given the vocabulary it may be the right call rather than a mistake.

## 6. What needs validating engine-side

The only unresolved question, and it decides whether §2 is engine work or content
work:

**Do `techLevel`, `intrigue` and `recon` exist as fields on a player?**

[FROM-CONTRACT] the engine describes `permanentResearch` and a derived wheel, and
never mentions any of the three. If they do not exist, fixing `Val` token
substitution is **not sufficient** — the path would resolve to a real player
object and then to `undefined`, and all four gates stay dead.

Three outcomes:

| If… | Then |
|---|---|
| all three exist | pure engine fix — `Val` substitution, content is correct as written |
| they exist under other names | **content correction** — rename the three paths |
| branch aggregates don't exist as a concept | **engine feature** — a tree-category query with a threshold, per §3 |

## 7. On the bunker, specifically

Content encodes `techLevel >= 1`; the user's intent is *"requires having a lab
already built."* These are the same gate only if tech level 1 is reachable
solely by building a lab. If tech can be raised another way — and §4 shows **25
content-granted Tech effects**, several of which are unrelated to labs — then the
gate is looser than intended, and a player could be offered the safe bunker route
having never built a lab.

**This is the one genuine candidate for a content correction in the whole sweep**,
and it is not fixable from the content side alone: it needs a building predicate
that does not exist (§5.2), or a flag set when a lab is built. **Flagging for the
user's ruling, not changing.**
