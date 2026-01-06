# Deep Dive Engineering

A comprehensive repository showcasing system design, data structures & algorithms, and technical concepts for senior engineers.

## 🎯 Repository Overview

This repository is organized into three main areas:
- **DSA** - Data Structures & Algorithms problems
- **Tech Concepts** - Core technical concepts (concurrency, databases, networking, etc.)
- **System Design** - Complete system design knowledge base

## 📚 Quick Navigation

### [System Design](./system-design/)

Comprehensive system design knowledge base covering fundamentals, distributed systems, data storage, networking, scaling, architectures, security, and real-world systems.

**Main Sections:**
- **[01. Fundamentals](./system-design/01-fundamentals/)** - Core concepts, scalability, reliability, API design, concurrency, access control, distributed systems
- **[02. Data Storage](./system-design/02-data-storage/)** - Database fundamentals, SQL vs NoSQL, indexing, sharding, replication
- **[03. Distributed Systems](./system-design/03-distributed-systems/)** - Consistent hashing, service discovery, consensus algorithms, CRDTs
- **[04. Networking Protocols](./system-design/04-networking-protocols/)** - HTTP/HTTPS, WebSockets, API Gateways, Webhooks, OSI model
- **[05. Scaling Patterns](./system-design/05-scaling-patterns/)** - Horizontal scaling, rate limiting, load balancing algorithms
- **[06. Architectures](./system-design/06-architectures/)** - Microservices, monolithic, peer-to-peer, event-driven, serverless
- **[07. Security & Compliance](./system-design/07-security-compliance/)** - IAM, secrets management, data security, AppSec, infrastructure security, monitoring, compliance, Secure SDLC
- **[08. Real-World Systems](./system-design/08-real-world/)** - Case studies and real-world system designs

### [DSA](./dsa/)

Data Structures & Algorithms organized by topic and difficulty.

**Topics:**
- Arrays
- Strings
- Linked List
- Stacks & Queues
- Trees
- Graphs
- Dynamic Programming
- Greedy
- Backtracking
- Bit Manipulation
- Math

**Difficulty Levels:** Easy, Medium, Hard

### [Tech Concepts](./tech-concepts/)

Core technical concepts for backend and distributed systems engineers.

**Topics:**
- Concurrency
- Databases
- Networking
- Distributed Systems
- Caching
- Messaging & Streaming
- Security & Auth
- Scalability & Performance

### [Templates](./templates/)

Ready-to-use templates for problem-solving and system design.

- **[DSA Problem Template](./templates/dsa-problem-template.md)** - Structured template for algorithm problems
- **[System Design Template](./templates/system-design-template.md)** - Template for system design interviews

## 🔍 Detailed Index

### System Design - Fundamentals

**Introduction:**
- What is System Design
- Top 30 System Design Concepts

**Scalability & Performance:**
- Horizontal Scaling
- Vertical Scaling
- Load Balancing
- Caching Strategies

**Reliability & Availability:**
- Availability
- Single Point of Failure (SPOF)
- Redundancy

**API Design:**
- What is an API
- REST API
- GraphQL
- API Gateway
- Rate Limiting
- Idempotency

**Concurrency:**
- Concurrency vs Parallelism
- Threading Models

**Access Control:**
- RBAC (Role-Based Access Control)
- ABAC (Attribute-Based Access Control)

**Distributed Systems:**
- CAP Theorem
- Eventual Consistency
- Consistent Hashing
- Service Discovery
- Consensus Algorithms (Raft, Paxos)
- CRDTs

**Data Management:**
- Database Fundamentals (ACID, SQL vs NoSQL, Indexing, Sharding, Replication)
- Data Compression
- Denormalization

### System Design - Security & Compliance

**IAM (Identity, Authentication & Authorization):**
- Authentication: JWT, Passwords, MFA, SSO, OAuth2, Passwordless, SAML, SLO, Session Management, Token Refresh
- Authorization: RBAC, ABAC, Least Privilege, Fine-grained Permissions, Policy-Based, OAuth Scopes, Resource Ownership
- Service Identity: mTLS, SPIFFE/SPIRE, Service Accounts

**Secrets Management:**
- API keys, DB passwords, Certificates, Encryption keys
- Best practices: Never hardcode, central vault, short-lived secrets

