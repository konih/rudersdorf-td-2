# Rudersdorf 2 Constitution

Rudersdorf 2 is a tower-defense game that a child learns Python with. Every rule below exists
to protect one of two things: the learner's experience, or the ability to change the game safely.

## Core Principles

### I. The learner comes first

- All text a learner reads is German: game text, mission documents, test messages, identifiers
  and comments in `werkstatt/`, `loesung/` and the engine. Specification documents under `specs/`
  are English.
- The learner's workspace is `werkstatt/`. It MUST ship unsolved: every mission function or method
  body raises `NochOffen`. The one exception is the craft missions whose subject is existing code
  (the bug hunt, the clean-up and the own-tests mission): they ship deliberately faulty, untidy or
  incomplete, because repairing them is the mission. The complete reference lives in `loesung/`
  with the same module names, the same public names and the same signatures.
- The reference is NEVER loaded silently. Only the explicit `--loesung` switch (or the
  `RUDERSDORF_LOESUNG=1` variable used by developer tooling) selects it.
- Mission tests check behaviour, never the shape of the source code. The only exceptions are the
  refactoring mission and the own-tests mission, whose subject is the source itself.
- Reference solutions use only language features the mission documents have introduced. A
  clever one-liner that a learner could not have written is a defect.

### II. Always playable, never secretly solved

- The game MUST start and run a full match with every mission unsolved.
- An unsolved capability is replaced by an *Ersatz*: a deliberately simple behaviour that is
  visibly worse than the real one and is labelled on screen with the mission that replaces it.
  An Ersatz MUST NOT be the reference behaviour or an equivalent of it.
- A genuine error in learner code MUST NOT crash the game: the match pauses and the screen names
  the file, the line and the message. The traceback also goes to the terminal.

### III. The core is pure and deterministic

- `rudersdorf/kern/`, `rudersdorf/labor/`, `werkstatt/` and `loesung/` MUST NOT import `pygame`.
  `rudersdorf/kern/` MUST NOT import `rudersdorf/ansicht/`.
- The simulation advances only through `Spiel.schritt(dt)` with a fixed time step. Given the same
  seed, map, difficulty and sequence of actions it MUST produce the same state. Randomness comes
  only from the `random.Random` instance the match owns.
- Drawing, animation and sound MUST NOT change the simulation state. They read state and events.

### IV. Tests first, standard library only

- Tests use `unittest` from the standard library, so a learner needs nothing beyond `pygame-ce`.
- Behaviour is specified by tests written before the implementation. A test task closes on a
  verified red; an implementation task turns it green without editing the test.
- All tests run without a display (`SDL_VIDEODRIVER=dummy`). A test that needs a real window or
  a real sound device is not allowed.
- `make check` (lint plus fast tests against the reference) MUST be green on every commit,
  except for tests listed as known red by a test task that a later task turns green.

### V. Content is data

- Towers, enemies, spells, village buildings, difficulty levels and waves are described in
  `rudersdorf/daten.py` and in map files under `karten/`. Adding a variant of an existing kind
  MUST be possible by editing data only.
- The only runtime dependency is `pygame-ce`. Graphics are drawn in code and sounds are
  synthesised in code; the repository contains no third-party image, font or sound files.

### VI. Simple enough to read

- A learner who has finished the missions should be able to read the engine. Prefer plain
  functions, small classes and explicit loops over metaprogramming, decorators with hidden
  behaviour, or deep inheritance.
- No abstraction without two real uses. No configuration option without a user-visible reason.

## Quality gates

| Gate | Command | When |
| --- | --- | --- |
| Style and format | `make lint` | after every edit |
| Fast tests against the reference | `make test` | every commit |
| Layering, parity and unsolved-workshop checks | part of `make test` (`tests/architektur/`) | every commit |
| Whole matches and winnability | `make test-lang` | balance and release tasks |
| Performance figures | `make bench` | performance tasks |

Allow-lists and baselines in the architecture and performance tests may only become stricter.
Loosening one is a decision for the owner.

## Governance

This constitution overrides other project guidance. A change to it needs the owner's approval
and a note in the commit message saying what changed and why. Commits carry only the change's
own content: no co-author trailers and no mention of tools or assistants.

**Version**: 1.1.0 | **Ratified**: 2026-11-24 | **Last Amended**: 2026-11-24
