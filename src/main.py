from bdi import*


# Example usage:
if __name__ == "__main__":
    thermo_agent = BDI_Agent("Thermal Plant A")
    thermo_agent.update_beliefs("capacity", 85.0)
    thermo_agent.update_beliefs("demand", 90.0)
    thermo_agent.add_desire("maximize_generation")
    thermo_agent.add_desire("reduce_consumption")
    thermo_agent.update_intentions()
    thermo_agent.execute_plans()

print ("----------------------------------------------------------")


# Example of simulating events:
if __name__ == "__main__":
    events = ["high_demand", "power_outage"]
    for event in events:
        simulate_system_event(thermo_agent, event)
        thermo_agent.update_intentions()
        thermo_agent.execute_plans()




print ("----------------------------------------------------------")


# Simulate the BDI cycle with events
if __name__ == "__main__":
    events = ["high_demand", "power_outage"]
    for event in events:
        bdi_cycle(thermo_agent, event)
