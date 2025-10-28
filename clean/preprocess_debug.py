import cv2
import numpy as np
import os
from pathlib import Path

DEBUG_SAVE = True
DEBUG_DIR = "outputs_debug"

def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)

def save_debug(img, base, stage):
    if DEBUG_SAVE:
        ensure_dir(DEBUG_DIR)
        cv2.imwrite(os.path.join(DEBUG_DIR, f"{base}__{stage}.png"), img)

def preprocess_image(input_path, output_path):
    base = Path(input_path).stem

    # Step 1 — Grayscale
    img = cv2.imread(input_path)
    if img is None:
        print(f"Skipping {input_path} (cannot read)")
        return
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    save_debug(gray, base, "1_grayscale")

    # Step 2 — Enhance contrast (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)
    save_debug(contrast, base, "2_contrast")

    # Step 3 — Remove noise (bilateral filter)
    denoised = cv2.bilateralFilter(contrast, 7, 75, 75)
    save_debug(denoised, base, "3_denoised")

    # Step 4 — Convert to binary (adaptive threshold)
    binary = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        21, 9
    )
    save_debug(binary, base, "4_binary")

    # Save final output
    ensure_dir(os.path.dirname(output_path) or ".")
    cv2.imwrite(output_path, binary)
    print(f"✅ Processed: {os.path.basename(input_path)} | Debug stages → {DEBUG_DIR}/")

def process_all(input_folder="sample_images", output_folder="outputs"):
    ensure_dir(output_folder)
    supported = (".png", ".jpg", ".jpeg", ".tif", ".bmp")
    for fname in sorted(os.listdir(input_folder)):
        if fname.lower().endswith(supported):
            in_path = os.path.join(input_folder, fname)
            out_path = os.path.join(output_folder, fname)
            preprocess_image(in_path, out_path)

if __name__ == "__main__":
    process_all()

