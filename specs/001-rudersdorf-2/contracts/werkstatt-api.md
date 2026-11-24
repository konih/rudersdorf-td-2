# Contract: the workshop API (missions 1–26)

This file fixes every name and signature the learner implements in `werkstatt/` and the reference
implements in `loesung/`. Both packages have the same modules, names and signatures. Tests and
engine code rely on exactly these. Rules listed here are the behaviour the mission tests check.

## Conventions

- A **cell** (`zelle`) is a tuple `(spalte, zeile)`, both 0-based integers; `spalte` grows to the
  right, `zeile` downwards. A **grid** (`raster`) is `list[list[str]]` indexed
  `raster[zeile][spalte]`. `breite = len(raster[0])`, `hoehe = len(raster)`.
- A **point** (`punkt`, `position`) is a tuple `(x, y)` of floats in map pixels. One cell is
  `ZELLE = 40` pixels; the centre of cell `(s, z)` is `(s * 40 + 20, z * 40 + 20)`.
- Terrain characters and the sets `BEGEHBAR = ".%^SZ"` and `BEBAUBAR = ".^"` come from
  `rudersdorf.daten`. Workshop modules may import `rudersdorf.daten` and `rudersdorf.fehler`
  and each other with relative imports (`from .horde import Frost`), nothing else from the engine.
- `rudersdorf.fehler.NochOffen` is a subclass of `NotImplementedError`. Every mission body in
  `werkstatt/` is `raise NochOffen("Mission N: <Titel>")`.
