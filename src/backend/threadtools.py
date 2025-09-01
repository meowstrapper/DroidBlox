from kivy.clock import Clock
from kivy.logger import Logger

from typing import Any, Callable

TAG = "DBThreadTools" + ": "

__all__ = ["scheduleInClock"]

def scheduleInClock(func: Callable[[Any], None]):
    Logger.debug(TAG + f"Scheduling function {func.__name__} to clock")
    def wrapper(*args, **kwargs):
        Clock.schedule_once(lambda delta: func(*args, **kwargs), 0)
    return wrapper

