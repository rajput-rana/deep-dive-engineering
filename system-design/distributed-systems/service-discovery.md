# Service Discovery

**Reference:** [AlgoMaster - Service Discovery](https://algomaster.io/learn/system-design/service-discovery)

## Summary

Service discovery enables services in a distributed system to find and communicate with each other dynamically. Instead of hardcoding service locations, services register themselves and clients discover them automatically.

## Key Concepts

### Service Discovery Patterns

1. **Client-Side Discovery**
   ```
   Client → Service Registry → Get service list → Direct connection
   ```
   - Client queries registry
   - Client connects directly to service
   - Simpler service implementation
   - Client complexity increases

2. **Server-Side Discovery**
   ```
   Client → Load Balancer → Service Registry → Route to service
   ```
   - Load balancer queries registry
   - Client connects via load balancer
   - Simpler client
   - Load balancer becomes critical component

### Service Registry Types

1. **Self-Registration**
   - Services register themselves
   - Services deregister on shutdown
   - Simple but requires health checks

2. **Third-Party Registration**
   - Service registrar handles registration
   - Monitors service health
   - More reliable, additional component

## Why It Matters

**Dynamic Environments:** In cloud/container environments, service instances come and go. Hardcoded IPs don't work.

**Scalability:** Services can scale up/down without client reconfiguration.

**Resilience:** Failed instances are automatically removed from discovery.

**Load Distribution:** Enables intelligent routing and load balancing.

## Real-World Examples

**Kubernetes:** Built-in service discovery via DNS and service objects.

**Consul:** Service discovery with health checking and key-value store.

**Eureka:** Netflix's service registry for microservices.

**Zookeeper:** Used by many systems for service coordination.

**AWS ECS/EC2:** Integrated service discovery via Route 53 or Cloud Map.

## Architecture Pattern

```
┌─────────┐
│ Service │
│   A     │
└────┬────┘
     │ Register
     ▼
┌──────────────┐
│   Service    │
│   Registry   │
└──────┬───────┘
       │ Query
       │
┌──────▼──────┐
│   Service   │
│     B       │
└─────────────┘
```

## Tradeoffs

### Client-Side vs Server-Side Discovery

| Aspect | Client-Side | Server-Side |
|--------|------------|-------------|
| Complexity | Client-side | Server-side |
| Load Balancer | Not needed | Required |
| Language Support | Client libraries needed | Language agnostic |
| Failure Handling | Client responsibility | Load balancer handles |

### Service Registry Options

**Consul:**
- ✅ Health checking
- ✅ Multi-datacenter support
- ❌ Additional infrastructure

**Eureka:**
- ✅ Netflix proven
- ✅ Self-preservation mode
- ❌ Java-focused

**Kubernetes:**
- ✅ Built-in, no extra component
- ✅ Integrated with orchestration
- ❌ Kubernetes-specific

## Design Considerations

### Health Checks
- Regular health check intervals
- Failure detection time
- Deregistration on failure

### Service Registration
- Register on startup
- Heartbeat to stay registered
- Deregister on graceful shutdown

### Load Balancing
- Distribute requests across instances
- Consider instance capacity
- Handle instance failures

### Caching
- Cache service locations in clients
- TTL for cache entries
- Refresh on failure

## Common Challenges

1. **Registry Failure:** Registry becomes single point of failure
   - Solution: Multiple registry instances, caching

2. **Stale Registrations:** Dead services remain registered
   - Solution: Health checks, TTLs

3. **Network Partitions:** Services can't reach registry
   - Solution: Caching, fallback mechanisms

## Interview Hints

When discussing service discovery:
1. Explain why it's needed (dynamic environments)
2. Choose pattern (client-side vs server-side)
3. Select registry solution
4. Address failure scenarios
5. Discuss caching and performance

## Reference

[AlgoMaster - Service Discovery](https://algomaster.io/learn/system-design/service-discovery)

