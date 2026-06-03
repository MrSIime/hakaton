from __future__ import annotations

import cv2

from scripts.robot import RobotControls
from scripts.black_line_center_detection import BlackLineCenterDetector


robot = RobotControls(speed=120, led="off")
detector = BlackLineCenterDetector(black_threshold=50, box=(0, 220, 320, 240))

while True:
    ret, frame = robot.streamframe
    if not ret:
        continue

    (cx, cy), vis = detector.analyze(frame)
    if cx == 0 and cy == 0:
        robot.move_stop()
    elif cx < 160:
        turn_speed = (1 - (cx / 160)) * 170
        new_speed = int(turn_speed) + 85
        print(f"cx: {cx}, turn_speed: {turn_speed}, new_speed: {new_speed}")
        robot.set_speed(new_speed)
        robot.move_left()
    elif cx > 160:
        turn_speed = ((cx - 160) / 160) * 170
        new_speed = int(turn_speed) + 85
        print(f"cx: {cx}, turn_speed: {turn_speed}, new_speed: {new_speed}")
        robot.set_speed(new_speed)
        robot.move_right()

    # cv2.imshow("Robot View", frame)
    cv2.imshow("Robot View", vis)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

robot.streamcap_stop()
cv2.destroyAllWindows()
