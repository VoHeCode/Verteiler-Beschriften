#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UI-Builder-Modul – Registry-Version (PEP‑8 konform)."""

import flet as ft

from constants import _, BFSIZE, BFSIZE2, ts


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
        # dd.on_change = self.app.wechsel_kunden_auswahl
        dd.on_text_change = self.app.wechsel_kunden_auswahl
        self.app.ui["kunden_auswahl"] = dd
        
        about_btn = ft.ElevatedButton(
            _("About", BFSIZE),
            on_click=self.app.zeige_about_dialog,
            width=about_button_width,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
        )
        
        auswahl_row = ft.Row(
            [dd, about_btn],
            spacing=spacing,
        )

        # Navigation
        nav_left = ft.ElevatedButton(
            _("◀", BFSIZE),
            on_click=self.app._navigiere_kunde_links,
            expand=True,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
        )
        nav_right = ft.ElevatedButton(
            _("▶", BFSIZE),
            on_click=self.app._navigiere_kunde_rechts,
            expand=True,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
        )
        self.app.ui["nav_left_btn"] = nav_left
        self.app.ui["nav_right_btn"] = nav_right
        
        nav = ft.Row(
            [nav_left, nav_right],
            spacing=5,
        )

        # Kunde Input
        self.tf("kunde_input", hint=_("Kundenname"))

        # Projektdaten - Datum-Label abhängig vom Format
        datum_format = self.app.settings.get("datum_format", "DE")
        datum_label = _("Datum (TT.MM.JJJJ)") if datum_format == "DE" else _("Datum (JJJJ-MM-TT)")
        
        projektfelder = {
            "kunde_projekt": _("Projektname"),
            "kunde_datum": datum_label,
            "kunde_adresse": _("Adresse"),
            "kunde_plz": _("PLZ"),
            "kunde_ort": _("Ort"),
            "kunde_ansprechpartner": _("Ansprechpartner"),
            "kunde_telefonnummer": _("Telefon"),
            "kunde_email": _("E-Mail"),
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
                ft.ElevatedButton(
                    _("NEU", BFSIZE),
                    on_click=self.app._kunde_neu_hinzufuegen,
                    expand=True,
                    style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
                ),
                ft.ElevatedButton(
                    _("UMBENENNEN", BFSIZE),
                    on_click=self.app._kunde_umbenennen,
                    expand=True,
                    style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
                ),
                ft.ElevatedButton(
                    _("LÖSCHEN", BFSIZE),
                    on_click=self.app.kunde_loeschen,
                    expand=True,
                    style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
                ),
            ],
            spacing=5,
        )

        return ft.Column(
            [
                ft.Text(_("Aktiver Kunde:"), weight=ft.FontWeight.BOLD),
                auswahl_row,  # Dropdown + About Button
                nav,
                ft.Text(_("Name (Neu/Umbenennen):"),
                        weight=ft.FontWeight.BOLD, size=10),
                self.app.ui["kunde_input"],
                aktionen,
                ft.Divider(height=1),
                *[self.app.ui[k] for k in projektfelder],
                ft.Divider(height=1),
                ft.Text(_("Verwaltete Anlagen:"),
                        weight=ft.FontWeight.BOLD),
                self.app.ui["anlagen_radiogroup"],
                # Zeile 1: Anlage bearbeiten - hinzufügen
                ft.Row([
                    ft.ElevatedButton(
                        _("ANLAGE BEARBEITEN", BFSIZE),
                        on_click=self.app.bearbeite_ausgewaehlte_anlage,
                        expand=True,
                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
                    ),
                    ft.ElevatedButton(
                        _("ANLAGE HINZUFÜGEN", BFSIZE),
                        on_click=self.app.anlage_hinzufuegen,
                        expand=True,
                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
                    ),
                ], spacing=5),
                # Zeile 2: Anlage Tabellenexport - löschen
                ft.Row([
                    ft.ElevatedButton(
                        _("ANLAGE TABELLENEXPORT", BFSIZE),
                        on_click=self.app.exportiere_anlage,
                        expand=True,
                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
                    ),
                    ft.ElevatedButton(
                        _("ANLAGE LÖSCHEN", BFSIZE),
                        on_click=self.app.anlage_loeschen,
                        expand=True,
                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
                    ),
                ], spacing=5),
                # Zeile 3: Kunde - Alle Kunden Text Export
                ft.Row([
                    ft.ElevatedButton(
                        _("KUNDE TEXT EXPORT", BFSIZE),
                        on_click=self.app.exportiere_kunde_odt,
                        expand=True,
                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
                    ),
                    ft.ElevatedButton(
                        _("ALLE KUNDEN TEXT EXPORT", BFSIZE),
                        on_click=self.app.exportiere_alle_kunden,
                        expand=True,
                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
                    ),
                ], spacing=5),
                # Zeile 4: Einstellungen - Kunden Export
                ft.Row([
                    ft.ElevatedButton(
                        _("EINSTELLUNGEN", BFSIZE),
                        on_click=self.app.navigiere_zu_settings,
                        expand=True,
                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
                    ),
                    ft.ElevatedButton(
                        _("AKTUELLEN KUNDEN EXPORT", BFSIZE),
                        on_click=self.app.exportiere_aktuellen_kunden,
                        expand=True,
                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
                    ),
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
        back = ft.ElevatedButton(
            _("« Zurück", BFSIZE),
            on_click=self.app.zurueck_zur_hauptansicht,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
        )

        # Felder
        felder = {
            "beschr_input": _("Beschreibung"),
            "name_input": _("Name"),
            "adresse_input": _("Adresse"),
            "plz_ort_input": _("PLZ + Ort"),
            "raum_input": _("Raum"),
            "gebaeude_input": _("Gebäude"),
            "geschoss_input": _("Geschoss"),
            "funktion_input": _("Funktion"),
            "zaehlernummer_input": _("Zählernummer"),
            "zaehlerstand_input": _("Zählerstand"),
            "code_input": _("Anlagen-Code (Auto)"),
            "bemerkung_input": _("Bemerkung"),
        }

        for key, label in felder.items():
            self.tf(key, label=label)

        # Auto-Speichern bei Feld-Verlassen
        for key in [
            "beschr_input", "name_input", "adresse_input", "plz_ort_input",
            "zaehlernummer_input", "zaehlerstand_input", "code_input",
            "bemerkung_input"
        ]:
            self.app.ui[key].on_blur = self.app.auto_speichere_detail_daten

        # Code-Aktualisierung bei Feld-Verlassen
        for key in ["raum_input", "gebaeude_input", "geschoss_input",
                    "funktion_input"]:
            self.app.ui[key].on_blur = (
                self.app.aktualisiere_anlagen_code_und_speichere
            )

        # Export-Konfiguration
        self.tf(
            "felder_input",
            label=_("Felder"),
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self.app.info_aktualisieren_und_speichern,
        )
        self.tf(
            "reihen_input",
            label=_("Reihen"),
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self.app.info_aktualisieren_und_speichern,
        )

        self.app.ui["info_label"] = ft.Text("", size=10)
        self.app.ui["verfuegbar_label"] = ft.Text("", size=10)

        # Text Editor
        editor = ft.TextField(
            label=_("Beschriftungen (1 Heizung | 3-6 Lüftung | 7+5 Elektrik)"),
            multiline=True,
            min_lines=10,
            max_lines=20,
            expand=True,
        )
        editor.on_change = self.app.info_aktualisieren_und_speichern
        self.app.ui["text_editor"] = editor

        return ft.Column(
            [
                back,
                ft.Divider(),
                ft.Text(_("Anlagen-Details"),
                        weight=ft.FontWeight.BOLD, size=14),
                self.app.ui["beschr_input"],
                ft.Divider(),
                ft.Text(_("Lokalisierung"),
                        weight=ft.FontWeight.BOLD, size=12),
                *[self.app.ui[k] for k in [
                    "name_input", "adresse_input", "plz_ort_input",
                    "raum_input", "gebaeude_input", "geschoss_input",
                    "funktion_input", "zaehlernummer_input",
                    "zaehlerstand_input", "code_input",
                    "bemerkung_input"
                ]],
                ft.Divider(),
                ft.Text(_("Export-Konfiguration"),
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
        back = ft.ElevatedButton(
            _("« Zurück", BFSIZE),
            on_click=self.app.zurueck_von_settings,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
        )

        settings_map = {
            "settings_felder_input": (_("Standard Felder"), "default_felder"),
            "settings_reihen_input": (_("Standard Reihen"), "default_reihen"),
            "settings_font_gemergt_input": (_("Font Gemergte Zelle (pt)"),
                                            "fontsize_gemergte_zelle"),
            "settings_font_beschr_input": (_("Font Beschriftung (pt)"),
                                           "fontsize_beschriftung_zelle"),
            "settings_font_inhalt_input": (_("Font Inhalt (pt)"),
                                           "fontsize_inhalt_zelle"),
            "settings_spalten_breite_input": (_("Spaltenbreite (cm)"),
                                              "spalten_breite"),
            "settings_beschr_hoehe_input": (_("Beschriftungszeile (cm)"),
                                            "beschriftung_row_hoehe"),
            "settings_inhalt_hoehe_input": (_("Inhaltszeile (cm)"),
                                            "inhalt_row_hoehe"),
            "settings_rand_oben_input": (_("Rand Oben (cm)"), "rand_oben"),
            "settings_rand_unten_input": (_("Rand Unten (cm)"), "rand_unten"),
            "settings_rand_links_input": (_("Rand Links (cm)"), "rand_links"),
            "settings_rand_rechts_input": (_("Rand Rechts (cm)"), "rand_rechts"),
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
            _("Zellen umranden"),
            self.app.settings["zellen_umrandung"],
            on_change=self.app.auto_speichere_settings,
        )

        # Datumsformat-Dropdown
        datum_dropdown = ft.Dropdown(
            label=_("Datumsformat"),
            options=[
                ft.dropdown.Option("ISO", _("ISO (JJJJ-MM-TT)")),
                ft.dropdown.Option("DE", _("Deutsch (TT.MM.JJJJ)")),
                ft.dropdown.Option("EN", _("Englisch (MM/TT/JJJJ)")),
                ft.dropdown.Option("SHORT", _("Kurz (TT.MM.JJ)")),
            ],
            value=self.app.settings.get("datum_format", "DE"),
            expand=True,
        )
        datum_dropdown.on_text_change = self.app.auto_speichere_settings
        self.app.ui["settings_datum_format"] = datum_dropdown
        
        # Sprache/Locale-Dropdown
        locale_dropdown = ft.Dropdown(
            label=_("Sprache"),
            options=[
                ft.dropdown.Option(loc, loc) for loc in ts.list_locales()
            ],
            value=self.app.settings.get("selected_locale", "de_DE"),
            expand=True,
        )
        locale_dropdown.on_text_change = self.app.on_locale_change
        self.app.ui["settings_locale"] = locale_dropdown
        
        # Beide Dropdowns nebeneinander
        format_locale_row = ft.Row([
            datum_dropdown,
            locale_dropdown,
        ], spacing=10)
        
        # Linebreak-Zeichen
        self.tf(
            "settings_linebreak_input",
            label=_("Zeichen für neue Zeile (max 3)"),
            on_blur=self.app.auto_speichere_settings
        )
        self.app.ui["settings_linebreak_input"].value = self.app.settings.get("linebreak_char", ";")

        return ft.Column(
            [
                back,
                ft.Divider(),
                ft.Text(_("Einstellungen"),
                        weight=ft.FontWeight.BOLD, size=14),
                ft.Text(_("Standard-Werte"),
                        weight=ft.FontWeight.BOLD, size=11),
                self.app.ui["settings_felder_input"],
                self.app.ui["settings_reihen_input"],
                format_locale_row,
                self.app.ui["settings_linebreak_input"],
                ft.Divider(),
                ft.Text(_("Schriftgrößen"),
                        weight=ft.FontWeight.BOLD, size=11),
                self.app.ui["settings_font_gemergt_input"],
                self.app.ui["settings_font_beschr_input"],
                self.app.ui["settings_font_inhalt_input"],
                ft.Divider(),
                ft.Text(_("Tabellen-Layout"),
                        weight=ft.FontWeight.BOLD, size=11),
                self.app.ui["settings_spalten_breite_input"],
                self.app.ui["settings_beschr_hoehe_input"],
                self.app.ui["settings_inhalt_hoehe_input"],
                self.app.ui["settings_umrandung_switch"],
                ft.Divider(),
                ft.Text(_("Seiten-Layout"),
                        weight=ft.FontWeight.BOLD, size=11),
                self.app.ui["settings_rand_oben_input"],
                self.app.ui["settings_rand_unten_input"],
                self.app.ui["settings_rand_links_input"],
                self.app.ui["settings_rand_rechts_input"],
                ft.Divider(),
                ft.Text(_("Datensicherung"),
                        weight=ft.FontWeight.BOLD, size=11),
                ft.ElevatedButton(
                    _("📤 Export zu Documents", BFSIZE),
                    on_click=self.app.exportiere_zu_downloads,
                    expand=True,
                    style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
                ),
                ft.ElevatedButton(
                    _("📥 Import von Documents", BFSIZE),
                    on_click=self.app.importiere_von_downloads,
                    expand=True,
                    style=ft.ButtonStyle(text_style=ft.TextStyle(size=BFSIZE2))
                ),
                ft.Text(
                    _("Erstellt: Verteiler_Daten.json & Verteiler_Einstellungen.json"),
                    size=8,
                ),
            ],
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )


if __name__ == "__main__":
    pass
