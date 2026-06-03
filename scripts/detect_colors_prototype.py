from __future__ import annotations
from pathlib import Path
import numpy as np
import cv2

INPUT_DIR = Path("images/input")
OUTPUT_DIR = Path("images/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png"]

COLORS: dict[str, tuple[np.ndarray, np.ndarray]] = {
    "red": (np.array([0, 210, 210]), np.array([4, 255, 255])),
    "yellow": (np.array([27, 220, 220]), np.array([33, 255, 255])),
    "green": (np.array([68, 180, 100]), np.array([80, 255, 255])),
    "cyan": (np.array([92, 180, 150]), np.array([105, 255, 255])),
    "blue": (np.array([109, 150, 100]), np.array([122, 255, 255])),
    "purple": (np.array([130, 120, 80]), np.array([144, 255, 255])),
    "pink": (np.array([152, 150, 150]), np.array([165, 255, 255])),
}

for filepath in INPUT_DIR.iterdir():
    if filepath.suffix.lower() not in ALLOWED_EXTENSIONS:
        continue

    print(f"Processing: {filepath.name}")
    image = cv2.imread(str(filepath))
    if image is None:
        continue

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    img_h, img_w = image.shape[:2]
    total_area = img_h * img_w
    blue_count = 0
    other_count = 0
    blue_area_sum = 0

    output_img = image.copy()

    for color_name, (lower, upper) in COLORS.items():
        btcol = (0, 0, 0)
        color_mask = cv2.inRange(hsv_image, lower, upper)
        contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 500:
                continue

            if color_name == "blue":
                blue_count += 1
                blue_area_sum += area

                x, y, w, h = cv2.boundingRect(contour)
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
                n = len(approx)
                hull_area = cv2.contourArea(cv2.convexHull(contour))
                solidity = area / hull_area if hull_area > 0 else 0

                cv2.rectangle(output_img, (x, y), (x + w, y + h), btcol, 2)
                text = f"{color_name} [n={n}] S:{solidity:.2f}"
                cv2.putText(output_img, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, btcol, 2)
                cx = x + w // 2
                cy = y + h // 2
                cv2.circle(output_img, (cx, cy), 5, (255, 255, 255), -1)
            else:
                other_count += 1

    blue_percent = (blue_area_sum / total_area) * 100

    overlay = output_img.copy()
    cv2.rectangle(overlay, (0, 0), (220, 110), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, output_img, 0.5, 0, output_img)

    stats = [
        f"Blue objects: {blue_count}",
        f"Other objects: {other_count}",
        f"Blue area: {blue_percent:.2f}%",
    ]
    for i, line in enumerate(stats):
        cv2.putText(output_img, line, (15, 30 + i * 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    output_path = OUTPUT_DIR / filepath.name
    cv2.imwrite(str(output_path), output_img)
    print(f"Saved processed image: {output_path.name}")
