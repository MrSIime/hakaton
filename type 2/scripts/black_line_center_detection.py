from __future__ import annotations
import cv2
import numpy as np

LOWER_BLACK = np.array([0, 0, 0])
UPPER_BLACK = np.array([180, 80, 70])


class BlackLineCenterDetector:
    def __init__(self, box: tuple[int, int, int, int] = (0, 200, 320, 240),
                 black_threshold: int = 70) -> None:
        self.box = box
        self.center_x = (box[2] - box[0]) // 2
        self.black_threshold = black_threshold

    def draw_center_line_deadzone(self, frame: np.ndarray,
                                  deadzone: int) -> None:
        x1, y1, x2, y2 = self.box
        h, w = frame.shape[:2]
        cx = self.center_x
        cv2.line(frame, (cx, 0), (cx, h), (0, 255, 0), 2)
        cv2.line(frame, (cx - deadzone, 0), (cx - deadzone, h), (0, 0, 255), 2)
        cv2.line(frame, (cx + deadzone, 0), (cx + deadzone, h), (0, 0, 255), 2)

    def analyze(self, frame: np.ndarray
                ) -> tuple[tuple[int, int] | None, np.ndarray]:
        x1, y1, x2, y2 = self.box
        roi = frame[y1:y2, x1:x2]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        hsv_blurred = cv2.GaussianBlur(hsv, (15, 15), 0)
        upper = np.array([180, 80, self.black_threshold])
        mask = cv2.inRange(hsv_blurred, LOWER_BLACK, upper)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        vis = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        contours, _ = cv2.findContours(mask,
                                       cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None, vis

        largest = max(contours, key=cv2.contourArea)

        line_mask = np.zeros_like(mask)
        cv2.drawContours(line_mask, [largest], -1, 255, thickness=cv2.FILLED)
        M = cv2.moments(line_mask)
        if M["m00"] == 0:
            return None, vis
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        cv2.circle(vis, (cx, cy), 5, (0, 0, 255), -1)
        return (cx, cy), vis
