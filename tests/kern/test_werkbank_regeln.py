"""Die Werkbank, zweiter Teil: Regeln, die beim Bauen der Werkbank festgelegt wurden.

``test_werkbank.py`` prüft, was die Aufgabe verlangt. Hier stehen die Fälle, die dort offen
geblieben waren, und die Verzeichnisse und Proben der Werkbank selbst. Die Probe-Pakete
kommen aus ``test_werkbank.py``.
"""

import importlib
import inspect
import os
import sys
import unittest

from rudersdorf import werkbank as werkbank_modul
from rudersdorf.fehler import Lernfehler, NochOffen
from rudersdorf.werkbank import ABHAENGIG, FAEHIGKEITEN, PROBEN, Werkbank, waehle_paket
from tests.kern import test_werkbank as basis

ERSTER_ECHT = """def erster(kandidaten, turm):
    return ("echt", kandidaten, turm)
"""
ERSTER_FEHLER = """def erster(kandidaten, turm):
    return kandidaten[99]
"""
ERSTER_SPAET_OFFEN = """def erster(kandidaten, turm):
    if turm == "spaet":
        raise NochOffen("Mission 7: Zielstrategien")
    return ("echt", kandidaten, turm)
"""
EIGENE_STRATEGIE = """def eigene(kandidaten, turm):
    return kandidaten[99]


STRATEGIEN = {"erster": erster, "eigene": eigene}
"""
STRATEGIEN_ALS_LISTE = "STRATEGIEN = [erster, letzter]\n"
SCHADEN_ZWEI_PARAMETER = """def berechne_schaden(schaden, art):
    return schaden
"""
FROST_METHODE_FEHLER = """class Frost(_Fertig):
    def __init__(self, dauer, faktor):
        self.faktor = faktor

    def tempo_faktor(self):
        return self.faktor / 0
"""
FROST_BAUPLAN_FEHLER = """class Frost(_Fertig):
    def __init__(self, dauer, faktor):
        self.faktor = faktor / 0
"""
SCHADEN_MIT_HELFER = """def berechne_schaden(schaden, art, resistenzen):
    return _anteil(schaden)


def _anteil(schaden):
    return schaden / 0
"""
SCHADEN_MIT_HELFERMODUL = """from . import helfer


def berechne_schaden(schaden, art, resistenzen):
    return helfer.WERT
"""
FROST_OHNE_METHODEN = """class Frost:
    def __init__(self, dauer, faktor):
        self.faktor = faktor

    @property
    def staerke(self):
        raise NochOffen("Mission 12: Effekte")
"""
NACHBARN_MIT_RUECKRUF = """def nachbarn(zelle, breite, hoehe):
    return breite()
"""
MODUL_MIT_FEHLER_OBEN = '''"""Ein Modul, das schon beim Laden scheitert."""

GRENZE = 1 / 0
'''
MODUL_MIT_FEHLENDEM_IMPORT = '''"""Ein Modul, das etwas importiert, das es nicht gibt."""

import gibt_es_nicht_wb_probe
'''


class ErsatzFrostMitStaerke(basis.ErsatzFrost):
    staerke = "ersatz"


def ersatz_zufall(kandidaten, turm):
    return ("zufall", kandidaten, turm)


class Verzeichnisse(unittest.TestCase):
    def test_jede_faehigkeit_hat_missionen_ein_modul_und_namen(self):
        self.assertEqual(18, len(FAEHIGKEITEN))
        for schluessel, eintrag in FAEHIGKEITEN.items():
            with self.subTest(faehigkeit=schluessel):
                self.assertEqual({"missionen", "modul", "namen"}, set(eintrag))
                self.assertTrue(eintrag["missionen"])
                self.assertTrue(eintrag["namen"])
                module = {
                    mission["modul"]
                    for mission in basis.MISSIONEN
                    if mission["faehigkeit"] == schluessel
                }
                self.assertEqual({eintrag["modul"]}, module, "Eine Fähigkeit, ein Modul.")

    def test_einzelne_eintraege_stimmen_mit_dem_verzeichnis_der_missionen(self):
        self.assertEqual(
            {"missionen": [2, 3, 4], "modul": "raster", "namen": basis_namen("wegfindung")},
            FAEHIGKEITEN["wegfindung"],
        )
        self.assertEqual(
            ["nachbarn", "ist_begehbar", "abstandskarte", "naechster_schritt"],
            FAEHIGKEITEN["wegfindung"]["namen"],
        )
        self.assertEqual([7, 8], FAEHIGKEITEN["strategien"]["missionen"])
        self.assertEqual(
            1, FAEHIGKEITEN["strategien"]["namen"].count("STRATEGIEN"), "Jeder Name nur einmal."
        )

    def test_abhaengig_ist_die_tabelle_des_vertrags(self):
        erwartet = {schluessel: [] for schluessel in FAEHIGKEITEN}
        erwartet["bauregel"] = ["wegfindung"]
        erwartet["magie"] = ["kettenblitz", "effekte"]
        erwartet["bot"] = ["wegfindung", "bauregel", "reichweite", "strategien"]
        self.assertEqual(erwartet, ABHAENGIG)


