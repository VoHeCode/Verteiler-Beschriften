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

        # Kunden-Auswahl
        dd = ft.Dropdown(
            options=[ft.dropdown.Option(k) for k in self.app.alle_kunden],
            value=self.app.aktiver_kunde_key,
            expand=True,
        )
        dd.on_change = self.app.wechsel_kunden_auswahl
        self.app.ui["kunden_auswahl"] = dd

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

        # Projektdaten
        projektfelder = {
            "kunde_projekt": "Projektname",
            "kunde_datum": "Datum (JJJJ-MM-TT)",
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
                on_change=self.app.speichere_projekt_daten
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
                dd,
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
                ft.ElevatedButton("ANLAGE BEARBEITEN",
                                  on_click=self.app.bearbeite_ausgewaehlte_anlage,
                                  expand=True),
                ft.ElevatedButton("ANLAGE LÖSCHEN",
                                  on_click=self.app.anlage_loeschen,
                                  expand=True),
                ft.ElevatedButton("ANLAGE HINZUFÜGEN",
                                  on_click=self.app.anlage_hinzufuegen,
                                  expand=True),
                ft.ElevatedButton("KUNDE EXPORTIEREN",
                                  on_click=self.app.exportiere_kunde_odt,
                                  expand=True),
                ft.ElevatedButton("EINSTELLUNGEN",
                                  on_click=self.app.navigiere_zu_settings,
                                  expand=True),
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

        export_btn = ft.ElevatedButton(
            "📊 Exportiere & Teile ODS",
            on_click=self.app.exportiere_anlage,
            expand=True,
        )

        teile_btn = ft.ElevatedButton(
            "🔗 Teile letzte ODS",
            on_click=self.app.teile_letzte_ods,
            disabled=True,
            expand=True,
        )
        self.app.ui["teile_button"] = teile_btn

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
                export_btn,
                teile_btn,
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
                                 on_click=self.app.zurueck_zur_hauptansicht)

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
                ft.ElevatedButton("📤 Export zu Downloads",
                                  on_click=self.app.exportiere_zu_downloads,
                                  expand=True),
                ft.ElevatedButton("📥 Import von Downloads",
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
