#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manuelle ODT-Erstellung mit ElementTree (ohne odfpy)."""

import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime

from constants import _, TOOL_FLET_VERSION


def create_odt_manual(customer_data, output_path):
    """Erstellt ODT-Datei manuell mit zipfile und ElementTree.
    
    Args:
        customer_data: Dictionary mit Kundendaten und Anlagen
        output_path: Ausgabepfad für ODT-Datei
    """
    # Namespace Definitionen
    NS = {
        'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
        'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
        'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
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
                    'application/vnd.oasis.opendocument.text',
                    compress_type=zipfile.ZIP_STORED)
        
        # 2. manifest.xml
        manifest = create_manifest_xml(NS)
        zf.writestr('META-INF/manifest.xml', 
                    ET.tostring(manifest, encoding='utf-8', xml_declaration=True))
        
        # 3. content.xml
        content = create_content_xml(customer_data, NS)
        zf.writestr('content.xml',
                    ET.tostring(content, encoding='utf-8', xml_declaration=True))
        
        # 4. meta.xml
        meta = create_meta_xml(NS)
        zf.writestr('meta.xml',
                    ET.tostring(meta, encoding='utf-8', xml_declaration=True))


def create_manifest_xml(NS):
    """Erstellt META-INF/manifest.xml."""
    manifest = ET.Element(f'{{{NS["manifest"]}}}manifest',
                         attrib={f'{{{NS["manifest"]}}}version': '1.2'})
    
    files = [
        ('/', 'application/vnd.oasis.opendocument.text'),
        ('content.xml', 'text/xml'),
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
    gen.text = _('Verteiler-Beschriften/{version}').format(version=TOOL_FLET_VERSION)
    
    # Datum
    now = datetime.now().isoformat()
    creation = ET.SubElement(meta, 'meta:creation-date')
    creation.text = now
    
    return root


def create_content_xml(customer_data, NS):
    """Erstellt content.xml mit Kundendaten."""
    root = ET.Element(f'{{{NS["office"]}}}document-content',
                     attrib={f'{{{NS["office"]}}}version': '1.2'})
    
    # Automatische Styles
    auto_styles = ET.SubElement(root, f'{{{NS["office"]}}}automatic-styles')
    
    # Style H1 (15pt bold)
    h1_style = ET.SubElement(auto_styles, f'{{{NS["style"]}}}style',
                            attrib={
                                f'{{{NS["style"]}}}name': 'H1',
                                f'{{{NS["style"]}}}family': 'paragraph'
                            })
    ET.SubElement(h1_style, f'{{{NS["style"]}}}text-properties',
                 attrib={
                     f'{{{NS["fo"]}}}font-size': '15pt',
                     f'{{{NS["fo"]}}}font-weight': 'bold'
                 })
    
    # Style H2 (13pt bold)
    h2_style = ET.SubElement(auto_styles, f'{{{NS["style"]}}}style',
                            attrib={
                                f'{{{NS["style"]}}}name': 'H2',
                                f'{{{NS["style"]}}}family': 'paragraph'
                            })
    ET.SubElement(h2_style, f'{{{NS["style"]}}}text-properties',
                 attrib={
                     f'{{{NS["fo"]}}}font-size': '13pt',
                     f'{{{NS["fo"]}}}font-weight': 'bold'
                 })
    
    # Style Bold
    bold_style = ET.SubElement(auto_styles, f'{{{NS["style"]}}}style',
                              attrib={
                                  f'{{{NS["style"]}}}name': 'Bold',
                                  f'{{{NS["style"]}}}family': 'text'
                              })
    ET.SubElement(bold_style, f'{{{NS["style"]}}}text-properties',
                 attrib={f'{{{NS["fo"]}}}font-weight': 'bold'})
    
    # Body
    body = ET.SubElement(root, f'{{{NS["office"]}}}body')
    text_body = ET.SubElement(body, f'{{{NS["office"]}}}text')
    
    # Extrahiere Daten
    customer_name = customer_data.get('kundenname', _('Unbekannt'))
    projekt = customer_data.get('projekt', '')
    datum = customer_data.get('datum', '')
    adresse = customer_data.get('adresse', '')
    plz = customer_data.get('plz', '')
    ort = customer_data.get('ort', '')
    contact_person = customer_data.get('ansprechpartner', '')
    phone_number = customer_data.get('telefonnummer', '')
    email = customer_data.get('email', '')
    electric_systems = customer_data.get('anlagen', [])
    
    # Kunde Header
    h1 = ET.SubElement(text_body, f'{{{NS["text"]}}}h',
                      attrib={
                          f'{{{NS["text"]}}}style-name': 'H1',
                          f'{{{NS["text"]}}}outline-level': '1'
                      })
    h1.text = _('Kunde: {name}').format(name=customer_name)
    
    # Leerzeile
    ET.SubElement(text_body, f'{{{NS["text"]}}}p')
    
    # Kundendaten
    add_labeled_paragraph(text_body, NS, _('Projekt'), projekt)
    add_labeled_paragraph(text_body, NS, _('Datum'), datum)
    add_labeled_paragraph(text_body, NS, _('Adresse'), adresse)
    add_labeled_paragraph(text_body, NS, _('PLZ'), plz)
    add_labeled_paragraph(text_body, NS, _('Ort'), ort)
    add_labeled_paragraph(text_body, NS, _('Ansprechpartner'), contact_person)
    add_labeled_paragraph(text_body, NS, _('Telefonnummer'), phone_number)
    add_labeled_paragraph(text_body, NS, _('E-Mail'), email)
    
    # Leerzeile
    ET.SubElement(text_body, f'{{{NS["text"]}}}p')
    
    # Anlagen
    if electric_systems:
        h2 = ET.SubElement(text_body, f'{{{NS["text"]}}}h',
                          attrib={
                              f'{{{NS["text"]}}}style-name': 'H2',
                              f'{{{NS["text"]}}}outline-level': '2'
                          })
        h2.text = _('Anlagen:')
        
        ET.SubElement(text_body, f'{{{NS["text"]}}}p')
        
        for electric_system in electric_systems:
            # Anlage Header
            p_anlage = ET.SubElement(text_body, f'{{{NS["text"]}}}p')
            span_bold = ET.SubElement(p_anlage, f'{{{NS["text"]}}}span',
                                     attrib={f'{{{NS["text"]}}}style-name': 'Bold'})
            span_bold.text = _("Anlage {id}: {beschreibung}").format(
                id=electric_system.get('id', '?'),
                beschreibung=electric_system.get('beschreibung', '')
            )
            
            # Anlage Details
            add_labeled_paragraph(text_body, NS, _('  Name'), electric_system.get('name', ''))
            add_labeled_paragraph(text_body, NS, _('  Adresse'), electric_system.get('adresse', ''))
            add_labeled_paragraph(text_body, NS, _('  PLZ/Ort'), electric_system.get('plz_ort', ''))
            
            # Lokalisierung
            if electric_system.get('gebaeude') or electric_system.get('geschoss') or electric_system.get('raum'):
                ET.SubElement(text_body, f'{{{NS["text"]}}}p')
                p_lok = ET.SubElement(text_body, f'{{{NS["text"]}}}p')
                span_lok = ET.SubElement(p_lok, f'{{{NS["text"]}}}span',
                                        attrib={f'{{{NS["text"]}}}style-name': 'Bold'})
                span_lok.text = _('  Lokalisierung:')
                add_labeled_paragraph(text_body, NS, _('    Gebäude'), electric_system.get('gebaeude', ''))
                add_labeled_paragraph(text_body, NS, _('    Geschoss'), electric_system.get('geschoss', ''))
                add_labeled_paragraph(text_body, NS, _('    Raum'), electric_system.get('raum', ''))
                add_labeled_paragraph(text_body, NS, _('    Funktion'), electric_system.get('funktion', ''))
            
            # Zähler
            if electric_system.get('zaehlernummer') or electric_system.get('zaehlerstand'):
                ET.SubElement(text_body, f'{{{NS["text"]}}}p')
                p_zaehler = ET.SubElement(text_body, f'{{{NS["text"]}}}p')
                span_zaehler = ET.SubElement(p_zaehler, f'{{{NS["text"]}}}span',
                                            attrib={f'{{{NS["text"]}}}style-name': 'Bold'})
                span_zaehler.text = _('  Zähler:')
                add_labeled_paragraph(text_body, NS, _('    Nummer'), electric_system.get('zaehlernummer', ''))
                add_labeled_paragraph(text_body, NS, _('    Stand'), electric_system.get('zaehlerstand', ''))
            
            # Export-Konfiguration
            ET.SubElement(text_body, f'{{{NS["text"]}}}p')
            p_export = ET.SubElement(text_body, f'{{{NS["text"]}}}p')
            span_export = ET.SubElement(p_export, f'{{{NS["text"]}}}span',
                                       attrib={f'{{{NS["text"]}}}style-name': 'Bold'})
            span_export.text = _('  Export-Konfiguration:')
            add_labeled_paragraph(text_body, NS, _('    Code'), electric_system.get('code', ''))
            add_labeled_paragraph(text_body, NS, _('    Felder'), str(electric_system.get('felder', 3)))
            add_labeled_paragraph(text_body, NS, _('    Reihen'), str(electric_system.get('reihen', 7)))
            
            # Beschriftungen
            if electric_system.get('text_inhalt'):
                ET.SubElement(text_body, f'{{{NS["text"]}}}p')
                p_beschr = ET.SubElement(text_body, f'{{{NS["text"]}}}p')
                span_beschr = ET.SubElement(p_beschr, f'{{{NS["text"]}}}span',
                                           attrib={f'{{{NS["text"]}}}style-name': 'Bold'})
                span_beschr.text = _('  Beschriftungen:')
                
                # Beschriftungen als vorformattierter Text
                label_lines = electric_system.get('text_inhalt', '').split('\n')
                for line in label_lines:
                    p_line = ET.SubElement(text_body, f'{{{NS["text"]}}}p')
                    p_line.text = f'    {line}'
            
            # Bemerkung
            if electric_system.get('bemerkung'):
                ET.SubElement(text_body, f'{{{NS["text"]}}}p')
                add_labeled_paragraph(text_body, NS, _('  Bemerkung'), electric_system.get('bemerkung', ''))
            
            # Leerzeile zwischen Anlagen
            ET.SubElement(text_body, f'{{{NS["text"]}}}p')
            ET.SubElement(text_body, f'{{{NS["text"]}}}p')
    
    return root


def add_labeled_paragraph(parent, NS, label, value):
    """Fügt Paragraph mit Label (fett) + Wert hinzu."""
    if not value:
        return
    
    p = ET.SubElement(parent, f'{{{NS["text"]}}}p')
    
    # Label (fett)
    span_bold = ET.SubElement(p, f'{{{NS["text"]}}}span',
                             attrib={f'{{{NS["text"]}}}style-name': 'Bold'})
    span_bold.text = f'{label}: '
    span_bold.tail = str(value)


if __name__ == "__main__":
    pass
