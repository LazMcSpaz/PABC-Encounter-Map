# `PEEK` — scope per site, and the taxonomy that makes it derivable

**All [VERIFIED-PARSED].** Supersedes §1–2 of `peek-resemantics-and-field-deck.md`
on the `deck` parameter. New rule per the user: **scope follows the fiction of the
firing site** — roadside readers foresee field events, seat-side seers foresee
settlement events.

---

## 1. The rule is mechanically derivable — no judgement call needed on 7 of 8

The corpus already records where every piece of content fires, and it is **not**
the table it lives in. The ground truth is the beat's own `deliver` mode:

| `deliver` | fires | scope |
|---|---|---|
| `discovered` (+ `placementFilter`) | placed on a hex, found by a unit on the map | **field** |
| `auto` / `conditional` | triggered at the seat | **settlement** |
| row in `field_encounters` | drawn from the field deck on a Move | **field** |
| row in `world_encounters` | triggered at the seat | **settlement** |

Applying it:

| Effect | Host | Firing site | **Scope** | `count` | `deck` |
|---|---|---|---|---:|---|
| `ef_reader_pay_peek` | `fe_ask_the_reader` | field encounter | **field** | 2 | **keep** |
| `ef_w3_offer_peek` | `qb_weather_3` | `discovered`, `{type:any}` | **field** | 3 | **keep** |
| `ef_c2_press_peek` | `qb_carto_2` | `discovered`, `{type:any}` | **field** | 2 | **keep** |
| `ef_mk2w_queue` | `qb_mk_2` | `discovered`, `{type:terrain}` | **field** | 3 | **keep** |
| `ef_fd2t_peek` | `qb_fd_2` | `discovered`, `{terrain:wetland}` | **field** | 4 | **keep** |
| `ef_rdr_pub_peek` | `we_reader_gate` | world encounter | **settlement** | 3 | **strip** |
| `ef_rdr_priv_peek` | `we_reader_gate` | world encounter | **settlement** | 3 | **strip** |
| `ef_sw2_peek` | `qb_sw_2` | `conditional`, no filter | **ambiguous — see §2** | 3 | see §2 |

**5 field · 2 settlement · 1 ambiguous.**

### Correction to my earlier recommendation

I previously wrote that `deck: "encounterDeck"` was *"dead on all 8"*. **That was
wrong.** `encounterDeck` is the field deck, and under the new rule it is **correct
on 5 of 8** — the very sites I had flagged as conflicts. The authors had it right;
my reading of the ruling was too narrow.

- **Keep `deck`** on the 5 field sites.
- **Strip `deck`** on the 2 settlement sites — there is no settlement deck for it to name, and the user notes there may no longer be a single encounter deck at all.
- **`reorder: false` is still dead everywhere.** Deck-manipulation, unused, and no site sets it true.
- **`count` stays everywhere**, per your ruling — graded foresight depth: 2 for a paid roadside reading, 3 for a seer at your seat, 4 for a four-month ledger.

### And every prose conflict dissolves

The four sites I flagged as conflicting are all **field**, and every one of them
said so in its own text — *"what is coming up this road behind him"*, *"read the
road"*, four months of ford crossings, a smuggling line at a creek bend. They were
never wrong. **They were being measured against the wrong scope.** No prose rewrite
is needed anywhere.

---

## 2. The one genuine ambiguity — `ef_sw2_peek`

`qb_sw_2` is the only `PEEK` host whose signals disagree, and I am flagging rather
than picking.

- **Delivery says settlement:** `deliver: "conditional"`, no `placementFilter` — it triggers at the seat, not on a hex. Beat 1 of the same quest *is* `discovered` with `hasRoad: true`, so the author switched modes deliberately between beats.
- **Fiction says both:** *"He finds you this time, which takes some doing, and he is carrying something he would rather not carry alone — **a route, a settlement, a party moving where they have no business being.**"*

**It is the only site in the corpus whose prose names both kinds explicitly.** If
the engine's scope parameter can take `both` — or if `count: 3` can be split
across the two pools — this site is the argument for it. If scope must be
singular, I would lean **field** on the strength of *"a route… a party moving"*
being two of the three things named, but that is a preference, not a derivation,
and the salt man coming to your seat is a real counter-signal.

---

## 3. The vocabulary muddle — it is real, and it runs one way only

The user is right, and the shape is precise.

**Three tables, but only two axes:** how many beats, and where it fires.

| | single-shot | multi-beat |
|---|---|---|
| **fires on the map** | `field_encounters` (11 rows) | **11 quests** |
| **fires at the seat** | `world_encounters` (18 rows) | 7 quests |
| **both** | — | 17 quests |

### 3a. 11 quests are field content with beats

Every beat `discovered` with a `placementFilter` — structurally indistinguishable
from a multi-beat field encounter, and living in the quest table only because the
quest table is the one with beats:

`q_carto` · `q_courier` · `q_debt` · `q_ford` · `q_glass` · `q_graves` · `q_herd` ·
`q_markers` · `q_rail` · `q_road` · `q_wire`

Their placement filters are terrain-scoped in the way field content is —
`{terrain: "wetland"}` for the ford, `{terrain: "rubble"}` for the glass field,
`{hasRoad: true}` for the courier.

### 3b. 17 more are genuinely hybrid

`q_caravan`, `q_claim`, `q_croppers`, `q_hire`, `q_massacre`, `q_runner`,
`q_saltman`, `q_salvage`, `q_signal`, `q_weather`, `q_works` and others mix
`discovered` beats with `auto`/`conditional` ones — a story that starts on the road
and comes home to the seat, or the reverse. `q_weather` is the clearest: beat 1
`discovered` (you find shelter in a storm), beat 2 `auto` (the night passes), beat 3
`discovered` (you meet him again, elsewhere).

**These are not miscategorised.** They are the reason a per-*quest* scope would be
wrong and a per-*beat* scope is right.

### 3c. The muddle does not run the other way

- **No `field_encounters` row has beats.** The editor supports multi-beat field stories via `copies: 0` sub-beat rows; **this corpus contains none** — all 11 have `copies` 1–3.
- **No `world_encounters` row chains into another.** `DELIVER_ENCOUNTER` appears once in the whole file, nested.
- **No quest has a single beat** — the minimum is 2, so nothing single-shot is masquerading as a quest.

**So the imprecision is one-directional: the quest table holds a large body of
field content, and nothing in the encounter tables is secretly a quest.** That is a
much smaller problem than "the vocabulary is muddled" suggests, and it needs no
data migration.

### 3d. Why this matters for implementation

**The table a thing lives in does not tell you where it fires. The beat's `deliver`
mode does.**

Any engine feature that needs to know *"is this a settlement thing or a road
thing"* — `PEEK` scope now, the skip tech later, and anything that filters or
reveals by kind — must read `deliver` + `placementFilter` at the **beat** level.
Keying off the table would misclassify **28 of 35 quests**: the 11 all-field ones
entirely, and the 17 hybrids on some of their beats.

That is the actionable form of the user's observation, and it is worth the engine
agent having before it builds the scope parameter.
