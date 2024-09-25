from typing import Dict, List

class BDI_Agent:
    """
    A class representing a BDI (Beliefs, Desires, Intentions) agent.

    Attributes:
    -----------
    name : str
        The name of the agent.
    beliefs : Dict[str, float]
        The beliefs of the agent about the world (e.g., system status).
    desires : List[str]
        The goals the agent aims to achieve.
    intentions : List[str]
        The plans or actions the agent intends to perform.
    """
    
    def __init__(self, name: str):
        """
        Initializes the BDI agent with a name, and empty beliefs, desires, and intentions.

        Parameters:
        -----------
        name : str
            The name of the agent.
        """
        self.name = name
        self.beliefs: Dict[str, float] = {}
        self.desires: List[str] = []
        self.intentions: List[str] = []
    
    def update_beliefs(self, key: str, value: float) -> None:
        """
        Updates the agent's beliefs by adding or modifying a belief.

        Parameters:
        -----------
        key : str
            The belief identifier (e.g., "capacity", "demand").
        value : float
            The value associated with the belief.
        """
        self.beliefs[key] = value
        print(f"Agent {self.name} updated belief: {key} = {value}")
    
    def add_desire(self, desire: str) -> None:
        """
        Adds a new desire to the agent's desire list if it's not already present.

        Parameters:
        -----------
        desire : str
            The new goal the agent wants to achieve.
        """
        if desire not in self.desires:
            self.desires.append(desire)
            print(f"Agent {self.name} added a new desire: {desire}")
    
    def update_intentions(self) -> None:
        """
        Updates the agent's intentions based on its current beliefs and desires.
        Intentions are plans or actions the agent commits to achieve its desires.
        """
        self.intentions = []  # Clear previous intentions
        for desire in self.desires:
            if self._evaluate_conditions(desire):
                self.intentions.append(desire)
                print(f"Agent {self.name} adopted a new intention: {desire}")
    
    def _evaluate_conditions(self, desire: str) -> bool:
        """
        Evaluates whether a desire can be achieved based on the agent's current beliefs.

        Parameters:
        -----------
        desire : str
            The desire to evaluate.

        Returns:
        --------
        bool:
            True if the desire is achievable, False otherwise.
        """
        if desire == "maximize_generation" and self.beliefs.get("capacity", 0) > 80:
            return True
        if desire == "reduce_consumption" and self.beliefs.get("demand", 0) > self.beliefs.get("capacity", 0):
            return True
        return False

    def execute_plans(self) -> None:
        """
        Executes the agent's current intentions by simulating the actions required to achieve them.
        """
        for intention in self.intentions:
            print(f"Agent {self.name} is executing: {intention}")
            # Add action logic for each intention here

# Example usage:
if __name__ == "__main__":
    thermo_agent = BDI_Agent("Thermal Plant A")
    thermo_agent.update_beliefs("capacity", 85.0)
    thermo_agent.update_beliefs("demand", 90.0)
    thermo_agent.add_desire("maximize_generation")
    thermo_agent.add_desire("reduce_consumption")
    thermo_agent.update_intentions()
    thermo_agent.execute_plans()







def simulate_system_event(agent: BDI_Agent, event: str) -> None:
    """
    Simulates an external event that causes the agent to update its beliefs.

    Parameters:
    -----------
    agent : BDI_Agent
        The BDI agent that will react to the event.
    event : str
        The event that occurs in the system, e.g., "high_demand", "power_outage".
    """
    if event == "high_demand":
        agent.update_beliefs("demand", agent.beliefs.get("demand", 0) + 10)
    elif event == "power_outage":
        agent.update_beliefs("capacity", agent.beliefs.get("capacity", 0) - 20)

# Example of simulating events:
if __name__ == "__main__":
    events = ["high_demand", "power_outage"]
    for event in events:
        simulate_system_event(thermo_agent, event)
        thermo_agent.update_intentions()
        thermo_agent.execute_plans()












def bdi_cycle(agent: BDI_Agent, system_event: str) -> None:
    """
    Simulates the BDI agent's cycle of perception (beliefs), deliberation (desires), 
    and action (intentions), based on external system events.

    Parameters:
    -----------
    agent : BDI_Agent
        The BDI agent.
    system_event : str
        The external event that impacts the agent's beliefs.
    """
    # 1. Update beliefs based on the event
    simulate_system_event(agent, system_event)
    
    # 2. Update desires (in a real system, this might be more complex)
    agent.add_desire("maximize_generation")
    agent.add_desire("reduce_consumption")
    
    # 3. Formulate intentions based on updated beliefs and desires
    agent.update_intentions()
    
    # 4. Execute the plans based on the agent's intentions
    agent.execute_plans()

# Simulate the BDI cycle with events
if __name__ == "__main__":
    events = ["high_demand", "power_outage"]
    for event in events:
        bdi_cycle(thermo_agent, event)
