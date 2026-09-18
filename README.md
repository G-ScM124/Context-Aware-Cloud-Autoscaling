# Context-Aware Cloud Autoscaling Simulator

A Python simulation that compares a traditional threshold-based cloud autoscaling policy with a context-aware controller that uses multiple system signals to make scaling decisions.

The project explores whether using additional context — specifically utilization, traffic trend, and modeled latency — can improve autoscaling behaviour compared with a controller that reacts only to utilization thresholds.

## Research Question

Can a controller that uses several pieces of system context make better scaling decisions than a controller that only reacts to utilization thresholds?

## Motivation

Cloud systems must balance two competing goals:

- maintaining good service performance
- avoiding unnecessary infrastructure usage

A controller that allocates too little capacity can cause high latency or dropped requests. A controller that allocates too much capacity can waste computing resources.

Traditional autoscaling approaches often rely on simple threshold rules, such as adding capacity when utilization becomes too high.

This project compares that type of controller with a context-aware policy that also considers recent traffic behaviour and current latency.

## Project Overview

The simulator models a web service receiving changing traffic over 500 one-second periods.

At every time step, the system tracks:

- incoming request demand
- active server count
- total available capacity
- server utilization
- modeled latency
- dropped requests
- recent traffic trend

Two autoscaling policies are evaluated on the exact same traffic trace:

1. Threshold Controller
2. Context-Aware Controller

Both simulations begin with 3 active servers and are constrained to between 1 and 10 servers.

Each server can process 100 requests per second.

## Simulation Model

For each time period `t`:

### Capacity

```text
capacity = active servers × 100 requests/second
```

### Utilization

```text
utilization = demand / capacity
```

### Latency

Latency is modeled using:

```text
latency = 40 / (1 - min(utilization, 0.95))
```

The utilization value is capped at 0.95 only inside the latency equation to prevent the denominator from approaching zero.

Utilization itself is allowed to exceed 1.

### Dropped Requests

```text
dropped requests = max(0, demand - capacity)
```

If demand exceeds total server capacity, the excess traffic is treated as dropped.

## Traffic Generation

The simulation uses a 500-second synthetic workload.

The traffic pattern contains several phases:

- seconds 0-99: stable demand around 180 requests per second
- seconds 100-199: increasing demand from 180 to 420 requests per second
- seconds 200-249: high demand around 520 requests per second
- seconds 250-349: stable demand around 350 requests per second
- seconds 350-449: decreasing demand from 350 to 180 requests per second
- seconds 450-499: stable demand around 180 requests per second

Gaussian noise is added to the base traffic pattern to create variation in the workload.

A fixed NumPy random seed of 42 is used so the experiment is reproducible.

Both controllers receive the exact same generated traffic array.

## Controllers

### Threshold Controller

The threshold controller uses utilization as its only system signal.

It scales up when:

```text
utilization > 0.75
```

It scales down when utilization remains below:

```text
0.30
```

for three consecutive periods.

Otherwise, it keeps the current number of servers unchanged.

### Context-Aware Controller

The context-aware controller uses:

- utilization
- recent traffic trend
- modeled latency

It scales up if any of the following conditions are true:

```text
utilization > 0.75
```

or:

```text
utilization > 0.60
and
traffic trend > 0.10
```

or:

```text
latency > 200 ms
and
traffic trend > 0.05
```

It scales down only when both of the following conditions remain true for three consecutive periods:

```text
utilization < 0.35
```

and:

```text
traffic trend <= 0
```

This allows the controller to react not only to current system load, but also to whether traffic is increasing and whether latency is becoming elevated.

## Traffic Trend

Traffic trend is calculated using the most recent six demand observations.

The previous three observations are averaged and compared with the most recent three observations:

```text
trend = (recent average - previous average) / previous average
```

A positive trend indicates increasing traffic.

A negative trend indicates decreasing traffic.

If fewer than six observations are available, trend is set to zero.

## Scaling Timing

A scaling decision made during period `t` affects the server count in period `t+1`.

Current traffic is therefore always handled using the server capacity that was already active at the beginning of that period.

The sequence is:

