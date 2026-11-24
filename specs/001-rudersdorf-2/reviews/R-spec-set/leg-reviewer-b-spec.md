## Verdict: BLOCK

## Findings
- [CRITICAL] T016's speed test cannot pass: at speed 4, `aktualisiere(0.1)` needs 0.4 s / DT = 24 steps, but the same test caps a call at 12 steps — `specs/001-rudersdorf-2/tasks.md:182`
  Failure: any implementation that honours the R4 cap (`research.md:43`) advances 0.2 s and fails. One that advances 0.4 s breaks the cap. T017 cannot turn T016 green.
  Fix: use `aktualisiere(0.05)` (12 steps), or assert the 12-step cap separately with a large input.
  Confidence: 95
- [CRITICAL] SC-003 contradicts the spec and the contract. The untouched workshop cannot fail every mission with "still open" — `spec.md:458`, `spec.md:246-249`, `contracts/werkstatt-api.md:201`, `:80`
  Failure: M21 ships with ordinary errors, M22's behaviour tests pass as shipped, M23's example test passes, and M8 fails with an assertion rather than `NochOffen`. T046's SC table can never be completed, and `.fortschritt.json` marks 8 and 21–23 as "begonnen" from day one (`data-model.md:190`).
  Fix: reword SC-003 to "missions 1–20 and 24–26 report still open; 8 and 21–23 report their shipped state", and add a test task that checks it.
  Confidence: 90
- [CRITICAL] The plan breaks Constitution I without recording it. "every mission function or method body raises `NochOffen`" (`constitution.md:13-14`), yet 21–23 ship faulty or untidy code. The plan still says "No violations" — `plan.md:30,37`, `contracts/werkstatt-api.md:201`
  Failure: `make check` guards contradict the constitution, which overrides the plan. Any agent applying the constitution literally would make 21–23 raise `NochOffen`.
  Fix: add a Complexity Tracking row, or have the owner amend Constitution I with the exception for the craft track.
  Confidence: 85
- [WARNING] Track D depends on tracks B and C, which breaks FR-022 ("any order across tracks") — `contracts/werkstatt-api.md:177-187`, `spec.md:380`
  Failure: `Feuerball` needs `Brand`/`fuege_effekt_hinzu` (M12/13), `Eissturm` needs `Frost` and `Blitzschlag` needs `kettenblitz` (M9). If the learner solves M19–20 first, their tests fail with `NochOffen` from another track, and the workbench labels `magie` as open even though M19–20 are done.
  Fix: give M20 its own minimal effect and chain inputs, or declare B/C as prerequisites and drop "any order" for D.
  Confidence: 85
- [WARNING] The `bauplan` contract allows two correct orders, but T022 fixes one exact list — `contracts/werkstatt-api.md:163-166`, `tasks.md:262`
  Failure: "a1 first, then a2's prerequisites" gives `[a1,c1,b1,a2]`; "prerequisites first" gives `[c1,b1,a1,a2]`. Both satisfy every stated rule, so a correct learner solution fails. The order in which `braucht` keys are visited is also unspecified. In addition, the contract says the population key is ignored, so the plan is not the "complete ordered list" FR-019 asks for (`spec.md:369`): kirche 3 needs 24 bewohner, i.e. haeuser 1.
  Fix: state the order explicitly (sorted keys, prerequisites before lower levels or the other way round), and either fold population into `haeuser` levels or narrow FR-019.
  Confidence: 85
- [WARNING] T014 tests things only later tasks implement — `tasks.md:165,168` vs T023/T026
  Failure: "interest capped" needs the market bonuses (M17, T023), and "`fuehre_aus` with each action kind" includes `dorf`, `zauber` and `zauber_ausbau` (T023/T026). T015 cannot go green without building the village and magic, which T025 tests again later.
  Fix: limit T014 to the build, upgrade, sell, strategy and wave actions with no market, and move the rest to T022/T025.
  Confidence: 80
- [WARNING] Neither the capability probe inputs nor how a probe failure is handled is fixed, yet T004 and T005 depend on them — `research.md:35-36`, `plan.md:123`, `tasks.md:74`
  Failure: `FAEHIGKEITEN` holds only missionen/modul/namen. The test author's temp packages and the implementer's probes can disagree about which functions and classes are called, and with what arguments. A learner BFS that loops forever freezes start-up with no panel.
  Fix: fix a probe table (capability → call and arguments) in `plan.md`, state that any non-`NochOffen` error in a probe becomes a `Lernfehler`, and add a time guard.
  Confidence: 75
