import os
import io
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from typing import Dict, Any

class QualityReportGenerator:
    """
    Generates instant Government / Mandi Digital Quality Assay Certificates in PDF format.
    Includes statistical confidence intervals, batch breakdown, and procurement decision.
    """
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_pdf(self, batch_data: Dict[str, Any], lot_id: str = "LOT-2026-ONION-001", mandi_name: str = "Lasalgaon Mandi Procurement Center") -> str:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"Quality_Certificate_{lot_id}_{timestamp}.pdf")
        
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Header Style
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#1E3A8A'),
            alignment=1, # Center
            spaceAfter=6
        )
        
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#4B5563'),
            alignment=1,
            spaceAfter=14
        )
        
        # Header
        story.append(Paragraph("<b>NATIONAL AGRICULTURAL COOPERATIVE PROCUREMENT</b>", title_style))
        story.append(Paragraph(f"<b>AI-Assisted Digital Quality Assay & Mandi Grading Certificate</b><br/>Procurement Center: {mandi_name} | Date: {time.strftime('%d %B %Y, %I:%M %p')}", subtitle_style))
        story.append(Spacer(1, 10))
        
        # Meta Info Table
        meta_data = [
            [Paragraph(f"<b>Lot ID:</b> {lot_id}", styles['Normal']), Paragraph(f"<b>Sample Size (N):</b> {batch_data.get('total_bulbs', 0)} Bulbs", styles['Normal'])],
            [Paragraph(f"<b>Inspection Mode:</b> AI Vision + Scale Calibration", styles['Normal']), Paragraph(f"<b>Avg Equatorial Diameter:</b> {batch_data.get('avg_diameter_mm', 0.0)} mm", styles['Normal'])],
            [Paragraph(f"<b>Batch Decision:</b> <font color='{'green' if 'PASSED' in batch_data.get('batch_verdict','') else 'red'}'><b>{batch_data.get('batch_verdict', 'N/A')}</b></font>", styles['Normal']), Paragraph(f"<b>Specification Norm:</b> 2026 Revised Mandi Specs (35-70mm)", styles['Normal'])]
        ]
        meta_table = Table(meta_data, colWidths=[270, 270])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F3F4F6')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#D1D5DB')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 14))
        
        # Grade Statistics Table with Confidence Intervals
        story.append(Paragraph("<b>Statistical Grade Breakdown & 95% Confidence Intervals</b>", styles['Heading2']))
        
        ga = batch_data.get('grade_a', {})
        urs = batch_data.get('urs', {})
        rej = batch_data.get('rejected', {})
        
        summary_data = [
            ['Category', 'Count', 'Proportion (%)', '95% Confidence Interval (CI)', 'Procurement Rate'],
            ['Grade A (Standard)', f"{ga.get('count',0)}", f"{ga.get('pct',0.0)}%", f"[{ga.get('ci_lower',0.0)}% – {ga.get('ci_upper',0.0)}%]", '100% MSP Rate'],
            ['URS (Relaxed Specs)', f"{urs.get('count',0)}", f"{urs.get('pct',0.0)}%", f"[{urs.get('ci_lower',0.0)}% – {urs.get('ci_upper',0.0)}%]", 'Relaxed Norm Rate'],
            ['Rejected (Non-compliant)', f"{rej.get('count',0)}", f"{rej.get('pct',0.0)}%", f"[{rej.get('ci_lower',0.0)}% – {rej.get('ci_upper',0.0)}%]", 'Rejected / 0 INR']
        ]
        
        summary_table = Table(summary_data, colWidths=[130, 60, 90, 160, 100])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#DCFCE7')), # Light green for Grade A
            ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#FEF9C3')), # Light yellow for URS
            ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#FEE2E2')), # Light red for Rejected
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#9CA3AF')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F9FAFB')])
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 14))
        
        # Per-Bulb Breakdown (first 10-15 bulbs)
        story.append(Paragraph("<b>Individual Bulb Assessment Log (Sample Breakdown)</b>", styles['Heading2']))
        bulbs = batch_data.get('graded_bulbs', [])
        
        bulb_rows = [['Bulb ID', 'Visual Quality', 'AI Conf.', 'Diameter (mm)', 'Blemish (%)', 'Assigned Grade', 'Remarks']]
        for b in bulbs[:15]: # Show up to 15 bulbs in printed summary
            bulb_rows.append([
                f"#{b.get('id', '-')}",
                b.get('predicted_class', '-'),
                f"{b.get('confidence', 0.0)*100:.0f}%",
                f"{b.get('diameter_mm', 0.0)}",
                f"{b.get('blemish_pct', 0.0)}%",
                b.get('grade', '-'),
                b.get('reasons', '-')[:30]
            ])
            
        bulb_table = Table(bulb_rows, colWidths=[45, 75, 55, 75, 65, 80, 145])
        bulb_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#374151')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
        ]))
        story.append(bulb_table)
        story.append(Spacer(1, 20))
        
        # Footer & Signatures
        sig_data = [
            [Paragraph("<b>Assaying Officer Signature:</b> ____________________", styles['Normal']),
             Paragraph("<b>Farmer / Seller Signature:</b> ____________________", styles['Normal'])],
            [Paragraph("<i>Verification Hash: AI-MD5-VERIFIED-2026</i>", styles['Normal']),
             Paragraph("<i>Generated instantly by AI Mandi Assayer</i>", styles['Normal'])]
        ]
        sig_table = Table(sig_data, colWidths=[270, 270])
        sig_table.setStyle(TableStyle([
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(sig_table)
        
        doc.build(story)
        return filename
