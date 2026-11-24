# Data model: Rudersdorf 2

All content tables live in `rudersdorf/daten.py` as plain dictionaries and lists. Numbers below
are starting values; task T033 (balance) may change numbers but not keys or shapes.

## Geometry

| Constant | Value | Meaning |
| --- | --- | --- |
| `SPALTEN`, `ZEILEN` | 24, 16 | grid size |
| `DORF_SPALTEN` | 6 | rightmost columns are village ground (`D`) |
| `ZELLE` | 40 | pixels per cell |
| `DT` | 1 / 60 | fixed simulation step in seconds |
| `LABOR_DT` | 1 / 20 | step used by the laboratory and slow tests |
| Base resolution | 1280 × 720 | top bar 80 high; map 960 × 640 at (0, 80); side panel 320 wide |

Terrain characters: `.` Wiese, `#` Fels, `~` Wasser, `%` Sumpf, `^` Hügel, `S` Orktor, `Z` Dorftor,
`D` Dorfgrund. `BEGEHBAR = ".%^SZ"`, `BEBAUBAR = ".^"`. Swamp speed factor 0.5. Hill range
factor 1.25.

Map rules checked by the engine (`kern/karte.py: pruefe_karte`): 16 rows of 24 characters; only
known characters; exactly one `Z`; at least one `S`; columns 18–23 are all `D`; no `D` elsewhere;
every `S` has a route to `Z`. Maps: `flusstal` (default, one gate, a river with two fords),
`zwei_tore` (two gates), `felsenmeer` (many rocks, narrow passages), `weites_feld` (almost empty),
`labor` (small open test map used by the laboratory and mission 26; same size, short route).

## Buildings on the grid — `BAUWERKE`

Key → `{"name", "kurz", "kosten": {"gold": n, "stein": n}, "werte": {...}, "ausbau": [stufe2],
"meister": {key: {"name", "kurz", "kosten", "braucht_schmiede": n, "ausbau"}}, "farbe"}`.
`ausbau` dictionaries have the shape mission 10 consumes: value name → `(sign, number)`.

| Key | Name | Cost | Values (level 1) | Role |
| --- | --- | --- | --- | --- |
| `pfeil` | Pfeilturm | 50 gold | schaden 12, art `stich`, reichweite 130, nachladezeit 0.7, trifft_luft | fast single target |
| `kanone` | Kanonenturm | 90 gold | schaden 26, art `wucht`, reichweite 150, nachladezeit 1.9, radius 55, ground only | area |
| `frost` | Frostturm | 70 gold | schaden 4, art `magie`, reichweite 115, nachladezeit 1.1, frost_dauer 2.0, frost_faktor 0.5, trifft_luft | slow |
| `gift` | Giftturm | 80 gold | schaden 2, art `gift`, reichweite 120, nachladezeit 1.4, gift_dauer 4.0, gift_schaden 7, trifft_luft | damage over time |
| `blitz` | Blitzturm | 120 gold, 10 stein | schaden 16, art `magie`, reichweite 125, nachladezeit 1.6, spruenge 3, sprungweite 85, trifft_luft | chain |
| `palisade` | Palisade | 5 gold, 3 stein | none (does not shoot) | blocks only |

Level 2 for every tower: `{"schaden": ("*", 1.6), "reichweite": ("+", 15)}`, cost 80 % of the
purchase price in gold. Master upgrades (level 3), two per tower, each with its own `ausbau`:

| Tower | Master A | Master B |
| --- | --- | --- |
| `pfeil` | Scharfschütze: range ×1.5, damage ×2.2 | Schnellfeuer: reload ×0.45 |
| `kanone` | Mörser: radius ×1.6, range +40 | Brandbombe: adds burn (brand_dauer 3, brand_schaden 10) |
| `frost` | Eiswind: slows all enemies within radius 60 of the target | Tiefkühler: frost_faktor = 0.25, frost_dauer +1.5 |
| `gift` | Seuche: gift_schaden ×2.2 | Giftwolke: poisons all within radius 50 of the target |
| `blitz` | Gewitter: spruenge +4 | Donnerschlag: damage ×2, stuns each hit 0.4 s |

