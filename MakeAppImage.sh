#!/bin/bash

# Projektordner (dieses Script liegt hier)
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Appname = Name des Projektordners
APPNAME="$(basename "$PROJECT_DIR")"

# lowercase für Flet-Build
APPNAME_LOWER="$(echo "$APPNAME" | tr '[:upper:]' '[:lower:]')"

# Prüfen, ob der Appname ermittelt werden konnte
if [ -z "$APPNAME_LOWER" ]; then
    echo "Fehler: Appname konnte nicht ermittelt werden. Bitte Script direkt im Projektordner ausführen."
    exit 1
fi

# Build-Verzeichnis
BUILDDIR="$PROJECT_DIR/build/linux"

# Prüfen, ob Build existiert
if [ ! -d "$BUILDDIR" ]; then
    echo "Fehler: Build-Verzeichnis $BUILDDIR wurde nicht gefunden."
    echo "Bitte zuerst den Flet-Build ausführen."
    exit 1
fi

# AppDir für AppImage
APPDIR="$PROJECT_DIR/AppDir"

# Icon-Pfade
ICON_PNG="$PROJECT_DIR/src/assets/icon.png"
ICON_JPG="$PROJECT_DIR/src/assets/icon.jpg"
ICON=""

# Icon auswählen (aber keinen Dummy mehr erzeugen)
if [ -f "$ICON_PNG" ]; then
    ICON="$ICON_PNG"
elif [ -f "$ICON_JPG" ]; then
    ICON="$ICON_JPG"
else
    echo "Hinweis: Kein Icon unter src/assets/icon.png oder icon.jpg gefunden – baue AppImage ohne Icon-Datei."
fi

# AppDir neu erstellen
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"

# Build kopieren
cp -r "$BUILDDIR/"* "$APPDIR/usr/bin/"

# Assets kopieren (wichtig für Flet!)
if [ -d "$PROJECT_DIR/src/assets" ]; then
    cp -r "$PROJECT_DIR/src/assets" "$APPDIR/usr/bin/"
fi

# AppRun erzeugen
cat << EOF > "$APPDIR/AppRun"
#!/bin/bash
HERE="\$(dirname "\$(readlink -f "\$0")")"
exec "\$HERE/usr/bin/$APPNAME_LOWER"
EOF
chmod +x "$APPDIR/AppRun"

# Desktop-Datei erzeugen
cat << EOF > "$APPDIR/$APPNAME.desktop"
[Desktop Entry]
Name=$APPNAME
Exec=$APPNAME_LOWER
Icon=$APPNAME
Type=Application
Categories=Utility;
EOF

# Icon nur kopieren, wenn vorhanden
if [ -n "$ICON" ]; then
    cp "$ICON" "$APPDIR/$APPNAME.png"
fi

# appimagetool herunterladen, falls nicht vorhanden
if [ ! -f "$PROJECT_DIR/appimagetool-x86_64.AppImage" ]; then
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage \
        -O "$PROJECT_DIR/appimagetool-x86_64.AppImage"
    chmod +x "$PROJECT_DIR/appimagetool-x86_64.AppImage"
fi

# AppImage bauen
"$PROJECT_DIR/appimagetool-x86_64.AppImage" "$APPDIR"
