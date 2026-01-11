# Redis Deep Dive for System Design Interviews

When an interviewer asks you to design a rate limiter, leaderboard, or session store, one technology comes up almost every time: Redis.
Redis delivers sub-millisecond latency by keeping all data in memory, and its rich set of data structures (lists, sets, sorted sets, streams) make it far more than a simple key-value store. 
But knowing that Redis is fast is not enough. Interviewers want to see that you understand **when** to use it, **which** data structure fits your problem, and **how** to handle failures and scaling. These decisions reveal your depth of understanding.
This chapter covers the practical knowledge you need: data structure selection, persistence trade-offs, replication strategies, clustering architecture, and battle-tested patterns. 
By the end, you will be able to confidently propose Redis in interviews and defend your design choices with clear reasoning.

### Redis Architecture Overview
Client applications connect to the **Redis primary**, which processes requests through a single-threaded **event loop**. This event loop multiplexes many client connections efficiently and executes commands quickly and predictably, one command at a time, making Redis very fast for in-memory workloads.
The primary stores data in RAM using Redis’s core **data structures** (Strings, Lists, Sets, Sorted Sets, Hashes). Most operations are designed to be O(1) or O(log n), which is why Redis is a common choice for caching, rate limiting, leaderboards, sessions, and queues.
To survive restarts and reduce data loss, Redis can persist in-memory state using:
- **RDB snapshots**: periodic point-in-time dumps (fast restarts, but you can lose recent writes between snapshots)
- **AOF (Append-Only File)**: logs every write command (better durability, but more write overhead; can be rewritten/compacted)

For availability and read scaling, Redis supports **replication**. The primary streams updates to **replicas** (Replica 1/2). Replicas can serve read traffic (with eventual consistency relative to the primary) and act as failover targets when combined with a system like Redis Sentinel or Redis Cluster failover.
Net effect: Redis is optimized for **low-latency in-memory operations**, with optional durability via RDB/AOF and higher availability through replication.
# 1. When to Choose Redis
Every technology choice in a system design interview requires justification. Simply saying "I'll use Redis for caching" is not enough. You need to explain why Redis fits your specific requirements better than the alternatives.
The key question is: what makes Redis the right tool for this job?

### 1.1 Choose Redis When You Need

#### Low latency requirements
Redis operates entirely in memory, delivering sub-millisecond response times. A typical Redis operation completes in 0.1-0.5ms, compared to 5-50ms for disk-based databases. When your system needs to respond in real-time, this difference matters.

#### Caching frequently accessed data
Database queries are expensive. By caching hot data in Redis, you reduce database load and improve response times. Redis's built-in TTL support and LRU eviction policies handle cache invalidation automatically.

#### Rate limiting and counting
Building a rate limiter requires atomic increment operations with expiration. Redis's INCR command is atomic by design, and TTL support lets counters expire automatically at window boundaries.

#### Real-time rankings and analytics
Some problems require maintaining sorted data with efficient updates. Redis Sorted Sets provide O(log N) insertions and O(log N + M) range queries, making them ideal for leaderboards, priority queues, and time-series data.

#### Session management
User sessions need fast lookups (every request checks the session) and automatic expiration (inactive sessions should disappear). Redis handles both naturally with its key-value model and TTL support.

#### Lightweight messaging
When you need to broadcast events to multiple subscribers without the complexity of a full message queue, Redis Pub/Sub provides a simple fire-and-forget model.

#### Distributed coordination
Building distributed locks, leader election, or resource coordination requires atomic operations with timeouts. Redis's single-threaded execution model guarantees atomicity without explicit locking.

### 1.2 When Redis is the Wrong Choice
Understanding Redis's limitations is equally important. Proposing Redis for the wrong use case signals a lack of depth.

#### Complex queries and aggregations
Redis has no query language. You cannot filter by arbitrary fields, join data across keys, or run aggregations. If your access patterns require flexible querying, you need a database with a query engine.

#### Data that exceeds available memory
Redis stores everything in RAM. While persistence options exist, they are for durability, not for working with datasets larger than memory. When data exceeds RAM, you face either eviction (data loss) or degraded performance from swap.

#### Strong durability requirements
Even with AOF persistence enabled, Redis can lose up to one second of writes during a crash (with the default `everysec` setting). Financial transactions, order processing, or any data where loss is unacceptable needs a database designed for durability first.

#### Complex relationships
Redis stores data in flat structures. If your domain involves many-to-many relationships, hierarchical data, or needs referential integrity, a relational database is more appropriate.

