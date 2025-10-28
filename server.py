from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import shutil, os, uuid
import numpy as np
from clean.preprocess_debug import preprocess_image
from aligning.align_robust import align_robust

app = FastAPI()

# ✅ Ensure required folders exist
for folder in ["uploads", "outputs_debug", "aligned_outputs", "clean/outputs"]:
    os.makedirs(folder, exist_ok=True)

# ✅ Mount static directories
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/outputs_debug", StaticFiles(directory="outputs_debug"), name="outputs_debug")
app.mount("/aligned_outputs", StaticFiles(directory="aligning/outputs"), name="aligned_outputs")
app.mount("/clean/outputs", StaticFiles(directory="clean/outputs"), name="clean_outputs")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/process/")
async def process_image(file: UploadFile = File(...)):
    try:
        # ✅ Generate unique name & save uploaded file
        unique_name = f"{uuid.uuid4().hex}_{file.filename}"
        upload_path = os.path.join("uploads", unique_name)
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # ✅ Step 1 – Clean (preprocessing)
        cleaned_output = os.path.join("clean/outputs", unique_name)
        preprocess_image(upload_path, cleaned_output)

        # ✅ Step 2 – Align (capture angle safely)
        aligned_output = os.path.join("aligning/outputs", f"{unique_name}_aligned.png")
        try:
            angle_applied = align_robust(cleaned_output, aligned_output)
            if isinstance(angle_applied, np.ndarray):
                angle_applied = float(angle_applied.mean())
        except Exception as e:
            print("⚠️ Alignment failed:", e)
            angle_applied = 0.0

        # ✅ Step 3 – Collect all debug stage images with names
        stage_names = {
            "1_gray": "Step 1 – Grayscale",
            "2_blur": "Step 2 – Noise Reduction",
            "3_edges": "Step 3 – Edge Detection",
            "4_binary": "Step 4 – Thresholding",
            "5_morph": "Step 5 – Morphological Filter",
            "6_contours": "Step 6 – Contour Refinement"
        }

        debug_images = []
        for folder in ["outputs_debug", "clean/outputs_debug"]:
            if os.path.exists(folder):
                for f in sorted(os.listdir(folder)):
                    if unique_name.split("_")[0] in f:
                        stage_label = next((label for key, label in stage_names.items() if key in f), "Intermediate Stage")
                        debug_images.append({"url": f"/{folder}/{f}", "label": stage_label})

        # ✅ Fallback if no debug images found
        if not debug_images:
            debug_images = [{"url": f"/clean/outputs/{os.path.basename(cleaned_output)}", "label": "Cleaned Output"}]

        print(f"✅ Finished processing {file.filename}")

        return JSONResponse({
            "original": f"/uploads/{unique_name}",
            "cleaned": f"/clean/outputs/{os.path.basename(cleaned_output)}",
            "aligned": f"/aligned_outputs/{os.path.basename(aligned_output)}",
            "angle": round(float(angle_applied), 2),
            "debugs": debug_images
        })

    except Exception as e:
        print("❌ Error:", e)
        return JSONResponse({"error": str(e)}, status_code=500)
