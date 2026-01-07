#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Anlagen Eingabe App – Registry-Version mit Dataclasses & Optimierungen."""

import os
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from date_utils import parse_date_input, format_date_display
import flet as ft

from constants import TOOL_FLET_VERSION, TOOL_FLET_NAME, COLUMNS_PER_UNIT
from data_manager import DataManager
from ui_builder import UIBuilder
from odf_exporter import (
    validiere_eintraege,
    exportiere_anlage_ods,
    exportiere_kunde_odt,
)

# ---------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------

@dataclass
class Anlage:
    id: int
    beschreibung: str = ""
    name: str = ""
    adresse: str = ""
    plz_ort: str = ""
    raum: str = ""
    gebaeude: str = ""
    geschoss: str = ""
    funktion: str = ""
    zaehlernummer: str = ""
    zaehlerstand: str = ""
    code: str = ""
    bemerkung: str = ""
    felder: int = 3
    reihen: int = 7
    text_inhalt: str = ""
    teile_text: str = ""
    teile_parsed: list = field(default_factory=list)
    code_auto_last: str = ""

@dataclass
class Kunde:
    id: int
    projekt: str = ""
    datum: str = ""
    adresse: str = ""
    plz: str = ""
    ort: str = ""
    ansprechpartner: str = ""
    telefonnummer: str = ""
    email: str = ""
    anlagen: list[Anlage] = field(default_factory=list)
    next_anlage_id: int = 1  # Pro Kunde

# ---------------------------------------------------------
# Dict-Konvertierung
# ---------------------------------------------------------

def anlage_to_dict(a: Anlage) -> dict:
    return asdict(a)

def anlage_from_dict(d: dict) -> Anlage:
    return Anlage(**d)

def kunde_to_dict(k: Kunde) -> dict:
    d = asdict(k)
    d["anlagen"] = [anlage_to_dict(a) for a in k.anlagen]
    return d

def kunde_from_dict(d: dict) -> Kunde:
    anlagen = [anlage_from_dict(a) for a in d.get("anlagen", [])]
    d = {k: v for k, v in d.items() if k != "anlagen"}
    return Kunde(**d, anlagen=anlagen)

# ---------------------------------------------------------
# Hauptklasse
# ---------------------------------------------------------

