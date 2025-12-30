#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UI-Builder-Modul für Flet.

Enthält alle Funktionen zum Erstellen der Benutzeroberfläche mit Flet.
"""

import flet as ft
from constants import SPALTEN_PRO_EINHEIT


class UIBuilder:
    """Helper-Klasse für UI-Erstellung mit Flet."""
    
    def __init__(self, app_instance, page):
        """Initialisiert den UIBuilder.
        
        Args:
            app_instance: Referenz zur App-Instanz
            page: Flet Page-Objekt
        """
        self.app = app_instance
        self.page = page
    
    def erstelle_hauptansicht(self):
        """Erstellt die Hauptansicht mit Kunden und Anlagen."""
        
        # --- KUNDEN-VERWALTUNG ---
        self.app.kunden_auswahl = ft.Dropdown(
            options=[ft.dropdown.Option(k) for k in self.app.alle_kunden.keys()],
            value=self.app.aktiver_kunde_key,
            on_change=self.app.wechsel_kunden_auswahl,
            expand=True,
        )
        
        # Navigation Buttons
        nav_row = ft.Row([
            ft.ElevatedButton("◀", on_click=self.app._navigiere_kunde_links, expand=True),
            ft.ElevatedButton("▶", on_click=self.app._navigiere_kunde_rechts, expand=True)
        ], spacing=5)
        
        # Kunde Input
        self.app.kunde_input = ft.TextField(hint_text="Kundenname", expand=True)
        
        # Action Buttons
        action_buttons = ft.Column([
            ft.ElevatedButton("⭐ Neu", on_click=self.app._kunde_neu_hinzufuegen, expand=True),
            ft.ElevatedButton("🔄 Umbenennen", on_click=self.app._kunde_umbenennen, expand=True),
            ft.ElevatedButton("🗑️ Lösche Kunde", on_click=self.app.kunde_loeschen, expand=True)
        ], spacing=5)
        
        # Projektdaten
        felder_reihenfolge = ['projekt', 'datum', 'adresse', 'plz', 'ort', 
                              'ansprechpartner', 'telefonnummer', 'email']
        projekt_fields = []
        
        for key in felder_reihenfolge:
            label_text = self._get_label_text(key)
            projekt_fields.append(
                ft.Column([
                    ft.Text(label_text + ':', weight=ft.FontWeight.BOLD, size=10),
                    self.app.kunden_daten[key]
                ], spacing=3)
            )
        
        # Anlagen-Tabelle
        self.app.anlagen_tabelle = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Beschreibung")),
                ft.DataColumn(ft.Text("Code")),
                ft.DataColumn(ft.Text("Ort")),
            ],
            rows=[]
        )
        
        # Hauptcontainer
        return ft.Column([
            ft.Text("Aktiver Kunde:", weight=ft.FontWeight.BOLD),
            self.app.kunden_auswahl,
            nav_row,
            ft.Text("Name (Neu/Umbenennen):", weight=ft.FontWeight.BOLD, size=10),
            self.app.kunde_input,
            action_buttons,
            ft.Divider(height=1),
            *projekt_fields,
            ft.Divider(height=1),
            ft.Text("Verwaltete Anlagen:", weight=ft.FontWeight.BOLD),
            self.app.anlagen_tabelle,
            ft.ElevatedButton("✏️ Bearbeiten", on_click=self.app.bearbeite_ausgewaehlte_anlage, expand=True),
            ft.ElevatedButton("🗑️ Lösche Anlage", on_click=self.app.anlage_loeschen, expand=True),
            ft.ElevatedButton("⭐ Anlage hinzufügen", on_click=self.app.anlage_hinzufuegen, expand=True),
            ft.ElevatedButton("📄 Kunde exportieren", on_click=self.app.exportiere_kunde_odt, expand=True),
            ft.ElevatedButton("⚙️ Einstellungen", on_click=self.app.navigiere_zu_settings, expand=True),
        ], spacing=5, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def erstelle_anlage_detail_view(self):
        """Erstellt die Detail-Ansicht für eine Anlage."""
        
        # Zurück-Button
        back_button = ft.ElevatedButton("« Zurück", on_click=self.app.zurueck_zur_hauptansicht)
        
        # Eingabefelder
        self.app.beschr_input = ft.TextField(label="Beschreibung", on_change=self.app.auto_speichere_detail_daten)
        self.app.name_input = ft.TextField(label="Name", on_change=self.app.auto_speichere_detail_daten)
        self.app.adresse_input = ft.TextField(label="Adresse", on_change=self.app.auto_speichere_detail_daten)
        self.app.plz_ort_input = ft.TextField(label="PLZ + Ort", on_change=self.app.auto_speichere_detail_daten)
        self.app.raum_input = ft.TextField(label="Raum", on_change=self.app.aktualisiere_anlagen_code_und_speichere)
        self.app.gebaeude_input = ft.TextField(label="Gebäude", on_change=self.app.aktualisiere_anlagen_code_und_speichere)
        self.app.geschoss_input = ft.TextField(label="Geschoss", on_change=self.app.aktualisiere_anlagen_code_und_speichere)
        self.app.funktion_input = ft.TextField(label="Funktion", on_change=self.app.aktualisiere_anlagen_code_und_speichere)
        self.app.zaehlernummer_input = ft.TextField(label="Zählernummer", on_change=self.app.auto_speichere_detail_daten)
        self.app.zaehlerstand_input = ft.TextField(label="Zählerstand", on_change=self.app.auto_speichere_detail_daten)
        self.app.code_input = ft.TextField(label="Anlagen-Code (Auto)", on_change=self.app.auto_speichere_detail_daten)
        self.app.bemerkung_input = ft.TextField(label="Bemerkung", on_change=self.app.auto_speichere_detail_daten)
        
        # Export-Konfiguration
        self.app.felder_input = ft.TextField(label="Felder", keyboard_type=ft.KeyboardType.NUMBER, 
                                              on_change=self.app.info_aktualisieren_und_speichern)
        self.app.reihen_input = ft.TextField(label="Reihen", keyboard_type=ft.KeyboardType.NUMBER,
                                              on_change=self.app.info_aktualisieren_und_speichern)
        
        self.app.info_label = ft.Text("", size=10)
        self.app.verfuegbar_label = ft.Text("", size=10)
        
        # Text Editor
        self.app.text_editor = ft.TextField(
            label="Beschriftungen (1 Heizung | 3-6 Lüftung | 7+5 Elektrik)",
            multiline=True,
            min_lines=10,
            max_lines=20,
            on_change=self.app.info_aktualisieren_und_speichern
        )
        
        # Export Buttons
        export_button = ft.ElevatedButton("📊 Exportiere & Teile ODS", 
                                          on_click=self.app.exportiere_anlage, expand=True)
        self.app.teile_button = ft.ElevatedButton("🔗 Teile letzte ODS", 
                                                   on_click=self.app.teile_letzte_ods, 
                                                   disabled=True, expand=True)
        
        return ft.Column([
            back_button,
            ft.Divider(),
            ft.Text("Anlagen-Details", weight=ft.FontWeight.BOLD, size=14),
            self.app.beschr_input,
            ft.Divider(),
            ft.Text("Lokalisierung", weight=ft.FontWeight.BOLD, size=12),
            self.app.name_input,
            self.app.adresse_input,
            self.app.plz_ort_input,
            self.app.raum_input,
            self.app.gebaeude_input,
            self.app.geschoss_input,
            self.app.funktion_input,
            self.app.zaehlernummer_input,
            self.app.zaehlerstand_input,
            self.app.code_input,
            self.app.bemerkung_input,
            ft.Divider(),
            ft.Text("Export-Konfiguration", weight=ft.FontWeight.BOLD, size=12),
            self.app.felder_input,
            self.app.reihen_input,
            self.app.info_label,
            self.app.verfuegbar_label,
            ft.Divider(),
            self.app.text_editor,
            export_button,
            self.app.teile_button,
        ], spacing=5, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def erstelle_settings_dialog(self):
        """Erstellt den Settings-Dialog."""
        
        back_button = ft.ElevatedButton("« Zurück", on_click=self.app.zurueck_zur_hauptansicht)
        
        # Settings Inputs
        self.app.settings_felder_input = ft.TextField(
            label="Standard Felder", 
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(self.app.settings['default_felder']),
            on_change=self.app.auto_speichere_settings
        )
        
        self.app.settings_reihen_input = ft.TextField(
            label="Standard Reihen",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(self.app.settings['default_reihen']),
            on_change=self.app.auto_speichere_settings
        )
        
        self.app.settings_font_gemergt_input = ft.TextField(
            label="Font Gemergte Zelle (pt)",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(self.app.settings['fontsize_gemergte_zelle']),
            on_change=self.app.auto_speichere_settings
        )
        
        self.app.settings_font_beschr_input = ft.TextField(
            label="Font Beschriftung (pt)",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(self.app.settings['fontsize_beschriftung_zelle']),
            on_change=self.app.auto_speichere_settings
        )
        
        self.app.settings_font_inhalt_input = ft.TextField(
            label="Font Inhalt (pt)",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(self.app.settings['fontsize_inhalt_zelle']),
            on_change=self.app.auto_speichere_settings
        )
        
        self.app.settings_spalten_breite_input = ft.TextField(
            label="Spaltenbreite (cm)",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(self.app.settings['spalten_breite']),
            on_change=self.app.auto_speichere_settings
        )
        
        self.app.settings_beschr_hoehe_input = ft.TextField(
            label="Beschriftungszeile (cm)",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(self.app.settings['beschriftung_row_hoehe']),
            on_change=self.app.auto_speichere_settings
        )
        
        self.app.settings_inhalt_hoehe_input = ft.TextField(
            label="Inhaltszeile (cm)",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(self.app.settings['inhalt_row_hoehe']),
            on_change=self.app.auto_speichere_settings
        )
        
        self.app.settings_umrandung_switch = ft.Switch(
            label="Zellen umranden",
            value=self.app.settings['zellen_umrandung'],
            on_change=self.app.auto_speichere_settings
        )
        
        self.app.settings_rand_oben_input = ft.TextField(
            label="Rand Oben (cm)",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(self.app.settings['rand_oben']),
            on_change=self.app.auto_speichere_settings
        )
        
        self.app.settings_rand_unten_input = ft.TextField(
            label="Rand Unten (cm)",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(self.app.settings['rand_unten']),
            on_change=self.app.auto_speichere_settings
        )
        
        self.app.settings_rand_links_input = ft.TextField(
            label="Rand Links (cm)",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(self.app.settings['rand_links']),
            on_change=self.app.auto_speichere_settings
        )
        
        self.app.settings_rand_rechts_input = ft.TextField(
            label="Rand Rechts (cm)",
            keyboard_type=ft.KeyboardType.NUMBER,
            value=str(self.app.settings['rand_rechts']),
            on_change=self.app.auto_speichere_settings
        )
        
        return ft.Column([
            back_button,
            ft.Divider(),
            ft.Text("Einstellungen", weight=ft.FontWeight.BOLD, size=14),
            ft.Text("Standard-Werte", weight=ft.FontWeight.BOLD, size=11),
            self.app.settings_felder_input,
            self.app.settings_reihen_input,
            ft.Divider(),
            ft.Text("Schriftgrößen", weight=ft.FontWeight.BOLD, size=11),
            self.app.settings_font_gemergt_input,
            self.app.settings_font_beschr_input,
            self.app.settings_font_inhalt_input,
            ft.Divider(),
            ft.Text("Tabellen-Layout", weight=ft.FontWeight.BOLD, size=11),
            self.app.settings_spalten_breite_input,
            self.app.settings_beschr_hoehe_input,
            self.app.settings_inhalt_hoehe_input,
            self.app.settings_umrandung_switch,
            ft.Divider(),
            ft.Text("Seiten-Layout", weight=ft.FontWeight.BOLD, size=11),
            self.app.settings_rand_oben_input,
            self.app.settings_rand_unten_input,
            self.app.settings_rand_links_input,
            self.app.settings_rand_rechts_input,
            ft.Divider(),
            ft.Text("Datensicherung", weight=ft.FontWeight.BOLD, size=11),
            ft.ElevatedButton("📤 Export zu Downloads", on_click=self.app.exportiere_zu_downloads, expand=True),
            ft.ElevatedButton("📥 Import von Downloads", on_click=self.app.importiere_von_downloads, expand=True),
            ft.Text("Erstellt: Verteiler_Daten.json & Verteiler_Einstellungen.json", size=8),
        ], spacing=5, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def _get_label_text(self, key):
        """Helper für Label-Texte."""
        labels = {
            'plz': 'PLZ',
            'email': 'E-Mail',
            'telefonnummer': 'Telefon',
            'ansprechpartner': 'Ansprechpartner',
            'datum': 'Datum (JJJJ-MM-TT)'
        }
        return labels.get(key, key.capitalize())
