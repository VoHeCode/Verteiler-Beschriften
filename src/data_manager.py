#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Daten- und Settings-Management.

Funktionen zum Laden, Speichern und Verwalten von Daten und Einstellungen.
"""

import json
from pathlib import Path
from constants import DEFAULT_SETTINGS, DATA_FILENAME, SETTINGS_FILENAME


class DataManager:
    """Manager für Daten- und Settings-Operationen."""

    def __init__(self, data_path):
        """Initialisiert den DataManager.

        Args:
            data_path: Pfad zum Datenverzeichnis (z.B. app.paths.data)
        """
        self.data_path = Path(data_path)
        self.settings = DEFAULT_SETTINGS.copy()

    def get_data_file_path(self):
        """Gibt den vollständigen Pfad zur Datendatei zurück.

        Returns:
            Path: Pfad zur Datendatei
        """
        result = self.data_path / DATA_FILENAME
        return result

    def get_settings_file_path(self):
        """Gibt den vollständigen Pfad zur Settings-Datei zurück.

        Returns:
            Path: Pfad zur Settings-Datei
        """
        return self.data_path / SETTINGS_FILENAME

    # ==================== Settings Management ====================

    def lade_settings(self):
        """Lädt die App-Einstellungen aus der JSON-Datei.

        Returns:
            dict: Geladene Settings oder Standard-Settings
        """
        settings_pfad = self.get_settings_file_path()

        if not settings_pfad.exists():
            return self.settings

        try:
            with open(settings_pfad, 'r', encoding='utf-8') as f:
                geladene_settings = json.load(f)

            # Aktualisiere nur vorhandene Keys
            for key, value in geladene_settings.items():
                if key in self.settings:
                    self.settings[key] = value

            return self.settings

        except Exception as e:
            return self.settings

    def speichere_settings(self, settings=None):
        """Speichert die App-Einstellungen in eine JSON-Datei.

        Args:
            settings (dict, optional): Settings zum Speichern.
                Wenn None, werden self.settings verwendet.

        Returns:
            tuple: (erfolg: bool, fehler_nachricht: str oder None)
        """
        if settings is not None:
            self.settings = settings

        settings_pfad = self.get_settings_file_path()

        try:
            settings_pfad.parent.mkdir(parents=True, exist_ok=True)
            with open(settings_pfad, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)  # type: ignore[arg-type]

            return True, None

        except Exception as e:
            return False, str(e)

    # ==================== Daten Management ====================

    def lade_daten(self):
        """Lädt alle Kundendaten aus der JSON-Datei.

        Returns:
            tuple: (alle_kunden: dict, next_kunden_id: int)
        """
        daten_pfad = self.get_data_file_path()

        if not daten_pfad.exists():
            return {}, 1

        try:
            with open(daten_pfad, 'r', encoding='utf-8') as f:
                alle_daten = json.load(f)
            

            alle_kunden = alle_daten.get('kunden', {})
            next_kunden_id = alle_daten.get('next_kunden_id', 1)
            
            # Migration: Füge next_anlage_id zu alten Kunden hinzu falls nicht vorhanden
            for kunde_data in alle_kunden.values():
                if 'next_anlage_id' not in kunde_data:
                    # Finde höchste Anlagen-ID + 1
                    max_id = max((a.get('id', 0) for a in kunde_data.get('anlagen', [])), default=0)
                    kunde_data['next_anlage_id'] = max_id + 1

            return alle_kunden, next_kunden_id

        except Exception as e:
            return {}, 1

    def speichere_daten(self, alle_kunden, next_kunden_id):
        """Speichert alle Kundendaten in die JSON-Datei.

        Args:
            alle_kunden (dict): Dictionary mit allen Kundendaten
            next_kunden_id (int): Nächste freie Kunden-ID

        Returns:
            tuple: (erfolg: bool, fehler_nachricht: str oder None)
        """
        daten_pfad = self.get_data_file_path()

        try:
            daten_pfad.parent.mkdir(parents=True, exist_ok=True)

            alle_daten = {
                'kunden': alle_kunden,
                'next_kunden_id': next_kunden_id,
                # next_anlage_id nicht mehr global - ist jetzt pro Kunde
            }

            with open(daten_pfad, 'w', encoding='utf-8') as f:
                json.dump(alle_daten, f, indent=4, ensure_ascii=False)  # type: ignore[arg-type]

            return True, None

        except Exception as e:
            return False, str(e)

    # ==================== Helper-Funktionen ====================

    def konvertiere_kunde_zu_speicherbar(self, kunde_data, aktive_daten_fields):
        """Konvertiert Kunde-Daten von UI zu speicherbaren Dictionaries.

        Args:
            kunde_data (dict): Kundendaten mit möglicherweise UI-Objekten
            aktive_daten_fields (list): Liste der Kundendaten-Felder

        Returns:
            dict: Speicherbare Kundendaten
        """
        speicherbar = {
            'id': kunde_data['id']
        }

        # Kopiere Kundendaten-Felder
        for field in aktive_daten_fields:
            speicherbar[field] = kunde_data[field]

        # Konvertiere Anlagen
        speicherbar['anlagen'] = [
            self._konvertiere_anlage_zu_speicherbar(anlage)
            for anlage in kunde_data.get('anlagen', [])
        ]

        return speicherbar

    def _konvertiere_anlage_zu_speicherbar(self, anlage):
        """Konvertiert eine Anlage zu einem speicherbaren Dictionary.

        Args:
            anlage (dict): Anlagen-Daten

        Returns:
            dict: Speicherbare Anlagen-Daten
        """
        return {
            'id': anlage['id'],
            'beschreibung': anlage['beschreibung'],
            'name': anlage.get('name', ''),
            'adresse': anlage.get('adresse', ''),
            'plz_ort': anlage.get('plz_ort', ''),
            'raum': anlage.get('raum', ''),
            'gebaeude': anlage.get('gebaeude', ''),
            'geschoss': anlage.get('geschoss', ''),
            'funktion': anlage.get('funktion', ''),
            'zaehlernummer': anlage.get('zaehlernummer', ''),
            'zaehlerstand': anlage.get('zaehlerstand', ''),
            'code': anlage.get('code', ''),
            'bemerkung': anlage.get('bemerkung', ''),
            'felder': anlage.get('felder', 3),
            'reihen': anlage.get('reihen', 7),
            'teile_text': anlage.get('teile_text', ''),
            'teile_parsed': anlage.get('teile_parsed', [])
        }

    # ==================== Export/Import ====================

    def exportiere_zu_verzeichnis(self, ziel_verzeichnis):
        """Exportiert Daten und Settings in ein Zielverzeichnis.

        Args:
            ziel_verzeichnis (Path): Zielverzeichnis

        Returns:
            tuple: (erfolg: bool, exportierte_dateien: list, fehler: str oder None)
        """
        from constants import EXPORT_DATEN_DATEI, EXPORT_SETTINGS_DATEI
        import shutil

        ziel_verzeichnis = Path(ziel_verzeichnis)
        exportierte_dateien = []

        try:
            # Kopiere Daten-Datei
            daten_quelle = self.get_data_file_path()
            if daten_quelle.exists():
                daten_ziel = ziel_verzeichnis / EXPORT_DATEN_DATEI
                shutil.copy2(daten_quelle, daten_ziel)
                exportierte_dateien.append(f"✓ {daten_ziel}")

            # Kopiere Settings-Datei
            settings_quelle = self.get_settings_file_path()
            if settings_quelle.exists():
                settings_ziel = ziel_verzeichnis / EXPORT_SETTINGS_DATEI
                shutil.copy2(settings_quelle, settings_ziel)
                exportierte_dateien.append(f"✓ {settings_ziel}")

            return True, exportierte_dateien, None

        except Exception as e:
            return False, exportierte_dateien, str(e)

    def importiere_von_verzeichnis(self, quell_verzeichnis):
        """Importiert Daten und Settings aus einem Quellverzeichnis.

        Args:
            quell_verzeichnis (Path): Quellverzeichnis

        Returns:
            tuple: (erfolg: bool, importierte_dateien: list, fehler: str oder None)
        """
        from constants import EXPORT_DATEN_DATEI, EXPORT_SETTINGS_DATEI
        import shutil

        quell_verzeichnis = Path(quell_verzeichnis)
        importierte_dateien = []

        try:
            daten_quelle = quell_verzeichnis / EXPORT_DATEN_DATEI
            settings_quelle = quell_verzeichnis / EXPORT_SETTINGS_DATEI

            # Importiere Daten
            if daten_quelle.exists():
                daten_ziel = self.get_data_file_path()
                shutil.copy2(daten_quelle, daten_ziel)
                importierte_dateien.append(f"✓ {EXPORT_DATEN_DATEI}")

            # Importiere Settings
            if settings_quelle.exists():
                settings_ziel = self.get_settings_file_path()
                shutil.copy2(settings_quelle, settings_ziel)
                importierte_dateien.append(f"✓ {EXPORT_SETTINGS_DATEI}")

            if not importierte_dateien:
                return False, [], "Keine Dateien gefunden"

            return True, importierte_dateien, None

        except Exception as e:
            return False, importierte_dateien, str(e)
