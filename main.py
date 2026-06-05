from __future__ import annotations
import time

import cv2

from scripts.robot import RobotControls
from scripts.black_line_center_detection import BlackLineCenterDetector
from scripts.pd_regulator import PDRegulator

robot = RobotControls(default_speed_forward=120, default_speed_backward=100,
                      deadzone=25, lag_threshold=0.05, led="off")
pd_regulator = PDRegulator(kp=1.0, kd=0.16, max_output=170)
detector = BlackLineCenterDetector(
    black_threshold=50, box=(0, 200, 320, 240)
)

last_error = 0
time_last = time.perf_counter()

while True:
    with robot._frame_lock:
        ret, frame = robot.streamframe
    if not ret:
        time_last = time.perf_counter()
        last_error = 0
        continue

    center, vis = detector.analyze(frame)

    if center is None:
        print("No line detected")
        robot.set_speed(robot.default_speed_backward)
        robot.move_backward()
        cv2.imshow("Robot View", vis)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        continue

    if time.perf_counter() - robot.last_frame_time > robot.lag_threshold:
        print("LAG!!!!!!!!!!!!!!!!")
        robot.move_stop()
        time_last = time.perf_counter()
        last_error = 0
        cv2.imshow("Robot View", vis)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        continue

    cx, _ = center
    error = detector.center_x - cx

    time_now = time.perf_counter()
    dtime = time_now - time_last
    time_last = time_now

    pd_output = pd_regulator.compute(error, last_error, dtime)
    pwm_speed = pd_regulator.output_to_pwm(pd_output, pwm_min=85, pwm_max=255)

    last_error = error

    if abs(error) < robot.deadzone:
        robot.set_speed(robot.default_speed_forward)
        robot.move_forward()
    elif pd_output > 0:
        robot.set_speed(pwm_speed)
        robot.move_left()
        robot.last_move = "left"
    elif pd_output < 0:
        robot.set_speed(pwm_speed)
        robot.move_right()
        robot.last_move = "right"

    cv2.imshow("Robot View", vis)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

robot.streamcap_stop()
cv2.destroyAllWindows()
