from src.bdi import (
    Belief,
    Desire,
    Intention,
    CECAPrioritizeBlockImportance,
    CECAMeetDemandDesire,
    CECAPrioritizeBlockOpinion,
    CECAPrioritizeConsecutiveDaysOff,
    CECAPrioritizeDaysOff,
    CECAGeneratedDesire,
    DesireGenerator,
    TAMaxPowerOutputDesire,
    TAMeetEnergyDemandDesire,
    TAMinimizeDowntimeDesire,
    TAPreventUnexpectedBreakdownDesire,
    TAPrioritizeCriticalPartsRepairDesire,
    TARepairPartsDesire,
)
from src.thermoelectrics import Thermoelectric
from src.circuits import Circuit, Block
from src.part import Part
from src.genetic_per_hour import genetic_algorithm
from src.simulation_constants import (
    DISTANCE_REGULATOR,
    OBJECTIVE_FUNCTION_INTENTION_PARAMS_WEIGHT,
    OBJECTIVE_FUNCTION_INTENTION_PARAMS_DEFAULT_WEIGHT,
    MIN_DAYS_TO_NEED_REPAIR,
)


class Person:
    """
    Base class representing a person with a name.
    It serves as a parent class for ThermoelectricAgent, ChiefElectricCompanyAgent, and Citizen.
    """

    def __init__(self, name: str):
        self.name = name
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
        thermoelectric: "Thermoelectric",
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

    def __str__(self):
        power_output = [
            (part.__class__.__name__, reduction)
            for part, reduction in self.power_output_reduction_on_part_failure
        ]

        parts_status = [(p.__class__.__name__, s, c) for p, s, c in self.parts_status]

        properties = f"""{{
            "thermoelectric: {self.thermoelectric},
            "plant_status": {self.plant_status},
            "parts_status": {parts_status},
            "broken_parts": {[str(part) for part in self.broken_parts]},
            "max_capacity": {self.max_capacity},
            "current_capacity": {self.current_capacity},
            "power_output_reduction_on_part_failure": {power_output},
            "general_deficit": {self.general_deficit},
            "general_demand": {self.general_demand},
            "general_offer": {self.general_offer},
        }}"""
        return properties


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

    def __str__(self):
        properties = f"""
            increase_power_output: {self.increase_power_output},
            operate_at_full_capacity: {self.operate_at_full_capacity},
            perform_maintenance_on_parts: {self.perform_maintenance_on_parts},
            reduce_downtime:{self.reduce_downtime},
            prioritize_repair_of_critical_parts: {self.prioritize_repair_of_critical_parts},
            repair_parts: {self.repair_parts}
        """
        return str(properties)


