from src.map import Map2D, GraphMap
from src.utils.gaussianmixture import DailyElectricityConsumptionBimodal
from src.circuits import Circuit, Block
from src.thermoelectrics import Thermoelectric
# from src.worldstate import WorldState
from numpy.random import default_rng
import networkx as nx
import matplotlib.pyplot as plt

NO_CIRCUITS = 50
NO_THERMOELECTRICS = 8

MIN_CITIZEN = 1000
MAX_CITIZEN = 10000
MAX_DEVIATION_CITIZEN_IN_BLOCK = 200

DEMAND_PER_PERSON = 1
DEMAND_INDUSTRIALIZATION = 5000

VARIABILITY_DEMAND_PER_PERSON = 0.01
VARIABILITY_DEMAND_PER_INDUSTRIALIZATION = 100

PEAK_CONSUMPTION_MORNING = 7
PEAK_CONSUMPTION_EVENING = 19

MAX_DEVIATION_MORNING = 2
MAX_DEVIATION_EVENING = 3

WEIGHT_MORNING = 10
WEIGHT_EVENING = 20

RANDOM_SEED = 42

MIN_BLOCKS_PER_CIRCUIT = 1
MAX_BLOCKS_PER_CIRCUIT = 10

# CHIEF PARAMS
IMPORTANCE_ALPHA = 0.374345


map_2d = Map2D(
    no_circuits=NO_CIRCUITS,
    no_thermoelectrics=NO_THERMOELECTRICS,
)

map_2d.visualize()

graphMap = GraphMap(
    thermoelectric_labels=[f"Th{i}" for i in range(NO_THERMOELECTRICS)],
    circuits_labels=[f"C{i}" for i in range(NO_CIRCUITS)],
    towers_labels=[f"Tw{i}" for i in range(len(map_2d.towers_positions))],
    thermoelectrics_positions=map_2d.thermoelectrics_positions,
    circuits_positions=map_2d.circuits_positions,
    towers_positions=map_2d.towers_positions,
)


distance_cost_template = graphMap.thermoelectric_generation_cost

# Generate circuits for map
rng = default_rng(RANDOM_SEED)

ci: list[Circuit] = []
for i in range(NO_CIRCUITS):
    citizen_count = rng.integers(MIN_CITIZEN, MAX_CITIZEN)
    citizen_range = (
        max(citizen_count - MAX_DEVIATION_CITIZEN_IN_BLOCK, 0),
        min(citizen_count + MAX_DEVIATION_CITIZEN_IN_BLOCK, MAX_CITIZEN),
    )

    industrialization = (
        rng.integers(0, DEMAND_INDUSTRIALIZATION) / DEMAND_INDUSTRIALIZATION
    )

    bimodal_consumption = DailyElectricityConsumptionBimodal(
        base_consumption=DEMAND_PER_PERSON * citizen_count
        + DEMAND_INDUSTRIALIZATION * industrialization,
        base_variability=VARIABILITY_DEMAND_PER_PERSON * citizen_count
        + VARIABILITY_DEMAND_PER_INDUSTRIALIZATION * industrialization,
        mean_morning=PEAK_CONSUMPTION_MORNING,
        mean_evening=PEAK_CONSUMPTION_EVENING,
        std_morning=rng.uniform(1.0, MAX_DEVIATION_MORNING),
        std_evening=rng.uniform(1.0, MAX_DEVIATION_EVENING),
        weight_morning=WEIGHT_MORNING,
        weight_evening=WEIGHT_EVENING,
    )

    ci.append(
        Circuit(
            graphMap.circuits_nodes[i].id,
            gaussian_mixture=bimodal_consumption,
            blocks_range=(MIN_BLOCKS_PER_CIRCUIT, MAX_BLOCKS_PER_CIRCUIT),
            citizens_range=citizen_range,
            industrialization=industrialization,
        )
    )


# Generate Thermoelectric generation based in the nearest circuits
mapper_circuit_with_thermoelectric = {}

for c in ci:

    filtered = [f for f in graphMap.thermoelectric_generation_cost if f[1] == c.id]
    filtered = sorted(filtered, key=lambda x: x[2])
    mapper_circuit_with_thermoelectric[c.id] = filtered[0][0]


# visualize the map
G = nx.Graph()
for i in mapper_circuit_with_thermoelectric:
    G.add_edge(
        f"C{i}",
        f"Th{mapper_circuit_with_thermoelectric[i]}",
    )

nx.draw(G, with_labels=True, font_weight="bold")
plt.show()


# Generate thermoelectrics
ti: list[Thermoelectric] = []

for (
    t
) in (
    graphMap.thermoelectrics_nodes
):  # TODO : FIX THE DEFAULT GENERATION OF THERMOELECTRIC
    circuits_filtered = [
        key
        for key in mapper_circuit_with_thermoelectric
        if mapper_circuit_with_thermoelectric[key] == t.id
    ]
    print(ci)
    generated_thermoelectric_min_cost = sum(
        [
            next(
                circuit.mock_electric_consume for circuit in ci if circuit.id == key
            )  # TODO : REMOVE MOCKS
            + sum(
                [x[2] for x in distance_cost_template if x[0] == t.id and x[1] == key]
            )
            for key in circuits_filtered
        ]
    )

    ti.append(
        Thermoelectric(
            id=t.id, parts=[], total_capacity=generated_thermoelectric_min_cost
        )
    )

for t in ti:
    print(t.id, t.total_capacity)

### CHIEF
# Auxiliary functions
max_population_of_circuits = -1
max_population_of_block = -1

for circuit in ci:
    max_population_of_circuits = max(
        circuit.get_all_block_population(), max_population_of_circuits
    )
    for block in circuit.blocks:
        max_population_of_block = max(block.citizens.amount, max_population_of_block)

auxiliary_data_max_population_of_circuits = max_population_of_circuits
auxiliary_data_max_population_of_block = max_population_of_block


def get_circuit_importance(circuit: Circuit) -> float:
    return (
        circuit.get_all_block_population() / auxiliary_data_max_population_of_circuits
    ) * IMPORTANCE_ALPHA + circuit.industrialization * (1 - IMPORTANCE_ALPHA)


def get_block_importance(block: Block) -> float:
    return (
        block.citizens / auxiliary_data_max_population_of_circuits
    ) * IMPORTANCE_ALPHA + block.industrialization * (1 - IMPORTANCE_ALPHA)


def distance_template_to_distance_matrix(
    template: list[tuple[str, str, float, list[str]]],
    thermoelectrics: list[Thermoelectric],
    circuits: list[Circuit],
):
    matrix = [[] * len(thermoelectrics)] * len(circuits)

    c_map = {}
    t_map = {}

    for i, t in enumerate(thermoelectrics):
        t_map[t.id] = i

    for i, c in enumerate(circuits):
        c_map[c.id] = i

    for t, c, cost, _ in template:
        matrix[t_map[t]][c_map[c]] = cost

    max_value = max(matrix)

    for t, c, _, _ in template:
        matrix[t_map[t]], matrix[c_map[c]] /= max_value

    return matrix


# print(distance_cost_template(distance_cost_template, ti, ci))


# worldstate = WorldState(ci, ti)
