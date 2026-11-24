"""Die Werkbank: Sie lädt Code der Werkstatt, benutzt Ersatz und meldet Fehler mit Ort.

Jeder Test baut sich ein kleines eigenes Paket in einem Wegwerf-Ordner. Es hat die Module
und Namen aus dem Verzeichnis der Missionen; alles darin gilt als gelöst, bis der Test
einzelne Namen durch eigenen Quelltext ersetzt oder weglässt. ``werkstatt`` und ``loesung``
werden hier nie geladen. Den Ersatz trägt der Test selbst in ``rudersdorf.ersatz.ERSATZ`` ein.
"""

import importlib
import itertools
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

from rudersdorf import ersatz
from rudersdorf.fehler import Lernfehler
from rudersdorf.missionen import MISSIONEN
from rudersdorf.werkbank import Werkbank, waehle_paket

KOPF = '''"""Ein Probe-Modul für die Tests der Werkbank."""

from rudersdorf.fehler import NochOffen


class _Fertig:
    """Eine Klasse, die alles annimmt und auf jede Methode mit None antwortet."""

    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, methode):
        if methode.startswith("__"):
            raise AttributeError(methode)
        return lambda *args, **kwargs: None
'''
FERTIGE_FUNKTION = "def {name}(*args, **kwargs):\n    return None\n"
FERTIGE_KLASSE = "class {name}(_Fertig):\n    pass\n"
FERTIGE_STRATEGIEN = (
    'STRATEGIEN = {"erster": erster, "letzter": letzter, "staerkster": staerkster,'
    ' "schwaechster": schwaechster, "naechster": naechster}\n'
)

SCHADEN_ECHT = """def berechne_schaden(schaden, art, resistenzen):
    return schaden * 3 + 1
"""
SCHADEN_NEU = """def berechne_schaden(schaden, art, resistenzen):
    return schaden * 5
"""
SCHADEN_OFFEN = """def berechne_schaden(schaden, art, resistenzen):
    raise NochOffen("Mission 11: Schadensarten")
"""
SCHADEN_SPAET_OFFEN = """def berechne_schaden(schaden, art, resistenzen):
    if art == "spaet":
        raise NochOffen("Mission 11: Schadensarten")
    return schaden * 3 + 1
"""
SCHADEN_FEHLER = """def berechne_schaden(schaden, art, resistenzen):
    anteil = schaden / 0
    return anteil
"""
SCHADEN_TIPPFEHLER = """def berechne_schaden(schaden, art, resistenzen)
    return schaden * 5
"""
WELLE_ECHT = """def erzeuge_welle(nummer, budget, katalog, zufall):
    return ["ork"] * nummer
"""
NACHBARN_ECHT = """def nachbarn(zelle, breite, hoehe):
    return [("echt", zelle)]
"""
ABSTANDSKARTE_OFFEN = """def abstandskarte(raster, ziel, gesperrt):
    raise NochOffen("Mission 3: Der kürzeste Weg")
"""
FROST_ECHT = """class Frost(_Fertig):
    def __init__(self, dauer, faktor):
        self.faktor = faktor

    def tempo_faktor(self):
        return self.faktor
"""
FROST_METHODE_OFFEN = """class Frost(_Fertig):
    def __init__(self, dauer, faktor):
        self.faktor = faktor

    def tempo_faktor(self):
        raise NochOffen("Mission 12: Effekte")
"""
FROST_GANZ_OFFEN = """class Frost(_Fertig):
    def __init__(self, dauer, faktor):
        raise NochOffen("Mission 12: Effekte")

    def tempo_faktor(self):
        raise NochOffen("Mission 12: Effekte")
"""
FROST_SPAET_OFFEN = """class Frost(_Fertig):
    def __init__(self, dauer, faktor):
        self.faktor = faktor

    def tick(self, gegner, sekunden):
        if sekunden == 777:
            raise NochOffen("Mission 12: Effekte")

    def tempo_faktor(self):
        return self.faktor
"""
ZAUBER_OFFEN = """class Zauber(_Fertig):
    def __init__(self, name, kosten, abklingzeit):
        raise NochOffen("Mission 19: Mana und Abklingzeit")
"""


def ersatz_schaden(schaden, art, resistenzen):
    return ("ersatz", schaden, art)


