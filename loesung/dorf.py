"""Referenz zu Spur D · Dorf und Magie (Missionen 16 bis 18).

Hier entsteht die vollständige Lösung. Solange eine Mission noch nicht gebaut ist,
meldet sie sich als offen, und das Spiel benutzt den Ersatz.
"""

from rudersdorf.fehler import NochOffen


def fehlende_voraussetzungen(braucht, stufen):
    """Mission 16: Was fehlt noch? Listet auf, welche Gebäude für einen Ausbau noch fehlen."""
    raise NochOffen("Referenz folgt: Mission 16")


def sammle_boni(stufen, katalog):
    """Mission 17: Die Kraft des Dorfes. Zählt die Boni aller gebauten Stufen zusammen."""
    raise NochOffen("Referenz folgt: Mission 17")


def bauplan(gebaeude, stufe, stufen, katalog):
    """Mission 18: Der Bauplan. Liefert, was der Reihe nach gebaut werden muss."""
    raise NochOffen("Referenz folgt: Mission 18")
