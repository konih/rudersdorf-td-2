# Loop — 001-rudersdorf-2

Repo: `/home/koni/Projects/rudersdorf-td-2` · Branch: `001-rudersdorf-2` · Base: `main` · Started: 2026-11-24 · Reviewers: two-model duo
Next: stage L — dispatch the task `task.sh next` names
Budget: paid review legs 3/14 (B reserve 3) · active hours 0/30 (sessions: 2026-11-24 start–) · source: set by the orchestrator at orient (default is claude=12, hours=8; raised because the feature has 46 tasks)

Budget arithmetic, in paid review legs: cap 14 · stage B reserve 3 · spent 3 (stage R two rounds, T005 one) · left for L 8.
Estimate per task: 0 (the per-task leg is reviewer A, not a paid leg); 1 only when a diff touches
CI, the Makefile, `close-task.yml`, dependencies or security posture, or reviewer A says BLOCK.
Expected over 46 tasks: 2–4.

## Stages

- [x] 0 orient — feature dir `specs/001-rudersdorf-2`; nothing existed (new repository); branch `001-rudersdorf-2` from `main`; no inbox, no open pull requests
- [x] P plan + tasks — generated: spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/werkstatt-api.md, tasks.md · spec set committed: 37f35ce
- [x] R spec-set review — round 1 on 37f35ce: BLOCK (5 CRITICAL, all fixed); round 2 on 44d37c9 in `reviews/R-spec-set/round-2/`: reviewer A BLOCK (2 CRITICAL, both mechanical contradictions from round-1 fixes, fixed), reviewer B CONCERNS · two-round cap reached; fixes of round 2 are unreviewed and listed in *Triage*
- [ ] L task loop — see *Tasks*
- [ ] B branch review — `reviews/B-branch/round-N/` · rounds: <n> · verdict: <…>
- [ ] Hand-off — <date> · `pr-description.md` · PR: <none | draft link>

## Fitness functions

| Characteristic | Command | Kind | Baseline (number, list, allow-list) | Per task / at B |
|---|---|---|---|---|
| Style and format | `make lint` | triggered | zero findings | per task |
| Layering (no pygame in core, laboratory, workshop, reference) | `tests/architektur/test_schichten.py` in `make check` (from T001) | triggered | no allow-list | per task |
| Workshop ships unsolved | `tests/architektur/test_werkstatt.py` in `make check` (from T003) | triggered | no allow-list | per task |
| Workshop and reference parity | `tests/architektur/test_paritaet.py` in `make check` (from T003) | triggered | no allow-list | per task |
| Content tables consistent | `tests/kern/test_daten.py` in `make check` (from T002) | triggered | — | per task |
| Determinism | `tests/kern/test_determinismus.py` in `make check` (from T014) | triggered | identical state hash | per task |
| Winnability and difficulty | `make test-lang` (`tests/kern/lang_balance.py`, from T030) | holistic | SC-005, SC-006 | T033, T037, T046, T047, B |
| Performance | `make bench`, `tests/kern/lang_leistung.py` (from T037) | holistic | step ≤ 4 ms, frame ≤ 8 ms | T037, T047, B |

Holistic run at B: not run yet

## Triage