#### Primary source of truth
Redis works best as a derived data store: a cache backed by a database, a session store that can be rebuilt, a rate limiter where losing state is recoverable. Avoid using Redis as your only copy of critical data.

### 1.3 Common Interview Systems Using Redis
| System | Why Redis Works |
| --- | --- |
| Rate Limiter | Atomic counters with TTL |
| Session Store | Fast lookups, automatic expiration |
| Leaderboard | Sorted Sets with O(log N) operations |
| Distributed Cache | LRU eviction, cluster scaling |
| Real-time Analytics | HyperLogLog, Streams, Pub/Sub |
| Distributed Lock | SETNX with TTL |
| Message Queue | Lists or Streams |
| Feature Flags | Hash structures, fast lookups |

When you propose Redis, connect it directly to your requirements. A weak answer sounds like: "I'll use Redis because it's fast." A strong answer explains the specific fit:
"Our rate limiter needs atomic increment operations with automatic expiration. Redis's INCR command is atomic, and TTL handles window boundaries without additional cleanup logic. We also need distributed state across multiple API servers, and Redis provides that naturally as a shared data store."
The key is specificity. Name the data structure, explain why its operations match your access patterns, and acknowledge what you are trading off (memory cost, durability limitations).
# 2. Core Data Structures
Choosing the right data structure is often the most important decision when using Redis. Each structure has different time complexities, memory characteristics, and supported operations. 
Picking the wrong one can mean the difference between O(1) and O(N) performance, or between a clean solution and a complex workaround.
The diagram below shows how Redis data structures map to common use cases:
Let's examine each data structure in detail.

### 2.1 Strings
Strings are the simplest and most commonly used data type. Despite the name, Redis strings can store text, serialized JSON, integers, or raw binary data up to 512 MB.

#### Use cases:
- Caching serialized objects
- Counters and rate limiters
- Session tokens
- Feature flags

**Time complexity:** O(1) for GET/SET, O(N) for MGET/MSET with N keys.

### 2.2 Lists
When you need to maintain order and efficiently add or remove elements from either end, Lists are the right choice. Redis implements them as linked lists, giving O(1) push and pop operations at both the head and tail.

#### Use cases:
- Message queues (LPUSH + BRPOP)
- Activity feeds (recent items)
- Background job queues

**Time complexity:** O(1) for push/pop at ends, O(N) for index access.
The blocking operations (BRPOP, BLPOP) are particularly useful for building work queues. A worker can block until a job appears, eliminating the need for polling.

### 2.3 Sets
Sets store unique elements without any ordering. They shine when you need to track membership, eliminate duplicates, or perform set operations like union and intersection.

#### Use cases:
- Tags and categories
- Tracking unique visitors
- Friend lists and social graphs
- Set operations (union, intersection, difference)

**Time complexity:** O(1) for add/remove/check, O(N) for SMEMBERS.

### 2.4 Sorted Sets (ZSets)
Sorted Sets combine the uniqueness guarantee of Sets with automatic ordering by a numeric score. This makes them one of Redis's most powerful data structures.
The internal implementation uses a skip list, which provides O(log N) insertions and lookups while maintaining sorted order. This is what makes leaderboards and priority queues efficient.

#### Use cases:
- Leaderboards and rankings
- Priority queues
- Time-based feeds (score = timestamp)
- Rate limiting with sliding windows

**Time complexity:** O(log N) for add/remove/rank, O(log N + M) for range queries where M is the number of elements returned.

### 2.5 Hashes
Hashes let you store multiple field-value pairs under a single key. Think of them as a miniature key-value store nested inside Redis.
This structure is more memory-efficient than storing separate string keys for each field, and it keeps related data together logically.

#### Use cases:
- Object storage (user profiles, product details)
- Counters per field
- Session data with multiple attributes

**Time complexity:** O(1) for single field operations, O(N) for HGETALL.

### 2.6 HyperLogLog
Counting unique items seems simple until you have billions of them. Storing each unique visitor ID in a Set would consume massive amounts of memory.
HyperLogLog solves this with a probabilistic approach: it estimates cardinality using only 12 KB of memory, regardless of whether you have tracked 1,000 or 1 billion unique elements.

#### Use cases:
- Unique visitor counting
- Cardinality estimation (distinct values)
- A/B test unique user tracking

**Trade-off:** The standard error is about 0.81%. For analytics and dashboards where "approximately 1.2 million unique visitors" is acceptable, HyperLogLog saves enormous amounts of memory. For cases requiring exact counts, use a Set instead.

