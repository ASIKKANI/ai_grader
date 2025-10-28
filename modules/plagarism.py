from typing import List, Dict


class PlagiarismDetector:
    """
    Detects plagiarism only when two answers are identical (full-text match).
    """

    def normalize(self, text: str) -> str:
        """
        Normalize text by trimming spaces and converting to lowercase.
        """
        return " ".join(text.lower().strip().split())

    def check_within_student(self, answers: List[str]) -> Dict[str, str]:
        """
        Check if a student repeated the same full answer multiple times.
        Returns { 'Answer i ↔ Answer j': answer_text }
        """
        results = {}
        normalized = [self.normalize(ans) for ans in answers]

        for i in range(len(normalized)):
            for j in range(i + 1, len(normalized)):
                if normalized[i] and normalized[i] == normalized[j]:
                    results[f"Answer {i+1} ↔ Answer {j+1}"] = answers[i]

        return results

    def check_across_students(self, student_answers: Dict[str, List[str]]) -> List[Dict]:
        """
        Check if two students have identical answers (whole answer).
        Returns list of dicts with matching question indices and answer text.
        """
        reports = []
        student_ids = list(student_answers.keys())

        for i in range(len(student_ids)):
            for j in range(i + 1, len(student_ids)):
                s1, s2 = student_ids[i], student_ids[j]
                ans1, ans2 = student_answers[s1], student_answers[s2]

                for q_idx in range(min(len(ans1), len(ans2))):
                    if self.normalize(ans1[q_idx]) == self.normalize(ans2[q_idx]) and ans1[q_idx].strip():
                        reports.append({
                            "student_a": s1,
                            "student_b": s2,
                            "question_index": q_idx + 1,
                            "identical_answer": ans1[q_idx]
                        })

        return reports