class ThermoelectricAgent(Person):
    """
    BDI Agent representing a thermoelectric power plant.
    Responsible for deciding maintenance cycles, repairs, and managing plant operation.
    Inherits from the Person class.
    """

    def __init__(
        self,
        name: str,
        thermoelectric: "Thermoelectric",
        rules,
        current_rules,
        perception: "ThermoelectricAgentPerception" = None,
    ) -> None:

        Person.__init__(self, name=name)
        self.thermoelectric = thermoelectric
        self.perception = perception
        self.rules = rules
        self.current_rules = current_rules
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
            "all_desires": Belief(self.rules, "All possible desires"),
            "current_desires": Belief(self.current_rules, "The current active desires"),
        }

        self.desires = {
            "maintain_maximum_power_output": False,
            "minimize_downtime": False,
            "meet_energy_demand": False,
            "prioritize_critical_part_repair": False,
            "prevent_unexpected_breakdowns": False,
            "repair_parts": False,
        }

        self.intentions = {
            "operate_at_full_capacity": Intention(
                False, "Intention to operate the plant at full capacity"
            ),
            "reduce_downtime": Intention(False, "Intention to minimize plant downtime"),
            "increase_power_output": Intention(
                False, "Intention to boost power output"
            ),
            "prioritize_repair_of_critical_parts": Intention(
                False, "Intention to prioritize the repair of critical parts"
            ),
            "perform_maintenance_on_parts": Intention(
                False,
                "Intention to perform maintenance on parts that need maintenance",
            ),
            "repair_parts": Intention(
                False,
                "Intention to repair parts that need repair",
            ),
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
        self.intentions["operate_at_full_capacity"].value = self.desires[
            "maintain_maximum_power_output"
        ]

        # If the agent desires to prevent unexpected breakdowns, he will intend to inspect critical parts and perform maintenance on parts
        self.intentions["perform_maintenance_on_parts"].value = self.desires[
            "prevent_unexpected_breakdowns"
        ]

        # If the agent desires to minimize downtime, he will intend to repair during low demand and reduce downtime
        self.intentions["reduce_downtime"].value = self.desires["minimize_downtime"]

        # If the agent desires to meet energy demand, he will intend to meet demand
        self.intentions["increase_power_output"].value = self.desires[
            "meet_energy_demand"
        ]

        # If the agent desires to prioritize repair of critical parts, he will intend to prioritize repair of critical parts
        self.intentions["prioritize_repair_of_critical_parts"].value = self.desires[
            "prioritize_critical_part_repair"
        ]

        # The agent will intend to repair parts that need repair
        self.intentions["repair_parts"].value = self.desires["repair_parts"]

        # print(f"Generated intentions: {self.intentions}")

    def get_most_important_repair_part(self, condition, time_prior=True):
        most_important_part_index = -1
        reduction_on_fail = 0
        left_time = int(1e9 + 9)

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
        perform_maintenance_on_parts = False
        reduce_downtime = False
        prioritize_repair_of_critical_parts = False
        repair_parts = False

        if self.intentions["operate_at_full_capacity"].value:
            operate_at_full_capacity = True
            self.intentions["operate_at_full_capacity"].value = False

            return ThermoelectricAgentAction(
                increase_power_output=increase_power_output,
                operate_at_full_capacity=operate_at_full_capacity,
                perform_maintenance_on_parts=perform_maintenance_on_parts,
                reduce_downtime=reduce_downtime,
                prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
                repair_parts=repair_parts,
            )

        if self.intentions["reduce_downtime"].value:
            reduce_downtime = True
            self.intentions["reduce_downtime"].value = False

            critical_parts_map = self.thermoelectric.get_criticals_part()

            most_important_part_index = self.get_most_important_repair_part(
                lambda i: critical_parts_map[i]
                and not self.beliefs["parts_status"].value[i][1]
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
            )

        if self.intentions["increase_power_output"].value:
            increase_power_output = True
            self.intentions["increase_power_output"].value = False

            most_important_part_index = self.get_most_important_repair_part(
                lambda i: not self.beliefs["parts_status"].value[i][1]
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
            )

        if self.intentions["prioritize_repair_of_critical_parts"].value:
            prioritize_repair_of_critical_parts = True
            self.intentions["prioritize_repair_of_critical_parts"].value = False

            critical_parts_map = self.thermoelectric.get_criticals_part()

            most_important_part_index = self.get_most_important_repair_part(
                lambda i: critical_parts_map[i]
                and not self.beliefs["parts_status"].value[i][1]
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
            )

        if self.intentions["perform_maintenance_on_parts"].value:
            perform_maintenance_on_parts = self.intentions[
                "perform_maintenance_on_parts"
            ].value

            self.intentions["perform_maintenance_on_parts"].value = False

            currently_maintenance = False
            for part, _, _ in self.beliefs["parts_status"].value:
                part: Part
                if part.is_currently_receiving_maintenance():
                    currently_maintenance = True

            if not currently_maintenance:

                def is_solution(index: int):
                    _, _, time = self.beliefs["parts_status"].value[index]
                    return (
                        time <= MIN_DAYS_TO_NEED_REPAIR
                        and self.beliefs["general_offer"].value
                        - self.beliefs["power_output_reduction_on_part_failure"].value[
                            index
                        ][1]
                        > self.beliefs["general_demand"].value * 3 / 4
                    )

                most_important_part_index = self.get_most_important_repair_part(
                    lambda i: is_solution(index=i)
                    and self.beliefs["parts_status"].value[i][1]
                )

                if most_important_part_index >= 0:
                    current_repair_index = (
                        self.thermoelectric.get_current_repair_part_index()
                    )

                    if current_repair_index >= 0:
                        self.thermoelectric.parts[current_repair_index].set_repairing(
                            False
                        )

                    self.thermoelectric.parts[most_important_part_index].maintenance()

            return ThermoelectricAgentAction(
                increase_power_output=increase_power_output,
                operate_at_full_capacity=operate_at_full_capacity,
                perform_maintenance_on_parts=perform_maintenance_on_parts,
                reduce_downtime=reduce_downtime,
                prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
                repair_parts=repair_parts,
            )

        if self.intentions["repair_parts"].value:

            repair_parts = self.intentions["repair_parts"].value
            self.intentions["repair_parts"].value = False

            most_important_part_index = self.get_most_important_repair_part(
                lambda i: not self.beliefs["parts_status"].value[i][1]
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
            )

        return ThermoelectricAgentAction(
            increase_power_output=increase_power_output,
            operate_at_full_capacity=operate_at_full_capacity,
            perform_maintenance_on_parts=perform_maintenance_on_parts,
            reduce_downtime=reduce_downtime,
            prioritize_repair_of_critical_parts=prioritize_repair_of_critical_parts,
            repair_parts=repair_parts,
        )

    def action(
        self, perception: "ThermoelectricAgentPerception"
    ) -> "ThermoelectricAgentAction":
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
        distance_matrix: list[tuple[str, str, float]],
        demand_per_block_in_circuit: list[tuple[int, int, list[float]]],
        total_demand_per_circuit: list[float],
        circuits_importance: list[float],
        importance_per_block_in_circuits: list[tuple[str, int, float]],
        opinion_per_block_in_circuits: list[tuple[str, int, float]],
        satisfaction_per_circuit: list[float],
        industrialization_per_circuit: list[float],
        last_days_off_per_block_in_circuits: list[tuple[str, int, float]],
        longest_sequence_off_per_block_in_circuits: list[tuple[str, int, float]],
        general_satisfaction: float,
    ) -> None:

        self.thermoelectrics_id = thermoelectrics_id

        self.circuits_id = circuits_id

        self.generation_per_thermoelectric = generation_per_thermoelectric

        self.distance_matrix = distance_matrix

        self.demand_per_block_in_circuits = demand_per_block_in_circuit

        self.total_demand_per_circuit = total_demand_per_circuit

        self.general_demand = sum(self.total_demand_per_circuit)

        self.general_offer = sum(generation_per_thermoelectric)

        self.general_deficit = max(self.general_demand - self.general_offer, 0)

        self.circuits_importance = circuits_importance

        self.importance_per_block_in_circuits = importance_per_block_in_circuits

        self.opinion_per_block_in_circuits = opinion_per_block_in_circuits

        self.satisfaction_per_circuit = satisfaction_per_circuit

        self.general_opinion = general_satisfaction

        self.industrialization_per_circuit = industrialization_per_circuit

        self.last_days_off_per_block_in_circuits = last_days_off_per_block_in_circuits

        self.longest_sequence_off_per_block_in_circuits = (
            longest_sequence_off_per_block_in_circuits
        )

        self.thermoelectrics_state = [x > 0 for x in generation_per_thermoelectric]

        self.working_thermoelectrics_amount = sum(self.thermoelectrics_state)

    def __str__(self):
        properties = f"""{{
            "thermoelectrics_id": {self.thermoelectrics_id},
            "circuits_id": {self.circuits_id},
            "generation_per_thermoelectric": {self.generation_per_thermoelectric},
            "distance_matrix": {self.distance_matrix},
            "demand_per_block_in_circuits": {self.demand_per_block_in_circuits},
            "total_demand_per_circuit": {self.total_demand_per_circuit},
            "general_demand": {self.general_demand},
            "general_offer": {self.general_offer},
            "general_deficit": {self.general_deficit},
            "circuits_importance": {self.circuits_importance},
            "importance_per_block_in_circuits": {self.importance_per_block_in_circuits},
            "opinion_per_block_in_circuits": {self.opinion_per_block_in_circuits},
            "satisfaction_per_circuit": {self.satisfaction_per_circuit},
            "general_opinion": {self.general_opinion},
            "industrialization_per_circuit": {self.industrialization_per_circuit},
            "last_days_off_per_block_in_circuits": {self.last_days_off_per_block_in_circuits},
            "longest_sequence_off_per_block_in_circuits": {self.longest_sequence_off_per_block_in_circuits},
            "working_thermoelectrics_amount": {self.working_thermoelectrics_amount},
            "thermoelectric_state": {self.thermoelectrics_state},
        }}"""
        return properties


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
        thermoelectrics: list["Thermoelectric"],
        circuits: list["Circuit"],
        perception: "ChiefElectricCompanyAgentPerception",
        rules,
        current_rules,
        mapper_key_to_circuit_block,
        learn=False,
    ):
        Person.__init__(self, name=name)

        self.circuits = circuits
        self.thermoelectrics = thermoelectrics
        self.rules = rules
        self.current_rules = current_rules

        self.perception = perception

        self.beliefs: dict[str, "Belief"] = {
            "thermoelectrics_id": Belief(
                [], description="The unique identifier for each thermoelectric plant."
            ),
            "circuits_id": Belief(
                [], description="The unique identifier for each circuit."
            ),
            "generation_per_thermoelectric": Belief(
                [],
                description="The electricity generated by each thermoelectric plant.",
            ),
            "distance_matrix": Belief(
                [],
                description="The cost of transmitting energy from a thermoelectric plant to a circuit. This is represented as a matrix: the columns are thermoelectrics and rows are circuits and the cell is the distance cost",
            ),
            "demand_per_block_in_circuits": Belief(
                [],
                description="The hourly demand for each block within the circuits. The tuple includes the circuit ID, block ID, and demand value.",
            ),
            "total_demand_per_circuit": Belief(
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
            "working_thermoelectrics_amount": Belief(
                0,
                description="The total number of thermoelectric plants that are operational.",
            ),
            "thermoelectric_state": Belief(
                [],
                description="The operational state of each thermoelectric plant. True if operational, false otherwise.",
            ),
            "general_opinion": Belief(0, description="The overall public opinion."),
            "all_desires": Belief(self.rules, "All possible desires"),
            "current_desires": Belief(self.current_rules, "The current active desires"),
        }

        self.desires = {
            "meet_demand": False,
            "prioritize_block_importance": False,
            "prioritize_block_opinion": False,
            "prioritize_consecutive_days_off": False,
            "prioritize_days_off": False,
            "max_stored_energy": False,
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
            "max_stored_energy": Intention(
                False, description="Intention to maximize the stored energy."
            ),
        }

        self.mapper_key_to_circuit_block = mapper_key_to_circuit_block

        self.max_importance_of_all_circuits = sum(
            sum(block.importance for block in circuit.blocks)
            for circuit in self.circuits
        )
        self.last_date_result = ([], 0)
        self.learn = learn

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
        self.beliefs["distance_matrix"].value = self.perception.distance_matrix

        # 5. Update belief about the demand per block in circuits
        self.beliefs["demand_per_block_in_circuits"].value = (
            self.perception.demand_per_block_in_circuits
        )

        # 6. Update belief about the total demand for circuits
        self.beliefs["total_demand_per_circuit"].value = (
            self.perception.total_demand_per_circuit
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
        self.beliefs["last_days_off_per_block_in_circuits"].value = (
            self.perception.last_days_off_per_block_in_circuits
        )

        # 14. Update belief about longest sequence  off per block in circuits
        self.beliefs["longest_sequence_off_per_block_in_circuits"].value = (
            self.perception.longest_sequence_off_per_block_in_circuits
        )

        # 15. Update belief about longest sequence  off per block in circuits
        self.beliefs["working_thermoelectrics_amount"].value = (
            self.perception.working_thermoelectrics_amount
        )

        # 16. Update belief about longest sequence  off per block in circuits
        self.beliefs["general_opinion"].value = self.perception.general_opinion

        if self.learn:
            self.learn_new_desires()

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

        self.intentions["meet_demand"].value = self.desires["meet_demand"]
        self.intentions["max_stored_energy"].value = self.desires["max_stored_energy"]
        self.intentions["prioritize_block_importance"].value = self.desires[
            "prioritize_block_importance"
        ]
        self.intentions["prioritize_block_opinion"].value = self.desires[
            "prioritize_block_opinion"
        ]
        self.intentions["prioritize_consecutive_days_off"].value = self.desires[
            "prioritize_consecutive_days_off"
        ]
        self.intentions["prioritize_days_off"].value = self.desires[
            "prioritize_days_off"
        ]

    def get_cost_to_meet_demand_from_thermoelectric_to_block(
        self, thermoelectric_index, block_key, hour, return_sum=True, predicted=True
    ) -> float | tuple[int, int]:

        (circuit_index, block_index) = self.mapper_key_to_circuit_block[block_key]

        circuit_id = self.circuits[circuit_index]
        thermoelectric_id = self.thermoelectrics[thermoelectric_index].id

        distance_cost = self.beliefs["distance_matrix"].value[thermoelectric_index][
            circuit_index
        ]

        if distance_cost < 0:
            raise RuntimeError(
                f"Distance cost from {thermoelectric_id} {block_key}, where {circuit_id, block_index}"
            )

        block: "Block" = self.circuits[circuit_index].blocks[block_index]

        demand: float = (
            block.predicted_demand_per_hour[hour]
            if predicted
            else block.demand_per_hour[hour]
        )

        return (
            demand + distance_cost * demand if return_sum else (distance_cost, demand)
        )

    def generic_objective_function(
        self, complete_distribution: list[list], funcs: callable, params: list
    ) -> float:

        y = 0

        for pi, func in enumerate(funcs):
            y += func(self.perception, complete_distribution) * params[pi]

        return y

    def build_new_perception(
        self, thermoelectrics: list["Thermoelectric"], circuits: list["Circuit"]
    ) -> ChiefElectricCompanyAgentPerception:
        return ChiefElectricCompanyAgentPerception(
            thermoelectrics_id=self.perception.thermoelectrics_id,
            circuits_id=self.perception.circuits_id,
            generation_per_thermoelectric=[t.current_capacity for t in thermoelectrics],
            distance_matrix=self.perception.distance_matrix,
            demand_per_block_in_circuit=[
                (circuit.id, idb, block.demand_per_hour)
                for circuit in circuits
                for idb, block in enumerate(circuit.blocks)
            ],
        )

    # TODO: Refactor to include common factors such as blocks supplied with energy, sum of costs, distances, etc.
    def distribute_energy_to_blocks_from_thermoelectrics(
        self,
        complete_distribution: list[list[int]],
        thermoelectrics: list["Thermoelectric"],
        circuits: list["Circuit"],
    ) -> list[tuple[int, int]]:  # make the distribution and return a flat distribution

        flat_distribution: list[tuple[int, int]] = (
            []
        )  #  block key, thermoelectric index

        for block_key, distribution in enumerate(complete_distribution):

            days_off = []

            (circuit_index, block_index) = self.mapper_key_to_circuit_block[block_key]

            for hour, thermoelectric_index in enumerate(distribution):

                flat_distribution.append((block_key, thermoelectric_index))

                if thermoelectric_index == -1:
                    days_off.append(True)
                    # print('El bloque', block_index, 'del circuito', circuit_index, 'no recibió energía')

                else:
                    days_off.append(False)
                    cost = self.get_cost_to_meet_demand_from_thermoelectric_to_block(
                        thermoelectric_index=thermoelectric_index,
                        block_key=block_key,
                        hour=hour,
                        predicted=False,
                    )

                    thermoelectrics[thermoelectric_index].consume_energy(cost)
                    # print(
                    #     "Termoeléctrica ",
                    #     thermoelectric_index,
                    #     "consumió ",
                    #     cost,
                    #     " y abasteció al bloque ",
                    #     block_index,
                    #     "del circuito ",
                    #     circuit_index,
                    # )

        circuits[circuit_index].blocks[block_index].set_days_distribution(days_off)
        return flat_distribution

    def max_stored_energy_intention_func(
        self,
        perception: "ChiefElectricCompanyAgentPerception",
        complete_distribution: list[list[int]],
    ):
        energy = 0
        distance_percent = 0
        count = 0

        for block_key, distribution in enumerate(complete_distribution):
            for hour, thermoelectric_index in enumerate(distribution):
                if thermoelectric_index != -1:
                    count += 1
                    cost = self.get_cost_to_meet_demand_from_thermoelectric_to_block(
                        thermoelectric_index=thermoelectric_index,
                        block_key=block_key,
                        hour=hour,
                        return_sum=False,
                    )
                    energy += cost[0]
                    distance_percent += cost[1]

        return (
            (1 - (distance_percent * DISTANCE_REGULATOR) / count)
            if energy >= self.beliefs["general_demand"].value
            else 0
        )

    def meet_demand_intention_func(
        self,
        perception: "ChiefElectricCompanyAgentPerception",
        complete_distribution: list[list[int]],
    ):
        energy = 0
        for block_key, distribution in enumerate(complete_distribution):
            for hour, thermoelectric_index in enumerate(distribution):
                if thermoelectric_index != -1:
                    cost = self.get_cost_to_meet_demand_from_thermoelectric_to_block(
                        thermoelectric_index=thermoelectric_index,
                        block_key=block_key,
                        hour=hour,
                        return_sum=False,
                    )
                    energy += cost[0]

        return (
            1
            - max(self.beliefs["general_demand"].value - energy, 0)
            / self.beliefs["general_demand"].value
        )

    def prioritize_block_importance_intention_func(
        self,
        perception: "ChiefElectricCompanyAgentPerception",
        complete_distribution: list[list[int]],
    ):
        total_importance = 0
        for block_key, distribution in enumerate(complete_distribution):
            (circuit_index, block_index) = self.mapper_key_to_circuit_block[block_key]
            on_hours = sum(1 for x in distribution if x >= 0)
            total_importance += (
                on_hours * self.circuits[circuit_index].blocks[block_index].importance
            )

        return total_importance / self.max_importance_of_all_circuits * 24

    def prioritize_block_opinion_intention_func(
        self,
        perception: "ChiefElectricCompanyAgentPerception",
        complete_distribution: list[list[int]],
    ):
        total_opinion = 0

        for block_key, distribution in enumerate(complete_distribution):
            on_hours = sum(1 for x in distribution if x >= 0)
            total_opinion += (
                on_hours
                * self.beliefs["opinion_per_block_in_circuits"].value[block_key][2]
            )

        return total_opinion / max(
            (
                sum(x[2] for x in self.beliefs["opinion_per_block_in_circuits"].value)
                * 24
            ),
            1,
        )

    def prioritize_consecutive_days_off_intention_func(
        self,
        perception: "ChiefElectricCompanyAgentPerception",
        complete_distribution: list[list[int]],
    ):
        total_consecutive_days = 0

        for block_key, distribution in enumerate(complete_distribution):
            on_hours = sum(1 for x in distribution if x >= 0)
            total_consecutive_days += (
                on_hours
                * self.beliefs["longest_sequence_off_per_block_in_circuits"].value[
                    block_key
                ][2]
            )

        return total_consecutive_days / max(
            (
                sum(
                    [
                        x[2]
                        for x in self.beliefs[
                            "longest_sequence_off_per_block_in_circuits"
                        ].value
                    ]
                )
                * 24
            ),
            1,
        )

    def prioritize_days_off_intention_func(
        self,
        perception: "ChiefElectricCompanyAgentPerception",
        complete_distribution: list[list[int]],
    ):
        total_off_days = 0

        for block_key, distribution in enumerate(complete_distribution):
            on_hours = sum(1 for x in distribution if x >= 0)
            total_off_days += (
                on_hours
                * self.beliefs["last_days_off_per_block_in_circuits"].value[block_key][
                    2
                ]
            )

        return total_off_days / max(
            (
                sum(
                    [
                        x[2]
                        for x in self.beliefs[
                            "last_days_off_per_block_in_circuits"
                        ].value
                    ]
                )
                * 24
            ),
            1,
        )

    def execute(self) -> "ChiefElectricCompanyAction":
        intention_executed = []

        intention_map = {
            "max_stored_energy": self.max_stored_energy_intention_func,
            "meet_demand": self.meet_demand_intention_func,
            "prioritize_block_importance": self.prioritize_block_importance_intention_func,
            "prioritize_block_opinion": self.prioritize_block_opinion_intention_func,
            "prioritize_consecutive_days_off": self.prioritize_consecutive_days_off_intention_func,
            "prioritize_days_off": self.prioritize_days_off_intention_func,
        }

        intentions_func = []
        intentions_params = []

        for intention, func in intention_map.items():
            if self.intentions[intention].value:
                self.intentions[intention].value = False
                intention_executed.append(intention)
                intentions_func.append(func)
                intentions_params.append(OBJECTIVE_FUNCTION_INTENTION_PARAMS_WEIGHT)
            else:
                intentions_params.append(
                    OBJECTIVE_FUNCTION_INTENTION_PARAMS_DEFAULT_WEIGHT
                )

        final_distribution, score = genetic_algorithm(
            get_cost_thermoelectric_to_block=self.get_cost_to_meet_demand_from_thermoelectric_to_block,
            capacities=self.beliefs["generation_per_thermoelectric"].value,
            generations=30,
            pop_size=10,
            blocks=len(self.mapper_key_to_circuit_block),
            mutation_rate=0,
            ft=lambda distribution: self.generic_objective_function(
                complete_distribution=distribution,
                funcs=intentions_func,
                params=intentions_params,
            ),
        )

        flat_distribution = self.distribute_energy_to_blocks_from_thermoelectrics(
            complete_distribution=final_distribution,
            thermoelectrics=self.thermoelectrics,
            circuits=self.circuits,
        )

        self.last_date_result = (flat_distribution, score)

        return ChiefElectricCompanyAction(
            meet_demand="meet_demand" in intention_executed,
            prioritize_block_importance="prioritize_block_importance"
            in intention_executed,
            prioritize_consecutive_days_off="prioritize_consecutive_days_off"
            in intention_executed,
            prioritize_days_off="prioritize_days_off" in intention_executed,
            prioritize_block_opinion="prioritize_block_opinion" in intention_executed,
        )

    def action(
        self, perception: "ChiefElectricCompanyAgentPerception"
    ) -> list["ChiefElectricCompanyAction"]:
        self.perception = perception
        self.brf()
        self.generate_desires()
        self.filter_intentions()
        return self.execute()

    def learn_new_desires(self):
        conditions = [
            (
                lambda beliefs: beliefs["general_offer"].value
                - beliefs["general_demand"].value
                > 1000,
                "fully covered system",
            ),
            (
                lambda beliefs: beliefs["general_offer"].value
                - beliefs["general_demand"].value
                < 1000
                and beliefs["general_deficit"].value <= 0,
                "tightly covered system",
            ),
            (
                lambda beliefs: beliefs["general_deficit"].value > 0
                and beliefs["general_deficit"].value <= 1000,
                "almost covered system",
            ),
            (
                lambda beliefs: beliefs["general_deficit"].value > 0
                and beliefs["general_deficit"].value > 1000,
                "not covered system",
            ),
            # TODO: belief general opinion
            (
                lambda beliefs: beliefs["general_opinion"].value > 0.7,
                "good general opinion",
            ),
            (
                lambda beliefs: beliefs["general_opinion"].value >= 0.4
                and beliefs["general_opinion"].value <= 0.7,
                "neutral general opinion",
            ),
            (
                lambda beliefs: beliefs["general_opinion"].value < 0.4,
                "bad general opinion",
            ),
            # TODO: working_thermoelectrics_amount
            (
                lambda beliefs: beliefs["working_thermoelectrics_amount"].value
                / len(beliefs["thermoelectrics_id"].value)
                > 0.7,
                "many thermoelectrics working",
            ),
            (
                lambda beliefs: beliefs["working_thermoelectrics_amount"].value
                / len(beliefs["thermoelectrics_id"].value)
                >= 0.4
                and beliefs["working_thermoelectrics_amount"].value
                / len(beliefs["thermoelectrics_id"].value)
                <= 0.7,
                "half of thermoelectrics working",
            ),
            (
                lambda beliefs: beliefs["working_thermoelectrics_amount"].value
                / len(beliefs["thermoelectrics_id"].value)
                < 0.4,
                "few thermoelectrics working",
            ),
        ]

        valid_cond = []

        for item in conditions:
            if item[0](self.beliefs):
                valid_cond.append(item)

        str_cond = "["
        for item in valid_cond:
            str_cond = str_cond + item[1] + ","
        str_cond = str_cond[:-1] + "]"

        generator = DesireGenerator()
        ans = generator.generate_new_desire(str_cond)

        desires = []
        chosen_cond = []
        condition_description = []

        for item in valid_cond:
            if item[1] in ans:
                condition_description.append(item[1])
                chosen_cond.append(item[0])

        for desire in self.desires.keys():
            if desire in ans:
                desires.append(desire)

        generated_desire = CECAGeneratedDesire(
            id="generated_desire_" + str(len(self.beliefs["all_desires"].value)),
            weight=1,
            desires=desires,
            conditions=chosen_cond,
            condition_description=condition_description,
        )

        self.beliefs["all_desires"].value[generated_desire.id] = generated_desire
        self.beliefs["current_desires"].value.append(generated_desire.id)