def ersatz_nachbarn(zelle, breite, hoehe):
    return [("ersatz", zelle)]


class ErsatzFrost:
    def __init__(self, dauer, faktor):
        self.faktor = faktor

    def tick(self, gegner, sekunden):
        return "ersatz-tick"

    def tempo_faktor(self):
        return 0.25


def module_und_namen():
    """Liefert Modul -> Namen aller Missionen, die dem Spiel eine Fähigkeit geben."""
    ergebnis = {}
    for eintrag in MISSIONEN:
        if eintrag["faehigkeit"] is None:
            continue
        namen = ergebnis.setdefault(eintrag["modul"], [])
        for name in eintrag["namen"]:
            if name not in namen:
                namen.append(name)
    return ergebnis


def fertiger_quelltext(name):
    """Liefert Quelltext, mit dem ``name`` als gelöst gilt."""
    if name == "STRATEGIEN":
        return FERTIGE_STRATEGIEN
    if name[0].isupper():
        return FERTIGE_KLASSE.format(name=name)
    return FERTIGE_FUNKTION.format(name=name)


class Probepaket:
    """Ein Wegwerf-Paket mit eigenem Namen; beim Aufräumen verschwindet es spurlos."""

    nummern = itertools.count(1)

    def __init__(self, test, ersetzt=None, ohne_module=(), ohne_namen=()):
        self.name = f"wb_probe_{os.getpid()}_{next(self.nummern)}"
        self._wurzel = tempfile.TemporaryDirectory()
        self.ordner = pathlib.Path(self._wurzel.name) / self.name
        self.ordner.mkdir()
        (self.ordner / "__init__.py").write_text('"""Ein Probe-Paket."""\n', encoding="utf-8")
        self._uhr = 1_000_000_000
        for modul in module_und_namen():
            if modul not in ohne_module:
                self.schreibe(modul, ersetzt, ohne_namen)
        sys.path.insert(0, self._wurzel.name)
        importlib.invalidate_caches()
        test.addCleanup(self.raeume_auf)

    def pfad(self, modul):
        return self.ordner / f"{modul}.py"

    def schreibe(self, modul, ersetzt=None, ohne_namen=()):
        """Schreibt ein Modul neu; ``ersetzt`` gibt für einzelne Namen eigenen Quelltext."""
        ersetzt = ersetzt or {}
        teile = [KOPF]
        for name in module_und_namen()[modul]:
            if name not in ohne_namen:
                teile.append(ersetzt.get(name) or fertiger_quelltext(name))
        self.schreibe_text(modul, "\n\n".join(teile))

    def schreibe_text(self, modul, text):
        """Schreibt beliebigen Text; die Uhrzeit der Datei rückt dabei jedes Mal weiter."""
        self.pfad(modul).write_text(text, encoding="utf-8")
        self._uhr += 10
        os.utime(self.pfad(modul), (self._uhr, self._uhr))

    def zeile(self, modul, stelle):
        """Liefert die Nummer der ersten Zeile des Moduls, in der ``stelle`` steht."""
        zeilen = self.pfad(modul).read_text(encoding="utf-8").splitlines()
        for nummer, zeile in enumerate(zeilen, start=1):
            if stelle in zeile:
                return nummer
        raise AssertionError(f"{stelle!r} steht nicht in {modul}.py")

    def raeume_auf(self):
        if self._wurzel.name in sys.path:
            sys.path.remove(self._wurzel.name)
        for name in list(sys.modules):
            if name == self.name or name.startswith(self.name + "."):
                del sys.modules[name]
        importlib.invalidate_caches()
        self._wurzel.cleanup()


class WerkbankTest(unittest.TestCase):
    """Gemeinsame Helfer: ein Probe-Paket bauen und eigenen Ersatz eintragen."""

    def paket(self, ersetzt=None, ohne_module=(), ohne_namen=()):
        return Probepaket(self, ersetzt, ohne_module, ohne_namen)

    def trage_ersatz_ein(self, eintraege):
        """Für die Dauer des Tests steht in ERSATZ genau das, was der Test einträgt."""
        flicken = mock.patch.dict(ersatz.ERSATZ, eintraege, clear=True)
        flicken.start()
        self.addCleanup(flicken.stop)


