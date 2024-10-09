import random as rnd


class LogNormal:
    def __init__(self, mu, sigma):
        """
        LogNormal Random Variable
        Used to describe time to repair a system
        mu: MEAN
        sigma: DEVIATION
        """
        if sigma <= 0:
            raise ValueError("sigma must be greater than 0")
        self.mu = mu
        self.sigma = sigma

    def generate(self):
        """
        Used to generate a random number from the log normal distribution for class instances
        """
        return rnd.lognormvariate(self.mu, self.sigma)

    def generate_with_params(self, mu, sigma):
        """
        Used to generate a random number from the log normal distribution
        sigma must be greater than 0
        """
        if sigma <= 0:
            raise ValueError("sigma must be greater than 0")
        return rnd.lognormvariate(mu, sigma)

    def get_mu(self):
        """
        Returns the mean of the log normal distribution
        """
        return self.mu

    def get_sigma(self):
        """
        Returns the standard deviation of the log normal distribution
        """
        return self.sigma


'''
Random Lib Code
def lognormvariate(self, mu, sigma):
        """Log normal distribution.
        If you take the natural logarithm of this distribution, you'll get a
        normal distribution with mean mu and standard deviation sigma.
        mu can have any value, and sigma must be greater than zero.
        """
        return _exp(self.normalvariate(mu, sigma))
'''
