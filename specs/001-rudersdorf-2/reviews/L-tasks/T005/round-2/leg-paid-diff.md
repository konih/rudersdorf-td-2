## Verdict: CONCERNS

## Findings
- [WARNING] A failed `lade_neu` leaves a stale package attribute behind for any submodule it imported for the first time, so a later `from . import x` can keep returning old code. — `rudersdorf/werkbank.py:518-527`
  Failure: the learner adds a new `werkstatt/helfer.py` (WERT = 1). Then `horde.py` gets `from . import helfer` plus a runtime error further down. `lade_neu` imports `helfer`, and the import machinery runs `setattr(werkstatt, "helfer", mod)`. `horde` then fails. `_setze_zurueck` removes `werkstatt.helfer` from `sys.modules` but only restores attributes for names in `vorher`, so `werkstatt.helfer` still points at the orphaned module. The learner fixes `horde.py` and sets WERT = 2. On the next `lade_neu`, `_wirf_weg` only walks the entries in `sys.modules`, so the orphan attribute survives. `_handle_fromlist` sees `hasattr(werkstatt, "helfer")` and skips the import, so the game runs WERT = 1. This is the same defect class as round-1 finding (c). `test_fehlgeschlagenes_neuladen_laesst_auch_das_hilfsmodul_stehen` (test_werkbank_regeln.py:425) only covers a helper that was already in `vorher`.
  Fix: in `_setze_zurueck`, for each name dropped from `sys.modules` that is not in `vorher`, `delattr(paket, kurz)` when the attribute is that module. Add a test with a helper that first appears in the failing reload.
  Confidence: 70
- [WARNING] `Werkstueck.__getattr__` turns a missing attribute into `Lernfehler` instead of `AttributeError`, which breaks `hasattr` and `getattr(obj, name, default)` on wrapped objects. — `rudersdorf/werkbank.py:402-417`
  Failure: the contract sets `self.letzte_wirkung` only after the first `zaubere` (contracts/werkstatt-api.md:184-186). Engine code such as `getattr(zauber, "letzte_wirkung", 0)` on a fresh `erzeuge("magie", "Feuerball", ...)` would raise `Lernfehler` instead of returning 0. Once the capability is open, the same call on the stand-in path (`:417`) returns the default. So the same engine code behaves differently depending on openness.
  Fix: make `Lernfehler` raised from `_lies` also an `AttributeError`, or document that the engine must never probe attributes optionally. Pin the chosen behaviour with a test.
  Confidence: 45 (depends on engine code that does not exist yet)
- [NOTE] Writes to a `Werkstueck` land on the wrapper, not on the real object. — `rudersdorf/werkbank.py:355-429`
  Failure: an engine statement such as `effekt.rest = 0` (or the learner's code setting an attribute on a wrapped object it was passed) shadows the value. Later reads see the wrapper's copy, while the real object's own methods keep using `self.rest`. No caller does this yet.
  Fix: add a `__setattr__` that forwards public names to `_aktives()`, or a docstring rule that wrapped objects are never written from outside.
  Confidence: 40
- [NOTE] When `STRATEGIEN` is not a dict, the error is filed under mission 7, but `STRATEGIEN` is mission 8's own deliverable as well as mission 7's. — `rudersdorf/werkbank.py:629`, `rudersdorf/missionen.py:56,60`
  Failure: `mission_von` returns the first mission whose `namen` contain `STRATEGIEN`, which is 7. A learner who breaks the table while working on mission 8 is sent back to mission 7. Evidence decision 10 says this is deliberate, so it is a judgement call.
  Fix: none needed if intended. Otherwise pass mission 8 explicitly.
  Confidence: 30

What I checked and found sound:
- **Registries:** `FAEHIGKEITEN` and `ABHAENGIG` are built from `MISSIONEN`, with no self-edges and no duplicates.
- **Openness:** `ist_offen` propagates transitively. `wartet_auf` follows its documented decision.
- **Errors:** the `versuche` paths are sound (`NochOffen` → open; `Lernfehler` passes through; other errors are located at the innermost frame inside the workshop, otherwise at the first line of `anfang` or `ziel`). The `Lernfehler` argument order matches `rudersdorf/fehler.py`.
- **Loading:** `_lade_modul` treats a module as missing only when the missing name is the module itself. A syntax error is located at its own file and line. The rollback restores `sys.modules`.
- **Strategies:** `functools.wraps` keeps the original strategy findable through `__wrapped__`.
- **Other functions:** `waehle_paket` and `ersatz_fuer` behave as documented.
- **Probes:** they run without a time guard, which plan.md:153 says is deliberate. Every probe builds fresh inputs.
- **Tests and layering:** `tests/kern/test_werkbank.py` does not appear in `git diff d3ab51f..HEAD --stat`, so it is unchanged. `werkbank.py` and `ersatz.py` do not import pygame.

## Could not check
- I did not run `make check`, the focused tests or the mutation script. Evidence row 17 and the FINAL `make check` are still marked pending in `specs/001-rudersdorf-2/evidence/T005.md:39,52`, so the closing sensor run is not recorded.
- The mutation script `mutanten.py` and its copy live outside the repository, so I could not verify the M01–M48 results.
- The round-1 review leg under `specs/001-rudersdorf-2/reviews/L-tasks/T005/` (untracked) is earlier review output, which I did not read.
- No engine callers of `rufe`, `erzeuge` or `strategien` exist yet, so the two `Werkstueck` findings are judged against the contract, not against real call sites.
