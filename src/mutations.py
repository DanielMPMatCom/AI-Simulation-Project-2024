import random

def single_point_0(
        chromosome:list[list[int]],
        capacities:list[int],
):
    index = random.randint(0, len(chromosome) - 1)
    time = random.randint(0, 23)
    chromosome[index][time] = random.randint(0, len(capacities) - 1)

def single_point_1(
        chromosome:list[list[int]],
        capacities:list[int],
):
    index = random.randint(0, len(chromosome) - 1)
    for time in range(24):
        chromosome[index][time] = random.randint(0, len(capacities) - 1)

def single_point_2(
        chromosome:list[list[int]],
        capacities:list[int],  
):
    for time in range(24):
        index = random.randint(len(chromosome) - 1)
        chromosome[index][time] = random.randint(0, len(capacities) - 1)
    
def multiple_points(
        chromosome:list[list[int]],
        capacities:list[int],  
):
    index_amount = random.randint(
        0, len(chromosome) // 2 * random.randint(1, 12)
    )
    for _ in index_amount:
        index = random.randint(len(chromosome) - 1)
        time = random.randint(0, 23)
        chromosome[index][time] = random.randint(len(capacities) - 1)

def swap_points(
        chromosome:list[list[int]],  
):
    index_amount = random.randint(
        0, len(chromosome) // 2 * random.randint(1, 12)
    )
    for _ in index_amount:
        index_1 = random.randint(0, len(chromosome) - 1)
        index_2 = random.randint(0, len(chromosome) - 1)
        time_1 = random.randint(0, 23)
        time_2 = random.randint(0, 23)

        chromosome[index_1][time_1], chromosome[index_2][time_2] = (
            chromosome[index_2][time_2],
            chromosome[index_1][time_1],
        )

def rotation(
        chromosome:list[list[int]],
):
    for time in range(24):
        index = random.randint(1, len(chromosome) - 2)
        if random.random() <= 0.5:
            chromosome = chromosome[index:][time] + chromosome[: index - 1][time]
        else:
            chromosome = chromosome[: index - 1][time] + chromosome[index:][time]