from part import *
from people import *
from circuits import *


class Thermoelectric:
    def __init__(self, parts: list[Part], circuits: list[Circuit], offer: int) -> None:
        self.parts = parts
        self._offer = offer

    def update(self):
        for part in self.parts:
            part.update()

    def is_working(self):
        pass

    def get_current_offer(self):
        pass
