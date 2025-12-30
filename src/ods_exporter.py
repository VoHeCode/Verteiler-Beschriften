#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ODS-Export-Modul.

Enthält die komplette Logik für den Export von Anlagen in ODS-Format
(OpenDocument Spreadsheet).
"""

import os
import re
from datetime import datetime
from pathlib import Path

from odf.opendocument import OpenDocumentSpreadsheet
from odf.table import Table, TableRow, TableCell, TableColumn, CoveredTableCell
from odf.text import P
from odf.style import (
    Style,
    TableColumnProperties,
    TableRowProperties,
    TableCellProperties,
    TextProperties,
    ParagraphProperties,
    PageLayout,
    PageLayoutProperties,
    MasterPage
)

from constants import SPALTEN_PRO_EINHEIT


def parse_zeile(zeile):
    """Parsed eine Eingabezeile im Format 'Spalten Beschreibung'.

    Unterstützte Formate:
    - "1 Heizung" → Spalte 1
    - "3-6 Lüftung" → Spalten 3 bis 6
    - "7+5 Elektrik" → Spalten 7 bis 12 (7 plus 5 weitere)

    Args:
        zeile (str): Eingabezeile

    Returns:
        dict: {'spalten': str, 'beschreibung': str} oder None bei Fehler
    """
    zeile = zeile.strip()
    if not zeile:
        return None

    # Erlaubt nur Ziffern, Bindestriche und Pluszeichen in der Spaltenangabe
    match = re.match(r'([\d\-\+]+)[\s\t;]*(.*)', zeile)
    if match:
        spalten_str = match.group(1).strip()
        beschreibung = match.group(2).strip()
        if spalten_str:
            return {'spalten': spalten_str, 'beschreibung': beschreibung}

    return None


def parse_spalten(spalten_str):
    """Konvertiert Spalten-String zu Liste von Spaltennummern.

    Args:
        spalten_str (str): Spalten-String (z.B. "1", "3-6", "7+5")

    Returns:
        list: Liste von Spaltennummern oder None bei Fehler
    """
    try:
        if '+' in spalten_str:
            start, anzahl = map(int, spalten_str.split('+'))
            # Bei 'X+Y' soll X bis X+Y gehen, also Y+1 Zahlen
            return list(range(start, start + anzahl + 1))
        elif '-' in spalten_str:
            start, ende = map(int, spalten_str.split('-'))
            return list(range(start, ende + 1)) if start <= ende else None
        else:
            return [int(spalten_str)]
    except (ValueError, AttributeError):
        return None


def validiere_eintraege(text_inhalt, felder, reihen):
    """Validiert die Einträge und prüft auf Fehler.

    Args:
        text_inhalt (str): Text mit allen Einträgen (zeilenweise)
        felder (int): Anzahl Felder
        reihen (int): Anzahl Reihen

    Returns:
        tuple: (is_valid: bool, gueltige_eintraege: list, fehler_anzahl: int,
                belegte_spalten: set, max_spalten: int)
    """
    max_spalten = felder * reihen * SPALTEN_PRO_EINHEIT
    belegte_spalten = set()
    fehler_anzahl = 0
    gueltige_eintraege = []

    for zeilen_nr, zeile in enumerate(text_inhalt.split('\n'), 1):
        if not zeile.strip():
            continue

        parsed = parse_zeile(zeile)
        if not parsed:
            fehler_anzahl += 1
            continue

        spalten = parse_spalten(parsed['spalten'])
        if not spalten:
            fehler_anzahl += 1
            continue

        if any(s < 1 or s > max_spalten for s in spalten):
            fehler_anzahl += 1
            continue

        if any(s in belegte_spalten for s in spalten):
            fehler_anzahl += 1
            continue

        for s in spalten:
            belegte_spalten.add(s)

        gueltige_eintraege.append({
            'spalten_liste': spalten,
            'beschreibung': parsed['beschreibung'],
            'spalten_str': parsed['spalten']
        })

    is_valid = (fehler_anzahl == 0)
    return is_valid, gueltige_eintraege, fehler_anzahl, belegte_spalten, max_spalten


def erstelle_ods_styles(doc, settings):
    """Erstellt alle Styles für das ODS-Dokument.

    Args:
        doc: OpenDocumentSpreadsheet Objekt
        settings (dict): Settings-Dictionary mit Formatierungsoptionen

    Returns:
        tuple: (spalten_style, beschr_row_style, inhalt_row_style)
    """
    # ============ PAGE LAYOUT: A4 Querformat mit konfigurierbaren Rändern ============
    page_layout = PageLayout(name="PageLayout1")
    page_layout_props = PageLayoutProperties(
        pagewidth=f"{settings['seite_breite']}cm",
        pageheight=f"{settings['seite_hoehe']}cm",
        margintop=f"{settings['rand_oben']}cm",
        marginbottom=f"{settings['rand_unten']}cm",
        marginleft=f"{settings['rand_links']}cm",
        marginright=f"{settings['rand_rechts']}cm",
        printorientation="landscape"
    )
    page_layout.addElement(page_layout_props)
    doc.automaticstyles.addElement(page_layout)

    # Master Page mit dem Page-Layout verknüpfen
    master_page = MasterPage(name="Default", pagelayoutname="PageLayout1")
    doc.masterstyles.addElement(master_page)

    # ============ STYLES mit konfigurierbaren Werten aus Settings ============

    # Spaltenbreite aus Settings
    spalten_style = Style(name="SpaltenBreite", family="table-column")
    spalten_style.addElement(
        TableColumnProperties(columnwidth=f"{settings['spalten_breite']}cm")
    )
    doc.automaticstyles.addElement(spalten_style)

    # Beschriftungszeile Höhe aus Settings
    beschr_row_style = Style(name="BeschriftungRow", family="table-row")
    beschr_row_style.addElement(
        TableRowProperties(rowheight=f"{settings['beschriftung_row_hoehe']}cm")
    )
    doc.automaticstyles.addElement(beschr_row_style)

    # Inhaltszeile Höhe aus Settings
    inhalt_row_style = Style(name="InhaltRow", family="table-row")
    inhalt_row_style.addElement(
        TableRowProperties(rowheight=f"{settings['inhalt_row_hoehe']}cm")
    )
    doc.automaticstyles.addElement(inhalt_row_style)

    # Border-Eigenschaften (wenn aktiviert)
    border_enabled = settings.get('zellen_umrandung', True)

    # Gemergte Zelle - Font aus Settings + Optional Border
    merged_cell_style = Style(name="GemergteZelle", family="table-cell")
    merged_cell_style.addElement(TextProperties(
        fontsize=f"{settings['fontsize_gemergte_zelle']}pt",
        fontweight="bold"
    ))
    merged_cell_style.addElement(ParagraphProperties(textalign="center"))
    cell_props_merged = TableCellProperties(verticalalign="top", wrapoption="wrap")
    if border_enabled:
        cell_props_merged.setAttribute('border', '0.5pt solid #000000')
    merged_cell_style.addElement(cell_props_merged)
    doc.styles.addElement(merged_cell_style)

    # Beschriftung Zelle - Font aus Settings + Optional Border
    beschr_cell_style = Style(name="BeschriftungZelle", family="table-cell")
    beschr_cell_style.addElement(TextProperties(
        fontsize=f"{settings['fontsize_beschriftung_zelle']}pt",
        fontweight="bold"
    ))
    beschr_cell_style.addElement(ParagraphProperties(textalign="center"))
    cell_props_beschr = TableCellProperties(verticalalign="top", wrapoption="wrap")
    if border_enabled:
        cell_props_beschr.setAttribute('border', '0.5pt solid #000000')
    beschr_cell_style.addElement(cell_props_beschr)
    doc.styles.addElement(beschr_cell_style)

    # Inhalt Zelle - Font aus Settings + Optional Border
    inhalt_cell_style = Style(name="InhaltZelle", family="table-cell")
    inhalt_cell_style.addElement(TextProperties(
        fontsize=f"{settings['fontsize_inhalt_zelle']}pt"
    ))
    inhalt_cell_style.addElement(ParagraphProperties(textalign="center"))
    cell_props_inhalt = TableCellProperties(verticalalign="top", wrapoption="wrap")
    if border_enabled:
        cell_props_inhalt.setAttribute('border', '0.5pt solid #000000')
    inhalt_cell_style.addElement(cell_props_inhalt)
    doc.styles.addElement(inhalt_cell_style)

    # Header bleibt bei 10pt (nicht konfigurierbar)
    header_cell_style = Style(name="HeaderCell", family="table-cell")
    header_cell_style.addElement(TextProperties(fontsize="10pt", fontweight="bold"))
    header_cell_style.addElement(ParagraphProperties(textalign="center"))
    doc.styles.addElement(header_cell_style)

    # Table Style mit masterpagename
    table_style = Style(name="MainTable", family="table")
    table_style.setAttribute('masterpagename', 'Default')
    doc.automaticstyles.addElement(table_style)

    return spalten_style, beschr_row_style, inhalt_row_style


def exportiere_anlage_ods(anlage, settings, export_base_path):
    """Exportiert eine Anlage als ODS-Datei.

    Args:
        anlage (dict): Anlagen-Dictionary mit allen Daten
        settings (dict): Settings-Dictionary
        export_base_path (Path): Basis-Pfad für Export-Verzeichnis

    Returns:
        Path: Pfad zur exportierten Datei

    Raises:
        ValueError: Wenn Anlage ungültig ist oder keine Einträge vorhanden
    """
    # Validierung
    if not anlage:
        raise ValueError('Keine Anlage zum Exportieren vorhanden.')

    felder = anlage.get('felder', 3)
    reihen = anlage.get('reihen', 7)
    text_inhalt = anlage.get('text_inhalt', '')

    is_valid, gueltige_eintraege, fehler_anzahl, _, _ = validiere_eintraege(
        text_inhalt, felder, reihen
    )

    if not is_valid:
        raise ValueError(
            'Die Anlage enthält fehlerhafte Beschriftungen. '
            'Bitte beheben Sie die Fehler vor dem Export.'
        )

    if not gueltige_eintraege:
        raise ValueError('Keine gültigen Beschriftungen zum Exportieren gefunden!')

    # Sortiere nach erster Spalte
    gueltige_eintraege.sort(key=lambda x: x['spalten_liste'][0])

    # Erstelle ODS-Dokument
    doc = OpenDocumentSpreadsheet()

    # Styles erstellen
    spalten_style, beschr_row_style, inhalt_row_style = erstelle_ods_styles(
        doc, settings
    )

    # ============ TABELLEN-LOGIK ============
    table = Table(name=anlage['beschreibung'], stylename="MainTable")

    # Spalten definieren
    for i in range(SPALTEN_PRO_EINHEIT):
        table.addElement(TableColumn(stylename=spalten_style))

    # Spalten-Map erstellen
    spalten_map = {}
    for beschr in gueltige_eintraege:
        spalten_map[beschr['spalten_liste'][0]] = {
            'beschreibung': beschr['beschreibung'],
            'anzahl': len(beschr['spalten_liste'])
        }

    globale_spalten_start = 1

    # Felder und Reihen durchlaufen
    for feld in range(1, felder + 1):
        for reihe in range(1, reihen + 1):
            # Beschriftungszeile (Spaltennummern)
            beschr_row = TableRow(stylename=beschr_row_style)
            temp_spalte_nr = globale_spalten_start

            for i in range(SPALTEN_PRO_EINHEIT):
                cell = TableCell(stylename="BeschriftungZelle")
                cell.addElement(P(text=str(temp_spalte_nr + i)))
                beschr_row.addElement(cell)

            table.addElement(beschr_row)

            # Inhaltszeile (Beschriftungen)
            inhalt_row = TableRow(stylename=inhalt_row_style)
            lokale_spalten_zaehler = 0

            while lokale_spalten_zaehler < SPALTEN_PRO_EINHEIT:
                globale_spalten_nr = globale_spalten_start + lokale_spalten_zaehler

                if globale_spalten_nr in spalten_map:
                    eintrag = spalten_map[globale_spalten_nr]
                    anzahl = eintrag['anzahl']
                    anzahl_in_reihe = min(
                        anzahl,
                        SPALTEN_PRO_EINHEIT - lokale_spalten_zaehler
                    )

                    cell = TableCell(
                        stylename="GemergteZelle",
                        numbercolumnsspanned=anzahl_in_reihe
                    )
                    cell.addElement(P(text=eintrag['beschreibung']))
                    inhalt_row.addElement(cell)

                    for _ in range(1, anzahl_in_reihe):
                        inhalt_row.addElement(CoveredTableCell())

                    lokale_spalten_zaehler += anzahl_in_reihe
                else:
                    cell = TableCell(stylename="InhaltZelle")
                    inhalt_row.addElement(cell)
                    lokale_spalten_zaehler += 1

            table.addElement(inhalt_row)
            globale_spalten_start += SPALTEN_PRO_EINHEIT

    doc.spreadsheet.addElement(table)

    # Speichern
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dateiname = f'{anlage["beschreibung"].replace(" ", "_")}_{timestamp}.ods'
    export_pfad = Path(export_base_path) / "Export" / dateiname
    os.makedirs(export_pfad.parent, exist_ok=True)

    doc.save(str(export_pfad))

    return export_pfad


