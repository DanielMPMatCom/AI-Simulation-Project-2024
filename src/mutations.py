import random


def single_point_0(
    chromosome: list[list[int]],
    capacities: list[int],
):
    """
    Perform a single-point mutation on a given chromosome.

    This function selects a random index in the chromosome and a random time slot,
    then assigns a random capacity value to that time slot.

    Args:
        chromosome (list[list[int]]): The chromosome to be mutated, represented as a list of lists of integers.
        capacities (list[int]): A list of possible capacity values.

    Returns:
        None: The function modifies the chromosome in place.
    """
    index = random.randint(0, len(chromosome) - 1)
    time = random.randint(0, 23)
    chromosome[index][time] = random.randint(0, len(capacities) - 1)


def single_point_1(
    chromosome: list[list[int]],
    capacities: list[int],
):
    """
    Performs a single-point mutation on a given chromosome.

    This function selects a random index in the chromosome and mutates the values
    at that index for each time slot (0-23) by assigning a random value from the
    range of capacities.

    Args:
        chromosome (list[list[int]]): A 2D list representing the chromosome to be mutated.
        capacities (list[int]): A list of capacities used to determine the range of mutation values.

    Returns:
        None: The function modifies the input chromosome in place.
    """
    index = random.randint(0, len(chromosome) - 1)
    for time in range(24):
        chromosome[index][time] = random.randint(0, len(capacities) - 1)


def single_point_2(
    chromosome: list[list[int]],
    capacities: list[int],
):
    """
    Perform a single-point mutation on a given chromosome.

    This function iterates over each hour of the day (0 to 23) and randomly selects
    an index in the chromosome to mutate. For the selected index, it assigns a random
    value from 0 to the length of the capacities list minus one.

    Args:
        chromosome (list[list[int]]): A 2D list representing the chromosome to be mutated.
        capacities (list[int]): A list of capacities used to determine the range of mutation values.

    Returns:
        None: The function modifies the chromosome in place.
    """
    for time in range(24):
        index = random.randint(len(chromosome) - 1)
        chromosome[index][time] = random.randint(0, len(capacities) - 1)


def multiple_points(
    chromosome: list[list[int]],
    capacities: list[int],
):
    """
    Applies multiple point mutations to a given chromosome.

    This function randomly selects a number of points within the chromosome and 
    mutates them by assigning a new random value based on the capacities list.

    Parameters:
    chromosome (list[list[int]]): A 2D list representing the chromosome to be mutated.
    capacities (list[int]): A list of capacities used to determine the new values for mutation.

    Returns:
    None: The function modifies the chromosome in place.
    """
    index_amount = random.randint(0, len(chromosome) // 2 * random.randint(1, 12))
    for _ in index_amount:
        index = random.randint(len(chromosome) - 1)
        time = random.randint(0, 23)
        chromosome[index][time] = random.randint(len(capacities) - 1)


def swap_points(
    chromosome: list[list[int]],
):
    """
    Randomly swaps points within a chromosome.
    This function takes a chromosome, which is a list of lists of integers, and performs a series of random swaps
    between points in the chromosome. The number of swaps is determined randomly based on the length of the chromosome.
    Args:
        chromosome (list[list[int]]): A list of lists where each sublist represents a chromosome with integer values.
    Returns:
        None: The function modifies the input chromosome in place.
    """
    index_amount = random.randint(0, len(chromosome) // 2 * random.randint(1, 12))
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
    chromosome: list[list[int]],
):
    """
    Perform a rotation mutation on a given chromosome.

    This function takes a chromosome, which is a list of lists of integers, and performs a rotation mutation.
    For each hour in a 24-hour period, it randomly selects an index within the chromosome and either rotates
    the elements to the left or right based on a random probability.

    Args:
        chromosome (list[list[int]]): The chromosome to be mutated, represented as a list of lists of integers.

    Returns:
        None: The function modifies the chromosome in place.
    """
    for time in range(24):
        index = random.randint(1, len(chromosome) - 2)
        if random.random() <= 0.5:
            chromosome = chromosome[index:][time] + chromosome[: index - 1][time]
        else:
            chromosome = chromosome[: index - 1][time] + chromosome[index:][time]
