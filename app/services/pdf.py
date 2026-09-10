import io
import os
import re
import tempfile
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.schemas import StatsSummary


def compile_clinical_pdf(stats: StatsSummary, summary_text: str, chart_png: bytes) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=32,
        bottomMargin=32,
    )
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        "HeaderTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=15,
        textColor=colors.HexColor("#0d47a1"),
    )
    sub_style = ParagraphStyle(
        "SubHeader",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor("#555555"),
    )
    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#0d47a1"),
        spaceBefore=5,
        spaceAfter=2,
    )
    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#222222"),
    )
    table_text = ParagraphStyle(
        "TText", parent=styles["Normal"], fontName="Helvetica", fontSize=7, leading=9
    )
    table_header = ParagraphStyle(
        "THead",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#0d47a1"),
    )

    story = [
        Paragraph("CLINICAL OUTPATIENT CONSULTATION BRIEF", header_style),
        Paragraph(
            f"Generated: {datetime.now().strftime('%d %b %Y')} | Assessment: Harvey-Bradshaw Index (HBI) & BSFS | Non-Diagnostic Decision Support",
            sub_style,
        ),
        Spacer(1, 4),
        HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#0d47a1"), spaceAfter=6),
    ]

    comps_display = ", ".join(stats.reported_complications) if stats.reported_complications else "None reported"
    delta = stats.hbi_trend_delta
    delta_str = f"+{delta}" if delta > 0 else str(delta)
    table_data = [
        [
            Paragraph("<b>Window:</b>", table_header),
            Paragraph(f"{stats.monitoring_window_days} Days", table_text),
            Paragraph("<b>Baseline HBI:</b>", table_header),
            Paragraph(str(stats.baseline_hbi_avg), table_text),
            Paragraph("<b>Current HBI:</b>", table_header),
            Paragraph(str(stats.current_hbi_avg), table_text),
        ],
        [
            Paragraph("<b>HBI Trend Δ:</b>", table_header),
            Paragraph(delta_str, table_text),
            Paragraph("<b>Med Adherence:</b>", table_header),
            Paragraph(f"{stats.medication_adherence_percent}%", table_text),
            Paragraph("<b>Total Liquid Stools:</b>", table_header),
            Paragraph(str(stats.total_liquid_stools_reported), table_text),
        ],
        [
            Paragraph("<b>Complications:</b>", table_header),
            Paragraph(clean_text_for_pdf(comps_display.title()), table_text),
            Paragraph("<b>Clinical Tier:</b>", table_header),
            Paragraph(stats.clinical_tier, table_text),
            Paragraph("<b>Adherence Note:</b>", table_header),
            Paragraph(stats.adherence_detail, table_text),
        ],
    ]

    table = Table(table_data, colWidths=[75, 95, 75, 95, 85, 95])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f7fa")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cfd8dc")),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#eceff1")),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 4))

    clean_lines = re.sub(r"#+\s*", "", summary_text).strip().split("\n")
    heading_prefixes = (
        "1.",
        "2.",
        "3.",
        "4.",
        "Baseline",
        "Onset",
        "Escalation",
        "Recovery",
        "Overall",
        "Current",
        "Middle",
        "Dietary",
        "Medication",
        "Complications",
    )
    for line in clean_lines:
        line = clean_text_for_pdf(line.strip())
        if not line:
            continue
        if any(line.startswith(prefix) for prefix in heading_prefixes):
            story.append(Paragraph(f"<b>{line}</b>", section_style))
        elif line.startswith(("-", "*")):
            story.append(Paragraph(f"• {line.lstrip('-* ')}", body_style))
        else:
            story.append(Paragraph(line, body_style))

    story.append(Spacer(1, 4))

    chart_path = None
    if chart_png:
        fd, chart_path = tempfile.mkstemp(suffix=".png")
        os.write(fd, chart_png)
        os.close(fd)
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#b0bec5"), spaceAfter=4))
        story.append(Image(chart_path, width=520, height=170))

    try:
        doc.build(story)
    finally:
        if chart_path and os.path.exists(chart_path):
            os.remove(chart_path)

    return buf.getvalue()


def clean_text_for_pdf(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2015\u2212]", "-", text)
    text = re.sub(r"[\u00A0\u2000-\u200B\u202F\u205F\u3000]", " ", text)
    text = re.sub(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[a-fA-F0-9]+);)", "&amp;", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    return text
