from __future__ import annotations
import time

import cv2

from scripts.robot import RobotControls
from scripts.black_line_center_detection import BlackLineCenterDetector
from scripts.pd_regulator import PDRegulator
from scripts.line_recovery import LineRecovery


KP = 1.4
KD = 0.8
PD_MAX_OUTPUT = 224

SPEED_FORWARD_DEFAULT = 200   # Базова швидкість вперед
SPEED_FORWARD_BOOST   = 255   # Швидкість на прямих ділянках
SPEED_TURN_MIN        = 100   # Мінімальний PWM при повороті
SPEED_TURN_MAX        = 220   # Максимальний PWM при повороті

BLACK_THRESHOLD = 70          # Поріг яскравості для чорного (0-255)
ROI_BOX = (0, 120, 320, 240)  # Область аналізу: (x1, y1, x2, y2)

DEADZONE      = 50            # Піксельна зона "прямо" (±px від центру)
LAG_THRESHOLD = 0.05          # Секунди — якщо кадр старший, зупиняємось

STRAIGHT_FRAMES_NEEDED   = 8  # Кадрів підряд з малою похибкою
STRAIGHT_ERROR_THRESHOLD = 20 # Пікселі — що вважається "прямо"

RECOVERY_SOFT_TURN_SPEED = 160  # PWM м'якого пошукового повороту
RECOVERY_SOFT_FRAMES     = 20   # Кадрів у м'якій фазі, потім — крутіше
RECOVERY_HARD_TURN_SPEED = 220  # PWM крутого пошукового повороту


robot = RobotControls(
    default_speed_forward=SPEED_FORWARD_DEFAULT,
    deadzone=DEADZONE,
    lag_threshold=LAG_THRESHOLD,
    led="off",
)
pd_regulator = PDRegulator(kp=KP, kd=KD, max_output=PD_MAX_OUTPUT)
detector = BlackLineCenterDetector(
    black_threshold=BLACK_THRESHOLD, box=ROI_BOX
)
recovery = LineRecovery(
    soft_turn_speed=RECOVERY_SOFT_TURN_SPEED,
    soft_frames=RECOVERY_SOFT_FRAMES,
    hard_turn_speed=RECOVERY_HARD_TURN_SPEED,
)

last_error       = 0
time_last        = time.perf_counter()
straight_counter = 0

while True:
    with robot._frame_lock:
        ret, frame = robot.streamframe
    if not ret:
        time_last = time.perf_counter()
        last_error = 0
        straight_counter = 0
        continue

    center, vis = detector.analyze(frame)

    if time.perf_counter() - robot.last_frame_time > robot.lag_threshold:
        print("LAG!!!!!!!!!!!!!!!!")
        robot.move_stop()
        time_last = time.perf_counter()
        last_error = 0
        straight_counter = 0
        detector.draw_center_line_deadzone(vis, robot.deadzone)
        cv2.imshow("Robot View", vis)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        continue

    if center is None:
        straight_counter = 0
        recovery.update_lost(robot, last_error)
        detector.draw_center_line_deadzone(vis, robot.deadzone)
        cv2.putText(vis, f"RECOVERY: {recovery.state}",
                    (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (0, 80, 255), 1, cv2.LINE_AA)
        cv2.imshow("Robot View", vis)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        continue

    recovery.reset()

    cx, _ = center
    error = detector.center_x - cx

    time_now  = time.perf_counter()
    dtime     = time_now - time_last
    time_last = time_now

    pd_output = pd_regulator.compute(error, last_error, dtime)
    pwm_speed = pd_regulator.output_to_pwm(
        pd_output, pwm_min=SPEED_TURN_MIN, pwm_max=SPEED_TURN_MAX
    )
    last_error = error

    if abs(error) < STRAIGHT_ERROR_THRESHOLD:
        straight_counter += 1
    else:
        straight_counter = 0

    on_straight   = straight_counter >= STRAIGHT_FRAMES_NEEDED
    forward_speed = SPEED_FORWARD_BOOST if on_straight else SPEED_FORWARD_DEFAULT

    if abs(error) < robot.deadzone:
        robot.set_speed(forward_speed)
        robot.move_forward()
    elif pd_output > 0:
        robot.set_speed(pwm_speed)
        robot.move_left()
    else:
        robot.set_speed(pwm_speed)
        robot.move_right()

    detector.draw_center_line_deadzone(vis, robot.deadzone)
    label = "BOOST" if on_straight else f"err={error:+.0f}"
    cv2.putText(vis, label, (5, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.imshow("Robot View", vis)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

robot.close()
cv2.destroyAllWindows()
