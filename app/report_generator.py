"""
report_generator.py - Professional Medical PDF Report Generator for RenalScan
Uses native ReportLab document APIs to produce publication-grade diagnostic PDF reports:
  - Document Flowables: Paragraph, Table, RLImage, Spacer, KeepTogether, HRFlowable
  - Custom NumberedCanvas: Two-pass dynamic page numbering ("Page X of Y"), running headers, running footers
  - High-contrast clinical visual styling: White background, RenalScan Red (#B9362F), Charcoal (#20283A), Slate (#6B7280)
  - Zero raw HTML/CSS leaks: All visual elements compiled to native PDF graphics and text objects
"""

import io
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import cv2
import numpy as np
from PIL import Image

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, KeepTogether, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas that accumulates page states to accurately compute total pages
    and draw professional running headers and footers on each page.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        page_w, page_h = letter

        # Running header on page 2 and later
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#20283A"))
            self.drawString(40, page_h - 26, "RENALSCAN")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#6B7280"))
            self.drawString(98, page_h - 26, "— AI-Assisted Kidney Stone Analysis Report")
            self.setStrokeColor(colors.HexColor("#E5E7EB"))
            self.setLineWidth(0.75)
            self.line(40, page_h - 32, page_w - 40, page_h - 32)

        # Running footer on every page
        self.setStrokeColor(colors.HexColor("#E5E7EB"))
        self.setLineWidth(0.75)
        self.line(40, 38, page_w - 40, 38)

        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#B9362F"))
        self.drawString(40, 24, "RenalScan")
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#6B7280"))
        self.drawString(88, 24, "• AI Kidney Stone Analysis • AI-assisted analysis — For research and demonstration purposes.")

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(page_w - 40, 24, page_str)
        self.restoreState()


