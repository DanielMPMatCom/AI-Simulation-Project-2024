import pickle
from src.people import TestCaseParams, ChiefElectricCompanyAgent

test: "TestCaseParams" = None

with open("ErrorOnDistribution.plk", "rb") as file:
    test = pickle.load(file)


agent = ChiefElectricCompanyAgent(
    name=test.name,
    thermoelectrics=test.thermoelectrics,
    circuits=test.circuits,
    perception=test.perception,
    rules=test.rules,
    current_rules=test.current_rules,
    mapper_key_to_circuit_block=test.mapper_key_to_circuit_block,
    learn=test.learn,
    mutation_rate=test.mutation_rate,
)

agent.action(test.perception)