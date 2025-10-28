import os
import re
import json
from pathlib import Path
from PIL import Image
import google.generativeai as genai

# Configure Gemini API
os.environ["GOOGLE_API_KEY"] = "AIzaSyB0kWddIA-t3ohBoQyj-NAPaHNuzF84a3E"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-2.5-flash")

# Input image path
image_path = r"D:\Projects\Hackathon\ai_grader\eval\test.jpg"
image = Image.open(image_path)

# Enhanced prompt with roll number extraction
extract_prompt = """
Extract text from the exam sheet and return ONLY valid JSON in this exact structure:

{
  "roll_number": "",
  "answers": [
    {
      "question_number": "",
      "question_text": "",
      "answer_text": ""
    }
  ]
}

Rules:
• Identify the student's roll number (look especially at the top-right or top area).
• Keep every question and answer separate.
• No summaries, no rephrasing, keep exact visible text.
• No markdown formatting.
• Ensure valid JSON only.
"""

# Run Gemini extraction
response = model.generate_content([extract_prompt, image])
raw_text = response.text.strip()

# Clean JSON formatting if wrapped
clean_text = re.sub(r"```json|```", "", raw_text).strip()

# Validate JSON
try:
    data = json.loads(clean_text)
except json.JSONDecodeError:
    print("⚠️ JSON malformed — raw text saved for debugging.")
    data = {"raw_output": raw_text}

# Save extracted output
output_dir = Path("inputs")
output_dir.mkdir(exist_ok=True)
output_path = output_dir / "student-answers.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Student data extracted successfully → {output_path}\n")
print(json.dumps(data, indent=2, ensure_ascii=False))
