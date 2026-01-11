# Handling High Write Traffic

While most systems are read-heavy, some of the most challenging problems in distributed systems involve handling massive write loads. Every GPS ping from an Uber driver, every click tracked by analytics, every log line from a server, every IoT sensor reading, these are all writes that must be captured reliably at enormous scale.
Here's the uncomfortable truth about writes: you can't cache your way out of them. With reads, you can add more replicas, layer caches in front of caches, and serve slightly stale data when needed. Writes don't offer the same luxury. 
Every write must eventually hit persistent storage, and that storage becomes your bottleneck. The strategies that work brilliantly for reads simply don't apply. The architecture that scales reads horizontally hits a wall when you try to scale writes the same way.
# Where This Pattern Shows Up
High write traffic challenges appear in systems that ingest massive amounts of data:
| Problem | Why High Write Handling Matters |
| --- | --- |
| Design Logging System | Millions of log entries per second from thousands of servers |
| Design Analytics Pipeline | Every click, scroll, and page view generates write events |
| Design Uber/Lyft | Drivers send location updates every few seconds, millions of drivers |
| Design IoT Platform | Millions of sensors reporting data continuously |
| Design Trading System | Every trade, quote, and order update must be captured with zero loss |
| Design Metrics/Monitoring | Every service emits metrics constantly, must handle spikes during incidents |

Understanding write scaling helps you answer the fundamental question: when every write must eventually hit persistent storage and you can't cache your way out of the problem, how do you handle millions of writes per second?
# 1. Understanding the Write Problem
Before diving into solutions, it's worth understanding exactly why writes are so much harder to scale than reads. This understanding will inform every architectural decision you make.

### 1.1 The Fundamental Asymmetry
Reads and writes have fundamentally different scaling characteristics:
With reads, you have options. You can add more cache layers, spin up additional replicas, serve slightly stale data when freshness isn't critical, or route requests to whichever server is least busy. Each of these strategies allows you to scale horizontally without fundamental architectural changes.
Writes don't have these escape hatches. Every write must go to the primary database. Every write must be durable, meaning it must survive crashes. Every write must maintain consistency with other writes. And unlike reads, you can't serve a "cached" version of a write, that doesn't even make sense.
This asymmetry explains why a database that handles 100,000 reads per second might struggle with 10,000 writes per second. The bottleneck is fundamentally different.

### 1.2 The Scale of the Problem
Let's make this concrete. Consider an IoT platform managing 10 million devices:
Each device sends data every 5 seconds. Each message is 500 bytes. That's 2 million writes per second, 1 GB of data ingested every second, and 86 TB of data generated every day. A single PostgreSQL instance handles maybe 10,000-50,000 writes per second on good hardware. You're looking at a 40x gap between what you need and what a traditional database can provide.
This gap is what drives the need for specialized write-scaling techniques.

### 1.3 Write-Heavy Systems in the Wild
Not all systems face this challenge equally. Here's where write optimization matters most:
| System | Writes/Second | Characteristics |
| --- | --- | --- |
| Logging/Monitoring | 1M+ | Append-only, time-series, can tolerate some loss |
| Analytics/Clickstream | 100K+ | Event streams, batch-friendly, eventual consistency OK |
| IoT Platforms | 1M+ | High volume, small payloads, geographic distribution |
| Financial Trading | 100K+ | Low latency critical, ordering matters, zero loss tolerance |
| Social Media Posts | 10K+ | Mixed with heavy reads, strong consistency needs |
| Ad Tech Bidding | 1M+ | Real-time decisions, sub-100ms latency requirements |

Notice the variation in requirements. A logging system might tolerate occasional data loss, but a trading system cannot lose a single transaction. An analytics platform can batch writes aggressively, but an ad bidding system needs sub-millisecond acknowledgment. These different requirements lead to different architectural choices.

