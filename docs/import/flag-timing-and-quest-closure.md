# Flag timing vs. quest closure — the two cases, read from the fiction

**Proposal only. Nothing written to the content file by this document.**
[VERIFIED-PARSED against `remnant_content_consolidated_rev2.json` @ `6fe0b3f`]

Two cases were handed to me as instances of the same bug: *a `COMPLETE_QUEST`
fires before the flag a later beat waits on can matter.* They are not the same
bug. One is a real authorial idea that the data structure cannot currently
express. The other, on the evidence in the file, is not broken at all.

---

## Case 1 — `qb_sig_dead`: the premise does not hold

**The brief says `ch_sig_end_ack` is the only writer of `technician_dead`. It is
not.** There are two writers:

| Writer | On choice | Completes q_signal? |
|---|---|---|
| `ef_sig_force_assault_roll` — `ROLL` `onFail`, 55% | `ch_sig_force_assault` "Go in hard" | **no** |
| `ef_sig_end_dead` — plain `SET_PLAYER_FLAG` | `ch_sig_end_ack` "See to it properly" | yes, same effect list |

`ch_sig_force_assault` carries `ADJUST_MENACE`, the `ROLL`, and
`ADVANCE_QUEST qb_sig_force`. **No `COMPLETE_QUEST`.** So on the assault-failure
branch the quest is still open, `technician_dead` is set, and `qb_sig_dead`
(`deliver: auto`, gate `has_flag technician_dead`, no prereq row) delivers
normally. That route is: *Answer him -> Take him -> Go in hard -> the roll fails.*

### Why the walk may still have called it unreachable

`qb_sig_dead`'s reachability depends on nothing but a `ROLL.onFail` branch — no
deferred timer, so the `--rounds` turns-vs-rounds defect is not the explanation
here. The likeliest reading is that the UNREACHABLE classification is produced
by a **static writer scan that does not descend into `ROLL` / `CONTEST` /
`FORCE_CHOICE` nested effect lists**, while DELIVERED is produced dynamically.
That would make `qb_sig_dead` a false positive.

It is worth testing on the engine side, because it is not a one-off: **nested
writes are load-bearing across the corpus.** `technician_stayed` — the gate on
`qb_sig_stays` — has five writers and **three of them are inside `ROLL.onFail`**
(`ef_sig_force_raid_roll`, `ef_sig_intr_run_roll`, `ef_sig_intr_bribe_roll`). A
scan blind to nesting would misjudge those too.

### What about the inert write at `qb_sig_end`?

`ef_sig_end_dead` genuinely cannot trigger anything: it sets `technician_dead`
in the same list that closes the quest, and `technician_dead` is read by
**exactly one thing in the whole corpus — `qb_sig_dead`'s gate**. So it is a
write with no reachable reader.

Whether that is a defect is an authorial question, and the two beats read like
this:

> **`qb_sig_end`** — "They found him in the morning at the bench, and everything
> he was working on was finished and labelled and left in order, because that
> was the last thing he could decide about. Word of it will travel. There are
> very few of these people and they know each other's names."

> **`qb_sig_dead`** — "He did not survive it. Whatever else this cost you, that
> is the part that will be remembered by the only people who could have replaced
> him."

These are **two endings of the same shape for two different routes**, not a
scene and its epilogue. `qb_sig_end` is the coerced-to-death ending and already
lands its own closing note about the other wire-readers. `qb_sig_dead`'s "He did
not survive it" is the language of a raid that went wrong, and it carries the
*same* closing note. Played back to back you would read the body being found,
then be told more vaguely that he did not survive.

**Recommendation: change nothing in `q_signal`.** `qb_sig_dead` already works as
the assault-failure ending. If you disagree and want the two routes to converge
on a shared epilogue, the change is not "move the completion" — it is to delete
`ef_sig_end_dead` and drop `COMPLETE_QUEST` from `ch_sig_end_ack`, which gives
the coerced route a second scene. I do not recommend it, and it removes an
existing effect, so it needs your explicit word either way.

