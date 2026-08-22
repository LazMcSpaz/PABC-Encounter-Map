# Terrain-blocked quests — re-siting proposals

**Content facts [VERIFIED-PARSED].** Board facts [FROM-CONTRACT §A10], measured
off generated boards.

**Supersedes my previous version of this file.** Two corrections below, one of
them mine.

---

## 1. Corrections

### 1a. I said ten quests were blocked. It is five. `hasRoad` is live.

I read §4.9's *"`hex.road` is `undefined`"* and counted the seven `hasRoad: true`
beats as dead. **§A10 measures `hasRoad` at 15 true / 15 false on a 30-hex board**
and explicitly corrects §4.9. So `q_caravan`, `q_courier`, `q_massacre`,
`q_runner` and `q_saltman` were never blocked — their openers place on roughly
half the map.

**Blocked openers, corrected — five quests, all on a `terrain:` value:**

| Quest | Beats | Opener filter |
|---|---:|---|
| `q_works` | 6 | `{type:"terrain", terrain:"rubble"}` |
| `q_glass` | 2 | `{type:"terrain", terrain:"rubble"}` |
| `q_ford` | 2 | `{type:"terrain", terrain:"wetland"}` |
| `q_croppers` | 6 | `{type:"terrain", terrain:"any"}` |
| `q_road` | 2 | `{type:"terrain", terrain:"any"}` |

**18 beats behind five blocked openers** — if `terrain:"any"` is dead. If it is
special-cased as a wildcard, `q_croppers` and `q_road` already place and the
figure is **10 beats behind three openers**. §A10 says `terrain` is dead and *"do
not re-site onto any terrain sub-type"* but does not say whether `"any"` short-
circuits. **One line settles it and it changes the count by 8 beats.**

Either way my count does not reconcile with the "9 of 14" I was given — flagging
rather than assuming one of us is right.

### 1b. My previous recommendation was too narrow

I proposed collapsing everything to `{"type":"terrain"}`. **That is only 7 of 30
hexes** — the scarcest type on the board. It would have unblocked the quests and
made them rare. The proposals below use `hasRoad`, which did not appear usable
when I wrote that.

---

## 2. Proposals

Fiction first, then the filter that carries it. §A10 measures
`{type:"terrain", hasRoad:false}` and `{type:"encounter", hasRoad:true}` at
**12/12 boards**, so both anchors below are already proven universal.

### `q_ford` — "Somebody's Watching the Ford" · 2 beats

**Fiction requires:** a crossing narrow enough that everyone who passes can be
counted from one blind. *"A blind above the river crossing… with a clean sight
line onto the ford and weeks of tally marks scratched into the back board."*

**Terrain named in prose:** `crossing`, `ford`, `river`, `bank` in the opener;
`ford` / `crossings` in four of `qb_fd_2`'s outcome texts. **The most
terrain-bound of the five.**

**Proposal: `{hasRoad: true}`** — optionally `{type:"encounter", hasRoad:true}`
(12/12 measured).

**A ford is where a road crosses water.** `hasRoad` is not an approximation of
this fiction, it *is* the fiction — far closer than `wetland`, which was never
right; a ford is a crossing, not a marsh. The author picked the nearest thing
available at the time.

**Prose cost: zero.** Every terrain word stays true.

This is the quest I previously said was the hard case. `hasRoad` being live makes
it the easiest.

### `q_road` — "The Grade" · 2 beats

**Fiction requires:** a surviving stretch of old-world roadbed. *"Two miles of
pre-collapse roadbed running dead flat and dead true across broken country, a
century on, with the drainage still working."*

**Terrain named:** `road`, `roadbed`.

**Proposal: `{hasRoad: true}`.** The quest is *about* a road. **Prose cost: zero.**

### `q_croppers` — "The Goddess of the Fields" · 6 beats

**Fiction requires:** somewhere out of the way enough to hold a rite unobserved.
*"Forty or fifty Croppers in a hollow in the middle of open country, **well away
from any road**."*

**Terrain named:** `road` — **in the negative.**

**Proposal: `{type:"terrain", hasRoad:false}` — 12/12 boards measured.**

The prose states the requirement outright, and the filter now says the same thing.
This is the best fiction-to-filter fit of the five, and it is universal.
**Prose cost: zero.**

