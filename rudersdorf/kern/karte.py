"""Die Karte des Spiels: prüfen, laden, Zellen und Tore.

Eine Zelle ist ``(spalte, zeile)``; das Raster liest man mit ``raster[zeile][spalte]``.
"""

import pathlib

from rudersdorf import daten
from rudersdorf.fehler import Lernfehler

# Hier liegen die Kartendateien: im Ordner karten/ neben dem Ordner rudersdorf/.
KARTENORDNER = pathlib.Path(daten.__file__).parent.parent / "karten"
# Ab dieser Spalte gehört die Karte dem Dorf.
ERSTE_DORFSPALTE = daten.SPALTEN - daten.DORF_SPALTEN


def pruefe_karte(raster) -> None:
    """Prüft ein Raster nach den Regeln des Spiels; bei einem Fehler: ValueError mit Grund."""
    _pruefe_groesse(raster)
    _pruefe_zeichen(raster)
    dorftore = _suche(raster, "Z")
    if len(dorftore) != 1:
        raise ValueError(
            f"Die Karte braucht genau ein Dorftor (Z), sie hat {len(dorftore)} Dorftore."
        )
    orktore = _suche(raster, "S")
    if len(orktore) == 0:
        raise ValueError("Die Karte braucht mindestens ein Orktor (S), sie hat keines.")
    erreichbar = _erreichbar_von(raster, dorftore[0])
    for orktor in orktore:
        if orktor not in erreichbar:
            raise ValueError(f"Vom Orktor {orktor} führt kein Weg zum Dorftor {dorftore[0]}.")


def _pruefe_groesse(raster):
    """Die Karte hat immer ZEILEN Zeilen mit je SPALTEN Zeichen."""
    if not isinstance(raster, (list, tuple)) or len(raster) == 0:
        raise ValueError("Die Karte ist leer: Sie hat keine einzige Zeile.")
    if len(raster) != daten.ZEILEN:
        raise ValueError(f"Die Karte braucht {daten.ZEILEN} Zeilen, sie hat {len(raster)}.")
    for zeile in raster:
        if not isinstance(zeile, (list, tuple, str)):
            raise ValueError("Jede Zeile der Karte muss eine Liste von Zeichen sein.")
    breite = len(raster[0])
    for nummer, zeile in enumerate(raster, start=1):
        if len(zeile) != breite:
            raise ValueError(
                f"Die Zeilen der Karte sind nicht gleich lang: Zeile {nummer} hat "
                f"{len(zeile)} Zeichen, Zeile 1 hat {breite}."
            )
    if breite != daten.SPALTEN:
        raise ValueError(f"Die Karte braucht {daten.SPALTEN} Spalten, sie hat {breite}.")


def _pruefe_zeichen(raster):
    """Nur bekannte Zeichen, und der Dorfgrund steht genau in den Spalten des Dorfes."""
    for zeile in range(daten.ZEILEN):
        for spalte in range(daten.SPALTEN):
            zeichen = raster[zeile][spalte]
            if zeichen not in daten.GELAENDE:
                raise ValueError(
                    f"Das Zeichen {zeichen!r} in Zeile {zeile + 1}, Spalte {spalte + 1} kennt "
                    f"das Spiel nicht. Erlaubt sind: {' '.join(daten.GELAENDE)}"
                )
            im_dorf = spalte >= ERSTE_DORFSPALTE
            if im_dorf and zeichen != "D":
                raise ValueError(
                    f"Die letzten {daten.DORF_SPALTEN} Spalten gehören dem Dorf (D). In Zeile "
                    f"{zeile + 1}, Spalte {spalte + 1} steht aber {zeichen!r}."
                )
            if zeichen == "D" and not im_dorf:
                raise ValueError(
                    f"Dorfgrund (D) gibt es nur in den letzten {daten.DORF_SPALTEN} Spalten, "
                    f"nicht in Zeile {zeile + 1}, Spalte {spalte + 1}."
                )


def _suche(raster, zeichen):
    """Liefert alle Zellen mit diesem Zeichen, Zeile für Zeile von oben nach unten."""
    gefunden = []
    for zeile in range(len(raster)):
        for spalte in range(len(raster[zeile])):
            if raster[zeile][spalte] == zeichen:
                gefunden.append((spalte, zeile))
    return gefunden


def _erreichbar_von(raster, anfang):
    """Liefert die Menge aller Zellen, zu denen man von ``anfang`` aus laufen kann.

    Beim Prüfen einer Karte gibt es noch keine Werkbank und keine Bauwerke. Darum schaut der
    Kern hier selbst nach, ganz einfach: Er geht von jeder gefundenen Zelle zu ihren
    begehbaren Nachbarn, bis nichts Neues mehr dazukommt. Im Spiel selbst kommen die Wege
    immer aus der Werkstatt (Missionen 2 bis 4).
    """
    erreichbar = {anfang}
    offen = [anfang]
    while len(offen) > 0:
        spalte, zeile = offen.pop()
        for nachbar in [
            (spalte, zeile - 1),
            (spalte + 1, zeile),
            (spalte, zeile + 1),
            (spalte - 1, zeile),
        ]:
            if nachbar in erreichbar:
                continue
            if not (0 <= nachbar[0] < daten.SPALTEN and 0 <= nachbar[1] < daten.ZEILEN):
                continue
            if raster[nachbar[1]][nachbar[0]] in daten.BEGEHBAR:
                erreichbar.add(nachbar)
                offen.append(nachbar)
    return erreichbar


