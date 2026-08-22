# The 20 crashing effects — every call site, and what each is *for*

**All [VERIFIED-PARSED]** from `remnant_content_consolidated_rev2.json`.
Full `paramsJson` verbatim; intent is my reading of the surrounding beat and
outcome text, and is labelled as such.

Governing principle: **narrative and outcomes are fixed, encoding is free.** Each
entry says what the fiction needs. Any mechanism producing that is correct.

---

## 1. First — three parameter facts that change the build

### 1.1 `ROLL` is *almost* a plain 1–100 RNG. One site isn't.

10 sites. Nine use `{chance, onSuccess[], onFail[]}`. **One carries an extra key:**

```json
// ef_car_extract_roll, on ch_car_extract_go "Give him the word"
{ "chance": 33,
  "chanceIfFlag": { "flag": "car_agent_armed", "chance": 66 },
  ... }
```

`chanceIfFlag` doubles the odds if the player armed the agent earlier — the payoff
for a setup two beats back. **If `ROLL` ships as a bare RNG, this site silently
uses 33 forever and that earlier choice stops mattering.** Cheap to support
(one conditional lookup), invisible if missed.

### 1.2 `CONTEST` needs an optional ally contribution

5 sites. Four use `{opponentStrength, target, onWin[], onLose[]}`. **One adds:**

```json
// ef_mas_rev_contest, on ch_mas_rev_fight "Take the wall"
{ "opponentStrength": 5, "allyStrength": 6, ... }
```

The beat is *"You go back with the Goldgrass at your shoulder and considerably
more of them than you expected."* `allyStrength` **is** that sentence. Drop it and
the return-with-allies beat fights identically to the solo attempt — the whole
point of the quest's second act.

### 1.3 `ADJUST_BASE_STRENGTH: -99` is a sentinel, not arithmetic

Four sites, all in `onLose` / `onFail`. Amounts across the corpus are
`-2 ×4, -99 ×4, -1, +1, +2` — so `-99` is plainly an idiom for **"the unit dies."**

Good news: [FROM-CONTRACT] `ADJUST_BASE_STRENGTH` clamps to `[0, cap]` and
**destroys a unit driven to 0**. So `-99` already does exactly the right thing.
Flagging it so nobody "fixes" it into `-4` and turns four deaths into four
woundings.

---

## 2. The five types with no handler

### 2.1 `ROLL` — 10 sites

| Effect | Choice | chance | success / failure |
|---|---|---:|---|
| `ef_bunker_lab_roll` | "Study it properly" | **15** | Tech +1 & `bunker_online` (3 rds) / −8 Resource, `bunker_blew` |
| `ef_bunker_rough_roll` | "Open it with the crew you have" | **50** | same / same |
| `ef_sig_force_assault_roll` | "Go in hard" | 45 | `sig_extracted` / `technician_dead` |
| `ef_sig_force_raid_roll` | "Hit the workshop only" | 60 | `sig_extracted` / `technician_stayed`, Str −2 |
| `ef_sig_intr_run_roll` | "Run it as planned" | 70 | extracted + clean / stayed |
| `ef_sig_intr_bribe_roll` | "Buy the gate watch first" | 90 | extracted + clean / stayed |
| `ef_car_extract_roll` | "Give him the word" | 33 / **66 if armed** | truth recovered, versari −2 / captured, versari −8, rep −2 |
| `ef_tem_result_roll` | "Settle accounts" | 60 | lakers +6, +10 Res / lakers −4 |
| `ef_cro_bar_fight` | "Take it from him" | 30 | relic, Str −2 / **death** |
| `ef_hire2_trap_roll` | "Set a trap at the ford" | 65 | won, +3 Res / missed |

**Intent [INFERRED]:** the chance numbers are *authored risk pricing*, and they are
internally consistent — `we_bunker` prices caution at 15% and recklessness at 50%
for identical stakes, and `q_signal` prices its three approaches 45 / 60 / 70,
rising to 90 if you pay 6 Resource first. **The whole design of those two
encounters is the odds.** Preserve the numbers exactly.

