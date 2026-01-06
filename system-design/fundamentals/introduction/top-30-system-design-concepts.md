# Top 30 System Design Concepts

## Summary

This document outlines the 30 most critical concepts every system designer must understand. These concepts form the foundation for designing scalable, reliable, and performant systems.

## Core Architecture Concepts

### 1. Client-Server Architecture

**Definition:** Client sends requests, server performs operations and sends responses.

**Key Points:**
- Client initiates communication
- Server processes requests and returns responses
- Foundation of most distributed systems

**Use Cases:** Web applications, APIs, microservices

---

### 2. IP Address

**Definition:** Every server has an IP address—that's where requests are sent and served.

**Key Points:**
- Unique identifier for devices on a network
- Client sends requests to server's IP address
- IPv4 (32-bit) and IPv6 (128-bit) formats

**Use Cases:** Network routing, server identification

---

### 3. DNS (Domain Name System)

**Definition:** Translates website names (like google.com) into IP addresses so browsers know where to send requests.

**Key Points:**
- Human-readable domain names → IP addresses
- Hierarchical distributed system
- Caching improves performance

**Use Cases:** Website access, service discovery

**Example:**
```
google.com → DNS lookup → 142.250.191.46
```

---

### 4. Proxy / Reverse Proxy

**Proxy (Forward Proxy):**
- Located on client side
- Keeps client IP address hidden from internet
- Positioned after the client layer

**Reverse Proxy:**
- Located before server layer
- Keeps server IP address hidden from internet
- Handles load balancing, SSL termination, caching

**Key Differences:**
- Proxy: Client → Proxy → Internet
- Reverse Proxy: Internet → Reverse Proxy → Server

**Use Cases:** Security, load balancing, caching, SSL termination

---

## Communication Protocols

### 5. HTTP/HTTPS

**HTTP (HyperText Transfer Protocol):**
- Communication protocol between client and server
- Sends data in plain text
- Security risk for sensitive data

**HTTPS (HTTP Secure):**
- Encrypts data using TLS or SSL protocols
- Secure communication channel
- Prevents eavesdropping and tampering

**Key Points:**
- HTTPS = HTTP + Encryption
- Uses port 443 (vs HTTP port 80)
- Required for secure web applications

**Use Cases:** Web browsing, API communication, secure transactions

---

### 6. APIs (Application Programming Interface)

**Definition:** Structure of payload, format of request, where to send—defines how software components interact.

**Key Components:**
- Endpoint (URL)
- Request format
- Response format
- Authentication

**Use Cases:** Service integration, third-party integrations, microservices communication

---

### 7. REST API

**Key Characteristics:**
- **Stateless:** Every request is independent
- **Resource-based:** URLs represent resources
- **HTTP Methods:** GET, PUT, POST, PATCH, DELETE

**Advantages:**
- Simple and standard
- Cacheable
- Easy to understand

**Disadvantages:**
- Returns more data than needed (over-fetching)
- Inefficient network usage
- Multiple requests for related data

**Use Cases:** Web APIs, microservices, CRUD operations

---

### 8. GraphQL

**Key Characteristics:**
- Introduced by Facebook
- Fetch only what you need
- Single endpoint for queries
- Type-safe queries

**Advantages:**
- Reduces over-fetching
- Flexible queries
- Single request for related data

**Disadvantages:**
- Needs more processing on server side
- Difficult to cache
- Learning curve

**Use Cases:** Complex data fetching, mobile applications, real-time dashboards

---

## Database Concepts

### 9. Database (DB)

**Definition:** Data is stored in data servers called databases.

**Key Functions:**
- Persistent storage
- Data retrieval
- Data relationships
- Transaction management

**Use Cases:** Application data storage, user data, transaction records

---

### 10. SQL vs NoSQL

**SQL (Relational Databases):**
- Fixed schema
- ACID properties
- Strong consistency
- Structured relationships
- Used in banking systems

