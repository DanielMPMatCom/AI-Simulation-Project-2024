from src.circuits import *
from src.thermoelectrics import *


class WorldState:
    def __init__(
        self,
        circuits: list['Circuit'],
        thermoelectrics: list['Thermoelectric'],
        distance_template: list[tuple[str, str, list[str]]],
        get_circuit_importance: callable,
        get_block_importance: callable,
    ) -> None:

        self.circuits = circuits
        self.thermoelectrics = thermoelectrics
        self.distance_template = [
            (t_id, c_id, cost) for (t_id, c_id, cost, _) in distance_template
        ]
        self.get_circuit_importance = get_circuit_importance
        self.get_block_importance = get_block_importance

        self.update()

    def update(self):
        self.generation_per_thermoelectric = [
            t.current_capacity for t in self.thermoelectrics
        ]

        self.demand_per_block_in_circuits = [
            (circuit.id, block_id, block.demand_per_hour)
            for circuit in self.circuits
            for block_id, block in enumerate(circuit.blocks)
        ]

        self.total_demand_per_circuits = [
            sum([block.demand_per_hour for block in circuit.blocks])
            for circuit in self.circuits
        ]

        self.general_demand = sum(self.total_demand_per_circuits)

        self.general_deficit = self.general_demand - sum(
            [t.current_capacity for t in self.thermoelectrics]
        )

        self.importance_circuit = [
            self.get_circuit_importance(circuit) for circuit in self.circuits
        ]

        self.importance_per_block_in_circuits = [
            (circuit.id, block_id, self.get_block_importance(block))
            for circuit in self.circuits
            for block_id, block in enumerate(circuit.blocks)
        ]

        self.opinion_per_block_in_circuits = [
            (circuit.id, block_id, block.get_block_opinion())
            for circuit in self.circuits
            for block_id, block in enumerate(circuit.blocks)
        ]

        self.satisfaction_per_circuit = [
            circuit.circuit_satisfaction for circuit in self.circuits
        ]

        self.industrialization_per_circuit = [
            circuit.industrialization for circuit in self.circuits
        ]

        self.last_days_off_per_block_in_circuits = [
            (circuit.id, block_id, block.last_days_off())
            for circuit in self.circuits
            for block_id, block in enumerate(circuit.blocks)
        ]

        self.longest_sequence_off_per_block_in_circuits = [
            (circuit.id, block_id, block.longest_sequence_of_days_off())
            for circuit in self.circuits
            for block_id, block in enumerate(circuit.blocks)
        ]

        self.total_offer = sum(
            [thermoelectric.current_capacity for thermoelectric in self.thermoelectrics]
        )
        self.total_demand = sum(
            [
                (block.get_consumed_energy_today for block in circuit.blocks)
                for circuit in self.circuits
            ]
        )
        self.total_deficit = min(self.total_demand - self.total_offer)
        self.general_satisfaction = self.get_general_satisfaction()

    def get_general_satisfaction(self):

        total_industrialization: float = 0
        total_importance: float = 0
        for circuit in self.circuits:
            total_importance += circuit.industrialization * circuit.circuit_satisfaction
            total_industrialization += circuit.industrialization

        return total_importance / total_industrialization

    def get_block_satisfaction(self):

        individual_satisfaction = {}
        for circuit in self.circuits:
            for block_id in range(len(circuit.blocks)):
                individual_satisfaction[(circuit.id, block_id)] = circuit.blocks[
                    block_id
                ].get_block_opinion()

        return individual_satisfaction

    def get_circuit_satisfaction(self):

        circuits_satisfaction = {}
        for circuit in self.circuits:
            circuit[circuit.id] = circuit.circuit_satisfaction

        return circuits_satisfaction
