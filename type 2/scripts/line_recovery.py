from __future__ import annotations

# ──────────────────────────────────────────────
#  LineRecovery — модуль розумного відновлення
#  після втрати чорної лінії
# ──────────────────────────────────────────────
#
#  Стани (state):
#    "idle"  — лінія є, нічого не робимо
#    "soft"  — м'який поворот вперед у напрямку
#              останньої відомої похибки
#    "hard"  — крутий поворот вперед у тому ж напрямку
#              (і залишається в цьому стані нескінченно)


class LineRecovery:
    def __init__(
        self,
        soft_turn_speed: int = 160,
        soft_frames: int = 20,
        hard_turn_speed: int = 220,
    ) -> None:
        self.soft_turn_speed = soft_turn_speed
        self.soft_frames     = soft_frames
        self.hard_turn_speed = hard_turn_speed

        self.state: str = "idle"
        self._frames_in_state: int = 0
        # -1 = повернути праворуч, +1 = ліворуч, 0 = невідомо
        self._lost_direction: int = 0

    def reset(self) -> None:
        """Викликати коли лінія знову знайдена."""
        self.state = "idle"
        self._frames_in_state = 0

    def update_lost(self, robot, last_error: float) -> None:
        """
        Викликати кожен кадр, коли лінія НЕ знайдена.
        last_error — похибка з попереднього кадру
                     (+ = лінія лівіше центру, треба повернути ліворуч).
        """
        if self.state == "idle":
            self._lost_direction = 1 if last_error >= 0 else -1
            self.state = "soft"
            self._frames_in_state = 0

        self._frames_in_state += 1

        if self.state == "soft" and self._frames_in_state > self.soft_frames:
            self.state = "hard"
            self._frames_in_state = 0

        if self.state == "soft":
            robot.set_speed(self.soft_turn_speed)
        else:  # "hard" — залишається назавжди поки не знайде лінію
            robot.set_speed(self.hard_turn_speed)

        if self._lost_direction >= 0:
            robot.move_left()
        else:
            robot.move_right()
