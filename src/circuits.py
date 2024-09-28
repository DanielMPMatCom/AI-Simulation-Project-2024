from src.people import Citizen
from utils.gaussianmixture import *


class Circuit:
    """
    Represents an electricity circuit consisting of multiple blocks.
    """

    def __init__(self, id) -> None:
        self.id = id
        self.mock_electric_consume = 200 # Modify this value is important
        self.blocks: list[Block] = []

    def update(self):
        for block in self.blocks:
            block.update()


class Block:
    """
    Represents a block within a circuit that consumes energy.
    """

    def __init__(self, gaussianmixture : DailyElectricityConsumptionBimodal) -> None:
        self.citizens: list[Citizen] = []
        self.history_report: list[str] = []
        self.off_hours: tuple[int, int] = (0, 0)
        self.demand_per_hour: list[float] = []
        self.gaussianmixture = gaussianmixture

    def update(self):
        pass

    def get_block_report(self):
        for citizen in self.citizens:
            citizen.generate_report(self.off_hours)

    def get_consumed_energy_today(self) -> float:
        return sum(self.demand_per_hour[: self.off_hours[0]]) + sum(
            self.demand_per_hour[self.off_hours[1] :]
        )
