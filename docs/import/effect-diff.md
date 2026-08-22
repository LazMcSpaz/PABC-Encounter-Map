# Effect diff — content census vs. engine contract

Content-side agent. Diffs the consolidated export's effect census against
`PABC/docs/encounter-import/engine-contract.md` (game-side agent, `main @ d623ae0`).

## Provenance — read this before using any number

| Source | Status |
|---|---|
| Engine side (42 types, targeting, silent-failure list) | **[VERIFIED-DOC]** — read directly from `E:\Repos\PABC\docs\encounter-import\engine-contract.md`. I did not re-derive it from engine source. Its own labels (`[VERIFIED-RUN]` etc.) carry over. |
| Content side (all counts below) | **[RELAYED]** — supplied to me second-hand. `remnant_content_consolidated_rev2.json` is **not yet on this machine**; `scripts/find_content.py` still returns zero hits. **Nothing below is parser-verified on the content side.** |

`scripts/diff_effects.py` in this repo reproduces the entire table from the real
file in one pass. **Run it the moment the file lands.** Until then every content
count here inherits the reliability of a human-relayed summary, and the relayer
explicitly flagged themselves as a lossy channel.

**One arithmetic check does pass:** the 22 relayed top-level counts sum to
exactly **1133**, matching the stated `effects` row count, and the nested counts
sum to exactly **158**. Internally consistent. That is not the same as correct.

---

## 1. The buckets

Engine implements **42** types. The editor's validator and JSON importer accept
**23** of them (a strict subset). The content uses **23 distinct types**, which
is a coincidence of size, not the same set.

Totals: **1,291 effect instances** = 1,133 top-level + 158 nested.

### Bucket 1 — implemented AND editor-accepted: 1,178 instances (91.2%)

| Type | top | nested | total | Engine group |
|---|---:|---:|---:|---|
| `SET_PLAYER_FLAG` | 378 | 96 | **474** | B |
| `ADVANCE_QUEST` | 191 | 0 | **191** | B ⚠️ see §3.1 |
| `ADJUST_RESOURCE` | 134 | 33 | **167** | A |
| `COMPLETE_QUEST` | 111 | 0 | **111** | B |
| `ADJUST_STANDING` | 78 | 10 | **88** | B ⚠️ self-standing no-ops |
| `QUEUE_DEFERRED` | 77 | 2 | **79** | B |
| `ADJUST_TRACK` | 41 | 3 | **44** | B |
| `ADJUST_BASE_STRENGTH` | 2 | 9 | **11** | C |
| `MODIFY_STAT` | 3 | 3 | **6** | A |
| `FORCE_CHOICE` | 5 | 0 | **5** | A ⚠️ always picks `options[0]` |
| `MOVE_CARD` | 1 | 0 | **1** | A |
| `DELIVER_ENCOUNTER` | 0 | 1 | **1** | B |

### Bucket 1b — editor-accepted, engine has a handler, handler does nothing: 10

Not "unsupported." Worse: these validate, import, run, emit no error, and have
no effect. Content authored against them is silently dead.

| Type | total | Why inert | Ref |
|---|---:|---|---|
| `PEEK` | **8** | handler body is an empty comment | `effects.js:308-310` |
| `SURCHARGE` | **2** | pushes to `state.surcharges`; nothing ever reads it | `effects.js:322-332` |

### Bucket 2 — implemented in engine, REJECTED by the editor pipeline: 83 (6.4%)

Both are Group D (diplomacy). They run correctly in a live game, but
`import.js:214-216` rejects any effect type outside the editor's 23, so **this
file cannot pass through the editor import path as authored.**

| Type | total |
|---|---:|
| `ADJUST_HONOR` | **59** |
| `ADJUST_MENACE` | **24** |

### Bucket 3 — not implemented at all → **hard throw**: 20 instances, 7 types

`applyEffect` throws on an unknown type (`effects.js:546-548`). This is the
engine's one loud failure. Each of these **takes down the turn that resolves it.**

| Type | total | Note |
|---|---:|---|
| **`ROLL`** | **10** | ⚠️ believed safe by both prior sources — see §2 |
| **`CONTEST`** | **5** | ⚠️ believed safe by both prior sources — see §2 |
| `GRANT_SAFE_PASSAGE` | 1 | |
| `TAKE_UNIT` | 1 | |
| `SET_MOVEMENT` | 1 | |
| `PERSISTENT_VISION` | 1 | |
| `ESTABLISH_DUAL_HOLDING` | 1 | |

1,178 + 10 + 83 + 20 = **1,291.** ✓

---

## 2. The headline: the prior "unsupported" list was wrong in both directions

Thread Web's README and its `SIMULATED_EFFECTS` table both named nine
unsupported types. Diffed against the engine contract, that list is wrong on
five of nine — and, far more seriously, it **omits the only two that crash.**

