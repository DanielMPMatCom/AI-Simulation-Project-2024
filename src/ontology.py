import random
import numpy as np
from owlready2 import *

# Crear una nueva ontología
onto = get_ontology("http://example.org/electricity_ontology.owl")

with onto:
    # Clases para los tipos de circuitos
    class Circuit(Thing): pass
    class IndustrialCircuit(Circuit): pass
    class ResidentialCircuit(Circuit): pass
    class RuralCircuit(Circuit): pass
    
    # Propiedad para representar el impacto económico
    class hasEconomicImpact(DataProperty, FunctionalProperty):
        domain = [Circuit]
        range = [float]
        
    # Propiedad para representar el historial de afectaciones
    class hasAffectationHistory(DataProperty, FunctionalProperty):
        domain = [Circuit]
        range = [int]
    
    # Definir una clase para los ciudadanos
    class Citizen(Thing): pass
    
    # Relación entre circuitos y ciudadanos afectados
    class affects(Circuit >> Citizen): pass

# Crear instancias de circuitos con sus propiedades
industrial_circuit = IndustrialCircuit("Industrial1")
industrial_circuit.hasEconomicImpact = 1000.0
industrial_circuit.hasAffectationHistory = 2

residential_circuit = ResidentialCircuit("Residential1")
residential_circuit.hasEconomicImpact = 500.0
residential_circuit.hasAffectationHistory = 5

# Guardar la ontología en un archivo
onto.save(file="electricity_ontology.owl")












# Definir los tipos de circuitos y su impacto económico
CIRCUIT_TYPES = ["Industrial", "Residential", "Rural"]
IMPACT_MEAN = {"Industrial": 1000, "Residential": 500, "Rural": 200}  # Impacto promedio por tipo
IMPACT_STD = {"Industrial": 200, "Residential": 100, "Rural": 50}     # Desviación estándar por tipo

# Generar datos para el historial de afectaciones (número de cortes)
HISTORIAL_AFFECTATION_MIN = 0
HISTORIAL_AFFECTATION_MAX = 10

# Generar datos para la irritación ciudadana (0-100)
IRRITATION_MIN = 0
IRRITATION_MAX = 100

# Función para generar datos de circuitos
def generate_circuit_data(num_circuits: int):
    circuit_data = []
    
    for i in range(num_circuits):
        circuit_type = random.choice(CIRCUIT_TYPES)
        economic_impact = np.random.normal(IMPACT_MEAN[circuit_type], IMPACT_STD[circuit_type])
        affectation_history = random.randint(HISTORIAL_AFFECTATION_MIN, HISTORIAL_AFFECTATION_MAX)
        irritation_level = calculate_irritation_level(affectation_history, circuit_type)
        
        circuit_data.append({
            "id": f"Circuit_{i}",
            "type": circuit_type,
            "economic_impact": max(0, economic_impact),  # Impacto económico no puede ser negativo
            "affectation_history": affectation_history,
            "irritation_level": irritation_level
        })
    
    return circuit_data

# Función para calcular el nivel de irritación ciudadana
def calculate_irritation_level(affectation_history: int, circuit_type: str) -> int:
    base_irritation = random.randint(IRRITATION_MIN, IRRITATION_MAX // 2)  # Irritación base aleatoria
    # Aumentar la irritación en función del historial de cortes y el tipo de circuito
    irritation_increase = affectation_history * (1 if circuit_type == "Rural" else 2 if circuit_type == "Residential" else 3)
    irritation_level = min(IRRITATION_MAX, base_irritation + irritation_increase)
    
    return irritation_level

# Generar datos para 20 circuitos
circuit_data = generate_circuit_data(20)

# Imprimir los datos generados
for circuit in circuit_data:
    print(circuit)






# Cargar la ontología
onto = get_ontology("electricity_ontology.owl").load()

# Alimentar la ontología con los datos generados
for circuit in circuit_data:
    if circuit['type'] == 'Industrial':
        new_circuit = onto.IndustrialCircuit(circuit['id'])
    elif circuit['type'] == 'Residential':
        new_circuit = onto.ResidentialCircuit(circuit['id'])
    else:
        new_circuit = onto.RuralCircuit(circuit['id'])
    
    new_circuit.hasEconomicImpact = circuit['economic_impact']
    new_circuit.hasAffectationHistory = circuit['affectation_history']

# Guardar los cambios en la ontología
onto.save(file="electricity_ontology.owl")








# # Cargar la ontología
# onto = get_ontology("electricity_ontology.owl").load()

# Obtener circuitos industriales
industrial_circuits = list(onto.IndustrialCircuit.instances())

# Tomar decisiones basadas en el impacto económico
for circuit in industrial_circuits:
    if circuit.hasEconomicImpact > 900:
        print(f"Circuit {circuit.name} has a high economic impact!")