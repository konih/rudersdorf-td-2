"""Architektur: Die Werkstatt wird ungelöst ausgeliefert.

Jede Funktion und jede Methode, die das Missionsverzeichnis für die Missionen 1 bis 20 und
24 bis 26 nennt, besteht in ``werkstatt/`` nur aus einem Docstring und
``raise NochOffen("Mission N: <Titel>")``. Die Referenz in ``loesung/`` darf fertig sein;
wo sie es noch nicht ist, sagt sie es mit ``raise NochOffen("Referenz folgt: Mission N")``.
Geprüft wird der Quelltext mit ``ast``, dazu einmal der echte Aufruf.
"""

import ast
import importlib
import inspect
import pathlib
import shutil
import tempfile
import types
import unittest

from rudersdorf.fehler import NochOffen
from rudersdorf.missionen import MISSIONEN
from tests.architektur.quelltext import (
    FUNKTION,
    definitionen,
    lies_modul,
    methoden,
    schreibe_dateien,
    zugewiesene_namen,
)

WURZEL = pathlib.Path(__file__).resolve().parent.parent.parent

# Mit Absicht ausgeschrieben: Die Missionen 21 bis 23 werden fehlerhaft oder unordentlich
# ausgeliefert und gehören nicht hierher.
UNGELOEST = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 24, 25, 26)
STANDARD = ("erster", "letzter", "staerkster", "schwaechster", "naechster")

TEXT_WERKSTATT = "Mission {nummer}: {titel}"
TEXT_REFERENZ = "Referenz folgt: Mission {nummer}"

REGEL_DATEI = "die Datei fehlt oder ist kein Python"
REGEL_NAME = "der Name fehlt"
REGEL_RUMPF = "der Rumpf darf nur aus Docstring und raise NochOffen(...) bestehen"
REGEL_TEXT = "die Meldung in NochOffen ist falsch"
REGEL_LEER = "der Rumpf ist leer; unfertig heißt raise NochOffen(...)"
REGEL_TABELLE = "STRATEGIEN muss ein ausgeschriebenes Wörterbuch aus Name und Funktion sein"
REGEL_EINTRAG = "STRATEGIEN muss diesen Namen an die gleichnamige Funktion binden"
REGEL_ZUSATZ = "STRATEGIEN hat in der Werkstatt nur die fünf Standardnamen"


def rumpf_ohne_docstring(funktion):
    rumpf = funktion.body
    erstes = rumpf[0]
    if isinstance(erstes, ast.Expr) and isinstance(erstes.value, ast.Constant):
        if isinstance(erstes.value.value, str):
            return rumpf[1:]
    return rumpf


def platzhalter_text(funktion):
    """Liefert den Text aus ``raise NochOffen("...")``, wenn der Rumpf nur daraus besteht."""
    rumpf = rumpf_ohne_docstring(funktion)
    if len(rumpf) != 1:
        return None
    anweisung = rumpf[0]
    if not isinstance(anweisung, ast.Raise) or anweisung.cause is not None:
        return None
    ruf = anweisung.exc
    if not isinstance(ruf, ast.Call) or not isinstance(ruf.func, ast.Name):
        return None
    if ruf.func.id != "NochOffen" or len(ruf.args) != 1 or ruf.keywords:
        return None
    text = ruf.args[0]
    if not isinstance(text, ast.Constant) or not isinstance(text.value, str):
        return None
    return text.value


def ist_leer(funktion):
    """Ein Rumpf nur aus Docstring, ``pass`` oder ``...`` tut nichts und sagt es nicht."""
    for anweisung in rumpf_ohne_docstring(funktion):
        if isinstance(anweisung, ast.Pass):
            continue
        if isinstance(anweisung, ast.Expr) and isinstance(anweisung.value, ast.Constant):
            continue
        return False
    return True


def missionsfunktionen(baum, name):
    """Liefert (Bezeichnung, Funktion) für die Funktion ``name`` oder die Methoden der Klasse."""
    for knoten in definitionen(baum, name):
        if isinstance(knoten, FUNKTION):
            yield name, knoten
        else:
            for methode in methoden(knoten):
                yield f"{name}.{methode.name}", methode


