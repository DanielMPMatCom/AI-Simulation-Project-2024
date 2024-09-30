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

    def action(self):
        """A simulation step where the agent updates beliefs, desires, and intentions."""
        raise NotImplementedError("This method should be implemented by subclasses")


class ThermoElectricAgentPerception:
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


class ThermoElectricAgentAction:
    def __init__(
        self,
        increase_power_output,
        operate_at_full_capacity,
        inspect_critical_parts,
        perform_maintenance_on_parts,
        repair_during_low_demand,
        reduce_downtime,
        meet_demand,
        prioritize_repair_of_critical_parts,
        repair_parts,
    ) -> None:
        self.increase_power_output = increase_power_output
        self.operate_at_full_capacity = operate_at_full_capacity
        self.inspect_critical_parts = inspect_critical_parts
        self.perform_maintenance_on_parts = perform_maintenance_on_parts
        self.repair_during_low_demand = repair_during_low_demand
        self.reduce_downtime = reduce_downtime
        self.meet_demand = meet_demand
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
        perception: ThermoElectricAgentPerception = None,
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
                    "prioritize_critical_parts_repair": TAPriorizeCriticalPartsRepairDesire(),
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
            # "boilers_status": [
            #     (boiler.is_working(), boiler.estimated_remaining_life)
            #     for boiler in thermoelectric.parts
            #     if isinstance(boiler, Boiler)
            # ],
            # "unique_parts_status": [
            #     (part.is_working(), part.estimated_remaining_life)
            #     for part in thermoelectric.parts
            #     if not isinstance(part, Boiler)
            # ],
        }
        # self.update_beliefs()

        self.desires = {
            "maintain_maximum_power_output": False,
            "prevent_unexpected_breakdowns": False,
            "minimize_downtime": False,
            "meet_energy_demand": False,
            "prioritize_critical_part_repair": False,
            # "schedule_repairs_during_low_demand": Desire(
            #     False, "Desire of schedule repairs during low demand"
            # ),  # REVISAR
            "repair_parts": [(part, False) for part in self.thermoelectric.parts],
        }

        self.intentions = {
            "increase_power_output": Intention(
                False, "Intention to increase power output"
            ),
            "operate_at_full_capacity": Intention(
                False, "Intention to operate at full capacity"
            ),
            "inspect_critical_parts": Intention(
                False, "Intention to inspect critical parts"
            ),  # REVISAR
            # "schedule_maintenance": Intention(
            #     [(part, False) for part in self.thermoelectric.parts],
            #     "A List of Tuples where the left side is the Part and the right side is True if the Part needs maintenance",
            # ),
            "perform_maintenance_on_parts": Intention(
                [(part, False) for part in self.thermoelectric.parts],
                "A List of Tuples where the left side is the Part and the right side is True if the Part needs maintenance",
            ),
            "repair_during_low_demand": Intention(
                False, "Intention to repair during low demand"
            ),  # REVISAR
            "reduce_downtime": Intention(False, "Intention to reduce downtime"),
            "meet_demand": Intention(False, "Intention to meet demand"),
            "prioritize_repair_of_critical_parts": Intention(
                False, "Intention to prioritize repair of critical parts"
            ),
            "repair_parts": Intention(
                [(part, False) for part in self.thermoelectric.parts]
            ),
        }

    # def get_general_deficit(self):
    #     raise NotImplementedError()

    # def get_general_demand(self):
    #     raise NotImplementedError()

    # def update_beliefs(self):
    #     """Updates the beliefs of the agent based on the current state of system."""
    #     self.beliefs["plant_is_working"] = self.thermoelectric.is_working()
    #     self.beliefs["parts_status"] = self.get_parts_status()
    #     self.beliefs["broken_parts"] = self.thermoelectric.get_broken_parts()
    #     self.beliefs["current_capacity"] = self.thermoelectric.current_capacity
    #     self.beliefs["power_output_reduction_on_part_failure"] = [
    #         (part, self.get_output_reduction_on_part_failure(part))
    #         for part in self.thermoelectric.parts
    #     ]
    #     self.beliefs["general_deficit"] = self.get_general_deficit()
    #     self.beliefs["general_demand"] = self.get_general_demand()

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

        # Optionally: Add logging or debugging information for the updated beliefs
        print(f"Updated beliefs: {self.beliefs}")

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
            self.intentions["increase_power_output"].value = True
            self.intentions["operate_at_full_capacity"].value = True
        else:
            self.intentions["increase_power_output"].value = False
            self.intentions["operate_at_full_capacity"].value = False

        # If the agent desires to prevent unexpected breakdowns, he will intend to inspect critical parts and perform maintenance on parts
        if self.desires["prevent_unexpected_breakdowns"]:
            self.intentions["inspect_critical_parts"].value = True
            self.intentions["perform_maintenance_on_parts"].value = [
                (part, time <= 1)
                for part, _, time in self.beliefs["parts_status"].value
            ]
        else:
            self.intentions["inspect_critical_parts"].value = False
            self.intentions["perform_maintenance_on_parts"].value = [
                (part, False) for part, _, _ in self.beliefs["parts_status"].value
            ]

        # If the agent desires to minimize downtime, he will intend to repair during low demand and reduce downtime
        if self.desires["minimize_downtime"]:
            self.intentions["repair_during_low_demand"].value = True
            self.intentions["reduce_downtime"].value = True
        else:
            self.intentions["repair_during_low_demand"].value = False
            self.intentions["reduce_downtime"].value = False

        # If the agent desires to meet energy demand, he will intend to meet demand
        if self.desires["meet_energy_demand"]:
            self.intentions["meet_demand"].value = True
        else:
            self.intentions["meet_demand"].value = False

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

    def execute(self):
        """
        Executes the intentions of the agent.
        """

        increase_power_output = False
        operate_at_full_capacity = False
        inspect_critical_parts = False
        perform_maintenance_on_parts = [
            (part, False) for part in self.thermoelectric.parts
        ]
        repair_during_low_demand = False
        reduce_downtime = False
        meet_demand = False
        prioritize_repair_of_critical_parts = False
        repair_parts = [(part, False) for part in self.thermoelectric.parts]

        #
        if self.intentions["increase_power_output"].value:
            increase_power_output = True
            self.intentions["increase_power_output"].value = False
            # Placeholder for increasing power output

            return ThermoElectricAgentAction(
                increase_power_output=increase_power_output,
                operate_at_full_capacity=operate_at_full_capacity,
                inspect_critical_parts=inspect_critical_parts,
                perform_maintenance_on_parts=perform_maintenance_on_parts,
                repair_during_low_demand=repair_during_low_demand,
                reduce_downtime=reduce_downtime,
                meet_demand=meet_demand,
                prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
                repair_parts=repair_parts,
            )

        if self.intentions["operate_at_full_capacity"].value:
            operate_at_full_capacity = True
            self.intentions["operate_at_full_capacity"].value = False
            # Placeholder for operating at full capacity

            return ThermoElectricAgentAction(
                increase_power_output=increase_power_output,
                operate_at_full_capacity=operate_at_full_capacity,
                inspect_critical_parts=inspect_critical_parts,
                perform_maintenance_on_parts=perform_maintenance_on_parts,
                repair_during_low_demand=repair_during_low_demand,
                reduce_downtime=reduce_downtime,
                meet_demand=meet_demand,
                prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
                repair_parts=repair_parts,
            )

        if self.intentions["inspect_critical_parts"].value:
            inspect_critical_parts = True
            self.intentions["inspect_critical_parts"].value = False
            # Placeholder for inspecting critical parts

            return ThermoElectricAgentAction(
                increase_power_output=increase_power_output,
                operate_at_full_capacity=operate_at_full_capacity,
                inspect_critical_parts=inspect_critical_parts,
                perform_maintenance_on_parts=perform_maintenance_on_parts,
                repair_during_low_demand=repair_during_low_demand,
                reduce_downtime=reduce_downtime,
                meet_demand=meet_demand,
                prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
                repair_parts=repair_parts,
            )

        if self.intentions["perform_maintenance_on_parts"].value:
            perform_maintenance_on_parts = self.intentions[
                "perform_maintenance_on_parts"
            ].value
            self.intentions["perform_maintenance_on_parts"].value = [
                (part, False) for part in self.thermoelectric.parts
            ]
            # Placeholder for performing maintenance on parts

            return ThermoElectricAgentAction(
                increase_power_output=increase_power_output,
                operate_at_full_capacity=operate_at_full_capacity,
                inspect_critical_parts=inspect_critical_parts,
                perform_maintenance_on_parts=perform_maintenance_on_parts,
                repair_during_low_demand=repair_during_low_demand,
                reduce_downtime=reduce_downtime,
                meet_demand=meet_demand,
                prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
                repair_parts=repair_parts,
            )

        if self.intentions["repair_during_low_demand"].value:
            repair_during_low_demand = True
            self.intentions["repair_during_low_demand"].value = False
            # Placeholder for repairing during low demand

            return ThermoElectricAgentAction(
                increase_power_output=increase_power_output,
                operate_at_full_capacity=operate_at_full_capacity,
                inspect_critical_parts=inspect_critical_parts,
                perform_maintenance_on_parts=perform_maintenance_on_parts,
                repair_during_low_demand=repair_during_low_demand,
                reduce_downtime=reduce_downtime,
                meet_demand=meet_demand,
                prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
                repair_parts=repair_parts,
            )

        if self.intentions["reduce_downtime"].value:
            reduce_downtime = True
            self.intentions["reduce_downtime"].value = False
            # Placeholder for reducing downtime

            return ThermoElectricAgentAction(
                increase_power_output=increase_power_output,
                operate_at_full_capacity=operate_at_full_capacity,
                inspect_critical_parts=inspect_critical_parts,
                perform_maintenance_on_parts=perform_maintenance_on_parts,
                repair_during_low_demand=repair_during_low_demand,
                reduce_downtime=reduce_downtime,
                meet_demand=meet_demand,
                prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
                repair_parts=repair_parts,
            )

        if self.intentions["meet_demand"].value:
            meet_demand = True
            self.intentions["meet_demand"].value = False
            # Placeholder for meeting demand

            return ThermoElectricAgentAction(
                increase_power_output=increase_power_output,
                operate_at_full_capacity=operate_at_full_capacity,
                inspect_critical_parts=inspect_critical_parts,
                perform_maintenance_on_parts=perform_maintenance_on_parts,
                repair_during_low_demand=repair_during_low_demand,
                reduce_downtime=reduce_downtime,
                meet_demand=meet_demand,
                prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
                repair_parts=repair_parts,
            )

        if self.intentions["prioritize_repair_of_critical_parts"].value:
            prioritize_repair_of_critical_parts = True
            self.intentions["prioritize_repair_of_critical_parts"].value = False
            # Placeholder for prioritizing repair of critical parts

            return ThermoElectricAgentAction(
                increase_power_output=increase_power_output,
                operate_at_full_capacity=operate_at_full_capacity,
                inspect_critical_parts=inspect_critical_parts,
                perform_maintenance_on_parts=perform_maintenance_on_parts,
                repair_during_low_demand=repair_during_low_demand,
                reduce_downtime=reduce_downtime,
                meet_demand=meet_demand,
                prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
                repair_parts=repair_parts,
            )

        if self.intentions["repair_parts"].value:
            repair_parts = self.intentions["repair_parts"].value
            self.intentions["repair_parts"].value = [
                (part, False) for part in self.thermoelectric.parts
            ]
            # Placeholder for repairing parts

            return ThermoElectricAgentAction(
                increase_power_output=increase_power_output,
                operate_at_full_capacity=operate_at_full_capacity,
                inspect_critical_parts=inspect_critical_parts,
                perform_maintenance_on_parts=perform_maintenance_on_parts,
                repair_during_low_demand=repair_during_low_demand,
                reduce_downtime=reduce_downtime,
                meet_demand=meet_demand,
                prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
                repair_parts=repair_parts,
            )

        # print(f"{self.name} is executing intentions.")

    def action(
        self, perception: ThermoElectricAgentPerception
    ) -> ThermoElectricAgentAction:
        """Executes a simulation step: updates beliefs, desires, and intentions, then acts."""
        self.perception = perception
        self.brf()
        self.generate_desires()
        self.filter_intentions()
        return self.execute()

    # def update_desires(self):
    #     """Sets the desires of the agent, such as maintaining full capacity and repairing broken parts."""
    #     self.desires.clear()
    #     if not self.beliefs["plant_is_operational"]:
    #         self.desires.append("repair_parts")
    #     else:
    #         self.desires.append("maintain_capacity")

    # def select_intentions(self):
    #     """Based on the desires, the agent commits to specific actions (intentions)."""
    #     self.intentions.clear()
    #     if "repair_parts" in self.desires:
    #         self.intentions.append(self.repair_broken_parts)
    #     if "maintain_capacity" in self.desires:
    #         self.intentions.append(self.schedule_maintenance)

    # def calculate_current_capacity(self) -> float:
    #     """Calculates the current capacity of the plant based on operational boilers."""
    #     working_boilers = [
    #         part
    #         for part in self.parts
    #         if isinstance(part, Boiler) and part.is_working()
    #     ]
    #     capacity = (
    #         len(working_boilers) / len([p for p in self.parts if isinstance(p, Boiler)])
    #     ) * self.max_capacity
    #     return capacity

    # def repair_broken_parts(self):
    #     """Repairs broken parts in the plant."""
    #     for part in self.beliefs["broken_parts"]:
    #         part.repair()
    #     self.update_beliefs()

    # def schedule_maintenance(self):
    #     """Schedule maintenance of parts to prevent breakdowns."""
    #     for part in self.parts:
    #         if random() > 0.5:  # Randomly decide to maintain parts for now
    #             part.planificate_break_date()


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
        thermoelectrics: List[ThermoelectricAgent],
        circuits: List["Circuit"],
    ):
        Person.__init__(self, name=name, id=id)
        self.thermoelectrics = thermoelectrics
        self.circuits = circuits

    def update_beliefs(self):
        """Updates the beliefs about the system state (e.g., available generation, circuit demands)."""
        self.beliefs["total_generation"] = sum(
            plant.calculate_current_capacity() for plant in self.thermoelectrics
        )
        self.beliefs["total_demand"] = sum(
            circuit.get_total_demand() for circuit in self.circuits
        )

    def update_desires(self):
        """Defines desires like balancing generation with demand and avoiding blackouts."""
        self.desires.clear()
        if self.beliefs["total_demand"] > self.beliefs["total_generation"]:
            self.desires.append("manage_deficit")
        else:
            self.desires.append("optimize_distribution")

    def select_intentions(self):
        """Based on desires, the agent creates intentions to act upon."""
        self.intentions.clear()
        if "manage_deficit" in self.desires:
            self.intentions.append(self.plan_power_cuts)
        if "optimize_distribution" in self.desires:
            self.intentions.append(self.allocate_optimal_distribution)

    def plan_power_cuts(self):
        """Plan power cuts across circuits in case of a generation deficit."""
        # Placeholder for Monte Carlo or optimization algorithm for power cuts

    def allocate_optimal_distribution(self):
        """Allocate the optimal electricity distribution to the circuits."""
        # Placeholder for optimization logic or fuzzy logic based on costs and demand

    def step(self):
        """Executes a simulation step: updates beliefs, desires, and intentions, then acts."""
        self.update_beliefs()
        self.update_desires()
        self.select_intentions()
        for intention in self.intentions:
            intention()


