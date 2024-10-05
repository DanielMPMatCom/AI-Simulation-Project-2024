from src.thermoelectrics import Thermoelectric
from typing import List
import random
from worldstate import *
from bdi import *
from part import *
from circuits import *
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class Person:
    """
    Base class representing a person with a name.
    It serves as a parent class for ThermoelectricAgent, ChiefElectricCompanyAgent, and Citizen.
    """

    def __init__(self, name: str, id: int):
        self.name = name
        self.id = id
        self.beliefs = {}
        self.desires = {}
        self.intentions = {}

    def brf(self):
        """
        Belief Revision Function: Updates the agent's beliefs based on new perceptions.
        """
        raise NotImplementedError("This method should be implemented by subclasses")

    def generate_desires(self):
        """
        Generates desires based on the current beliefs of the agent.
        """
        raise NotImplementedError("This method should be implemented by subclasses")

    def filter_intentions(self):
        """
        Filter intentions based on the current beliefs and desires of the agent.
        """
        raise NotImplementedError("This method should be implemented by subclasses")

    def execute(self):
        """
        Executes the intentions of the agent.
        """
        raise NotImplementedError("This method should be implemented by subclasses")

    def action(self, perception):
        """A simulation step where the agent updates beliefs, desires, and intentions."""
        raise NotImplementedError("This method should be implemented by subclasses")


# region Thermoelectric Agent
class ThermoelectricAgentPerception:
    def __init__(
        self,
        thermoelectric: Thermoelectric,
        general_deficit: float,
        general_demand: float,
        general_offer: float,
    ) -> None:
        self.thermoelectric = thermoelectric
        self.plant_status = self.thermoelectric.is_working()
        self.parts_status = self.thermoelectric.get_parts_status()
        self.broken_parts = self.thermoelectric.get_broken_parts()
        self.max_capacity = thermoelectric.total_capacity
        self.current_capacity = thermoelectric.current_capacity
        self.power_output_reduction_on_part_failure = [
            (part, self.thermoelectric.get_output_reduction_on_part_failure(part))
            for part in self.thermoelectric.parts
        ]
        self.general_deficit = general_deficit
        self.general_demand = general_demand
        self.general_offer = general_offer


class ThermoelectricAgentAction:
    def __init__(
        self,
        increase_power_output,
        operate_at_full_capacity,
        perform_maintenance_on_parts,
        reduce_downtime,
        prioritize_repair_of_critical_parts,
        repair_parts,
    ) -> None:
        self.increase_power_output = increase_power_output
        self.operate_at_full_capacity = operate_at_full_capacity
        self.perform_maintenance_on_parts = perform_maintenance_on_parts
        self.reduce_downtime = reduce_downtime
        self.prioritize_repair_of_critical_parts = prioritize_repair_of_critical_parts
        self.repair_parts = repair_parts


