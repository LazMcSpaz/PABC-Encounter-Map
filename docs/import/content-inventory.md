# Content inventory — PABC-Encounter-Map

**Status: BLOCKED — the encounter/quest content is not in this repository.**

Written by the content-side agent, phase one (inventory, read-only). Nothing in
this repo was modified except the addition of this file and
`scripts/find_content.py`.

Every claim below is tagged **[VERIFIED]** (established by parsing files or
running git commands, reproducibly) or **[SECONDARY]** (read out of prose in
this repo's own README — i.e. an *assertion by the tool's author about a file I
do not have*, not something I checked).

---

## 1. The headline finding

This repository contains **no encounter JSON, no quest JSON, and no content
data of any kind.** It is the source of a single-file authoring tool
("Thread Web"), not a content store.

**[VERIFIED]** The complete file list of `origin/main` at commit `d302f10`:

| path | bytes |
|---|---|
| `.github/workflows/pages.yml` | 945 |
| `README.md` | 13,745 |
| `index.html` | 182,502 (working tree, 174,158 as committed blob) |
| `thread-web-build-doc.md` | 16,124 |
| `thread-web-v2.jsx.txt` | 40,043 |

Five files. No `.json` files.

**[VERIFIED]** This is true of *every* branch and *every* commit, not just the
tip. `git rev-list --objects --all` yields **29 objects total**, and the
complete set of paths that has ever existed in this repository's history is:

```
.github
.github/workflows
.github/workflows/pages.yml
README.md
index.html
thread-web-build-doc.md
thread-web-v2.jsx.txt
```

There are three remote branches — `main`,
`claude/data-export-import-tool-lfp6ph`, and
`claude/quests-encounters-progression-4qrnnt`. **[VERIFIED]** All three have
identical file lists; the branch whose name suggests quest content
(`claude/quests-encounters-progression-4qrnnt`) contains the same five files
and no data.

**[VERIFIED]** `git log --all --diff-filter=D --name-only` returns empty: no
content file was ever added and later deleted. The content was never here.

### Repo state

**[VERIFIED]** No pre-existing local clone was found (see §5). A fresh clone was
made at `E:\Repos\PABC-Encounter-Map`, beside the game repo at `E:\Repos\PABC`.
It is clean, on `main`, in sync with `origin/main` at `d302f10 Merge flag
tokenizer fix and either/or fork`. Nothing has been pushed.

---

## 2. What this repo actually is

**[VERIFIED, by reading `README.md` and `index.html`]** Thread Web is a
zero-dependency, single-file HTML canvas for *authoring and reviewing* encounter
content. It has no backend and makes no network calls. It:

- autosaves the working board to browser `localStorage` under the key
  `remnant.threadweb.board.v1` — per-browser, per-device;
- imports and exports JSON, merging by `id`, never deleting;
- **imports the encounter builder's own table-grouped export directly**, keeping
  every source row verbatim under `board.engine` so the file round-trips
  byte-identical unless edited.

The critical consequence: **the content travels as a JSON file that lives
outside this repo.** The README says so in as many words — "the JSON file is how
a board travels".

---

## 3. The content file this repo expects (schema only — no data)

**[VERIFIED, from `index.html`]** The importer recognises a file as the engine
format when at least three of these seven top-level arrays are present, and
`choices` and `effects` are both arrays:

```js
var ENGINE_TABLES = ["world_encounters", "field_encounters", "quests",
                     "quest_beats", "quest_beat_prereqs", "choices", "effects"];
```

So the content file is **table-grouped**, with those seven tables plus an
optional `_readme` object carrying `required_systems`,
`known_breaks_pre_existing`, and `faction_coverage.gated_chains`.

**[VERIFIED, from `index.html`]** An effect row is `{ type, params | paramsJson }`.
Effects nest: the importer recurses through `params.effects`,
`params.onSuccess`, `params.onFail`, `params.onWin`, `params.onLose`, and
`params.options[].effects`. **Any true effect-type census must recurse — a
flat count of top-level effect rows will undercount.**

### 3a. Effect types the *tool* simulates

**[VERIFIED, from `index.html`]** — this is the **tool's** capability list, NOT
a census of the content. It is a different artifact from the one this document
was supposed to contain, and should not be substituted for it.

```js
var SIMULATED_EFFECTS = {
  SET_PLAYER_FLAG, ADJUST_RESOURCE, ADJUST_TRACK, ADJUST_STANDING,
  ADJUST_HONOR, ADJUST_MENACE, ADVANCE_QUEST, COMPLETE_QUEST,
  QUEUE_DEFERRED, ROLL, CONTEST, FORCE_CHOICE, PEEK, DELIVER_ENCOUNTER
};
```

