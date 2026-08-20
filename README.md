# Thread Web

A pannable canvas for authoring Remnant Continent encounter content: cluster by
type, color by faction (or status), tie encounters together through shared
narrative flags, edit everything in plain language, and export JSON for Claude to
mechanize.

Everything is one self-contained file — [`index.html`](index.html). No backend,
no build step, no network calls. It runs from GitHub Pages and equally well from
a file on disk.

Built to [`thread-web-build-doc.md`](thread-web-build-doc.md); the look and feel
follows the [`thread-web-v2.jsx`](thread-web-v2.jsx.txt) prototype.

---

## Using it

**Hosted:** enable Pages once (Settings → Pages → Source: *GitHub Actions*).
Every push to `main` republishes the file via
[`.github/workflows/pages.yml`](.github/workflows/pages.yml).

**Local:** open `index.html` in a browser. Everything works, downloads included.

The board autosaves to `localStorage` under `remnant.threadweb.board.v1` and
restores on reload. That storage is per-browser and per-device — **the JSON file
is how a board travels**, between machines and into a chat.

| Control | What it does |
|---|---|
| **+ Encounter** | Drops a card at the center of the view and opens it for editing |
| **Play** | Walks the board as a player would — see *Playtest* below |
| **Connect** | Pick two cards to draw a manual (teal, dashed) link; tap a link to remove it |
| **Legend** | Doubles as the filter — toggle any faction / type / status to dim the rest |
| **Coverage chip** | Always-visible gap readout: open threads · needs with no source · empty faction poles. Tap for the full breakdown |
| **Systems** | What the mechanized content asks the engine for — see *Engine format* below |
| **color: faction / status** | Recolors the cards; the corner dot always shows the other dimension |
| **Search** | Matches title, hook, teaches, notes, id, flags and choices; dims everything else |
| **Fit / Tidy** | Frame the whole board · re-lay-out into clean type clusters |
| **⋯** | Reset to the nine seed encounters, or clear the board. On a phone it also holds Fit, Tidy and the color toggle |

Pan by dragging empty canvas; zoom with the wheel, the `+`/`–` buttons, or a
two-finger pinch. Dragging a card pushes its neighbours aside — cards never
overlap. `Esc` closes whatever is open.

---

## The Claude round-trip

1. **Export** → *Download .json*, and attach the file to a chat.
2. Claude reads it, writes or revises encounters, and hands back JSON.
3. **Import** → drop that file in. The board **merges by id**: matching ids are
   updated in place, new ones are added, and **nothing is ever deleted**. You get
   a summary (`3 new · 5 updated · 4 unchanged`) before anything is applied.

Every export carries its own return-format contract at
`meta.howToReplyToThisFile`, so the chat knows the rules without being told
again. The export modal shows the same text with a **Copy for chat** button. In
short: reply with a file (or one fenced `json` block) shaped like the export,
include only the encounters you added or changed, repeat existing ids exactly,
send whole encounter objects, omit `x`/`y`, and keep the prose prose.

Because the merge only applies the keys a file actually contains, a partial
encounter — say, a new `hook` and nothing else — updates that field and leaves
everything else on the board untouched.

---

## Playtest

**Play** walks the board the way a session would: pick an encounter, read the
hook, take a choice, and carry the flags it sets forward. It is strictly
read-only — a run never edits or saves anything.

Sequencing is a **thread-walk**. After each choice, encounters your new flags
reach are listed first under *your flags reach these*, with the reason shown
(`holds found_water`); everything else is available below. So a chain can be
followed end to end, or abandoned for whatever else is in the pool.

Start by picking the faction you're playing as. That only matters for
`scope: "gated"` encounters, which spawn for their own faction; choose *no
faction* and nothing is gated out.

### How a choice's flags are worked out

This applies to hand-written content only. A choice imported from the encounter
builder states its effects and its condition outright, so the run uses those and
infers nothing — see *Engine format* below.

For hand-written encounters, flags live on the encounter (`out` / `in`) while
your prose says which choice touches them, so the run reads the `fx` text and
shows every inference on the choice itself:

- A choice **grants** any `out` flag its `fx` text names — `"+1 Tech · sets
  studied_oldworld_machine"` grants that flag, and the button shows
  `sets studied_oldworld_machine`.
