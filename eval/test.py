import os
import google.generativeai as genai
from PIL import Image

# ✅ Configure Gemini API
os.environ["GOOGLE_API_KEY"] = "AIzaSyB0kWddIA-t3ohBoQyj-NAPaHNuzF84a3E"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# ✅ Load model
model = genai.GenerativeModel("gemini-2.5-flash")

# ✅ Load handwritten answer image
image_path = "/Users/bharani/Desktop/eval/test.jpg"   # <-- change this path
image = Image.open(image_path)

# ✅ Extraction prompt
extract_prompt = """
Extract all readable text from this image in clear line-by-line format.
Preserve the structure of questions and answers as accurately as possible.
Do NOT summarize or skip any part.
"""

# ✅ Run Gemini extraction
response_extract = model.generate_content([extract_prompt, image])

# ✅ Save extracted text
with open("extracted_text.txt", "w") as f:
    f.write(response_extract.text)

print("\n--- ✅ Extracted Text ---\n")
print(response_extract.text)
print("\n(Text also saved as extracted_text.txt)")