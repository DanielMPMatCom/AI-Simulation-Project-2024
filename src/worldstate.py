from circuits import *
from part import *
from people import *
from thermoelectrics import *
from map import *


class WorldState:
    def __init__(self, energy_demand) -> None:
        self.energy_demand = energy_demand