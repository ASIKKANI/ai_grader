from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import json
import tempfile
from modules.plagarism import PlagiarismDetector

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store latest result globally
LATEST_PLAGIARISM_REPORT = {
    "intra_student_results": [],
    "cross_student_results": []
}

@app.post("/plagiarism/check")
async def plagiarism_check(files: list[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    student_answers = {}

    # Save and extract answers from uploaded JSON files
    for file in files:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))

        student_id = data.get("student_id", file.filename.replace(".json", ""))
        answers = [a.get("answer_text", "") for a in data.get("answers", [])]
        student_answers[student_id] = answers

    detector = PlagiarismDetector()

    # Intra-student check
    intra_report = []
    for sid, answers in student_answers.items():
        result = detector.check_within_student(answers)
        if result:
            intra_report.append({"student_id": sid, "matches": result})

    # Cross-student check
    cross_report = detector.check_across_students(student_answers)

    # Save results to global variable
    global LATEST_PLAGIARISM_REPORT
    LATEST_PLAGIARISM_REPORT = {
        "intra_student_results": intra_report,
        "cross_student_results": cross_report
    }

    return LATEST_PLAGIARISM_REPORT


@app.get("/plagiarism/results")
async def get_latest_results():
    return LATEST_PLAGIARISM_REPORT
