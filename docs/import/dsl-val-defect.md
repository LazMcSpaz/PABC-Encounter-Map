# The `Val` resolution defect — 26 of 29 comparisons in the corpus do not work

**All content facts [VERIFIED-PARSED].** Engine behaviour [FROM-CONTRACT]
(`engine-contract.md` §4.8, `dsl.js:39-52`).

**This is bigger than the three choices the engine agent found, and it contains a
sequencing hazard that would make one of my own recommendations actively harmful
if applied on its own.** That hazard is §4 and it is the most urgent thing here.

---

## 1. One root cause

[FROM-CONTRACT] `Val` resolution: *a string is a dot-path into state **if and only
if it contains a `.`**; otherwise it is a literal string.* Unknown paths resolve to
`null`, and `null` on either side makes the predicate false.

**The DSL performs no token substitution in `Val` position.** Three consequences,
one cause:

| Written by the author | Intended | Actually resolves to |
|---|---|---|
| `"active"` | the active player's id | the literal string `"active"` |
| `"players.active.techLevel"` | that player's tech level | path `players → active` — no such key — `null` |
| `"round"` | `state.round` | the literal string `"round"` |

The content is written against a sane reading of the DSL. **The content is not
wrong.** Per the lesson from `we_bunker`: this looked like authoring noise and is
an engine defect.

---

## 2. The census: 29 `op` comparisons, 26 broken

| Class | n | Behaviour | Direction |
|---|---:|---|---|
| `active` vs faction, `ne` | 10 | `"active" != "versari"` → **always true** | **fails OPEN** |
| `active` vs faction, `eq` | 3 | `"active" == "versari"` → **always false** | **fails CLOSED** |
| `players.active.<stat>` | 4 | unresolved path → null → false | **fails CLOSED** |
| `round` vs int | 6 | string vs int → false | **fails CLOSED** |
| `count_flags` | 3 | unimplemented form → false | fails CLOSED |
| `score` | 3 | **works** | ✅ |

**26 of 29.** Only the three `score` comparisons behave as written.

### 2a. The 10 `ne` sites fail open — every faction exclusion is inert

These gate whole quests away from the faction they are *about*:

| Beat / choice | Gate | Intent |
|---|---|---|
| `qb_not_1` | `active != goldgrass` | don't run "The Notes" as the Goldgrass |
| `qb_sea_1` | `active != goldgrass` | don't run "The Season and the Hour" as the Goldgrass |
| `qb_hire_1` | `active != goldgrass` | — |
| `qb_clm_1` | `active != plainers` | — |
| `qb_hau_1` | `active != plainers` | — |
| `qb_wks_1` | `active != lakers` | — |
| `qb_run_1` | `active != lakers` | — |
| `qb_app_1` | `active != versari` | — |
| `qb_db_1` | `active != versari` | — |
| `ch_bunker_versari` | `active != versari` | don't offer "Send word to the Versari" *to* the Versari |

**Every one of these is currently inert.** Playing as the Goldgrass you can be
offered "The Notes" — a quest in which the Goldgrass hall extends *you* credit and
Mother Sabine Orr comes to *your* seat to negotiate. The player is on both sides.
That will read as broken writing.

### 2b. The 3 `eq` sites fail closed — faction-specific content never appears

| Choice | Gate | What is lost |
|---|---|---|
| `ch_bunker_lab` | `... or active == versari` | the Versari route into the safe bunker option |
| `ch_fever_stores_versari` | `active == versari` | "Requisition a physician" — the Versari answer to a plague |
| `ch_cro_relic_plainers` | `active == goldgrass` | "Gift it to the Free Plainers" — explicitly *"a thing only a Goldgrass power could do"* |

These are the three the engine agent found. **They are the smaller half.**

---

## 3. Capability gating — the whole class is dead, and the answer to your question

**Yes. Every "you can only do this if you have X" option in the corpus has never
been offered.** There are four, all using `players.active.<stat>`:

