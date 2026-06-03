from __future__ import annotations
import threading

from websocket import create_connection
import cv2


class RobotControls:
    def __init__(self, wsip: str = "ws://10.1.66.69/ws",
                 streamcapip: str = "http://10.1.66.69:81/stream",
                 speed: int = 170, led: str = "off") -> None:
        self.speed = speed
        self.led = led
        self.ws = create_connection(wsip)
        self.streamcapip = streamcapip
        self.set_led(led)
        self.set_speed(speed)
        self.streamcap_start()

    def streamcap_loop(self) -> None:
        self.streamcap = cv2.VideoCapture(self.streamcapip)
        while not self._stop_event.is_set():
            self.streamframe = self.streamcap.read()
        self.streamcap.release()

    def streamcap_start(self) -> None:
        self._stop_event = threading.Event()
        self.streamframe = (False, None)
        self.thread = threading.Thread(target=self.streamcap_loop, daemon=True)
        self.thread.start()

    def streamcap_stop(self) -> None:
        self._stop_event.set()
        self.thread.join()

    def set_speed(self, speed: int) -> None:
        self.speed = speed
        self.ws.send(f"speed:{self.speed}")

    def set_led(self, led: str) -> None:
        self.led = led
        self.ws.send(f"led:{self.led}")

    def move_forward(self) -> None:
        self.ws.send("forward")

    def move_backward(self) -> None:
        self.ws.send("backward")

    def move_stop(self) -> None:
        self.ws.send("stop")

    def move_right(self) -> None:
        self.ws.send("right")

    def move_left(self) -> None:
        self.ws.send("left")
