from people import Citizen


class Circuit:
    def __init__(self) -> None:
        self.blocks: list[Block] = []

    def update(self):
        for block in self.blocks:
            block.update()


class Block:
    def __init__(self) -> None:
        self.citizens: list[Citizen] = []
        self.history_report: list[str] = []
        self.off_hours: tuple[int, int] = (0, 0)
        self.demand_per_hour: list[float] = []

    def update(self):
        pass

    def get_block_report(self):
        for c in self.citizens:
            c.generate_report(self.off_hours)

    def get_consumed_energy_today(self):
        return sum(self.demand_per_hour[: self.off_hours[0]]) + sum(
            self.demand_per_hour[self.off_hours[1] :]
        )
