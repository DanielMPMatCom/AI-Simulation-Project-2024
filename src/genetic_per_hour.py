from src.mutations import (
    single_point_0,
    single_point_1,
    single_point_2,
    swap_points,
    multiple_points,
    rotation,
)
from src.simulation_constants import RANDOM


def assign_thermoelectric_to_block(
    block: int,
    time: int,
    chromosome: list[list[int]],
    capacities: list[int],
    get_cost_thermoelectric_to_block: callable,
):
    """
    Assigns a thermoelectric unit to a specific block at a given time based on available capacities and costs.
    Parameters:
    block (int): The block to which the thermoelectric unit is to be assigned.
    time (int): The time slot for the assignment.
    chromosome (list[list[int]]): The chromosome representing the assignment of thermoelectric units to blocks over time.
    capacities (list[int]): The list of available capacities for each thermoelectric unit.
    get_cost_thermoelectric_to_block (callable): A function that calculates the cost of assigning a thermoelectric unit to a block at a specific time.
    Returns:
    None: The function modifies the chromosome and capacities in place.
    """

    remaining_capacities = capacities[:]

    valid_thermoelectrics = [
        th
        for th in range(len(remaining_capacities))
        if remaining_capacities[th] >= get_cost_thermoelectric_to_block(th, block, time)
    ]

    assigned_thermoelectric = (
        RANDOM.choice(valid_thermoelectrics) if valid_thermoelectrics else -1
    )

    chromosome[block][time] = assigned_thermoelectric

    if assigned_thermoelectric != -1:
        remaining_capacities[
            assigned_thermoelectric
        ] -= get_cost_thermoelectric_to_block(assigned_thermoelectric, block, time)


def is_invalid(
    chromosome: list[list[int]],
    capacities: list[int],
    get_cost_thermoelectric_to_block: callable,
):
    """
    Checks if a given chromosome configuration is invalid based on the capacities of thermoelectric units.
    Args:
        chromosome (list[list[int]]): A 2D list where each sublist represents a block and contains integers
                                      representing thermoelectric units assigned to that block over time.
        capacities (list[int]): A list of integers representing the initial capacities of each thermoelectric unit.
        get_cost_thermoelectric_to_block (callable): A function that takes three arguments (thermoelectric, block, time)
                                                     and returns the cost of assigning the thermoelectric unit to the block at the given time.
    Returns:
        bool: True if the chromosome configuration is invalid (i.e., any thermoelectric unit's capacity goes below zero),
              False otherwise.
    """

    current_capacities = capacities[:]

    for block in range(len(chromosome)):
        for time, thermoelectric in enumerate(chromosome[block]):

            current_capacities[thermoelectric] -= get_cost_thermoelectric_to_block(
                thermoelectric, block, time
            )

    return any(capacity < 0 for capacity in current_capacities)


def repair_chromosome(
    chromosome: list[list[int]],
    capacities: list[int],
    get_cost_thermoelectric_to_block: callable,
):
    """
    Repairs a given chromosome by ensuring that the capacities of thermoelectric units
    are not exceeded for each time block.
    Args:
        chromosome (list[list[int]]): A 2D list representing the assignment of thermoelectric
                                      units to blocks over 24 hours.
        capacities (list[int]): A list of initial capacities for each thermoelectric unit.
        get_cost_thermoelectric_to_block (callable): A function that calculates the cost of
                                                     assigning a thermoelectric unit to a block
                                                     at a specific time.
    Returns:
        None: The function modifies the chromosome in place to ensure valid assignments.
    """

    current_capacities = capacities[:]

    for time in range(24):
        for block, thermoelectric in enumerate(chromosome[time]):

            current_capacities[thermoelectric] -= get_cost_thermoelectric_to_block(
                thermoelectric, block, time
            )

    waiting = []

    for thermoelectric, capacity in enumerate(current_capacities):

        current_capacity = capacity

        if current_capacity < 0:
            thermoelectric_blocks = []
            for bi in range(len(chromosome)):
                thermoelectric_blocks += [
                    (bi, time)
                    for time, th in enumerate(chromosome[bi])
                    if th == thermoelectric
                ]

            RANDOM.shuffle(thermoelectric_blocks)

            for block, time in thermoelectric_blocks:

                if current_capacity >= 0:
                    break

                current_capacity += get_cost_thermoelectric_to_block(
                    thermoelectric, block, time
                )

                chromosome[block][time] = -1

                waiting.append((block, time))

        current_capacities[thermoelectric] = current_capacity

    RANDOM.shuffle(waiting)

    for block, time in waiting:
        assign_thermoelectric_to_block(
            block, time, chromosome, capacities, get_cost_thermoelectric_to_block
        )

    waiting = [(bi, time) for bi in range(len(chromosome[time])) for time in range(24)]

    RANDOM.shuffle(waiting)
    for block, time in waiting:
        assign_thermoelectric_to_block(
            block, time, chromosome, capacities, get_cost_thermoelectric_to_block
        )


