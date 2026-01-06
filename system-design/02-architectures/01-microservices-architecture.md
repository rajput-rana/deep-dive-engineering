# Microservices Architecture

**What it is:** An architectural approach where applications are built as a collection of small, independently deployable services.

**One-line:** Small, independently deployable services that focus on doing one thing well, aligned to specific business capabilities.

## What Problem Do Microservices Solve?

### The Monolith (Starting Point)

A monolith is a single application:
- One codebase
- One deployment unit
- One database (usually)

**Example:**
```
E-commerce App
├── User Management
├── Product Catalog
├── Orders
├── Payments
└── Notifications
```

### Why Monoliths Hurt at Scale

Monoliths work well early, but struggle when:
- **Teams grow** - Merge conflicts, ownership confusion
- **Releases slow down** - Everything deploys together
- **One bug can crash everything** - No isolation
- **Scaling one feature requires scaling the whole app** - Inefficient

**Microservices exist to optimize for team velocity, scalability, and ownership.**

## What Is a Microservice?

A microservice is:
- A small, independently deployable service
- Focused on one business capability
- Owned by one team
- Has its own data

**Example:**
- **User Service** → manages users
- **Order Service** → manages orders
- **Payment Service** → handles payments
- **Notification Service** → sends emails/push

**Each service:**
- Has its own codebase
- Runs in its own process
- Communicates via APIs/events

## Microservices Language Selection

**IMPORTANT:** Language choice depends on workload characteristics, latency SLAs, team expertise, and operational maturity.

| Language | Best Used For | Typical Latency (p95) | Throughput | K8s Cost | Strengths | Tradeoffs |
|----------|---------------|----------------------|------------|----------|-----------|-----------|
| **Java** | Core backend services + CPU heavy logics | 20–50 ms | High (10k–100k RPS) | Medium–High | Strong typing, mature ecosystem, excellent observability | Slower startup, higher memory |
| **Node.js** | API orchestration, BFFs | 10–30 ms | Medium–High (5k–50k RPS) | Low–Medium | Non-blocking I/O, fast dev, efficient for I/O | Poor CPU scaling |
| **Python** | ML, data-heavy services | 50–200 ms | Low–Medium (1k–10k RPS) | High | Best ML ecosystem, rapid iteration | GIL, slower runtime |
| **Go** | Infra & networking services | 5–20 ms | High (20k–200k RPS) | Low | Fast startup, low memory, great concurrency | Verbose business logic |
| **C/C++** | Ultra-low latency systems | <5 ms | Very High | Low (per pod) / High dev cost | Max performance, memory control | Hard to maintain |
| **C#/.NET** | Enterprise backend services | 20–40 ms | High (10k–80k RPS) | Medium | Excellent async model, strong tooling | Smaller OSS ecosystem |
| **Rust** | Safety-critical, high-perf | 5–15 ms | Very High | Low | Memory safety + performance | Steep learning curve |

### Why Java for Core Backend Services?

**Core backend services do:**
- Payments
- Orders
- Pricing
- Authorization
- State machines
- Workflows

**These involve:**
- Complex business rules
- Heavy data validation
- Calculations
- State transitions
- Consistency guarantees

**Java provides:**
- Strong typing
- Compile-time guarantees
- Mature concurrency primitives
- Safer refactoring

**For money & state:** Predictability beats raw efficiency

### Why Node.js for I/O-Heavy Services?

**Non-blocking I/O** means a thread doesn't wait while an I/O operation completes, allowing it to handle other work.

**Node.js is:**
- Single-threaded
- Event-loop based
- Efficient for I/O-heavy workloads

**But:** One slow CPU task can block the entire service

## Core Principles

### 1. Single Responsibility (Business-Oriented)

A service should map to a business domain, not a technical layer.

**❌ Bad:**
- AuthService
- DBService

**✅ Good:**
- BillingService
- InventoryService

### 2. Independent Deployment

You must be able to:
- Deploy Order Service without redeploying User Service

**If you can't → you don't really have microservices.**

### 3. Own Your Data

Each service owns its database.

**❌ Shared DB:**
```
User Service ↔ Orders DB ↔ Order Service
```

**✅ Isolated DBs:**
```
User Service → User DB
Order Service → Order DB
```

This prevents tight coupling.

## How Microservices Communicate

### 1. Synchronous (Request/Response)

Usually HTTP/REST or gRPC.