| Type | Prior belief | Engine reality | Instances |
|---|---|---|---:|
| `ADJUST_BASE_STRENGTH` | unsupported | **fully implemented** (Group C, editor-accepted) | 11 |
| `MODIFY_STAT` | unsupported | **fully implemented** (Group A) | 6 |
| `MOVE_CARD` | unsupported | **implemented** (Group A) | 1 |
| `SURCHARGE` | unsupported | implemented **but inert** | 2 |
| `SET_MOVEMENT`, `GRANT_SAFE_PASSAGE`, `TAKE_UNIT`, `PERSISTENT_VISION`, `ESTABLISH_DUAL_HOLDING` | unsupported | correct — absent, will throw | 5 |
| **`ROLL`** | **"the run executes it against its stated chance"** | **absent from all 42. Throws.** | **10** |
| **`CONTEST`** | **"pauses the run and asks which branch"** | **absent from all 42. Throws.** | **5** |

`ROLL` and `CONTEST` appear **zero times** in the entire 45 KB engine contract —
not in Group A, B, C, or D, not in the silent-failure inventory, not in the
stale-docs section. Thread Web simulates both, which is exactly why nobody
flagged them: the authoring tool's playtest mode executes them convincingly, so
they look proven.

**15 of the 20 throwing instances are types everyone believed were working.**
This is the highest-severity finding in the diff. It is also the one most worth
re-verifying: if the engine contract merely *omitted* `ROLL`/`CONTEST` rather
than establishing their absence, the severity collapses. **The game-side agent
should confirm `Object.keys(EFFECTS)` contains neither, explicitly.**

---

## 3. Semantic collisions — types that are implemented and still wrong

These do not show up in a type-presence diff at all. They are worse than the
missing types because nothing will error.

### 3.1 `ADVANCE_QUEST` ×191 — probable double-advance

The contract, on `ADVANCE_QUEST`:

> "**You rarely author this** — `beatAsEncounter` appends an `ADVANCE_QUEST` to
> *every* choice on *every* beat automatically (`quests.js:50-56`)."

The content authors **191 explicit** `ADVANCE_QUEST` effects. If the engine also
auto-appends one per choice, every authored beat advances **twice** — skipping a
beat per resolution and completing quests at roughly double speed. With 131 beats
and 35 quests this would corrupt essentially every quest line, silently, with no
error and no log anomaly beyond quests finishing early.

**Unresolved and load-bearing.** Two readings: (a) the content was authored for a
pipeline where the auto-append does not apply, or (b) the auto-append is real and
these 191 rows must be stripped on import. **This needs the game-side agent to
answer before anything is imported.** [INFERRED — from the contract's prose; I
have not read `quests.js`.]

### 3.2 `deliverCondition` is never read

Silent-failure #9: the engine looks for `beat.condition`, but the editor writes
`deliverCondition` (`quests.js:93` vs `snapshot.js:120`). The editor's validator
*requires* `deliverCondition` for `deliver: "conditional"`.

So every conditional beat in the file **fires unconditionally.** Count unknown
until I can parse `quest_beats` — this is a top-priority number in
`diff_effects.py`.

### 3.3 `count_flags` is not in the DSL

The authors flagged this themselves ("now load-bearing, not optional"). The
contract independently confirms it: §4.8 enumerates every implemented condition
form and `count_flags` is **not among them**, and an unrecognised object shape
evaluates to `false` (`dsl.js:247`).

Two sources agreeing from opposite directions is the strongest signal in this
document. Concrete consequence, as the authors stated: `ch_clm3_install` gates on
`count_flags{prefix:'rule_'} >= 2` and will **never offer**; `ch_clm4i_hard` /
`ch_clm4i_soft` never split.

### 3.4 Every choice auto-resolves to ordinal 0

Silent-failure #13: there is no UI for world encounters or quest beats, and
`evaluateTriggers` is called with no `ctx.interact`, so delivery falls through to
`headlessPick` → `0`. With **383 authored choices**, the overwhelming majority
are unreachable today. `FORCE_CHOICE` ×5 compounds it — it also picks
`options[0]`.

This does not corrupt data, but it means an import cannot be validated by
playing it. [VERIFIED-DOC]

### 3.5 `recurring_yield` — authors' HIGHEST PRIORITY

Seven sites want a per-round yield and are authored as fixed `QUEUE_DEFERRED`
chains carrying a `_note`, to be collapsed when the effect lands. `recurring_yield`
appears **zero times** in the engine contract — it is not among the 42, and no
Group D entry resembles it. So the workaround is currently load-bearing and the
`QUEUE_DEFERRED` ×79 count includes scaffolding that is not meant to survive.

---

## 4. Shape questions for the import path

