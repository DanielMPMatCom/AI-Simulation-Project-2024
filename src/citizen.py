import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np


class Citizen:
    """
    Represents a citizen in the simulation.
    """

    def __init__(self, amount: int, days_between_opinion: int=7) -> None:
        self.amount = amount
        self.opinion = None
        self.days_between_opinion = days_between_opinion
        self.last_opinion_date = days_between_opinion

    def set_opinion(
        self,
        input_last_day_off: int,
        input_industrialization: float,
        input_days_off_relation: float,
        input_general_satisfaction: float,
        verbose: bool = False,
    ) -> None:
        """
        Sets the opinion of the citizens based on various input factors.

        This method uses fuzzy logic to determine the personal satisfaction of citizens
        based on the last day off, industrialization level, days off relation, and general satisfaction.

        Args:
            input_last_day_off (int): The number of days since the last day off.
            input_industrialization (float): The level of industrialization.
            input_days_off_relation (float): The ratio of days off to total days.
            input_general_satisfaction (float): The general satisfaction level.
            verbose (bool, optional): If True, prints detailed information about the inputs and outputs. Defaults to False.
        """

        # Variables universe
        days = np.arange(0, 24, 1)
        percents = np.arange(0, 11, 1)

        # Antecedents and consequent
        last_day_off = ctrl.Antecedent(np.arange(0, 23, 1), "last_day_off")
        industrialization = ctrl.Antecedent(
            np.arange(0, 11, 1), "industrialization"
        )
        days_off_relation = ctrl.Antecedent(np.arange(0, 11, 1), "days_off_relation")
        general_satisfaction = ctrl.Antecedent(
            np.arange(0, 11, 1), "general_satisfaction"
        )
        personal_satisfaction = ctrl.Consequent(
            np.arange(0, 11, 1), "personal_satisfaction"
        )

        # Membership functions for last_day_off
        last_day_off["recent"] = fuzz.trapmf(last_day_off.universe, [0, 0, 5, 10])
        last_day_off["moderate"] = fuzz.trimf(last_day_off.universe, [7, 12, 15])
        last_day_off["distant"] = fuzz.trapmf(last_day_off.universe, [14, 18, 20, 20])

        # Membership functions for industrialization
        industrialization["low"] = fuzz.trapmf(
            industrialization.universe, [0, 0, 5, 6]
        )
        industrialization["medium"] = fuzz.trimf(
            industrialization.universe, [5, 7, 8]
        )
        industrialization["high"] = fuzz.trapmf(
            industrialization.universe, [7, 8, 10, 10]
        )

        # Membership functions for days_off_relation
        days_off_relation["low"] = fuzz.trapmf(
            days_off_relation.universe, [0, 0, 1, 2]
        )
        days_off_relation["medium"] = fuzz.trimf(
            days_off_relation.universe, [1, 3, 4]
        )
        days_off_relation["high"] = fuzz.trapmf(
            days_off_relation.universe, [3, 5, 10, 10]
        )

        # Membership functions for general_satisfaction
        general_satisfaction["low"] = fuzz.trapmf(
            general_satisfaction.universe, [0, 0, 4, 6]
        )
        general_satisfaction["medium"] = fuzz.trimf(
            general_satisfaction.universe, [5, 7, 8]
        )
        general_satisfaction["high"] = fuzz.trapmf(
            general_satisfaction.universe, [7, 9, 10, 10]
        )

        # Membership functions for personal_satisfaction
        personal_satisfaction["low"] = fuzz.trapmf(
            personal_satisfaction.universe, [0, 0, 4, 6]
        )
        personal_satisfaction["medium"] = fuzz.trimf(
            personal_satisfaction.universe, [5, 7, 8]
        )
        personal_satisfaction["high"] = fuzz.trapmf(
            personal_satisfaction.universe, [7, 9, 10, 10]
        )

        # Fuzzy rules
        rules = [

            # Complex rules
            ctrl.Rule(
                days_off_relation["medium"]
                & industrialization["high"],
                personal_satisfaction["medium"],
            ),
            ctrl.Rule(
                last_day_off["distant"]
                & days_off_relation["low"]
                & industrialization["medium"]
                & general_satisfaction["low"],
                personal_satisfaction["medium"],
            ),
            ctrl.Rule(
                last_day_off["recent"]
                & days_off_relation["medium"]
                & industrialization["medium"]
                & general_satisfaction["medium"],
                personal_satisfaction["low"],
            ),
            ctrl.Rule(
                last_day_off["recent"]
                & days_off_relation["medium"]
                & industrialization["low"]
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
                & general_satisfaction["medium"],
                personal_satisfaction["high"],
            ),

            # Low personal satisfaction
            ctrl.Rule(last_day_off["recent"] & industrialization["high"], personal_satisfaction["low"]),
            ctrl.Rule(last_day_off["recent"] & days_off_relation["high"], personal_satisfaction["low"]),
            ctrl.Rule(last_day_off["recent"] & general_satisfaction["low"], personal_satisfaction["low"]),
            ctrl.Rule(industrialization["high"] & days_off_relation["high"], personal_satisfaction["low"]),
            ctrl.Rule(industrialization["high"] & general_satisfaction["low"], personal_satisfaction["low"]),
            ctrl.Rule(days_off_relation["high"] & general_satisfaction["low"], personal_satisfaction["low"]),

            # Medium personal satisfaction
            ctrl.Rule(last_day_off["moderate"] & industrialization["medium"] & days_off_relation["medium"],
                      personal_satisfaction["medium"]),
            ctrl.Rule(last_day_off["moderate"] & industrialization["medium"] & general_satisfaction["medium"],
                      personal_satisfaction["medium"]),
            ctrl.Rule(last_day_off["moderate"] & days_off_relation["medium"] & general_satisfaction["medium"],
                      personal_satisfaction["medium"]),
            ctrl.Rule(industrialization["medium"] & days_off_relation["medium"] & general_satisfaction["medium"],
                      personal_satisfaction["medium"]),

            # High personal satisfaction
            ctrl.Rule(last_day_off["distant"] & industrialization["low"], personal_satisfaction["high"]),
            ctrl.Rule(last_day_off["distant"] & days_off_relation["low"], personal_satisfaction["high"]),
            ctrl.Rule(last_day_off["distant"] & general_satisfaction["high"], personal_satisfaction["high"]),
            ctrl.Rule(industrialization["low"] & days_off_relation["low"], personal_satisfaction["high"]),
            ctrl.Rule(industrialization["low"] & general_satisfaction["high"], personal_satisfaction["high"]),
            ctrl.Rule(days_off_relation["low"] & general_satisfaction["high"], personal_satisfaction["high"]),
        ]

        # Create control system
        satisfaction_control = ctrl.ControlSystem(rules)
        satisfaction_simulation = ctrl.ControlSystemSimulation(satisfaction_control)

        # Nearest input index
        last_day_off_index = (np.abs(input_last_day_off - days)).argmin()
        industrialization_index = (np.abs(input_industrialization * 10 - percents)).argmin()
        days_off_relation_index = (np.abs(input_days_off_relation * 10 - percents)).argmin()
        general_satisfaction_index = (np.abs(input_general_satisfaction * 10 - percents)).argmin()

        # Provide input values to the simulation
        satisfaction_simulation.input["last_day_off"] = days[last_day_off_index]
        satisfaction_simulation.input["industrialization"] = percents[industrialization_index]
        satisfaction_simulation.input["days_off_relation"] = percents[days_off_relation_index]
        satisfaction_simulation.input["general_satisfaction"] = (
            percents[general_satisfaction_index]
        )

        # Compute result
        satisfaction_simulation.compute()

        # Verbose
        if verbose:
            print(input_last_day_off)
            print(input_industrialization)
            print(input_days_off_relation)
            print(input_general_satisfaction)
            print(satisfaction_simulation.input)
            print(satisfaction_simulation.output)

        # Return personal satisfaction
        self.opinion = satisfaction_simulation.output["personal_satisfaction"]

    # def complain():
    #     pass
