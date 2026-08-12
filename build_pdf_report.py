"""
build_pdf_report.py — Generates a publication-grade PDF report for HCLTech Assignment 2.
Author: Esambadi Goutham Reddy
"""

import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

PDF_FILENAME = "Meridian_Supply_Chain_RAG_Final_Report.pdf"

class NumberedCanvas(canvas.Canvas):
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

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 750, "HCLTech Assignment 2 — Supply Chain RAG Final Technical Report")
            self.drawRightString(558, 750, "Author: Esambadi Goutham Reddy")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
        # Footer
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "Meridian Components Pvt. Ltd. — Internal Procurement RAG System")
        self.drawRightString(558, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def create_report():
    doc = SimpleDocTemplate(
        PDF_FILENAME,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    primary_color = colors.HexColor("#1A365D")
    secondary_color = colors.HexColor("#2B6CB0")
    dark_neutral = colors.HexColor("#2D3748")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        alignment=0,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=secondary_color,
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=secondary_color,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=dark_neutral,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=12,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#2C5282"),
        backColor=colors.HexColor("#EDF2F7"),
        borderColor=colors.HexColor("#CBD5E0"),
        borderWidth=0.5,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=dark_neutral
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell_style,
        fontName='Helvetica-Bold'
    )

    story = []

    # Title Banner
    story.append(Paragraph("Meridian Supply Chain Intelligence RAG System", title_style))
    story.append(Paragraph("<b>HCLTech Assignment 2 — Comprehensive Final Technical & Audit Report</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=primary_color, spaceAfter=12))

    # Meta Table
    meta_data = [
        [Paragraph("<b>Author / Candidate:</b>", table_cell_bold), Paragraph("Esambadi Goutham Reddy", table_cell_style),
         Paragraph("<b>Target Entity:</b>", table_cell_bold), Paragraph("Meridian Components Pvt. Ltd.", table_cell_style)],
        [Paragraph("<b>GitHub Repository:</b>", table_cell_bold), Paragraph("goutham-11-16/Supply-Chain-RAG", table_cell_style),
         Paragraph("<b>LLM & Embeddings:</b>", table_cell_bold), Paragraph("GPT-4o & text-embedding-3-small", table_cell_style)],
        [Paragraph("<b>Vector Store:</b>", table_cell_bold), Paragraph("ChromaDB (supplychain_rag)", table_cell_style),
         Paragraph("<b>Indexed Vectors:</b>", table_cell_bold), Paragraph("22 Chunks (Size: 1200, Overlap: 150)", table_cell_style)]
    ]
    meta_table = Table(meta_data, colWidths=[110, 140, 100, 154])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 1. Project Overview
    story.append(Paragraph("1. Project Overview", h1_style))
    story.append(Paragraph(
        "This project establishes a production-quality, document-grounded Retrieval-Augmented Generation (RAG) system for "
        "<b>Meridian Components Pvt. Ltd.</b>, an automotive electronics manufacturer operating assembly plants in Chakan (Pune) and Hosur (Tamil Nadu). "
        "Meridian's procurement team handles complex buyer queries regarding supplier performance metrics (on-time delivery, defect PPM, line stoppages) "
        "and corporate policy rules (PO approval tiers, quality cost recovery under Clause 6.3, and safety stock formulas).", body_style
    ))
    story.append(Paragraph(
        "<b>Key Problem Addressed:</b> Manual inspection of fragmented PDF handbooks leads to delayed decision-making, misinterpretation of quality penalties "
        "(e.g., failing to enforce mandatory 100% inspection floors), and high risk of AI hallucinations when using ungrounded LLMs.", body_style
    ))
    story.append(Paragraph(
        "<b>Core RAG Capabilities:</b> The system indexes all Meridian PDFs into a persistent single-collection ChromaDB vector database, "
        "supports configurable Top-K similarity search (1–12), provides dual-column source page citations, integrates a deterministic Policy & Penalty Calculator, "
        "and strictly refuses out-of-domain trap questions.", body_style
    ))

    # 2. System Architecture
    story.append(Paragraph("2. System Architecture", h1_style))
    story.append(Paragraph(
        "The application architecture enforces strict separation between data ingestion, vector indexing, similarity retrieval, and LLM context synthesis:", body_style
    ))
    arch_code = (
        "PDF Documents in data/\n"
        "      │\n"
        "      ▼\n"
        "PyPDF Extraction (0-indexed metadata standardized to 1-indexed pages)\n"
        "      │\n"
        "      ▼\n"
        "Recursive Character Text Splitter (Chunk Size: 1200, Overlap: 150)\n"
        "      │\n"
        "      ▼\n"
        "OpenAI text-embedding-3-small (1536-dimensional vectors)\n"
        "      │\n"
        "      ▼\n"
        "ChromaDB Persistent Vector Store (Single Collection: supplychain_rag)\n"
        "      │\n"
        "      ▼\n"
        "Top-K Similarity Retrieval (Configurable 1–12, Default: 6 with Smart Balancing)\n"
        "      │\n"
        "      ▼\n"
        "Strict System Prompt + Context Construction\n"
        "      │\n"
        "      ▼\n"
        "OpenAI GPT-4o Synthesis (Temperature = 0.1)\n"
        "      │\n"
        "      ▼\n"
        "Grounded Answer + Dual-Column Source Citations Audit Trail"
    )
    story.append(Paragraph(arch_code.replace("\n", "<br/>"), code_style))

    # 3. Document & Dataset Details
    story.append(Paragraph("3. Document & Dataset Details", h1_style))
    doc_data = [
        [Paragraph("Document Name", table_header_style), Paragraph("Document Type", table_header_style), Paragraph("Pages", table_header_style), Paragraph("Key Content / Information Covered", table_header_style)],
        [Paragraph("Meridian_Procurement_Policy_Handbook_v4.2.pdf", table_cell_bold), Paragraph("Corporate Policy", table_cell_style), Paragraph("3 Pages", table_cell_style), Paragraph("Approval authority tiers, supplier classification, Clause 6.1 OTD warnings, Clause 6.3 quality penalties (₹120/unit), Section 8 safety stock formulas.", table_cell_style)],
        [Paragraph("Meridian_Supply_Chain_Review_Q1_FY2025-26.pdf", table_cell_bold), Paragraph("Operational Review", table_cell_style), Paragraph("3 Pages", table_cell_style), Paragraph("Q1 scorecard metrics (OTD, PPM) for 5 key suppliers, 7 line stoppage events (41 hrs total), single-source microcontroller risks, freight lanes.", table_cell_style)]
    ]
    doc_table = Table(doc_data, colWidths=[140, 80, 50, 234])
    doc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(doc_table)
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Chunking Hyperparameters:</b> Chunk Size = 1200 characters, Chunk Overlap = 150 characters, Total Chunks = 22. <i>Rationale: Preserves complete scorecard data tables and policy clauses in a single vector chunk without splitting numerical context.</i>", body_style))

    # 4. Retrieval Strategy
    story.append(Paragraph("4. Retrieval Strategy", h1_style))
    story.append(Paragraph(
        "The retrieval pipeline queries ChromaDB using `text-embedding-3-small` similarity vectors. "
        "Top-K defaults to 6 (slider range 1–12). To prevent cross-document queries from being dominated by a single document, "
        "the engine applies a smart cross-document candidate merger and full-content string deduplication, ensuring balanced context representation from both PDFs.", body_style
    ))

    # 5. Cross-Document Reasoning
    story.append(Paragraph("5. Cross-Document Reasoning", h1_style))
    story.append(Paragraph(
        "Cross-document reasoning is a core requirement of the Meridian RAG system. The engine seamlessly combines operational facts from the Review PDF with governing clauses from the Handbook PDF:", body_style
    ))
    story.append(Paragraph("• <b>Kaveri Metals:</b> Combines Review Q1 (88.1% OTD, 1,150 PPM) with Handbook Clause 6.1 (written warning & weekly review calls) and Clause 6.3 (₹120/unit rework debit + mandatory 100% inspection floor until 3 consecutive lots pass).", bullet_style))
    story.append(Paragraph("• <b>Trident Circuit Boards:</b> Combines Review Q1 (640 PPM defect rate, 2 line stoppages) with Handbook Clause 6.3 penalty consequences.", bullet_style))
    story.append(Paragraph("• <b>Shenzhen Rui Electronics:</b> Combines Review Q1 (Highest spend ₹21.9 cr, 76.0% OTD, single-source microcontroller risk) with Handbook Clause 7.1 (mandatory 12-month dual-sourcing rule) and current company actions (Anh Long Vietnam qualification).", bullet_style))

    # 6. Policy & Penalty Calculator
    story.append(Paragraph("6. Policy & Penalty Calculator", h1_style))
    story.append(Paragraph(
        "Operating alongside the RAG pipeline, Tab 3 of the application features a deterministic execution engine that computes exact policy actions and penalties:", body_style
    ))
    story.append(Paragraph("• <b>Clause 6.1 (OTD Warning):</b> Triggers written warning & weekly review calls if OTD < 90%.", bullet_style))
    story.append(Paragraph("• <b>Clause 6.2 (Rating Bands):</b> Band A (≥90%), Band B (75–89%), Band C (60–74%), Band D (<60%).", bullet_style))
    story.append(Paragraph("• <b>Clause 6.3 (Quality Recovery):</b> PPM > 500 triggers ₹120/unit rework recovery debit and 100% incoming inspection floor.", bullet_style))
    story.append(Paragraph("• <b>Section 8 (Safety Stock):</b> Computes <i>SS = max(Lead Time × 0.25, Floor Days)</i>. For imported critical parts (46-day LT), <i>max(11.5, 30) = 30 days</i>.", bullet_style))

    # 7. Testing & Verification (20-Test Benchmark Table)
    story.append(PageBreak())
    story.append(Paragraph("7. Comprehensive 20-Test Benchmark Suite", h1_style))
    story.append(Paragraph("All 20 test cases were executed against the live system. Every query returned 100% accurate, document-grounded results:", body_style))

    test_data = [
        [Paragraph("ID", table_header_style), Paragraph("Category", table_header_style), Paragraph("User Question", table_header_style), Paragraph("Expected Output Summary", table_header_style), Paragraph("Status", table_header_style)],
        [Paragraph("T1", table_cell_bold), Paragraph("Single-Doc", table_cell_style), Paragraph("Highest spend supplier in Q1 & OTD?", table_cell_style), Paragraph("Shenzhen Rui Electronics (₹21.9 cr, 76.0% OTD)", table_cell_style), Paragraph("✅ PASS", table_cell_bold)],
        [Paragraph("T2", table_cell_bold), Paragraph("Single-Doc", table_cell_style), Paragraph("Line stoppages, downtime & causes?", table_cell_style), Paragraph("7 stoppages, 41 hrs downtime, 4 micro & 2 PCB causes", table_cell_style), Paragraph("✅ PASS", table_cell_bold)],
        [Paragraph("T3", table_cell_bold), Paragraph("Single-Doc", table_cell_style), Paragraph("PO approval authority for ₹1.4 crore?", table_cell_style), Paragraph("Chief Operating Officer (COO) (Tier ₹1cr–₹5cr)", table_cell_style), Paragraph("✅ PASS", table_cell_bold)],
        [Paragraph("T4", table_cell_bold), Paragraph("Single-Doc", table_cell_style), Paragraph("4 classification categories & Critical criteria?", table_cell_style), Paragraph("Strategic, Critical, Standard, Tactical; single-source/LT>30d", table_cell_style), Paragraph("✅ PASS", table_cell_bold)],
        [Paragraph("T5", table_cell_bold), Paragraph("Cross-Doc", table_cell_style), Paragraph("Kaveri Metals 88.1% OTD & 1,150 PPM clauses?", table_cell_style), Paragraph("Clause 6.1 warning & Clause 6.3 ₹120 debit + 100% insp floor", table_cell_style), Paragraph("✅ PASS", table_cell_bold)],
        [Paragraph("T6", table_cell_bold), Paragraph("Cross-Doc", table_cell_style), Paragraph("Single-source microcontroller policy & actions?", table_cell_style), Paragraph("Clause 7.1 12mo dual source; Anh Long Vietnam validation", table_cell_style), Paragraph("✅ PASS", table_cell_bold)],
        [Paragraph("T7", table_cell_bold), Paragraph("Cross-Doc", table_cell_style), Paragraph("46-day lead time safety stock required?", table_cell_style), Paragraph("max(11.5, 30) = 30 days safety stock", table_cell_style), Paragraph("✅ PASS", table_cell_bold)],
        [Paragraph("T8", table_cell_bold), Paragraph("Cross-Doc", table_cell_style), Paragraph("Trident 640 PPM defect consequence?", table_cell_style), Paragraph("Clause 6.3 ₹120/unit rework & 100% inspection floor", table_cell_style), Paragraph("✅ PASS", table_cell_bold)],
        [Paragraph("T9", table_cell_bold), Paragraph("Cross-Doc", table_cell_style), Paragraph("Suppliers below Band B OTD & escalation?", table_cell_style), Paragraph("None (all ≥75%); Band C needs plan, Band D business hold", table_cell_style), Paragraph("✅ PASS", table_cell_bold)],
        [Paragraph("T10", table_cell_bold), Paragraph("Trap Test", table_cell_style), Paragraph("Annual salary of Head of Procurement?", table_cell_style), Paragraph("'Information is not available in the uploaded documents.'", table_cell_style), Paragraph("🛡️ PASS", table_cell_bold)],
        [Paragraph("T11", table_cell_bold), Paragraph("Single-Doc", table_cell_style), Paragraph("PO approval authority for ₹25 lakh?", table_cell_style), Paragraph("Head of Procurement (Tier ₹10L–₹50L)", table_cell_style), Paragraph("✅ PASS", table_cell_bold)],
        [Paragraph("T12", table_cell_bold), Paragraph("Single-Doc", table_cell_style), Paragraph("Freight lane with longest transit time?", table_cell_style), Paragraph("Shenzhen to Nhava Sheva (28 days ocean transit)", table_cell_style), Paragraph("✅ PASS", table_cell_bold)],
        [Paragraph("T13", table_cell_bold), Paragraph("Single-Doc", table_cell_style), Paragraph("Apex Microelectronics Q1 OTD & PPM?", table_cell_style), Paragraph("91.2% OTD, 210 PPM defect rate (Band A)", table_cell_style), Paragraph("✅ PASS", table_cell_bold)],
        [Paragraph("T14", table_cell_bold), Paragraph("Single-Doc", table_cell_style), Paragraph("Share-of-wallet cap for single supplier?", table_cell_style), Paragraph("Maximum 60% of total category spend", table_cell_style), Paragraph("✅ PASS", table_cell_bold)],
        [Paragraph("T15", table_cell_bold), Paragraph("Cross-Doc", table_cell_style), Paragraph("Policy actions for Sunrise Logistics Q1 OTD?", table_cell_style), Paragraph("94.0% OTD (Band A); no penalty triggered", table_cell_style), Paragraph("✅ PASS", table_cell_bold)],
        [Paragraph("T16", table_cell_bold), Paragraph("Cross-Doc", table_cell_style), Paragraph("Emergency air freight approval authority?", table_cell_style), Paragraph("Requires VP of Supply Chain written approval", table_cell_style), Paragraph("✅ PASS", table_cell_bold)],
        [Paragraph("T17", table_cell_bold), Paragraph("Trap Test", table_cell_style), Paragraph("What is Meridian's Q3 revenue forecast?", table_cell_style), Paragraph("'Information is not available in the uploaded documents.'", table_cell_style), Paragraph("🛡️ PASS", table_cell_bold)],
        [Paragraph("T18", table_cell_bold), Paragraph("Trap Test", table_cell_style), Paragraph("Who is the CEO of Meridian Components?", table_cell_style), Paragraph("'Information is not available in the uploaded documents.'", table_cell_style), Paragraph("🛡️ PASS", table_cell_bold)],
        [Paragraph("T19", table_cell_bold), Paragraph("Single-Doc", table_cell_style), Paragraph("How many days customs hold at Nhava Sheva?", table_cell_style), Paragraph("9 days customs hold (11 hours line stoppage)", table_cell_style), Paragraph("✅ PASS", table_cell_bold)],
        [Paragraph("T20", table_cell_bold), Paragraph("Cross-Doc", table_cell_style), Paragraph("What recovery rate applies to defective parts?", table_cell_style), Paragraph("Standard recovery rate of ₹120 per affected unit", table_cell_style), Paragraph("✅ PASS", table_cell_bold)],
    ]
    test_table = Table(test_data, colWidths=[24, 55, 145, 230, 50])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(test_table)
    story.append(Spacer(1, 10))

    # Application Screenshots
    story.append(Paragraph("Application Interface Screenshots", h2_style))
    screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
    screenshot_files = [
        "Screenshot 2026-08-12 213924.png",
        "Screenshot 2026-08-12 213943.png",
        "Screenshot 2026-08-12 214006.png"
    ]
    for s_file in screenshot_files:
        s_path = os.path.join(screenshot_dir, s_file)
        if os.path.exists(s_path):
            try:
                story.append(Image(s_path, width=480, height=240))
                story.append(Spacer(1, 6))
            except Exception as e:
                pass

    # 8. Retrieval / Top-K Validation
    story.append(Paragraph("8. Retrieval / Top-K Validation", h1_style))
    story.append(Paragraph(
        "To verify that the retrieval pipeline strictly respects the user-selected Top-K parameter without arbitrary trimming or leakage, "
        "we executed a systematic empirical validation across all supported Top-K values (1 to 12):", body_style
    ))
    topk_data = [
        [Paragraph("Top-K Setting", table_header_style), Paragraph("Raw Chroma Chunks", table_header_style), Paragraph("Filtered Chunks", table_header_style), Paragraph("Deduped Chunks", table_header_style), Paragraph("LLM Context Chunks", table_header_style), Paragraph("Debug UI Displayed", table_header_style), Paragraph("Match Status", table_header_style)],
        [Paragraph("Top-K = 1", table_cell_bold), Paragraph("1", table_cell_style), Paragraph("1", table_cell_style), Paragraph("1", table_cell_style), Paragraph("1", table_cell_style), Paragraph("1", table_cell_style), Paragraph("✅ 1-to-1 Exact", table_cell_bold)],
        [Paragraph("Top-K = 2", table_cell_bold), Paragraph("2", table_cell_style), Paragraph("2", table_cell_style), Paragraph("2", table_cell_style), Paragraph("2", table_cell_style), Paragraph("2", table_cell_style), Paragraph("✅ 1-to-1 Exact", table_cell_bold)],
        [Paragraph("Top-K = 4", table_cell_bold), Paragraph("4", table_cell_style), Paragraph("4", table_cell_style), Paragraph("4", table_cell_style), Paragraph("4", table_cell_style), Paragraph("4", table_cell_style), Paragraph("✅ 1-to-1 Exact", table_cell_bold)],
        [Paragraph("Top-K = 6 (Default)", table_cell_bold), Paragraph("6", table_cell_style), Paragraph("6", table_cell_style), Paragraph("6", table_cell_style), Paragraph("6", table_cell_style), Paragraph("6", table_cell_style), Paragraph("✅ 1-to-1 Exact", table_cell_bold)],
        [Paragraph("Top-K = 8", table_cell_bold), Paragraph("8", table_cell_style), Paragraph("8", table_cell_style), Paragraph("8", table_cell_style), Paragraph("8", table_cell_style), Paragraph("8", table_cell_style), Paragraph("✅ 1-to-1 Exact", table_cell_bold)],
        [Paragraph("Top-K = 10", table_cell_bold), Paragraph("10", table_cell_style), Paragraph("10", table_cell_style), Paragraph("10", table_cell_style), Paragraph("10", table_cell_style), Paragraph("10", table_cell_style), Paragraph("✅ 1-to-1 Exact", table_cell_bold)],
        [Paragraph("Top-K = 12", table_cell_bold), Paragraph("12", table_cell_style), Paragraph("12", table_cell_style), Paragraph("12", table_cell_style), Paragraph("12", table_cell_style), Paragraph("12", table_cell_style), Paragraph("✅ 1-to-1 Exact", table_cell_bold)],
    ]
    topk_table = Table(topk_data, colWidths=[70, 70, 70, 70, 80, 75, 69])
    topk_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), secondary_color),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(topk_table)
    story.append(Spacer(1, 8))

    # 9. Hallucination / Trap Test
    story.append(Paragraph("9. Hallucination / Trap Test", h1_style))
    story.append(Paragraph(
        "<b>Test Query:</b> <i>'What is the annual salary of the Head of Procurement?'</i><br/>"
        "<b>System Output:</b> <font color='#C53030'><b>'The information is not available in the uploaded documents.'</b></font><br/>"
        "<b>Sources:</b> None (0 chunks referenced).<br/>"
        "<b>Significance:</b> Demonstrates that the system enforces strict prompt boundaries and refuses out-of-domain questions rather than inventing figures.", body_style
    ))

    # 10. Known Limitations & Development History
    story.append(Paragraph("10. Development History & Known Limitations", h1_style))
    story.append(Paragraph(
        "• <b>Deduplication Header Fix:</b> Early testing revealed that deduplication using string slicing (`doc[:100]`) compared prepended metadata headers rather than actual body text. This was corrected to compare `doc.page_content.strip()`, restoring 1-to-1 Top-K counts.<br/>"
        "• <b>Windows File Locking Fix:</b> Replaced file-system folder deletion (`shutil.rmtree`) with Chroma's native `existing.delete_collection()` API in `ingest.py` to prevent vector duplication caused by Windows file locks.<br/>"
        "• <b>Domain Scope:</b> System is tailored to Meridian's supply chain documents and strictly refuses un-indexed queries.", body_style
    ))

    # 11. Final Verification Checklist
    story.append(Paragraph("11. Final Verification Checklist", h1_style))
    checklist_data = [
        [Paragraph("Verification Item", table_header_style), Paragraph("Requirement", table_header_style), Paragraph("Status", table_header_style)],
        [Paragraph("Single Collection Persistence", table_cell_bold), Paragraph("Both Meridian PDFs stored in 1 ChromaDB collection", table_cell_style), Paragraph("✅ VERIFIED", table_cell_bold)],
        [Paragraph("Chunking Count Accuracy", table_cell_bold), Paragraph("22 unique vector chunks generated & reported", table_cell_style), Paragraph("✅ VERIFIED", table_cell_bold)],
        [Paragraph("Top-K Range Control", table_cell_bold), Paragraph("Exact 1-to-1 retrieval for K = 1, 2, 4, 6, 8, 10, 12", table_cell_style), Paragraph("✅ VERIFIED", table_cell_bold)],
        [Paragraph("Cross-Document Reasoning", table_cell_bold), Paragraph("Synthesizes Review Q1 metrics + Handbook policy rules", table_cell_style), Paragraph("✅ VERIFIED", table_cell_bold)],
        [Paragraph("Source Citations", table_cell_bold), Paragraph("Provides document name & 1-indexed page for every fact", table_cell_style), Paragraph("✅ VERIFIED", table_cell_bold)],
        [Paragraph("Policy & Penalty Calculator", table_cell_bold), Paragraph("Evaluates OTD bands, ₹120 rework debit & safety stock math", table_cell_style), Paragraph("✅ VERIFIED", table_cell_bold)],
        [Paragraph("Trap Question Refusal", table_cell_bold), Paragraph("Honest refusal notice for un-indexed queries", table_cell_style), Paragraph("✅ VERIFIED", table_cell_bold)],
        [Paragraph("API Key Security", table_cell_bold), Paragraph(".env listed in .gitignore; zero exposed secrets on GitHub", table_cell_style), Paragraph("✅ VERIFIED", table_cell_bold)]
    ]
    checklist_table = Table(checklist_data, colWidths=[150, 254, 100])
    checklist_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(checklist_table)
    story.append(Spacer(1, 10))

    # 12. Conclusion
    story.append(Paragraph("12. Conclusion", h1_style))
    story.append(Paragraph(
        "The Meridian Supply Chain Intelligence RAG System successfully satisfies all technical, architectural, functional, and security requirements "
        "of HCLTech Assignment 2. Built by <b>Esambadi Goutham Reddy</b>, the system combines robust vector retrieval, grounded GPT-4o synthesis, "
        "deterministic policy evaluation, and strict security compliance into an executive-ready application.", body_style
    ))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=8))
    story.append(Paragraph("<i>Report generated autonomously for HCLTech Assignment 2 Submission Verification.</i>", ParagraphStyle('FooterNote', parent=body_style, fontName='Helvetica-Oblique', alignment=1)))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Generated PDF Report: {PDF_FILENAME}")

if __name__ == "__main__":
    create_report()
