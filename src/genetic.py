import random

def assign_thermoelectric_to_circuit(circuit:int, chromosome:list[int], capacities:list[int], P:list[list[int]]):
    valid_thermoelectrics = [i for i in range(len(capacities)) if capacities[i] >= P[i][circuit]]
    assigned_thermoelectric = random.choice(valid_thermoelectrics) if valid_thermoelectrics else -1
    chromosome[circuit] = assigned_thermoelectric
    capacities[assigned_thermoelectric] -= P[assigned_thermoelectric][circuit]

def generate_population(P:list[list[int]], capacities:list[int], circuits:int, pop_size:int):
    population = []
    for _ in range(pop_size):
        chromosome = [-1] * circuits
        remaining_capacities = capacities[:]
        
        waiting = [i for i in range(circuits)]
        random.shuffle(waiting)

        for circuit in waiting:
            assign_thermoelectric_to_circuit(circuit, chromosome, remaining_capacities, P)

        population.append(chromosome)
    return population

def crossover(parent_1:list[int], parent_2:list[int], capacities:list[int], P:list[list[int]]):
    position = random.randint(1, len(parent_1) - 1)
    chromosome = parent_1[:position] + parent_2[position:]

    if is_invalid(chromosome, capacities, P):
        repair_chromosome(chromosome, capacities, P)

    return chromosome

def is_invalid(chromosome:list[int], capacities:list[int], P:list[list[int]]):
    
    current_capacities = capacities[:] 

    for circuit, thermoelectric in enumerate(chromosome):
        current_capacities[thermoelectric] -= P[thermoelectric][circuit]

    return any(capacity < 0 for capacity in current_capacities)

def repair_chromosome(chromosome:list[int], capacities:list[int], P:list[list[int]]):

    current_capacities = capacities[:]
    for circuit, thermoelectric in enumerate(chromosome):
        current_capacities[thermoelectric] -= P[thermoelectric][circuit]

    remaining_capacities = [0] * len(current_capacities)
    for thermoelectric, capacity in enumerate(current_capacities):
        
        current_capacity = capacity
        waiting = []

        while current_capacity < 0:
            thermoelectric_circuits = [ci for ci, th in enumerate(chromosome) if th == thermoelectric]

            point = random.randint(0, len(thermoelectric_circuits) - 1)
            circuit = thermoelectric_circuits[point]
            current_capacity += P[thermoelectric][circuit]
            chromosome[circuit] = -1
            waiting.append(circuit)

        remaining_capacities[thermoelectric] = current_capacity

    random.shuffle(waiting)
    for circuit in waiting:
        assign_thermoelectric_to_circuit(circuit, chromosome, remaining_capacities, P)

    waiting = [i for i in range(len(chromosome)) if chromosome[i] == -1]
    random.shuffle(waiting)
    
    for circuit in range(len(chromosome)):
            assign_thermoelectric_to_circuit(circuit, chromosome, remaining_capacities, P)

capacities = [2, 1, 2]
P = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]

q = generate_population(
    P = P, 
    capacities = capacities,
    circuits = 3,
    pop_size = 5
)

children = [crossover(q[i], q[i+1], capacities, P) for i in range(len(q) - 1)]

print("Population")
for chromosome in q:
    print(chromosome)


print("Children")
for child in children:
    print(child)