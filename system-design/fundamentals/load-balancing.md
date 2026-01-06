# Load Balancing

**Reference:** [AlgoMaster - Load Balancing](https://algomaster.io/learn/system-design/load-balancing)

## Problem / Concept Overview

Load balancing distributes incoming network traffic across multiple servers to ensure no single server is overwhelmed. It's essential for horizontal scaling and high availability.

## Key Ideas

### Load Balancing Algorithms

1. **Round Robin**
   - Distributes requests sequentially
   - Simple, fair distribution
   - Doesn't consider server load

2. **Least Connections**
   - Routes to server with fewest active connections
   - Better for long-lived connections
   - More complex to implement

3. **Weighted Round Robin**
   - Assigns weights based on server capacity
   - Routes more traffic to powerful servers
   - Requires manual configuration

4. **IP Hash**
   - Routes based on client IP hash
   - Ensures same client → same server (sticky sessions)
   - Can cause uneven distribution

5. **Least Response Time**
   - Routes to fastest-responding server
   - Considers both connections and response time
   - Most intelligent but complex

## Architecture Pattern

```
┌─────────┐
│ Clients │
└────┬────┘
     │
     ▼
┌──────────────┐
│Load Balancer │
└──────┬───────┘
       │
   ┌───┴───┬────┬────┐
   │       │    │    │
   ▼       ▼    ▼    ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐
│Srv1│ │Srv2│ │Srv3│ │Srv4│
└────┘ └────┘ └────┘ └────┘
```

## Why It Matters

**High Availability:** If one server fails, traffic routes to healthy servers.

**Scalability:** Add servers without code changes—just update load balancer config.

**Performance:** Distributes load, prevents any server from becoming bottleneck.

**SSL Termination:** Handle TLS/SSL at load balancer, reducing backend load.

## Real-World Examples

**AWS ELB/ALB:** Distributes traffic across EC2 instances automatically.

**NGINX:** Popular software load balancer, handles millions of requests.

**Google Cloud Load Balancer:** Global load balancing across regions.

**Netflix:** Uses multiple load balancers for different services.

## Tradeoffs

### Layer 4 (Transport Layer) Load Balancing
- **Pros:** Fast, simple, works with any protocol
- **Cons:** No content awareness, can't route based on URL

### Layer 7 (Application Layer) Load Balancing
- **Pros:** Content-aware routing, SSL termination, advanced routing
- **Cons:** More CPU intensive, higher latency

## Types of Load Balancers

1. **Hardware Load Balancer**
   - Dedicated appliances (F5, Citrix)
   - High performance, expensive
   - Less flexible

2. **Software Load Balancer**
   - Runs on commodity hardware (NGINX, HAProxy)
   - Cost-effective, flexible
   - Lower performance than hardware

3. **Cloud Load Balancer**
   - Managed service (AWS ELB, GCP LB)
   - Auto-scaling, integrated with cloud services
   - Vendor lock-in

## Health Checks

Load balancers continuously check server health:
- **Active:** Send requests to servers periodically
- **Passive:** Monitor response times and errors
- **Graceful Shutdown:** Stop sending new requests, wait for existing to complete

## Session Affinity (Sticky Sessions)

**Problem:** Some applications require same client → same server.

**Solutions:**
- IP-based routing (not reliable with NAT)
- Cookie-based routing (application-level)
- Session data in shared cache (Redis)

**Tradeoff:** Reduces load distribution flexibility.

## Design Considerations

- **Single Point of Failure:** Use multiple load balancers (active-passive or active-active)
- **Geographic Distribution:** Route users to nearest data center
- **Auto-scaling:** Automatically add/remove servers based on load
- **Monitoring:** Track metrics (requests/sec, error rates, latency)

## Common Patterns

1. **Load Balancer → Application Servers**
   - Simple, common pattern
   - Stateless application servers

2. **Load Balancer → API Gateway → Services**
   - Microservices pattern
   - API gateway handles routing

3. **CDN → Load Balancer → Servers**
   - Global distribution
   - CDN for static, LB for dynamic

## Interview Tips

When discussing load balancing:
1. Identify where it's needed (frontend, API, database)
2. Choose algorithm based on use case
3. Discuss health checks and failover
4. Address session affinity if needed
5. Consider geographic distribution

