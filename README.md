# Verteiler Beschriften - Flet App

Moderne Cross-Platform-App zur Erstellung von Verteilungsbeschriftungen für **Hager UZ005 Beschriftungshalterungen**.

Erstellt zuschneidbare Tabellen im ODS-Format (OpenDocument Spreadsheet) für professionelle Elektroverteilungen.

## 📊 Projekt-Status

- Bereit für Desktop, Web & Mobile (Android/iOS)

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

# AppImage erstellen
# aus dem Projektordner
./MakeAppImage.sh 

```


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