def basis_namen(faehigkeit):
    """Liefert die Namen einer Fähigkeit direkt aus dem Verzeichnis der Missionen."""
    namen = []
    for mission in basis.MISSIONEN:
        if mission["faehigkeit"] == faehigkeit:
            namen.extend(name for name in mission["namen"] if name not in namen)
    return namen


class Proben(unittest.TestCase):
    """Die Proben gegen die ungelöste Werkstatt, so wie sie ausgeliefert wird."""

    def test_jede_faehigkeit_hat_proben(self):
        self.assertEqual(list(FAEHIGKEITEN), list(PROBEN))
        for schluessel, proben in PROBEN.items():
            self.assertTrue(proben, f"{schluessel} hat keine Probe.")

    def test_jede_probe_erreicht_den_code_der_werkstatt(self):
        # Eine Probe mit falschen Argumenten bekäme TypeError statt NochOffen.
        for schluessel, proben in PROBEN.items():
            modul = importlib.import_module(f"werkstatt.{FAEHIGKEITEN[schluessel]['modul']}")
            for nummer, probe in enumerate(proben, start=1):
                with self.subTest(faehigkeit=schluessel, probe=nummer):
                    with self.assertRaises(NochOffen):
                        probe(modul)

    def test_die_proben_nennen_jeden_namen_der_faehigkeit(self):
        # STRATEGIEN ist ein Wörterbuch und wird nicht aufgerufen; alles andere schon.
        for schluessel, proben in PROBEN.items():
            quelltext = "\n".join(inspect.getsource(probe) for probe in proben)
            for name in FAEHIGKEITEN[schluessel]["namen"]:
                if name == "STRATEGIEN":
                    continue
                with self.subTest(faehigkeit=schluessel, name=name):
                    self.assertIn(f".{name}(", quelltext)

    def test_die_ausgelieferte_werkstatt_hat_alles_offen(self):
        werkbank = Werkbank("werkstatt")
        self.assertEqual(list(FAEHIGKEITEN), werkbank.offene())
        for schluessel in FAEHIGKEITEN:
            self.assertEqual([], werkbank.wartet_auf(schluessel))

    def test_eine_probe_veraendert_die_eingabe_der_naechsten_nicht(self):
        self.assertIsNot(werkbank_modul.probe_raster(), werkbank_modul.probe_raster())
        self.assertIsNot(werkbank_modul.probe_zustand(), werkbank_modul.probe_zustand())
        self.assertIsNot(werkbank_modul.probe_sicht(), werkbank_modul.probe_sicht())


# Mit Absicht ausgeschrieben: die Fähigkeiten, deren Referenz fertig ist (Spuren A bis C).
# Wer eine weitere Spur der Referenz baut, trägt ihre Fähigkeiten hier ein.
IN_DER_REFERENZ_GELOEST = (
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
)