**Examples:** MySQL, PostgreSQL, Oracle

**NoSQL (Non-Relational Databases):**
- Highly scalable
- Performant
- Flexible schema
- Types:
  - Key-Value (Redis, DynamoDB)
  - Document Store (MongoDB, CouchDB)
  - Graph (Neo4j)
  - Wide Column Store (Cassandra, HBase)

**Use Cases:** 
- SQL: Financial systems, structured data
- NoSQL: Big data, real-time applications, flexible schemas

---

### 11. Database Indexing

**Definition:** As volume of data grows, we can scale DB vertically by adding more CPU, RAM, and storage. But there is a limit.

**Key Points:**
- Indexing speeds up read queries
- Slows down writes (trade-off)
- Super efficient lookup data
- Index and pointers structure

**When to Use:**
- Indexes created on frequently used columns
- Primary keys and foreign keys
- Columns used in WHERE clauses

**Trade-offs:**
- ✅ Faster reads
- ❌ Slower writes
- ❌ Additional storage

**Use Cases:** Large tables, frequent queries, search operations

---

### 12. Replication

**Definition:** Copies of database—Primary Replica, Read Replicas for reading.

**Types:**
- **Master-Slave (Primary-Replica):** One master handles writes, replicas handle reads
- **Master-Master:** Multiple masters handle writes

**Benefits:**
- High availability
- Read scaling
- Disaster recovery

**Use Cases:** Read-heavy workloads, high availability requirements

---

### 13. Sharding (Horizontal Partitioning)

**Definition:** Distribute database into multiple servers to make it more manageable.

**Key Points:**
- Divide database into small databases by rows
- Data distributed based on key (shard key)
- Optimizes database load
- Enables horizontal scaling

**Challenges:**
- Cross-shard queries expensive
- Rebalancing difficult
- Transaction complexity

**Use Cases:** Large-scale applications, horizontal scaling needs

---

### 14. Vertical Partitioning

**Definition:** Split or shard based on columns, not rows.

**Key Points:**
- Split a bigger table into smaller tables
- Different columns in different tables
- Reduces table size

**Use Cases:**
- Hot/cold data separation
- Security isolation
- Performance optimization

**Example:**
```
Users Table → Users_Core + Users_Profile + Users_Activity
```

---

### 15. Caching

**Definition:** Retrieving from database is always slower than retrieving from memory.

**Cache-Aside Pattern:**
1. Check in cache first—if found, serve it
2. If not in cache, check from database
3. Put result in cache for future requests

**Key Points:**
- Cache data in memory (Redis, Memcached)
- Faster than database access
- Reduces database load

**Use Cases:** Frequently accessed data, expensive queries, read-heavy workloads

---

### 16. Denormalization

**Definition:** Reduces joins by combining related data in a single table.

**Key Points:**
- Normalization reduces redundancy but introduces joins
- Denormalization trades storage for query speed
- Faster queries for reads
- Complex update queries
- Increases storage

**Example:**
Instead of:
- `users` table + `orders` table (with joins)

Create:
- `user_orders` table (denormalized)

**Trade-offs:**
- ✅ Faster read queries
- ❌ Complex updates
- ❌ Increased storage

**Use Cases:** Read-heavy workloads, analytics, reporting

---

## Scaling Concepts

### 17. Vertical Scaling

**Definition:** Making the machine powerful—upgrade server by adding RAM, CPU, storage.

**Key Points:**
- Scale up (bigger machine)
- Simple to implement
- Limited by hardware constraints
- Single point of failure

**Use Cases:** Small to medium applications, quick performance boost

---

### 18. Horizontal Scaling

**Definition:** Add more servers, distribute the workload.

**Key Points:**
- Scale out (more machines)
- Nearly unlimited growth
- Better fault tolerance
- Requires load balancing

**Use Cases:** Large-scale applications, high availability needs

---

### 19. Load Balancers

**Definition:** How client knows which server to connect to—load balancer routes the traffic.

