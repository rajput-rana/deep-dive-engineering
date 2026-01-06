# What is System Design?

**Source:** // (// 

## Definition

**System Design** is the process of defining how different parts of a software system interact to meet both **functional** (what it should do) and **non-functional** (how well it should do it) requirements.

It's about making **high-level architectural decisions** that balance scalability, reliability, performance, and cost—not writing code yet.

### Analogy: Designing a Skyscraper

Just like an architect designs a skyscraper by:
- Understanding requirements (floors, capacity, soil conditions)
- Creating blueprints (foundation, structure, utilities)
- Planning for expansion and fault tolerance

System design translates to:
- **Architecture:** Monolith vs microservices vs event-driven
- **Components:** Databases, servers, load balancers, caches, message queues
- **Interfaces:** REST APIs, gRPC, communication protocols
- **Data:** Storage, management, access patterns, consistency

## 10 Big Questions of System Design

1. **Scalability** - Handle large number of users/requests simultaneously
2. **Latency and Performance** - Reduce response time, ensure low-latency under load
3. **Communication** - How components interact with each other
4. **Data Management** - Store, retrieve, and manage data efficiently
5. **Fault Tolerance and Reliability** - Handle crashes and unreachable components
6. **Security** - Protect against unauthorized access, breaches, DoS attacks
7. **Maintainability and Extensibility** - Easy to maintain, monitor, debug, evolve
8. **Cost Efficiency** - Balance performance with infrastructure cost
9. **Observability and Monitoring** - Monitor health and diagnose issues
10. **Compliance and Privacy** - Comply with GDPR, HIPAA, etc.

## Key Components of a System

### 1. Client/Frontend
- User-facing interface (web browsers, mobile apps)
- Displays information, collects input, communicates with backend

### 2. Server/Backend
- Core functionality processing
- Handles requests, executes business logic, interacts with databases
- Sends responses back to client

### 3. Database/Storage
- Stores and manages data
- Types: Relational (SQL), NoSQL, in-memory caches, distributed object storage

### 4. Networking Layer
- Load balancers, APIs, communication protocols
- Ensures reliable and efficient component interaction

### 5. Third-party Services
- External APIs/platforms (payment processors, email/SMS, auth providers, analytics, cloud AI)

## The Process of System Design

### Step 1: Requirements Gathering

**Questions to ask:**
- What are the **functional requirements** (core features and workflows)?
- What are the **non-functional requirements** (scalability, availability, latency, consistency)?
- Who are the users, and how many expected initially and at scale?
- What's the expected **data volume** and **traffic pattern**?
- Are there any **constraints** (technologies, budgets, compliance)?

### Step 2: Back-of-the-Envelope Estimation

Estimate scale:
- **Data size** (storage requirements)
- **QPS/RPS** (queries/requests per second)
- **Bandwidth** needs
- **Number of servers** required

These rough calculations guide architectural decisions.

### Step 3: High-Level Design (HLD)

Visualize core components and interactions:
- Main modules and services
- Data flow between components
- External dependencies (third-party APIs, databases)

Create the **architecture blueprint**—bird's-eye view of the system.

### Step 4: Data Model / API Design

Define data and interfaces:
- Choose **database type(s)** (relational, NoSQL, time-series)
- Define **schemas, tables, relationships**
- Design **APIs** for service interaction (e.g., `POST /tweet`, `GET /timeline`)

### Step 5: Detailed Design / Deep Dive

Zoom into each component:
- Internal logic, caching, concurrency handling
- **Scaling strategies** (horizontal vs vertical)
- **Replication, partitioning, fault tolerance**
- Address **non-functional requirements** (availability, reliability, latency)

Go from _what_ the system does to _how_ it does it.

### Step 6: Identify Bottlenecks and Trade-offs

Evaluate potential issues:
- Where could the system break under high load?
- What are the **single points of failure**?
- Can caching or replication help?
- Is **eventual consistency** acceptable for higher availability?

Make trade-offs **explicit** and **justifiable**.

### Step 7: Review, Explain, and Iterate

Final evaluation:
- Explain design decisions clearly
- Justify choices and how they meet requirements
- Be open to feedback
- Iterate on weak spots
- Refine and evolve the design

Adaptability and refinement matter more than perfection on the first try.

## Conclusion

System design is essential for building **reliable, scalable, and maintainable** software. Understanding system design principles helps you:
- Make better architectural decisions
- Choose the right technologies
- Optimize performance with confidence

Whether designing a small web app or a massive distributed platform, these principles apply.

