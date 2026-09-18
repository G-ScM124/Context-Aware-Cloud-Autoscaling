def calculate_trend(demand_history):
    """Calculate the demand trend between the two most recent 3-period windows."""
    if len(demand_history) < 6:
        return 0.0

    recent_average = sum(demand_history[-3:]) / 3
    previous_average = sum(demand_history[-6:-3]) / 3

    if previous_average == 0:
        return 0.0

    return (recent_average - previous_average) / previous_average


def threshold_controller(utilization_history):
    """Return the threshold controller's action for the current period."""
    current_utilization = utilization_history[-1]

    if current_utilization > 0.75:
        return 1

    if (
        len(utilization_history) >= 3
        and all(
            utilization < 0.30
            for utilization in utilization_history[-3:]
        )
    ):
        return -1

    return 0


def context_controller(utilization_history, latency, trend_history):
    """Return the context-aware controller's action for the current period."""
    current_utilization = utilization_history[-1]
    current_trend = trend_history[-1]

    if current_utilization > 0.75:
        return 1

    if current_utilization > 0.60 and current_trend > 0.10:
        return 1

    if latency > 200 and current_trend > 0.05:
        return 1

    if (
        len(utilization_history) >= 3
        and len(trend_history) >= 3
        and all(
            utilization < 0.35 and trend <= 0
            for utilization, trend in zip(
                utilization_history[-3:],
                trend_history[-3:],
            )
        )
    ):
        return -1

    return 0