class ThermoelectricAgent(Person):
    """
    BDI Agent representing a thermoelectric power plant.
    Responsible for deciding maintenance cycles, repairs, and managing plant operation.
    Inherits from the Person class.
    """

    def __init__(
        self,
        name: str,
        id: int,
        thermoelectric: Thermoelectric,
        perception: ThermoelectricAgentPerception = None,
    ) -> None:

        Person.__init__(self, name=name, id=id)
        self.thermoelectric = thermoelectric
        self.perception = perception

        self.beliefs = {
            "plant_is_working": Belief(
                False,
                "True if the Agent's Thermoelectric Plant is working, False otherwise",
            ),
            "parts_status": Belief(
                [],
                "A List of Tuples with 3 elements, where the left side is the part instance, the middle side is True if the part is working and False otherwise, \
                    and the right side indicates the estimated remaining life time",
            ),
            "broken_parts": Belief([], "A List of Parts that are currently broken"),
            "max_capacity": Belief(
                0, "The maximum capacity of the Thermoelectric Plant"
            ),
            "current_capacity": Belief(
                0, "The current capacity of the Thermoelectric Plant"
            ),
            "power_output_reduction_on_part_failure": Belief(
                [],
                "A List of Tuples where the left side is the Part and the right side is the power output \
                    reduction on its failure",
            ),
            "general_deficit": Belief(0, "The general deficit of the Electric System"),
            "general_demand": Belief(0, "The general demand of the Electric System"),
            "general_offer": Belief(0, "The general offer of the Electric System"),
            "all_desires": Belief(
                {
                    "max_power_output": TAMaxPowerOutputDesire(),
                    "prevent_unexpected_breakdowns": TAPreventUnexpectedBreakdownDesire(),
                    "minimize_downtime": TAMinimizeDowntimeDesire(),
                    "meet_energy_demand": TAMeetEnergyDemandDesire(),
                    "prioritize_critical_parts_repair": TAPrioritizeCriticalPartsRepairDesire(),
                    "repair_parts": TARepairPartsDesire(),
                },
                "All possible desires of the Agent",
            ),
            "current_desires": Belief(
                [
                    "max_power_output",
                    "prevent_unexpected_breakdowns",
                    "minimize_downtime",
                    "meet_energy_demand",
                    "prioritize_critical_parts_repair",
                    "repair_parts",
                ],
                "The current desires of the Agent",
            ),
        }

        self.desires = {
            "maintain_maximum_power_output": False,
            "prevent_unexpected_breakdowns": False,
            "minimize_downtime": False,
            "meet_energy_demand": False,
            "prioritize_critical_part_repair": False,
            "repair_parts": [(part, False) for part in self.thermoelectric.parts],
            # "schedule_repairs_during_low_demand": Desire(
            #     False, "Desire of schedule repairs during low demand"
            # ),  # TODO
        }

        self.intentions = {
            "increase_power_output": Intention(
                False, "Intention to increase power output"
            ),
            "operate_at_full_capacity": Intention(
                False, "Intention to operate at full capacity"
            ),
            "perform_maintenance_on_parts": Intention(
                [(part, False) for part in self.thermoelectric.parts],
                "A List of Tuples where the left side is the Part and the right side is True if the Part needs maintenance",
            ),
            "reduce_downtime": Intention(False, "Intention to reduce downtime"),
            "prioritize_repair_of_critical_parts": Intention(
                False, "Intention to prioritize repair of critical parts"
            ),
            "repair_parts": Intention(
                [(part, False) for part in self.thermoelectric.parts]
            ),
            # "meet_demand": Intention(False, "Intention to meet demand"),
            # "inspect_critical_parts": Intention(
            #     False, "Intention to inspect critical parts"
            # ),  # TODO
            # "schedule_maintenance": Intention(
            #     [(part, False) for part in self.thermoelectric.parts],
            #     "A List of Tuples where the left side is the Part and the right side is True if the Part needs maintenance",
            # ),
            # "repair_during_low_demand": Intention(
            #     False, "Intention to repair during low demand"
            # ),  # TODO
        }

    def brf(self) -> None:
        """
        Belief Revision Function: Updates the agent's beliefs based on new perceptions.
        """

        # Update beliefs based on the new perception

        # 1. Update belief about whether the plant is working
        self.beliefs["plant_is_working"].value = self.perception.plant_status

        # 2. Update beliefs about the status of the parts
        # The belief stores a list of tuples with part status (is_working, estimated_remaining_life)
        self.beliefs["parts_status"].value = self.perception.parts_status

        # 3. Update the broken parts list
        self.beliefs["broken_parts"].value = self.perception.broken_parts

        # 4. Update the current and maximum capacity of the thermoelectric plant
        self.beliefs["max_capacity"].value = self.perception.max_capacity
        self.beliefs["current_capacity"].value = self.perception.current_capacity

        # 5. Update beliefs about power output reduction due to part failures
        self.beliefs["power_output_reduction_on_part_failure"].value = (
            self.perception.power_output_reduction_on_part_failure
        )

        # 6. Update the belief about the general energy deficit, demand and offer
        self.beliefs["general_deficit"].value = self.perception.general_deficit
        self.beliefs["general_demand"].value = self.perception.general_demand
        self.beliefs["general_offer"].value = self.perception.general_offer

        # # Optionally: Add logging or debugging information for the updated beliefs
        # print(f"Updated beliefs: {self.beliefs}")

    def generate_desires(self) -> None:
        """
        Generates desires based on the current beliefs of the agent.
        """

        self.beliefs["current_desires"].value.sort(
            key=lambda x: self.beliefs["all_desires"].value[x].weight
        )

        for desire in self.beliefs["current_desires"].value:
            self.beliefs["all_desires"].value[desire].evaluate(self)

        # print(f"Generated desires: {self.desires}")

    def filter_intentions(self):
        """
        Filter intentions based on the current beliefs and desires of the agent.
        """
        # If the agent desires to maintain maximum power output, he will intend to increase power output and operate at full capacity
        if self.desires["max_power_output"]:
            self.intentions["operate_at_full_capacity"].value = True
        else:
            self.intentions["operate_at_full_capacity"].value = False

        # If the agent desires to prevent unexpected breakdowns, he will intend to inspect critical parts and perform maintenance on parts
        if self.desires["prevent_unexpected_breakdowns"]:
            # self.intentions["inspect_critical_parts"].value = True
            self.intentions["perform_maintenance_on_parts"].value = [
                (part, time <= 1)
                for part, _, time in self.beliefs["parts_status"].value
            ]
        else:
            # self.intentions["inspect_critical_parts"].value = False
            self.intentions["perform_maintenance_on_parts"].value = [
                (part, False) for part, _, _ in self.beliefs["parts_status"].value
            ]

        # If the agent desires to minimize downtime, he will intend to repair during low demand and reduce downtime
        if self.desires["minimize_downtime"]:
            # self.intentions["repair_during_low_demand"].value = True
            self.intentions["reduce_downtime"].value = True
        else:
            # self.intentions["repair_during_low_demand"].value = False
            self.intentions["reduce_downtime"].value = False

        # If the agent desires to meet energy demand, he will intend to meet demand
        if self.desires["meet_energy_demand"]:
            self.intentions["increase_power_output"].value = True
        else:
            self.intentions["increase_power_output"].value = False

        # If the agent desires to prioritize repair of critical parts, he will intend to prioritize repair of critical parts
        if self.desires["prioritize_critical_part_repair"]:
            self.intentions["prioritize_repair_of_critical_parts"].value = True
        else:
            self.intentions["prioritize_repair_of_critical_parts"].value = False

        # The agent will intend to repair parts that need repair
        self.intentions["repair_parts"].value = [
            (part, need_repair) for part, need_repair in self.desires["repair_parts"]
        ]

        # print(f"Generated intentions: {self.intentions}")

    def get_most_important_repair_part(self, condition, time_prior=True):
        most_important_part_index = -1
        reduction_on_fail = 0
        left_time = int("inf")

        for i, (_, _, time) in enumerate(self.beliefs["parts_status"].value):
            if condition(i):
                if (
                    reduction_on_fail
                    < self.beliefs["power_output_reduction_on_part_failure"].value[i][1]
                ):
                    most_important_part_index = i
                    left_time = time
                    reduction_on_fail = self.beliefs[
                        "power_output_reduction_on_part_failure"
                    ].value[i][1]

                elif time_prior and left_time > time:
                    most_important_part_index = i
                    left_time = time

        return most_important_part_index

    def execute(self):
        """
        Executes the intentions of the agent.
        """

        increase_power_output = False
        operate_at_full_capacity = False
        perform_maintenance_on_parts = [
            (part, False) for part in self.thermoelectric.parts
        ]
        reduce_downtime = False
        prioritize_repair_of_critical_parts = False
        repair_parts = [
            (part, part.is_repairing()) for part in self.thermoelectric.parts
        ]
        # meet_demand = False
        # repair_during_low_demand = False
        # inspect_critical_parts = False

        if self.intentions["repair_parts"].value:

            repair_parts = self.intentions["repair_parts"].value
            self.intentions["repair_parts"].value = [
                (part, False) for part in self.thermoelectric.parts
            ]

            most_important_part_index = self.get_most_important_repair_part(
                lambda i: not self.beliefs["part_status"].value[i][1]
            )

            if most_important_part_index >= 0:
                current_repair_index = (
                    self.thermoelectric.get_current_repair_part_index()
                )

                if current_repair_index >= 0:
                    self.thermoelectric.parts[current_repair_index].set_repairing(False)

                self.thermoelectric.parts[most_important_part_index].set_repairing(True)

            return ThermoelectricAgentAction(
                increase_power_output=increase_power_output,
                operate_at_full_capacity=operate_at_full_capacity,
                perform_maintenance_on_parts=perform_maintenance_on_parts,
                reduce_downtime=reduce_downtime,
                prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
                repair_parts=repair_parts,
                # meet_demand=meet_demand,
                # repair_during_low_demand=repair_during_low_demand,
                # inspect_critical_parts=inspect_critical_parts,
            )

        if self.intentions["increase_power_output"].value:
            increase_power_output = True
            self.intentions["increase_power_output"].value = False

            most_important_part_index = self.get_most_important_repair_part(
                lambda i: not self.beliefs["part_status"].value[i][1]
            )

            if most_important_part_index >= 0:
                current_repair_index = (
                    self.thermoelectric.get_current_repair_part_index()
                )

                if current_repair_index >= 0:
                    self.thermoelectric.parts[current_repair_index].set_repairing(False)

                self.thermoelectric.parts[most_important_part_index].set_repairing(True)

            return ThermoelectricAgentAction(
                increase_power_output=increase_power_output,
                operate_at_full_capacity=operate_at_full_capacity,
                perform_maintenance_on_parts=perform_maintenance_on_parts,
                reduce_downtime=reduce_downtime,
                prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
                repair_parts=repair_parts,
                # meet_demand=meet_demand,
                # repair_during_low_demand=repair_during_low_demand,
                # inspect_critical_parts=inspect_critical_parts,
            )

        if self.intentions["operate_at_full_capacity"].value:
            operate_at_full_capacity = True
            self.intentions["operate_at_full_capacity"].value = False

            most_important_part_index = self.get_most_important_repair_part(
                lambda i: not self.beliefs["part_status"].value[i][1], False
            )

            if most_important_part_index >= 0:
                current_repair_index = (
                    self.thermoelectric.get_current_repair_part_index()
                )

                if current_repair_index >= 0:
                    self.thermoelectric.parts[current_repair_index].set_repairing(False)

                self.thermoelectric.parts[most_important_part_index].set_repairing(True)
                self.thermoelectric.parts[most_important_part_index].hurry_repair()

            return ThermoelectricAgentAction(
                increase_power_output=increase_power_output,
                operate_at_full_capacity=operate_at_full_capacity,
                perform_maintenance_on_parts=perform_maintenance_on_parts,
                reduce_downtime=reduce_downtime,
                prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
                repair_parts=repair_parts,
                # meet_demand=meet_demand,
                # repair_during_low_demand=repair_during_low_demand,
                # inspect_critical_parts=inspect_critical_parts,
            )

        if self.intentions["perform_maintenance_on_parts"].value:
            perform_maintenance_on_parts = self.intentions[
                "perform_maintenance_on_parts"
            ].value

            self.intentions["perform_maintenance_on_parts"].value = [
                (part, False) for part in self.thermoelectric.parts
            ]

            part: Part = perform_maintenance_on_parts[0][0]
            part.repair()

            return ThermoelectricAgentAction(
                increase_power_output=increase_power_output,
                operate_at_full_capacity=operate_at_full_capacity,
                perform_maintenance_on_parts=perform_maintenance_on_parts,
                reduce_downtime=reduce_downtime,
                prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
                repair_parts=repair_parts,
                # meet_demand=meet_demand,
                # repair_during_low_demand=repair_during_low_demand,
                # inspect_critical_parts=inspect_critical_parts,
            )

        if self.intentions["reduce_downtime"].value:
            reduce_downtime = True
            self.intentions["reduce_downtime"].value = False

            critical_parts_map = self.thermoelectric.get_criticals_part()

            most_important_part_index = self.get_most_important_repair_part(
                lambda i: critical_parts_map[i]
            )

            if most_important_part_index >= 0:
                current_repair_index = (
                    self.thermoelectric.get_current_repair_part_index()
                )

                if current_repair_index >= 0:
                    self.thermoelectric.parts[current_repair_index].set_repairing(False)

                self.thermoelectric.parts[most_important_part_index].set_repairing(True)
                self.thermoelectric.parts[most_important_part_index].hurry_repair()

            return ThermoelectricAgentAction(
                increase_power_output=increase_power_output,
                operate_at_full_capacity=operate_at_full_capacity,
                perform_maintenance_on_parts=perform_maintenance_on_parts,
                reduce_downtime=reduce_downtime,
                prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
                repair_parts=repair_parts,
                # meet_demand=meet_demand,
                # repair_during_low_demand=repair_during_low_demand,
                # inspect_critical_parts=inspect_critical_parts,
            )

        if self.intentions["prioritize_repair_of_critical_parts"].value:
            prioritize_repair_of_critical_parts = True
            self.intentions["prioritize_repair_of_critical_parts"].value = False

            critical_parts_map = self.thermoelectric.get_criticals_part()

            most_important_part_index = self.get_most_important_repair_part(
                lambda i: critical_parts_map[i]
            )

            if most_important_part_index >= 0:
                current_repair_index = (
                    self.thermoelectric.get_current_repair_part_index()
                )

                if current_repair_index >= 0:
                    self.thermoelectric.parts[current_repair_index].set_repairing(False)

                self.thermoelectric.parts[most_important_part_index].set_repairing(True)
                self.thermoelectric.parts[most_important_part_index].repair()

            return ThermoelectricAgentAction(
                increase_power_output=increase_power_output,
                operate_at_full_capacity=operate_at_full_capacity,
                perform_maintenance_on_parts=perform_maintenance_on_parts,
                reduce_downtime=reduce_downtime,
                prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
                repair_parts=repair_parts,
                # meet_demand=meet_demand,
                # repair_during_low_demand=repair_during_low_demand,
                # inspect_critical_parts=inspect_critical_parts,
            )

        # if self.intentions["repair_during_low_demand"].value:
        #     repair_during_low_demand = True
        #     self.intentions["repair_during_low_demand"].value = False
        #     # Placeholder for repairing during low demand

        #     return ThermoelectricAgentAction(
        #         increase_power_output=increase_power_output,
        #         operate_at_full_capacity=operate_at_full_capacity,
        #         inspect_critical_parts=inspect_critical_parts,
        #         perform_maintenance_on_parts=perform_maintenance_on_parts,
        #         repair_during_low_demand=repair_during_low_demand,
        #         reduce_downtime=reduce_downtime,
        #         meet_demand=meet_demand,
        #         prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
        #         repair_parts=repair_parts,
        #     )

        # if self.intentions["meet_demand"].value:
        #     meet_demand = True
        #     self.intentions["meet_demand"].value = False
        #     # Placeholder for meeting demand

        #     return ThermoelectricAgentAction(
        #         increase_power_output=increase_power_output,
        #         operate_at_full_capacity=operate_at_full_capacity,
        #         inspect_critical_parts=inspect_critical_parts,
        #         perform_maintenance_on_parts=perform_maintenance_on_parts,
        #         repair_during_low_demand=repair_during_low_demand,
        #         reduce_downtime=reduce_downtime,
        #         meet_demand=meet_demand,
        #         prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
        #         repair_parts=repair_parts,
        #     )

        # if self.intentions["inspect_critical_parts"].value:
        #     inspect_critical_parts = True
        #     self.intentions["inspect_critical_parts"].value = False
        #     # Placeholder for inspecting critical parts

        #     return ThermoelectricAgentAction(
        #         increase_power_output=increase_power_output,
        #         operate_at_full_capacity=operate_at_full_capacity,
        #         inspect_critical_parts=inspect_critical_parts,
        #         perform_maintenance_on_parts=perform_maintenance_on_parts,
        #         repair_during_low_demand=repair_during_low_demand,
        #         reduce_downtime=reduce_downtime,
        #         meet_demand=meet_demand,
        #         prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
        #         repair_parts=repair_parts,
        #     )

        # print(f"{self.name} is executing intentions.")

    def action(
        self, perception: ThermoelectricAgentPerception
    ) -> ThermoelectricAgentAction:
        """Executes a simulation step: updates beliefs, desires, and intentions, then acts."""
        self.perception = perception
        self.brf()
        self.generate_desires()
        self.filter_intentions()
        return self.execute()


