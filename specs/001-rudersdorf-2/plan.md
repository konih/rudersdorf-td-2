# Implementation Plan: Rudersdorf 2 · Das Labyrinth

**Branch**: `001-rudersdorf-2` | **Date**: 2026-11-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-rudersdorf-2/spec.md`

## Summary

A grid tower-defense game in Python on pygame-ce with a pure, deterministic simulation core, a
drawn-in-code presentation, a village and magic layer, and a learner workshop of 26 missions
whose unsolved capabilities are replaced by labelled stand-ins. A complete reference (`loesung/`)
mirrors the workshop (`werkstatt/`). Fixed names and signatures: [contracts/werkstatt-api.md](contracts/werkstatt-api.md).
Content tables and shapes: [data-model.md](data-model.md). Decisions: [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.10+ (developed on 3.14)
**Primary Dependencies**: `pygame-ce >= 2.5.6` (runtime); `ruff` (development only)
**Storage**: JSON files in the repository root (`spielstand.json`, `einstellungen.json`, `.fortschritt.json`), all git-ignored
**Testing**: `unittest` (standard library), headless (`SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=dummy`)
**Target Platform**: desktop Linux, Windows, macOS
**Project Type**: single desktop application with a learner workspace
**Performance Goals**: step ≤ 4 ms and frame ≤ 8 ms on average with 200 enemies and 50 towers (SC-004); headless campaign ≥ 20× real time (SC-006)
**Constraints**: no third-party assets; core never imports pygame; deterministic fixed step
**Scale/Scope**: 24 × 16 grid, 6 building kinds, 12 enemy kinds, 8 village lines, 5 spells, 5 maps, 26 missions

## Constitution Check

| Principle | How the plan complies |
| --- | --- |
| I. Learner first | German everywhere outside `specs/`; `werkstatt/` ships unsolved (craft missions 21–23 in their faulty or untidy shipped state, the constitution's exception) and is checked by `tests/architektur/test_werkstatt.py`; `loesung/` mirrors it (parity test); reference only via `--loesung` / `RUDERSDORF_LOESUNG=1` |
| II. Always playable | every engine call into the workshop goes through `Werkbank`; stand-ins in `rudersdorf/ersatz.py`; `tests/kern/test_ersatz_spiel.py` and `tests/kern/lang_faehigkeiten.py` run matches with every capability open, each one open alone and each one solved alone; a stand-in test asserts it differs from the reference result on a stated input |
| III. Pure deterministic core | `tests/architektur/test_schichten.py` forbids the imports; `Spiel.zustand_hash()` compared across runs |
| IV. Tests first | every behaviour story has a test task before its implementation task in `tasks.md` |
| V. Content is data | all tables in `rudersdorf/daten.py`; `tests/kern/test_daten.py` validates shapes and references |
| VI. Simple to read | plain modules, small classes, no decorators with hidden behaviour, no metaclasses |

No violations; the Complexity Tracking table is empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-rudersdorf-2/
├── spec.md  plan.md  research.md  data-model.md  quickstart.md  tasks.md
├── contracts/werkstatt-api.md
├── loop.md  task-prompt.md          # loop state (spec-loop)
├── evidence/                        # one state file per task
└── reviews/                         # review registers and leg reports
```

### Source Code (repository root)

