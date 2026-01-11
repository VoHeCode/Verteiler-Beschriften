# Verteiler Beschriften - Professionelle Elektroverteilungs-Beschriftung

**Version 3.1.0** | Desktop (Linux · Windows) · Android

> **Erstellt perfekte Beschriftungen für Hager UZ005 Beschriftungshalterungen**  
> Mit dieser App können Sie professionelle, zuschneidbare Beschriftungen für Elektroverteilungen erstellen - direkt auf Ihrem Smartphone, Tablet oder Computer.

---

## 🎯 Was kann die App?

### ✨ Hauptfunktionen

- **📱 Mobile Datenerfassung**: Erfassen Sie Anlagendaten direkt vor Ort mit Smartphone oder Tablet
- **🏷️ Perfekte Beschriftungen**: Erstellt zuschneidbare Tabellen speziell für **Hager UZ005 Beschriftungshalterungen**
- **📊 Professionelle Dokumentation**: Automatische Erstellung von Anlagendokumentation für die Schaltschranktür
- **👥 Kundenverwaltung**: Verwalten Sie mehrere Kunden mit allen Projektdaten an einem Ort
- **🏢 Anlagenverwaltung**: Detaillierte Erfassung mit Lokalisierung (Raum, Gebäude, Geschoss, Funktion)
- **💾 Datenaustausch**: Einfacher Datentransfer zwischen Handy und Computer
- **☁️ Backup & Synchronisation**: Export/Import für Datensicherung und Geräte-Synchronisation

### 🎨 Praktische Beispiele

Die wichtigsten Anwendungsbeispiele finden Sie im Ordner **"Ergebnisse der Software"**:
- Fertige Beschriftungstabellen (ODS-Format)
- Anlagendokumentation (ODT-Format)
- Kundendokumentation

---

## 🚀 Schnellstart für Anwender

### Desktop (Linux, Windows)

1. **App starten**: Doppelklick auf `main.py` oder Verknüpfung
2. **Kunden anlegen**: Button "NEU" → Name eingeben
3. **Projektdaten erfassen**: Adresse, Ansprechpartner, etc. ausfüllen
4. **Anlage hinzufügen**: Button "ANLAGE HINZUFÜGEN"
5. **Beschriftungen eingeben**: Format: `1 Heizung` oder `3-6 Lüftung` oder `7+5 Elektrik`
6. **Exportieren**: Button "ANLAGE TABELLENEXPORT" → ODS-Datei wird erstellt

### Android

1. **App installieren**: APK installieren
2. **Gleiche Schritte** wie Desktop - die Bedienung ist identisch!
3. **Tipp**: Nutzen Sie Export/Import um Daten zwischen Geräten zu übertragen

---

## 📋 Typischer Workflow

```
1️⃣ Vor Ort (Smartphone/Tablet)
   └─ Kundendaten erfassen
   └─ Anlagen dokumentieren
   └─ Beschriftungen notieren

2️⃣ Datentransfer
   └─ Export auf Handy
   └─ Dateien auf PC kopieren
   └─ Import am PC

3️⃣ Büro (Computer)
   └─ Beschriftungen exportieren
   └─ ODS-Datei öffnen (LibreOffice/Excel)
   └─ Ausdrucken und zuschneiden
   └─ In Hager UZ005 einlegen

4️⃣ Dokumentation
   └─ Kunde Text Export
   └─ Anlagendoku ausdrucken
   └─ In Schaltschranktür heften
```

---

## 💾 Datenverwaltung - Einfach & Transparent

### Wo werden meine Daten gespeichert?

Alle Daten werden **transparent und zugänglich** im Dokumente-Ordner gespeichert:

**Windows:**
```
C:\Users\[IhrName]\Documents\Verteiler_Beschriften\
├── anlagen_daten.json          # Alle Ihre Kunden & Anlagen
├── app_settings.json           # Ihre Einstellungen
├── Export\                     # Ihre Sicherungen
└── Import\                     # Für Datenimport
```

**Linux:**
```
~/Documents/Verteiler_Beschriften/
oder
~/Dokumente/Verteiler_Beschriften/
└── (gleiche Struktur wie Windows)
```

**Android:**
```
/storage/emulated/0/Documents/Verteiler_Beschriften/
└── (gleiche Struktur)
```

### ✅ Vorteile

