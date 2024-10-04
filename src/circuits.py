from itertools import groupby
from src.people import Citizen
from src.worldstate import WorldState
from utils.gaussianmixture import *
import random


class Circuit:
    """
    Represents an electricity circuit consisting of multiple blocks.
    """

    def __init__(
        self,
        id,
        gaussian_mixture,
        blocks_range,
        citizens_range,
        industrialization,
    ) -> None:

        # General Params
        self.id = id
        self.gaussian_mixture = gaussian_mixture
        self.blocks_range = blocks_range
        self.citizens_range = citizens_range

        self.blocks: list[Block] = self.create_blocks()
        self.circuit_satisfaction = self.set_circuit_satisfaction()

        # General Data
        self.industrialization = industrialization

    def get_all_block_population(self):
        return sum([block.citizens for block in self.blocks])

    def update(self):
        for block in self.blocks:
            block.update()

    def create_blocks(self):
        blocks = []
        amount_of_blocks = random.randint(self.blocks_range[0], self.blocks_range[1])
        for _ in range(amount_of_blocks):
            blocks.append(
                Block(
                    self.gaussian_mixture, self.citizens_range, self.industrialization
                )
            )
        return blocks

    def set_circuit_satisfaction(self):
        total_people: float = 0
        total_satisfaction: float = 0
        for block in self.blocks:
            total_satisfaction += block.citizens.amount + block.get_block_opinion()
            total_people += block.citizens.amount
        return total_satisfaction / total_people


class BlockReport:
    def __init__(
        self,
        time_off: int,
        total_demand: float,
        citizens_opinion_state: float,
    ):
        self.time_off = time_off
        self.total_demand = total_demand
        self.citizens_opinion = citizens_opinion_state


class Block:
    """
    Represents a block within a circuit that consumes energy.
    """

    def __init__(
        self,
        gaussian_mixture: DailyElectricityConsumptionBimodal,
        citizens_range,
        industrialization,
        memory_of_history_report,
    ) -> None:
        self.citizens: Citizen = Citizen(
            self, random.randint(citizens_range[0], citizens_range[1])
        )
        self.history_report: list[BlockReport] = []
        self.off_hours: tuple[int, int] = (0, 0)
        self.demand_per_hour: list[float] = []
        self.gaussian_mixture = gaussian_mixture
        self.industrialization = industrialization
        self.memory_of_history_report = memory_of_history_report

    def update(self, off_hours, world_state: WorldState):

        self.off_hours = off_hours
        self.demand_per_hour = self.gaussian_mixture.generate()

        time_off = off_hours[1] - off_hours[0]
        total_demand = self.get_consumed_energy_today()

        history_report = self.history_report[: self.memory_of_history_report : -1]

        days_off: float = sum(1 for report in history_report if report.time_off > 0) + (
            1 if time_off > 0 else 0
        )

        days_amount: float = len(history_report) + 1

        near_days_off = [  # preguntar a toledo si aqui es la intecion desde  el inicio
            i for i, report in enumerate(history_report, 1) if report.time_off > 0
        ]

        last_day_off = 20 if not near_days_off else min(near_days_off)

        if time_off > 0:
            last_day_off = 0

        self.citizens.set_opinion(
            input_general_satisfaction=world_state.general_satisfaction,
            input_industrialization=self.industrialization,
            input_days_off_relation=days_off / days_amount,
            input_last_day_off=last_day_off,
        )

        daily_report = BlockReport(
            time_off=time_off,
            total_demand=total_demand,
            citizens_opinion_state=self.citizens.opinion,
        )
        self.history_report.append(daily_report)

    def get_block_opinion(self) -> float:
        return self.citizens.opinion

    def get_consumed_energy_today(self) -> float:
        return sum(self.demand_per_hour[: self.off_hours[0]]) + sum(
            self.demand_per_hour[self.off_hours[1] :]
        )

    def last_days_off(self):  # preguntar a toledo si esto esta bien
        return sum(1 for report in self.history_report if report.time_off > 0)

    def longest_sequence_of_days_off(self):
        return max(
            sum(1 for _ in group)
            for _, group in groupby(
                self.history_report, key=lambda report: report.time_off > 0
            )
        )
