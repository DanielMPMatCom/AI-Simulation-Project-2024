import random


def assign_thermoelectric_to_circuit(
    circuit: int,
    chromosome: list[int],
    capacities: list[int],
    get_cost_thermoelectric_to_block: callable,
):
    """
    Assigns a thermoelectric generator to a specific circuit based on available capacities and costs.

    Parameters:
    circuit (int): The index of the circuit to which a thermoelectric generator is to be assigned.
    chromosome (list[int]): The list representing the chromosome where the assignment will be recorded.
    capacities (list[int]): The list of available capacities for each thermoelectric generator.
    get_cost_thermoelectric_to_block (callable): A function that takes the indices of a thermoelectric generator and a circuit,
                                                 and returns the cost of assigning that generator to the circuit.

    Returns:
    None: The function modifies the chromosome and capacities lists in place.
    """
    valid_thermoelectrics = [
        i
        for i in range(len(capacities))
        if capacities[i] >= get_cost_thermoelectric_to_block(i, circuit)
    ]
    assigned_thermoelectric = (
        random.choice(valid_thermoelectrics) if valid_thermoelectrics else -1
    )
    chromosome[circuit] = assigned_thermoelectric
    capacities[assigned_thermoelectric] -= get_cost_thermoelectric_to_block(
        assigned_thermoelectric, circuit
    )


def generate_population(
    get_cost_thermoelectric_to_block: callable,
    capacities: list[int],
    circuits: int,
    pop_size: int,
):
    """
    Generates a population of chromosomes for a genetic algorithm.
    Each chromosome represents a potential solution to the problem, where each gene
    in the chromosome corresponds to a circuit and its assigned thermoelectric block.
    Args:
        get_cost_thermoelectric_to_block (callable): A function that calculates the cost
            of assigning a thermoelectric block to a circuit.
        capacities (list[int]): A list of capacities for each thermoelectric block.
        circuits (int): The number of circuits to be assigned thermoelectric blocks.
        pop_size (int): The size of the population to generate.
    Returns:
        list[list[int]]: A list of chromosomes, where each chromosome is a list of integers
        representing the assigned thermoelectric blocks for each circuit.
    """
    population = []
    for _ in range(pop_size):
        chromosome = [-1] * circuits
        remaining_capacities = capacities[:]

        waiting = [i for i in range(circuits)]
        random.shuffle(waiting)

        for circuit in waiting:
            assign_thermoelectric_to_circuit(
                circuit,
                chromosome,
                remaining_capacities,
                get_cost_thermoelectric_to_block,
            )

        population.append(chromosome)
    return population


def crossover(
    parent_1: list[int],
    parent_2: list[int],
    capacities: list[int],
    get_cost_thermoelectric_to_block: callable,
):
    """
    Perform a crossover operation between two parent chromosomes to produce a new chromosome.
    Args:
        parent_1 (list[int]): The first parent chromosome.
        parent_2 (list[int]): The second parent chromosome.
        capacities (list[int]): A list of capacities used for validation and repair.
        get_cost_thermoelectric_to_block (callable): A function to calculate the cost of thermoelectric to block.
    Returns:
        list[int]: The resulting chromosome after crossover and potential repair.
    """
    position = random.randint(1, len(parent_1) - 1)
    chromosome = parent_1[:position] + parent_2[position:]

    if is_invalid(chromosome, capacities, get_cost_thermoelectric_to_block):
        repair_chromosome(chromosome, capacities, get_cost_thermoelectric_to_block)

    return chromosome


