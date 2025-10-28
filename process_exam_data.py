import os
import json
import re
from pathlib import Path
from PIL import Image
import google.generativeai as genai

# Configure Gemini
os.environ["GOOGLE_API_KEY"] = "AIzaSyB0kWddIA-t3ohBoQyj-NAPaHNuzF84a3E"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

# Paths
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "D:\Projects\Hackathon\ai_grader\eval\test.jpg"
INPUT_DIR.mkdir(exist_ok=True)

STUDENT_IMG_PATH = INPUT_DIR / "student-uploaded.jpg"
ANSWER_KEY_PATH = INPUT_DIR / "answer-key.json"
STUDENT_OUTPUT_PATH = INPUT_DIR / "student-answers.json"


def extract_student_answers():
    if not STUDENT_IMG_PATH.exists():
        print("⚠️ Student answer sheet not found in inputs/ folder.")
        return False

    print("📸 Reading and extracting student answers...")
    image = Image.open(STUDENT_IMG_PATH)

    prompt = """
    Extract all readable exam content as strict JSON:

    {
      "student_id": "",
      "answers": [
        {
          "question_number": "",
          "question_text": "",
          "answer_text": ""
        }
      ]
    }

    Follow these rules:
    • Keep original text structure
    • Separate each question and its answer
    • Absolutely no summaries or markdown
    • Return only valid JSON
    """

    response = model.generate_content([prompt, image])
    raw = response.text.strip()

    # Cleanup any accidental markdown decorations
    clean = re.sub(r"```json|```", "", raw).strip()

    try:
        data = json.loads(clean)
    except json.JSONDecodeError:
        print("⚠️ JSON malformed! Saving raw text instead.")
        data = {"raw_output": raw}

    with open(STUDENT_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Extracted answers saved → {STUDENT_OUTPUT_PATH}")
    return True


def answer_key_exists():
    if ANSWER_KEY_PATH.exists():
        print(f"📚 Answer key found → {ANSWER_KEY_PATH}")
        return True
    else:
        print("🚫 No answer key available!")
        print("Please use Professor Answer Collector HTML to generate one.")
        return False


def main():
    print("\n🚀 Smart Exam Extractor Starting...\n")

    has_student = extract_student_answers()
    has_key = answer_key_exists()

    print("\n📌 Status Report:")
    if has_student and has_key:
        print("✅ Ready for auto-evaluation phase! Run evaluation script next.")
    else:
        if not has_student:
            print("➡️ Add student-uploaded.jpg inside inputs/ folder.")
        if not has_key:
            print("➡️ Generate answer-key.json via HTML and place in inputs/ folder.")

    print("\n🟢 Process Completed.\n")


if __name__ == "__main__":
    main()
