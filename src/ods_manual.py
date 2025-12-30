#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manuelle ODS/ODT Erstellung für Android (ohne odfpy)."""

import io
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime


def create_ods_manual(data, settings, output_path):
    """Erstellt ODS-Datei manuell mit zipfile und XML.
    
    Args:
        data: Dictionary mit Tabellendaten
        settings: Settings Dictionary
        output_path: Ausgabepfad
    """
    # Namespace Definitionen
    NS = {
        'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
        'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
        'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
        'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
        'fo': 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0',
        'manifest': 'urn:oasis:names:tc:opendocument:xmlns:manifest:1.0',
    }
    
    # Registriere Namespaces
    for prefix, uri in NS.items():
        ET.register_namespace(prefix, uri)
    
    # Erstelle ZIP
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 1. mimetype (MUSS erste Datei sein, unkomprimiert)
        zf.writestr('mimetype', 
                    'application/vnd.oasis.opendocument.spreadsheet',
                    compress_type=zipfile.ZIP_STORED)
        
        # 2. manifest.xml
        manifest = create_manifest_xml(NS)
        zf.writestr('META-INF/manifest.xml', 
                    ET.tostring(manifest, encoding='utf-8', xml_declaration=True))
        
        # 3. content.xml
        content = create_content_xml(data, settings, NS)
        zf.writestr('content.xml',
                    ET.tostring(content, encoding='utf-8', xml_declaration=True))
        
        # 4. styles.xml
        styles = create_styles_xml(settings, NS)
        zf.writestr('styles.xml',
                    ET.tostring(styles, encoding='utf-8', xml_declaration=True))
        
        # 5. meta.xml
        meta = create_meta_xml(NS)
        zf.writestr('meta.xml',
                    ET.tostring(meta, encoding='utf-8', xml_declaration=True))


def create_manifest_xml(NS):
    """Erstellt META-INF/manifest.xml."""
    manifest = ET.Element(f'{{{NS["manifest"]}}}manifest',
                         attrib={f'{{{NS["manifest"]}}}version': '1.2'})
    
    files = [
        ('/', 'application/vnd.oasis.opendocument.spreadsheet'),
        ('content.xml', 'text/xml'),
        ('styles.xml', 'text/xml'),
        ('meta.xml', 'text/xml'),
    ]
    
    for path, media_type in files:
        ET.SubElement(manifest, f'{{{NS["manifest"]}}}file-entry',
                     attrib={
                         f'{{{NS["manifest"]}}}full-path': path,
                         f'{{{NS["manifest"]}}}media-type': media_type
                     })
    
    return manifest


def create_meta_xml(NS):
    """Erstellt meta.xml mit Metadaten."""
    root = ET.Element(f'{{{NS["office"]}}}document-meta',
                     attrib={f'{{{NS["office"]}}}version': '1.2'})
    
    meta = ET.SubElement(root, f'{{{NS["office"]}}}meta')
    
    # Generator
    gen = ET.SubElement(meta, 'meta:generator')
    gen.text = 'Verteiler-Beschriften/2.3.4'
    
    # Datum
    now = datetime.now().isoformat()
    creation = ET.SubElement(meta, 'meta:creation-date')
    creation.text = now
    
    return root