def crossover_uniform(
    parent_1: list[int],
    parent_2: list[int],
    capacities: list[int],
    get_cost_thermoelectric_to_block: callable,
    prob_p1: float = 0.5,
    prob_p2: float = 0.5,
):
    """
    Perform a uniform crossover between two parent chromosomes to generate a new chromosome.
    Args:
        parent_1 (list[int]): The first parent chromosome.
        parent_2 (list[int]): The second parent chromosome.
        capacities (list[int]): A list of capacities used for validation and repair.
        get_cost_thermoelectric_to_block (callable): A function to calculate the cost of assigning a thermoelectric unit to a block.
        prob_p1 (float, optional): Probability of selecting a gene from parent_1. Defaults to 0.5.
        prob_p2 (float, optional): Probability of selecting a gene from parent_2. Defaults to 0.5.
    Returns:
        list[int]: The new chromosome generated from the crossover.
    """
    chromosome = [-1] * len(parent_1)

    for i in range(len(parent_1)):
        prob = random.random()

        if prob <= prob_p1:
            chromosome[i] = parent_1[i]
        elif prob <= prob_p1 + prob_p2:
            chromosome[i] = parent_2[i]
        else:
            chromosome[i] = random.randint(len(capacities) - 1)

    if is_invalid(chromosome, capacities, get_cost_thermoelectric_to_block):
        repair_chromosome(chromosome, capacities, get_cost_thermoelectric_to_block)

    return chromosome


def is_invalid(
    chromosome: list[int],
    capacities: list[int],
    get_cost_thermoelectric_to_block: callable,
):
    """
    Determines if a given chromosome configuration is invalid based on the capacities
    of thermoelectric blocks and the cost associated with each block.
    Args:
        chromosome (list[int]): A list representing the chromosome where each index 
                                corresponds to a circuit and the value at that index 
                                represents the assigned thermoelectric block.
        capacities (list[int]): A list of integers representing the initial capacities 
                                of each thermoelectric block.
        get_cost_thermoelectric_to_block (callable): A function that takes two arguments 
                                                     (thermoelectric, circuit) and returns 
                                                     the cost of assigning the thermoelectric 
                                                     block to the circuit.
    Returns:
        bool: True if the chromosome configuration is invalid (i.e., any thermoelectric 
              block's capacity goes below zero), False otherwise.
    """
    current_capacities = capacities[:]

    for circuit, thermoelectric in enumerate(chromosome):
        current_capacities[thermoelectric] -= get_cost_thermoelectric_to_block(
            thermoelectric, circuit
        )

    return any(capacity < 0 for capacity in current_capacities)


def repair_chromosome(
    chromosome: list[int],
    capacities: list[int],
    get_cost_thermoelectric_to_block: callable,
):
    """
    Repairs a chromosome by ensuring that the capacities of thermoelectric units are not exceeded.
    Args:
        chromosome (list[int]): A list representing the chromosome where each index is a circuit and the value is the assigned thermoelectric unit.
        capacities (list[int]): A list of integers representing the capacities of each thermoelectric unit.
        get_cost_thermoelectric_to_block (callable): A function that takes a thermoelectric unit and a circuit as arguments and returns the cost of assigning that thermoelectric unit to the circuit.
    Returns:
        None: The function modifies the chromosome in place to ensure that no thermoelectric unit exceeds its capacity.
    """

    current_capacities = capacities[:]
    for circuit, thermoelectric in enumerate(chromosome):
        current_capacities[thermoelectric] -= get_cost_thermoelectric_to_block(
            thermoelectric, circuit
        )

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
            current_capacity += get_cost_thermoelectric_to_block(
                thermoelectric, circuit
            )
            chromosome[circuit] = -1
            waiting.append(circuit)

        remaining_capacities[thermoelectric] = current_capacity

    random.shuffle(waiting)
    for circuit in waiting:
        assign_thermoelectric_to_circuit(
            circuit, chromosome, remaining_capacities, get_cost_thermoelectric_to_block
        )

    waiting = [i for i in range(len(chromosome)) if chromosome[i] == -1]
    random.shuffle(waiting)

    for circuit in range(len(chromosome)):
        assign_thermoelectric_to_circuit(
            circuit, chromosome, remaining_capacities, get_cost_thermoelectric_to_block
        )


