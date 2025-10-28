# tools/rule_engine.py
import re

def normalize(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', ' ', text.lower()).strip()

def score_mcq(student, correct, points):
    if student.strip().lower() == correct.strip().lower():
        return points, "Exact MCQ match"
    return 0.0, f"MCQ mismatch: expected {correct}, got {student}"

def score_fillup(student, correct, points):
    if normalize(student) == normalize(correct):
        return points, "Exact text match"
    elif normalize(correct) in normalize(student):
        return round(points * 0.5, 2), "Partial match (substring)"
    return 0.0, "No match"

def score_descriptive(student, rubric):
    keyw = rubric.get("keywords", [])
    points = rubric.get("points", 5)
    if not keyw:
        return 0.0, "No keywords in rubric"

    found = [k for k in keyw if k.lower() in student.lower()]
    ratio = len(found) / len(keyw)
    score = round(points * ratio, 2)
    explain = f"Found {len(found)}/{len(keyw)} keywords: {found}"
    return score, explain