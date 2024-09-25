import numpy as np

def monte_carlo_simulation(n_simulations: int, demand_mean: float, demand_std: float, capacity_mean: float, capacity_std: float) -> np.ndarray:
    """
    Simulates multiple scenarios of demand and generation capacity using Monte Carlo method.

    Parameters:
    -----------
    n_simulations : int
        The number of Monte Carlo simulations to run.
    demand_mean : float
        The mean value of energy demand.
    demand_std : float
        The standard deviation of energy demand (represents variability).
    capacity_mean : float
        The mean value of energy generation capacity.
    capacity_std : float
        The standard deviation of generation capacity (represents variability).
    
    Returns:
    --------
    np.ndarray
        An array where each row represents a simulated scenario [demand, capacity, difference].
    """
    # Simulate demand and generation capacity
    demand_simulations = np.random.normal(demand_mean, demand_std, n_simulations)
    capacity_simulations = np.random.normal(capacity_mean, capacity_std, n_simulations)
    
    # Calculate the difference between generation and demand
    difference = capacity_simulations - demand_simulations
    
    # Return the results as an array of [demand, capacity, difference]
    results = np.column_stack((demand_simulations, capacity_simulations, difference))
    return results

# Example usage
if __name__ == "__main__":
    n_sims = 10000
    demand_mean = 1000  # Mean energy demand in MW
    demand_std = 100    # Standard deviation of demand
    capacity_mean = 1050  # Mean generation capacity in MW
    capacity_std = 50    # Standard deviation of generation capacity
    
    results = monte_carlo_simulation(n_sims, demand_mean, demand_std, capacity_mean, capacity_std)
    
    # Analyze results
    print(f"Simulated {n_sims} scenarios.")
    print(f"Percentage of scenarios with a deficit: {np.mean(results[:, 2] < 0) * 100:.2f}%")