# region Chief of Electric Company Agent
class ChiefElectricCompanyAgentPerception:
    def __init__(
        self,
        thermoelectrics_id: list[str],
        circuits_id: list[str],
        generation_per_thermoelectric: list[float],
        distance_template: list[tuple[str, str, float]],
        demand_per_block_in_circuit: list[int, int, list[float]],
        total_demand_per_circuits: list[float],
        circuits_importance: list[float],
        importance_per_block_in_circuits: list[str, int, float],
        opinion_per_block_in_circuits: list[str, int, float],
        satisfaction_per_circuit: list[float],
        industrialization_per_circuit: list[float],
        last_days_off_per_block_in_circuits: list[str, int, int],
        longest_sequence_off_per_block_in_circuits: list[str, int, int],
    ) -> None:

        self.thermoelectrics_id = thermoelectrics_id

        self.circuits_id = circuits_id

        self.generation_per_thermoelectric = generation_per_thermoelectric

        self.distance_template = [
            (t_id, c_id, cost) for (t_id, c_id, cost, _) in distance_template
        ]

        self.demand_per_block_in_circuits = demand_per_block_in_circuit

        self.total_demand_per_circuits = total_demand_per_circuits

        self.general_demand = sum(self.total_demand_per_circuits)

        self.general_offer = sum(generation_per_thermoelectric)

        self.general_deficit = max(self.general_demand - self.general_offer, 0)

        self.circuits_importance = circuits_importance

        self.importance_per_block_in_circuits = importance_per_block_in_circuits

        self.opinion_per_block_in_circuits = opinion_per_block_in_circuits

        self.satisfaction_per_circuit = satisfaction_per_circuit

        self.industrialization_per_circuit = industrialization_per_circuit

        self.last_days_off_per_block_in_circuits = last_days_off_per_block_in_circuits

        self.longest_sequence_off_per_block_in_circuits = (
            longest_sequence_off_per_block_in_circuits
        )

    def generate_desires(self) -> None:
        """
        Generates desires based on the current beliefs of the agent.
        """


