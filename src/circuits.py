from src.citizen import Citizen
from src.simulation_constants import (
    DAYS_OF_MEMORY,
    K_PREDICT_CONSUMPTION_ITER,
    DEMAND_INDUSTRIALIZATION,
    DEMAND_PER_PERSON,
    VARIABILITY_DEMAND_PER_INDUSTRIALIZATION,
    VARIABILITY_DEMAND_PER_PERSON,
    PEAK_CONSUMPTION_EVENING,
    PEAK_CONSUMPTION_MORNING,
    MAX_DEVIATION_MORNING,
    MAX_DEVIATION_EVENING,
    WEIGHT_EVENING,
    WEIGHT_MORNING,
    MIN_CITIZEN,
    MAX_CITIZEN,
    MAX_DEVIATION_CITIZEN_IN_BLOCK,
    MIN_BLOCKS_PER_CIRCUIT,
    MAX_BLOCKS_PER_CIRCUIT,
)
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
    ) -> None:

        # General Params
        self.id = id

        self.blocks_range = (MIN_BLOCKS_PER_CIRCUIT, MAX_BLOCKS_PER_CIRCUIT)

        citizen_count = RANDOM.integers(MIN_CITIZEN, MAX_CITIZEN)
        self.citizens_range = (
            max(citizen_count - MAX_DEVIATION_CITIZEN_IN_BLOCK, 0),
            min(citizen_count + MAX_DEVIATION_CITIZEN_IN_BLOCK, MAX_CITIZEN),
        )

        self.industrialization = (
            RANDOM.integers(1, DEMAND_INDUSTRIALIZATION) / DEMAND_INDUSTRIALIZATION
        )

        self.blocks: list["Block"] = self.create_blocks()
        self.circuit_satisfaction = self.set_circuit_satisfaction()
        self.mock_electric_consume = self.get_mock_electric_consume()

        self.importance = 0

    def get_all_block_population(self):
        """
        Returns the total population of all blocks within the circuit.
        """
        return sum([block.citizens.amount for block in self.blocks])

    def update(self, general_satisfaction: float, opinion_day: bool):
        """
        Updates the state of each block within the circuit based on general satisfaction and whether it is an opinion day.

        Args:
            general_satisfaction (float): The general satisfaction level to be used for updating blocks.
            opinion_day (bool): A flag indicating if it is an opinion day, affecting how citizens' opinions are updated.
        """
        for block in self.blocks:
            block.update(
                general_satisfaction=general_satisfaction, opinion_day=opinion_day
            )
        self.set_circuit_satisfaction()

    def create_blocks(self):
        """
        Creates and returns a list of Block objects for the circuit.

        The number of blocks is determined randomly within the range specified by self.blocks_range.
        Each block is initialized with a range of citizens and an industrialization level.

        Returns:
            list[Block]: A list of Block objects.
        """
        blocks = []
        amount_of_blocks = RANDOM.integers(self.blocks_range[0], self.blocks_range[1])
        for _ in range(amount_of_blocks):
            blocks.append(Block(self.citizens_range, self.industrialization))
        return blocks

    def get_mock_electric_consume(self):
        """
        Calculates the mock electricity consumption for the circuit.

        This method iterates over all blocks in the circuit and sums up their mock electricity consumption.

        Returns:
            float: The total mock electricity consumption for the circuit.
        """

        mock_value = 0
        for block in self.blocks:
            mock_value += block.mock_electric_consume

        return mock_value

    def set_circuit_satisfaction(self):
        """
        Calculates and sets the overall satisfaction for the circuit.

        This method iterates over all blocks in the circuit, summing up the satisfaction
        levels of all citizens weighted by their amount. The overall satisfaction is
        then calculated as the average satisfaction across all citizens.

        Returns:
            float: The overall satisfaction level of the circuit.
        """

        total_people: float = 0
        total_satisfaction: float = 0
        for block in self.blocks:
            total_satisfaction += block.citizens.amount * block.get_block_opinion()
            total_people += block.citizens.amount
        return total_satisfaction / total_people


class BlockReport:
    """
    Represents a report for a block within a circuit.
    """

    def __init__(
        self,
        time_off: int,
        total_consumed: float,
        total_demand: float,
        citizens_opinion_state: float,
    ):
        self.time_off = time_off
        self.total_consumed = total_consumed
        self.total_demand = total_demand
        self.citizens_opinion = citizens_opinion_state


