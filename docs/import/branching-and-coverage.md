# Branching, and the beat-coverage number

Content-side agent. **All content numbers here are [VERIFIED-PARSED]** from
`remnant_content_consolidated_rev2.json` (548,375 bytes, sha256 `2e5220a36c2f…`,
commit `1a6a5c8` on `claude/quests-encounters-progression-4qrnnt`). Engine
behaviour is **[FROM-CONTRACT]**, taken from `PABC/docs/encounter-import/engine-contract.md`.

Reproduce with `scripts/diff_effects.py` and `scripts/audit_choices.py`.

---

## 1. How this content expresses branching — answered

The question was: a bare "advance" can't express a branch, so what does?

**Answer: branching is expressed by a flag/condition pair, and `ADVANCE_QUEST`
names the destination alongside it. Both are load-bearing. `quest_beat_prereqs`
expresses ordering only and cannot select a branch at all.**

Worked example, `q_notes` beat 3 — three choices, three endings:

| Choice | sets flag | `ADVANCE_QUEST` | target's `deliverCondition` |
|---|---|---|---|
| "Give her the pledge" | `notes_pledged` | `qb_not_4_settled` | `has_flag notes_pledged` |
| "Refuse the pledge" | `notes_credit_closed` | `qb_not_4_sovereign` | `has_flag notes_credit_closed` |
| "Take the credit and keep your options" | `notes_pledge_broken` | `qb_not_4_called` | `has_flag notes_pledge_broken` |

All three mechanisms agree, per branch. Meanwhile **all three target beats carry
the identical prereq `qb_not_3`** — so the prereq table cannot distinguish them.
The same triple-redundant pattern holds in `q_seasons`, `q_claim`, `q_baron`,
`q_hire`. **[VERIFIED-PARSED]**

### The second mechanism: pacing

The 20 "mismatches" my first pass flagged are not incoherent — they are the
*linear* advances, where the target gates on a `*_due` flag that no choice sets.
Those flags are set by **`QUEUE_DEFERRED` with `delayRounds` 2–10**: 30 distinct
`*_due` flags, and every one of them is written from inside a deferred packet
(two exceptions set directly). **[VERIFIED-PARSED]**

So `deliverCondition` carries two different jobs:

- **pacing** — `has_flag notes_second_due`, armed by a deferred timer. *"Come back in three rounds."*
- **branching** — `has_flag notes_pledged`, armed by the choice. *"…but only on this path."*

### The content is internally disciplined

334 distinct flags are written, 166 are read by `has_flag`, and **exactly one
flag is read but never written: `sold_bunker_to_versari`** — precisely what the
authors' own `_readme` says. A 383-choice corpus with one known dangling
reference, self-documented. **[VERIFIED-PARSED]**

**The mismatch is not in the content.** The intent is unambiguous and consistently
encoded. Two engine fields need to honour it.

---

## 2. Coverage: **at most 107 of 131 beats are reachable. 24 are structurally lost.**

Static prediction from the data alone. Two independent engine behaviours combine,
and they combine badly.

### 2a. 24 beats: marked complete, never delivered

49 `ADVANCE_QUEST` effects name a beat other than the one they sit on. **All 49
point forward; none point backward.** They name **24 distinct beats.**
[FROM-CONTRACT] the engine marks a named forward beat *complete* without
delivering it — text never shown, choices never offered, effects never applied,
quest still completes and pays out.

Lost if unaddressed: **24 beats, 8,778 characters of prose, 57 choices, 263 effects.**

Nine quests, and in every one the damage is the same shape — everything after the
opener:

| Quest | beats | at risk |
|---|---:|---:|
| `q_claim` | 6 | **5** |
| `q_notes` | 6 | **5** |
| `q_seasons` | 6 | **5** |
| `q_baron` | 3 | 2 |
| `q_haulers` | 3 | 2 |
| `q_hire` | 3 | 2 |
| `q_glass` | 2 | 1 |
| `q_road` | 2 | 1 |
| `q_wire` | 2 | 1 |

Those nine quests would play as: **opening beat, then silent completion and
payout.** 24 of their 33 beats never seen.

### 2b. 44 beats: gate ignored, fire regardless

[FROM-CONTRACT] silent-failure #9 — the engine reads `beat.condition`; the editor
writes `deliverCondition`. The field is never read. **44 conditional beats carry a
`deliverCondition` that will not be evaluated.** **[VERIFIED-PARSED]**

This breaks both jobs from §1 at once:

- **Branching collapses** — every branch alternative becomes eligible, not just the chosen one.
- **Pacing collapses** — every `*_due` gate is ignored, so beats meant to arrive 2–10 rounds later become eligible immediately. The multi-round rhythm disappears.

### 2c. The interaction — worse than lost story

Take "Give her the pledge":