| Stage | Finding (one line) | Sev | Reviewers | Disposition (fix / reject / defer) | Where it went / why | Needs user? |
|---|---|---|---|---|---|---|
| R1 | T016 speed test impossible (0.4 s needs 24 steps, cap is 12) | CRITICAL | A, B | fix | T016 case rewritten (12 steps at 4× for 0.05 s; backlog discarded); rule in plan.md | no |
| R1 | Magic (missions 19–20) depends on effects and chain lightning of other tracks | CRITICAL (A) / WARNING (B) | A, B | fix | prerequisites made explicit: registry `braucht`, `ABHAENGIG` in the workbench, FR-022 and SC-002 reworded, tests in T004, T018, T020, T025, T046 | no |
| R1 | `bauplan` ignored population, so the plan was not executable; order ambiguous | CRITICAL (A) / WARNING (B) | A, B | fix | population requirements replaced by `haeuser` levels in data and FR-016/FR-019; exact procedure and example in the contract; T022 tests execution of the plan | no |
| R1 | Missions 21–23 ship faulty code, against Constitution I and SC-003 | CRITICAL | A, B | fix | Constitution I amended to 1.1.0 with the craft-mission exception (decision by the orchestrator: the owner chose the bug-hunt topics in the brainstorm; pending owner validation); SC-003 reworded; mission 8 reports "still open" itself | validate |
| R1 | Mutable-default exercise fails lint rule B006 | CRITICAL | A | fix | per-file ignore for `werkstatt/fehlerjagd.py` in pyproject.toml | no |
| R1 | Mission 22 and 23 contracts too vague to test | WARNING | A | fix | functions, checks, base class and report schema fixed in the contract | no |
| R1 | Terminal traceback (FR-025) not tested | WARNING | A | fix | `Lernfehler.spur`; cases in T004 and T020 | no |
| R1 | SC-010: three commands did not reach a test result | WARNING | A | fix | quickstart order; SC-010 and T042 reworded | no |
| R1 | T014 tested interest and village/spell actions built later | WARNING | B | fix | moved to T022 and T025; `fuehre_aus` rule in plan.md | no |
| R1 | Probe inputs and probe failures undefined | WARNING | B | fix | `PROBEN`, missing-name rule, ignored probe errors in plan.md; T004 cases. Time guard rejected: a never-ending learner loop hangs any Python program; mission documents explain Ctrl+C | no |
| R1 | Mission 26 test: which package plays | WARNING | B | fix | always the package under test; prerequisites 3–7 in the registry; skeleton in the document | no |
| R1 | Where resistances apply | WARNING | B | fix | `Gegner.erleide_schaden` rule in plan.md and contract; T012 case | no |
| R1 | Wrong-return-value location, `spielen.main`, pause key | WARNING | B | fix | plan.md; T016 and T020 cases | no |
| R1 | Where the known-red list lives | WARNING | B | fix | tasks.md conventions: loop.md *Known red* | no |
| R1 | Presentation tasks have tests inside, not a separate test task | WARNING | B | reject | close-task records the red inside the task; behaviour is specified by the core test tasks; splitting six presentation tasks would add six fresh-agent rounds for drawing code | no |
| R1 | Coverage gaps: all capabilities, `endlos` in the save, end statistics, FR-008 integration, SC-007 drawn vs headless, FR-030 step time | WARNING | A, B | fix | new T046; `endlos` in contract and data model; `statistik()`; cases in T014, T020, T035 | no |
| R1 | Two unlock sources for spells; stale task ids and file names | NOTE | B | fix | `frei_ab_kirche` only; references corrected | no |
| R1 | Fast tests read the live `werkstatt/` and go red once the learner solves something | NOTE | B | reject | the developer suite is defined on the shipped state (tasks.md conventions); the learner uses `pruefen.py` | no |
| R1 | Balance tables, particle cap, hard-level threshold go beyond explicit requirements | NOTE | A | reject | they are design values the plan needs; T033 may tune the numbers | no |
| R2 | T004 forced-open case contradicted prerequisite propagation | CRITICAL | A | fix | case split: `schadensarten` alone; `wegfindung` with its dependants. Mechanical; no third round (two-round cap) | no |
| R2 | Mission 23 base class import forbidden by the layering guard | CRITICAL | A | fix | `rudersdorf.uebung` added to the allowed imports in T001, contract and plan. Mechanical | no |
| R2 | Constitution 1.1.0 amended without recorded owner approval | WARNING | A, B | fix | reason recorded in this commit's message; the owner chose bug hunts, clean-up and own-tests as topics in the brainstorm on 2026-11-24 and was told of the amendment the same day; still listed for validation at hand-off | validate |
| R2 | `bauregel` stand-in could seal a one-cell ford; a faulty `darf_bauen` could freeze a match | WARNING | B | fix | engine safety net in contract and plan; cases in T006 and T012 | no |
| R2 | `bauplan` recursion: which copy is shared | WARNING | B | fix | contract: one shared copy, inner helper, second example | no |
| R2 | T014 smithy case and reference stubs counted as solved | WARNING | B | fix | case moved to T029; reference stubs raise `NochOffen`; plan says which capabilities the engine calls from which task | no |
| R2 | Constructors of `Karte`, `Gegner`, `Bauwerk`, `Dorf` not fixed | WARNING | A, B | fix | plan.md *Fixed engine interfaces*; `Spiel.erzeuge_gegner` | no |
| R2 | Breaker and the placement rule | WARNING | B | fix | plan.md rule; T028 case | no |
| R2 | Spells adding effects without `fuege_effekt_hinzu`; tick wording; "nothing hit" message | WARNING | A, B | fix | contract; T025 cases | no |
| R2 | Capability check did not reach the end of a match | WARNING | A | fix | T046 plays whole campaigns | no |
| R2 | Mission 24 nested types; `labor.py` options; end screen; SC-003 for all missions | WARNING | A, B | fix | contract type list; plan `labor.main`; T016/T017; T018; T039 | no |
| R2 | Prerequisites in two places; `spur` parameter; `schwer` case wording; research wording; FR-020 level count | NOTE | B | fix | derived from the registry; signatures and wording corrected | no |
| R2 | Empty defence on `leicht` may survive past wave 4 with the starting numbers | NOTE | B | defer | T033 tunes the numbers until T030's slow tests pass | no |