class ChiefElectricCompanyAction:
    def __init__(
        self,
        meet_demand,
        prioritize_block_importance,
        prioritize_block_opinion,
        prioritize_consecutive_days_off,
        prioritize_days_off,
    ) -> None:
        self.meet_demand = meet_demand
        self.prioritize_block_importance = prioritize_block_importance
        self.prioritize_block_opinion = prioritize_block_opinion
        self.prioritize_consecutive_days_off = prioritize_consecutive_days_off
        self.prioritize_days_off = prioritize_days_off


class ChiefElectricCompanyAgent(Person):
    """
    BDI Agent representing the chief of the electric company.
    Responsible for deciding optimal electricity distribution and planning power cuts.
    Inherits from the Person class.
    """

    def __init__(
        self,
        name: str,
        id: int,
        thermoelectrics: list[Thermoelectric],
        circuits: list[Circuit],
        perception: ChiefElectricCompanyAgentPerception,
    ):
        Person.__init__(self, name=name, id=id)

        self.circuits = circuits
        self.thermoelectrics = thermoelectrics

        self.perception = perception

        self.beliefs: dict[str, Belief] = {
            "generation_per_thermoelectric": Belief(
                [],
                description="The electricity generated by each thermoelectric plant.",
            ),
            "distance_template": Belief(
                [],
                description="The cost of transmitting energy from a thermoelectric plant to a circuit. This is represented as a tuple: the first element is the thermoelectric ID, the second is the circuit ID, and the third is the transmission cost.",
            ),
            "demand_per_block_in_circuits": Belief(
                [],
                description="The hourly demand for each block within the circuits. The tuple includes the circuit ID, block ID, and demand value.",
            ),
            "total_demand_per_circuits": Belief(
                [], description="The total hourly demand for each circuit."
            ),
            "general_demand": Belief(
                0, description="The total electricity demand across all circuits."
            ),
            "general_offer": Belief(
                0,
                description="The total electricity generation capacity of the thermoelectric system.",
            ),
            "general_deficit": Belief(
                0, description="The total electricity deficit in the system."
            ),
            "circuits_importance": Belief(
                [], description="The importance ranking of each circuit."
            ),
            "importance_per_block_in_circuits": Belief(
                [],
                description="The importance of each block within the circuits. Each tuple consists of the circuit ID, block ID, and importance value.",
            ),
            "opinion_per_block_in_circuits": Belief(
                [],
                description="The opinion rating of each block within the circuits. Each tuple contains the circuit ID, block ID, and opinion score.",
            ),
            "satisfaction_per_circuit": Belief(
                [],
                description="The satisfaction level for each circuit, represented as a float.",
            ),
            "industrialization_per_circuit": Belief(
                [],
                description="The industrialization level of each circuit, represented as a float.",
            ),
            "last_days_off_per_block_in_circuits": Belief(
                [],
                description="The number of recent consecutive days off for each block within the circuits. Each tuple contains the circuit ID, block ID, and the number of days off.",
            ),
            "longest_sequence_off_per_block_in_circuits": Belief(
                [],
                description="The longest sequence of consecutive days off for each block within the circuits. Each tuple contains the circuit ID, block ID, and the number of consecutive days off.",
            ),
            "all_desires": Belief(
                {
                    "meet_demand": CECAMeetDemandDesire(),
                    "prioritize_block_importance": CECAPrioritizeBlockImportance(),
                    "prioritize_block_opinion": CECAPrioritizeBlockOpinion(),
                    "prioritize_consecutive_days_off": CECAPrioritizeConsecutiveDaysOff(),
                    "prioritize_days_off": CECAPrioritizeDaysOff(),
                }
            ),
            "current_desires": [
                "meet_demand",
                "prioritize_block_importance",
                "prioritize_block_opinion",
                "prioritize_consecutive_days_off",
                "prioritize_days_off",
            ],
        }

        self.desires = {
            "meet_demand": False,
            "prioritize_block_importance": False,
            "prioritize_block_opinion": False,
            "prioritize_consecutive_days_off": False,
            "prioritize_days_off": False,
        }

        self.intentions = {
            "meet_demand": Intention(
                False,
                description="Intention to meet the demand using the current capacity.",
            ),
            "prioritize_block_importance": Intention(
                False,
                description="Intention to prioritize the block with the highest importance.",
            ),
            "prioritize_block_opinion": Intention(
                False,
                description="Intention to prioritize blocks based on their negative opinions.",
            ),
            "prioritize_consecutive_days_off": Intention(
                False,
                description="Intention to prioritize blocks with the most consecutive days off.",
            ),
            "prioritize_days_off": Intention(
                False,
                description="Intention to prioritize circuits that have had the most days without energy.",
            ),
        }

        self.mapper_key_to_circuit_block = self.make_mapper_block_and_circuits(
            self.circuits
        )

    def brf(self) -> None:
        """
        Belief Revision Function: Updates the agent's beliefs based on new perceptions.
        """

        # Update beliefs based on the new perception

        # 1. Update belief about thermoelectric plants
        self.beliefs["thermoelectrics_id"].value = self.perception.thermoelectrics_id

        # 2. Update belief about circuits
        self.beliefs["circuits_id"].value = self.perception.circuits_id

        # 3. Update belief about electricity generation per thermoelectric plant
        self.beliefs["generation_per_thermoelectric"].value = (
            self.perception.generation_per_thermoelectric
        )

        # 4. Update belief about the distance template
        self.beliefs["distance_template"].value = self.perception.distance_template

        # 5. Update belief about the demand per block in circuits
        self.beliefs["demand_per_block_in_circuits"].value = (
            self.perception.demand_per_block_in_circuits
        )

        # 6. Update belief about the total demand for circuits
        self.beliefs["total_demand_per_circuits"].value = (
            self.perception.total_demand_per_circuits
        )

        # 7. Update belief about the general demand, offer, and deficit
        self.beliefs["general_demand"].value = self.perception.general_demand
        self.beliefs["general_offer"].value = self.perception.general_offer
        self.beliefs["general_deficit"].value = self.perception.general_deficit

        # 8. Update belief about the importance of circuits
        self.beliefs["circuits_importance"].value = self.perception.circuits_importance

        # 9. Update belief about the importance per block in circuits
        self.beliefs["importance_per_block_in_circuits"].value = (
            self.perception.importance_per_block_in_circuits
        )

        # 10. Update belief about the opinion per block in circuits
        self.beliefs["opinion_per_block_in_circuits"].value = (
            self.perception.opinion_per_block_in_circuits
        )

        # 11. Update belief about the satisfaction per circuit
        self.beliefs["satisfaction_per_circuit"].value = (
            self.perception.satisfaction_per_circuit
        )

        # 12. Update belief about the industrialization per circuit
        self.beliefs["industrialization_per_circuit"].value = (
            self.perception.industrialization_per_circuit
        )

        # 13. Update belief about last days off per block in circuits
        self.beliefs["last_days_off_per_block_in_circuits"] = (
            self.perception.last_days_off_per_block_in_circuits
        )

        # 14. Update belief about longest sequence  off per block in circuits
        self.beliefs["longest_sequence_off_per_block_in_circuits"] = (
            self.perception.longest_sequence_off_per_block_in_circuits
        )

        # 15. Update belief about mapper key to (c.id, block.id)
        self.beliefs["mapper_id_to_circuit_block"] = (
            self.perception.mapper_id_to_circuit_block
        )

    def generate_desires(self) -> None:
        """
        Generates the agent's desires based on its beliefs.
        """

        self.beliefs["current_desires"].value.sort(
            key=lambda x: self.beliefs["all_desires"].value[x].weight
        )

        for desire in self.beliefs["current_desires"].value:
            self.beliefs["all_desires"].value[desire].evaluate(self)

    def filter_intentions(self):
        """
        Filter intentions based on the current beliefs and desires of the agent.
        """
        if self.desires["meet_demand"]:
            self.intentions["meet_demand"].value = True
        else:
            self.intentions["meet_demand"].value = False

        if self.desires["prioritize_block_importance"]:
            self.intentions["prioritize_block_importance"].value = True
        else:
            self.intentions["prioritize_block_importance"].value = False

        if self.desires["prioritize_block_opinion"]:
            self.intentions["prioritize_block_opinion"].value = True
        else:
            self.intentions["prioritize_block_opinion"].value = False

        if self.desires["prioritize_consecutive_days_off"]:
            self.intentions["prioritize_consecutive_days_off"] = True

        else:
            self.intentions["prioritize_consecutive_days_off"] = False

        if self.desires["prioritize_days_off"]:
            self.intentions["prioritize_days_off"] = True

        else:
            self.intentions["prioritize_days_off"] = False

    def make_mapper_block_and_circuits(self, circuits: list[Circuit]):
        mapper = {}
        key = 0

        for c in circuits:
            for block_id in range(len(c.blocks)):
                mapper[key] = (c.id, block_id)
                key += 1

        return mapper

    def get_cost_to_meet_demand_from_thermoelectric_to_block(self, thermoelectric_number,  )

    def meet_demand_function():
        return

    def execute(self) -> list[ChiefElectricCompanyAction]:
        intentions_executed = []

        while True:
            active_index = [
                intention
                for intention in self.intentions
                if self.intentions[intention].value
            ]

            if len(active_index) <= 0:
                break

            if self.intentions["meet_demand"].value:
                self.intentions["meet_demand"].value = False

                # update belief if necessary, maybe using a new perception
                intentions_executed.append("meet_demand")

        return [
            ChiefElectricCompanyAction(
                meet_demand="meet_demand" in intentions_executed,
                prioritize_block_importance="prioritize_block_importance"
                in intentions_executed,
                prioritize_consecutive_days_off="prioritize_consecutive_days_off"
                in intentions_executed,
                prioritize_days_off="prioritize_days_off" in intentions_executed,
                prioritize_block_opinion="prioritize_block_opinion"
                in intentions_executed,
            )
        ]

    def action(
        self, perception: ChiefElectricCompanyAgentPerception
    ) -> list[ChiefElectricCompanyAction]:
        self.perception = perception
        self.brf()
        self.generate_desires()
        self.filter_intentions()
        return self.execute()