def werkstatt_regel(funktion, mission):
    text = platzhalter_text(funktion)
    if text is None:
        return REGEL_RUMPF
    if text != TEXT_WERKSTATT.format(**mission):
        return REGEL_TEXT
    return None


def referenz_regel(funktion, mission):
    if ist_leer(funktion):
        return REGEL_LEER
    text = platzhalter_text(funktion)
    if text is not None and text != TEXT_REFERENZ.format(**mission):
        return REGEL_TEXT
    return None


def finde_verstoesse(ordner, missionen, regel=werkstatt_regel):
    """Prüft jede Funktion und Methode, die ``missionen`` nennt, im Paket ``ordner``."""
    verstoesse = []
    for mission in missionen:
        modul = mission["modul"]
        baum = lies_modul(ordner, modul)
        if baum is None:
            verstoesse.append(f"{modul}.py: {REGEL_DATEI}")
            continue
        for name in mission["namen"]:
            if not definitionen(baum, name) and name not in zugewiesene_namen(baum):
                verstoesse.append(f"{modul}.py: {name}: {REGEL_NAME}")
            for bezeichnung, funktion in missionsfunktionen(baum, name):
                gebrochen = regel(funktion, mission)
                if gebrochen:
                    verstoesse.append(f"{modul}.py: {bezeichnung}: {gebrochen}")
    return list(dict.fromkeys(verstoesse))


def finde_strategie_verstoesse(ordner, nur_standard):
    """Prüft das Wörterbuch ``STRATEGIEN`` in ``ordner/strategien.py``."""
    baum = lies_modul(ordner, "strategien")
    if baum is None:
        return [f"strategien.py: {REGEL_DATEI}"]
    tabelle = None
    for knoten in baum.body:
        if isinstance(knoten, ast.Assign) and len(knoten.targets) == 1:
            ziel = knoten.targets[0]
            if isinstance(ziel, ast.Name) and ziel.id == "STRATEGIEN":
                tabelle = knoten.value
    if not isinstance(tabelle, ast.Dict):
        return [f"strategien.py: {REGEL_TABELLE}"]
    eintraege = {}
    for schluessel, wert in zip(tabelle.keys, tabelle.values, strict=True):
        if not isinstance(schluessel, ast.Constant) or not isinstance(wert, ast.Name):
            return [f"strategien.py: {REGEL_TABELLE}"]
        eintraege[schluessel.value] = wert.id
    verstoesse = []
    for name in STANDARD:
        if eintraege.get(name) != name or not definitionen(baum, name):
            verstoesse.append(f"strategien.py: {name}: {REGEL_EINTRAG}")
    if nur_standard and set(eintraege) - set(STANDARD):
        verstoesse.append(f"strategien.py: {REGEL_ZUSATZ}")
    return verstoesse


def ungeloeste_missionen():
    return [mission for mission in MISSIONEN if mission["nummer"] in UNGELOEST]


class Werkstatt(unittest.TestCase):
    def test_ungeloest_sind_alle_missionen_ausser_21_bis_23(self):
        alle = [mission["nummer"] for mission in MISSIONEN]
        self.assertEqual([n for n in alle if n not in (21, 22, 23)], list(UNGELOEST))
        self.assertEqual(23, len(ungeloeste_missionen()))

    def test_die_werkstatt_ist_ungeloest(self):
        verstoesse = finde_verstoesse(WURZEL / "werkstatt", ungeloeste_missionen())
        self.assertEqual(
            [], verstoesse, "Die Werkstatt ist nicht ungelöst:\n" + "\n".join(verstoesse)
        )

    def test_die_referenz_ist_fertig_oder_sagt_dass_sie_folgt(self):
        verstoesse = finde_verstoesse(WURZEL / "loesung", ungeloeste_missionen(), referenz_regel)
        self.assertEqual([], verstoesse, "\n".join(verstoesse))

    def test_strategien_haben_die_fuenf_standardnamen(self):
        self.assertEqual([], finde_strategie_verstoesse(WURZEL / "werkstatt", nur_standard=True))
        self.assertEqual([], finde_strategie_verstoesse(WURZEL / "loesung", nur_standard=False))

    def test_jeder_aufruf_in_der_werkstatt_meldet_seine_mission(self):
        gezaehlt = 0
        for mission in ungeloeste_missionen():
            modul = importlib.import_module(f"werkstatt.{mission['modul']}")
            erwartet = TEXT_WERKSTATT.format(**mission)
            for name in mission["namen"]:
                for bezeichnung, funktion in aufrufbare(name, getattr(modul, name)):
                    with self.subTest(mission=mission["nummer"], name=bezeichnung):
                        with self.assertRaises(NochOffen) as gefangen:
                            funktion(*pflichtwerte(funktion))
                        self.assertEqual(erwartet, str(gefangen.exception))
                        gezaehlt += 1
        platzhalter = 0
        for datei in (WURZEL / "werkstatt").glob("*.py"):
            platzhalter += datei.read_text(encoding="utf-8").count("raise NochOffen(")
        self.assertEqual(platzhalter, gezaehlt, "Nicht jeder Platzhalter wurde aufgerufen.")


