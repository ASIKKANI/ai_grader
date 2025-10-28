import os
import glob
import csv
from tabulate import tabulate  # for beautiful console tables
from analyzer import analyze_student_data
from visualizer import (
    plot_exam_difficulty,
    plot_question_difficulty,
    plot_confidence_vs_exam,
    plot_class_averages,
    plot_question_analytics
)
from report_generator import generate_final_report


def clean_charts_directory(charts_dir):
    """Remove existing PNG charts before creating new ones."""
    if os.path.exists(charts_dir):
        old_charts = glob.glob(os.path.join(charts_dir, "*.png"))
        for chart in old_charts:
            try:
                os.remove(chart)
            except Exception as e:
                print(f"⚠️ Could not remove {chart}: {e}")
    else:
        os.makedirs(charts_dir, exist_ok=True)


if __name__ == "__main__":
    # Define directories
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "../data")
    charts_dir = os.path.join(base_dir, "../reports/charts")
    final_report_path = os.path.join(base_dir, "../reports/final_report.png")
    csv_path = os.path.join(base_dir, "../reports/question_summary.csv")

    # Ensure directories exist
    os.makedirs(os.path.dirname(final_report_path), exist_ok=True)
    clean_charts_directory(charts_dir)

    # 🔍 Step 1: Analyze all student data
    results = analyze_student_data(data_dir)

    # 🧾 Step 2: Export question analytics to CSV (Flags column removed)
    try:
        with open(csv_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Question ID", "Attempts", "Avg Score (%)", "Avg Confidence (%)"])
            for qid, info in results["question_summary"].items():
                writer.writerow([
                    qid,
                    info["attempts"],
                    f"{info['avg_score']*100:.2f}%",
                    f"{info['avg_confidence']*100:.2f}%"
                ])
        print(f"✅ CSV exported to: {csv_path}")
    except Exception as e:
        print(f"⚠️ Could not save CSV: {e}")

    # 🎨 Step 3: Display a clean summary table in console (no Flags column)
    try:
        table_data = []
        for qid, info in results["question_summary"].items():
            table_data.append([
                qid,
                info["attempts"],
                f"{info['avg_score']*100:.2f}%",
                f"{info['avg_confidence']*100:.2f}%"
            ])

        print("\n📊 Question Performance Summary:\n")
        print(tabulate(
            table_data,
            headers=["Question ID", "Attempts", "Avg Score", "Avg Confidence"],
            tablefmt="fancy_grid",
            stralign="center"
        ))
    except Exception as e:
        print(f"⚠️ Could not display table: {e}")

    # 📈 Step 4: Generate charts
    plot_exam_difficulty(results["exam_difficulty"], charts_dir)
    plot_question_difficulty({k: v["avg_score"] for k, v in results["question_summary"].items()}, charts_dir)
    plot_confidence_vs_exam(results["exam_difficulty"], results["overall_avg_confidence"], charts_dir)
    plot_class_averages(results["class_averages"], charts_dir)
    plot_question_analytics(results["question_summary"], charts_dir)

    # 🖼️ Step 5: Generate final report image
    generate_final_report(results, charts_dir, final_report_path)

    print(f"\n🖼️ Final report image generated at: {final_report_path}")