**Example:**
```
Order Service → calls → Payment Service
```

**Pros:**
- ✅ Simple
- ✅ Easy to debug

**Cons:**
- ❌ Tight coupling
- ❌ Cascading failures

### 2. Asynchronous (Events)

Using Kafka, RabbitMQ, SQS, etc.

**Example:**
```
OrderPlaced Event
→ Payment Service
→ Inventory Service
→ Notification Service
```

**Pros:**
- ✅ Loose coupling
- ✅ Better scalability

**Cons:**
- ❌ Harder debugging
- ❌ Event versioning complexity

**Mature systems use both.**

## Data Consistency: The Hard Part

### The Problem

**In a monolith:**
```sql
BEGIN TRANSACTION
  Create Order
  Charge Payment
  Update Inventory
COMMIT
```

**In microservices → no distributed transactions.**

### Solution: Eventual Consistency

#### Saga Pattern

Break one transaction into steps.

**Example:**
1. Order Service creates order (PENDING)
2. Emits OrderCreated
3. Payment Service charges card
4. Emits PaymentSuccessful
5. Order Service marks order CONFIRMED

**If step fails → compensating action.**

## Service Discovery & Routing

### Problem

Services scale dynamically. IPs change.

### Solutions

- **Kubernetes DNS**
- **Service Mesh** (Istio, Linkerd)
- **API Gateway**

### API Gateway

**Single entry point:**
```
Client → API Gateway → Services
```

**Responsibilities:**
- Auth
- Rate limiting
- Routing
- Monitoring

## Deployment & Infrastructure

### Containers

**Docker** packages service + dependencies

### Orchestration

**Kubernetes** manages:
- Scaling
- Health checks
- Restarts

**Typical setup:**
```
Pod → Service → Ingress → Gateway
```

## Observability (Non-Negotiable)

Microservices fail silently unless observed.

### Required Pillars

1. **Logging**
   - Centralized logs (ELK, Loki)

2. **Metrics**
   - Latency
   - Error rates
   - Throughput

3. **Tracing**
   - Distributed tracing (Jaeger, Zipkin)

**Example:**
- Request ID travels across services

## Testing Strategy

### Test Pyramid (Modified)

- **Unit tests** (inside service)
- **Contract tests** (between services)
- **Integration tests** (critical paths)

**Avoid:**
- End-to-end tests for everything (slow, flaky)

## Security Basics

- **Zero trust** between services
- **mTLS** (service-to-service auth)
- **Secrets** via Vault/K8s secrets
- **Never trust internal traffic blindly**

## Common Anti-Patterns

### ❌ Distributed Monolith

- Services must deploy together
- Shared DB

### ❌ Chatty Services

- 10+ synchronous calls per request

### ❌ Too Many Services Too Early

- 20 services with 3 engineers

### ❌ Tech-Oriented Split

- Split by controllers/repos instead of business

## When NOT to Use Microservices

**Do NOT start with microservices if:**
- Team < 10 engineers
- Product still finding market fit
- No DevOps maturity

**Start with a well-structured monolith.**

**Path:** Monolith → Modular Monolith → Microservices

## How to Go from 0 → 1 (Practical Path)

1. **Learn Domain Modeling**
   - Understand business boundaries

2. **Build a Modular Monolith**
   - Clear modules
   - No circular dependencies

3. **Extract First Service**
   - Choose low-risk domain (Notifications, Search)

4. **Add Infra**
   - CI/CD
   - Monitoring
   - Gateway

5. **Scale Gradually**
   - One service at a time

## Mental Model Summary

**Microservices are:**
- An organizational architecture, not just technical
- Optimized for team autonomy
- Expensive but powerful

**If you don't need independent teams, you don't need microservices.**

## Common Interview Questions

### Foundational Questions

**Q: What is a microservice?**
A microservice is a small, independently deployable unit that focuses on doing one thing well, often aligned to a specific business feature. It owns its own logic and data store, can be developed/deployed/scaled independently, and communicates via lightweight protocols.

**Q: How is a monolith different from microservices?**
In a monolith, everything is bundled into a single application deployed as one entity. A bug in one module can disrupt everything. In microservices, each function resides in its own service, bringing flexibility but also complexity.

**Q: What are the main benefits?**
- Scalability: Scale just the bottleneck service
- Deployment speed: Faster CI/CD cycles
- Tech freedom: Each service can use best language/framework
- Fault isolation: One failing service doesn't bring down entire system

