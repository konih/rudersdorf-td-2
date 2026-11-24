## Verdict: CONCERNS

## Findings
- [WARNING] The `bauregel` stand-in still lets the player close the route. — `contracts/werkstatt-api.md:285`
  Failure: `wegfindung` solved, `bauregel` open (the learner has done missions 2–4 but not 5). On `flusstal`, one tower in each one-cell ford never touches another building, so the stand-in allows both. Gates then drop out of the distance map, `naechster_schritt` returns `None`, enemies stand still and the wave never ends. This breaks FR-024 and FR-004. T046 uses "a simple scripted defence" and would not catch it.
  Fix: make the stand-in also run the engine's reachability check (gates and `besetzt` must stay in the distance map), and add a T006/T020 case with a single-gap corridor.
  Confidence: 80
- [WARNING] The `bauplan` procedure contradicts itself about which copy the recursion updates. — `contracts/werkstatt-api.md:166-174`
  Failure: "On a private copy of `stufen`… recursively, by the same procedure" reads as if each call makes its own copy. Implemented that way, `kirche` 5 lists `kirche 3`/`steinbruch 1` twice (via `bauhuette` 3 and the church's own levels). That fails T022's "appears once" case, yet it follows the text. For the child this is shared mutable state through recursion, a big jump within track D.
  Fix: say the recursion shares and updates the one copy (pass it down), and add a two-paths-to-one-prerequisite example.
  Confidence: 75
- [WARNING] T014 tests the smithy gate on master upgrades before the village exists. Meanwhile the `loesung/` stubs raise `NotImplementedError`, which the workbench counts as *solved*. — `tasks.md:178`, `tasks.md:59`, `plan.md:149-152`
  Failure: `schmiede_stufe` comes from `sammle_boni` (mission 17). In T015, `loesung/dorf.py` is still a T003 stub raising `NotImplementedError`. That is not `NochOffen`, so the probe ignores it, the capability counts as solved and every call becomes a `Lernfehler`. The "with the smithy → true" case cannot go green honestly, and any T015 income or bonus call does the same thing to T017's `--probelauf`.
  Fix: move the smithy case to T029, which already has it. State in plan.md that the engine does not call `voraussetzungen`/`boni`/`bauplan`/`magie`/`speichern`/`auswertung`/`bot` before their story, or let the reference stubs raise `NochOffen`.
  Confidence: 65
- [WARNING] The constitution was amended to 1.1.0 without owner approval and without the commit note that governance requires. Tasks T003, T038 and T040 depend on that amendment. — `.specify/memory/constitution.md:13-16,83-84`, `loop.md:43`
  Failure: commit 44d37c9's whole message is one subject line, with no "what changed and why". loop.md says "pending owner validation". If the owner rejects it, missions 21–23 and SC-003 have no basis.
  Fix: get the owner's approval and record it (a commit note or decisions entry) before T003 is dispatched.
  Confidence: 90
- [WARNING] The placement rule is undefined while a breaker is demolishing something. — `plan.md:209`, `data-model.md:74`
  Failure: `besetzt` = every walking enemy's `zelle` and `ziel_zelle`. If a breaker's `ziel_zelle` is the building it is tearing down, that blocked cell can never appear in the distance map. `darf_bauen` would then refuse every placement on the map for 5 s. `rest_weg` for breakers (labyrinth map or empty map?) is also not fixed, so `erster`/`letzter` can disagree between implementations.
  Fix: state the breaker's `ziel_zelle` during demolition (its own cell), say whether it is in `besetzt`, and say which map its `rest_weg` uses. Add a T028 case.
  Confidence: 60
- [WARNING] It is unclear whether Mission 20's `Eissturm` and `Glockenschlag` add their effect through `fuege_effekt_hinzu`; only `Feuerball` says so. — `contracts/werkstatt-api.md:188-189,197-198`
  Failure: one learner uses `effekte.append(Frost(...))`, another uses `fuege_effekt_hinzu`. Both match the text, but the first stacks two frosts, which breaks FR-011. Whether T025 catches it depends on which fixture its author picks.
  Fix: say "through `fuege_effekt_hinzu`" for every spell that adds an effect, and add a T025 case with an existing frost or stun.
  Confidence: 70
- [WARNING] The engine constructors that T012 needs are not fixed anywhere. — `plan.md:110`, `tasks.md:154-156`
  Failure: T012 should write stubs "carrying the plan's signatures", but the plan only fixes `Spiel`, not `Karte`/`pruefe_karte`, `Gegner(...)`, `Bauwerk(...)` or `Dorf(...)`. Tests must place enemies directly, and it is open whether a broken `kartentext` raises or falls back. T012 invents an API that later fresh agents (T014, T028, T037, T046) never see in their cited documents.
  Fix: add these constructor signatures to *Fixed engine interfaces*, and say what `Spiel(kartentext=<broken>)` does.
  Confidence: 70
- [WARNING] FR-032 is only partly delivered: the CLI of `labor.py` is never specified. — `tasks.md:497`, `spec.md:413`
  Failure: there is no option for map or bot, and no task checks results per difficulty (US7 scenario 5). A `labor.py` with only `--spiele/--schwierigkeit/--loesung` passes T039 but not FR-032.
  Fix: fix the `labor.main` options in plan.md (`--karte`, `--bot`, several levels) and add a T039 case.
  Confidence: 65
- [NOTE] Prerequisites come from two sources that disagree. — `tasks.md:56`, `contracts/werkstatt-api.md:277-279`, `data-model.md:182`
  Failure: mission 5 has `braucht: [3]`, a mission in its own track, even though `braucht` is defined as "other tracks". In the game, `bauregel` waits for the whole `wegfindung` (2, 3, 4). Mission 26 leaves out mission 2. So the board can suggest mission 5 while the game still labels it "wartet auf Mission 2, 3, 4".
  Fix: derive one from the other.
  Confidence: 70
- [NOTE] `Lernfehler`'s fixed `__init__` has no `spur` parameter, yet T004 tests `spur`. — `plan.md:116-117,142`
  Fix: add `spur=""` to the signature.
  Confidence: 60
- [NOTE] With the starting data, the empty defence on `leicht` probably survives past wave 4. — `data-model.md:84,96`, `tasks.md:392`
  Failure: rough estimate: about 28 breach damage over waves 1–4 against 30 village life.
  Fix: none needed in the spec; T033 has to tune toward this case, and the evidence should show it.
  Confidence: 50
- [NOTE] The `schwer` case of T030 cannot be read as one testable condition ("does not win all… without village and magic switched on"). — `tasks.md:393`
  Confidence: 70
- [NOTE] Research says the other test folders always use the reference, but T018, T020 and T038 use `werkstatt`. — `research.md:63-64`
  Confidence: 60
- [NOTE] Gaps with no task:
  - the end screen's "offer a new match" (US1 scenario 6);
  - the message "nothing was hit" when a spell hits nothing (edge case; T025);
  - whether "at least three levels bought in the library" (FR-020) is met when data has only two buyable upgrades (`data-model.md:133-139`).
  Confidence: 55

## Fixes from round 1, checked
- Hold: T016 speed case, magic prerequisites (`ABHAENGIG`, `wartet_auf`, T004/T020/T046), B006 per-file ignore (`pyproject.toml`), contracts for missions 22 and 23, `spur` case, quickstart order for SC-010, T014 split into T022/T025, `PROBEN`, mission 26 package rule, `erleide_schaden`, keys and `spielen.main`, `endlos`/`statistik`, `frei_ab_kirche`.
- Partial: `bauplan` (contradicts itself, see above), the constitution amendment (governance), the `spur` signature.
- FR-001–FR-038 and SC-001–SC-010 each map to a task. The partial ones are FR-032, FR-020 and US1 scenario 6.

## Could not check
- `specs/001-rudersdorf-2/reviews/R-spec-set/round-2/` (other reviewers, deliberately not read), `task-prompt.md` and the first-round leg reports.
- No tests or Python were run. The float behaviour of the 12-step backlog and the SC-005 balance figures are estimates.
- `.github/workflows/pruefung.yml`, the source of the close-task and spec-loop skills, and anything outside the repository.
