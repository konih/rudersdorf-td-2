"""Die Werkbank: der einzige Weg, auf dem das Spiel Code aus der Werkstatt benutzt.

Sie lädt ein Paket (``werkstatt`` oder ``loesung``), probiert aus, welche Fähigkeiten schon
gelöst sind, und reicht jeden Aufruf weiter. Ist eine Mission noch offen, antwortet der
Ersatz aus ``rudersdorf/ersatz.py``. Macht der Code der Werkstatt einen echten Fehler, wird
daraus ein ``Lernfehler`` mit Datei und Zeile.

Noch ist hier nichts gebaut: Es stehen nur die Namen und Parameter fest.
"""

# Fähigkeit -> {"missionen": [Nummern], "modul": Name, "namen": [Namen]}, aus dem Verzeichnis
# der Missionen gebaut, in dessen Reihenfolge.
FAEHIGKEITEN: dict[str, dict] = {}

# Fähigkeit -> Liste kleiner Funktionen, die je einen Namen der Werkstatt einmal ausprobieren.
PROBEN: dict[str, list] = {}

# Fähigkeit -> Fähigkeiten, auf die sie wartet (aus "braucht" im Verzeichnis der Missionen).
ABHAENGIG: dict[str, list] = {}


class Werkbank:
    """Lädt ein Paket der Werkstatt und leitet die Aufrufe des Spiels dorthin."""

    def __init__(self, paket: str, gesperrt=()):
        """Lädt ``paket``; ``gesperrt`` nennt Fähigkeiten, die für Tests als offen gelten."""
        raise NotImplementedError

    def lade_neu(self) -> None:
        """Liest die Module neu ein; bei einem Fehler bleibt der alte Code in Betrieb."""
        raise NotImplementedError

    def ist_offen(self, faehigkeit: str) -> bool:
        """Sagt, ob für diese Fähigkeit gerade der Ersatz benutzt wird."""
        raise NotImplementedError

    def offene(self) -> list[str]:
        """Liefert alle offenen Fähigkeiten in der Reihenfolge des Verzeichnisses."""
        raise NotImplementedError

    def wartet_auf(self, faehigkeit: str) -> list[int]:
        """Liefert die Nummern der Missionen, auf die diese Fähigkeit wartet."""
        raise NotImplementedError

    def rufe(self, faehigkeit: str, name: str, *args, **kwargs):
        """Ruft die Funktion ``name`` der Werkstatt auf, oder ihren Ersatz."""
        raise NotImplementedError

    def erzeuge(self, faehigkeit: str, klasse: str, *args, **kwargs):
        """Erzeugt ein Objekt der Klasse ``klasse`` der Werkstatt, oder ihres Ersatzes."""
        raise NotImplementedError

    def strategien(self) -> dict:
        """Liefert die Zielstrategien: Name -> Funktion."""
        raise NotImplementedError


def waehle_paket(loesung: bool | None = None) -> str:
    """Entscheidet zwischen ``werkstatt`` und ``loesung``; ``None`` fragt RUDERSDORF_LOESUNG."""
    raise NotImplementedError
