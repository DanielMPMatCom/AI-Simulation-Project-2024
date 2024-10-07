import numpy as np
import matplotlib.pyplot as plt

class DailyElectricityConsumptionBimodal:
    """
    This class models daily electricity consumption using a bimodal Gaussian distribution to represent
    two peaks of consumption: one in the morning and another larger one in the evening, plus a base consumption
    that includes random variability for non-peak hours.
    """
    
    def __init__(self, base_consumption: float, base_variability: float, mean_morning: float, std_morning: float, 
                 mean_evening: float, std_evening: float, weight_morning: float, weight_evening: float) -> None:
        """
        Initializes the model with base consumption and parameters for the morning and evening Gaussian peaks.
        
        :param base_consumption: Minimum consumption that applies to all hours.
        :param base_variability: Variability to add to the base consumption.
        :param mean_morning: Mean hour for the morning peak (e.g., 7 for 7 am).
        :param std_morning: Standard deviation for the morning peak.
        :param mean_evening: Mean hour for the evening peak (e.g., 19 for 7 pm).
        :param std_evening: Standard deviation for the evening peak.
        :param weight_morning: Weight factor for the morning peak.
        :param weight_evening: Weight factor for the evening peak.
        """
        self.base_consumption = base_consumption
        self.base_variability = base_variability
        self.mean_morning = mean_morning
        self.std_morning = std_morning
        self.mean_evening = mean_evening
        self.std_evening = std_evening
        self.weight_morning = weight_morning
        self.weight_evening = weight_evening
    
    def generate(self, size: int = 24) -> np.ndarray:
        """
        Generates an array representing hourly electricity consumption for a day based on the bimodal distribution.
        
        :param size: Number of hours to generate (default is 24 for a full day).
        :return: An array of electricity consumption values for each hour.
        """
        hours = np.arange(size)  # Hours from 0 to 23 (representing a day)
        
        # Morning peak: Gaussian distribution centered around the mean morning hour
        morning_peak = self.weight_morning * np.exp(-0.5 * ((hours - self.mean_morning) / self.std_morning) ** 2)
        
        # Evening peak: Gaussian distribution centered around the mean evening hour
        evening_peak = self.weight_evening * np.exp(-0.5 * ((hours - self.mean_evening) / self.std_evening) ** 2)
        
        # Base consumption with random variability for each hour
        base_consumption_random = self.base_consumption + np.random.normal(0, self.base_variability, size)
        
        # Total consumption is the sum of the base consumption and both peaks
        consumption = base_consumption_random + morning_peak + evening_peak
        
        return consumption

# # Instantiate the class with more abrupt peaks and added variability in the base consumption
# bimodal_consumption = DailyElectricityConsumptionBimodal(
#     base_consumption=100, base_variability=5, mean_morning=7, std_morning=1, 
#     mean_evening=19, std_evening=1, weight_morning=20, weight_evening=40
# )

# # Generate consumption data for 24 hours
# consumption_bimodal = bimodal_consumption.generate()

# # Plotting the consumption by hour
# hours = np.arange(24)
# plt.figure(figsize=(10, 6))
# plt.plot(hours, consumption_bimodal, marker='o', linestyle='-', color='b')
# plt.title('Bimodal Hourly Electricity Consumption with Morning and Evening Peaks (Abrupt)')
# plt.xlabel('Hour of the Day')
# plt.ylabel('Electricity Consumption (kWh)')
# plt.grid(True)
# plt.xticks(hours)
# plt.show()