def aufrufbare(name, ding):
    """Liefert (Bezeichnung, Funktion) für eine Funktion oder die eigenen Methoden einer Klasse."""
    if inspect.isclass(ding):
        for methode, wert in vars(ding).items():
            if isinstance(wert, types.FunctionType):
                yield f"{name}.{methode}", wert
    elif isinstance(ding, types.FunctionType):
        yield name, ding


def pflichtwerte(funktion):
    """Ein ``None`` für jeden Parameter ohne Standardwert."""
    parameter = inspect.signature(funktion).parameters.values()
    return [None for p in parameter if p.default is inspect.Parameter.empty]


# --- Selbsttest ------------------------------------------------------------------------------

PROBE = [{"nummer": 4, "titel": "Probe", "modul": "probe", "namen": ["tu_was", "Ding", "TAFEL"]}]

GUT = '''"""Ein ungelöstes Modul."""

from rudersdorf.fehler import NochOffen


def tu_was(a, b=2):
    """Erklärt, was zu tun ist."""
    raise NochOffen("Mission 4: Probe")


class Ding:
    """Eine Klasse der Mission."""

    groesse = 3

    def __init__(self, a):
        raise NochOffen("Mission 4: Probe")

    async def mach(self):
        """Mit Docstring."""
        raise NochOffen("Mission 4: Probe")


class Kind(Ding):
    """Gehört zu keiner Mission und darf fertig sein."""

    def mach(self):
        return 1


def hilfe():
    return "gehört zu keiner Mission"


TAFEL = {"tu_was": tu_was}
'''

OFFEN = 'raise NochOffen("Mission 4: Probe")'
ERSTE = f'    """Erklärt, was zu tun ist."""\n    {OFFEN}'
IN_INIT = f"    def __init__(self, a):\n        {OFFEN}"
IN_MACH = f'        """Mit Docstring."""\n        {OFFEN}'