def create_styles_xml(settings, NS):
    """Erstellt styles.xml mit Page Layout und Styles."""
    root = ET.Element(f'{{{NS["office"]}}}document-styles',
                     attrib={f'{{{NS["office"]}}}version': '1.2'})
    
    # Automatische Styles
    auto_styles = ET.SubElement(root, f'{{{NS["office"]}}}automatic-styles')
    
    # Page Layout
    page_layout = ET.SubElement(auto_styles, f'{{{NS["style"]}}}page-layout',
                                attrib={f'{{{NS["style"]}}}name': 'PageLayout1'})
    
    page_props = ET.SubElement(page_layout, f'{{{NS["style"]}}}page-layout-properties',
                              attrib={
                                  f'{{{NS["fo"]}}}page-width': f"{settings.get('seite_breite', 29.7)}cm",
                                  f'{{{NS["fo"]}}}page-height': f"{settings.get('seite_hoehe', 21.0)}cm",
                                  f'{{{NS["fo"]}}}margin-top': f"{settings.get('rand_oben', 2.0)}cm",
                                  f'{{{NS["fo"]}}}margin-bottom': f"{settings.get('rand_unten', 2.0)}cm",
                                  f'{{{NS["fo"]}}}margin-left': f"{settings.get('rand_links', 2.0)}cm",
                                  f'{{{NS["fo"]}}}margin-right': f"{settings.get('rand_rechts', 2.0)}cm",
                                  'style:print-orientation': 'landscape',
                              })
    
    # Master Styles
    master_styles = ET.SubElement(root, f'{{{NS["office"]}}}master-styles')
    master_page = ET.SubElement(master_styles, f'{{{NS["style"]}}}master-page',
                               attrib={
                                   f'{{{NS["style"]}}}name': 'Default',
                                   f'{{{NS["style"]}}}page-layout-name': 'PageLayout1'
                               })
    
    return root


