import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
)
from reportlab.lib.units import inch


def generate_final_report(results, charts_dir, output_path):
    """Generates a final visual report combining analytics and charts — without the Flags column."""
    try:
        # Create PDF/PNG-style report document
        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40
        )
        styles = getSampleStyleSheet()
        elements = []

        # Title
        elements.append(Paragraph("<b>Exam Performance Summary Report</b>", styles["Title"]))
        elements.append(Spacer(1, 12))

        # Overall statistics
        summary_text = f"""
        <b>Overall Average Score:</b> {results['overall_avg_score']*100:.2f}%<br/>
        <b>Overall Average Confidence:</b> {results['overall_avg_confidence']*100:.2f}%<br/>
        <b>Toughest Exam:</b> {results['toughest_exam']}<br/>
        <b>Easiest Exam:</b> {results['easiest_exam']}<br/>
        """
        elements.append(Paragraph(summary_text, styles["Normal"]))
        elements.append(Spacer(1, 12))

        # 📊 Question summary table — Flags removed
        data = [["Question ID", "Attempts", "Avg Score (%)", "Avg Confidence (%)"]]
        for qid, info in results["question_summary"].items():
            data.append([
                qid,
                info["attempts"],
                f"{info['avg_score']*100:.2f}%",
                f"{info['avg_confidence']*100:.2f}%"
            ])

        table = Table(data, colWidths=[100, 80, 100, 120])
        table_style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
        ])
        table.setStyle(table_style)

        elements.append(Paragraph("<b>Question Analytics</b>", styles["Heading2"]))
        elements.append(Spacer(1, 8))
        elements.append(table)
        elements.append(Spacer(1, 12))

        # 📈 Add charts from the charts directory
        chart_files = [
            "exam_difficulty.png",
            "question_difficulty.png",
            "confidence_vs_exam.png",
            "class_averages.png",
            "question_analytics.png",
        ]

        for chart_file in chart_files:
            chart_path = os.path.join(charts_dir, chart_file)
            if os.path.exists(chart_path):
                elements.append(Spacer(1, 12))
                elements.append(Image(chart_path, width=5.5 * inch, height=3.0 * inch))
            else:
                elements.append(Paragraph(f"⚠️ Missing chart: {chart_file}", styles["Normal"]))

        # Build the final report
        doc.build(elements)
        print(f"✅ Final report generated: {output_path}")

    except Exception as e:
        print(f"⚠️ Could not generate final report: {e}")
