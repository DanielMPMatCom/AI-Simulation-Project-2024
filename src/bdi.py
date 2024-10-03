from thermoelectrics import ThermoelectricAgent
from part import Part, Coils, SteamTurbine, Generator, Boiler


class Belief:
    def __init__(self, value, description: str = "") -> None:
        self.value = value
        self.description = description


class Desire:
    def __init__(self, value, description: str = "", id: str = "") -> None:
        self.value = value
        self.description = description
        self.id = id

    def evaluate(self):
        return self.value


class Intention:
    def __init__(self, value, description: str = "") -> None:
        self.value = value
        self.description = description


class TAMaxPowerOutputDesire(Desire):
    def __init__(self, value: bool) -> None:
        Desire.__init__(
            value, "Desire to maintain maximum power output", "max_power_output"
        )
        self.weight = 1

    def evaluate(self, agent: ThermoelectricAgent):
        if (
            agent.beliefs["general_deficit"].value > 0
            and agent.beliefs["current_capacity"] < agent.beliefs["max_capacity"]
        ):
            agent.desires["maintain_maximum_power_output"] = True
        else:
            agent.desires["maintain_maximum_power_output"] = False


class TAPreventUnexpectedBreakdownDesire(Desire):
    def __init__(self, value) -> None:
        Desire.__init__(
            value,
            "Desire to prevent unexpected breakdowns",
            "prevent_unexpected_breakdowns",
        )
        self.weight = 2

    def evaluate(self, agent: ThermoelectricAgent):
        if any(
            [(time <= 1) for _, _, time in agent.beliefs["parts_status"].value]
        ) and all(
            [
                (
                    (agent.beliefs["general_offer"].value - reduction)
                    > agent.beliefs["general_demand"].value * 3 / 4
                )
                for _, reduction in agent.beliefs[
                    "power_output_reduction_on_part_failure"
                ].value
            ]
        ):
            agent.desires["prevent_unexpected_breakdowns"] = True
        else:
            agent.desires["prevent_unexpected_breakdowns"] = False


class TAMinimizeDowntimeDesire(Desire):
    def __init__(self, value) -> None:
        Desire.__init__(value, "Desire to minimize downtime", "minimize_downtime")
        self.weight = 3

    def evaluate(self, agent: ThermoelectricAgent):
        if (
            agent.beliefs["plant_is_working"].value == False
            and agent.beliefs["general_deficit"].value > 0
        ):
            agent.desires["minimize_downtime"] = True
        else:
            agent.desires["minimize_downtime"] = False


class TAMeetEnergyDemandDesire(Desire):
    def __init__(self, value) -> None:
        Desire.__init__(value, "Desire to meet energy demand", "meet_energy_demand")
        self.weight = 4

    def evaluate(self, agent: ThermoelectricAgent):
        if agent.beliefs["general_offer"].value < agent.beliefs["general_demand"].value:
            agent.desires["meet_energy_demand"] = True
        else:
            agent.desires["meet_energy_demand"] = False


class TAPriorizeCriticalPartsRepairDesire(Desire):
    def __init__(self, value) -> None:
        Desire.__init__(
            value,
            "Desire to prioritize critical part repair",
            "prioritize_critical_parts_repair",
        )
        self.weight = 5

    def evaluate(self, agent: ThermoelectricAgent):

        broken_boilers = sum(
            1
            for part in agent.beliefs["broken_parts"].value
            if isinstance(part, Boiler)
        )

        if broken_boilers == agent.thermoelectric.get_total_boilers():
            agent.desires["prioritize_critical_parts_repair"] = False
        elif any(
            [
                (isinstance(part, (Coils, SteamTurbine, Generator)))
                for part in agent.beliefs["broken_parts"].value
            ]
        ):
            agent.desires["prioritize_critical_parts_repair"] = True
        else:
            agent.desires["prioritize_critical_parts_repair"] = False


class TARepairPartsDesire(Desire):
    def __init__(self, value) -> None:
        Desire.__init__(
            value,
            "Desire to repair parts if necessary. \
            A List of Tuples where the left side is the Part and the right side is True if the Part needs repair",
            "repair_parts",
        )
        self.weight = 6

    def evaluate(self, agent: ThermoelectricAgent):
        agent.desires["repair_parts"] = [
            (part, part in agent.beliefs["broken_parts"].value)
            for part in agent.thermoelectric.parts
        ]
