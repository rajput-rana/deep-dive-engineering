# Scalability

**Reference:** [AlgoMaster - Scalability](https://algomaster.io/learn/system-design/scalability)

## Problem / Concept Overview

Scalability is the ability of a system to handle increasing amounts of work by adding resources. As your user base grows from 1,000 to 1 million users, can your system accommodate this growth without breaking?

## Key Ideas

### Vertical Scaling (Scale Up)
- Add more power to existing machines (CPU, RAM, storage)
- **Pros:** Simple, no code changes needed
- **Cons:** Limited by hardware, expensive, single point of failure

### Horizontal Scaling (Scale Out)
- Add more machines to your system
- **Pros:** Nearly unlimited growth, cost-effective, fault-tolerant
- **Cons:** Requires distributed system design, data consistency challenges

### Scalability Dimensions
1. **User Scalability** - Handle more concurrent users
2. **Data Scalability** - Store and query larger datasets
3. **Geographic Scalability** - Serve users across regions

## Why It Matters

A system that doesn't scale becomes a bottleneck. When traffic spikes (e.g., Black Friday sales), unscalable systems crash, leading to:
- Lost revenue
- Poor user experience
- Reputation damage

## Real-World Examples

**Netflix:** Scales horizontally across AWS regions to serve 200M+ subscribers globally.

**Twitter:** Handles 500M+ tweets/day through horizontal scaling, sharding, and caching.

**Amazon:** Scales dynamically during Prime Day using auto-scaling groups.

## Tradeoffs

| Aspect | Vertical Scaling | Horizontal Scaling |
|--------|-----------------|-------------------|
| Complexity | Low | High |
| Cost | High (premium hardware) | Lower (commodity hardware) |
| Fault Tolerance | Single point of failure | Distributed, resilient |
| Limits | Hardware constraints | Nearly unlimited |

## Design Considerations

- **Stateless services** enable horizontal scaling
- **Load balancers** distribute traffic across instances
- **Database sharding** partitions data across machines
- **Caching** reduces load on backend systems
- **CDN** distributes static content globally

## Interview Tips

When discussing scalability:
1. Start with capacity estimation (users, QPS, data volume)
2. Identify bottlenecks (database, CPU, network)
3. Propose scaling strategies (horizontal preferred)
4. Discuss tradeoffs explicitly