**Functions:**
- Distribute traffic across servers
- Health checks
- SSL termination
- Session affinity

**Load Balancer Algorithms:**
- **Round Robin:** Distribute sequentially
- **Least Connections:** Route to server with fewest connections
- **IP Hashing:** Route based on client IP (sticky sessions)

**Use Cases:** High availability, traffic distribution, horizontal scaling

---

## Distributed Systems Concepts

### 20. CAP Theorem

**Definition:** No distributed system can achieve all 3 at the same time: Consistency, Availability, and Partition Tolerance.

**The Three Properties:**

**Consistency:**
- Same data from all replicated servers
- All nodes see same data simultaneously

**Availability:**
- Data is served even if it's not latest
- System remains operational

**Partition Tolerance:**
- System operates even if a server has crashed
- Handles network partitions

**Trade-offs:**
- **CP:** Consistency + Partition Tolerance (e.g., databases)
- **AP:** Availability + Partition Tolerance (e.g., NoSQL)
- **CA:** Not practical in distributed systems

**Use Cases:** Database selection, system architecture decisions

---

## Storage Concepts

### 21. Blob Storage

**Definition:** Amazon S3—Blob storage/File storage.

**Key Characteristics:**
- Scalable (petabytes)
- Automatic replication
- Easy to access
- Pay as you use

**Use Cases:**
- Static files (images, videos)
- Backups
- Data archives
- Content distribution

**Examples:** AWS S3, Google Cloud Storage, Azure Blob Storage

---

### 22. CDN (Content Delivery Network)

**Definition:** A network of distributed servers that deliver content from the nearest location to users, improving speed and reliability.

**Key Points:**
- CDN serves content faster
- Delivers:
  - HTML pages
  - JavaScript files
  - Images
  - Videos

**Benefits:**
- Reduced latency
- Lower bandwidth costs
- Better user experience globally

**Use Cases:** Static content, media files, global applications

---

## Real-Time Communication

### 23. WebSockets

**Definition:** HTTP request/response is not efficient when it comes to real dashboards, chat systems, etc. Polling might not be efficient.

**Key Points:**
- WebSocket allows 2-way communication
- Client initiates handshake to establish connection
- Connection is set up for continuous communication
- Enables real-time interactions
- Removes the need for polling

**Use Cases:**
- Chat applications
- Real-time dashboards
- Live notifications
- Gaming applications

**Comparison:**
- **HTTP:** Request → Response (one-way)
- **WebSocket:** Persistent bidirectional connection

---

### 24. Webhooks

**Definition:** One server needs to notify another server when an event occurs.

**How It Works:**
1. Receiver registers a webhook URL
2. Provider sends message when event occurs
3. Webhooks are the events emitted

**Key Points:**
- Event-driven communication
- Server-to-server notification
- Real-time event delivery

**Use Cases:**
- Payment notifications
- CI/CD pipelines
- Third-party integrations
- Event-driven architectures

**Example:**
```
GitHub → Webhook → CI/CD Server (on code push)
```

---

## Architecture Patterns

### 25. Microservices

**Monolith:**
- All features in one large codebase
- For large scale: hard to manage, change, or deploy

**Microservices:**
- Divided responsibility
- Each service has its own database
- Services can talk to other services

**Advantages:**
- Independent deployment
- Technology diversity
- Scalability per service
- Fault isolation

**Disadvantages:**
- Increased complexity
- Network latency
- Data consistency challenges

**Use Cases:** Large-scale applications, complex systems, multiple teams

---

### 26. Message Queues

**Definition:** Services communicate asynchronously.

**Architecture:**
- Producer-consumer pattern
- Decouples services
- Handles traffic spikes

**Key Points:**
- Asynchronous communication
- Message buffering
- Reliable delivery

**Use Cases:**
- Background jobs
- Event processing
- Service decoupling
- Task queues

**Examples:** RabbitMQ, Apache Kafka, AWS SQS