### 2.7 Streams
Streams provide an append-only log structure, similar to Kafka but built into Redis. Unlike Pub/Sub (which is fire-and-forget), Streams persist messages and support consumer groups for reliable processing.

#### Use cases:
- Event sourcing
- Activity logs
- Message queues with persistence
- Real-time data pipelines

**Consumer groups:** Allow multiple consumers to process stream entries with acknowledgment.

### 2.8 Data Structure Selection Guide
| Need | Data Structure | Why |
| --- | --- | --- |
| Simple cache | String | Fast, supports TTL |
| Object with fields | Hash | Access individual fields |
| Queue (FIFO) | List | LPUSH + RPOP |
| Unique items | Set | Automatic deduplication |
| Ranked items | Sorted Set | Score-based ordering |
| Unique count (approx) | HyperLogLog | Constant memory |
| Event log | Stream | Persistence, consumer groups |
| Real-time broadcast | Pub/Sub | Fire-and-forget messaging |

Never just say "I'll store this in Redis." Specify the data structure and explain why it fits. Compare these two responses:
Weak: "I'll store the leaderboard in Redis because it's fast."
Strong: "For the leaderboard, I'll use a Redis Sorted Set. Each player's score becomes their sort value, so the set stays automatically ordered. ZREVRANGE gives us the top N players in O(log N + N), and ZINCRBY lets us update scores atomically. Getting a player's rank is O(log N) with ZREVRANK. This scales to millions of players."
The second answer shows you understand not just what Redis does, but how its internals match your access patterns.
# 3. Persistence Options
"If Redis stores everything in memory, what happens when the server restarts?"
This is a common interview question, and the answer reveals whether you understand Redis's design philosophy. Redis prioritizes speed, but it offers persistence options when you need durability. The key is understanding what you are trading off with each approach.

### 3.1 RDB (Redis Database Snapshots)
RDB persistence creates point-in-time snapshots of your entire dataset. Think of it as periodic backups: every N minutes (or after N write operations), Redis saves everything to a binary file called `dump.rdb`.

#### How RDB snapshots work:
The clever part is how Redis avoids blocking while creating snapshots. It forks a child process, which inherits a copy of the memory through the operating system's copy-on-write mechanism. The child writes the snapshot to disk while the parent continues serving requests. Only when the parent modifies a memory page does the OS actually copy it.
This design means normal operations are not blocked during persistence. The trade-off is memory: during a snapshot, you need enough free memory for copy-on-write pages that get modified.

#### When RDB works well:
- Backups and disaster recovery (point-in-time restore)
- Fast restarts (loading a single binary file is quick)
- Caches where losing recent data is acceptable

#### When RDB falls short:
- If your save interval is 5 minutes and Redis crashes after 4 minutes of writes, those 4 minutes of data are gone
- With large datasets (tens of GB), the fork operation can cause latency spikes
- Applications that cannot tolerate any data loss

### 3.2 AOF (Append-Only File)
AOF takes a different approach: instead of periodic snapshots, it logs every write operation as it happens. On restart, Redis replays the log to reconstruct the dataset.
This provides much stronger durability guarantees, but with different trade-offs.

#### AOF file example:

#### The fsync trade-off:
The `appendfsync` setting controls how often Redis forces the operating system to write buffered data to disk:
- **always**: Safest but slowest. Every write waits for disk confirmation.
- **everysec**: Good balance. Buffers for up to one second. You might lose up to one second of data.
- **no**: Fastest but least safe. The OS decides when to flush (typically every 30 seconds).

Most production systems use `everysec` as a reasonable compromise between durability and performance.

#### When AOF works well:
- Applications that cannot lose more than one second of data
- Scenarios where you need to inspect or repair the write log
- Recovery from partial corruption (redis-check-aof can truncate a corrupted file)

#### When AOF falls short:
- AOF files grow larger than RDB files (every operation is logged)
- Restart time increases with file size (must replay all operations)
- Write amplification: every command is written to disk, even if it overwrites the same key

### 3.3 AOF Rewrite
There is an obvious problem with logging every operation: the file grows without bound. If you increment a counter 10,000 times, the log contains 10,000 INCR commands, even though the final state is just one value.
AOF rewrite solves this by generating a new AOF file that contains only the commands needed to recreate the current state.

### 3.4 Hybrid Persistence (RDB + AOF)
RDB provides fast restarts. AOF provides durability. The hybrid approach combines both: the AOF file starts with an RDB snapshot (fast to load), followed by the operations that occurred after the snapshot (providing durability).

