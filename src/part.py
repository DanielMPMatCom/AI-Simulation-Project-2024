from src.utils.lognormal import LogNormal
from src.utils.weibull import Weibull
from src.simulation_constants import (
    RANDOM,
    HURRY_REPAIR_SHAPE_MAX,
    HURRY_REPAIR_SCALE_MIN,
    HURRY_REPAIR_SCALE_MAX,
    HURRY_REPAIR_SHAPE_MIN,
)


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

        self.plan_break_date()

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

            if self.remaining_repair_days <= -1:
                raise RuntimeError("Remaining repair days should be greater than 0" + str(self.remaining_repair_days))

            if self.estimated_repair_days <= -1:
                raise RuntimeError("Estimated repair days should be greater than 0" + str(self.estimated_repair_days))

            self.remaining_repair_days -= 1
            self.estimated_repair_days -= 1

            if self.remaining_repair_days <= 0:
                self.finish_repair()

    def hurry_repair(self):
        if self.is_repairing():
            self.finish_repair(hard=True)

        else:
            raise RuntimeError("Hurry repair in part that isn't repairing")

    def maintenance(self):
        """
        Start the maintenance process by setting the repair days.
        """
        if (
            self.remaining_repair_days and self.remaining_repair_days >= 0
        ) or not self.is_working():
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

    def plan_break_date(self, hard=False, was_a_maintenance=False):
        """
        Plan the date when the part will break based on its life expectancy.
        """
        shape = 0
        scale = 0

        if hard:
            shape = RANDOM.uniform(HURRY_REPAIR_SHAPE_MIN, HURRY_REPAIR_SHAPE_MAX)
            scale = self.weibull.scale + RANDOM.uniform(
                HURRY_REPAIR_SCALE_MIN, HURRY_REPAIR_SCALE_MAX
            )

        elif was_a_maintenance:
            shape = self.weibull.shape + 1
            scale = self.weibull.scale

        else:
            shape = self.weibull.shape
            scale = self.weibull.scale

        self.remaining_life = self.weibull.generate_with_params(
            scale=scale, shape=shape
        )

        count = 0
        self.estimated_remaining_life = 0
        for _ in range(1000):
            count += 1
            value = self.weibull.generate_with_params(scale=scale, shape=shape)
            self.estimated_remaining_life += value
        self.estimated_remaining_life /= count

    def set_repairing(self, value: bool):
        if value and (
            not self.remaining_repair_days or self.remaining_repair_days <= 0
        ):
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

    def finish_repair(self, hard=False):
        """
        Finishes the repair process and reinitialize the part's lifespan.
        """
        self.remaining_repair_days = 0
        self.estimated_repair_days = 0

        was_maintenance_process = self.maintenance_process
        self.maintenance_process = False

        self.set_repairing(False)
        self.plan_break_date(was_a_maintenance=was_maintenance_process, hard=hard)

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