class ProbenGegenDieReferenz(unittest.TestCase):
    """Die Proben gegen die fertige Referenz.

    Die ungelöste Werkstatt meldet sich schon im Bauplan einer Klasse als offen. Ob eine Probe
    auch die Methoden richtig aufruft, zeigt sich darum erst an gelöstem Code. Und die Werkbank
    überhört beim Proben jeden anderen Fehler: Eine Probe mit falschen Argumenten hielte eine
    gelöste Mission stillschweigend für gelöst, ohne sie je erreicht zu haben.
    """

    def test_jede_probe_laeuft_an_der_referenz_ohne_fehler_durch(self):
        for schluessel in IN_DER_REFERENZ_GELOEST:
            modul = importlib.import_module(f"loesung.{FAEHIGKEITEN[schluessel]['modul']}")
            for nummer, probe in enumerate(PROBEN[schluessel], start=1):
                with self.subTest(faehigkeit=schluessel, probe=nummer):
                    try:
                        probe(modul)
                    except Exception as fehler:
                        self.fail(
                            f"Die Probe {nummer} für {schluessel} passt nicht zur Referenz: "
                            f"{type(fehler).__name__}: {fehler}"
                        )

    def test_die_werkbank_haelt_diese_faehigkeiten_der_referenz_fuer_geloest(self):
        werkbank = Werkbank("loesung")
        for schluessel in IN_DER_REFERENZ_GELOEST:
            with self.subTest(faehigkeit=schluessel):
                self.assertFalse(werkbank.ist_offen(schluessel))
                self.assertEqual([], werkbank.wartet_auf(schluessel))

    def test_die_proben_der_klassen_rufen_jede_methode_der_mission_selbst_auf(self):
        # Eine halb gelöste Klasse meldet sich vielleicht nur in einer einzigen Methode als
        # offen. Darum muss die Probe jede Methode jeder Klasse selbst aufrufen, auch die
        # geerbten: Es genügt nicht, dass eine andere Methode sie nebenbei benutzt.
        for schluessel in ("effekte", "faehigkeiten"):
            modul = importlib.import_module(f"loesung.{FAEHIGKEITEN[schluessel]['modul']}")
            erwartet = set()
            for name in FAEHIGKEITEN[schluessel]["namen"]:
                klasse = getattr(modul, name)
                if isinstance(klasse, type):
                    for methode, _ in inspect.getmembers(klasse, inspect.isfunction):
                        if not methode.startswith("_"):
                            erwartet.add((name, methode))
            mitschrift = Mitschrift()
            for probe in PROBEN[schluessel]:
                probe(mitschrift)
            self.assertEqual(set(), erwartet - mitschrift.aufrufe, schluessel)


class Mitschrift:
    """Steht an der Stelle eines Moduls der Werkstatt und schreibt nur mit.

    Jeder Name mit großem Anfangsbuchstaben ist eine Klasse: Ihre Objekte merken sich in
    ``aufrufe`` jedes Paar (Klasse, Methode), das eine Probe bei ihnen aufruft. Jeder andere
    Name ist eine Funktion, die nichts tut.
    """

    def __init__(self):
        self.aufrufe = set()

    def __getattr__(self, name):
        if name[0].isupper():
            return lambda *args, **kwargs: MitschriftObjekt(self.aufrufe, name)
        return lambda *args, **kwargs: None


class MitschriftObjekt:
    def __init__(self, aufrufe, klasse):
        self._aufrufe = aufrufe
        self._klasse = klasse

    def __getattr__(self, methode):
        self._aufrufe.add((self._klasse, methode))
        return lambda *args, **kwargs: None


