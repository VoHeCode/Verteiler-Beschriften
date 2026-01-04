"""
Datums-Hilfsfunktionen für die Ausrüstungsverwaltung.

Dieses Modul enthält alle Funktionen zur Verarbeitung von Datumsangaben:
- parse_date_input: Parst verschiedene Datumsformate nach ISO (YYYY-MM-DD)
- format_date_display: Formatiert ISO-Datum für Anzeige
"""

import re
from datetime import datetime

def parse_date_input(date_str: str) -> str:
    """
    Parst verschiedene Datumsformate in ISO-Format (YYYY-MM-DD).

    Unterstützte Formate:
    - ISO: 2024-12-31, 2024-12, 2024
    - Deutsch: 31.12.2024, 12.2024, 2024
    - Kurz: 24.12.31, 24-12-31
    - Mit Punkten: 2024.12.31, 2024.12
    - Mit Monatsnamen: 2024-Dec, Dez. 2024, dec 2024

    Fehlende Werte werden mit 01 gesetzt:
    - 03.2024 → 2024-03-01
    - 2024 → 2024-01-01
    - REPARATUR: 2024-00-01 → 2024-01-01 (alte Bugs)
    """
    if not date_str:
        return ""

    date_str = date_str.strip()
    if not date_str:
        return ""

    # REPARATUR: Behebe alte Bugs mit Monat 00
    if re.match(r'^\d{4}-00-\d{1,2}$', date_str):
        parts = date_str.split('-')
        year, day = parts[0], parts[2]
        date_str = f"{year}-01-{day}"

    # Monatsnamen-Mapping (Deutsch und Englisch)
    month_names_de = {  # Deutsch
        'jan': '01', 'januar': '01', 'feb': '02', 'februar': '02', 'mär': '03', 'märz': '03', 'maerz': '03',
        'apr': '04', 'april': '04', 'mai': '05', 'jun': '06', 'juni': '06', 'jul': '07', 'juli': '07', 'aug': '08',
        'august': '08', 'sep': '09', 'september': '09', 'okt': '10', 'oktober': '10', 'nov': '11', 'november': '11',
        'dez': '12', 'dezember': '12', }
    # Englisch
    month_names_en = {'jan': '01', 'january': '01', 'feb': '02', 'february': '02', 'mar': '03', 'march': '03',
                      'apr': '04', 'april': '04', 'may': '05', 'jun': '06', 'june': '06', 'jul': '07', 'july': '07',
                      'aug': '08',
                      'august': '08', 'sep': '09', 'september': '09', 'oct': '10', 'october': '10', 'nov': '11',
                      'november': '11',
                      'dec': '12', 'december': '12', }

    original_input = date_str
    date_str_lower = date_str.lower()

    # Monatsnamen durch Nummern ersetzen
    for month_name, month_num in month_names_de.items():
        if month_name in date_str_lower:
            # Entferne Punkte und ersetze Monatsnamen
            date_str_lower = date_str_lower.replace('.', ' ').replace('-', ' ')
            date_str_lower = date_str_lower.replace(month_name, month_num)
            date_str = date_str_lower
            break
    for month_name, month_num in month_names_en.items():
        if month_name in date_str_lower:
            # Entferne Punkte und ersetze Monatsnamen
            date_str_lower = date_str_lower.replace('.', ' ').replace('-', ' ')
            date_str_lower = date_str_lower.replace(month_name, month_num)
            date_str = date_str_lower
            break

    # Normalisiere Trennzeichen (auch / zu -)
    date_str = date_str.replace('.', '-').replace('/', '-').strip()

    # Entferne mehrfache Leerzeichen
    date_str = ' '.join(date_str.split())

    try:
        # Format 1: Vollständiges Datum (YYYY-MM-DD oder DD-MM-YYYY oder MM-DD-YYYY)
        if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', date_str):
            # YYYY-MM-DD
            parts = date_str.split('-')
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])

            # Validierung und Auto-Korrektur
            if month == 0:
                month = 1
            if day == 0:
                day = 1

            return datetime(year, month, day).strftime('%Y-%m-%d')

        elif re.match(r'^\d{1,2}-\d{1,2}-\d{4}$', date_str):
            # Kann DD-MM-YYYY oder MM-DD-YYYY sein
            parts = date_str.split('-')
            first, second, year = int(parts[0]), int(parts[1]), int(parts[2])

            # Heuristik: Wenn first > 12, dann ist es DD-MM-YYYY
            # Sonst versuchen wir MM-DD-YYYY (amerikanisches Format)
            if first > 12:
                # Definitiv DD-MM-YYYY
                day, month = first, second
            elif second > 12:
                # Definitiv MM-DD-YYYY
                month, day = first, second
            else:
                # Mehrdeutig - Standard für Deutschland: DD-MM-YYYY
                # Punkte (1.5.2022) werden immer als Tag.Monat.Jahr interpretiert
                day, month = first, second

            # Validierung und Auto-Korrektur
            if month == 0:
                month = 1
            if day == 0:
                day = 1

            return datetime(year, month, day).strftime('%Y-%m-%d')

        # Format 2: Kurzes Jahr (YY-MM-DD oder DD-MM-YY)
        elif re.match(r'^\d{1,2}-\d{1,2}-\d{2}$', date_str):
            parts = date_str.split('-')
            first, second, third = int(parts[0]), int(parts[1]), int(parts[2])

            # Heuristik zur Bestimmung des Formats
            # DD-MM-YY wenn:
            # - first > 12 (definitiv ein Tag)
            # - ODER second < 12 UND third könnte ein Jahr sein (typischerweise DD-MM-YY in Europa)

            if first > 12:
                # Definitiv DD-MM-YY (Tag > 12)
                day, month, year = first, second, third
            elif second > 12:
                # Definitiv YY-MM-DD (Monat > 12 nicht möglich, also ist second der Tag)
                year, month, day = first, second, third
            else:
                # Mehrdeutig: Könnte DD-MM-YY oder YY-MM-DD sein
                # Da wir aus Deutschland kommen, nehmen wir DD-MM-YY an
                day, month, year = first, second, third

            # 2-stelliges Jahr zu 4-stellig (20YY wenn YY < 50, sonst 19YY)
            if year < 100:
                year = 2000 + year if year < 50 else 1900 + year

            # Validierung und Auto-Korrektur
            if month == 0:
                month = 1
            if day == 0:
                day = 1

            return datetime(year, month, day).strftime('%Y-%m-%d')

        # Format 3: Jahr und Monat (YYYY-MM oder MM-YYYY)
        elif re.match(r'^\d{4}-\d{1,2}$', date_str):
            # YYYY-MM
            parts = date_str.split('-')
            year, month = int(parts[0]), int(parts[1])

            # Validierung und Auto-Korrektur
            if month == 0:
                month = 1

            return datetime(year, month, 1).strftime('%Y-%m-%d')

        elif re.match(r'^\d{1,2}-\d{4}$', date_str):
            # MM-YYYY
            parts = date_str.split('-')
            month, year = int(parts[0]), int(parts[1])

            # Validierung und Auto-Korrektur
            if month == 0:
                month = 1

            return datetime(year, month, 1).strftime('%Y-%m-%d')

        # Format 4: Nur Jahr (YYYY)
        elif re.match(r'^\d{4}$', date_str):
            year = int(date_str)
            return datetime(year, 1, 1).strftime('%Y-%m-%d')

        # Format 5: Monatsnamen mit Jahr (z.B. "12 2024" nach Ersetzung)
        elif re.match(r'^\d{1,2}\s+\d{4}$', date_str):
            # MM YYYY
            parts = date_str.split()
            month, year = int(parts[0]), int(parts[1])

            # Validierung und Auto-Korrektur
            if month == 0:
                month = 1

            return datetime(year, month, 1).strftime('%Y-%m-%d')

        elif re.match(r'^\d{4}\s+\d{1,2}$', date_str):
            # YYYY MM
            parts = date_str.split()
            year, month = int(parts[0]), int(parts[1])

            # Validierung und Auto-Korrektur
            if month == 0:
                month = 1

            return datetime(year, month, 1).strftime('%Y-%m-%d')

    except (ValueError, IndexError) as e:
        return original_input

    # Wenn nichts passt, Original zurückgeben
    return original_input


def format_date_display(iso_date: str, format_type: str = 'ISO') -> str:
    """
    Formatiert ein ISO-Datum (YYYY-MM-DD) für die Anzeige.

    Args:
        iso_date: Datum im ISO-Format (YYYY-MM-DD)
        format_type: 'ISO', 'DE' (Deutsch), 'EN' (Englisch), 'SHORT' (Kurz)

    Returns:
        Formatiertes Datum als String
    """
    if not iso_date or iso_date.strip() == "":
        return ""

    try:
        # Parse ISO-Datum
        dt = datetime.strptime(iso_date.strip(), '%Y-%m-%d')

        if format_type == 'ISO':
            return dt.strftime('%Y-%m-%d')
        elif format_type == 'DE':
            return dt.strftime('%d.%m.%Y')
        elif format_type == 'EN':
            return dt.strftime('%m/%d/%Y')
        elif format_type == 'SHORT':
            return dt.strftime('%d.%m.%y')
        else:
            return iso_date
    except ValueError:
        # Wenn Parsing fehlschlägt, Original zurückgeben
        return iso_date