| Choice | Gate | The option lost |
|---|---|---|
| `ch_bunker_lab` "Study it properly" | `techLevel >= 1` | the 15% safe bunker route |
| `ch_sig_intrigue` "Get him out quietly" | `intrigue >= 2` | the no-shot-fired extraction |
| `ch_car_spy` "Offer to find out why" | `recon >= 2` | the intelligence offer |
| `ch_cro_observe` "Watch from the ridge" | `recon >= 1` | the scouting approach |

Same shape as the `count_flags` ledger: a design that exists in the writing and
has never once fired in play.

### 3a. On the bunker specifically — the encoding does *not* match the stated intent

The user's intent is *"requires having a lab already built."* The author encoded
**`players.active.techLevel >= 1`** — a tech-level threshold, not a building
predicate. Two separate questions for the engine side:

1. **Does `techLevel` exist on a player at all?** The contract describes
   `permanentResearch` and a derived wheel, and never mentions `techLevel`.
   Likewise `intrigue` and `recon`. **If those three fields do not exist, fixing
   token substitution alone still leaves all four gates dead** — the path would
   resolve to a real player object and then to `undefined`.
2. **Is `techLevel >= 1` the right proxy for "has a lab"?** If tech level can be
   raised without building a lab, the gate is looser than intended. If a lab is
   the only way to reach tech 1, it is exact.

**This is the one place the content may need a correction rather than the engine.**
I would not change it without knowing whether `techLevel` exists and how it
relates to buildings. Flagging, not fixing.

### 3b. What the content does *not* use

[FROM-CONTRACT] the engine implements `has_chip`, `unit_count`, `controls_count`,
`control_duration`, `quest_active`, `quest_completed`, `zoc_contains`. **The corpus
uses none of them.** Full form census across all conditions:

```
has_flag 184 | not 45 | op 29 | all 19 | any 11 | score 3 | count_flags 3 | if 1
```

So the content expresses capability *entirely* through `players.active.<stat>`
paths — the one form that is broken — while seven working predicates go unused.
Worth putting in front of the author: `unit_count` and `controls_count` are live
today and would express several of these gates directly.

---

## 4. ⚠️ SEQUENCING HAZARD — do not fix `deliverCondition` before `Val`

I previously recommended the routing fix and the `deliverCondition` fix as a
single change, and said neither should ship alone. **That recommendation is now
incomplete and, taken literally, dangerous.**

`deliverCondition` is currently never read, so its contents cannot hurt anything.
**The moment it starts being read, the `Val` defect activates inside it.**
Simulating every gate under current `Val` semantics, **five go dark:**

| Gate | Effect of fixing `deliverCondition` alone |
|---|---|
| `qb_app_1` (ordinal 0) | **`q_apprentice` never starts** |
| `qb_db_1` (ordinal 0) | **`q_debtbook` never starts** |
| `qb_not_1` (ordinal 0) | **`q_notes` never starts** |
| `qb_sea_1` (ordinal 0) | **`q_seasons` never starts** |
| `we_reader_gate` | never triggers |

All four are **quest opening beats**, blocked by `gte round N` evaluating false.
Two of them — `q_notes` and `q_seasons` — are Tier-1 quests from
`what-the-lost-beats-cost.md`. Fixing `deliverCondition` without `Val` would take
them from *"loses everything after the opener"* to **"never appears at all."**

**Corrected fix set — three changes, and the order matters:**

1. **`Val` token substitution** (`active` → active pid; `round` → `state.round`) — safe alone, and it repairs 23 comparisons immediately.
2. **`ADVANCE_QUEST` routing semantics** — recovers 23 of the 24 lost beats.
3. **`deliverCondition`** — **only after (1).** Before (1) it is a regression.

`count_flags` remains a fourth, needed for `qb_clm_4_installed` and the ledger.

---

## 5. Summary for the user, in story terms

- Nine quests are offered to the faction they are about, because faction exclusion never fires.
- Three faction-specific choices — including the only Goldgrass-flavoured gesture in `q_croppers` — have never appeared.
- Four capability options, the whole "if you have the lab / the spies / the scouts" class, have never appeared. The bunker's safe route is one of them.
- None of this is the writing's fault. One resolver, three symptoms.

**And one correction to my own earlier advice: the two-fix recommendation was
wrong. It is three, and `deliverCondition` must go last.**
