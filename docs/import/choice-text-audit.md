# Choice-text audit — 383 choices

**All numbers [VERIFIED-PARSED]** from `remnant_content_consolidated_rev2.json`.
Reproduce: `python scripts/audit_choices.py <file>`.

**Standard applied** (the user's): the player must understand *what they are
choosing to do*; they must **not** learn *what the outcome will be*. **There is no
length target.** A clear three-word label is already correct.

So this audit **does not flag short labels.** Length is reported for context only.
Scoring on length would have produced exactly the pad-everything-to-a-sentence
outcome the brief warns against.

**Nothing has been rewritten.** §4 is a register sample for reaction.

---

## 1. Headline

**383 choices, 45 flagged (11.7%), 338 clean.** The corpus is in good shape; this
is a tail, not a rewrite.

| Category | n | What it means |
|---|---:|---|
| `NO_OBJECT` | 25 | verb with no object |
| `DEICTIC` | 23 | "it"/"them" with no antecedent in the label |
| `BARE_VERB` | 17 | a posture with no object — "Decline" *what?* |
| `SIBLING_DUP` | 6 | reads like its neighbour |
| `MISLEADING_CANDIDATE` | 4 | flagged for human read — **all four cleared, see §3** |
| `HEDGE` | 2 | "something"/"somehow" hides the action |

Categories overlap; 45 distinct choices.

Length distribution, for context only — **not a defect axis**:

```
1 word: 9 | 2: 47 | 3: 114 | 4: 94 | 5: 73 | 6: 28 | 7: 13 | 8: 3 | 10: 1 | 11: 1
```

Median 4 words. The corpus is already terse-but-concrete; the flagged tail is
where terseness tipped into ambiguity.

---

## 2. Sibling threshold — tuned to **0.70**, and why

Swept over every sibling pair in the corpus:

```
>=0.60 -> 14 pairs   >=0.65 -> 8   >=0.70 -> 3   >=0.72 -> 2   >=0.80 -> 1
```

**Below 0.70 the check inverts.** Opposite-meaning pairs that share a noun score
in the 0.61–0.67 band — "Honor the tally" / "Refuse the tally" (0.61), "Press the
request" / "Withdraw the request" (0.62), "Give her the pledge" / "Refuse the
pledge" (0.64). Those are *maximally* distinct choices. Loosening the threshold
buys only false positives, so I did not loosen it.

0.70 keeps all three genuine hits; 0.72 (my original guess) would have dropped a
real one — `we_petition` at 0.71. I also added a contrastive-verb guard so a
give/refuse pair can never be flagged however similar its string.

**But two of the three hits turned out to be false positives for a better
reason** — see §3.2. String similarity was the wrong instrument; **choice
`condition` is the right one.**

---

## 3. What I read myself

### 3.1 `MISLEADING` — the category came back **empty**. Report this as a negative.

My first pass produced 16 hits. **All 16 were artifacts of my own heuristic**, and
I am reporting that rather than passing them on.

- **12 were a substring bug.** "Take the **pay**ment", "Take the **share**", "Take
  what she **offer**s" matched a generosity word list by substring. Fixed to
  word-boundary regex.
- **The remaining 4 I read by hand** — beat text, label, outcome text, and the
  full effect list — and **all four are coherent**:

| Choice | Verdict |
|---|---|
| "Leave it as it stands" (+2 lakers) | Correct. Leaving a holding unresolved preserves a profitable arrangement. Outcome: *"Nothing is settled. Everything works."* |
| "Say nothing about the arrangement" (+3 goldgrass, +2 Res, **honor −1**) | Correct — and well-written. The honor cost *is* the moral price. |
| "Refuse the rate" (**−2 Res**, honor +1) | Correct. Refusing costs resources; my filter caught it only on the honor term. |
| "Leave the family to it" (honor +2) | Correct. |

I also **deleted** the generosity and aggression detectors rather than repairing
them. Their premise — *gave something away but score rose = misleading* — is
simply wrong in this fiction, where generosity is *rewarded* with standing and
honor. Twelve false positives, zero true ones. The faction-mismatch detector
survives; it compares data to data.

**Finding: zero misleading labels in 383.**

### 3.2 `SIBLING_DUP` — 4 of 6 are false positives, and the reason matters

`qb_gr_2` carries two choices both labelled **"Ask them what happened"** — a 1.00
string match, and the defect I was most confident in. It is not a defect:

```
ord0  cond = { not: { has_flag: heard_witch_account } }
ord1  cond = {      has_flag: heard_witch_account   }
```

**Mutually exclusive. The player never sees both.** They are the same question
asked with and without prior knowledge, and the second outcome pays off the
corroborating detail. That is careful writing, not duplication.

Same at `we_petition`: "Refuse them plainly" is unconditional, "Refuse them, and
be heard" gates on `rule_soft_assize_need`. Variants on your record, not siblings.

**The genuinely weak pair is `we_petition` ord3/ord4** — "Deal with the leaders
privately" (unconditional) vs "Try to deal with the leaders" (gated on
`rule_hard_assize_contribution`). Here both *can* be visible together, and the
difference between them — that the second is the same act attempted from a worse
reputation — is not legible from either label.

