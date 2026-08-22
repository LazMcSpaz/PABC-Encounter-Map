# `PEEK` under the new semantics, and what the skip tech needs

**All [VERIFIED-PARSED].** New `PEEK` meaning per the user: *see the next upcoming
**settlement** encounter or quest — whatever will fire related to your settlement,
not a field encounter.*

---

## 1. All 8 instances carry now-meaningless deck parameters

Every one of the 8 has the identical parameter shape:

```json
{ "deck": "encounterDeck", "count": <2|3|4>, "reorder": false, "target": "active" }
```

| Effect | count | Host |
|---|---:|---|
| `ef_w3_offer_peek` | 3 | `qb_weather_3` |
| `ef_c2_press_peek` | 2 | `qb_carto_2` |
| `ef_reader_pay_peek` | 2 | `fe_ask_the_reader` |
| `ef_rdr_pub_peek` | 3 | `we_reader_gate` |
| `ef_rdr_priv_peek` | 3 | `we_reader_gate` |
| `ef_mk2w_queue` | 3 | `qb_mk_2` *(nested in QUEUE_DEFERRED)* |
| `ef_sw2_peek` | 3 | `qb_sw_2` |
| `ef_fd2t_peek` | 4 | `qb_fd_2` |

**`deck: "encounterDeck"` is dead on all 8 — and it was pointing at the wrong deck
even before this ruling.** [FROM-CONTRACT] `game.encounterDeck` is the **field**
encounter deck; it is what `buildEncounterPrompt` reads on the Move path. So every
`PEEK` in the corpus currently names the field deck, which is precisely the thing
the new semantics excludes.

`reorder: false` is also deck-manipulation and now meaningless. **`count` is the
open question** — the new wording says *"the next upcoming"*, singular. If the
answer is genuinely one, then the 2/3/4 spread is lost information: the authors
were grading how much foresight each source gives, and a reader paid for a fee
(2) sees less than a reader sitting with your seat (3), and a four-month ledger
(4) sees most. **Worth preserving `count` as "how many upcoming settlement events"
if the engine can support it.** That grading is authored intent, not noise.

---

## 2. Narrative check — 2 fit, 2 partial, 4 conflict

A clean rule emerged: **`PEEK` reads correctly where it fires at the seat, and
wrongly where it fires on the road.**

### ✅ Fits perfectly (2) — both at the settlement

**`ef_rdr_pub_peek` / `ef_rdr_priv_peek`** — `we_reader_gate`. *"She offers to sit
with you before your next decision — not a prophecy... just the shape of what she
feels coming."* She came to your gate and asked for your seat by name. Non-specific,
settlement-located, about what is coming to **you**. This is the new semantics
written out in prose before the ruling existed. **No change.**

### ⚠️ Conflicts (4) — the text names the road

| Effect | The problem |
|---|---|
| **`ef_reader_pay_peek`** | **Worst case.** The label is literally **"Have her read the road"**, she *"reads the road ahead for travelers"*, and the host is itself a **field** encounter (`fe_ask_the_reader`). Label, prose and location all say road. |
| **`ef_w3_offer_peek`** | Outcome: *"He tells you what is coming up **this road** behind him."* A scout reporting road traffic cannot reveal a settlement event. |
| **`ef_fd2t_peek`** | A ford-crossing ledger — *"who, how many, which direction, what they were hauling."* Traffic on a crossing is field information by definition. |
| **`ef_mk2w_queue`** | A smuggling handoff at a dry creek bend, *"no road, no water worth stopping for."* You learn *"what this line carries and who it carries it for"* — a route, not a settlement. |

### ◐ Partial (2)

- **`ef_sw2_peek`** — the salt man gives up *"a route, **a settlement**, a party moving where they have no business being."* The word *settlement* is already in the prose, so it survives with the weakest edit of the four — but *route* and *party moving* still point at the road.
- **`ef_c2_press_peek`** — the cartographer's reveal is *who else has bought maps*, which is about rival powers rather than terrain. The surrounding fiction is *"grades, fords, the two crossings your own scouts had wrong"* — field-flavoured, but the revealed fact is political and could plausibly foreshadow something arriving at your seat.

**Recommendation:** `ef_rdr_pub_peek` and `ef_rdr_priv_peek` need nothing.
`ef_reader_pay_peek` needs the most work and may be the wrong home for the effect
entirely — a roadside reader charging travellers a fee to read *the road* is a
field-information fiction from top to bottom. The cleanest correction may be to
drop `PEEK` from it rather than rewrite a field encounter into a settlement one.
**Flagging; not changing** — four of these are prose rewrites and one is a
structural call, and both want the user's eye.

---