---

## Case 2 — `qb_cro_blowback`: a real idea in the wrong quest

This one is exactly what you suspected. The timing is deliberate and the fix
must keep it.

### What the author built

`ch_cro_baron_barter` — "Hear his price" — is the **only choice in the corpus
that arms two deferred timers**, and the gap between them is the whole point:

| Effect | Delay | Sets | Feeds |
|---|---:|---|---|
| `ef_cro_bar_relic` | **6 rounds** | `cro_has_relic` | `qb_cro_relic` (ord 4) |
| `ef_cro_bar_blowback` | **10 rounds** | `cro_baron_blowback_due` | `qb_cro_blowback` (ord 5) |

All three choices at `qb_cro_relic` carry `COMPLETE_QUEST q_croppers`. So the
quest closes at T+6 and the blowback lands at T+10, four rounds into a dropped
quest record. `qb_cro_blowback` is the only writer of `blamed_for_barons_war`,
and `qb_bar_1` opens on it — so **all three beats of `q_baron` die with it.**
That is the five: one blowback beat plus three Baron beats, and `qb_sig_dead`
which I do not think belongs on the list.

**The 6/10 split is not a mistake.** The author is saying: you lend the Baron
your unit, you get your plough iron back and hand the Croppers' story its
ending, and *then*, once you have moved on, the bill for what he did under your
colors arrives. Collapsing that so everything resolves before the quest closes
would destroy the idea.

### Why the blowback is in the wrong quest

Read what the beats are actually about.

`q_croppers` is *The Goddess of the Fields*: a harvest rite you interrupted, a
debt you owe for it, a plough iron worked with figures along the beam. Its
ending is `qb_cro_relic` — return it, sell it, or gift it. That is a complete
story and it ends where it should.

`qb_cro_blowback` is about something else entirely:

> "Whatever Baron Juan did with your people, he did it against another Plainer
> leader, and he did it under colors that were not his own. The main body of the
> Free Plainers is not confused about whose troops those were."

Not one word about the Croppers, the rite, or the relic. And `qb_bar_1` opens:

> "Baron Juan sends a rider... He has heard that you wore the blame for a job he
> did under your colors. He is grateful."

**The blowback is not the Croppers' epilogue. It is the Baron story's inciting
incident.** It is currently filed as the last beat of the quest it has nothing
to do with, and gated behind that quest's closure, which is why it cannot fire.

### Proposal — re-parent the blowback to `q_baron`

Move `qb_cro_blowback` out of `q_croppers` and make it `q_baron`'s opening beat.

| | Before | After |
|---|---|---|
| `qb_cro_blowback.questId` | `q_croppers` | `q_baron` |
| `qb_cro_blowback.ordinal` | 5 | 0 |
| `qb_bar_1` / `qb_bar_2` / `qb_bar_3` ordinals | 0 / 1 / 2 | 1 / 2 / 3 |
| `ch_cro_blowback_ack` closing effect | `COMPLETE_QUEST q_croppers` | `ADVANCE_QUEST q_baron` |

Everything else stays: the beat text, the choice label, the outcome text, the
`-5` Plainers standing, and the `blamed_for_barons_war` write are all untouched.
`qb_bar_1` keeps its existing gate on `blamed_for_barons_war` and becomes
satisfiable for the first time. The 10-round timer is untouched — it now arms a
beat belonging to a quest that has not started, so nothing closes over it.

**No engine change required.** Worth saying plainly, because it bears on the
question you put to the engine agent: the deferred *packet* already survives —
it lives in the player-scoped deferred queue, not in the quest — and A16 shows
packets firing on schedule long after the choice that armed them. What cannot
survive is the *beat*, because A11 records that re-delivering a beat after its
quest completed was a re-entrancy bug they deliberately fixed. Asking them to
loosen that would reopen a fixed defect across all 131 beats. **This proposal
does not need them to.** If they answer that a packet can outlive its quest,
that is true already and does not change the recommendation.

