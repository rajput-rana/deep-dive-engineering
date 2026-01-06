# System Design Fundamentals

Core concepts and foundational knowledge for system design, organized by topic area.

## Table of Contents

### 📚 Introduction
- **[What is System Design?](./introduction/what-is-system-design.md)** - Introduction to system design, key questions, components, and the design process
- **[Top 30 System Design Concepts](./introduction/top-30-system-design-concepts.md)** - Overview of the 30 most critical concepts every system designer must understand

### ⚡ Scalability & Performance
- **[Scalability](./scalability-performance/scalability.md)** - Vertical vs horizontal scaling, scalability dimensions, design considerations
- **[Performance](./scalability-performance/performance.md)** - Latency, throughput, optimization strategies, bottlenecks
- **[Load Balancing](./scalability-performance/load-balancing.md)** - Algorithms, types, health checks, session affinity
- **[Caching](./scalability-performance/caching.md)** - Cache patterns, levels, invalidation strategies, replacement policies

### 🛡️ Reliability & Availability
- **[Reliability](./reliability-availability/reliability.md)** - Fault tolerance, MTBF, MTTR, failure scenarios, design principles
- **[Availability](./reliability-availability/availability.md)** - Availability levels (nines), calculation methods, achieving high availability
- **[Single Point of Failure (SPOF)](./reliability-availability/single-point-of-failure.md)** - Identifying and mitigating SPOFs, redundancy strategies

### 🌐 API Design
- **[API Design](./api-design/api-design.md)** - RESTful principles, versioning, error handling, best practices
- **[What is an API?](./api-design/what-is-an-api.md)** - API types (REST, GraphQL, gRPC), components, design principles

### 🔄 Concurrency
- **[Concurrency vs Parallelism](./concurrency/concurrency-vs-parallelism.md)** - Understanding the difference, when to use each, real-world examples

### 🔐 Access Control
- **[Role-Based Access Control (RBAC)](./access-control/rbac.md)** - RBAC models, implementation patterns, security best practices

### 💾 Storage
- **[Object Storage](./storage/object-storage.md)** - Object storage vs alternatives, use cases, storage tiers

### 🌍 Distributed Systems
- **[CAP Theorem](./distributed-systems/cap-theorem.md)** - Consistency, Availability, Partition Tolerance trade-offs
- **[Idempotency](./distributed-systems/idempotency.md)** - Idempotent operations, implementation patterns, real-world examples

### 📊 Data Management
- **[Database Sharding](./data-management/database-sharding.md)** - Sharding strategies, challenges, rebalancing, tradeoffs

## Quick Reference by Category

### Getting Started
Start with the **Introduction** section to understand system design basics and the 30 key concepts.

### Performance Optimization
For performance-focused topics, see:
- Scalability & Performance section
- Caching strategies
- Load balancing techniques

### System Reliability
For reliability and availability topics, see:
- Reliability & Availability section
- Single Point of Failure mitigation
- Distributed Systems concepts (CAP Theorem)

### API & Integration
For API-related topics, see:
- API Design section
- Concurrency patterns

### Data & Storage
For data management topics, see:
- Data Management section
- Storage section
- See also: [`../data-storage/`](../data-storage/) for comprehensive database fundamentals

## Design Process Overview

1. **Requirements Gathering** - Functional and non-functional requirements
2. **Back-of-the-Envelope Estimation** - Capacity planning
3. **High-Level Design (HLD)** - Architecture blueprint
4. **Data Model / API Design** - Database schemas and interfaces
5. **Detailed Design** - Component deep dives
6. **Identify Bottlenecks and Trade-offs** - SPOFs, consistency vs availability
7. **Review, Explain, and Iterate** - Refinement and evolution

## Related Sections

- **[Data Storage](../data-storage/)** - Database fundamentals, replication, indexing, sharding
- **[Distributed Systems](../distributed-systems/)** - Consensus algorithms, consistent hashing, service discovery
- **[Networking Protocols](../networking-protocols/)** - HTTP/HTTPS, WebSockets, API Gateways, Webhooks
- **[Scaling Patterns](../scaling-patterns/)** - Horizontal scaling, rate limiting, load balancing algorithms
- **[Design Patterns](../design-patterns/)** - Microservices, monolithic, event-driven architectures
- **[Authentication](../authentication/)** - JWT, OAuth, SSO, security patterns

## Learning Path

1. **Start Here:** Read [What is System Design?](./introduction/what-is-system-design.md)
2. **Core Concepts:** Review [Top 30 System Design Concepts](./introduction/top-30-system-design-concepts.md)
3. **Scalability:** Understand [Scalability](./scalability-performance/scalability.md) and [Performance](./scalability-performance/performance.md)
4. **Reliability:** Learn about [Reliability](./reliability-availability/reliability.md) and [Availability](./reliability-availability/availability.md)
5. **Distributed Systems:** Study [CAP Theorem](./distributed-systems/cap-theorem.md) and [Idempotency](./distributed-systems/idempotency.md)
6. **Deep Dives:** Explore specific topics based on your needs

## Interview Preparation

When preparing for system design interviews:
- Master the fundamentals in this section
- Understand trade-offs (scalability vs cost, consistency vs availability)
- Practice designing systems from scratch
- Review real-world case studies
- Be able to explain your design decisions clearly