### 1.4 The Durability-Performance Trade-off
Every write system faces a fundamental tension between speed and safety. How quickly you can acknowledge a write depends entirely on how much durability you're willing to guarantee.
| Durability Level | Method | Latency | What Survives |
| --- | --- | --- | --- |
| Level 1 | Memory only | ~1μs | Nothing (data lost on crash) |
| Level 2 | Async disk write | ~100μs | Process crash (not machine crash) |
| Level 3 | Sync disk write (fsync) | ~1-10ms | Machine crash |
| Level 4 | Sync + replica acknowledgment | ~10-50ms | Machine loss |
| Level 5 | Multi-region sync | ~50-200ms | Datacenter loss |

The right choice depends on your use case. A metrics system might accept Level 2, knowing that losing a few seconds of data on a crash is acceptable. A banking system needs Level 4 or 5, where losing even a single transaction is unacceptable. Understanding where your system falls on this spectrum is the first step in designing your write architecture.
# 2. The Write Scaling Toolkit
When facing high write traffic, you have several techniques at your disposal. Each addresses a different aspect of the problem, and in practice, you'll combine multiple approaches.
| Technique | What It Does | When to Use |
| --- | --- | --- |
| Batching | Combines multiple writes into one operation | Always (first optimization to consider) |
| Async Processing | Decouples write acceptance from processing | When immediate confirmation isn't required |
| Sharding | Distributes writes across multiple databases | When single database can't handle load |
| Write-Optimized Storage | Uses storage structures designed for writes | When write throughput is the primary bottleneck |
| Event Sourcing/CQRS | Separates write and read models entirely | Complex domains with different read/write patterns |
| Backpressure | Prevents system overload through flow control | Always (defensive measure) |

The order here is intentional. Batching is almost always your first step because it's simple and universally applicable. Async processing comes next when you can tolerate eventual consistency. Sharding becomes necessary when you've exhausted single-node optimizations. And so on.
Let's explore each technique in depth.
# 3. Batching and Buffering
The simplest and often most effective way to improve write throughput is to stop writing one record at a time. Every database operation carries overhead: network round trips, query parsing, transaction management, and disk synchronization. By combining multiple writes into a single operation, you amortize this overhead across many records.

### 3.1 Why Batching Works
Consider what happens when you insert a single row:
The actual data write takes 0.5ms, but the overhead adds 4.5ms. Now imagine doing this 1,000 times: that's 5 seconds of wall-clock time to insert 1,000 rows.
With batching, you pay the overhead once for many rows:
1,000 rows in 55ms instead of 5,000ms. That's nearly a 100x improvement, and the only thing that changed was how you organized the writes.

### 3.2 Client-Side Batching
The most common approach is to buffer writes in your application and flush them periodically:
The buffer flushes when either condition is met: reaching the size limit or exceeding the time limit. This ensures you don't wait forever for a full batch during low-traffic periods.
The trade-off is latency for throughput. Individual writes complete immediately. Batched writes might wait up to your time limit before being persisted. For many use cases, like analytics or logging, this delay is perfectly acceptable. For others, like payment processing, it might not be.

### 3.3 Database-Side Batching
Different databases offer different mechanisms for bulk writes, and the performance differences are dramatic:
| Method | 10,000 Rows | Relative Speed |
| --- | --- | --- |
| Individual INSERTs | 30 seconds | 1x |
| Multi-value INSERT | 0.5 seconds | 60x |
| COPY command | 0.1 seconds | 300x |

The COPY command bypasses SQL parsing entirely, streaming binary data directly into the table. It's the fastest way to bulk load data into PostgreSQL and similar databases. Use it when you're loading large amounts of data and can format it appropriately.

### 3.4 The Write-Behind Pattern
For maximum write speed with eventual persistence, buffer writes in fast storage and persist asynchronously:
The application writes to Redis and returns immediately, achieving sub-millisecond latency. A background worker reads from Redis, batches the data, and writes to the database at its own pace. This pattern excels at absorbing traffic spikes, since Redis can handle far more writes per second than most databases.
The risk, of course, is data loss. If Redis crashes before the worker has persisted the data to the database, those writes are gone. This is acceptable for metrics and analytics, but not for financial transactions. Choose this pattern when you can tolerate occasional data loss in exchange for dramatic performance improvements.
# 4. Asynchronous Processing
Batching optimizes how writes are performed. Asynchronous processing changes when they're performed. By decoupling write acceptance from write processing, you gain flexibility that's impossible with synchronous writes.