class Entscheidungen(basis.WerkbankTest):
    def test_altes_objekt_antwortet_nach_dem_oeffnen_ueber_den_ersatz(self):
        self.trage_ersatz_ein({"effekte": {"Frost": basis.ErsatzFrost}})
        werkbank = Werkbank(self.paket({"Frost": basis.FROST_SPAET_OFFEN}).name)
        frost = werkbank.erzeuge("effekte", "Frost", 2.0, 0.9)
        self.assertEqual(0.9, frost.tempo_faktor())
        frost.tick(None, 777)
        self.assertEqual(0.25, frost.tempo_faktor(), "Echt und Ersatz dürfen sich nicht mischen.")
        self.assertEqual(0.9, frost.faktor, "Der Ersatz entsteht mit denselben Argumenten.")

    def test_ein_anderes_altes_objekt_wechselt_auch_zum_ersatz(self):
        self.trage_ersatz_ein({"effekte": {"Frost": basis.ErsatzFrost}})
        werkbank = Werkbank(self.paket({"Frost": basis.FROST_SPAET_OFFEN}).name)
        alt = werkbank.erzeuge("effekte", "Frost", 2.0, 0.9)
        werkbank.erzeuge("effekte", "Frost", 2.0, 0.5).tick(None, 777)
        self.assertEqual(0.25, alt.tempo_faktor())

    def test_werkstueck_reicht_werte_weiter_und_behaelt_eigenes_fuer_sich(self):
        werkbank = Werkbank(self.paket({"Frost": basis.FROST_ECHT}).name)
        frost = werkbank.erzeuge("effekte", "Frost", 2.0, 0.5)
        self.assertEqual(0.5, frost.faktor)
        with self.assertRaises(AttributeError):
            _ = frost._gibt_es_nicht

    def test_offene_faehigkeit_fasst_die_klasse_der_werkstatt_nicht_an(self):
        self.trage_ersatz_ein({"effekte": {"Frost": basis.ErsatzFrost}})
        paket = self.paket({"Frost": FROST_BAUPLAN_FEHLER})
        werkbank = Werkbank(paket.name, gesperrt=("effekte",))
        frost = werkbank.erzeuge("effekte", "Frost", 2.0, 0.5)
        self.assertEqual(0.25, frost.tempo_faktor())

    def test_wartet_auf_nennt_nur_missionen_offener_faehigkeiten(self):
        werkbank = Werkbank(self.paket().name, gesperrt=("kettenblitz",))
        self.assertEqual([9], werkbank.wartet_auf("magie"))
        werkbank = Werkbank(self.paket().name, gesperrt=("wegfindung",))
        self.assertEqual([2, 3, 4, 5], werkbank.wartet_auf("bot"))
        werkbank = Werkbank(self.paket().name, gesperrt=("strategien",))
        self.assertEqual([7], werkbank.wartet_auf("bot"))

    def test_schalter_aus_waehlt_die_werkstatt_trotz_variable(self):
        wahl = basis.Paketwahl.wahl
        self.assertEqual("werkstatt", wahl(self, "1", loesung=False))
        self.assertEqual("werkstatt", wahl(self, None, loesung=False))

    def test_nur_die_eins_waehlt_die_loesung(self):
        for wert in ("", "2", "ja", "true", " 1"):
            self.assertEqual("werkstatt", basis.Paketwahl.wahl(self, wert), repr(wert))
        self.assertIs(waehle_paket(True), "loesung")

    def test_fehlender_ersatz_ist_ein_fehler_des_spiels(self):
        self.trage_ersatz_ein({})
        paket = self.paket(
            {"berechne_schaden": basis.SCHADEN_OFFEN, "Frost": basis.FROST_GANZ_OFFEN}
        )
        werkbank = Werkbank(paket.name)
        with self.assertRaises(RuntimeError) as gefangen:
            werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {})
        self.assertIn("schadensarten", str(gefangen.exception))
        self.assertNotIsInstance(gefangen.exception, NotImplementedError)
        with self.assertRaises(RuntimeError) as gefangen:
            werkbank.erzeuge("effekte", "Frost", 2.0, 0.5)
        self.assertIn("effekte", str(gefangen.exception))
        with self.assertRaises(RuntimeError) as gefangen:
            Werkbank(paket.name, gesperrt=("strategien",)).strategien()
        self.assertIn("strategien", str(gefangen.exception))

    def test_unbekannter_name_ist_ein_fehler_des_spiels(self):
        werkbank = Werkbank(self.paket().name)
        with self.assertRaises(RuntimeError) as gefangen:
            werkbank.rufe("schadensarten", "gibt_es_nicht", 1)
        self.assertIn("gibt_es_nicht", str(gefangen.exception))


