#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UI-Builder-Modul – Registry-Version (PEP‑8 konform)."""

import flet as ft


class UIBuilder:
    """Erzeugt alle UI-Elemente und speichert sie in app.ui[...]"""

    def __init__(self, app, page):
        self.app = app
        self.page = page

    # ---------------------------------------------------------
    # Hilfsfunktionen
    # ---------------------------------------------------------

    def tf(self, key, label=None, hint=None, value=None, expand=True,
           on_change=None, **kw):
        """Erzeugt ein TextField und speichert es in self.app.ui[key]."""
        field = ft.TextField(
            label=label,
            hint_text=hint,
            value=value,
            expand=expand,
            **kw
        )
        if on_change:
            field.on_change = on_change

        self.app.ui[key] = field
        return field

    def sw(self, key, label, value, on_change=None):
        """Switch erzeugen und registrieren."""
        s = ft.Switch(label=label, value=value)
        if on_change:
            s.on_change = on_change
        self.app.ui[key] = s
        return s

    # ---------------------------------------------------------
    # Hauptansicht
    # ---------------------------------------------------------

    def erstelle_hauptansicht(self):
        """Erstellt die Hauptansicht."""

        # Kunden-Auswahl mit About-Button
        # Berechne Dropdown-Breite: Page-Breite - Button-Breite - Spacing - 10%
        about_button_width = 100
        spacing = 10
        dropdown_width = self.app.page.width - about_button_width - spacing - (self.app.page.width * 0.1) if self.app.page.width else 400
        
        dd = ft.Dropdown(
            options=[ft.dropdown.Option(k) for k in self.app.alle_kunden],
            value=self.app.aktiver_kunde_key,
            width=dropdown_width,
        )
        dd.on_change = self.app.wechsel_kunden_auswahl
        self.app.ui["kunden_auswahl"] = dd
        
        about_btn = ft.ElevatedButton(
            "About",
            on_click=self.app.zeige_about_dialog,
            width=about_button_width,
        )
        
        auswahl_row = ft.Row(
            [dd, about_btn],
            spacing=spacing,
        )

        # Navigation
        nav = ft.Row(
            [
                ft.ElevatedButton("◀", on_click=self.app._navigiere_kunde_links,
                                  expand=True),
                ft.ElevatedButton("▶", on_click=self.app._navigiere_kunde_rechts,
                                  expand=True),
            ],
            spacing=5,
        )

        # Kunde Input
        self.tf("kunde_input", hint="Kundenname")

        # Projektdaten - Datum-Label abhängig vom Format
        datum_format = self.app.settings.get("datum_format", "DE")
        datum_label = "Datum (TT.MM.JJJJ)" if datum_format == "DE" else "Datum (JJJJ-MM-TT)"
        
        projektfelder = {
            "kunde_projekt": "Projektname",
            "kunde_datum": datum_label,
            "kunde_adresse": "Adresse",
            "kunde_plz": "PLZ",
            "kunde_ort": "Ort",
            "kunde_ansprechpartner": "Ansprechpartner",
            "kunde_telefonnummer": "Telefon",
            "kunde_email": "E-Mail",
        }

        for key, label in projektfelder.items():
            self.tf(
                key,
                label=label,
                on_blur=self.app.on_kunde_feld_blur
            )

        # Anlagen Container und RadioGroup
        anlagen_container = ft.Column([], spacing=5)
        
        # RadioGroup mit container als content
        radiogroup = ft.RadioGroup(content=anlagen_container)
        radiogroup.on_change = self.app.on_anlage_selected
        
        self.app.ui["anlagen_container"] = anlagen_container
        self.app.ui["anlagen_radiogroup"] = radiogroup

        # Action Buttons in Row
        aktionen = ft.Row(
            [
                ft.ElevatedButton("NEU",
                                  on_click=self.app._kunde_neu_hinzufuegen,
                                  expand=True),
                ft.ElevatedButton("UMBENENNEN",
                                  on_click=self.app._kunde_umbenennen,
                                  expand=True),
                ft.ElevatedButton("LÖSCHEN",
                                  on_click=self.app.kunde_loeschen,
                                  expand=True),
            ],
            spacing=5,
        )

        return ft.Column(
            [
                ft.Text("Aktiver Kunde:", weight=ft.FontWeight.BOLD),
                auswahl_row,  # Dropdown + About Button
                nav,
                ft.Text("Name (Neu/Umbenennen):",
                        weight=ft.FontWeight.BOLD, size=10),
                self.app.ui["kunde_input"],
                aktionen,
                ft.Divider(height=1),
                *[self.app.ui[k] for k in projektfelder],
                ft.Divider(height=1),
                ft.Text("Verwaltete Anlagen:",
                        weight=ft.FontWeight.BOLD),
                self.app.ui["anlagen_radiogroup"],
                # Zeile 1: Anlage bearbeiten - hinzufügen
                ft.Row([
                    ft.ElevatedButton("ANLAGE BEARBEITEN",
                                      on_click=self.app.bearbeite_ausgewaehlte_anlage,
                                      expand=True),
                    ft.ElevatedButton("ANLAGE HINZUFÜGEN",
                                      on_click=self.app.anlage_hinzufuegen,
                                      expand=True),
                ], spacing=5),
                # Zeile 2: Anlage Tabellenexport - löschen
                ft.Row([
                    ft.ElevatedButton("ANLAGE TABELLENEXPORT",
                                      on_click=self.app.exportiere_anlage,
                                      expand=True),
                    ft.ElevatedButton("ANLAGE LÖSCHEN",
                                      on_click=self.app.anlage_loeschen,
                                      expand=True),
                ], spacing=5),
                # Zeile 3: Kunde - Alle Kunden Text Export
                ft.Row([
                    ft.ElevatedButton("KUNDE TEXT EXPORT",
                                      on_click=self.app.exportiere_kunde_odt,
                                      expand=True),
                    ft.ElevatedButton("ALLE KUNDEN TEXT EXPORT",
                                      on_click=self.app.exportiere_alle_kunden,
                                      expand=True),
                ], spacing=5),
                # Zeile 4: Einstellungen - JSON Export
                ft.Row([
                    ft.ElevatedButton("EINSTELLUNGEN",
                                      on_click=self.app.navigiere_zu_settings,
                                      expand=True),
                    ft.ElevatedButton("ALLE DATEN JSON EXPORT",
                                      on_click=self.app.exportiere_alle_daten_json,
                                      expand=True),
                ], spacing=5),
            ],
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    # ---------------------------------------------------------
    # Detailansicht
    # ---------------------------------------------------------

    def erstelle_anlage_detail_view(self):
        back = ft.ElevatedButton("« Zurück",
                                 on_click=self.app.zurueck_zur_hauptansicht)

        # Felder
        felder = {
            "beschr_input": "Beschreibung",
            "name_input": "Name",
            "adresse_input": "Adresse",
            "plz_ort_input": "PLZ + Ort",
            "raum_input": "Raum",
            "gebaeude_input": "Gebäude",
            "geschoss_input": "Geschoss",
            "funktion_input": "Funktion",
            "zaehlernummer_input": "Zählernummer",
            "zaehlerstand_input": "Zählerstand",
            "code_input": "Anlagen-Code (Auto)",
            "bemerkung_input": "Bemerkung",
        }

        for key, label in felder.items():
            self.tf(key, label=label)

        # Auto-Speichern
        for key in [
            "beschr_input", "name_input", "adresse_input", "plz_ort_input",
            "zaehlernummer_input", "zaehlerstand_input", "code_input",
            "bemerkung_input"
        ]:
            self.app.ui[key].on_change = self.app.auto_speichere_detail_daten

        # Code-Aktualisierung
        for key in ["raum_input", "gebaeude_input", "geschoss_input",
                    "funktion_input"]:
            self.app.ui[key].on_change = (
                self.app.aktualisiere_anlagen_code_und_speichere
            )

        # Export-Konfiguration
        self.tf(
            "felder_input",
            label="Felder",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self.app.info_aktualisieren_und_speichern,
        )
        self.tf(
            "reihen_input",
            label="Reihen",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self.app.info_aktualisieren_und_speichern,
        )

        self.app.ui["info_label"] = ft.Text("", size=10)
        self.app.ui["verfuegbar_label"] = ft.Text("", size=10)

        # Text Editor
        editor = ft.TextField(
            label="Beschriftungen (1 Heizung | 3-6 Lüftung | 7+5 Elektrik)",
            multiline=True,
            min_lines=10,
            max_lines=20,
        )
        editor.on_change = self.app.info_aktualisieren_und_speichern
        self.app.ui["text_editor"] = editor

        return ft.Column(
            [
                back,
                ft.Divider(),
                ft.Text("Anlagen-Details",
                        weight=ft.FontWeight.BOLD, size=14),
                self.app.ui["beschr_input"],
                ft.Divider(),
                ft.Text("Lokalisierung",
                        weight=ft.FontWeight.BOLD, size=12),
                *[self.app.ui[k] for k in [
                    "name_input", "adresse_input", "plz_ort_input",
                    "raum_input", "gebaeude_input", "geschoss_input",
                    "funktion_input", "zaehlernummer_input",
                    "zaehlerstand_input", "code_input",
                    "bemerkung_input"
                ]],
                ft.Divider(),
                ft.Text("Export-Konfiguration",
                        weight=ft.FontWeight.BOLD, size=12),
                self.app.ui["felder_input"],
                self.app.ui["reihen_input"],
                self.app.ui["info_label"],
                self.app.ui["verfuegbar_label"],
                ft.Divider(),
                editor,
            ],
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    # ---------------------------------------------------------
    # Settings
    # ---------------------------------------------------------

    def erstelle_settings_dialog(self):
        back = ft.ElevatedButton("« Zurück",
                                 on_click=self.app.zurueck_von_settings)

        settings_map = {
            "settings_felder_input": ("Standard Felder", "default_felder"),
            "settings_reihen_input": ("Standard Reihen", "default_reihen"),
            "settings_font_gemergt_input": ("Font Gemergte Zelle (pt)",
                                            "fontsize_gemergte_zelle"),
            "settings_font_beschr_input": ("Font Beschriftung (pt)",
                                           "fontsize_beschriftung_zelle"),
            "settings_font_inhalt_input": ("Font Inhalt (pt)",
                                           "fontsize_inhalt_zelle"),
            "settings_spalten_breite_input": ("Spaltenbreite (cm)",
                                              "spalten_breite"),
            "settings_beschr_hoehe_input": ("Beschriftungszeile (cm)",
                                            "beschriftung_row_hoehe"),
            "settings_inhalt_hoehe_input": ("Inhaltszeile (cm)",
                                            "inhalt_row_hoehe"),
            "settings_rand_oben_input": ("Rand Oben (cm)", "rand_oben"),
            "settings_rand_unten_input": ("Rand Unten (cm)", "rand_unten"),
            "settings_rand_links_input": ("Rand Links (cm)", "rand_links"),
            "settings_rand_rechts_input": ("Rand Rechts (cm)", "rand_rechts"),
        }

        for key, (label, setting_key) in settings_map.items():
            self.tf(
                key,
                label=label,
                value=str(self.app.settings[setting_key]),
                keyboard_type=ft.KeyboardType.NUMBER,
                on_change=self.app.auto_speichere_settings,
            )

        self.sw(
            "settings_umrandung_switch",
            "Zellen umranden",
            self.app.settings["zellen_umrandung"],
            on_change=self.app.auto_speichere_settings,
        )

        # Datumsformat-Dropdown
        datum_dropdown = ft.Dropdown(
            label="Datumsformat",
            options=[
                ft.dropdown.Option("ISO", "ISO (JJJJ-MM-TT)"),
                ft.dropdown.Option("DE", "Deutsch (TT.MM.JJJJ)"),
                ft.dropdown.Option("EN", "Englisch (MM/TT/JJJJ)"),
                ft.dropdown.Option("SHORT", "Kurz (TT.MM.JJ)"),
            ],
            value=self.app.settings.get("datum_format", "DE"),
        )
        datum_dropdown.on_change = self.app.auto_speichere_settings
        self.app.ui["settings_datum_format"] = datum_dropdown

        return ft.Column(
            [
                back,
                ft.Divider(),
                ft.Text("Einstellungen",
                        weight=ft.FontWeight.BOLD, size=14),
                ft.Text("Standard-Werte",
                        weight=ft.FontWeight.BOLD, size=11),
                self.app.ui["settings_felder_input"],
                self.app.ui["settings_reihen_input"],
                self.app.ui["settings_datum_format"],
                ft.Divider(),
                ft.Text("Schriftgrößen",
                        weight=ft.FontWeight.BOLD, size=11),
                self.app.ui["settings_font_gemergt_input"],
                self.app.ui["settings_font_beschr_input"],
                self.app.ui["settings_font_inhalt_input"],
                ft.Divider(),
                ft.Text("Tabellen-Layout",
                        weight=ft.FontWeight.BOLD, size=11),
                self.app.ui["settings_spalten_breite_input"],
                self.app.ui["settings_beschr_hoehe_input"],
                self.app.ui["settings_inhalt_hoehe_input"],
                self.app.ui["settings_umrandung_switch"],
                ft.Divider(),
                ft.Text("Seiten-Layout",
                        weight=ft.FontWeight.BOLD, size=11),
                self.app.ui["settings_rand_oben_input"],
                self.app.ui["settings_rand_unten_input"],
                self.app.ui["settings_rand_links_input"],
                self.app.ui["settings_rand_rechts_input"],
                ft.Divider(),
                ft.Text("Datensicherung",
                        weight=ft.FontWeight.BOLD, size=11),
                ft.ElevatedButton("📤 Export zu Documents",
                                  on_click=self.app.exportiere_zu_downloads,
                                  expand=True),
                ft.ElevatedButton("📥 Import von Documents",
                                  on_click=self.app.importiere_von_downloads,
                                  expand=True),
                ft.Text(
                    "Erstellt: Verteiler_Daten.json & "
                    "Verteiler_Einstellungen.json",
                    size=8,
                ),
            ],
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
