# Horizontal Scaling

## Summary

Horizontal scaling (scaling out) adds more machines to handle increased load. It's the preferred approach for cloud-native applications, enabling nearly unlimited growth and better fault tolerance compared to vertical scaling.

## Key Concepts

### Horizontal vs Vertical Scaling

**Horizontal Scaling (Scale Out):**
- Add more machines
- Distribute load across instances
- Nearly unlimited capacity
- Requires load balancing

**Vertical Scaling (Scale Up):**
- Add more power to existing machine
- Simpler, no code changes
- Limited by hardware
- Single point of failure

## Why It Matters

**Unlimited Growth:** Can add machines as needed.

**Fault Tolerance:** Multiple instances = no single point of failure.

**Cost Effective:** Use commodity hardware.

**Cloud Native:** Works well with auto-scaling.

## Real-World Examples

**Netflix:** Scales horizontally across AWS regions.

**Google:** Distributes search across thousands of servers.

**Amazon:** Auto-scales EC2 instances based on load.

**Kubernetes:** Orchestrates horizontal scaling automatically.

## Tradeoffs

### Advantages
- ✅ Nearly unlimited capacity
- ✅ Fault tolerant
- ✅ Cost effective (commodity hardware)
- ✅ Works with auto-scaling

### Challenges
- ❌ Requires distributed system design
- ❌ Data consistency challenges
- ❌ More complex operations
- ❌ Network latency between instances

## Design Considerations

### Stateless Design
- Services must be stateless for horizontal scaling
- Store state in shared storage (database, cache)
- Use session stores for user sessions

### Load Balancing
- Distribute traffic across instances
- Health checks for automatic failover
- Session affinity if needed

### Data Management
- Shared database or sharding
- Distributed caching
- Eventual consistency considerations

## Interview Hints

When discussing horizontal scaling:
1. Compare with vertical scaling
2. Explain stateless design requirement
3. Discuss load balancing
4. Address data consistency
5. Mention auto-scaling benefits
