# from src.people import ThermoelectricAgent, ChiefElectricCompanyAgent
from src.generative_ai import GenAIModel
from src.part import Coils, SteamTurbine, Generator, Boiler
from src.simulation_constants import MIN_DAYS_TO_NEED_REPAIR


class Belief:
    """
    A class to represent a belief in the BDI (Belief-Desire-Intention) model.
    """

    def __init__(self, value, description: str = "") -> None:
        self.value = value
        self.description = description


class Desire:
    """
    Desire class represents a goal or objective that an agent aims to achieve.
    """

    def __init__(self, description: str, id: str) -> None:
        self.description = description
        self.id = id

    def evaluate(self, agent):
        raise NotImplementedError("This function must be implemented on a subclass")


class Intention:
    """
    Represents an intention with a specific value and an optional description.
    """

    def __init__(self, value, description: str = "") -> None:
        self.value = value
        self.description = description


# region Thermoelectric Agent Desires


class TAMaxPowerOutputDesire(Desire):
    """
    Represents a desire for a thermoelectric agent to maintain maximum power output.
    """

    def __init__(self) -> None:
        Desire.__init__(
            self, "Desire to maintain maximum power output", "max_power_output"
        )
        self.weight = 1

    def evaluate(self, agent):

        agent.desires["maintain_maximum_power_output"] = (
            agent.beliefs["general_deficit"].value <= 0
            and agent.beliefs["max_capacity"].value
            - agent.beliefs["current_capacity"].value
            <= 1e-8
        )


class TAMinimizeDowntimeDesire(Desire):
    """
    Represents a desire to minimize downtime in a thermoelectric plant.
    """

    def __init__(self) -> None:
        Desire.__init__(self, "Desire to minimize downtime", "minimize_downtime")
        self.weight = 2

    def evaluate(self, agent):

        agent.desires["minimize_downtime"] = (
            not agent.beliefs["plant_is_working"].value
            and agent.beliefs["general_deficit"].value > 0
        )


class TAMeetEnergyDemandDesire(Desire):  # increase power output
    """
    A class representing the desire to meet energy demand for a thermoelectric agent.
    """

    def __init__(self) -> None:
        Desire.__init__(self, "Desire to meet energy demand", "meet_energy_demand")
        self.weight = 3

    def evaluate(self, agent):

        agent.desires["meet_energy_demand"] = (
            agent.beliefs["general_deficit"].value > 0
            and len(agent.beliefs["broken_parts"].value) > 0
        )


class TAPrioritizeCriticalPartsRepairDesire(Desire):
    """
    A desire class that prioritizes the repair of critical parts in a thermoelectric agent.
    """

    def __init__(self) -> None:
        Desire.__init__(
            self,
            "Desire to prioritize critical part repair",
            "prioritize_critical_parts_repair",
        )
        self.weight = 4

    def evaluate(self, agent):

        broken_boilers = sum(
            1
            for part in agent.beliefs["broken_parts"].value
            if isinstance(part, Boiler)
        )

        if broken_boilers == agent.thermoelectric.get_total_boilers():
            agent.desires["prioritize_critical_parts_repair"] = False

        else:
            agent.desires["prioritize_critical_parts_repair"] = any(
                [
                    (isinstance(part, (Coils, SteamTurbine, Generator)))
                    for part in agent.beliefs["broken_parts"].value
                ]
            )


class TAPreventUnexpectedBreakdownDesire(Desire):
    """
    TAPreventUnexpectedBreakdownDesire is a subclass of Desire that represents the
    desire to prevent unexpected breakdowns in a thermoelectric agent.
    """

    def __init__(self) -> None:
        Desire.__init__(
            self,
            "Desire to prevent unexpected breakdowns",
            "prevent_unexpected_breakdowns",
        )
        self.weight = 5

    def evaluate(self, agent):

        agent.desires["prevent_unexpected_breakdowns"] = any(
            [
                (
                    time <= MIN_DAYS_TO_NEED_REPAIR
                    and agent.beliefs["general_offer"].value
                    - agent.beliefs["power_output_reduction_on_part_failure"].value[
                        index
                    ][1]
                    > agent.beliefs["general_demand"].value * 3 / 4
                )
                for index, (_, is_working, time) in enumerate(
                    agent.beliefs["parts_status"].value
                )
            ]
        )


