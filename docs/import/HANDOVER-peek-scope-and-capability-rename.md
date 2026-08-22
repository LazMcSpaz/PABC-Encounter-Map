# Handover — `PEEK` scope list (delivered) + capability rename (blocked on syntax)

---

## PART 1 — `PEEK` scope, all 8 sites. **Delivered, use as-is.**

Derived from the beat's own `deliver` mode, which is the corpus's record of where
a thing fires. `discovered` + `placementFilter` = placed on a hex, found by a unit
→ **field**. `auto` / `conditional` = triggered at the seat → **settlement**.
Table membership is *not* the signal (see Part 3).

| Effect id | Host | Firing site | **scope** | `count` | `deck` |
|---|---|---|---|---:|---|
| `ef_reader_pay_peek` | `fe_ask_the_reader` | field encounter | **`field`** | 2 | keep |
| `ef_w3_offer_peek` | `qb_weather_3` | `discovered` `{type:any}` | **`field`** | 3 | keep |
| `ef_c2_press_peek` | `qb_carto_2` | `discovered` `{type:any}` | **`field`** | 2 | keep |
| `ef_mk2w_queue` | `qb_mk_2` | `discovered` `{type:terrain}` | **`field`** | 3 | keep |
| `ef_fd2t_peek` | `qb_fd_2` | `discovered` `{terrain:wetland}` | **`field`** | 4 | keep |
| `ef_rdr_pub_peek` | `we_reader_gate` | world encounter | **`settlement`** | 3 | **strip** |
| `ef_rdr_priv_peek` | `we_reader_gate` | world encounter | **`settlement`** | 3 | **strip** |
| `ef_sw2_peek` | `qb_sw_2` | `conditional`, no filter | **ambiguous** | 3 | — |

**5 field · 2 settlement · 1 ambiguous.**

- `reorder: false` is dead on **all 8** — no site sets it true.
- `deck: "encounterDeck"` is **correct on the 5 field sites** (it is the field deck) and wrong only on the 2 settlement ones. *This corrects my earlier claim that it was dead on all 8.*
- `count` is retained everywhere per the mechanism call — graded foresight depth (2 roadside fee, 3 seer at your seat, 4 four-month ledger).

### The ambiguous one — `ef_sw2_peek`, flagged not picked

Signals genuinely disagree:

- **Delivery says settlement:** `deliver: "conditional"`, no `placementFilter`. Beat 1 of the same quest *is* `discovered` with `hasRoad: true`, so the author switched modes deliberately between beats.
- **Fiction says both:** *"he is carrying something he would rather not carry alone — **a route, a settlement, a party moving where they have no business being**."*

It is the only site in the corpus whose prose names both kinds. **If `scope` accepts
`both`, this is the site that argues for it.** If scope must be singular I lean
`field` — two of the three things named are road things — but the salt man coming
to your seat is a real counter-signal, and this is a preference rather than a
derivation.

---

## PART 2 — Capability rename. **Blocked: the contract does not carry the syntax.**

I went to `engine-contract.md` rather than the paraphrase, as instructed. **§A3
announces the new predicates but specifies no parameter shapes, and §4.8 still
documents the *old* `has_chip`** (`{holder, chipId, player?, hex?}`). Searching the
whole 52 KB: `chipIds` 0 hits, `has_tech` 1 (prose only), `count_tech` 1 (prose
only), `resolveHex` 1 (prose only). So the exact forms are not yet written down.

Rather than guess at four gates that are already causing trouble, here is exactly
what I need. All four are one line each.

### Q1 — `has_chip`, generalised, hex-scoped

A3 says it *"now accepts a list of chip ids"*. Need the literal shape:

```jsonc
{ "has_chip": { "holder": "???", "chipIds": ["???"], "hex": "encounter-hex" } }
```

- Is the list key `chipIds`, or does `chipId` now accept an array?
- Which `holder` value scopes to *locations on one hex* — the old vocabulary had `any-location-on-hex`. Is that still it?
- Does `hex` take the token `"encounter-hex"` directly, or a wrapper?