#### How it works:
During AOF rewrite, Redis creates a new file that begins with a binary RDB snapshot of the current state. New write operations are then appended in the normal AOF text format. On restart, Redis loads the RDB portion quickly, then replays only the tail of AOF operations.
This gives you fast restart times (most data loads from the binary RDB portion) with strong durability (recent operations are in the AOF tail).

### 3.5 Persistence Strategy Decision
| Strategy | Data Loss | Performance | Restart Speed |
| --- | --- | --- | --- |
| None | All data | Fastest | Instant (empty) |
| RDB only | Minutes | Fast | Fast |
| AOF everysec | ~1 second | Good | Slower |
| AOF always | Minimal | Slow | Slower |
| RDB + AOF | ~1 second | Good | Fast |

Your choice should match the data's importance and recoverability. Consider two scenarios:
For a session cache backed by a database: "RDB snapshots every 5 minutes are sufficient. If we lose the cache on restart, sessions are just refetched from the database. The slight delay is acceptable."
For a rate limiter protecting against abuse: "We use AOF with everysec sync. Losing rate limit state on restart could allow a burst of requests that exceeds our limits. One second of potential data loss is acceptable; minutes is not."
The key is connecting the persistence choice to the specific consequences of data loss for that use case.
# 4. Replication and High Availability
A single Redis instance, no matter how reliable, is a single point of failure. When it goes down, your cache goes cold and your rate limiters reset. For production systems, you need replication for redundancy and automatic failover for recovery.
Redis provides two mechanisms: master-replica replication for data redundancy, and Sentinel for automatic failover management.

### 4.1 Master-Replica Replication
In Redis replication, one node (the master) handles all writes and propagates changes to one or more replicas. Replicas can serve read traffic, but all writes must go through the master.
**Configuration:**

#### How replication works:
When a replica connects to a master for the first time (or after a long disconnection), it needs a full copy of the data. The master triggers a background save (BGSAVE), creating an RDB snapshot. 
While the snapshot is being created, the master buffers all new write commands. Once the snapshot is complete, the master sends the RDB file to the replica, followed by the buffered commands. From that point on, the master streams every write command to the replica in real-time.

#### Understanding asynchronous replication:
By default, Redis replication is asynchronous. The master does not wait for replicas to acknowledge writes before responding to clients. This design prioritizes low latency: writes complete as soon as they are processed locally.
The trade-off is potential data loss during failures. If the master crashes before a write propagates to replicas, that write is lost. In practice, replication lag is typically sub-millisecond, but during network issues or replica overload, it can grow.

### 4.2 Synchronous Replication with WAIT
For writes where data loss is unacceptable, you can make replication synchronous on a per-command basis using the WAIT command:
WAIT blocks until the specified number of replicas have acknowledged receiving all commands up to the current point, or until the timeout expires. This gives you synchronous durability when you need it, without paying the latency cost for every operation.
The trade-off is increased write latency. Use WAIT selectively for critical operations, not for every write.

### 4.3 Redis Sentinel
Replication alone does not provide automatic failover. If the master crashes, someone (or something) needs to promote a replica to become the new master and reconfigure the other replicas to follow it.
Redis Sentinel is a separate process that handles this automatically.

#### What Sentinel does:
Sentinel runs as a separate process alongside your Redis nodes. Multiple Sentinel instances (typically 3 or 5) work together to make failover decisions. This consensus prevents split-brain scenarios where multiple nodes think they are the master.
- **Continuous monitoring:** Sentinels ping the master and replicas, tracking their health
- **Failure detection:** When enough Sentinels agree the master is unreachable (a quorum), they initiate failover
- **Automatic promotion:** A replica is promoted to master without human intervention
- **Service discovery:** Clients connect to Sentinel to find the current master, so they automatically follow after failover

#### How failover works:
When Sentinels detect the master is down, they do not immediately fail over. Instead, they coordinate:
1. Each Sentinel that cannot reach the master marks it as "subjectively down"
2. When enough Sentinels agree (reaching quorum), the master is marked "objectively down"
3. The Sentinels elect a leader Sentinel to coordinate the failover
4. The leader selects the best replica (most up-to-date, least replication lag)
5. The chosen replica is promoted to master
6. Other replicas are reconfigured to replicate from the new master
7. When the old master comes back online, it becomes a replica of the new master

This process typically completes in 10-30 seconds, depending on configuration.

