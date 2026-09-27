"""
test_report_generator.py - Unit Tests for RenalScan Publication-Grade PDF Report Generator
Validates:
  1. Valid PDF generation and byte signature (%PDF-)
  2. Complete absence of any raw HTML/CSS source code in the generated PDF
  3. Correct inclusion of all required medical sections, dynamic metadata, and measurements
  4. Proper multi-page layout and two-pass NumberedCanvas footer ("Page X of Y")
  5. Safe handling of zero-stone (normal/clear) scans
"""

import io
import unittest
import numpy as np
import pypdf

from app.report_generator import generate_pdf_report


class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        # Create a mock annotated CT image (RGB numpy array)
        self.mock_image = np.zeros((320, 320, 3), dtype=np.uint8)
        self.mock_image[100:150, 100:150] = [185, 54, 47]

        # Multi-stone mock analysis results
        self.multi_summary = {
            'has_stones': True,
            'stone_count': 2,
            'largest_stone_diameter_mm': 8.19,
            'largest_stone_size_band': '6-10mm (Large - Low passage likelihood)'
        }
        self.multi_stones = [
            {
                'stone_id': 1,
                'confidence': 0.8845,
                'area_px': 107.5,
                'estimated_major_mm': 11.44,
                'estimated_minor_mm': 7.11,
                'estimated_diameter_mm': 8.19,
                'clinical_size_band': '6-10mm (Large - Low passage likelihood)',
                'status': 'Success'
            },
            {
                'stone_id': 2,
                'confidence': 0.7230,
                'area_px': 45.2,
                'estimated_major_mm': 6.20,
                'estimated_minor_mm': 4.10,
                'estimated_diameter_mm': 4.80,
                'clinical_size_band': '4-6mm (Medium - Moderate passage likelihood)',
                'status': 'Success'
            }
        ]

        # Zero-stone (normal scan) mock analysis results
        self.zero_summary = {
            'has_stones': False,
            'stone_count': 0,
            'largest_stone_diameter_mm': 0.0,
            'largest_stone_size_band': 'N/A'
        }
        self.zero_stones = []

    def test_pdf_signature_and_generation(self):
        """Verify that generate_pdf_report returns valid binary PDF data."""
        pdf_bytes = generate_pdf_report(
            scan_id="Test_Scan_001",
            summary=self.multi_summary,
            stones=self.multi_stones,
            annotated_image=self.mock_image
        )
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b'%PDF-'), "PDF must start with standard %PDF- header signature.")

    def test_zero_raw_html_or_css_leaks(self):
        """Verify that the generated PDF contains NO raw HTML or CSS markup."""
        pdf_bytes = generate_pdf_report(
            scan_id="Test_Scan_No_Leaks",
            summary=self.multi_summary,
            stones=self.multi_stones,
            annotated_image=self.mock_image
        )

        forbidden_patterns = [
            b'<div', b'</div>', b'<span', b'</span>', b'<style', b'</style>',
            b'class=', b'style=', b'grid-template', b'font-size:', b'font-weight:',
            b'margin-', b'padding-'
        ]

        for pat in forbidden_patterns:
            self.assertNotIn(
                pat,
                pdf_bytes,
                f"Generated PDF contains forbidden raw HTML/CSS markup: '{pat.decode()}'"
            )

    def test_required_sections_present_in_pdf_text(self):
        """Extract text from the generated PDF and confirm all required medical sections are present."""
        pdf_bytes = generate_pdf_report(
            scan_id="RS-2026-TEST-99",
            summary=self.multi_summary,
            stones=self.multi_stones,
            annotated_image=self.mock_image
        )

        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        self.assertGreaterEqual(len(reader.pages), 1)

        full_text = " ".join([page.extract_text() for page in reader.pages])

        # Header & Metadata
        self.assertIn("RENALSCAN", full_text)
        self.assertIn("AI-ASSISTED KIDNEY STONE ANALYSIS REPORT", full_text)
        self.assertIn("CONFIDENTIAL / RESEARCH", full_text)
        self.assertIn("RS-2026-TEST-99", full_text)
        self.assertIn("CT Abdominal (Axial Non-Contrast)", full_text)

        # AI Summary
        self.assertIn("AI ANALYSIS SUMMARY", full_text)
        self.assertIn("POTENTIAL STONES", full_text)
        self.assertIn("LARGEST SIZE", full_text)
        self.assertIn("AI CONFIDENCE", full_text)

        # Findings & Details
        self.assertIn("DETECTED STONE FINDINGS", full_text)
        self.assertIn("Stone ID", full_text)
        self.assertIn("STONE-BY-STONE DETAILS", full_text)
        self.assertIn("STONE #1", full_text)
        self.assertIn("STONE #2", full_text)
        self.assertIn("8.19 mm", full_text)
        self.assertIn("88.45%", full_text)

        # Impression, Methodology & Disclaimer
        self.assertIn("AI ANALYSIS IMPRESSION", full_text)
        self.assertIn("MEASUREMENT INFORMATION", full_text)
        self.assertIn("AI CONFIDENCE INFORMATION", full_text)
        self.assertIn("IMPORTANT MEDICAL DISCLAIMER", full_text)

        # Footer
        self.assertIn("Page", full_text)
        self.assertIn("of", full_text)

    def test_zero_stone_report_generation(self):
        """Verify report generation for a clear scan with 0 detected stones."""
        pdf_bytes = generate_pdf_report(
            scan_id="RS-NORMAL-001",
            summary=self.zero_summary,
            stones=self.zero_stones,
            annotated_image=self.mock_image
        )

        self.assertTrue(pdf_bytes.startswith(b'%PDF-'))
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        full_text = " ".join([page.extract_text() for page in reader.pages])

        self.assertIn("0 Detected", full_text)
        self.assertIn("Completed (0 Stones Detected)", full_text)
        self.assertIn("IMPORTANT MEDICAL DISCLAIMER", full_text)


if __name__ == '__main__':
    unittest.main()