**Q: What are the downsides?**
- Increased complexity: More services, more DevOps overhead
- Debugging nightmare: Tracing bugs across services
- Distributed data management: No simple JOINs
- Latency and failure handling: Network calls can fail

**Q: How do microservices communicate?**
- HTTP/REST APIs: Simple, synchronous
- gRPC: Faster, more compact, ideal for internal calls
- Message brokers (Kafka, RabbitMQ): Asynchronous, event-driven

**Q: What is an API Gateway?**
Sits between clients and services. Handles routing, authentication, rate limiting, and aggregating responses. Without it, clients would need to know location and protocol for each microservice.

**Q: Synchronous vs asynchronous communication?**
- Synchronous: Service calls another and waits (HTTP requests)
- Asynchronous: Service sends message and continues (Kafka topics)
- Async is great for performance and fault tolerance but more complicated

**Q: What is service discovery?**
Services are dynamic - they scale up/down, move across hosts, change IPs. Service discovery solves how services find each other without hardcoding locations. Tools: Consul, Eureka, Kubernetes DNS.

**Q: What does stateless mean?**
A stateless service doesn't store session data between requests. Each request is independent. Enables easier scaling, fewer sync issues, simpler deployments. State should be stored externally (Redis, database).

**Q: How do containers fit in?**
Containers (Docker) package service + dependencies into lightweight, portable units. Leads to consistency across environments, isolation, and easy scaling with orchestrators like Kubernetes.

### Intermediate Questions

**Q: How does service discovery work?**
1. Service registration: Service registers with central registry (name, IP, port, metadata)
2. Service lookup: Query registry to find target service
3. Instance selection: Registry returns available instances
4. Communication: Requesting service communicates with selected instance

**Q: What is API versioning strategy?**
- URI versioning: `/api/v1/products` (most readable, 90% of cases)
- Header versioning: `Accept: application/vnd.api.v1+json`
- Query param: `/api/products?version=1`

**Why it matters:** Backward compatibility, controlled updates, reduced risk, better communication, flexibility.

**Q: How do you secure microservices?**
- Centralized authentication: OAuth/OpenID Connect
- Least privilege: Each service only has required permissions
- Secure communication: mTLS for service-to-service
- API gateways: Centralize authentication logic
- Rate limiting: Prevent DoS/DDoS attacks

**Q: What is a circuit breaker pattern?**
Stops failing service from bringing down entire system. If service fails too many times:
1. Circuit opens - blocks further calls
2. Half-opens after interval - tests if service recovered
3. Closes if restored - allows regular traffic

**Benefits:** Prevents cascading failures, reduces resource consumption, allows service recovery.

**Q: How do you handle centralized logging?**
- Log shippers: Collect logs (Fluentd, Logstash)
- Storage and search: Elasticsearch
- Visualization: Kibana, Grafana
- Always add trace_id and span_id to logs

**Q: How do you monitor microservices?**
- Metrics: Prometheus
- Dashboards: Grafana
- Tracing: Jaeger, OpenTelemetry
- Alerting: PagerDuty

**Q: What are common deployment strategies?**
- Blue-green: Switch traffic between two identical environments
- Canary releases: Roll out to subset, monitor, gradually increase
- Rolling updates: Gradually replace old instances with new ones

**Q: How do you handle failures across multiple services?**
- Retries with exponential backoff
- Circuit breakers
- Fallbacks & graceful degradation
- Monitoring & alerting
- Redundancy & failover

**Q: How do you test microservices?**
- Unit tests: Validate individual service logic
- Integration tests: Test interactions with dependencies
- Contract tests: Ensure services agree on API contracts
- End-to-end tests: Validate entire system flow

**Q: How do you manage configuration?**
- External config: Environment variables, config files, config management systems
- Secrets management: AWS Secrets Manager, Vault, Kubernetes secrets
- Version control: GitOps approach

### Advanced Questions

**Q: How do you handle data consistency?**
You don't handle it all the time - you manage eventual consistency.

