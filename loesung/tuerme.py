"""Referenz zu Spur B · Die Türme (Missionen 6, 9 und 10).

Hier entsteht die vollständige Lösung. Solange eine Mission noch nicht gebaut ist,
meldet sie sich als offen, und das Spiel benutzt den Ersatz.
"""

from rudersdorf.fehler import NochOffen


def in_reichweite(position, reichweite, gegner):
    """Mission 6: Wer ist in Reichweite? Liefert die lebenden Gegner, die nah genug sind."""
    raise NochOffen("Referenz folgt: Mission 6")


def kettenblitz(start, gegner, spruenge, sprungweite):
    """Mission 9: Der Kettenblitz. Liefert, wen der Blitz der Reihe nach trifft."""
    raise NochOffen("Referenz folgt: Mission 9")


def wende_ausbau_an(werte, ausbau):
    """Mission 10: Die Turmschmiede. Rechnet aus den Werten eines Turms die verbesserten."""
    raise NochOffen("Referenz folgt: Mission 10")
