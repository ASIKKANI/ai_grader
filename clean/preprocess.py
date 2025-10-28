import cv2
import numpy as np
import os

def clean_image(input_path, output_path):
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Skipping {input_path} (cannot read)")
        return

    # 1. Edge-preserving denoise (keeps handwriting strokes)
    blur = cv2.bilateralFilter(img, 7, 50, 50)

    # 2. Gentle local contrast enhancement (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(blur)

    # 3. Adaptive thresholding tuned for handwriting
    thresh = cv2.adaptiveThreshold(
        enhanced, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        17, 7
    )

    # 4. Light morphological cleaning (preserves thin strokes)
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # 5. Mild sharpening (keeps text crisp without thickening)
    kernel_sharp = np.array([[0, -0.5, 0],
                             [-0.5, 3, -0.5],
                             [0, -0.5, 0]])
    sharpened = cv2.filter2D(cleaned, -1, kernel_sharp)

    # Save the cleaned image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, sharpened)
    print(f"✅ Cleaned and enhanced: {os.path.basename(input_path)} → {output_path}")

def clean_all_images(input_folder="sample_images", output_folder="outputs"):
    supported_ext = (".png", ".jpg", ".jpeg", ".tif", ".bmp")
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(supported_ext)]
    if not files:
        print("No valid image files found in sample_images/")
        return
    for filename in files:
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        clean_image(input_path, output_path)

if __name__ == "__main__":
    clean_all_images()




