# `qb_mas_compound` — is the `withinHexesOf` adjacency load-bearing?

**No. It contradicts the fiction, and the author already sited the same place
without it.** [VERIFIED-PARSED]

## 1. The fiction requires distance, not adjacency

The chain, in the content's own words:

| Beat | Text |
|---|---|
| `qb_mas_1` | *"…points out **the tracks going west**."* Choice: **"Follow the tracks"** → *"Heavy wheels and a lot of them, **running west and not troubling to hide it**."* |
| `qb_mas_compound` | *"**The tracks end** at a wall built out of the old world…"* |
| `qb_mas_goldgrass` | *"…the ring of welded haulers **a half day west of here**."* |

The whole premise is a pursuit. You find bodies, you are shown tracks heading
west, you follow them, and they *end* somewhere. **A compound one hex from the
massacre is not somewhere the tracks "end" — it is somewhere you could see from
the bodies.** And `qb_mas_goldgrass` puts real distance on it explicitly: half a
day's travel.

Range 1 does not merely under-place the beat. **It states the opposite of what the
prose says.**

## 2. The author already placed the same location unanchored

`qb_mas_revenge` (ordinal 4) is the *same compound* — *"You go back with the
Goldgrass at your shoulder… This time nobody on the rampart asks what you want."*

Its filter:

```json
{"type": "location", "factionAffiliation": "plainers"}
```

**Unanchored.** So the author's own treatment of that place, two beats later, is
exactly the filter proposed as the replacement. The anchor at ordinal 2 is
inconsistent with ordinal 4, not with a design.

## 3. The anchor could not have done what it looks like it does

`withinHexesOf: {hex: "encounter-hex", range: 1}` anchors to **whatever encounter
is currently firing** — not to the massacre site.

And `qb_mas_compound` has **no prereq and `deliverCondition: null`**, so it is not
gated on `qb_mas_1` at all. It can become ready independently, at which point
`encounter-hex` resolves to something arbitrary. **The anchor was never reliably
pinning the compound near the bodies**, even on the 9 boards in 12 where it
placed.

## 4. Recommendation

**Drop the anchor: `{"type": "location", "factionAffiliation": "plainers"}`.**

- Matches `qb_mas_revenge` exactly, which is the same location.
- 2 hexes per board, unanchored — universal.
- Recovers `q_massacre`'s ordinal-2 beat and, downstream, `q_haulers`, which opens on `mas_knows_location` and can only get it here.
- **Prose cost: zero.** Distance is what the text already describes.

## 5. One thing the drop does *not* solve, and the mechanism that would

With both `qb_mas_compound` and `qb_mas_revenge` on `{location, plainers}` and two
such hexes per board, they can land on **different** hexes — so *"you go back"*
could return to a compound you have never seen.

The anchor may have been an attempt to prevent that. It could not have — it
anchored to `encounter-hex`, not to where the compound was placed.

**The right mechanism now exists.** The engine agent's fix for `ef_wks4l_holding`
made a quest remember where it was discovered and carry that into every later
beat. If that discovery hex is exposed as a placement token — a
`quest-hex` alongside `encounter-hex` / `unit-hex` / `capital-hex` — then
`qb_mas_revenge` becomes:

```json
{"type": "location", "factionAffiliation": "plainers",
 "withinHexesOf": {"hex": "quest-hex", "range": 0}}
```

…i.e. *the same place*, which is what the fiction means. **Worth raising as a
capability question rather than blocking on it** — dropping the anchor is correct
and universal today, and the pinning is a refinement that costs nothing to defer.