### What it does to the story

The Croppers keep a clean three-act shape that ends when the relic is resolved.
The Baron gets a first act he was always missing — right now `q_baron` starts
*in medias res* with a rider thanking you for blame you took offstage. Under
this change you take the blame on screen, in front of the Free Plainers, and
Juan's rider arrives afterwards to thank you for it. The gratitude lands far
harder when the audience watched the cost.

It also fixes an ordering oddity nobody flagged: today `blamed_for_barons_war`
would be written by the final beat of a quest and read by a quest that opens on
it — a handoff that only works because the reader is a separate quest that has
not begun. Making it the opener of the quest that reads it removes the handoff.

### Alternatives considered and rejected

- **Hold `q_croppers` open until the blowback resolves** (drop `COMPLETE_QUEST`
  from the three `qb_cro_relic` choices). Rejected: on the `ch_cro_baron_fight`
  success route no blowback is ever armed, so the quest would never close at
  all; and it denies the Croppers story its ending for four rounds to wait on a
  scene about someone else.
- **Ask the engine to deliver beats for completed quests.** Rejected above.
- **Re-issue the blowback as a world encounter.** A larger structural change for
  no narrative gain over re-parenting.

---

## Unrelated finding, flagged not acted on

**`ch_cro_baron_fight` "Take it from him" can strand `q_croppers` outright.** The
`ROLL` is 30%; `onSuccess` sets `cro_has_relic`, but `onFail` carries only
`ADJUST_BASE_STRENGTH -99` and sets no flag. On the 70% failure the quest has
advanced past `qb_cro_baron` with no gate satisfied anywhere — `qb_cro_relic`
needs `cro_has_relic` and `qb_cro_blowback` needs a timer that branch never
arms. The quest hangs open forever.

This is the same class of defect as the nine closures in `6fe0b3f`, but it sits
behind a die roll rather than a choice, which is why the earlier sweep did not
catch it. **Not touched here** — it is outside what you asked for, and a `-99`
base strength hit suggests the author may have intended that route to be
catastrophic in some way that wants your reading, not mine.

---

## The `q_tempest` gate — smaller than described, applied

The brief says all five beats gate on `score honor <= 2`. **The gate occurs in
exactly one place in the entire corpus:** `qb_tem_1`'s `deliverCondition`, the
opening beat. The other four beats gate on `tempest_heard`, `tempest_call_due`,
`tempest_resolved` and `tempest_betrayed` — they were blocked *by consequence*,
because a quest whose opener never delivers can never start.

So it is one edit, not five: `right: 2` -> `right: 3`.

For sizing: players start at honour 4, and there are **19 negative
`ADJUST_HONOR` effects** in the corpus, at -1, -2 and -3. At `<= 2` the quest
needed two dishonourable acts before it would even appear; at `<= 3` a single
-1 opens it. That matches the intent of the ruling.

**This one edit has been applied** — a ruled value change with no structural
consequence. The two cases above are held for your word.

---

## Note for the record — the `--rounds` correction

The engine walk's `--rounds` flag was counting turns rather than rounds, so
every deferred timer in every previous measurement was judged against roughly a
quarter of its intended window. Checked against my own earlier work: the
stalled-branch sweep behind `6fe0b3f` reasoned about *whether* a choice closed
its quest, never about *when* a timer landed, and it explicitly excluded the two
`qb_sig_drift` choices on the grounds that `qb_sig_end` fires "whatever happens
at drift" — a claim about routing, not timing. **Nothing in that analysis leaned
on the round counts, so nothing in it needs revisiting.**

The correction does explain why case 2 only surfaced now: at a quarter window a
10-round timer never landed inside the walk at all, so the collision between it
and a quest that closes at T+6 could not be observed.
