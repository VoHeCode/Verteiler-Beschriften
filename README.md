# Anlagen Eingabe App - Flet Version

Moderne Cross-Platform-App mit Flet Framework.

## 📊 Projekt-Status

- **✅ Flet-Migration abgeschlossen**
- Von Toga/Beeware zu Flet portiert
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
```

## 📝 Features

- ✅ Kunden-Verwaltung
- ✅ Anlagen-Verwaltung mit Lokalisierung
- ✅ ODS-Export mit konfigurierbaren Styles
- ✅ Cross-Platform (Desktop, Web, Mobile)
- ✅ Persistente Settings (JSON)
- ✅ Export/Import über Downloads
- ✅ Eingabe-Validierung
- ✅ Responsive Design

## 🎨 Flet Vorteile

- **Flutter-basiert**: Native Performance
- **Ein Codebase**: Desktop + Web + Mobile
- **Hot Reload**: Schnelle Entwicklung
- **Material Design**: Moderne UI
- **Einfache Deployment**: Web ohne Server möglich

## 📄 Lizenz

[Lizenz hier einfügen]

## 👤 Autor

[Autor hier einfügen]