## 3. Capability earn-vs-check — context for the engine agent's field question

You asked for anything about how `intrigue` / `recon` are *earned* versus checked.
The answer is clean and it points one way:

```
ADJUST_RESOURCE pools used : Resource ×142, Tech ×25
ADJUST_TRACK tracks used   : trust ×23, alignment ×19, reputation ×2
MODIFY_STAT stats used     : Movement ×4, Strength ×2
Effects writing intrigue / recon / techLevel : NONE
```

**The content never writes `intrigue`, `recon` or `techLevel`. It only reads
them.** Contrast with `Tech`, which the content grants 25 times.

So the authors treated the three as **engine-side tree state that content queries
but does not modify** — exactly what you would expect of a skill tree. `Tech` is
the content-side currency you earn; `techLevel` / `intrigue` / `recon` are the
tree positions you spend it into, owned by the engine.

That supports the reading that these are real engine concepts under some name,
rather than fields the author invented. It also means **no content change can make
these gates work** — nothing in the corpus could ever set them.

---

## 4. The skip tech — my view as content authority

### 4.1 The problem is worse than "none are negative"

**Ten of the eleven field encounters carry no mechanical effect on any choice.**
The only two effects in the entire field deck are `SET_MOVEMENT` on
`fe_bridge_toll` ("Take the long way") and `−1 Resource + PEEK` on
`fe_ask_the_reader`. Everything else is pure prose.

So a skip currently saves the player nothing at all. It is not that the encounters
are mildly positive — **there is no mechanical stake to avoid.**

### 4.2 The binding constraint: 77% of the deck is protected

The authors' own `_readme` declares a `flavor_only` list — *"Carry no mechanical
effect by design and **must not be 'fixed'**"* — naming eight of the eleven field
encounters: `fe_the_silo`, `fe_tattooed_man`, `fe_goldgrass_notes`,
`fe_ashfall_year`, `fe_foundry_boy`, `fe_no_answer`, `fe_the_hulk`,
`fe_wrong_water`.

By deck copies that is **17 of 22 cards, 77% of the deck, explicitly off-limits.**

**So adversity cannot come from editing the existing deck.** It has to be added,
and the deck rebalanced around a protected flavour core. I would treat that
`flavor_only` list as binding — those vignettes are doing worldbuilding work, and
a deck that is all consequence is a worse deck.

### 4.3 The design point that matters most

**Adversity has to live in the encounter *firing*, not in its choices.**

Every current field encounter is *"here is a situation, choose a response, nothing
bad happens."* Even a deck full of hard *choices* makes skip worthless, because
the player can already choose the harmless option. A skip only has value against
an encounter that **imposes a cost with no good option** — a toll you pay or
detour around, a raid that costs strength either way, a sickness that follows the
column. `fe_bridge_toll` is the one existing card with this shape: both options
cost you something. It is the template.

### 4.4 Numbers

With 17 protected flavour cards fixed, and adding **A** adverse cards to a 22-card deck:

| Target adverse share | New cards | Final deck |
|---:|---:|---:|
| 25% | **~7** | ~29 |
| 33% | **~11** | ~33 |
| 40% | **~15** | ~37 |

**My recommendation: ~7–9 new adverse cards, landing near 25–30%.** Reasoning:

- Below ~20% the player rarely meets one and the tech is dead weight.
- Above ~40% the field deck stops being the game's texture and becomes a tax, which would drown the protected flavour cards the authors care about.
- A skip is **once per turn**, so it does not need a high hit-rate to feel good — it needs the player to think *"I'm glad I had that"* a few times per run, not every turn.

### 4.5 The multiplier nobody has costed yet

**A blind skip is worth a fraction of an informed one.** Right now there is no way
to see a field encounter coming, so a field skip is a coin flip — the player burns
it and never learns whether it mattered.

The new `PEEK` fixes exactly this problem **on the settlement side only**. So the
intrigue tree's first tech ("skip one, settlement or field, player's choice") and
the seer's `PEEK` ("see the next settlement event") are a **matched pair on
settlements, and the field half is blind.**

Two ways to read that, and it is worth the user choosing deliberately:

1. **Intended asymmetry** — settlement events are the ones you plan around; field encounters are weather you ride through. Then the field half of the skip is a minor convenience and the adverse-card count can sit at the low end.
2. **A gap** — if field skipping is meant to matter, something needs to reveal the field deck too, and the old `PEEK` was that thing before it was re-pointed at settlements.

**If the answer is (2), the adverse-card requirement roughly doubles**, because a
blind skip needs a much denser deck to be reliably useful. That is the single
biggest lever on the number in §4.4, and it is a design decision rather than a
content one.