### 4.1 The Async Pattern
The core idea is simple: instead of writing directly to the database, write to a message queue. A separate consumer reads from the queue and performs the actual database writes.
This separation provides several benefits:
**Decoupling:** Producers don't wait for database writes. They push to the queue and move on. If the database is slow or temporarily unavailable, producers keep working.
**Buffering:** The queue absorbs traffic spikes. A sudden surge of writes fills the queue, and consumers drain it at a sustainable pace. Your database never sees the spike directly.
**Scalability:** Consumers scale independently. If you're falling behind, add more consumers. If the database can handle more load, add more consumers. The queue provides the coordination.
**Resilience:** If the database goes down, writes aren't lost. They wait in the queue until the database recovers. This is a fundamental shift from synchronous writes, where a database outage means failed requests.

### 4.2 Choosing the Right Queue
Different queues have different characteristics:
| Queue | Throughput | Latency | Ordering | Best For |
| --- | --- | --- | --- | --- |
| Kafka | 1M+ msg/sec | 5-50ms | Per partition | High-throughput streaming, log aggregation |
| RabbitMQ | 50K msg/sec | 1-5ms | Per queue | Low-latency messaging, complex routing |
| SQS | 100K+ msg/sec | 10-50ms | FIFO optional | Serverless, managed infrastructure |
| Redis Streams | 100K+ msg/sec | <1ms | Per stream | Simple use cases, already using Redis |

Kafka dominates for high-throughput scenarios because of its partitioned design. Each partition is an independent log, and you can have as many partitions as you need. With 100 partitions and 100 consumers, you can process 100 messages in parallel while maintaining order within each partition.

### 4.3 Consumer Patterns
How you consume from the queue matters as much as which queue you choose:
**Competing Consumers (Scale Out):**
Multiple consumers share the workload. Each message is processed by exactly one consumer. This pattern scales horizontally, but doesn't guarantee ordering across messages.
**Partitioned Consumers (Ordered + Scaled):**
Messages are partitioned by key (e.g., user_id). All messages for a given key go to the same partition, and each partition has exactly one consumer. This gives you both ordering (within a partition) and scale (across partitions).

### 4.4 Handling Failures with Idempotency
In distributed systems, failures happen. A consumer might crash after processing a message but before acknowledging it. The queue will redeliver the message to another consumer, resulting in duplicate processing.
The solution is **idempotent processing**: design your writes so that processing the same message twice produces the same result as processing it once.
The processed_events table (or set in Redis) acts as a deduplication log. Before processing any message, check if you've seen its ID before. This simple pattern makes your consumer resilient to duplicates.
# 5. Write-Optimized Storage
The databases most developers reach for first, PostgreSQL, MySQL, MongoDB, are general-purpose. They're designed to handle both reads and writes reasonably well. But for write-heavy workloads, there's a class of databases built specifically for maximum write throughput.
The key innovation is the **Log-Structured Merge Tree (LSM Tree)**, a data structure that trades read performance for dramatically faster writes.

### 5.1 B-Tree vs LSM Tree
Traditional databases use B-trees, which are optimized for reads:
Every write in a B-tree requires finding the right page, reading it from disk, modifying it, and writing it back. This is **random I/O**, the slowest thing you can do to a disk. Worse, a single logical write might update multiple pages (the data page plus index pages), causing **write amplification** of 10-30x.
LSM trees take a completely different approach:
Writes go to an in-memory buffer (memtable). When the buffer fills, it's flushed to disk as a sorted file (SSTable). Background processes merge and compact these files over time. The critical insight: **all disk I/O is sequential**. No random access, no reading pages to modify them. Just appending data.

