from generative_ai import GenAIModel
from src.people import ThermoelectricAgent, ChiefElectricCompanyAgent
from part import Coils, SteamTurbine, Generator, Boiler


class Belief:
    def __init__(self, value, description: str = "") -> None:
        self.value = value
        self.description = description


class Desire:
    def __init__(self, value, description: str, id: str) -> None:
        self.value = value
        self.description = description
        self.id = id

    def evaluate(self, agent):
        return self.value


class Intention:
    def __init__(self, value, description: str = "") -> None:
        self.value = value
        self.description = description


# region Thermoelectric Agent Desires


class TAMaxPowerOutputDesire(Desire):
    def __init__(self, value: bool) -> None:
        Desire.__init__(
            value, "Desire to maintain maximum power output", "max_power_output"
        )
        self.weight = 1

    def evaluate(self, agent: "ThermoelectricAgent"):
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

    def evaluate(self, agent: "ThermoelectricAgent"):
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

    def evaluate(self, agent: "ThermoelectricAgent"):
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

    def evaluate(self, agent: "ThermoelectricAgent"):
        if agent.beliefs["general_offer"].value < agent.beliefs["general_demand"].value:
            agent.desires["meet_energy_demand"] = True
        else:
            agent.desires["meet_energy_demand"] = False


class TAPrioritizeCriticalPartsRepairDesire(Desire):
    def __init__(self, value) -> None:
        Desire.__init__(
            value,
            "Desire to prioritize critical part repair",
            "prioritize_critical_parts_repair",
        )
        self.weight = 5

    def evaluate(self, agent: "ThermoelectricAgent"):

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

    def evaluate(self, agent: "ThermoelectricAgent"):
        agent.desires["repair_parts"] = [
            (part, part in agent.beliefs["broken_parts"].value)
            for part in agent.thermoelectric.parts
        ]


# region Chief of Electric Company Agent Desires
class CECAMeetDemandDesire(Desire):
    def __init__(self, value) -> None:
        Desire.__init__(
            self,
            value,
            description="Desire to meet the overall energy demand",
            id="meet_demand",
        )
        self.weight = 5

    def evaluate(self, agent: "ChiefElectricCompanyAgent"):
        if agent.beliefs["general_demand"].value < agent.beliefs["general_offer"].value:
            agent.desires["meet_demand"] = True
        else:
            agent.desires["meet_demand"] = False


class CECAPrioritizeBlockImportance(Desire):
    def __init__(self, value) -> None:
        Desire.__init__(
            self,
            value,
            description="Desire to prioritize energy supply for the most critical blocks",
            id="prioritize_block_importance",
        )
        self.weight = 2

    def evaluate(self, agent: "ChiefElectricCompanyAgent"):
        if agent.beliefs["general_offer"].value < agent.beliefs["general_demand"].value:
            agent.desires["prioritize_block_importance"] = True
        else:
            agent.desires["prioritize_block_importance"] = False


class CECAPrioritizeBlockOpinion(Desire):
    def __init__(self, value, description: str = "", id: str = "") -> None:
        Desire.__init__(
            self,
            value,
            description="Desire to prioritize energy supply for blocks with the most influential public opinions",
            id="prioritize_block_opinion",
        )
        self.weight = 2

    def evaluate(self, agent: "ChiefElectricCompanyAgent"):
        bad_opinions = [
            opinion < 0.5
            for (_, _, opinion) in agent.beliefs["opinion_per_block_in_circuits"].value
        ]
        exist_bad_opinions = len(bad_opinions) > 0

        if (
            exist_bad_opinions
            and agent.beliefs["general_offer"].value
            < agent.beliefs["general_demand"].value
        ):
            agent.desires["prioritize_block_opinion"] = True
        else:
            agent.desires["prioritize_block_opinion"] = False


class CECAPrioritizeConsecutiveDaysOff(Desire):
    def __init__(self, value) -> None:
        Desire.__init__(
            self,
            value,
            description="Desire to prioritize energy supply for blocks with a significant number of consecutive off days",
            id="prioritize_consecutive_days_off",
        )
        self.weight = 1

    def evaluate(self, agent: "ChiefElectricCompanyAgent"):
        sequences = agent.beliefs["longest_sequence_off_per_block_in_circuits"].value
        affected_blocks = [days > 3 for days in sequences]

        if (
            any(affected_blocks)
            and agent.beliefs["general_offer"].value
            < agent.beliefs["general_demand"].value
        ):
            agent.desires["prioritize_consecutive_days_off"] = True
        else:
            agent.desires["prioritize_consecutive_days_off"] = False


class CECAPrioritizeDaysOff(Desire):
    def __init__(self, value) -> None:
        Desire.__init__(
            self,
            value,
            description="Desire to prioritize energy supply for blocks with a significant number of off days",
            id="prioritize_days_off",
        )
        self.weight = 1

    def evaluate(self, agent: "ChiefElectricCompanyAgent"):
        days_off = agent.beliefs["days_off_per_block_in_circuits"].value
        affected_blocks = [days > 7 for days in days_off]

        if (
            any(affected_blocks)
            and agent.beliefs["general_offer"].value
            < agent.beliefs["general_demand"].value
        ):
            agent.desires["prioritize_days_off"] = True
        else:
            agent.desires["prioritize_days_off"] = False


class CECAGeneratedDesire:
    def __init__(self, id, description, weight, desires, conditions) -> None:
        self.id = id
        self.description = description
        self.weight = weight
        self.desires = desires
        self.conditions = conditions

    def evaluate(self, agent: ChiefElectricCompanyAgent):
        for condition in self.conditions:
            if not condition(agent.beliefs):
                return
        for desire in self.desires:
            agent.desires[desire] = True


class DesireGenerator:
    def __init__(self) -> None:
        self.api = GenAIModel(
            system_instruction="""
            You are an intelligent agent with a BDI architecture simulating the chief of an 
            electric company. I will provide you with a list of desires and a list of conditions. 
            Your task is to evaluate which desires could be activated based on all or a subset of 
            those conditions. Return only two lists: one containing the subset of selected 
            conditions and another containing the subset of desires that would be activated.
            Do not provide any explanations or additional text. I only want the two lists.
            Example output:
            conditions = ["fully covered system", "neutral general opinion", "many thermoelectrics working"]
            desires = ["prioritize_block_opinion", "prioritize_block_importance"]
            The desires list is: ["meet_demand", "prioritize_block_importance", "prioritize_block_opinion", "prioritize_consecutive_days_off", "prioritize_days_off"]
            Here are the desires you should consider and an explination of what each one of them means in this context:
            "meet_demand": Desire to meet the demand when there is a generation deficit.
            "prioritize_block_importance": Desire to prioritize supplying energy to blocks of greater importance.
            "prioritize_block_opinion": Desire to prioritize supplying energy to blocks with the worst public opinion.
            "prioritize_consecutive_days_off": Desire to prioritize supplying energy to blocks that have suffered power cuts for more consecutive days.
            "prioritize_days_off": Desire to prioritize supplying energy to blocks that have experienced more power cuts in total days.
            Now that you know the desires, I will send you the list of conditions for evaluation.
            """
        )

        self.conversation = self.api.model.start_chat(history=[])

    def generate_new_desire(self, conditions: str = "no conditions"):
        if conditions == "no conditions":
            raise Exception("No conditions have been provided")

        query = f"""
        The list of conditions is as follows: {conditions}
        """
        ans = self.conversation.send_message(query)
        return ans.text.strip()
