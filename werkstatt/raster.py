"""Spur A · Das Raster: Das Spiel lernt, die Karte zu lesen und Wege zu finden.

Hier liegen die Missionen 1 bis 5. Was genau zu tun ist, steht in
missionen/spur_a_raster.md. Ob eine Mission stimmt, zeigt dir:  python pruefen.py 1

Eine Zelle ist ein Paar (spalte, zeile). Das Raster ist eine Liste von Zeilen,
du liest es mit raster[zeile][spalte].
"""

from collections import deque

from rudersdorf.daten import BEBAUBAR, BEGEHBAR
from rudersdorf.fehler import NochOffen


def lies_karte(text):
    """Mission 1: Die Karte lesen. Macht aus dem Kartentext ein Raster aus Zeichen."""
    raise NochOffen("Mission 1: Die Karte lesen")


def finde(raster, zeichen):
    """Mission 1: Die Karte lesen. Sucht alle Zellen, in denen dieses Zeichen steht."""
    raise NochOffen("Mission 1: Die Karte lesen")


def nachbarn(zelle, breite, hoehe):
    """Mission 2: Nachbarn. Liefert die Zellen oben, rechts, unten und links von der Zelle."""
    raise NochOffen("Mission 2: Nachbarn")


def ist_begehbar(raster, zelle, gesperrt):
    """Mission 2: Nachbarn. Sagt, ob ein Ork diese Zelle betreten kann."""
    raise NochOffen("Mission 2: Nachbarn")


def abstandskarte(raster, ziel, gesperrt):
    """Mission 3: Der kürzeste Weg. Zählt für jede Zelle die Schritte bis zum Ziel."""
    raise NochOffen("Mission 3: Der kürzeste Weg")


def naechster_schritt(abstaende, zelle, breite, hoehe):
    """Mission 4: Dem Weg folgen. Wählt die Nachbarzelle, die näher am Ziel liegt."""
    raise NochOffen("Mission 4: Dem Weg folgen")


def darf_bauen(raster, zelle, gesperrt, starts, ziel, besetzt):
    """Mission 5: Nicht einmauern! Erlaubt ein Bauwerk nur, wenn alle Wege offen bleiben."""
    raise NochOffen("Mission 5: Nicht einmauern!")
