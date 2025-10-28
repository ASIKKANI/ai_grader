import os
import json
from plagarism import PlagiarismDetector


DATA_DIR = "inpputs"


def load_all_student_answers(data_dir: str):
    """
    Load all student JSON files from the given folder.
    Returns {student_id: [answers]}.
    """
    student_answers = {}

    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                student_id = data.get("student_id", filename.replace(".json", ""))
                answers = [a.get("answer_text", "").strip() for a in data.get("answers", [])]

                if answers:
                    student_answers[student_id] = answers
                    print(f"✅ Loaded {filename} ({len(answers)} answers)")
                else:
                    print(f"⚠️ Skipped {filename}: No answers found.")
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")

    return student_answers


def display_intra_student_report(student_id: str, report: dict):
    """Display plagiarism within one student's answers."""
    if not report:
        return

    print(f"\n🧠 Intra-student plagiarism detected for {student_id}:")
    for pair, text in report.items():
        print(f"  🔁 {pair}")
        print(f"     🧾 Identical answer: \"{text[:80]}{'...' if len(text) > 80 else ''}\"")


def display_cross_student_report(report: list):
    """Display plagiarism between students."""
    if not report:
        print("\n✅ No cross-student plagiarism detected.")
        return

    print("\n⚠️ Cross-student plagiarism detected:")
    for entry in report:
        print(f"  🔸 {entry['student_a']} ↔ {entry['student_b']} | Q.{entry['question_index']}")
        print(f"     🧾 Identical answer: \"{entry['identical_answer'][:80]}{'...' if len(entry['identical_answer']) > 80 else ''}\"")


def main():
    print("📂 Loading all student answer files...\n")
    all_students = load_all_student_answers(DATA_DIR)
    print("-" * 70)

    if not all_students:
        print("❌ No student files found. Please add .json files in modules/data/")
        return

    detector = PlagiarismDetector()

    # 1️⃣ Intra-student plagiarism
    print("\n🧩 Checking for plagiarism within each student's own answers...")
    for student_id, answers in all_students.items():
        report = detector.check_within_student(answers)
        display_intra_student_report(student_id, report)
    print("-" * 70)

    # 2️⃣ Cross-student plagiarism
    print("\n🔗 Checking for plagiarism between all students...")
    cross_report = detector.check_across_students(all_students)
    display_cross_student_report(cross_report)
    print("-" * 70)

    print("\n✅ Full-answer plagiarism check completed for all students.")


if __name__ == "__main__":
    main()