```text
observe traffic
→ calculate system state
→ make scaling decision
→ apply decision to the next period
```

## Evaluation Metrics

The two controllers are compared using:

- Average Servers
- Total Server-Time
- Average Latency
- 95th Percentile Latency
- SLA Violations
- Total Dropped Requests
- Scaling Actions

An SLA violation is defined as:

```text
latency > 250 ms
```

Scaling actions count only successful changes in server count.

## Results

| Metric | Threshold | Context-Aware |
|---|---:|---:|
| Average Servers | 5.932 | 6.276 |
| Total Server-Time (server-seconds) | 2966 | 3138 |
| Average Latency (ms) | 88.41 | 80.29 |
| 95th Percentile Latency (ms) | 130.53 | 123.90 |
| SLA Violations | 1 | 1 |
| Total Dropped Requests | 0 | 0 |
| Scaling Actions | 8 | 11 |

The context-aware controller achieved lower average latency and lower 95th-percentile latency.

However, it also used more servers on average, consumed more total server-time, and performed more scaling actions.

Both controllers experienced one SLA violation and dropped no requests.

The experiment therefore shows a tradeoff between service performance and resource usage rather than one controller outperforming the other on every metric.

## Interpretation

The threshold controller was more conservative in its resource usage.

The context-aware controller reacted earlier during periods of rising demand and maintained more spare capacity during some high-demand periods.

That additional capacity contributed to improved latency.

The context-aware controller also scaled down earlier during falling traffic, showing that additional context influenced both scale-up and scale-down behaviour.

However, the added responsiveness came at the cost of more scaling activity and greater overall resource use.

Under this workload, the main benefit of the context-aware policy was improved latency rather than improved reliability, since both controllers avoided dropped traffic and recorded the same number of SLA violations.

## Visualizations

The `results/` directory contains three generated figures:

- `demand_vs_capacity.png`
- `latency_comparison.png`
- `active_servers.png`

It also contains:

- `comparison.csv`
- `results_summary.md`

## Project Structure

```text
Context-Aware-Cloud-Autoscaling/
│
├── simulator.py
├── controllers.py
├── experiment.py
├── requirements.txt
├── README.md
├── LICENSE
│
└── results/
    ├── comparison.csv
    ├── demand_vs_capacity.png
    ├── latency_comparison.png
    ├── active_servers.png
    └── results_summary.md
```

## File Descriptions

### `simulator.py`

Contains the system model and traffic generation logic.

It defines:

- server capacity
- base latency
- traffic generation
- utilization calculation
- latency calculation
- dropped-request calculation

### `controllers.py`

Contains the autoscaling policies.

It defines:

- traffic-trend calculation
- threshold controller
- context-aware controller

### `experiment.py`

Runs both controllers on the same workload.

It:

- executes the simulations
- stores time-series results
- calculates evaluation metrics
- creates the comparison table
- generates the three result graphs

### `results/`

Contains the experiment outputs and written summary.

## Requirements

The project uses:

- Python
- NumPy
- pandas
- Matplotlib

Install the dependencies with:

```bash
pip install -r requirements.txt
```

## How to Run

From the project directory, run:

```bash
python experiment.py
```

The simulation will run both controllers and generate the comparison table and graphs inside the `results/` directory.

## Reproducibility

The traffic generator uses a fixed NumPy random seed:

```text
42
```

This ensures the same synthetic traffic trace is generated each time the experiment is run.

Because both controllers are evaluated on the same traffic array, the comparison is performed under identical workload conditions.

## Limitations

This project uses a simplified simulation rather than a production cloud environment.

Limitations include:

- synthetic traffic
- fixed server capacity
- simplified latency modeling
- deterministic controller rules
- no server startup or provisioning delay
- no explicit infrastructure cost model
- no request queue or backlog
- evaluation on a single reproducible traffic trace

## Future Work

Possible extensions include:

- testing real workload traces
- introducing server provisioning delays
- modeling infrastructure cost
- adding request queues
- using more realistic latency models
- testing multiple traffic scenarios
- comparing additional autoscaling strategies
- exploring predictive or learning-based controllers

## License

This project is licensed under the MIT License.
