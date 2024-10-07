import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np


class Citizen:
    def __init__(self, amount: int) -> None:
        self.amount = amount
        self.opinion

    def set_opinion(
        self,
        input_last_day_off: int,
        input_industrialization: float,
        input_days_off_relation: float,
        input_general_satisfaction: float,
    ):

        last_day_off = ctrl.Antecedent(np.arange(0, 22, 1), "last_day_off")
        industrialization = ctrl.Antecedent(
            np.arange(0, 1, 1, 0.1), "industrialization"
        )
        days_off_relation = ctrl.Antecedent(np.arange(0, 1.1, 0.1), "days_off_relation")
        general_satisfaction = ctrl.Antecedent(
            np.arange(0, 1.1, 0.1), "general_satisfaction"
        )
        personal_satisfaction = ctrl.Consequent(
            np.arange(0, 1, 1, 0.1), "personal_satisfaction"
        )

        # Membership functions for last_day_off
        last_day_off["recent"] = fuzz.trapmf(last_day_off.universe, [0, 0, 5, 10])
        last_day_off["moderate"] = fuzz.trimf(last_day_off.universe, [7, 12, 15])
        last_day_off["distant"] = fuzz.trapmf(last_day_off.universe, [14, 18, 20, 20])

        # Membership functions for industrialization
        industrialization["low"] = fuzz.trapmf(
            industrialization.universe, [0, 0, 0.5, 0.6]
        )
        industrialization["medium"] = fuzz.trimf(
            industrialization.universe, [0.5, 0.7, 0.8]
        )
        industrialization["high"] = fuzz.trapmf(
            industrialization.universe, [0.7, 0.8, 1.0, 1.0]
        )

        # Membership functions for days_off_relation
        days_off_relation["low"] = fuzz.trapmf(
            days_off_relation.universe, [0, 0, 0.1, 0.2]
        )
        days_off_relation["medium"] = fuzz.trimf(
            days_off_relation.universe, [0.1, 0, 3, 0, 4]
        )
        days_off_relation["high"] = fuzz.trapmf(
            days_off_relation.universe, [0.3, 0.5, 1.0, 1.0]
        )

        # Membership functions for general_satisfaction
        general_satisfaction["lowest"] = fuzz.trapmf(
            general_satisfaction.universe, [0, 0, 0.3, 0.4]
        )
        general_satisfaction["lower"] = fuzz.trimf(
            general_satisfaction.universe, [0.3, 0.4, 0.6]
        )
        general_satisfaction["low"] = fuzz.trimf(
            general_satisfaction.universe, [0.5, 0.6, 0.7]
        )
        general_satisfaction["medium"] = fuzz.trimf(
            general_satisfaction.universe, [0.7, 0.8, 0.9]
        )
        general_satisfaction["high"] = fuzz.trapmf(
            general_satisfaction.universe, [0.8, 0.9, 1.0, 1.0]
        )

        # Membership functions for personal_satisfaction
        personal_satisfaction["lowest"] = fuzz.trapmf(
            personal_satisfaction.universe, [0, 0, 0.3, 0.4]
        )
        personal_satisfaction["lower"] = fuzz.trimf(
            personal_satisfaction.universe, [0.3, 0.4, 0.6]
        )
        personal_satisfaction["low"] = fuzz.trimf(
            personal_satisfaction.universe, [0.5, 0.6, 0.7]
        )
        personal_satisfaction["medium"] = fuzz.trimf(
            personal_satisfaction.universe, [0.7, 0.8, 0.9]
        )
        personal_satisfaction["high"] = fuzz.trapmf(
            personal_satisfaction.universe, [0.8, 0.9, 1.0, 1.0]
        )

        # Fuzzy rules
        rules = [
            ctrl.Rule(
                last_day_off["distant"]
                & days_off_relation["low"]
                & industrialization["medium"]
                & general_satisfaction["high"],
                personal_satisfaction["high"],
            ),
            ctrl.Rule(
                last_day_off["distant"]
                & days_off_relation["low"]
                & industrialization["high"]
                & general_satisfaction["high"],
                personal_satisfaction["medium"],
            ),
            ctrl.Rule(
                last_day_off["distant"]
                & days_off_relation["low"]
                & industrialization["high"]
                & general_satisfaction["medium"],
                personal_satisfaction["high"],
            ),
            ctrl.Rule(
                last_day_off["distant"]
                & days_off_relation["low"]
                & industrialization["high"]
                & general_satisfaction["low"],
                personal_satisfaction["medium"],
            ),
            ctrl.Rule(
                last_day_off["recent"]
                & days_off_relation["medium"]
                & industrialization["medium"]
                & general_satisfaction["medium"],
                personal_satisfaction["lower"],
            ),
            ctrl.Rule(
                last_day_off["recent"]
                & days_off_relation["medium"]
                & industrialization["low"]
                & general_satisfaction["medium"],
                personal_satisfaction["medium"],
            ),
            ctrl.Rule(
                last_day_off["recent"]
                & days_off_relation["high"]
                & industrialization["low"]
                & general_satisfaction["lower"],
                personal_satisfaction["lowest"],
            ),
            ctrl.Rule(
                last_day_off["recent"]
                & days_off_relation["high"]
                & industrialization["low"]
                & general_satisfaction["lowest"],
                personal_satisfaction["lower"],
            ),
            ctrl.Rule(
                last_day_off["moderate"]
                & days_off_relation["medium"]
                & industrialization["medium"]
                & general_satisfaction["medium"],
                personal_satisfaction["medium"],
            ),
            ctrl.Rule(
                last_day_off["moderate"]
                & days_off_relation["medium"]
                & industrialization["medium"]
                & general_satisfaction["high"],
                personal_satisfaction["low"],
            ),
            ctrl.Rule(
                last_day_off["moderate"]
                & days_off_relation["medium"]
                & industrialization["medium"]
                & general_satisfaction["low"],
                personal_satisfaction["medium"],
            ),
        ]

        # Create control system
        satisfaction_control = ctrl.ControlSystem(rules)
        satisfaction_simulation = ctrl.ControlSystemSimulation(satisfaction_control)

        # Provide input values to the simulation
        satisfaction_simulation.input["last_day_off"] = input_last_day_off
        satisfaction_simulation.input["industrialization"] = input_industrialization
        satisfaction_simulation.input["days_off_relation"] = input_days_off_relation
        satisfaction_simulation.input["general_satisfaction"] = (
            input_general_satisfaction
        )

        # Compute result
        satisfaction_simulation.compute()

        # Return personal satisfaction
        self.opinion = satisfaction_simulation.output["personal_satisfaction"]

    # def complain():
    #     pass
