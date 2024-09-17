from people import Citizen

class Circuit:
    def __init__(self) -> None:
        self.blocks : list[Block] = []
    
class Block:
    def __init__(self) -> None:
        self.citizens : list[Citizen]= []
        self.history_report : list[str] = []
        self.block_state : tuple[int, int] = (0, 0)
        self.demand_per_hour : list[float] = []
        
    def get_block_report(self):
        for c in self.citizens:
            c.generate_report(self.block_state)