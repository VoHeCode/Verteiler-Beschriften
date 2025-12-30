#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validierungs- und Formatierungsfunktionen."""

import re
from datetime import datetime


def extrahiere_dimension(text):
    """Extrahiert Felder x Reihen aus Text wie '3x7' oder '3 x 7'.

    Args:
        text (str): Text mit Dimensionsangabe

    Returns:
        tuple: (felder, reihen) oder (None, None) wenn nicht gefunden
    """
    match = re.search(r'(\d+)\s*x\s*(\d+)', text.lower())
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None


def formatiere_datum(datum_str=None):
    """Formatiert ein Datum im Format YYYY-MM-DD.

    Args:
        datum_str (str, optional): Datum als String.
            Wenn None, wird heutiges Datum verwendet.

    Returns:
        str: Formatiertes Datum
    """
    if datum_str is None:
        return datetime.now().date().strftime('%Y-%m-%d')

    # Kein äußeres try mehr!
    for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']:
        try:
            datum_obj = datetime.strptime(datum_str, fmt)
            return datum_obj.strftime('%Y-%m-%d')
        except ValueError:
            continue
    return datum_str


def validiere_integer(wert, min_wert=1, max_wert=100, default=1):
    """Validiert und konvertiert einen Wert zu Integer.

    Args:
        wert: Wert zum Validieren
        min_wert (int): Minimalwert
        max_wert (int): Maximalwert
        default (int): Standardwert bei Fehler

    Returns:
        int: Validierter Integer-Wert
    """
    try:
        zahl = int(wert)
        if min_wert <= zahl <= max_wert:
            return zahl
        return default
    except (ValueError, TypeError):
        return default


def validiere_float(wert, min_wert=0.0, max_wert=100.0, default=1.0):
    """Validiert und konvertiert einen Wert zu Float.

    Args:
        wert: Wert zum Validieren
        min_wert (float): Minimalwert
        max_wert (float): Maximalwert
        default (float): Standardwert bei Fehler

    Returns:
        float: Validierter Float-Wert
    """
    try:
        # Ersetze Komma durch Punkt für deutsche Eingaben
        if isinstance(wert, str):
            wert = wert.replace(',', '.')
        
        zahl = float(wert)
        if min_wert <= zahl <= max_wert:
            return zahl
        return default
    except (ValueError, TypeError):
        return default


def bereinige_text(text):
    """Bereinigt Text von führenden/trailing Leerzeichen.

    Args:
        text: Text zum Bereinigen

    Returns:
        str: Bereinigter Text
    """
    if text is None:
        return ""
    return str(text).strip()


def ist_gueltige_email(email):
    """Prüft ob eine E-Mail-Adresse gültig aussieht.

    Args:
        email (str): E-Mail-Adresse

    Returns:
        bool: True wenn gültig
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def formatiere_telefonnummer(nummer):
    """Formatiert eine Telefonnummer (einfache Formatierung).

    Args:
        nummer (str): Telefonnummer

    Returns:
        str: Formatierte Telefonnummer
    """
    if not nummer:
        return ""
    
    # Entferne alle nicht-numerischen Zeichen außer +
    nummer = re.sub(r'[^\d+]', '', nummer)
    return nummer
