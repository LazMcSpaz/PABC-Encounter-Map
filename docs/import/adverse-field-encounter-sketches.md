# Three adverse field encounters — shapes, not content

**Sketches for discussion. Nothing written into the content file.**

Template: `fe_bridge_toll` — *"The crossing has a price"* — both options cost, in
different currencies, and neither is the wrong answer. The cost is in **meeting
the encounter**, not in choosing badly.

Each sketch below demonstrates a **different mechanism of unavoidability**, so the
user is choosing between kinds rather than between flavours. All three use effects
the engine implements today (`ADJUST_RESOURCE`, `ADJUST_BASE_STRENGTH`,
`MODIFY_STAT`, `ADJUST_STANDING`, `ADJUST_HONOR`, `QUEUE_DEFERRED`,
`SET_PLAYER_FLAG`) and none uses a crashing type. `MODIFY_STAT{stat:"Movement"}`
is used in preference to `SET_MOVEMENT`, which has no handler.

Field-deck scale: swings are small — `−1` to `−4` Resource, `−1` Strength, `−1` to
`−2` standing. Quest beats carry the big numbers; the road should nag, not maul.

---

## A. Attrition — the world takes something. *"The Water Below the Camp"*

**Mechanism:** a physical need with no free answer. Every option spends a
different resource. This is the simplest adverse shape and the one that reads most
clearly as *"I wish I hadn't drawn that."*

> **art:** A shallow river in flat light; upstream, a picket line and cook-smoke; downstream, a column watering horses.

**text**
> The only water between here and the escarpment runs past a camp that has been in
> one place too long. Not a settlement — a work gang, or what is left of one, sixty
> or seventy people who stopped moving before they meant to. Their latrine trench
> is upstream of the ford and has been for a season. Nobody there is hostile and
> nobody there is well. Your farrier looks at the water and then at you and does not
> say anything, because it is not his to say.

| choice | outcome | effects |
|---|---|---|
| **Water the column here** | Most of them are fine. Eleven are not, and two of those are people you would have named if asked to name your best. | `ADJUST_BASE_STRENGTH −1` · flag `drank_below_the_camp` |
| **Boil what you can carry** | A day's fuel and half a night's rest for perhaps two days of clean water, which is not two days of riding. | `ADJUST_RESOURCE Resource −3` · `MODIFY_STAT Movement −1 this_turn` |
| **Ride dry to the escarpment** | You arrive in the condition of people who have ridden dry, and the escarpment has water, and the horses remember the crossing you did not stop at. | `MODIFY_STAT Movement −1 until_your_next_turn` · `ADJUST_BASE_STRENGTH −1` |

**Why it works as a skip target:** the cost is guaranteed and legible before you
choose. A player who could see this coming would route around it, which is exactly
the feeling the tech should sell.

---

## B. Standing — every option offends someone. *"The Stock on the Line"*

**Mechanism:** no material cost at all; the cost is that you are the only authority
on the road and everyone will hear what you did. Adversity through **obligation**
rather than damage.

> **art:** A wire fence across open grass, cut and knotted twice; two families thirty yards apart, neither closer.

**text**
> Two holdings share a fence and forty head of stock, and the fence has been cut
> twice by people who each believe they were putting it back. Both families have
> been waiting for somebody with a seat to come along this road, and now somebody
> has. They are not angry. They are patient in the specific way of people who have
> rehearsed. Whatever you say here will be repeated accurately in two halls by
> nightfall, including if you say nothing.

| choice | outcome | effects |
|---|---|---|
| **Rule for the older claim** | The older family is vindicated and does not gloat, which is worse. The younger one moves stock off ground they have worked for six years and is careful to be seen doing it. | `ADJUST_STANDING goldgrass +1` · `ADJUST_HONOR −1` · flag `rule_hard_fence_seniority` |
| **Rule for the working claim** | Possession answers it. It is the practical ruling and it is heard as a seat that will move a fence for whoever is standing nearest it. | `ADJUST_STANDING goldgrass −1` · `ADJUST_HONOR +1` · flag `rule_soft_fence_use` |
| **Decline to rule** | You tell them it is not yours to settle. They accept this politely and both understand that a seat which rides past a fence is a seat with a limit on it, and now they know where the limit is. | `ADJUST_TRACK reputation −1` · flag `declined_the_fence` |

**Two notes.** This is the only sketch that costs no material at all, and it may be
the most unwelcome of the three for exactly that reason — the player cannot pay
their way out.

It also **feeds the `rule_*` ledger**, which currently draws on 15 sources, none of
them field encounters. If the moral ledger is to reflect a run's whole shape,
putting a ruling on the road is a cheap way to widen its reach. Adverse encounters
that are *also* ledger sources do two jobs at once.

---

## C. Deferred — the bill arrives later whatever you do. *"The Column That Crossed Ahead of You"*

**Mechanism:** the cost is **out of sight at decision time**. This is the shape
that makes a skip genuinely valuable, because the player learns the deck can
charge them on a delay and cannot reason their way out in the moment.

> **art:** A churned crossing on an empty road; many horses, one direction, hours old.

**text**
> The trail is hours old and the count is not ambiguous — sixty or seventy riders
> moving fast and not caring who reads it, heading for country where you have
> people and interests and no garrison worth the word. They are not coming toward
> you. That is the whole of what you can say for certain, and it is going to matter
> shortly which of the several things you could do about it you did.

| choice | outcome | effects |
|---|---|---|
| **Shadow them** | You follow at distance for two days and learn where they are going, which costs you the two days and the ground you meant to cover. | `MODIFY_STAT Movement −1 until_your_next_turn` · `ADJUST_RESOURCE Resource −2` · flag `shadowed_the_column` |
| **Send a rider ahead** | The warning goes out under your colors, ahead of any confirmation, to people who will remember both that you sent it and what it cost them to act on it. | `ADJUST_RESOURCE Resource −2` · `QUEUE_DEFERRED 4 → ADJUST_STANDING <faction> −1`, flag `warned_ahead` |
| **Note it and ride on** | You write down the count and the hour and the direction, which is the correct thing to do and takes no time at all. | `QUEUE_DEFERRED 5 → ADJUST_HONOR −2, ADJUST_TRACK trust −1`, flag `let_the_column_pass` |

**Why the third option is the point.** It is free at the table, correct by any
reasonable standard, and it is the expensive one. A player meets it once, pays five
rounds later, and understands the field deck differently from then on. **That
single lesson is what converts the skip tech from a curiosity into something people
research.**

---

## How these three sit together

| | cost currency | visible when choosing? | pays for a skip because… |
|---|---|---|---|
| **A. Water** | strength / resource / tempo | yes | the loss is certain and you would route around it |
| **B. Fence** | standing / honor / reputation | yes | you cannot pay your way out |
| **C. Column** | deferred standing, honor, trust | **no** | you cannot see it coming |

**If only one gets built, build C.** A and B make the deck harder; **C makes the
deck untrustworthy**, and an untrustworthy deck is the only thing that makes
foresight and avoidance worth paying for. It is also the shape that would most
change how the existing 17 protected flavour cards read — once any draw might be a
deferred bill, riding past the silo stops being free and starts being a small
relief.

Two caveats I would not want lost:

- **These are additions.** Per `_readme.flavor_only`, none of the eight protected encounters should acquire mechanics to make room for these.
- **Voice check.** I have written to the register rather than around it — concrete physical detail, no adverbs of drama, the sting in the last clause. If the user reads these as pastiche rather than continuation, that is the more useful signal and worth more than the mechanics.