1. `ADVANCE_QUEST(qb_not_4_settled)` marks the chosen ending **complete without delivering it.**
2. `qb_not_4_called` and `qb_not_4_sovereign` have their prereq satisfied and their gate ignored, so **both become eligible and fire.**

**The player sees the two endings they did not choose, and never sees the one they
did.** That is not story loss, it is story inversion, and it will read as a bug in
the writing rather than in the engine. [INFERRED — a direct composition of two
contract-stated behaviours; **worth confirming by execution**, and §3 is how.]

---

## 3. What I need from the engine agent — the coverage test

The user's test is the right one: *"if you see a beat in the json that isn't
appearing in the tests, you're missing content."* Here is the enumeration side,
done.

**`docs/import/expected-beats.json`** (in this repo) — all 131 beats, each with
`beatId`, `questId`, `ordinal`, `deliver`, `gateFlag`, `prereqs`, `routedFrom`,
and my static `predicted` verdict (`SKIPPED` / `reachable`).

**The ask, precisely:**

1. Load the consolidated file into the engine.
2. For each of the 35 quests, drive it to completion through the harness,
   exhaustively across choice branches (every choice at every beat), not one
   representative walk — branch coverage is the whole question.
3. Log every `beatId` **actually delivered** — i.e. reaching `presentToPlayer`,
   not merely marked complete. **That distinction is the entire test**; a beat
   marked complete without delivery is exactly the failure being measured.
4. Return the set of delivered `beatId`s.

I diff it against the 131 and report `N of 131`.

**Three specific predictions to falsify:**

- The 24 beats listed as `predicted: SKIPPED` never appear. → **107/131.**
- In `q_notes`, choosing "Give her the pledge" delivers `qb_not_4_called` and
  `qb_not_4_sovereign` but **not** `qb_not_4_settled` (§2c).
- No beat gated on a `*_due` flag waits for its `delayRounds`; all fire on the
  first eligible round.

If coverage is 131 and those three predictions fail, the import is structurally
sound and everything else is detail.

---

## 4. Where the 20 throwing effects sit — the narrative cost

Not evenly distributed. **8 of 20 sit on quest-ending choices** — the payoff of
the line: **[VERIFIED-PARSED]**

| Effect | Choice | Quest-ending |
|---|---|---|
| `CONTEST` | "Challenge them for the spoils" | ✅ |
| `CONTEST` | "Take the wall" | ✅ |
| `CONTEST` | "Break out" | ✅ |
| `ROLL` | "Give him the word" | ✅ |
| `ROLL` | "Settle accounts" | ✅ |
| `PERSISTENT_VISION` | "Buy him" | ✅ |
| `ESTABLISH_DUAL_HOLDING` | "Leave it as it stands" | ✅ |

`ROLL` and `CONTEST` are confirmed cheap to add (contests already exist; `ROLL` is
a 1–100 RNG). That leaves **five one-off effects** — `GRANT_SAFE_PASSAGE`,
`TAKE_UNIT`, `SET_MOVEMENT`, `PERSISTENT_VISION`, `ESTABLISH_DUAL_HOLDING` — one
instance each.

Per the narrative-first principle, what each is *trying to do* in the fiction, so
the engine agent can pick any mechanism that produces it:

| Effect | Where | What the fiction needs |
|---|---|---|
| `ESTABLISH_DUAL_HOLDING` | `qb_wks_4_left`, ending of `q_works`. Outcome: *"Nothing is settled. Everything works."* | A hex both you and the lakers benefit from, with ownership deliberately unresolved. A shared-yield or contested-but-peaceful marker. Not a transfer of control. |
| `PERSISTENT_VISION` | `qb_fd_2` "Buy him", quest-ending | You bought an informant. Ongoing visibility of something you would not otherwise see. `GRANT_VISION` (already implemented, Group D) is very likely sufficient. |
| `GRANT_SAFE_PASSAGE` | `qb_car_1` "See it safely to Dambar" | A convoy crosses hostile ground unmolested this once. A one-shot immunity, or simply narrating success. |
| `TAKE_UNIT` | `qb_cro_baron` "Hear his price" | **CORRECTED — I had this backwards.** The Baron takes **your** unit, on loan for six rounds, and returns it two Strength weaker. You do not gain a unit; you lose the use of one. See `crashing-effects-call-sites.md` §2.4. |
| `SET_MOVEMENT` | `fe_bridge_toll` "Take the long way" | Avoiding a toll costs you distance. `MODIFY_STAT{stat:"Movement"}` is close **but not equivalent** — `SET_MOVEMENT` is an absolute override (`value: 1`), `MODIFY_STAT` is a delta. See `crashing-effects-call-sites.md` §2.5. |

Two of five have an implemented near-equivalent today (`GRANT_VISION`,
`MODIFY_STAT`). The other three are single instances where, if the effect is
expensive, **the outcome text alone carries the fiction** and the mechanical
payload could be dropped without the player noticing a gap.
