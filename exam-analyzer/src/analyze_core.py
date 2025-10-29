import os
import json
import pandas as pd
import matplotlib.pyplot as plt


def analyze_json_data(data_dir, output_dir, csv_output_path):
    """Analyze multiple JSON exam files and produce summary + graphs."""

    records = []

    # Parse each JSON file
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            with open(os.path.join(data_dir, filename), "r", encoding="utf-8") as f:
                data = json.load(f)
                exam_id = data.get("exam_id")
                student_id = data.get("student_id")

                for q in data.get("evaluation", []):
                    records.append({
                        "exam_id": exam_id,
                        "student_id": student_id,
                        "question_id": q["question_id"],
                        "type": q["type"],
                        "mark_awarded": q["mark_awarded"],
                        "max_mark": q["max_mark"],
                        "confidence": q["confidence"],
                        "flags": ", ".join(q["flags"]) if q["flags"] else "none"
                    })

    df = pd.DataFrame(records)

    if df.empty:
        return {"error": "No data found."}

    # Compute derived metrics
    df["percentage"] = (df["mark_awarded"] / df["max_mark"]) * 100

    # Export per-question CSV
    os.makedirs(os.path.dirname(csv_output_path), exist_ok=True)
    df.to_csv(csv_output_path, index=False)

    os.makedirs(output_dir, exist_ok=True)

    # Plot 1: Score distribution
    plt.figure()
    df["percentage"].hist(bins=10)
    plt.title("Score Distribution")
    plt.xlabel("Percentage")
    plt.ylabel("Frequency")
    score_dist_path = os.path.join(output_dir, "score_distribution.png")
    plt.savefig(score_dist_path)
    plt.close()

    # Plot 2: Flag Breakdown
    plt.figure()
    df["flags"].value_counts().plot(kind="bar")
    plt.title("Flag Breakdown")
    plt.xlabel("Flags")
    plt.ylabel("Count")
    flag_breakdown_path = os.path.join(output_dir, "flag_breakdown.png")
    plt.tight_layout()
    plt.savefig(flag_breakdown_path)
    plt.close()

    # Plot 3: Average Mark per Question
    plt.figure()
    df.groupby("question_id")["mark_awarded"].mean().plot(kind="bar")
    plt.title("Average Mark per Question")
    plt.xlabel("Question ID")
    plt.ylabel("Average Marks")
    avg_mark_path = os.path.join(output_dir, "avg_mark.png")
    plt.tight_layout()
    plt.savefig(avg_mark_path)
    plt.close()

    # Plot 4: Average Confidence per Question
    plt.figure()
    df.groupby("question_id")["confidence"].mean().plot(kind="bar", color="orange")
    plt.title("Average Confidence per Question")
    plt.xlabel("Question ID")
    plt.ylabel("Confidence")
    avg_conf_path = os.path.join(output_dir, "avg_confidence.png")
    plt.tight_layout()
    plt.savefig(avg_conf_path)
    plt.close()

    # Return image paths relative to static/
    return {
        "images": {
            "score_distribution": "images/score_distribution.png",
            "flag_breakdown": "images/flag_breakdown.png",
            "avg_mark": "images/avg_mark.png",
            "avg_confidence": "images/avg_confidence.png"
        },
        "csv_path": "outputs/question_analysis.csv"
    }