# (Was wurde verändert, alter Text, neuer Text, erwartete Meldungen)
FEHLERHAFT = (
    ("gelöst", ERSTE, "    return a + b", ["probe.py: tu_was: " + REGEL_RUMPF]),
    (
        "gelöst mit Docstring",
        ERSTE,
        '    """Text."""\n    return a',
        ["probe.py: tu_was: " + REGEL_RUMPF],
    ),
    (
        "etwas vor dem raise",
        ERSTE,
        f"    x = a + b\n    {OFFEN}",
        ["probe.py: tu_was: " + REGEL_RUMPF],
    ),
    (
        "etwas nach dem raise",
        ERSTE,
        f"    {OFFEN}\n    return a",
        ["probe.py: tu_was: " + REGEL_RUMPF],
    ),
    (
        "raise nur unter einer Bedingung",
        ERSTE,
        f"    if a:\n        {OFFEN}",
        ["probe.py: tu_was: " + REGEL_RUMPF],
    ),
    ("nur Docstring", ERSTE, '    """Text."""', ["probe.py: tu_was: " + REGEL_RUMPF]),
    ("nur pass", ERSTE, "    pass", ["probe.py: tu_was: " + REGEL_RUMPF]),
    (
        "anderer Fehler",
        ERSTE,
        '    raise NotImplementedError("Mission 4: Probe")',
        ["probe.py: tu_was: " + REGEL_RUMPF],
    ),
    ("raise ohne Aufruf", ERSTE, "    raise NochOffen", ["probe.py: tu_was: " + REGEL_RUMPF]),
    ("raise ohne Text", ERSTE, "    raise NochOffen()", ["probe.py: tu_was: " + REGEL_RUMPF]),
    (
        "raise mit zwei Texten",
        ERSTE,
        '    raise NochOffen("Mission 4: Probe", "x")',
        ["probe.py: tu_was: " + REGEL_RUMPF],
    ),
    (
        "raise mit berechnetem Text",
        ERSTE,
        '    raise NochOffen("Mission 4: " + "Probe")',
        ["probe.py: tu_was: " + REGEL_RUMPF],
    ),
    (
        "raise mit Ursache",
        ERSTE,
        f"    {OFFEN} from None",
        ["probe.py: tu_was: " + REGEL_RUMPF],
    ),
    (
        "raise über das Modul",
        ERSTE,
        '    raise fehler.NochOffen("Mission 4: Probe")',
        ["probe.py: tu_was: " + REGEL_RUMPF],
    ),
    (
        "falsche Nummer",
        ERSTE,
        '    raise NochOffen("Mission 5: Probe")',
        ["probe.py: tu_was: " + REGEL_TEXT],
    ),
    (
        "falscher Titel",
        ERSTE,
        '    raise NochOffen("Mission 4: Probe!")',
        ["probe.py: tu_was: " + REGEL_TEXT],
    ),
    (
        "Text der Referenz",
        ERSTE,
        '    raise NochOffen("Referenz folgt: Mission 4")',
        ["probe.py: tu_was: " + REGEL_TEXT],
    ),
    (
        "Methode ohne Docstring gelöst",
        IN_INIT,
        "    def __init__(self, a):\n        self.a = a",
        ["probe.py: Ding.__init__: " + REGEL_RUMPF],
    ),
    (
        "Methode mit Docstring gelöst",
        IN_MACH,
        '        """Mit Docstring."""\n        return 1',
        ["probe.py: Ding.mach: " + REGEL_RUMPF],
    ),
    ("Funktion umbenannt", "def tu_was(", "def tu_etwas(", ["probe.py: tu_was: " + REGEL_NAME]),
    ("Klasse umbenannt", "class Ding:", "class Dings:", ["probe.py: Ding: " + REGEL_NAME]),
    ("Tafel fehlt", "TAFEL = ", "TAFELN = ", ["probe.py: TAFEL: " + REGEL_NAME]),
    (
        "Funktion nur unter einer Bedingung",
        "def tu_was(a, b=2):\n" + ERSTE,
        f"if True:\n    def tu_was(a, b=2):\n        {OFFEN}",
        ["probe.py: tu_was: " + REGEL_NAME],
    ),
    (
        "zweite, gelöste Fassung weiter unten",
        "def hilfe():",
        "def tu_was(a, b=2):\n    return a\n\n\ndef hilfe():",
        ["probe.py: tu_was: " + REGEL_RUMPF],
    ),
    ("kein Python", "def tu_was(a, b=2):", "def tu_was(a, b=2:", ["probe.py: " + REGEL_DATEI]),
)


def pruefe_text(text, regel=werkstatt_regel, missionen=PROBE):
    with tempfile.TemporaryDirectory() as ordner:
        schreibe_dateien(ordner, {"probe.py": text})
        return finde_verstoesse(ordner, missionen, regel)


def ersetze_einmal(text, alt, neu):
    if text.count(alt) != 1:
        raise AssertionError(f"Der Text kommt nicht genau einmal vor: {alt!r}")
    return text.replace(alt, neu)


