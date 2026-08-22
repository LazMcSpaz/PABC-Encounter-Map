# Proposed choice-label rewrites — for review before anything is committed

**Nothing has been written to the content file.** Proposals only. Machine-readable
set in `docs/import/proposed-labels.json`.

**Standard:** the label states the action clearly and stays silent about whether
it works. No length target. Sibling set must stay distinct and parallel.

**45 flagged → 25 rewritten, 20 deliberately left alone.** The 20 matter as much
as the 25; reasons in §3.

Corpus effect: **1,490 → 1,546 words across 383 labels (+3.8%)**, 358 untouched.
Four edits are the same length or shorter.

---

## 1. The confidence-hedged sweep — a class of one

Swept all 383 for `try to | tries | attempt | hope to | see if | if you can |
manage to | do your best`, and separately for outcome-telegraphing
(`successfully | fail | in vain | futile | and win | and lose`).

**One hit total: `ch_petition_split_weak`, "Try to deal with the leaders."** The
telegraphing sweep returned nothing.

So the class the user ruled on is a single instance. Worth having swept — the
result is a fact about the corpus rather than an assumption — but it means the
ruling is cheap to apply. **[VERIFIED-PARSED]**

---

## 2. The 25 rewrites

Grouped by why. Beat context in brackets where it drove the wording.

### 2a. Missing object — the label names a posture, the beat names the thing (13)

| id | before | after |
|---|---|---|
| `ch_car_req_refuse` | `Decline` | `Decline the second shipment` |
| `ch_hire1_decline` | `Decline` | `Decline the contract` |
| `ch_db1_decline` | `Decline` | `Decline the advance` |
| `ch_fav2_refuse` | `Refuse` | `Refuse the passage` |
| `ch_gr1_leave` | `Leave them` | `Leave the graves` |
| `ch_hau2_stop` | `Stop` | `End the arrangement` |
| `ch_cro_baron_leave` | `Withdraw` | `Withdraw without the relic` |
| `ch_weather2_talk` | `Talk` | `Talk with them through the storm` |
| `ch_rail1_walk` | `Leave them to it` | `Leave them to close the gap alone` |
| `ch_run2_pass` | `Leave them to it` | `Leave them to find their own panel` |
| `ch_rd1_leave` | `Leave them to it` | `Leave the locals to quarry it` |
| `ch_app3k_ack` | `Leave him to it` | `Leave him at the bench` |
| `ch_sw1_pass` | `Leave him to it` | `Let him ride the dark stretch alone` |

Note the four separate `Leave them/him to it` labels: identical strings on four
different beats meaning four different things. Each now names its own object, and
none of them got longer than six words.

### 2b. Stakes concealed by a pronoun (4)

The case the brief is really about — not unclear, **unweighted**.

| id | before | after | why |
|---|---|---|---|
| `ch_salvage2_force` | `Take it` | `Drive the families off and take the wreck` | "it" hides that the wreck is a camp with children in it |
| `ch_wir1_take` | `Take her` | `Take her by force` | she is a person being moved like freight; sibling is "Hire her honestly" |
| `ch_sig_force` | `Take him` | `Take him by force` | parallel with siblings "openly" / "quietly" |
| `ch_asm2_comply` | `Comply` | `Honor the block you granted them` | names what is being honoured and that you granted it |

### 2c. Genuinely ambiguous — the label could mean two different actions (3)

| id | before | after | ambiguity resolved |
|---|---|---|---|
| `ch_sea3_take` | `Take them on` | `Take the Croppers onto your ground` | read equally as *fight them* or *employ them*; outcome confirms employ |
| `ch_mas_gg_decline` | `Leave it with them` | `Leave the hall to deal with it` | "it" could be the loot or the matter; siblings involve handing over loot |
| `ch_cro_leave` | `Leave them to it` | `Ride on without approaching` | siblings are "Ride down to them" / "Watch from the ridge" — this is the third distance |

`ch_sea3_take` is the most consequential fix in the set: a player reading "Take
them on" as *fight* would choose it expecting the opposite of what happens.

### 2d. Hedged or vague quantifier (2)

| id | before | after |
|---|---|---|
| `ch_stew_outsider` | `Hire someone who's done it` | `Pay for an experienced steward` |
| `ch_fav2_partial` | `Offer something else` | `Offer them goods instead of passage` |

