#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Anlagen Eingabe App – vereinfachte Registry-Version."""

import flet as ft
from datetime import datetime
from pathlib import Path

from constants import APP_VERSION, APP_NAME, SPALTEN_PRO_EINHEIT
from data_manager import DataManager
from ui_builder import UIBuilder
from ods_exporter import validiere_eintraege, exportiere_anlage_ods
from android_handler import exportiere_zu_downloads as export_downloads, importiere_von_downloads as import_downloads


class AnlagenApp:
    """Hauptanwendung – alle UI-Controls liegen in self.ui[...]"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = f"{APP_NAME} V{APP_VERSION}"
        self.page.scroll = ft.ScrollMode.AUTO

        # Registry für ALLE UI-Elemente
        self.ui = {}

        # Datenpfad
        self.data_path = Path.home() / ".anlagen_app"
        self.data_path.mkdir(exist_ok=True)

        # Manager
        self.data_manager = DataManager(self.data_path)
        self.settings = self.data_manager.lade_settings()

        # Daten
        self.alle_kunden = {}
        self.aktiver_kunde_key = None
        self.next_kunden_id = 1
        self.anlagen_daten = []
        self.next_anlage_id = 1
        self.aktuelle_anlage = None
        self.ausgewaehlte_anlage_id = None
        self.letzte_export_datei = None

        # UIBuilder
        self.ui_builder = UIBuilder(self, page)

        self.init_app()

    # ---------------------------------------------------------
    # Hilfsfunktionen
    # ---------------------------------------------------------

    def show(self, view):
        self.page.controls[:] = [view]
        self.page.update()

    def dialog(self, title, msg):
        """Zeigt einfachen Info-Dialog."""
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(msg),
            actions=[ft.TextButton("OK", on_click=lambda e: self.page.pop_dialog())],
        )
        self.page.show_dialog(dlg)

    def show_file_snackbar(self, action, filename):
        """Zeigt Snackbar für Datei-Operationen (5 Sek)."""
        snackbar = ft.SnackBar(
            content=ft.Text(f"{action}: {filename}"),
            duration=5000,
        )
        self.page.show_snack_bar(snackbar)

    def confirm_dialog(self, title, message, on_yes_callback):
        """Zeigt modalen Bestätigungsdialog mit Ja/Nein Buttons."""
        def handle_yes(e):
            self.page.pop_dialog()
            on_yes_callback()
        
        def handle_no(e):
            self.page.pop_dialog()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("Ja", on_click=handle_yes),
                ft.TextButton("Nein", on_click=handle_no),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)

    def map_set(self, mapping, source):
        for ui_key, data_key in mapping.items():
            if ui_key in self.ui:
                self.ui[ui_key].value = source.get(data_key, "")

    def map_get(self, mapping, target):
        for ui_key, data_key in mapping.items():
            if ui_key in self.ui:
                target[data_key] = self.ui[ui_key].value or ""

    # ---------------------------------------------------------
    # Initialisierung
    # ---------------------------------------------------------

    def init_app(self):
        self.lade_daten()
        haupt = self.ui_builder.erstelle_hauptansicht()
        self.page.add(haupt)
        self.aktualisiere_aktive_daten()

    # ---------------------------------------------------------
    # Daten
    # ---------------------------------------------------------

    def lade_daten(self):
        self.alle_kunden, self.next_kunden_id, self.next_anlage_id = self.data_manager.lade_daten()
        if self.alle_kunden:
            self.aktiver_kunde_key = next(iter(self.alle_kunden))
        self.show_file_snackbar("Geladen", "anlagen_daten.json")

    def speichere_daten(self, _e=None):
        self.speichere_projekt_daten()
        
        # Anlagen-Daten zurückschreiben zum aktiven Kunden
        if self.aktiver_kunde_key and self.aktiver_kunde_key in self.alle_kunden:
            self.alle_kunden[self.aktiver_kunde_key]["anlagen"] = self.anlagen_daten

        out = {}
        for key, kunde in self.alle_kunden.items():
            out[key] = {
                "id": kunde["id"],
                "projekt": kunde.get("projekt", ""),
                "datum": kunde.get("datum", ""),
                "adresse": kunde.get("adresse", ""),
                "plz": kunde.get("plz", ""),
                "ort": kunde.get("ort", ""),
                "ansprechpartner": kunde.get("ansprechpartner", ""),
                "telefonnummer": kunde.get("telefonnummer", ""),
                "email": kunde.get("email", ""),
                "anlagen": kunde.get("anlagen", []),
            }

        ok, fehler = self.data_manager.speichere_daten(out, self.next_kunden_id, self.next_anlage_id)
        if not ok:
            self.dialog("Speicher-Fehler", fehler)
        else:
            self.show_file_snackbar("Gespeichert", "anlagen_daten.json")

    def speichere_projekt_daten(self, _e=None):
        if not self.aktiver_kunde_key:
            return

        kunde = self.alle_kunden[self.aktiver_kunde_key]

        mapping = {
            "kunde_projekt": "projekt",
            "kunde_datum": "datum",
            "kunde_adresse": "adresse",
            "kunde_plz": "plz",
            "kunde_ort": "ort",
            "kunde_ansprechpartner": "ansprechpartner",
            "kunde_telefonnummer": "telefonnummer",
            "kunde_email": "email",
        }

        self.map_get(mapping, kunde)

    def aktualisiere_aktive_daten(self):
        if not self.aktiver_kunde_key:
            return

        kunde = self.alle_kunden[self.aktiver_kunde_key]

        mapping = {
            "kunde_projekt": "projekt",
            "kunde_datum": "datum",
            "kunde_adresse": "adresse",
            "kunde_plz": "plz",
            "kunde_ort": "ort",
            "kunde_ansprechpartner": "ansprechpartner",
            "kunde_telefonnummer": "telefonnummer",
            "kunde_email": "email",
        }

        self.map_set(mapping, kunde)

        self.anlagen_daten = kunde.get("anlagen", [])
        self.aktualisiere_anlagen_tabelle()
        self.page.update()

    # ---------------------------------------------------------
    # Tabelle
    # ---------------------------------------------------------

    def aktualisiere_anlagen_tabelle(self):
        """Aktualisiert die Anlagen-Liste mit RadioButtons."""
        if "anlagen_container" not in self.ui:
            return

        container = self.ui["anlagen_container"]
        container.controls.clear()

        for anlage in self.anlagen_daten:
            anlage_id = str(anlage["id"])
            
            # Erste Zeile: Radio | ID | Beschreibung
            zeile1 = ft.Row([
                ft.Radio(value=anlage_id, label=f"ID {anlage_id}: {anlage['beschreibung']}"),
            ], spacing=5)
            
            # Zweite Zeile: Code | Ort (eingerückt)
            zeile2 = ft.Row([
                ft.Container(width=50),  # Einrückung
                ft.Text(f"Code: {anlage.get('code', '-')}", size=12),
                ft.Text(f"Ort: {anlage.get('plz_ort', '-')}", size=12),
            ], spacing=10)
            
            container.controls.append(zeile1)
            container.controls.append(zeile2)
            container.controls.append(ft.Divider(height=1))

        self.page.update()

    def on_anlage_selected(self, e):
        """Callback wenn Anlage in RadioGroup ausgewählt wird."""
        if e.control.value:
            self.ausgewaehlte_anlage_id = int(e.control.value)

    # ---------------------------------------------------------
    # Kunden
    # ---------------------------------------------------------

    def wechsel_kunden_auswahl(self, e):
        key = e.control.value
        if key in self.alle_kunden:
            self.aktiver_kunde_key = key
            self.aktualisiere_aktive_daten()

    def _navigiere_kunde_links(self, _e):
        keys = list(self.alle_kunden)
        idx = keys.index(self.aktiver_kunde_key)
        self.aktiver_kunde_key = keys[(idx - 1) % len(keys)]
        self.ui["kunden_auswahl"].value = self.aktiver_kunde_key
        self.aktualisiere_aktive_daten()

    def _navigiere_kunde_rechts(self, _e):
        keys = list(self.alle_kunden)
        idx = keys.index(self.aktiver_kunde_key)
        self.aktiver_kunde_key = keys[(idx + 1) % len(keys)]
        self.ui["kunden_auswahl"].value = self.aktiver_kunde_key
        self.aktualisiere_aktive_daten()

    def _kunde_neu_hinzufuegen(self, _e):
        name = (self.ui["kunde_input"].value or "").strip()
        if not name:
            return self.dialog("Fehler", "Bitte Kundennamen eingeben.")
        if name in self.alle_kunden:
            return self.dialog("Fehler", f'Kunde "{name}" existiert bereits.')

        self.alle_kunden[name] = {
            "id": self.next_kunden_id,
            "projekt": "",
            "datum": datetime.now().date().strftime("%Y-%m-%d"),
            "adresse": "",
            "plz": "",
            "ort": "",
            "ansprechpartner": "",
            "telefonnummer": "",
            "email": "",
            "anlagen": [],
        }

        self.next_kunden_id += 1
        self.aktiver_kunde_key = name

        self.ui["kunden_auswahl"].options = [ft.dropdown.Option(k) for k in self.alle_kunden]
        self.ui["kunden_auswahl"].value = name

        self.aktualisiere_aktive_daten()
        self.speichere_daten()

        self.ui["kunde_input"].value = ""
        self.page.update()

        self.dialog("Erfolg", f'Kunde "{name}" hinzugefügt.')

    def _kunde_umbenennen(self, _e):
        if not self.aktiver_kunde_key:
            return self.dialog("Fehler", "Kein Kunde ausgewählt.")

        neuer = (self.ui["kunde_input"].value or "").strip()
        if not neuer:
            return self.dialog("Fehler", "Bitte neuen Namen eingeben.")
        if neuer in self.alle_kunden:
            return self.dialog("Fehler", f'Kunde "{neuer}" existiert bereits.')

        alt = self.aktiver_kunde_key
        self.alle_kunden[neuer] = self.alle_kunden.pop(alt)
        self.aktiver_kunde_key = neuer

        self.ui["kunden_auswahl"].options = [ft.dropdown.Option(k) for k in self.alle_kunden]
        self.ui["kunden_auswahl"].value = neuer

        self.speichere_daten()
        self.ui["kunde_input"].value = ""
        self.page.update()

        self.dialog("Erfolg", f'Kunde umbenannt: "{alt}" → "{neuer}"')

    def kunde_loeschen(self, _e):
        if not self.aktiver_kunde_key:
            return self.dialog("Fehler", "Kein Kunde ausgewählt.")

        def confirm(e):
            dlg.open = False
            self.page.update()
            if e.control.text == "Ja":
                del self.alle_kunden[self.aktiver_kunde_key]
                self.aktiver_kunde_key = next(iter(self.alle_kunden), None)
                self.ui["kunden_auswahl"].options = [ft.dropdown.Option(k) for k in self.alle_kunden]
                self.ui["kunden_auswahl"].value = self.aktiver_kunde_key
                self.aktualisiere_aktive_daten()
                self.speichere_daten()

        dlg = ft.AlertDialog(
            title=ft.Text("Kunde löschen"),
            content=ft.Text(f'Wirklich Kunde "{self.aktiver_kunde_key}" löschen?'),
            actions=[ft.TextButton("Ja", on_click=confirm), ft.TextButton("Nein", on_click=confirm)],
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    # ---------------------------------------------------------
    # Anlagen
    # ---------------------------------------------------------

    def anlage_hinzufuegen(self, _e):
        if not self.aktiver_kunde_key:
            return self.dialog("Fehler", "Bitte zuerst Kunden auswählen.")

        neue = {
            "id": self.next_anlage_id,
            "beschreibung": f"Anlage {self.next_anlage_id}",
            "name": "",
            "adresse": "",
            "plz_ort": "",
            "raum": "",
            "gebaeude": "",
            "geschoss": "",
            "funktion": "",
            "zaehlernummer": "",
            "zaehlerstand": "",
            "code": "",
            "bemerkung": "",
            "felder": self.settings.get("default_felder", 3),
            "reihen": self.settings.get("default_reihen", 7),
            "text_inhalt": "",
            "teile_text": "",
            "teile_parsed": [],
        }

        self.next_anlage_id += 1
        self.anlagen_daten.append(neue)
        self.speichere_daten()
        
        # Hauptansicht komplett neu aufbauen
        hauptansicht = self.ui_builder.erstelle_hauptansicht()
        self.show(hauptansicht)
        self.aktualisiere_anlagen_tabelle()

        self.dialog("Erfolg", f'Anlage "{neue["beschreibung"]}" hinzugefügt.')

    def anlage_loeschen(self, _e):
        print("LÖSCHEN-BUTTON GEKLICKT!")
        print(f"ausgewaehlte_anlage_id = {self.ausgewaehlte_anlage_id} (Typ: {type(self.ausgewaehlte_anlage_id)})")
        print(f"anlagen_daten IDs: {[(a['id'], type(a['id'])) for a in self.anlagen_daten]}")
        
        if not self.ausgewaehlte_anlage_id:
            return self.dialog("Fehler", "Bitte zuerst Anlage auswählen.")

        anlage = next((a for a in self.anlagen_daten if a["id"] == self.ausgewaehlte_anlage_id), None)
        print(f"Gefundene Anlage: {anlage}")
        
        if not anlage:
            return self.dialog("Fehler", "Anlage nicht gefunden.")

        def do_delete():
            geloeschte_id = self.ausgewaehlte_anlage_id
            self.anlagen_daten = [a for a in self.anlagen_daten if a["id"] != self.ausgewaehlte_anlage_id]
            # Zurückschreiben in alle_kunden
            self.alle_kunden[self.aktiver_kunde_key]["anlagen"] = self.anlagen_daten
            print(f"Anlage ID {geloeschte_id} gelöscht")
            self.ausgewaehlte_anlage_id = None
            self.speichere_daten()
            # Hauptansicht komplett neu aufbauen
            hauptansicht = self.ui_builder.erstelle_hauptansicht()
            self.show(hauptansicht)
            self.aktualisiere_anlagen_tabelle()

        self.confirm_dialog(
            "Anlage löschen",
            f'Wirklich Anlage "{anlage["beschreibung"]}" löschen?',
            do_delete
        )

    def bearbeite_ausgewaehlte_anlage(self, _e):
        if not self.ausgewaehlte_anlage_id:
            return self.dialog("Fehler", "Bitte zuerst Anlage auswählen.")

        self.aktuelle_anlage = next(
            (a for a in self.anlagen_daten if a["id"] == self.ausgewaehlte_anlage_id), None
        )

        if not self.aktuelle_anlage:
            return self.dialog("Fehler", "Anlage nicht gefunden.")

        self.navigiere_zu_detail_view()

    # ---------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------

    def navigiere_zu_detail_view(self):
        view = self.ui_builder.erstelle_anlage_detail_view()

        mapping = {
            "beschr_input": "beschreibung",
            "name_input": "name",
            "adresse_input": "adresse",
            "plz_ort_input": "plz_ort",
            "raum_input": "raum",
            "gebaeude_input": "gebaeude",
            "geschoss_input": "geschoss",
            "funktion_input": "funktion",
            "zaehlernummer_input": "zaehlernummer",
            "zaehlerstand_input": "zaehlerstand",
            "code_input": "code",
            "bemerkung_input": "bemerkung",
        }

        self.map_set(mapping, self.aktuelle_anlage)

        self.ui["felder_input"].value = str(self.aktuelle_anlage.get("felder", 3))
        self.ui["reihen_input"].value = str(self.aktuelle_anlage.get("reihen", 7))
        self.ui["text_editor"].value = self.aktuelle_anlage.get("text_inhalt", "")

        self.info_aktualisieren()

        self.show(view)

    def navigiere_zu_settings(self, _e):
        view = self.ui_builder.erstelle_settings_dialog()
        self.show(view)

    def zurueck_zur_hauptansicht(self, _e):
        self.speichere_detail_daten()
        self.speichere_daten()
        haupt = self.ui_builder.erstelle_hauptansicht()
        self.show(haupt)
        self.aktualisiere_anlagen_tabelle()

    # ---------------------------------------------------------
    # Detail-Daten
    # ---------------------------------------------------------

    def speichere_detail_daten(self):
        if not self.aktuelle_anlage:
            return

        mapping = {
            "beschr_input": "beschreibung",
            "name_input": "name",
            "adresse_input": "adresse",
            "plz_ort_input": "plz_ort",
            "raum_input": "raum",
            "gebaeude_input": "gebaeude",
            "geschoss_input": "geschoss",
            "funktion_input": "funktion",
            "zaehlernummer_input": "zaehlernummer",
            "zaehlerstand_input": "zaehlerstand",
            "code_input": "code",
            "bemerkung_input": "bemerkung",
        }

        self.map_get(mapping, self.aktuelle_anlage)

        try:
            self.aktuelle_anlage["felder"] = int(self.ui["felder_input"].value)
        except:
            self.aktuelle_anlage["felder"] = 3

        try:
            self.aktuelle_anlage["reihen"] = int(self.ui["reihen_input"].value)
        except:
            self.aktuelle_anlage["reihen"] = 7

        self.aktuelle_anlage["text_inhalt"] = self.ui["text_editor"].value

    def auto_speichere_detail_daten(self, _e):
        self.speichere_detail_daten()
        self.speichere_daten()

        # ---------------------------------------------------------
        # Code-Generierung
        # ---------------------------------------------------------

    def generiere_code_string(self):
        fun = self.ui["funktion_input"].value.strip()
        geb = self.ui["gebaeude_input"].value.strip()
        etage = self.ui["geschoss_input"].value.strip()
        raum = self.ui["raum_input"].value.strip()

        teile = []
        if fun:
            teile.append(f"={fun}")
        if geb:
            teile.append(f"++{geb}")
            if etage:
                teile.append(f"-{etage}")
        else:
            if etage:
                teile.append(f"++{etage}")
        if raum:
            teile.append(f"+{raum}")

        return "".join(teile).upper() if teile else ""

    def aktualisiere_anlagen_code(self, _e=None):
        neuer = self.generiere_code_string()
        alt = self.aktuelle_anlage.get("code_auto_last", "")

        if not self.ui["code_input"].value or self.ui["code_input"].value == alt:
            self.ui["code_input"].value = neuer
            self.aktuelle_anlage["code_auto_last"] = neuer
            self.page.update()

        self.speichere_detail_daten()

    def aktualisiere_anlagen_code_und_speichere(self, e):
        self.aktualisiere_anlagen_code(e)
        self.speichere_daten()

        # ---------------------------------------------------------
        # Info-Aktualisierung
        # ---------------------------------------------------------

    def info_aktualisieren(self, _e=None):
        if not self.aktuelle_anlage:
            return False, []

        self.speichere_detail_daten()

        felder = self.aktuelle_anlage["felder"]
        reihen = self.aktuelle_anlage["reihen"]
        text = self.aktuelle_anlage["text_inhalt"]

        is_valid, gueltige, fehler_anzahl, belegte, max_spalten = validiere_eintraege(
            text, felder, reihen
        )

        self.ui["info_label"].value = (
            f"Gesamt-Spalten: {felder} × {reihen} × {SPALTEN_PRO_EINHEIT} = {max_spalten}"
        )

        if fehler_anzahl > 0:
            self.ui["verfuegbar_label"].value = f"❌ {fehler_anzahl} Fehler!"
            self.ui["verfuegbar_label"].color = ft.Colors.RED_700
        else:
            verfuegbar = max_spalten - len(belegte)
            self.ui["verfuegbar_label"].value = f"✓ Verfügbar: {verfuegbar} von {max_spalten}"
            self.ui["verfuegbar_label"].color = (
                ft.Colors.GREEN_700 if verfuegbar == max_spalten else ft.Colors.ORANGE_700
            )

        self.page.update()
        return is_valid, gueltige

    def info_aktualisieren_und_speichern(self, e=None):
        self.info_aktualisieren(e)
        self.speichere_detail_daten()
        self.speichere_daten()

        # ---------------------------------------------------------
        # Export
        # ---------------------------------------------------------

    def exportiere_anlage(self, _e):
        if not self.aktuelle_anlage:
            return self.dialog("Fehler", "Keine Anlage ausgewählt.")

        try:
            pfad = exportiere_anlage_ods(self.aktuelle_anlage, self.settings, self.data_path)
            self.letzte_export_datei = pfad
            self.ui["teile_button"].disabled = False
            self.page.update()
            self.show_file_snackbar("Exportiert", pfad.name)
            self.dialog("Erfolg", f"ODS exportiert: {pfad.name}")

        except ValueError as e:
            self.dialog("Validierungs-Fehler", str(e))
        except Exception as e:
            self.dialog("Export-Fehler", f"Fehler beim Export:\n{str(e)}")

    def teile_letzte_ods(self, _e):
        if not self.letzte_export_datei or not self.letzte_export_datei.exists():
            return self.dialog("Fehler", "Keine Datei gefunden.")
        self.dialog("Info", f"Datei: {self.letzte_export_datei}")

    def exportiere_kunde_odt(self, _e):
        self.dialog("Info", "Kunden-ODT-Export noch nicht implementiert.")

        # ---------------------------------------------------------
        # Settings
        # ---------------------------------------------------------

    def auto_speichere_settings(self, _e):
        try:
            self.settings["default_felder"] = int(self.ui["settings_felder_input"].value)
            self.settings["default_reihen"] = int(self.ui["settings_reihen_input"].value)
            self.settings["fontsize_gemergte_zelle"] = int(self.ui["settings_font_gemergt_input"].value)
            self.settings["fontsize_beschriftung_zelle"] = int(self.ui["settings_font_beschr_input"].value)
            self.settings["fontsize_inhalt_zelle"] = int(self.ui["settings_font_inhalt_input"].value)
            self.settings["spalten_breite"] = float(self.ui["settings_spalten_breite_input"].value)
            self.settings["beschriftung_row_hoehe"] = float(self.ui["settings_beschr_hoehe_input"].value)
            self.settings["inhalt_row_hoehe"] = float(self.ui["settings_inhalt_hoehe_input"].value)
            self.settings["zellen_umrandung"] = self.ui["settings_umrandung_switch"].value
            self.settings["rand_oben"] = float(self.ui["settings_rand_oben_input"].value)
            self.settings["rand_unten"] = float(self.ui["settings_rand_unten_input"].value)
            self.settings["rand_links"] = float(self.ui["settings_rand_links_input"].value)
            self.settings["rand_rechts"] = float(self.ui["settings_rand_rechts_input"].value)

            self.data_manager.speichere_settings(self.settings)
        except:
            pass

        # ---------------------------------------------------------
        # Export/Import
        # ---------------------------------------------------------

    def exportiere_zu_downloads(self, _e):
        ok, dateien, fehler = export_downloads(self.data_manager)
        if ok:
            for datei in dateien:
                self.show_file_snackbar("Exportiert", datei)
            self.dialog("Export erfolgreich", "\n".join(dateien))
        else:
            self.dialog("Export-Fehler", fehler)

    def importiere_von_downloads(self, _e):
        ok, dateien, fehler = import_downloads(self.data_manager)
        if ok:
            for datei in dateien:
                self.show_file_snackbar("Importiert", datei)
            self.settings = self.data_manager.lade_settings()
            self.lade_daten()
            self.aktualisiere_aktive_daten()
            self.dialog("Import erfolgreich", "\n".join(dateien))
        else:
            if "Keine" in fehler:
                self.dialog("Keine Dateien", fehler)
            else:
                self.dialog("Import-Fehler", fehler)


def main(page: ft.Page):
    AnlagenApp(page)


if __name__ == "__main__":
    ft.app(target=main)
