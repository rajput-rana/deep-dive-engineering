# Load Balancing Algorithms

**Reference:** [AlgoMaster - Load Balancing Algorithms](https://algomaster.io/learn/system-design/load-balancing-algorithms)

## Summary

Load balancing algorithms determine how incoming requests are distributed across multiple servers. The choice of algorithm significantly impacts performance, resource utilization, and user experience.

## Key Concepts

### Algorithm Types

1. **Round Robin**
   - Distributes requests sequentially
   - Simple, fair distribution
   - Doesn't consider server load
   - Good for equal-capacity servers

2. **Weighted Round Robin**
   - Assigns weights based on capacity
   - More traffic to powerful servers
   - Requires manual configuration
   - Good for heterogeneous servers

3. **Least Connections**
   - Routes to server with fewest active connections
   - Better for long-lived connections
   - More complex to implement
   - Good for connection-pooling scenarios

4. **Least Response Time**
   - Routes to fastest-responding server
   - Considers both connections and latency
   - Most intelligent but complex
   - Good for latency-sensitive applications

5. **IP Hash**
   - Routes based on client IP hash
   - Ensures same client → same server
   - Can cause uneven distribution
   - Good for session affinity

6. **Geographic**
   - Routes to nearest data center
   - Lowers latency
   - Requires geographic awareness
   - Good for global applications

## Why It Matters

**Performance:** Right algorithm reduces latency and improves throughput.

**Resource Utilization:** Efficient distribution maximizes server usage.

**User Experience:** Consistent routing improves session handling.

**Cost Efficiency:** Better load distribution = fewer servers needed.

## Real-World Examples

**NGINX:** Supports all major algorithms, default is round robin.

**AWS ELB:** Uses least connections for TCP, round robin for HTTP.

**HAProxy:** Advanced algorithms including least response time.

**Google Cloud LB:** Geographic routing for global distribution.

**F5:** Hardware load balancers with advanced algorithms.

## Tradeoffs

| Algorithm | Complexity | Performance | Fairness | Use Case |
|-----------|-----------|-------------|----------|----------|
| Round Robin | Low | Medium | High | Equal servers |
| Weighted RR | Medium | Medium | Medium | Heterogeneous |
| Least Connections | Medium | High | High | Long connections |
| Least Response Time | High | Highest | High | Latency critical |
| IP Hash | Low | Medium | Low | Session affinity |

## Design Considerations

### Choosing an Algorithm

**Consider:**
1. Server capacity (equal vs heterogeneous)
2. Connection type (short vs long-lived)
3. Latency requirements
4. Session requirements
5. Geographic distribution

### Algorithm Selection Guide

- **Equal servers, stateless:** Round Robin
- **Different capacities:** Weighted Round Robin
- **Long connections:** Least Connections
- **Latency critical:** Least Response Time
- **Session affinity:** IP Hash
- **Global users:** Geographic

## Performance Impact

**Round Robin:**
- Simple but can overload slow servers
- Good for equal-capacity servers

**Least Connections:**
- Better load distribution
- Handles varying request processing times

**Least Response Time:**
- Optimal performance
- Requires monitoring overhead

## Interview Hints

When discussing load balancing:
1. Identify server characteristics
2. Consider connection patterns
3. Choose appropriate algorithm
4. Discuss tradeoffs
5. Address edge cases (server failures, etc.)

## Reference

[AlgoMaster - Load Balancing Algorithms](https://algomaster.io/learn/system-design/load-balancing-algorithms)