- 👁️ **Keine versteckten Daten** - Sie sehen immer wo Ihre Daten sind
- 📂 **Direkter Zugriff** - Dateien mit jedem Dateimanager erreichbar
- 💾 **Einfache Backups** - Kopieren Sie einfach den ganzen Ordner
- 🔄 **Geräteübergreifend** - Gleiche Struktur auf allen Plattformen

---

## 🔄 Daten sichern & zwischen Geräten übertragen

### Daten sichern (Backup erstellen)

1. **Einstellungen öffnen**: Button "EINSTELLUNGEN"
2. **Export starten**: Button "📤 Export zu Documents"
3. **Fertig!** Die Dateien liegen im `Export/` Ordner mit Zeitstempel

**Exportierte Dateien:**
```
Export/
├── Verteiler_Daten_20260109_143052.json
└── Verteiler_Einstellungen_20260109_143052.json
```

### Daten wiederherstellen oder übertragen

**Variante 1: Automatischer Import (empfohlen)**
1. **Import-Button**: Button "📥 Import von Documents"
2. **Datei wählen**: Gewünschte JSON-Datei auswählen
3. **Import-Option wählen**:
   - **Überschreiben** - Alle Daten ersetzen (für Wiederherstellung)
   - **Zusammenführen** - Neue Kunden hinzufügen, bestehende behalten
   - **Abbrechen** - Nichts ändern

**Variante 2: Manuell**
- Legen Sie die JSON-Datei in den `Import/` Ordner
- Nutzen Sie dann den Import-Button

### Geräte-Synchronisation

**Von Android → PC:**
1. Android: Export erstellen
2. Dateien auf PC kopieren (USB-Kabel, Cloud, E-Mail, etc.)
3. PC: Import-Funktion nutzen

**Von PC → Android:**
1. PC: Export erstellen  
2. Dateien auf Android kopieren
3. Android: Import-Funktion nutzen

---

## 📱 Beschriftungsformat - So geht's

Die App unterstützt drei praktische Formate für Beschriftungen:

### Einzelne Spalte
```
1 Heizung
2 Lüftung
5 Beleuchtung
```
→ Jede Beschriftung belegt genau eine Spalte

### Spaltenbereich
```
3-6 Lüftung RLT-Anlage
7-10 Elektrik Maschine 1
```
→ Beschriftung erstreckt sich über mehrere Spalten (von-bis)

### Spalten plus weitere
```
7+5 Elektrik Hauptverteiler
```
→ Start bei Spalte 7, plus 5 weitere = Spalten 7-12

### Tipps
- ✅ Eine Beschriftung pro Zeile
- ✅ Format: `Spaltennummer(n) Beschreibung`
- ✅ Leerzeichen oder Tab zwischen Nummer und Text
- ❌ Keine Überlappungen erlaubt

---

## ⚙️ Einstellungen anpassen

In den Einstellungen können Sie die App nach Ihren Wünschen konfigurieren:

### Standard-Werte
- **Felder & Reihen**: Vorgabe für neue Anlagen (Standard: 3 × 7)
- **Datumsformat**: DE, ISO, EN oder Kurz
- **Zeilenumbruch-Zeichen**: Für mehrzeilige Beschriftungen (Standard: `;`)

### Tabellen-Design
- **Schriftgrößen**: Für Beschriftungen und Inhalte
- **Spaltenbreite**: In Zentimetern
- **Zeilenhöhe**: Beschriftungs- und Inhaltszeilen
- **Umrandung**: Zellen umranden ein/aus

### Seiten-Layout
- **Seitenränder**: Oben, Unten, Links, Rechts (in cm)

---

## 🎓 Häufige Fragen (FAQ)

<details>
<summary><strong>❓ Wo finde ich meine exportierten Tabellen?</strong></summary>

Die ODS-Dateien werden automatisch gespeichert in:
- **Desktop**: `~/Documents/Verteiler_Beschriften/[Kundenname]/`
- **Android**: `/storage/emulated/0/Documents/Verteiler_Beschriften/[Kundenname]/`

Dateiname: `Kunde_[Name]_Anlage_[ID]_[Datum-Zeit].ods`
</details>

<details>
<summary><strong>❓ Kann ich die ODS-Dateien in Excel öffnen?</strong></summary>

Ja! ODS ist ein Standard-Format und kann geöffnet werden mit:
- ✅ LibreOffice Calc (kostenlos, empfohlen)
- ✅ Microsoft Excel
- ✅ Google Sheets (online)
- ✅ WPS Office
</details>

<details>
<summary><strong>❓ Wie übertrage ich Daten vom Handy zum PC?</strong></summary>