- If **no** choice in an encounter names any of its `out` flags, the encounter
  grants them all however it ends.
- A choice **requires** any `in` flag its `fx` names — `"needs befriended_reader
  OR trusted_watersense"` locks the choice until you hold one of them (the
  word *or* makes it any-of; otherwise all named flags are required).

That inference is the point as much as the walk is: a choice showing `sets
nothing`, or a locked choice you can never satisfy, is a finding about the
writing.

### What the summary tells you

Ending a run (or exhausting the pool) gives an on-screen recap: the path with
the choice taken at each step, flags held, **flags this run never picked up**,
encounters **gated out by faction**, encounters **never reached**, choices you
couldn't take and what they needed, and **flags no choice sets** — an `out` flag
in an encounter whose other choices do name flags, meaning no player can ever
obtain it.

Keyboard: `1`–`9` take a choice, `Enter` continues, `Esc` leaves the run.

---

## Engine format — the encounter builder's own JSON

The tool reads the builder's table-grouped export directly: drop a file with
`world_encounters`, `field_encounters`, `quests`, `quest_beats`,
`quest_beat_prereqs`, `choices` and `effects` into **Import** and it is
recognised on sight. The consolidated Remnant content (29 encounters, 35 quests,
131 beats, 383 choices, 1,133 effects) loads as 160 cards on one canvas.

**Nothing is dropped, and nothing is rewritten.** The source tables are kept
whole, and every choice keeps a pointer to its own rows, so ⋯ → *Export back to
the encounter builder* hands the file back byte-identical unless you edited
something the format has a place for. What is written back: encounter, field and
quest titles, body text, and choice labels and outcome text. What is not: new
encounters, changed flags, links, and beat titles — `quest_beats` rows have no
title field, so the ones on the canvas are the tool's own. The export dialog
counts the rows that differ before you download.

How the two models line up:

| Builder | Thread Web |
|---|---|
| `world_encounters` / `field_encounters` | encounters, typed `world` / `field` |
| `quests` + `quest_beats` | quests with beats — beats are cards on the canvas, clustered inside their quest's container |
| `quest_beat_prereqs` | `prereqs` on a beat, drawn as quiet grey sequence edges |
| `choices` + `effects` | `choices[]`, with `fx` written out in plain language (`+1 Tech · sets bunker_online`) and the rows kept verbatim underneath |
| `SET_PLAYER_FLAG` anywhere in a choice's effects | that encounter's `out` — which is what draws the gold flag ties |
| flags read by `condition` / `triggerCondition` / `deliverCondition` | that encounter's `in` |
| a choice gated on `active == <faction>` | `faction` + `scope: "gated"` |
| `_readme.faction_coverage.gated_chains` | the faction of the quests it names |

Faction is only claimed where the file states it. Everything else stays
frontier/none rather than being guessed at from standing changes.

### Systems — what the content is asking for

**Systems** in the toolbar is the reconciliation report. It lists every effect
type and condition operator the content uses, split by whether a run can
actually carry it out; the authors' own `_note` on individual effects; the
file's `required_systems` and `known_breaks_pre_existing` rendered as text
instead of buried in JSON; and flags read that nothing writes.

On the consolidated file that comes to 23 effect types, of which 14 run and 9 —
`ADJUST_BASE_STRENGTH`, `MODIFY_STAT`, `SURCHARGE`, `SET_MOVEMENT`,
`GRANT_SAFE_PASSAGE`, `TAKE_UNIT`, `PERSISTENT_VISION`,
`ESTABLISH_DUAL_HOLDING`, `MOVE_CARD` — do not. Those are preserved, exported
unchanged, and reported during a run as *"the engine would…"* with the author's
note attached. The one flag read that nothing writes is
`sold_bunker_to_versari`, exactly as the file's own readme says.

### What a run does with mechanized content

Where an encounter carries real effects, the run stops guessing and executes
them. It keeps a ledger of Resource and Tech, the `trust` and `alignment`
tracks, per-faction standing, honor and menace; it runs `ROLL` against its
stated chance; it queues `QUEUE_DEFERRED` on a round clock and lands it rounds
later; it advances and completes quests, gating each beat on its prereqs and
`deliverCondition`; and it evaluates the full condition language — `has_flag`,
`all` / `any` / `not`, `op` comparisons against `score`, and **`count_flags`**,
the prefix tally the readme calls load-bearing but unbuilt.