def select_chromosomes(fitness_scores: list[tuple[int, int]], amount: int):
    """
    Selects a specified number of chromosomes based on their fitness scores.

    Args:
        fitness_scores (list[tuple[int, int]]): A list of tuples where each tuple contains a chromosome identifier and its corresponding fitness score.
        amount (int): The number of chromosomes to select.

    Returns:
        list[int]: A list of chromosome identifiers corresponding to the top 'amount' fitness scores.
    """
    return [th for th, _ in sorted(fitness_scores, key=lambda x: x[1])[:amount]]


def mutate(
    chromosome: list[int],
    capacities: list[int],
    get_cost_thermoelectric_to_block,
    mutation: str = "single_point",
):
    """
    Applies a mutation to a given chromosome based on the specified mutation type.
    Parameters:
    chromosome (list[int]): The chromosome to be mutated, represented as a list of integers.
    capacities (list[int]): A list of capacities used to determine valid mutation values.
    get_cost_thermoelectric_to_block (function): A function to calculate the cost of thermoelectric to block.
    mutation (str): The type of mutation to apply. Options are "single_point", "multiple_points", "swap", and "rotation". Default is "single_point".
    Returns:
    None: The function modifies the chromosome in place.
    Notes:
    - "single_point": Mutates a single gene in the chromosome.
    - "multiple_points": Mutates multiple genes in the chromosome.
    - "swap": Swaps two genes in the chromosome.
    - "rotation": Rotates a segment of the chromosome.
    - If the mutated chromosome is invalid, it will be repaired using the provided capacities and cost function.
    """

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
    elif mutation == "rotation" and len(chromosome) >= 2:
        index = random.randint(1, len(chromosome) - 2)
        chromosome = chromosome[index:] + chromosome[: index - 1]

    if is_invalid(chromosome, capacities, get_cost_thermoelectric_to_block):
        repair_chromosome(chromosome, capacities, get_cost_thermoelectric_to_block)


def genetic_algorithm(
    get_cost_thermoelectric_to_block,
    capacities: list[int],
    generations: int,
    pop_size: int,
    circuits: int,
    mutation_rate: float,
    ft: callable,
):
    """
    Executes a genetic algorithm to optimize a given problem.
    Args:
        get_cost_thermoelectric_to_block (callable): Function to calculate the cost of thermoelectric to block.
        capacities (list[int]): List of capacities for each circuit.
        generations (int): Number of generations to run the algorithm.
        pop_size (int): Size of the population.
        circuits (int): Number of circuits.
        mutation_rate (float): Probability of mutation occurring in a chromosome.
        ft (callable): Fitness function to evaluate the chromosomes.
    Returns:
        tuple: A tuple containing the best chromosome and its fitness score.
    """

    population = generate_population(
        get_cost_thermoelectric_to_block, capacities, circuits, pop_size
    )

    best_chromosome = None
    best_fitness = float("inf")

    for _ in range(generations):
        fitness_scores = [(chromosome, ft(chromosome)) for chromosome in population]

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
                population.append(
                    crossover(
                        parent_1, parent_2, capacities, get_cost_thermoelectric_to_block
                    )
                )

        for i in range(len(population)):
            if random.random() < mutation_rate:
                mutate(population[i], capacities, get_cost_thermoelectric_to_block)

    return best_chromosome, best_fitness


def get_cost_thermoelectric_to_block(thermoelectric: int, block: int):
    """
    Calculate the cost of connecting a thermoelectric unit to a block.

    Args:
        thermoelectric (int): The index of the thermoelectric unit.
        block (int): The index of the block.

    Returns:
        int: The cost of connecting the specified thermoelectric unit to the specified block.
    """
    M = [[1, 1, 1], [1, 1, 1]]
    return M[thermoelectric][block]


A = [100, 5000]


def fx(x):
    y = 0
    for i, t in enumerate(x):
        y += get_cost_thermoelectric_to_block(t, i)
    return A[t] - y


print(genetic_algorithm(get_cost_thermoelectric_to_block, A, 100, 10, 3, 0, ft=fx))