**Data Security & Privacy:**
- Data Classification (PII, PHI, PCI)
- Encryption at Rest (Disk, Database, Application-level)
- Encryption in Transit (TLS, mTLS)
- Hashing (SHA-256, Password hashing, HMAC)
- Encryption Fundamentals (Symmetric vs Asymmetric, Algorithms)
- Tokenization
- Data Masking
- GDPR Compliance
- Data Residency
- Consent Management

**Application Security:**
- OWASP Top 10
- Secure Coding Practices
- Dependency Security (SBOM, Vulnerability Scanning)
- SAST/DAST

**Infrastructure & Network Security:**
- Network Security (VPCs, Firewalls, Security Groups, Zero Trust)
- Host Security (OS Hardening, Patch Management)
- Container & K8s Security

**Monitoring & Incident Response:**
- SIEM, IDS/IPS, Anomaly Detection
- Audit Logs, Immutable Logs
- Incident Response Playbooks

**Compliance & Governance:**
- SOC 2, ISO 27001, PCI DSS, HIPAA, GDPR
- Access Reviews, Change Management, Vendor Risk

**Secure SDLC:**
- DevSecOps
- Threat Modeling
- Secure CI/CD
- Secrets Scanning

### System Design - Architectures

**Microservices Architecture:**
- Principles, Communication Patterns
- Language Selection Guide
- Data Consistency (Saga Pattern)
- Service Discovery & API Gateway
- Deployment & Infrastructure
- Observability
- Testing Strategy
- Security Basics
- Common Anti-Patterns
- Interview Questions (40+)

**Monolithic Architecture:**
- When to use, Migration paths

**Peer-to-Peer Architecture:**
- Decentralized networks, DHT

### System Design - Distributed Systems

- Consistent Hashing
- Service Discovery
- Consensus Algorithms (Raft, Paxos)
- CRDTs (Conflict-free Replicated Data Types)

### System Design - Networking Protocols

- HTTP/HTTPS
- WebSockets
- API Gateways
- Webhooks
- OSI Model

### System Design - Scaling Patterns

- Horizontal Scaling
- Vertical Scaling
- Rate Limiting
- Load Balancing Algorithms
- Auto-scaling

### System Design - Data Storage

- Database Fundamentals (comprehensive guide)
- ACID Transactions
- SQL vs NoSQL
- Indexing
- Sharding
- Vertical Partitioning
- Replication
- Connection Pooling
- Denormalization
- Data Compression

### System Design - Real-World Systems

Case studies and designs for:
- Twitter, Facebook, Instagram
- Netflix, Uber, WhatsApp
- YouTube, Chat Systems
- News Feed, Search Engine
- Payment Systems
- Notification Systems
- Rate Limiters
- Distributed Cache
- File Storage Systems
- URL Shorteners

## 🚀 Getting Started

1. **For System Design:** Start with [Fundamentals](./system-design/01-fundamentals/)
2. **For DSA:** Browse by topic in [DSA](./dsa/)
3. **For Tech Concepts:** Explore [Tech Concepts](./tech-concepts/)
4. **For Templates:** Use [Templates](./templates/) for structured problem-solving

## 📖 Learning Path

### Beginner
1. System Design Fundamentals
2. Basic DSA problems (Easy)
3. Core Tech Concepts

### Intermediate
1. Distributed Systems concepts
2. Security & Compliance basics
3. Medium DSA problems
4. Architecture patterns

### Advanced
1. Advanced distributed systems (CRDTs, Consensus)
2. Security deep dives
3. Hard DSA problems
4. Real-world system designs
5. Interview preparation

## 🎯 Interview Preparation

This repository is designed to help you prepare for:
- **System Design Interviews** - Complete coverage from fundamentals to real-world systems
- **DSA Interviews** - Problems organized by topic and difficulty
- **Technical Deep Dives** - Senior engineer-level understanding

## 📝 Contributing

This is a personal learning repository. Feel free to fork and adapt for your own learning journey.

## 📄 License

See [LICENSE](./LICENSE) file for details.

---

**Note:** This repository focuses on publicly available content. Paywalled content is organized separately and not included in the main index.
