"""Spur D · Dorf und Magie: Rudersdorf wächst von der Holzkapelle bis zur Kathedrale.

Hier liegen die Missionen 16 bis 18. Was genau zu tun ist, steht in
missionen/spur_d_dorf_und_magie.md. Prüfen:  python pruefen.py 16

stufen sagt, wie weit jedes Gebäude ausgebaut ist, zum Beispiel {"kirche": 2}.
Ein Gebäude, das dort fehlt, hat Stufe 0.
"""

from rudersdorf.fehler import NochOffen


def fehlende_voraussetzungen(braucht, stufen):
    """Mission 16: Was fehlt noch? Listet auf, welche Gebäude für einen Ausbau noch fehlen."""
    raise NochOffen("Mission 16: Was fehlt noch?")


def sammle_boni(stufen, katalog):
    """Mission 17: Die Kraft des Dorfes. Zählt die Boni aller gebauten Stufen zusammen."""
    raise NochOffen("Mission 17: Die Kraft des Dorfes")


def bauplan(gebaeude, stufe, stufen, katalog):
    """Mission 18: Der Bauplan. Liefert, was der Reihe nach gebaut werden muss."""
    raise NochOffen("Mission 18: Der Bauplan")