### 5.2 The Trade-off
Nothing comes for free. LSM trees trade read performance for write performance:
| Aspect | B-Tree (PostgreSQL) | LSM Tree (Cassandra) |
| --- | --- | --- |
| Write speed | Moderate | Very Fast |
| Read speed | Fast | Moderate (may check multiple levels) |
| Write amplification | High (10-30x) | Lower (2-10x) |
| Space amplification | Low | Higher (during compaction) |
| Best for | Mixed workloads, transactions | Write-heavy, append-mostly |

Reads in LSM trees might need to check multiple SSTables across multiple levels. Bloom filters and careful tuning mitigate this, but an LSM database will never match a B-tree for point lookups on large datasets.

### 5.3 LSM Tree Databases
Several production-grade databases use LSM trees:
| Database | Type | Use Case |
| --- | --- | --- |
| Cassandra | Wide-column | Time-series, IoT, high-volume writes |
| ScyllaDB | Wide-column | Cassandra-compatible with better performance |
| RocksDB | Embedded key-value | Storage engine for other systems |
| ClickHouse | Columnar | Analytics, log aggregation |
| InfluxDB | Time-series | Metrics, monitoring, IoT |

When your write throughput requirements exceed what PostgreSQL or MySQL can handle, these databases should be on your shortlist.

### 5.4 Append-Only Logs
For the ultimate in write performance, nothing beats an append-only log:
An append-only log doesn't even try to organize data. It just writes records sequentially to the end of a file. No indexes, no sorting, no structure, just pure sequential I/O at the speed the disk can handle.
This is how Kafka topics work. It's how database write-ahead logs (WAL) work. It's the foundation of event sourcing. The trade-off is that reading requires either scanning the entire log or building external indexes. But for use cases like logging, event capture, and replication, append-only logs are unbeatable.
# 6. Sharding for Writes
When you've optimized your database choice, batched your writes, and processed them asynchronously, you might still hit a wall. A single database instance has finite capacity. When you need to go beyond that, you distribute writes across multiple databases.

### 6.1 Write Sharding Architecture
With 4 shards, each database handles 25% of writes. Your total capacity is 4x a single database. Need more? Add more shards. This is horizontal scaling for writes.
The shard router determines which shard receives each write, typically by hashing a key (like user_id) and taking the modulo of the shard count.

### 6.2 Choosing the Shard Key
The shard key determines how data is distributed, and choosing poorly leads to hot shards:
| Shard Key | Distribution | Pros | Cons |
| --- | --- | --- | --- |
| user_id | Even (if users are similar) | User data co-located | Viral users create hot shards |
| timestamp | Uneven (all current = one shard) | Time-range queries easy | New shard gets all writes |
| random/UUID | Perfect distribution | Even load | Related data scattered |
| Composite key | Controllable | Balances concerns | More complex routing |

The best shard key distributes writes evenly while keeping related data together. For user-centric applications, user_id is often good. For time-series data, a composite key like `hash(device_id) XOR time_bucket` prevents hot shards while preserving device locality.

### 6.3 Consistent Hashing
When you add or remove shards, you need to rebalance data. Naive modulo hashing is catastrophic:
With naive modulo, adding one shard to a three-shard cluster moves about 75% of your data. With consistent hashing, adding one shard moves only about 25% (1/4 of the data moves to the new shard, the rest stays put).
Consistent hashing places shards on a conceptual ring. Each key hashes to a point on the ring and is assigned to the next shard clockwise. When you add a shard, it takes over a portion of the ring from its neighbor. Only keys in that portion move.

### 6.4 The Cross-Shard Problem
Sharding creates a new problem: what happens when a single operation needs to touch multiple shards?
Transferring money from User A (on Shard 1) to User B (on Shard 3) requires updating both shards atomically. If the debit succeeds but the credit fails, you've lost money.
| Approach | Consistency | Performance | Complexity |
| --- | --- | --- | --- |
| Two-Phase Commit (2PC) | Strong | Slow (locks across shards) | High |
| Saga Pattern | Eventual | Good | Medium |
| Avoid cross-shard writes | N/A | Best | Requires good data modeling |

