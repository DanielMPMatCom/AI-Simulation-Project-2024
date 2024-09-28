from src.people import Citizen
from utils.gaussianmixture import *
import random

class Circuit:
    """
    Represents an electricity circuit consisting of multiple blocks.
    """

    def __init__(self, id, gaussian_mixture, blocks_range = (4, 8), citizens_range = (100, 200)) -> None:
        self.id = id
        self.blocks_range = blocks_range
        self.citizens_range = citizens_range
        self.gaussian_mixture = gaussian_mixture
        self.blocks: list[Block] = self.create_bolcks()
        self.mock_electric_consume = self.generate_mock_consume()

    def update(self):
        for block in self.blocks:
            block.update()

    def create_bolcks(self):
        blocks = []
        amount_of_blocks = random.randint(self.blocks_range[0], self.blocks_range[1])
        for i in range(amount_of_blocks):
            blocks.append(Block(self.gaussian_mixture, self.citizens_range))
        
        return blocks
    
    def generate_mock_consume(self):
        mock_value = 0
        for block in self.blocks:
            mock_value += block.mock_electric_consume

        return mock_value



class Block:
    """
    Represents a block within a circuit that consumes energy.
    """

    def __init__(self, gaussian_mixture : DailyElectricityConsumptionBimodal, citizens_range) -> None:
        self.citizens: list[Citizen] = []
        self.history_report: list[str] = []
        self.off_hours: tuple[int, int] = (0, 0)
        self.demand_per_hour: list[float] = []
        self.gaussian_mixture = gaussian_mixture
        self.mock_electric_consume = self.get_mock_electric_consume()

    def update(self):
        pass

    def get_block_report(self):
        for citizen in self.citizens:
            citizen.generate_report(self.off_hours)

    def get_consumed_energy_today(self) -> float:
        return sum(self.demand_per_hour[: self.off_hours[0]]) + sum(
            self.demand_per_hour[self.off_hours[1] :]
        )
    
    def get_mock_electric_consume(self) -> float:
        mock_value = 0
        for i in range(300):
            day_consume = sum(self.gaussian_mixture.generate())
            mock_value = max(mock_value, day_consume)