### 4.4 Sentinel Configuration
| Setting | Meaning |
| --- | --- |
| monitor | Master name, IP, port, quorum (2 Sentinels must agree) |
| down-after-milliseconds | Time before master considered down |
| failover-timeout | Maximum time for failover |
| parallel-syncs | Replicas to reconfigure simultaneously |

### 4.5 Replication Topologies
**Simple:** 1 master, N replicas
**Chained:** Reduce master load for many replicas
**Replica of replica:** Used in geo-distribution
When discussing Redis HA, explain the failure scenario you are protecting against and how your design handles it:
"For the session store, I would deploy a Redis master with two replicas, monitored by three Sentinel nodes. If the master fails, Sentinel detects the failure within a few seconds, promotes the most up-to-date replica, and reconfigures the cluster. Our application uses Sentinel-aware clients that automatically discover the new master. During the failover window (roughly 10-30 seconds), session lookups will fail, but users can simply re-authenticate since sessions are not critical data."
This shows you understand the mechanism, the timing, and the impact on your application.
# 5. Clustering and Scaling
Sentinel gives you high availability, but all your data still lives on a single master. What happens when your dataset grows beyond the memory of a single machine, or when write throughput exceeds what one node can handle?
Redis Cluster solves this by partitioning data across multiple master nodes, each responsible for a portion of the keyspace. Each master can have replicas for high availability, giving you both horizontal scaling and fault tolerance.

### 5.1 Redis Cluster Architecture

#### Understanding hash slots:
Rather than mapping keys directly to nodes, Redis Cluster uses an intermediate concept called hash slots. There are exactly 16384 slots, and each key maps to one slot based on its hash value. The slots are then distributed among the cluster's master nodes.
This indirection is what makes cluster operations (adding/removing nodes) manageable. When you add a node, you migrate slots to it. When you remove a node, you migrate its slots elsewhere. Keys automatically follow their slots.
**Key to slot mapping:** `slot = CRC16(key) mod 16384`
Each master owns a contiguous range of slots, and each master has one or more replicas for failover.

### 5.2 How Data is Distributed
When a client wants to access a key, it first calculates which slot the key belongs to, then determines which node owns that slot.

#### Client request flow:
1. Client calculates slot from key
2. Client sends request to node owning that slot
3. If wrong node, receives MOVED redirect
4. Smart clients cache slot→node mapping

### 5.3 Hash Tags for Multi-Key Operations
The slot-based sharding creates a problem: what if you need to operate on multiple keys atomically? In a non-clustered Redis, you can use MGET, transactions, or Lua scripts across any keys. In a cluster, this only works if all the keys happen to be on the same node.
Hash tags solve this by letting you control which part of the key is hashed:

### 5.4 Cluster Limitations
Redis Cluster's sharding model imposes constraints that do not exist with a single instance. Understanding these limitations is critical for interviews because they affect your design decisions.
| Operation | Cluster Support | Why |
| --- | --- | --- |
| Single-key operations | Full | Key routes to one node |
| Multi-key (same slot) | Full | All keys on same node |
| Multi-key (different slots) | Not supported | Would require cross-node coordination |
| Transactions (same slot) | Supported | MULTI/EXEC runs on one node |
| Transactions (different slots) | Not supported | No distributed transactions |
| Lua scripts (same slot) | Supported | Script executes atomically on one node |
| Pub/Sub | Cluster-wide broadcast | Works but inefficient at scale |

The key insight: Redis Cluster trades some flexibility for horizontal scalability. Operations that span multiple slots require application-level handling.

### 5.5 Scaling Operations
**Adding nodes:**
1. Add new empty node to cluster
2. Reshard: Migrate slots from existing nodes
3. Cluster rebalances automatically

**Removing nodes:**
1. Reshard: Move all slots to other nodes
2. Remove empty node from cluster

**Resharding is online:** No downtime required.

### 5.6 Cluster vs Sentinel Decision
| Factor | Sentinel | Cluster |
| --- | --- | --- |
| Use case | High availability | HA + Horizontal scaling |
| Max data size | Single node memory | Aggregate cluster memory |
| Complexity | Lower | Higher |
| Multi-key operations | Full support | Same-slot only |
| Minimum nodes | 3 Sentinels + 1 Master + 2 Replicas | 6 (3 masters + 3 replicas) |

