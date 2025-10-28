# tools/validator.py
import json, sys, os

def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate(real_path, student_path):
    real = load(real_path)
    stud = load(student_path)
    errors = []

    if real.get('exam_id') != stud.get('exam_id'):
        errors.append("exam_id mismatch")

    real_qs = {q['question_id']: q for q in real.get('answer_key', [])}
    for a in stud.get('answers', []):
        qid = a.get('question_id')
        if qid not in real_qs:
            errors.append(f"student answer qid '{qid}' not found in real_answer_key")
            continue
        # basic required fields
        r = real_qs[qid]
        if 'rubric' not in r or 'points' not in r['rubric']:
            errors.append(f"rubric.points missing for question {qid}")

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(" -", e)
        return 1
    print("VALIDATION OK")
    return 0

if __name__ == '__main__':
    real = sys.argv[1] if len(sys.argv)>1 else "inputs/real_answer_key.json"
    stud = sys.argv[2] if len(sys.argv)>2 else "inputs/student_answers.json"
    sys.exit(validate(real, stud))