def generate_population(
    get_cost_thermoelectric_to_block: callable,
    capacities: list[int],
    blocks: int,
    pop_size: int,
):
    """
    Generates a population of chromosomes for a genetic algorithm.
    Each chromosome represents a schedule of thermoelectric block assignments over 24 hours.
    Args:
        get_cost_thermoelectric_to_block (callable): A function that calculates the cost of assigning a thermoelectric unit to a block.
        capacities (list[int]): A list of capacities for each thermoelectric unit.
        blocks (int): The number of blocks to be scheduled.
        pop_size (int): The size of the population to generate.
    Returns:
        list[list[list[int]]]: A list of chromosomes, where each chromosome is a 2D list representing block assignments over 24 hours.
    """

    population = []
    for _ in range(pop_size):

        chromosome = [[-1] * 24 for _ in range(blocks)]
        remaining_capacities = capacities[:]

        waiting = [(bi, ti) for bi in range(blocks) for ti in range(24)]
        RANDOM.shuffle(waiting)

        for block, time in waiting:
            assign_thermoelectric_to_block(
                block,
                time,
                chromosome,
                remaining_capacities,
                get_cost_thermoelectric_to_block,
            )

        population.append(chromosome)
    return population


def crossover(
    parent_1: list[list[int]],
    parent_2: list[list[int]],
    capacities: list[int],
    get_cost_thermoelectric_to_block: callable,
):
    """
    Perform a crossover operation between two parent chromosomes to produce a new chromosome.
    Args:
        parent_1 (list[list[int]]): The first parent chromosome, represented as a list of lists of integers.
        parent_2 (list[list[int]]): The second parent chromosome, represented as a list of lists of integers.
        capacities (list[int]): A list of integers representing the capacities for each block.
        get_cost_thermoelectric_to_block (callable): A function that calculates the cost of thermoelectric energy for a given block.
    Returns:
        list[list[int]]: A new chromosome generated by combining the genes of the two parent chromosomes.
    """

    chromosome = [[-1] * 24 for _ in range(len(parent_1))]

    parent_time = [RANDOM.integers(0, len(parent_1) - 1) for _ in range(24)]
    first_parent = [RANDOM.uniform(0, 1) < 0.5 for _ in range(len(parent_1))]

    for time in range(24):
        for block in range(len(parent_1)):
            if (block <= parent_time[time] and first_parent[block]) or (
                block > parent_time[time] and not first_parent[block]
            ):
                chromosome[block][time] = parent_1[block][time]
            else:
                chromosome[block][time] = parent_2[block][time]

    if is_invalid(chromosome, capacities, get_cost_thermoelectric_to_block):
        repair_chromosome(chromosome, capacities, get_cost_thermoelectric_to_block)

    return chromosome


def select_chromosomes(fitness_scores: list[tuple[int, int]], amount: int):
    """
    Selects a specified number of chromosomes based on their fitness scores.

    Args:
        fitness_scores (list[tuple[int, int]]): A list of tuples where each tuple contains a chromosome and its corresponding fitness score.
        amount (int): The number of chromosomes to select.

    Returns:
        list[int]: A list of selected chromosomes with the highest fitness scores.
    """
    return [
        chromosome
        for chromosome, _ in sorted(fitness_scores, key=lambda x: x[1])[:amount]
    ]


def mutate(
    get_cost_thermoelectric_to_block: callable,
    chromosome: list[list[int]],
    capacities: list[int],
    mutation: str = "single_point_0",
):
    """
    Applies a mutation operation to a given chromosome based on the specified mutation type.
    Parameters:
    - get_cost_thermoelectric_to_block (callable): A function to get the cost of thermoelectric to block.
    - chromosome (list[list[int]]): The chromosome to be mutated, represented as a list of lists of integers.
    - capacities (list[int]): A list of capacities corresponding to the chromosome.
    - mutation (str): The type of mutation to apply. Options are:
        - "single_point_0"
        - "single_point_1"
        - "single_point_2"
        - "multiple_points"
        - "swap_points"
        - "rotation"
    Notes:
    - If the mutation type is "rotation", the chromosome must have at least 2 elements.
    - After mutation, the chromosome is checked for validity. If invalid, it is repaired using the provided capacities and cost function.
    """

    remaining_capacities = capacities[:]

    if mutation == "single_point_0":
        single_point_0(chromosome, remaining_capacities)

    elif mutation == "single_point_1":
        single_point_1(chromosome, remaining_capacities)

    elif mutation == "single_point_2":
        single_point_2(chromosome, remaining_capacities)

    elif mutation == "multiple_points":
        multiple_points(chromosome, remaining_capacities)

    elif mutation == "swap_points":
        swap_points(chromosome)

    elif mutation == "rotation" and len(chromosome) >= 2:
        rotation(chromosome)

    if is_invalid(chromosome, remaining_capacities, get_cost_thermoelectric_to_block):
        repair_chromosome(
            chromosome, remaining_capacities, get_cost_thermoelectric_to_block
        )


