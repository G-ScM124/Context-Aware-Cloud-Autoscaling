import pandas as pd

from controllers import (
    calculate_trend,
    context_controller,
    threshold_controller,
)
from simulator import (
    SERVER_CAPACITY,
    calculate_dropped_requests,
    calculate_latency,
    calculate_utilization,
    generate_traffic,
)


def run_simulation(traffic, controller_type):
    """Run one controller against the supplied traffic trace."""
    if controller_type not in {"threshold", "context"}:
        raise ValueError(
            "controller_type must be either 'threshold' or 'context'"
        )

    servers = 3
    demand_history = []
    utilization_history = []
    trend_history = []
    records = []

    for time, demand in enumerate(traffic):
        capacity = servers * SERVER_CAPACITY
        utilization = calculate_utilization(demand, servers)
        latency = calculate_latency(utilization)
        dropped_requests = calculate_dropped_requests(demand, servers)

        demand_history.append(demand)
        trend = calculate_trend(demand_history)

        utilization_history.append(utilization)
        trend_history.append(trend)

        if controller_type == "threshold":
            action = threshold_controller(utilization_history)
        else:
            action = context_controller(
                utilization_history,
                latency,
                trend_history,
            )

        record = {
            "time": time,
            "demand": demand,
            "servers": servers,
            "capacity": capacity,
            "utilization": utilization,
            "latency": latency,
            "dropped_requests": dropped_requests,
            "trend": trend,
            "action": action,
        }

        next_servers = max(1, min(10, servers + action))
        record["next_servers"] = next_servers
        records.append(record)

        servers = next_servers

    return pd.DataFrame(records)


def run_experiment():
    """Run both controllers against the same generated traffic trace."""
    traffic = generate_traffic()

    threshold_results = run_simulation(
        traffic,
        controller_type="threshold",
    )
    context_results = run_simulation(
        traffic,
        controller_type="context",
    )

    return threshold_results, context_results


if __name__ == "__main__":
    threshold_results, context_results = run_experiment()