- Enemies passed to workshop functions are duck-typed objects with at least: `leben`, `max_leben`,
  `x`, `y`, `rest_weg` (float, remaining distance to the village gate; smaller is further ahead),
  `effekte` (list), `fliegt` (bool), `ist_boss` (bool), and the methods
  `erleide_schaden(menge, art)` and `heile(menge)`. `erleide_schaden` takes the raw amount: the
  enemy itself applies its resistances (through mission 11's function) and never goes below 0
  life. Workshop code never multiplies by a resistance itself, except in mission 11. Tests use a small stand-alone test double with
  exactly these members; the engine's `Gegner` has them too.
- "Living" means `leben > 0`. Distances are Euclidean on `(x, y)`; "within r" means `<= r`.
- Unless stated, functions do not modify their arguments and ties keep the earlier list element.

## Track A · Das Raster — `raster.py`

| M | Name | Signature |
| --- | --- | --- |
| 1 | Die Karte lesen | `lies_karte(text: str) -> list[list[str]]`, `finde(raster, zeichen: str) -> list[tuple[int, int]]` |
| 2 | Nachbarn | `nachbarn(zelle, breite: int, hoehe: int) -> list[tuple[int, int]]`, `ist_begehbar(raster, zelle, gesperrt: set) -> bool` |
| 3 | Der kürzeste Weg | `abstandskarte(raster, ziel, gesperrt: set) -> dict[tuple[int, int], int]` |
| 4 | Dem Weg folgen | `naechster_schritt(abstaende: dict, zelle, breite: int, hoehe: int) -> tuple[int, int] \| None` |
| 5 | Nicht einmauern! | `darf_bauen(raster, zelle, gesperrt: set, starts: list, ziel, besetzt: set) -> bool` |

Rules:

- `lies_karte`: split `text` into lines; ignore lines that are empty after removing trailing
  whitespace; each remaining line (trailing whitespace removed) becomes a list of its characters.
  Raise `ValueError` if no line remains or the rows differ in length. It does not judge characters.
- `finde`: all cells whose character equals `zeichen`, row by row from the top, left to right
  within a row. Empty list if none.
- `nachbarn`: the up to four cells above, right, below, left, in exactly that order, leaving out
  those outside `0 <= spalte < breite`, `0 <= zeile < hoehe`.
- `ist_begehbar`: `False` outside the grid; otherwise `True` exactly if the character is in
  `BEGEHBAR` and the cell is not in `gesperrt`.
- `abstandskarte`: breadth-first search from `ziel`. Result maps every cell reachable from `ziel`
  over walkable cells to its number of steps; `ziel` itself maps to `0`. Unreachable and
  non-walkable cells are absent. `gesperrt` is not modified.
- `naechster_schritt`: `None` if `zelle` is not in `abstaende` or its distance is `0`. Otherwise
  the neighbour (in `nachbarn` order) that is in `abstaende` with the smallest distance, provided
  that distance is smaller than the cell's own; first one wins ties; `None` if there is none.
- `darf_bauen`: `False` if `zelle` is outside the grid, its character is not in `BEBAUBAR`, it is
  in `gesperrt`, or it is in `besetzt`. Otherwise build a new set `gesperrt | {zelle}`, compute
  `abstandskarte`, and return `True` exactly if every cell in `starts` and every cell in `besetzt`
  is in the result. `gesperrt` and `besetzt` are not modified.

## Track B · Die Türme — `tuerme.py`, `strategien.py`

| M | Name | Signature |
| --- | --- | --- |
| 6 | Wer ist in Reichweite? | `tuerme.in_reichweite(position, reichweite: float, gegner: list) -> list` |
| 7 | Zielstrategien | `strategien.erster(kandidaten, turm)`, `letzter`, `staerkster`, `schwaechster`, `naechster` (same parameters), and the dictionary `strategien.STRATEGIEN` |
| 8 | Deine eigene Strategie | at least one further entry in `STRATEGIEN` |
| 9 | Der Kettenblitz | `tuerme.kettenblitz(start, gegner: list, spruenge: int, sprungweite: float) -> list` |
| 10 | Die Turmschmiede | `tuerme.wende_ausbau_an(werte: dict, ausbau: dict) -> dict` |

Rules:

- `in_reichweite`: new list of the living enemies within `reichweite` of `position`, in their
  original order.
- A strategy takes `kandidaten` (a list of living enemies, possibly empty) and `turm` (an object
  with `x`, `y`) and returns one element of `kandidaten`, or `None` when the list is empty.
  `erster`: smallest `rest_weg`. `letzter`: largest `rest_weg`. `staerkster`: largest `leben`.
  `schwaechster`: smallest `leben`. `naechster`: smallest distance to the tower.
- `STRATEGIEN` maps the names `"erster"`, `"letzter"`, `"staerkster"`, `"schwaechster"`,
  `"naechster"` to those functions. In `werkstatt/` the dictionary ships with these five keys
  bound to the unsolved functions.
- Mission 8's test reports "still open" (it raises `NochOffen` itself) while `STRATEGIEN` has only
  the five standard keys. It is solved when `STRATEGIEN` has at least one more key whose function follows the
  strategy contract on the test's candidate lists (returns a candidate, or `None` for an empty
  list) and differs from each of the five standard strategies on at least one of them. The
  reference adds `"gefaehrlichster"`: among the candidates within the smallest 25 % of `rest_weg`
  range the one with the most `leben` — any documented own rule is acceptable.
- `kettenblitz`: returns the hit order, starting with `[start]`. Up to `spruenge` times, append
  the living enemy not yet in the list that is nearest to the last one and within `sprungweite`
  of it; stop early when there is none. `start` is included even though it is given.
- `wende_ausbau_an`: returns a new dictionary: a copy of `werte` in which, for each key of
  `ausbau`, the value is changed by the pair `(zeichen, zahl)`: `"+"` adds, `"*"` multiplies,
  `"="` replaces (and may add a new key). Raise `ValueError` for any other sign, and for `"+"` or
  `"*"` on a key missing from `werte`. `werte` is not modified.

## Track C · Die Horde — `horde.py`

| M | Name | Signature |
| --- | --- | --- |
| 11 | Schadensarten | `berechne_schaden(schaden: float, art: str, resistenzen: dict) -> float` |
| 12 | Effekte | classes `Effekt`, `Frost(Effekt)`, `Gift(Effekt)`, `Brand(Gift)`, `Betaeubung(Effekt)` |
| 13 | Die Effektliste | `fuege_effekt_hinzu(effekte: list, neu) -> None`, `gesamt_tempo_faktor(effekte: list) -> float`, `raeume_effekte_auf(effekte: list) -> list` |
| 14 | Besondere Fähigkeiten | classes `Regeneration`, `Heiler`, `Beschwoerer` |
| 15 | Die Wellenschmiede | `erzeuge_welle(nummer: int, budget: int, katalog: dict, zufall) -> list[str]` |

