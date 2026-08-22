# Gate discrimination, the seen-guard gap, and the `outcomeText` pass

**All [VERIFIED-PARSED]** against the post-rename
`remnant_content_consolidated_rev2.json`.

---

## 1. Capability rename — complete, 4 of 4

| Choice | New predicate |
|---|---|
| `ch_bunker_lab` | `{any:[{has_chip:{holder:"location-on-hex", chipId:["labs","advanced-lab"], player:"active", hex:"encounter-hex"}}, {op:"eq", left:"active", right:"versari"}]}` |
| `ch_sig_intrigue` | `{has_tech:{path:"intelligence", branch:"b", player:"active"}}` |
| `ch_cro_observe` | `{has_tech:{path:"intelligence", player:"active"}}` |
| `ch_car_spy` | `{has_tech:{path:"intelligence", branch:"b", player:"active"}}` |

Residuals: `players.active.techLevel` **0**, `.intrigue` **0**, `.recon` **0**.
All seven table counts unchanged. Diff is 23 insertions / 12 deletions — the four
conditions and nothing else.

Note `ch_car_spy` and `ch_sig_intrigue` now carry the **same** predicate. That is
correct: both are "you run espionage", and the original `recon>=2` / `intrigue>=2`
were two authors' names for one capability.

---

## 2. `q_signal` — the three-ending fire

**Verdict: the test almost certainly inflated it, but two of the three can
legitimately co-fire, in sequence, by design.**

The three gates are single permanent flags:

```
qb_sig_out    (ord 5)  has_flag sig_extracted
qb_sig_stays  (ord 8)  has_flag technician_stayed
qb_sig_dead   (ord 9)  has_flag technician_dead
```

**`sig_extracted` and `technician_stayed` are mutually exclusive** — every site
that sets either sets them as **alternative `ROLL` branches of the same choice**
(`qb_sig_force` "Hit the workshop only": success ⇒ extracted, failure ⇒ stayed;
same shape on both `qb_sig_intr` choices). The only unconditional setters of
`technician_stayed` are `qb_sig_2` "Leave it alone" and `qb_sig_dip` "Withdraw the
request", both abandon paths that never set `sig_extracted`. **So those two
endings cannot both fire in one legitimate walk.**

**`sig_extracted` and `technician_dead` can both be true, and should be.** The
route is: extract him → `qb_sig_out` "Put him to work" → `sig_death_due` on a
**5-round `QUEUE_DEFERRED`** → `qb_sig_end` "See to it properly" sets
`technician_dead` → `qb_sig_dead` delivers. That is a sequence across five rounds,
not a fan-out. `qb_sig_out` at ordinal 5 is not an ending at all — it is the
what-do-you-do-with-him beat; `qb_sig_dead` at ordinal 9 is the coda.

**So all three at once requires `technician_stayed` alongside `sig_extracted`,
which no path produces.** Consistent with the agent's own suspicion that its run
walked every marker at once.

### 2a. The systematic check — only 2 single-choice collisions in the corpus

**26 of 35 quests have no routing at all** and rest entirely on `deliverCondition`
(`q_apprentice`, `q_assembly`, `q_caravan`, `q_carto`, `q_courier`, `q_croppers`,
`q_debt`, `q_debtbook`, `q_favor`, `q_ford`, `q_graves`, `q_herd`, `q_markers`,
`q_massacre`, `q_rail`, `q_readerright`, `q_returned`, `q_runner`, `q_saltman`,
`q_salvage`, `q_signal`, `q_stewardbook`, `q_tempest`, `q_weather`,
`q_wirereader`, `q_works`). So the class the question asks about is most of the
game, not one quest.

Across all of them, testing every choice's flag output against every beat's
positive gate — and treating `ROLL`/`CONTEST`/`FORCE_CHOICE` branches as
alternatives rather than co-occurrences — **exactly two choices satisfy more than
one gate:**

| Choice | Satisfies | Verdict |
|---|---|---|
| `qb_sig_out` "Put him to work" | `qb_sig_drift` + `qb_sig_end` | **By design** — `sig_death_due` is on a 5-round `QUEUE_DEFERRED`; the drift beat is now, the reckoning is later |
| `qb_cro_baron` "Hear his price" | `qb_cro_relic` + `qb_cro_blowback` | **By design** — deferred at **6** and **10** rounds respectively |

**Both are deliberate deferred sequences, not fan-out bugs.** Which means the
content's branch discrimination is sound — *provided the deferred timers fire on
schedule.* If `QUEUE_DEFERRED` resolved immediately, both would present as exactly
the "several endings at once" symptom.

**That is the thing worth testing next:** the two known multi-gate choices are both
timer-dependent, so a `QUEUE_DEFERRED` regression would look like a content bug.

---

## 3. The real structural gap: **no non-opening beat guards against re-delivery**

| | has `not has_flag` self-guard | none |
|---|---:|---:|
| **opening beats** (ordinal 0) | 20 | 15 |
| **all other beats** (ordinal > 0) | **0** | **96** |

**Zero of 96.** Openers commonly carry `not has_flag seen_notes` and similar;
**no beat after the first carries any equivalent.** Every one of those 96 gates is
a permanent flag that, once set, stays true for the rest of the game.

So **delivery-once is entirely the engine's bookkeeping.** Nothing in the content
prevents a beat re-firing every round its gate remains true, and the gates never
stop being true. Given a re-entrancy bug was already found and fixed in the
delivery loop, this is worth stating plainly:

> **96 of 131 beats have no content-side re-delivery guard. If the delivered-once
> record is ever bypassed, lost on load, or not consulted, those beats repeat
> indefinitely.**

This is not a content defect — self-guarding every beat would be noise, and the
opener guards exist because openers are trigger-scored rather than prereq-gated.
But it is a load-bearing engine invariant that the content silently assumes, and
it should be an explicit test rather than an emergent property.

---

## 4. `outcomeText` — audited, and it needs no pass

Now that it is visible, the question was whether any of the 383 were written
assuming they would not be. **They were not. Nothing needs changing.**

- **0 empty or missing.** All 383 carry text.
- **0 authoring-note tells** — no `TODO`, `TBD`, `FIXME`, `placeholder`, no bracketed or angle-bracketed stubs.
- **Length:** min 23 chars, median 131, max 363. The five shortest are deliberate and land well — *"Nothing is settled. Everything works."*, *"The works adapts. It adapts downward."*, *"There is nothing to do but carry it."*
- **No mechanical leakage.** A scan for stat names returned 9 hits, and **all 9 are false positives** — every one uses the word in its ordinary English sense, not as a stat: *"a **standing** voice on anything you sign"*, *"none of his **standing**, which out here is the more serious loss"*, *"the same counsel and none of the **standing**"*. Read as prose, which is what they now are.

These were written as player-facing prose throughout. The UI surfacing them
recovers authored work rather than exposing scaffolding.

---

## 5. Art

**0 of 131 beats carry an `art` field**, so the text-only path is the only path.
Field encounters *do* carry `art` — all 11 have an art direction string
(`fe_bridge_toll`: *"A trestle bridge over a cut river; a folding table at the near
end, a man with an open ledger, no escort."*) — as do the world encounters.

So the asymmetry is specific: **single-shot content is art-directed, quest beats
are not.** If art is coming, the 131 beats are the gap, and the field/world
encounters already model the house format for those prompts.
