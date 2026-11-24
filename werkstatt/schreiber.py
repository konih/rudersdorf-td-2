"""Spur E · Die Werkstatt: Der Dorfschreiber speichert das Spiel und lädt es wieder.

Hier liegt die Mission 24. Was genau zu tun ist, steht in
missionen/spur_e_werkstatt.md. Prüfen:  python pruefen.py 24
"""

from rudersdorf.fehler import NochOffen


def zu_daten(zustand):
    """Mission 24: Der Dorfschreiber. Macht aus dem Spielzustand Daten, die in eine Datei passen."""
    raise NochOffen("Mission 24: Der Dorfschreiber")


def aus_daten(daten):
    """Mission 24: Der Dorfschreiber. Prüft gelesene Daten und baut daraus den Spielzustand."""
    raise NochOffen("Mission 24: Der Dorfschreiber")
