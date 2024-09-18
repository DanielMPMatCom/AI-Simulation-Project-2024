from utils.lognormal import*
from utils.weibull import*

class Part:
    def __init__(self, lognormal : LogNormal, weibull : Weibull) -> None:
        self.lognormal = lognormal
        self.weibull = weibull
class Boiler(Part):
    def __init__(self, lognormal : LogNormal, weibull : Weibull) -> None:
        Part.__init__(self, lognormal=lognormal, weibull=weibull)
class Coils(Part):
    def __init__(self, lognormal : LogNormal, weibull : Weibull) -> None:
        Part.__init__(self, lognormal=lognormal, weibull=weibull) 
class SteamTurbine(Part):
    def __init__(self, lognormal : LogNormal, weibull : Weibull) -> None:
        Part.__init__(self, lognormal=lognormal, weibull=weibull)
class Generator(Part):
    def __init__(self, lognormal : LogNormal, weibull : Weibull) -> None:
        Part.__init__(self, lognormal=lognormal, weibull=weibull)