Selling refunds `verkauf_anteil` (base 0.6, raised by the market) of `ausgegeben`, rounded down.
Each building stores `ausgegeben` (gold only; stone is not refunded).

## Enemies — `GEGNER`

Key → `{"name", "leben", "tempo" (pixels/s), "belohnung", "dorfschaden", "preis", "ab_welle",
"boss": bool, "fliegt": bool, "resistenzen": {art: factor}, "faehigkeiten": [(class_name, kwargs)],
"teilt_in": [kind, ...], "bricht": bool, "groesse", "farbe"}`.

| Key | Name | Life | Speed | Price | From wave | Special |
| --- | --- | --- | --- | --- | --- | --- |
| `ork` | Ork | 45 | 48 | 5 | 1 | none |
| `wolf` | Wolfsreiter | 30 | 90 | 6 | 2 | fast |
| `oger` | Oger | 160 | 30 | 16 | 4 | wucht ×0.7 |
| `schildork` | Schildork | 80 | 40 | 12 | 5 | stich ×0.4 |
| `harpyie` | Harpyie | 55 | 70 | 14 | 6 | flies |
| `troll` | Troll | 220 | 26 | 24 | 7 | Regeneration(12) |
| `schamane` | Schamane | 90 | 38 | 22 | 8 | Heiler(radius 90, 14) |
| `schleim` | Schleim | 120 | 34 | 18 | 9 | teilt_in 2 × `schleimling`; gift ×0.5 |
| `schleimling` | Schleimling | 35 | 60 | 4 | never generated | only from splitting |
| `geist` | Geist | 70 | 55 | 20 | 11 | stich ×0.25, wucht ×0.25, magie ×1.5 |
| `brecher` | Brecher | 260 | 28 | 30 | 12 | bricht: walks the route of the empty map and destroys buildings in its way (palisade 2 s, tower 5 s) |
| `orkkoenig` | Orkkönig | 2600 | 20 | boss | 10, 20 | Beschwoerer(6 s, `ork`, 3); ignores stun; frost factor at best 0.8 |

`dorfschaden`: 1 for ork, wolf, schleimling; 2 for schildork, harpyie, schamane, geist, schleim;
3 for oger, brecher; 4 for troll; 20 for the boss.

Damage types: `stich`, `wucht`, `magie`, `gift`, `feuer`.

## Waves and difficulty

`KAMPAGNE_WELLEN = 20`. Budget of wave `n`: `round((18 + 9 * n + 0.9 * n * n) * budget_faktor)`.
Life of every enemy in wave `n`: `leben * leben_faktor * (1 + 0.06 * (n - 1))`. Waves 10 and 20
are the generated wave at 60 % budget plus one `orkkoenig` (two in wave 20) appended at the end.
Endless waves continue the formulas with `n > 20` and a boss every tenth wave.
Spawn interval: `max(0.25, 1.1 - 0.03 * n)` seconds; with several gates enemies alternate.
A wave's list is generated when the previous wave ends (or at match start), so the preview shows it.

`SCHWIERIGKEIT`: key → `{"name", "leben_faktor", "budget_faktor", "start": {"gold", "stein"},
"dorf_leben"}`.

| Key | Life × | Budget × | Start gold / stone | Village life |
| --- | --- | --- | --- | --- |
| `leicht` | 0.75 | 0.8 | 320 / 40 | 30 |
| `normal` | 1.0 | 1.0 | 260 / 30 | 20 |
| `schwer` | 1.3 | 1.25 | 220 / 20 | 15 |
| `albtraum` | 1.7 | 1.5 | 200 / 10 | 10 |

Wave end income: 40 gold + 5 stone + market and quarry bonuses + interest
(`zinsen_prozent` of gold, at most `zinsen_max`).

## Village — `DORFGEBAEUDE`