Two things it hands back to you rather than deciding alone: `CONTEST`, which has
no unit model here, and `FORCE_CHOICE`, which is a real choice — both pause the
run and ask which branch to walk.

---

## The data contract

The one part that must not drift. Export shape:

```json
{
  "meta": { "tool": "thread-web", "version": 1, "exportedAt": "<ISO 8601>",
            "importMode": "merge-by-id", "howToReplyToThisFile": [ "…" ] },
  "encounters": [ /* Encounter */ ],
  "links": [ { "from": "<encounterId>", "to": "<encounterId>" } ],
  "quests": [ /* optional; omitted when empty */ ]
}
```

| field | type | meaning |
|---|---|---|
| `id` | string | unique, stable, `fe_` prefix. Never regenerated on edit — this is what makes round-trips lossless |
| `n` | int \| null | optional human-facing number; display only |
| `title` | string | encounter name |
| `type` | enum | `salvage` \| `uncanny` \| `hazard` \| `parley` \| `social` — the cluster |
| `faction` | enum | `none` \| `versari` \| `lakers` \| `goldgrass` \| `plainers` — the color |
| `scope` | enum | `universal` \| `gated` |
| `status` | enum | `idea` \| `drafted` \| `structured` |
| `hook` | string (NL) | what the player reads |
| `teaches` | string (NL) | the world-fact this exposes |
| `choices` | `{label, fx}[]` | `fx` is the effect in plain language, never engine JSON |
| `out` | string[] | flags this encounter sets |
| `in` | string[] | flags it requires |
| `notes` | string (NL) | free notes for Claude at conversion time |
| `x`, `y` | number | canvas position (world coords) |

**Derived, never stored:** flag-edges (every `out` flag that appears in another
encounter's `in`) and dangling flags (an `out` nobody reads — the open threads).

Enums are additive: an unrecognised value is preserved verbatim and shown as
`(unknown)` rather than being rewritten, so old and newer exports both load.
Unknown top-level fields on an encounter ride along untouched through a
round-trip.

### Quests (build doc §7)

```json
{ "id": "q_settle_the_dry_line", "title": "Settle the Dry Line",
  "mode": "single-player", "notes": "Pays off found_water.",
  "beats": [ { "id": "qb_…", "title": "…", "deliver": "auto",
               "text": "…", "choices": [ { "label": "…", "fx": "…" } ],
               "out": [], "in": [], "prereqs": [ "qb_previous" ], "notes": "" } ] }
```

Beats are full citizens: cards on the canvas inside their quest's container,
participants in the flag graph, editable in the same drawer (with a `deliver`
selector and a prereq field), and playable in a run. They merge by beat id, so a
chat can hand back one revised beat without disturbing the chain.

---

## Notes for future work

- **Persistence is swappable.** All storage goes through the `Store` object
  (promise-based `load` / `save` / `clear`). Moving to a server is replacing
  those three methods; nothing else knows where the board lives.
- **Rendering is split in three.** `renderCanvas()` rebuilds structure,
  `renderGeometry()` only moves/recolors what exists (drag, zoom, filter,
  select), and per-card `textUpdaters` refresh one card's text. Drawer typing
  deliberately avoids the structural path so the web doesn't rebuild on every
  keystroke.
- **Engine content is kept whole, in two places.** `board.engine.source` holds
  the imported tables verbatim for the round-trip; each choice also carries its
  own rows on `choice.engine` so the run, the gating and the Systems report can
  read them without walking the source. A 160-card library costs about 920 KB in
  `localStorage`, well inside the usual quota.
- **Rendering splits three ways.** `renderCanvas()` rebuilds structure,
  `renderGeometry()` only moves and recolors what exists, and per-card
  `textUpdaters` refresh one card. Positions are separated in place across
  encounters and beats together, so a node's container never changes with its
  coordinates.
- **Still to build:** minimap and multi-board [Later]. The nine unimplemented
  effect types and the recurring-yield system the content keeps asking for are
  the engine's to build — the tool now names them precisely.