class Block:
    """
    Represents a block within a circuit that consumes energy.
    """

    def __init__(
        self,
        citizens_range,
        industrialization,
    ) -> None:
        self.citizens: "Citizen" = Citizen(
            RANDOM.integers(citizens_range[0], citizens_range[1])
        )
        self.history_report: list["BlockReport"] = []
        self.off_hours: list[bool] = [False] * 24

        self.industrialization = industrialization
        self.last_day_off = 20

        self.gaussian_mixture = DailyElectricityConsumptionBimodal(
            base_consumption=DEMAND_PER_PERSON * self.citizens.amount
            + DEMAND_INDUSTRIALIZATION * industrialization,
            base_variability=VARIABILITY_DEMAND_PER_PERSON * self.citizens.amount
            + VARIABILITY_DEMAND_PER_INDUSTRIALIZATION * industrialization,
            mean_morning=PEAK_CONSUMPTION_MORNING,
            mean_evening=PEAK_CONSUMPTION_EVENING,
            std_morning=RANDOM.uniform(1.0, MAX_DEVIATION_MORNING),
            std_evening=RANDOM.uniform(1.0, MAX_DEVIATION_EVENING),
            weight_morning=WEIGHT_MORNING,
            weight_evening=WEIGHT_EVENING,
        )

        self.demand_per_hour: list[float] = self.gaussian_mixture.generate()

        self.predicted_demand_per_hour: list[float] = self.predict_demand_per_hour()
        self.predicted_total_demand = sum(self.predicted_demand_per_hour)
        self.importance = 0
        self.mock_electric_consume = self.get_mock_electric_consume()

    def predict_demand_per_hour(self):
        """
        Predicts the electricity demand per hour for the block.

        This method generates multiple predictions of hourly demand using a Gaussian mixture model
        and selects the maximum value for each hour across all predictions.

        Returns:
            list[float]: A list of predicted electricity demand values for each hour.
        """

        predicted_demand_per_hour = self.gaussian_mixture.generate()

        for _ in range(K_PREDICT_CONSUMPTION_ITER - 1):
            new_prediction = self.gaussian_mixture.generate()
            predicted_demand_per_hour = [
                max(predicted_demand_per_hour[i], new_prediction[i])
                for i in range(len(new_prediction))
            ]

        return predicted_demand_per_hour

    def update(self, general_satisfaction: float, opinion_day: bool):
        """
        Updates the block's state based on general satisfaction and whether it is an opinion day.

        This method regenerates the block's hourly demand, updates the citizens' opinions if it is an opinion day,
        and appends a daily report to the block's history.

        Args:
            general_satisfaction (float): The general satisfaction level to be used for updating the block.
            opinion_day (bool): A flag indicating if it is an opinion day, affecting how citizens' opinions are updated.
        """

        total_demand = sum(self.demand_per_hour)
        self.demand_per_hour = self.gaussian_mixture.generate()

        time_off = sum(self.off_hours)
        total_consumed = self.get_consumed_energy_today()

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

        self.last_day_off = last_day_off

        if opinion_day:
            self.citizens.set_opinion(
                input_general_satisfaction=general_satisfaction,
                input_industrialization=self.industrialization,
                input_days_off_relation=days_off / days_amount,
                input_last_day_off=last_day_off,
            )

        daily_report = BlockReport(
            time_off=time_off,
            total_consumed=total_consumed,
            total_demand=total_demand,
            citizens_opinion_state=self.citizens.opinion,
        )
        self.history_report.append(daily_report)

    def get_block_opinion(self) -> float:
        """
        Returns the opinion of the citizens in the block.

        If the citizens' opinion is not set, a default value of 0.8 is returned.
        """
        return self.citizens.opinion if self.citizens.opinion is not None else 0.8

    def get_consumed_energy_today(self) -> float:
        """
        Calculates the total energy consumed by the block today.

        This method sums up the hourly demand for each hour that is not marked as an off hour.
        """
        # real energy consumed in the day
        return sum(
            [
                demand
                for hour, demand in enumerate(self.demand_per_hour)
                if not self.off_hours[hour]
            ]
        )

    def get_predicted_consume_for_today(self) -> float:
        """
        Returns the predicted total electricity consumption for the block for today.

        This method sums up the predicted hourly demand values to get the total predicted consumption.
        """
        return self.predicted_total_demand

    def last_days_off(self):
        """
        Returns the number of days since the last day off.

        This method calculates the number of days that have passed since the last day
        the block had any off hours.
        """

        return self.last_day_off

    def longest_sequence_of_days_off(self):
        return max(
            (
                sum(1 for _ in group)
                for _, group in groupby(
                    self.history_report, key=lambda report: report.time_off > 0
                )
            ),
            default=0,
        )

    def set_days_distribution(self, off_hours: list[bool]):
        """
        Returns the longest sequence of consecutive days off.

        This method iterates through the block's history report and identifies the longest
        sequence of consecutive days where the block had any off hours.
        """
        if len(off_hours) != 24:
            raise RuntimeError(
                f"Off hours must be and array of length 24, and {off_hours} was given"
            )

        self.off_hours = off_hours

    def get_mock_electric_consume(self) -> float:
        """
        Returns the predicted total electricity consumption for the block.

        This method sums up the predicted hourly demand values to get the total predicted consumption.
        """
        return sum(self.predicted_demand_per_hour)
