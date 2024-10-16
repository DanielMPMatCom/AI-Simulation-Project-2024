from src.part import Coils, Boiler, SteamTurbine, Generator, Part
from src.utils.lognormal import LogNormal
from src.utils.weibull import Weibull
from src.simulation_constants import (
    RANDOM,
    BOILER_PART_WEIBULL_SCALE_MAX,
    BOILER_PART_WEIBULL_SCALE_MIN,
    BOILER_PART_WEIBULL_SHAPE_MAX,
    BOILER_PART_WEIBULL_SHAPE_MIN,
    BOILER_PART_LOGNORMAL_MEAN_MAX,
    BOILER_PART_LOGNORMAL_MEAN_MIN,
    BOILER_PART_LOGNORMAL_DEVIATION_MAX,
    BOILER_PART_LOGNORMAL_DEVIATION_MIN,
    COILS_PART_LOGNORMAL_DEVIATION_MAX,
    COILS_PART_LOGNORMAL_DEVIATION_MIN,
    COILS_PART_LOGNORMAL_MEAN_MAX,
    COILS_PART_LOGNORMAL_MEAN_MIN,
    COILS_PART_WEIBULL_SCALE_MAX,
    COILS_PART_WEIBULL_SCALE_MIN,
    COILS_PART_WEIBULL_SHAPE_MAX,
    COILS_PART_WEIBULL_SHAPE_MIN,
    boiler_amount_for_capacity,
    STEAM_TURBINE_PART_LOGNORMAL_DEVIATION_MAX,
    STEAM_TURBINE_PART_LOGNORMAL_DEVIATION_MIN,
    STEAM_TURBINE_PART_LOGNORMAL_MEAN_MAX,
    STEAM_TURBINE_PART_LOGNORMAL_MEAN_MIN,
    STEAM_TURBINE_PART_WEIBULL_SCALE_MAX,
    STEAM_TURBINE_PART_WEIBULL_SCALE_MIN,
    STEAM_TURBINE_PART_WEIBULL_SHAPE_MAX,
    STEAM_TURBINE_PART_WEIBULL_SHAPE_MIN,
    GENERATOR_PART_LOGNORMAL_DEVIATION_MAX,
    GENERATOR_PART_LOGNORMAL_DEVIATION_MIN,
    GENERATOR_PART_LOGNORMAL_MEAN_MAX,
    GENERATOR_PART_LOGNORMAL_MEAN_MIN,
    GENERATOR_PART_WEIBULL_SCALE_MAX,
    GENERATOR_PART_WEIBULL_SCALE_MIN,
    GENERATOR_PART_WEIBULL_SHAPE_MAX,
    GENERATOR_PART_WEIBULL_SHAPE_MIN,
)


