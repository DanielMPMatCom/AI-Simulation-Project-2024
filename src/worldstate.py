from src.circuits import Circuit
from src.thermoelectrics import Thermoelectric

class WorldState:
    def __init__(self, circuits:list[Circuit], thermoelectrics:list[Thermoelectric]) -> None:
        
        self.circuits = circuits
        self.thermoelectrics = thermoelectrics

        self.update()

    def update(self):

        self.total_offer = sum([thermoelectric.current_capacity for thermoelectric in self.thermoelectrics])
        self.total_demand = sum([(block.get_consumed_energy_today for block in circuit.blocks) for circuit in self.circuits])
        self.total_deficit = min(self.total_demand - self.total_offer)
        self.general_satisfaction = self.get_general_satisfaction()

    def get_general_satisfaction(self):
        
        total_industrialization:float = 0
        total_importance:float = 0
        for circuit in self.circuits:
            total_importance += circuit.industrialization * circuit.get_circuit_satisfaction
            total_industrialization += circuit.industrialization

        return total_importance / total_industrialization
    
    def get_block_satisfaction(self):

        individual_satisfaction = {}
        for circuit in self.circuits:
            for block_id in range(len(circuit.blocks)):
                individual_satisfaction[(circuit.id, block_id)] = circuit.blocks[block_id].get_block_opinion()

        return individual_satisfaction
    
    def get_circuit_satisfaction(self):

        circuits_satisfaction = {}
        for circuit in self.circuits:
            circuit[circuit.id] = circuit.circuit_satisfaction

        return circuits_satisfaction
        