`ch_fav2_partial`'s outcome is *"You substitute material for permission"* — the
label now says that much and nothing about whether it is accepted.

### 2e. The `we_petition` pair (2) — and a structural recommendation

| id | before | after |
|---|---|---|
| `ch_petition_split` | `Deal with the leaders privately` | `Buy the leaders off separately` |
| `ch_petition_split_weak` | `Try to deal with the leaders` | `Make the leaders private offers` |

This drops the pair from 0.71 similarity to below threshold and removes the hedge.
**But it is a workaround, and I want to be straight about that.**

These two are *the same action* with reputation-dependent outcomes:
`ch_petition_split` is unconditional and succeeds; `ch_petition_split_weak` is
gated on `rule_hard_assize_contribution` and fails because *"they have seen your
seat pick the profitable side before."* A player holding that flag currently sees
**both**, and no honest label can distinguish two identical acts.

**Recommended instead:** gate `ch_petition_split` on
`{not: {has_flag: rule_hard_assize_contribution}}`, mirroring
`ch_petition_split_weak`. Then only one ever shows, both can carry the same clear
label, and no rewording is needed. **This is the author's own established
pattern** — exactly what `qb_gr_2` does.

That is a content change (one condition), so I have not made it. If the user
prefers it, the two rewrites above become unnecessary. **Option A: one condition.
Option B: two labels. Not both.**

### 2f. Also removes the hedge (1)

`we_steward` above; counted in 2d.

---

## 3. The 20 left alone — and why that matters

Flagged by the audit, deliberately not changed. Roughly half the flagged set.

### 3a. Mutually exclusive by gate — leave alone (2)

`ch_gr2_press` / `ch_gr2_press_match`, both `Ask them what happened`. Gated on
`not has_flag heard_witch_account` and `has_flag heard_witch_account`. **The
player never sees both.** Same question with and without prior knowledge; the
second pays off a corroborating detail. Careful writing.

### 3b. The sibling supplies the contrast — leave alone (11)

`Refuse him` reads as underspecified in isolation. Next to `Pay him` / `Hang him
in the square` / `Have it done quietly`, it is exact. Padding it to "Refuse his
demand for more pay" would add words and no information.

`ch_car_bm_refuse`, `ch_tem_reject`, `ch_ret3_block`, `ch_bar1_refuse`,
`ch_wr2_ignore`, `ch_wr3_stop`, `ch_cr2_press`, `ch_app1_dismiss`,
`ch_water_wait`, `ch_db2_decline`, and `ch_reader_public`/`ch_reader_private` —
where "in the open" vs "privately" **is** the whole decision and is entirely
legible. That pair sits at 0.76 and I am leaving it there on purpose.

### 3c. False positives from my own detectors (4)

`ch_db1_take` `Take the advance` and `ch_not1_take` `Take the trade` were flagged
`NO_OBJECT` — both plainly have objects. Detector artifact.

### 3d. Cleared on manual read (4)

`ch_salvage2_walk`, `ch_wks4l_ack`, `ch_hire3_paid`, `ch_gls2_leave` — the
`MISLEADING_CANDIDATE` rows I read against beat, outcome and effects. All
coherent. `ch_wks4l_ack` is the sole choice on its beat and needs no
differentiation at all.

---

## 4. Post-rewrite verification

Re-ran the 0.70 sibling check across all 383 with proposals applied. **Two pairs
remain, both intentional:**

```
0.76  we_reader_gate  'Take her counsel in the open' || 'Take her counsel privately'   (neither gated — §3b)
1.00  qb_gr_2         'Ask them what happened'       || 'Ask them what happened'       (both gated — §3a)
```

The `we_petition` pair cleared. **No rewrite introduced a new collision**, and no
rewrite made a flagged choice read as the obviously-correct option — the additions
are objects and methods, never merits.

---

## 5. One thing I could not fix with labels

`ch_petition_split` / `_weak` (§2e) is a **structural** duplicate, not a wording
problem. Two identical actions, both visible, distinguished only by an outcome the
player cannot see. Every wording I tried either leaked the outcome (the original
"Try to") or invented a distinction the fiction does not support.

The condition mirror is the real fix. **Flagging rather than doing.**
