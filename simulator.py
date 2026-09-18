import numpy as np


SERVER_CAPACITY = 100
BASE_LATENCY = 40


def generate_traffic():
    """Generate the reproducible 500-second traffic demand trace."""
    np.random.seed(42)

    base_demand = np.concatenate(
        [
            np.full(100, 180.0),
            np.linspace(180.0, 420.0, 100),
            np.full(50, 520.0),
            np.full(100, 350.0),
            np.linspace(350.0, 180.0, 100),
            np.full(50, 180.0),
        ]
    )

    noise = np.random.normal(0.0, 15.0, 500)
    return np.maximum(base_demand + noise, 0.0)


def calculate_utilization(demand, servers):
    """Calculate demand as a fraction of total active-server capacity."""
    return demand / (servers * SERVER_CAPACITY)


def calculate_latency(utilization):
    """Calculate latency in milliseconds using utilization capped at 0.95."""
    return BASE_LATENCY / (1 - min(utilization, 0.95))


def calculate_dropped_requests(demand, servers):
    """Calculate demand that exceeds the active servers' total capacity."""
    return max(0, demand - servers * SERVER_CAPACITY)
