from thermoelectrics import*

class People:
    def __init__(self) -> None:
        pass
    
class Planner(People):
    def __init__(self, thermoelectric : Thermoelectric) -> None:
        self.thermoelectric = thermoelectric
    
class Citizen(People):
    def __init__(self) -> None:
        pass
    
    def generate_report(self, block_state):
        pass