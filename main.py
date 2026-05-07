from __future__ import annotations
from pathlib import Path
import numpy as np
import cv2

INPUT_DIR = Path("images/input")
OUTPUT_DIR = Path("images/output")
ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png"]

COLORS: dict[str, tuple[np.ndarray, np.ndarray, tuple[int, int, int]]] = {
    "red": (np.array([0, 210, 210]), np.array([4, 255, 255]), (0, 0, 254)),
    "yellow": (np.array([27, 220, 220]), np.array([33, 255, 255]), (1, 255, 255)),
    "green": (np.array([68, 180, 100]), np.array([80, 255, 255]), (80, 175, 0)),
    "cyan": (np.array([92, 180, 150]), np.array([105, 255, 255]), (240, 174, 3)),
    "blue": (np.array([109, 150, 100]), np.array([122, 255, 255]), (238, 66, 36)),
    "purple": (np.array([130, 120, 80]), np.array([144, 255, 255]), (160, 48, 112)),
    "pink": (np.array([152, 150, 150]), np.array([165, 255, 255]), (180, 38, 239)),
}

for filepath in INPUT_DIR.iterdir():
    if filepath.suffix.lower() not in ALLOWED_EXTENSIONS:
        continue

    print(f"Processing: {filepath.name}")
    image = cv2.imread(str(filepath))
    if image is None:
        continue

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    for color_name, (lower, upper, btcol) in COLORS.items():
        color_mask = cv2.inRange(hsv_image, lower, upper)
        contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) < 500:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
            n = len(approx)

            hull_area = cv2.contourArea(cv2.convexHull(contour))
            solidity = cv2.contourArea(contour) / hull_area if hull_area > 0 else 0

            cv2.rectangle(image, (x, y), (x + w, y + h), btcol, 2)
            cv2.circle(image, (x, y), 5, (255, 255, 255), -1)

            text = f"{color_name} [n={n}] S:{solidity:.2f}"
            cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, btcol, 2)

    output_path = OUTPUT_DIR / filepath.name
    cv2.imwrite(str(output_path), image)
    print(f"Saved processed image: {output_path.name}")