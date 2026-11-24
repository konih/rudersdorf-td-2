"""Die Karte des Spiels: prüfen, laden, Zellen und Tore.

Eine Zelle ist ``(spalte, zeile)``; das Raster liest man mit ``raster[zeile][spalte]``.
"""


def pruefe_karte(raster) -> None:
    """Prüft ein Raster nach den Regeln des Spiels; bei einem Fehler: ValueError mit Grund."""
    raise NotImplementedError


class Karte:
    """Eine geprüfte Karte: ``raster``, ``name``, ``breite``, ``hoehe``, ``starts``, ``ziel``."""

    def __init__(self, raster, name="eigene"):
        raise NotImplementedError


def lade_karte(name: str, werkbank) -> Karte:
    """Liest ``karten/<name>.txt`` mit der Fähigkeit ``karten`` und liefert die Karte."""
    raise NotImplementedError


def zentrum(zelle) -> tuple:
    """Liefert den Mittelpunkt einer Zelle in Pixeln."""
    raise NotImplementedError
