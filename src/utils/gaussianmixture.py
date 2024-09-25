import numpy as np

class DailyElectricityConsumption:
    """
    This class models the daily electricity consumption using a mixture of two Gaussian distributions.
    One peak represents the morning (5 am to 9 am) and another larger peak represents the evening (5 pm to 9 pm).
    """
    
    def __init__(self, mean_morning: float, std_morning: float, mean_evening: float, std_evening: float, weight_evening: float) -> None:
        """
        Initializes the Gaussian mixture model with means, standard deviations, and weights for morning and evening peaks.
        
        :param mean_morning: Mean consumption for the morning peak (5 am to 9 am).
        :param std_morning: Standard deviation for the morning peak.
        :param mean_evening: Mean consumption for the evening peak (5 pm to 9 pm).
        :param std_evening: Standard deviation for the evening peak.
        :param weight_evening: Weight of the evening peak in comparison to the morning peak (higher weight = larger evening peak).
        """
        self.mean_morning = mean_morning
        self.std_morning = std_morning
        self.mean_evening = mean_evening
        self.std_evening = std_evening
        self.weight_evening = weight_evening
    
    def generate(self, size: int = 24) -> np.ndarray:
        """
        Generates an array representing hourly electricity consumption for a day based on the Gaussian mixture.
        
        :param size: Number of hours to generate (default is 24 for a full day).
        :return: An array of electricity consumption values for each hour.
        """
        hours = np.zeros(size)
        
        # Morning peak: 5 am to 9 am (hours 5 to 8)
        morning_hours = np.random.normal(loc=self.mean_morning, scale=self.std_morning, size=4)
        hours[5:9] = morning_hours
        
        # Evening peak: 5 pm to 9 pm (hours 17 to 20)
        evening_hours = np.random.normal(loc=self.mean_evening, scale=self.std_evening, size=4)
        hours[17:21] = evening_hours * self.weight_evening
        
        return hours
    
    def generate_with_params(self, mean_morning: float, std_morning: float, mean_evening: float, std_evening: float, weight_evening: float, size: int = 24) -> np.ndarray:
        """
        Generates hourly electricity consumption for a day using custom parameters for the Gaussian mixture.
        
        :param mean_morning: Mean consumption for the morning peak (5 am to 9 am).
        :param std_morning: Standard deviation for the morning peak.
        :param mean_evening: Mean consumption for the evening peak (5 pm to 9 pm).
        :param std_evening: Standard deviation for the evening peak.
        :param weight_evening: Weight of the evening peak.
        :param size: Number of hours to generate (default is 24 for a full day).
        :return: An array of electricity consumption values for each hour.
        """
        hours = np.zeros(size)
        
        # Morning peak: 5 am to 9 am
        morning_hours = np.random.normal(loc=mean_morning, scale=std_morning, size=4)
        hours[5:9] = morning_hours
        
        # Evening peak: 5 pm to 9 pm
        evening_hours = np.random.normal(loc=mean_evening, scale=std_evening, size=4)
        hours[17:21] = evening_hours * weight_evening
        
        return hours
    
    def get_mean_morning(self) -> float:
        """
        Returns the mean of the morning consumption peak.
        """
        return self.mean_morning
    
    def get_std_morning(self) -> float:
        """
        Returns the standard deviation of the morning consumption peak.
        """
        return self.std_morning
    
    def get_mean_evening(self) -> float:
        """
        Returns the mean of the evening consumption peak.
        """
        return self.mean_evening
    
    def get_std_evening(self) -> float:
        """
        Returns the standard deviation of the evening consumption peak.
        """
        return self.std_evening
    
    def get_weight_evening(self) -> float:
        """
        Returns the weight factor of the evening consumption peak.
        """
        return self.weight_evening