**Approaches:**
- Sagas: Series of local transactions with compensating actions
- Outbox pattern: Write to DB and message queue in single transaction
- Event sourcing: Store sequence of state-changing events
- 2PC: Two-phase commit (complex, performance bottleneck, doesn't scale well)

**Q: What is CAP theorem and how does it apply?**
CAP theorem: In distributed systems, you can only guarantee two of three:
- Consistency
- Availability
- Partition tolerance (must tolerate partitions)

**In practice:** Partitions are inevitable, so choose between consistency and availability.

- Banking app: Consistency > Availability
- Social media: Availability > Consistency

**Q: What's the difference between event sourcing and CRUD?**
- CRUD: Database stores only latest state (updating balance overwrites old value)
- Event sourcing: Every change stored as immutable event, current state reconstructed by replaying events

**Advantages:** Full audit trail, easy to recreate state at any point, decouples services.

**Drawbacks:** More complex, requires careful design.

**Q: What is distributed tracing?**
In microservices, user request hops across multiple services. Tracing helps follow that path.

**Components:**
- Trace ID: One ID per request, shared across services
- Span: Unit of work within a service
- Tools: Jaeger, Zipkin, OpenTelemetry

**Q: How do you manage schema evolution in event-driven systems?**
- Schema registries: Central registry to store different versions
- Versioning: Assign versions, maintain backward compatibility
- Data transformation: Transform events from older to newer schemas

**Q: How would you design a multi-region system?**
- Traffic routing: Direct users to nearest region (geographic DNS, global load balancer)
- Data strategy: Region-local databases, replicate only necessary data, accept eventual consistency
- Service design: Keep services stateless
- Failover planning: Automated failover between regions
- Compliance: Data zones per region for regulatory requirements

**Q: How do you implement rate limiting?**
- Token Bucket: Tokens added at fixed rate, requests consume tokens
- Leaky Bucket: Requests processed at fixed rate, excess queued or dropped
- Fixed/Sliding Window: Count requests within time window

**Q: What's chaos engineering?**
Intentionally breaking things to test resilience. Tools like Chaos Monkey simulate failures (kill pods, cut network, delay responses). Goal: Determine how system responds to stress.

**Q: How do you benchmark performance?**
Test for throughput, response time, error rate, latency, resource usage. Use test environment mirroring production. Tools: Locust, k6, Gatling for load testing; Prometheus + Grafana for metrics; Jaeger for tracing.

**Q: How do you decide the right size of a microservice?**
Balance complexity and independence:
- Aligned to single business capability
- One team should own it
- If too many dependencies, probably too big
- No right/wrong answer - depends on specific setup

### Behavioral Questions

**Q: Describe a microservice failure in production.**
Structure: Root cause → Impact → Response → Lesson learned

**Q: How do you convince a team to break up a monolith?**
Focus on their pain points: bottlenecks in deployment, team ownership issues, fragile code, difficult scaling. Highlight transition path: start small, use feature toggles, create clear API contracts.

**Q: Describe a microservices project you regret.**
Example regrets: Over-engineering too early, splitting without clear ownership, no central logging/observability, wrong protocol choices. Share experiences and learnings.

**Q: How would you design a logging strategy?**
- Every service logs with trace IDs
- Structured logs in JSON
- Ship to central store (ELK, Loki)
- Visualize and alert (Grafana, Kibana)

**Q: How do you balance team autonomy with architectural consistency?**
- Shared libraries for common tasks (auth, logging)
- Internal standards and linters (OpenAPI, protocol schemas)
- Platform teams offering clear paths and tooling
- Documentation hubs

**Q: How do you handle an outage in upstream service you don't control?**
- Graceful degradation (cached/stale data, hide broken features)
- Retry strategy with backoff
- Circuit breaker pattern
- Clear error messaging for users

**Q: How do you onboard new engineers?**
- Start with few key services
- Provide documentation and API mocks
- Pair with senior developers
- Invest in developer portals

**Q: How do you approach rewriting a critical service?**
- Wrap legacy service in API
- Rewrite in small pieces (strangler fig pattern)
- Continuously test and shift traffic
- Highlight improvements

**Q: How do you prioritize fixing tech debt?**
- Track debt in backlog
- Use impact scores
- Address debt during new feature work
- Quarterly debt sprints

## Related Topics

- **[Monolithic Architecture](./02-monolithic-architecture.md)** - Alternative architecture
- **[Event-Driven Architecture](./03-event-driven-architecture.md)** - Communication pattern
- **[Service Discovery](../03-distributed-systems/02-service-discovery.md)** - Finding services
- **[Consensus Algorithms](../03-distributed-systems/03-consensus-algorithms.md)** - Strong consistency
- **[API Gateway](../04-communication-protocols/05-api-gateway.md)** - Entry point

