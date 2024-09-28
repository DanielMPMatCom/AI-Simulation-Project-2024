# from generative_ai import GenAIModel

# model = GenAIModel()

# ans = model.ask_model("What is the meaning of life?")

# print(ans)


# Make a map

from src.map import Map2D, GraphMap
from src.circuits import Circuit
from src.thermoelectrics import Thermoelectric
from src.worldstate import WorldState
from src.utils.gaussianmixture import DailyElectricityConsumptionBimodal
from numpy.random import randint
import networkx as nx
import matplotlib.pyplot as plt

no_circuits = 50
no_thermoelectrics = 8

map_2d = Map2D(
    no_circuits=no_circuits,
    no_thermoelectrics=no_thermoelectrics,
)

graphMap = GraphMap(
    thermoelectric_labels=[f"Th{i}" for i in range(no_thermoelectrics)],
    circuits_labels=[f"C{i}" for i in range(no_circuits)],
    towers_labels=[f"Tw{i}" for i in range(len(map_2d.towers_positions))],
    thermoelectrics_positions=map_2d.thermoelectrics_positions,
    circuits_positions=map_2d.circuits_positions,
    towers_positions=map_2d.towers_positions,
)


distance_cost_template = graphMap.thermoelectric_generation_cost

bimodal_consumption = DailyElectricityConsumptionBimodal(
    base_consumption=100, base_variability=5, mean_morning=7, std_morning=1, 
    mean_evening=19, std_evening=1, weight_morning=20, weight_evening=40
)

# Generate a circuits for map
ci: list[Circuit] = []
for i in range(no_circuits):
    ci.append(Circuit(graphMap.circuits_nodes[i].id, bimodal_consumption))

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

for t in graphMap.thermoelectrics_nodes:
    circuits_filtered = [
        key
        for key in mapper_circuit_with_thermoelectric
        if mapper_circuit_with_thermoelectric[key] == t.id
    ]
    print(ci)
    generated_thermoelectric_min_cost = sum(
        [
            next(circuit.mock_electric_consume for circuit in ci if circuit.id == key)
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

worldstate = WorldState(ci, ti)