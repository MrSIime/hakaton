from __future__ import annotations


class PDRegulator:
    def __init__(self, kp: float,
                 kd: float,
                 max_output: int) -> None:
        self.kp = kp
        self.kd = kd
        self.max_output = max_output

    def compute(self, error: float,
                last_error: float,
                dtime: float) -> float:
        p_term = self.kp * error

        d_term = self.kd * (error - last_error) / dtime if dtime != 0 else 0.0

        return p_term + d_term

    def output_to_pwm(self, pd_output: float,
                      pwm_min: int = 85,
                      pwm_max: int = 255) -> int:
        magnitude = min(abs(pd_output), self.max_output)
        return int(pwm_min
                   + (magnitude / self.max_output)
                   * (pwm_max - pwm_min))
