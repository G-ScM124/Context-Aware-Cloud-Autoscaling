from pathlib import Path

import matplotlib.pyplot as plt
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


SLA_THRESHOLD = 250
RESULTS_DIR = Path("results")


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


def calculate_metrics(results):
    """Calculate the evaluation metrics for one controller run."""
    return {
        "Average Servers": results["servers"].mean(),
        "Total Server-Time (server-seconds)": results["servers"].sum(),
        "Average Latency (ms)": results["latency"].mean(),
        "95th Percentile Latency (ms)": results["latency"].quantile(0.95),
        "SLA Violations": (results["latency"] > SLA_THRESHOLD).sum(),
        "Total Dropped Requests": results["dropped_requests"].sum(),
        "Scaling Actions": (
            results["next_servers"] != results["servers"]
        ).sum(),
    }


def create_comparison_table(threshold_results, context_results):
    """Create a side-by-side comparison of both controller runs."""
    threshold_metrics = calculate_metrics(threshold_results)
    context_metrics = calculate_metrics(context_results)

    return pd.DataFrame(
        {
            "Metric": list(threshold_metrics.keys()),
            "Threshold": list(threshold_metrics.values()),
            "Context-Aware": list(context_metrics.values()),
        }
    )


def create_graphs(threshold_results, context_results):
    """Create and save the three planned comparison graphs."""
    plt.figure()
    plt.plot(
        threshold_results["time"],
        threshold_results["demand"],
        label="Traffic Demand",
    )
    plt.plot(
        threshold_results["time"],
        threshold_results["capacity"],
        label="Threshold Capacity",
    )
    plt.plot(
        context_results["time"],
        context_results["capacity"],
        label="Context-Aware Capacity",
    )
    plt.title("Demand vs Capacity")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Requests per Second")
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "demand_vs_capacity.png")
    plt.close()

    plt.figure()
    plt.plot(
        threshold_results["time"],
        threshold_results["latency"],
        label="Threshold Latency",
    )
    plt.plot(
        context_results["time"],
        context_results["latency"],
        label="Context-Aware Latency",
    )
    plt.axhline(
        y=SLA_THRESHOLD,
        label="SLA Threshold (250 ms)",
    )
    plt.title("Latency Comparison")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Latency (ms)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "latency_comparison.png")
    plt.close()

    plt.figure()
    plt.plot(
        threshold_results["time"],
        threshold_results["servers"],
        label="Threshold Servers",
    )
    plt.plot(
        context_results["time"],
        context_results["servers"],
        label="Context-Aware Servers",
    )
    plt.title("Active Servers")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Number of Active Servers")
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "active_servers.png")
    plt.close()


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

    RESULTS_DIR.mkdir(exist_ok=True)

    comparison = create_comparison_table(
        threshold_results,
        context_results,
    )
    comparison.to_csv(RESULTS_DIR / "comparison.csv", index=False)

    create_graphs(threshold_results, context_results)
