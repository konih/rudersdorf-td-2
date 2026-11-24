"""Architektur: Werkstatt und Lösung haben dieselben Module, Namen und Signaturen.

Für jedes Modul des Missionsverzeichnisses, das es in beiden Paketen gibt, müssen die
öffentlichen Funktionen, Klassen und Methoden übereinstimmen: gleiche Namen, gleiche
Parameternamen, gleiche Standardwerte. Die Module der Missionen 21 bis 23 werden fehlerhaft
oder unordentlich ausgeliefert; dort zählt nur, dass die Namen des Verzeichnisses in beiden
Paketen stehen. Verglichen wird der Quelltext mit ``ast``.
"""

import ast
import copy
import pathlib
import shutil
import tempfile
import unittest

from rudersdorf.missionen import MISSIONEN
from tests.architektur.quelltext import (
    FUNKTION,
    lies_modul,
    methoden,
    schreibe_dateien,
    zugewiesene_namen,
)

WURZEL = pathlib.Path(__file__).resolve().parent.parent.parent

# Mit Absicht ausgeschrieben: Diese Missionen werden nur über ihre Namen verglichen.
NUR_NAMEN = (21, 22, 23)
# Mission 8 ist eine eigene Erfindung: Die Referenz darf dort weitere Strategien haben.
EIGENE_STRATEGIE = 8
STRATEGIE_PARAMETER = "kandidaten, turm"

REGEL_EINSEITIG = "das Modul gibt es nur in einem der beiden Pakete"
REGEL_LESBAR = "die Datei lässt sich nicht als Python lesen"
REGEL_ART = "ist in einem Paket eine Funktion und im anderen eine Klasse"
REGEL_PARAMETER = "andere Parameter"
REGEL_BASIS = "andere Oberklasse"


def parameter(funktion):
    """Die Parameter als Text, mit Standardwerten und ohne Typangaben: ``a, b=2, *, c``."""
    alle = copy.deepcopy(funktion.args)
    einzelne = [*alle.posonlyargs, *alle.args, *alle.kwonlyargs, alle.vararg, alle.kwarg]
    for einer in einzelne:
        if einer is not None:
            einer.annotation = None
    return ast.unparse(alle)


def zaehlt(name):
    """Öffentlich ist, was nicht mit ``_`` beginnt; ``__init__`` und Verwandte zählen mit."""
    return not name.startswith("_") or (name.startswith("__") and name.endswith("__"))


def form(baum):
    """Name → ("Funktion", Parameter) oder ("Klasse", Oberklassen, {Methode: Parameter})."""
    ergebnis = {}
    for knoten in baum.body:
        if isinstance(knoten, FUNKTION) and zaehlt(knoten.name):
            ergebnis[knoten.name] = ("Funktion", parameter(knoten))
        elif isinstance(knoten, ast.ClassDef) and zaehlt(knoten.name):
            eigene = {m.name: parameter(m) for m in methoden(knoten) if zaehlt(m.name)}
            oberklassen = ", ".join(ast.unparse(basis) for basis in knoten.bases)
            ergebnis[knoten.name] = ("Klasse", oberklassen, eigene)
    return ergebnis


def fehlt_in(paket):
    return f"fehlt in {paket}"


def vergleiche(name, werkstatt, loesung):
    """Liefert die Unterschiede zwischen zwei Einträgen aus ``form``."""
    if werkstatt[0] != loesung[0]:
        return [f"{name}: {REGEL_ART}"]
    if werkstatt[0] == "Funktion":
        return vergleiche_parameter(name, werkstatt[1], loesung[1])
    unterschiede = []
    if werkstatt[1] != loesung[1]:
        unterschiede.append(
            f"{name}: {REGEL_BASIS}: werkstatt ({werkstatt[1]}), loesung ({loesung[1]})"
        )
    for methode in sorted(set(werkstatt[2]) | set(loesung[2])):
        if methode not in werkstatt[2]:
            unterschiede.append(f"{name}.{methode}: {fehlt_in('werkstatt')}")
        elif methode not in loesung[2]:
            unterschiede.append(f"{name}.{methode}: {fehlt_in('loesung')}")
        else:
            unterschiede += vergleiche_parameter(
                f"{name}.{methode}", werkstatt[2][methode], loesung[2][methode]
            )
    return unterschiede


