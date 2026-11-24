"""Referenz zu Spur E · Die Werkstatt (Mission 24).

Hier entsteht die vollständige Lösung. Solange eine Mission noch nicht gebaut ist,
meldet sie sich als offen, und das Spiel benutzt den Ersatz.
"""

from rudersdorf.fehler import NochOffen


def zu_daten(zustand):
    """Mission 24: Der Dorfschreiber. Macht aus dem Spielzustand Daten, die in eine Datei passen."""
    raise NochOffen("Referenz folgt: Mission 24")


def aus_daten(daten):
    """Mission 24: Der Dorfschreiber. Prüft gelesene Daten und baut daraus den Spielzustand."""
    raise NochOffen("Referenz folgt: Mission 24")
