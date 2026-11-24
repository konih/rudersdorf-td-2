# Research: Rudersdorf 2

Decisions taken before planning, each with the alternatives that were weighed.

## R1 · Graphics library: pygame-ce

- **Decision**: `pygame-ce >= 2.5.6`, the only runtime dependency.
- **Why**: real blitting, alpha, scaling, sound and a 60 Hz loop; version 1's Tkinter canvas
  recreated every item each frame. Verified on 2026-11-24: `pygame-ce 2.5.8` installs from a
  wheel and imports on Python 3.14.6 on the owner's machine (SDL 2.32.10).
- **Alternatives**: Tkinter with a retained-mode renderer (zero install, weak graphics, owner
  chose against it); Python Arcade (needs working OpenGL on every machine); a browser build
  (worse debugging and test loop for the learner).

## R2 · Routing: one breadth-first search from the village gate

- **Decision**: a distance map from the village gate over walkable, unblocked cells; each walking
  enemy steps to the neighbour with the smallest distance. Recomputed only when the set of blocked
  cells changes.
- **Why**: one search serves every enemy (performance), it is the textbook next algorithm for the
  learner (queue, visited set, nested lists), and its result can be drawn on the grid as numbers.
- **Alternatives**: A* per enemy (slower, harder to show); Dijkstra with terrain cost (kept as an
  open challenge: swamp slows but does not change routing).
- **Placement check**: recompute the map with the candidate cell blocked; refuse if a gate or an
  occupied cell is missing from it. 24 × 16 cells make this trivially cheap.

## R3 · "Always playable": capabilities with labelled stand-ins

- **Decision**: the engine calls workshop code only through `Werkbank.rufe(...)`. A function that
  raises `NochOffen` marks its capability open; the engine then uses the stand-in from
  `rudersdorf/ersatz.py` and shows a label. Other exceptions become a `Lernfehler` carrying file,
  line and mission, which the presentation shows while the match is paused.
- **Why**: version 1 stopped the game at the first unsolved mission. The learner should see the
  game get better with each mission, and should never get the reference behaviour for free.
- **Probing**: at load and reload the workbench calls each capability once with a tiny fixed input
  to learn which are open, so labels are right before the first wave.
- **Alternatives**: strict blocking as in version 1 (owner chose against it); silently falling
  back to the reference (forbidden by the constitution).

## R4 · Deterministic fixed-step core, presentation reads events

- **Decision**: `Spiel.schritt(DT)` with `DT = 1/60`; the window accumulates real time and runs
  0..n steps per frame (speed factor multiplies the accumulated time; at most 12 steps per frame).
  The core appends event dictionaries; the presentation turns them into projectiles, particles
  and sounds. Shots take effect when fired.
- **Why**: the same match can run without a window for tests, the laboratory and the bot, and
  give the same result. Drawing cannot change the outcome.
- **Laboratory speed**: the laboratory and slow tests use `LABOR_DT = 1/20`. The step size is part
  of what determines a result, so comparisons are always made at the same step size.

## R5 · Drawing: procedural sprites cached as surfaces

- **Decision**: every sprite is drawn once with `pygame.draw` into a cached `Surface` (per kind,
  level and animation frame); the terrain is one pre-rendered surface per map; each frame is
  blits plus a few primitives. Rendering targets a 1280 × 720 surface that is scaled to the window.
- **Why**: no third-party assets (constitution V), the learner can read and change how things are
  drawn, and blitting cached surfaces is what makes 60 frames per second reachable in Python.
- **Sound**: short tones synthesised into `bytes` with the standard library and played through
  `pygame.mixer.Sound(buffer=...)`; if the mixer cannot start, sound is off and nothing fails.

## R6 · Tests with `unittest`, reference selected by environment

- **Decision**: all tests are `unittest`; `tests/missionen/` runs against `werkstatt` unless
  `RUDERSDORF_LOESUNG=1`; everything else always uses `loesung`. Slow whole-match tests live in
  files named `lang_*.py` so the default discovery pattern skips them.
- **Why**: the learner needs nothing but `pygame-ce`; the split keeps `make test` fast.
- **Own-tests mission**: judged by running the learner's test class against one correct and
  several faulty subjects, a small form of mutation testing that needs no extra tool.

## R7 · Language of identifiers

- **Decision**: German identifiers, comments and messages everywhere outside `specs/`, as in
  version 1, without umlauts in identifiers (`ae`, `oe`, `ue`, `ss`).
- **Why**: continuity for the learner; every name he reads means something to him.

## R8 · What is deliberately left out

Multiplayer, network features, a level editor (maps are text files), building life points,
projectile travel time in the simulation, routing by travel time, releases and installers.
