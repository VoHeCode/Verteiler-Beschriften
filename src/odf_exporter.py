#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ODF-Export-Modul.

Enthält die komplette Logik für den Export von Anlagen in ODS-Format
(OpenDocument Spreadsheet) und Kunden in ODT-Format (OpenDocument Text).
Nutzt manuelle ZIP+XML Erstellung für alle Plattformen.
"""

import os
import re
from datetime import datetime
from pathlib import Path

# Manuelle ODS/ODT-Erstellung
from ods_manual import create_ods_manual
from odt_manual import create_odt_manual

from constants import COLUMNS_PER_UNIT, _


def convert_anlage_to_manual_format(anlage, gueltige_eintraege, felder, reihen):
    """Konvertiert Anlagen-Daten in Format für manuelle ODS-Erstellung.
    
    Args:
        anlage: Anlage Dictionary
        gueltige_eintraege: Liste gültiger Beschriftungen
        felder: Anzahl Felder
        reihen: Anzahl Reihen
    
    Returns:
        dict: Daten im Format für create_ods_manual
    """
    # Spalten-Map erstellen
    spalten_map = {}
    for beschr in gueltige_eintraege:
        spalten_map[beschr['spalten_liste'][0]] = {
            'beschreibung': beschr['beschreibung'],
            'anzahl': len(beschr['spalten_liste'])
        }
    
    rows = []
    globale_spalten_start = 1
    
    # Felder und Reihen durchlaufen
    for feld in range(1, felder + 1):
        for reihe in range(1, reihen + 1):
            # Beschriftungszeile (Spaltennummern)
            beschr_cells = []
            temp_spalte_nr = globale_spalten_start
            
            for i in range(COLUMNS_PER_UNIT):
                beschr_cells.append({
                    'text': str(temp_spalte_nr + i),
                    'style': 'ce1',
                    'colspan': 1
                })
            
            rows.append({
                'is_header': True,
                'cells': beschr_cells
            })
            
            # Inhaltszeile (Beschriftungen)
            inhalt_cells = []
            lokale_spalten_zaehler = 0
            
            while lokale_spalten_zaehler < COLUMNS_PER_UNIT:
                globale_spalten_nr = globale_spalten_start + lokale_spalten_zaehler
                
                if globale_spalten_nr in spalten_map:
                    eintrag = spalten_map[globale_spalten_nr]
                    anzahl = eintrag['anzahl']
                    anzahl_in_reihe = min(
                        anzahl,
                        COLUMNS_PER_UNIT - lokale_spalten_zaehler
                    )
                    
                    inhalt_cells.append({
                        'text': eintrag['beschreibung'],
                        'style': 'ce2',
                        'colspan': anzahl_in_reihe
                    })
                    
                    lokale_spalten_zaehler += anzahl_in_reihe
                else:
                    inhalt_cells.append({
                        'text': '',
                        'style': 'ce3',
                        'colspan': 1
                    })
                    lokale_spalten_zaehler += 1
            
            rows.append({
                'is_header': False,
                'cells': inhalt_cells
            })
            
            globale_spalten_start += COLUMNS_PER_UNIT
    
    return {
        'name': anlage['beschreibung'],
        'num_cols': COLUMNS_PER_UNIT,
        'rows': rows
    }


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
                belegte_spalten: set, max_spalten: int, fehler_details: list)
    """
    max_spalten = felder * reihen * COLUMNS_PER_UNIT
    belegte_spalten = set()
    fehler_anzahl = 0
    gueltige_eintraege = []
    fehler_details = []

    for zeilen_nr, zeile in enumerate(text_inhalt.split('\n'), 1):
        if not zeile.strip():
            continue

        parsed = parse_zeile(zeile)
        if not parsed:
            fehler_anzahl += 1
            fehler_details.append(_('{zeile} - Ungültiges Format').format(zeile=f'"{zeile.strip()}"'))
            continue

        spalten = parse_spalten(parsed['spalten'])
        if not spalten:
            fehler_anzahl += 1
            fehler_details.append(_('{zeile} - Spalten nicht erkennbar').format(zeile=f'"{zeile.strip()}"'))
            continue

        # Prüfe ob Spalten außerhalb des Bereichs
        ungueltige = [s for s in spalten if s < 1 or s > max_spalten]
        if ungueltige:
            fehler_anzahl += 1
            fehler_details.append(_('{zeile} - Spalte(n) {spalten} außerhalb Bereich (1-{max})').format(
                zeile=f'"{zeile.strip()}"',
                spalten=ungueltige,
                max=max_spalten
            ))
            continue

        # Prüfe auf Doppelbelegung
        doppelt = [s for s in spalten if s in belegte_spalten]
        if doppelt:
            fehler_anzahl += 1
            fehler_details.append(_('{zeile} - Spalte(n) {spalten} bereits belegt').format(
                zeile=f'"{zeile.strip()}"',
                spalten=doppelt
            ))
            continue

        for s in spalten:
            belegte_spalten.add(s)

        gueltige_eintraege.append({
            'spalten_liste': spalten,
            'beschreibung': parsed['beschreibung'],
            'spalten_str': parsed['spalten']
        })

    is_valid = (fehler_anzahl == 0)
    return is_valid, gueltige_eintraege, fehler_anzahl, belegte_spalten, max_spalten, fehler_details