```text
spielen.py              # start the game: [--loesung] [--karte NAME] [--schwierigkeit NAME] [--saat N]
pruefen.py              # learner test runner and mission board
labor.py                # laboratory: headless matches with a bot
werkstatt/              # the learner's workspace (ships unsolved)
│   raster.py  tuerme.py  strategien.py  horde.py  dorf.py  magie.py
│   fehlerjagd.py  aufraeumen.py  meine_tests.py  schreiber.py  forschung.py
loesung/                # the reference: same modules, names and signatures
rudersdorf/
│   fehler.py           # NochOffen, Lernfehler
│   daten.py            # all content tables (no logic beyond constants)
│   missionen.py        # the mission registry
│   werkbank.py         # loads a workshop package, probes capabilities, routes calls
│   ersatz.py           # the labelled stand-ins
│   kern/               # pure simulation — never imports pygame
│   │   karte.py        # Karte: load, validate, cells, gates, blocked set, distance cache
│   │   gegner.py       # Gegner
│   │   bauwerk.py      # Bauwerk and its shot logic
│   │   dorf.py         # Dorf: resources, levels, bonuses
│   │   wellen.py       # budget, life scaling, boss waves, spawn timing
│   │   zauberei.py     # spell book: unlocking, levels, casting through the workbench
│   │   spiel.py        # Spiel: phases, schritt, actions, events, sicht, hash, save/load
│   labor/              # headless tools — never import pygame
│   │   lauf.py         # play one match with a bot; play many
│   │   bots.py         # zufallsbot (stand-in), referenzbot used by balance tests
│   │   messung.py      # performance figures (`make bench`)
│   uebung/             # subjects for the craft missions
│   │   schatzkammer.py pruefer.py aufraeum_pruefung.py
│   ansicht/            # pygame presentation
│       fenster.py      # window, scaling, main loop, input, speed, focus pause
│       szenen.py       # menu, match, options, mission board
│       gelaende.py     # terrain surfaces
│       figuren.py      # enemy and tower sprites
│       dorfbild.py     # village and the five church stages
│       effekte.py      # projectiles, particles, floating text, screen shake
│       hud.py          # top bar, side panel, spell bar, tooltips, labels for stand-ins
│       overlays.py     # distance, range and frame-rate overlays; error panel
│       ton.py          # synthesised sounds
│       vorschau.py     # render scripted scenes to PNG without a window
karten/                 # flusstal.txt zwei_tore.txt felsenmeer.txt weites_feld.txt labor.txt
missionen/              # German mission documents: spur_a_raster.md … spur_e_werkstatt.md
docs/                   # FUER-ELTERN.md ERWEITERN.md KNOBELAUFGABEN.md bilder/
tests/
    architektur/        # test_schichten.py test_werkstatt.py test_paritaet.py
    missionen/          # test_m01.py … test_m26.py (class MissionNN) + helfer.py
    kern/               # engine tests; lang_*.py for whole matches
    ansicht/            # headless presentation smoke tests
    lernen/             # pruefen.py, mission board, documentation checks
```

