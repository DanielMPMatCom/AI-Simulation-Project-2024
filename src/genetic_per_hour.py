from src.mutations import single_point_0, single_point_1, single_point_2, swap_points, multiple_points, rotation
import random


def assign_thermoelectric_to_block(
    block: int,
    time: int,
    chromosome: list[list[int]],
    capacities: list[int],
    get_cost_thermoelectric_to_block: callable,
):

    valid_thermoelectrics = [
        th
        for th in range(len(capacities))
        if capacities[th] >= get_cost_thermoelectric_to_block(th, block, time)
    ]

    assigned_thermoelectric = (
        random.choice(valid_thermoelectrics) if valid_thermoelectrics else -1
    )

    chromosome[block][time] = assigned_thermoelectric

    if assigned_thermoelectric != -1:
        capacities[assigned_thermoelectric] -= get_cost_thermoelectric_to_block(
            assigned_thermoelectric, block, time
        )


def is_invalid(
    chromosome: list[list[int]],
    capacities: list[int],
    get_cost_thermoelectric_to_block: callable,
):

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

    current_capacities = capacities[:]

    for time in range(24):
        for block, thermoelectric in enumerate(chromosome[time]):

            current_capacities[thermoelectric] -= get_cost_thermoelectric_to_block(
                thermoelectric, block, time
            )

    waiting = []

    for thermoelectric, capacity in enumerate(current_capacities):

        current_capacity = capacity

        while current_capacity < 0:

            thermoelectric_blocks = []
            for bi in range(len(chromosome)):
                thermoelectric_blocks += [
                    (bi, time)
                    for time, th in enumerate(chromosome[bi])
                    if th == thermoelectric
                ]

            point = random.randint(0, len(thermoelectric_blocks) - 1)
            block = thermoelectric_blocks[point][0]
            time = thermoelectric_blocks[point][1]
            current_capacity += get_cost_thermoelectric_to_block(
                thermoelectric, block, time
            )
            chromosome[block][time] = -1
            waiting.append((block, time))

        current_capacities[thermoelectric] = current_capacity

    random.shuffle(waiting)

    for block, time in waiting:
        assign_thermoelectric_to_block(
            block, time, chromosome, capacities, get_cost_thermoelectric_to_block
        )

    waiting = [(bi, time) for bi in range(len(chromosome[time])) for time in range(24)]

    random.shuffle(waiting)
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

    population = []
    for _ in range(pop_size):

        chromosome = [[-1] * 24 for _ in range(blocks)]
        remaining_capacities = capacities[:]

        waiting = [(bi, ti) for bi in range(blocks) for ti in range(24)]
        random.shuffle(waiting)

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

    chromosome = [[-1] * 24 for _ in range(len(parent_1))]

    parent_time = [random.randint(0, len(parent_1) - 1) for _ in range(24)]
    first_parent = [random.random() < 0.5 for _ in range(len(parent_1))]

    for time in range(24):
        for block in range(len(parent_1)):
            if (block <= parent_time[time] and first_parent[block]) or (block > parent_time[time] and not first_parent[block]):
                chromosome[block][time] = parent_1[block][time]
            else:
                chromosome[block][time] = parent_2[block][time]

    if is_invalid(chromosome, capacities, get_cost_thermoelectric_to_block):
        repair_chromosome(chromosome, capacities, get_cost_thermoelectric_to_block)

    return chromosome


def select_chromosomes(fitness_scores: list[tuple[int, int]], amount: int):
    return [
        chromosome
        for chromosome, _ in sorted(fitness_scores, key=lambda x: x[1])[:amount]
    ]

def mutate(
    get_cost_thermoelectric_to_block:callable,
    chromosome: list[list[int]],
    capacities: list[int],
    mutation: str = "single_point_0",
):

    if mutation == "single_point_0":
        single_point_0(chromosome, capacities)

    elif mutation == "single_point_1":
        single_point_1(chromosome, capacities)

    elif mutation == "single_point_2":
        single_point_2(chromosome, capacities)

    elif mutation == "multiple_points":
        multiple_points(chromosome, capacities)

    elif mutation == "swap_points":
        swap_points(chromosome)

    elif mutation == "rotation" and len(chromosome) >= 2:
        rotation(chromosome)

    if is_invalid(chromosome, capacities, get_cost_thermoelectric_to_block):
        repair_chromosome(chromosome, capacities, get_cost_thermoelectric_to_block)


def create_new_population(
    get_cost_thermoelectric_to_block: callable,
    selection: list[list[list[int]]],
    pop_size: int,
):
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

    population = generate_population(
        get_cost_thermoelectric_to_block, capacities, blocks, pop_size
    )

    best_chromosome = None
    best_fitness = 0

    for _ in range(generations):
        fitness_scores = [(chromosome, ft(chromosome)) for chromosome in population]

        for chromosome, score in fitness_scores:
            if score > best_fitness:
                best_fitness = score
                best_chromosome = [row[:] for row in chromosome]

        selection = select_chromosomes(fitness_scores, pop_size)

        population = create_new_population(
            get_cost_thermoelectric_to_block,
            selection,
            pop_size
        )

        for i in range(len(population)):
            if random.random() < mutation_rate:
                mutate(population[i], capacities, get_cost_thermoelectric_to_block)

    return best_chromosome, best_fitness


def cost(thermoelectric, block, time):
    return (abs(thermoelectric - block) + 1) if thermoelectric != -1 else 0


def ft(chromosome):
    result = 1
    for block in chromosome:
        for ti in block:
            if ti == -1:
                continue

            result += 1

    return result


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
