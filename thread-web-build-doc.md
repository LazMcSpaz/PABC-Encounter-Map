# Thread Web — Build Doc

*A standalone, single-file web tool for authoring Remnant Continent encounter
content on a pannable canvas, then exporting it for mechanization. This doc is
the brief for building the shippable version. It describes **what the tool must
do and the data it must preserve** — implementation choices (framework, exact
layout math, build tooling) are the builder's to make, as long as the behavior
and the data contract below hold.*

**Source of truth for look & feel:** the working prototype (`thread-web-v2.jsx`).
Build to match its behavior and aesthetic; this doc fills in the parts a
prototype can't carry (persistence, portability) and the parts we deferred
(quests).

**Downstream format:** the tool's export is handed to Claude, who converts it to
the encounter-builder's table-grouped JSON. See the *Encounter & Quest Authoring
Guide* for that target schema. The tool itself never emits engine JSON — it
captures authoring intent in natural language plus light structure.

---

## 1. The job it does

A game designer authors a growing library of encounters for a 4X strategy game.
Each encounter has to do two things at once: **teach something about the world**
and **produce a mechanical change**. The designer needs to see the whole library
as a connected web — how encounters tie together through shared narrative flags,
where the loose threads and coverage gaps are — and to add and edit encounters
directly on that web in plain language.

When a work session ends, the designer exports the board as JSON, hands it to
Claude, and gets back encounter-builder JSON to import into the actual game
pipeline. The designer keeps editing across many sessions; the same board gets
exported and re-mechanized repeatedly. **The round-trip must be lossless**, which
means stable ids and a stable export schema.

Single user. No auth, no collaboration, no server required for v1.

---

## 2. Architecture & constraints

- **Single self-contained HTML file.** One `index.html` with inlined CSS and JS
  (a bundled build that outputs one file is fine). Drop it on Netlify or open it
  locally — both must work with no backend.
- **Persistence via `localStorage`.** The board autosaves on every change and
  reloads on open. (This is why it can't live as a Claude.ai artifact — those
  can't use `localStorage`. Outside Claude.ai it works normally.) Namespace the
  key, e.g. `remnant.threadweb.board.v1`.
- **Export / import JSON is the portability layer.** Because `localStorage` is
  browser-and-device-bound, JSON export is how a board moves between machines and
  how it reaches Claude. Import replaces the current board (with a confirm).
- **Portable data model.** Keep the board a plain serializable object with no
  view-framework coupling, so a later move to a Supabase-backed multi-device
  version is a persistence swap, not a rewrite. Treat that migration as a real
  future step, not a hypothetical — don't bake `localStorage` assumptions into
  the data layer.
- **Quality floor:** responsive down to a phone, works with touch (pinch-zoom,
  drag), visible focus states, `prefers-reduced-motion` respected. The designer
  works on mobile regularly — mobile is a first-class target, not an afterthought.

---

## 3. Data model — the contract

This is the part to get exactly right; everything else can vary. The export is a
single JSON object:

```json
{
  "meta": { "tool": "thread-web", "version": 1, "exportedAt": "<ISO 8601>" },
  "encounters": [ /* Encounter */ ],
  "links": [ /* Link */ ],
  "quests": [ /* Quest — see §7; omit if unused */ ]
}
```

### Encounter

| field | type | meaning |
|---|---|---|
| `id` | string | unique, stable. Prefix `fe_`. **Never regenerated on edit** — this is what makes round-trips lossless. |
| `n` | int \| null | optional human-facing number; display only |
| `title` | string | encounter name |
| `type` | enum | `salvage` \| `uncanny` \| `hazard` \| `parley` \| `social` — the cluster |
| `faction` | enum | `none` \| `versari` \| `lakers` \| `goldgrass` \| `plainers` — the color |
| `scope` | enum | `universal` \| `gated` (faction-restricted at spawn) |
| `status` | enum | `idea` \| `drafted` \| `structured` — authoring progress |
| `hook` | string (NL) | what the player reads |
| `teaches` | string (NL) | the world-fact this exposes (the exposition job) |
| `choices` | Choice[] | see below |
| `out` | string[] | flags this encounter **sets** |
| `in` | string[] | flags this encounter **requires / reads** (gates a choice) |
| `notes` | string (NL) | free notes for Claude at conversion time (engine caveats, variant ideas, etc.) |
| `x`, `y` | number | canvas position (world coords) |

**Choice:** `{ "label": string, "fx": string }` — `label` is the button text,
`fx` is the effect **in plain language** (e.g. `"+1 Tech · sets studied_oldworld_machine"`).
The tool does **not** author engine effect JSON; Claude translates `fx` into the
real effect palette. Keep `fx` human-readable and specific.

### Link (manual thematic / sequence tie)

`{ "from": "<encounterId>", "to": "<encounterId>" }` — a relationship the author
draws by hand that isn't expressed by a shared flag (thematic pairing, suggested
play order). Distinct from flag-edges, which are derived, not stored.

### Derived, never stored

