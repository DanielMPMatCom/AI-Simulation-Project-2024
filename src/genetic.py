import random


def fitness():
    pass


def assign_thermoelectric_to_circuit(
    circuit: int, chromosome: list[int], capacities: list[int], P: list[list[int]]
):
    valid_thermoelectrics = [
        i for i in range(len(capacities)) if capacities[i] >= P[i][circuit]
    ]
    assigned_thermoelectric = (
        random.choice(valid_thermoelectrics) if valid_thermoelectrics else -1
    )
    chromosome[circuit] = assigned_thermoelectric
    capacities[assigned_thermoelectric] -= P[assigned_thermoelectric][circuit]


def generate_population(
    P: list[list[int]], capacities: list[int], circuits: int, pop_size: int
):
    population = []
    for _ in range(pop_size):
        chromosome = [-1] * circuits
        remaining_capacities = capacities[:]

        waiting = [i for i in range(circuits)]
        random.shuffle(waiting)

        for circuit in waiting:
            assign_thermoelectric_to_circuit(
                circuit, chromosome, remaining_capacities, P
            )

        population.append(chromosome)
    return population


def crossover(
    parent_1: list[int], parent_2: list[int], capacities: list[int], P: list[list[int]]
):
    position = random.randint(1, len(parent_1) - 1)
    chromosome = parent_1[:position] + parent_2[position:]

    if is_invalid(chromosome, capacities, P):
        repair_chromosome(chromosome, capacities, P)

    return chromosome


def crossover_uniform(
    parent_1: list[int],
    parent_2: list[int],
    capacities: list[int],
    P: list[list[int]],
    prob_p1: float = 0.5,
    prob_p2: float = 0.5,
):
    chromosome = [-1] * len(parent_1)

    for i in range(len(parent_1)):
        prob = random.random()

        if prob <= prob_p1:
            chromosome[i] = parent_1[i]
        elif prob <= prob_p1 + prob_p2:
            chromosome[i] = parent_2[i]
        else:
            chromosome[i] = random.randint(len(capacities) - 1)

    if is_invalid(chromosome, capacities, P):
        repair_chromosome(chromosome, capacities, P)

    return chromosome


def is_invalid(chromosome: list[int], capacities: list[int], P: list[list[int]]):

    current_capacities = capacities[:]

    for circuit, thermoelectric in enumerate(chromosome):
        current_capacities[thermoelectric] -= P[thermoelectric][circuit]

    return any(capacity < 0 for capacity in current_capacities)


def repair_chromosome(chromosome: list[int], capacities: list[int], P: list[list[int]]):

    current_capacities = capacities[:]
    for circuit, thermoelectric in enumerate(chromosome):
        current_capacities[thermoelectric] -= P[thermoelectric][circuit]

    waiting = []
    remaining_capacities = [0] * len(current_capacities)
    for thermoelectric, capacity in enumerate(current_capacities):

        current_capacity = capacity

        while current_capacity < 0:
            thermoelectric_circuits = [
                ci for ci, th in enumerate(chromosome) if th == thermoelectric
            ]

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


def select_chromosomes(fitness_scores: list[tuple[int, int]], amount: int):
    return sorted(fitness_scores, key=lambda x: x[1])[:amount]


def mutatate(
    chromosome: list[int],
    capacities: list[int],
    P: list[list[int]],
    mutation: str = "single_point",
):

    if mutation == "single_point":
        index = random.randint(0, len(chromosome) - 1)
        chromosome[index] = random.randint(len(capacities))
    elif mutation == "multiple_points":
        index_amount = random.randint(0, len(chromosome) // 2)
        for _ in index_amount:
            index = random.randint(len(chromosome))
            chromosome[index] = random.randint(0, len(capacities) - 1)
    elif mutation == "swap":
        index_1 = random.randint(0, len(chromosome) - 1)
        index_2 = random.randint(0, len(chromosome) - 1)
        chromosome[index_1], chromosome[index_2] = (
            chromosome[index_2],
            chromosome[index_1],
        )
    elif mutation == "rotation":
        if len(chromosome) >= 2:
            index = random.randint(1, len(chromosome) - 2)
            chromosome = chromosome[index:] + chromosome[: index - 1]

    if is_invalid(chromosome, capacities, P):
        repair_chromosome(chromosome)


def genetic_algorithm(
    P: list[list[int]],
    capacities: list[int],
    generations: int,
    pop_size: int,
    circuits: int,
    mutation_rate: float = 0,
    ft=fitness,
):

    population = generate_population(P, capacities, circuits, pop_size)

    best_chromosome = None
    best_fitness = float("inf")

    for generation in range(generations):
        fitness_scores = [
            (chromosome, fitness(chromosome)) for chromosome in population
        ]

        for chromosome, score in fitness_scores:
            if score < best_fitness:
                best_fitness = score
                best_chromosome = chromosome[:]

        selection = select_chromosomes(fitness_scores, pop_size)
        random.shuffle(selection)

        population = []
        for i in range(pop_size):
            parent_1 = selection[i]

            for _ in range(3):
                parent_2 = random.choice(selection)
                population.append(crossover(parent_1, parent_2, capacities, P))

        for i in range(len(population)):
            if random.random() < mutation_rate:
                mutatate(population[i], capacities, P)

    return best_chromosome, best_fitness
