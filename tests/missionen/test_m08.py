"""Mission 8 · Deine eigene Strategie: eine sechste Regel, die du dir selbst ausdenkst.

Solange in STRATEGIEN nur die fünf Regeln aus Mission 7 stehen, ist die Mission noch offen.
Sobald du eine eigene Regel eingetragen hast, prüfen diese Tests vier Dinge: Sie sucht aus
jeder Testliste einen der Kandidaten aus, sie antwortet auf eine leere Liste mit None, sie
lässt die Liste der Kandidaten, wie sie war, und sie ist keine Kopie einer der fünf Regeln.
Welche Regel du erfindest, ist deine Sache.

Hast du mehrere eigene Regeln eingetragen, genügt es, wenn eine davon alles erfüllt.
"""

from rudersdorf.fehler import NochOffen
from tests.missionen import helfer
from tests.missionen.helfer import TestGegner, TestTurm

STANDARD = ["erster", "letzter", "staerkster", "schwaechster", "naechster"]

TIPP_KANDIDAT = (
    "Eine Strategie gibt immer einen der Gegner aus kandidaten zurück: den Gegner selbst, "
    "nicht seine Nummer in der Liste, nicht True und keine neue Liste."
)
TIPP_LEER = (
    "Ist die Liste leer, gibt es niemanden auszusuchen. Prüfe das als Erstes und gib dann "
    "None zurück."
)
TIPP_GELIEHEN = (
    "Die Liste kandidaten ist nur geliehen. kandidaten.sort() sortiert sie um, remove und pop "
    "nehmen etwas heraus. Brauchst du eine sortierte Liste, dann bau dir mit sorted(kandidaten) "
    "eine eigene."
)
TIPP_KOPIE = (
    "Eine eigene Regel entscheidet irgendwo anders als die fünf vorhandenen. Du kannst zum "
    "Beispiel zwei Eigenschaften zusammen ansehen (rest_weg und leben) oder auf fliegt, "
    "ist_boss oder max_leben achten."
)


def testlisten():
    """Die Kandidatenlisten, an denen eine eigene Regel gemessen wird. Der Turm steht auf (200, 200).

    Die Gegner unterscheiden sich in allem, was eine Regel ansehen kann: Restweg, Leben,
    volles Leben, Platz, und ob sie fliegen oder ein Boss sind.
    """
    return {
        "gemischt": [
            TestGegner(leben=50, x=400.0, y=200.0, rest_weg=100.0),
            TestGegner(leben=30, x=300.0, y=200.0, rest_weg=500.0),
            TestGegner(leben=90, x=200.0, y=500.0, rest_weg=300.0),
            TestGegner(leben=10, x=500.0, y=500.0, rest_weg=200.0),
            TestGegner(leben=60, x=220.0, y=200.0, rest_weg=400.0),
        ],
        "vorhut": [
            TestGegner(leben=20, x=300.0, y=200.0, rest_weg=100.0),
            TestGegner(leben=80, x=320.0, y=200.0, rest_weg=120.0),
            TestGegner(leben=200, x=600.0, y=200.0, rest_weg=900.0),
            TestGegner(leben=5, x=210.0, y=210.0, rest_weg=500.0),
        ],
        "besondere": [
            TestGegner(leben=15, x=250.0, y=250.0, rest_weg=600.0, fliegt=True),
            TestGegner(leben=400, max_leben=500, x=500.0, y=200.0, rest_weg=700.0, ist_boss=True),
            TestGegner(leben=30, max_leben=300, x=400.0, y=400.0, rest_weg=300.0),
            TestGegner(leben=60, x=100.0, y=500.0, rest_weg=200.0),
        ],
        "allein": [
            TestGegner(leben=25, x=300.0, y=300.0, rest_weg=120.0),
        ],
    }


def ist_einer_von(antwort, kandidaten):
    """Sagt, ob ``antwort`` genau einer der Kandidaten ist. Kommt mit jeder Antwort zurecht."""
    return any(antwort is kandidat for kandidat in kandidaten)