- **Flag-edges:** for every flag in some encounter's `out` that appears in
  another's `in`, a directed edge source→consumer. Recompute from the data.
- **Dangling flags:** any flag in an `out` with no consumer anywhere — rendered
  as a frayed stub. These are the "open threads."

### Enum stability

The four faction ids intentionally match the engine (`versari, goldgrass,
lakers, plainers`) so `faction` maps straight through. `none` means
frontier/universal. If enums grow, add — don't rename — so old exports still load.

---

## 4. The Claude round-trip

The export is the entire interface between this tool and mechanization. What
makes it work:

- **Stable ids.** Editing an encounter must not change its `id`. Claude keys off
  ids to know "this is the same encounter I mechanized last time," so a re-export
  after edits produces a clean diff, not duplicates.
- **Plain-language effects.** `choices[].fx`, `hook`, `teaches`, and `notes` stay
  natural language. Claude owns the translation into the encounter-builder's
  effect types, conditions, and recipient tokens (`ADJUST_RESOURCE`,
  `SET_PLAYER_FLAG` ↔ `has_flag`, `QUEUE_DEFERRED`, etc.). The author should
  never have to think in engine tokens here.
- **Flags are the through-line.** `out` / `in` are the one place the tool is
  strict, because they drive the flag graph *and* map directly to the engine's
  player-flag memory. Keep flag names snake_case and consistent.
- **`scope: "gated"` and `notes`** carry the two known engine dependencies
  (self-faction token; field-encounter faction gating) forward as authoring
  intent, so Claude knows to handle them at conversion.

The doc a builder should keep open alongside this one is the *Encounter & Quest
Authoring Guide* — it defines the target JSON. This tool is the front porch to it.

---

## 5. Visual system

Match the prototype. The identity is a **dusk-over-the-plains field instrument** —
a working surveyor's canvas, not a marketing page. Two independent encodings that
must not fight:

- **Faction = node color** (the vivid layer). Node is a solid dark card with a
  faction-colored tint, a solid faction-color left spine, and a faction-color
  border. Cards are **opaque** so background/region lines never bleed through.
- **Type = spatial cluster + a labeled region wash** behind the cluster (faint,
  dashed, near-neutral so it never competes with faction color). The region is
  the bounding area of its type's nodes and follows them as they move.
- **Status = a small corner dot** (idea/drafted/structured).

**Palette (tokens):**

```
bg        #1b1a17     panel     #211f1b     line      #39352d
bone      #e9e3d5     muted     #9a9484     faint     #6a655a
gold      #d4b26a  (flag ties, accents)     teal      #4a9d9d  (manual links)

faction.none       #a59d8c
faction.versari    #3fb6b6
faction.lakers     #5b95e6
faction.goldgrass  #e0b53f
faction.plainers   #e0634a

status.idea        #6a655a
status.drafted     #e0b53f
status.structured  #7a9b6e
```

**Type:** a three-role pairing carries the "story + system" duality that *is* this
project — a serif for narrative (node titles, drawer title), a monospace for
system/data (labels, ids, effects, flags), a sans for body. System-font stacks
are fine (no web-font dependency required): `Georgia`-class serif,
`ui-monospace`-class mono, `system-ui` sans.

**Edges:** flag-ties are solid gold curves with arrowheads and a small flag label
at the midpoint; manual links are dashed teal; dangling flags are gold dotted
stubs trailing off the node. Selecting a node **brightens the edges connected to
it** so a thread can be traced.

Spend the one aesthetic risk on the **thread rendering** — the web of gold ties
and frayed open threads is the memorable element. Keep everything else quiet.

---

## 6. Interactions (parity with the prototype)

- **Pan:** drag empty canvas. **Zoom:** mouse wheel (desktop) and two-finger
  **pinch** (touch), plus `+ / – / Fit` buttons and a live zoom-% readout. Zoom
  is anchored to cursor/pinch-midpoint. (Pinch is essential — the designer hit a
  wall on mobile without it.)
- **Node drag with overlap prevention:** dragging a card **pushes overlapping
  neighbors out of the way**; no two cards may overlap. A separation pass runs on
  load, on drag, and on add. The dragged card is authoritative (never displaced).
- **Select → edit drawer.** Tapping a node opens a side drawer (bottom sheet on
  mobile) with every field editable live and in plain language: title, type,
  faction, scope, status, id, hook, teaches, choices (add/remove rows of
  label + fx), sets-flags, needs-flags (comma-separated), and notes-for-Claude.
- **Add / delete** encounters. New node drops at viewport center and opens for
  editing.
- **Connect mode** for manual links: pick a node, then a second, to tie them;
  tap a link to delete it. Also reachable as "link from here" in the drawer.
- **Legend = filter,** reachable from the toolbar (not a bottom-anchored floater —
  those get clipped by mobile browser chrome). Toggling any faction / type /
  status dims the non-matching nodes so the web keeps its shape. The panel is
  anchored below the toolbar and capped/scrollable so it never eats the screen.
