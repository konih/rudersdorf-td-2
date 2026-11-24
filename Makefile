# Rudersdorf 2 — Entwicklerbefehle. Lernende brauchen nur: python spielen.py / python pruefen.py
export SDL_VIDEODRIVER ?= dummy
export SDL_AUDIODRIVER ?= dummy
export RUDERSDORF_LOESUNG ?= 1
PY := uv run python

.PHONY: lint format test test-lang bench check
lint: ## Stil und Format prüfen
	uv run ruff check .
	uv run ruff format --check .

format: ## Format anwenden
	uv run ruff format .
	uv run ruff check --fix .

test: ## Schnelle Tests gegen die Referenzlösung (ohne Fenster)
	$(PY) -m unittest discover -s tests -t . -p "test_*.py"

test-lang: ## Langsame Tests: ganze Partien, Gewinnbarkeit (Dateien lang_*.py)
	$(PY) -m unittest discover -s tests -t . -p "lang_*.py"

bench: ## Leistungsmessung ausgeben
	$(PY) -m rudersdorf.labor.messung

check: lint test ## Alles, was vor jedem Commit grün sein muss