class TARepairPartsDesire(Desire):
    """
    TARepairPartsDesire is a class that represents the desire of a thermoelectric agent to repair parts if necessary.
    """

    def __init__(self) -> None:
        Desire.__init__(
            self,
            "Desire to repair parts if necessary. \
            A List of Tuples where the left side is the Part and the right side is True if the Part needs repair",
            "repair_parts",
        )
        self.weight = 6

    def evaluate(self, agent):

        agent.desires["repair_parts"] = any(
            [
                (not is_working)
                for _, is_working, time in agent.beliefs["parts_status"].value
            ]
        )


# region Chief of Electric Company Agent Desires
class CECAMaxStoredEnergyDesire(Desire):
    """
    CECAMaxStoredEnergyDesire is a subclass of Desire that represents the desire to maximize stored energy.
    """

    def __init__(self) -> None:
        Desire.__init__(
            self,
            description="Desire to maximize stored energy",
            id="max_stored_energy",
        )
        self.weight = 5

    def evaluate(self, agent):
        agent.desires["max_stored_energy"] = (
            self.weight
            if agent.beliefs["general_demand"].value
            < agent.beliefs["general_offer"].value
            else 0
        )


class CECAMeetDemandDesire(Desire):
    """
    CECAMeetDemandDesire is a subclass of Desire that represents the desire to meet the overall energy demand.
    """

    def __init__(self) -> None:
        Desire.__init__(
            self,
            description="Desire to meet the overall energy demand",
            id="meet_demand",
        )
        self.weight = 5

    def evaluate(self, agent):

        agent.desires["meet_demand"] = (
            self.weight
            if agent.beliefs["general_demand"].value
            >= agent.beliefs["general_offer"].value
            else 0
        )


class CECAPrioritizeBlockImportance(Desire):
    """
    CECAPrioritizeBlockImportance is a class that represents the desire to prioritize energy supply for the most critical blocks.
    """

    def __init__(self) -> None:
        Desire.__init__(
            self,
            description="Desire to prioritize energy supply for the most critical blocks",
            id="prioritize_block_importance",
        )
        self.weight = 2

    def evaluate(self, agent):
        agent.desires["prioritize_block_importance"] = (
            self.weight
            if agent.beliefs["general_offer"].value
            < agent.beliefs["general_demand"].value
            else 0
        )


class CECAPrioritizeBlockOpinion(Desire):
    """
    A desire class that represents the priority to supply energy
    to blocks with the most negative public opinions.
    """

    def __init__(self) -> None:
        Desire.__init__(
            self,
            description="Desire to prioritize energy supply for blocks with the most influential public opinions",
            id="prioritize_block_opinion",
        )
        self.weight = 2

    def evaluate(self, agent):
        bad_opinions = [
            opinion < 0.5
            for (_, _, opinion) in agent.beliefs["opinion_per_block_in_circuits"].value
        ]
        exist_bad_opinions = len(bad_opinions) > 0

        agent.desires["prioritize_block_opinion"] = (
            self.weight
            if exist_bad_opinions
            and agent.beliefs["general_offer"].value
            < agent.beliefs["general_demand"].value
            else 0
        )