class Strategien(basis.WerkbankTest):
    def test_geloest_sind_es_die_strategien_der_werkstatt(self):
        self.trage_ersatz_ein({"strategien": {"zufall": ersatz_zufall}})
        werkbank = Werkbank(self.paket({"erster": ERSTER_ECHT}).name)
        strategien = werkbank.strategien()
        self.assertEqual(
            ["erster", "letzter", "staerkster", "schwaechster", "naechster"], list(strategien)
        )
        self.assertEqual(("echt", [1, 2], "turm"), strategien["erster"]([1, 2], "turm"))

    def test_offen_gibt_es_nur_den_zufall(self):
        self.trage_ersatz_ein({"strategien": {"zufall": ersatz_zufall}})
        werkbank = Werkbank(self.paket({"erster": ERSTER_ECHT}).name, gesperrt=("strategien",))
        strategien = werkbank.strategien()
        self.assertEqual(["zufall"], list(strategien))
        self.assertEqual(("zufall", [1], "turm"), strategien["zufall"]([1], "turm"))

    def test_fehler_in_einer_strategie_wird_zum_lernfehler(self):
        paket = self.paket({"erster": ERSTER_FEHLER})
        werkbank = Werkbank(paket.name)
        with self.assertRaises(Lernfehler) as gefangen:
            werkbank.strategien()["erster"]([], None)
        fehler = gefangen.exception
        self.assertEqual(
            ("strategien", "IndexError", 7), (fehler.faehigkeit, fehler.art, fehler.mission)
        )
        self.assertEqual(paket.zeile("strategien", "kandidaten[99]"), fehler.zeile)

    def test_fehler_in_einer_eigenen_strategie_gehoert_zu_mission_8(self):
        paket = self.paket({"STRATEGIEN": EIGENE_STRATEGIE})
        werkbank = Werkbank(paket.name)
        with self.assertRaises(Lernfehler) as gefangen:
            werkbank.strategien()["eigene"]([], None)
        self.assertEqual(8, gefangen.exception.mission)

    def test_noch_offen_in_einer_strategie_schaltet_auf_den_zufall_um(self):
        self.trage_ersatz_ein({"strategien": {"zufall": ersatz_zufall}})
        werkbank = Werkbank(self.paket({"erster": ERSTER_SPAET_OFFEN}).name)
        erster = werkbank.strategien()["erster"]
        self.assertEqual(("echt", [1], "turm"), erster([1], "turm"))
        self.assertEqual(("zufall", [1], "spaet"), erster([1], "spaet"))
        self.assertTrue(werkbank.ist_offen("strategien"))
        self.assertEqual(("zufall", [1], "turm"), erster([1], "turm"))
        self.assertEqual(["zufall"], list(werkbank.strategien()))

    def test_die_echte_funktion_bleibt_auffindbar(self):
        paket = self.paket({"erster": ERSTER_ECHT})
        erster = Werkbank(paket.name).strategien()["erster"]
        self.assertEqual(paket.zeile("strategien", "def erster"), inspect.getsourcelines(erster)[1])

    def test_strategien_als_liste_ist_ein_lernfehler(self):
        werkbank = Werkbank(self.paket({"STRATEGIEN": STRATEGIEN_ALS_LISTE}).name)
        with self.assertRaises(Lernfehler) as gefangen:
            werkbank.strategien()
        self.assertEqual(
            ("strategien", 7), (gefangen.exception.faehigkeit, gefangen.exception.mission)
        )


