# align_robust.py
# Robust alignment for tilted question papers
# Combines three angle estimators (minAreaRect, PCA, Hough) and uses the median angle.
# Author: Asik Kani (improved)

import cv2
import numpy as np
import math

def angle_from_minarea(thresh):
    # coords of foreground pixels
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) < 10:
        return None
    rect = cv2.minAreaRect(coords)
    angle = rect[-1]
    # convert OpenCV angle to rotation angle (degrees)
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    return float(angle)

def angle_from_pca(thresh):
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) < 10:
        return None
    # PCA using SVD on centered coords
    coords = coords.astype(np.float32)
    mean = coords.mean(axis=0)
    centered = coords - mean
    u, s, vt = np.linalg.svd(centered, full_matrices=False)
    # first principal component direction
    pc = vt[0]
    angle_rad = math.atan2(pc[0], pc[1])  # note: coords are (row=y, col=x) so swap
    angle_deg = np.degrees(angle_rad)
    # convert to deskew rotation (negative)
    return -angle_deg

def angle_from_hough(gray):
    # detect strong lines and compute their angles
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    # use probabilistic Hough to get line segments
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=20)
    if lines is None:
        return None
    angles = []
    for x1, y1, x2, y2 in lines[:,0]:
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            continue
        ang = math.degrees(math.atan2(dy, dx))
        # we want angles near 0 (horizontal) — convert to -90..90
        if ang > 90:
            ang -= 180
        if ang <= -90:
            ang += 180
        # consider mostly near-horizontal lines; filter steep ones
        if abs(ang) < 45:
            angles.append(ang)
    if len(angles) == 0:
        return None
    # return mean of angles
    return float(np.median(angles))

def normalize_angle(a):
    # normalize to -90..90
    if a is None:
        return None
    a = float(a)
    while a <= -90:
        a += 180
    while a > 90:
        a -= 180
    return a

def rotate_image(img, angle):
    (h, w) = img.shape[:2]
    center = (w//2, h//2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def crop_to_content(rotated):
    gray = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # invert so content is white
    th_inv = 255 - th
    coords = cv2.findNonZero(th_inv)
    if coords is None:
        return rotated
    x, y, w, h = cv2.boundingRect(coords)
    cropped = rotated[y:y+h, x:x+w]
    return cropped

def preprocess_for_angles(img):
    # create a threshold image highlighting ink/text
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # equalize and blur a bit
    gray_eq = cv2.equalizeHist(gray)
    blur = cv2.GaussianBlur(gray_eq, (5,5), 0)
    # adaptive threshold might help with uneven lighting
    th = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 31, 15)
    # invert: we want ink=white (255)
    th_inv = 255 - th
    # morphological opening to remove small noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    th_inv = cv2.morphologyEx(th_inv, cv2.MORPH_OPEN, kernel, iterations=1)
    return gray_eq, th_inv

def align_robust(image_path, output_path="aligned_robust.jpg", debug=False):
    img = cv2.imread(image_path)
    if img is None:
        print("❌ Image not found.")
        return None

    # Work on copy for angle estimation but keep original resolution
    gray_for_hough, thresh = preprocess_for_angles(img)

    a1 = angle_from_minarea(thresh)
    a2 = angle_from_pca(thresh)
    a3 = angle_from_hough(gray_for_hough)

    a1 = normalize_angle(a1)
    a2 = normalize_angle(a2)
    a3 = normalize_angle(a3)

    # collect available angles
    candidates = [a for a in (a1, a2, a3) if a is not None]
    if len(candidates) == 0:
        print("⚠️ Could not estimate skew angle — saving original.")
        cv2.imwrite(output_path, img)
        return img

    # use median for robustness
    final_angle = float(np.median(candidates))

    # If angle tiny, skip rotation
    if abs(final_angle) < 0.15:
        print(f"🧭 Estimated angle {final_angle:.3f}° (tiny) — no rotation applied.")
        rotated = img.copy()
    else:
        rotated = rotate_image(img, final_angle)

    cropped = crop_to_content(rotated)

    cv2.imwrite(output_path, cropped)
    if debug:
        print("Angles (deg): minAreaRect={:.3f}, PCA={:.3f}, Hough={:.3f}".format(
            a1 if a1 is not None else float('nan'),
            a2 if a2 is not None else float('nan'),
            a3 if a3 is not None else float('nan')))
        print(f"Final applied rotation: {final_angle:.3f}°")
        # save debug visuals
        cv2.imwrite("debug_thresh.png", thresh)
        cv2.imwrite("debug_rotated.png", rotated)
        cv2.imwrite("debug_cropped.png", cropped)

    print(f"✅ Aligned saved: {output_path}  (angle applied: {final_angle:.3f}°)")
    return cropped

if __name__ == "__main__":
    path = input("📂 Enter image path: ").strip()
    out = input("📂 Output filename (ENTER for aligned_robust.jpg): ").strip()
    if out == "":
        out = "aligned_robust.jpg"
    aligned = align_robust(path, out, debug=True)
    if aligned is not None:
        cv2.imshow("Aligned", aligned)
        print("\nPress any key on the image window to close it.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