def vergleiche_parameter(name, werkstatt, loesung):
    if werkstatt == loesung:
        return []
    return [f"{name}: {REGEL_PARAMETER}: werkstatt ({werkstatt}), loesung ({loesung})"]


def vergleiche_modul(werkstatt, loesung, namen, eigene_erlaubt):
    """Vergleicht alle öffentlichen Funktionen und Klassen zweier Syntaxbäume."""
    form_w, form_l = form(werkstatt), form(loesung)
    unterschiede = []
    for name in sorted(set(form_w) | set(form_l)):
        if name not in form_l:
            unterschiede.append(f"{name}: {fehlt_in('loesung')}")
        elif name not in form_w:
            if not (eigene_erlaubt and form_l[name] == ("Funktion", STRATEGIE_PARAMETER)):
                unterschiede.append(f"{name}: {fehlt_in('werkstatt')}")
        else:
            unterschiede += vergleiche(name, form_w[name], form_l[name])
    # Namen des Verzeichnisses, die keine Funktion und keine Klasse sind (STRATEGIEN).
    uebrige = [name for name in namen if name not in form_w and name not in form_l]
    return unterschiede + vergleiche_namen(werkstatt, loesung, uebrige)


def vergleiche_namen(werkstatt, loesung, namen):
    """Jeder Name des Verzeichnisses muss in beiden Paketen ganz außen im Modul stehen."""
    unterschiede = []
    for name in namen:
        for paket, baum in (("werkstatt", werkstatt), ("loesung", loesung)):
            if name not in form(baum) and name not in zugewiesene_namen(baum):
                unterschiede.append(f"{name}: {fehlt_in(paket)}")
    return unterschiede


def finde_unterschiede(wurzel, missionen):
    """Vergleicht ``wurzel/werkstatt`` mit ``wurzel/loesung`` für alle Module in ``missionen``."""
    wurzel = pathlib.Path(wurzel)
    nummern, namen = {}, {}
    for mission in missionen:
        nummern.setdefault(mission["modul"], []).append(mission["nummer"])
        namen.setdefault(mission["modul"], []).extend(mission["namen"])
    unterschiede = []
    for modul in nummern:
        ordner = [wurzel / "werkstatt", wurzel / "loesung"]
        vorhanden = [(pfad / f"{modul}.py").is_file() for pfad in ordner]
        if not any(vorhanden):
            continue
        if not all(vorhanden):
            unterschiede.append(f"{modul}.py: {REGEL_EINSEITIG}")
            continue
        werkstatt, loesung = (lies_modul(pfad, modul) for pfad in ordner)
        if werkstatt is None or loesung is None:
            unterschiede.append(f"{modul}.py: {REGEL_LESBAR}")
            continue
        einmalig = list(dict.fromkeys(namen[modul]))
        if any(nummer in NUR_NAMEN for nummer in nummern[modul]):
            gefunden = vergleiche_namen(werkstatt, loesung, einmalig)
        else:
            eigene_erlaubt = EIGENE_STRATEGIE in nummern[modul]
            gefunden = vergleiche_modul(werkstatt, loesung, einmalig, eigene_erlaubt)
        unterschiede += [f"{modul}.py: {text}" for text in gefunden]
    return unterschiede


class Paritaet(unittest.TestCase):
    def test_werkstatt_und_loesung_stimmen_ueberein(self):
        unterschiede = finde_unterschiede(WURZEL, MISSIONEN)
        self.assertEqual([], unterschiede, "Unterschiede:\n" + "\n".join(unterschiede))

    def test_die_module_der_ungeloesten_missionen_gibt_es_in_beiden_paketen(self):
        module = ("raster", "tuerme", "strategien", "horde", "dorf", "magie")
        for modul in (*module, "schreiber", "forschung"):
            for paket in ("werkstatt", "loesung"):
                with self.subTest(paket=paket, modul=modul):
                    self.assertTrue((WURZEL / paket / f"{modul}.py").is_file())


