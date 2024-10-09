import random as rnd

import numpy as np


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
        return rnd.weibullvariate(self.scale, self.shape)

    def generate_with_params(self, alpha, scale):
        """
        Used to generate a random number from the Weibull distribution
        """
        if alpha <= 0 or scale <= 0:
            raise ValueError("alpha and scale must be greater than 0")
        return rnd.weibullvariate(alpha, scale)

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