Your choice depends on two factors: data size and throughput requirements.
Sentinel example: "For our rate limiter, the working set is about 10GB, which fits comfortably on a single node. We need high availability but not horizontal scaling. Redis Sentinel with one master and two replicas gives us automatic failover. Read replicas can help distribute the load if needed."
Cluster example: "Our distributed cache needs to hold 200GB of product data with 500K reads per second. This exceeds what a single node can handle. I would deploy a Redis Cluster with 8 shards (each handling ~25GB and ~60K ops/sec). Each shard has one replica for failover. We will use hash tags to keep related data on the same shard where we need atomic operations."
The key is matching the architecture to the actual requirements, not defaulting to the more complex option.
# 6. Memory Management
Since Redis stores all data in RAM, memory is your primary constraint. When memory runs out, Redis must either reject writes or evict existing data. Understanding how to configure and monitor memory usage is essential for reliable operation.

### 6.1 Memory Configuration

### 6.2 Eviction Policies
When Redis reaches `maxmemory`, it needs to make room for new writes. The eviction policy determines which keys get removed. This choice depends on your use case.
| Policy | Description |
| --- | --- |
| noeviction | Return error on writes (default) |
| allkeys-lru | Evict least recently used from all keys |
| allkeys-lfu | Evict least frequently used from all keys |
| allkeys-random | Evict random keys |
| volatile-lru | LRU among keys with TTL |
| volatile-lfu | LFU among keys with TTL |
| volatile-random | Random among keys with TTL |
| volatile-ttl | Evict keys with shortest TTL |

### 6.3 LRU vs LFU
Both algorithms try to keep "useful" data in cache, but they define usefulness differently.
**LRU (Least Recently Used)** evicts the key that was accessed longest ago. This works well when recent access is a good predictor of future access. Most caching scenarios fall into this category.
**LFU (Least Frequently Used)** tracks access counts and evicts the key accessed least often. This is better when some data is consistently hot regardless of when it was last accessed.
The difference matters in specific scenarios:
For most caches, LRU is the safe default. Consider LFU when you have clearly defined hot spots that should never be evicted, or when you experience cache pollution from periodic full scans.

### 6.4 Memory Optimization Techniques
**1. Use appropriate data structures:**
**2. Use short key names in production:**
**3. Set appropriate TTLs:**
**4. Use compression for large values:**

### 6.5 Memory Monitoring
# 7. Common Patterns and Use Cases
Knowing Redis data structures is necessary but not sufficient. Interviewers expect you to combine them into patterns that solve real problems. This section covers the patterns that appear most frequently in system design interviews.

### 7.1 Distributed Locking
When multiple processes need exclusive access to a resource, you need distributed locking. Redis is commonly used for this because its atomic operations provide the building blocks for lock acquisition and release.
**Basic locking with SET NX:**

#### Redlock for stronger guarantees:
A single Redis instance is still a single point of failure. If the Redis node fails while holding a lock, the lock is lost (though it will eventually expire). For higher reliability, the Redlock algorithm acquires locks on multiple independent Redis instances:
1. Try to acquire the lock on N Redis instances (typically 5)
2. Calculate elapsed time, subtract from lock validity
3. Consider the lock acquired if held on N/2+1 instances and validity time remains
4. If lock fails, release on all instances

### 7.2 Rate Limiting
Rate limiting is perhaps the most common Redis use case in interviews. The challenge is counting requests per user within a time window, while handling concurrent requests correctly and cleaning up old data automatically.
**Fixed window counter:**
The simplest approach divides time into fixed windows (e.g., per-minute buckets) and counts requests in each window.
The downside is the boundary problem: a user could make 100 requests at 10:59:59 and another 100 at 11:00:01, effectively doubling their rate at the window boundary.
**Sliding window with Sorted Set:**
For more accurate rate limiting, use a sliding window that considers the actual time of each request.
**Token bucket:**
Token bucket is more flexible than counting: it allows bursts up to bucket capacity while maintaining an average rate. This is often preferred for APIs where occasional bursts are acceptable.

### 7.3 Leaderboard
Leaderboards require maintaining a sorted collection with efficient rank lookups and updates. Redis Sorted Sets are purpose-built for this: the score is the player's points, and the member is their identifier.

### 7.4 Session Store
Session management needs fast reads (checked on every request), automatic expiration (for security), and support for storing structured data (user info, permissions). Redis hashes with TTL handle all of these naturally.

### 7.5 Cache-Aside Pattern
Cache-aside (also called lazy loading) is the most common caching strategy. The application checks the cache first, falls back to the database on a miss, and populates the cache for next time.

### 7.6 Pub/Sub for Real-Time Notifications
Redis Pub/Sub provides a simple broadcast mechanism: publishers send messages to channels, and all subscribed clients receive them immediately.