class FehlerMitOrt(basis.WerkbankTest):
    def test_tippfehler_nennt_datei_und_zeile_des_tippfehlers(self):
        paket = self.paket({"berechne_schaden": basis.SCHADEN_ECHT})
        werkbank = Werkbank(paket.name)
        paket.schreibe("horde", {"berechne_schaden": basis.SCHADEN_TIPPFEHLER})
        with self.assertRaises(Lernfehler) as gefangen:
            werkbank.lade_neu()
        fehler = gefangen.exception
        self.assertTrue(fehler.datei.replace("\\", "/").endswith(f"{paket.name}/horde.py"))
        self.assertEqual(paket.zeile("horde", "def berechne_schaden"), fehler.zeile)
        self.assertEqual("SyntaxError", fehler.art)
        self.assertIsNone(fehler.faehigkeit)
        self.assertIsNone(fehler.mission)
        self.assertIn("SyntaxError", fehler.spur.strip().splitlines()[-1])

    def test_tippfehler_schon_beim_start_ist_ein_lernfehler(self):
        paket = self.paket({"berechne_schaden": basis.SCHADEN_TIPPFEHLER})
        with self.assertRaises(Lernfehler) as gefangen:
            Werkbank(paket.name)
        self.assertEqual("SyntaxError", gefangen.exception.art)

    def test_fehler_beim_laden_eines_moduls_laesst_den_alten_code_laufen(self):
        paket = self.paket({"berechne_schaden": basis.SCHADEN_ECHT})
        werkbank = Werkbank(paket.name)
        paket.schreibe_text("horde", MODUL_MIT_FEHLER_OBEN)
        with self.assertRaises(Lernfehler) as gefangen:
            werkbank.lade_neu()
        fehler = gefangen.exception
        self.assertEqual("ZeroDivisionError", fehler.art)
        self.assertEqual(paket.zeile("horde", "1 / 0"), fehler.zeile)
        self.assertEqual(31, werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}))
        self.assertEqual([], werkbank.offene())
        self.assertEqual([], Werkbank(paket.name).offene(), "Die alten Module sind zurück.")

    def test_fehlender_import_in_einem_modul_ist_ein_lernfehler_und_nicht_offen(self):
        paket = self.paket()
        paket.schreibe_text("horde", MODUL_MIT_FEHLENDEM_IMPORT)
        with self.assertRaises(Lernfehler) as gefangen:
            Werkbank(paket.name)
        self.assertEqual("ModuleNotFoundError", gefangen.exception.art)
        self.assertEqual(paket.zeile("horde", "import gibt_es"), gefangen.exception.zeile)

    def test_lade_neu_vergisst_geloeschte_namen(self):
        paket = self.paket()
        werkbank = Werkbank(paket.name)
        paket.schreibe("horde", ohne_namen=("berechne_schaden",))
        werkbank.lade_neu()
        self.assertEqual(["schadensarten"], werkbank.offene())

    def test_lade_neu_bemerkt_ein_geloeschtes_modul(self):
        paket = self.paket()
        werkbank = Werkbank(paket.name)
        paket.pfad("forschung").unlink()
        werkbank.lade_neu()
        self.assertEqual(["auswertung", "bot"], werkbank.offene())

    def test_fehler_in_einer_methode_nennt_die_mission_der_klasse(self):
        paket = self.paket({"Frost": FROST_METHODE_FEHLER})
        frost = Werkbank(paket.name).erzeuge("effekte", "Frost", 2.0, 0.5)
        with self.assertRaises(Lernfehler) as gefangen:
            frost.tempo_faktor()
        fehler = gefangen.exception
        self.assertEqual(
            ("effekte", 12, "ZeroDivisionError"), (fehler.faehigkeit, fehler.mission, fehler.art)
        )
        self.assertEqual(paket.zeile("horde", "self.faktor / 0"), fehler.zeile)

    def test_fehlende_methode_ist_ein_lernfehler_der_auf_die_klasse_zeigt(self):
        paket = self.paket({"Frost": FROST_OHNE_METHODEN})
        werkbank = Werkbank(paket.name)
        self.assertEqual([], werkbank.offene())
        frost = werkbank.erzeuge("effekte", "Frost", 2.0, 0.5)
        for zugriff in (lambda: frost.tempo_faktor(), lambda: frost.rest):
            with self.assertRaises(Lernfehler) as gefangen:
                zugriff()
            fehler = gefangen.exception
            self.assertEqual(
                ("effekte", 12, "AttributeError"), (fehler.faehigkeit, fehler.mission, fehler.art)
            )
            self.assertTrue(fehler.datei.replace("\\", "/").endswith(f"{paket.name}/horde.py"))
            self.assertEqual(paket.zeile("horde", "class Frost"), fehler.zeile)

    def test_noch_offen_beim_lesen_eines_wertes_schaltet_auf_den_ersatz_um(self):
        self.trage_ersatz_ein({"effekte": {"Frost": ErsatzFrostMitStaerke}})
        werkbank = Werkbank(self.paket({"Frost": FROST_OHNE_METHODEN}).name)
        frost = werkbank.erzeuge("effekte", "Frost", 2.0, 0.5)
        self.assertEqual(0.5, frost.faktor)
        self.assertEqual("ersatz", frost.staerke)
        self.assertTrue(werkbank.ist_offen("effekte"))
        self.assertEqual(0.25, frost.tempo_faktor())

    def test_lade_neu_liest_auch_bei_gleicher_uhrzeit_und_groesse_neu(self):
        paket = self.paket({"berechne_schaden": basis.SCHADEN_ECHT})
        werkbank = Werkbank(paket.name)
        self.assertEqual(31, werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}))
        pfad = paket.pfad("horde")
        zeit = os.stat(pfad).st_mtime
        alt = pfad.read_text(encoding="utf-8")
        neu = alt.replace("schaden * 3 + 1", "schaden * 4 + 1")
        self.assertEqual(len(alt), len(neu))
        pfad.write_text(neu, encoding="utf-8")
        os.utime(pfad, (zeit, zeit))
        werkbank.lade_neu()
        self.assertEqual(41, werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}))

    def test_lade_neu_liest_auch_ein_hilfsmodul_neu(self):
        paket = self.paket()
        paket.schreibe_text("helfer", "WERT = 1\n")
        paket.schreibe("horde", {"berechne_schaden": SCHADEN_MIT_HELFERMODUL})
        werkbank = Werkbank(paket.name)
        self.assertEqual(1, werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}))
        paket.schreibe_text("helfer", "WERT = 2\n")
        werkbank.lade_neu()
        self.assertEqual(2, werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}))

    def test_fehlgeschlagenes_neuladen_laesst_auch_das_hilfsmodul_stehen(self):
        paket = self.paket()
        paket.schreibe_text("helfer", "WERT = 1\n")
        paket.schreibe("horde", {"berechne_schaden": SCHADEN_MIT_HELFERMODUL})
        werkbank = Werkbank(paket.name)
        altes = sys.modules[f"{paket.name}.helfer"]
        paket.schreibe_text("helfer", "WERT = 1 / 0\n")
        with self.assertRaises(Lernfehler):
            werkbank.lade_neu()
        self.assertIs(altes, sys.modules[f"{paket.name}.helfer"])
        self.assertIs(altes, sys.modules[paket.name].helfer)
        self.assertEqual(1, werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}))

    def test_neues_hilfsmodul_aus_einem_fehlgeschlagenen_neuladen_bleibt_nicht_haengen(self):
        paket = self.paket()
        werkbank = Werkbank(paket.name)
        paket.schreibe_text("helfer", "WERT = 1\n")
        kaputt = SCHADEN_MIT_HELFERMODUL + "\n\nGRENZE = 1 / 0\n"
        paket.schreibe("horde", {"berechne_schaden": kaputt})
        with self.assertRaises(Lernfehler):
            werkbank.lade_neu()
        self.assertFalse(hasattr(sys.modules[paket.name], "helfer"))
        paket.schreibe_text("helfer", "WERT = 2\n")
        paket.schreibe("horde", {"berechne_schaden": SCHADEN_MIT_HELFERMODUL})
        werkbank.lade_neu()
        self.assertEqual(2, werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {}))

    def test_der_ort_ist_die_innerste_zeile_in_der_werkstatt(self):
        paket = self.paket({"berechne_schaden": SCHADEN_MIT_HELFER})
        werkbank = Werkbank(paket.name)
        with self.assertRaises(Lernfehler) as gefangen:
            werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {})
        self.assertEqual(paket.zeile("horde", "schaden / 0"), gefangen.exception.zeile)

    def test_falsche_parameter_zeigen_auf_den_anfang_der_funktion(self):
        paket = self.paket({"berechne_schaden": SCHADEN_ZWEI_PARAMETER})
        werkbank = Werkbank(paket.name)
        with self.assertRaises(Lernfehler) as gefangen:
            werkbank.rufe("schadensarten", "berechne_schaden", 10, "feuer", {})
        fehler = gefangen.exception
        self.assertEqual("TypeError", fehler.art)
        self.assertTrue(fehler.datei.replace("\\", "/").endswith(f"{paket.name}/horde.py"))
        self.assertEqual(paket.zeile("horde", "def berechne_schaden"), fehler.zeile)

    def test_fertiger_lernfehler_von_innen_kommt_unveraendert_heraus(self):
        innerer = Lernfehler("schadensarten", "horde.py", 3, "ValueError", "innen", 11)

        def rueckruf():
            raise innerer

        werkbank = Werkbank(self.paket({"nachbarn": NACHBARN_MIT_RUECKRUF}).name)
        with self.assertRaises(Lernfehler) as gefangen:
            werkbank.rufe("wegfindung", "nachbarn", (0, 0), rueckruf, 1)
        self.assertIs(innerer, gefangen.exception)


if __name__ == "__main__":
    unittest.main()
