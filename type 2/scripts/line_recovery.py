from __future__ import annotations

# ──────────────────────────────────────────────
#  LineRecovery — модуль розумного відновлення
#  після втрати чорної лінії
# ──────────────────────────────────────────────
#
#  Стани:
#    "idle"  — лінія є
#    "soft"  — м'який пошук: більше forward, менше turn
#    "hard"  — крутий пошук: більше turn, менше forward
#
#  Оскільки робот має лише команди forward/left/right (танк),
#  для імітації дуги чергуємо forward і turn імпульсами.
#
#  КАЛІБРУВАННЯ:
#    SOFT_FORWARD_FRAMES  — скільки кадрів forward у soft-фазі
#    SOFT_TURN_FRAMES     — скільки кадрів turn   у soft-фазі
#    HARD_FORWARD_FRAMES  — скільки кадрів forward у hard-фазі
#    HARD_TURN_FRAMES     — скільки кадрів turn   у hard-фазі
#
#  Приклад (soft): forward 4 кадри → turn 2 кадри → forward 4 → ...
#  Приклад (hard): forward 1 кадр  → turn 4 кадри → forward 1 → ...


# --- Константи імпульсів (можна змінювати) ---
SOFT_FORWARD_FRAMES = 4   # кадрів вперед у м'якій фазі
SOFT_TURN_FRAMES    = 2   # кадрів повороту у м'якій фазі

HARD_FORWARD_FRAMES = 1   # кадрів вперед у крутій фазі
HARD_TURN_FRAMES    = 4   # кадрів повороту у крутій фазі


class LineRecovery:
    def __init__(
        self,
        soft_turn_speed: int = 160,
        soft_forward_speed: int = 160,
        soft_frames: int = 20,
        hard_turn_speed: int = 220,
        hard_forward_speed: int = 180,
    ) -> None:
        self.soft_turn_speed    = soft_turn_speed
        self.soft_forward_speed = soft_forward_speed
        self.soft_frames        = soft_frames
        self.hard_turn_speed    = hard_turn_speed
        self.hard_forward_speed = hard_forward_speed

        self.state: str = "idle"
        self._frames_in_state: int = 0
        self._pulse_counter: int = 0   # лічильник всередині одного імпульсу
        self._lost_direction: int = 0  # +1 = ліво, -1 = право

    def reset(self) -> None:
        self.state = "idle"
        self._frames_in_state = 0
        self._pulse_counter = 0

    def update_lost(self, robot, last_error: float) -> None:
        if self.state == "idle":
            self._lost_direction = 1 if last_error >= 0 else -1
            self.state = "soft"
            self._frames_in_state = 0
            self._pulse_counter = 0

        self._frames_in_state += 1
        self._pulse_counter += 1

        if self.state == "soft" and self._frames_in_state > self.soft_frames:
            self.state = "hard"
            self._frames_in_state = 0
            self._pulse_counter = 0

        if self.state == "soft":
            fwd_frames  = SOFT_FORWARD_FRAMES
            turn_frames = SOFT_TURN_FRAMES
            fwd_speed   = self.soft_forward_speed
            turn_speed  = self.soft_turn_speed
        else:  # hard
            fwd_frames  = SOFT_FORWARD_FRAMES
            turn_frames = SOFT_TURN_FRAMES
            fwd_speed   = self.hard_forward_speed
            turn_speed  = self.hard_turn_speed

        cycle = fwd_frames + turn_frames
        phase = self._pulse_counter % cycle

        if phase < fwd_frames:
            robot.set_speed(fwd_speed)
            robot.move_forward()
        else:
            robot.set_speed(turn_speed)
            if self._lost_direction >= 0:
                robot.move_left()
            else:
                robot.move_right()
