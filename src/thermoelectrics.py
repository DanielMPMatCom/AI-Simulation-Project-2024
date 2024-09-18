from part import *
from people import *
from circuits import *


class Thermoelectric:
    def __init__(self, parts: list[Part], circuits: list[Circuit], offer: int) -> None:
        self.parts = parts
        self.circuits = circuits
        self._offer = offer

    def update(self):
        for part in self.parts:
            part.update()
        
        for circuits in self.circuits:
            circuits.update()

    def is_working(self):
        pass

    def get_current_offer(self):
        pass
