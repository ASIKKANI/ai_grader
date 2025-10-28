import os
import re
import json
from pathlib import Path
from PIL import Image
import google.generativeai as genai

# ✅ Configure Gemini API
os.environ["GOOGLE_API_KEY"] = "AIzaSyB0kWddIA-t3ohBoQyj-NAPaHNuzF84a3E"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# ✅ Load model
model = genai.GenerativeModel("gemini-2.5-flash")

# ✅ Input image path
image_path = r"D:\Projects\Hackathon\ai_grader\eval\test.jpg"
image = Image.open(image_path)

# ✅ Extraction prompt
extract_prompt = """
Extract all readable text from this image and organize it into JSON format:

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

Rules:
- Each question and answer must be separate.
- Preserve text line-by-line.
- Do NOT wrap or summarize.
Return only JSON — no markdown, no explanations.
"""

# ✅ Run Gemini extraction
response = model.generate_content([extract_prompt, image])
raw_text = response.text.strip()

# ✅ Clean Markdown fences if present
clean_text = re.sub(r"^```json\s*|\s*```$", "", raw_text.strip(), flags=re.MULTILINE).strip()

# ✅ Try to parse JSON safely
try:
    data = json.loads(clean_text)
except json.JSONDecodeError:
    print("⚠️ Gemini returned malformed JSON — saving raw output instead.")
    data = {"raw_output": raw_text}

# ✅ Save to inputs/student-answers.json
output_dir = Path("inputs")
output_dir.mkdir(exist_ok=True)
output_path = output_dir / "student-answers.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Clean JSON saved to {output_path}\n")
print(json.dumps(data, indent=2, ensure_ascii=False))
