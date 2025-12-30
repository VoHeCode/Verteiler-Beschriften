#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Anlagen Eingabe App - Flet Version.

Hauptdatei mit App-Klasse für Flet.
"""

import flet as ft
from datetime import datetime
from pathlib import Path

# Module importieren
from constants import APP_VERSION, APP_NAME, SPALTEN_PRO_EINHEIT
from data_manager import DataManager
from ui_builder import UIBuilder
from ods_exporter import validiere_eintraege, exportiere_anlage_ods
from android_handler import exportiere_zu_downloads as export_downloads, importiere_von_downloads as import_downloads


class AnlagenApp:
    """Hauptanwendung für Anlagen-Eingabe und -Export."""

    def __init__(self, page: ft.Page):
        """Initialisiert die App.
        
        Args:
            page: Flet Page-Objekt
        """
        self.page = page
        self.page.title = f"{APP_NAME} V{APP_VERSION}"
        self.page.scroll = ft.ScrollMode.AUTO
        
        # Daten-Pfad
        self.data_path = Path.home() / ".anlagen_app"
        self.data_path.mkdir(exist_ok=True)
        
        # Daten-Manager
        self.data_manager = DataManager(self.data_path)
        
        # Settings
        self.settings = self.data_manager.lade_settings()
        
        # UI-Builder
        self.ui_builder = UIBuilder(self, page)
        
        # Daten
        self.kunden_daten = {}
        self.anlagen_daten = []
        self.next_anlage_id = 1
        self.aktuelle_anlage = None
        self.alle_kunden = {}
        self.aktiver_kunde_key = None
        self.next_kunden_id = 1
        
        # UI-Komponenten
        self.kunden_auswahl = None
        self.kunde_input = None
        self.anlagen_tabelle = None
        
        # Anlage-Detail UI
        self.beschr_input = None
        self.name_input = None
        self.adresse_input = None
        self.plz_ort_input = None
        self.raum_input = None
        self.gebaeude_input = None
        self.geschoss_input = None
        self.funktion_input = None
        self.zaehlernummer_input = None
        self.zaehlerstand_input = None
        self.code_input = None
        self.bemerkung_input = None
        self.felder_input = None
        self.reihen_input = None
        self.info_label = None
        self.verfuegbar_label = None
        self.text_editor = None
        self.teile_button = None
        self.letzte_export_datei = None
        
        # Settings UI
        self.settings_felder_input = None
        self.settings_reihen_input = None
        self.settings_font_gemergt_input = None
        self.settings_font_beschr_input = None
        self.settings_font_inhalt_input = None
        self.settings_spalten_breite_input = None
        self.settings_beschr_hoehe_input = None
        self.settings_inhalt_hoehe_input = None
        self.settings_umrandung_switch = None
        self.settings_rand_oben_input = None
        self.settings_rand_unten_input = None
        self.settings_rand_links_input = None
        self.settings_rand_rechts_input = None
        
        # Initialisiere
        self.init_app()
    
    def init_app(self):
        """Initialisiert die App-Daten und UI."""
        # Initialisiere Kundendaten-Widgets
        self.kunden_daten = {
            'projekt': ft.TextField(hint_text="Projektname", on_change=self.speichere_projekt_daten),
            'datum': ft.TextField(
                value=datetime.now().date().strftime('%Y-%m-%d'),
                hint_text="YYYY-MM-DD",
                on_change=self.speichere_projekt_daten
            ),
            'adresse': ft.TextField(hint_text="Straße und Hausnummer", on_change=self.speichere_projekt_daten),
            'plz': ft.TextField(hint_text="PLZ", on_change=self.speichere_projekt_daten),
            'ort': ft.TextField(hint_text="Ort", on_change=self.speichere_projekt_daten),
            'ansprechpartner': ft.TextField(hint_text="Ansprechpartner", on_change=self.speichere_projekt_daten),
            'telefonnummer': ft.TextField(hint_text="Telefonnummer", on_change=self.speichere_projekt_daten),
            'email': ft.TextField(hint_text="E-Mail", on_change=self.speichere_projekt_daten),
        }
        
        # Lade Daten
        self.lade_daten()
        
        # Erstelle UI
        hauptansicht = self.ui_builder.erstelle_hauptansicht()
        self.page.add(hauptansicht)
    
    # ==================== Daten laden/speichern ====================
    
    def lade_daten(self):
        """Lädt alle Kundendaten."""
        alle_kunden, next_kunden_id, next_anlage_id = self.data_manager.lade_daten()
        
        self.alle_kunden = alle_kunden
        self.next_kunden_id = next_kunden_id
        self.next_anlage_id = next_anlage_id
        
        if self.alle_kunden:
            self.aktiver_kunde_key = list(self.alle_kunden.keys())[0]
            self.aktualisiere_aktive_daten()
    
    def speichere_daten(self, e=None):
        """Speichert alle Kundendaten."""
        self.speichere_projekt_daten()
        
        speicherbare_kunden = {}
        aktive_felder = list(self.kunden_daten.keys())
        
        for key, kunde_data in self.alle_kunden.items():
            speicherbare_kunden[key] = self.data_manager.konvertiere_kunde_zu_speicherbar(
                kunde_data, aktive_felder
            )
        
        erfolg, fehler = self.data_manager.speichere_daten(
            speicherbare_kunden, self.next_kunden_id, self.next_anlage_id
        )
        
        if not erfolg:
            self.show_error("Speicher-Fehler", f"Fehler: {fehler}")
    
    def speichere_projekt_daten(self, e=None):
        """Speichert Projektdaten des aktiven Kunden."""
        if not self.aktiver_kunde_key or self.aktiver_kunde_key not in self.alle_kunden:
            return
        
        kunde = self.alle_kunden[self.aktiver_kunde_key]
        for key, widget in self.kunden_daten.items():
            kunde[key] = widget.value
    
    def aktualisiere_aktive_daten(self):
        """Aktualisiert UI mit Daten des aktiven Kunden."""
        if not self.aktiver_kunde_key or self.aktiver_kunde_key not in self.alle_kunden:
            return
        
        kunde = self.alle_kunden[self.aktiver_kunde_key]
        
        for key, widget in self.kunden_daten.items():
            widget.value = kunde.get(key, '')
        
        self.anlagen_daten = kunde.get('anlagen', [])
        self.aktualisiere_anlagen_tabelle()
        
        if self.page:
            self.page.update()
    
    def aktualisiere_anlagen_tabelle(self):
        """Aktualisiert die Anlagen-Tabelle."""
        if not self.anlagen_tabelle:
            return
        
        self.anlagen_tabelle.rows.clear()
        for anlage in self.anlagen_daten:
            self.anlagen_tabelle.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(anlage['id']))),
                        ft.DataCell(ft.Text(anlage['beschreibung'])),
                        ft.DataCell(ft.Text(anlage.get('code', ''))),
                        ft.DataCell(ft.Text(anlage.get('plz_ort', ''))),
                    ],
                    data=anlage  # Speichere Anlage in row.data
                )
            )
        
        if self.page:
            self.page.update()
    
    # ==================== Helper für Dialoge ====================
    
    def show_error(self, title, message):
        """Zeigt Fehler-Dialog."""
        dlg = ft.AlertDialog(title=ft.Text(title), content=ft.Text(message))
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    def show_info(self, title, message):
        """Zeigt Info-Dialog."""
        dlg = ft.AlertDialog(title=ft.Text(title), content=ft.Text(message))
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    # ==================== Kunden-Verwaltung ====================
    
    def wechsel_kunden_auswahl(self, e):
        """Wechselt aktiven Kunden."""
        if e.control.value and e.control.value in self.alle_kunden:
            self.aktiver_kunde_key = e.control.value
            self.aktualisiere_aktive_daten()
    
    def _navigiere_kunde_links(self, e):
        """Navigiert zum vorherigen Kunden."""
        if not self.alle_kunden:
            return
        
        keys = list(self.alle_kunden.keys())
        if self.aktiver_kunde_key in keys:
            idx = keys.index(self.aktiver_kunde_key)
            new_idx = (idx - 1) % len(keys)
            self.aktiver_kunde_key = keys[new_idx]
            self.kunden_auswahl.value = self.aktiver_kunde_key
            self.aktualisiere_aktive_daten()
    
    def _navigiere_kunde_rechts(self, e):
        """Navigiert zum nächsten Kunden."""
        if not self.alle_kunden:
            return
        
        keys = list(self.alle_kunden.keys())
        if self.aktiver_kunde_key in keys:
            idx = keys.index(self.aktiver_kunde_key)
            new_idx = (idx + 1) % len(keys)
            self.aktiver_kunde_key = keys[new_idx]
            self.kunden_auswahl.value = self.aktiver_kunde_key
            self.aktualisiere_aktive_daten()
    
    def _kunde_neu_hinzufuegen(self, e):
        """Fügt neuen Kunden hinzu."""
        name = self.kunde_input.value.strip()
        if not name:
            self.show_error('Fehler', 'Bitte Kundennamen eingeben.')
            return
        
        if name in self.alle_kunden:
            self.show_error('Fehler', f'Kunde "{name}" existiert bereits.')
            return
        
        self.alle_kunden[name] = {
            'id': self.next_kunden_id,
            'projekt': '',
            'datum': datetime.now().date().strftime('%Y-%m-%d'),
            'adresse': '', 'plz': '', 'ort': '',
            'ansprechpartner': '', 'telefonnummer': '', 'email': '',
            'anlagen': []
        }
        self.next_kunden_id += 1
        self.aktiver_kunde_key = name
        
        self.kunden_auswahl.options = [ft.dropdown.Option(k) for k in self.alle_kunden.keys()]
        self.kunden_auswahl.value = name
        self.aktualisiere_aktive_daten()
        self.speichere_daten()
        self.kunde_input.value = ''
        self.page.update()
        
        self.show_info('Erfolg', f'Kunde "{name}" hinzugefügt.')
    
    def _kunde_umbenennen(self, e):
        """Benennt aktiven Kunden um."""
        if not self.aktiver_kunde_key:
            self.show_error('Fehler', 'Kein Kunde ausgewählt.')
            return
        
        neuer_name = self.kunde_input.value.strip()
        if not neuer_name:
            self.show_error('Fehler', 'Bitte neuen Namen eingeben.')
            return
        
        if neuer_name in self.alle_kunden:
            self.show_error('Fehler', f'Kunde "{neuer_name}" existiert bereits.')
            return
        
        alter_name = self.aktiver_kunde_key
        self.alle_kunden[neuer_name] = self.alle_kunden.pop(alter_name)
        self.aktiver_kunde_key = neuer_name
        
        self.kunden_auswahl.options = [ft.dropdown.Option(k) for k in self.alle_kunden.keys()]
        self.kunden_auswahl.value = neuer_name
        self.speichere_daten()
        self.kunde_input.value = ''
        self.page.update()
        
        self.show_info('Erfolg', f'Kunde umbenannt: "{alter_name}" → "{neuer_name}"')
    
    def kunde_loeschen(self, e):
        """Löscht aktiven Kunden."""
        if not self.aktiver_kunde_key:
            self.show_error('Fehler', 'Kein Kunde ausgewählt.')
            return
        
        # TODO: Bestätigungs-Dialog implementieren
        del self.alle_kunden[self.aktiver_kunde_key]
        
        if self.alle_kunden:
            self.aktiver_kunde_key = list(self.alle_kunden.keys())[0]
        else:
            self.aktiver_kunde_key = None
        
        self.kunden_auswahl.options = [ft.dropdown.Option(k) for k in self.alle_kunden.keys()]
        if self.aktiver_kunde_key:
            self.kunden_auswahl.value = self.aktiver_kunde_key
            self.aktualisiere_aktive_daten()
        else:
            self.anlagen_tabelle.rows.clear()
        
        self.speichere_daten()
        self.page.update()
    
    # ==================== Anlagen-Verwaltung ====================
    
    def anlage_hinzufuegen(self, e):
        """Fügt neue Anlage hinzu."""
        if not self.aktiver_kunde_key:
            self.show_error('Fehler', 'Bitte zuerst Kunden auswählen.')
            return
        
        neue_anlage = {
            'id': self.next_anlage_id,
            'beschreibung': f'Anlage {self.next_anlage_id}',
            'name': '', 'adresse': '', 'plz_ort': '',
            'raum': '', 'gebaeude': '', 'geschoss': '', 'funktion': '',
            'zaehlernummer': '', 'zaehlerstand': '', 'code': '', 'bemerkung': '',
            'felder': self.settings.get('default_felder', 3),
            'reihen': self.settings.get('default_reihen', 7),
            'text_inhalt': '', 'teile_text': '', 'teile_parsed': []
        }
        self.next_anlage_id += 1
        
        self.anlagen_daten.append(neue_anlage)
        self.aktualisiere_anlagen_tabelle()
        self.speichere_daten()
        
        self.show_info('Erfolg', f'Anlage "{neue_anlage["beschreibung"]}" hinzugefügt.')
    
    def anlage_loeschen(self, e):
        """Löscht ausgewählte Anlage."""
        # TODO: Selektion implementieren
        self.show_error('Info', 'Bitte Anlage zum Bearbeiten auswählen.')
    
    def bearbeite_ausgewaehlte_anlage(self, e):
        """Öffnet Detail-Ansicht für ausgewählte Anlage."""
        # TODO: Selektion implementieren
        if self.anlagen_daten:
            self.aktuelle_anlage = self.anlagen_daten[0]  # Erste Anlage als Test
            self.navigiere_zu_detail_view()
        else:
            self.show_error('Fehler', 'Keine Anlage vorhanden.')
    
    # ==================== Navigation ====================
    
    def navigiere_zu_detail_view(self):
        """Navigiert zur Anlage-Detailansicht."""
        detail_view = self.ui_builder.erstelle_anlage_detail_view()
        
        if self.aktuelle_anlage:
            self.beschr_input.value = self.aktuelle_anlage.get('beschreibung', '')
            self.name_input.value = self.aktuelle_anlage.get('name', '')
            self.adresse_input.value = self.aktuelle_anlage.get('adresse', '')
            self.plz_ort_input.value = self.aktuelle_anlage.get('plz_ort', '')
            self.raum_input.value = self.aktuelle_anlage.get('raum', '')
            self.gebaeude_input.value = self.aktuelle_anlage.get('gebaeude', '')
            self.geschoss_input.value = self.aktuelle_anlage.get('geschoss', '')
            self.funktion_input.value = self.aktuelle_anlage.get('funktion', '')
            self.zaehlernummer_input.value = self.aktuelle_anlage.get('zaehlernummer', '')
            self.zaehlerstand_input.value = self.aktuelle_anlage.get('zaehlerstand', '')
            self.code_input.value = self.aktuelle_anlage.get('code', '')
            self.bemerkung_input.value = self.aktuelle_anlage.get('bemerkung', '')
            self.felder_input.value = str(self.aktuelle_anlage.get('felder', 3))
            self.reihen_input.value = str(self.aktuelle_anlage.get('reihen', 7))
            self.text_editor.value = self.aktuelle_anlage.get('text_inhalt', '')
            
            self.info_aktualisieren()
        
        self.page.controls.clear()
        self.page.add(detail_view)
        self.page.update()
    
    def navigiere_zu_settings(self, e):
        """Navigiert zu Settings."""
        settings_view = self.ui_builder.erstelle_settings_dialog()
        self.page.controls.clear()
        self.page.add(settings_view)
        self.page.update()
    
    def zurueck_zur_hauptansicht(self, e):
        """Navigiert zurück zur Hauptansicht."""
        self.speichere_detail_daten()
        self.speichere_daten()
        hauptansicht = self.ui_builder.erstelle_hauptansicht()
        self.page.controls.clear()
        self.page.add(hauptansicht)
        self.aktualisiere_anlagen_tabelle()
        self.page.update()
    
    # ==================== Detail-Daten ====================
    
    def speichere_detail_daten(self):
        """Speichert Detail-Daten der aktuellen Anlage."""
        if not self.aktuelle_anlage:
            return
        
        self.aktuelle_anlage['beschreibung'] = self.beschr_input.value
        self.aktuelle_anlage['name'] = self.name_input.value
        self.aktuelle_anlage['adresse'] = self.adresse_input.value
        self.aktuelle_anlage['plz_ort'] = self.plz_ort_input.value
        self.aktuelle_anlage['raum'] = self.raum_input.value
        self.aktuelle_anlage['gebaeude'] = self.gebaeude_input.value
        self.aktuelle_anlage['geschoss'] = self.geschoss_input.value
        self.aktuelle_anlage['funktion'] = self.funktion_input.value
        self.aktuelle_anlage['zaehlernummer'] = self.zaehlernummer_input.value
        self.aktuelle_anlage['zaehlerstand'] = self.zaehlerstand_input.value
        self.aktuelle_anlage['code'] = self.code_input.value
        self.aktuelle_anlage['bemerkung'] = self.bemerkung_input.value
        
        try:
            self.aktuelle_anlage['felder'] = int(self.felder_input.value)
        except:
            self.aktuelle_anlage['felder'] = 3
        
        try:
            self.aktuelle_anlage['reihen'] = int(self.reihen_input.value)
        except:
            self.aktuelle_anlage['reihen'] = 7
        
        self.aktuelle_anlage['text_inhalt'] = self.text_editor.value
    
    def auto_speichere_detail_daten(self, e):
        """Auto-Speichern bei Änderung."""
        self.speichere_detail_daten()
        self.speichere_daten()
    
    # ==================== Code-Generierung ====================
    
    def generiere_code_string(self):
        """Generiert Code-String aus Lokalisierungsfeldern."""
        teile = []
        
        fun = self.funktion_input.value.strip()
        geb = self.gebaeude_input.value.strip()
        etage = self.geschoss_input.value.strip()
        raum = self.raum_input.value.strip()
        
        if fun:
            teile.append(f'={fun}')
        if geb:
            teile.append(f'++{geb}')
            if etage:
                teile.append(f'-{etage}')
        else:
            if etage:
                teile.append(f'++{etage}')
        
        if raum:
            teile.append(f'+{raum}')
        
        return ''.join(teile).upper() if teile else ''
    
    def aktualisiere_anlagen_code(self, e=None):
        """Generiert Anlagen-Code dynamisch."""
        neuer_code = self.generiere_code_string()
        
        if not self.code_input.value or self.code_input.value == self.aktuelle_anlage.get('code_auto_last', ''):
            self.code_input.value = neuer_code
            self.aktuelle_anlage['code_auto_last'] = neuer_code
            self.page.update()
        
        self.speichere_detail_daten()
    
    def aktualisiere_anlagen_code_und_speichere(self, e):
        """Aktualisiert Code und speichert."""
        self.aktualisiere_anlagen_code(e)
        self.speichere_daten()
    
    # ==================== Info-Aktualisierung ====================
    
    def info_aktualisieren(self, e=None):
        """Aktualisiert Info-Anzeige."""
        if not self.aktuelle_anlage or not self.felder_input:
            return False, []
        
        self.speichere_detail_daten()
        
        felder = self.aktuelle_anlage['felder']
        reihen = self.aktuelle_anlage['reihen']
        text = self.aktuelle_anlage['text_inhalt']
        
        is_valid, gueltige_eintraege, fehler_anzahl, belegte_spalten, max_spalten = validiere_eintraege(
            text, felder, reihen
        )
        
        self.info_label.value = f'Gesamt-Spalten: {felder} × {reihen} × {SPALTEN_PRO_EINHEIT} = {max_spalten}'
        
        if fehler_anzahl > 0:
            self.verfuegbar_label.value = f'❌ {fehler_anzahl} Fehler!'
            self.verfuegbar_label.color = ft.colors.RED_700
        else:
            verfuegbar = max_spalten - len(belegte_spalten)
            self.verfuegbar_label.value = f'✓ Verfügbar: {verfuegbar} von {max_spalten}'
            self.verfuegbar_label.color = ft.colors.GREEN_700 if verfuegbar == max_spalten else ft.colors.ORANGE_700
        
        self.page.update()
        return is_valid, gueltige_eintraege
    
    def info_aktualisieren_und_speichern(self, e=None):
        """Aktualisiert Info und speichert."""
        self.info_aktualisieren(e)
        self.speichere_detail_daten()
        self.speichere_daten()
    
    # ==================== Export ====================
    
    def exportiere_anlage(self, e):
        """Exportiert aktuelle Anlage als ODS."""
        if not self.aktuelle_anlage:
            self.show_error('Fehler', 'Keine Anlage ausgewählt.')
            return
        
        try:
            export_pfad = exportiere_anlage_ods(
                self.aktuelle_anlage, self.settings, self.data_path
            )
            
            self.letzte_export_datei = export_pfad
            self.teile_button.disabled = False
            self.page.update()
            
            # TODO: Share implementieren für Android
            self.show_info('Erfolg', f'ODS exportiert: {export_pfad.name}')
            
        except ValueError as e:
            self.show_error('Validierungs-Fehler', str(e))
        except Exception as e:
            self.show_error('Export-Fehler', f'Fehler beim Export:\n{str(e)}')
    
    def teile_letzte_ods(self, e):
        """Teilt letzte ODS."""
        if not self.letzte_export_datei or not self.letzte_export_datei.exists():
            self.show_error('Fehler', 'Keine Datei gefunden.')
            return
        
        # TODO: Android Share implementieren
        self.show_info('Info', f'Datei: {self.letzte_export_datei}')
    
    def exportiere_kunde_odt(self, e):
        """Placeholder für Kunden-Export."""
        self.show_info('Info', 'Kunden-ODT-Export noch nicht implementiert.')
    
    # ==================== Settings ====================
    
    def auto_speichere_settings(self, e):
        """Speichert Settings automatisch."""
        try:
            self.settings['default_felder'] = int(self.settings_felder_input.value)
            self.settings['default_reihen'] = int(self.settings_reihen_input.value)
            self.settings['fontsize_gemergte_zelle'] = int(self.settings_font_gemergt_input.value)
            self.settings['fontsize_beschriftung_zelle'] = int(self.settings_font_beschr_input.value)
            self.settings['fontsize_inhalt_zelle'] = int(self.settings_font_inhalt_input.value)
            self.settings['spalten_breite'] = float(self.settings_spalten_breite_input.value)
            self.settings['beschriftung_row_hoehe'] = float(self.settings_beschr_hoehe_input.value)
            self.settings['inhalt_row_hoehe'] = float(self.settings_inhalt_hoehe_input.value)
            self.settings['zellen_umrandung'] = self.settings_umrandung_switch.value
            self.settings['rand_oben'] = float(self.settings_rand_oben_input.value)
            self.settings['rand_unten'] = float(self.settings_rand_unten_input.value)
            self.settings['rand_links'] = float(self.settings_rand_links_input.value)
            self.settings['rand_rechts'] = float(self.settings_rand_rechts_input.value)
            
            self.data_manager.speichere_settings(self.settings)
        except:
            pass
    
    # ==================== Export/Import ====================
    
    def exportiere_zu_downloads(self, e):
        """Exportiert zu Downloads."""
        erfolg, dateien, fehler = export_downloads(self.data_manager)
        
        if erfolg:
            self.show_info('Export erfolgreich', '\n'.join(dateien))
        else:
            self.show_error('Export-Fehler', fehler)
    
    def importiere_von_downloads(self, e):
        """Importiert von Downloads."""
        erfolg, dateien, fehler = import_downloads(self.data_manager)
        
        if erfolg:
            self.settings = self.data_manager.lade_settings()
            self.lade_daten()
            self.aktualisiere_aktive_daten()
            self.show_info('Import erfolgreich', '\n'.join(dateien))
        else:
            if "Keine" in fehler:
                self.show_info('Keine Dateien', fehler)
            else:
                self.show_error('Import-Fehler', fehler)


def main(page: ft.Page):
    """Haupteinstiegspunkt der Flet-Anwendung."""
    app = AnlagenApp(page)


if __name__ == '__main__':
    ft.app(target=main)