def exportiere_anlage_ods_manual(anlage, settings, export_base_path, kundenname, projekt=''):
    """Exportiert eine Anlage als ODS-Datei manuell (Android).

    Args:
        anlage (dict): Anlagen-Dictionary mit allen Daten
        settings (dict): Settings-Dictionary
        export_base_path (Path): Basis-Pfad für Export-Verzeichnis
        kundenname (str): Name des Kunden für Unterordner
        projekt (str): Projekt-Name für Fußzeile

    Returns:
        Path: Pfad zur exportierten Datei

    Raises:
        ValueError: Wenn Anlage ungültig ist oder keine Einträge vorhanden
    """
    # Validierung
    if not anlage:
        raise ValueError(_('Keine Anlage zum Exportieren vorhanden.'))

    felder = anlage.get('felder', 3)
    reihen = anlage.get('reihen', 7)
    text_inhalt = anlage.get('text_inhalt', '')

    is_valid, gueltige_eintraege, fehler_anzahl, _, _, _ = validiere_eintraege(
        text_inhalt, felder, reihen
    )

    if not is_valid:
        raise ValueError(_(
            'Die Anlage enthält fehlerhafte Beschriftungen. '
            'Bitte beheben Sie die Fehler vor dem Export.'
        ))

    if not gueltige_eintraege:
        raise ValueError(_('Keine gültigen Beschriftungen zum Exportieren gefunden!'))

    # Sortiere nach erster Spalte
    gueltige_eintraege.sort(key=lambda x: x['spalten_liste'][0])

    # Konvertiere Daten
    data = convert_anlage_to_manual_format(anlage, gueltige_eintraege, felder, reihen)

    # Speichern
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    anlage_id = anlage.get("id", "0")
    dateiname = f'Kunde_{kundenname.replace(" ", "_")}_Anlage_{anlage_id}_{timestamp}.ods'
    export_pfad = Path(export_base_path) / kundenname / dateiname
    os.makedirs(export_pfad.parent, exist_ok=True)

    # Fußzeilen-Daten
    footer_data = {
        'filepath': str(export_pfad),
        'customer': kundenname,
        'project': projekt,
        'code': anlage.get('code', ''),
        'description': anlage.get('beschreibung', '')
    }

    # Erstelle ODS manuell
    create_ods_manual(data, settings, str(export_pfad), footer_data)

    return export_pfad


def exportiere_anlage_ods(anlage, settings, export_base_path, kundenname, projekt=''):
    """Exportiert eine Anlage als ODS-Datei.

    Args:
        anlage (dict): Anlagen-Dictionary mit allen Daten
        settings (dict): Settings-Dictionary
        export_base_path (Path): Basis-Pfad für Export-Verzeichnis
        kundenname (str): Name des Kunden für Unterordner
        projekt (str): Projekt-Name für Fußzeile

    Returns:
        Path: Pfad zur exportierten Datei

    Raises:
        ValueError: Wenn Anlage ungültig ist oder keine Einträge vorhanden
    """
    return exportiere_anlage_ods_manual(anlage, settings, export_base_path, kundenname, projekt)


def exportiere_kunde_odt_manual(kunde, kundenname, export_base_path):
    """Exportiert alle Daten eines Kunden als ODT-Datei manuell (Android).

    Args:
        kunde (dict): Kunden-Dictionary mit allen Daten
        kundenname (str): Name des Kunden
        export_base_path (Path): Basis-Pfad für Export-Verzeichnis

    Returns:
        Path: Pfad zur exportierten Datei

    Raises:
        ValueError: Wenn Kunde ungültig ist
    """
    if not kunde:
        raise ValueError(_('Kein Kunde zum Exportieren vorhanden.'))
    
    # Konvertiere Kunde für manuelle ODT-Erstellung
    kunde_data = {
        'kundenname': kundenname,
        'projekt': kunde.get('projekt', ''),
        'datum': kunde.get('datum', ''),
        'adresse': kunde.get('adresse', ''),
        'plz': kunde.get('plz', ''),
        'ort': kunde.get('ort', ''),
        'ansprechpartner': kunde.get('ansprechpartner', ''),
        'telefonnummer': kunde.get('telefonnummer', ''),
        'email': kunde.get('email', ''),
        'anlagen': kunde.get('anlagen', [])
    }
    
    # Speichern
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dateiname = f'Kunde_{kundenname.replace(" ", "_")}_{timestamp}.odt'
    export_pfad = Path(export_base_path) / kundenname / dateiname
    os.makedirs(export_pfad.parent, exist_ok=True)
    
    # Erstelle ODT manuell
    create_odt_manual(kunde_data, str(export_pfad))
    
    return export_pfad


def exportiere_kunde_odt(kunde, kundenname, export_base_path):
    """Exportiert alle Daten eines Kunden als ODT-Datei.

    Args:
        kunde (dict): Kunden-Dictionary mit allen Daten
        kundenname (str): Name des Kunden
        export_base_path (Path): Basis-Pfad für Export-Verzeichnis

    Returns:
        Path: Pfad zur exportierten Datei

    Raises:
        ValueError: Wenn Kunde ungültig ist
    """
    return exportiere_kunde_odt_manual(kunde, kundenname, export_base_path)


if __name__ == "__main__":
    pass