## Tasks

| Task | Verdict | Review (legs, rounds, paid leg?) | Gaps / decision request |
|---|---|---|---|
| T001 | CLOSED | reviewer A (diff), 1 round, CONCERNS → APPROVE (only finding: final `make check` pending, then run green); no paid leg (no trigger) | none; proposal: forbid `rudersdorf/labor` → `rudersdorf.ansicht` in the layering guard (not in the task text) |
| T002 | CLOSED | reviewer A (diff), 2 rounds: round 1 CONCERNS (2 WARNINGs, both verified and fixed: split-only enemy was purchasable under mission 15's rule; tower values unchecked), round 2 CONCERNS (1 NOTE, wording fixed, design change rejected) → APPROVE; no paid leg (no trigger) | none; note for T011/T028: `daten.GEGNER` as a whole is the catalogue for `erzeuge_welle` (`schleimling` has `ab_welle` = `NIE_VON_SELBST`, the boss a price that is never used) |
| T003 | CLOSED | reviewer A (diff), 1 round, CLEAN → APPROVE; no paid leg (no trigger) | none; notes for later tasks: document anchors are `#mission-N` (T042–T045); the names-only parity rule for missions 21–23 means "every registry name exists in both packages" (T040); in the module of mission 8 the reference may add functions with the parameters `kandidaten, turm` |
| T004 | CLOSED (verified red: 34 tests) | reviewer A (diff), 2 rounds: round 1 CONCERNS (1 WARNING, verified and fixed: no test failed when the stand-in registry was copied at construction), round 2 CLEAN → APPROVE; no paid leg (no trigger) | none; notes for T005: stand-ins live in `rudersdorf.ersatz.ERSATZ` (capability → name → function or class), looked up at every call, never needed for construction or probing; not asserted because the spec set leaves it open: what an object created before its capability opened answers afterwards, `wartet_auf` for a capability open by itself with an open prerequisite, `waehle_paket(False)`, the location fields of the `Lernfehler` of a syntax error |
| T005 | CLOSED-WITH-GAPS (34 known-red tests green; 40 tests added) | reviewer A (diff), 2 rounds: round 1 BLOCK (3 WARNINGs, all verified and fixed: stale byte-code on reload, raw `AttributeError` from a wrapped instance, package attribute keeping an old helper module), round 2 BLOCK (1 WARNING, verified and fixed: helper first imported by a failed reload stays on the package); paid leg: 1, in round 2 because of the round-1 BLOCK, CONCERNS (the same WARNING; 1 WARNING deferred, 2 NOTEs rejected) → REQUEST_CHANGES, fixed | gaps: the fix after round 2 is unreviewed (own test and mutant); reviewer A's last word was BLOCK; probe method signatures of classes are checked only once the references exist (T011, T026); notes for later tasks: a `Lernfehler` from an import error has `faehigkeit` and `mission` `None`; the engine never writes to or probes (`hasattr`) an object from `erzeuge` (T015, T026); objects the learner's code creates itself are not wrapped (T015); `strategien()` returns wrapped entries, `inspect` still finds the original |
| T006 | CLOSED (verified red: 86 tests; 36 helper self-tests green) | reviewer A (diff), 2 rounds: round 1 CONCERNS (2 WARNINGs, both verified and fixed: a malformed `nachbarn` answer crashed the test's hint choice; no M4 case for neighbours outside `breite` and `hoehe`), round 2 CLEAN → APPROVE; no paid leg (no trigger) | none; notes for T007: the stand-in tests fix `lies_karte(text)` → a fresh `flusstal` grid whatever the text, `abstandskarte` → Manhattan distance for every cell of the grid, `darf_bauen` → false for the eight cells around a cell in `gesperrt`; every name of `karten`, `wegfindung`, `bauregel` needs an entry in `ERSATZ`; not asserted: the `karten` stand-in on a broken text, terrain, border and `besetzt` in the `bauregel` stand-in; notes for T008 and later test tasks: `tests/missionen/helfer.py` has `Missionstest` (`modul = "…"`, `pruefe_gleich`, `pruefe_fehler`, `rufe_sicher`, `pruefe_unveraendert`), `meldung`, `TestGegner`; a change to a helper needs its case in `tests/missionen/test_helfer.py` |

## Known red

Tests a test task left red for a later task; excluded from "green" at close, nothing else is.

| Test (file:name) | Story | Written in | Cleared in |
|---|---|---|---|
| `tests/kern/test_werkbank.py`: `Aufrufe` (7): `test_rufe_liefert_den_wert_der_funktion`, `test_rufe_reicht_benannte_argumente_weiter`, `test_offene_funktion_wird_durch_den_ersatz_beantwortet`, `test_noch_offen_erst_beim_aufruf_schaltet_auf_den_ersatz_um`, `test_ersatz_wird_bei_jedem_aufruf_frisch_nachgeschlagen`, `test_halb_geloeste_faehigkeit_benutzt_ueberall_den_ersatz`, `test_geloeste_faehigkeit_benutzt_die_echte_funktion` | foundational | T004 | T005 |
| `tests/kern/test_werkbank.py`: `FehlerImLernendenCode` (3): `test_fehler_wird_zum_lernfehler_mit_datei_zeile_art_text_und_mission`, `test_lernfehler_traegt_die_urspruengliche_spur`, `test_fehler_in_der_probe_haelt_den_start_nicht_auf` | foundational | T004 | T005 |
| `tests/kern/test_werkbank.py`: `Offenheit` (8): `test_ein_geloestes_paket_hat_nichts_offen`, `test_offene_stehen_schon_vor_dem_ersten_aufruf_fest`, `test_gesperrt_macht_nur_diese_faehigkeit_auf`, `test_gesperrte_wegfindung_macht_auch_die_wartenden_auf`, `test_fehlendes_modul_macht_seine_faehigkeiten_auf`, `test_fehlender_name_macht_seine_faehigkeit_auf`, `test_fehlende_klasse_macht_ihre_faehigkeit_auf`, `test_leeres_paket_hat_alles_offen` | foundational | T004 | T005 |
| `tests/kern/test_werkbank.py`: `Voraussetzungen` (4): `test_magie_wartet_auf_gesperrte_effekte`, `test_magie_wartet_auf_ungeloeste_effekte`, `test_magie_ist_nicht_offen_wenn_alles_geloest_ist`, `test_selbst_offene_magie_wartet_auf_nichts` | foundational | T004 | T005 |
| `tests/kern/test_werkbank.py`: `NeuLaden` (4): `test_lade_neu_benutzt_den_geaenderten_code`, `test_lade_neu_bemerkt_eine_geloeste_mission`, `test_lade_neu_bemerkt_eine_wieder_offene_mission`, `test_tippfehler_beim_neuladen_laesst_den_alten_code_laufen` | foundational | T004 | T005 |
| `tests/kern/test_werkbank.py`: `Klassen` (4): `test_erzeuge_baut_die_klasse_der_werkstatt`, `test_offene_methode_wird_von_der_ersatzklasse_beantwortet`, `test_offener_bauplan_der_klasse_fuehrt_zur_ersatzklasse`, `test_noch_offen_erst_im_methodenaufruf_schaltet_auf_die_ersatzklasse_um` | foundational | T004 | T005 |
| `tests/kern/test_werkbank.py`: `Paketwahl` (4): `test_ohne_die_variable_wird_die_werkstatt_gewaehlt`, `test_mit_null_wird_die_werkstatt_gewaehlt`, `test_mit_eins_wird_die_loesung_gewaehlt`, `test_der_schalter_waehlt_die_loesung_auch_ohne_variable` | foundational | T004 | T005 |
| `tests/missionen/test_m01.py`: `Mission01` (14): `test_jede_zeile_wird_eine_liste_aus_einzelnen_zeichen`, `test_leerzeichen_am_zeilenende_gehoeren_nicht_zur_karte`, `test_leere_zeilen_davor_dazwischen_und_danach_werden_uebersprungen`, `test_leerzeilen_ringsum_und_leerzeichen_am_ende_zusammen`, `test_die_letzte_zeile_braucht_keinen_zeilenumbruch`, `test_leerzeichen_am_zeilenanfang_bleiben_stehen`, `test_unbekannte_zeichen_sind_hier_noch_kein_fehler`, `test_eine_zu_kurze_zeile_ist_ein_fehler`, `test_ein_leerer_text_ist_ein_fehler`, `test_ein_text_nur_aus_leerzeilen_ist_ein_fehler`, `test_finde_nennt_erst_die_spalte_und_dann_die_zeile`, `test_finde_sucht_zeile_fuer_zeile_von_oben_nach_unten`, `test_finde_liefert_eine_leere_liste_wenn_das_zeichen_fehlt`, `test_finde_laesst_das_raster_wie_es_war` | US1 | T006 | |
| `tests/missionen/test_m02.py`: `Mission02` (14): `test_eine_zelle_in_der_mitte_hat_vier_nachbarn_oben_rechts_unten_links`, `test_die_ecke_oben_links_hat_nur_zwei_nachbarn`, `test_die_ecke_unten_rechts_hat_nur_zwei_nachbarn`, `test_eine_zelle_am_oberen_rand_hat_drei_nachbarn`, `test_eine_zelle_am_rechten_rand_hat_drei_nachbarn`, `test_eine_zelle_am_unteren_rand_hat_drei_nachbarn`, `test_auf_einer_karte_aus_einer_einzigen_zelle_gibt_es_keine_nachbarn`, `test_wiese_sumpf_huegel_und_die_beiden_tore_sind_begehbar`, `test_fels_wasser_und_dorfgrund_sind_nicht_begehbar`, `test_eine_gesperrte_wiese_ist_nicht_begehbar`, `test_neben_einer_gesperrten_zelle_bleibt_die_wiese_begehbar`, `test_links_und_oberhalb_der_karte_ist_nichts_begehbar`, `test_rechts_und_unterhalb_der_karte_ist_nichts_begehbar`, `test_ist_begehbar_laesst_raster_und_gesperrt_wie_sie_waren` | US1 | T006 | |
| `tests/missionen/test_m03.py`: `Mission03` (7): `test_auf_freier_wiese_zaehlt_der_abstand_die_schritte_bis_zum_ziel`, `test_das_ziel_selbst_hat_den_abstand_null`, `test_um_eine_felswand_mit_einer_luecke_fuehrt_nur_der_umweg`, `test_eine_wand_aus_bauwerken_wirkt_genauso_wie_eine_felswand`, `test_eine_eingeschlossene_zelle_fehlt_in_der_abstandskarte`, `test_sumpf_huegel_und_orktor_zaehlen_wie_wiese_einen_schritt`, `test_abstandskarte_laesst_gesperrt_und_das_raster_wie_sie_waren` | US1 | T006 | |
| `tests/missionen/test_m04.py`: `Mission04` (12): `test_der_schritt_geht_zum_nachbarn_mit_dem_kleineren_abstand`, `test_von_mehreren_kleineren_nachbarn_gewinnt_der_kleinste`, `test_bei_gleichstand_gewinnt_rechts_vor_unten`, `test_bei_gleichstand_gewinnt_oben_vor_rechts`, `test_bei_gleichstand_gewinnt_unten_vor_links`, `test_ein_nachbar_ohne_abstand_wird_nie_betreten`, `test_ein_nachbar_ausserhalb_der_karte_wird_nie_betreten`, `test_am_ziel_gibt_es_keinen_schritt_mehr`, `test_fuer_eine_zelle_ohne_abstand_gibt_es_keinen_schritt`, `test_bergauf_geht_es_nie`, `test_wer_den_schritten_folgt_kommt_auf_dem_kuerzesten_weg_ans_ziel`, `test_naechster_schritt_laesst_die_abstandskarte_wie_sie_war` | US1 | T006 | |
| `tests/missionen/test_m05.py`: `Mission05` (20): `test_auf_einer_freien_wiese_abseits_des_weges_darf_gebaut_werden`, `test_auf_einem_freien_huegel_darf_gebaut_werden`, `test_mitten_im_weg_darf_gebaut_werden_wenn_ein_anderer_weg_bleibt`, `test_auf_fels_wasser_sumpf_und_dorfgrund_darf_nicht_gebaut_werden`, `test_auf_den_toren_darf_nicht_gebaut_werden`, `test_wo_schon_ein_bauwerk_steht_darf_nicht_gebaut_werden`, `test_wo_gerade_ein_ork_steht_darf_nicht_gebaut_werden`, `test_links_und_oberhalb_der_karte_darf_nicht_gebaut_werden`, `test_rechts_und_unterhalb_der_karte_darf_nicht_gebaut_werden`, `test_die_letzte_luecke_einer_mauer_darf_nicht_geschlossen_werden`, `test_neben_der_letzten_luecke_darf_weiter_gebaut_werden`, `test_in_einer_furt_die_nur_eine_zelle_breit_ist_darf_nicht_gebaut_werden`, `test_vor_und_hinter_der_furt_darf_gebaut_werden`, `test_ein_ork_in_der_nische_darf_nicht_eingesperrt_werden`, `test_neben_dem_eingang_der_nische_darf_gebaut_werden`, `test_ist_die_nische_leer_darf_ihr_eingang_zugebaut_werden`, `test_bei_zwei_toren_darf_das_zweite_tor_nicht_abgeschnitten_werden`, `test_bei_zwei_toren_darf_das_erste_tor_nicht_abgeschnitten_werden`, `test_bei_zwei_toren_darf_gebaut_werden_wenn_beide_ihren_weg_behalten`, `test_darf_bauen_laesst_alles_wie_es_war` | US1 | T006 | |
| `tests/kern/test_ersatz_a.py`: `ErsatzVollstaendig` (3): `test_karten_hat_einen_ersatz_fuer_jeden_namen`, `test_wegfindung_hat_einen_ersatz_fuer_jeden_namen`, `test_bauregel_hat_einen_ersatz_fuer_jeden_namen` | US1 | T006 | |
| `tests/kern/test_ersatz_a.py`: `ErsatzKarten` (5): `test_aus_einem_anderen_kartentext_wird_trotzdem_das_flusstal`, `test_aus_der_datei_einer_anderen_karte_wird_trotzdem_das_flusstal`, `test_das_flusstal_des_ersatzes_hat_24_spalten_und_16_zeilen`, `test_jeder_aufruf_liefert_ein_eigenes_raster`, `test_der_ersatz_findet_orktor_und_dorftor_im_flusstal` | US1 | T006 | |
| `tests/kern/test_ersatz_a.py`: `ErsatzWegfindung` (6): `test_hinter_der_mauer_zaehlt_der_ersatz_die_luftlinie_statt_des_umwegs`, `test_auch_fels_und_bauwerke_haben_beim_ersatz_einen_abstand`, `test_jede_zelle_der_karte_hat_ihre_luftlinie_als_abstand`, `test_das_ziel_hat_auch_beim_ersatz_den_abstand_null`, `test_ein_geist_laeuft_gerade_durch_die_mauer_zum_ziel`, `test_der_ersatz_laesst_gesperrt_und_das_raster_wie_sie_waren` | US1 | T006 | |
| `tests/kern/test_ersatz_a.py`: `ErsatzBauregel` (5): `test_schraeg_neben_einem_bauwerk_verbietet_der_ersatz_das_bauen`, `test_direkt_neben_einem_bauwerk_verbietet_der_ersatz_das_bauen`, `test_mit_einer_zelle_abstand_erlaubt_der_ersatz_das_bauen`, `test_ohne_andere_bauwerke_erlaubt_der_ersatz_das_bauen`, `test_der_ersatz_laesst_gesperrt_wie_es_war` | US1 | T006 | |

## Test changes

Tests from a test task changed by a later task (close-task `TEST` class); each one changes what green means.

| Test (file:name) | Written in | Changed in | Evidence it was wrong |
|---|---|---|---|

## Lessons

<!-- master list: one line per reusable lesson with the task ids that hit it -->
- A guard's self-test loops over directories written out in the test, never over the guard's own rule tuples; otherwise a narrowed rule narrows its test (T001).
- No mutation gate and no Markdown gate here: prove guards and logic with hand-written mutants on a copy outside the repository, run with `.venv/bin/python` and `PYTHONDONTWRITEBYTECODE=1` (T001).
- Reviewer A flags a pending final `make check` as a WARNING; it is the planned order, answer it by running FINAL and recording it (T001).
- A table handed to learner code must be valid under the contract's rule for that code: test the real table with the contract's rule written out in the test, not only its keys (T002).
- A faulty-copy self-test changes a value nothing else refers to, or the checker rightly reports two errors; a cycle self-test needs a cycle that exists only through the implicit "level before" edge (T002).
- `make check` takes under a second while the engine is small: run it before the review as well and record it, so the reviewer has no pending gate to flag (T002).
- A written-out list in a guard is compared with something it was not filtered by; a test that filters the registry by the list and compares the result with the list cannot fail (T003).
- Besides invented fixtures, break each guarded place of a copy of the real package in turn (each placeholder, each signature): that proves the guard's scope has no hole (T003).
- The parity guard reports every public function or method the reference has and the workshop lacks: reference helpers start with an underscore or are inner functions; the only exception is extra strategies `(kandidaten, turm)` in `strategien.py` (T003).
- The workshop guard pins each placeholder to the text `Mission N: <Titel>` of the registry, and `tests/architektur/test_missionen.py` writes the contract's tables out again: a changed title, name or module is changed in the registry, that test and the stubs together (T003).
- A test task for a module that does not exist yet: write a throwaway implementation outside the repository, show the tests green on it and red on its mutants; that proves the tests are satisfiable together and that each one can fail (T004).
- A rule a stub's docstring states for the implementer (here: stand-ins are looked up at every call) needs its own test, or the implementer may break it unnoticed; reviewer A looks for exactly that (T004).
- Tests that rewrite a module and reload it must move the file's modification time on (`os.utime`), or the byte-code cache serves the old code for a same-second, same-length edit; temporary packages are built from `rudersdorf.missionen` so they stay solved under any probe input (T004).
- Two review legs launched side by side need separate output directories: the launcher names its single leg `reviewer-a` and replaces reviewer A's file; the text can be recovered from the transcript's final message (T005).
- Reloading Python modules means clearing three places (`sys.modules`, the attribute on the parent package, the cached byte-code: Python compares whole-second time and size) on two paths (fresh load, roll-back after a failed load); write one test per place and path before the review (T005).
- A wrapper that forwards attribute access treats the look-up as learner code too: a missing method must become a `Lernfehler`, not a raw `AttributeError` (T005).
- Tests added by an implementation task are green at their first run: run the hand-written mutants before the review, they show the missing cases (T005).
- Test code that inspects a learner's answer before comparing it (sorting, indexing) must survive any answer, `None` and mixed lists included: put it in `tests/missionen/helfer.py` with its own case in `test_helfer.py` (T006).
- A contract rule left out of a mission test "because the hint would confuse" comes back as a review finding: write the case with a plain hint (T006).
- After a mutant run, print the tests no mutant turned red; each one needs a mutant that reaches it or a reason why another rule implies it (T006).
- Mission tests draw their maps with `helfer.raster_aus` and call the package directly (`self.werkstatt.<name>`), so `NochOffen` reaches the runner; negative cells in "outside the grid" cases are chosen so that Python's wrap-around lands on an allowed cell, or a missing border check passes unnoticed (T006).

## Where a human should look first

<!-- filled at hand-off -->

## Proposed harness changes

| Lesson | Seen in | Proposed change (AGENTS.md line / sensor / close-task.yml) |
|---|---|---|

## Owner tasks (skipped by the loop)

| Task | Command sheet |
|---|---|
