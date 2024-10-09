from src.citizen import Citizen
from src.simulation_constants import DAYS_OF_MEMORY, K_PREDICT_CONSUMPTION_ITER
from src.utils.gaussianmixture import DailyElectricityConsumptionBimodal
from itertools import groupby
from src.simulation_constants import RANDOM


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
        self.industrialization = industrialization

        self.blocks: list["Block"] = self.create_blocks()
        self.circuit_satisfaction = self.set_circuit_satisfaction()
        self.mock_electric_consume = self.get_mock_electric_consume()

        # General Data
        self.industrialization = industrialization
        self.importance = 0

    def get_all_block_population(self):
        return sum([block.citizens.amount for block in self.blocks])

    def update(self):
        for block in self.blocks:
            block.update()
        self.set_circuit_satisfaction()

    def create_blocks(self):
        blocks = []
        amount_of_blocks = RANDOM.integers(self.blocks_range[0], self.blocks_range[1])
        for _ in range(amount_of_blocks):
            blocks.append(
                Block(
                    self.gaussian_mixture, self.citizens_range, self.industrialization
                )
            )
        return blocks

    def get_mock_electric_consume(self):
        mock_value = 0
        for block in self.blocks:
            mock_value += block.mock_electric_consume

        return mock_value

    def set_circuit_satisfaction(self):
        total_people: float = 0
        total_satisfaction: float = 0
        for block in self.blocks:
            total_satisfaction += (
                block.citizens.amount * block.get_block_opinion()
            )  # TODO: Review this sum, changed: mean
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
        gaussian_mixture: "DailyElectricityConsumptionBimodal",
        citizens_range,
        industrialization,
    ) -> None:
        self.citizens: "Citizen" = Citizen(
            RANDOM.integers(citizens_range[0], citizens_range[1])
        )
        self.history_report: list["BlockReport"] = []
        self.off_hours: list[bool] = [False] * 24

        self.gaussian_mixture = gaussian_mixture
        self.industrialization = industrialization

        self.demand_per_hour: list[float] = []
        self.predicted_demand_per_hour: list[float] = self.predict_demand_per_hour()
        self.importance = 0
        self.mock_electric_consume = self.get_mock_electric_consume()

    def predict_demand_per_hour(self):
        predicted_demand_per_hour = self.gaussian_mixture.generate()

        for _ in range(K_PREDICT_CONSUMPTION_ITER - 1):
            new_prediction = self.gaussian_mixture.generate()
            predicted_demand_per_hour = [
                max(predicted_demand_per_hour[i], new_prediction[i])
                for i in range(len(new_prediction))
            ]

        return predicted_demand_per_hour

    def update(self, general_satisfaction: float):

        self.demand_per_hour = self.gaussian_mixture.generate()

        time_off = sum(self.off_hours)
        total_demand = self.get_consumed_energy_today()

        history_report = self.history_report[:DAYS_OF_MEMORY:-1]

        days_off: float = sum(1 for report in history_report if report.time_off > 0) + (
            1 if time_off > 0 else 0
        )

        days_amount: float = len(history_report) + 1

        near_days_off = [
            i for i, report in enumerate(history_report, 1) if report.time_off > 0
        ]

        last_day_off = 20 if not near_days_off else min(near_days_off)

        if time_off > 0:
            last_day_off = 0

        self.citizens.set_opinion(
            input_general_satisfaction=general_satisfaction,
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
        return self.citizens.opinion if self.citizens.opinion is not None else 0.8

    def get_consumed_energy_today(self) -> float:
        return sum(self.demand_per_hour[: self.off_hours[0]]) + sum(
            self.demand_per_hour[self.off_hours[1] :]
        )

    def last_days_off(self):
        return sum(1 for report in self.history_report if report.time_off > 0)

    def longest_sequence_of_days_off(self):
        return max(
            sum(1 for _ in group)
            for _, group in groupby(
                self.history_report, key=lambda report: report.time_off > 0
            )
        )

    def set_days_distribution(self, off_hours: list[bool]):
        if len(off_hours) != 24:
            raise RuntimeError(
                f"Off hours must be and array of length 24, and {off_hours} was given"
            )

        self.off_hours = off_hours

    def get_mock_electric_consume(self) -> float:
        return sum(self.predicted_demand_per_hour)