class Mission08(helfer.Missionstest):
    modul = "strategien"

    def setUp(self):
        super().setUp()
        self.turm = TestTurm(x=200.0, y=200.0)
        tabelle = getattr(self.werkstatt, "STRATEGIEN", None)
        eigene = []
        if isinstance(tabelle, dict):
            eigene = [name for name in tabelle if name not in STANDARD]
        if not eigene:
            # Noch keine eigene Regel eingetragen: Die Mission ist offen, nicht falsch.
            raise NochOffen("Mission 8: Deine eigene Strategie")
        # Geprüft wird die erste eigene Regel, die alles erfüllt. Erfüllt keine alles,
        # zeigen die Tests an der ersten eigenen Regel, was noch fehlt.
        self.name = eigene[0]
        for name in eigene:
            self.aufruf = f"STRATEGIEN[{name!r}]"
            if self.erfuellt_alles(tabelle[name]):
                self.name = name
                break
        self.regel = tabelle[self.name]
        self.aufruf = f"STRATEGIEN[{self.name!r}]"

    # --- die vier Fragen, jede liefert None oder (erwartet, bekommen, tipp) ----------------

    def mangel_bei_den_kandidaten(self, regel):
        for titel, kandidaten in testlisten().items():
            antwort = regel(kandidaten, self.turm)
            if not ist_einer_von(antwort, kandidaten):
                return (
                    f"{self.aufruf}(kandidaten, turm) ergibt für die Testliste {titel!r} "
                    f"einen dieser Kandidaten: {kandidaten}",
                    repr(antwort),
                    TIPP_KANDIDAT,
                )
        return None

    def mangel_bei_der_leeren_liste(self, regel):
        antwort = regel([], self.turm)
        if antwort is not None:
            return (f"{self.aufruf}([], turm) ergibt None", repr(antwort), TIPP_LEER)
        return None

    def mangel_weil_liste_veraendert(self, regel):
        for titel, kandidaten in testlisten().items():
            vorher = list(kandidaten)
            regel(kandidaten, self.turm)
            if kandidaten != vorher:
                return (
                    f"{self.aufruf}(kandidaten, turm) lässt die Testliste {titel!r} so, "
                    f"wie sie war: {vorher}",
                    f"danach war die Liste {kandidaten}",
                    TIPP_GELIEHEN,
                )
        return None

    def mangel_weil_kopie(self, regel):
        for standard in STANDARD:
            vorbild = getattr(self.werkstatt, standard)
            anders = False
            for kandidaten in testlisten().values():
                if regel(kandidaten, self.turm) is not vorbild(kandidaten, self.turm):
                    anders = True
            if not anders:
                return (
                    f"{self.aufruf} sucht auf mindestens einer Testliste einen anderen Gegner "
                    f"aus als {standard}",
                    f"auf allen {len(testlisten())} Testlisten denselben Gegner wie {standard}",
                    TIPP_KOPIE,
                )
        return None

    def erfuellt_alles(self, regel):
        """Probiert die vier Fragen still durch.

        Ein Absturz zählt als "nicht erfüllt", und eine Regel, die sich noch als offen meldet,
        auch. So verdirbt ein angefangener Eintrag keinen fertigen, der daneben steht.
        """
        try:
            return (
                self.mangel_bei_den_kandidaten(regel) is None
                and self.mangel_bei_der_leeren_liste(regel) is None
                and self.mangel_weil_liste_veraendert(regel) is None
                and self.mangel_weil_kopie(regel) is None
            )
        except Exception:
            return False

    def pruefe_ohne_mangel(self, frage, tipp):
        mangel = self.rufe_sicher(f"{self.aufruf}(kandidaten, turm)", tipp, frage, self.regel)
        if mangel is not None:
            self.fail(helfer.meldung(*mangel))

    # --- die Tests ---------------------------------------------------------------------------

    def test_die_eigene_regel_waehlt_aus_jeder_testliste_einen_der_kandidaten(self):
        self.pruefe_ohne_mangel(self.mangel_bei_den_kandidaten, TIPP_KANDIDAT)

    def test_die_eigene_regel_waehlt_aus_einer_leeren_liste_none(self):
        self.pruefe_ohne_mangel(self.mangel_bei_der_leeren_liste, TIPP_LEER)

    def test_die_eigene_regel_laesst_die_liste_der_kandidaten_wie_sie_war(self):
        self.pruefe_ohne_mangel(self.mangel_weil_liste_veraendert, TIPP_GELIEHEN)

    def test_die_eigene_regel_ist_keine_kopie_einer_der_fuenf_regeln(self):
        self.pruefe_ohne_mangel(self.mangel_weil_kopie, TIPP_KOPIE)