### Q2 — the lab chip ids

**The user's ruling is that the lab must be at the hex where the encounter fires**
— *"the lab needs to be in that place to study that place."* So this must be
hex-scoped, not territory-wide.

I need **the actual chip ids for the lab tiers.** I have no chip registry on the
content side; the corpus contains zero chip references (`chipId` 0, `has_chip` 0
across 548 KB). Whatever the list is — `lab-1`, `lab`, `research-bench`, … — please
send it verbatim.

### Q3 — `has_tech` for `intrigue`

```jsonc
{ "has_tech": { "path": "???", "branch": "???" } }
```

The semantic wanted is A3's own example — *"has this player put anything into
Espionage"*. Need the literal branch identifier and whether `path` and `branch` are
alternatives or used together.

### Q4 — `count_tech` for `recon`, and a genuine ambiguity

```jsonc
{ "op": "gte", "left": { "count_tech": { "path": "???" } }, "right": 1 }
```

Need the branch identifier. **But flagging a real ambiguity before it is
hardcoded:** §A4 records a chip named **`recon-team`** (Location) carrying
`encounterRedraws`. So `recon` in the content may mean *the recon-team chip*, not a
tech branch — and the content grades it 1 and 2, which reads more like a count of
somethings than a branch depth.

The two sites:

| Choice | Threshold | Fiction |
|---|---:|---|
| `ch_cro_observe` "Watch from the ridge" | `recon >= 1` | *"Your scouts get up on the high ground and put glasses on the hollow without ever breaking the skyline."* |
| `ch_car_spy` "Offer to find out why" | `recon >= 2` | *"you have people who can go and look"* — running an intelligence operation for a foreign power |

Both read as **scouts you possess**, which is closer to `count_chips` on a
recon-team than to tech investment. **Please confirm which before I write it** —
the two-tier grading (1 = look at a hillside, 2 = run an operation abroad) should
survive whichever predicate is used.

### Ready to execute

`scripts/apply_capability_rename.py` is written and parameterised. The moment Q1–Q4
land it is a four-line fill-in and one run. No other content edit is pending.

### Why Q2 is urgent

Per §A2 — *"every player starts with `techLevel: 1`"* — that gate now **fails
open**: the safe bunker route is offered to every player from turn one regardless
of whether they own a lab. It has gone from invisible to wrongly universal, and it
is the one item on my list that is actively worse than before the `Val` fix.

---

## PART 3 — Two things from my side that bear on the bugs you hit

### 3a. The vocabulary finding, in the form that would have predicted both bugs

`A1`'s taxonomy matches what I derived independently from the data, and the
operative consequence is worth stating as a rule:

> **The table a thing lives in does not tell you where it fires. The beat's
> `deliver` mode does.**

Anything keyed off the table misclassifies **28 of 35 quests** — the 11 that are
entirely `discovered` (field content with beats, living in the quest table only
because that is the table with beats), plus 17 hybrids that mix `discovered` beats
with seat-delivered ones. `q_weather` is the clearest: road, seat, road.

That is exactly the shape of the marker bug — a quest beat is encounter-shaped,
delivered by the same code, and is not in either encounter registry.

The **11 fully field-placed quests**: `q_carto`, `q_courier`, `q_debt`, `q_ford`,
`q_glass`, `q_graves`, `q_herd`, `q_markers`, `q_rail`, `q_road`, `q_wire`.

### 3b. `withinHexesOf: {hex: "encounter-hex"}` — one site, and it is the only one

You hit this crashing the turn on `qb_mas_compound`. Confirming from the content
side: **`encounter-hex` appears 3 times in the whole corpus** — once in that
`withinHexesOf`, and twice as the `hex` param of `PERSISTENT_VISION`
(`ef_fd2b_vision`) and `ESTABLISH_DUAL_HOLDING` (`ef_wks4l_holding`).

So the hex-token vocabulary has exactly three consumers in this content, and the
other two are on quest-ending choices. Worth checking both resolve now that
`resolveHex` exists — they would fizzle silently rather than crash, which is the
harder failure to notice.
