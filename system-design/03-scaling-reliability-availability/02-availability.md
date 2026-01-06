# Availability

// (// 

## Summary

Availability measures the percentage of time a system is operational and accessible to users. It's typically expressed as "nines" (99.9%, 99.99%, etc.), where each additional nine represents exponentially more uptime.

## Key Concepts

### Availability Levels

- **99% (Two Nines):** ~87.6 hours downtime/year
- **99.9% (Three Nines):** ~8.76 hours downtime/year
- **99.99% (Four Nines):** ~52.56 minutes downtime/year
- **99.999% (Five Nines):** ~5.26 minutes downtime/year

### Calculating Availability

For components in **series** (all must work):
```
Availability = A1 × A2 × A3 × ...
```

For components in **parallel** (any can work):
```
Availability = 1 - (1 - A1) × (1 - A2) × ...
```

### Achieving High Availability

1. **Redundancy:** Multiple instances of critical components
2. **Failover:** Automatic switching to backup systems
3. **Health Monitoring:** Detect failures quickly
4. **Graceful Degradation:** Continue operating with reduced functionality
5. **Disaster Recovery:** Plan for catastrophic failures

## Why It Matters

**Business Impact:** Downtime costs money. Amazon's 2017 S3 outage cost companies millions in lost revenue.

**User Trust:** Users expect services to be available 24/7. Frequent outages damage reputation.

**SLA Requirements:** Many enterprise contracts require specific availability levels.

## Real-World Examples

**AWS:** 99.99% SLA for most services through multi-AZ deployment.

**Google:** Achieves 99.9%+ availability through global infrastructure.

**Netflix:** Designed for high availability to avoid service interruptions.

**Banking Systems:** Require 99.99%+ availability for critical operations.

## Tradeoffs

| Strategy | Availability Gain | Cost |
|----------|------------------|------|
| Single server | Baseline | Low |
| Multi-AZ redundancy | +1-2 nines | 2x cost |
| Multi-region | +2-3 nines | 3-4x cost |
| Active-active | Highest | Highest |

## Design Considerations

### Single Points of Failure
Identify and eliminate:
- Single database instance
- Single load balancer
- Single data center
- Single network path

### Failure Modes
Plan for:
- Server crashes
- Network partitions
- Database failures
- Third-party service outages
- Natural disasters

### Monitoring
- Uptime monitoring
- Health checks
- Alerting systems
- Incident response procedures

## Interview Hints

When discussing availability:
1. Calculate availability for your system design
2. Identify single points of failure
3. Propose redundancy strategies
4. Discuss tradeoffs (cost vs availability)
5. Explain how to measure and monitor availability
// (// 

