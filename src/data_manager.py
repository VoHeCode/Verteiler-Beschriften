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

    def validate_setting_value(self, key, value, default_value):
        """Validiert einen einzelnen Settings-Wert gegen seinen Typ.
        
        Args:
            key: Settings-Key
            value: Zu validierender Wert
            default_value: Default-Wert (definiert erwarteten Typ)
            
        Returns:
            Validierter Wert oder Default bei Fehler
        """
        try:
            # Type-Check basierend auf Default
            if isinstance(default_value, bool):
                # Bool muss explizit geprüft werden (vor int!)
                if isinstance(value, bool):
                    return value
                return bool(value)
            elif isinstance(default_value, int):
                return int(value)
            elif isinstance(default_value, float):
                return float(value)
            elif isinstance(default_value, str):
                return str(value)
            else:
                return value
        except (ValueError, TypeError):
            # Bei Fehler: Default verwenden
            return default_value

    def load_settings(self):
        """Lädt die App-Einstellungen aus der JSON-Datei.

        Returns:
            dict: Geladene Settings oder Standard-Settings
        """
        settings_path = self.get_settings_file_path()

        if not settings_path.exists():
            return self.settings

        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)

            # Aktualisiere nur vorhandene Keys mit Validierung
            for key, value in loaded_settings.items():
                if key in self.settings:
                    default_value = self.settings[key]
                    self.settings[key] = self.validate_setting_value(key, value, default_value)

            return self.settings

        except Exception as e:
            return self.settings

    def save_settings(self, settings=None):
        """Speichert die App-Einstellungen in eine JSON-Datei.

        Args:
            settings (dict, optional): Settings zum Speichern.
                Wenn None, werden self.settings verwendet.

        Returns:
            tuple: (erfolg: bool, fehler_nachricht: str oder None)
        """
        if settings is not None:
            self.settings = settings

        settings_path = self.get_settings_file_path()

        try:
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)  # type: ignore[arg-type]

            return True, None

        except Exception as e:
            return False, str(e)

    # ==================== Daten Management ====================

    def load_data(self):
        """Lädt alle Kundendaten aus der JSON-Datei.

        Returns:
            tuple: (all_customers: dict, next_customer_id: int)
        """
        data_path = self.get_data_file_path()

        if not data_path.exists():
            return {}, 1

        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                all_data = json.load(f)

            all_customers = all_data.get('kunden', {})
            next_customer_id = all_data.get('next_kunden_id', 1)

            # Migration: Füge next_anlage_id zu alten Kunden hinzu falls nicht vorhanden
            for customer_data in all_customers.values():
                if 'next_anlage_id' not in customer_data:
                    # Finde höchste Anlagen-ID + 1
                    max_id = max((a.get('id', 0) for a in customer_data.get('anlagen', [])), default=0)
                    customer_data['next_anlage_id'] = max_id + 1

            return all_customers, next_customer_id

        except Exception as e:
            return {}, 1

    def save_data(self, all_customers, next_customer_id):
        """Speichert alle Kundendaten in die JSON-Datei.

        Args:
            all_customers (dict): Dictionary mit allen Kundendaten
            next_customer_id (int): Nächste freie Kunden-ID

        Returns:
            tuple: (erfolg: bool, fehler_nachricht: str oder None)
        """
        data_path = self.get_data_file_path()

        try:
            data_path.parent.mkdir(parents=True, exist_ok=True)

            all_data = {
                'kunden': all_customers,
                'next_kunden_id': next_customer_id,
                # next_anlage_id nicht mehr global - ist jetzt pro Kunde
            }

            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=4, ensure_ascii=False)  # type: ignore[arg-type]

            return True, None

        except Exception as e:
            return False, str(e)

    # ==================== Helper-Funktionen ====================

    def convert_kunde_to_dict(self, customer_data, active_data_fields):
        """Konvertiert Kunde-Daten von UI zu speicherbaren Dictionaries.

        Args:
            customer_data (dict): Kundendaten mit möglicherweise UI-Objekten
            active_data_fields (list): Liste der Kundendaten-Felder

        Returns:
            dict: Speicherbare Kundendaten
        """
        saveable = {
            'id': customer_data['id']
        }

        # Kopiere Kundendaten-Felder
        for field in active_data_fields:
            saveable[field] = customer_data[field]

        # Konvertiere Anlagen
        saveable['anlagen'] = [
            self._convert_anlage_to_dict(electric_system)
            for electric_system in customer_data.get('anlagen', [])
        ]

        return saveable

    def _convert_anlage_to_dict(self, electric_system):
        """Konvertiert eine Anlage zu einem speicherbaren Dictionary.

        Args:
            electric_system (dict): Anlagen-Daten

        Returns:
            dict: Speicherbare Anlagen-Daten
        """
        return {
            'id': electric_system['id'],
            'beschreibung': electric_system['beschreibung'],
            'name': electric_system.get('name', ''),
            'adresse': electric_system.get('adresse', ''),
            'plz_ort': electric_system.get('plz_ort', ''),
            'raum': electric_system.get('raum', ''),
            'gebaeude': electric_system.get('gebaeude', ''),
            'geschoss': electric_system.get('geschoss', ''),
            'funktion': electric_system.get('funktion', ''),
            'zaehlernummer': electric_system.get('zaehlernummer', ''),
            'zaehlerstand': electric_system.get('zaehlerstand', ''),
            'code': electric_system.get('code', ''),
            'bemerkung': electric_system.get('bemerkung', ''),
            'felder': electric_system.get('felder', 3),
            'reihen': electric_system.get('reihen', 7)
        }

    # ==================== Export/Import ====================
    # Exportfunktionen wurden entfernt - nicht verwendet


if __name__ == "__main__":
    pass
