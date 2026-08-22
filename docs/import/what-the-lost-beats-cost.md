# What the 24 lost beats actually cost — a story-level reading

Companion to `branching-and-coverage.md`. That file has the counts; this one
answers the question the counts don't: **which stories break, and how badly.**

Structural facts [VERIFIED-PARSED]; the readings of what each quest is *about*
are mine [JUDGEMENT].

**The shape of the damage is uniform: in all nine quests the opening beat
survives and everything after it is lost.** Each becomes a premise with no
second act — the player is introduced to a situation, makes one choice, and the
quest silently completes and pays out.

---

## Tier 1 — quests that lose their entire meaning (3 quests, 15 beats)

These are the six-beat chains. Each loses beats 2 and 3 *and* all three endings.

### `q_notes` — "The Notes" — **the worst single loss in the file**

A settlement invents paper money. Beat 1: a trader offers to settle in notes.
Then: your granary steward asks to keep accounts in notes because conversion is
quietly costing him every week (2) → the Goldgrass hall offers credit against
next year's harvest if your grain land stays in grain (3) → and one of three
endings.

Those endings are the entire argument:

- **`qb_not_4_settled`** — the currency takes hold. *"A farmer who has never been east of the river keeps his savings in a promise signed by a woman he will never meet."*
- **`qb_not_4_called`** — a bank run. *"On a Tuesday in the second month every note in your territory is presented for redemption at once — every hall, every factor, every waystation, on the same morning, by people who had no way of coordinating it and did it anyway."*
- **`qb_not_4_sovereign`** — you issue your own. *"What circulates in your market now is yours, backed by your stores, counted by your steward."*

**A fully authored set-piece on monetary sovereignty, and a bank run written as a
spontaneous coordinated act.** All of it unreachable. What survives is a trader
offering an unusual payment method, then nothing.

### `q_seasons` — "The Season and the Hour"

The Croppers won't harvest on the contracted day because the day belongs to a
rite. Lost: the elder Nane Fisk answering every question courteously and
conceding nothing (2) → the hall repricing Cropper labour out of existence,
*"forty years of custom ends as a line item in a schedule Chelle did not write
and cannot amend"* (3) → and three endings in which a people is **bound**
(absorbed into your territory, keeping their calendar), **scattered** (absorbed
by the Free Plainers), or **restored** (you spend everything to buy back the rate).

**All three fates of an entire people. The quest's whole moral content is in the
endings; without them it is a scheduling dispute.**

### `q_claim` — "Nobody Speaks For Them"

Three men claim the same ground; sixty families live on it. Lost: the Widow Ansel
arriving with forty riders and a claim two generations older (2) → Cutter, who
has no claim and forty people who have worked the ground for eleven years, and
*"has not come to be paid"* (3) → and three endings.

`qb_clm_4_taken` is the thesis statement, not just of this quest:

> *"Three claims, eleven years of work, and sixty families amounted to nothing at
> all the moment somebody with a state behind him decided they did."*

**That is the most explicitly thematic paragraph I've read in the corpus, and it
is unreachable.** `qb_clm_4_installed` is worse off still — blocked twice over,
by the skip *and* by unbuilt `count_flags`.

---

## Tier 2 — quests that lose the reveal the rest depends on (2 quests)

You asked specifically whether any loss takes out a **reveal**. Two do, and
`q_haulers` is the clean case.

### `q_haulers` — "The Ring" — **the reveal itself is the lost beat**

Beat 1: a freight ring offers you a good rate. Reasonable, businesslike, an
accountant named Ledger. You accept or decline.

Beat 2 — **lost** — is the reveal: your quartermaster brings you a tarpaulin
*"because he has recognized the repair on it."* Chain, tack, grain hoppers, cart
axles — off the carts from the raided road. **Ledger's own dated book lines up
with the week those people died.** The freight business is the raiders.

**Without beat 2 the quest is: a man offers you a fair price, you take it, done.**
The player never learns who they are buying from. Beat 3 — Ledger's seasonal
account renewal, *"in the same hand he uses for invoices"* — is unreadable
without the reveal; it lands as bookkeeping instead of complicity.

This is the strongest case in the file for the priority the user set: **the story
does not merely lose an ending, it loses the fact that makes it a story.**

### `q_claim` — the escalation reveal

Beat 2 is also load-bearing as a reveal: the premise of beat 1 is "a man wants
paying for this ground," and beat 2 reveals **there is more than one such man, and
no court.** Without it, beat 1 reads as a simple transaction.

---

## Tier 3 — setup with no payoff (4 quests)

Two- and three-beat quests losing everything after the opener.

- **`q_baron`** (loses 2 of 3) — a baron trades on your name. Lost: Colonel Ives, who lost eleven people to *"troops flying your colors"* and will hear your version **once, in person**; and the resolution, *"not in a battle anyone names, but in who is still holding a gate at the end of the season."* The premise is a favour; the story is the reckoning.
- **`q_hire`** (loses 2 of 3) — a village hires you against raiders. **The lost beat 2 is the actual job** — meet them openly, trap them at the ford, buy them off, or take the fund and sell out to Sull instead. Beat 3 is Dorn's reckoning. What survives is being asked.
- **`q_road`** (loses 1 of 2) — you rule on an old stone grade. Lost: *"A season later the district has arranged itself around whatever you decided... Nobody argued at the time. Everybody has an opinion now."* A consequence beat, and the quest is only about consequence.
- **`q_wire`** / **`q_glass`** (lose 1 of 2 each) — same shape. `q_wire`'s lost beat is where the escort's reputation settles; `q_glass`'s is the wire-reader walking out onto the field and standing there a long time.

---

## The part that is worse than loss

Restating from `branching-and-coverage.md` §2c because it lands hardest here.

For the three Tier-1 quests, the endings are branch alternatives gated on a flag
set by the choice. The skip removes the **chosen** ending; the ignored
`deliverCondition` lets the **unchosen** ones fire.

So in `q_notes`, a player who chooses "Give her the pledge" — who accepts the
hall's credit and puts their grain land under someone else's plan — does not see
the currency take hold. **They see the bank run and the sovereign-currency
ending, neither of which they chose, and which contradict each other.**

That will not read as an engine bug. It will read as writing that doesn't follow
from the player's decisions — the single most damaging way for this content to
fail, given that following from decisions is the entire point of it.

---

## Priority, if the fixes have to be ordered

1. **`ADVANCE_QUEST` routing semantics** — recovers all 24 beats, all nine quests, both reveals, every ending. One behaviour.
2. **`deliverCondition`** — stops the wrong endings firing, and restores pacing across all 30 `*_due` timers.

These are the same bug from the player's side and there is no partial credit:
fixing only #1 shows the player every ending at once; fixing only #2 still hides
the one they chose. **Neither is worth shipping alone.**

Everything else in the diff — the 20 crashing effects, `count_flags`, the 83
editor-rejected diplomacy effects — is smaller than these two, and all of it is
recoverable later without rewriting content.