Shape as in the contract (missions 16–18). Bonus names (all additive):
`turm_schaden_prozent`, `gold_pro_welle`, `zinsen_prozent`, `zinsen_max`, `verkauf_prozent`,
`stein_pro_welle`, `bewohner`, `dorf_leben`, `dorf_ruestung` (reduces each breach by this, at
least 1 remains), `bau_rabatt_prozent`, `zauber_stufe_max`, `zauber_tempo_prozent`,
`mana_pro_sekunde`, `mana_max`, `heilung_pro_welle`, `glocken_intervall` (seconds between bell strokes; 0 or less means no bells; church level 4
gives +40 and level 5 gives −15, so the sum is 40, then 25), `glocken_dauer`, `schmiede_stufe` (unlocks master
upgrades). Spells are unlocked only by `ZAUBER[name]["frei_ab_kirche"]`, not by a bonus.

| Key | Line | Levels (names) | Main bonuses | Notable requirements |
| --- | --- | --- | --- | --- |
| `kirche` | Kirche | Holzkapelle, Dorfkirche, Basilika, Kathedrale, Kathedrale mit Türmen | mana, heal per wave, unlocks spells (1: Segen, 2: Feuerball and Eissturm, 3: Blitzschlag, 4: Glockenschlag and bells every 40 s, 5: bells every 25 s, doubled mana rate) | 3: steinbruch 1, haeuser 1; 4: bauhuette 2, steinbruch 2, haeuser 3; 5: bauhuette 3, bibliothek 2, haeuser 4 |
| `schmiede` | Schmiede | 3 | tower damage +10 % per level, `schmiede_stufe` | 2: steinbruch 1 |
| `markt` | Markt | 4 | gold per wave, interest, selling share | 3: haeuser 2 |
| `steinbruch` | Steinbruch | 3 | stone per wave | none |
| `haeuser` | Wohnhäuser | 5 | +12 bewohner per level, small gold per wave | 4: markt 2 |
| `mauer` | Stadtmauer | 4 | village life +6 per level, armour from level 3 | 2: steinbruch 1; 4: bauhuette 1 |
| `bauhuette` | Bauhütte | 3 | building prices −8 % per level (grid and village) | 1: steinbruch 1; 3: kirche 3 |
| `bibliothek` | Bibliothek | 3 | `zauber_stufe_max` +1 per level (base 1), spell cooldown −10 % per level | 1: kirche 2; 3: kirche 4 |

Population starts at 12 and is shown in the game; requirements never refer to it directly. Village state: `stufen` (dict), `vorraete` (`gold`, `stein`, `mana`),
`leben`, `max_leben`, `bewohner`, `boni` (the summed dictionary, recomputed after each purchase).

## Spells — `ZAUBER`

Key → `{"name", "klasse", "frei_ab_kirche": n, "braucht_ziel": bool, "ausbau_kosten": [{...}, {...}],
"stufen": [params_1, params_2, params_3]}`; `params_n` are the keyword arguments of the class.

| Key | Class | Church | Level 1 (cost / cooldown / effect) | Upgrades |
| --- | --- | --- | --- | --- |
| `segen` | `Segen` | 1 | 30 mana / 25 s / heal 3 | heal 5, 8 |
| `feuerball` | `Feuerball` | 2 | 40 / 12 s / radius 70, damage 60, no burn | damage 100 + burn 3 s × 12; radius 95, damage 150, burn 4 s × 20 |
| `eissturm` | `Eissturm` | 2 | 35 / 18 s / radius 100, 4 s, factor 0.4 | radius 130; 6 s, factor 0.25 |
| `blitzschlag` | `Blitzschlag` | 3 | 50 / 15 s / damage 220, 0 jumps | damage 320, 2 jumps; damage 480, 4 jumps |
| `glockenschlag` | `Glockenschlag` | 4 | 80 / 60 s / stun 2.5 s | 3.5 s; 5 s |

## Engine entities (`rudersdorf/kern/`)