- [WARNING] Neither the contract nor T039 says which package runs the match in M26's survival test — `contracts/werkstatt-api.md:240-242`, `tasks.md:470`
  Failure: if the engine uses `loesung`, the reference is loaded without the switch (Constitution I). If it uses the learner's `werkstatt`, ghost walk and the `bauregel` stand-in make five waves depend on other tracks. M26 is also a large step up in difficulty from M25.
  Fix: run the test with a fixed engine package and only `bot` swapped, document this in the contract, and add a `labor`-map scaffold bot to the mission document.
  Confidence: 75
- [WARNING] Where resistances are applied is undefined: in `Gegner.erleide_schaden`, or by the caller through M11 — `contracts/werkstatt-api.md:19-23,114`, `data-model.md:143-146`
  Failure: poison on a slime (gift ×0.5) is halved, applied twice or not applied at all, depending on the implementer. T028's ghost "quarter damage" check and the balance numbers then disagree between tasks.
  Fix: in the `Gegner` section of `plan.md`, state that `erleide_schaden` applies `berechne_schaden` through the workbench and that towers pass raw damage.
  Confidence: 70
- [WARNING] Several test tasks rely on things the plan and contract never fix:
  - T020 requires a file and line for a strategy that returns a non-candidate, but no traceback frame exists in that case (`tasks.md:226`, `plan.md:139`).
  - T016 tests `spielen.py` argument parsing, but no `main(argv)` or parse function is fixed (`tasks.md:184`).
  - `N`/space means both "start wave" and "pause", while the edge case says that key does nothing during a wave (`plan.md:223`, `spec.md:298`).
  Fix: define the location for value errors (the function's `def` line), add `spielen.main(argv) -> int`, and give pause its own key (`P`).
  Confidence: 75
- [WARNING] "make check (known red excepted)" is in almost every Verify line, but no task says where the known-red list lives — `tasks.md:112,124,...`, `constitution.md:48-49`
  Failure: a fresh agent cannot tell an allowed red from a regression, so the gate cannot be checked by a machine.
  Fix: have each test task append its test ids to `evidence/known-red.txt`, and have each implementation task remove them.
  Confidence: 70
- [WARNING] US6 has no test task ahead of its implementation. T024, T027 and T034–T036 merge "tests first inside this task", so no verified red is ever recorded (Constitution IV) — `tasks.md:408,426,277,321,388`
  Fix: split each into a test task that closes on red, followed by an implementation task.
  Confidence: 65
- [WARNING] Coverage gaps:
  - FR-024/SC-002 are checked only for capabilities of tracks A–C, and in the inverse form ("only k open" rather than "only k solved") (`tasks.md:224`).
  - The mission 24 `zustand` has no `endlos` flag, so an endless save reloads as a campaign (`contracts/werkstatt-api.md:227-230`).
  - The victory and defeat statistics (enemies defeated, gold earned, US1-6) have no interface or test.
  Fix: loop over all 18 capabilities with `gesperrt` set to all but k, add `endlos` to `zustand`, and add counters to `Spiel`.
  Confidence: 70
- [NOTE] The plan leaves room for disagreement and stale guidance:
  - Spell unlocking has two sources of truth: `frei_ab_kirche` and the `zauber_frei_<name>` bonus (`data-model.md:112,130`).
  - The M22 checks "written-out formula" and "15 statements" are ambiguous for `ast` (`contracts/werkstatt-api.md:212-215`).
  - Stale cross-references: "T027 (balance)" (`data-model.md:4`), "belongs to T032" should read T031 (`tasks.md:174`), `test_ersatz.py` (`plan.md:31`), and "last part of `test_ersatz_e`" when no earlier task creates a first part (`tasks.md:466`).
  - The fast tests in T020/T038 read the live `werkstatt/` and go red once the learner solves anything.
  Fix: keep one unlock source, define the `ast` rules exactly, correct the ids, and copy an untouched `werkstatt` into a temp directory for those tests.
  Confidence: 70

## Could not check
- I did not read `.github/workflows/pruefung.yml`, so I don't know whether CI runs `make test-lang`, where the machine-dependent thresholds of SC-004 and T037 would apply.
- I ran no commands or tests; nothing is implemented yet, so every finding comes from reading the documents.
- Whether `python -m rudersdorf.ansicht.vorschau` (T035) and T017's "five seconds under the dummy driver" can be run as written: the plan fixes no `__main__` and no time limit.