### `q_glass` — "The Glass Field" · 2 beats

**Fiction requires:** open country with something inexplicable in it, remote
enough that a family has grazed goats beside it for eleven years without anyone
doing anything about it.

**Terrain named:** none. The current filter **contradicts the writing** — *"It is
not a crater. There is no bowl, no rim, and no spoil anywhere."* Grass grows right
up to the edge. That is the opposite of rubble.

**Proposal: `{type:"terrain", hasRoad:false}` — 12/12 boards.**

Off the road matches *"a wire-reader passing through the district on somebody
else's business"* — she is passing through the district, not along that hex.
**Prose cost: zero**, and it resolves a mismatch that predates the terrain problem.

### `q_works` — "The Works" · 6 beats

**Fiction requires:** a quantity of old-world iron lying unclaimed, reachable
enough that forty people can be fed there and hauls can go east. *"There is a
Laker crew on the scrap field… this iron has been lying here since before either
of your grandmothers."*

**Terrain named in the opener:** none. `rubble` was a proxy for *"where salvage
is"*. But `qb_wks_3` names *"a name painted on a board at the **road end**"*, and
`qb_wks_2` needs *"safe passage for the hauls going east"*.

**Proposal: `{hasRoad: true}`** — the quest's own later prose puts it on a road.

**Prose cost: zero**, and it makes `qb_wks_3` literally true rather than
incidentally so.

---

## 3. Should any stop being `discovered`? — No, and here is why

Each of the five opens with something the player's riders **come upon**: a blind
above a crossing, a crew already pouring a footing, forty acres of glass with a
house at the edge, singing in a hollow, two miles of roadbed. The discovery is the
beat.

Converting to `conditional` would sidestep placement entirely — it is the most
robust answer mechanically — but it costs 1–2 rewritten sentences per opener to
turn a thing you ride into a thing you are told about, and it removes what makes
them field content. **Since every proposal above is either measured at 12/12 or
sits on half the board, the robustness argument for converting has gone.** I would
not convert any of them.

---

## 4. Two structural points

### 4a. A "fallback clause" is not expressible in content today

§A10 recommends a fallback for placements that must work on every board. **§4.9
says `hexMatches` has no OR and no NOT compound operators** — all keys are AND-ed.
So content cannot express *"a road hex, or failing that any terrain hex."*

Either the engine gains a fallback (an ordered list of filters, first match wins),
or content must use single wide filters. **The proposals above take the second
route deliberately** — one or two keys, each measured wide — rather than assuming
a capability that does not exist.

### 4b. `qb_mas_compound` at range 3 is 9/12, and that is not enough

Widening recovers it on most boards, but a quest that fails on 3 boards in 12 is
still a quest a player may never see. Since `q_haulers` opens on a flag only
`qb_mas_compound` writes, **that 3-in-12 failure silently costs two quests, not
one.**

If the target is genuinely 131/131 on every board, range-anchored placement cannot
get there without either a fallback (4a) or dropping the `withinHexesOf` anchor.
`{type:"location", factionAffiliation:"plainers"}` unanchored is 2 hexes per board
and would be universal — the anchor is what makes it fragile. **Worth asking
whether the "within 1 hex of where the last beat fired" adjacency is load-bearing
fiction, or was tightening for its own sake.** I can check the prose if useful.

---

## 5. Summary

| Quest | Beats | Proposed filter | Expected reach | Prose cost |
|---|---:|---|---|---|
| `q_ford` | 2 | `{hasRoad: true}` | ~15/30 hexes | none |
| `q_road` | 2 | `{hasRoad: true}` | ~15/30 | none |
| `q_works` | 6 | `{hasRoad: true}` | ~15/30 | none |
| `q_croppers` | 6 | `{type:"terrain", hasRoad:false}` | **12/12 boards** | none |
| `q_glass` | 2 | `{type:"terrain", hasRoad:false}` | **12/12 boards** | none |

**18 beats, zero words of prose changed, and two of the five now say in their
filter what they already said in their text.**

Please measure the three `{hasRoad: true}` proposals across the 12-board sample —
I would rather have the number than the estimate, and if bare `hasRoad` comes back
below 12/12 the natural tightening is `{type:"encounter", hasRoad:true}`, which
§A10 already measures at 12/12.
