from __future__ import annotations
import cv2
import numpy as np

LOWER_BLACK = np.array([0, 0, 0])


class BlackLineCenterDetector:
    def __init__(self, box: tuple[int, int, int, int] = (0, 200, 320, 240),
                 black_threshold: int = 50) -> None:
        self.box = box
        self.center_x = (box[2] - box[0]) // 2
        self.black_threshold = black_threshold

    def analyze(self, frame: np.ndarray
                ) -> tuple[tuple[int, int] | None, np.ndarray]:
        x1, y1, x2, y2 = self.box
        roi = frame[y1:y2, x1:x2]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        hsv_blurred = cv2.GaussianBlur(hsv, (15, 15), 0)
        mask = cv2.inRange(
            hsv_blurred, LOWER_BLACK,
            np.array([180, 255, self.black_threshold])
        )
        vis = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        M = cv2.moments(mask)
        if M["m00"] == 0:
            return None, vis
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        cv2.circle(vis, (cx, cy), 5, (0, 0, 255), -1)
        return (cx, cy), vis
