# System Design Fundamentals

Core concepts and foundational knowledge for system design, organized by topic area.

## Table of Contents

### 📚 01. Introduction
- **[01. What is System Design?](./01-introduction/01-what-is-system-design.md)** - Introduction to system design, key questions, components, and the design process
- **[02. Top 30 System Design Concepts](./01-introduction/02-top-30-system-design-concepts.md)** - Overview of the 30 most critical concepts every system designer must understand

### ⚡ 02. Scalability & Performance
- **[01. Scalability](./02-scalability-performance/01-scalability.md)** - Vertical vs horizontal scaling, scalability dimensions, design considerations
- **[02. Performance](./02-scalability-performance/02-performance.md)** - Latency, throughput, optimization strategies, bottlenecks
- **[03. Load Balancing](./02-scalability-performance/03-load-balancing.md)** - Algorithms, types, health checks, session affinity
- **[04. Caching](./02-scalability-performance/04-caching.md)** - Cache patterns, levels, invalidation strategies, replacement policies

### 🛡️ 03. Reliability & Availability
- **[01. Reliability](./03-reliability-availability/01-reliability.md)** - Fault tolerance, MTBF, MTTR, failure scenarios, design principles
- **[02. Availability](./03-reliability-availability/02-availability.md)** - Availability levels (nines), calculation methods, achieving high availability
- **[03. Single Point of Failure (SPOF)](./03-reliability-availability/03-single-point-of-failure.md)** - Identifying and mitigating SPOFs, redundancy strategies

### 🌐 04. API Design
- **[01. What is an API?](./04-api-design/01-what-is-an-api.md)** - API types (REST, GraphQL, gRPC), components, design principles
- **[02. API Design](./04-api-design/02-api-design.md)** - RESTful principles, versioning, error handling, best practices

### 🔄 05. Concurrency
- **[01. Concurrency vs Parallelism](./05-concurrency/01-concurrency-vs-parallelism.md)** - Understanding the difference, when to use each, real-world examples

### 🔐 06. Access Control
- **[01. Role-Based Access Control (RBAC)](./06-access-control/01-rbac.md)** - RBAC models, implementation patterns, security best practices

### 💾 07. Storage
- **[01. Object Storage](./07-storage/01-object-storage.md)** - Object storage vs alternatives, use cases, storage tiers

### 🌍 08. Distributed Systems
- **[01. CAP Theorem](./08-distributed-systems/01-cap-theorem.md)** - Consistency, Availability, Partition Tolerance trade-offs
- **[02. Idempotency](./08-distributed-systems/02-idempotency.md)** - Idempotent operations, implementation patterns, real-world examples

### 📊 09. Data Management
- **[01. Database Sharding](./09-data-management/01-database-sharding.md)** - Sharding strategies, challenges, rebalancing, tradeoffs

## Quick Reference by Category

### Getting Started
Start with the **01. Introduction** section to understand system design basics and the 30 key concepts.

### Performance Optimization
For performance-focused topics, see:
- 02. Scalability & Performance section
- Caching strategies
- Load balancing techniques

### System Reliability
For reliability and availability topics, see:
- 03. Reliability & Availability section
- Single Point of Failure mitigation
- Distributed Systems concepts (CAP Theorem)

### API & Integration
For API-related topics, see:
- 04. API Design section
- Concurrency patterns

### Data & Storage
For data management topics, see:
- 09. Data Management section
- 07. Storage section
- See also: [`../02-data-storage/`](../02-data-storage/) for comprehensive database fundamentals

## Design Process Overview

1. **Requirements Gathering** - Functional and non-functional requirements
2. **Back-of-the-Envelope Estimation** - Capacity planning
3. **High-Level Design (HLD)** - Architecture blueprint
4. **Data Model / API Design** - Database schemas and interfaces
5. **Detailed Design** - Component deep dives
6. **Identify Bottlenecks and Trade-offs** - SPOFs, consistency vs availability
7. **Review, Explain, and Iterate** - Refinement and evolution

## Related Sections

- **[02. Data Storage](../02-data-storage/)** - Database fundamentals, replication, indexing, sharding
- **[03. Distributed Systems](../03-distributed-systems/)** - Consensus algorithms, consistent hashing, service discovery
- **[04. Networking Protocols](../04-networking-protocols/)** - HTTP/HTTPS, WebSockets, API Gateways, Webhooks
- **[05. Scaling Patterns](../05-scaling-patterns/)** - Horizontal scaling, rate limiting, load balancing algorithms
- **[06. Design Patterns](../06-design-patterns/)** - Microservices, monolithic, event-driven architectures
- **[07. Authentication](../07-authentication/)** - JWT, OAuth, SSO, security patterns

## Learning Path

1. **Start Here:** Read [01. What is System Design?](./01-introduction/01-what-is-system-design.md)
2. **Core Concepts:** Review [02. Top 30 System Design Concepts](./01-introduction/02-top-30-system-design-concepts.md)
3. **Scalability:** Understand [01. Scalability](./02-scalability-performance/01-scalability.md) and [02. Performance](./02-scalability-performance/02-performance.md)
4. **Reliability:** Learn about [01. Reliability](./03-reliability-availability/01-reliability.md) and [02. Availability](./03-reliability-availability/02-availability.md)
5. **Distributed Systems:** Study [01. CAP Theorem](./08-distributed-systems/01-cap-theorem.md) and [02. Idempotency](./08-distributed-systems/02-idempotency.md)
6. **Deep Dives:** Explore specific topics based on your needs

## Interview Preparation

When preparing for system design interviews:
- Master the fundamentals in this section
- Understand trade-offs (scalability vs cost, consistency vs availability)
- Practice designing systems from scratch
- Review real-world case studies
- Be able to explain your design decisions clearly
