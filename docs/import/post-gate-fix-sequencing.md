# `q_signal` / `q_caravan` under honoured gates, and the ending-density read

**All [VERIFIED-PARSED]** against the post-edit file. First analysis of these
quests under gates that are actually consulted.

---

## 1. Placement edits — applied

All nine written. **Beat texts changed: 0. Choice labels/outcomes changed: 0.**
Diff 32 insertions / 30 deletions. Residual `"terrain":` **0**, `hasAbility` **0**.
Every one of the 45 placement filters now uses only live keys.

I did not wait on the three `{hasRoad:true}` measurements: **`{hasRoad:true}` is a
strict superset of `{type:"encounter", hasRoad:true}`**, which §A10 measures at
12/12. A superset of a 12/12 filter cannot be worse than 12/12. Proven rather than
estimated.

---

## 2. `q_signal` — sequences correctly now. Two dead ends.

With gates honoured, every branch routes as written:

```
qb_sig_1 "Answer him"            -> qb_sig_2
qb_sig_2 "Ask for him openly"    -> qb_sig_dip      "Take him" -> qb_sig_force
         "Get him out quietly"   -> qb_sig_intr     "Leave it alone" -> qb_sig_stays
qb_sig_dip/force/intr            -> qb_sig_out (success) | qb_sig_stays / qb_sig_dead (failure)
qb_sig_out "Put him to work"     -> qb_sig_drift now + qb_sig_end at +5 rounds
qb_sig_end / stays / dead        -> COMPLETE
```

The three-endings-at-once was entirely the ignored-gate bug. **Nothing to
restructure.**

### Two paths that never close the quest

| Choice | What happens |
|---|---|
| `qb_sig_1` **"Log it and move on"** | Sets `signal_ignored`, which nothing reads. The quest opens and then permanently stalls with **9 of 10 beats undelivered**. |
| `qb_sig_out` **"Tell him he's free to go"** | Sets `technician_willing` + `technician_with_player`. Nothing in `q_signal` gates on either, and the choice carries no `COMPLETE_QUEST`. |

The second is the one worth the user's attention. **It is the humane ending** —
you extracted the man and then let him go — and it is the only outcome of
`qb_sig_out` that does not resolve. Its sibling "Put him to work" closes cleanly
five rounds later via `qb_sig_end`. So the coercive branch completes and the
generous one hangs.

`qb_sig_drift`'s two choices are also dead ends but **harmlessly** — that beat is
only reached via "Put him to work", which has already queued `sig_death_due`, so
`qb_sig_end` closes the quest regardless of what happens at drift.

## 3. `q_caravan` — two whole terminal beats never close the quest

| Beat | Choices | Status |
|---|---:|---|
| `qb_car_blackmail` | **4 of 4** | none completes, none opens another beat |
| `qb_car_request` | **2 of 2** | same |

Taking the wagons at `qb_car_1` leads to `qb_car_blackmail`, and that is the end
of the road — the five beats on the escort branch never deliver, so "all beats
done" is never true and the quest cannot auto-complete either. **6 of 17 choices
leave `q_caravan` permanently open.**

The escort branch by contrast resolves cleanly on every path
(`qb_car_arrive` → `agent` → `extract`/`abort`, all completing).

So the raid branch is unfinished relative to the escort branch. That reads as
authoring incompleteness rather than intent — `qb_car_blackmail` is a full beat
with four written outcomes and a `rule_*` ledger entry on three of them.

## 4. This is a known class — the authors documented one instance

`_readme.known_breaks_pre_existing`:

> **`ch_cro_blowback_ack`** — *"Sets a flag and adjusts standing but neither
> advances nor completes `q_croppers`, so the quest never closes on that path.
> Present in the source file."*

**They found one. There are more**, and they cluster the same way: a fully written
branch that resolves narratively but carries no `COMPLETE_QUEST`. Confirmed
instances beyond the documented one:

- `q_signal` — "Log it and move on", "Tell him he's free to go"
- `q_caravan` — all of `qb_car_blackmail` (4), all of `qb_car_request` (2)

**Recommendation:** treat this as one content fix — add `COMPLETE_QUEST` to the
terminal choices of each stalled branch. It is additive, changes no prose, and
directly serves the 131/131 target, since a quest stuck open can block anything
gated on its completion. **I have not applied it** — adding a completion is a
narrative judgement about whether a branch is *meant* to end there, and three of
these are branches a writer might have intended to continue.

---

## 5. Ending density — `q_runner` is **exactly typical**, not steep

| | value |
|---|---|
| Corpus | **111 of 303 quest choices carry `COMPLETE_QUEST` — 36.6%** |
| Per-quest ratio | **median 0.38, mean 0.39** |
| `q_runner` | **0.38** — 3 of 8 choices |

`q_runner` sits on the median exactly. **Its 2-of-3 at `qb_run_3` is not unusual —
it is milder than the corpus norm.**

The norm at a *terminal* beat is that **every** choice ends the quest. 23 beats
have ≥2 ending choices, and most are total:

```
4 of 4   qb_fd_2 · qb_gr_2 · qb_hire_3 · qb_mk_2
3 of 3   qb_bar_3 · qb_cr_2 · qb_cro_relic · qb_hau_3 · qb_rd_2 · qb_stb_3 · qb_wir_2
2 of 2   qb_app_3_kept · qb_app_3_returned · qb_clm_4_installed · qb_db_4 ·
         qb_gls_2 · qb_not_4_sovereign · qb_rr_3 · qb_ret_3 · qb_wr_3
```

So `qb_run_3` having one continuing branch of three makes it **more** generous
than a typical closing beat, not less.

### The pacing fact worth knowing

The distribution is bimodal, and that is the interesting part:

- **Six quests carry zero `COMPLETE_QUEST`** — `q_carto`, `q_debt`, `q_herd`, `q_rail`, `q_salvage`, `q_weather`. All are **placement-driven**: every beat is `discovered`, so they complete implicitly by exhausting their beats. Completion is a function of exploration, not choice.
- **Three quests end on 83% of choices** — `q_ford`, `q_graves`, `q_markers`, all two-beat placement-driven stories where the second beat is the ending.
- **The long quests are the least ending-dense** — `q_signal` 0.15 over 10 beats, `q_caravan` 0.24 over 7, `q_seasons` 0.23 over 6.

That is a coherent design: short discoveries resolve on contact, long stories hold
their endings back. **The corpus does not have a pacing problem.** What it has is
the handful of unfinished branches in §4, which read as gaps in otherwise
consistent authoring rather than as a systemic tendency to end early.
