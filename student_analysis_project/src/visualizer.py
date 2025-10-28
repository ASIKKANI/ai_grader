import matplotlib.pyplot as plt
import os
import math

def plot_exam_difficulty(exam_difficulty, save_path):
    exams = list(exam_difficulty.keys())
    avg_scores = [exam_difficulty[e] * 100 for e in exams]

    plt.figure(figsize=(8, 5))
    plt.bar(exams, avg_scores)  # use default colors for neutrality
    plt.title("Average Score per Exam")
    plt.xlabel("Exam ID")
    plt.ylabel("Average Score (%)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, "exam_difficulty.png"))
    plt.close()

def plot_question_difficulty(question_difficulty, save_path):
    questions = list(question_difficulty.keys())
    avg_scores = [question_difficulty[q] * 100 for q in questions]

    plt.figure(figsize=(10, 6))
    plt.barh(questions, avg_scores)
    plt.title("Average Performance by Question")
    plt.xlabel("Average Score (%)")
    plt.ylabel("Question ID")
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, "question_difficulty.png"))
    plt.close()

def plot_confidence_vs_exam(exam_difficulty, overall_confidence, save_path):
    exams = list(exam_difficulty.keys())
    avg_scores = [exam_difficulty[e] * 100 for e in exams]
    confidences = [overall_confidence * 100 for _ in exams]

    plt.figure(figsize=(8, 5))
    plt.plot(exams, avg_scores, marker='o', label='Average Score')
    plt.plot(exams, confidences, marker='x', label='Confidence', linestyle='--')
    plt.title("Exam Performance vs Grading Confidence")
    plt.xlabel("Exam ID")
    plt.ylabel("Percentage (%)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, "confidence_vs_exam.png"))
    plt.close()

# ----------------------
# NEW: Class averages bar chart (clean)
# ----------------------
def plot_class_averages(class_averages, save_path):
    """
    class_averages: dict exam_id -> fraction (0..1)
    """
    exams = list(class_averages.keys())
    averages = [class_averages[e] * 100 for e in exams]

    plt.figure(figsize=(9, 5))
    # clean style: simple bars, light grid
    plt.bar(exams, averages)
    plt.title("Class Average per Exam")
    plt.xlabel("Exam ID")
    plt.ylabel("Class Average (%)")
    plt.ylim(0, 100)
    plt.grid(axis='y', linestyle=':', linewidth=0.7, alpha=0.7)
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, "class_averages.png"))
    plt.close()

# ----------------------
# NEW: Question analytics table saved as PNG
# ----------------------
def plot_question_analytics(question_summary, save_path):
    """
    question_summary: dict of qid -> {attempts, avg_score, avg_confidence, flags_count}
    Produces a table image question_analytics.png
    """
    # Build table rows
    columns = ["Question ID", "Attempts", "Avg Score (%)", "Avg Confidence (%)", "Flags"]
    rows = []
    for qid, info in sorted(question_summary.items()):
        attempts = info.get("attempts", 0)
        avg_score_pct = info.get("avg_score", 0.0) * 100
        avg_conf_pct = info.get("avg_confidence", 0.0) * 100
        flags_dict = info.get("flags_count", {})
        flags_str = ", ".join(f"{k}:{v}" for k, v in flags_dict.items()) if flags_dict else ""
        rows.append([qid, attempts, f"{avg_score_pct:.1f}", f"{avg_conf_pct:.1f}", flags_str])

    # Determine figure size based on number of rows (so it remains readable)
    n_rows = max(1, len(rows))
    row_height = 0.4
    fig_height = max(2.5, n_rows * row_height + 1.5)

    fig, ax = plt.subplots(figsize=(10, fig_height))
    ax.axis('off')  # hide axes

    # Create table
    table = ax.table(cellText=rows, colLabels=columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.2)

    plt.title("Question Analytics", pad=12)
    plt.tight_layout()
    out_path = os.path.join(save_path, "question_analytics.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
