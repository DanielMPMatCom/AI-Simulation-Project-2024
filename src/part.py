from utils.lognormal import LogNormal
from utils.weibull import Weibull


class Part:
    """
    Represents a general part of a thermoelectric plant. Each part has a life expectancy and can be repaired.
    """
    def __init__(self, lognormal: LogNormal, weibull: Weibull) -> None:
        self.lognormal = lognormal
        self.weibull = weibull
        self.remained_repairs_days = None
        self.remained_life = None
        self.planificate_break_date()  # Initialize the part's lifespan

    def update(self):
        """
        Update the part's status, decrementing life or repair days.
        """
        if self.is_working():
            self.remained_life -= 1

        if self.is_repairing():
            self.remained_repairs_days -= 1
            if self.remained_repairs_days <= 0:
                self.finish_repair()

        if self.remained_life <= 0 and not self.is_repairing():
            self.repair()

    def repair(self):
        """
        Start the repair process by setting the repair days.
        """
        self.remained_repairs_days = self.lognormal.generate()

    def planificate_break_date(self):
        """
        Plan the date when the part will break based on its life expectancy.
        """
        self.remained_life = self.weibull.generate()

    def is_repairing(self) -> bool:
        """
        Check if the part is currently under repair.
        """
        return self.remained_repairs_days is not None and self.remained_repairs_days > 0

    def is_working(self) -> bool:
        """
        Check if the part is currently functioning.
        """
        return self.remained_life is not None and self.remained_life > 0

    def finish_repair(self):
        """
        Finishes the repair process and reinitialize the part's lifespan.
        """
        self.remained_repairs_days = None
        self.planificate_break_date()


class Boiler(Part):
    """
    Represents a Boiler part in the thermoelectric plant.
    """
    def __init__(self, lognormal: LogNormal, weibull: Weibull) -> None:
        super().__init__(lognormal=lognormal, weibull=weibull)


class Coils(Part):
    """
    Represents a Coils part in the thermoelectric plant.
    """
    def __init__(self, lognormal: LogNormal, weibull: Weibull) -> None:
        super().__init__(lognormal=lognormal, weibull=weibull)


class SteamTurbine(Part):
    """
    Represents a SteamTurbine part in the thermoelectric plant.
    """
    def __init__(self, lognormal: LogNormal, weibull: Weibull) -> None:
        super().__init__(lognormal=lognormal, weibull=weibull)


class Generator(Part):
    """
    Represents a Generator part in the thermoelectric plant.
    """
    def __init__(self, lognormal: LogNormal, weibull: Weibull) -> None:
        super().__init__(lognormal=lognormal, weibull=weibull)
