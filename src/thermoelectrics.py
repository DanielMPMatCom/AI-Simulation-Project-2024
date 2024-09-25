from part import *
from people import *
from circuits import *


class Thermoelectric:
    """
    Represents a Thermoelectric plant with multiple parts (Boilers, Coils, SteamTurbine, Generator)
    and provides the electricity generation functionality.
    """
    def __init__(self, parts: list[Part], total_capacity: int) -> None:
        self.parts = parts
        # self.circuits = circuits
        self.total_capacity = total_capacity
        self.update_capacity()

    def update(self):
        """
        Updates the state of all parts in the thermoelectric.
        """
        for part in self.parts:
            part.update()
        self.update_capacity()

    def is_working(self) -> bool:
        """
        Returns True if the thermoelectric is working.
        
        The plant stops working if Coils, SteamTurbine, or Generator are broken or if all the Boilers are Broken.
        """
        broken_boilers = 0
        
        # Check if critical parts are working (Coils, SteamTurbine, Generator) or some of the Boilers are working.
        for part in self.parts:
            if isinstance(part, (Coils, SteamTurbine, Generator)) and not part.is_working():
                return False
            elif isinstance(part, Boiler) and not part.is_working():
                broken_boilers += 1
        
        if broken_boilers == self.get_total_boilers():
            return False
        
        return True

    def update_capacity(self):
        """
        Updates the current capacity of the thermoelectric based on the number of working Boilers.
        """
        working_boilers = self.get_working_boilers()
        if working_boilers > 0:
            self.current_capacity = (working_boilers / self.get_total_boilers()) * self.total_capacity
        else:
            self.current_capacity = 0

    def get_current_offer(self) -> int:
        """
        Returns the current electricity offer (capacity) of the thermoelectric.
        """
        if self.is_working():
            return self.current_capacity
        return 0

    def get_total_boilers(self) -> int:
        """
        Returns the total number of boilers in the thermoelectric plant.
        """
        return sum(1 for part in self.parts if isinstance(part, Boiler))
    
    def get_working_boilers(self) -> int:
        """
        Returns the number of working boilers.
        """
        return sum(1 for part in self.parts if isinstance(part, Boiler) and part.is_working())
        