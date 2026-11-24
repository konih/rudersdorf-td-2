"""Referenz zu Spur A · Das Raster (Missionen 1 bis 5).

Hier entsteht die vollständige Lösung. Solange eine Mission noch nicht gebaut ist,
meldet sie sich als offen, und das Spiel benutzt den Ersatz.
"""

from rudersdorf.fehler import NochOffen


def lies_karte(text):
    """Mission 1: Die Karte lesen. Macht aus dem Kartentext ein Raster aus Zeichen."""
    raise NochOffen("Referenz folgt: Mission 1")


def finde(raster, zeichen):
    """Mission 1: Die Karte lesen. Sucht alle Zellen, in denen dieses Zeichen steht."""
    raise NochOffen("Referenz folgt: Mission 1")


def nachbarn(zelle, breite, hoehe):
    """Mission 2: Nachbarn. Liefert die Zellen oben, rechts, unten und links von der Zelle."""
    raise NochOffen("Referenz folgt: Mission 2")


def ist_begehbar(raster, zelle, gesperrt):
    """Mission 2: Nachbarn. Sagt, ob ein Ork diese Zelle betreten kann."""
    raise NochOffen("Referenz folgt: Mission 2")


def abstandskarte(raster, ziel, gesperrt):
    """Mission 3: Der kürzeste Weg. Zählt für jede Zelle die Schritte bis zum Ziel."""
    raise NochOffen("Referenz folgt: Mission 3")


def naechster_schritt(abstaende, zelle, breite, hoehe):
    """Mission 4: Dem Weg folgen. Wählt die Nachbarzelle, die näher am Ziel liegt."""
    raise NochOffen("Referenz folgt: Mission 4")


def darf_bauen(raster, zelle, gesperrt, starts, ziel, besetzt):
    """Mission 5: Nicht einmauern! Erlaubt ein Bauwerk nur, wenn alle Wege offen bleiben."""
    raise NochOffen("Referenz folgt: Mission 5")