#### Important limitations to understand:
Pub/Sub is fire-and-forget. If a subscriber is disconnected when a message is published, that message is lost. There is no message persistence, no acknowledgment, and no replay capability.
This makes Pub/Sub suitable for real-time updates where losing occasional messages is acceptable (live dashboards, typing indicators), but not for reliable message delivery. For guaranteed delivery, use Redis Streams or a dedicated message queue like Kafka or RabbitMQ.

### 7.7 Pattern Summary
| Pattern | Data Structure | Key Design |
| --- | --- | --- |
| Distributed lock | String | lock:{resource} |
| Rate limiter | String or Sorted Set | rate:{user}:{window} |
| Leaderboard | Sorted Set | leaderboard:{game} |
| Session store | Hash | session:{token} |
| Cache | String/Hash | cache:{entity}:{id} |
| Queue | List or Stream | queue:{name} |
| Pub/Sub | Pub/Sub or Stream | channel:{topic} |

# 8. Transactions and Lua Scripting
Many operations require multiple commands to execute atomically. Without atomicity, concurrent clients can interleave their operations in unexpected ways. Redis provides two mechanisms for atomic operations: MULTI/EXEC transactions and Lua scripting.

### 8.1 MULTI/EXEC Transactions
MULTI/EXEC groups multiple commands to execute together without interleaving from other clients.

#### Important differences from database transactions:
Redis transactions are simpler than ACID database transactions. Commands between MULTI and EXEC are queued (not executed immediately), then run as a batch. If one command fails, the others still execute. There is no rollback.
This isolation is sufficient for many use cases: you are guaranteed that no other client's commands run in the middle of your transaction. But you cannot read values and make decisions based on them within the transaction, because reads return QUEUED, not the actual value.

### 8.2 Optimistic Locking with WATCH
To build conditional logic (check a value, then modify it), use WATCH for optimistic locking.

### 8.3 Lua Scripting
Lua scripts provide true atomic execution with conditional logic. The entire script runs to completion without any other client's commands interleaving. You can read values, make decisions, and modify data, all atomically.

#### Advantages of Lua:
- True atomicity (script runs uninterrupted)
- Conditional logic within atomic operation
- Reduced network round trips
- Scripts are cached (EVALSHA)

### 8.4 Script Best Practices
1. **Keep scripts short:** Long scripts block other operations
2. **Avoid unbounded loops:** Can freeze Redis
3. **Use EVALSHA:** Cache scripts to reduce network overhead
4. **Test thoroughly:** Scripts are hard to debug

Lua scripts are the answer whenever you need to read, decide, and write atomically. 
Common examples:
- Rate limiting: Read current count, compare to limit, increment if allowed
- Inventory reservation: Check quantity, decrement if available
- Lock acquisition: Check if lock exists, set if not, return success/failure
- Balance transfers: Check source balance, decrement source, increment destination

The alternative (WATCH + MULTI/EXEC) requires retry logic for conflicts. Lua scripts handle the logic server-side in a single round trip and never conflict. This makes them both simpler and more efficient for conditional operations.
# 9. Redis vs Other Databases
In interviews, you will often need to justify why Redis is the right choice over alternatives. Understanding these comparisons helps you make and defend design decisions.

### 9.1 Redis vs Memcached
Memcached is the other major in-memory caching solution. Both offer sub-millisecond latency, but they differ significantly in capabilities.
| Aspect | Redis | Memcached |
| --- | --- | --- |
| Data structures | Rich (strings, lists, sets, etc.) | Strings only |
| Persistence | RDB + AOF | None |
| Replication | Built-in | None (client-side) |
| Clustering | Redis Cluster | Client-side consistent hashing |
| Pub/Sub | Built-in | None |
| Memory efficiency | Good | Better for simple strings |
| Multithreading | Single-threaded (mostly) | Multi-threaded |

#### When to choose which:
Redis is the default choice for most caching scenarios because its data structures solve problems that would require multiple Memcached operations (or external logic). Need a leaderboard? Redis Sorted Set. Need atomic increment with TTL? Built-in. Need to cache an object and update one field? Redis Hash.
Memcached makes sense when you have a simple cache workload (serialize objects, store by key, retrieve by key) and need maximum throughput. Memcached's multithreaded architecture can handle higher request rates on a single node, and its simpler memory model can be more efficient for uniform-sized values.

