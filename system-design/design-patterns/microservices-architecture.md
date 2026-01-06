# Microservices Architecture

**Reference:** [AlgoMaster - Microservices Architecture](https://algomaster.io/learn/system-design/microservices-architecture)

## Problem / Concept Overview

Microservices architecture decomposes an application into small, independent services that communicate over well-defined APIs. Each service owns its data and can be developed, deployed, and scaled independently.

## Key Ideas

### Core Principles
- **Service Independence:** Each service runs in its own process
- **Decentralized Data:** Each service manages its own database
- **Technology Diversity:** Services can use different tech stacks
- **Failure Isolation:** One service failure doesn't crash the system

### Architecture Pattern

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  API Gateway    │
└──────┬──────────┘
       │
   ┌───┴───┬────────┬────────┐
   │       │        │        │
   ▼       ▼        ▼        ▼
┌────┐ ┌────┐  ┌────┐  ┌────┐
│User│ │Order│ │Pay │ │Notif│
│Svc │ │Svc │ │Svc │ │Svc │
└────┘ └────┘ └────┘ └────┘
```

## Why It Matters

**Scalability:** Scale individual services based on demand (e.g., scale payment service during checkout peaks).

**Team Autonomy:** Teams can work independently, ship faster.

**Technology Flexibility:** Use the right tool for each service (Python for ML, Go for high-throughput).

**Fault Isolation:** Payment service failure doesn't affect user authentication.

## Real-World Examples

**Netflix:** 700+ microservices handling streaming, recommendations, billing.

**Amazon:** Each team owns services end-to-end, enabling rapid innovation.

**Uber:** Separate services for ride matching, payment, notifications, maps.

## Tradeoffs

### Advantages
- ✅ Independent scaling
- ✅ Technology diversity
- ✅ Team autonomy
- ✅ Fault isolation
- ✅ Easier to understand (smaller codebase per service)

### Disadvantages
- ❌ Network latency (service-to-service calls)
- ❌ Data consistency challenges (distributed transactions)
- ❌ Operational complexity (monitoring, deployment)
- ❌ Testing complexity (integration tests)
- ❌ Higher infrastructure costs

## Communication Patterns

1. **Synchronous:** REST, gRPC
   - Simple, but creates coupling
   - Cascading failures possible

2. **Asynchronous:** Message queues, event streaming
   - Decoupled, resilient
   - Eventual consistency

## Design Considerations

- **API Gateway:** Single entry point, handles routing, auth, rate limiting
- **Service Discovery:** Services find each other (Consul, Eureka)
- **Configuration Management:** Centralized config (Config Server)
- **Distributed Tracing:** Track requests across services (Jaeger, Zipkin)
- **Circuit Breaker:** Prevent cascading failures

## When to Use

**Good for:**
- Large, complex applications
- Multiple teams
- Different scaling requirements per feature
- Need for technology diversity

**Avoid when:**
- Small team/application
- Tight coupling between features
- Simple CRUD application
- Limited operational expertise

## Migration Strategy

1. Start with monolith
2. Identify bounded contexts
3. Extract one service at a time
4. Use strangler fig pattern
5. Gradually decompose

