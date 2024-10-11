# # # import matplotlib.pyplot as plt
# # # from src.circuits import Block
# # # from src.utils.gaussianmixture import DailyElectricityConsumptionBimodal
# # # from src.simulation_constants import (
# # #     NO_CIRCUITS,
# # #     NO_THERMOELECTRICS,
# # #     MIN_CITIZEN,
# # #     MAX_CITIZEN,
# # #     MAX_DEVIATION_CITIZEN_IN_BLOCK,
# # #     DEMAND_PER_PERSON,
# # #     DEMAND_INDUSTRIALIZATION,
# # #     VARIABILITY_DEMAND_PER_PERSON,
# # #     VARIABILITY_DEMAND_PER_INDUSTRIALIZATION,
# # #     PEAK_CONSUMPTION_MORNING,
# # #     PEAK_CONSUMPTION_EVENING,
# # #     MAX_DEVIATION_MORNING,
# # #     MAX_DEVIATION_EVENING,
# # #     WEIGHT_MORNING,
# # #     WEIGHT_EVENING,
# # #     RANDOM_SEED,
# # # )

# # # from numpy.random import default_rng

# # # rng = default_rng(RANDOM_SEED)

# # # citizen_count = rng.integers(MIN_CITIZEN, MAX_CITIZEN)

# # # citizen_range = (
# # #     max(citizen_count - MAX_DEVIATION_CITIZEN_IN_BLOCK, 0),
# # #     min(citizen_count + MAX_DEVIATION_CITIZEN_IN_BLOCK, MAX_CITIZEN),
# # # )

# # # industrialization = rng.integers(0, DEMAND_INDUSTRIALIZATION) / DEMAND_INDUSTRIALIZATION


# # # myBlock = Block(
# # #     gaussian_mixture=DailyElectricityConsumptionBimodal(
# # #         base_consumption=DEMAND_PER_PERSON * citizen_count
# # #         + DEMAND_INDUSTRIALIZATION * industrialization,
# # #         base_variability=VARIABILITY_DEMAND_PER_PERSON * citizen_count
# # #         + VARIABILITY_DEMAND_PER_INDUSTRIALIZATION * industrialization,
# # #         mean_morning=PEAK_CONSUMPTION_MORNING,
# # #         mean_evening=PEAK_CONSUMPTION_EVENING,
# # #         std_morning=rng.uniform(1.0, MAX_DEVIATION_MORNING),
# # #         std_evening=rng.uniform(1.0, MAX_DEVIATION_EVENING),
# # #         weight_morning=WEIGHT_MORNING,
# # #         weight_evening=WEIGHT_EVENING,
# # #     ),
# # #     citizens_range=citizen_range,
# # #     industrialization=industrialization,
# # # )


# # # predicted_consumption = myBlock.predicted_demand_per_hour



# # # plt.plot(predicted_consumption)
# # # plt.show()

# # # # from src.thermoelectrics import Thermoelectric

# # # # myThermoelectric = Thermoelectric("testingID", total_capacity=41 * 1e3)


# # # # days = 10**6
# # # # for p in myThermoelectric.parts:
# # # #     days = min(p.remaining_life, days)

# # # # for i in range(int(days + 2)):
# # # #     print("DAY: ", i)
# # # #     for p in myThermoelectric.parts:
# # # #         print(p)
# # # #         if not p.is_working():
# # # #             p.repair()
# # # #             p.hurry_repair()
# # # #             print("HURRY REPAIR!!!  ---------------------------------------------------------------------->")

# # # #     myThermoelectric.update()


# # # # for i in range(int(5)):
# # # #     print("DAY: ", i)
# # # #     for p in myThermoelectric.parts:
# # # #         print(p)
# # # #         if not p.is_working():
# # # #             p.repair()
# # # #             p.hurry_repair()
          

# # # #     myThermoelectric.update()
# # from src.people import ThermoelectricAgentAction

# # # Función para contar las propiedades activas
# # def contar_propiedades_activas(actions):
# #     counts = {}

# #     for action in actions:
# #         for key, value in vars(action).items():
# #             if value:
# #                 if key in counts:
# #                     counts[key] += 1
# #                 else:
# #                     counts[key] = 1

# #     return counts

# # # Ejemplo de uso
# # actions = [
# #     ThermoelectricAgentAction(True, False, True, False, True, True),
# #     ThermoelectricAgentAction(False, True, True, True, False, True),
# #     ThermoelectricAgentAction(True, True, False, True, True, False),
# # ]

# # resultados = contar_propiedades_activas(actions)
# # print(resultados)


# import numpy as np
# from scipy.stats import chi2_contingency

# # Ejemplo de distribuciones diarias (cada día tiene 4 bloques, 24 horas por bloque)
# distribuciones_dias = [
#     [
#         [1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2],  # Bloque 1, Día 1
#         [2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1],  # Bloque 2, Día 1
#         [3, 2, 1, -1, 3, 2, 1, -1, 3, 2, 1, -1, 3, 2, 1, -1, 3, 2, 1, -1, 3, 2, 1, -1]   # Bloque 3, Día 1
#     ],
#     [
#         [1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2],  # Bloque 1, Día 2
#         [2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1, 2, 1, -1],  # Bloque 2, Día 2
#         [3, 2, 1, -1, 3, 2, 1, -1, 3, 2, 1, -1, 3, 2, 1, -1, 3, 2, 1, -1, 3, 2, 1, -1]   # Bloque 3, Día 2
#     ]
# ]