# --- Selbsttest ------------------------------------------------------------------------------

PROBE = [
    {"nummer": 1, "modul": "probe", "namen": ["tu_was", "Ding"]},
    {"nummer": 2, "modul": "probe", "namen": ["TAFEL"]},
    {"nummer": 8, "modul": "wahl", "namen": ["TAFEL"]},
    {"nummer": 22, "modul": "kram", "namen": ["ordne", "Kiste"]},
]

WERKSTATT = {
    "probe": (
        "from math import hypot\n\n\n"
        "def tu_was(a, b=2, *rest, c, d=None, **mehr):\n    raise NochOffen('x')\n\n\n"
        "class Ding(Basis):\n"
        "    def __init__(self, a, b=1):\n        raise NochOffen('x')\n\n"
        "    def mach(self, x):\n        raise NochOffen('x')\n\n\n"
        "class Leer(Ding):\n    pass\n\n\n"
        "TAFEL = {}\n"
    ),
    "wahl": "def erster(kandidaten, turm):\n    raise NochOffen('x')\n\n\nTAFEL = {}\n",
    "kram": (
        "def ordne(a, liste=[]):\n    return 1\n\n\n"
        "def unordentlich(x):\n    return x\n\n\n"
        "class Kiste:\n    def auf(self):\n        return 1\n"
    ),
}

LOESUNG = {
    # Andere Rümpfe, Typangaben, Docstrings, private Helfer und Konstanten stören nicht.
    "probe": (
        '"""Fertig."""\n\nGRENZE = 3\n\n\n'
        "def _helfer(x):\n    return x\n\n\n"
        "def tu_was(a: int, b: int = 2, *rest, c, d=None, **mehr) -> int:\n"
        '    """Fertig."""\n    return _helfer(a) + b\n\n\n'
        "class Ding(Basis):\n"
        "    art = 'ding'\n\n"
        "    def __init__(self, a, b=1):\n        self.a = a\n\n"
        "    def mach(self, x):\n        return self._innen(x)\n\n"
        "    def _innen(self, x):\n        return x\n\n\n"
        "class Leer(Ding):\n    art = 'leer'\n\n\n"
        "TAFEL = {'a': 1}\n"
    ),
    # Im Modul der Mission 8 darf die Referenz eigene Strategien haben.
    "wahl": (
        "def erster(kandidaten, turm):\n    return None\n\n\n"
        "def gefaehrlichster(kandidaten, turm):\n    return None\n\n\n"
        "TAFEL = {'gefaehrlichster': gefaehrlichster}\n"
    ),
    # Module der Missionen 21 bis 23: nur die Namen des Verzeichnisses zählen.
    "kram": (
        "MAX = 5\n\n\n"
        "def abstand(a, b):\n    return 0\n\n\n"
        "def ordne(a, liste=None):\n    return 1\n\n\n"
        "class Kiste:\n    def auf(self, weit):\n        return 1\n"
    ),
}

W_TU = "def tu_was(a, b=2, *rest, c, d=None, **mehr):"
L_TU = "def tu_was(a: int, b: int = 2, *rest, c, d=None, **mehr) -> int:"
L_INIT = "    def __init__(self, a, b=1):\n        self.a = a\n\n"
L_MACH = "    def mach(self, x):\n        return self._innen(x)\n\n"
ANDERE = "probe.py: tu_was: " + REGEL_PARAMETER + ": werkstatt (a, b=2, *rest, c, d=None, **mehr)"

