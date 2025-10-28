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


def generate_final_report_pdf(results, charts_dir, output_path):
    """Creates a clean, readable PDF report containing analytics, tables, and charts."""

    try:
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=60,
            bottomMargin=40
        )
        styles = getSampleStyleSheet()
        elements = []

        # 🏷️ Title
        elements.append(Paragraph("<b>Exam Performance Report</b>", styles["Title"]))
        elements.append(Spacer(1, 12))

        # 📊 Summary Info
        summary_html = f"""
        <b>Overall Average Score:</b> {results['overall_avg_score']*100:.2f}%<br/>
        <b>Overall Average Confidence:</b> {results['overall_avg_confidence']*100:.2f}%<br/>
        <b>Toughest Exam:</b> {results['toughest_exam']}<br/>
        <b>Easiest Exam:</b> {results['easiest_exam']}<br/>
        """
        elements.append(Paragraph(summary_html, styles["Normal"]))
        elements.append(Spacer(1, 16))

        # 🧾 Question Summary Table (No Flags)
        data = [["Question ID", "Attempts", "Avg Score (%)", "Avg Confidence (%)"]]
        for qid, info in results["question_summary"].items():
            data.append([
                qid,
                info["attempts"],
                f"{info['avg_score']*100:.2f}%",
                f"{info['avg_confidence']*100:.2f}%"
            ])

        table = Table(data, colWidths=[100, 80, 100, 120])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2b4c7e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
        ]))

        elements.append(Paragraph("<b>Question Analytics</b>", styles["Heading2"]))
        elements.append(Spacer(1, 8))
        elements.append(table)
        elements.append(Spacer(1, 16))

        # 📉 Charts Section
        chart_files = [
            "exam_difficulty.png",
            "question_difficulty.png",
            "confidence_vs_exam.png",
            "class_averages.png",
            "question_analytics.png"
        ]

        elements.append(Paragraph("<b>Visual Analytics</b>", styles["Heading2"]))
        elements.append(Spacer(1, 8))

        for chart_file in chart_files:
            chart_path = os.path.join(charts_dir, chart_file)
            if os.path.exists(chart_path):
                elements.append(Image(chart_path, width=5.5 * inch, height=3.0 * inch))
                elements.append(Spacer(1, 12))
            else:
                elements.append(Paragraph(f"⚠️ Missing chart: {chart_file}", styles["Normal"]))

        # 🧱 Build PDF
        doc.build(elements)
        print(f"✅ PDF report generated at: {output_path}")

    except Exception as e:
        print(f"⚠️ Could not generate PDF: {e}")
