# Deferred: a legibility pass over the whole corpus

**Deferred intent, recorded so it is not re-derived.** Nothing here has been
applied. Scope is **131 beats and 383 choices** — every quest, not just the ones
touched so far.

This came out of `q_tempest`. A beat was written so that its argument arrived
entirely by implication, and the user's response was the useful one: *"the level
of intelligence needed to understand what the Laker messenger is saying is too
high. I don't feel it's clear enough to a majority."* The prose was good. It was
the wrong good.

The corpus was written by an author with a strong, consistent voice — concrete,
unsentimental, fond of the sideways observation. That voice is an asset and this
pass must not flatten it. The failure it is looking for is narrower and it is
always the same failure: **the information the player needs has been placed
inside the clever phrasing instead of beside it.**

---

## The test

For every beat and every choice, ask:

> **Could a player who is half paying attention tell what they are being asked
> and what is at stake?**

That framing matters. These boxes appear once, mid-turn, with a map and a
resource bar and someone else's turn timer on screen. A reader who is giving the
text their full attention is not the reader to design for. The prose does not
get a second pass from the person it is written for.

And underneath it, the sharper diagnostic — the one that actually finds things:

> **Is the information sitting *inside* the clever phrasing, or *beside* it?**

Beside it is fine. A plain sentence carrying the stakes, followed by an oblique
one carrying the texture, is this corpus at its best and there is a great deal
of it. Inside it is the defect. If deleting the clever construction would delete
a fact the player needs, the construction is load-bearing and has to be
rewritten.

**The fix is never to flatten into instructions.** The aim is that the *stakes*
are unmissable while the *texture* stays. Short declarative sentences carrying
real content still sound like this world — `qb_tem_3`'s rider is the model:

> He tells you where it is and when it starts, and that a wagon which gets there
> before the lines close is worth two that arrive after. Whether you come
> yourself is a separate question, and he does not ask it.

Two sentences, one job each, no voice lost.

---

## The four failure shapes

All four were found in one quest in one sitting, which is why they are worth
naming — they will recur, and naming them makes the pass mechanical rather than
a matter of taste.

### 1. A figurative verb doing literal work

> *"Tempest will have turned them into men before you get there."*

The player has to learn that **scrap becomes troops** — it is a mechanic, and
this sentence was the only place it was taught. A metaphor is the wrong carrier
for a rule.

**Fixed:** *"Tempest will spend it on men before you get there."*

### 2. An ambiguous pronoun

> *"They will be standing in line by the time the works are dug."*

"They" could be the scrap or the men it bought. The reader has to pick, and only
one reading teaches the mechanic.

**Fixed:** *"Tempest will have two companies standing because of it before the
digging is done."*

### 3. A riddle standing in for a plain noun

> *"there is nothing here that either of you could produce later"*

Six words of puzzle for **no evidence**. It is a good line and it costs the
reader more than it returns.

**Fixed:** *"There is no document, no seal and no witness, which is exactly what
both of you want."*

### 4. An idea delivered sideways

> *"which is not generosity but record-keeping"*

> *"a man who has watched people work out, at exactly this distance, that they
> had pictured something else"*

The most common shape and the hardest to give up, because these are the best
sentences in the draft. The idea is real and the phrasing makes the reader
assemble it. Say it forwards; the observation survives.

**Fixed:** *"They want it on the record that they paid you."* / *"He has seen
people get this close and realise they had imagined something smaller."*

---

## What passes, and should be left alone

Worth stating so the pass does not become a purge. These all stayed:

- **`"He does not thank you extravagantly; among Lakers, that would suggest he
  had doubted you."`** The stakes are in the first four words — you committed to
  the field — and the rest is characterisation sitting *beside* the fact.
- **`"and the waiting is the courtesy."`** A plain statement, not a riddle. It is
  what makes the captain a person.
- **`"She goes without arguing, which is worse than arguing."`** Clear on first
  read and does real emotional work.

The rule of thumb that emerged: **if the clever part is in the second half of
the sentence and the first half already carried the fact, leave it.**

---

## Same class, same pass: vocabulary consistency

`"loads"` survives in **seven places across six quests** — `qb_mas_identify`,
`qb_sw_1`, `qb_sea_4_scattered`, and the outcome texts of `ch_car_supply`,
`ch_db3_full`, `ch_hau1_hire`, `ch_hau3_both`. The ruled player-facing term is
**scrap**, which `qb_wks_1`, `qb_wks_4_expel`, `qb_tem_betray`, `ch_wks1_rent`
and `ch_run3_trade` already use.

Left alone deliberately — changing them is a corpus-wide consistency pass, not a
side effect of a quest rebuild. It belongs here because it is the same kind of
problem: **a player cannot map a word to the resource bar if the text calls it
two different things.** That is a legibility defect, not a style preference.

Worth checking for other resource and mechanic nouns with the same split while
the pass is running.

---

## Not started

Explicitly deferred by the user. This document exists so the finding is not
re-derived and so whoever runs the pass inherits the test rather than inventing
one.

`q_tempest` has already been through it, at `638bb16`, and can be read as the
worked example.