def create_content_xml(data, settings, NS):
    """Erstellt content.xml mit Tabellendaten."""
    root = ET.Element(f'{{{NS["office"]}}}document-content',
                     attrib={f'{{{NS["office"]}}}version': '1.2'})
    
    # Automatische Styles
    auto_styles = ET.SubElement(root, f'{{{NS["office"]}}}automatic-styles')
    
    # Spalten Style
    col_style = ET.SubElement(auto_styles, f'{{{NS["style"]}}}style',
                             attrib={
                                 f'{{{NS["style"]}}}name': 'co1',
                                 f'{{{NS["style"]}}}family': 'table-column'
                             })
    ET.SubElement(col_style, f'{{{NS["style"]}}}table-column-properties',
                 attrib={f'{{{NS["style"]}}}column-width': f"{settings.get('spalten_breite', 1.75)}cm"})
    
    # Row Styles
    beschr_row = ET.SubElement(auto_styles, f'{{{NS["style"]}}}style',
                              attrib={
                                  f'{{{NS["style"]}}}name': 'ro1',
                                  f'{{{NS["style"]}}}family': 'table-row'
                              })
    ET.SubElement(beschr_row, f'{{{NS["style"]}}}table-row-properties',
                 attrib={f'{{{NS["style"]}}}row-height': f"{settings.get('beschriftung_row_hoehe', 0.5)}cm"})
    
    inhalt_row = ET.SubElement(auto_styles, f'{{{NS["style"]}}}style',
                              attrib={
                                  f'{{{NS["style"]}}}name': 'ro2',
                                  f'{{{NS["style"]}}}family': 'table-row'
                              })
    ET.SubElement(inhalt_row, f'{{{NS["style"]}}}table-row-properties',
                 attrib={f'{{{NS["style"]}}}row-height': f"{settings.get('inhalt_row_hoehe', 0.5)}cm"})
    
    # Cell Styles
    border = '0.5pt solid #000000' if settings.get('zellen_umrandung', True) else 'none'
    
    # Beschriftung Cell
    beschr_cell = ET.SubElement(auto_styles, f'{{{NS["style"]}}}style',
                               attrib={
                                   f'{{{NS["style"]}}}name': 'ce1',
                                   f'{{{NS["style"]}}}family': 'table-cell'
                               })
    ET.SubElement(beschr_cell, f'{{{NS["style"]}}}table-cell-properties',
                 attrib={
                     f'{{{NS["fo"]}}}border': border,
                     f'{{{NS["style"]}}}vertical-align': 'top',
                 })
    ET.SubElement(beschr_cell, f'{{{NS["style"]}}}text-properties',
                 attrib={
                     f'{{{NS["fo"]}}}font-size': f"{settings.get('fontsize_beschriftung_zelle', 7)}pt",
                     f'{{{NS["fo"]}}}font-weight': 'bold',
                 })
    ET.SubElement(beschr_cell, f'{{{NS["style"]}}}paragraph-properties',
                 attrib={f'{{{NS["fo"]}}}text-align': 'center'})
    
    # Gemergte Cell
    merged_cell = ET.SubElement(auto_styles, f'{{{NS["style"]}}}style',
                               attrib={
                                   f'{{{NS["style"]}}}name': 'ce2',
                                   f'{{{NS["style"]}}}family': 'table-cell'
                               })
    ET.SubElement(merged_cell, f'{{{NS["style"]}}}table-cell-properties',
                 attrib={
                     f'{{{NS["fo"]}}}border': border,
                     f'{{{NS["style"]}}}vertical-align': 'top',
                 })
    ET.SubElement(merged_cell, f'{{{NS["style"]}}}text-properties',
                 attrib={
                     f'{{{NS["fo"]}}}font-size': f"{settings.get('fontsize_gemergte_zelle', 7)}pt",
                     f'{{{NS["fo"]}}}font-weight': 'bold',
                 })
    ET.SubElement(merged_cell, f'{{{NS["style"]}}}paragraph-properties',
                 attrib={f'{{{NS["fo"]}}}text-align': 'center'})
    
    # Inhalt Cell
    inhalt_cell = ET.SubElement(auto_styles, f'{{{NS["style"]}}}style',
                               attrib={
                                   f'{{{NS["style"]}}}name': 'ce3',
                                   f'{{{NS["style"]}}}family': 'table-cell'
                               })
    ET.SubElement(inhalt_cell, f'{{{NS["style"]}}}table-cell-properties',
                 attrib={
                     f'{{{NS["fo"]}}}border': border,
                     f'{{{NS["style"]}}}vertical-align': 'top',
                 })
    ET.SubElement(inhalt_cell, f'{{{NS["style"]}}}text-properties',
                 attrib={f'{{{NS["fo"]}}}font-size': f"{settings.get('fontsize_inhalt_zelle', 6)}pt"})
    ET.SubElement(inhalt_cell, f'{{{NS["style"]}}}paragraph-properties',
                 attrib={f'{{{NS["fo"]}}}text-align': 'center'})
    
    # Body
    body = ET.SubElement(root, f'{{{NS["office"]}}}body')
    spreadsheet = ET.SubElement(body, f'{{{NS["office"]}}}spreadsheet')
    
    # Tabelle
    table = ET.SubElement(spreadsheet, f'{{{NS["table"]}}}table',
                         attrib={
                             f'{{{NS["table"]}}}name': data.get('name', 'Tabelle1'),
                             f'{{{NS["table"]}}}style-name': 'ta1'
                         })
    
    # Spalten definieren
    num_cols = data.get('num_cols', 12)
    for _ in range(num_cols):
        ET.SubElement(table, f'{{{NS["table"]}}}table-column',
                     attrib={f'{{{NS["table"]}}}style-name': 'co1'})
    
    # Rows mit Daten
    rows = data.get('rows', [])
    for row_data in rows:
        row_style = 'ro1' if row_data.get('is_header', False) else 'ro2'
        row = ET.SubElement(table, f'{{{NS["table"]}}}table-row',
                           attrib={f'{{{NS["table"]}}}style-name': row_style})
        
        for cell_data in row_data.get('cells', []):
            cell_attribs = {f'{{{NS["table"]}}}style-name': cell_data.get('style', 'ce3')}
            
            # Merged cells
            if cell_data.get('colspan', 1) > 1:
                cell_attribs[f'{{{NS["table"]}}}number-columns-spanned'] = str(cell_data['colspan'])
            
            cell = ET.SubElement(row, f'{{{NS["table"]}}}table-cell', attrib=cell_attribs)
            
            # Text
            if cell_data.get('text'):
                p = ET.SubElement(cell, f'{{{NS["text"]}}}p')
                p.text = cell_data['text']
            
            # Covered cells nach merged cell
            for _ in range(cell_data.get('colspan', 1) - 1):
                ET.SubElement(row, f'{{{NS["table"]}}}covered-table-cell')
    
    return root
