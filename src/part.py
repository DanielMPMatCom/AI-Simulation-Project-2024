from utils.lognormal import *
from utils.weibull import *


class Part:
    def __init__(self, lognormal: LogNormal, weibull: Weibull) -> None:
        self.lognormal = lognormal
        self.weibull = weibull
        self.remaind_repairs_days = None
        self.remaind_life = None

    def update(self):
        if self.is_working():
            self.remaind_life -= 1

        if self.is_reparing():
            self.remaind_repairs_days -= 1
            if self.remaind_life <= 0:
                self.planificate_break_date()

    def repair(self):
        self.remaind_repairs_days = self.lognormal.generate()
        return

    def planificate_break_date(self):
        self.remaind_life = self.weibull.generate()
        return

    def is_reparing(self) -> bool:
        return self.remaind_repairs_days > 0

    def is_working(self) -> bool:
        return self.remaind_life > 0


class Boiler(Part):
    def __init__(self, lognormal: LogNormal, weibull: Weibull) -> None:
        Part.__init__(self, lognormal=lognormal, weibull=weibull)


class Coils(Part):
    def __init__(self, lognormal: LogNormal, weibull: Weibull) -> None:
        Part.__init__(self, lognormal=lognormal, weibull=weibull)


class SteamTurbine(Part):
    def __init__(self, lognormal: LogNormal, weibull: Weibull) -> None:
        Part.__init__(self, lognormal=lognormal, weibull=weibull)


class Generator(Part):
    def __init__(self, lognormal: LogNormal, weibull: Weibull) -> None:
        Part.__init__(self, lognormal=lognormal, weibull=weibull)
