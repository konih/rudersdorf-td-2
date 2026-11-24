"""Spur B · Die Türme: Auf wen schießt ein Turm zuerst?

Hier liegen die Missionen 7 und 8. Was genau zu tun ist, steht in
missionen/spur_b_tuerme.md. Prüfen:  python pruefen.py 7

Eine Strategie bekommt die Liste der Kandidaten und den Turm und sucht einen Gegner aus.
In Mission 8 erfindest du eine eigene Strategie und trägst sie unten in STRATEGIEN ein.
"""

from math import hypot

from rudersdorf.fehler import NochOffen


def erster(kandidaten, turm):
    """Mission 7: Zielstrategien. Wählt den Gegner, der dem Dorf am nächsten ist."""
    raise NochOffen("Mission 7: Zielstrategien")


def letzter(kandidaten, turm):
    """Mission 7: Zielstrategien. Wählt den Gegner, der noch am weitesten laufen muss."""
    raise NochOffen("Mission 7: Zielstrategien")


def staerkster(kandidaten, turm):
    """Mission 7: Zielstrategien. Wählt den Gegner mit dem meisten Leben."""
    raise NochOffen("Mission 7: Zielstrategien")


def schwaechster(kandidaten, turm):
    """Mission 7: Zielstrategien. Wählt den Gegner mit dem wenigsten Leben."""
    raise NochOffen("Mission 7: Zielstrategien")


def naechster(kandidaten, turm):
    """Mission 7: Zielstrategien. Wählt den Gegner, der dem Turm am nächsten steht."""
    raise NochOffen("Mission 7: Zielstrategien")


# Das Spiel zeigt diese Namen im Menü eines Turms an.
STRATEGIEN = {
    "erster": erster,
    "letzter": letzter,
    "staerkster": staerkster,
    "schwaechster": schwaechster,
    "naechster": naechster,
}
