# import matplotlib.pyplot as plt
# from src.circuits import Block
# from src.utils.gaussianmixture import DailyElectricityConsumptionBimodal
# from src.simulation_constants import (
#     NO_CIRCUITS,
#     NO_THERMOELECTRICS,
#     MIN_CITIZEN,
#     MAX_CITIZEN,
#     MAX_DEVIATION_CITIZEN_IN_BLOCK,
#     DEMAND_PER_PERSON,
#     DEMAND_INDUSTRIALIZATION,
#     VARIABILITY_DEMAND_PER_PERSON,
#     VARIABILITY_DEMAND_PER_INDUSTRIALIZATION,
#     PEAK_CONSUMPTION_MORNING,
#     PEAK_CONSUMPTION_EVENING,
#     MAX_DEVIATION_MORNING,
#     MAX_DEVIATION_EVENING,
#     WEIGHT_MORNING,
#     WEIGHT_EVENING,
#     RANDOM_SEED,
# )

# from numpy.random import default_rng

# rng = default_rng(RANDOM_SEED)

# citizen_count = rng.integers(MIN_CITIZEN, MAX_CITIZEN)

# citizen_range = (
#     max(citizen_count - MAX_DEVIATION_CITIZEN_IN_BLOCK, 0),
#     min(citizen_count + MAX_DEVIATION_CITIZEN_IN_BLOCK, MAX_CITIZEN),
# )

# industrialization = rng.integers(0, DEMAND_INDUSTRIALIZATION) / DEMAND_INDUSTRIALIZATION


# myBlock = Block(
#     gaussian_mixture=DailyElectricityConsumptionBimodal(
#         base_consumption=DEMAND_PER_PERSON * citizen_count
#         + DEMAND_INDUSTRIALIZATION * industrialization,
#         base_variability=VARIABILITY_DEMAND_PER_PERSON * citizen_count
#         + VARIABILITY_DEMAND_PER_INDUSTRIALIZATION * industrialization,
#         mean_morning=PEAK_CONSUMPTION_MORNING,
#         mean_evening=PEAK_CONSUMPTION_EVENING,
#         std_morning=rng.uniform(1.0, MAX_DEVIATION_MORNING),
#         std_evening=rng.uniform(1.0, MAX_DEVIATION_EVENING),
#         weight_morning=WEIGHT_MORNING,
#         weight_evening=WEIGHT_EVENING,
#     ),
#     citizens_range=citizen_range,
#     industrialization=industrialization,
# )


# predicted_consumption = myBlock.predicted_demand_per_hour

# plt.plot(predicted_consumption)
# plt.show()

from src.thermoelectrics import Thermoelectric

myThermoelectric = Thermoelectric("testingID", total_capacity=41 * 1e3)


days = 10**6
for p in myThermoelectric.parts:
    days = min(p.remaining_life, days)

for i in range(int(days + 2)):
    print("DAY: ", i)
    for p in myThermoelectric.parts:
        print(p)
        if not p.is_working():
            p.repair()
            p.hurry_repair()
            print("HURRY REPAIR!!!  ---------------------------------------------------------------------->")

    myThermoelectric.update()


for i in range(int(5)):
    print("DAY: ", i)
    for p in myThermoelectric.parts:
        print(p)
        if not p.is_working():
            p.repair()
            p.hurry_repair()
          

    myThermoelectric.update()
