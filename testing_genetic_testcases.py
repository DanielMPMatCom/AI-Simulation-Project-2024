import pickle
from src.people import TestCaseParams, ChiefElectricCompanyAgent
from src.bdi import (
    CECAGeneratedDesire,
    CECAMaxStoredEnergyDesire,
    CECAMeetDemandDesire,
    CECAPrioritizeBlockImportance,
    CECAPrioritizeBlockOpinion,
    CECAPrioritizeConsecutiveDaysOff,
    CECAPrioritizeDaysOff,
)

test: "TestCaseParams" = None

with open("./ErrorOnDistribution.pkl", "rb") as file:
    test = pickle.load(file)


chief_agent_desires = {
    "meet_demand": CECAMeetDemandDesire(),
    "prioritize_block_importance": CECAPrioritizeBlockImportance(),
    "prioritize_block_opinion": CECAPrioritizeBlockOpinion(),
    "prioritize_consecutive_days_off": CECAPrioritizeConsecutiveDaysOff(),
    "prioritize_days_off": CECAPrioritizeDaysOff(),
}

chief_agent_current_desires = [
    "meet_demand",
    "prioritize_block_importance",
    "prioritize_block_opinion",
    "prioritize_consecutive_days_off",
    "prioritize_days_off",
]

agent = ChiefElectricCompanyAgent(
    name=test.name,
    thermoelectrics=test.thermoelectrics,
    circuits=test.circuits,
    perception=test.perception,
    rules=chief_agent_desires,
    current_rules=chief_agent_current_desires,
    mapper_key_to_circuit_block=test.mapper_key_to_circuit_block,
    learn=test.learn,
    mutation_rate=test.mutation_rate,
)

agent.action(test.perception)
