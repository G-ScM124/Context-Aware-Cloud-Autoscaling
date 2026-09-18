# Results Summary

## Main Findings
The context-aware controller achieved lower latency than the traditional threshold controller, but it did so by using slightly more server capacity and making more scaling decisions.

Across the 500-second simulation, both controllers successfully handled all incoming traffic without dropping requests. Both also experienced one SLA violation, meaning that the main performance difference between the controllers was latency rather than reliability.

The context-aware controller reduced both average latency and 95th-percentile latency, suggesting that incorporating traffic trend and latency information helped the controller maintain better service performance during changing traffic conditions.

## Metric Comparison
The threshold controller used an average of 5.932 active servers, compared with 6.276 for the context-aware controller.

This resulted in:

- Threshold controller: 2966 server-seconds
- Context-aware controller: 3138 server-seconds

Average latency decreased from 88.41 ms with the threshold controller to 80.29 ms with the context-aware controller.

The 95th-percentile latency also decreased:

- Threshold controller: 130.53 ms
- Context-aware controller: 123.90 ms

Both controllers recorded:

- 1 SLA violation
- 0 dropped requests

The context-aware controller performed 11 successful scaling actions, compared with 8 for the threshold controller.

The complete numerical results are available in `comparison.csv`.

## Interpretation
The results demonstrate a tradeoff between service performance and resource usage.

The context-aware controller achieved better average and tail latency, but required more server capacity and more frequent scaling. Its average server usage increased from 5.932 to 6.276 servers, while its total server-time increased by 172 server-seconds.

This additional capacity appears to have contributed to the lower latency observed during the simulation.

However, the additional resource use did not reduce the number of SLA violations or dropped requests. Both controllers experienced one SLA violation and zero dropped requests.

Therefore, under this workload, the primary benefit of the context-aware policy was improved latency rather than improved reliability.

## Observed Behaviour
The context-aware controller generally scaled earlier and more aggressively during periods of increasing traffic.

For example, it increased server capacity before the threshold controller during the early traffic ramp and eventually reached a maximum of 9 active servers, compared with 8 for the threshold controller.

During the high-demand portion of the simulation, the context-aware controller maintained more spare capacity, which helped reduce latency.

The controller also scaled down earlier during falling demand, eventually finishing with fewer active servers than the threshold controller.

However, the context-aware controller was not better at every moment. It experienced a short latency spike above the 250 ms SLA threshold around the high-demand transition. This contributed to its single SLA violation.

Its higher number of scaling actions also suggests that the additional context made the controller more responsive, but also somewhat more active than the simpler threshold policy.

## Limitations
This experiment uses a simplified simulation and should not be interpreted as a model of a production cloud platform.

Important limitations include:

- synthetic rather than real-world traffic
- fixed server capacity of 100 requests per second
- a simplified latency equation
- deterministic scaling rules
- no server startup or provisioning delay
- no explicit infrastructure cost model
- no queueing or request backlog model
- evaluation using a single reproducible traffic trace

Future work could test the controllers against real workload traces, model server provisioning delays, include monetary cost, use more realistic queueing behaviour, and compare additional control strategies.
