# Reliability

**Reference:** [AlgoMaster - Reliability](https://algomaster.io/learn/system-design/reliability)

## Problem / Concept Overview

Reliability is the probability that a system will perform its intended function without failure over a specified period. In distributed systems, failures are inevitable—design for them.

## Key Ideas

### Reliability Metrics
- **MTBF (Mean Time Between Failures):** Average time between system failures
- **MTTR (Mean Time To Repair):** Average time to fix a failure
- **Availability:** Percentage of time system is operational
  - 99.9% = ~8.76 hours downtime/year
  - 99.99% = ~52.56 minutes downtime/year

### Fault Tolerance Strategies

1. **Redundancy**
   - Multiple instances of critical components
   - Active-active or active-passive configurations
   - Eliminates single points of failure

2. **Health Checks & Monitoring**
   - Regular health checks detect failures early
   - Automatic failover to healthy instances
   - Examples: Kubernetes liveness/readiness probes

3. **Graceful Degradation**
   - System continues operating with reduced functionality
   - Better than complete failure
   - Example: Show cached data when database is down

4. **Circuit Breaker Pattern**
   - Stop calling failing services
   - Prevents cascading failures
   - Auto-recovery after timeout

## Why It Matters

**Business Impact:** Downtime costs money. Amazon's 2017 S3 outage cost companies millions.

**User Trust:** Unreliable systems lose users permanently.

**Compliance:** Many industries require high availability (finance, healthcare).

## Real-World Examples

**AWS Multi-AZ:** Replicates data across availability zones for 99.99% uptime.

**Netflix Chaos Engineering:** Intentionally breaks systems to improve reliability.

**Gmail:** 99.9% uptime through redundancy and automatic failover.

## Tradeoffs

| Strategy | Reliability Gain | Cost |
|----------|-----------------|------|
| Redundancy | High | 2x infrastructure cost |
| Monitoring | Early detection | Operational overhead |
| Graceful Degradation | Better UX | Code complexity |
| Circuit Breaker | Prevents cascades | Additional latency |

## Failure Scenarios

Design for these common failures:
1. **Server crashes:** Process dies, machine reboots
2. **Network partitions:** Services can't communicate
3. **Database failures:** Connection loss, data corruption
4. **Third-party outages:** External API failures
5. **Resource exhaustion:** Memory, CPU, disk full

## Design Principles

- **Assume failures will happen:** Design defensively
- **Fail fast:** Detect and handle errors quickly
- **Idempotency:** Operations safe to retry
- **Timeouts:** Don't wait indefinitely
- **Retries with backoff:** Handle transient failures
- **Monitoring:** Know when things break

## Availability Calculation

For components in series:
```
Availability = A1 × A2 × A3 × ...
```

For components in parallel:
```
Availability = 1 - (1 - A1) × (1 - A2) × ...
```

**Example:** 3 servers with 99% availability each:
- Series: 99% × 99% × 99% = 97.03%
- Parallel: 1 - (0.01 × 0.01 × 0.01) = 99.9999%