**[VERIFIED]** Parameter names, recovered from the tool's `effectPhrase()`
renderer — these are the fields each type is expected to carry:

| type | params |
|---|---|
| `SET_PLAYER_FLAG` | `flag`, `value` (`false` = clear) |
| `ADJUST_RESOURCE` | `amount`, `resource` |
| `ADJUST_TRACK` | `track`, `amount` |
| `ADJUST_STANDING` | `amount`, `faction` |
| `ADJUST_HONOR` | `amount` |
| `ADJUST_MENACE` | `amount` |
| `ADJUST_BASE_STRENGTH` | `amount` |
| `MODIFY_STAT` | `stat`, `amount`, `duration` (optional) |
| `ADVANCE_QUEST` | `beatId` |
| `COMPLETE_QUEST` | `questId` |
| `QUEUE_DEFERRED` | `delayRounds`, `effects[]` |
| `ROLL` | `chance`, `onSuccess[]`, `onFail[]` |
| `CONTEST` | `opponentStrength`, `onWin[]`, `onLose[]` |
| `FORCE_CHOICE` | `options[]` (each `{label, effects[]}`) |
| `PEEK` | `count`, `deck` |

Note `ADJUST_BASE_STRENGTH` and `MODIFY_STAT` have renderers but are absent from
`SIMULATED_EFFECTS` — the tool can describe them but not execute them.

### 3b. Condition language

**[VERIFIED, from `index.html`]**

```js
var SIMULATED_CONDITIONS = {
  has_flag, count_flags, all, any, not, op, score, "if"
};
```

`op` takes `eq | ne | lt | lte | gt | gte` with `left` / `right` operands.
`has_flag` carries `{flag}`. `count_flags` carries `{prefix}` — a prefix tally.
Conditions appear on choices under `condition`, and the tool also reads
`triggerCondition` and `deliverCondition`.

### 3c. Other vocabularies the tool knows

**[VERIFIED, from `README.md`'s data contract]** Thread Web's *own* encounter
shape (distinct from the builder format) constrains:

- `type`: `salvage | uncanny | hazard | parley | social`
- `faction`: `none | versari | lakers | goldgrass | plainers`
- `scope`: `universal | gated`
- `status`: `idea | drafted | structured`
- ids are prefixed `fe_`, stable, never regenerated

---

## 4. What the README claims about the missing content

**[SECONDARY — every number in this section is quoted prose from this repo's
README describing a file I could not obtain. None of it is verified. Do not
build against these numbers.]**

> "The consolidated Remnant content (29 encounters, 35 quests, 131 beats, 383
> choices, 1,133 effects) loads as 160 cards on one canvas."

> "On the consolidated file that comes to 23 effect types, of which 14 run and 9
> — `ADJUST_BASE_STRENGTH`, `MODIFY_STAT`, `SURCHARGE`, `SET_MOVEMENT`,
> `GRANT_SAFE_PASSAGE`, `TAKE_UNIT`, `PERSISTENT_VISION`,
> `ESTABLISH_DUAL_HOLDING`, `MOVE_CARD` — do not."

> "The one flag read that nothing writes is `sold_bunker_to_versari`, exactly as
> the file's own readme says."

Three things are worth flagging even at this level of confidence:

1. **The 23 effect types are not enumerated anywhere.** 14 simulated are named
   in code (§3a); 9 unsupported are named in the README. That is 23 — but
   `SIMULATED_EFFECTS` has 14 entries and `MODIFY_STAT` / `ADJUST_BASE_STRENGTH`
   appear in *both* the renderer and the unsupported list, so the arithmetic
   does not obviously close. **This needs resolving against the real file, not
   against prose.**
2. **No per-type frequencies exist anywhere in this repo.** The whole point of
   the requested inventory — how often each unsupported effect fires — cannot be
   answered from what is here. 1,133 effects across 23 types could be a long
   tail of one-offs or nine hard blockers used two hundred times each.
3. `count_flags` is described as "the prefix tally the readme calls load-bearing
   but unbuilt" — i.e. the content's own authors flagged it as an engine gap.

---

## 5. Where I looked for the content

**[VERIFIED — reproducible via `scripts/find_content.py` in this repo]**

Searched for any file containing `world_encounters`, `quest_beat_prereqs`, or
`SET_PLAYER_FLAG`:

