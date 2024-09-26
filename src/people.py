from thermoelectrics import *
from typing import List
import random


class Person:
    """
    Base class representing a person with a name. 
    It serves as a parent class for ThermoelectricAgent, ChiefElectricCompanyAgent, and Citizen.
    """
    def __init__(self, name: str):
        self.name = name
        self.beliefs = {}
        self.desires = []
        self.intentions = []

    def update_beliefs(self):
        """Method to update beliefs of the person."""
        raise NotImplementedError("This method should be implemented by subclasses")

    def update_desires(self):
        """Method to update desires of the person."""
        raise NotImplementedError("This method should be implemented by subclasses")

    def select_intentions(self):
        """Method to update intentions based on desires."""
        raise NotImplementedError("This method should be implemented by subclasses")

    def step(self):
        """A simulation step where the agent updates beliefs, desires, and intentions."""
        raise NotImplementedError("This method should be implemented by subclasses")


class ThermoelectricAgent(Person):
    """
    BDI Agent representing a thermoelectric power plant.
    Responsible for deciding maintenance cycles, repairs, and managing plant operation.
    Inherits from the Person class.
    """
    def __init__(self, name: str, parts: List[Part], max_capacity: float):
        Person.__init__(name)
        self.parts = parts  # Boiler, Coils, SteamTurbine, Generator
        self.max_capacity = max_capacity
        self.current_capacity = max_capacity

    def update_beliefs(self):
        """Updates the beliefs of the agent based on the current state of the plant's parts."""
        working_parts = [part.is_working() for part in self.parts]
        self.beliefs['plant_is_operational'] = all(working_parts)
        self.beliefs['broken_parts'] = [part for part in self.parts if not part.is_working()]
        self.beliefs['current_capacity'] = self.calculate_current_capacity()

    def update_desires(self):
        """Sets the desires of the agent, such as maintaining full capacity and repairing broken parts."""
        self.desires.clear()
        if not self.beliefs['plant_is_operational']:
            self.desires.append('repair_parts')
        else:
            self.desires.append('maintain_capacity')

    def select_intentions(self):
        """Based on the desires, the agent commits to specific actions (intentions)."""
        self.intentions.clear()
        if 'repair_parts' in self.desires:
            self.intentions.append(self.repair_broken_parts)
        if 'maintain_capacity' in self.desires:
            self.intentions.append(self.schedule_maintenance)

    def calculate_current_capacity(self) -> float:
        """Calculates the current capacity of the plant based on operational boilers."""
        working_boilers = [part for part in self.parts if isinstance(part, Boiler) and part.is_working()]
        capacity = (len(working_boilers) / len([p for p in self.parts if isinstance(p, Boiler)])) * self.max_capacity
        return capacity

    def repair_broken_parts(self):
        """Repairs broken parts in the plant."""
        for part in self.beliefs['broken_parts']:
            part.repair()
        self.update_beliefs()

    def schedule_maintenance(self):
        """Schedule maintenance of parts to prevent breakdowns."""
        for part in self.parts:
            if random() > 0.5:  # Randomly decide to maintain parts for now
                part.planificate_break_date()

    def step(self):
        """Executes a simulation step: updates beliefs, desires, and intentions, then acts."""
        self.update_beliefs()
        self.update_desires()
        self.select_intentions()
        for intention in self.intentions:
            intention()


class ChiefElectricCompanyAgent(Person):
    """
    BDI Agent representing the chief of the electric company.
    Responsible for deciding optimal electricity distribution and planning power cuts.
    Inherits from the Person class.
    """
    def __init__(self, name: str, thermoelectrics: List[ThermoelectricAgent], circuits: List[Circuit]):
        Person.__init__(name)
        self.thermoelectrics = thermoelectrics
        self.circuits = circuits

    def update_beliefs(self):
        """Updates the beliefs about the system state (e.g., available generation, circuit demands)."""
        self.beliefs['total_generation'] = sum(plant.calculate_current_capacity() for plant in self.thermoelectrics)
        self.beliefs['total_demand'] = sum(circuit.get_total_demand() for circuit in self.circuits)

    def update_desires(self):
        """Defines desires like balancing generation with demand and avoiding blackouts."""
        self.desires.clear()
        if self.beliefs['total_demand'] > self.beliefs['total_generation']:
            self.desires.append('manage_deficit')
        else:
            self.desires.append('optimize_distribution')

    def select_intentions(self):
        """Based on desires, the agent creates intentions to act upon."""
        self.intentions.clear()
        if 'manage_deficit' in self.desires:
            self.intentions.append(self.plan_power_cuts)
        if 'optimize_distribution' in self.desires:
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


class Citizen(Person):
    """
    Class representing a citizen in a block of a circuit.
    Citizens react to changes in electricity supply, like blackouts or power restoration.
    Inherits from the Person class.
    """
    def __init__(self, name: str, block: Block):
        super().__init__(name)
        self.block = block

    def update_beliefs(self):
        """Citizens update their beliefs based on the status of electricity in their block."""
        self.beliefs['has_power'] = self.block.has_power()

    def update_desires(self):
        """Citizens desire uninterrupted power supply."""
        self.desires.clear()
        if not self.beliefs['has_power']:
            self.desires.append('restore_power')

    def select_intentions(self):
        """Citizens' intentions reflect their need for power restoration."""
        self.intentions.clear()
        if 'restore_power' in self.desires:
            self.intentions.append(self.complain_to_authorities)

    def complain_to_authorities(self):
        """Action taken when power is out for too long: complain."""
        print(f"{self.name} is complaining about power outage in {self.block.name}")

    def step(self):
        """Executes a simulation step for the citizen: updates beliefs, desires, and intentions."""
        self.update_beliefs()
        self.update_desires()
        self.select_intentions()
        for intention in self.intentions:
            intention()
