#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Konstanten und Konfiguration für die Anlagen-App."""

from translator import TranslationSystem

# SYNC WITH pyproject.toml [tool.flet]
TOOL_FLET_NAME = "Verteiler_Beschriften"
TOOL_FLET_VERSION = "3.0.0"
TOOL_FLET_DESCRIPTION = "Anlagen Eingabe und Verteiler-Beschriftung"

# App-ID für Android Package
APP_ID = "com.vohegg.verteiler_beschriften"

# Dateinamen
DATA_FILENAME = 'Verteiler_Daten.json'
SETTINGS_FILENAME = 'Verteiler_Einstellungen.json'

# Internationalization (i18n)
# def _(astring, size=14)->str:
#     # a dummy function for later translation
#     return astring
ts = TranslationSystem("de_DE")
_ = ts.tr
#ts.run_tr_extractor_ui()# comment this after each settig
#exit() # comment this after each settig


# Button Font Sizes
BFSIZE = 14
BFSIZE2 = BFSIZE

# Layout-Konstanten
COLUMNS_PER_UNIT = 12

# Standard-Einstellungen (als Referenz für neue Installationen)
DEFAULT_SETTINGS = {
    'default_felder': 3,
    'default_reihen': 7,
    'fontsize_gemergte_zelle': 7,
    'fontsize_beschriftung_zelle': 7,
    'fontsize_inhalt_zelle': 6,
    'spalten_breite': 1.75,  # in cm
    'beschriftung_row_hoehe': 0.5,  # in cm
    'inhalt_row_hoehe': 1.5,  # in cm
    'zellen_umrandung': True,  # Umrandung aktiviert
    'linebreak_char': ';',  # Zeichen für neue Zeile (max 3 Zeichen)
    'selected_locale': 'de_DE',  # Standard-Sprache
    # Page Layout Einstellungen
    'seite_breite': 29.7,  # A4 Querformat Breite in cm
    'seite_hoehe': 21.0,  # A4 Querformat Höhe in cm
    'rand_oben': 2.0,  # in cm
    'rand_unten': 1.5,  # in cm
    'rand_links': 1.0,  # in cm
    'rand_rechts': 1.0  # in cm
}

# Android Request Codes
CREATE_FILE_REQUEST = 1


if __name__ == "__main__":
    pass