- **909 `.json` files** scanned under `C:\Users\Laz PC` and `E:\` (3 KB–80 MB,
  first 400 KB of each read). **Zero hits.**
- `E:\Repos` — see §5a; the decisive hit is there.
- `C:\Users\Laz PC\Downloads` — inspected. Contains `events_master.json`,
  `flag_registry.json` and `EVENT_SYSTEM_HANDOFF.md`, but these are
  **Void Meridian**, a different project with a completely different schema
  (`node_type`, `depth_zone`, `min_resonance`, crew roles). Not PABC content.
  Also present: `ashland-conquest-log-2026-08-15T23-50-45-047Z.txt` (engine log)
  and `remnant_archive.html` (a styled reader, no engine tables).
- `E:\PABC_backups` — five files, all unit-model pipeline material. No encounters.
- Git object store, all branches, all history — see §1.
- Browser `localStorage` (`remnant.threadweb.board.v1`) — **not reachable**; no
  Chrome extension instance is connected to this machine. This is the single
  most likely place the consolidated file currently exists.


### 5a. Where the content almost certainly *is*

**[VERIFIED — `scripts/find_content.py` output]** The marker search does hit
files, but none of them are data. Every hit is *code that defines or consumes*
the format, and the important cluster is inside the game repo:

```
E:\Repos\PABC\editor\sql\0001_init.sql              world_encounters, quest_beat_prereqs
E:\Repos\PABC\editor\src\lib\api.js                 world_encounters, quest_beat_prereqs
E:\Repos\PABC\editor\src\lib\import.js              world_encounters, quest_beat_prereqs
E:\Repos\PABC\editor\src\lib\snapshot.js            world_encounters, quest_beat_prereqs
E:\Repos\PABC\editor\src\lib\schema.js              SET_PLAYER_FLAG
E:\Repos\PABC\editor\src\lib\validation.js          SET_PLAYER_FLAG
E:\Repos\PABC\editor\src\components\EffectEditor.jsx  SET_PLAYER_FLAG
E:\Repos\PABC\src\game\effects.js                   SET_PLAYER_FLAG
E:\Repos\PABC\src\game\content\field-encounters.js  SET_PLAYER_FLAG
```

**"The encounter builder"** — the tool Thread Web's README repeatedly refers to
without ever linking — is `E:\Repos\PABC\editor\`. It is not a separate
project; it lives inside the game repo.

**[INFERRED — from file *names* only; I did not open these files, per the
instruction not to work in the game repo]** The presence of `sql/0001_init.sql`
alongside `api.js` and `snapshot.js` strongly suggests the builder is
**database-backed, not file-backed**: the seven tables are Postgres tables, the
canonical content lives in a database, and the "consolidated export" is a
*snapshot artifact* produced on demand rather than a file that lives anywhere
permanently. That is a complete and sufficient explanation for why 909 JSON
files on this machine contain zero encounter data.

**[VERIFIED]** The three Supabase projects on the connected account are
`morys auto website`, `easy-draft`, and `cascade-home-connect`. **None is
PABC.** So either the builder points at a Supabase project outside this
account, a local Postgres, or something else entirely — `editor/src/lib/api.js`
will say which, in one line, to whoever is cleared to read it.

This is the single most consequential finding in this document, and it changes
the shape of the job: **the content-side source of truth is a database schema
plus its rows, not a JSON file in this repo.** The inventory this document was
meant to contain should be generated by querying that database (or by exporting
a snapshot from it), not by parsing files here.

---

## 6. What is needed to unblock

In rough order of how clean the result would be:

1. **Point me at the builder's database** (§5a). Direct read access to the seven
   tables gives an exact, reproducible census with no snapshot drift.
   `scripts/effect_census.py` in this repo already implements the recursion
   correctly and will run against a snapshot unchanged.
2. **Export a snapshot from the builder** and drop the JSON anywhere on disk.
   `editor/src/lib/snapshot.js` appears to exist for exactly this.
3. **Lift the "don't touch the game repo" restriction for reads of
   `E:\Repos\PABC\editor\`** — that alone would let me resolve where the data
   lives and read the schema, without writing anything anywhere.
4. Failing all three: open Thread Web in a browser that has the board loaded and
   use ⋯ → *Export back to the encounter builder*. That reconstructs the source
   file from `localStorage`, but only if a board is currently saved there — and
   it is a reconstruction, so prefer 1 or 2.

Once the data is reachable, the originally-requested inventory (effect
vocabulary with counts, reference vocabularies, internal inconsistencies) can be
produced in one pass — the recursion rules and table shapes in §3 are already
established, so the census script is straightforward.

**Until then, the engine agent should not treat any number in §4 as a target.**