class AnlagenApp:
    """Hauptanwendung – alle UI-Controls liegen in self.ui[...]"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = f"{TOOL_FLET_NAME} V{TOOL_FLET_VERSION}"
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.theme_mode = ft.ThemeMode.LIGHT
        
        # Ermittle is_mobile direkt aus page.platform
        self.is_mobile = self.page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]
        
        # Mobile: Padding für System-Overlays
        if self.is_mobile:
            self.page.padding = ft.padding.only(top=25, bottom=25)

        self.ui = {}

        # Mappings
        self.kunden_mapping = {
            "kunde_projekt": "projekt",
            "kunde_datum": "datum",
            "kunde_adresse": "adresse",
            "kunde_plz": "plz",
            "kunde_ort": "ort",
            "kunde_ansprechpartner": "ansprechpartner",
            "kunde_telefonnummer": "telefonnummer",
            "kunde_email": "email",
        }

        self.detail_mapping = {
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

        # Datenpfad
        if self.is_mobile:
            self.data_path = Path("/storage/emulated/0/Documents/Verteiler_Beschriften")
        else:
            docs_de = Path.home() / "Dokumente" / "Verteiler_Beschriften"
            docs_en = Path.home() / "Documents" / "Verteiler_Beschriften"
            self.data_path = docs_de if docs_de.parent.exists() else docs_en

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
        self.aktuelle_anlage = None
        self.ausgewaehlte_anlage_id = None
        self.letzte_export_datei = None

        self.daten_dirty = False
        self.settings_dirty = False
        self.original_kunde_values = {}

        self.ui_builder = UIBuilder(self, page)

        self.init_app()

    # ---------------------------------------------------------
    # Hilfsfunktionen
    # ---------------------------------------------------------

    def show(self, view):
        self.page.controls[:] = [view]
        self.page.update()

    def dialog(self, title, msg):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(msg),
            actions=[ft.TextButton("OK", on_click=lambda e: self.page.pop_dialog())],
        )
        self.page.show_dialog(dlg)

    def show_file_snackbar(self, action, filename):
        """Zeigt Snackbar für Dateioperationen."""
        # Vollständiger Pfad für Datendateien
        if filename == "anlagen_daten.json" or filename == "app_settings.json":
            filepath = str(self.data_path / filename)
        else:
            filepath = filename
            
        snackbar = ft.SnackBar(
            content=ft.Text(f"{action}: {filepath}"),
            duration=4000  # 4 Sekunden
        )
        self.page.overlay.append(snackbar)
        snackbar.open = True
        self.page.update()

    def update_status(self, text=""):
        if "status_text" in self.ui:
            self.ui["status_text"].value = text
            self.page.update()

    def _timestamp(self):
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _copy_file(self, src: Path, dst: Path, label: str):
        try:
            import shutil
            shutil.copy(src, dst)
            self.show_file_snackbar("Exportiert", dst.name)
            return True
        except Exception as e:
            self.show_snackbar(f"{label}-Fehler: {e}")
            return False

    def map_set_obj(self, mapping, obj):
        for ui_key, attr in mapping.items():
            if ui_key in self.ui:
                self.ui[ui_key].value = getattr(obj, attr, "")

    def map_get_obj(self, mapping, obj):
        for ui_key, attr in mapping.items():
            if ui_key in self.ui:
                setattr(obj, attr, self.ui[ui_key].value or "")

    # ---------------------------------------------------------
    # Initialisierung
    # ---------------------------------------------------------

    
    def init_app(self):
        self.lade_daten()
        haupt = self.ui_builder.erstelle_hauptansicht()
        self.page.add(haupt)
        self.page.update()
        self.aktualisiere_aktive_daten()
        self.update_status(f"Daten: {self.data_path}")

    def confirm_dialog(self, title: str, message: str, on_yes_callback):
        """Zeigt modalen Bestätigungsdialog mit Ja/Nein Buttons."""

        def handle_yes(_event):
            self.page.pop_dialog()
            on_yes_callback()

        def handle_no(_event):
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

    def get_export_base_path(self) -> Path:
        """
        Liefert den Export-Ordner:
        <Datenpfad>/Export
        """
        export_path = self.data_path / "Export"
        export_path.mkdir(parents=True, exist_ok=True)
        return export_path

    # ---------------------------------------------------------
    # Daten
    # ---------------------------------------------------------

    def lade_daten(self):
        """Lädt Daten über DataManager und konvertiert zu Dataclasses."""
        alle_kunden_raw, self.next_kunden_id = self.data_manager.lade_daten()
        self.alle_kunden = {
            name: kunde_from_dict(kdict) for name, kdict in alle_kunden_raw.items()
        }
        if self.alle_kunden:
            self.aktiver_kunde_key = next(iter(self.alle_kunden))
        self.show_file_snackbar("Geladen", "anlagen_daten.json")

    def speichere_daten(self, _e=None):
        """Schreibt Dataclasses zurück in Dict-Struktur und speichert."""
        if not self.daten_dirty:
            return

        if self.aktiver_kunde_key in self.alle_kunden:
            self.alle_kunden[self.aktiver_kunde_key].anlagen = list(self.anlagen_daten)

        out = {key: kunde_to_dict(kunde) for key, kunde in self.alle_kunden.items()}

        ok, fehler = self.data_manager.speichere_daten(
            out, self.next_kunden_id
        )
        if not ok:
            self.show_snackbar(f"Speicher-Fehler: {fehler}")
        else:
            self.daten_dirty = False
            self.show_file_snackbar("Gespeichert", "anlagen_daten.json")

    def speichere_projekt_daten(self, _e=None):
        if not self.aktiver_kunde_key:
            return
        kunde = self.alle_kunden[self.aktiver_kunde_key]
        self.map_get_obj(self.kunden_mapping, kunde)
        self.daten_dirty = True
        self.speichere_daten()

    def on_kunde_feld_blur(self, e):
        """Prüft bei Feldverlassen, ob Wert geändert wurde."""
        if not self.aktiver_kunde_key:
            return

        field_key = next((k for k, ctrl in self.ui.items() if ctrl == e.control), None)
        if not field_key or field_key not in self.original_kunde_values:
            return

        current = e.control.value or ""

        # ⭐ Datumsfeld → immer ISO speichern, dann User-Format anzeigen
        if field_key == "kunde_datum":
            iso_datum = parse_date_input(current)
            current = iso_datum
            # Zeige wieder im User-Format
            fmt = self.settings.get("datum_format", "DE")
            e.control.value = format_date_display(iso_datum, fmt)

        original = self.original_kunde_values[field_key]

        if current != original:
            kunde = self.alle_kunden[self.aktiver_kunde_key]
            attr = self.kunden_mapping.get(field_key)
            if attr:
                setattr(kunde, attr, current)
            self.original_kunde_values[field_key] = current
            self.daten_dirty = True
            self.speichere_daten()
            self.show_file_snackbar("Gespeichert", "anlagen_daten.json")

    def aktualisiere_aktive_daten(self):
        if not self.aktiver_kunde_key:
            return

        kunde = self.alle_kunden[self.aktiver_kunde_key]
        self.map_set_obj(self.kunden_mapping, kunde)

        # ⭐ Datumsfeld nachträglich im User-Format anzeigen
        iso = getattr(kunde, "datum", "")  # oder kunde.kunde_datum
        fmt = self.settings.get("datum_format", "DE")
        if "kunde_datum" in self.ui:
            self.ui["kunde_datum"].value = format_date_display(iso, fmt)

        if "kunde_input" in self.ui:
            self.ui["kunde_input"].value = self.aktiver_kunde_key

        self.original_kunde_values = {
            key: getattr(kunde, attr, "") for key, attr in self.kunden_mapping.items()
        }

        self.anlagen_daten = list(kunde.anlagen)
        self.aktualisiere_anlagen_tabelle()
        self.page.update()

    # ---------------------------------------------------------
    # Navigation (optimiert)
    # ---------------------------------------------------------

    def navigate(self, view_name: str):
        """Zentrale Navigation: baut Views konsistent auf."""
        if view_name == "main":
            view = self.ui_builder.erstelle_hauptansicht()
            self.show(view)
            self.aktualisiere_aktive_daten()  # Kundendaten laden!
            return

        if view_name == "detail":
            view = self.ui_builder.erstelle_anlage_detail_view()
            self.map_set_obj(self.detail_mapping, self.aktuelle_anlage)
            self.ui["felder_input"].value = str(self.aktuelle_anlage.felder)
            self.ui["reihen_input"].value = str(self.aktuelle_anlage.reihen)
            self.ui["text_editor"].value = self.aktuelle_anlage.text_inhalt
            self.info_aktualisieren()
            self.show(view)
            return

        if view_name == "settings":
            view = self.ui_builder.erstelle_settings_dialog()
            self.show(view)

    def refresh_main(self):
        self.navigate("main")

    def navigiere_zu_detail_view(self):
        self.navigate("detail")

    def navigiere_zu_settings(self, _e):
        self.navigate("settings")

    def zeige_about_dialog(self, _e):
        """Zeigt About-Dialog mit App-Informationen."""
        about_text = (
            "Version 2.7.0\n\n"
            "Autor: Volker Heggemann\n"
            "vohegg@gmail.com\n\n"
            "Copyright © 2026 Volker Heggemann\n"
            "Alle Rechte vorbehalten\n\n"
            "Optimiert für Hager UZ005\n"
            "Beschriftungshalterungen"
        )
        self.dialog("Verteiler Beschriften", about_text)
    
    def zurueck_von_settings(self, _e):
        """Zurück von Settings zur Hauptansicht (ohne Detail-Daten zu speichern)."""
        self.refresh_main()
    
    def zurueck_zur_hauptansicht(self, _e):
        self.speichere_detail_daten()
        self.daten_dirty = True
        self.speichere_daten()
        self.navigate("main")

    # ---------------------------------------------------------
    # Kunden
    # ---------------------------------------------------------

    def wechsel_kunden_auswahl(self, e):
        key = e.control.value
        if key in self.alle_kunden:
            self.aktiver_kunde_key = key
            self.aktualisiere_aktive_daten()
            self.page.update()

    def _navigiere_kunde_links(self, _e):
        if not self.alle_kunden or not self.aktiver_kunde_key:
            return
        keys = list(self.alle_kunden)
        idx = keys.index(self.aktiver_kunde_key)
        self.aktiver_kunde_key = keys[(idx - 1) % len(keys)]
        self.ui["kunden_auswahl"].value = self.aktiver_kunde_key
        self.aktualisiere_aktive_daten()

    def _navigiere_kunde_rechts(self, _e):
        if not self.alle_kunden or not self.aktiver_kunde_key:
            return
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

        kunde = Kunde(
            id=self.next_kunden_id,
            projekt="",
            datum=datetime.now().date().strftime("%Y-%m-%d"),
            adresse="",
            plz="",
            ort="",
            ansprechpartner="",
            telefonnummer="",
            email="",
            anlagen=[],
        )

        self.alle_kunden[name] = kunde
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
            return
        
        del self.alle_kunden[self.aktiver_kunde_key]
        self.aktiver_kunde_key = next(iter(self.alle_kunden), None)
        
        self.daten_dirty = True
        self.speichere_daten()
        
        # Komplette UI neu aufbauen
        self.refresh_main()
        
        # Falls noch Kunden da sind, deren Daten laden
        if self.aktiver_kunde_key:
            self.aktualisiere_aktive_daten()

    # ---------------------------------------------------------
    # Anlagen (Teil 1)
    # ---------------------------------------------------------

    def anlage_hinzufuegen(self, _e):
        if not self.aktiver_kunde_key:
            return self.dialog("Fehler", "Bitte zuerst Kunden auswählen.")

        kunde = self.alle_kunden[self.aktiver_kunde_key]
        
        neue = Anlage(
            id=kunde.next_anlage_id,
            beschreibung=f"Anlage {kunde.next_anlage_id}",
            felder=self.settings.get("default_felder", 3),
            reihen=self.settings.get("default_reihen", 7),
        )

        kunde.next_anlage_id += 1
        self.anlagen_daten.append(neue)

        self.ausgewaehlte_anlage_id = neue.id
        self.aktuelle_anlage = neue

        self.daten_dirty = True
        self.speichere_daten()

        self.refresh_main()
        self.dialog("Erfolg", f'Anlage "{neue.beschreibung}" hinzugefügt.')

    def anlage_loeschen(self, _e):
        if not self.ausgewaehlte_anlage_id:
            return self.dialog("Fehler", "Bitte zuerst Anlage auswählen.")

        anlage = next((a for a in self.anlagen_daten if a.id == self.ausgewaehlte_anlage_id), None)
        if not anlage:
            return self.dialog("Fehler", "Anlage nicht gefunden.")

        # Direkt löschen ohne Bestätigung
        self.anlagen_daten = [
            a for a in self.anlagen_daten if a.id != self.ausgewaehlte_anlage_id
        ]
        self.alle_kunden[self.aktiver_kunde_key].anlagen = list(self.anlagen_daten)
        self.ausgewaehlte_anlage_id = None
        self.daten_dirty = True
        self.speichere_daten()
        self.refresh_main()

    def bearbeite_ausgewaehlte_anlage(self, _e):
        if not self.ausgewaehlte_anlage_id:
            return self.dialog("Fehler", "Bitte zuerst Anlage auswählen.")

        self.aktuelle_anlage = next(
            (a for a in self.anlagen_daten if a.id == self.ausgewaehlte_anlage_id), None
        )

        if not self.aktuelle_anlage:
            return self.dialog("Fehler", "Anlage nicht gefunden.")

        self.navigiere_zu_detail_view()
    # ---------------------------------------------------------
    # Anlagen (Teil 2)
    # ---------------------------------------------------------

    def aktualisiere_anlagen_tabelle(self):
        """Aktualisiert die Anlagen-Liste mit RadioButtons."""
        container = self.ui.get("anlagen_container")
        if not container:
            return

        container.controls.clear()

        for anlage in self.anlagen_daten:
            anlage_id = str(anlage.id)

            zeile1 = ft.Row(
                [ft.Radio(value=anlage_id, label=f"ID {anlage_id}: {anlage.beschreibung}")],
                spacing=5,
            )

            zeile2 = ft.Row(
                [
                    ft.Container(width=50),
                    ft.Text(f"Code: {anlage.code or '-'}", size=12),
                    ft.Text(f"Ort: {anlage.plz_ort or '-'}", size=12),
                ],
                spacing=10,
            )

            container.controls.extend([zeile1, zeile2, ft.Divider(height=1)])

        # Auto-Select: Bei 1 Anlage erste wählen, sonst aktuelle beibehalten
        if len(self.anlagen_daten) == 1:
            anlage = self.anlagen_daten[0]
            self.ausgewaehlte_anlage_id = anlage.id
            self.aktuelle_anlage = anlage

        # RadioGroup visuell setzen (bei jeder Anzahl von Anlagen)
        if self.ausgewaehlte_anlage_id and "anlagen_radiogroup" in self.ui:
            self.ui["anlagen_radiogroup"].value = str(self.ausgewaehlte_anlage_id)

        self.page.update()

    def on_anlage_selected(self, e):
        """Callback, wenn Anlage in RadioGroup ausgewählt wird."""
        if e.control.value:
            self.ausgewaehlte_anlage_id = int(e.control.value)
            for anlage in self.anlagen_daten:
                if anlage.id == self.ausgewaehlte_anlage_id:
                    self.aktuelle_anlage = anlage
                    break

    # ---------------------------------------------------------
    # Detail-Daten
    # ---------------------------------------------------------

    def speichere_detail_daten(self):
        if not self.aktuelle_anlage:
            return

        self.map_get_obj(self.detail_mapping, self.aktuelle_anlage)

        try:
            self.aktuelle_anlage.felder = int(self.ui["felder_input"].value)
        except (ValueError, TypeError):
            self.aktuelle_anlage.felder = 3

        try:
            self.aktuelle_anlage.reihen = int(self.ui["reihen_input"].value)
        except (ValueError, TypeError):
            self.aktuelle_anlage.reihen = 7

        self.aktuelle_anlage.text_inhalt = self.ui["text_editor"].value

    def auto_speichere_detail_daten(self, _e):
        self.speichere_detail_daten()
        self.daten_dirty = True
        self.speichere_daten()

    # ---------------------------------------------------------
    # Code-Generierung
    # ---------------------------------------------------------

    def generiere_code_string(self) -> str:
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
        elif etage:
            teile.append(f"++{etage}")
        if raum:
            teile.append(f"+{raum}")

        return "".join(teile).upper() if teile else ""

    def aktualisiere_anlagen_code(self, _e=None):
        if not self.aktuelle_anlage:
            return

        neuer = self.generiere_code_string()
        alt = self.aktuelle_anlage.code_auto_last or ""

        if not self.ui["code_input"].value or self.ui["code_input"].value == alt:
            self.ui["code_input"].value = neuer
            self.aktuelle_anlage.code_auto_last = neuer
            self.aktuelle_anlage.code = neuer
            self.page.update()

        self.speichere_detail_daten()

    def aktualisiere_anlagen_code_und_speichere(self, e):
        self.aktualisiere_anlagen_code(e)
        self.daten_dirty = True
        self.speichere_daten()

    # ---------------------------------------------------------
    # Info-Berechnung (optimiert)
    # ---------------------------------------------------------

    def berechne_info(self, anlage: Anlage):
        """Berechnet Validierung + verfügbare Spalten."""
        felder = anlage.felder
        reihen = anlage.reihen
        text = anlage.text_inhalt

        is_valid, gueltige, fehler, belegte, max_spalten = validiere_eintraege(
            text, felder, reihen
        )

        verfuegbar = max_spalten - len(belegte)

        return {
            "is_valid": is_valid,
            "gueltige": gueltige,
            "fehler": fehler,
            "belegte": belegte,
            "max_spalten": max_spalten,
            "verfuegbar": verfuegbar,
        }

    def info_aktualisieren(self, _e=None):
        if not self.aktuelle_anlage:
            return False, []

        self.speichere_detail_daten()
        info = self.berechne_info(self.aktuelle_anlage)

        self.ui["info_label"].value = (
            f"Gesamt-Spalten: {self.aktuelle_anlage.felder} × "
            f"{self.aktuelle_anlage.reihen} × {COLUMNS_PER_UNIT} = "
            f"{info['max_spalten']}"
        )

        if info["fehler"] > 0:
            self.ui["verfuegbar_label"].value = f"❌ {info['fehler']} Fehler!"
            self.ui["verfuegbar_label"].color = ft.Colors.RED_700
        else:
            self.ui["verfuegbar_label"].value = (
                f"✓ Verfügbar: {info['verfuegbar']} von {info['max_spalten']}"
            )
            self.ui["verfuegbar_label"].color = (
                ft.Colors.GREEN_700
                if info["verfuegbar"] == info["max_spalten"]
                else ft.Colors.ORANGE_700
            )

        self.page.update()
        return info["is_valid"], info["gueltige"]

    def info_aktualisieren_und_speichern(self, e=None):
        self.info_aktualisieren(e)
        self.speichere_detail_daten()
        self.daten_dirty = True
        self.speichere_daten()
    # ---------------------------------------------------------
    # Export / Import (optimiert)
    # ---------------------------------------------------------

    def exportiere_anlage(self, _e):
        if not self.aktuelle_anlage:
            return self.dialog("Fehler", "Keine Anlage ausgewählt.")

        try:
            projekt = ""
            if self.aktiver_kunde_key in self.alle_kunden:
                projekt = self.alle_kunden[self.aktiver_kunde_key].projekt

            pfad = exportiere_anlage_ods(
                anlage_to_dict(self.aktuelle_anlage),
                self.settings,
                self.get_export_base_path(),
                self.aktiver_kunde_key,
                projekt,
            )
            self.letzte_export_datei = pfad
            self.show_file_snackbar("Exportiert", pfad.name)
            pass  # Snackbar bereits gesetzt

        except Exception as e:
            self.show_snackbar(f"Export-Fehler: {e}")

    def teile_letzte_ods(self, _e):
        if not self.letzte_export_datei or not self.letzte_export_datei.exists():
            return self.show_snackbar("Keine Datei gefunden")
        self.show_snackbar(f"Datei: {self.letzte_export_datei}")

    def exportiere_kunde_odt(self, _e):
        if not self.aktiver_kunde_key:
            return self.dialog("Fehler", "Kein Kunde ausgewählt.")

        self.speichere_projekt_daten()
        kunde = self.alle_kunden[self.aktiver_kunde_key]

        try:
            pfad = exportiere_kunde_odt(
                kunde_to_dict(kunde),
                self.aktiver_kunde_key,
                self.get_export_base_path(),
            )
            self.show_file_snackbar("Exportiert", pfad.name)
            pass  # Snackbar bereits gesetzt

        except Exception as e:
            self.show_snackbar(f"Export-Fehler: {e}")

    def exportiere_zu_downloads(self, _e):
        """Exportiert Daten + Settings als JSON."""
        export_base = self.get_export_base_path()
        ts = self._timestamp()

        daten = self.data_path / "anlagen_daten.json"
        settings = self.data_path / "app_settings.json"

        exported = []

        if daten.exists():
            dst = export_base / f"Verteiler_Daten_{ts}.json"
            if self._copy_file(daten, dst, "Export"):
                exported.append(dst.name)

        if settings.exists():
            dst = export_base / f"Verteiler_Einstellungen_{ts}.json"
            if self._copy_file(settings, dst, "Export"):
                exported.append(dst.name)

        if exported:
            # Snackbar für jeden exportierten File
            for filename in exported:
                self.show_file_snackbar("Exportiert", filename)
        else:
            self.show_snackbar("Keine Daten zum Exportieren")

    def exportiere_alle_kunden(self, _e):
        """Exportiert alle Kunden als ODT."""
        if not self.alle_kunden:
            return self.dialog("Fehler", "Keine Kunden vorhanden.")

        try:
            count = 0
            base = self.get_export_base_path()

            for name, kunde in self.alle_kunden.items():
                exportiere_kunde_odt(kunde_to_dict(kunde), name, base)
                count += 1

            self.show_snackbar(f"{count} Kunden exportiert nach {base}")

        except Exception as e:
            self.show_snackbar(f"Export-Fehler: {e}")

    def exportiere_alle_daten_json(self, _e):
        """Exportiert anlagen_daten.json mit Zeitstempel."""
        src = self.data_path / "anlagen_daten.json"
        if not src.exists():
            return self.show_snackbar("Keine Daten zum Exportieren")

        dst = self.get_export_base_path() / f"anlagen_daten_{self._timestamp()}.json"
        if self._copy_file(src, dst, "Export"):
            pass  # Snackbar bereits gesetzt

    async def importiere_von_downloads(self, _e):
        """Öffnet FilePicker für JSON-Import."""
        files = await ft.FilePicker().pick_files(
            allowed_extensions=["json"],
            allow_multiple=False,
            dialog_title="JSON-Datei zum Importieren wählen"
        )
        
        if not files:
            return  # Abgebrochen
        
        file_path = Path(files[0].path)
        await self.process_import_file(file_path)
    
    async def process_import_file(self, file_path):
        """Verarbeitet ausgewählte Import-Datei."""
        file_name = file_path.name.lower()
        
        # Snackbar: Prüfung gestartet
        self.show_snackbar(f"Prüfe Datei: {file_path.name}")
        
        # 1. Validiere Dateinamen
        is_daten = "daten" in file_name or "anlagen" in file_name
        is_settings = "setting" in file_name or "einstellung" in file_name
        
        if not (is_daten or is_settings):
            return self.dialog("Ungültige Datei", 
                             "Die Datei muss 'daten'/'anlagen' oder 'settings'/'einstellung' im Namen enthalten.")
        
        # 2. Lade und validiere JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
        except Exception as ex:
            return self.show_snackbar(f"Datei-Fehler: {ex}")
        
        # 3. Settings-Import (immer ohne Prüfung)
        if is_settings:
            target = self.data_path / "app_settings.json"
            if self._copy_file(file_path, target, "Import"):
                self.settings = self.data_manager.lade_settings()
                self.show_snackbar("Einstellungen importiert")
                return  # Snackbar bereits gesetzt
            else:
                return self.show_snackbar("Einstellungen-Import fehlgeschlagen")
        
        # 4. Daten-Import mit Vergleich
        if is_daten:
            self._import_daten_mit_vergleich(file_path, import_data)
    
    def _import_daten_mit_vergleich(self, file_path, import_data):
        """Importiert Daten mit Vergleich und Merge-Option."""
        # Zähle Import-Daten
        import_kunden = len(import_data.get('alle_kunden', {}))
        import_anlagen = sum(len(k.get('anlagen', [])) for k in import_data.get('alle_kunden', {}).values())
        
        # Zähle aktuelle Daten
        aktuelle_kunden = len(self.alle_kunden)
        aktuelle_anlagen = sum(len(k.anlagen) for k in self.alle_kunden.values())
        
        # Prüfe ob Merge möglich (unterschiedliche Kunden)
        import_kunde_keys = set(import_data.get('alle_kunden', {}).keys())
        aktuelle_kunde_keys = set(self.alle_kunden.keys())
        neue_kunden = import_kunde_keys - aktuelle_kunde_keys
        
        merge_moeglich = len(neue_kunden) > 0
        
        # Vergleich
        if import_kunden < aktuelle_kunden or import_anlagen < aktuelle_anlagen:
            # Weniger Daten
            msg = f"Wir haben hier schon mehr Daten:\n\nAktuell: {aktuelle_kunden} Kunden, {aktuelle_anlagen} Anlagen\nImport: {import_kunden} Kunden, {import_anlagen} Anlagen\n\nTrotzdem importieren?"
            if merge_moeglich:
                msg += f"\n\nODER: {len(neue_kunden)} neue Kunden mergen?"
                self._confirm_import_dialog(msg, file_path, merge_moeglich, neue_kunden, import_data)
            else:
                self._confirm_import_dialog(msg, file_path, False, None, import_data)
        elif import_kunden == aktuelle_kunden and import_anlagen == aktuelle_anlagen:
            # Gleiche Daten
            msg = f"Die Daten sind gleich:\n\n{aktuelle_kunden} Kunden, {aktuelle_anlagen} Anlagen\n\nTrotzdem importieren?"
            self._confirm_import_dialog(msg, file_path, merge_moeglich, neue_kunden, import_data)
        else:
            # Mehr Daten - direkt importieren
            if merge_moeglich:
                msg = f"Import enthält mehr Daten:\n\nAktuell: {aktuelle_kunden} Kunden, {aktuelle_anlagen} Anlagen\nImport: {import_kunden} Kunden, {import_anlagen} Anlagen\n\nImportieren oder {len(neue_kunden)} neue Kunden mergen?"
                self._confirm_import_dialog(msg, file_path, True, neue_kunden, import_data)
            else:
                self._do_import(file_path)
    
    def _confirm_import_dialog(self, message, file_path, merge_moeglich, neue_kunden, import_data):
        """Zeigt Bestätigungs-Dialog mit Import/Merge-Optionen."""
        def on_import(e):
            dlg.open = False
            self.page.update()
            self._do_import(file_path)
        
        def on_merge(e):
            dlg.open = False
            self.page.update()
            self._do_merge(neue_kunden, import_data)
        
        def on_cancel(e):
            dlg.open = False
            self.page.update()
            self.show_snackbar("Import abgebrochen")
        
        actions = [
            ft.TextButton("Importieren", on_click=on_import),
        ]
        
        if merge_moeglich:
            actions.insert(0, ft.TextButton("Mergen", on_click=on_merge))
        
        actions.append(ft.TextButton("Abbrechen", on_click=on_cancel))
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Import-Optionen"),
            content=ft.Text(message),
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    def _do_import(self, file_path):
        """Führt Import durch (überschreibt alles)."""
        target = self.data_path / "anlagen_daten.json"
        if self._copy_file(file_path, target, "Import"):
            self.lade_daten()
            self.aktualisiere_aktive_daten()
            self.refresh_main()  # UI aktualisieren!
            self.show_snackbar("Daten importiert")
            pass  # Snackbar bereits gesetzt
        else:
            self.show_snackbar("Daten-Import fehlgeschlagen")
    
    def _do_merge(self, neue_kunde_keys, import_data):
        """Führt Merge durch (nur neue Kunden hinzufügen)."""
        import_kunden = import_data.get('alle_kunden', {})
        
        merged_count = 0
        for kunde_key in neue_kunde_keys:
            if kunde_key in import_kunden:
                # Konvertiere zu Dataclass
                kunde_raw = import_kunden[kunde_key]
                kunde = Kunde(**kunde_raw)
                kunde.anlagen = [Anlage(**a) for a in kunde_raw.get('anlagen', [])]
                self.alle_kunden[kunde_key] = kunde
                merged_count += 1
        
        if merged_count > 0:
            self.speichere_daten()
            self.aktualisiere_aktive_daten()
            self.refresh_main()  # UI aktualisieren!
            self.show_snackbar(f"{merged_count} Kunden gemergt")
            self.dialog("Merge erfolgreich", f"{merged_count} neue Kunden wurden hinzugefügt.")
        else:
            self.show_snackbar("Keine neuen Kunden gefunden")
    
    def show_snackbar(self, message):
        """Zeigt Snackbar-Nachricht."""
        snackbar = ft.SnackBar(
            content=ft.Text(message),
            duration=4000  # 4 Sekunden
        )
        self.page.overlay.append(snackbar)
        snackbar.open = True
        self.page.update()

    # ---------------------------------------------------------
    # Settings (optimiert)
    # ---------------------------------------------------------

    def auto_speichere_settings(self, _e):
        """Speichert alle Settings generisch über ein Mapping."""
        # Merke altes Datumsformat
        old_format = self.settings.get("datum_format", "DE")
        
        mapping = {
            "settings_felder_input": ("default_felder", int),
            "settings_reihen_input": ("default_reihen", int),
            "settings_font_gemergt_input": ("fontsize_gemergte_zelle", int),
            "settings_font_beschr_input": ("fontsize_beschriftung_zelle", int),
            "settings_font_inhalt_input": ("fontsize_inhalt_zelle", int),
            "settings_spalten_breite_input": ("spalten_breite", float),
            "settings_beschr_hoehe_input": ("beschriftung_row_hoehe", float),
            "settings_inhalt_hoehe_input": ("inhalt_row_hoehe", float),
            "settings_rand_oben_input": ("rand_oben", float),
            "settings_rand_unten_input": ("rand_unten", float),
            "settings_rand_links_input": ("rand_links", float),
            "settings_rand_rechts_input": ("rand_rechts", float),
        }

        bool_mapping = {
            "settings_umrandung_switch": "zellen_umrandung",
        }

        str_mapping = {
            "settings_datum_format": "datum_format",
        }
        
        # Spezielle Behandlung für linebreak_char (max 3 Zeichen)
        if "settings_linebreak_input" in self.ui:
            linebreak = self.ui["settings_linebreak_input"].value or ";"
            linebreak = linebreak[:3]  # Maximal 3 Zeichen
            self.settings["linebreak_char"] = linebreak
            self.ui["settings_linebreak_input"].value = linebreak  # Zurücksetzen falls zu lang

        try:
            for ui_key, (setting_key, cast) in mapping.items():
                if ui_key in self.ui:
                    raw = self.ui[ui_key].value
                    try:
                        self.settings[setting_key] = cast(raw)
                    except (ValueError, TypeError):
                        pass

            for ui_key, setting_key in bool_mapping.items():
                if ui_key in self.ui:
                    self.settings[setting_key] = bool(self.ui[ui_key].value)

            for ui_key, setting_key in str_mapping.items():
                if ui_key in self.ui:
                    self.settings[setting_key] = self.ui[ui_key].value

            try:
                self.data_manager.speichere_settings(self.settings)
            except (OSError, ValueError, TypeError):
                pass
            
            # Wenn Datumsformat geändert wurde, refresh main view
            new_format = self.settings.get("datum_format", "DE")
            if old_format != new_format:
                self.refresh_main()
                # Datum im neuen Format anzeigen
                if self.aktiver_kunde_key and "kunde_datum" in self.ui:
                    kunde = self.alle_kunden[self.aktiver_kunde_key]
                    iso = getattr(kunde, "datum", "")
                    self.ui["kunde_datum"].value = format_date_display(iso, new_format)
                    self.page.update()

        except (OSError, ValueError, TypeError):
            pass

    # ---------------------------------------------------------
    # Logs
    # ---------------------------------------------------------

    def zeige_logs(self, _e):
        log_file = os.getenv("FLET_APP_CONSOLE")
        if log_file:
            try:
                with open(log_file, "r") as f:
                    logs = f.read()
                if len(logs) > 5000:
                    logs = "...\n" + logs[-5000:]
                self.dialog("Debug Logs", logs)
            except Exception as e:
                self.dialog("Log-Fehler", f"Konnte Logs nicht lesen: {e}")
        else:
            self.dialog("Keine Logs", "FLET_APP_CONSOLE nicht verfügbar")

    # ---------------------------------------------------------
    # main()
    # ---------------------------------------------------------

def main(page: ft.Page):
    AnlagenApp(page)

if __name__ == "__main__":
    ft.app(target=main)
