"""Spur B · Die Türme: Die Türme lernen zu sehen, zu treffen und stärker zu werden.

Hier liegen die Missionen 6, 9 und 10 (7 und 8 stehen in strategien.py). Was genau zu
tun ist, steht in missionen/spur_b_tuerme.md. Prüfen:  python pruefen.py 6

Ein Punkt ist ein Paar (x, y). Jeder Gegner kennt sein x, sein y und sein leben.
"""

from math import hypot

from rudersdorf.fehler import NochOffen


def in_reichweite(position, reichweite, gegner):
    """Mission 6: Wer ist in Reichweite? Liefert die lebenden Gegner, die nah genug sind."""
    raise NochOffen("Mission 6: Wer ist in Reichweite?")


def kettenblitz(start, gegner, spruenge, sprungweite):
    """Mission 9: Der Kettenblitz. Liefert, wen der Blitz der Reihe nach trifft."""
    raise NochOffen("Mission 9: Der Kettenblitz")


def wende_ausbau_an(werte, ausbau):
    """Mission 10: Die Turmschmiede. Rechnet aus den Werten eines Turms die verbesserten."""
    raise NochOffen("Mission 10: Die Turmschmiede")
