from __future__ import annotations
import cv2
import numpy as np


class BlackFillDetector:
    def __init__(
        self,
        box1: tuple[int, int, int, int] = (0, 60, 80, 180),
        box2: tuple[int, int, int, int] = (240, 60, 320, 180),
        black_threshold: int = 50,
    ) -> None:
        self.black_threshold = black_threshold
        self.box1 = box1
        self.box2 = box2

    def analyze(self, frame: np.ndarray) -> tuple[float, float]:
        box1_fill = self._black_percent(frame, self.box1)
        box2_fill = self._black_percent(frame, self.box2)
        return box1_fill, box2_fill

    def visualize(self, frame: np.ndarray) -> np.ndarray:
        box1_fill, box2_fill = self.analyze(frame)
        vis = frame.copy()

        self._draw_box(vis, self.box1, box1_fill, label="L")
        self._draw_box(vis, self.box2, box2_fill, label="R")

        return vis

    def _black_percent(
            self, frame: np.ndarray, box: tuple[int, int, int, int]
            ) -> float:
        x1, y1, x2, y2 = box
        roi = frame[y1:y2, x1:x2]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        black_mask = cv2.inRange(
            hsv,
            np.array([0, 0, 0]),
            np.array([180, 255, self.black_threshold]),
        )
        total_pixels = (y2 - y1) * (x2 - x1)
        if total_pixels == 0:
            return 0.0
        return float(np.count_nonzero(black_mask)) / total_pixels * 100.0

    @staticmethod
    def _draw_box(
        img: np.ndarray,
        box: tuple[int, int, int, int],
        fill_pct: float,
        label: str,
    ) -> None:
        x1, y1, x2, y2 = box
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 255), 2)
        cv2.putText(img, f"{label}: {fill_pct:.1f}%", (x1 + 4, y1 + 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1,
                    cv2.LINE_AA)