- **`Gegner`**: `art`, `name`, `leben`, `max_leben`, `tempo`, `x`, `y`, `zelle`, `ziel_zelle`,
  `rest_weg`, `effekte`, `faehigkeiten`, `fliegt`, `ist_boss`, `resistenzen`, `belohnung`,
  `dorfschaden`, `bricht`, `abriss_rest`; methods `erleide_schaden(menge, art)`, `heile(menge)`,
  `ist_besiegt()`.
- **`Bauwerk`**: `art`, `zelle`, `x`, `y`, `stufe`, `meister`, `strategie`, `werte` (dict),
  `ausgegeben`, `abklingzeit`, `winkel` (for drawing only, set by the core as the last aim).
- **`Dorf`**: see *Village*; methods `heile(menge) -> int`, `erleide_schaden(menge)`,
  `kann_bezahlen(kosten)`, `bezahle(kosten) -> bool`.
- **`Spiel`**: the match; public interface in `plan.md`.
- **Events** (`spiel.ereignisse`, a list of dictionaries with `"art"` and data, appended by the
  core and removed by whoever reads them through `hole_ereignisse()`): `schuss` (von, nach,
  turm_art), `treffer` (punkt, menge, schadensart, schwach), `tod` (punkt, gegner_art, belohnung),
  `durchbruch` (schaden), `gebaut`, `verkauft`, `ausgebaut`, `abgerissen` (zelle), `zauber` (name,
  punkt, wirkung), `glocken`, `welle_start` (nummer, boss), `welle_ende` (nummer, einkommen),
  `dorf_ausbau` (gebaeude, stufe), `sieg`, `niederlage`, `meldung` (text).

## Bot view and bot actions (missions 25–26, autopilot, laboratory)

`Spiel.sicht()` returns a new plain dictionary (no engine objects):

```text
{"phase": str, "welle": int, "wellen_gesamt": int, "endlos": bool, "raster": list[list[str]],
 "starts": [zelle], "ziel": zelle, "abstaende": {zelle: int},
 "vorraete": {"gold", "stein", "mana"}, "dorf_leben": int, "dorf_max_leben": int,
 "dorf_stufen": {key: int}, "bauwerke": {zelle: {"art", "stufe", "strategie"}},
 "gegner": [{"art", "leben", "x", "y", "zelle", "rest_weg", "fliegt"}],
 "vorschau": {kind: count}, "preise": {building_key: {"gold", "stein"}},
 "zauber": {name: {"bereit": bool, "kosten": int}}}
```

`Spiel.fuehre_aus(aktion) -> bool` accepts `{"aktion": "baue", "art", "zelle"}`,
`{"aktion": "ausbau", "zelle", "meister": key | None}`, `{"aktion": "verkaufe", "zelle"}`,
`{"aktion": "strategie", "zelle", "name"}`, `{"aktion": "dorf", "gebaeude"}`,
`{"aktion": "zauber", "name", "punkt"}`, `{"aktion": "zauber_ausbau", "name"}`,
`{"aktion": "welle"}`. Anything malformed or not allowed returns `False` and changes nothing.

## Mission registry — `rudersdorf/missionen.py`

`MISSIONEN`: list of dictionaries `{"nummer", "spur" ("A".."E"), "titel", "modul", "namen":
[public names], "faehigkeit": key | None, "braucht": [numbers of missions of other capabilities it builds on], "testklasse": "tests.missionen.test_mNN.MissionNN",
"dokument": "missionen/spur_x.md#anchor", "sterne": 1..3}`. Single source for the test runner,
the mission board, the stand-in labels and the documentation checks.

## Files written at run time (all git-ignored, all in the repository root)

`spielstand.json` (mission 24 format), `einstellungen.json` (sound, speed, full screen, last map
and difficulty, best endless wave), `.fortschritt.json` (written by `pruefen.py`: mission number →
`"geloest" | "begonnen" | "offen"`, where *begonnen* means at least one test passes or a test
fails with something other than `NochOffen`).