The best solution is often to design your shard key so related data lands on the same shard. If User A's wallet and User B's wallet were on the same shard, the transfer would be a local transaction. This isn't always possible, but it's worth pursuing.
# 7. Event Sourcing and CQRS
For systems with extreme write requirements or complex domain logic, you can fundamentally change how you think about data storage. Instead of storing current state, store the sequence of events that led to that state.

### 7.1 Event Sourcing
Traditional databases store the current state of your data. When something changes, you update the record in place:
Event sourcing stores the events themselves:
To get the current balance, replay all events for that user. The sum of deposits minus withdrawals gives you the current state.
This might seem inefficient, and it would be if you replayed events on every read. In practice, you maintain read-optimized projections that are updated as new events arrive. But the events remain the source of truth.
**Why this helps writes:**
| Aspect | Traditional | Event Sourcing |
| --- | --- | --- |
| Write operation | Update in place (random I/O) | Append to log (sequential I/O) |
| Concurrency | Conflicts on same row | No conflicts (different events) |
| Write speed | Moderate | Very fast |
| History | Lost on update | Complete audit trail |
| Debugging | "What happened?" | Replay to any point in time |

Event sourcing turns writes into appends, the fastest possible operation. There are no conflicts because you're never modifying existing data, just adding new events.

### 7.2 CQRS (Command Query Responsibility Segregation)
Event sourcing pairs naturally with CQRS, which separates the write model from the read model:
Commands (writes) go to the event store, which is optimized for appending. Events are projected into read models optimized for specific query patterns. You might have one read model in PostgreSQL for transactional queries, another in Elasticsearch for search, and a third in Redis for real-time dashboards.
The beauty is that each model is independently optimized. The write path is pure appends. The read paths are tailored to their query patterns. You scale them independently.

### 7.3 When to Use Event Sourcing/CQRS
This pattern isn't for every system. It adds complexity that's only justified in certain scenarios:
**Good Fit:**
- Audit requirements (finance, healthcare, compliance)
- Complex domain logic with many state transitions
- Need for multiple read models with different structures
- High write throughput with eventual consistency acceptable
- Event-driven architectures with downstream consumers

**Poor Fit:**
- Simple CRUD applications
- Strong consistency required on every read
- Small scale where the complexity isn't justified
- Team unfamiliar with event-driven patterns

# 8. Backpressure and Rate Limiting
Every system has limits. When write traffic exceeds those limits, you have a choice: crash ungracefully or degrade gracefully. The techniques in this section ensure your system fails safely.

### 8.1 The Overload Problem
Without flow control, overload cascades:
The server accepts requests faster than it can process them. The internal queue grows. Memory fills up. The process crashes. Every in-flight request is lost, and the traffic that caused the problem is now hitting your other servers.

### 8.2 Rate Limiting
The simplest defense: reject requests that exceed a defined rate.
Common algorithms:
| Algorithm | Behavior | Use Case |
| --- | --- | --- |
| Token Bucket | Allows bursts up to bucket size | API rate limiting |
| Leaky Bucket | Smooth output, no bursts | Steady processing |
| Fixed Window | Count per time window | Simple quota tracking |
| Sliding Window | Rolling count, smoother | More accurate limiting |

The token bucket is most common. Tokens accumulate at a steady rate (say, 100 per second) up to a maximum (say, 500). Each request consumes one token. This allows short bursts (up to 500 requests) while enforcing an average rate (100 per second).

### 8.3 Backpressure
Rate limiting is a blunt instrument, it just says "no" to excess traffic. Backpressure is more sophisticated: it signals upstream systems to slow down.
Backpressure mechanisms:
| Mechanism | How It Works |
| --- | --- |
| Blocking | Producer blocks when queue is full |
| Credits | Consumer grants credits; producer pauses when depleted |
| HTTP 503 | Service returns "Service Unavailable" with Retry-After |
| TCP flow control | Receiver advertises window size |

