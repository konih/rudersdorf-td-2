"""Hilfen für die Missionstests: das richtige Paket laden, Karten zeichnen, klar melden.

Jede Meldung eines Missionstests hat drei Teile:

    Erwartet: was herauskommen sollte
    Bekommen: was dein Code geliefert hat
    Tipp: ein Hinweis, wo du suchen kannst

Geprüft wird die Werkstatt. Nur mit RUDERSDORF_LOESUNG=1 wird stattdessen die Lösung geprüft.
"""

import importlib
import unittest

from rudersdorf.fehler import NochOffen
from rudersdorf.werkbank import waehle_paket

# ---------------------------------------------------------------------------------------
# 1. Das Paket wählen
# ---------------------------------------------------------------------------------------


def lade_modul(name):
    """Lädt das Modul ``name`` aus dem Paket, das geprüft wird (``werkstatt`` oder ``loesung``)."""
    return importlib.import_module(f"{waehle_paket()}.{name}")


# ---------------------------------------------------------------------------------------
# 2. Meldungen
# ---------------------------------------------------------------------------------------


def meldung(erwartet, bekommen, tipp):
    """Baut die Meldung aus drei Teilen. Sie beginnt in einer neuen Zeile, damit man sie findet."""
    return f"\nErwartet: {erwartet}\nBekommen: {bekommen}\nTipp: {tipp}"


def nur_die_reihenfolge_ist_anders(bekommen, erwartet):
    """Sagt, ob ``bekommen`` dieselben Einträge hat wie die Liste ``erwartet``, nur anders gereiht.

    Die Funktion kommt mit jeder Antwort zurecht, auch mit ``None`` oder einer Liste, in der
    etwas Unpassendes steht. Dann ist die Antwort einfach ``False``.
    """
    if not isinstance(bekommen, list) or len(bekommen) != len(erwartet):
        return False
    if bekommen == erwartet:
        return False
    return all(eintrag in bekommen for eintrag in erwartet)


class Missionstest(unittest.TestCase):
    """Die Grundlage aller Missionstests: lädt das Modul und meldet Fehler in drei Teilen."""

    modul = "raster"  # so heißt die Datei in der Werkstatt, ohne ".py"
    longMessage = False  # nur unsere eigene Meldung zeigen, nicht noch eine englische davor

    def setUp(self):
        self.werkstatt = lade_modul(self.modul)

    def pruefe_gleich(self, bekommen, erwartet, aufruf, tipp):
        """Meldet einen Fehler, wenn ``bekommen`` nicht genau ``erwartet`` ist."""
        if bekommen != erwartet:
            self.fail(meldung(f"{aufruf} ergibt {erwartet!r}", repr(bekommen), tipp))

    def pruefe_fehler(self, fehlerart, aufruf, tipp, funktion, *argumente):
        """Ruft ``funktion`` auf und verlangt, dass sie einen Fehler dieser Art meldet."""
        erwartet = f"{aufruf} meldet einen {fehlerart.__name__}"
        try:
            ergebnis = funktion(*argumente)
        except NochOffen:
            raise
        except fehlerart:
            return
        except Exception as fehler:
            self.fail(meldung(erwartet, f"ein {type(fehler).__name__}: {fehler}", tipp))
        self.fail(meldung(erwartet, f"kein Fehler, sondern das Ergebnis {ergebnis!r}", tipp))

    def rufe_sicher(self, aufruf, tipp, funktion, *argumente):
        """Ruft ``funktion`` auf. Stürzt sie ab, gibt es eine Meldung mit Tipp statt nur den Absturz."""
        try:
            return funktion(*argumente)
        except NochOffen:
            raise
        except Exception as fehler:
            self.fail(
                meldung(
                    f"{aufruf} läuft ohne Absturz durch",
                    f"ein {type(fehler).__name__}: {fehler}",
                    tipp,
                )
            )

    def pruefe_unveraendert(self, vorher, nachher, was, aufruf, tipp):
        """Meldet einen Fehler, wenn der Aufruf etwas verändert hat, das ihm nur geliehen war."""
        if vorher != nachher:
            self.fail(
                meldung(
                    f"{aufruf} lässt {was} so, wie es war: {vorher!r}",
                    f"danach war {was} {nachher!r}",
                    tipp,
                )
            )

    def pruefe_abstaende(self, bekommen, erwartet, aufruf, tipp):
        """Vergleicht zwei Abstandskarten und nennt die erste Zelle, die nicht stimmt."""
        if not isinstance(bekommen, dict):
            self.fail(
                meldung(
                    f"{aufruf} ergibt ein Wörterbuch von Zelle zu Abstand",
                    repr(bekommen),
                    "Die Abstandskarte ist ein dict. Der Schlüssel ist die Zelle (spalte, zeile), "
                    "der Wert die Zahl der Schritte bis zum Ziel.",
                )
            )
        for zelle in sorted(erwartet, key=lambda z: (z[1], z[0])):
            if zelle not in bekommen:
                self.fail(
                    meldung(
                        f"{aufruf}: Zelle {zelle} hat den Abstand {erwartet[zelle]}",
                        f"Zelle {zelle} fehlt in der Abstandskarte",
                        tipp,
                    )
                )
            if bekommen[zelle] != erwartet[zelle]:
                self.fail(
                    meldung(
                        f"{aufruf}: Zelle {zelle} hat den Abstand {erwartet[zelle]}",
                        f"Zelle {zelle} hat den Abstand {bekommen[zelle]!r}",
                        tipp,
                    )
                )
        zu_viel = sorted((zelle for zelle in bekommen if zelle not in erwartet), key=repr)
        if zu_viel:
            zelle = zu_viel[0]
            self.fail(
                meldung(
                    f"{aufruf}: Zelle {zelle} steht nicht in der Abstandskarte, "
                    "weil von dort kein Weg zum Ziel führt",
                    f"Zelle {zelle} hat den Abstand {bekommen[zelle]!r}",
                    tipp,
                )
            )