Rules:

- `berechne_schaden`: `0` if `schaden <= 0`; otherwise `schaden * resistenzen.get(art, 1.0)`.
- `Effekt.__init__(self, dauer)`: sets `self.dauer = dauer`, `self.rest = dauer`. Class attribute
  `name = "effekt"`. `tick(self, gegner, sekunden)`: lowers `rest` by `sekunden`, never below 0;
  negative `sekunden` changes nothing. `ist_vorbei(self) -> bool`: `rest <= 0`.
  `tempo_faktor(self) -> float`: `1.0`.
- `Frost.__init__(self, dauer, faktor)`, `name = "frost"`; `tempo_faktor` returns `faktor` while
  not over, else `1.0`.
- `Gift.__init__(self, dauer, schaden_pro_sekunde)`, `name = "gift"`, class attribute
  `schadensart = "gift"`. `tick`: first calls
  `gegner.erleide_schaden(schaden_pro_sekunde * min(sekunden, rest), self.schadensart)` when that
  amount is positive, then the base `tick`.
- `Brand(Gift)`: `name = "brand"`, `schadensart = "feuer"`; nothing else changes.
- `Betaeubung.__init__(self, dauer)`, `name = "betaeubung"`; `tempo_faktor` returns `0.0` while
  not over, else `1.0`.
- `fuege_effekt_hinzu`: if `effekte` holds an effect with the same `name`, replace it by `neu`
  when `neu.rest >= ` its `rest`, otherwise keep the old one; if none, append `neu`.
- `gesamt_tempo_faktor`: the smallest `tempo_faktor()` of all effects that are not over; `1.0`
  for none.
- `raeume_effekte_auf`: new list without the effects that are over, order kept.
- Abilities share the method `aktualisiere(self, traeger, alle: list, sekunden) -> list[str]`,
  which returns the kinds of enemies to summon now (usually `[]`).
  `Regeneration.__init__(self, pro_sekunde)`: heals `traeger` by `pro_sekunde * sekunden` through
  `traeger.heile(...)` if it is living and has no effect named `"brand"` that is not over.
  `Heiler.__init__(self, radius, pro_sekunde)`: if `traeger` is living, heals every other living
  enemy in `alle` within `radius` of it by `pro_sekunde * sekunden`; never itself.
  `Beschwoerer.__init__(self, intervall, art, anzahl=1)`: keeps `self.rest = intervall`; each call
  lowers `rest` by `sekunden`; when it reaches 0 or less and `traeger` is living, it returns
  `[art] * anzahl` and adds `intervall` to `rest`; otherwise `[]`.
- `erzeuge_welle`: `katalog` maps kind → dictionary with `"preis"` (int > 0), `"ab_welle"` (int)
  and `"boss"` (bool). Start with `rest = budget` and an empty list. Repeat: the candidates are
  the non-boss kinds with `ab_welle <= nummer` and `preis <= rest`, sorted by name; if there are
  none, stop; choose one with `zufall.choice(kandidaten)`, append it, subtract its price.
  `zufall` is a `random.Random`. Tests check the properties (only unlocked non-boss kinds, total
  price `<= budget`, nothing affordable left, same seed gives the same wave), not one sequence.

## Track D · Dorf und Magie — `dorf.py`, `magie.py`

| M | Name | Signature |
| --- | --- | --- |
| 16 | Was fehlt noch? | `dorf.fehlende_voraussetzungen(braucht: dict, stufen: dict) -> list[str]` |
| 17 | Die Kraft des Dorfes | `dorf.sammle_boni(stufen: dict, katalog: dict) -> dict` |
| 18 | Der Bauplan | `dorf.bauplan(gebaeude: str, stufe: int, stufen: dict, katalog: dict) -> list[tuple[str, int]]` |
| 19 | Mana und Abklingzeit | class `magie.Zauber` |
| 20 | Das Zauberbuch | classes `magie.Feuerball`, `Eissturm`, `Blitzschlag`, `Segen`, `Glockenschlag` |

