import os
import json
from collections import defaultdict

def analyze_student_data(folder_path):
    exam_scores = defaultdict(list)  # exam_id -> list of score ratios (0..1)
    exam_confidences = defaultdict(list)
    student_results = defaultdict(lambda: {"total_score": 0, "total_max": 0, "confidences": []})

    # question_stats: qid -> aggregated info
    question_stats = defaultdict(lambda: {
        "total_score": 0.0,
        "total_max": 0.0,
        "attempts": 0,
        "confidences": [],
        "flags_counter": defaultdict(int)  # flag -> count
    })

    # Load JSON files
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                data = json.load(f)

            exam_id = data.get("exam_id")
            student_id = data.get("student_id")
            total_score = float(data.get("total_score", 0))
            total_max = float(data.get("total_max", 0))
            overall_conf = float(data.get("overall_confidence", 0.0))

            # student accumulators
            student_results[student_id]["total_score"] += total_score
            student_results[student_id]["total_max"] += total_max
            student_results[student_id]["confidences"].append(overall_conf)

            # exam accumulators (store fraction 0..1)
            if total_max > 0:
                exam_scores[exam_id].append(total_score / total_max)
            else:
                exam_scores[exam_id].append(0.0)
            exam_confidences[exam_id].append(overall_conf)

            # per-question accumulators
            for q in data.get("evaluation", []):
                qid = q.get("question_id")
                q_score = float(q.get("mark_awarded", 0))
                q_max = float(q.get("max_mark", 0))
                q_conf = float(q.get("confidence", 0.0))
                q_flags = q.get("flags", [])

                qs = question_stats[qid]
                qs["total_score"] += q_score
                qs["total_max"] += q_max
                qs["attempts"] += 1
                qs["confidences"].append(q_conf)

                for flag in q_flags:
                    qs["flags_counter"][flag] += 1

    # compute overall averages
    total_score_accum = sum([student_results[s]["total_score"] for s in student_results])
    total_max_accum = sum([student_results[s]["total_max"] for s in student_results])
    overall_avg_score = (total_score_accum / total_max_accum) if total_max_accum > 0 else 0.0

    all_conf_lists = [student_results[s]["confidences"] for s in student_results]
    flattened_confs = [c for sub in all_conf_lists for c in sub]
    overall_avg_confidence = (sum(flattened_confs) / len(flattened_confs)) if flattened_confs else 0.0

    # question-level summary derived values
    question_summary = {}
    for qid, info in question_stats.items():
        avg_score = (info["total_score"] / info["total_max"]) if info["total_max"] > 0 else 0.0
        avg_conf = (sum(info["confidences"]) / len(info["confidences"])) if info["confidences"] else 0.0
        flags_count = dict(info["flags_counter"])
        question_summary[qid] = {
            "attempts": info["attempts"],
            "avg_score": avg_score,            # fraction 0..1
            "avg_confidence": avg_conf,       # 0..1
            "flags_count": flags_count,
            "total_score": info["total_score"],
            "total_max": info["total_max"]
        }

    # exam-level summary (class averages)
    exam_difficulty = {}
    class_averages = {}
    for e, scores in exam_scores.items():
        avg_frac = (sum(scores) / len(scores)) if scores else 0.0
        exam_difficulty[e] = avg_frac
        class_averages[e] = avg_frac  # alias: fraction 0..1

    # identify most/least etc (same as before)
    most_struggled = None
    most_excellent = None
    if question_summary:
        most_struggled = min(question_summary, key=lambda k: question_summary[k]["avg_score"])
        most_excellent = max(question_summary, key=lambda k: question_summary[k]["avg_score"])

    toughest_exam = None
    if exam_difficulty:
        toughest_exam = min(exam_difficulty, key=exam_difficulty.get)

    # text summary print (unchanged)
    print("\n===== 📊 PERFORMANCE ANALYSIS REPORT =====")
    print(f"Overall Average Score: {overall_avg_score*100:.2f}%")
    print(f"Overall Average Confidence: {overall_avg_confidence*100:.2f}%")
    if toughest_exam:
        print(f"Toughest Exam: {toughest_exam} ({exam_difficulty[toughest_exam]*100:.2f}% avg score)")
    if most_struggled:
        print(f"Question Most Struggled With: {most_struggled} ({question_summary[most_struggled]['avg_score']*100:.2f}% avg)")
    if most_excellent:
        print(f"Question Most Excelled In: {most_excellent} ({question_summary[most_excellent]['avg_score']*100:.2f}% avg)")
    print("==========================================\n")

    return {
        "overall_avg_score": overall_avg_score,
        "overall_avg_confidence": overall_avg_confidence,
        "toughest_exam": toughest_exam,
        "exam_difficulty": exam_difficulty,
        "class_averages": class_averages,        # new: exam -> fraction
        "question_summary": question_summary,    # new: richer per-question analytics
        "most_struggled_question": most_struggled,
        "most_excellent_question": most_excellent
    }