# # Extraer los IDs de termoeléctricas (excluyendo el -1)
# termoelectricas = set()
# for distribucion_dia in distribuciones_dias:
#     for bloque in distribucion_dia:
#         termoelectricas.update([t for t in bloque if t != -1])

# # Para cada bloque (misma posición en cada día)
# num_bloques = len(distribuciones_dias[0])  # Número de bloques por día
# resultados_chi2 = []

# for bloque_idx in range(num_bloques):
#     # Crear la tabla de contingencia para el bloque en diferentes días
#     tabla_contingencia = []

#     for distribucion_dia in distribuciones_dias:
#         bloque = distribucion_dia[bloque_idx]
#         conteo = [bloque.count(t) for t in termoelectricas]
#         tabla_contingencia.append(conteo)

#     # Convertir a array numpy para mejor manejo
#     tabla_contingencia = np.array(tabla_contingencia)

#     tabla_contingencia += 1

#     # Test de chi-cuadrado
#     chi2, p, dof, ex = chi2_contingency(tabla_contingencia)

#     resultados_chi2.append((chi2, p, dof))

# # Resultados
# for i, (chi2, p, dof) in enumerate(resultados_chi2):
#     print(f"Bloque {i + 1}: Chi-cuadrado: {chi2}, Valor p: {p}, Grados de libertad: {dof}")

#     # Interpretar el resultado
#     alpha = 0.05
#     if p < alpha:
#         print(f"Bloque {i + 1}: Rechazamos la hipótesis nula. Hay evidencia de que las asignaciones no son aleatorias.")
#     else:
#         print(f"Bloque {i + 1}: No podemos rechazar la hipótesis nula. Las asignaciones parecen ser aleatorias.")
import numpy as np
from scipy.spatial.distance import jensenshannon

# Ejemplo de distribuciones diarias (cada día tiene 3 bloques, 24 horas por bloque)
distribuciones_dias = [
    [
        [2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3],  # Bloque 1, Día 1
        [3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0],  # Bloque 2, Día 1
        [4, 3, 2, 0, 4, 3, 2, 0, 4, 3, 2, 0, 4, 3, 2, 0, 4, 3, 2, 0, 4, 3, 2, 0]   # Bloque 3, Día 1
    ],
    [
        [2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3],  # Bloque 1, Día 2
        [3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0, 3, 2, 0],  # Bloque 2, Día 2
        [4, 3, 2, 0, 4, 3, 2, 0, 4, 3, 2, 0, 4, 3, 2, 0, 4, 3, 2, 0, 4, 3, 2, 0]   # Bloque 3, Día 2
    ]
]

# Extraer los IDs de termoeléctricas (excluyendo el -1)
termoelectricas = sorted(list(set(t for distribucion_dia in distribuciones_dias for bloque in distribucion_dia for t in bloque if t != -1)))

# Para cada bloque (misma posición en cada día)
num_bloques = len(distribuciones_dias[0])  # Número de bloques por día
num_horas = len(distribuciones_dias[0][0])  # Número de horas por bloque

# Crear una lista de distribuciones por bloque y hora
distribuciones_por_hora = {i: [[] for _ in range(num_horas)] for i in range(num_bloques)}

for distribucion_dia in distribuciones_dias:
    for bloque_idx, bloque in enumerate(distribucion_dia):
        for hora_idx, termoelec in enumerate(bloque):
            distribuciones_por_hora[bloque_idx][hora_idx].append(termoelec)

# Calcular la similitud entre distribuciones hora por hora para cada bloque
for bloque_idx, distribuciones_horarias in distribuciones_por_hora.items():
    print(f"\nBloque {bloque_idx + 1}")
    
    for hora_idx, distribuciones_hora in enumerate(distribuciones_horarias):
        # Contar las frecuencias de cada termoeléctrica en la hora actual
        conteo_por_dia = [[1 if termoelec == t else 0 for t in termoelectricas] for termoelec in distribuciones_hora]

        # Convertir a numpy array para normalizar y calcular la distancia
        conteo_por_dia = np.array(conteo_por_dia, dtype=float)

        # Normalizar las distribuciones para que sumen 1 (frecuencias de termoeléctricas)
        if conteo_por_dia.sum(axis=1).all():  # Evitar la división por 0
            conteo_por_dia /= conteo_por_dia.sum(axis=1, keepdims=True)

        # Calcular la matriz de similitud usando JS para las distribuciones en esta hora
        num_dias = conteo_por_dia.shape[0]
        similitudes = []
        
        for i in range(num_dias):
            for j in range(i + 1, num_dias):
                js_distance = jensenshannon(conteo_por_dia[i], conteo_por_dia[j])
                similitudes.append(js_distance)
        
        # Promedio de similitudes
        promedio_js = np.mean(similitudes) if similitudes else 0
        
        print(f"Hora {hora_idx + 1}: Distancia promedio de Jensen-Shannon: {promedio_js:.4f}")
        
        # Definir un umbral para determinar si las distribuciones son similares
        umbral = 0.1  # Por ejemplo
        if promedio_js < umbral:
            print(f"Hora {hora_idx + 1}: Las distribuciones horarias son muy similares. No es aleatorio.")
        else:
            print(f"Hora {hora_idx + 1}: Las distribuciones horarias no son similares. Podría ser aleatorio.")
