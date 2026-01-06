#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Platform-Handler - Vereinfacht für Flet.

Flet kümmert sich um Platform-spezifische Details.
Wir nutzen einfach normale Dateisystem-Operationen.
"""

from pathlib import Path
import shutil
from constants import EXPORT_DATA_FILE, EXPORT_SETTINGS_FILE


def exportiere_zu_downloads(data_manager):
    """Exportiert Daten und Settings zu Downloads.
    
    Args:
        data_manager: DataManager-Instanz
        
    Returns:
        tuple: (erfolg: bool, exportierte_dateien: list, fehler: str)
    """
    try:
        downloads = Path.home() / "Downloads"
        downloads.mkdir(exist_ok=True)
        
        exportierte_dateien = []
        
        # Exportiere Daten
        daten_pfad = data_manager.get_data_file_path()
        if daten_pfad.exists():
            ziel = downloads / EXPORT_DATA_FILE
            shutil.copy2(daten_pfad, ziel)
            exportierte_dateien.append(f"✓ {EXPORT_DATA_FILE}")
        
        # Exportiere Settings
        settings_pfad = data_manager.get_settings_file_path()
        if settings_pfad.exists():
            ziel = downloads / EXPORT_SETTINGS_FILE
            shutil.copy2(settings_pfad, ziel)
            exportierte_dateien.append(f"✓ {EXPORT_SETTINGS_FILE}")
        
        if not exportierte_dateien:
            return False, [], "Keine Dateien zum Exportieren gefunden"
        
        return True, exportierte_dateien, None
        
    except Exception as e:
        return False, [], f"Export-Fehler: {str(e)}"


def importiere_von_downloads(data_manager):
    """Importiert Daten und Settings von Downloads.
    
    Args:
        data_manager: DataManager-Instanz
        
    Returns:
        tuple: (erfolg: bool, importierte_dateien: list, fehler: str)
    """
    try:
        downloads = Path.home() / "Downloads"
        importierte_dateien = []
        
        # Importiere EXPORT_DATA_FILE
        daten_quelle = downloads / EXPORT_DATA_FILE
        if daten_quelle.exists():
            shutil.copy2(daten_quelle, data_manager.get_data_file_path())
            importierte_dateien.append(f"✓ {EXPORT_DATA_FILE}")
        
        # Importiere Settings
        settings_quelle = downloads / EXPORT_SETTINGS_FILE
        if settings_quelle.exists():
            shutil.copy2(settings_quelle, data_manager.get_settings_file_path())
            importierte_dateien.append(f"✓ {EXPORT_SETTINGS_FILE}")
        
        if not importierte_dateien:
            return False, [], "Keine Backup-Dateien im Downloads-Ordner gefunden"
        
        return True, importierte_dateien, None
        
    except Exception as e:
        return False, [], f"Import-Fehler: {str(e)}"