# class Citizen(Person):
#     """
#     Class representing a citizen in a block of a circuit.
#     Citizens react to changes in electricity supply, like blackouts or power restoration.
#     Inherits from the Person class.
#     """

#     def __init__(self, name: str, block: "Block", motivation: str):
#         Person.__init__(self, name)
#         self.block = block
#         self.motivation = motivation

#     def update_beliefs(self):
#         """Citizens update their beliefs based on the status of electricity in their block."""
#         self.beliefs["has_power"] = self.block.has_power()

#     def update_desires(self):
#         """Citizens desire uninterrupted power supply."""
#         self.desires.clear()
#         if not self.beliefs["has_power"]:
#             self.desires.append("restore_power")

#     def select_intentions(self):
#         """Citizens' intentions reflect their need for power restoration."""
#         self.intentions.clear()
#         if "restore_power" in self.desires:
#             self.intentions.append(self.complain_to_authorities)

#     def complain_to_authorities(self):
#         """Action taken when power is out for too long: complain."""
#         print(f"{self.name} is complaining about power outage in {self.block.name}")

#     def step(self):
#         """Executes a simulation step for the citizen: updates beliefs, desires, and intentions."""
#         self.update_beliefs()
#         self.update_desires()
#         self.select_intentions()
#         for intention in self.intentions:
#             intention()


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
        industrialization = ctrl.Atecedent(np.arange(0, 1, 1, 0.1), "industrialization")
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

    def complain():
        pass