# (Was, Paket, Modul, alter Text, neuer Text, erwartete Meldungen)
UNGLEICH = (
    (
        "Parameter umbenannt",
        "loesung",
        "probe",
        L_TU,
        "def tu_was(x, b=2, *rest, c, d=None, **mehr):",
        [ANDERE + ", loesung (x, b=2, *rest, c, d=None, **mehr)"],
    ),
    (
        "Standardwert geändert",
        "loesung",
        "probe",
        L_TU,
        "def tu_was(a, b=3, *rest, c, d=None, **mehr):",
        [ANDERE + ", loesung (a, b=3, *rest, c, d=None, **mehr)"],
    ),
    (
        "Standardwert entfernt",
        "loesung",
        "probe",
        L_TU,
        "def tu_was(a, b, *rest, c, d=None, **mehr):",
        [ANDERE + ", loesung (a, b, *rest, c, d=None, **mehr)"],
    ),
    (
        "Standardwert nach dem Stern geändert",
        "loesung",
        "probe",
        L_TU,
        "def tu_was(a, b=2, *rest, c, d=0, **mehr):",
        [ANDERE + ", loesung (a, b=2, *rest, c, d=0, **mehr)"],
    ),
    (
        "Parameter fehlt",
        "loesung",
        "probe",
        L_TU,
        "def tu_was(a, *rest, c, d=None, **mehr):",
        [ANDERE + ", loesung (a, *rest, c, d=None, **mehr)"],
    ),
    (
        "Reihenfolge vertauscht",
        "loesung",
        "probe",
        L_TU,
        "def tu_was(b=2, a=1, *rest, c, d=None, **mehr):",
        [ANDERE + ", loesung (b=2, a=1, *rest, c, d=None, **mehr)"],
    ),
    (
        "Stern-Parameter umbenannt",
        "loesung",
        "probe",
        L_TU,
        "def tu_was(a, b=2, *alle, c, d=None, **mehr):",
        [ANDERE + ", loesung (a, b=2, *alle, c, d=None, **mehr)"],
    ),
    (
        "nicht mehr nur mit Namen",
        "loesung",
        "probe",
        L_TU,
        "def tu_was(a, b=2, c=0, d=None, *rest, **mehr):",
        [ANDERE + ", loesung (a, b=2, c=0, d=None, *rest, **mehr)"],
    ),
    (
        "Funktion fehlt in der Referenz",
        "loesung",
        "probe",
        L_TU,
        "def tu_etwas(a):",
        ["probe.py: tu_etwas: fehlt in werkstatt", "probe.py: tu_was: fehlt in loesung"],
    ),
    (
        "Funktion zu viel in der Werkstatt",
        "werkstatt",
        "probe",
        "TAFEL = {}\n",
        "TAFEL = {}\n\n\ndef neu(a):\n    pass\n",
        ["probe.py: neu: fehlt in loesung"],
    ),
    (
        "öffentlicher Helfer in der Referenz",
        "loesung",
        "probe",
        "def _helfer(x):\n    return x\n",
        "def helfer(x):\n    return x\n",
        ["probe.py: helfer: fehlt in werkstatt"],
    ),
    (
        "Klasse statt Funktion",
        "loesung",
        "probe",
        "class Leer(Ding):\n    art = 'leer'\n",
        "def Leer(Ding):\n    pass\n",
        ["probe.py: Leer: " + REGEL_ART],
    ),
    (
        "Klasse fehlt in der Werkstatt",
        "werkstatt",
        "probe",
        "class Leer(Ding):\n    pass\n\n\n",
        "",
        ["probe.py: Leer: fehlt in werkstatt"],
    ),
    (
        "andere Oberklasse",
        "loesung",
        "probe",
        "class Leer(Ding):\n    art",
        "class Leer(Basis):\n    art",
        ["probe.py: Leer: " + REGEL_BASIS + ": werkstatt (Ding), loesung (Basis)"],
    ),
    (
        "Methode fehlt in der Referenz",
        "loesung",
        "probe",
        L_MACH,
        "",
        ["probe.py: Ding.mach: fehlt in loesung"],
    ),
    (
        "Methode zu viel in der Referenz",
        "loesung",
        "probe",
        "    def _innen(self, x):",
        "    def innen(self, x):",
        ["probe.py: Ding.innen: fehlt in werkstatt"],
    ),
    (
        "Methode mit anderen Parametern",
        "loesung",
        "probe",
        "    def mach(self, x):\n        return self",
        "    def mach(self, y):\n        return self",
        ["probe.py: Ding.mach: " + REGEL_PARAMETER + ": werkstatt (self, x), loesung (self, y)"],
    ),
    (
        "__init__ mit anderem Standardwert",
        "loesung",
        "probe",
        L_INIT,
        "    def __init__(self, a, b=2):\n        self.a = a\n\n",
        [
            "probe.py: Ding.__init__: "
            + REGEL_PARAMETER
            + ": werkstatt (self, a, b=1), loesung (self, a, b=2)"
        ],
    ),
    (
        "__init__ fehlt in der Referenz",
        "loesung",
        "probe",
        L_INIT,
        "",
        ["probe.py: Ding.__init__: fehlt in loesung"],
    ),
    (
        "Tafel fehlt in der Referenz",
        "loesung",
        "probe",
        "TAFEL = {'a': 1}\n",
        "TAFELN = {'a': 1}\n",
        ["probe.py: TAFEL: fehlt in loesung"],
    ),
    (
        "Tafel fehlt in der Werkstatt",
        "werkstatt",
        "probe",
        "TAFEL = {}\n",
        "TAFELN = {}\n",
        ["probe.py: TAFEL: fehlt in werkstatt"],
    ),
    (
        "kein Python",
        "loesung",
        "probe",
        L_TU,
        "def tu_was(a:",
        ["probe.py: " + REGEL_LESBAR],
    ),
    (
        "eigene Strategie mit anderen Parametern",
        "loesung",
        "wahl",
        "def gefaehrlichster(kandidaten, turm):",
        "def gefaehrlichster(kandidaten, turm, mehr=1):",
        ["wahl.py: gefaehrlichster: fehlt in werkstatt"],
    ),
    (
        "eigene Klasse im Modul der Mission 8",
        "loesung",
        "wahl",
        "def gefaehrlichster(kandidaten, turm):\n    return None\n",
        "class gefaehrlichster:\n    pass\n",
        ["wahl.py: gefaehrlichster: fehlt in werkstatt"],
    ),
    (
        "eigene Strategie nur in der Werkstatt",
        "werkstatt",
        "wahl",
        "TAFEL = {}\n",
        "def meine(kandidaten, turm):\n    pass\n\n\nTAFEL = {}\n",
        ["wahl.py: meine: fehlt in loesung"],
    ),
    (
        "Standardstrategie mit anderen Parametern",
        "loesung",
        "wahl",
        "def erster(kandidaten, turm):",
        "def erster(kandidaten):",
        [
            "wahl.py: erster: "
            + REGEL_PARAMETER
            + ": werkstatt (kandidaten, turm), loesung (kandidaten)"
        ],
    ),
    (
        "Handwerk: Name fehlt in der Referenz",
        "loesung",
        "kram",
        "def ordne(a, liste=None):",
        "def sortiere(a, liste=None):",
        ["kram.py: ordne: fehlt in loesung"],
    ),
    (
        "Handwerk: Name fehlt in der Werkstatt",
        "werkstatt",
        "kram",
        "class Kiste:",
        "class Kisten:",
        ["kram.py: Kiste: fehlt in werkstatt"],
    ),
)