> ⚠️ `we_bunker`: "Study it properly" (15%) has *worse* odds than "Open it with
> the crew you have" (50%) for the same payoff — and costs a Tech/faction gate to
> even see. That reads **inverted**. It may be deliberate (the careful method is
> slower, and the 3-round delay models that) but as written, caution is strictly
> dominated. **Flagging as a possible authoring error — not presenting it as
> spec.** Worth a writer's ruling.

### 2.2 `CONTEST` — 5 sites

| Effect | Choice | opponent | ally | win / lose |
|---|---|---:|---:|---|
| `ef_mas_chal_contest` | "Challenge them for the spoils" | 5 | — | +6 Res, `mas_took_spoils` / **death** |
| `ef_mas_threat_contest` | "Threaten to tell the Goldgrass" | 5 | — | identical to above |
| `ef_mas_rev_contest` | "Take the wall" | 5 | **6** | +10 Res, goldgrass +4 / **death** |
| `ef_cro_fight_contest` | "Break out" | 4 | — | alignment −2, goldgrass −3 / Str −2 |
| `ef_hire2_open_contest` | "Meet them in the open" | 5 | — | won, +5 Res / lost, Str −2 |

**Intent [INFERRED]:** a strength check against a stated opposing number, with the
player's own unit strength as the other side. `ef_cro_fight_contest` is the
interesting one — *winning* costs you alignment and Goldgrass standing, because
the people you beat are **farmers with hand tools**. The outcome text says so:
*"they close anyway, which is worse to remember than a real fight would have
been."* A contest whose victory is a moral loss. Whatever mechanism is used must
let `onWin` carry penalties.

### 2.3 `GRANT_SAFE_PASSAGE` — 1 site

```json
// ef_car_escort_passage, on ch_car_escort "See it safely to Dambar"
{ "factions": ["versari"], "whileFlag": "car_escorting", "target": "active" }
```

**Intent:** you escort a Versari supply train; while escorting, Versari forces
don't treat you as hostile. Duration is flag-scoped, not round-scoped.