---

## API Management

### 27. Rate Limiting

**Definition:** Prevent overload on public APIs—limit the number of requests a client can send (e.g., 100 requests per minute).

**Rate Limiting Algorithms:**
- **Fixed Window:** Limit per fixed time period
- **Sliding Window:** More accurate, considers recent requests
- **Token Bucket:** Allows bursts up to bucket capacity

**Use Cases:**
- API protection
- DDoS prevention
- Fair usage enforcement
- Cost control

---

### 28. API Gateway

**Definition:** Central layer handling auth, rate limiting, logging, monitoring, request routing.

**How It Works:**
- Client sends to gateway
- Gateway sends to correct microservice
- Single entry point

**Functions:**
- Authentication & authorization
- Rate limiting
- Request routing
- Logging & monitoring
- API composition

**Use Cases:** Microservices architecture, API management, security

---

## Reliability Concepts

### 29. Idempotency

**Definition:** Retry or repeated request produces the same result. Uses a unique ID.

**Key Points:**
- Same operation multiple times = same result
- Prevents duplicate operations
- Critical for retries and failures

**Implementation:**
- Idempotency keys
- Unique request IDs
- Server-side deduplication

**Use Cases:**
- Payment processing
- Order creation
- Resource creation
- Retry scenarios

**Example:**
```
POST /payments
Idempotency-Key: abc123
→ First request: Creates payment
→ Retry with same key: Returns same payment (no duplicate)
```

---

## Serverless Computing

### 30. Lambda / Serverless Functions

**Use Lambda When:**
- Workload is stateless
- Event-driven
- Bursty traffic (e.g., auth, webhooks, async jobs)
- Instant scaling needed
- High availability required
- Low operational overhead acceptable

**Use a Service When:**
- Traffic is steady or high-QPS
- Latency must be consistently low
- Stateful behavior needed
- Long-lived connections required
- Heavy in-memory caching needed
- Services are cheaper at sustained scale

**Lambda Characteristics:**
- ✅ Instant scaling
- ✅ Pay per use
- ✅ High availability
- ❌ Cold starts
- ❌ Per-invoke cost
- ❌ Execution time limits

**Use Cases:**
- Event processing
- API endpoints
- Scheduled tasks
- Real-time data processing

---

## Summary by Category

### Architecture & Communication
1. Client-Server Architecture
2. IP Address
3. DNS
4. Proxy/Reverse Proxy
5. HTTP/HTTPS
6. APIs
7. REST API
8. GraphQL

### Database & Storage
9. Database
10. SQL vs NoSQL
11. Database Indexing
12. Replication
13. Sharding
14. Vertical Partitioning
15. Caching
16. Denormalization
21. Blob Storage

### Scaling & Performance
17. Vertical Scaling
18. Horizontal Scaling
19. Load Balancers
22. CDN

### Distributed Systems
20. CAP Theorem
23. WebSockets
24. Webhooks
25. Microservices
26. Message Queues

### API Management & Reliability
27. Rate Limiting
28. API Gateway
29. Idempotency
30. Lambda/Serverless

## Interview Hints

When asked about system design concepts:
1. Group concepts by category (architecture, database, scaling, etc.)
2. Explain trade-offs between related concepts (SQL vs NoSQL, vertical vs horizontal scaling)
3. Give real-world examples for each concept
4. Show understanding of when to apply each concept
5. Discuss how concepts work together in system design

## Learning Path

1. **Start with Basics:** Client-Server, IP Address, DNS, HTTP/HTTPS
2. **Understand Data:** Database concepts, SQL vs NoSQL, Indexing
3. **Learn Scaling:** Vertical vs Horizontal, Load Balancing, Caching
4. **Master Distributed:** CAP Theorem, Replication, Sharding
5. **Explore Patterns:** Microservices, Message Queues, API Gateway
6. **Advanced Topics:** WebSockets, Webhooks, Serverless
