# Quickstart: Rudersdorf 2

## For the developer

```sh
uv sync                 # create .venv with pygame-ce and ruff
make check              # lint + fast tests against the reference, no window
make test-lang          # whole matches, winnability (slow)
make bench              # performance figures
uv run python spielen.py --loesung        # play the reference
uv run python -m rudersdorf.ansicht.vorschau docs/bilder   # render preview images headless
```

One test file:

```sh
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy RUDERSDORF_LOESUNG=1 \
  uv run python -m unittest tests.kern.test_spiel -v
```

## For the learner (what the start page will say)

```sh
python -m pip install pygame-ce
python spielen.py       # runs at once, with stand-ins for every open mission
python pruefen.py       # mission board and suggested next mission
python pruefen.py 3     # test mission 3
```

In the game: `F5` reloads the workshop after a change, `Tab` shows the mission board, `F1` shows
the route distances your own code computed.

## Checking the feature by hand

1. `uv run python spielen.py` with an untouched `werkstatt/`: the game starts, labels name the
   active stand-ins, three waves play without an error panel (US2).
2. `uv run python spielen.py --loesung`: build a wall with one gap and watch the orcs re-route;
   try to close the gap and read the refusal (US1).
3. Raise the church to stage 5 over a match and compare the five pictures (US3); cast every spell
   (US4); meet a harpy, a shaman, a slime, a breaker and the orc king (US5).
4. `uv run python labor.py --spiele 20 --schwierigkeit normal --loesung` prints a results table (US7).
