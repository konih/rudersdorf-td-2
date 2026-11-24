# Tasks: Rudersdorf 2 · Das Labyrinth

**Input**: Design documents from `specs/001-rudersdorf-2/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/werkstatt-api.md

**Tests**: Test tasks are included for every behaviour story and come before its implementation.
A test task closes on a verified red; its tests are fixed points for the implementation task.

## Conventions for every task

- Read the task's cited sections only: `contracts/werkstatt-api.md` (called *contract*),
  `data-model.md`, the *Fixed engine interfaces* in `plan.md`, and the FR/SC ids in `spec.md`.
- Focused test: `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy RUDERSDORF_LOESUNG=1 uv run python -m unittest <module> -v`.
  Gate: `make check`. Slow tier: `make test-lang`. All run in the repository root.
- Mission tests live in `tests/missionen/test_mNN.py`, class `MissionNN`, load the package under
  test through `tests/missionen/helfer.py` (`werkstatt`, or `loesung` when `RUDERSDORF_LOESUNG=1`),
  and give German failure messages that state expectation, actual result and one hint.
- Everything a learner reads is German. Reference code uses only what the missions teach.
- "Known red" means the tests listed in `specs/001-rudersdorf-2/loop.md`, section *Known red*.
  A test task adds its tests there; the implementation task that turns them green removes them.
  `make check` counts as green when its only failures are tests on that list.
- "Tests first inside this task" (presentation tasks): write the tests, run them, and record each
  red with its failure line in the evidence before implementing, as close-task's IMPLEMENT step
  requires. These tasks close green.
- Tests that need the untouched workshop use the repository's `werkstatt/` as shipped; the
  developer test suite is defined on the shipped state.

## Phase 1: Setup

**Purpose**: packages, content tables, the unsolved workshop and the architecture guards

- [x] T001 Create the package skeleton and the layering guard.
  Create `rudersdorf/__init__.py`, `rudersdorf/fehler.py` (`NochOffen`, `Lernfehler` as in plan.md),
  empty packages `rudersdorf/kern`, `rudersdorf/labor`, `rudersdorf/ansicht`, `rudersdorf/uebung`,
  `werkstatt`, `loesung`, and test packages `tests/architektur`, `tests/missionen`, `tests/kern`,
  `tests/ansicht`, `tests/lernen`. Write `tests/architektur/test_schichten.py`: it parses every
  Python file with `ast` and fails when a file under `rudersdorf/kern`, `rudersdorf/labor`,
  `werkstatt` or `loesung` imports `pygame`, when `rudersdorf/kern` imports `rudersdorf.ansicht`,
  or when `werkstatt`/`loesung` import anything from `rudersdorf` other than `daten`, `fehler` and `uebung`.
  The scanning function takes a root directory so the test can prove itself on a temporary tree
  containing one violation of each kind. Verify: `make check`. — closed 2026-11-24, evidence: evidence/T001.md
- [x] T002 Write the content tables and the maps.
  `rudersdorf/daten.py` with every constant and table of data-model.md (Geometry, `BAUWERKE`,
  `GEGNER`, damage types, wave and difficulty formulas as plain functions `wellen_budget(n, faktor)`,
  `wellen_leben_faktor(n)`, `spawn_abstand(n)`, `SCHWIERIGKEIT`, `DORFGEBAEUDE` with all eight lines
  and every level's `kosten`, `braucht`, `boni`, `ZAUBER`). Five map files under `karten/` obeying
  the map rules. `tests/kern/test_daten.py` checks: required keys of every entry; every
  `braucht` key is a village building and its level exists; requirements contain no cycle;
  every ability class name and spell class name is one from the contract; every `teilt_in` kind
  exists; price and `ab_welle` are positive for generated kinds; each map file is 16 × 24, uses
  only known characters, has one `Z`, at least one `S`, and `D` exactly in columns 18–23;
  `zwei_tore` has two `S`. Verify: `make check`. — closed 2026-11-24, evidence: evidence/T002.md
- [x] T003 Create the mission registry, the unsolved workshop and its guards.
  `rudersdorf/missionen.py` with all 26 entries (data-model.md, *Mission registry*), including
  `braucht` (mission 5: [2, 3, 4]; mission 20: [9, 12, 13]; mission 26: [2, 3, 4, 5, 6, 7]; else empty). Stub modules
  for missions 1–20 and 24–26 in `werkstatt/` and `loesung/` with exactly the contract's names and
  signatures: in `werkstatt/` every body is a German docstring plus `raise NochOffen("Mission N: <Titel>")`,
  in `loesung/` a docstring plus `raise NochOffen("Referenz folgt: Mission N")` (so the stand-in rule also protects the half-built reference). `werkstatt/strategien.py` and
  `loesung/strategien.py` define `STRATEGIEN` with the five standard keys. Write
  `tests/architektur/test_werkstatt.py` (by `ast`: every function and method the registry names
  for missions 1–20 and 24–26 in `werkstatt/` has a body that is only an optional docstring and
  `raise NochOffen(...)`) and `tests/architektur/test_paritaet.py` (for every registry module that
  exists in both packages: same public functions, classes and methods with the same parameter
  names and defaults; modules of missions 21–23 are compared by public names only). Both tests
  prove themselves on a temporary package with one violation. Verify: `make check`.
  — closed 2026-11-24, evidence: evidence/T003.md

---

## Phase 2: Foundational

**Purpose**: the workbench that routes every engine call into the workshop

- [x] T004 Write the tests for the workbench in `tests/kern/test_werkbank.py`, using small
  temporary packages created in a temp directory (not `werkstatt` or `loesung`). Add
  `rudersdorf/werkbank.py` and `rudersdorf/ersatz.py` as stubs with the plan's signatures; the
  constructor is `Werkbank(paket, gesperrt=())`, where `gesperrt` names capabilities forced open.
  The temporary packages use the real module and function names of the capabilities they
  exercise (`horde.berechne_schaden` for a one-function capability, the four functions of
  `raster.py` for `wegfindung`, the effect classes for a class capability).
  Cases, each as given / when / then, with the failure it exposes:
  - given a function that returns a value / when `rufe` / then that value is returned (exposes: routing to the wrong module or name)
  - given a function raising `NochOffen` / when `rufe` / then the registered stand-in's result is returned and `ist_offen` is true (exposes: open missions crash the game)
  - given a capability with two functions of which one raises `NochOffen` / when the solved one is called through `rufe` / then the stand-in is used for it too (exposes: half-solved capabilities mixing real and stand-in rules)
  - given a function raising `ZeroDivisionError` on line L / when `rufe` / then `Lernfehler` with that file, line L, `"ZeroDivisionError"`, the message and the mission number (exposes: learner errors crash or lose their location)
  - given a fresh workbench / when created / then `offene()` already lists every capability whose probe raised `NochOffen`, in registry order (exposes: labels wrong before the first call)
  - given `gesperrt=("schadensarten",)` on a fully solved package / then only that capability is open; given `gesperrt=("wegfindung",)` / then `wegfindung` and the capabilities waiting for it (`bauregel`, `bot`) are open (exposes: test hook not honoured, prerequisites not propagated)
  - given a module edited on disk / when `lade_neu` / then the new behaviour is used and openness is probed again (exposes: reload keeps stale code)
  - given an edit with a syntax error / when `lade_neu` / then `Lernfehler` is raised and the previous code still answers (exposes: a typo kills the running game)
  - given a class with a method raising `NochOffen` / when created through `erzeuge` and the method is called / then the stand-in class's method answers (exposes: classes bypass the stand-in rule)
  - given a package without the module or name a capability needs / then that capability is open (exposes: import errors at start-up for a half-filled workshop)
  - given a capability whose prerequisite capability is open (`magie` with `effekte` forced open) / then it is open too and `wartet_auf` names the prerequisite's missions; with the prerequisite solved it is not (exposes: solved missions failing on another track's open code)
  - given a probe that raises `ZeroDivisionError` / then the capability counts as solved and no exception leaves the constructor (exposes: a learner bug preventing the game from starting)
  - given a function raising an error / then the `Lernfehler` has a `spur` text containing the original traceback's last line (exposes: lost tracebacks)
  - given `RUDERSDORF_LOESUNG` unset, `"0"`, `"1"` / when `waehle_paket(None)` / then `"werkstatt"`, `"werkstatt"`, `"loesung"`; and `waehle_paket(True)` is `"loesung"` (exposes: the reference loaded silently)
  Verify: the new tests fail for these reasons; `make lint` is green.
  — closed 2026-11-24, evidence: evidence/T004.md
- [x] T005 Implement `rudersdorf/werkbank.py` (registry `FAEHIGKEITEN` built from
  `rudersdorf/missionen.py`, loading, probing, `rufe`, `erzeuge`, `strategien`, `lade_neu`,
  `wartet_auf`, `PROBEN`, `ABHAENGIG`, `waehle_paket`) and the stand-in registry mechanism in `rudersdorf/ersatz.py` (a dictionary
  capability → name → callable or class; the stand-ins themselves arrive with their stories).
  Turn T004's tests green without changing them. Verify: `make check`.
  — closed 2026-11-24, evidence: evidence/T005.md

**Checkpoint**: the engine can call workshop code safely.

---

## Phase 3: User Story 1 - Defend the village on a free grid (Priority: P1) 🎯 MVP

**Goal**: a playable reference match on the grid with routing, towers, basic enemies, win and loss

**Independent Test**: `uv run python spielen.py --loesung`, bend the route with towers, win or lose

### Tests and implementation for User Story 1 (each test task directly before its implementation)

- [x] T006 [US1] Write the mission tests for track A in `tests/missionen/test_m01.py` … `test_m05.py`
  and `tests/missionen/helfer.py` (package selection, a `TestGegner` double as in the contract's
  conventions, German message helpers), and the stand-in tests `tests/kern/test_ersatz_a.py`.
  Cases come from the contract's rules for missions 1–5, at least:
  - M1 given a three-line text with trailing spaces and blank lines around / then a 3-row grid of characters (exposes: whitespace handling); given rows of different length or an empty text / then `ValueError` (exposes: silent acceptance of broken maps); `finde` returns `(spalte, zeile)` in row order (exposes: swapped coordinates)
  - M2 given a corner, an edge and an inner cell / then 2, 3 and 4 neighbours in the order up, right, down, left (exposes: off-by-one at the border, wrong order); `ist_begehbar` false outside the grid, on rock and water, on a blocked meadow, true on swamp, hill, gates (exposes: index errors, forgetting `gesperrt`)
  - M3 given an open 5 × 5 grid / then the distance equals the Manhattan distance; given a wall with one gap / then cells behind the wall have the detour distance; given an enclosed cell / then it is absent; `ziel` maps to 0; `gesperrt` unchanged (exposes: depth-first instead of breadth-first, revisiting, mutation)
  - M4 given a distance map / then the step goes to the smaller neighbour, ties to the first in order; `None` at the goal and for unknown cells (exposes: walking uphill, wrong tie rule)
  - M5 given a free meadow off the route / then true; rock, water, swamp, gates, an already blocked cell, a cell in `besetzt`, a cell outside / then false; the last gap of a wall / then false; a cell that cuts off a cell in `besetzt` / then false; with two gates, cutting off one / then false; arguments unchanged (exposes: mutation, checking only one gate)
  - stand-ins: `wegfindung` stand-in returns Manhattan distances through rock and buildings (differs from the contract on a walled grid); `bauregel` stand-in refuses a cell diagonally next to a building and allows an isolated one; `karten` stand-in offers only `flusstal`
  - M5 extra: a corridor one cell wide / then building in it is false (exposes: sealing a ford)
  Verify: every new test fails with `NochOffen` or an assertion; `make lint` green.
  — closed 2026-11-24, evidence: evidence/T006.md
- [x] T007 [US1] Implement `loesung/raster.py` (missions 1–5) with a `collections.deque` for the
  search, and the stand-ins `karten`, `wegfindung`, `bauregel` in `rudersdorf/ersatz.py`. Turn
  T006's tests green without changing them. Verify: `make check` (known red excepted).
  — closed 2026-11-24, evidence: evidence/T007.md
- [x] T008 [US1] Write the mission tests for track B in `tests/missionen/test_m06.py` … `test_m10.py`
  and `tests/kern/test_ersatz_b.py`. Cases from the contract's rules for missions 6–10, at least:
  - M6 given enemies inside, exactly on, and outside the range, and a defeated one inside / then the living ones within range in original order, a new list (exposes: `<` instead of `<=`, shooting the dead)
  - M7 given candidates with distinct `rest_weg`, `leben` and positions / then each of the five strategies picks the stated one; ties keep the earlier; empty list gives `None`; `STRATEGIEN` has the five names bound to these functions (exposes: min/max mix-ups, crashes on empty lists)
  - M8 given `STRATEGIEN` with only the five standard keys / then the test raises `NochOffen` ("still open"); given a sixth entry / then it returns a candidate for each test list, `None` for the empty list, and differs from each standard strategy on at least one test list (exposes: a copy of a standard strategy)
  - M9 given a row of enemies 50 apart and `sprungweite` 60 / then the chain follows the row up to `spruenge` jumps; a gap larger than `sprungweite` ends it; nobody is hit twice; defeated enemies are skipped; `spruenge` 0 gives `[start]` (exposes: jumping back and forth, measuring from the start instead of the last)
  - M10 given values and an upgrade with `+`, `*` and `=` / then a new dictionary with the changes and the original untouched; `=` on a new key adds it; an unknown sign, or `+`/`*` on a missing key / then `ValueError` (exposes: mutating the tower's base values)
  - stand-ins: `reichweite` sees an enemy in the tower's row within range and not a diagonal one inside the circle; `strategien` returns some candidate and offers only `zufall`; `kettenblitz` returns `[start]`; `ausbau` reports that upgrades are unavailable
  Verify: every new test fails with `NochOffen` or an assertion; `make lint` green.
  — closed 2026-11-24, evidence: evidence/T008.md
- [x] T009 [US1] Implement `loesung/tuerme.py` and `loesung/strategien.py` (missions 6–10, with
  the sixth strategy `gefaehrlichster`) and the stand-ins `reichweite`, `strategien`,
  `kettenblitz`, `ausbau`. Turn T008's tests green. Verify: `make check` (known red excepted).
  — closed 2026-11-24, evidence: evidence/T009.md
- [x] T010 [US1] Write the mission tests for track C in `tests/missionen/test_m11.py` … `test_m15.py`
  and `tests/kern/test_ersatz_c.py`. Cases from the contract's rules for missions 11–15, at least:
  - M11 given damage 20 and factor 0.4 / then 8; a missing type counts as 1; zero and negative damage give 0 (exposes: healing by negative damage, `KeyError`)
  - M12 given each effect class / then `name`, `rest`, `ist_vorbei`, `tempo_faktor` as stated; `tick` never goes below 0 and ignores negative time; `Gift` with 1 s left and a 3 s tick deals one second of damage of type `gift`; `Brand` deals `feuer`; `Betaeubung` gives factor 0 until over; `Frost`, `Gift`, `Betaeubung` are subclasses of `Effekt` and `Brand` of `Gift` (exposes: damage after the effect ended, duplicated instead of inherited code)
  - M13 given a list with a frost of rest 1 / when a frost of rest 2 is added / then one frost with rest 2; adding one with rest 0.5 keeps the old; a different kind is appended; `gesamt_tempo_faktor` is the minimum over effects not over and 1.0 for none; `raeume_effekte_auf` returns a new list without finished effects (exposes: stacking, mutation while iterating)
  - M14 given a wounded carrier / then `Regeneration` heals `pro_sekunde * sekunden`, not when burning, not when defeated; `Heiler` heals others in radius, not itself, not the defeated, not those outside; `Beschwoerer` returns `[]` until the interval has passed, then `[art] * anzahl`, and again one interval later; all three return a list (exposes: self-healing shamans, summoning every tick)
  - M15 given a catalogue and seeds / then only unlocked non-boss kinds, total price within budget, nothing affordable left over, same seed same wave, different seeds usually different waves, budget below the cheapest price gives `[]` (exposes: bosses in ordinary waves, endless loops, overspending)
  - stand-ins: `schadensarten` returns the damage unchanged for factor 0.4; `effekte` classes exist with factor 1.0 and no damage; `faehigkeiten` classes return `[]` and heal nobody; `wellen` returns only `ork`
  Verify: every new test fails with `NochOffen` or an assertion; `make lint` green.
  — closed 2026-11-24, evidence: evidence/T010.md
- [x] T011 [US1] Implement `loesung/horde.py` (missions 11–15) and the stand-ins `schadensarten`,
  `effekte`, `faehigkeiten`, `wellen`. Turn T010's tests green. Verify: `make check` (known red excepted).
  — closed 2026-11-24, evidence: evidence/T011.md
- [ ] T012 [US1] Write the core tests for map, movement and building in `tests/kern/test_karte.py`,
  `tests/kern/test_bewegung.py`, `tests/kern/test_bauen.py`, with stubs for `rudersdorf/kern/karte.py`,
  `gegner.py`, `bauwerk.py`, `dorf.py` and `spiel.py` carrying the plan's signatures (plan.md, *Fixed engine interfaces*; enemies are placed with `Spiel.erzeuge_gegner`). Tests build a
  `Spiel` with `Werkbank("loesung")` and a small `kartentext`. Cases (FR-001–FR-006), at least:
  - given each of the broken maps of the Edge Cases / when loaded / then a `ValueError` with a German reason; given `karte="gibtsnicht"` / then `flusstal` is used and `meldung` says so (exposes: crashes on bad maps)
  - given a straight corridor / when a walking enemy is stepped for t seconds / then it has moved `tempo * t` pixels along the cells and `rest_weg` fell by the same (exposes: frame-rate dependence, diagonal moves)
  - given swamp cells / then speed halves on them (exposes: terrain ignored)
  - given a building placed on the route during a wave / then enemies finish their current step and then follow the new route; none ever enters a blocked cell (exposes: enemies walking through new towers)
  - given enough gold / when `baue` on a meadow / then true, a `Bauwerk` exists, the price is gone, a `gebaut` event exists; on rock, water, swamp, a gate, village ground, an occupied cell, outside, with too little gold or stone, or an unknown kind / then false, nothing paid, `meldung` gives the reason (exposes: paying for refused buildings)
  - given a wall with one gap / when `baue` in the gap / then false with the "need a way" message; given an enemy on or heading into a cell / then false (exposes: enclosing, building on enemies)
  - given a tower on a hill / then its range is 1.25 times the base (exposes: terrain bonus missing)
  - given a built tower / when `verkaufe` / then gold rises by the selling share of `ausgegeben` rounded down, the cell is free and routes are recomputed; on an empty cell false (exposes: selling without re-routing)
  - given a workbench whose `darf_bauen` always answers yes (temporary package) / when `baue` would seal the route / then false, and `meldung` names mission 5 (exposes: a faulty rule freezing the match)
  - given an enemy with a resistance 0.4 against `stich` / when `erleide_schaden(20, "stich")` / then it loses 8 life, the call returns 8, and life never goes below 0 (exposes: resistances applied twice or not at all)
  - given a reached village gate / then the village loses the enemy's `dorfschaden`, a `durchbruch` event exists, the enemy is gone and pays nothing (exposes: reward for breaches)
  Verify: new tests fail for these reasons (not for import errors); `make lint` green.
- [ ] T013 [US1] Implement `rudersdorf/kern/karte.py` (`Karte`, `pruefe_karte`, loading by name
  from `karten/` through the `karten` capability, the blocked set, the cached distance map through
  the `wegfindung` capability), `gegner.py`, `bauwerk.py` (data and values only), a minimal
  `dorf.py` (life, resources, pay) and the parts of `spiel.py` for construction, building, selling,
  movement and breaches. Turn T012's tests green. Verify: `make check` (known red excepted).
- [ ] T014 [US1] Write the core tests for combat, waves and the match in `tests/kern/test_kampf.py`,
  `tests/kern/test_wellen.py`, `tests/kern/test_spiel.py`, `tests/kern/test_determinismus.py`, with a
  stub for `rudersdorf/kern/wellen.py`. Cases (FR-006–FR-008, FR-010–FR-012, FR-014, FR-015, FR-037), at least:
  - given a tower and an enemy in range / when its reload time passes / then one shot: a `schuss` and a `treffer` event, damage reduced by the enemy's resistance, `schwach` true when the factor is below 1; no shot while reloading or without a target (exposes: shooting every step)
  - given each tower kind / then its effect: cannon hits all ground enemies in `radius` and no flyer; frost adds `Frost`; poison adds `Gift`; lightning hits the chain; palisade never shoots (exposes: one generic hit for all towers)
  - given two enemies / when `setze_strategie` to each standard rule / then the next shot goes to the enemy that rule names; an unknown rule returns false (exposes: targeting rule ignored)
  - given a level-1 tower / when `baue_aus` / then level 2 values per data, gold spent, `ausgegeben` raised; a second `baue_aus` returns false while there is no smithy (master upgrades arrive with T029) (exposes: free or unlimited upgrades)
  - given a defeated enemy / then its reward is added once, a `tod` event exists, it leaves the list (exposes: double rewards)
  - given poison on an enemy / then it loses life over time and can die from it, paying its reward (exposes: effects not ticking, kills by effects unpaid)
  - given `starte_welle` in the build phase / then the phase is `welle`, the wave number rises, enemies of the previewed kinds spawn at the spawn interval; a second call during the wave returns false (exposes: overlapping waves)
  - given the last enemy gone / then the phase returns to `bauen`, the base wave income is paid (gold and stone), a `welle_ende` event exists, and `vorschau()` describes the next wave (exposes: missing income, stale preview)
  - given the last campaign wave cleared / then `sieg`; given village life 0 / then `verloren`; afterwards `schritt` and actions change nothing (exposes: playing on after the end)
  - given the same seed and the same scripted actions / when run twice, and once in steps of `DT` split differently across calls of the caller / then identical `zustand_hash()` (exposes: hidden randomness, wall-clock use)
  - given `fuehre_aus` with the actions `baue`, `ausbau`, `verkaufe`, `strategie`, `welle` and with malformed actions / then the corresponding method's result, and false without change for nonsense (exposes: bots crashing the match)
  - given a workshop with a sixth registered strategy / then `setze_strategie` accepts its name and the tower uses it (exposes: learner strategies not reaching the game)
  - given a finished match / then `statistik()` reports the wave reached, the enemies defeated and the gold earned from kills and income (exposes: empty end screens)
  Verify: new tests fail for these reasons; `make lint` green.
- [ ] T015 [US1] Implement shooting in `bauwerk.py`, `rudersdorf/kern/wellen.py`, and the rest of
  `spiel.py`: the fixed step order of plan.md, effects and abilities through the workbench,
  rewards, wave lifecycle, income, victory and defeat, `vorschau`, `sicht`, `fuehre_aus`,
  `zustand_hash`. Special enemy behaviour (flying over the labyrinth, splitting, breaking, boss
  rules) belongs to T031 and boss waves to T032; until then such kinds behave like ordinary walkers. Turn T014's tests
  green. Verify: `make check` (known red excepted).
- [ ] T016 [US1] Write the presentation tests in `tests/ansicht/test_anwendung.py` and
  `tests/lernen/test_spielen.py`, with stubs for `rudersdorf/ansicht/fenster.py` (plan signatures)
  and `spielen.py`. All run on an off-screen surface with the dummy video driver. Cases, at least:
  - given an `Anwendung` in a match / when `zeichne` is called in each phase (build, wave, victory, defeat, paused) / then no exception and the surface is not uniformly one colour (exposes: drawing code that only works with a window)
  - given a chosen building and a mouse click at the pixel of a free cell, with the window scaled to another size / then that cell holds the building (exposes: wrong pixel-to-cell conversion under scaling)
  - given key events for start wave (`N`, and space in the build phase), pause (`P`, and space during a wave), speed, cancel, upgrade, sell, next rule / then the match state changes accordingly; `N` during a wave changes nothing (exposes: dead keys, overlapping waves)
  - given speed 4 / when `aktualisiere(0.05)` / then exactly 12 steps of `DT` ran (0.2 s simulated); given speed 1 / when `aktualisiere(0.05)` / then 3 steps; given `aktualisiere(1.0)` / then 12 steps and the rest of the backlog is discarded, so a following `aktualisiere(0.0)` runs none (exposes: frame-rate dependent simulation, spiral of death)
  - given a focus-lost event / then the match is paused (exposes: playing on in the background)
  - given a match in the phase `sieg` or `verloren` / then the drawn end screen's text contains the three figures of `statistik()`, and the key `R` (or a click on its button) starts a new match on the same map and difficulty (exposes: dead end screens)
  - given `spielen.main(argv)` / then `--loesung`, `--karte`, `--schwierigkeit`, `--saat`, `--probelauf` are accepted, `--probelauf 1` returns 0 after about one simulated second without opening a real window under the dummy driver, unknown maps and levels are refused with a German message, and without `--loesung` the package is `werkstatt` (exposes: the reference loaded silently)
  Verify: new tests fail for these reasons; `make lint` green.

### Implementation for User Story 1
- [ ] T017 [US1] Implement the first presentation: `rudersdorf/ansicht/fenster.py` (window,
  scaling with preserved proportions, the fixed-step loop, input, speed, focus pause),
  `szenen.py` (the match scene), `gelaende.py` (one pre-rendered terrain surface per map),
  `figuren.py` (a cached sprite per tower kind and enemy kind), `hud.py` (top bar with resources,
  village life and wave; side panel with the building buttons, prices, the selected tower's
  values, targeting rule, upgrade and sell; the next-wave preview; the message line; the victory
  and defeat screens with the statistics and the new-match action) and `spielen.py`. Turn T016's tests green. Verify: `make check`; then
  `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python spielen.py --loesung --probelauf 5` exits 0.

**Checkpoint**: the reference is playable from start to victory or defeat.

---

## Phase 4: User Story 2 - Learn by upgrading a game that always runs (Priority: P1)

**Goal**: the untouched workshop plays; stand-ins are labelled; errors pause; reload works; the
test runner and the mission board guide the learner

**Independent Test**: `uv run python spielen.py` with an untouched workshop; `uv run python pruefen.py`

### Tests for User Story 2

- [ ] T018 [US2] Write `tests/lernen/test_pruefen.py` with a stub `pruefen.py`. The runner is
  driven as a function `main(argv) -> int` with captured output. Cases (FR-027, FR-028, SC-003), at least:
  - given mission 3 and the reference / then exit 0 and a German success line per test (exposes: reference not selectable)
  - given mission 3 and the untouched workshop / then exit 1, every test reported as "noch offen" with the mission title, and no traceback (exposes: frightening output for unsolved missions)
  - given a temporary package whose mission 2 is wrong / then exit 1 and each failing test shows expectation, actual result and one hint (exposes: bare assertion dumps)
  - given a temporary package whose mission 2 raises `TypeError` / then the error type, message, file and line are shown (exposes: hidden learner errors)
  - given `--spur A`, `--alle` and a number together / then a usage error; each alone selects the right missions (exposes: wrong selection)
  - given `--alle` on the untouched workshop / then every mission of 1–20 and 24–26 that exists in the registry reports "noch offen" and nothing else (exposes: SC-003 broken for some mission)
  - given no arguments / then the mission board: every mission by track with title, stars and one of solved / begun / open, and a suggested next mission that is open, has all its `braucht` missions solved, and has the fewest stars within the first unfinished track; a mission with unsolved prerequisites is shown with "braucht Mission …" (exposes: no guidance, suggesting a mission that cannot work yet)
  - given mission 20 selected while mission 12 is open in the package / then the output says first which missions it builds on (exposes: confusing "still open" from another file)
  - given any run / then `.fortschritt.json` holds the state of every mission run, merged with earlier states, written to the directory passed for tests (exposes: board and game out of date)
  - given `--loesung` absent and `RUDERSDORF_LOESUNG=1` in the environment / then the workshop is still tested (exposes: the reference used by accident)
  Verify: new tests fail for these reasons; `make lint` green.
- [ ] T020 [US2] Write `tests/kern/test_ersatz_spiel.py` and `tests/ansicht/test_lernhilfen.py`.
  Cases (FR-023–FR-026, FR-030, SC-001, SC-002), at least:
  - given `Werkbank("werkstatt")` / when a match is played for three waves with a simple scripted defence at `LABOR_DT` / then no exception, and `offene()` lists every capability that exists at this point (exposes: the untouched workshop crashing)
  - given `Werkbank("loesung", gesperrt=(k,))` for each capability `k` of tracks A–C in turn / then three waves play without exception and the open set is exactly `k` plus the capabilities waiting for it (exposes: stand-ins that only work together)
  - given `Werkbank("loesung", gesperrt=all capabilities of tracks A–C except k and its prerequisites)` for each `k` in turn / then three waves play without exception and `k` is not open (exposes: a solved mission that only works when others are solved, SC-002)
  - given the `wegfindung` stand-in / then an enemy walks through a tower cell; given it solved / then it does not (exposes: a stand-in that is secretly the real rule)
  - given a temporary workshop whose strategy returns an object that is not a candidate, and one whose `in_reichweite` raises `NameError` / when the match steps / then `Lernfehler` reaches the caller with file, line and mission; for the wrong return value the line is the function's first line and the type is "Rückgabewert" (exposes: silent misbehaviour)
  - given an `Anwendung` and a `Lernfehler` during `aktualisiere` / then the match is paused, the drawn panel's text contains file name, line, error type and mission title, and the original traceback was written to standard error (captured in the test) (exposes: crash to desktop, lost traceback)
  - given an `Anwendung` on an untouched workshop / then the HUD's label list names each open capability with mission number and title, and a waiting capability with the missions it waits for (exposes: unlabelled stand-ins)
  - given the reload key and a temporary workshop changed on disk / then a new match on the same map and difficulty runs the new code; with a syntax error the panel shows and the old code stays (exposes: restart needed, crash on typo)
  - given the mission-board key and a `.fortschritt.json` / then the board scene lists the missions with those states (exposes: board ignoring test results)
  - given the overlay keys / then distances are drawn from `Spiel.abstaende()`, ranges for every tower, and the frame rate with the mean simulation time per step; each toggles off again (exposes: overlays showing reference data instead of the active code's)
  Verify: new tests fail for these reasons; `make lint` green.

### Implementation for User Story 2

- [ ] T019 [US2] Implement `pruefen.py` (argument parsing, selection by number, `--spur`,
  `--alle`, `--loesung`, the German result printer, the mission board, the suggestion rule, the
  progress file in `rudersdorf/fortschritt.py`). Turn T018's tests green. Verify: `make check`
  (known red excepted); `uv run python pruefen.py` prints the board with everything open.
- [ ] T021 [US2] Implement the learning aids in the presentation: stand-in labels in `hud.py`,
  the error panel and the three overlays in `rudersdorf/ansicht/overlays.py`, the mission-board
  scene in `szenen.py`, the reload key in `fenster.py`. Turn T020's tests green.
  Verify: `make check` (known red excepted); `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python spielen.py --probelauf 5`
  (untouched workshop) exits 0.

**Checkpoint**: a learner can start, play, test and reload.

---

## Phase 5: User Story 3 - Grow the village and its cathedral (Priority: P2)

**Goal**: eight village lines with levels, requirements and bonuses; the five-stage church

**Independent Test**: in the reference, raise three buildings and the church to stage 5

### Tests for User Story 3

- [ ] T022 [US3] Write `tests/missionen/test_m16.py` … `test_m18.py`, `tests/kern/test_ersatz_d.py`
  (village part) and `tests/kern/test_dorf.py`. Cases (contract missions 16–18, FR-015–FR-019), at least:
  - M16 given requirements all met / then `[]`; given three requirements of which two are unmet / then two texts `"<key> Stufe <n>"` in sorted-key order; a missing key in `stufen` counts as level 0 (exposes: `KeyError`, wrong order)
  - M17 given a small catalogue and levels / then the sum over all bought levels of all buildings; level 0 and unknown keys add nothing; a new dictionary each call (exposes: counting only the top level, mutation)
  - M18 given the contract's example (a2 needs b1, b1 needs c1, nothing built) / then exactly `[("a",1),("c",1),("b",1),("a",2)]`; purchases already owned are left out; a prerequisite shared by two requirements appears once; a building needing nothing at level 1 gives `[(g,1)]`; `stufen` is unchanged; for the real `DORFGEBAEUDE` and every building and level, buying the plan in order passes mission 16's check at every step and ends at the target (exposes: duplicates, wrong order, endless recursion, plans that cannot be executed)
  - stand-ins: `voraussetzungen` allows level 1 only; `boni` counts first levels only; `bauplan` yields `None`
  - given enough resources and met requirements / when `dorf_ausbau` in the build phase / then true, cost paid, level raised, `dorf_ausbau` event; during a wave, with too little, with unmet requirements, at the top level, or for an unknown key / then false and nothing paid (exposes: buying during waves, skipping requirements)
  - given each bonus name of data-model.md / then its effect is measurable: tower damage, gold and stone per wave, interest, selling share, population, village life (raising current life by the same amount), armour (each breach reduced, at least 1), price discount in `preis()` for grid and village, `schmiede_stufe` gating master upgrades (exposes: bonuses bought but not applied)
  - given a church at stage 1 and a wounded village / when a wave ends / then life rises by `heilung_pro_welle` up to the maximum; during a wave mana rises by `mana_pro_sekunde` per second up to `mana_max`; without a church mana stays 0 (exposes: healing above maximum, mana in the build phase)
  - given a church at stage 4 / when `glocken_intervall` seconds of wave time pass / then every non-boss enemy has a stun, a `glocken` event exists, and it repeats one interval later (exposes: bells ringing once or stunning bosses)
  - given `dorf_info` for a locked level / then `fehlend` and `bauplan` as the workshop functions return them (exposes: panel without guidance)
  - given a market with interest / when a wave ends / then interest is `zinsen_prozent` of the gold, at most `zinsen_max` (exposes: uncapped interest)
  - given `fuehre_aus({"aktion": "dorf", "gebaeude": k})` / then the result of `dorf_ausbau(k)` (exposes: bots unable to build the village)
  Verify: new tests fail for these reasons; `make lint` green.

### Implementation for User Story 3

- [ ] T023 [US3] Implement `loesung/dorf.py` (missions 16–18, mission 18 recursively), the
  stand-ins `voraussetzungen`, `boni`, `bauplan`, the full `rudersdorf/kern/dorf.py`, and the
  village parts of `spiel.py` (`dorf_ausbau`, `dorf_info`, `preis`, bonuses applied to towers,
  income, selling, healing, mana, bells). Turn T022's tests green. Verify: `make check` (known red excepted).
- [ ] T024 [US3] Implement the village presentation, tests first inside this task
  (`tests/ansicht/test_dorfbild.py`). `rudersdorf/ansicht/dorfbild.py` draws the village ground,
  each building line at each level, villagers, and the church in five stages: (1) a wooden chapel
  with a small bell turret; (2) a stone village church with a pointed-arch door and a spire;
  (3) a basilica with a nave, side aisles and a rose window; (4) a gothic cathedral with flying
  buttresses, pinnacles, tall pointed windows and a crossing spire; (5) the cathedral with twin
  west towers, a large rose window and stained glass that glows with the current mana share.
  `hud.py` gains the village panel: clicking a village building shows its name, level, bonuses,
  the next level's cost, missing requirements and the build order, and a buy button.
  Tests: the five church surfaces differ pairwise and their drawn height grows from stage to stage
  (SC-008); every line and level draws without error; a click on a building opens its panel and
  the buy button calls `dorf_ausbau`; a locked level shows the missing requirements and the plan.
  Verify: `make check` (known red excepted).

**Checkpoint**: the village is a second game beside the battlefield.

---

## Phase 6: User Story 4 - Cast magic (Priority: P2)

**Goal**: five spells with mana, cooldown, unlocking and three levels

**Independent Test**: in the reference with a church, cast each spell in a wave

### Tests for User Story 4

- [ ] T025 [US4] Write `tests/missionen/test_m19.py`, `test_m20.py`, the magic part of
  `tests/kern/test_ersatz_d.py`, and `tests/kern/test_zauberei.py`, with a stub for
  `rudersdorf/kern/zauberei.py`. Cases (contract missions 19–20, FR-020), at least:
  - M19 given a spell with cost 30 and cooldown 10 / then `bereit` is false with 29 mana, true with 30; `zaubere` on a base `Zauber` raises `NotImplementedError` from `wirke` only when ready; with a test subclass, `zaubere` returns mana minus cost, sets `rest` to the cooldown and stores `letzte_wirkung`; when not ready it returns mana unchanged and does not call `wirke`; `tick` lowers `rest` by the time and never below 0 (10 becomes 9 after one second and 0 after twenty) (exposes: paying without casting, casting during cooldown)
  - M20 given enemies inside and outside the radius / then `Feuerball` damages those inside with type `feuer` and adds `Brand` only when `brand_dauer > 0`; `Eissturm` adds `Frost` inside only; `Blitzschlag` starts at the enemy nearest the point within 120 pixels, follows the chain, returns 0 without a start; `Segen` returns what `dorf.heile` returns; `Glockenschlag` stuns all living non-boss enemies; each returns the number affected; each is a subclass of `Zauber` with its fixed name; while mission 9, 12 or 13 is open in the package under test, mission 20's tests raise `NochOffen` naming those missions (exposes: hitting the defeated, stunning bosses, wrong counts)
  - M20 given an enemy that already has a frost, respectively a stun / when `Eissturm`, respectively `Glockenschlag`, hits it / then it still has exactly one effect of that kind (exposes: stacking through `append`)
  - given a cast that reaches no enemy / then mana and cooldown are spent and `meldung` says nothing was hit (exposes: silent wasted casts)
  - stand-in: `magie` reports every spell as unavailable and `zaubere` returns false with the mission label in `meldung`
  - given no church / then `zauber_info()` marks every spell locked; given church stages 1 to 4 / then the spells of data-model.md unlock at their stages (exposes: spells without a church)
  - given a wave, enough mana and a ready spell / when `zaubere` / then true, mana reduced, a `zauber` event with the effect count, and a second cast before the cooldown returns false with a reason; in the build phase false (exposes: free or unlimited casting)
  - given a library level and resources / when `zauber_ausbau` / then the level rises up to `zauber_stufe_max`, the next cast uses the new parameters, and the cooldown is shortened by `zauber_tempo_prozent` (exposes: upgrades without effect)
  - given `fuehre_aus` with the two spell actions / then the same results (exposes: bots unable to use magic)
  Verify: new tests fail for these reasons; `make lint` green.

### Implementation for User Story 4

- [ ] T026 [US4] Implement `loesung/magie.py` (missions 19–20), the stand-in `magie`,
  `rudersdorf/kern/zauberei.py` and the magic parts of `spiel.py` (`zaubere`, `zauber_ausbau`,
  `zauber_info`, cooldowns in the step, the two actions, spell levels in `zustand`). Turn T025's
  tests green. Verify: `make check` (known red excepted).
- [ ] T027 [US4] Implement the magic presentation, tests first inside this task
  (`tests/ansicht/test_zauberleiste.py`): the spell bar in `hud.py` (icon, key, mana cost, cooldown
  sweep, locked state with its requirement, level and upgrade button in the build phase), the
  mana bar, a targeting cursor showing the radius, and one distinct visual effect per spell in
  `rudersdorf/ansicht/effekte.py` driven by the `zauber` and `glocken` events. Tests: each key
  selects its spell and a click casts it at the cell's pixel; a locked or unready spell shows its
  reason; each spell event creates its effect; drawing with active effects does not raise.
  Verify: `make check` (known red excepted).

**Checkpoint**: the player acts during waves.

---

## Phase 7: User Story 5 - Face a varied, much harder horde (Priority: P2)

**Goal**: special enemies, the 20-wave campaign with bosses, four difficulty levels, five maps,
master upgrades, the endless mode, and a campaign that is winnable but hard

**Independent Test**: play the reference on normal; lose with one tower kind

### Tests for User Story 5

- [ ] T028 [US5] Write `tests/kern/test_sondergegner.py`. Cases (FR-009–FR-011, US5 scenarios 1–2), at least:
  - given a labyrinth and a harpy / then it moves in a straight line from its gate to the village gate, building under it is allowed, the cannon never hits it and the arrow tower does (exposes: flyers walking the maze)
  - given a wounded orc beside a shaman / then it regains life over time, the shaman itself does not (exposes: abilities not wired)
  - given a troll / then it regenerates, and not while it has a burn effect (exposes: burn rule missing)
  - given a slime defeated at a point / then two slimelings appear there with that cell as position and continue to the gate; they pay their own reward (exposes: split enemies restarting at the gate)
  - given a breaker and a tower on its straight route / then it stops beside it, a `abgerissen` event follows after the tower time (palisade: the shorter time), the cell is free, routes are recomputed and it walks on; killing it earlier saves the building (exposes: breakers walking through buildings)
  - given a breaker demolishing a building / then other placements elsewhere are still accepted, its `rest_weg` comes from the empty-map distances, and a building placed on its own cell is demolished next (exposes: breakers blocking all building)
  - given the orc king / then it adds three orcs every six seconds at its own position, a stun does not slow it, and frost slows it to at best factor 0.8 (exposes: bosses frozen in place)
  - given a ghost hit by an arrow / then the `treffer` event is marked `schwach` and the damage is a quarter (exposes: resistances unused)
  Verify: new tests fail for these reasons; `make lint` green.
- [ ] T029 [US5] Write `tests/kern/test_kampagne.py`. Cases (FR-002, FR-007, FR-012–FR-014, US5 scenarios 3–7), at least:
  - given waves 10 and 20 / then the generated list ends with one, respectively two, `orkkoenig`, and the `welle_start` event is marked as boss (exposes: no bosses)
  - given the four difficulty levels / then enemy life, wave budget, starting resources and village life follow `SCHWIERIGKEIT`, and wave life grows by 6 % per wave (exposes: difficulty without effect)
  - given the map `zwei_tore` / then spawns alternate between the gates and each enemy follows the shortest route from its own gate (exposes: one gate unused)
  - given every shipped map / then it loads, passes `pruefe_karte`, and each gate has a route (exposes: broken shipped maps)
  - given victory / when `weiter_endlos` / then the phase is `bauen`, `endlos` is true, wave 21 can start, its budget follows the formula, a boss comes at wave 30, and there is no further victory (exposes: endless mode ending)
  - given a level-2 tower and a smithy below the required level / then `baue_aus` with a master key is false; with the smithy / then true and the values follow that master's `ausbau`; each of the ten master upgrades changes what its row in data-model.md says (burn from the fire bomb, area slow from the ice wind, poison cloud, stun from the thunder strike) (exposes: master upgrades that are only numbers)
  - given the preview before a boss wave / then it counts the boss (exposes: surprise bosses)
  Verify: new tests fail for these reasons; `make lint` green.
- [ ] T030 [US5] Write `tests/kern/test_lauf.py` and the slow `tests/kern/lang_balance.py`, with
  stubs for `rudersdorf/labor/lauf.py` and `rudersdorf/labor/bots.py` (`zufallsbot(sicht)`,
  `referenzbot(sicht)`, `referenzbot_ohne_dorf(sicht)`, `einseitiger_bot(sicht)`, `leerer_bot(sicht)`). Cases (SC-005, SC-006, FR-032), at least:
  - given a bot returning one build action and the wave action / when `spiele` / then the result dictionary has the five keys and counts invalid actions (exposes: runner ignoring the bot)
  - given a bot that never starts the wave / then the runner starts it (exposes: endless build phases)
  - given the same bot and seed twice / then equal results (exposes: nondeterministic laboratory)
  - slow: `referenzbot` wins the campaign on `flusstal` at `leicht` and `normal` for seeds 1–3 (exposes: an unwinnable game)
  - slow: `einseitiger_bot` (arrow towers only, no village, no magic) loses on `normal` for seeds 1–3 (exposes: a game without depth)
  - slow: `leerer_bot` loses before wave 5 on every level (exposes: a game that plays itself)
  - slow: `referenzbot` on `schwer` reaches at least wave 12 for seeds 1–3; `referenzbot_ohne_dorf` (the same rules without village and spell actions) loses on `schwer` for all three seeds (exposes: flat difficulty, a village that does not matter)
  - slow: one campaign at `LABOR_DT` takes less than a twentieth of its simulated time (exposes: a slow core)
  Verify: the fast tests fail for these reasons; the slow file is collected by `make test-lang` and fails there.

### Implementation for User Story 5

- [ ] T031 [US5] Implement the special enemies in `gegner.py` and `spiel.py`: flight, splitting,
  the breaker with its route over the empty map and its demolition timer, boss rules. Turn T028's
  tests green. Verify: `make check` (known red excepted).
- [ ] T032 [US5] Implement the campaign in `wellen.py` and `spiel.py`: boss waves, difficulty
  scaling, alternating gates, `weiter_endlos`, master upgrades with their special effects. Turn
  T029's tests green. Verify: `make check` (known red excepted).
- [ ] T033 [US5] Implement `rudersdorf/labor/lauf.py` and `rudersdorf/labor/bots.py`, then tune
  the numbers in `rudersdorf/daten.py` (numbers only, no keys or shapes) until T030's slow tests
  are green. `referenzbot` is a plain rule list a learner could read: build a winding wall of
  towers along the route, mix tower kinds against the previewed enemies, upgrade, raise the
  village, cast spells when ready. Record the final win rates per level in the evidence.
  Verify: `make check` and `make test-lang` (known red excepted).
- [ ] T034 [US5] Implement the menus, tests first inside this task (`tests/ansicht/test_menue.py`):
  a start scene with map choice (a small picture of each map; only `flusstal` while the `karten`
  capability is open, with its label) and difficulty choice with a description of each level; an
  options scene (sound, speed, full screen) stored in `einstellungen.json` through
  `rudersdorf/einstellungen.py`; the boss announcement; the master-upgrade choice in the tower
  panel; the endless prompt on the victory screen with the best endless wave. Tests: choosing map
  and level starts that match; options survive a restart of `Anwendung` and a damaged options
  file is ignored; the master choice calls `baue_aus` with the chosen key. Verify: `make check`
  (known red excepted).

**Checkpoint**: the campaign is varied and hard.

---

## Phase 8: User Story 6 - See and hear a lively, smooth game (Priority: P2)

**Goal**: polished drawn graphics, effects, sound, and the performance targets

**Independent Test**: play a late wave at speed 4 with the frame-rate overlay; view the preview images

- [ ] T035 [US6] Raise the graphics to the final quality, tests first inside this task
  (`tests/ansicht/test_grafik.py`). `gelaende.py`: varied meadow tiles, rock, animated water with
  banks, swamp, hills, both gate kinds, soft cell hints only while building. `figuren.py`: every
  enemy kind recognisable by silhouette and colour with a walk or flight animation, facing its
  direction, life bar, effect markers (frost, poison, burn, stun), boss larger with a crown;
  every tower kind and level distinct, the head turning to its last target, master upgrades
  marked. `effekte.py`: projectiles per tower kind flying from tower to target, hit sparks, cannon
  blast ring, frost shards, poison bubbles, fire, lightning arcs along the chain, coins and
  floating numbers on kills (weak hits grey), dust on building and demolition, screen shake on
  boss arrival and breaches, capped at 600 live particles. All sprites are cached surfaces.
  `vorschau.py`: `erzeuge_bilder` renders scripted scenes to PNG: `gelaende_<karte>.png` for each
  map, `tuerme.png` (every kind and level), `gegner.png` (every kind), `kirche_1.png` …
  `kirche_5.png`, `dorf_voll.png`, `zauber.png` (every spell effect), `schlacht.png` (a late wave),
  `werkstatt_ersatz.png` (the untouched workshop with labels), `missionstafel.png`.
  Tests: the preview writes every listed file, none uniformly coloured; sprites of different
  kinds and levels differ; each event kind creates its effect; the particle cap holds; drawing
  the same state twice leaves the match's `zustand_hash()` unchanged; the same scripted match
  played through `Anwendung` with a drawn frame after every step and played without any drawing
  ends with the same `zustand_hash()` (FR-036, FR-037, FR-038, SC-007, SC-008).
  Verify: `make check` (known red excepted); `uv run python -m rudersdorf.ansicht.vorschau docs/bilder`.
- [ ] T036 [US6] Implement sound, tests first inside this task (`tests/ansicht/test_ton.py`).
  `rudersdorf/ansicht/ton.py` synthesises short tones with the standard library (shot per tower
  kind, hit, kill, coin, build, sell, upgrade, each spell, bells, wave horn, boss drum, breach,
  victory, defeat) and plays them from the event list; the `M` key and the option switch it; a
  failing mixer start leaves the game silent. Tests: every event kind maps to a sound; the buffers
  are valid 16-bit mono data of the stated length; with the mixer unavailable (simulated) nothing
  raises; the switch silences playback (FR-034–FR-036, US6 scenario 4). Verify: `make check` (known red excepted).
- [ ] T037 [US6] Reach the performance targets. Write `rudersdorf/labor/messung.py` (prints, for
  a fixed scene of 200 enemies and 50 towers on `weites_feld`: mean and worst milliseconds per
  step over 600 steps, and mean and worst milliseconds per drawn frame over 300 frames on an
  off-screen surface) and the slow test `tests/kern/lang_leistung.py` asserting SC-004 with the
  thresholds 4 ms per step and 8 ms per frame on average. Profile with `cProfile`, then optimise
  where the profile points (for example squared distances, a per-cell bucket of enemies for range
  queries inside the engine, cached text surfaces, dirty terrain only on change) without changing
  results: `tests/kern/test_determinismus.py` and all core tests stay green and unchanged. Record
  the figures before and after in the evidence. Verify: `make check`, `make bench`, `make test-lang`
  (known red excepted).

**Checkpoint**: the game looks, sounds and runs well.

---

## Phase 9: User Story 7 - Work like a programmer in the workshop (Priority: P3)

**Goal**: the craft track (missions 21–26), save and load, the laboratory, autopilot

**Independent Test**: `uv run python labor.py --spiele 20 --loesung`; `uv run python pruefen.py --spur E --loesung`

### Tests for User Story 7

- [ ] T038 [US7] Write `tests/missionen/test_m21.py` … `test_m23.py` and `tests/lernen/test_uebung.py`,
  with stubs for `rudersdorf/uebung/schatzkammer.py`, `pruefer.py` and `aufraeum_pruefung.py`.
  Cases (contract missions 21–23, FR-031, US7 scenarios 1–3), at least:
  - M21 given `leeres_raster(3, 2)` / when one cell is changed / then only that cell changed; given a list with adjacent defeated enemies / then `entferne_besiegte` returns all living ones and the input list is unchanged; given two calls of `zaehle_arten` / then the second count does not contain the first's (exposes: the three classic faults)
  - M22 given the module / then the behaviour tests pass on a table of inputs, and each tidiness check of the contract holds (exposes: clean-up that changes results, or no clean-up)
  - M23 given the learner's test class / when `pruefe_tests` runs / then it passes on the correct subject and at least one test fails on each faulty variant (exposes: tests that cannot catch mistakes)
  - checker: given a test class with only the shipped example test / then the report says which variants survive; given the reference tests / then all are caught; given a test that fails on the correct subject / then that is reported first (exposes: a checker that accepts anything)
  - shipped state: on the untouched workshop, mission 21's tests fail with wrong results or ordinary errors, mission 22's behaviour tests pass and its tidiness checks fail, mission 23 reports surviving variants (exposes: craft missions shipped solved)
  Verify: new tests fail for these reasons; `make lint` green.
- [ ] T039 [US7] Write `tests/missionen/test_m24.py` … `test_m26.py`, `tests/kern/test_ersatz_e.py`, `tests/kern/test_speichern.py` and `tests/lernen/test_labor.py`,
  with a stub `labor.py` exposing `main(argv) -> int`. Cases (contract missions 24–26, FR-021, FR-032, US7 scenarios 4–6), at least:
  - M24 given a valid state / then `zu_daten` is JSON-serialisable, has version 2 and buildings sorted by row then column, and `aus_daten(zu_daten(z)) == z`; given a non-dictionary, a wrong version, each missing key, each wrong type of the contract's type list (including a `bool` for a number, a string level in `dorf_stufen`, `stufe` 0 or 4, `meister` as a number), a negative number, two buildings on one cell / then `ValueError` with a German text; `meister` `None` is valid; arguments unchanged (exposes: tuples as JSON keys, silent acceptance)
  - M25 given six results over two levels / then the stated totals, rate, best, mean and per-level blocks; given `[]` / then zeros and `{}` (exposes: division by zero)
  - M26 given `mein_bot` and seeds 1–3 on the `labor` map at `leicht` / then it survives five waves each time, played entirely with the package under test; it returns a list of dictionaries for a view in the build phase and in a wave (exposes: a bot that does nothing)
  - stand-ins: `speichern` refuses with the mission label; `auswertung` leaves the laboratory printing raw rows; `bot` is the random bot
  - given a match in the build phase with towers, village levels and spell levels / when saved and loaded into a new `Spiel` / then `zustand()` is equal, including `endlos` for a match saved in the endless mode; saving during a wave is refused; a damaged file, a file from another map, an unknown tower kind and a level above the maximum are refused with a reason and the running match's `zustand_hash()` is unchanged (exposes: half-loaded matches)
  - given `labor.main` with `--spiele 4 --schwierigkeit leicht,normal --bot referenz --karte labor --loesung` / then exit 0 and one row per level plus a total; an unknown bot, map or level is a usage error (exposes: FR-032 options missing)
  - given `labor.py --spiele 4 --schwierigkeit leicht --loesung` / then exit 0 and a table with wins, rate, best and mean wave; without `--loesung` on the untouched workshop / then the raw rows with the stand-in notice (exposes: laboratory unusable before mission 25)
  - given the autopilot key in an `Anwendung` / then the bot's actions are applied each build phase and second, and the key switches it off again (exposes: autopilot that cannot be stopped)
  Verify: new tests fail for these reasons; `make lint` green.

### Implementation for User Story 7

- [ ] T040 [US7] Implement missions 21–23: `rudersdorf/uebung/schatzkammer.py` (the correct
  subject and the faulty variants as subclasses not visible from `werkstatt/`), `pruefer.py`,
  `aufraeum_pruefung.py`; the shipped faulty or untidy `werkstatt/fehlerjagd.py`,
  `werkstatt/aufraeumen.py`, `werkstatt/meine_tests.py`; their solved counterparts in `loesung/`;
  the registry and `tests/architektur/test_werkstatt.py` extended so the shipped state of 21–23 is
  guarded. Turn T038's tests green. Verify: `make check` (known red excepted).
- [ ] T041 [US7] Implement missions 24–26 in `loesung/schreiber.py` and `loesung/forschung.py`
  (the reference bot of mission 26 is a short, readable rule list, simpler than `referenzbot`),
  the stand-ins `speichern`, `auswertung`, `bot`, `Spiel.speichere` and `Spiel.lade`, `labor.py`,
  and in the presentation the save, load and autopilot keys. Turn T039's tests green.
  Verify: `make check` (known red excepted); `uv run python labor.py --spiele 4 --loesung`.

**Checkpoint**: the craft track works end to end.

---

## Phase 10: User Story 8 - Find one's way as learner and parent (Priority: P3)

**Goal**: German mission documents with fading help, start page, parents' page, extension guide,
open challenges

**Independent Test**: three random mission documents are each enough to solve their mission

### Tests for User Story 8

- [ ] T042 [US8] Write `tests/lernen/test_dokumente.py`. Cases (FR-033, SC-009, SC-010), at least:
  - given each registry entry / then its document file exists and has a section for the mission with the parts: story, "Du übst", "Vertrag", "Beispiele", "Fertig, wenn", at least two `<details>` hints, "Im Spiel", "Denkfrage" (exposes: missing documents or parts)
  - given every code span in the documents that looks like a file path, a `python …` command, a `module.name` reference or a key / then the file exists, the command's script and options exist, the name exists in `werkstatt/`, and the key is one the presentation handles (exposes: documentation that lies)
  - given the start page / then it contains the first three learner commands of quickstart.md in order (install, start the game, test mission 1) and links to every track document, the parents' page, the extension guide and the open challenges, and every link target exists (exposes: dead links)
  - given the track documents in order A to E / then the mean number of worked examples per mission does not rise from A to E (exposes: help that does not fade)
  Verify: new tests fail for these reasons; `make lint` green.

### Implementation for User Story 8

- [ ] T043 [US8] Write `missionen/spur_a_raster.md` and `missionen/spur_b_tuerme.md` (missions
  1–10) in German for a child who knows version 1's topics: per mission the story in Rudersdorf's
  world, what is practised, the exact contract in plain words with a table where it helps, worked
  examples, the done-when line with the test command, two or three hints in `<details>` going from
  a nudge to a near-solution without giving the code, what changes in the game and which stand-in
  disappears, and a thinking question. Each track opens with a short cheat sheet of the new
  Python ideas (nested lists, tuples, sets, `deque`, `min`/`max` with `key`, functions in
  dictionaries). Verify: T042's tests for these missions pass; `make check` (known red excepted).
- [ ] T044 [US8] Write `missionen/spur_c_horde.md` and `missionen/spur_d_dorf_und_magie.md`
  (missions 11–20) to the same standard, with fewer worked examples than tracks A and B, and
  cheat sheets for class hierarchies, composition, `random.Random`, recursion and nested
  dictionaries. The church and the cathedral carry the story of track D.
  Verify: T042's tests for these missions pass; `make check` (known red excepted).
- [ ] T045 [US8] Write `missionen/spur_e_werkstatt.md` (missions 21–26, goals rather than
  recipes; how to read a traceback; what refactoring means; why a test must be able to fail),
  the final `README.md` (start page with the preview images from `docs/bilder/`, install, start,
  first test, keys, the track table, the reference switch, where everything is),
  `docs/FUER-ELTERN.md` (the idea, how to help without solving, what each track teaches, how the
  stand-ins work, troubleshooting), `docs/ERWEITERN.md` (add a tower, an enemy, a spell, a village
  building, a map: which table, which class, which drawing function) and `docs/KNOBELAUFGABEN.md`
  (at least eight open challenges with stars and suggested own tests, among them routing by travel
  time with swamps, a new tower, a new spell, a sixth church stage, a map of his own, a smarter
  bot, waves that adapt to the defence, a measurement of his own code's speed).
  Verify: all of T042's tests pass; `make check`.

**Checkpoint**: the learner can work alone.

---

## Phase 11: Polish

- [ ] T046 Prove "always playable" over all eighteen capabilities in the slow test
  `tests/kern/lang_faehigkeiten.py` (FR-023, FR-024, SC-001, SC-002). For every capability `k` of
  the workbench registry: (a) with only `k` (and what waits for it) forced open on the reference,
  a whole campaign on `flusstal` at `leicht` is played at `LABOR_DT` to victory, with the village
  life set to a million by the test so that all twenty waves, both bosses and the end of the
  match are reached, with the reference bot's actions, at least one village purchase, one spell
  cast and one save and load attempted, without any exception; (b) with everything forced open
  except `k` and its prerequisites, three waves play the same way and the open set is as
  expected; (c) the untouched `werkstatt` plays a whole campaign as in (a) and one normal match
  to its defeat; (d) for each capability, its stand-in's result differs from the reference's on
  one stated input. The outcome may already hold: then record it and close
  green; any failure is fixed in the engine or the stand-in, never in the test's expectation.
  Verify: `make test-lang` (known red excepted).
- [ ] T047 Final verification and hand-over material. Run `make check`, `make test-lang` and
  `make bench` on the final tree and record the results; regenerate `docs/bilder/`; walk through
  `quickstart.md` step by step under the dummy driver and record each step's outcome; check each
  success criterion SC-001 to SC-010 against its test or measurement in a table in the evidence;
  list anything not machine-verified (visual quality, sound quality, fun) for the owner to judge.
  Verify: the three commands are green and the table is complete.

---

## Dependencies & Execution Order

- Phases run in order, and tasks within a phase in the order written. In Phase 3 each test
  task is directly followed by its implementation task; in later phases a story's test tasks
  come first, then its implementation tasks.
- Later stories build on the match core of User Story 1 and the workbench of Phase 2.
- User Story 8 needs every earlier story, because it documents the finished thing.
