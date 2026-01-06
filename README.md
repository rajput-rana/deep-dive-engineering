# Deep Dive Engineering

A comprehensive repository showcasing system design, data structures & algorithms, and technical concepts for senior engineers.

## 🎯 Repository Overview

This repository is organized into three main areas:
- **[DSA](./dsa/)** - Data Structures & Algorithms problems
- **Tech Concepts** - Core technical concepts (concurrency, databases, networking, etc.)
- **[System Design](./system-design/)** - Complete system design knowledge base

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
- [Arrays](./dsa/arrays/)
- [Strings](./dsa/strings/)
- [Linked List](./dsa/linked-list/)
- [Stacks & Queues](./dsa/stacks-queues/)
- [Trees](./dsa/trees/)
- [Graphs](./dsa/graphs/)
- [Dynamic Programming](./dsa/dynamic-programming/)
- [Greedy](./dsa/greedy/)
- [Backtracking](./dsa/backtracking/)
- [Bit Manipulation](./dsa/bit-manipulation/)
- [Math](./dsa/math/)

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

### Templates

Ready-to-use templates for problem-solving and system design.

- **[DSA Problem Template](./dsa/dsa-problem-template.md)** - Structured template for algorithm problems
- **[System Design Template](./system-design/system-design-template.md)** - Template for system design interviews

## 🔍 Detailed Index

### System Design - Fundamentals

**Introduction:**
- [What is System Design](./system-design/01-fundamentals/01-introduction/01-what-is-system-design.md)
- [Top 30 System Design Concepts](./system-design/01-fundamentals/01-introduction/02-top-30-system-design-concepts.md)

**Scalability & Performance:**
- [Scalability](./system-design/01-fundamentals/02-scalability-performance/01-scalability.md)
- [Performance](./system-design/01-fundamentals/02-scalability-performance/02-performance.md)
- [Load Balancing](./system-design/01-fundamentals/02-scalability-performance/03-load-balancing.md)
- [Caching](./system-design/01-fundamentals/02-scalability-performance/04-caching.md)

**Reliability & Availability:**
- [Reliability](./system-design/01-fundamentals/03-reliability-availability/01-reliability.md)
- [Availability](./system-design/01-fundamentals/03-reliability-availability/02-availability.md)
- [Single Point of Failure (SPOF)](./system-design/01-fundamentals/03-reliability-availability/03-single-point-of-failure.md)

**API Design:**
- [What is an API](./system-design/01-fundamentals/04-api-design/01-what-is-an-api.md)
- [API Design](./system-design/01-fundamentals/04-api-design/02-api-design.md)

**Concurrency:**
- [Concurrency vs Parallelism](./system-design/01-fundamentals/05-concurrency/01-concurrency-vs-parallelism.md)

**Access Control:**
- [RBAC (Role-Based Access Control)](./system-design/01-fundamentals/06-access-control/01-rbac.md)

**Storage:**
- [Object Storage](./system-design/01-fundamentals/07-storage/01-object-storage.md)

**Distributed Systems:**
- [CAP Theorem](./system-design/01-fundamentals/08-distributed-systems/01-cap-theorem.md)
- [Idempotency](./system-design/01-fundamentals/08-distributed-systems/02-idempotency.md)

**Data Management:**
- [Database Sharding](./system-design/01-fundamentals/09-data-management/01-database-sharding.md)

### System Design - Security & Compliance

**IAM (Identity, Authentication & Authorization):**