**Method correction:** any future duplicate check must read choice `condition`
first. String similarity without it is close to useless here.

### 3.3 A consequence: 8 of the 16 "too many choices" violations are false alarms too

The editor caps a beat at 3 choices; 16 parents exceed it. But counting only
*unconditional* choices, **8 of the 16 drop to 3 or fewer** — `we_bunker` has 5
rows but only 2 unconditional, `qb_gr_2` has 4 but only 2.

**8 are real** and exceed 3 even unconditionally: `qb_app_2`, `qb_car_blackmail`,
`qb_fd_2`, `qb_hire_2`, `qb_mk_2`, `qb_sea_1`, `qb_tem_2`, `we_reader_gate`.

Worth raising with the engine agent: if the validator counted
simultaneously-eligible choices rather than total rows, half these violations
disappear without touching content.

---

## 4. Register sample — before/after, for reaction only

Drawn from real flagged rows, with the beat text that surrounds them. Each adds
the **object** and, where it matters, the **stakes** — while saying nothing about
the outcome.

**1. `ch_car_req_refuse` — `BARE_VERB`**
Context: the high city asks for a second grain shipment; the asking costs them more than the grain is worth.
- before: `Decline`
- after: `Decline the second shipment`
- *Adds the object. Four words instead of one. Nothing about consequence.*

**2. `ch_salvage2_force` — `DEICTIC`**
Context: families, not soldiers — cutting gear, a windlass, a camp with children in it. They say plainly they know how a fight would go.
- before: `Take it`
- after: `Drive the families off and take the wreck`
- *This is the case the brief is really about. "Take it" is not unclear so much as **unweighted** — it hides that the object is a camp with children in it. The stakes become legible; the outcome does not.*

**3. `ch_asm2_comply` — `BARE_VERB`**
Context: they block something you need, for reasons defensible but wrong. You gave them this authority. Taking it back is a thing you could do in an afternoon.
- before: `Comply`
- after: `Honor the block you granted them`
- *Names what is being honoured and why it stings. Still four words.*

**4. `ch_rail1_walk` — `BARE_VERB`**
Context: a work gang closing a mile-wide gap in the rail line, short of iron.
- before: `Leave them to it`
- after: `Leave them to close the gap alone`
- *Same length. The object arrives.*

**5. `ch_weather2_talk` — `BARE_VERB`**
Context: a storm, one overhang, two groups. Somebody says more than they meant to.
- before: `Talk`
- after: `Talk with them through the storm`
- *Sibling is "Keep to your own fire", so the axis is already implied — this is the mildest case, and arguably fine as-is. Included to mark the floor.*

**6. `ch_petition_split_weak` — `SIBLING_DUP` (the real one)**
- before: `Try to deal with the leaders` / sibling `Deal with the leaders privately`
- after: `Approach the three leaders separately` / `Buy off the leaders one by one`
- *Differentiates by method rather than by confidence. "Try to" leaks that it may fail — which is outcome information, and the one place the current text arguably breaks the rule in the other direction.*

**Register summary:** verb + object, concrete noun from the beat text, no
adverbs of confidence ("try to", "attempt"), no outcome. Most fixes land at 4–6
words. **Nine one-word labels exist and not all need to change** — where the
sibling supplies the contrast, one word is enough.

---

## 5. Recommendation

The 45 flagged rows split roughly:

- **~6 worth fixing regardless** — the `we_petition` pair, and the handful where the object is genuinely missing rather than merely implied.
- **~25 worth a pass** for stakes-legibility, of which `ch_salvage2_force` is the model case.
- **~14 are fine** once you accept that a sibling can supply the contrast.

I would not touch 338 clean rows.

**One thing to decide before any rewriting:** "Try to deal with the leaders" leaks
the *outcome* (that it may fail) while hiding the *action*. That is precisely
backwards from the standard. If the user agrees, that inversion — not length — is
the real editorial target, and it is worth grepping for other confidence-hedged
labels before a rewrite pass begins.
