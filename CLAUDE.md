# Rudersdorf 2 — notes for agents

A tower-defense learning game in Python (pygame-ce). A child solves missions in `werkstatt/`;
the complete reference is `loesung/`. Read `.specify/memory/constitution.md` before changing code.

## Commands

| Purpose | Command |
| --- | --- |
| Install | `uv sync` |
| Lint and format check | `make lint` |
| Apply formatting | `make format` |
| Fast tests (reference, no window) | `make test` |
| One test file | `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy RUDERSDORF_LOESUNG=1 uv run python -m unittest tests.kern.test_spiel -v` |
| Slow tests (whole matches) | `make test-lang` |
| Performance figures | `make bench` |
| Gate before every commit | `make check` |
| Play the reference | `uv run python spielen.py --loesung` |
| Learner test runner | `uv run python pruefen.py 3` |

## Rules that are easy to break

- German for everything a learner reads, including identifiers. English only under `specs/`.
- `rudersdorf/kern`, `rudersdorf/labor`, `werkstatt`, `loesung` never import `pygame`.
- `werkstatt/` ships unsolved (`raise NochOffen(...)`); never copy reference code into it.
- A cell is `(spalte, zeile)`; the grid is indexed `raster[zeile][spalte]`.
- Tests are `unittest`, run headless, and never open a real window or sound device.
- No third-party assets. No new runtime dependency.
- Commit messages: Conventional Commits, no trailers, no mention of tools or assistants.