Data shape: `katalog` (the engine passes `daten.DORFGEBAEUDE`) maps a building key to
`{"name": str, "stufen": [stufe_1, stufe_2, ...]}`; each `stufe_n` is
`{"name": str, "kosten": dict, "braucht": dict, "boni": dict}`. `braucht` maps a building key to
the minimum level (population is expressed through the level of `haeuser`; there is no other
kind of requirement). `stufen` maps building keys to the current level; a missing key means level 0.

Rules:

- `fehlende_voraussetzungen`: one text `"<key> Stufe <n>"` per unmet entry of `braucht`, in the
  order of sorted keys. Empty list if all are met.
- `sammle_boni`: adds up, over every building in `stufen` and every level from 1 to its current
  level, all entries of that level's `boni`. Returns a new dictionary bonus name → sum. Buildings
  at level 0 and keys missing from `katalog` contribute nothing.
- `bauplan`: the ordered list of `(gebaeude, stufe)` purchases still needed to reach `stufe` of
  `gebaeude`. The order is fixed by this procedure, on a private copy of `stufen`: for each level
  `n` from the building's current level + 1 up to `stufe`, first, for each key of that level's
  `braucht` in sorted order whose required level is above the copy's level, insert the plan for
  that requirement (recursively, by the same procedure); then append `(gebaeude, n)` and record
  level `n` in the copy. Purchases already covered are therefore left out and nothing appears
  twice. Example: `a` level 1 needs nothing, `a` level 2 needs `b` 1, `b` 1 needs `c` 1, nothing
  built: `[("a", 1), ("c", 1), ("b", 1), ("a", 2)]`. Buying the list in order always satisfies
  mission 16's check at every step. The data has no cycles. `stufen` is not modified.
- `Zauber.__init__(self, name, kosten, abklingzeit)`: stores them and sets `self.rest = 0.0`.
  `bereit(self, mana) -> bool`: `rest <= 0` and `mana >= kosten`.
  `tick(self, sekunden)`: lowers `rest`, never below 0.
  `wirke(self, punkt, gegner: list, dorf) -> int`: in the base class raises `NotImplementedError`;
  subclasses return the number of enemies affected (for `Segen`: the life points healed).
  `zaubere(self, mana, punkt, gegner, dorf) -> float`: if not `bereit(mana)`, returns `mana`
  unchanged and does nothing else; otherwise sets `rest = abklingzeit`, calls `wirke`, stores its
  result in `self.letzte_wirkung` and returns `mana - kosten`.
- Spell subclasses call `super().__init__` with their fixed `name` and take keyword parameters
  from `daten.ZAUBER[name]["stufen"][level - 1]`:
  `Feuerball(kosten, abklingzeit, radius, schaden, brand_dauer, brand_schaden)`: every living
  enemy within `radius` of `punkt` takes `schaden` of type `"feuer"`; if `brand_dauer > 0`, each
  also gets `Brand(brand_dauer, brand_schaden)` through `fuege_effekt_hinzu`.
  `Eissturm(kosten, abklingzeit, radius, dauer, faktor)`: every living enemy within `radius` gets
  `Frost(dauer, faktor)`.
  `Blitzschlag(kosten, abklingzeit, schaden, spruenge, sprungweite)`: the living enemy nearest to
  `punkt` within 120 pixels is the start of a `kettenblitz`; each enemy in the chain takes
  `schaden` of type `"magie"`. Returns `0` if there is no start.
  `Segen(kosten, abklingzeit, heilung)`: calls `dorf.heile(heilung)` and returns what it returns.
  Mission 20 builds on missions 9, 12 and 13 (`kettenblitz`, the effect classes,
  `fuege_effekt_hinzu`), which it imports with relative imports. Its tests report "still open"
  with a pointer to those missions while they are unsolved.
  `Glockenschlag(kosten, abklingzeit, dauer)`: every living enemy with `ist_boss == False` gets
  `Betaeubung(dauer)`.
  `dorf` here is a duck-typed object with `heile(menge) -> int` (life actually restored).

## Track E · Die Werkstatt — `fehlerjagd.py`, `aufraeumen.py`, `meine_tests.py`, `schreiber.py`, `forschung.py`

