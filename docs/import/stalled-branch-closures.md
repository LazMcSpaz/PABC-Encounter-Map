# Stalled branches — full sweep and proposed closures

**Proposal only. Nothing written.** [VERIFIED-PARSED]

**9 choices across 3 quests.** 4 reuse an existing flag, 5 need a new one.

---

## 1. Sweep method, and 47 candidates ruled out

The naive sweep — *"choice completes nothing and opens no gated beat"* — returns
**56 choices across 10 quests**. Most are not stalls. Three exclusions:

### 1a. Six quests complete by exhaustion — 44 excluded

`q_carto`, `q_debt`, `q_herd`, `q_rail`, `q_salvage`, `q_weather` are
placement-driven, and **every choice in all six carries a self-referential
`ADVANCE_QUEST`** (8/8, 7/7, 6/6, 7/7, 8/8, 8/8). Each beat marks itself complete
on resolution, and the engine completes a quest when all its beats are done. They
close by being played out, not by a `COMPLETE_QUEST`. **Nothing to fix.**

### 1b. `q_massacre` — 2 excluded

Both "Follow the tracks" choices set no flag, but `qb_mas_compound` is
`discovered` with `deliverCondition: null` — it is findable on the map regardless.
The chain continues by exploration.

### 1c. `q_signal`'s two `qb_sig_drift` choices — 2 excluded

`qb_sig_drift` is only reachable via `qb_sig_out` "Put him to work", which has
already queued `sig_death_due` on a 5-round timer. `qb_sig_end` fires and
completes the quest whatever happens at drift. **Harmless dead ends.**

---

## 2. The nine genuine stalls

### `q_signal` (2)

| Choice | Proposed | Flag |
|---|---|---|
| `ch_sig_ignore` — "Log it and move on" | `COMPLETE_QUEST` | **reuse `signal_ignored`** |
| `ch_sig_out_free` — "Tell him he's free to go" | `COMPLETE_QUEST` | **reuse `technician_willing`** |

`signal_ignored` is written and read by nothing — it exists precisely to mark this
outcome. `technician_willing` is **already read elsewhere in the corpus**, so it is
functioning as a continuation hook today; it just never closed its own quest.
Neither needs a new flag.

> **Judgement call — "Log it and move on".** I flagged this earlier as possibly a
> branch that should not exist, since it strands nine of ten beats. On reading the
> outcome — *"Your officer writes down the band and the time and the fact that no
> reply was sent. It stays in the log."* — **it is a deliberate, complete ending**:
> the player declines the hook, the same shape as "Ride on" elsewhere in the
> corpus. I recommend closing it rather than removing it.
>
> **It costs no coverage.** The nine beats are not lost — they are the branch that
> was declined, and a run taking "Answer him" reaches them normally.

### `q_croppers` (1) — the instance the authors documented

| Choice | Proposed | Flag |
|---|---|---|
| `ch_cro_blowback_ack` — "Answer for it" | `COMPLETE_QUEST` | **reuse `blamed_for_barons_war`** |

`_readme.known_breaks_pre_existing` describes this exactly: *"Sets a flag and
adjusts standing but neither advances nor completes `q_croppers`."*
`blamed_for_barons_war` is **already read by `q_baron`**, so the continuation hook
the user asked for is in place — only the closure is missing.

### `q_caravan` (6) — the whole raid branch

Two complete terminal beats, neither of which closes the quest. Taking the wagons
at `qb_car_1` leads to `qb_car_blackmail`, and the escort branch's five beats are
gated on `car_escorting`, which the raid never sets. Nothing further is reachable.

| Choice | Proposed | Flag | New? |
|---|---|---|---|
| `ch_car_bm_pay` — "Pay him" | `COMPLETE_QUEST` | `car_blackmail_paid` | new |
| `ch_car_bm_refuse` — "Refuse him" | `COMPLETE_QUEST` | `car_blackmail_refused` | new |
| `ch_car_bm_public` — "Hang him in the square" | `COMPLETE_QUEST` | `car_witness_hanged` | new |
| `ch_car_bm_quiet` — "Have it done quietly" | `COMPLETE_QUEST` | `car_witness_vanished` | new |
| `ch_car_req_pay` — "Send it" | `COMPLETE_QUEST` | **reuse `thwarted_versari`** | — |
| `ch_car_req_refuse` — "Decline" | `COMPLETE_QUEST` | `car_supply_declined` | new |

**On not reusing the ledger flags.** Three of the blackmail choices already write
`rule_soft_paid_blackmail` / `rule_hard_public_execution` /
`rule_hard_quiet_execution`. I have **not** reused those: they are consumed by
`count_flags` on the `rule_` and `rule_hard_` prefixes, so they are load-bearing
for the moral ledger. Making them double as continuation hooks would mean a later
chain could not branch on the ending without also implying something about the
tally. The new flags sit alongside them.

`thwarted_versari` is written by "Send it" and read by nothing — it already names
that ending in the fiction, so it is reused as-is.

**Naming.** All five new flags follow the existing `car_*` vocabulary —
`car_raided`, `car_aborted`, `car_escorting`, `car_truth_recovered`,
`car_agent_captured` — past-participle state names describing what happened, not
what closed. No `_closed` or `_done` suffixes.

---

## 3. What each ending now records

The point of the flag is continuation, so stated as the hook a later chain reads:

| Flag | The door it leaves open |
|---|---|
| `signal_ignored` | you never answered the signal — the wire-reader is still out there, held by someone else |
| `technician_willing` | you freed him and he stayed by choice — a loyal specialist, not a captive |
| `blamed_for_barons_war` | the Plainers hold you responsible for the Baron's war |
| `car_blackmail_paid` | a soldier who knows what you did on that road, and can be asked again |
| `car_blackmail_refused` | the Versari know who was on that road |
| `car_witness_hanged` | you executed a man publicly on a false charge, in front of the garrison |
| `car_witness_vanished` | he disappeared on patrol; nothing proven, nobody who served with him believes it |
| `thwarted_versari` | you broke the high city's dependence on Versari supply |
| `car_supply_declined` | they asked twice and you gave once; they will not ask again |

Four of the nine are distinctions a later chain would plausibly want —
particularly the two `q_caravan` execution variants, which differ only in whether
the garrison watched.

---

## 4. Assertions the apply script will make

- beat texts changed: **0**
- choice labels and `outcomeText` changed: **0**
- effects added: **9 `COMPLETE_QUEST` + 5 `SET_PLAYER_FLAG`** — no effect removed or modified
- table counts unchanged except `effects` 1133 → **1147**
- every one of the 9 choices resolves to `COMPLETES` on a re-run of the stall sweep
- the four reused flags still written exactly once each

Awaiting go-ahead before writing.
