# align_single.py
# Single image alignment using OpenCV
# Author: Asik Kani ⚡

import cv2
import numpy as np

def align_image(image_path, output_path="aligned_output.jpg"):
    img = cv2.imread(image_path)
    if img is None:
        print("❌ Image not found.")
        return None

    # Step 1: Resize + grayscale + edge detect
    img = cv2.resize(img, (1000, 1400))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 75, 200)

    # Step 2: Find largest contour (paper)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    doc_cnt = None
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            doc_cnt = approx
            break

    if doc_cnt is None:
        print("❌ Could not find paper outline. Try clearer scan.")
        return None

    # Step 3: Order points
    def order_points(pts):
        pts = pts.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]      # top-left
        rect[2] = pts[np.argmax(s)]      # bottom-right
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]   # top-right
        rect[3] = pts[np.argmax(diff)]   # bottom-left
        return rect

    rect = order_points(doc_cnt)
    (tl, tr, br, bl) = rect

    # Step 4: Perspective transform
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = int(max(widthA, widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = int(max(heightA, heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    aligned = cv2.warpPerspective(img, M, (maxWidth, maxHeight))

    # Step 5: Enhance and save
    gray_aligned = cv2.cvtColor(aligned, cv2.COLOR_BGR2GRAY)
    enhanced = cv2.adaptiveThreshold(gray_aligned, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 15, 8)

    cv2.imwrite(output_path, enhanced)
    print(f"✅ Image aligned and saved as: {output_path}")

    return enhanced

# ---------- Run ----------
if __name__ == "__main__":
    image_path = input("📂 Enter image path: ").strip()
    output = align_image(image_path)
    if output is not None:
        cv2.imshow("Aligned Output", output)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