The key insight is that rejecting work you can't handle is better than accepting it and failing later. A 503 response that the client can retry is better than a timeout that wastes everyone's resources.

### 8.4 Load Shedding
When you must reject requests, be strategic about which ones:
**Shedding strategies:**
| Strategy | How It Works | Trade-off |
| --- | --- | --- |
| Random | Drop random requests | Fair but wasteful |
| LIFO | Drop oldest requests first | They may have timed out anyway |
| Priority | Drop low-priority first | Protects important traffic |
| Client-based | Drop from over-quota clients | Fair to well-behaved clients |

The best strategy depends on your use case. For a payment system, you might prioritize completing in-progress transactions over accepting new ones. For analytics, you might drop events from high-volume clients first to maintain coverage across all clients.

### 8.5 Graceful Degradation
Instead of failing completely, reduce functionality to maintain core service:
Under normal load, a write might update the database, refresh caches, send events to analytics, and trigger notifications. Under heavy load, you might defer analytics and skip notifications entirely, preserving capacity for the core operation.
# 9. Putting It All Together
Here's how these techniques combine into a complete architecture for a high-write system:
**How data flows through the system:**
1. **INGESTION:** Load balancer distributes requests. Rate limiter prevents overload. API servers validate and accept writes quickly.
2. **BUFFERING:** Kafka absorbs traffic spikes. Partitioning enables parallelism. Replication provides durability.
3. **PROCESSING:** Consumer groups process in parallel. Batch writes to storage. Idempotent processing handles retries.
4. **STORAGE:** Cassandra (LSM-based) handles high write throughput. Sharding distributes load. Replication ensures durability.
5. **PROJECTION:** Events projected to read-optimized stores. Elasticsearch for search. Redis for real-time. ClickHouse for analytics.

# 12. Key Takeaways
1. **Writes can't be cached away.** Unlike reads, every write must eventually hit persistent storage. The database is your bottleneck, and you must plan for it.
2. **Batching is your first lever.** Combining multiple writes into one operation reduces overhead by orders of magnitude. Consider batching before anything else.
3. **Async processing decouples acceptance from processing.** Message queues absorb spikes, provide durability, and let you scale consumers independently.
4. **LSM trees are write-optimized.** Databases like Cassandra, RocksDB, and ClickHouse use append-only structures that dramatically outperform B-trees for writes.
5. **Shard for horizontal scale.** When single-node optimization isn't enough, distribute writes across shards. Choose your shard key carefully to avoid hot spots.
6. **CQRS separates concerns.** When reads and writes have different requirements, optimize each path independently.
7. **Backpressure prevents cascading failures.** Rate limiting, load shedding, and graceful degradation keep your system stable under stress.
8. **Idempotency enables safe retries.** In distributed systems, duplicates are inevitable. Make your writes idempotent so retries are harmless.

# References
- [Kafka: The Definitive Guide](https://www.oreilly.com/library/view/kafka-the-definitive/9781491936153/) - Deep dive into Kafka for high-throughput streaming
- [Designing Data-Intensive Applications](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/) by Martin Kleppmann - Essential reading on storage engines and distributed data
- [Discord: How Discord Stores Billions of Messages](https://discord.com/blog/how-discord-stores-billions-of-messages) - Real-world Cassandra at scale
- [Uber: Scaling Real-Time Infrastructure](https://www.uber.com/blog/scaling-real-time-infrastructure/) - Handling millions of location updates
- [The Log: What every software engineer should know](https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying) - Jay Kreps on append-only logs
- [CQRS Journey by Microsoft](https://docs.microsoft.com/en-us/previous-versions/msp-n-p/jj554200(v=pandp.10)) - Comprehensive guide to CQRS and event sourcing

# Quiz

## High Write Traffic Quiz
Why is scaling writes generally harder than scaling reads in distributed systems?