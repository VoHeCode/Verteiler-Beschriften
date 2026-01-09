# Verteiler Beschriften - Flet App

**Version 2.9.8**

Moderne Cross-Platform-App zur Erstellung von Verteilungsbeschriftungen für **Hager UZ005 Beschriftungshalterungen**.

Erstellt zuschneidbare Tabellen im ODS-Format (OpenDocument Spreadsheet) für professionelle Elektroverteilungen.

## 📊 Projekt-Status

- ✅ **Produktionsreif** für Desktop (Linux, Windows, macOS)
- ✅ **Produktionsreif** für Mobile (Android, iOS)
- ✅ Kundenspezifische Anlagen-IDs (verhindert Merge-Konflikte)
- ✅ FilePicker-basierter Import
- ✅ Plattformübergreifende Datensynchronisation

## 📁 Projekt-Struktur

```
anlagen_app/
├── main.py                 # Flet App (637 Zeilen)
├── constants.py            # Konstanten
├── validators.py           # Validierungsfunktionen
├── data_manager.py         # Daten-Management (JSON)
├── android_handler.py      # Platform-spezifisch
├── ods_exporter.py         # ODS-Export
├── ui_builder.py           # UI-Komponenten (Flet)
└── requirements.txt        # Dependencies
```

## 🎯 Technologie-Stack

- **UI-Framework:** Flet (Flutter-basiert)
- **Export-Format:** ODS (OpenDocument)
- **Daten:** JSON
- **Platform:** Cross-Platform (Desktop, Web, Android, iOS)

## 🚀 Installation & Start

### System-Anforderungen

- **Python:** 3.8 oder höher
- **Flet:** 0.24.0 oder höher
- **Betriebssystem:** Linux, Windows, macOS, Android, iOS

### Installation

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# Desktop-App starten
python main.py

# Als Web-App starten
flet run main.py --web

# Für Android bauen
flet build apk

# Für Linux bauen
flet build linux

# AppImage erstellen (Linux)
./MakeAppImage.sh 
```

## 💾 Datenstruktur & Speicherort

Die App speichert alle Daten transparent und zugänglich im Dokumenten-Ordner:

**Desktop (Linux/macOS):**
```
~/Documents/Verteiler_Beschriften/
├── anlagen_daten.json          # Alle Kunden & Anlagen
├── app_settings.json           # Einstellungen
├── Export/                     # Exportierte Backups
│   ├── Verteiler_Daten_TIMESTAMP.json
│   └── Verteiler_Einstellungen_TIMESTAMP.json
└── Import/                     # Für manuellen Import
```

**Android:**
```
/storage/emulated/0/Documents/Verteiler_Beschriften/
└── (gleiche Struktur wie Desktop)
```

**Vorteile:**
- ✅ Keine versteckten App-Daten
- ✅ Direkter Dateizugriff möglich
- ✅ Einfache Backup-Erstellung
- ✅ Plattformübergreifender Datenaustausch

## 📤 Export & Import

### Export
1. Klick auf **"Export zu Documents"** in den Einstellungen
2. Dateien werden in `Export/` Ordner gespeichert
3. Timestamp im Dateinamen für Versionierung
4. Snackbar bestätigt erfolgreichen Export (4 Sekunden)

### Import
1. Klick auf **"Import"** Button
2. FilePicker öffnet sich
3. Wähle JSON-Datei (aus `Import/`, `Export/` oder beliebigem Ordner)
4. **Intelligente Import-Optionen:**
   - **Überschreiben:** Alle Daten ersetzen
   - **Mergen:** Nur neue Kunden hinzufügen (bei unterschiedlichen Datensätzen)
   - **Abbrechen:** Nichts ändern

### Datenaustausch zwischen Geräten
1. Desktop: Exportiere Daten → `Export/` Ordner
2. Kopiere Dateien zum Android-Gerät (USB, Cloud, etc.)
3. Android: Lege Dateien in `Documents/Verteiler_Beschriften/Import/`
4. Android: Nutze Import-Button und wähle Datei

## 🚀 Installation & Start


## 📝 Features

- ✅ **Hager UZ005 Beschriftungen**: Perfekt zugeschnitten für Beschriftungshalterungen
- ✅ **Zuschneidbare Tabellen**: ODS-Export zum direkten Ausschneiden
- ✅ Kunden-Verwaltung mit Projektdaten
- ✅ Anlagen-Verwaltung mit Lokalisierung (Raum, Gebäude, Geschoss)
- ✅ Flexible Tabellen-Konfiguration (Felder × Reihen)
- ✅ ODS-Export mit konfigurierbaren Styles
- ✅ Automatische Code-Generierung (Raum-Gebäude-Geschoss-Funktion)
- ✅ Cross-Platform (Desktop, Web, Android, iOS)
- ✅ Persistente Settings (JSON)
- ✅ Export/Import über Documents
- ✅ Eingabe-Validierung
- ✅ Responsive Design
- ✅ Watermark-Unterstützung in Tabellen

## 🎨 Flet Vorteile

- **Flutter-basiert**: Native Performance
- **Ein Codebase**: Desktop + Web + Mobile
- **Hot Reload**: Schnelle Entwicklung
- **Material Design**: Moderne UI
- **Einfache Deployment**: Web ohne Server möglich

## 📱 Plattformspezifische Hinweise

### Android
- **Permissions:** App benötigt `READ/WRITE_EXTERNAL_STORAGE` und `MANAGE_EXTERNAL_STORAGE`
- **Speicherort:** `/storage/emulated/0/Documents/Verteiler_Beschriften/`
- **UI-Anpassung:** Automatischer Padding (25px oben/unten) für System-Overlays
- **Build:** `flet build apk` (pyproject.toml konfiguriert Permissions automatisch)

### Linux
- **AppImage:** Portable, keine Installation nötig
- **Build:** `flet build linux` → dann `./MakeAppImage.sh`
- **Speicherort:** `~/Documents/Verteiler_Beschriften/` oder `~/Dokumente/Verteiler_Beschriften/`

### iOS
- **Speicherort:** Nutzt iOS Documents-Verzeichnis
- **Build:** Benötigt macOS mit Xcode

## 🔧 Unterstützte Dateiformate

### Export
- **ODS (OpenDocument Spreadsheet):** Hauptformat für Beschriftungen
- **JSON:** Backup von Daten und Einstellungen

### Import
- **JSON:** Daten und Einstellungen
- Automatische Erkennung des Dateityps (Daten vs. Einstellungen)

## 📄 Lizenz

**Proprietäre Software - Alle Rechte vorbehalten**

Copyright © 2026 Volker Heggemann

Diese Software ist nur für **private, nicht-kommerzielle Nutzung** bestimmt.  
Kommerzielle Nutzung, Änderungen oder Weiterverbreitung sind **nicht gestattet**.

Für kommerzielle Lizenzen oder andere Nutzungsrechte kontaktieren Sie:  
📧 vohegg@gmail.com

Details siehe [LICENSE](LICENSE) Datei.

## 👤 Autor

**Volker Heggemann**  
📧 vohegg@gmail.com

---

*Optimiert für Hager UZ005 Beschriftungshalterungen - professionelle Verteilungsbeschriftung leicht gemacht!*