class Thermoelectric:
    """
    Represents a Thermoelectric plant with multiple parts (Boilers, Coils, SteamTurbine, Generator)
    and provides the electricity generation functionality.
    """

    def __init__(self, id, total_capacity: int) -> None:
        self.id = id
        self.parts: list["Part"] = []
        self.total_capacity = total_capacity
        self.current_capacity = 0
        self.stored_energy = 0
        self.create_parts()
        self.update_capacity()

    def __str__(self):
        properties = f"""
            id: {self.id},
            total_capacity: {self.total_capacity},
            current_capacity: {self.current_capacity},
            stored_energy: {self.stored_energy},
            parts: [
            {chr(10).join(str(part) for part in self.parts)}
            ],
        """
        return properties

    def create_parts(self):
        """
        Creates and initializes the parts of the thermoelectric plant.
        This includes Boilers, Coils, SteamTurbine, and Generator.
        """
        boiler_amount = boiler_amount_for_capacity(self.total_capacity)

        created_parts = []

        for _ in range(boiler_amount):
            created_parts.append(self.create_boiler())

        created_parts.append(self.create_generator())
        created_parts.append(self.create_coils())
        created_parts.append(self.create_steam_turbine())
        self.parts = created_parts

    def create_lognormal_and_weibull(
        self,
        mean_min: float,
        mean_max: float,
        deviation_min: float,
        deviation_max: float,
        scale_min: float,
        scale_max: float,
        shape_min: float,
        shape_max: float,
    ) -> tuple["LogNormal", "Weibull"]:
        """
        Creates LogNormal and Weibull distributions with the given parameters.

        Parameters:
        mean_min (float): Minimum mean value for the LogNormal distribution.
        mean_max (float): Maximum mean value for the LogNormal distribution.
        deviation_min (float): Minimum deviation value for the LogNormal distribution.
        deviation_max (float): Maximum deviation value for the LogNormal distribution.
        scale_min (float): Minimum scale value for the Weibull distribution.
        scale_max (float): Maximum scale value for the Weibull distribution.
        shape_min (float): Minimum shape value for the Weibull distribution.
        shape_max (float): Maximum shape value for the Weibull distribution.

        Returns:
        tuple[LogNormal, Weibull]: A tuple containing the created LogNormal and Weibull distributions.
        """

        log_normal = LogNormal(
            mu=RANDOM.uniform(mean_min, mean_max),
            sigma=RANDOM.uniform(deviation_min, deviation_max),
        )

        weibull = Weibull(
            scale=RANDOM.uniform(scale_min, scale_max),
            shape=RANDOM.uniform(shape_min, shape_max),
        )
        return log_normal, weibull

    def create_steam_turbine(self) -> "SteamTurbine":
        """
        Creates a SteamTurbine part for the thermoelectric plant.

        Returns:
            SteamTurbine: The created SteamTurbine part.
        """
        log_normal, weibull = self.create_lognormal_and_weibull(
            STEAM_TURBINE_PART_LOGNORMAL_MEAN_MIN,
            STEAM_TURBINE_PART_LOGNORMAL_MEAN_MAX,
            STEAM_TURBINE_PART_LOGNORMAL_DEVIATION_MIN,
            STEAM_TURBINE_PART_LOGNORMAL_DEVIATION_MAX,
            STEAM_TURBINE_PART_WEIBULL_SCALE_MIN,
            STEAM_TURBINE_PART_WEIBULL_SCALE_MAX,
            STEAM_TURBINE_PART_WEIBULL_SHAPE_MIN,
            STEAM_TURBINE_PART_WEIBULL_SHAPE_MAX,
        )
        return SteamTurbine(log_normal, weibull)

    def create_generator(self) -> "Generator":
        """
        Creates a Generator part for the thermoelectric plant.

        Returns:
            Generator: The created Generator part.
        """
        log_normal, weibull = self.create_lognormal_and_weibull(
            GENERATOR_PART_LOGNORMAL_MEAN_MIN,
            GENERATOR_PART_LOGNORMAL_MEAN_MAX,
            GENERATOR_PART_LOGNORMAL_DEVIATION_MIN,
            GENERATOR_PART_LOGNORMAL_DEVIATION_MAX,
            GENERATOR_PART_WEIBULL_SCALE_MIN,
            GENERATOR_PART_WEIBULL_SCALE_MAX,
            GENERATOR_PART_WEIBULL_SHAPE_MIN,
            GENERATOR_PART_WEIBULL_SHAPE_MAX,
        )
        return Generator(log_normal, weibull)

    def create_coils(self) -> "Coils":
        """
        Creates a Coils part for the thermoelectric plant.

        Returns:
            Coils: The created Generator part.
        """
        log_normal, weibull = self.create_lognormal_and_weibull(
            COILS_PART_LOGNORMAL_MEAN_MIN,
            COILS_PART_LOGNORMAL_MEAN_MAX,
            COILS_PART_LOGNORMAL_DEVIATION_MIN,
            COILS_PART_LOGNORMAL_DEVIATION_MAX,
            COILS_PART_WEIBULL_SCALE_MIN,
            COILS_PART_WEIBULL_SCALE_MAX,
            COILS_PART_WEIBULL_SHAPE_MIN,
            COILS_PART_WEIBULL_SHAPE_MAX,
        )

        return Coils(log_normal, weibull)

    def create_boiler(self) -> "Boiler":
        """
        Creates a Boiler part for the thermoelectric plant.

        Returns:
            Boiler: The created Generator part.
        """
        log_normal, weibull = self.create_lognormal_and_weibull(
            BOILER_PART_LOGNORMAL_MEAN_MIN,
            BOILER_PART_LOGNORMAL_MEAN_MAX,
            BOILER_PART_LOGNORMAL_DEVIATION_MIN,
            BOILER_PART_LOGNORMAL_DEVIATION_MAX,
            BOILER_PART_WEIBULL_SCALE_MIN,
            BOILER_PART_WEIBULL_SCALE_MAX,
            BOILER_PART_WEIBULL_SHAPE_MIN,
            BOILER_PART_WEIBULL_SHAPE_MAX,
        )

        return Boiler(log_normal, weibull)

    def update(self):
        """
        Updates the state of all parts in the thermoelectric.
        """
        self.stored_energy = min(
            max(self.current_capacity, 0), self.total_capacity * 1/20
        )

        for part in self.parts:
            part.update()

        self.update_capacity()

        self.current_capacity += self.stored_energy

    def get_total_broken_boilers(self) -> int:
        """
        Returns the total number of broken boilers in the thermoelectric plant.

        A boiler is considered broken if it is an instance of the Boiler class and its
        `is_working` method returns False.

        Returns:
            int: The number of broken boilers.
        """
        broken_boilers = 0

        for part in self.parts:
            if isinstance(part, Boiler) and not part.is_working():
                broken_boilers += 1

        return broken_boilers

    def is_default_critical_part(self, part: "Part") -> bool:
        """
        Determines if a given part is a default critical part of the thermoelectric plant.

        Parameters:
        part (Part): The part to check.

        Returns:
        bool: True if the part is a default critical part (Coils, SteamTurbine, Generator), False otherwise.
        """
        return isinstance(part, (Coils, SteamTurbine, Generator))

    def is_working(self) -> bool:
        """
        Returns True if the thermoelectric is working.

        The plant stops working if Coils, SteamTurbine, or Generator are broken or if all the Boilers are Broken.
        """
        # Check if critical parts are working (Coils, SteamTurbine, Generator) or some of the Boilers are working.
        for part in self.parts:
            if self.is_default_critical_part(part) and not part.is_working():
                return False

        if self.get_total_broken_boilers() == self.get_total_boilers():
            return False

        return True

    def update_capacity(self):
        """
        Updates the current capacity of the thermoelectric based on the number of working Boilers.
        """
        working_boilers = self.get_working_boilers()

        if working_boilers > 0:
            self.current_capacity = (
                working_boilers / self.get_total_boilers()
            ) * self.total_capacity

        else:
            self.current_capacity = 0

        return self.current_capacity

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
        return sum(
            1 for part in self.parts if isinstance(part, Boiler) and part.is_working()
        )

    def get_working_parts(self) -> list["Part"]:
        """
        Returns a list of working parts in the thermoelectric.
        """
        return [part for part in self.parts if part.is_working()]

    def get_broken_parts(self) -> list["Part"]:
        """
        Returns a list of broken parts in the thermoelectric.
        """
        return [part for part in self.parts if not part.is_working()]

    def get_parts_status(self):
        """
        Retrieves the status of all parts.

        Returns:
            list of tuple: A list of tuples where each tuple contains:
                - bool: The working status of the part.
                - float: The estimated remaining life of the part.
        """
        return [
            (part, part.is_working(), part.estimated_remaining_life)
            for part in self.parts
        ]

    def get_output_reduction_on_part_failure(self, part: "Part"):
        """
        Calculate the reduction in output capacity when a specific part fails.
        Parameters:
        part (Part): The part that has failed. This can be an instance of any part,
                     but if it is an instance of Boiler, a different calculation is applied.
        Returns:
        float: The reduced output capacity. If the failed part is not a Boiler,
               the current capacity is returned. If the failed part is a Boiler,
               the total capacity divided by the number of total boilers is returned.
        """

        return (
            self.current_capacity
            if not isinstance(part, Boiler)
            else self.total_capacity / self.get_total_boilers()
        )

    def is_repairing_something(self) -> bool:
        """
        Check if the thermoelectric is currently repairing any part.
        """
        return any(part.is_repairing() for part in self.parts)

    def get_current_repair_part_index(self) -> int:
        """
        Get the index of the part that is currently under repair.
        """
        for i, part in enumerate(self.parts):
            if part.is_repairing():
                return i
        return -1

    def get_criticals_part(self) -> list[bool]:
        """
        Array of len N where ith is true if the part is critical
        """
        boilers_are_critical = False
        if self.get_total_broken_boilers() == self.get_total_boilers():
            boilers_are_critical = True

        critical_part_map: list[bool] = []
        for part in self.parts:

            critical_part_map.append(
                self.is_default_critical_part(part)
                or (boilers_are_critical and isinstance(part, Boiler))
            )

        return critical_part_map

    def consume_energy(self, amount):
        """
        Consumes a specified amount of energy from the thermoelectric plant's current capacity.

        Parameters:
            amount (float): The amount of energy to consume.

        Raises:
            RuntimeError: If the amount to consume is greater than the current capacity.

        Returns:
            float: The amount of energy consumed.
        """
        if amount > self.current_capacity:
            raise RuntimeError(
                f"Thermoelectric consume energy ({amount}) must be le than his current capacity {self.current_capacity}, id: {self.id}"
            )

        self.current_capacity -= amount
        return amount
