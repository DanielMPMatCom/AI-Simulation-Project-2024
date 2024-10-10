from scipy.stats import weibull_min
import numpy as np
import matplotlib.pyplot as plt


class Weibull:
    """
    Weibull distribution.
    Used to describe the life of a product.
    alpha is the scale parameter and beta is the shape parameter.
    """

    def __init__(self, scale: float, shape: float):
        """
        scale: scale parameter
        shape: shape parameter
        scale > 0, shape > 0
        """
        if scale <= 0 or shape <= 0:
            raise ValueError("scale and shape must be greater than 0")

        self.scale = scale
        self.shape = shape

    def generate(self):
        """
        Used to generate a random number from the Weibull distribution for class instances
        """
        return self.generate_with_params(scale=self.scale, shape=self.shape)

    def generate_with_params(self, scale, shape):
        """
        Used to generate a random number from the Weibull distribution
        """
        if shape <= 0 or scale <= 0:
            raise ValueError("alpha and scale must be greater than 0")
        return weibull_min.rvs(self.shape, scale=self.scale)

    def get_shape(self):
        """
        Un valor α < 1 indica que la tasa de fallos decrece con el tiempo.
        Cuando α = 1, la tasa de fallos es constante en el tiempo.
        Un valor α > 1 indica que la tasa de fallos crece con el tiempo.
        """
        return self.shape

    def get_scale(self):
        """
        El parámetro λ es un factor de escala que estira o comprime la distribución.
        Proporciona una estimación de la "vida característica" del producto,
        que es el tiempo en el que el 63,2% de los equipos habrá fallado.
        """
        return self.scale

    @staticmethod
    def fit(data):
        """
        Fit the Weibull distribution to the data and return the estimated shape and scale parameters.
        """
        shape, loc, scale = weibull_min.fit(data, floc=0)
        return scale, shape

    @staticmethod
    def from_data(data):
        """
        Create a Weibull instance by fitting the distribution to the provided data.
        """
        scale, shape = Weibull.fit(data)
        return Weibull(scale, shape)


if __name__ == "__main__":

    data = np.array([40, 100])
    weibull_instance = Weibull.from_data(data)
    print(f"Estimated scale: {weibull_instance.get_scale()}")
    print(f"Estimated shape: {weibull_instance.get_shape()}")
    random_value = weibull_instance.generate()
    print(f"Generated random value from Weibull distribution: {random_value}")

    x = np.linspace(0, 200, 1000)

    pdf = weibull_min.pdf(
        x, weibull_instance.get_shape(), scale=weibull_instance.get_scale()
    )

    plt.plot(x, pdf, label="Weibull PDF")

    plt.scatter(data, [0, 0], color="red", label="Data points")

    plt.xlabel("Value")
    plt.ylabel("Probability Density")
    plt.title("Weibull Distribution Fit")
    plt.legend()

    plt.show()

    cont = 0
    ceil = 0
    floor = 0
    instance = Weibull(79.3324187138614, 2.618558429048514)
    for _ in range(100000):
        value = instance.generate()
        if value > 100:
            ceil += 1

        elif value < 40:
            floor += 1
    cont = ceil + floor
    print(
        f"Percentage of values outside the range: {cont/100000}%, with {cont} values, where {ceil} are greater({ceil/100000}%) than 100 and {floor} are less than 40({floor/100000}%)"
    )