class Aufrufe(WerkbankTest):
    def test_rufe_liefert_den_wert_der_funktion(self):
        paket = self.paket({"berechne_schaden": SCHADEN_ECHT, "erzeuge_welle": WELLE_ECHT})
        werkbank = Werkbank(paket.name)
        self.assertEqual(paket.name, werkbank.paket)
        self.assertEqual(31, werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}))
        self.assertEqual(["ork"] * 3, werkbank.rufe("wellen", "erzeuge_welle", 3, 50, {}, None))
        self.assertFalse(werkbank.ist_offen("schadensarten"))

    def test_rufe_reicht_benannte_argumente_weiter(self):
        paket = self.paket({"berechne_schaden": SCHADEN_ECHT})
        werkbank = Werkbank(paket.name)
        ergebnis = werkbank.rufe(
            "schadensarten", "berechne_schaden", schaden=2, art="eis", resistenzen={}
        )
        self.assertEqual(7, ergebnis)

    def test_offene_funktion_wird_durch_den_ersatz_beantwortet(self):
        self.trage_ersatz_ein({"schadensarten": {"berechne_schaden": ersatz_schaden}})
        paket = self.paket({"berechne_schaden": SCHADEN_OFFEN})
        werkbank = Werkbank(paket.name)
        ergebnis = werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {})
        self.assertEqual(("ersatz", 10, "feuer"), ergebnis)
        self.assertTrue(werkbank.ist_offen("schadensarten"))

    def test_noch_offen_erst_beim_aufruf_schaltet_auf_den_ersatz_um(self):
        self.trage_ersatz_ein({"schadensarten": {"berechne_schaden": ersatz_schaden}})
        paket = self.paket({"berechne_schaden": SCHADEN_SPAET_OFFEN})
        werkbank = Werkbank(paket.name)
        self.assertEqual(31, werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}))
        self.assertEqual(
            ("ersatz", 10, "spaet"),
            werkbank.rufe("schadensarten", "berechne_schaden", 10, "spaet", {}),
        )
        self.assertTrue(werkbank.ist_offen("schadensarten"))
        self.assertIn("schadensarten", werkbank.offene())
        self.assertEqual(
            ("ersatz", 10, "feuer"),
            werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}),
            "Solange die Fähigkeit offen ist, antwortet nur noch der Ersatz.",
        )

    def test_ersatz_wird_bei_jedem_aufruf_frisch_nachgeschlagen(self):
        self.trage_ersatz_ein({"schadensarten": {"berechne_schaden": ersatz_schaden}})
        paket = self.paket({"berechne_schaden": SCHADEN_OFFEN})
        werkbank = Werkbank(paket.name)
        self.assertEqual(
            ("ersatz", 10, "feuer"),
            werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}),
        )
        anderer = {"schadensarten": {"berechne_schaden": lambda *args: "anderer Ersatz"}}
        with mock.patch.dict(ersatz.ERSATZ, anderer):
            self.assertEqual(
                "anderer Ersatz",
                werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}),
                "Die Werkbank darf sich das Verzeichnis ERSATZ nicht merken.",
            )

    def test_halb_geloeste_faehigkeit_benutzt_ueberall_den_ersatz(self):
        self.trage_ersatz_ein({"wegfindung": {"nachbarn": ersatz_nachbarn}})
        paket = self.paket({"nachbarn": NACHBARN_ECHT, "abstandskarte": ABSTANDSKARTE_OFFEN})
        werkbank = Werkbank(paket.name)
        self.assertEqual(
            [("ersatz", (1, 1))],
            werkbank.rufe("wegfindung", "nachbarn", (1, 1), 3, 3),
            "Echte und Ersatz-Regeln einer Fähigkeit dürfen sich nicht mischen.",
        )
        self.assertTrue(werkbank.ist_offen("wegfindung"))

    def test_geloeste_faehigkeit_benutzt_die_echte_funktion(self):
        self.trage_ersatz_ein({"wegfindung": {"nachbarn": ersatz_nachbarn}})
        paket = self.paket({"nachbarn": NACHBARN_ECHT})
        werkbank = Werkbank(paket.name)
        self.assertEqual([("echt", (1, 1))], werkbank.rufe("wegfindung", "nachbarn", (1, 1), 3, 3))
        self.assertFalse(werkbank.ist_offen("wegfindung"))