| M | Name | What the learner changes |
| --- | --- | --- |
| 21 | Fehlerjagd | fixes three prepared faulty functions in `fehlerjagd.py` |
| 22 | Aufräumen | tidies `aufraeumen.py` without changing behaviour |
| 23 | Eigene Tests | writes test methods in `meine_tests.py` |
| 24 | Der Dorfschreiber | `schreiber.zu_daten(zustand: dict) -> dict`, `schreiber.aus_daten(daten) -> dict` |
| 25 | Das Labor | `forschung.auswertung(ergebnisse: list[dict]) -> dict` |
| 26 | Der Bot | `forschung.mein_bot(sicht: dict) -> list[dict]` |

Missions 21–23 do not raise `NochOffen`; they ship in a deliberately faulty or untidy state
  (the constitution's stated exception).

- **21** `fehlerjagd.py` ships three functions, each with one fault, each fault a classic:
  `leeres_raster(breite, hoehe, zeichen=".")` (must return independent rows; ships with aliased
  rows), `entferne_besiegte(gegner)` (must return the list of living enemies and leave the input
  list unchanged; ships removing from the list while iterating over it),
  `zaehle_arten(arten, zaehler=None)` (must return a fresh count per call; ships with a mutable
  default argument). The reference file contains the fixed functions.
- **22** `aufraeumen.py` ships a working but untidy module. A tower is a dictionary
  `{"x", "y", "auf_huegel"}`, an enemy a dictionary `{"x", "y"}`. Public functions, whose
  behaviour must not change: `turm_trifft(turm, gegner) -> bool` (distance at most the tower's
  range, which is 120, times 1.25 on a hill); `anzahl_in_reichweite(turm, gegner_liste) -> int`;
  `naechster_gegner(turm, gegner_liste)` (the nearest enemy, the earlier on a tie, `None` for an
  empty list, range does not matter); `ist_ueberlastet(turm, gegner_liste) -> bool` (more than
  five enemies in range). As shipped, the distance is computed with `hypot` in three functions,
  booleans are returned through `if`/`else` pairs, and 120, 1.25 and 5 appear as bare numbers.
  Behaviour tests pass as shipped and must keep passing. Tidiness checks, done on the syntax tree
  by `rudersdorf.uebung.aufraeum_pruefung.pruefe(quelltext) -> list[str]` (German texts of the
  unmet checks, empty when tidy): (a) a function `abstand(a, b)` exists; (b) a call of `hypot` or
  `sqrt`, or a power with exponent `0.5`, occurs inside exactly one function; (c) no `if`
  statement has `return True` in one branch and `return False` in the other as their only
  statements; (d) module-level names `REICHWEITE_GRUND`, `BONUS_HUEGEL` and `MAX_GEGNER` are
  assigned, and the numbers 120, 1.25 and 5 occur nowhere else in the module; (e) no function has
  more than 15 statement nodes in its body, counted recursively.
- **23** The subject is `rudersdorf.uebung.schatzkammer.Schatzkammer` with the documented rules:
  `__init__(self, gold=0)`; `einzahlen(menge)` adds a positive amount and raises `ValueError`
  otherwise; `auszahlen(menge)` removes a positive amount not above the balance, returns it, and
  raises `ValueError` otherwise leaving the balance unchanged; `zinsen(prozent)` adds
  `int(gold * prozent / 100)`, at most 50, and returns the amount added. `meine_tests.py` ships a
  `unittest.TestCase` with one example test. The checker
  (`rudersdorf.uebung.pruefer.pruefe_tests(testklasse) -> dict`) runs the learner's tests against
  the correct class and at least four faulty variants (accepts negative deposits; allows
  overdrawing; changes the balance before raising; no cap on interest). Solved when the tests pass
  on the correct class and at least one test fails on every variant. The learner's class
  `MeineTests` extends `rudersdorf.uebung.pruefer.KammerTest` (a `unittest.TestCase`) and reaches
  the subject only through `self.neue_kammer(gold=0)`. `pruefe_tests` returns
  `{"korrekt_bestanden": bool, "fehler_auf_korrekt": [test names], "varianten": {variant name:
  caught (bool)}, "geloest": bool}`.
- **24** `zustand` is a dictionary with the keys `karte` (str), `schwierigkeit` (str), `saat`
  (int), `welle` (int), `endlos` (bool), `vorraete` (dict str → number), `dorf_leben` (int), `dorf_stufen` (dict),
  `zauber_stufen` (dict), `bauwerke` (dict cell → `{"art", "stufe", "meister", "strategie",
  "ausgegeben"}`). `zu_daten` returns a JSON-compatible dictionary with `"version": 2`, the plain
  entries copied, and `bauwerke` as a list of dictionaries with `"spalte"`, `"zeile"` and the five
  fields, sorted by `(zeile, spalte)`. `aus_daten` is the inverse and returns a `zustand`
  dictionary; it raises `ValueError` with a German message when `daten` is not a dictionary, the
  version is not 2, a key is missing, a type is wrong, a number is negative, or two buildings
  share a cell. `aus_daten(zu_daten(z)) == z` for every valid `z`. Neither modifies its argument.
- **25** Each result is `{"schwierigkeit": str, "sieg": bool, "welle": int, "gold": int}`.
  `auswertung` returns `{"spiele": n, "siege": k, "siegquote": k / n, "beste_welle": max,
  "mittlere_welle": mean, "nach_schwierigkeit": {name: {the same five keys}}}`; for an empty list
  all numbers are `0` and `nach_schwierigkeit` is `{}`.
- **26** `sicht` is the dictionary described in `data-model.md` (*Bot view*). `mein_bot` returns a
  list of action dictionaries (*Bot actions*). Solved when the bot survives five waves on the
  laboratory map at the easy level for three fixed seeds. The test plays with the package under
  test for everything (the learner's own workshop, stand-ins included, or the reference when the
  reference is selected); it never mixes in the reference. The registry therefore names missions
  3, 4, 5, 6 and 7 as prerequisites of mission 26, and the mission document gives a starting
  skeleton for the bot.

## Capabilities and stand-ins

The engine uses workshop code only through capabilities. A capability is *open* when any of its
functions raises `NochOffen`, or when a module or name it needs is missing; then its stand-in
(`rudersdorf/ersatz.py`) is used and labelled. A capability whose missions name prerequisites is
also treated as open (label: "wartet auf Mission …") while a prerequisite capability is open:
`magie` waits for `effekte` and `kettenblitz`; `bauregel` waits for `wegfindung`; `bot` waits for
`wegfindung`, `bauregel`, `reichweite` and `strategien`.

| Capability | Missions | Stand-in (visibly weaker, never the real rule) |
| --- | --- | --- |
| `karten` | 1 | only the built-in map `flusstal` can be chosen |
| `wegfindung` | 2, 3, 4 | "ghost walk": distance is the Manhattan distance ignoring terrain and buildings; enemies walk through everything |
| `bauregel` | 5 | a building is refused next to (including diagonally) any other building, so no wall can form |
| `reichweite` | 6 | "tunnel vision": a tower sees only enemies in its own cell row or column within range |
| `strategien` | 7 (8 adds entries) | a random candidate; the rule menu shows only "Zufall" |
| `kettenblitz` | 9 | the lightning tower and the lightning spell hit only the first target |
| `ausbau` | 10 | towers cannot be upgraded |
| `schadensarten` | 11 | every multiplier counts as 1 |
| `effekte` | 12, 13 | effects do nothing: no slow, poison, burn or stun |
| `faehigkeiten` | 14 | trolls do not regenerate, shamans do not heal, the boss summons nothing |
| `wellen` | 15 | every wave is orcs only, `budget // price` of them |
| `voraussetzungen` | 16 | only level 1 of each village building can be bought |
| `boni` | 17 | only the bonuses of each building's first level count |
| `bauplan` | 18 | the panel shows "Bauplan unbekannt" |
| `magie` | 19, 20 | no spells can be cast; the spell bar is locked |
| `speichern` | 24 | saving and loading are switched off |
| `auswertung` | 25 | the laboratory prints the raw result rows only |
| `bot` | 26 | autopilot and the laboratory use a random bot |

Missions 21–23 have no capability; their state shows only on the mission board.
