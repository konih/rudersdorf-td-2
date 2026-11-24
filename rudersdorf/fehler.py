"""Die zwei Fehlerklassen, an denen das Spiel Lernenden-Code erkennt."""


class NochOffen(NotImplementedError):
    """Diese Mission ist noch nicht gelöst; das Spiel benutzt so lange einen Ersatz."""


class Lernfehler(Exception):
    """Ein echter Fehler im Code der Werkstatt, mit Datei und Zeile, damit man ihn findet."""

    def __init__(self, faehigkeit, datei, zeile, art, text, mission, spur=""):
        super().__init__(f"{datei}, Zeile {zeile}: {art}: {text}")
        self.faehigkeit = faehigkeit
        self.datei = datei
        self.zeile = zeile
        self.art = art
        self.text = text
        self.mission = mission
        self.spur = spur