class Selbsttest(unittest.TestCase):
    """Beweist an erfundenen Paketen, dass die Suche jede gelöste Stelle findet."""

    def test_ungeloestes_modul_ist_ohne_verstoss(self):
        self.assertEqual([], pruefe_text(GUT))

    def test_jede_art_von_verstoss_wird_gemeldet(self):
        for was, alt, neu, erwartet in FEHLERHAFT:
            with self.subTest(was=was):
                self.assertEqual(erwartet, pruefe_text(ersetze_einmal(GUT, alt, neu)))

    def test_fehlende_datei_ist_ein_verstoss(self):
        with tempfile.TemporaryDirectory() as ordner:
            self.assertEqual(["probe.py: " + REGEL_DATEI], finde_verstoesse(ordner, PROBE))

    def test_jede_mission_wird_mit_ihrer_eigenen_meldung_geprueft(self):
        zwei = [
            {"nummer": 1, "titel": "Eins", "modul": "probe", "namen": ["a"]},
            {"nummer": 2, "titel": "Zwei", "modul": "probe", "namen": ["b"]},
        ]
        vorlage = 'def a():\n    raise NochOffen("{}")\n\n\ndef b():\n    raise NochOffen("{}")\n'
        richtig = vorlage.format("Mission 1: Eins", "Mission 2: Zwei")
        vertauscht = vorlage.format("Mission 2: Zwei", "Mission 1: Eins")
        self.assertEqual([], pruefe_text(richtig, missionen=zwei))
        self.assertEqual(
            ["probe.py: a: " + REGEL_TEXT, "probe.py: b: " + REGEL_TEXT],
            pruefe_text(vertauscht, missionen=zwei),
        )

    def test_die_referenz_darf_fertig_sein_aber_nicht_leer(self):
        referenz = GUT.replace("Mission 4: Probe", "Referenz folgt: Mission 4")
        self.assertEqual([], pruefe_text(referenz, referenz_regel))
        platzhalter = (
            '    """Erklärt, was zu tun ist."""\n    raise NochOffen("Referenz folgt: Mission 4")'
        )
        faelle = (
            ("fertig", "    return a + b", []),
            ("nur Docstring", '    """Text."""', ["probe.py: tu_was: " + REGEL_LEER]),
            ("nur pass", "    pass", ["probe.py: tu_was: " + REGEL_LEER]),
            ("nur Punkte", "    ...", ["probe.py: tu_was: " + REGEL_LEER]),
            (
                "Text der Werkstatt",
                '    raise NochOffen("Mission 4: Probe")',
                ["probe.py: tu_was: " + REGEL_TEXT],
            ),
            (
                "falsche Nummer",
                '    raise NochOffen("Referenz folgt: Mission 5")',
                ["probe.py: tu_was: " + REGEL_TEXT],
            ),
        )
        for was, neu, erwartet in faelle:
            with self.subTest(was=was):
                text = ersetze_einmal(referenz, platzhalter, neu)
                self.assertEqual(erwartet, pruefe_text(text, referenz_regel))


TAFEL_GUT = (
    "def erster(k, t):\n    pass\n\n\ndef letzter(k, t):\n    pass\n\n\n"
    "def staerkster(k, t):\n    pass\n\n\ndef schwaechster(k, t):\n    pass\n\n\n"
    "def naechster(k, t):\n    pass\n\n\ndef eigene(k, t):\n    pass\n\n\n"
    "STRATEGIEN = {\n"
    '    "erster": erster,\n'
    '    "letzter": letzter,\n'
    '    "staerkster": staerkster,\n'
    '    "schwaechster": schwaechster,\n'
    '    "naechster": naechster,\n'
    "}\n"
)


def pruefe_tafel(text, nur_standard):
    with tempfile.TemporaryDirectory() as ordner:
        schreibe_dateien(ordner, {"strategien.py": text})
        return finde_strategie_verstoesse(ordner, nur_standard)


