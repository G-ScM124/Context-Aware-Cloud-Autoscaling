# Results Summary

## Main Findings
Briefly state the main differences between the two controllers.

## Metric Comparison
Refer to comparison.csv and summarize the most important numbers.

## Interpretation
Explain the tradeoff between latency/reliability and resource usage.

## Observed Behaviour
Mention where the context-aware controller helped or overreacted.

## Limitations
Remind the reader that this is a simplified simulation.

## This experiment compared a traditional CPU-threshold autoscaling policy with a context-aware policy that also considered recent traffic trends and modeled latency.

The threshold controller used an average of 5.932 active servers, while the context-aware controller used 6.276. This resulted in 2966 server-seconds of total resource use for the threshold policy and 3138 server-seconds for the context-aware policy.

The additional resource allocation produced lower latency in the context-aware controller. Average modeled latency decreased from 88.41 ms to 80.29 ms, while 95th-percentile latency decreased from 130.53 ms to 123.90 ms.

Both controllers experienced one SLA violation, defined as latency exceeding 250 ms. Neither controller dropped any requests during the 500-second simulation, indicating that both policies maintained sufficient raw capacity for the generated workload.

The context-aware controller performed 11 successful scaling actions compared with 8 for the threshold controller. This reflects its greater responsiveness to changes in utilization, traffic trend, and latency.

Overall, the results demonstrate a resource-performance tradeoff. The context-aware controller achieved lower average and tail latency, but required greater average server allocation and more frequent scaling. Under this simulated workload, the primary benefit of incorporating additional system context was improved latency rather than a reduction in dropped requests or SLA violations.

These results are specific to the synthetic workload and simplified system model used in this project. Real cloud systems would also need to account for factors such as server startup delays, queueing behavior, infrastructure cost, and more complex traffic patterns.