**Authentication:**
- [Authentication Overview](./system-design/07-security-compliance/01-iam/01-authentication/01-authentication-overview.md)
- [Username & Password](./system-design/07-security-compliance/01-iam/01-authentication/02-username-password.md)
- [API Keys](./system-design/07-security-compliance/01-iam/01-authentication/03-api-keys.md)
- [Bearer Tokens](./system-design/07-security-compliance/01-iam/01-authentication/04-bearer-tokens.md)
- [JWT](./system-design/07-security-compliance/01-iam/01-authentication/05-jwt.md)
- [OAuth2](./system-design/07-security-compliance/01-iam/01-authentication/06-oauth2.md)
- [Certificates & mTLS](./system-design/07-security-compliance/01-iam/01-authentication/07-certificates-mtls.md)
- [HMAC Signatures](./system-design/07-security-compliance/01-iam/01-authentication/08-hmac-signatures.md)
- [OpenID Connect](./system-design/07-security-compliance/01-iam/01-authentication/09-openid-connect.md)
- [SSO](./system-design/07-security-compliance/01-iam/01-authentication/10-sso.md)
- [MFA](./system-design/07-security-compliance/01-iam/01-authentication/11-mfa.md)
- [Passwordless](./system-design/07-security-compliance/01-iam/01-authentication/12-passwordless.md)
- [SAML](./system-design/07-security-compliance/01-iam/01-authentication/13-saml.md)
- [SLO](./system-design/07-security-compliance/01-iam/01-authentication/14-slo.md)
- [Session Management](./system-design/07-security-compliance/01-iam/01-authentication/15-session-management.md)
- [Token Refresh](./system-design/07-security-compliance/01-iam/01-authentication/16-token-refresh.md)
- [OAuth vs JWT](./system-design/07-security-compliance/01-iam/01-authentication/17-oauth-vs-jwt.md)

**Authorization:**
- [RBAC](./system-design/07-security-compliance/01-iam/02-authorization/01-rbac.md)
- [ABAC](./system-design/07-security-compliance/01-iam/02-authorization/02-abac.md)
- [Least Privilege](./system-design/07-security-compliance/01-iam/02-authorization/03-least-privilege.md)
- [Fine-grained Permissions](./system-design/07-security-compliance/01-iam/02-authorization/04-fine-grained-permissions.md)
- [Policy-Based Authorization](./system-design/07-security-compliance/01-iam/02-authorization/05-policy-based-authorization.md)
- [OAuth Scopes](./system-design/07-security-compliance/01-iam/02-authorization/06-oauth-scopes.md)
- [Resource Ownership](./system-design/07-security-compliance/01-iam/02-authorization/07-resource-ownership.md)
- [Authorization Comparison](./system-design/07-security-compliance/01-iam/02-authorization/08-authorization-comparison.md)

**Service Identity:**
- [Service Identity](./system-design/07-security-compliance/01-iam/03-service-identity/) - mTLS, SPIFFE/SPIRE, Service Accounts

**Secrets Management:**
- [Secrets Management](./system-design/07-security-compliance/02-secrets-management/) - API keys, DB passwords, Certificates, Encryption keys

**Data Security & Privacy:**
- [Data Security & Privacy](./system-design/07-security-compliance/03-data-security-privacy/) - Data Classification (PII, PHI, PCI)
- [Encryption at Rest](./system-design/07-security-compliance/03-data-security-privacy/02-encryption-at-rest.md) - Disk, Database, Application-level
- [Encryption in Transit](./system-design/07-security-compliance/03-data-security-privacy/03-encryption-in-transit.md) - TLS, mTLS
- [Hashing](./system-design/07-security-compliance/03-data-security-privacy/04-hashing.md) - SHA-256, Password hashing, HMAC
- [Encryption Fundamentals](./system-design/07-security-compliance/03-data-security-privacy/05-encryption-fundamentals.md) - Symmetric vs Asymmetric, Algorithms

**Application Security:**
- [Application Security](./system-design/07-security-compliance/04-application-security/) - OWASP Top 10, Secure Coding Practices, Dependency Security, SAST/DAST

**Infrastructure & Network Security:**
- [Infrastructure & Network Security](./system-design/07-security-compliance/05-infrastructure-network-security/) - Network Security (VPCs, Firewalls, Security Groups, Zero Trust), Host Security, Container & K8s Security

**Monitoring & Incident Response:**
- [Monitoring & Incident Response](./system-design/07-security-compliance/06-monitoring-logging-incident-response/) - SIEM, IDS/IPS, Anomaly Detection, Audit Logs, Incident Response Playbooks