- **Search** highlights matching nodes (title / hook / flags), dims the rest.
- **Tidy** re-lays-out all nodes into clean type clusters. **Fit** frames the
  whole board.
- **Export / import** modal with copy-to-clipboard. **Autosave** to `localStorage`
  on every change; reload on open; a **Reset to seed** action to restore the
  starter set.

Seed the shipped tool with the nine starter encounters from the prototype so an
empty board is never the first experience.

---

## 7. Beyond the prototype

Priority-tagged. **[V1]** = build now, **[V1.1]** = next, **[Later]** = when it earns it.

### [V1] Coverage badge
A small always-visible readout of the gap analysis the separate Thread Map view
used to show, now living on the canvas: open-thread count, empty faction poles
(e.g. "Dambaran/martial pole: 0"), and type distribution. This is the tool's
single highest-value insight and it's cheap to derive from data already present.

### [V1] Color-by toggle
A switch to recolor nodes by **status** instead of **faction** (keeping type as
the cluster either way). Lets the author see "what's still just an idea vs
structured" at a glance without opening anything.

### [V1.1] Quests / beats — the real content gap
The prototype only models single encounters. The library is heading toward
multi-beat quests (the open threads exist to be paid off by them), so the tool
needs first-class quests. Spec:

A **Quest** is a container with ordered **beats**. Beats participate in the flag
graph exactly like encounters (they have `out` / `in`), and beats can have
**prereq** beats (a DAG, matching the engine's `quest_beat_prereqs`). Proposed
shape, aligned to the *Encounter & Quest Authoring Guide* tables:

```json
{
  "id": "q_settle_the_dry_line",
  "title": "Settle the Dry Line",
  "mode": "single-player",              // or "global"
  "notes": "Pays off found_water + brokered_peace.",
  "beats": [
    {
      "id": "qb_...",
      "title": "...",
      "deliver": "auto",                // auto | discovered | conditional
      "text": "...",                    // NL, = an encounter's hook
      "choices": [ { "label": "...", "fx": "..." } ],
      "out": [ "..." ],
      "in":  [ "found_water" ],
      "prereqs": [ "qb_previousBeatId" ],
      "notes": "..."
    }
  ]
}
```

**On the canvas:** a quest reads as a container/region with its beats as
sub-nodes inside it, sequenced by prereq edges (a distinct edge style from
flag-ties and manual links). Beats still draw flag-ties to encounters and other
beats, so a quest that consumes `found_water` visibly reaches back to The Dry
Line. Keep beats editable with the same drawer as encounters, plus a `deliver`
selector and a prereq picker. Export adds the top-level `quests` array; encounters
and links are unchanged, so older boards still load.

### [Later] Minimap
A corner overview for when the board outgrows a screen. Nice, not needed until
the library is large.

### [Later] Multi-board / project switching
More than one named board in `localStorage` (e.g. "core deck," "faction quests").
Trivial once persistence is abstracted; skip until there's a second board to hold.

---

## 8. Build notes & non-goals

- **Don't over-specify to the coding agent.** Communicate the behavior and the
  data contract; let it choose the framework and the geometry. The prototype is
  the reference for feel — point the agent at it rather than re-deriving pixel
  values in prose.
- **The data model is the one hard contract.** Field names, enums, id-stability,
  and the export schema must match §3 so Claude's mechanization and the
  round-trip keep working. Everything visual can be re-derived; the schema can't.
- **Non-goals for v1:** no accounts, no realtime, no server, no engine-JSON
  emission (that stays Claude's job), no simulation. Keep the surface small and
  the file portable.
- **Leave room, don't build it:** the persistence layer should be swappable
  (localStorage now, Supabase later) and the enums extensible, but don't
  implement either speculative path in v1.

---

## 9. Acceptance checklist

- [ ] Single HTML file runs from Netlify **and** from a local file, no backend.
- [ ] Board autosaves to `localStorage` and restores on reload; Reset-to-seed works.
- [ ] Export produces the §3 schema; import round-trips it losslessly (same ids).
- [ ] Pan, wheel-zoom, **pinch-zoom**, +/–/Fit, and zoom-% all work; mobile included.
- [ ] Node drag never lets two cards overlap; neighbors are pushed aside.
- [ ] Cards are opaque; faction color is clearly legible; type regions sit behind.
- [ ] Full plain-language editing in the drawer, including flags and notes.
- [ ] Flag-edges auto-draw; dangling flags render as open threads; selection
      brightens connected edges.
- [ ] Legend/filter is in the toolbar, never clipped on mobile, and filters the web.
- [ ] Tidy and Fit and Search behave as in the prototype.
- [ ] Coverage badge shows open threads + empty poles. **[V1]**
- [ ] Color-by faction/status toggle. **[V1]**
- [ ] Responsive to phone; visible focus; reduced-motion respected.

---

*Feel reference: `thread-web-v2.jsx`. Downstream target: the Encounter & Quest
Authoring Guide. Keep both open while building.*
