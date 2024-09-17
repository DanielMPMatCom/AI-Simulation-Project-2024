import random as rnd


class Weibull:
    """
    Weibull distribution.
    Used to describe the life of a product.
    alpha is the scale parameter and beta is the shape parameter.
    """

    def __init__(self, alpha: float, lambd: float):
        """
        alpha: scale parameter
        lambd: shape parameter
        alpha > 0, lambd > 0
        """
        if alpha <= 0 or lambd <= 0:
            raise ValueError("alpha and lambd must be greater than 0")

        self.scale = alpha
        self.shape = lambd

    def generate(self):
        """
        Used to generate a random number from the Weibull distribution for class instances
        """
        return rnd.weibullvariate(self.scale, self.shape)

    def generate_with_params(alpha, lambd):
        """
        Used to generate a random number from the Weibull distribution
        """
        if alpha <= 0 or lambd <= 0:
            raise ValueError("alpha and lambd must be greater than 0")
        return rnd.weibullvariate(alpha, lambd)

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


"""
Random Lib Code:

 def weibullvariate(self, alpha, beta):
        # Jain, pg. 499; bug fix courtesy Bill Arms
        u = 1.0 - self.random()
        return alpha * (-_log(u)) ** (1.0 / beta)
"""