def generate_pdf_report(
    scan_id: str,
    summary: Dict[str, Any],
    stones: List[Dict[str, Any]],
    annotated_image: Optional[np.ndarray] = None,
    image_format: str = "CT Abdominal (Axial Non-Contrast)",
    assumed_mm_per_px: float = 0.70
) -> bytes:
    """
    Builds a complete, multi-page professional medical diagnostic report in PDF format.
    Zero HTML or CSS source code is exposed in the output.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=46
    )

    RED_PRIMARY = colors.HexColor("#B9362F")
    RED_DARK = colors.HexColor("#8F2924")
    RED_LIGHT = colors.HexColor("#FCEDEC")
    RED_TINT = colors.HexColor("#FFF7F7")
    TEXT_DARK = colors.HexColor("#20283A")
    TEXT_MUTED = colors.HexColor("#6B7280")
    BORDER_COLOR = colors.HexColor("#E5E7EB")
    BG_LIGHT = colors.HexColor("#F9FAFB")
    SUCCESS_GREEN = colors.HexColor("#10B981")

    base_styles = getSampleStyleSheet()

    styles = {
        'TitleLogo': ParagraphStyle(
            'TitleLogo',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=21,
            leading=23,
            textColor=TEXT_DARK
        ),
        'SubTitle': ParagraphStyle(
            'SubTitle',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=11,
            textColor=TEXT_MUTED,
            spaceAfter=3
        ),
        'Badge': ParagraphStyle(
            'Badge',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=7.5,
            leading=9,
            alignment=1,
            textColor=RED_PRIMARY
        ),
        'SectionHeading': ParagraphStyle(
            'SectionHeading',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10.5,
            leading=13,
            textColor=TEXT_DARK,
            spaceBefore=10,
            spaceAfter=5
        ),
        'MetaLabel': ParagraphStyle(
            'MetaLabel',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=7.5,
            leading=10,
            textColor=TEXT_MUTED
        ),
        'MetaVal': ParagraphStyle(
            'MetaVal',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=11,
            textColor=TEXT_DARK
        ),
        'MetricLabel': ParagraphStyle(
            'MetricLabel',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=7.5,
            leading=9,
            alignment=1,
            textColor=TEXT_MUTED
        ),
        'MetricVal': ParagraphStyle(
            'MetricVal',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=16,
            alignment=1,
            textColor=RED_PRIMARY
        ),
        'TableHeader': ParagraphStyle(
            'TableHeader',
            parent=base_styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            alignment=1,
            textColor=colors.white
        ),
        'TableCell': ParagraphStyle(
            'TableCell',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            alignment=1,
            textColor=TEXT_DARK
        ),
        'TableCellLeft': ParagraphStyle(
            'TableCellLeft',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            alignment=0,
            textColor=TEXT_DARK
        ),
        'Body': ParagraphStyle(
            'Body',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=8.2,
            leading=11.5,
            textColor=TEXT_DARK
        ),
        'ImpressionText': ParagraphStyle(
            'ImpressionText',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=12.5,
            textColor=TEXT_DARK
        ),
        'DisclaimerText': ParagraphStyle(
            'DisclaimerText',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=7.5,
            leading=10.5,
            textColor=TEXT_MUTED
        ),
        'Caption': ParagraphStyle(
            'Caption',
            parent=base_styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=7.5,
            leading=9,
            alignment=1,
            textColor=TEXT_MUTED
        )
    }

    story = []

    # =========================================================================
    # 1. HEADER ROW (LOGO + CONFIDENTIAL BADGE)
    # =========================================================================
    header_data = [
        [
            Paragraph('RENAL<font color="#B9362F">SCAN</font>', styles['TitleLogo']),
            Paragraph('CONFIDENTIAL / RESEARCH', styles['Badge'])
        ],
        [
            Paragraph('AI-ASSISTED KIDNEY STONE ANALYSIS REPORT', styles['SubTitle']),
            ''
        ]
    ]
    header_table = Table(header_data, colWidths=[382, 150])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('BACKGROUND', (1,0), (1,0), RED_LIGHT),
        ('BOX', (1,0), (1,0), 1, RED_PRIMARY),
        ('TOPPADDING', (1,0), (1,0), 4),
        ('BOTTOMPADDING', (1,0), (1,0), 4),
        ('LEFTPADDING', (1,0), (1,0), 8),
        ('RIGHTPADDING', (1,0), (1,0), 8),
        ('SPAN', (0,1), (0,1)),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('LEFTPADDING', (0,0), (0,-1), 0),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=2, color=RED_PRIMARY, spaceBefore=5, spaceAfter=8))

    # =========================================================================
    # 2. SCAN INFORMATION (METADATA CARD)
    # =========================================================================
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    has_stones = summary.get('has_stones', False)
    status_str = "Completed (Calculi Identified)" if has_stones else "Completed (0 Stones Detected)"

    scan_info_data = [
        [
            Paragraph("Scan ID:", styles['MetaLabel']),
            Paragraph(scan_id, styles['MetaVal']),
            Paragraph("Date / Time:", styles['MetaLabel']),
            Paragraph(now_str, styles['MetaVal'])
        ],
        [
            Paragraph("Modality:", styles['MetaLabel']),
            Paragraph(image_format, styles['MetaVal']),
            Paragraph("Analysis Status:", styles['MetaLabel']),
            Paragraph(status_str, styles['MetaVal'])
        ]
    ]
    info_table = Table(scan_info_data, colWidths=[85, 181, 85, 181])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 8))

    # =========================================================================
    # 3. AI ANALYSIS SUMMARY METRICS
    # =========================================================================
    story.append(Paragraph("AI ANALYSIS SUMMARY", styles['SectionHeading']))
    stone_count = summary.get('stone_count', 0)
    largest_mm = summary.get('largest_stone_diameter_mm', 0.0)
    largest_band = summary.get('largest_stone_size_band', 'N/A')

    if stones and len(stones) > 0:
        mean_conf = float(np.mean([s['confidence'] for s in stones])) * 100
        conf_str = f"{mean_conf:.1f}%"
    else:
        conf_str = "N/A"

    summary_cards_data = [
        [
            Paragraph("POTENTIAL STONES", styles['MetricLabel']),
            Paragraph("LARGEST SIZE", styles['MetricLabel']),
            Paragraph("AI CONFIDENCE", styles['MetricLabel'])
        ],
        [
            Paragraph(f"{stone_count} Detected" if has_stones else "0 Detected", styles['MetricVal']),
            Paragraph(f"{largest_mm:.2f} mm" if has_stones else "0.0 mm", styles['MetricVal']),
            Paragraph(conf_str, styles['MetricVal'])
        ]
    ]
    summary_table = Table(summary_cards_data, colWidths=[177, 178, 177])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), RED_TINT),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#F1D5D5")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#F1D5D5")),
        ('TOPPADDING', (0,0), (-1,0), 5),
        ('BOTTOMPADDING', (0,0), (-1,0), 2),
        ('TOPPADDING', (0,1), (-1,1), 2),
        ('BOTTOMPADDING', (0,1), (-1,1), 6),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 8))

    # =========================================================================
    # 4. AI ANALYSIS VISUALIZATION (ANNOTATED CT IMAGE)
    # =========================================================================
    if annotated_image is not None and isinstance(annotated_image, np.ndarray):
        story.append(Paragraph("AI ANALYSIS VISUALIZATION", styles['SectionHeading']))
        img_pil = Image.fromarray(annotated_image)
        max_dim = 210
        w, h = img_pil.size
        scale = min(max_dim / w, max_dim / h)
        render_w, render_h = int(w * scale), int(h * scale)

        img_io = io.BytesIO()
        img_pil.save(img_io, format='PNG')
        img_io.seek(0)

        rl_img = RLImage(img_io, width=render_w, height=render_h)
        img_table = Table(
            [
                [rl_img],
                [Paragraph("Annotated CT slice with AI stone detection bounding boxes, Otsu segmentation contours, and physical caliper axes.", styles['Caption'])]
            ],
            colWidths=[532]
        )
        img_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0,0), (0,0), colors.HexColor("#0B0E14")),
            ('BOX', (0,0), (0,0), 1, BORDER_COLOR),
            ('TOPPADDING', (0,0), (0,0), 4),
            ('BOTTOMPADDING', (0,0), (0,0), 4),
            ('TOPPADDING', (0,1), (0,1), 4),
            ('BOTTOMPADDING', (0,1), (0,1), 2),
        ]))
        story.append(img_table)
        story.append(Spacer(1, 8))

    # =========================================================================
    # 5. DETECTED STONE FINDINGS TABLE
    # =========================================================================
    story.append(Paragraph("DETECTED STONE FINDINGS", styles['SectionHeading']))

    if has_stones and len(stones) > 0:
        table_rows = [
            [
                Paragraph("Stone ID", styles['TableHeader']),
                Paragraph("Confidence", styles['TableHeader']),
                Paragraph("Area", styles['TableHeader']),
                Paragraph("Major Axis", styles['TableHeader']),
                Paragraph("Minor Axis", styles['TableHeader']),
                Paragraph("Diameter", styles['TableHeader']),
                Paragraph("Category", styles['TableHeader']),
            ]
        ]
        for s in stones:
            if s.get('status') == 'Success':
                table_rows.append([
                    Paragraph(f"#{s['stone_id']}", styles['TableCell']),
                    Paragraph(f"{s['confidence']*100:.2f}%", styles['TableCell']),
                    Paragraph(f"{s['area_px']:.1f} px<sup>2</sup>", styles['TableCell']),
                    Paragraph(f"{s['estimated_major_mm']:.2f} mm", styles['TableCell']),
                    Paragraph(f"{s['estimated_minor_mm']:.2f} mm", styles['TableCell']),
                    Paragraph(f"<b>{s['estimated_diameter_mm']:.2f} mm</b>", styles['TableCell']),
                    Paragraph(s['clinical_size_band'], styles['TableCellLeft']),
                ])

        findings_table = Table(table_rows, colWidths=[50, 65, 72, 75, 75, 75, 120])
        t_style = [
            ('BACKGROUND', (0,0), (-1,0), RED_PRIMARY),
            ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0,0), (-1,-1), 4.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]
        for i in range(1, len(table_rows)):
            if i % 2 == 0:
                t_style.append(('BACKGROUND', (0,i), (-1,i), BG_LIGHT))
            else:
                t_style.append(('BACKGROUND', (0,i), (-1,i), colors.white))
        findings_table.setStyle(TableStyle(t_style))
        story.append(findings_table)
    else:
        no_stones_table = Table(
            [[Paragraph("No stone regions detected above model confidence threshold. Examination unremarkable for high-attenuation calculus in the active CT slice.", styles['Body'])]],
            colWidths=[532]
        )
        no_stones_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
            ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(no_stones_table)

    story.append(Spacer(1, 10))

    # Clean PageBreak for multi-stone reports to give full technical depth on Page 2
    if has_stones and len(stones) > 0:
        story.append(PageBreak())

    # =========================================================================
    # 6. STONE-BY-STONE DETAILS (DETAILED PARAMETERS)
    # =========================================================================
    if has_stones and len(stones) > 0:
        story.append(Paragraph("STONE-BY-STONE DETAILS", styles['SectionHeading']))
        for s in stones:
            if s.get('status') == 'Success':
                stone_detail_data = [
                    [
                        Paragraph(f"<b>STONE #{s['stone_id']}</b>", styles['MetaVal']),
                        Paragraph(f"<b>Confidence:</b> {s['confidence']*100:.2f}%", styles['MetaVal']),
                        Paragraph(f"<b>Area:</b> {s['area_px']:.1f} px<sup>2</sup>", styles['MetaVal'])
                    ],
                    [
                        Paragraph(f"<b>Major Axis:</b> {s['estimated_major_mm']:.2f} mm", styles['MetaVal']),
                        Paragraph(f"<b>Minor Axis:</b> {s['estimated_minor_mm']:.2f} mm", styles['MetaVal']),
                        Paragraph(f"<b>Diameter:</b> {s['estimated_diameter_mm']:.2f} mm", styles['MetaVal'])
                    ],
                    [
                        Paragraph(f"<b>Category:</b> {s['clinical_size_band']}", styles['MetaVal']),
                        "",
                        ""
                    ]
                ]
                stn_tbl = Table(stone_detail_data, colWidths=[177, 178, 177])
                stn_tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
                    ('BOX', (0,0), (-1,-1), 0.75, BORDER_COLOR),
                    ('LINELEFT', (0,0), (0,-1), 3.5, RED_PRIMARY),
                    ('SPAN', (0,2), (2,2)),
                    ('TOPPADDING', (0,0), (-1,-1), 4),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                    ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ]))
                story.append(KeepTogether(stn_tbl))
                story.append(Spacer(1, 5))
        story.append(Spacer(1, 6))

    # =========================================================================
    # 7. AI ANALYSIS IMPRESSION (NEUTRAL CLINICAL SUMMARY)
    # =========================================================================
    story.append(Paragraph("AI ANALYSIS IMPRESSION", styles['SectionHeading']))
    if has_stones:
        impression_text = (
            f"AI analysis identified {stone_count} potential stone region(s) in the analyzed CT image. "
            f"The primary detected calculus demonstrates an estimated equivalent diameter of {largest_mm:.2f} mm "
            f"({largest_band}). Physical dimensions are calculated via sub-pixel contour segmentation and calibrated mm conversion. "
            f"Spontaneous passage probability and intervention decisions should be evaluated by the attending clinical team. "
            f"Non-contrast abdominal CT findings are consistent with renal calculus localization."
        )
    else:
        impression_text = (
            "AI analysis identified no focal high-attenuation calculus in the analyzed CT image slice above the specified confidence threshold. "
            "Findings are consistent with a normal non-contrast abdominal CT examination in the evaluated slice plane. "
            "Routine clinical correlation is advised."
        )

    impression_table = Table([[Paragraph(impression_text, styles['ImpressionText'])]], colWidths=[532])
    impression_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), RED_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#F1D5D5")),
        ('LINELEFT', (0,0), (0,-1), 4, RED_PRIMARY),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(KeepTogether(impression_table))
    story.append(Spacer(1, 8))

    # =========================================================================
    # 8. MEASUREMENT & CONFIDENCE METHODOLOGY INFORMATION
    # =========================================================================
    method_data = [
        [
            Paragraph("<b>MEASUREMENT INFORMATION</b>", styles['MetaLabel']),
            Paragraph("<b>AI CONFIDENCE INFORMATION</b>", styles['MetaLabel'])
        ],
        [
            Paragraph(
                f"Calculus boundaries isolated using local Otsu thresholding with convex perimeter analysis. "
                f"Physical scaling assumes standard non-contrast pixel spacing of {assumed_mm_per_px:.2f} mm/px. "
                f"Major and minor diameters represent principal moment axes. Diameter indicates circular area equivalence.",
                styles['Body']
            ),
            Paragraph(
                "Detection coordinates localized by fine-tuned YOLOv8 convolutional architecture trained on abdominal CT imaging. "
                "Confidence ratings indicate mathematical softmax certainty. Regions below threshold are filtered from reporting.",
                styles['Body']
            )
        ]
    ]
    method_table = Table(method_data, colWidths=[261, 261])
    method_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(KeepTogether(method_table))
    story.append(Spacer(1, 8))

    # =========================================================================
    # 9. IMPORTANT MEDICAL DISCLAIMER
    # =========================================================================
    disclaimer_text = (
        "<b>IMPORTANT MEDICAL DISCLAIMER:</b> RenalScan is an AI-assisted medical image analysis system developed "
        "for research and demonstration purposes. AI-generated findings are not a medical diagnosis and should "
        "be reviewed by a qualified healthcare professional. Do not make diagnostic or treatment decisions based "
        "solely on this automated report."
    )
    disclaimer_table = Table([[Paragraph(disclaimer_text, styles['DisclaimerText'])]], colWidths=[532])
    disclaimer_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F3F4F6")),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('LINELEFT', (0,0), (0,-1), 3, colors.HexColor("#9CA3AF")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(KeepTogether(disclaimer_table))

    # Build document with NumberedCanvas for dynamic running headers/footers
    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()