### 9.2 Redis vs DynamoDB
This comparison comes up when designing systems that need persistence alongside caching.
| Aspect | Redis | DynamoDB |
| --- | --- | --- |
| Latency | Sub-millisecond | Single-digit millisecond |
| Data model | Rich structures | Key-value/document |
| Persistence | Optional | Built-in (durable) |
| Scaling | Manual cluster | Automatic |
| Cost | Memory-based | Request-based |
| Use case | Cache, real-time | Primary database |

#### The key distinction:
Redis and DynamoDB serve different purposes. Redis is an in-memory data store optimized for speed, typically used as a cache or for transient data. DynamoDB is a durable NoSQL database designed as a primary data store.
Use Redis when latency is critical and data loss is tolerable (caches, sessions, rate limiters). Use DynamoDB when data must survive failures and persist long-term (user accounts, orders, configuration).
A common pattern is to use both: DynamoDB as the source of truth, with Redis caching hot data for faster access.

### 9.3 Redis vs Kafka
When messaging or event streaming is part of your design, you might consider Redis Streams or Pub/Sub. Understanding how they compare to Kafka helps you choose correctly.
| Aspect | Redis | Kafka |
| --- | --- | --- |
| Primary use | Cache, real-time data | Event streaming |
| Message persistence | Optional (Streams) | Built-in (days/forever) |
| Throughput | High | Very high |
| Consumer groups | Streams only | Native |
| Ordering | Per-stream | Per-partition |
| Replay | Limited | Full history |

#### Different tools for different problems:
Redis messaging (Pub/Sub and Streams) works well for real-time notifications, lightweight queuing, and scenarios where you are already using Redis for caching. Redis Streams add persistence and consumer groups, making them suitable for reliable message processing at moderate scale.
Kafka is designed for event streaming at massive scale with long-term retention. When you need to process millions of events per second, replay historical data, or build event-sourced systems, Kafka is the right tool.
In practice, many systems use both: Kafka for the core event pipeline and Redis for caching derived data or handling real-time notifications to connected clients.

### 9.4 Redis vs Database Caching
| Aspect | Redis Cache | Database Cache |
| --- | --- | --- |
| Latency | ~0.5ms | ~5-50ms |
| Scalability | Cluster scales horizontally | Limited by DB |
| Control | Explicit invalidation | Automatic |
| Memory | Dedicated servers | Shared with queries |
| Cross-request | Shared across all servers | Per-connection |

# Summary
Redis is a versatile tool that appears in almost every system design interview. Here are the key takeaways:
1. **Choose Redis for speed.** Sub-millisecond latency for caching, sessions, rate limiting, and real-time features. Not for primary data storage.
2. **Pick the right data structure.** Strings for simple cache, Hashes for objects, Sorted Sets for leaderboards, Lists for queues. The structure determines what operations are efficient.
3. **Understand persistence trade-offs.** RDB for fast recovery, AOF for durability, hybrid for both. Know that Redis prioritizes speed over durability.
4. **Plan for high availability.** Sentinel for automatic failover, Cluster for horizontal scaling. Match complexity to requirements.
5. **Manage memory carefully.** Set maxmemory and eviction policy. Monitor usage. Redis performance degrades when memory is exhausted.
6. **Use Lua for complex atomics.** When you need conditional logic within an atomic operation, Lua scripts are more powerful than MULTI/EXEC.
7. **Know common patterns.** Distributed locks (SETNX), rate limiting (Sorted Set), leaderboards (ZSet), cache-aside, session storage.
8. **Compare with alternatives.** Memcached for simple caching, DynamoDB for durable storage, Kafka for event streaming.

When proposing Redis in an interview, be specific about which features and data structures solve your requirements. Show awareness of limitations (memory-bound, eventual consistency) and how you would handle them. This depth demonstrates real understanding.
# References
- [Redis Documentation](https://redis.io/docs/) - Official Redis documentation covering all commands, data types, and features
- [Redis University](https://university.redis.com/) - Free courses on Redis data structures and use cases
- [Redis in Action](https://www.manning.com/books/redis-in-action) - Manning book covering practical Redis patterns and applications
- [Designing Data-Intensive Applications](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/) - Martin Kleppmann's book with excellent coverage of caching and distributed systems
- [How Discord Stores Trillions of Messages](https://discord.com/blog/how-discord-stores-trillions-of-messages) - Real-world case study of Redis usage at scale
- [Redlock Algorithm](https://redis.io/docs/latest/develop/use/patterns/distributed-locks/) - Official documentation on distributed locking with Redis

# Quiz

## Redis Quiz
What is the main reason Redis can often deliver sub-millisecond latency?