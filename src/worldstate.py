from src.circuits import Circuit
from src.thermoelectrics import Thermoelectric


class WorldState:
    def __init__(
        self,
        circuits: list["Circuit"],
        thermoelectrics: list["Thermoelectric"],
        distance_matrix: list[list[float]],
        get_circuit_importance: callable,
        get_block_importance: callable,
    ) -> None:

        self.circuits = circuits
        self.thermoelectrics = thermoelectrics
        self.distance_matrix = distance_matrix
        self.get_circuit_importance = get_circuit_importance
        self.get_block_importance = get_block_importance
        self.update()

        self.thermoelectrics_id = [t.id for t in self.thermoelectrics]
        self.circuits_id = [c.id for c in self.circuits]
        self.predicted_total_demand_per_circuit = [
            sum([block.predicted_total_demand for block in circuit.blocks])
            for circuit in self.circuits
        ]

        self.mapper_key_to_circuit_block = self.make_mapper_block_and_circuits(
            self.circuits
        )

    def basic_info_str(self):
        properties = f""" 
        General Demand: {self.general_demand},
        General Offer: {self.general_offer},
        General Deficit: {self.general_deficit},
        General Satisfaction: {self.general_satisfaction},
        """

        return properties

    def __str__(self):

        tab = " " * 4

        representation = ""

        representation += f"General offer: {self.general_offer}\n"
        representation += f"General demand: {self.general_demand}\n"
        representation += f"General deficit: {self.general_deficit}\n"
        representation += f"General satisfaction: {self.general_satisfaction}\n"

        for ti, thermoelectric in enumerate(self.thermoelectrics):
            representation += f"Thermoelectric: {thermoelectric.id}, Generation: {self.generation_per_thermoelectric[ti]}MW\n"

        base = 0
        for ci, circuit in enumerate(self.circuits):
            representation += "\n"
            representation += f"Circuit: {circuit.id}, Satisfaction: {self.satisfaction_per_circuit[ci]}, Importance: {self.circuits_importance[ci]}, Industrialization: {self.industrialization_per_circuit[ci]}\n"
            for bi, block in enumerate(circuit.blocks):
                representation += f"{tab}Block: {bi}, Satisfaction: {self.opinion_per_block_in_circuits[base + bi]}, Importance: {self.importance_per_block_in_circuits[base + bi]}, Demand: {self.demand_per_block_in_circuits[base + bi]}\n"
                representation += f"{tab}Last day off: {self.last_days_off_per_block_in_circuits[base + bi]}, Longest sequence off: {self.longest_sequence_off_per_block_in_circuits[base + bi]}\n"
            base += len(circuit.blocks)

        return representation

    def update_only_thermoelectric_stats(self, thermoelectric_index):
        old_generation = self.generation_per_thermoelectric[thermoelectric_index]
        self.generation_per_thermoelectric[thermoelectric_index] = self.thermoelectrics[
            thermoelectric_index
        ].current_capacity
        self.general_offer += (
            self.generation_per_thermoelectric[thermoelectric_index] - old_generation
        )

    def update(self):
        self.generation_per_thermoelectric = [
            t.current_capacity for t in self.thermoelectrics
        ]

        self.demand_per_block_in_circuits = [
            (circuit.id, block_id, block.demand_per_hour)
            for circuit in self.circuits
            for block_id, block in enumerate(circuit.blocks)
        ]

        self.predicted_demand_per_block_in_circuits = [
            (circuit.id, block_id, block.predicted_demand_per_hour)
            for circuit in self.circuits
            for block_id, block in enumerate(circuit.blocks)
        ]

        self.circuits_importance = [
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

        self.citizens_per_block_in_circuit = [
            (circuit.id, block_id, block.citizens.amount)
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

        self.general_offer = sum(
            [thermoelectric.current_capacity for thermoelectric in self.thermoelectrics]
        )

        self.general_demand = sum(
            [
                sum(block.get_predicted_consume_for_today() for block in circuit.blocks)
                for circuit in self.circuits
            ]
        )

        self.general_deficit = max(self.general_demand - self.general_offer, 0)
        self.general_satisfaction = self.get_general_satisfaction()

    def get_general_satisfaction(self):  # TODO : TOLEDO MUST REVIEW THIS

        total_importance: float = 0
        total_satisfaction: float = 0
        for circuit in self.circuits:
            total_satisfaction += circuit.importance * circuit.circuit_satisfaction
            total_importance += circuit.importance

        return total_satisfaction / total_importance

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
            circuits_satisfaction[circuit.id] = circuit.circuit_satisfaction

        return circuits_satisfaction

    def make_mapper_block_and_circuits(self, circuits: list["Circuit"]):
        mapper = {}
        key = 0

        for ci, c in enumerate(circuits):
            for block_id in range(len(c.blocks)):
                mapper[key] = (ci, block_id)
                key += 1

        return mapper
