from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import shutil, os, uuid, time
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
async def process_images(files: list[UploadFile] = File(...)):
    """Process multiple uploaded images"""
    results = []
    try:
        for file in files:
            start_time = time.time()
            unique_name = f"{uuid.uuid4().hex}_{file.filename}"
            upload_path = os.path.join("uploads", unique_name)
            with open(upload_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # ✅ Step 1 – Clean
            cleaned_output = os.path.join("clean/outputs", unique_name)
            preprocess_image(upload_path, cleaned_output)

            # ✅ Step 2 – Align (get angle)
            aligned_output = os.path.join("aligning/outputs", f"{unique_name}_aligned.png")
            try:
                aligned_img = align_robust(cleaned_output, aligned_output)
                angle_applied = getattr(aligned_img, "angle", 0.0) if hasattr(aligned_img, "angle") else 0.0
            except Exception as e:
                print(f"⚠️ Alignment failed for {file.filename}: {e}")
                angle_applied = 0.0

            # ✅ Step 3 – Collect debug images
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
                            stage_label = next((label for key, label in stage_names.items() if key in f),
                                               "Intermediate Stage")
                            debug_images.append({"url": f"/{folder}/{f}", "label": stage_label})

            if not debug_images:
                debug_images = [{"url": f"/clean/outputs/{os.path.basename(cleaned_output)}",
                                 "label": "Cleaned Output"}]

            elapsed = round(time.time() - start_time, 2)
            print(f"✅ {file.filename} processed in {elapsed}s")

            results.append({
                "filename": file.filename,
                "original": f"/uploads/{unique_name}",
                "cleaned": f"/clean/outputs/{os.path.basename(cleaned_output)}",
                "aligned": f"/aligned_outputs/{os.path.basename(aligned_output)}",
                "angle": round(float(angle_applied), 2),
                "time": elapsed,
                "debugs": debug_images
            })

        return JSONResponse(results)

    except Exception as e:
        print("❌ Error:", e)
        return JSONResponse({"error": str(e)}, status_code=500)