Mehrere Möglichkeiten:
1. **USB-Kabel**: Dateien direkt kopieren
2. **Cloud**: Google Drive, Dropbox, etc.
3. **E-Mail**: JSON-Dateien als Anhang senden
4. **Netzwerk**: Über WLAN/LAN teilen
</details>

<details>
<summary><strong>❓ Was passiert beim Import mit "Zusammenführen"?</strong></summary>

- **Neue Kunden** werden hinzugefügt
- **Bestehende Kunden** bleiben unverändert
- Ideal wenn Sie Daten von mehreren Geräten kombinieren möchten
</details>

<details>
<summary><strong>❓ Gehen meine Daten verloren wenn ich die App deinstalliere?</strong></summary>

**Nein!** Ihre Daten liegen im Documents-Ordner, nicht im App-Ordner:
- ✅ Überleben App-Deinstallation
- ✅ Können manuell gesichert werden
- ✅ Sind für Sie immer zugänglich

**Tipp**: Erstellen Sie regelmäßig Backups mit dem Export-Button!
</details>

<details>
<summary><strong>❓ Kann ich die App auf mehreren Geräten gleichzeitig nutzen?</strong></summary>

Ja! Nutzen Sie Export/Import um Daten zu synchronisieren:
1. Gerät A: Export erstellen
2. Dateien zu Gerät B kopieren
3. Gerät B: Import mit "Zusammenführen"
</details>

---

## 🛠️ Technische Informationen (für IT-Interessierte)

<details>
<summary><strong>Für Entwickler & Technik-Enthusiasten</strong></summary>

### Technologie-Stack
- **UI-Framework**: Flet (Flutter-basiert) - Cross-Platform
- **Export-Format**: ODS (OpenDocument Spreadsheet)
- **Datenspeicherung**: JSON
- **Plattformen**: Linux, Windows, Android

### System-Anforderungen
- **Python**: 3.8 oder höher
- **Flet**: 0.24.0 oder höher
- **Betriebssystem**: Linux, Windows, Android

### Installation für Entwickler

```bash
# Repository klonen
git clone [repository-url]
cd anlagen_app

# Abhängigkeiten installieren
pip install -r requirements.txt

# App starten
python main.py
```

### Build-Befehle

```bash
# Desktop-Version
flet build linux        # Linux
flet build windows      # Windows  

# Mobile-Version
flet build apk          # Android

# Web-Version (experimentell)
flet run main.py --web

# Linux AppImage erstellen
./MakeAppImage.sh
```

### Projekt-Struktur
```
anlagen_app/
├── main.py                 # Hauptanwendung
├── constants.py            # Konstanten & Einstellungen
├── data_manager.py         # Daten-Management
├── ui_builder.py           # UI-Komponenten
├── odf_exporter.py         # ODS-Export
├── ods_manual.py           # ODS-Erstellung
├── odt_manual.py           # ODT-Dokumentation
└── requirements.txt        # Dependencies
```

### Android-spezifisch
- **Permissions**: Automatisch konfiguriert via pyproject.toml
- **Storage**: `/storage/emulated/0/Documents/`
- **UI**: Automatischer Padding für System-Overlays

</details>

---

## 📄 Lizenz & Nutzung

**Proprietäre Software - Alle Rechte vorbehalten**

Copyright © 2026 Volker Heggemann

### Erlaubte Nutzung
✅ **Private, nicht-kommerzielle Nutzung** - Kostenlos und uneingeschränkt

### Nicht erlaubt
❌ Kommerzielle Nutzung  
❌ Weiterverbreitung  
❌ Veränderung des Quellcodes  

### Kommerzielle Lizenz gewünscht?
Für gewerbliche Nutzung oder andere Lizenzmodelle kontaktieren Sie:

**Volker Heggemann**  
📧 vohegg@gmail.com

Details siehe [LICENSE](LICENSE) Datei.

---

## 💡 Support & Kontakt

### 🐛 Problem gefunden?
Beschreiben Sie das Problem und senden Sie es an: vohegg@gmail.com

### 💬 Fragen oder Anregungen?
Kontaktieren Sie uns unter: vohegg@gmail.com

### 🌟 Sie mögen die App?
Feedback ist immer willkommen!

---

<p align="center">
  <strong>Optimiert für Hager UZ005 Beschriftungshalterungen</strong><br>
  <em>Professionelle Verteilungsbeschriftung - einfach, mobil, zuverlässig!</em>
</p>

---

**Version 3.1.0** | Letzte Aktualisierung: Januar 2026
