#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Android-spezifische Funktionen.

Behandelt Android-spezifische Operationen wie Datei-Export/Import
über MediaStore und Downloads-Ordner.
"""

from pathlib import Path
from constants import EXPORT_DATEN_DATEI, EXPORT_SETTINGS_DATEI


def ist_android_plattform(page=None):
    """Prüft ob die App auf Android läuft.

    Args:
        page: Flet Page-Objekt (optional für Kompatibilität)

    Returns:
        bool: True wenn Android-Plattform
    """
    if page:
        return page.platform == "android"
    
    # Fallback: Java-Import Test
    try:
        from java import jclass
        return True
    except (ImportError, AttributeError):
        return False


def hole_android_klassen():
    """Importiert und gibt Android-Klassen zurück.

    Returns:
        tuple: (jclass, Intent, Activity, Environment) oder (None, None, None, None)
    """
    if not ist_android_plattform():
        return None, None, None, None

    try:
        from java import jclass
        Intent = jclass("android.content.Intent")
        Activity = jclass("android.app.Activity")

        try:
            Environment = jclass("android.os.Environment")
        except ImportError:
            Environment = None

        return jclass, Intent, Activity, Environment

    except Exception as e:
        print(f"Fehler beim Laden der Android-Klassen: {e}")
        return None, None, None, None


def schreibe_datei_zu_downloads(content_resolver, collection_uri,
                                       datei_name, quell_pfad):
    """Schreibt eine Datei in den Android Downloads-Ordner.

    Args:
        content_resolver: Android ContentResolver
        collection_uri: URI zur Downloads-Collection
        datei_name (str): Name der Zieldatei
        quell_pfad (Path): Pfad zur Quelldatei

    Returns:
        bool: True wenn erfolgreich
    """
    try:
        from java import jclass

        ContentValues = jclass("android.content.ContentValues")
        values = ContentValues()
        values.put("_display_name", datei_name)
        values.put("mime_type", "application/json")

        # Lösche existierende Datei
        selection = "_display_name = ?"
        selection_args = [datei_name]
        content_resolver.delete(collection_uri, selection, selection_args)

        # Erstelle neue Datei
        file_uri = content_resolver.insert(collection_uri, values)
        if not file_uri:
            print(f"Fehler beim Erstellen von {datei_name}")
            return False

        # Schreibe Dateiinhalt
        output_stream = content_resolver.openOutputStream(file_uri)

        with open(quell_pfad, "rb") as source:
            buffer_size = 8192
            while True:
                chunk = source.read(buffer_size)
                if not chunk:
                    break
                output_stream.write(chunk)

        output_stream.close()
        return True

    except Exception as e:
        print(f"Fehler beim Schreiben von {datei_name}: {e}")
        return False


def lese_datei_von_downloads(content_resolver, collection_uri,
                                    datei_name, ziel_pfad):
    """Liest eine Datei aus dem Android Downloads-Ordner.

    Args:
        content_resolver: Android ContentResolver
        collection_uri: URI zur Downloads-Collection
        datei_name (str): Name der Quelldatei
        ziel_pfad (Path): Pfad zur Zieldatei

    Returns:
        bool: True wenn erfolgreich
    """
    try:
        from java import jclass

        # Suche nach der exakten Datei
        projection = ["_id", "_display_name"]
        selection = "_display_name = ?"
        selection_args = [datei_name]

        cursor = content_resolver.query(
            collection_uri, projection, selection, selection_args, None
        )

        if not cursor or not cursor.moveToFirst():
            print(f"Datei {datei_name} nicht gefunden")
            if cursor:
                cursor.close()
            return False

        # Hole die URI der Datei
        Uri = jclass("android.net.Uri")
        id_column = cursor.getColumnIndexOrThrow("_id")
        file_id = cursor.getLong(id_column)
        file_uri = Uri.withAppendedPath(collection_uri, str(file_id))
        cursor.close()

        # Lese den Dateiinhalt
        input_stream = content_resolver.openInputStream(file_uri)

        with open(ziel_pfad, "wb") as dest:
            buffer_size = 8192
            while True:
                # Lese Bytes aus dem InputStream
                bytes_array = bytearray(buffer_size)
                bytes_read = input_stream.read(bytes_array)

                if bytes_read == -1:  # End of stream
                    break

                dest.write(bytes_array[:bytes_read])

        input_stream.close()
        return True

    except Exception as e:
        print(f"Fehler beim Lesen von {datei_name}: {e}")
        return False


def exportiere_android(app_impl, data_manager):
    """Exportiert Daten und Settings über Android MediaStore.

    Args:
        app_impl: App-Implementation (self._impl)
        data_manager: DataManager-Instanz

    Returns:
        tuple: (erfolg: bool, exportierte_dateien: list, fehler: str oder None)
    """
    try:
        from java import jclass

        mediastore = jclass("android.provider.MediaStore")

        # Hole Activity und Context
        activity = app_impl.native
        context = activity.getApplicationContext()
        content_resolver = context.getContentResolver()

        collection_uri = mediastore.Downloads.EXTERNAL_CONTENT_URI
        exportierte_dateien = []

        # Exportiere Daten-Datei
        daten_pfad = data_manager.get_data_file_path()
        if daten_pfad.exists():
            erfolg = schreibe_datei_zu_downloads(
                content_resolver,
                collection_uri,
                EXPORT_DATEN_DATEI,
                daten_pfad
            )
            if erfolg:
                exportierte_dateien.append(f"✓ {EXPORT_DATEN_DATEI}")

        # Exportiere Settings-Datei
        settings_pfad = data_manager.get_settings_file_path()
        if settings_pfad.exists():
            erfolg = schreibe_datei_zu_downloads(
                content_resolver,
                collection_uri,
                EXPORT_SETTINGS_DATEI,
                settings_pfad
            )
            if erfolg:
                exportierte_dateien.append(f"✓ {EXPORT_SETTINGS_DATEI}")

        if not exportierte_dateien:
            return False, [], "Keine Dateien konnten exportiert werden"

        return True, exportierte_dateien, None

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return False, [], f"{str(e)}\n\n{error_details[:500]}"


def importiere_android(app_impl, data_manager):
    """Importiert Daten und Settings über Android MediaStore.

    Args:
        app_impl: App-Implementation (self._impl)
        data_manager: DataManager-Instanz

    Returns:
        tuple: (erfolg: bool, importierte_dateien: list, fehler: str oder None)
    """
    try:
        from java import jclass

        mediastore = jclass("android.provider.MediaStore")

        # Hole Activity und Context
        activity = app_impl.native
        context = activity.getApplicationContext()
        content_resolver = context.getContentResolver()

        collection_uri = mediastore.Downloads.EXTERNAL_CONTENT_URI
        importierte_dateien = []

        # Importiere Daten-Datei
        daten_gefunden = lese_datei_von_downloads(
            content_resolver,
            collection_uri,
            EXPORT_DATEN_DATEI,
            data_manager.get_data_file_path()
        )
        if daten_gefunden:
            importierte_dateien.append(f"✓ {EXPORT_DATEN_DATEI}")

        # Importiere Settings-Datei
        settings_gefunden = lese_datei_von_downloads(
            content_resolver,
            collection_uri,
            EXPORT_SETTINGS_DATEI,
            data_manager.get_settings_file_path()
        )
        if settings_gefunden:
            importierte_dateien.append(f"✓ {EXPORT_SETTINGS_DATEI}")

        if not importierte_dateien:
            return False, [], "Keine Backup-Dateien im Downloads-Ordner gefunden"

        return True, importierte_dateien, None

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return False, [], f"{str(e)}\n\n{error_details[:300]}"


def exportiere_desktop(data_manager):
    """Desktop-Fallback für Export.

    Args:
        data_manager: DataManager-Instanz

    Returns:
        tuple: (erfolg: bool, exportierte_dateien: list, fehler: str oder None)
    """
    try:
        downloads_path = Path.home() / "Downloads"
        return data_manager.exportiere_zu_verzeichnis(downloads_path)

    except Exception as e:
        return False, [], f"Fehler beim Desktop-Export: {str(e)}"


def importiere_desktop(data_manager):
    """Desktop-Fallback für Import.

    Args:
        data_manager: DataManager-Instanz

    Returns:
        tuple: (erfolg: bool, importierte_dateien: list, fehler: str oder None)
    """
    try:
        downloads_path = Path.home() / "Downloads"

        daten_quelle = downloads_path / EXPORT_DATEN_DATEI
        settings_quelle = downloads_path / EXPORT_SETTINGS_DATEI

        if not daten_quelle.exists() and not settings_quelle.exists():
            return False, [], (
                f'Keine Backup-Dateien gefunden in: {downloads_path}\n\n'
                f'Erwartet:\n- {EXPORT_DATEN_DATEI}\n- {EXPORT_SETTINGS_DATEI}'
            )

        return data_manager.importiere_von_verzeichnis(downloads_path)

    except Exception as e:
        return False, [], f"Fehler beim Desktop-Import: {str(e)}"
