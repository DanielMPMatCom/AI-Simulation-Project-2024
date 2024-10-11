from numpy import random

class RandomGenerator:
    """
    A class used to generate random numbers using random module of numpy.

    Attributes
    ----------
    seed : int
        The seed for the random number generator.
    map_generator_seed : int
        The seed for the map generator's random state.
    random : numpy.random.Generator
        The random number generator instance.
    state : numpy.random.RandomState
        The random state for the map generator.
    """

    def __init__(self, seed, map_generator_seed = 42):
        self.seed = seed
        self.random = random.default_rng(seed)

        # random.seed(map_generator_seed)
        self.map_generator_seed = map_generator_seed
        self.state = random.RandomState(map_generator_seed)

    def integers(self, low, high):
        return self.random.integers(low, high)

    def uniform(self, low, high):
        return self.random.uniform(low, high)

    def choice(self, a):
        return self.random.choice(a)

    def shuffle(self, a):
        return self.random.shuffle(a)
    
    def permutation(self,a):
        return self.random.permutation(a)

    def rand(self, *args):
        return self.random.random(tuple(*args))