# ---------------------------------------------------------------------------------------
# 3. Karten und Abstandskarten als Text zeichnen
# ---------------------------------------------------------------------------------------


def raster_aus(bild):
    """Macht aus einer gezeichneten Karte ein Raster. Eingerückte Zeilen sind erlaubt.

    Das benutzen die Tests ab Mission 2, damit sie nicht von Mission 1 abhängen.
    """
    return [list(zeile.strip()) for zeile in bild.strip().splitlines()]


def abstaende_aus(bild):
    """Macht aus gezeichneten Zahlen eine Abstandskarte: ``{(spalte, zeile): abstand}``.

    Die Einträge einer Zeile sind durch Leerzeichen getrennt. Wo keine Zahl steht (zum Beispiel
    ``#`` für Fels oder ``-`` für "nicht erreichbar"), bekommt die Zelle keinen Eintrag.
    """
    abstaende = {}
    for zeile, text in enumerate(bild.strip().splitlines()):
        for spalte, eintrag in enumerate(text.split()):
            if eintrag.isdigit():
                abstaende[(spalte, zeile)] = int(eintrag)
    return abstaende


# ---------------------------------------------------------------------------------------
# 4. Ein Gegner zum Testen
# ---------------------------------------------------------------------------------------


class TestGegner:
    """Ein Gegner nur für Tests. Er hat genau das, was Code der Werkstatt von Gegnern benutzt.

    Er schreibt mit, was mit ihm geschieht: ``schaeden`` ist die Liste aller ``(menge, art)``,
    ``heilungen`` die Liste aller Mengen. Resistenzen kennt er nicht, er zieht die Menge so ab,
    wie sie kommt.
    """

    def __init__(
        self, leben=100.0, x=0.0, y=0.0, rest_weg=0.0, max_leben=None, fliegt=False, ist_boss=False
    ):
        self.leben = leben
        self.max_leben = leben if max_leben is None else max_leben
        self.x = x
        self.y = y
        self.rest_weg = rest_weg
        self.effekte = []
        self.fliegt = fliegt
        self.ist_boss = ist_boss
        self.schaeden = []
        self.heilungen = []

    def erleide_schaden(self, menge, art):
        """Zieht Leben ab, nie unter 0, und liefert, wie viel Leben wirklich verloren ging."""
        self.schaeden.append((menge, art))
        verloren = min(self.leben, max(menge, 0))
        self.leben -= verloren
        return verloren

    def heile(self, menge):
        """Gibt Leben zurück, nie über ``max_leben`` hinaus."""
        self.heilungen.append(menge)
        self.leben = min(self.max_leben, self.leben + max(menge, 0))

    def __repr__(self):
        return f"TestGegner(leben={self.leben}, x={self.x}, y={self.y}, rest_weg={self.rest_weg})"
