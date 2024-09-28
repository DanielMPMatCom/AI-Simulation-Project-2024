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