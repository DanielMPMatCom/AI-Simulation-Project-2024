from src.utils.lognormal import LogNormal
from src.utils.weibull import Weibull


class Part:
    """
    Represents a general part of a thermoelectric plant. Each part has a life expectancy and can be repaired.
    """

    def __init__(self, lognormal: LogNormal, weibull: Weibull) -> None:
        self.lognormal = lognormal
        self.weibull = weibull
        self.remaining_repair_days = None
        self.remaining_life = None
        self.estimated_remaining_life = None
        self.estimated_repair_days = None
        self.planificate_break_date()  # Initialize the part's lifespan

    def update(self):
        """
        Update the part's status, decrementing life or repair days.
        """
        if self.is_working():
            self.remaining_life -= 1

        if self.is_repairing():
            self.remaining_repair_days -= 1
            if self.remaining_repair_days <= 0:
                self.finish_repair()

        if self.remaining_life <= 0 and not self.is_repairing():
            self.repair()

    def repair(self):
        """
        Start the repair process by setting the repair days.
        """
        self.remaining_repair_days = self.lognormal.generate()

    def planificate_break_date(self):
        """
        Plan the date when the part will break based on its life expectancy.
        """
        self.remaining_life = self.weibull.generate()

    def is_repairing(self) -> bool:
        """
        Check if the part is currently under repair.
        """
        return self.remaining_repair_days is not None and self.remaining_repair_days > 0

    def is_working(self) -> bool:
        """
        Check if the part is currently functioning.
        """
        return self.remaining_life is not None and self.remaining_life > 0

    def finish_repair(self):
        """
        Finishes the repair process and reinitialize the part's lifespan.
        """
        self.remaining_repair_days = None
        self.planificate_break_date()
        
    def get_estimate_remaining_life(self):
        """
        Estimates the remaining life of the part based on the current state.
        """
        self.estimated_remaining_life = self.lognormal.generate() if self.is_working() else 0
        return self.estimated_remaining_life
    
    def get_estimated_repair_days(self):
        """
        Estimates the repair days of the part based on the current state.
        """
        self.estimated_repair_days = self.weibull.generate()
        return self.estimated_repair_days
        


class Boiler(Part):
    """
    Represents a Boiler part in the thermoelectric plant.
    """

    def __init__(self, lognormal: LogNormal, weibull: Weibull) -> None:
        Part.__init__(self, lognormal=lognormal, weibull=weibull)


class Coils(Part):
    """
    Represents a Coils part in the thermoelectric plant.
    """

    def __init__(self, lognormal: LogNormal, weibull: Weibull) -> None:
        Part.__init__(self, lognormal=lognormal, weibull=weibull)


class SteamTurbine(Part):
    """
    Represents a SteamTurbine part in the thermoelectric plant.
    """

    def __init__(self, lognormal: LogNormal, weibull: Weibull) -> None:
        Part.__init__(self, lognormal=lognormal, weibull=weibull)


class Generator(Part):
    """
    Represents a Generator part in the thermoelectric plant.
    """

    def __init__(self, lognormal: LogNormal, weibull: Weibull) -> None:
        Part.__init__(self, lognormal=lognormal, weibull=weibull)
