from src.utils.lognormal import LogNormal
from src.utils.weibull import Weibull
from src.simulation_constants import RANDOM, HURRY_REPAIR_ALPHA


class Part:
    """
    Represents a general part of a thermoelectric plant. Each part has a life expectancy and can be repaired.
    """

    def __init__(self, lognormal: "LogNormal", weibull: "Weibull") -> None:
        self.lognormal = lognormal
        self.weibull = weibull

        self.remaining_repair_days = None
        self.remaining_life = None

        self.estimated_remaining_life = None
        self.estimated_repair_days = None

        self.maintenance_process = False
        self.repairing = False

        self.plan_break_date()  # Initialize the part's lifespan

    def __str__(self):
        return f"""Part: {self.__class__.__name__},
            Repairing: {self.is_repairing()},
            Working: {self.is_working()},
            Maintenance: {self.maintenance_process_was_started()},
            Remaining life: {self.remaining_life},
            Remaining repair days: {self.remaining_repair_days},
            Estimated remaining life: {self.estimated_remaining_life},
            Estimated repair days: {self.estimated_repair_days}"""

    def update(self):
        """
        Update the part's status, decrementing life or repair days.
        """
        if self.is_working():
            self.remaining_life -= 1
            self.estimated_remaining_life -= 1

        if self.is_repairing():
            self.remaining_repair_days -= 1
            self.estimated_repair_days -= 1

            if self.remaining_repair_days <= 0:
                self.finish_repair()

    def hurry_repair(self):
        if self.is_repairing():
            self.remaining_repair_days = 0
            self.estimated_repair_days = 0
            self.plan_break_date(hard=True)

        else:
            raise RuntimeError("Hurry repair in part that isn't repairing")

    def maintenance(self):
        """
        Start the maintenance process by setting the repair days.
        """
        if self.remaining_repair_days >= 0 or not self.is_working():
            raise RuntimeError(
                "Maintenance process, but the part was in repair process"
            )

        self.remaining_life = 0
        self.estimated_remaining_life = 0

        self.set_repairing(True)
        self.maintenance_process = True

        self.remaining_repair_days = self.lognormal.generate_with_params(
            mu=self.lognormal.mu * 4 / 5, sigma=self.lognormal.sigma * 4 / 5
        )

        count = 0
        self.estimated_repair_days = 0
        for _ in range(1000):
            count += 1
            self.estimated_repair_days += self.lognormal.generate_with_params(
                mu=self.lognormal.mu * 4 / 5, sigma=self.lognormal.sigma * 4 / 5
            )
        self.estimated_repair_days /= count

    def repair(self):
        """
        Start the repair process by setting the repair days.
        """
        if self.is_working():
            raise RuntimeError("Repair process, but the part is working")

        self.remaining_repair_days = self.lognormal.generate()

        count = 0
        self.estimated_repair_days = 0
        for _ in range(1000):
            count += 1
            self.estimated_repair_days += self.lognormal.generate()
        self.estimated_repair_days /= count

    def plan_break_date(self, hard=False):
        """
        Plan the date when the part will break based on its life expectancy.
        """
        self.remaining_life = (
            self.weibull.generate()
            if not hard
            else self.weibull.generate_with_params(
                alpha=RANDOM.uniform(0, HURRY_REPAIR_ALPHA), scale=self.weibull.scale
            )
        )

        count = 0
        self.estimated_remaining_life = 0
        for _ in range(1000):
            count += 1
            self.estimated_remaining_life += (
                self.weibull.generate()
                if not hard
                else self.weibull.generate_with_params(
                    alpha=RANDOM.uniform(0, HURRY_REPAIR_ALPHA),
                    scale=self.weibull.scale,
                )
            )
        self.estimated_remaining_life /= count

    def set_repairing(self, value: bool):
        if value and self.remaining_repair_days <= 0:
            self.repair()
        self.repairing = value

    def is_repairing(self) -> bool:
        """
        Check if the part is currently under repair.
        """
        return self.repairing

    def is_currently_receiving_maintenance(self):
        return self.is_repairing() and self.maintenance_process

    def maintenance_process_was_started(self) -> bool:
        return self.maintenance_process

    def is_working(self) -> bool:
        """
        Check if the part is currently functioning.
        """
        return self.remaining_life is not None and self.remaining_life > 0

    def finish_repair(self):
        """
        Finishes the repair process and reinitialize the part's lifespan.
        """
        self.maintenance_process = False
        self.set_repairing(False)
        self.plan_break_date()

    def get_estimate_remaining_life(self):
        """
        Estimates the remaining life of the part based on the current state.
        """

        return self.estimated_remaining_life if self.is_working() else 0


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
