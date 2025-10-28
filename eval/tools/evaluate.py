import json, os
from rule_engine import score_mcq, score_fillup, score_descriptive
from dotenv import load_dotenv
import google.generativeai as genai

# ------------------------------------------------------------------
#  Load environment and configure Gemini
# ------------------------------------------------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ------------------------------------------------------------------
#  Gemini semantic evaluator for descriptive answers
# ------------------------------------------------------------------
def call_gemini(question_text, real_answer, student_answer, rubric):
    """
    Uses Gemini 2.5 Flash for semantic grading.
    Returns: {"score": float, "confidence": float, "explanation": str}
    """
    points = rubric.get("points", 5)
    prompt = f"""
You are an academic evaluator AI that strictly follows scoring rubrics.

Question: {question_text}
Correct Answer (Reference): {real_answer}
Student Answer: {student_answer}
Rubric Details: {rubric}

Evaluation Rules:
1. If type is "mcq":
   - Award full points only if student's answer matches the correct answer exactly.
   - Otherwise, award 0 points.

2. If type is "fillup":
   - Award full points for an exact or equivalent correct answer.
   - Minor case differences or formatting differences should still be accepted.
   - Otherwise, award 0 points.

3. If type is "descriptive":
   - Check each keyword listed in the rubric.
   - Award the specific points assigned to each found keyword.
   - If student provides misinformation that contradicts reference answer, subtract the associated keyword points.
   - Consider clarity, context relevance, and completion. If explanation lacks meaning or is irrelevant, reduce score appropriately.
   - Score must not exceed the total rubric points.

Your Output:
Return ONLY a JSON response with the following keys:

{{
  "score": <numeric_score_between_0_and_{points}>,
  "confidence": <value_between_0.0_and_1.0>,
  "explanation": "A short one-sentence justification of scoring decision"
}}
"""


    try:
        # ✅ Correct model for the latest Gemini 2.5 Flash
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt)

        # Gemini sometimes adds extra text around JSON; safely extract only the JSON part
        text = response.text.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        json_str = text[start:end]

        return json.loads(json_str)

    except Exception as e:
        print("Gemini call failed:", e)
        return {
            "score": points * 0.5,
            "confidence": 0.5,
            "explanation": f"Gemini API fallback (error: {e})"
        }

# ------------------------------------------------------------------
def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ------------------------------------------------------------------
def evaluate(real_path, student_path, out_path):
    real = load(real_path)
    stud = load(student_path)
    exam_id = real["exam_id"]
    student_id = stud["student_id"]

    qmap = {q["question_id"]: q for q in real["answer_key"]}
    results = []
    total, max_total = 0.0, 0.0

    for ans in stud["answers"]:
        qid = ans["question_id"]
        student_ans = ans["answer"]
        q = qmap.get(qid)
        if not q:
            continue

        qtype = q["type"]
        rubric = q["rubric"]
        max_mark = rubric["points"]

        if qtype == "mcq":
            score, explain = score_mcq(student_ans, q["correct_answer"], max_mark)
            conf = 1.0 if score == max_mark else 0.6

        elif qtype == "fillup":
            score, explain = score_fillup(student_ans, q["correct_answer"], max_mark)
            conf = 1.0 if score == max_mark else 0.7

        else:
            question_text = q.get("question_text", q.get("question_id", "Descriptive question"))
            llm_output = call_gemini(question_text, q["correct_answer"], student_ans, rubric)
            score = llm_output["score"]
            explain = llm_output["explanation"]
            conf = llm_output["confidence"]

        total += score
        max_total += max_mark

        results.append({
            "question_id": qid,
            "type": qtype,
            "mark_awarded": score,
            "max_mark": max_mark,
            "confidence": conf,
            "explanation": explain,
            "flags": [] if score == max_mark else ["partial_or_incorrect"]
        })

    output = {
        "exam_id": exam_id,
        "student_id": student_id,
        "evaluation": results,
        "total_score": round(total, 2),
        "total_max": round(max_total, 2),
        "overall_confidence": round(total / max_total if max_total else 0, 2)
    }

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Evaluation saved to {out_path}")
    return output

# ------------------------------------------------------------------
if __name__ == "__main__":
    evaluate("inputs/real_answer_key.json",
             "inputs/student-answers.json",
             "outputs/evaluation_result.json")