class SelbsttestStrategien(unittest.TestCase):
    def test_die_fuenf_standardnamen_reichen(self):
        self.assertEqual([], pruefe_tafel(TAFEL_GUT, nur_standard=True))
        self.assertEqual([], pruefe_tafel(TAFEL_GUT, nur_standard=False))

    def test_jeder_standardname_muss_an_seiner_funktion_haengen(self):
        for name in ("erster", "letzter", "staerkster", "schwaechster", "naechster"):
            eintrag = f'    "{name}": {name},\n'
            faelle = (
                ("fehlt", ""),
                ("falsch gebunden", f'    "{name}": eigene,\n'),
                ("anderer Schlüssel", f'    "{name}_": {name},\n'),
            )
            for was, neu in faelle:
                with self.subTest(name=name, was=was):
                    text = ersetze_einmal(TAFEL_GUT, eintrag, neu)
                    self.assertEqual(
                        [f"strategien.py: {name}: {REGEL_EINTRAG}"],
                        pruefe_tafel(text, nur_standard=False),
                    )

    def test_die_funktion_zum_namen_muss_es_geben(self):
        text = ersetze_einmal(TAFEL_GUT, "def letzter(k, t):\n    pass\n\n\n", "letzter = erster\n")
        self.assertEqual(
            [f"strategien.py: letzter: {REGEL_EINTRAG}"], pruefe_tafel(text, nur_standard=True)
        )

    def test_ein_sechster_eintrag_ist_nur_in_der_referenz_erlaubt(self):
        text = ersetze_einmal(TAFEL_GUT, "}\n", '    "eigene": eigene,\n}\n')
        self.assertEqual([f"strategien.py: {REGEL_ZUSATZ}"], pruefe_tafel(text, nur_standard=True))
        self.assertEqual([], pruefe_tafel(text, nur_standard=False))

    def test_die_tafel_muss_ausgeschrieben_sein(self):
        for neu in ("STRATEGIEN = dict(erster=erster)\n", "TAFEL = {}\n", "STRATEGIEN = {**x}\n"):
            with self.subTest(neu=neu):
                text = TAFEL_GUT[: TAFEL_GUT.index("STRATEGIEN")] + neu
                self.assertEqual(
                    [f"strategien.py: {REGEL_TABELLE}"], pruefe_tafel(text, nur_standard=False)
                )

    def test_fehlende_datei_ist_ein_verstoss(self):
        with tempfile.TemporaryDirectory() as ordner:
            self.assertEqual(
                [f"strategien.py: {REGEL_DATEI}"], finde_strategie_verstoesse(ordner, True)
            )


class SelbsttestAmEchtenPaket(unittest.TestCase):
    """Löst in einer Kopie der echten Werkstatt jede Stelle einzeln und erwartet eine Meldung."""

    def test_jede_einzelne_geloeste_stelle_der_werkstatt_wird_gemeldet(self):
        with tempfile.TemporaryDirectory() as ordner:
            kopie = pathlib.Path(ordner) / "werkstatt"
            shutil.copytree(
                WURZEL / "werkstatt", kopie, ignore=shutil.ignore_patterns("__pycache__")
            )
            self.assertEqual([], finde_verstoesse(kopie, ungeloeste_missionen()))
            stellen = 0
            for datei in sorted(kopie.glob("*.py")):
                original = datei.read_text(encoding="utf-8")
                zeilen = original.split("\n")
                for nummer, zeile in enumerate(zeilen):
                    if "raise NochOffen(" not in zeile:
                        continue
                    einzug = zeile[: len(zeile) - len(zeile.lstrip())]
                    geloest = [*zeilen[:nummer], einzug + "return None", *zeilen[nummer + 1 :]]
                    datei.write_text("\n".join(geloest), encoding="utf-8")
                    verstoesse = finde_verstoesse(kopie, ungeloeste_missionen())
                    with self.subTest(datei=datei.name, zeile=nummer + 1):
                        self.assertEqual(1, len(verstoesse), verstoesse)
                        self.assertTrue(verstoesse[0].startswith(datei.name), verstoesse)
                        self.assertTrue(verstoesse[0].endswith(REGEL_RUMPF), verstoesse)
                    stellen += 1
                datei.write_text(original, encoding="utf-8")
            self.assertGreater(stellen, 50, "In der Werkstatt stehen zu wenige Platzhalter.")


if __name__ == "__main__":
    unittest.main()