**Compliance & Governance:**
- [Compliance & Governance](./system-design/07-security-compliance/07-compliance-governance-risk/) - SOC 2, ISO 27001, PCI DSS, HIPAA, GDPR, Access Reviews, Change Management, Vendor Risk

**Secure SDLC:**
- [Secure SDLC](./system-design/07-security-compliance/08-secure-sdlc/) - DevSecOps, Threat Modeling, Secure CI/CD, Secrets Scanning

### System Design - Architectures

- [Microservices Architecture](./system-design/06-architectures/01-microservices-architecture.md)
- [Monolithic Architecture](./system-design/06-architectures/01-monolithic-architecture.md)
- [Peer-to-Peer Architecture](./system-design/06-architectures/03-peer-to-peer-architecture.md)

### System Design - Distributed Systems

- [Consistent Hashing](./system-design/03-distributed-systems/01-consistent-hashing.md)
- [Service Discovery](./system-design/03-distributed-systems/02-service-discovery.md)
- [Consensus Algorithms](./system-design/03-distributed-systems/03-consensus-algorithms.md) - Raft, Paxos
- [CRDTs (Conflict-free Replicated Data Types)](./system-design/03-distributed-systems/04-crdts.md)

### System Design - Networking Protocols

- [HTTP/HTTPS](./system-design/04-networking-protocols/01-http-https.md)
- [OSI Model](./system-design/04-networking-protocols/02-osi.md)
- [WebSockets](./system-design/04-networking-protocols/03-websockets.md)
- [Webhooks](./system-design/04-networking-protocols/04-webhooks.md)
- [API Gateway](./system-design/04-networking-protocols/05-api-gateway.md)

### System Design - Scaling Patterns

- [Horizontal Scaling](./system-design/05-scaling-patterns/01-horizontal-scaling.md)
- [Load Balancing Algorithms](./system-design/05-scaling-patterns/02-load-balancing-algorithms.md)
- [Rate Limiting](./system-design/05-scaling-patterns/03-rate-limiting.md)

### System Design - Data Storage

- [Database Fundamentals](./system-design/02-data-storage/01-database-fundamentals.md) - Comprehensive guide covering ACID, SQL vs NoSQL, indexing, sharding, replication
- [Indexing](./system-design/02-data-storage/02-indexing.md)
- [Sharding](./system-design/02-data-storage/03-sharding.md)
- [Database Replication](./system-design/02-data-storage/04-database-replication.md)

### System Design - Real-World Systems

Case studies and designs for:
- [Design a URL Shortener](./system-design/08-real-world/01-design-a-url-shortener.md)
- [Design Search Autocomplete System](./system-design/08-real-world/02-design-search-autocomplete-system.md)

## 🚀 Getting Started

1. **For System Design:** Start with [Fundamentals](./system-design/01-fundamentals/)
2. **For DSA:** Browse by topic in [DSA](./dsa/)
3. **For Tech Concepts:** Explore [Tech Concepts](./tech-concepts/)
4. **For Templates:** Use [DSA Template](./dsa/dsa-problem-template.md) or [System Design Template](./system-design/system-design-template.md)

## 📖 Learning Path

### Beginner
1. [System Design Fundamentals](./system-design/01-fundamentals/)
2. Basic DSA problems (Easy)
3. Core Tech Concepts

### Intermediate
1. [Distributed Systems concepts](./system-design/03-distributed-systems/)
2. [Security & Compliance basics](./system-design/07-security-compliance/)
3. Medium DSA problems
4. [Architecture patterns](./system-design/06-architectures/)

### Advanced
1. Advanced distributed systems ([CRDTs](./system-design/03-distributed-systems/04-crdts.md), [Consensus](./system-design/03-distributed-systems/03-consensus-algorithms.md))
2. [Security deep dives](./system-design/07-security-compliance/)
3. Hard DSA problems
4. [Real-world system designs](./system-design/08-real-world/)
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
