from scipy.stats import lognorm
from math import log, exp, sqrt


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
        return self.generate_with_params(mu=self.mu, sigma=self.sigma)

    def generate_with_params(self, mu, sigma):
        """
        Used to generate a random number from the log normal distribution
        sigma must be greater than 0
        """
        if sigma <= 0:
            raise ValueError("sigma must be greater than 0")
        return lognorm.rvs(s=sigma, scale=mu)

    def get_mu(self):
        """
        Returns the mean of the log normal distribution
        """
        return self.mu

    def get_sigma(self):
        """
        Returns the standard deviation of the log normal distribution
        """


def get_params_for_range(min_val, max_val):
    """
    Returns the mu and sigma parameters for the log normal distribution
    such that the generated values are within the specified range.
    """
    if min_val <= 0 or max_val <= 0:
        raise ValueError("min_val and max_val must be greater than 0")
    sigma = (log(max_val) - log(min_val)) / 4
    mu = exp((log(min_val) + log(max_val)) / 2)

    return mu, sigma


def get_params_for_mean_deviation(mean, deviation):
    """
    Returns the mu and sigma parameters for the log normal distribution
    such that the generated values have the specified mean and deviation.
    """
    mu = log(mean / sqrt(1 + (deviation**2) / (mean**2)))
    sigma = sqrt(log(1 + (deviation**2) / (mean**2)))

    return mu, sigma


# mu, sigma = get_params_for_range(7, 15)
# print(f"Mu: {mu}, Sigma: {sigma}")


# import matplotlib.pyplot as plt
# import numpy as np

# # Generate samples
# lognormal_dist = LogNormal(mu, sigma)
# samples = [lognormal_dist.generate() for _ in range(1000)]

# plt.hist(samples, bins=50, density=True, alpha=0.6, color="g")

# xmin, xmax = plt.xlim()
# x = np.linspace(xmin, xmax, 100)
# p = lognorm.pdf(x, s=sigma, scale=mu)
# plt.plot(x, p, "k", linewidth=2)

# title = f"Fit results: mu = {mu}, sigma = {sigma}"
# plt.title(title)
# plt.show()
