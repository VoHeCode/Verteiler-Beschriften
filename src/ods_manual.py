#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manuelle ODS/ODT Erstellung für Android (ohne odfpy)."""

import io
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime

WATERMARK_TEXT = "Verteiler beschriften (C) 2026 vohegg@gmail.com"
WATERMARK_COLOR = "#666666"  # Dunkelgrau zum Testen
def create_ods_manual(data, settings, output_path, footer_data=None):
    """Erstellt ODS-Datei manuell mit zipfile und XML.
    
    Args:
        data: Dictionary mit Tabellendaten
        settings: Settings Dictionary
        output_path: Ausgabepfad
        footer_data: Optional - Dictionary mit Fußzeilen-Daten
                    {filepath, kunde, projekt, code, beschreibung}
    """
    # Namespace Definitionen
    NS = {
        'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
        'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
        'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
        'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
        'fo': 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0',
        'svg': 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0',
        'draw': 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0',
        'loext': 'urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0',
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
        content = create_content_xml(data, settings, NS, footer_data)
        zf.writestr('content.xml',
                    ET.tostring(content, encoding='utf-8', xml_declaration=True))
        
        # 4. styles.xml
        styles = create_styles_xml(settings, NS, footer_data)
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


def create_styles_xml(settings, NS, footer_data=None):
    """Erstellt styles.xml mit Page Layout, Header, Footer und Styles."""
    root = ET.Element(f'{{{NS["office"]}}}document-styles',
                     attrib={f'{{{NS["office"]}}}version': '1.2'})
    
    # Automatische Styles
    auto_styles = ET.SubElement(root, f'{{{NS["office"]}}}automatic-styles')
    
    # Text-Style MT1 für Header (10pt)
    text_style_header = ET.SubElement(auto_styles, f'{{{NS["style"]}}}style',
                              attrib={
                                  f'{{{NS["style"]}}}name': 'MT1',
                                  f'{{{NS["style"]}}}family': 'text'
                              })
    ET.SubElement(text_style_header, f'{{{NS["style"]}}}text-properties',
                 attrib={
                     f'{{{NS["fo"]}}}font-size': '10pt',
                     f'{{{NS["fo"]}}}font-family': 'Liberation Sans',
                 })
    
    # Text-Style MT2 für Footer (6pt)
    text_style_footer = ET.SubElement(auto_styles, f'{{{NS["style"]}}}style',
                              attrib={
                                  f'{{{NS["style"]}}}name': 'MT2',
                                  f'{{{NS["style"]}}}family': 'text'
                              })
    ET.SubElement(text_style_footer, f'{{{NS["style"]}}}text-properties',
                 attrib={
                     f'{{{NS["fo"]}}}font-size': '6pt',
                     f'{{{NS["fo"]}}}font-family': 'Liberation Sans',
                 })
    
    # Page Layout mit Header/Footer-Style
    page_layout = ET.SubElement(auto_styles, f'{{{NS["style"]}}}page-layout',
                                attrib={f'{{{NS["style"]}}}name': 'PageLayout1'})
    
    page_props = ET.SubElement(page_layout, f'{{{NS["style"]}}}page-layout-properties',
                              attrib={
                                  f'{{{NS["fo"]}}}page-width': f"{settings.get('seite_breite', 29.7)}cm",
                                  f'{{{NS["fo"]}}}page-height': f"{settings.get('seite_hoehe', 21.0)}cm",
                                  f'{{{NS["fo"]}}}margin-top': f"{settings.get('rand_oben', 2.0)}cm",
                                  f'{{{NS["fo"]}}}margin-bottom': f"{settings.get('rand_unten', 1.5)}cm",
                                  f'{{{NS["fo"]}}}margin-left': f"{settings.get('rand_links', 1.0)}cm",
                                  f'{{{NS["fo"]}}}margin-right': f"{settings.get('rand_rechts', 1.0)}cm",
                                  'style:print-orientation': 'landscape',
                              })
    
    # Header-Style
    header_style = ET.SubElement(page_layout, f'{{{NS["style"]}}}header-style')
    ET.SubElement(header_style, f'{{{NS["style"]}}}header-footer-properties',
                 attrib={
                     f'{{{NS["fo"]}}}min-height': '0.75cm',
                     f'{{{NS["fo"]}}}margin-left': '0cm',
                     f'{{{NS["fo"]}}}margin-right': '0cm',
                     f'{{{NS["fo"]}}}margin-bottom': '0.25cm',
                 })
    
    # Footer-Style
    footer_style = ET.SubElement(page_layout, f'{{{NS["style"]}}}footer-style')
    ET.SubElement(footer_style, f'{{{NS["style"]}}}header-footer-properties',
                 attrib={
                     f'{{{NS["svg"]}}}height': '0.75cm',
                     f'{{{NS["fo"]}}}margin-left': '0cm',
                     f'{{{NS["fo"]}}}margin-right': '0cm',
                     f'{{{NS["fo"]}}}margin-top': '0.25cm',
                 })
    
    # Master Styles
    master_styles = ET.SubElement(root, f'{{{NS["office"]}}}master-styles')
    master_page = ET.SubElement(master_styles, f'{{{NS["style"]}}}master-page',
                               attrib={
                                   f'{{{NS["style"]}}}name': 'Default',
                                   f'{{{NS["style"]}}}page-layout-name': 'PageLayout1'
                               })
    
    # Header mit 3 Regionen
    if footer_data:
        header = ET.SubElement(master_page, f'{{{NS["style"]}}}header')
        
        # Region Links: Kundenname
        region_left = ET.SubElement(header, f'{{{NS["style"]}}}region-left')
        p_left = ET.SubElement(region_left, f'{{{NS["text"]}}}p')
        p_left.text = footer_data.get('kunde', '')
        
        # Region Mitte: Projekt
        region_center = ET.SubElement(header, f'{{{NS["style"]}}}region-center')
        p_center = ET.SubElement(region_center, f'{{{NS["text"]}}}p')
        p_center.text = footer_data.get('projekt', '')
        
        # Region Rechts: Anlagenbeschreibung
        region_right = ET.SubElement(header, f'{{{NS["style"]}}}region-right')
        p_right = ET.SubElement(region_right, f'{{{NS["text"]}}}p')
        span_right = ET.SubElement(p_right, f'{{{NS["text"]}}}span',
                                  attrib={f'{{{NS["text"]}}}style-name': 'MT1'})
        span_right.text = footer_data.get('beschreibung', '')
    
    # Leerer Footer (normal)
    ET.SubElement(master_page, f'{{{NS["style"]}}}footer')
    
    # Footer-First mit 2 Regionen
    if footer_data:
        footer_first = ET.SubElement(master_page, f'{{{NS["style"]}}}footer-first')
        
        # Region Links: Dateipfad
        region_left = ET.SubElement(footer_first, f'{{{NS["style"]}}}region-left')
        p_left = ET.SubElement(region_left, f'{{{NS["text"]}}}p')
        span_left = ET.SubElement(p_left, f'{{{NS["text"]}}}span',
                                 attrib={f'{{{NS["text"]}}}style-name': 'MT2'})
        span_left.text = footer_data.get('filepath', '')
        
        # Region Rechts: Code
        region_right = ET.SubElement(footer_first, f'{{{NS["style"]}}}region-right')
        p_right = ET.SubElement(region_right, f'{{{NS["text"]}}}p')
        span_right = ET.SubElement(p_right, f'{{{NS["text"]}}}span',
                                  attrib={f'{{{NS["text"]}}}style-name': 'MT2'})
        span_right.text = footer_data.get('code', '')
    
    return root


def create_content_xml(data, settings, NS, footer_data=None):
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
                     f'{{{NS["fo"]}}}wrap-option': 'wrap',
                     f'{{{NS["style"]}}}vertical-align': 'top',
                 })
    ET.SubElement(beschr_cell, f'{{{NS["style"]}}}text-properties',
                 attrib={
                     f'{{{NS["fo"]}}}font-size': f"{settings.get('fontsize_beschriftung_zelle', 7)}pt",
                     f'{{{NS["fo"]}}}font-weight': 'bold',
                     f'{{{NS["fo"]}}}hyphenate': 'true',
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
                     f'{{{NS["fo"]}}}wrap-option': 'wrap',
                     f'{{{NS["style"]}}}vertical-align': 'top',
                 })
    ET.SubElement(merged_cell, f'{{{NS["style"]}}}text-properties',
                 attrib={
                     f'{{{NS["fo"]}}}font-size': f"{settings.get('fontsize_gemergte_zelle', 7)}pt",
                     f'{{{NS["fo"]}}}font-weight': 'bold',
                     f'{{{NS["fo"]}}}hyphenate': 'true',
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
                     f'{{{NS["fo"]}}}wrap-option': 'wrap',
                     f'{{{NS["style"]}}}vertical-align': 'top',
                 })
    ET.SubElement(inhalt_cell, f'{{{NS["style"]}}}text-properties',
                 attrib={
                     f'{{{NS["fo"]}}}font-size': f"{settings.get('fontsize_inhalt_zelle', 6)}pt",
                     f'{{{NS["fo"]}}}hyphenate': 'true',
                 })
    ET.SubElement(inhalt_cell, f'{{{NS["style"]}}}paragraph-properties',
                 attrib={f'{{{NS["fo"]}}}text-align': 'center'})
    
    # Watermark Text Style (5pt, grau)
    watermark_style = ET.SubElement(auto_styles, f'{{{NS["style"]}}}style',
                                   attrib={
                                       f'{{{NS["style"]}}}name': 'P1',
                                       f'{{{NS["style"]}}}family': 'paragraph'
                                   })
    ET.SubElement(watermark_style, f'{{{NS["style"]}}}text-properties',
                 attrib={
                     f'{{{NS["fo"]}}}font-size': '5pt',
                     f'{{{NS["fo"]}}}color': WATERMARK_COLOR,
                 })
    
    # Text Span Style für Watermark
    span_style = ET.SubElement(auto_styles, f'{{{NS["style"]}}}style',
                              attrib={
                                  f'{{{NS["style"]}}}name': 'T1',
                                  f'{{{NS["style"]}}}family': 'text'
                              })
    ET.SubElement(span_style, f'{{{NS["style"]}}}text-properties',
                 attrib={
                     f'{{{NS["fo"]}}}font-size': '5pt',
                     f'{{{NS["fo"]}}}color': WATERMARK_COLOR,
                     f'{{{NS["loext"]}}}opacity': '100%',
                 })
    
    # Watermark Graphic Style (für draw:frame)
    graphic_style = ET.SubElement(auto_styles, f'{{{NS["style"]}}}style',
                                 attrib={
                                     f'{{{NS["style"]}}}name': 'gr1',
                                     f'{{{NS["style"]}}}family': 'graphic',
                                     f'{{{NS["style"]}}}parent-style-name': 'Default'
                                 })
    ET.SubElement(graphic_style, f'{{{NS["style"]}}}graphic-properties',
                 attrib={
                     f'{{{NS["draw"]}}}stroke': 'none',
                     f'{{{NS["draw"]}}}fill': 'none',
                     f'{{{NS["draw"]}}}textarea-horizontal-align': 'left',
                     f'{{{NS["draw"]}}}textarea-vertical-align': 'bottom',
                     f'{{{NS["fo"]}}}min-height': '0.4cm',
                     f'{{{NS["loext"]}}}decorative': 'false',
                 })
    ET.SubElement(graphic_style, f'{{{NS["style"]}}}paragraph-properties',
                 attrib={
                     f'{{{NS["style"]}}}writing-mode': 'lr-tb'
                 })
    ET.SubElement(graphic_style, f'{{{NS["style"]}}}text-properties',
                 attrib={
                     f'{{{NS["fo"]}}}font-size': '5pt',
                     f'{{{NS["fo"]}}}color': WATERMARK_COLOR,
                     f'{{{NS["loext"]}}}opacity': '100%',
                 })
    
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
    absolute_row_counter = 1  # Startet bei 1
    
    for row_data in rows:
        row_style = 'ro1' if row_data.get('is_header', False) else 'ro2'
        row = ET.SubElement(table, f'{{{NS["table"]}}}table-row',
                           attrib={f'{{{NS["table"]}}}style-name': row_style})
        
        # Watermark in Zeile 2, 6, 10, 14... (row_counter ist 1, 5, 9...)
        add_watermark = (absolute_row_counter % 4 == 1)
        
        absolute_row_counter += 1  # NACH der Prüfung erhöhen
        
        for idx, cell_data in enumerate(row_data.get('cells', [])):
            cell_attribs = {f'{{{NS["table"]}}}style-name': cell_data.get('style', 'ce3')}
            
            # Merged cells
            if cell_data.get('colspan', 1) > 1:
                cell_attribs[f'{{{NS["table"]}}}number-columns-spanned'] = str(cell_data['colspan'])
            
            cell = ET.SubElement(row, f'{{{NS["table"]}}}table-cell', attrib=cell_attribs)
            
            # Watermark in erste Zelle jeder ungeraden Zeile
            if add_watermark and idx == 0:
                row_height = settings.get('inhalt_row_hoehe', 0.5)
                watermark_y = row_height - 0.05  # Relativ zur Zelle!
                
                frame = ET.SubElement(cell, f'{{{NS["draw"]}}}frame',
                                     attrib={
                                         f'{{{NS["draw"]}}}z-index': '0',
                                         f'{{{NS["draw"]}}}name': f'Watermark_{absolute_row_counter}',
                                         f'{{{NS["draw"]}}}style-name': 'gr1',
                                         f'{{{NS["draw"]}}}text-style-name': 'P1',
                                         f'{{{NS["table"]}}}table-background': 'true',
                                         f'{{{NS["svg"]}}}x': '0.001cm',
                                         f'{{{NS["svg"]}}}y': f'{watermark_y:.2f}cm',
                                         f'{{{NS["svg"]}}}width': '3cm',
                                         f'{{{NS["svg"]}}}height': '0.4cm',
                                     })
                textbox = ET.SubElement(frame, f'{{{NS["draw"]}}}text-box')
                p = ET.SubElement(textbox, f'{{{NS["text"]}}}p')
                span = ET.SubElement(p, f'{{{NS["text"]}}}span',
                                    attrib={f'{{{NS["text"]}}}style-name': 'T1'})
                span.text = WATERMARK_TEXT
            
            # Text
            if cell_data.get('text'):
                p = ET.SubElement(cell, f'{{{NS["text"]}}}p')
                p.text = cell_data['text']
            
            # Covered cells nach merged cell
            for _ in range(cell_data.get('colspan', 1) - 1):
                ET.SubElement(row, f'{{{NS["table"]}}}covered-table-cell')
    
    return root