class FehlerImLernendenCode(WerkbankTest):
    def fehler_beim_aufruf(self):
        paket = self.paket({"berechne_schaden": SCHADEN_FEHLER})
        werkbank = Werkbank(paket.name)
        with self.assertRaises(Lernfehler) as gefangen:
            werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {})
        return paket, gefangen.exception

    def test_fehler_wird_zum_lernfehler_mit_datei_zeile_art_text_und_mission(self):
        paket, fehler = self.fehler_beim_aufruf()
        self.assertEqual("schadensarten", fehler.faehigkeit)
        datei = fehler.datei.replace("\\", "/")
        self.assertTrue(
            datei.endswith(f"{paket.name}/horde.py"), f"Falsche Datei im Lernfehler: {datei}"
        )
        self.assertEqual(paket.zeile("horde", "schaden / 0"), fehler.zeile)
        self.assertEqual("ZeroDivisionError", fehler.art)
        self.assertEqual("division by zero", fehler.text)
        self.assertEqual(11, fehler.mission)

    def test_lernfehler_traegt_die_urspruengliche_spur(self):
        _, fehler = self.fehler_beim_aufruf()
        self.assertIsInstance(fehler.spur, str)
        letzte_zeile = fehler.spur.strip().splitlines()[-1]
        self.assertEqual("ZeroDivisionError: division by zero", letzte_zeile)

    def test_fehler_in_der_probe_haelt_den_start_nicht_auf(self):
        paket = self.paket({"berechne_schaden": SCHADEN_FEHLER})
        werkbank = Werkbank(paket.name)
        self.assertFalse(
            werkbank.ist_offen("schadensarten"),
            "Ein Fehler beim Ausprobieren heißt nicht, dass die Mission offen ist.",
        )
        self.assertEqual([], werkbank.offene())


class Offenheit(WerkbankTest):
    def test_ein_geloestes_paket_hat_nichts_offen(self):
        werkbank = Werkbank(self.paket().name)
        self.assertEqual([], werkbank.offene())

    def test_offene_stehen_schon_vor_dem_ersten_aufruf_fest(self):
        paket = self.paket(
            {
                "auswertung": 'def auswertung(*args):\n    raise NochOffen("Mission 25")\n',
                "erzeuge_welle": 'def erzeuge_welle(*args):\n    raise NochOffen("Mission 15")\n',
                "berechne_schaden": SCHADEN_OFFEN,
                "lies_karte": 'def lies_karte(text):\n    raise NochOffen("Mission 1")\n',
            }
        )
        werkbank = Werkbank(paket.name)
        self.assertEqual(["karten", "schadensarten", "wellen", "auswertung"], werkbank.offene())
        self.assertTrue(werkbank.ist_offen("wellen"))
        self.assertFalse(werkbank.ist_offen("effekte"))

    def test_gesperrt_macht_nur_diese_faehigkeit_auf(self):
        self.trage_ersatz_ein({"schadensarten": {"berechne_schaden": ersatz_schaden}})
        paket = self.paket({"berechne_schaden": SCHADEN_ECHT})
        werkbank = Werkbank(paket.name, gesperrt=("schadensarten",))
        self.assertEqual(["schadensarten"], werkbank.offene())
        self.assertTrue(werkbank.ist_offen("schadensarten"))
        self.assertEqual(
            ("ersatz", 10, "feuer"),
            werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}),
        )
        werkbank.lade_neu()
        self.assertEqual(["schadensarten"], werkbank.offene(), "Gesperrt bleibt gesperrt.")

    def test_gesperrte_wegfindung_macht_auch_die_wartenden_auf(self):
        werkbank = Werkbank(self.paket().name, gesperrt=("wegfindung",))
        self.assertEqual(["wegfindung", "bauregel", "bot"], werkbank.offene())
        self.assertEqual([2, 3, 4], werkbank.wartet_auf("bauregel"))
        self.assertEqual([], werkbank.wartet_auf("wegfindung"))

    def test_fehlendes_modul_macht_seine_faehigkeiten_auf(self):
        werkbank = Werkbank(self.paket(ohne_module=("horde",)).name)
        self.assertEqual(
            ["schadensarten", "effekte", "faehigkeiten", "wellen", "magie"], werkbank.offene()
        )

    def test_fehlender_name_macht_seine_faehigkeit_auf(self):
        self.trage_ersatz_ein({"schadensarten": {"berechne_schaden": ersatz_schaden}})
        werkbank = Werkbank(self.paket(ohne_namen=("berechne_schaden",)).name)
        self.assertEqual(["schadensarten"], werkbank.offene())
        self.assertEqual(
            ("ersatz", 10, "feuer"),
            werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}),
        )

    def test_fehlende_klasse_macht_ihre_faehigkeit_auf(self):
        werkbank = Werkbank(self.paket(ohne_namen=("Frost",)).name)
        self.assertEqual(["effekte", "magie"], werkbank.offene())

    def test_leeres_paket_hat_alles_offen(self):
        werkbank = Werkbank(self.paket(ohne_module=tuple(module_und_namen())).name)
        self.assertEqual(
            [
                "karten",
                "wegfindung",
                "bauregel",
                "reichweite",
                "strategien",
                "kettenblitz",
                "ausbau",
                "schadensarten",
                "effekte",
                "faehigkeiten",
                "wellen",
                "voraussetzungen",
                "boni",
                "bauplan",
                "magie",
                "speichern",
                "auswertung",
                "bot",
            ],
            werkbank.offene(),
        )