class Karte:
    """Eine geprüfte Karte: ``raster``, ``name``, ``breite``, ``hoehe``, ``starts``, ``ziel``.

    Die Karte merkt sich auch, welche Zellen durch Bauwerke gesperrt sind (``gesperrt``), und
    die Abstandskarte dazu. Die Abstandskarte wird nur dann neu berechnet, wenn sich an den
    gesperrten Zellen etwas geändert hat: Eine einzige Suche reicht für alle Gegner.
    """

    def __init__(self, raster, name="eigene"):
        pruefe_karte(raster)
        # Eine eigene Kopie: Wer das Raster hereingegeben hat, kann die Karte nicht verändern.
        self.raster = [list(zeile) for zeile in raster]
        self.name = name
        self.breite = daten.SPALTEN
        self.hoehe = daten.ZEILEN
        self.starts = _suche(self.raster, "S")  # die Orktore
        self.ziel = _suche(self.raster, "Z")[0]  # das Dorftor
        self.gesperrt = set()  # die Zellen, auf denen ein Bauwerk steht
        self._abstaende = None  # None heißt: Die Abstandskarte muss neu berechnet werden.

    def gelaende(self, zelle):
        """Liefert das Zeichen des Geländes auf dieser Zelle."""
        spalte, zeile = zelle
        return self.raster[zeile][spalte]

    def enthaelt(self, zelle):
        """Sagt, ob die Zelle auf der Karte liegt."""
        spalte, zeile = zelle
        return 0 <= spalte < self.breite and 0 <= zeile < self.hoehe

    def abstaende(self, werkbank):
        """Liefert die Abstandskarte zum Dorftor; gerechnet wird nur, wenn es nötig ist."""
        if self._abstaende is None:
            self._abstaende = self.abstaende_mit(self.gesperrt, werkbank)
        return self._abstaende

    def abstaende_mit(self, gesperrt, werkbank):
        """Rechnet die Abstandskarte für diese gesperrten Zellen aus (Fähigkeit wegfindung)."""
        return werkbank.rufe("wegfindung", "abstandskarte", self.raster, self.ziel, gesperrt)

    def sperre(self, zelle, abstaende=None):
        """Sperrt die Zelle für die Gegner.

        Wer die Abstandskarte mit dieser Sperre schon ausgerechnet hat, gibt sie mit. Dann
        muss sie nicht noch einmal berechnet werden.
        """
        self.gesperrt.add(zelle)
        self._abstaende = abstaende

    def gib_frei(self, zelle):
        """Gibt eine gesperrte Zelle wieder frei."""
        self.gesperrt.discard(zelle)
        self._abstaende = None

    def vergiss_abstaende(self):
        """Lässt die Abstandskarte beim nächsten Mal neu berechnen (nach neuem Werkstatt-Code)."""
        self._abstaende = None


def lies_raster(text, werkbank):
    """Macht aus einem Kartentext ein Raster (Fähigkeit karten); kaputter Text: ValueError."""
    try:
        return werkbank.rufe("karten", "lies_karte", text)
    except Lernfehler as fehler:
        # Meldet lies_karte selbst einen ValueError, dann ist der Text kaputt und nicht der
        # Code. Jeder andere Fehler ist ein Fehler im Code der Werkstatt und bleibt einer.
        if fehler.art == "ValueError":
            raise ValueError(fehler.text) from fehler
        raise


def lade_karte(name: str, werkbank) -> Karte:
    """Liest ``karten/<name>.txt`` mit der Fähigkeit ``karten`` und liefert die Karte."""
    datei = KARTENORDNER / f"{name}.txt"
    try:
        text = datei.read_text(encoding="utf-8")
    except (OSError, ValueError) as fehler:
        raise ValueError(f"Die Kartendatei karten/{name}.txt lässt sich nicht lesen.") from fehler
    raster = lies_raster(text, werkbank)
    if werkbank.ist_offen("karten"):
        # Der Ersatz der Mission 1 liest den Text nicht: Er liefert immer die Standardkarte.
        name = daten.STANDARD_KARTE
    return Karte(raster, name)


def zentrum(zelle) -> tuple:
    """Liefert den Mittelpunkt einer Zelle in Pixeln."""
    spalte, zeile = zelle
    return (spalte * daten.ZELLE + daten.ZELLE / 2, zeile * daten.ZELLE + daten.ZELLE / 2)