# region Citizen


class Citizen:
    def __init__(self, block: Block, amount: int) -> None:
        self.amount = amount
        self.block = block

        self.opinion

    def set_opinion(
        self,
        input_last_day_off: int,
        input_industrialization: float,
        input_days_off_relation: float,
        input_general_satisfaction: float,
    ):

        last_day_off = ctrl.Antecedent(np.arange(0, 22, 1), "last_day_off")
        industrialization = ctrl.Antecedent(
            np.arange(0, 1, 1, 0.1), "industrialization"
        )
        days_off_relation = ctrl.Antecedent(np.arange(0, 1.1, 0.1), "days_off_relation")
        general_satisfaction = ctrl.Antecedent(
            np.arange(0, 1.1, 0.1), "general_satisfaction"
        )
        personal_satisfaction = ctrl.Consequent(
            np.arange(0, 1, 1, 0.1), "personal_satisfaction"
        )

        # Membership functions for last_day_off
        last_day_off["recent"] = fuzz.trapmf(last_day_off.universe, [0, 0, 5, 10])
        last_day_off["moderate"] = fuzz.trimf(last_day_off.universe, [7, 12, 15])
        last_day_off["distant"] = fuzz.trapmf(last_day_off.universe, [14, 18, 20, 20])

        # Membership functions for industrialization
        industrialization["low"] = fuzz.trapmf(
            industrialization.universe, [0, 0, 0.5, 0.6]
        )
        industrialization["medium"] = fuzz.trimf(
            industrialization.universe, [0.5, 0.7, 0.8]
        )
        industrialization["high"] = fuzz.trapmf(
            industrialization.universe, [0.7, 0.8, 1.0, 1.0]
        )

        # Membership functions for days_off_relation
        days_off_relation["low"] = fuzz.trapmf(
            days_off_relation.universe, [0, 0, 0.1, 0.2]
        )
        days_off_relation["medium"] = fuzz.trimf(
            days_off_relation.universe, [0.1, 0, 3, 0, 4]
        )
        days_off_relation["high"] = fuzz.trapmf(
            days_off_relation.universe, [0.3, 0.5, 1.0, 1.0]
        )

        # Membership functions for general_satisfaction
        general_satisfaction["lowest"] = fuzz.trapmf(
            general_satisfaction.universe, [0, 0, 0.3, 0.4]
        )
        general_satisfaction["lower"] = fuzz.trimf(
            general_satisfaction.universe, [0.3, 0.4, 0.6]
        )
        general_satisfaction["low"] = fuzz.trimf(
            general_satisfaction.universe, [0.5, 0.6, 0.7]
        )
        general_satisfaction["medium"] = fuzz.trimf(
            general_satisfaction.universe, [0.7, 0.8, 0.9]
        )
        general_satisfaction["high"] = fuzz.trapmf(
            general_satisfaction.universe, [0.8, 0.9, 1.0, 1.0]
        )

        # Membership functions for personal_satisfaction
        personal_satisfaction["lowest"] = fuzz.trapmf(
            personal_satisfaction.universe, [0, 0, 0.3, 0.4]
        )
        personal_satisfaction["lower"] = fuzz.trimf(
            personal_satisfaction.universe, [0.3, 0.4, 0.6]
        )
        personal_satisfaction["low"] = fuzz.trimf(
            personal_satisfaction.universe, [0.5, 0.6, 0.7]
        )
        personal_satisfaction["medium"] = fuzz.trimf(
            personal_satisfaction.universe, [0.7, 0.8, 0.9]
        )
        personal_satisfaction["high"] = fuzz.trapmf(
            personal_satisfaction.universe, [0.8, 0.9, 1.0, 1.0]
        )

        # Fuzzy rules
        rules = [
            ctrl.Rule(
                last_day_off["distant"]
                & days_off_relation["low"]
                & industrialization["medium"]
                & general_satisfaction["high"],
                personal_satisfaction["high"],
            ),
            ctrl.Rule(
                last_day_off["distant"]
                & days_off_relation["low"]
                & industrialization["high"]
                & general_satisfaction["high"],
                personal_satisfaction["medium"],
            ),
            ctrl.Rule(
                last_day_off["distant"]
                & days_off_relation["low"]
                & industrialization["high"]
                & general_satisfaction["medium"],
                personal_satisfaction["high"],
            ),
            ctrl.Rule(
                last_day_off["distant"]
                & days_off_relation["low"]
                & industrialization["high"]
                & general_satisfaction["low"],
                personal_satisfaction["medium"],
            ),
            ctrl.Rule(
                last_day_off["recent"]
                & days_off_relation["medium"]
                & industrialization["medium"]
                & general_satisfaction["medium"],
                personal_satisfaction["lower"],
            ),
            ctrl.Rule(
                last_day_off["recent"]
                & days_off_relation["medium"]
                & industrialization["low"]
                & general_satisfaction["medium"],
                personal_satisfaction["medium"],
            ),
            ctrl.Rule(
                last_day_off["recent"]
                & days_off_relation["high"]
                & industrialization["low"]
                & general_satisfaction["lower"],
                personal_satisfaction["lowest"],
            ),
            ctrl.Rule(
                last_day_off["recent"]
                & days_off_relation["high"]
                & industrialization["low"]
                & general_satisfaction["lowest"],
                personal_satisfaction["lower"],
            ),
            ctrl.Rule(
                last_day_off["moderate"]
                & days_off_relation["medium"]
                & industrialization["medium"]
                & general_satisfaction["medium"],
                personal_satisfaction["medium"],
            ),
            ctrl.Rule(
                last_day_off["moderate"]
                & days_off_relation["medium"]
                & industrialization["medium"]
                & general_satisfaction["high"],
                personal_satisfaction["low"],
            ),
            ctrl.Rule(
                last_day_off["moderate"]
                & days_off_relation["medium"]
                & industrialization["medium"]
                & general_satisfaction["low"],
                personal_satisfaction["medium"],
            ),
        ]

        # Create control system
        satisfaction_control = ctrl.ControlSystem(rules)
        satisfaction_simulation = ctrl.ControlSystemSimulation(satisfaction_control)

        # Provide input values to the simulation
        satisfaction_simulation.input["last_day_off"] = input_last_day_off
        satisfaction_simulation.input["industrialization"] = input_industrialization
        satisfaction_simulation.input["days_off_relation"] = input_days_off_relation
        satisfaction_simulation.input["general_satisfaction"] = (
            input_general_satisfaction
        )

        # Compute result
        satisfaction_simulation.compute()

        # Return personal satisfaction
        self.opinion = satisfaction_simulation.output["personal_satisfaction"]

    # def complain():
    #     pass
