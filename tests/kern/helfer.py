"""Helfer für die Tests des Spielkerns: kleine Karten zeichnen, Partien bauen, Wege nachrechnen.

Die Tests kennen von der Partie nur, was der Plan festlegt: ``Spiel(...)``, seine Methoden und
die Eigenschaften von Gegnern, Bauwerken und Dorf. Zeit vergeht nur durch ``schritt``.
"""

import importlib
import itertools
import os
import pathlib
import sys
import tempfile

from rudersdorf import daten
from rudersdorf.kern.spiel import Spiel
from rudersdorf.werkbank import Werkbank

FELD_SPALTEN = daten.SPALTEN - daten.DORF_SPALTEN  # so viele Spalten gehören nicht dem Dorf
GENAU = 1e-6  # so nah müssen Pixel und Strecken an der Rechnung liegen

# ---------------------------------------------------------------------------------------
# 1. Karten zeichnen
# ---------------------------------------------------------------------------------------


def karte_aus(bild, rand="#"):
    """Macht aus einer kleinen Zeichnung den Text einer ganzen Karte.

    Die Zeichnung ist die linke obere Ecke der Karte: Die Zelle ``(spalte, zeile)`` der
    Zeichnung ist dieselbe Zelle der Karte. Was rechts und unten fehlt, wird mit ``rand``
    aufgefüllt (Fels, wenn nichts anderes gesagt ist), und ganz rechts kommt das Dorf dazu.
    """
    zeilen = [zeile.strip() for zeile in bild.strip().splitlines()]
    if len(zeilen) > daten.ZEILEN:
        raise AssertionError(
            f"Die Zeichnung hat {len(zeilen)} Zeilen, erlaubt sind {daten.ZEILEN}."
        )
    fertig = []
    for nummer in range(daten.ZEILEN):
        zeile = zeilen[nummer] if nummer < len(zeilen) else ""
        if len(zeile) > FELD_SPALTEN:
            raise AssertionError(
                f"Zeile {nummer + 1} der Zeichnung ist breiter als {FELD_SPALTEN}."
            )
        fertig.append(zeile + rand * (FELD_SPALTEN - len(zeile)) + "D" * daten.DORF_SPALTEN)
    return "\n".join(fertig) + "\n"


def raster_von(bild, rand="#"):
    """Wie ``karte_aus``, aber gleich als Raster: eine Liste von Zeilen aus einzelnen Zeichen."""
    return [list(zeile) for zeile in karte_aus(bild, rand).splitlines()]


def zeilen_von(raster):
    """Liefert die Zeilen eines Rasters als Texte, egal ob es Listen oder Texte enthält."""
    return ["".join(zeile) for zeile in raster]


# ---------------------------------------------------------------------------------------
# 2. Partien bauen
# ---------------------------------------------------------------------------------------


def partie(bild, rand="#", werkbank=None, schwierigkeit="normal"):
    """Baut eine Partie auf der gezeichneten Karte, ohne andere Angabe mit der Lösung."""
    if werkbank is None:
        werkbank = Werkbank("loesung")
    return Spiel(werkbank, schwierigkeit=schwierigkeit, kartentext=karte_aus(bild, rand))


def reich(spiel, gold=10_000, stein=10_000):
    """Gibt dem Dorf so viel Gold und Stein, dass der Preis im Test keine Rolle spielt."""
    spiel.dorf.vorraete["gold"] = gold
    spiel.dorf.vorraete["stein"] = stein
    return spiel


def ereignisse(spiel, art):
    """Holt alle Ereignisse ab und liefert die mit dieser Art."""
    return [ereignis for ereignis in spiel.hole_ereignisse() if ereignis["art"] == art]


def ist_dabei(spiel, gegner):
    """Sagt, ob genau dieser Gegner noch in der Partie ist."""
    return any(anderer is gegner for anderer in spiel.gegner)


def laufe(spiel, schritte, dt=daten.DT):
    """Rechnet die Partie um so viele Schritte weiter."""
    for _ in range(schritte):
        spiel.schritt(dt)


def schritte_fuer(strecke, tempo, dt=daten.DT):
    """So viele ganze Schritte braucht ein Gegner mit diesem Tempo ungefähr für die Strecke."""
    return round(strecke / tempo / dt)


# ---------------------------------------------------------------------------------------
# 3. Wege nachrechnen
# ---------------------------------------------------------------------------------------


def mitte(zelle):
    """Der Mittelpunkt einer Zelle in Pixeln, hier noch einmal unabhängig vom Spiel gerechnet."""
    spalte, zeile = zelle
    return (spalte * daten.ZELLE + daten.ZELLE / 2, zeile * daten.ZELLE + daten.ZELLE / 2)