def create_new_population(
    get_cost_thermoelectric_to_block: callable,
    selection: list[list[list[int]]],
    capacities: list[int],
    pop_size: int,
):
    """
    Generates a new population using crossover from a given selection.

    Args:
        get_cost_thermoelectric_to_block (callable): A function to calculate the cost of thermoelectric to block.
        selection (list[list[list[int]]]): A list of selected individuals, where each individual is represented as a list of lists of integers.
        capacities (list[int]): A list of capacities for each thermoelectric plant.
        pop_size (int): The size of the population to generate.

    Returns:
        list: A new population generated by performing crossover on the selected individuals.
    """
    remaining_capacities = capacities[:]
    population = []
    for i in range(pop_size):
        parent_1 = selection[i]
        for _ in range(3):
            parent_2 = RANDOM.choice(selection)
            population.append(
                crossover(
                    parent_1,
                    parent_2,
                    remaining_capacities,
                    get_cost_thermoelectric_to_block,
                )
            )
    return population


def genetic_algorithm(
    get_cost_thermoelectric_to_block: callable,
    capacities: list[int],
    generations: int,
    pop_size: int,
    blocks: int,
    mutation_rate: float,
    ft: callable,
):
    """
    Executes a genetic algorithm to optimize a given problem.
    Args:
        get_cost_thermoelectric_to_block (callable): A function that calculates the cost of assigning a thermoelectric plant to a block.
        capacities (list[int]): A list of capacities for each thermoelectric plant.
        generations (int): The number of generations to run the algorithm.
        pop_size (int): The size of the population.
        blocks (int): The number of blocks to be assigned.
        mutation_rate (float): The probability of mutation occurring in a chromosome.
        ft (callable): A fitness function that evaluates the fitness of a chromosome.
    Returns:
        tuple: A tuple containing the best chromosome found and its corresponding fitness score.
    """

    population = generate_population(
        get_cost_thermoelectric_to_block, capacities, blocks, pop_size
    )

    best_chromosome = population[0]
    best_fitness = ft(population[0])

    for _ in range(generations):
        fitness_scores = [(chromosome, ft(chromosome)) for chromosome in population]

        for chromosome, score in fitness_scores:
            if score > best_fitness:
                best_fitness = score
                best_chromosome = [row[:] for row in chromosome]

        selection = select_chromosomes(fitness_scores, pop_size)

        population = create_new_population(
            get_cost_thermoelectric_to_block, selection, capacities, pop_size
        )

        for i in range(len(population)):
            if RANDOM.uniform(0, 1) < mutation_rate:
                mutate(population[i], capacities, get_cost_thermoelectric_to_block)

    return best_chromosome, best_fitness


def cost(thermoelectric, block, time):
    """
    Calculate the cost based on the difference between thermoelectric and block values.

    Args:
        thermoelectric (int): The value representing the thermoelectric measurement. If -1, it indicates no measurement.
        block (int): The value representing the block measurement.
        time (int): The time at which the measurement is taken (not used in the current implementation).

    Returns:
        int: The calculated cost. If thermoelectric is -1, the cost is 0. Otherwise, the cost is the absolute difference
        between thermoelectric and block, plus 1.
    """
    return (abs(thermoelectric - block) + 1) if thermoelectric != -1 else 0


def ft(chromosome):
    result = 1
    for block in chromosome:
        for ti in block:
            if ti == -1:
                continue

            result += 1

    return result


"""EXample
capacities = [24, 24, 24, 24]
generations = 5
pop_size = 1
blocks = 4
mutation_rate = 0

chromosome, fitness = genetic_algorithm(
    cost, capacities, generations, pop_size, blocks, mutation_rate, ft
)

print(fitness)

for t in range(len(chromosome) - 1):
    print(f"{t} {chromosome[t]}")
"""