1. **snake_case vs camelCase — no problem, and the concern was misdirected.**
   The contract (§4.2) specifies top-level keys that are **snake_case table
   names** (`world_encounters`, `quest_beat_prereqs`, …) whose values are arrays
   of rows **in camelCase**. The file reportedly has exactly that: snake_case
   keys, and effect rows `{id, parentKind, parentId, ordinal, type, paramsJson}`,
   which is camelCase. **Both sides match.** No transformation needed.

2. **`paramsJson` vs `params` — a real open question.** The contract says the
   editor emits `{id, type, params: {…}}` and `normalizeEffect`
   (`content-loader.js:18-33`) flattens that to `{type, ...params}`. The content
   carries **`paramsJson`**. The importer does stringify object values for
   JSON-TEXT columns (`import.js:36-41`), so `paramsJson` is plausibly the DB
   column and `params` the runtime form — but if `normalizeEffect` keys on
   `params` literally, **every effect in the file flattens to nothing**. Highest-
   value cheap check on the engine side.

3. **`triggerWeight` column gap.** `ALLOWED_COLUMNS.world_encounters` omits
   `triggerWeight`, though migration `0006` added it and `triggers.js:40` reads
   it. Any `world_encounters` row carrying it is rejected as an unknown column.
   Need to check all 18 rows. In `diff_effects.py`.

4. **Max 3 choices per beat** (`validation.js:220-222`). 383 choices across ~160
   parents averages 2.4, so the mean is fine but the max may not be.
   In `diff_effects.py`.

---

## 5. Recipient tokens — the item I cannot yet answer

This was flagged to me as the highest-risk item in the import, and I agree with
that assessment. **I cannot answer it without the file.**

Six of fourteen "locked" recipient tokens are unimplemented. They resolve to
their own literal string (`targeting.js:70-72`), `state.players["most-raided"]`
is `undefined`, and the effect vanishes — no error, no log line. The editor's
`isValidRecipient` accepts all six, so they validate, import, export, and do
nothing. **[VERIFIED-DOC, engine-side `[VERIFIED-RUN]`]**

| Token | Status |
|---|---|
| `active`, `each`, `triggering-player`, `chosen-by-active`, `claimant`, literal fid | ✅ resolves |
| `random` | ❌ **silent no-op** |
| `most-raided` | ❌ **silent no-op** |
| `least-engaged` | ❌ **silent no-op** |
| `lowest-standing-with:<fid>` | ❌ **silent no-op** |
| `highest-standing-with:<fid>` | ❌ **silent no-op** |
| `controller-of:<hex>` | ❌ **silent no-op** |

The one sampled value was `"target": "active"`, which is the safest token in the
vocabulary — but a single sample from a 548 KB file establishes nothing about the
other ~1,290 instances. `random` in particular is the kind of token that gets
reached for constantly in encounter writing, and it is dead.

Note also that `ADJUST_STANDING` (88 instances) does **not** run its `faction`
field through the resolver — it must be a literal fid — and self-standing
(`pid === fid`) is an additional silent no-op. Two distinct ways for those 88 to
vanish.

`scripts/diff_effects.py` counts every distinct `target` / `recipient` /
`player` / `claimant` token with frequencies and flags dead ones. **Ready to run;
blocked only on the file.**

---

## 7. Verification status of this document

**[VERIFIED]** `scripts/diff_effects.py` was run against a synthetic fixture
built to the relayed census. It reproduced every bucket in §1 exactly:
1,178 OK / 10 inert / 83 editor-rejects / 20 throws, 23 distinct types, and the
nested-recursion count of 158 (the fixture hides all nested effects inside a
`QUEUE_DEFERRED.paramsJson.effects` carrier, so a non-recursing parser scores 0
on that line). The fixture run reports one extra instance throughout — that is
the carrier row itself, not a discrepancy.

**So the bucketing logic is proven; the inputs are not.** The classification of
any given type is sound. Whether the content actually contains 378
`SET_PLAYER_FLAG` rows remains [RELAYED] until the file lands.

The fixture also demonstrates the §5 risk concretely: pointing 158 nested effects
at `"target": "random"` produces *no error anywhere* — they simply never happen.
That is what the real failure will look like.

---

## 6. What I need

1. **`remnant_content_consolidated_rev2.json` on disk**, anywhere. Everything in
   §4 and §5 resolves in one pass, and every relayed number in §1 gets re-derived
   rather than trusted.
2. **Game-side confirmation on two points**, both cheap and both load-bearing:
   - Does `Object.keys(EFFECTS)` contain `ROLL` or `CONTEST`? (§2 — severity of
     the worst finding depends entirely on this.)
   - Does `beatAsEncounter` auto-append `ADVANCE_QUEST`, and does that apply to
     imported content? (§3.1 — decides whether 191 rows must be stripped.)