def pruefe_pakete(werkstatt, loesung, missionen=PROBE):
    dateien = {f"werkstatt/{modul}.py": text for modul, text in werkstatt.items()}
    dateien.update({f"loesung/{modul}.py": text for modul, text in loesung.items()})
    with tempfile.TemporaryDirectory() as ordner:
        schreibe_dateien(ordner, dateien)
        return finde_unterschiede(ordner, missionen)


def ersetze_einmal(text, alt, neu):
    if text.count(alt) != 1:
        raise AssertionError(f"Der Text kommt nicht genau einmal vor: {alt!r}")
    return text.replace(alt, neu)


class Selbsttest(unittest.TestCase):
    """Beweist an erfundenen Paketen, dass der Vergleich jeden Unterschied findet."""

    def test_gleiche_pakete_sind_ohne_unterschied(self):
        self.assertEqual([], pruefe_pakete(WERKSTATT, LOESUNG))

    def test_jede_art_von_unterschied_wird_gemeldet(self):
        for was, paket, modul, alt, neu, erwartet in UNGLEICH:
            with self.subTest(was=was):
                pakete = {"werkstatt": dict(WERKSTATT), "loesung": dict(LOESUNG)}
                pakete[paket][modul] = ersetze_einmal(pakete[paket][modul], alt, neu)
                self.assertEqual(erwartet, pruefe_pakete(pakete["werkstatt"], pakete["loesung"]))

    def test_ein_modul_in_nur_einem_paket_ist_ein_unterschied(self):
        for modul in ("probe", "wahl", "kram"):
            for paket in ("werkstatt", "loesung"):
                with self.subTest(modul=modul, fehlt_in=paket):
                    pakete = {"werkstatt": dict(WERKSTATT), "loesung": dict(LOESUNG)}
                    del pakete[paket][modul]
                    self.assertEqual(
                        [f"{modul}.py: {REGEL_EINSEITIG}"],
                        pruefe_pakete(pakete["werkstatt"], pakete["loesung"]),
                    )

    def test_ein_modul_das_es_noch_nirgends_gibt_wird_uebersprungen(self):
        ohne = {"probe": WERKSTATT["probe"], "wahl": WERKSTATT["wahl"]}
        self.assertEqual(
            [], pruefe_pakete(ohne, {"probe": LOESUNG["probe"], "wahl": LOESUNG["wahl"]})
        )

    def test_nur_die_missionen_21_bis_23_werden_nach_namen_verglichen(self):
        for nummer in (20, 24):
            with self.subTest(nummer=nummer):
                streng = [{"nummer": nummer, "modul": "kram", "namen": ["ordne", "Kiste"]}]
                self.assertEqual(
                    [
                        "kram.py: Kiste.auf: " + REGEL_PARAMETER + ": werkstatt (self), "
                        "loesung (self, weit)",
                        "kram.py: abstand: fehlt in werkstatt",
                        "kram.py: ordne: " + REGEL_PARAMETER + ": werkstatt (a, liste=[]), "
                        "loesung (a, liste=None)",
                        "kram.py: unordentlich: fehlt in loesung",
                    ],
                    pruefe_pakete(WERKSTATT, LOESUNG, streng),
                )
        for nummer in (21, 22, 23):
            with self.subTest(nummer=nummer):
                nach_namen = [{"nummer": nummer, "modul": "kram", "namen": ["ordne", "Kiste"]}]
                self.assertEqual([], pruefe_pakete(WERKSTATT, LOESUNG, nach_namen))

    def test_eigene_strategien_sind_nur_im_modul_der_mission_8_erlaubt(self):
        for nummer in (7, 9):
            with self.subTest(nummer=nummer):
                andere = [{"nummer": nummer, "modul": "wahl", "namen": ["TAFEL"]}]
                self.assertEqual(
                    ["wahl.py: gefaehrlichster: fehlt in werkstatt"],
                    pruefe_pakete(WERKSTATT, LOESUNG, andere),
                )


class SelbsttestAmEchtenPaket(unittest.TestCase):
    """Verändert in einer Kopie der echten Pakete eine Signatur und erwartet eine Meldung."""

    def test_eine_geaenderte_signatur_in_der_referenz_wird_gemeldet(self):
        with tempfile.TemporaryDirectory() as ordner:
            kopie = pathlib.Path(ordner)
            for paket in ("werkstatt", "loesung"):
                muster = shutil.ignore_patterns("__pycache__")
                shutil.copytree(WURZEL / paket, kopie / paket, ignore=muster)
            self.assertEqual([], finde_unterschiede(kopie, MISSIONEN))
            datei = kopie / "loesung" / "raster.py"
            text = datei.read_text(encoding="utf-8")
            alt = "def abstandskarte(raster, ziel, gesperrt):"
            datei.write_text(ersetze_einmal(text, alt, "def abstandskarte(raster, ziel):"))
            self.assertEqual(
                [
                    "raster.py: abstandskarte: " + REGEL_PARAMETER + ": werkstatt (raster, ziel, "
                    "gesperrt), loesung (raster, ziel)"
                ],
                finde_unterschiede(kopie, MISSIONEN),
            )


if __name__ == "__main__":
    unittest.main()
