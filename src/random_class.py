from numpy import random

class RandomGenerator:
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

    def rand(self, *args):
        return self.random.random(tuple(*args))