class CECAPrioritizeConsecutiveDaysOff(Desire):
    """
    A desire class that prioritizes energy supply for blocks with a significant number of consecutive off days.
    """

    def __init__(self) -> None:
        Desire.__init__(
            self,
            description="Desire to prioritize energy supply for blocks with a significant number of consecutive off days",
            id="prioritize_consecutive_days_off",
        )
        self.weight = 1

    def evaluate(self, agent):
        sequences = agent.beliefs["longest_sequence_off_per_block_in_circuits"].value
        affected_blocks = [days > 3 for cid, bid, days in sequences]

        agent.desires["prioritize_consecutive_days_off"] = (
            self.weight
            if any(affected_blocks)
            and agent.beliefs["general_offer"].value
            < agent.beliefs["general_demand"].value
            else 0
        )


class CECAPrioritizeDaysOff(Desire):
    """
    A class representing the desire to prioritize energy supply for blocks with a significant number of off days.
    """

    def __init__(self) -> None:
        Desire.__init__(
            self,
            description="Desire to prioritize energy supply for blocks with a significant number of off days",
            id="prioritize_days_off",
        )
        self.weight = 1

    def evaluate(self, agent):
        days_off = agent.beliefs["last_days_off_per_block_in_circuits"].value
        affected_blocks = [days > 7 for cid, blockId, days in days_off]

        agent.desires["prioritize_days_off"] = (
            self.weight
            if any(affected_blocks)
            and agent.beliefs["general_offer"].value
            < agent.beliefs["general_demand"].value
            else 0
        )


class CECAGeneratedDesire:
    """
    CECAGeneratedDesire represents a desire generated by the Chief Electric Company Agent (CECA).
    """

    def __init__(self, id, weight, desires, conditions, condition_description) -> None:
        self.id = id
        self.description = (
            "IF "
            + " AND ".join(condition_description)
            + " THEN "
            + " AND ".join(desires)
        )
        self.weight = weight
        self.desires = desires
        self.conditions = conditions
        self.condition_description = condition_description
        print("Imprimiendo GENERATED DESIRE", self)

    def __str__(self):
        return f"""
        id: {self.id}.
        description : {self.description},
        weight: {self.weight}.
        """

    def evaluate(self, agent):
        for condition in self.conditions:
            if not condition(agent.beliefs):
                return
        for desire in self.desires:
            agent.desires[desire] = self.weight


class DesireGenerator:
    """
    DesireGenerator is a class that interacts with a generative AI model to simulate the decision-making process of an intelligent agent with a BDI (Belief-Desire-Intention) architecture. The agent acts as the chief of an electric company, evaluating which desires to activate based on given conditions.
    Attributes:
        api (GenAIModel): An instance of the generative AI model configured with specific system instructions.
        conversation (Chat): An ongoing conversation with the AI model to facilitate continuous interaction.
    Methods:
        __init__(): Initializes the DesireGenerator with the AI model and starts a new chat conversation.
        generate_new_desire(conditions: str): Generates a new desire based on the provided conditions. Raises an exception if no conditions are provided.
    Raises:
        Exception: If no conditions are provided to the generate_new_desire method.
    """

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
            Here are the desires you should consider and an explanation of what each one of them means in this context:
            "meet_demand": Desire to meet the demand when there is a generation deficit.
            "prioritize_block_importance": Desire to prioritize supplying energy to blocks of greater importance.
            "prioritize_block_opinion": Desire to prioritize supplying energy to blocks with the worst public opinion.
            "prioritize_consecutive_days_off": Desire to prioritize supplying energy to blocks that have suffered power cuts for more consecutive days.
            "prioritize_days_off": Desire to prioritize supplying energy to blocks that have experienced more power cuts in total days.
            "max_stored_energy": Desire to maximize stored energy. Stored energy is the energy left over when a complete distribution is carried out.
            Now that you know the desires, I will send you the list of conditions for evaluation.
            """
        )

        self.conversation = self.api.model.start_chat(history=[])

    def generate_new_desire(self, conditions: str = "no conditions"):
        if conditions == "no conditions":
            raise RuntimeError("No conditions have been provided")

        query = f"""
        The list of conditions is as follows: {conditions}
        """
        ans = self.conversation.send_message(query)
        return ans.text.strip()
