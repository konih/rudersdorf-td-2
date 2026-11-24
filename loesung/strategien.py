"""Referenz zu Spur B · Die Türme (Missionen 7 und 8).

Hier entsteht die vollständige Lösung. Solange eine Mission noch nicht gebaut ist,
meldet sie sich als offen, und das Spiel benutzt den Ersatz.
"""

from rudersdorf.fehler import NochOffen


def erster(kandidaten, turm):
    """Mission 7: Zielstrategien. Wählt den Gegner, der dem Dorf am nächsten ist."""
    raise NochOffen("Referenz folgt: Mission 7")


def letzter(kandidaten, turm):
    """Mission 7: Zielstrategien. Wählt den Gegner, der noch am weitesten laufen muss."""
    raise NochOffen("Referenz folgt: Mission 7")


def staerkster(kandidaten, turm):
    """Mission 7: Zielstrategien. Wählt den Gegner mit dem meisten Leben."""
    raise NochOffen("Referenz folgt: Mission 7")


def schwaechster(kandidaten, turm):
    """Mission 7: Zielstrategien. Wählt den Gegner mit dem wenigsten Leben."""
    raise NochOffen("Referenz folgt: Mission 7")


def naechster(kandidaten, turm):
    """Mission 7: Zielstrategien. Wählt den Gegner, der dem Turm am nächsten steht."""
    raise NochOffen("Referenz folgt: Mission 7")


# Das Spiel zeigt diese Namen im Menü eines Turms an.
STRATEGIEN = {
    "erster": erster,
    "letzter": letzter,
    "staerkster": staerkster,
    "schwaechster": schwaechster,
    "naechster": naechster,
}
