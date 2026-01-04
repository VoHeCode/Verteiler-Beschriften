#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Anlagen Eingabe App – vereinfachte Registry-Version."""

import flet as ft
from datetime import datetime
from pathlib import Path

from constants import APP_VERSION, APP_NAME, SPALTEN_PRO_EINHEIT
from data_manager import DataManager
from ui_builder import UIBuilder
from odf_exporter import validiere_eintraege, exportiere_anlage_ods, exportiere_kunde_odt


class AnlagenApp:
    """Hauptanwendung – alle UI-Controls liegen in self.ui[...]"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = f"{APP_NAME} V{APP_VERSION}"
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.theme_mode = ft.ThemeMode.LIGHT  # Fix für Android Dark Mode

        # Registry für ALLE UI-Elemente
        self.ui = {}

        # Datenpfad - User-zugänglich auf ALLEN Plattformen
        import os
        storage = os.getenv("FLET_APP_STORAGE_DATA")
        if storage:
            # Mobile (Android/iOS) - User-zugänglich unter Documents
            self.data_path = Path("/storage/emulated/0/Documents/Verteiler_Beschriften")
        else:
            # Desktop - Sichtbarer Ordner in Dokumente
            docs_de = Path.home() / "Dokumente" / "Verteiler_Beschriften"
            docs_en = Path.home() / "Documents" / "Verteiler_Beschriften"
            if docs_de.parent.exists():
                self.data_path = docs_de
            else:
                self.data_path = docs_en
        
        # Erstelle Basis-Ordnerstruktur beim Start
        self.data_path.mkdir(parents=True, exist_ok=True)
        (self.data_path / "Export").mkdir(parents=True, exist_ok=True)
        (self.data_path / "Import").mkdir(parents=True, exist_ok=True)

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

        # Dirty Flags für Speicheroptimierung
        self.daten_dirty = False
        self.settings_dirty = False
        self.original_kunde_values = {}

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
        """Zeigt Snackbar für Datei-Operationen (4 Sek)."""
        snackbar = ft.SnackBar(
            content=ft.Text(f"{action}: {filename}"),
            duration=4000,
        )
        self.page.show_dialog(snackbar)

    def update_status(self, text=""):
        """Aktualisiert den Statustext in der Titelzeile."""
        if "status_text" in self.ui:
            self.ui["status_text"].value = text
            self.page.update()

    def get_export_path(self):
        """Gibt Export-Pfad MIT Kundenname zurück - IMMER user-zugänglich."""
        kundenname = self.aktiver_kunde_key or "Allgemein"
        base = self.get_export_base_path()
        export_path = base / kundenname
        export_path.mkdir(parents=True, exist_ok=True)
        return export_path

    def get_export_base_path(self):
        """Gibt Basis-Export-Pfad zurück (ohne Kundenname) - IMMER user-zugänglich.
        
        Returns:
            Path: Export-Basis-Pfad
        """
        export_path = self.data_path / "Export"
        export_path.mkdir(parents=True, exist_ok=True)
        return export_path

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

    def pruefe_import_ordner(self):
        """Prüft Import-Ordner auf JSON-Dateien und importiert diese."""
        import_path = self.data_path / "Import"
        
        if not import_path.exists():
            return
        
        # Suche JSON-Dateien
        json_files = list(import_path.glob("*.json"))
        if not json_files:
            return
        
        # Importiere erste gefundene Datei
        import_file = json_files[0]
        try:
            import shutil
            # Kopiere nach Datenpfad
            target = self.data_path / "anlagen_daten.json"
            shutil.copy(import_file, target)
            
            # Lösche aus Import-Ordner
            import_file.unlink()
            
            self.show_file_snackbar("Import erfolgreich", import_file.name)
            self.dialog("Import erfolgreich", 
                       f"Daten importiert aus:\n{import_file.name}")
        except Exception as e:
            self.dialog("Import-Fehler", str(e))

    def init_app(self):
        self.pruefe_import_ordner()
        self.lade_daten()
        haupt = self.ui_builder.erstelle_hauptansicht()
        self.page.add(haupt)
        self.page.update()
        self.aktualisiere_aktive_daten()
        
        # Statusleiste: Zeige Datenpfad (user-zugänglich auf allen Plattformen)
        self.update_status(f"Daten: {self.data_path}")

    # ---------------------------------------------------------
    # Daten
    # ---------------------------------------------------------

    def lade_daten(self):
        self.alle_kunden, self.next_kunden_id, self.next_anlage_id = self.data_manager.lade_daten()
        if self.alle_kunden:
            self.aktiver_kunde_key = next(iter(self.alle_kunden))
        self.show_file_snackbar("Geladen", "anlagen_daten.json")

    def speichere_daten(self, _e=None):
        # Nur speichern wenn Änderungen vorhanden
        if not self.daten_dirty:
            return
        
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
            self.daten_dirty = False  # Flag zurücksetzen nach erfolgreichem Speichern
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
        
        # Markiere als geändert und speichere
        self.daten_dirty = True
        self.speichere_daten()

    def on_kunde_feld_blur(self, e):
        """Prüft bei Feldverlassen ob Wert geändert wurde."""
        if not self.aktiver_kunde_key:
            return
        
        # Finde UI-Key des Feldes
        field_key = None
        for key, field in self.ui.items():
            if field == e.control:
                field_key = key
                break
        
        if not field_key or field_key not in self.original_kunde_values:
            return
        
        # Vergleiche mit Original
        current_value = e.control.value or ""
        original_value = self.original_kunde_values[field_key]
        
        if current_value != original_value:
            # Wert hat sich geändert - schreibe direkt in RAM
            kunde = self.alle_kunden[self.aktiver_kunde_key]
            
            # Mapping UI-Key → Daten-Key
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
            
            data_key = mapping.get(field_key)
            if data_key:
                kunde[data_key] = current_value
            
            # Aktualisiere Original-Wert
            self.original_kunde_values[field_key] = current_value
            
            # Markiere als geändert und speichere
            self.daten_dirty = True
            self.speichere_daten()

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
        
        # Aktualisiere kunde_input mit aktivem Kundennamen
        if "kunde_input" in self.ui:
            self.ui["kunde_input"].value = self.aktiver_kunde_key
        
        # Original-Werte für Vergleich speichern
        self.original_kunde_values = {
            key: kunde.get(data_key, "") for key, data_key in mapping.items()
        }

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

        # Auto-Select wenn nur 1 Anlage
        if len(self.anlagen_daten) == 1:
            anlage = self.anlagen_daten[0]
            self.ausgewaehlte_anlage_id = anlage["id"]
            self.aktuelle_anlage = anlage
            self.ui["anlagen_radiogroup"].value = str(anlage["id"])

        self.page.update()

    def on_anlage_selected(self, e):
        """Callback wenn Anlage in RadioGroup ausgewählt wird."""
        if e.control.value:
            self.ausgewaehlte_anlage_id = int(e.control.value)
            
            # Setze auch aktuelle_anlage für Export
            for anlage in self.anlagen_daten:
                if anlage['id'] == self.ausgewaehlte_anlage_id:
                    self.aktuelle_anlage = anlage
                    break

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
        
        self.daten_dirty = True
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

        self.daten_dirty = True
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
                self.daten_dirty = True
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
        
        # Neue Anlage automatisch auswählen
        self.ausgewaehlte_anlage_id = neue["id"]
        self.aktuelle_anlage = neue
        
        self.daten_dirty = True
        self.speichere_daten()
        
        # Hauptansicht komplett neu aufbauen
        hauptansicht = self.ui_builder.erstelle_hauptansicht()
        self.show(hauptansicht)
        self.aktualisiere_anlagen_tabelle()

        self.dialog("Erfolg", f'Anlage "{neue["beschreibung"]}" hinzugefügt.')

    def anlage_loeschen(self, _e):
        if not self.ausgewaehlte_anlage_id:
            return self.dialog("Fehler", "Bitte zuerst Anlage auswählen.")

        anlage = next((a for a in self.anlagen_daten if a["id"] == self.ausgewaehlte_anlage_id), None)
        
        if not anlage:
            return self.dialog("Fehler", "Anlage nicht gefunden.")

        def do_delete():
            self.anlagen_daten = [a for a in self.anlagen_daten if a["id"] != self.ausgewaehlte_anlage_id]
            # Zurückschreiben in alle_kunden
            self.alle_kunden[self.aktiver_kunde_key]["anlagen"] = self.anlagen_daten
            self.ausgewaehlte_anlage_id = None
            self.daten_dirty = True
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
        self.daten_dirty = True
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
        self.daten_dirty = True
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
        self.daten_dirty = True
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
        self.daten_dirty = True
        self.speichere_daten()

        # ---------------------------------------------------------
        # Export
        # ---------------------------------------------------------

    def exportiere_anlage(self, _e):
        if not self.aktuelle_anlage:
            return self.dialog("Fehler", "Keine Anlage ausgewählt.")

        try:
            # Hole Projekt vom aktiven Kunden
            projekt = ''
            if self.aktiver_kunde_key and self.aktiver_kunde_key in self.alle_kunden:
                projekt = self.alle_kunden[self.aktiver_kunde_key].get('projekt', '')
            
            pfad = exportiere_anlage_ods(
                self.aktuelle_anlage, 
                self.settings, 
                self.get_export_base_path(),  # OHNE Kundenname - wird in odf_exporter hinzugefügt
                self.aktiver_kunde_key,
                projekt
            )
            self.letzte_export_datei = pfad
            self.show_file_snackbar("Exportiert", str(pfad))
            self.dialog("Erfolg", f"ODS exportiert:\n\n{pfad}")

        except ValueError as e:
            self.dialog("Validierungs-Fehler", str(e))
        except Exception as e:
            self.dialog("Export-Fehler", f"Fehler beim Export:\n{str(e)}")

    def teile_letzte_ods(self, _e):
        if not self.letzte_export_datei or not self.letzte_export_datei.exists():
            return self.dialog("Fehler", "Keine Datei gefunden.")
        self.dialog("Info", f"Datei: {self.letzte_export_datei}")

    def exportiere_kunde_odt(self, _e):
        """Exportiert alle Daten des aktiven Kunden als ODT."""
        if not self.aktiver_kunde_key or self.aktiver_kunde_key not in self.alle_kunden:
            return self.dialog('Fehler', 'Kein Kunde ausgewählt.')

        self.speichere_projekt_daten()

        kunde = self.alle_kunden[self.aktiver_kunde_key]

        try:
            pfad = exportiere_kunde_odt(
                kunde, 
                self.aktiver_kunde_key, 
                self.get_export_base_path()  # OHNE Kundenname - wird in odf_exporter hinzugefügt
            )
            self.show_file_snackbar("Exportiert", str(pfad))
            self.dialog('Erfolg', f'ODT exportiert:\n\n{pfad}')

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.dialog('Export-Fehler', f'Fehler beim ODT-Export:\n{str(e)}\n\n{error_details[:300]}')

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
        """Exportiert Daten und Settings als JSON zu Documents/Export."""
        try:
            import shutil
            from datetime import datetime
            
            export_base = self.get_export_base_path()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            dateien = []
            
            # Exportiere Anlagen-Daten
            source_daten = self.data_path / "anlagen_daten.json"
            if source_daten.exists():
                target_daten = export_base / f"Verteiler_Daten_{timestamp}.json"
                shutil.copy(source_daten, target_daten)
                dateien.append(target_daten.name)
                self.show_file_snackbar("Exportiert", target_daten.name)
            
            # Exportiere Settings
            source_settings = self.data_path / "app_settings.json"
            if source_settings.exists():
                target_settings = export_base / f"Verteiler_Einstellungen_{timestamp}.json"
                shutil.copy(source_settings, target_settings)
                dateien.append(target_settings.name)
                self.show_file_snackbar("Exportiert", target_settings.name)
            
            if dateien:
                self.dialog("Export erfolgreich", 
                           f"Dateien exportiert nach:\n{export_base}\n\n" + "\n".join(dateien))
            else:
                self.dialog("Fehler", "Keine Daten zum Exportieren vorhanden.")
        
        except Exception as e:
            self.dialog("Export-Fehler", str(e))

    def exportiere_alle_kunden(self, _e):
        """Exportiert alle Kunden als einzelne ODT-Dateien."""
        if not self.alle_kunden:
            return self.dialog("Fehler", "Keine Kunden vorhanden.")
        
        try:
            anzahl = 0
            for kundenname, kunde in self.alle_kunden.items():
                pfad = exportiere_kunde_odt(
                    kunde, 
                    kundenname, 
                    self.get_export_base_path()
                )
                anzahl += 1
            
            self.show_file_snackbar("Exportiert", f"{anzahl} Kunden als ODT")
            self.dialog('Erfolg', f'{anzahl} Kunden als ODT exportiert:\n\n{self.get_export_base_path() / "Export"}')
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.dialog('Export-Fehler', f'Fehler beim Export:\n{str(e)}\n\n{error_details[:300]}')
    
    def exportiere_alle_daten_json(self, _e):
        """Exportiert alle Kundendaten als JSON in Export-Ordner."""
        try:
            import shutil
            from datetime import datetime
            
            # Quelle: aktuelle Datendatei
            source = self.data_path / "anlagen_daten.json"
            if not source.exists():
                return self.dialog("Fehler", "Keine Daten zum Exportieren vorhanden.")
            
            # Ziel: Export-Ordner (OHNE Kundenname)
            export_base = self.get_export_base_path()
            
            # Dateiname mit Timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            target = export_base / f"anlagen_daten_{timestamp}.json"
            
            # Kopiere Datei
            shutil.copy(source, target)
            
            self.show_file_snackbar("Exportiert", str(target))
            self.dialog("Export erfolgreich", 
                       f"Alle Kundendaten exportiert:\n\n{target}")
        
        except Exception as e:
            self.dialog("Export-Fehler", str(e))

    def zeige_logs(self, _e):
        """Zeigt Flet Console Logs für Debugging."""
        import os
        log_file = os.getenv("FLET_APP_CONSOLE")
        if log_file:
            try:
                with open(log_file, "r") as f:
                    logs = f.read()
                # Zeige letzte 5000 Zeichen
                if len(logs) > 5000:
                    logs = "...\n" + logs[-5000:]
                self.dialog("Debug Logs", logs)
            except Exception as e:
                self.dialog("Log-Fehler", f"Konnte Logs nicht lesen: {e}")
        else:
            self.dialog("Keine Logs", "FLET_APP_CONSOLE nicht verfügbar")

    def importiere_von_downloads(self, _e):
        """Importiert Daten und Settings aus Documents/Import."""
        try:
            import shutil
            
            import_path = self.data_path / "Import"
            
            if not import_path.exists():
                return self.dialog("Keine Dateien", 
                                  f"Import-Ordner nicht gefunden:\n{import_path}")
            
            # Suche JSON-Dateien
            json_files = list(import_path.glob("*.json"))
            if not json_files:
                return self.dialog("Keine Dateien", 
                                  f"Keine JSON-Dateien im Import-Ordner:\n{import_path}")
            
            dateien = []
            
            # Importiere Dateien
            for json_file in json_files:
                filename = json_file.name.lower()
                
                if "daten" in filename or "anlagen" in filename:
                    # Anlagen-Daten
                    target = self.data_path / "anlagen_daten.json"
                    shutil.copy(json_file, target)
                    dateien.append(json_file.name)
                    self.show_file_snackbar("Importiert", json_file.name)
                    
                elif "einstellung" in filename or "settings" in filename:
                    # Settings
                    target = self.data_path / "app_settings.json"
                    shutil.copy(json_file, target)
                    dateien.append(json_file.name)
                    self.show_file_snackbar("Importiert", json_file.name)
                
                # Lösche importierte Datei aus Import-Ordner
                json_file.unlink()
            
            if dateien:
                # Lade neue Daten
                self.settings = self.data_manager.lade_settings()
                self.lade_daten()
                self.aktualisiere_aktive_daten()
                self.dialog("Import erfolgreich", 
                           f"Importierte Dateien:\n" + "\n".join(dateien))
            else:
                self.dialog("Keine Dateien", "Keine passenden JSON-Dateien gefunden.")
        
        except Exception as e:
            self.dialog("Import-Fehler", str(e))


def main(page: ft.Page):
    AnlagenApp(page)


if __name__ == "__main__":
    ft.app(target=main)
