"""
Generazione PDF del Quaderno di Campagna
Formato conforme alla normativa italiana
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import date
from typing import List, Dict


def genera_quaderno_pdf(azienda, trattamenti, output_path: str):
    """
    Genera PDF del quaderno di campagna
    
    Args:
        azienda: Oggetto Azienda
        trattamenti: Lista di oggetti Trattamento
        output_path: Percorso file PDF da creare
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Container per gli elementi del PDF
    story = []
    
    # Stili
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#16a34a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#059669'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 9
    
    # === INTESTAZIONE ===
    story.append(Paragraph("QUADERNO DI CAMPAGNA", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # === DATI AZIENDA ===
    story.append(Paragraph("DATI AZIENDA", heading_style))
    
    dati_azienda = [
        ["Ragione Sociale:", azienda.ragione_sociale or ""],
        ["P.IVA:", azienda.p_iva or ""],
        ["Codice Fiscale:", getattr(azienda, 'codice_fiscale', None) or ""],
        ["Indirizzo:", azienda.indirizzo or ""],
        ["Comune:", getattr(azienda, 'comune', None) or ""],
        ["Provincia:", getattr(azienda, 'provincia', None) or ""],
        ["CAP:", getattr(azienda, 'cap', None) or ""],
        ["Legale Rappresentante:", azienda.legale_rappresentante or ""],
        ["Telefono:", getattr(azienda, 'telefono', None) or ""],
        ["Email:", getattr(azienda, 'email', None) or ""],
        ["N. Registro Imprese:", getattr(azienda, 'numero_registro_imprese', None) or ""],
    ]
    
    # Rimuovi righe vuote
    dati_azienda = [[k, v] for k, v in dati_azienda if v]
    
    tab_azienda = Table(dati_azienda, colWidths=[5*cm, 12*cm])
    tab_azienda.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0fdf4')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    story.append(tab_azienda)
    story.append(Spacer(1, 1*cm))
    
    # === TABELLA TRATTAMENTI ===
    if trattamenti:
        story.append(Paragraph("REGISTRO TRATTAMENTI", heading_style))
        
        # Intestazione tabella
        header = [
            "Data",
            "Campo",
            "Prodotto",
            "Tipo",
            "Avversità",
            "Dose (kg/ha)",
            "Quantità Tot.",
            "Operatore",
            "Mezzo",
            "Note"
        ]
        
        # Dati trattamenti
        data = [header]
        for tr in trattamenti:
            row = [
                tr.data.strftime("%d/%m/%Y") if tr.data else "",
                tr.campo.nome if tr.campo else "",
                tr.prodotto.nome_commerciale if tr.prodotto else "",
                tr.prodotto.tipo.value if tr.prodotto and tr.prodotto.tipo else "",
                tr.avversita or "",
                f"{tr.quantita_per_ettaro:.2f}" if tr.quantita_per_ettaro else "",
                f"{tr.quantita_totale:.2f} {tr.prodotto.unita_misura if tr.prodotto else ''}" if tr.quantita_totale else "",
                tr.operatore or "",
                tr.mezzo.nome if tr.mezzo else "",
                (tr.note or "")[:30] + "..." if tr.note and len(tr.note) > 30 else (tr.note or "")
            ]
            data.append(row)
        
        # Crea tabella
        tab_trattamenti = Table(data, colWidths=[
            2*cm,  # Data
            2.5*cm,  # Campo
            2.5*cm,  # Prodotto
            1.5*cm,  # Tipo
            2*cm,  # Avversità
            1.5*cm,  # Dose
            2*cm,  # Quantità
            2*cm,  # Operatore
            2*cm,  # Mezzo
            2*cm   # Note
        ])
        
        tab_trattamenti.setStyle(TableStyle([
            # Intestazione
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a34a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Dati
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
        ]))
        
        story.append(tab_trattamenti)
    else:
        story.append(Paragraph("Nessun trattamento registrato.", normal_style))
    
    # === FOOTER ===
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        f"<i>Documento generato il {date.today().strftime('%d/%m/%Y')} - AgriNote</i>",
        ParagraphStyle('Footer', parent=normal_style, alignment=TA_CENTER, fontSize=8, textColor=colors.grey)
    ))
    
    # Genera PDF
    doc.build(story)
    return output_path