class Voraussetzungen(WerkbankTest):
    def test_magie_wartet_auf_gesperrte_effekte(self):
        werkbank = Werkbank(self.paket().name, gesperrt=("effekte",))
        self.assertTrue(werkbank.ist_offen("magie"))
        self.assertEqual([12, 13], werkbank.wartet_auf("magie"))
        self.assertEqual(["effekte", "magie"], werkbank.offene())

    def test_magie_wartet_auf_ungeloeste_effekte(self):
        werkbank = Werkbank(self.paket({"Frost": FROST_GANZ_OFFEN}).name)
        self.assertTrue(werkbank.ist_offen("magie"))
        self.assertEqual([12, 13], werkbank.wartet_auf("magie"))

    def test_magie_ist_nicht_offen_wenn_alles_geloest_ist(self):
        werkbank = Werkbank(self.paket().name)
        self.assertFalse(werkbank.ist_offen("magie"))
        self.assertEqual([], werkbank.wartet_auf("magie"))

    def test_selbst_offene_magie_wartet_auf_nichts(self):
        werkbank = Werkbank(self.paket({"Zauber": ZAUBER_OFFEN}).name)
        self.assertEqual(["magie"], werkbank.offene())
        self.assertEqual([], werkbank.wartet_auf("magie"))


class NeuLaden(WerkbankTest):
    def test_lade_neu_benutzt_den_geaenderten_code(self):
        paket = self.paket({"berechne_schaden": SCHADEN_ECHT})
        werkbank = Werkbank(paket.name)
        self.assertEqual(31, werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}))
        paket.schreibe("horde", {"berechne_schaden": SCHADEN_NEU})
        werkbank.lade_neu()
        self.assertEqual(50, werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}))

    def test_lade_neu_bemerkt_eine_geloeste_mission(self):
        paket = self.paket({"berechne_schaden": SCHADEN_OFFEN})
        werkbank = Werkbank(paket.name)
        self.assertEqual(["schadensarten"], werkbank.offene())
        paket.schreibe("horde", {"berechne_schaden": SCHADEN_ECHT})
        werkbank.lade_neu()
        self.assertEqual([], werkbank.offene())
        self.assertEqual(31, werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}))

    def test_lade_neu_bemerkt_eine_wieder_offene_mission(self):
        self.trage_ersatz_ein({"schadensarten": {"berechne_schaden": ersatz_schaden}})
        paket = self.paket({"berechne_schaden": SCHADEN_ECHT})
        werkbank = Werkbank(paket.name)
        self.assertEqual([], werkbank.offene())
        paket.schreibe("horde", {"berechne_schaden": SCHADEN_OFFEN})
        werkbank.lade_neu()
        self.assertEqual(["schadensarten"], werkbank.offene())
        self.assertEqual(
            ("ersatz", 10, "feuer"),
            werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}),
        )

    def test_tippfehler_beim_neuladen_laesst_den_alten_code_laufen(self):
        paket = self.paket({"berechne_schaden": SCHADEN_ECHT})
        werkbank = Werkbank(paket.name)
        paket.schreibe("horde", {"berechne_schaden": SCHADEN_TIPPFEHLER})
        with self.assertRaises(Lernfehler):
            werkbank.lade_neu()
        self.assertEqual(
            31,
            werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}),
            "Nach einem Tippfehler muss der vorige Code weiter antworten.",
        )
        self.assertEqual([], werkbank.offene())
        paket.schreibe("horde", {"berechne_schaden": SCHADEN_NEU})
        werkbank.lade_neu()
        self.assertEqual(50, werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}))