**Structure Decision**: one project. The dependency direction is
`ansicht → kern → (werkbank → werkstatt | loesung, ersatz) → daten, fehler`; `labor → kern`.
`werkstatt` and `loesung` import only `rudersdorf.daten`, `rudersdorf.fehler`, `rudersdorf.uebung`
(mission 23's base class) and themselves.

## Fixed engine interfaces

Test tasks write stubs with exactly these signatures (bodies `raise NotImplementedError`).

### `rudersdorf/fehler.py`

```python
class NochOffen(NotImplementedError): ...
class Lernfehler(Exception):
    def __init__(self, faehigkeit, datei, zeile, art, text, mission, spur=""): ...
```

### `rudersdorf/werkbank.py`

```python
FAEHIGKEITEN: dict[str, dict]   # key -> {"missionen": [int], "modul": str, "namen": [str]}

class Werkbank:
    def __init__(self, paket: str, gesperrt=()): ...   # "werkstatt" or "loesung"; gesperrt: capabilities forced open (tests)
    paket: str
    def lade_neu(self) -> None: ...              # re-import modules; on failure raise Lernfehler and keep the old ones
    def ist_offen(self, faehigkeit: str) -> bool: ...
    def offene(self) -> list[str]: ...           # open capabilities, registry order
    def wartet_auf(self, faehigkeit: str) -> list[int]: ...   # mission numbers it waits for; [] if none
    def rufe(self, faehigkeit: str, name: str, *args, **kwargs): ...
    def erzeuge(self, faehigkeit: str, klasse: str, *args, **kwargs): ...
    def strategien(self) -> dict: ...            # name -> callable; {"zufall": ...} while open

def waehle_paket(loesung: bool | None = None) -> str: ...   # None: read RUDERSDORF_LOESUNG
```

`rufe` calls the workshop function `name` of the capability's module; on `NochOffen` it marks the
capability open and returns the stand-in's result; on any other exception it raises `Lernfehler`
built from the innermost traceback frame inside the workshop package. `Lernfehler` also carries
the formatted original traceback as `spur` (a string); whoever shows the error prints `spur` to
standard error. When the engine itself finds a returned value unusable (a strategy returning
something that is not a candidate), it raises `Lernfehler` located at the first line of that
workshop function, with `art = "Rückgabewert"`.

Probing (at construction and after `lade_neu`): `PROBEN` in `werkbank.py` maps each capability to
a list of small functions that each call one workshop function, or construct one class and call
each of its mission methods once, with the smallest valid input from the contract's rules. A
probe that raises `NochOffen`, or finds the module or name missing, makes the capability open; any
other exception during a probe is ignored (the capability counts as solved and the error will
surface as a `Lernfehler` during play). There is no time guard: a learner loop that never ends
hangs the program as any Python program would, and the mission documents say how to stop it.
`ABHAENGIG` maps a capability to the capabilities it waits for (contract, *Capabilities and
stand-ins*); a capability with an open prerequisite is open. `erzeuge` does the same for
classes and wraps the instance so that its method calls are routed the same way. While a
capability is open, `rufe` and `erzeuge` go straight to the stand-in.

### `rudersdorf/kern/karte.py`, `gegner.py`, `bauwerk.py`, `dorf.py`

```python
def pruefe_karte(raster) -> None: ...            # raises ValueError with a German reason
class Karte:
    def __init__(self, raster, name="eigene"): ...   # validates with pruefe_karte
    raster: list; name: str; breite: int; hoehe: int; starts: list; ziel: tuple
def lade_karte(name: str, werkbank) -> Karte: ...     # reads karten/<name>.txt through the `karten` capability
def zentrum(zelle) -> tuple: ...                      # pixel centre of a cell

class Gegner:
    def __init__(self, art: str, werkbank, leben_faktor=1.0): ...   # values from daten.GEGNER[art]
class Bauwerk:
    def __init__(self, art: str, zelle, auf_huegel=False): ...      # values from daten.BAUWERKE[art]
class Dorf:
    def __init__(self, schwierigkeit: str): ...
```

`Spiel(kartentext=...)` with a broken text raises `ValueError`. `Spiel(karte=name)` with an unknown
name, or a file that fails validation, uses `flusstal` and says so in `meldung`.

### `rudersdorf/kern/spiel.py`

```python
class Spiel:
    def __init__(self, werkbank, karte="flusstal", schwierigkeit="normal", saat=1, kartentext=None): ...
    phase: str            # "bauen" | "welle" | "sieg" | "verloren"
    welle: int            # number of the last started wave, 0 before the first
    endlos: bool
    karte: Karte
    dorf: Dorf
    bauwerke: dict        # zelle -> Bauwerk
    gegner: list
    meldung: str
    zeit: float           # simulated seconds
    def schritt(self, dt: float) -> None: ...
    def erzeuge_gegner(self, art: str, zelle=None, start=None) -> Gegner: ...   # used for spawning, summoning, splitting, and by tests
    def baue(self, art: str, zelle) -> bool: ...
    def verkaufe(self, zelle) -> bool: ...
    def baue_aus(self, zelle, meister: str | None = None) -> bool: ...
    def setze_strategie(self, zelle, name: str) -> bool: ...
    def starte_welle(self) -> bool: ...
    def weiter_endlos(self) -> bool: ...
    def dorf_ausbau(self, gebaeude: str) -> bool: ...
    def dorf_info(self, gebaeude: str) -> dict: ...   # next level, cost, fehlend: [str], bauplan: [(str, int)] | None
    def zaubere(self, name: str, punkt) -> bool: ...
    def zauber_ausbau(self, name: str) -> bool: ...
    def zauber_info(self) -> dict: ...                 # name -> {"frei", "stufe", "kosten", "rest", "bereit"}
    def vorschau(self) -> dict: ...                    # kind -> count of the next wave
    def abstaende(self) -> dict: ...                   # the distance map in use
    def preis(self, art: str) -> dict: ...             # current price including discounts
    def hole_ereignisse(self) -> list: ...
    def sicht(self) -> dict: ...
    def fuehre_aus(self, aktion: dict) -> bool: ...
    def statistik(self) -> dict: ...                   # {"welle", "besiegt", "gold_verdient"}
    def zustand(self) -> dict: ...                     # the dictionary of mission 24
    def zustand_hash(self) -> str: ...
    def speichere(self, pfad) -> bool: ...
    def lade(self, pfad) -> bool: ...
```

Rules the core tests fix (details in `spec.md` and `data-model.md`):

- Building is allowed in the phases `bauen` and `welle`; village and spell upgrades only in
  `bauen`; saving only in `bauen`; casting only in `welle`.
- One `schritt`: spawn; move enemies; abilities and effects; towers shoot; spell cooldowns and
  mana; bells; collect the defeated (reward, splitting); breaches; breaker demolition; end of
  wave or match. The order is fixed here because the result depends on it.
- A walking enemy moves in pixels towards the centre of `ziel_zelle`; on arrival it asks for the
  next step. Flyers move in a straight line from their gate to the village gate and have
  `zelle = None`. `rest_weg` is `abstand * ZELLE` minus the progress inside the current step for
  walkers and the straight remaining distance for flyers.
- The cells in `besetzt` for the placement rule are the `zelle` and `ziel_zelle` of every walking
  enemy that follows the labyrinth. Flyers and breakers are not in it. A breaker follows its own
  distance map (computed without buildings), its `rest_weg` comes from that map, and while it
  demolishes a building its `ziel_zelle` is its own `zelle`. A building placed on a breaker's
  cell is the next thing it demolishes.
- After `darf_bauen` (or its stand-in) said yes, the engine applies its safety net (contract,
  *Capabilities and stand-ins*) before accepting the placement.
- Before a story is implemented the engine does not call that story's capabilities: village
  (`voraussetzungen`, `boni`, `bauplan`) from T023, `magie` from T026, `speichern`, `auswertung`
  and `bot` from T041. Until then master upgrades are unavailable (smithy level 0).
- All randomness comes from `self.zufall = random.Random(saat)`.
- `Gegner.erleide_schaden(menge, art) -> float` applies the `schadensarten` capability with its own
  `resistenzen`, lowers `leben` (never below 0) and returns the life actually lost. Towers,
  effects and spells always pass the raw amount.
- `fuehre_aus` returns `False` for an action kind whose story is not implemented yet; each story
  adds its own kinds (village: T023, spells: T026).

### `rudersdorf/labor/lauf.py`

```python
def spiele(bot, werkbank, karte="labor", schwierigkeit="leicht", saat=1, wellen=None, dt=LABOR_DT) -> dict: ...
def spiele_viele(bot, werkbank, anzahl, karte, schwierigkeit, saat=1) -> list[dict]: ...
```

`spiele` returns `{"schwierigkeit", "sieg", "welle", "gold", "ungueltig"}`. The bot is called once
per build phase and then every simulated second during a wave; its actions are passed to
`fuehre_aus`; if it does not start the wave within one call, the runner starts it.

### `labor.py`

```python
def main(argv=None) -> int: ...
# --spiele N (default 10) --schwierigkeit NAME[,NAME...] (default leicht) --karte NAME (default labor)
# --bot mein|zufall|referenz (default mein) --saat N (default 1) --loesung
```

It prints one row per difficulty level plus a total (through the `auswertung` capability).

### `rudersdorf/ansicht/`

```python
# fenster.py
def starte(werkbank, karte=None, schwierigkeit=None, saat=None, probelauf=None) -> int: ...   # blocks until the window closes, or for `probelauf` seconds
class Anwendung:
    def __init__(self, werkbank, flaeche=None): ...   # flaeche given: draw there, open no window
    def ereignis(self, ereignis) -> None: ...         # one pygame event
    def aktualisiere(self, sekunden: float) -> None: ...
    def zeichne(self) -> None: ...
# vorschau.py   (also runnable: python -m rudersdorf.ansicht.vorschau ORDNER, always with the reference)
def erzeuge_bilder(ziel_ordner, werkbank) -> list[str]: ...   # file names written
def main(argv=None) -> int: ...

# spielen.py
def main(argv=None) -> int: ...   # --loesung --karte NAME --schwierigkeit NAME --saat N --probelauf SEKUNDEN
```

`--probelauf SEKUNDEN` is a developer option: the game runs that long (auto-starting waves) and
exits with status 0, or 1 if an error panel appeared. `aktualisiere(sekunden)` multiplies the time
by the speed, adds it to a backlog, runs whole steps of `DT` from the backlog, at most 12 per
call, and discards any backlog beyond those 12 steps.

Keys: `1`–`6` choose a building; left click builds or selects; right click or `Esc` cancels;
`A` upgrade, `V` sell, `T` next targeting rule; `Q W E R G` cast the five spells; `N` starts the
next wave (nothing during a wave); space starts the wave in the build phase and pauses or continues
during a wave; `P` pauses or continues; `F` speed; `F1` distances, `F2` ranges, `F3` frame rate; `F5` reload the
workshop; `Tab` mission board; `B` autopilot; `S` / `L` save and load; `M` sound; `F11` full screen.

## Fitness functions (architecture guards)

| Characteristic | Test | Kind |
| --- | --- | --- |
| Layering (no pygame in core, laboratory, workshop, reference; core does not import presentation) | `tests/architektur/test_schichten.py` | triggered |
| Workshop ships unsolved | `tests/architektur/test_werkstatt.py` | triggered |
| Workshop and reference have the same public names and signatures | `tests/architektur/test_paritaet.py` | triggered |
| Data tables are consistent | `tests/kern/test_daten.py` | triggered |
| Determinism | `tests/kern/test_determinismus.py` | triggered |
| Style | `make lint` | triggered |
| Winnability and difficulty | `tests/kern/lang_balance.py` (`make test-lang`) | holistic |
| Performance | `tests/kern/lang_leistung.py` and `make bench` | holistic |

## Phasing

Phases follow the user stories; see `tasks.md`. Each behaviour story has its test task first.
The reference solution of a mission is implemented together with the engine part that uses it,
because the engine tests run against the reference.

## Complexity Tracking

No constitution violations to justify.