> ⚠️ **`car_escorting` is set `permanent` and is never cleared anywhere in the
> corpus** (one write, no clear). Taken literally, safe passage from the Versari
> lasts the rest of the game for one escort job. **Almost certainly an oversight**
> — the fiction is one road, one journey ("until the road runs out at the high
> city"). Flagging rather than speccing; needs a writer's call on when it ends.

### 2.4 `TAKE_UNIT` — 1 site — **I previously reported this backwards**

```json
// ef_cro_bar_take_unit, on ch_cro_baron_barter "Hear his price"
{ "target": "active", "rounds": 6,
  "returnStrengthDelta": -2, "returnFlag": "cro_baron_used_unit" }
```

**Intent — corrected:** Baron Juan wants to *borrow your unit* for a season, for a
job he'd rather not put his own name on. Outcome text: *"He wants your unit. Not
forever — a season... The relic is yours when they come back."*

So: **your unit is removed from play for 6 rounds and returns 2 Strength weaker.**
It is a loan under duress, not an acquisition. My earlier note in
`branching-and-coverage.md` said "you gain what was his" — **wrong, now corrected
in place.**

The surrounding effects confirm the timing: `QUEUE_DEFERRED delayRounds: 6` grants
`cro_has_relic`, and a second at `delayRounds: 10` fires the blowback. The whole
choice is a three-stage arrangement over ten rounds.

### 2.5 `SET_MOVEMENT` — 1 site

```json
// ef_bridge_around_mv, on ch_bridge_around "Take the long way"
{ "value": 1, "when": "next_turn", "target": "active" }
```

**Intent:** refuse a bridge toll, take the long road, arrive slowly. *"Two extra
fords and a great deal of broken ground."*

**Note the correction to my earlier claim:** `SET_MOVEMENT` is an **absolute
override** (`value: 1` = movement *becomes* 1), whereas `MODIFY_STAT` is a
**delta**. Substituting `MODIFY_STAT{stat:"Movement", amount:-1}` is only
equivalent for a unit whose base movement is 2. Fine if all units are 2; a real
difference otherwise. The fiction just needs *"slow next turn"* — a delta is
acceptable, an override is exact.

### 2.6 `PERSISTENT_VISION` — 1 site (quest-ending)

```json
// ef_fd2b_vision, on ch_fd2_buy "Buy him"
{ "hex": "encounter-hex", "target": "active" }
```

**Intent:** you buy the enemy's counter-spotter. *"He keeps counting for them and
sends you a copy of everything, and this ford does not go dark to you again."*
Permanent visibility of one hex. `GRANT_VISION` (implemented, Group D) is very
likely sufficient **if it persists**; if it is one-shot, it isn't — the word in
the fiction is *"again."*

### 2.7 `ESTABLISH_DUAL_HOLDING` — 1 site (quest-ending) — **depends on `recurring_yield`**

```json
// ef_wks4l_holding, on ch_wks4l_ack "Leave it as it stands"
{ "hex": "encounter-hex", "owners": ["active", "lakers"],
  "playerYield": 3, "target": "active" }
```

**Intent:** a hex nobody owns and everybody benefits from. *"Nothing is settled.
Everything works."* Not a transfer of control — a deliberate refusal to resolve
ownership, which pays 3 per round.

**`playerYield: 3` is a per-round yield** — so this effect is a consumer of
`recurring_yield`, the authors' own HIGHEST-PRIORITY missing system. Build them
together or `q_works`'s ending pays nothing.

### 2.8 A shared blocker: `"hex": "encounter-hex"`

Three sites use the string `"encounter-hex"` where a hex id is expected. It is a
**symbolic token meaning "the hex this encounter fired on"** — i.e. `ctx.source.hexId`.
[FROM-CONTRACT] hex resolution expects real ids, and an unmatched hex is a silent
fizzle. **The resolver needs this token, or all three effects no-op even once their
handlers exist.**

---

## 3. `count_flags` — the ledger is real, coherent, and reachable

Asked to sanity-check before it gets built. **It holds up.**

**One tally, not several groups.** 30 flags — 19 `rule_hard_*`, 11 `rule_soft_*` —
written from **15 distinct sources** (8 world encounters, 7 quest beats). Each
source is a single ruling with mutually exclusive options, contributing exactly
one flag. The prefix is a real taxonomy, not a coincidence: every flag names a
judgement the player handed down — `hanged_prisoner` / `released_prisoner`,
`overrode_assembly`, `fever_cordon`, `buried_the_theft`, `shared_the_seat`.

**Maximum lifetime tally: 15.** Thresholds are `>= 2` (`rule_`) and `>= 2`
(`rule_hard_`). Fourteen of the fifteen sources can yield a hard flag.

**Verdict: comfortably reachable.** Two rulings out of fifteen opportunities is a
low bar — this is not a ledger nobody can trip. The authors were evidently
worried about exactly this and said so: *"q_road and we_standard and we_reading
were written partly to pad the rule_* tally so the big ruling chains are not
carrying it alone."* That padding worked.

**Two caveats:**

1. `we_fever_house` yields `rule_hard_fever_camp` **or** `rule_hard_fever_cordon`
   — both hard. That encounter contributes to the hard tally whichever way you
   rule. Consistent with its fiction (both options are harsh), but it means the
   hard threshold is slightly easier to trip than a naive read suggests.
2. The one place the ledger *is* blocked is `qb_clm_4_installed`, and it is
   blocked **twice over** — `ch_clm3_install` needs `count_flags` (unbuilt), and
   the beat is also one of the 24 skipped by the `ADVANCE_QUEST` inversion. Fixing
   `count_flags` alone will not reach it.

**Recommendation: build it.** 15 authored ruling sites feeding three gates is a
real system with real reach, and it is the game's moral memory.