class Klassen(WerkbankTest):
    def test_erzeuge_baut_die_klasse_der_werkstatt(self):
        self.trage_ersatz_ein({"effekte": {"Frost": ErsatzFrost}})
        werkbank = Werkbank(self.paket({"Frost": FROST_ECHT}).name)
        frost = werkbank.erzeuge("effekte", "Frost", 2.0, 0.5)
        self.assertEqual(0.5, frost.tempo_faktor())
        self.assertFalse(werkbank.ist_offen("effekte"))

    def test_offene_methode_wird_von_der_ersatzklasse_beantwortet(self):
        self.trage_ersatz_ein({"effekte": {"Frost": ErsatzFrost}})
        werkbank = Werkbank(self.paket({"Frost": FROST_METHODE_OFFEN}).name)
        frost = werkbank.erzeuge("effekte", "Frost", 2.0, 0.5)
        self.assertEqual(0.25, frost.tempo_faktor())
        self.assertTrue(werkbank.ist_offen("effekte"))

    def test_offener_bauplan_der_klasse_fuehrt_zur_ersatzklasse(self):
        self.trage_ersatz_ein({"effekte": {"Frost": ErsatzFrost}})
        werkbank = Werkbank(self.paket({"Frost": FROST_GANZ_OFFEN}).name)
        frost = werkbank.erzeuge("effekte", "Frost", 2.0, 0.5)
        self.assertEqual(0.25, frost.tempo_faktor())
        self.assertTrue(werkbank.ist_offen("effekte"))

    def test_noch_offen_erst_im_methodenaufruf_schaltet_auf_die_ersatzklasse_um(self):
        self.trage_ersatz_ein({"effekte": {"Frost": ErsatzFrost}})
        werkbank = Werkbank(self.paket({"Frost": FROST_SPAET_OFFEN}).name)
        frost = werkbank.erzeuge("effekte", "Frost", 2.0, 0.5)
        self.assertEqual(0.5, frost.tempo_faktor())
        self.assertEqual("ersatz-tick", frost.tick(None, 777))
        self.assertTrue(werkbank.ist_offen("effekte"))
        neuer_frost = werkbank.erzeuge("effekte", "Frost", 2.0, 0.5)
        self.assertEqual(0.25, neuer_frost.tempo_faktor())


class Paketwahl(unittest.TestCase):
    def wahl(self, wert, loesung=None):
        """Ruft ``waehle_paket`` mit RUDERSDORF_LOESUNG = ``wert`` auf (None: nicht gesetzt)."""
        with mock.patch.dict(os.environ):
            os.environ.pop("RUDERSDORF_LOESUNG", None)
            if wert is not None:
                os.environ["RUDERSDORF_LOESUNG"] = wert
            return waehle_paket(loesung)

    def test_ohne_die_variable_wird_die_werkstatt_gewaehlt(self):
        self.assertEqual("werkstatt", self.wahl(None))

    def test_mit_null_wird_die_werkstatt_gewaehlt(self):
        self.assertEqual("werkstatt", self.wahl("0"))

    def test_mit_eins_wird_die_loesung_gewaehlt(self):
        self.assertEqual("loesung", self.wahl("1"))

    def test_der_schalter_waehlt_die_loesung_auch_ohne_variable(self):
        self.assertEqual("loesung", self.wahl(None, loesung=True))
        self.assertEqual("loesung", self.wahl("0", loesung=True))


if __name__ == "__main__":
    unittest.main()