def zelle_unter(x, y):
    """Die Zelle, über der dieser Punkt liegt."""
    return (int(x // daten.ZELLE), int(y // daten.ZELLE))


def punkt_auf_weg(zellen, strecke):
    """Der Punkt, an dem man steht, wenn man von der Mitte der ersten Zelle aus ``strecke``
    Pixel weit von Mitte zu Mitte durch die Zellen gelaufen ist."""
    rest = strecke
    for von, nach in zip(zellen, zellen[1:], strict=False):
        if rest <= daten.ZELLE:
            x, y = mitte(von)
            return (x + (nach[0] - von[0]) * rest, y + (nach[1] - von[1]) * rest)
        rest = rest - daten.ZELLE
    raise AssertionError(f"Der Weg {zellen} ist kürzer als {strecke} Pixel.")


def auf_linie(x, y):
    """Sagt, ob der Punkt auf einer Linie durch Zellmitten liegt (waagerecht oder senkrecht).

    Wer nur von Mitte zu Mitte zwischen Nachbarzellen läuft, steht immer auf so einer Linie.
    Wer schräg läuft oder eine Ecke abschneidet, verlässt sie.
    """
    for wert in (x, y):
        neben = (wert - daten.ZELLE / 2) % daten.ZELLE
        if min(neben, daten.ZELLE - neben) <= GENAU:
            return True
    return False


def fehler_im_weg(zellen, abstaende):
    """Prüft, ob die Zellen ein kürzester Weg nach dieser Abstandskarte sind.

    Liefert ``None``, wenn jeder Schritt zu einer Nachbarzelle führt, deren Abstand genau um
    eins kleiner ist. Sonst kommt ein Satz zurück, der den ersten falschen Schritt nennt.
    """
    for von, nach in zip(zellen, zellen[1:], strict=False):
        if abs(von[0] - nach[0]) + abs(von[1] - nach[1]) != 1:
            return f"Der Schritt von {von} nach {nach} führt nicht zu einer Nachbarzelle."
        if von not in abstaende or nach not in abstaende:
            return f"Der Schritt von {von} nach {nach} berührt eine Zelle ohne Abstand."
        if abstaende[nach] != abstaende[von] - 1:
            return (
                f"Der Schritt von {von} (Abstand {abstaende[von]}) nach {nach} "
                f"(Abstand {abstaende[nach]}) führt nicht um eins näher ans Ziel."
            )
    return None


class Spur:
    """Was die Tests über den Lauf eines Gegners mitschreiben."""

    def __init__(self, gegner):
        self.gegner = gegner
        self.punkte = [(gegner.x, gegner.y)]

    def merke(self):
        self.punkte.append((self.gegner.x, self.gegner.y))

    def zellen(self):
        """Die Zellen, über die der Gegner gelaufen ist; jede so oft, wie er sie betreten hat."""
        ergebnis = []
        for x, y in self.punkte:
            zelle = zelle_unter(x, y)
            if not ergebnis or ergebnis[-1] != zelle:
                ergebnis.append(zelle)
        return ergebnis

    def neben_der_linie(self):
        """Alle Punkte, an denen der Gegner schräg unterwegs war."""
        return [punkt for punkt in self.punkte if not auf_linie(*punkt)]


def verfolge(spiel, gegner, schritte, dt=daten.DT):
    """Rechnet höchstens ``schritte`` weiter und schreibt den Lauf dieser Gegner mit.

    Aufgehört wird früher, sobald keiner von ihnen mehr in der Partie ist. Zurück kommt zu
    jedem Gegner eine ``Spur``, in derselben Reihenfolge.
    """
    spuren = [Spur(einer) for einer in gegner]
    for _ in range(schritte):
        if not any(ist_dabei(spiel, spur.gegner) for spur in spuren):
            break
        spiel.schritt(dt)
        for spur in spuren:
            if ist_dabei(spiel, spur.gegner):
                spur.merke()
    return spuren


# ---------------------------------------------------------------------------------------
# 4. Ein Paket wie die Lösung, mit einzelnen eigenen Funktionen
# ---------------------------------------------------------------------------------------

_NUMMERN = itertools.count(1)


def paket_wie_loesung(test, eigenes):
    """Baut ein Wegwerf-Paket, das sich wie die Lösung verhält, bis auf ``eigenes``.

    ``eigenes`` ist ``{modul: quelltext}``. Der Quelltext steht hinter den Namen der Lösung
    und ersetzt deshalb gleichnamige Funktionen. Zurück kommt der Name des Pakets für
    ``Werkbank(name)``; nach dem Test verschwindet das Paket wieder.
    """
    name = f"kern_probe_{os.getpid()}_{next(_NUMMERN)}"
    wurzel = tempfile.TemporaryDirectory()
    ordner = pathlib.Path(wurzel.name) / name
    ordner.mkdir()
    (ordner / "__init__.py").write_text('"""Ein Probe-Paket."""\n', encoding="utf-8")
    vorlage = pathlib.Path(importlib.import_module("loesung").__file__).parent
    for datei in sorted(vorlage.glob("*.py")):
        if datei.name == "__init__.py":
            continue
        text = f'"""Wie die Lösung."""\n\nfrom loesung.{datei.stem} import *  # noqa: F403\n'
        text = text + "\n\n" + eigenes.get(datei.stem, "")
        (ordner / datei.name).write_text(text, encoding="utf-8")
    sys.path.insert(0, wurzel.name)
    importlib.invalidate_caches()

    def raeume_auf():
        if wurzel.name in sys.path:
            sys.path.remove(wurzel.name)
        for modul in list(sys.modules):
            if modul == name or modul.startswith(name + "."):
                del sys.modules[modul]
        importlib.invalidate_caches()
        wurzel.cleanup()

    test.addCleanup(raeume_auf)
    return name
