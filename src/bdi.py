from thermoelectrics import ThermoelectricAgent


class Belief:
    def __init__(self, value, description: str = "") -> None:
        self.value = value
        self.description = description


class Desire:
    def __init__(self, value, description: str = "") -> None:
        self.value = value
        self.description = description

    def evaluate(self):
        return self.value


class Intention:
    def __init__(self, value, description: str = "") -> None:
        self.value = value
        self.description = description


class TAMaxPowerOutputDesire(Desire):
    def __init__(self, value: bool) -> None:
        Desire.__init__(value, "Desire to maintain maximum power output")
        self.weight = 1

    def evaluate(self, agent: ThermoelectricAgent):
        if (
            agent.beliefs["plant_is_working"].value
            and len(agent.beliefs["broken_parts"].value) == 0
            and agent.beliefs["max_capacity"].value
            == agent.beliefs["current_capacity"].value
            and agent.beliefs["general_deficit"].value == 0
            and all([(time > 1) for _, time in agent.beliefs["parts_status"].value])
            and all(
                [
                    (
                        agent.beliefs["general_offer"].value - reduction
                        >= agent.beliefs["general_demand"].value
                    )
                    for _, reduction in agent.beliefs[
                        "power_output_reduction_on_part_failure"
                    ].value
                ]
            )
        ):
            agent.desires["maintain_maximum_power_output"].value = True
        else:
            agent.desires["maintain_maximum_power_output"].value = False


class TAPreventUnexpectedBreakdownDesire(Desire):
    def __init__(self, value) -> None:
        Desire.__init__(value, "Desire to prevent unexpected breakdowns")
        self.weight = 2

    def evaluate(self, agent: ThermoelectricAgent):
        if any([(time <= 1) for _, time in agent.beliefs["parts_status"].value]):
            agent.desires["prevent_unexpected_breakdowns"] = True

class TAMinimizeDowntimeDesire(Desire):
    def __init__(self, value) -> None:
        Desire.__init__(value, "Desire to minimize downtime")
        self.weight = 3


class TAMeetEnergyDemandDesire(Desire):
    def __init__(self, value) -> None:
        Desire.__init__(value, "Desire to meet energy demand")
        self.weight = 4


class TAPriorizeCriticalPartsRepairDesire(Desire):
    def __init__(self, value) -> None:
        Desire.__init__(value, "Desire to prioritize critical part repair")
        self.weight = 5


class TARepairPartsDesire(Desire):
    def __init__(self, value) -> None:
        Desire.__init__(
            value,
            "Desire to repair parts if necessary. \
            A List of Tuples where the left side is the Part and the right side is True if the Part needs repair",
        )
        self.weight = 6
