#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manuelle ODT-Erstellung für Android (ohne odfpy)."""

import zipfile
from datetime import datetime


def create_odt_manual(kunde_data, output_path):
    """Erstellt ODT-Datei manuell mit zipfile und XML-Strings.
    
    Args:
        kunde_data: Dictionary mit Kundendaten und Anlagen
        output_path: Ausgabepfad für ODT-Datei
    """
    
    # Extrahiere Daten
    kundenname = kunde_data.get('kundenname', 'Unbekannt')
    projekt = kunde_data.get('projekt', '')
    datum = kunde_data.get('datum', '')
    adresse = kunde_data.get('adresse', '')
    plz = kunde_data.get('plz', '')
    ort = kunde_data.get('ort', '')
    ansprechpartner = kunde_data.get('ansprechpartner', '')
    telefonnummer = kunde_data.get('telefonnummer', '')
    email = kunde_data.get('email', '')
    anlagen = kunde_data.get('anlagen', [])
    
    # Content-XML aufbauen
    content_parts = []
    
    # Header
    content_parts.append("""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    office:version="1.2">
  <office:automatic-styles>
    <style:style style:name="H1" style:family="paragraph">
      <style:text-properties fo:font-size="15pt" fo:font-weight="bold"/>
    </style:style>
    <style:style style:name="H2" style:family="paragraph">
      <style:text-properties fo:font-size="13pt" fo:font-weight="bold"/>
    </style:style>
    <style:style style:name="Bold" style:family="text">
      <style:text-properties fo:font-weight="bold"/>
    </style:style>
  </office:automatic-styles>
  <office:body>
    <office:text>
""")
    
    # Titel
    content_parts.append(f'      <text:h text:style-name="H1">Kunde: {escape_xml(kundenname)}</text:h>\n')
    content_parts.append('      <text:p></text:p>\n')
    
    # Kundendaten
    if projekt:
        content_parts.append(f'      <text:p><text:span text:style-name="Bold">Projekt:</text:span> {escape_xml(projekt)}</text:p>\n')
    if datum:
        content_parts.append(f'      <text:p><text:span text:style-name="Bold">Datum:</text:span> {escape_xml(datum)}</text:p>\n')
    if adresse:
        content_parts.append(f'      <text:p><text:span text:style-name="Bold">Adresse:</text:span> {escape_xml(adresse)}</text:p>\n')
    if plz or ort:
        content_parts.append(f'      <text:p><text:span text:style-name="Bold">PLZ/Ort:</text:span> {escape_xml(plz)} {escape_xml(ort)}</text:p>\n')
    if ansprechpartner:
        content_parts.append(f'      <text:p><text:span text:style-name="Bold">Ansprechpartner:</text:span> {escape_xml(ansprechpartner)}</text:p>\n')
    if telefonnummer:
        content_parts.append(f'      <text:p><text:span text:style-name="Bold">Telefon:</text:span> {escape_xml(telefonnummer)}</text:p>\n')
    if email:
        content_parts.append(f'      <text:p><text:span text:style-name="Bold">E-Mail:</text:span> {escape_xml(email)}</text:p>\n')
    
    content_parts.append('      <text:p></text:p>\n')
    
    # Anlagen
    content_parts.append('      <text:h text:style-name="H1">Anlagen</text:h>\n')
    content_parts.append('      <text:p></text:p>\n')
    
    for idx, anlage in enumerate(anlagen, 1):
        beschreibung = anlage.get('beschreibung', f'Anlage {idx}')
        content_parts.append(f'      <text:h text:style-name="H2">{idx}. {escape_xml(beschreibung)}</text:h>\n')
        
        # Anlagendetails
        code = anlage.get('code', '')
        bemerkung = anlage.get('bemerkung', '')
        
        # Lokalisierung
        name = anlage.get('name', '')
        anlage_adresse = anlage.get('adresse', '')
        plz_ort = anlage.get('plz_ort', '')
        raum = anlage.get('raum', '')
        gebaeude = anlage.get('gebaeude', '')
        geschoss = anlage.get('geschoss', '')
        funktion = anlage.get('funktion', '')
        
        if code:
            content_parts.append(f'      <text:p><text:span text:style-name="Bold">Code:</text:span> {escape_xml(code)}</text:p>\n')
        if bemerkung:
            content_parts.append(f'      <text:p><text:span text:style-name="Bold">Bemerkung:</text:span> {escape_xml(bemerkung)}</text:p>\n')
        
        if any([name, anlage_adresse, plz_ort, raum, gebaeude, geschoss, funktion]):
            content_parts.append('      <text:p><text:span text:style-name="Bold">Lokalisierung:</text:span></text:p>\n')
            if name:
                content_parts.append(f'      <text:p>  Name: {escape_xml(name)}</text:p>\n')
            if anlage_adresse:
                content_parts.append(f'      <text:p>  Adresse: {escape_xml(anlage_adresse)}</text:p>\n')
            if plz_ort:
                content_parts.append(f'      <text:p>  PLZ/Ort: {escape_xml(plz_ort)}</text:p>\n')
            if gebaeude:
                content_parts.append(f'      <text:p>  Gebäude: {escape_xml(gebaeude)}</text:p>\n')
            if geschoss:
                content_parts.append(f'      <text:p>  Geschoss: {escape_xml(geschoss)}</text:p>\n')
            if raum:
                content_parts.append(f'      <text:p>  Raum: {escape_xml(raum)}</text:p>\n')
            if funktion:
                content_parts.append(f'      <text:p>  Funktion: {escape_xml(funktion)}</text:p>\n')
        
        # Zähler
        zaehlernummer = anlage.get('zaehlernummer', '')
        zaehlerstand = anlage.get('zaehlerstand', '')
        if zaehlernummer or zaehlerstand:
            content_parts.append('      <text:p><text:span text:style-name="Bold">Zähler:</text:span></text:p>\n')
            if zaehlernummer:
                content_parts.append(f'      <text:p>  Zählernummer: {escape_xml(zaehlernummer)}</text:p>\n')
            if zaehlerstand:
                content_parts.append(f'      <text:p>  Zählerstand: {escape_xml(zaehlerstand)}</text:p>\n')
        
        # Export-Konfiguration
        felder = anlage.get('felder', '')
        reihen = anlage.get('reihen', '')
        if felder or reihen:
            content_parts.append('      <text:p><text:span text:style-name="Bold">Export-Konfiguration:</text:span></text:p>\n')
            if felder:
                content_parts.append(f'      <text:p>  Felder: {escape_xml(str(felder))}</text:p>\n')
            if reihen:
                content_parts.append(f'      <text:p>  Reihen: {escape_xml(str(reihen))}</text:p>\n')
        
        # Beschriftungen
        text_inhalt = anlage.get('text_inhalt', '')
        if text_inhalt:
            content_parts.append('      <text:p><text:span text:style-name="Bold">Beschriftungen:</text:span></text:p>\n')
            for line in text_inhalt.split('\n'):
                if line.strip():
                    content_parts.append(f'      <text:p>  {escape_xml(line)}</text:p>\n')
        
        content_parts.append('      <text:p></text:p>\n')
    
    # Footer
    content_parts.append("""    </office:text>
  </office:body>
</office:document-content>
""")
    
    content_xml = ''.join(content_parts)
    
    # Manifest
    manifest_xml = """<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest
    xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
  <manifest:file-entry manifest:media-type="application/vnd.oasis.opendocument.text" manifest:full-path="/"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="content.xml"/>
</manifest:manifest>
"""
    
    # ODT erstellen
    mimetype = "application/vnd.oasis.opendocument.text"
    
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_STORED) as odt:
        # mimetype MUSS unkomprimiert und als erstes rein
        odt.writestr("mimetype", mimetype, compress_type=zipfile.ZIP_STORED)
        odt.writestr("content.xml", content_xml)
        odt.writestr("META-INF/manifest.xml", manifest_xml)


def escape_xml(text):
    """Escaped XML-Sonderzeichen."""
    if not text:
        return ''
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    return text
