# Design Distributed Cache

## What is a Distributed Cache?

A distributed cache is a caching system that stores data across multiple servers, allowing applications to retrieve frequently accessed data much faster than querying a primary database.
The core idea is to reduce latency and database load by keeping "hot" data in memory, spread across a cluster of cache nodes that can scale horizontally. Unlike a single-server cache, a distributed cache can handle massive amounts of data and traffic by adding more nodes to the cluster.
**Popular Examples:** [Redis](https://redis.io/), [Memcached](https://memcached.org/), [Amazon ElastiCache](https://aws.amazon.com/elasticache/), [Hazelcast](https://hazelcast.com/)
This problem touches on many fundamental system design concepts: **data partitioning**, **consistency vs availability** trade-offs, **failure handling**, and **cache invalidation** (famously one of the two hard problems in computer science).
In this chapter, we will explore the **high-level design of a distributed cache**.
Let's start by clarifying the requirements:
# 1. Clarifying Requirements
Before we start sketching architectures, we need to understand what we are actually building. 
A distributed cache for a mobile gaming backend has very different requirements than one for a financial trading platform. The questions we ask upfront will shape every design decision that follows.
Here is how a requirements discussion might unfold in an interview:
**Candidate:** "What is the expected scale? How many read and write operations per second?"
**Interviewer:** "Let's design for 1 million reads per second and 100,000 writes per second at peak."
**Candidate:** "What is the expected data size? How much data do we need to cache?"
**Interviewer:** "Assume we need to store around 100 TB of data across the cluster."
**Candidate:** "What are the latency requirements for cache operations?"
**Interviewer:** "We need sub-millisecond latency for reads, ideally p99 under 5ms."
**Candidate:** "What consistency guarantees do we need? Is eventual consistency acceptable?"
**Interviewer:** "Eventual consistency is acceptable for most use cases, but we should minimize stale reads."
**Candidate:** "Should the cache support automatic expiration of keys?"
**Interviewer:** "Yes, TTL-based expiration is required. Keys should expire after a configurable time."
**Candidate:** "Do we need to support different data types or just simple key-value pairs?"
**Interviewer:** "For now, let's focus on key-value pairs where both key and value are byte arrays."
After gathering the details, we can summarize the key system requirements.

## 1.1 Functional Requirements
Based on our discussion, here are the core operations our cache must support:
- **Put:** Store a key-value pair in the cache. Users can optionally specify a TTL (time-to-live) after which the entry automatically expires.
- **Get:** Retrieve a value by its key. Returns null or a cache miss indicator if the key does not exist or has expired.
- **Delete:** Explicitly remove a key-value pair from the cache before its natural expiration.
- **TTL Support:** Keys should automatically become inaccessible after their TTL expires.
- **Bulk Operations:** Support batch get and put operations to reduce network round trips when working with multiple keys.

## 1.2 Non-Functional Requirements
Beyond the basic operations, we need to think about the qualities that make this cache production-ready:
- **High Availability:** The cache should be available 99.99% of the time.
- **Low Latency:** Read operations should complete in sub-millisecond time (p99 < 5ms).
- **Scalability:** Should scale horizontally to handle millions of operations per second.
- **Fault Tolerance:** The system should continue operating even when individual nodes fail.
- **Consistency:** Eventual consistency is acceptable, but stale reads should be minimized.

# 2. Back-of-the-Envelope Estimation
Before diving into architecture, let us run some quick numbers to understand the scale we are dealing with. These calculations will guide our decisions about how many nodes we need, what kind of hardware to provision, and where potential bottlenecks might appear.

### 2.1 Traffic Estimates
We are designing for 1 million reads per second and 100,000 writes per second at peak load. This gives us a read-to-write ratio of 10:1, which is typical for caching workloads. Most applications read cached data far more often than they update it.
At this scale, the read path is clearly where we need to optimize. A single machine cannot handle a million requests per second, so we will need to distribute the load across many nodes.

### 2.2 Storage Estimates
We need to cache 100 TB of data. Let us break down what a typical cache entry looks like:
| Component | Size | Notes |
| --- | --- | --- |
| Key | ~100 bytes | User IDs, session tokens, product IDs |
| Value | ~1 KB | Serialized objects, JSON, binary data |
| Metadata | ~32 bytes | TTL, timestamps, flags |
| Total per entry | ~1.1 KB |  |

With 100 TB of data and entries averaging 1.1 KB each, we are looking at roughly 90 billion cache entries. That is a lot of keys to keep track of.

### 2.3 Node Requirements
How many cache nodes do we need? Let us work backwards from our storage requirement.
Modern servers commonly have 64 GB to 256 GB of RAM. If we use nodes with 64 GB of usable memory (leaving some headroom for the operating system and cache overhead):
That is a substantial cluster, but manageable. Companies like Twitter and Netflix run cache clusters with thousands of nodes.

### 2.4 Throughput per Node
With 1,600 nodes handling 1 million reads per second:
This is very comfortable. A single Redis instance on modest hardware can handle 100,000+ operations per second. We have plenty of headroom, which is good because real-world traffic is never perfectly distributed across nodes. Some nodes will be hotter than others.

### 2.5 Network Bandwidth
Network bandwidth is often an overlooked bottleneck. Let us make sure we are not going to saturate our network:
Per node, that works out to less than 1 MB/s, which is trivial for modern networking. Even 10 Gbps network cards can handle over 1 GB/s. Network bandwidth will not be our bottleneck.

### 2.6 Key insights from these Numbers
These calculations tell us several important things:
1. **We need a distributed system.** 100 TB does not fit on one machine. We need roughly 1,600 nodes to hold all the data.
2. **Throughput per node is modest.** At ~700 operations per second per node, each node has plenty of capacity. This gives us room to handle traffic spikes and uneven distribution.
3. **Network is not the bottleneck.** With less than 1 MB/s per node, network bandwidth is not a concern.
4. **Data partitioning is critical.** With 1,600 nodes, we need a reliable way to route requests to the right node. This is where consistent hashing will become essential.

# 3. Core APIs
With our requirements and scale understood, let us define the API contract. A cache API should be simple and fast. Every millisecond of overhead in the API layer eats into the latency budget. We will design a clean REST-ish API with four core operations.

### 3.1 Put (Store a Key-Value Pair)

#### Endpoint: PUT /cache/{key}
This is how applications store data in the cache. The operation should be atomic: either the entire key-value pair is stored successfully, or nothing changes.

#### Request Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| key | string | Yes | The cache key (max 250 bytes). This is what you use to retrieve the data later |
| value | bytes | Yes | The data to store (max 1 MB). Can be JSON, protobuf, or any binary format |
| ttl_seconds | integer | No | How long until the entry expires. If omitted, the entry lives until explicitly deleted or evicted |

#### Example Request:

#### Success Response (200 OK):

#### Error Responses:
| Status | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Invalid input | Key exceeds 250 bytes, value exceeds 1 MB, or invalid TTL |
| 503 Service Unavailable | System overloaded | Cache cluster is at capacity or unreachable |

## 3.2 Get (Retrieve a Value)

#### Endpoint: GET /cache/{key}
The most frequently called endpoint. Applications will call this millions of times per second, so it needs to be fast and return useful information about the cache entry's state.

#### Path Parameters:
| Parameter | Type | Description |
| --- | --- | --- |
| key | string | The cache key to look up |

#### Success Response (200 OK):
We include `ttl_remaining` so clients can make intelligent decisions about refreshing data that is about to expire.

#### Cache Miss Response (200 OK):
Notice we return 200 even for cache misses. A cache miss is not an error. It is normal operation. The client simply needs to fetch the data from the source of truth and potentially cache it.

#### Error Responses:
| Status | Meaning | When It Occurs |
| --- | --- | --- |
| 503 Service Unavailable | System error | Cache cluster is unreachable |

### 3.3 Delete (Remove a Key)

#### Endpoint: DELETE /cache/{key}
Explicitly removes an entry from the cache. This is typically called when the underlying data changes and you want to invalidate the cached copy immediately rather than waiting for TTL expiration.

#### Path Parameters:
| Parameter | Type | Description |
| --- | --- | --- |
| key | string | The cache key to delete |

#### Success Response (200 OK):
The `existed` field tells the caller whether the key was actually in the cache. This is useful for debugging and monitoring cache hit rates.
Deleting a non-existent key is not an error. It returns success with `existed: false`. This makes retry logic simple: clients can safely retry delete operations without worrying about the current state.

### 3.4 Batch Get

#### Endpoint: POST /cache/batch
When an application needs to fetch many keys at once, making individual GET requests would be wasteful. Each request has network overhead. Batch operations reduce this overhead dramatically.

#### Request Body:

#### Success Response (200 OK):
The response separates found keys from missing ones, making it easy for the client to know which keys need to be fetched from the database.
We typically cap batch requests at 100-1000 keys. Larger batches increase latency (the response is only as fast as the slowest key lookup) and can cause memory pressure on both client and server. For very large key sets, clients should make multiple batch requests.
# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complete architecture diagram upfront, we will build the design incrementally. 
We will start with the simplest possible cache and add complexity only as we encounter problems that require it. This mirrors how you would approach the problem in an interview and makes the reasoning behind each component clear.
Our cache needs to do three things well:
1. **Store and retrieve data fast.** This is the core purpose. If lookups are not sub-millisecond, why bother with a cache?
2. **Distribute data across nodes.** 100 TB does not fit on one machine. We need to spread the data across our 1,600 nodes.
3. **Stay available when things break.** Nodes fail. Networks partition. The cache should keep working.

Let us tackle these one at a time.

## 4.1 Starting Simple: A Single Cache Node
Before we distribute anything, let us understand what happens on a single cache node. The simplest cache is just a hash table in memory.

#### Cache Client Library
The cache client is a library embedded in your application. When you call `cache.get("user:123")`, the client library handles all the complexity of talking to the cache cluster. It manages connection pools, handles retries on failures, and (as we will see) routes requests to the correct node.
For now, with just one node, the client simply opens a TCP connection and sends the request.

#### Cache Node
The cache node is where data actually lives. At its core, it is a hash table in memory. When a PUT request arrives, the node computes a hash of the key, stores the key-value pair at that hash slot, and returns success. GET requests look up the key in the hash table and return the value (or a miss indicator if not found).
Modern in-memory stores like Redis can handle 100,000+ operations per second on a single node. The bottleneck is usually network I/O, not CPU or memory lookups.
**The flow for a single node is straightforward:**
This works great until you need to store more data than fits in one machine's memory. That is our next challenge.

## 4.2 Distributing Data Across Nodes
With 100 TB of data and 64 GB per node, we need about 1,600 nodes. But now we have a problem: when a request comes in for key "user:123", how do we know which of the 1,600 nodes has it?
The naive approach would be simple modular hashing:
This works, but it has a fatal flaw. When you add or remove a node, `number_of_nodes` changes. With 1,600 nodes, adding one node means `hash(key) % 1600` becomes `hash(key) % 1601`. Nearly every key maps to a different node. You would have to move almost all your data, which is catastrophic for a running system.
**This is where consistent hashing saves the day.**

### Consistent Hashing: The Key Insight
Consistent hashing arranges both keys and nodes on a virtual ring. Think of a clock face, but instead of 12 hours, you have billions of positions (the range of a hash function). Each node gets a position on this ring based on the hash of its identifier. Each key also gets a position based on its hash.
To find which node owns a key, you compute the key's hash and walk clockwise around the ring until you hit a node. That node owns the key.
When you add a node, it takes a position on the ring. Only keys between the new node and the previous node (counterclockwise) need to move.Instead of rehashing everything, you only relocate about 1/N of the keys. With 1,600 nodes, adding one more node only affects about 0.06% of keys.

### The Router: Mapping Keys to Nodes
The cache client needs to know the ring topology to route requests correctly. This mapping logic is called the router.
Here is how a request flows now:
1. Application calls `cache.get("user:123")`
2. Cache client computes `hash("user:123")` to get a position on the ring
3. Router finds the first node clockwise from that position
4. Client sends the request directly to that node
5. Node looks up the key and returns the value

The client maintains a local copy of the ring topology, so routing happens locally with no network overhead. The cache client knows exactly which node to contact for any given key.

## 4.3 Handling Node Failures with Replication
So far, each key lives on exactly one node. If that node dies, the data is gone. For a cache, losing data is not catastrophic since you can always refetch from the database. 
But having a large portion of your cache suddenly become empty causes a "thundering herd" of requests to hit the database, potentially causing cascading failures.
**We need replication.**

### Replication Strategy
Each key is stored on multiple nodes, typically 3. Using the consistent hashing ring, we define:
- **Primary replica:** The first node clockwise from the key's position
- **Secondary replicas:** The next N-1 nodes clockwise

When a write comes in:
1. Client sends the write to the primary node
2. Primary writes locally and forwards to replicas
3. Depending on consistency requirements, the client may wait for replica acknowledgments or return immediately

When a read comes in:
1. Client can read from any replica (typically the primary for freshest data)
2. If the primary is unavailable, client fails over to a secondary replica

### The Cluster Manager
Someone needs to keep track of which nodes are alive and coordinate the cluster. This is the cluster manager's job.
The cluster manager:
- **Monitors node health** by sending periodic heartbeats. If a node misses several heartbeats (typically 3), it is considered dead.
- **Maintains the ring topology** by tracking which nodes are alive and their positions on the ring.
- **Notifies clients** when the topology changes so they can update their local routing tables.
- **Coordinates rebalancing** when nodes are added or removed, ensuring data moves to the right places.

### Handling a Node Failure
When Node B fails, here is what happens:
1. Cluster manager detects Node B is unresponsive
2. It marks Node B as down and updates the ring
3. It broadcasts the new topology to all clients
4. Clients update their routing tables
5. Requests that would have gone to Node B now go to the next replica (Node C)
6. When Node B recovers, it rejoins the cluster and synchronizes data from its neighbors

The beauty of this design is that the failure is handled transparently. Applications do not need to know that Node B died. The cache client library handles the failover automatically.

## 4.4 The Complete Architecture
Let us put all the pieces together. Here is the complete architecture of our distributed cache:

### How Components Work Together
| Component | Responsibility | Scaling |
| --- | --- | --- |
| Cache Client Library | Routes requests to correct node, handles failover, manages connection pools | Runs in each application instance |
| Cache Nodes | Store key-value pairs in memory, handle expiration, serve requests | Add more nodes as data grows |
| Consistent Hash Ring | Maps keys to nodes with minimal remapping when cluster size changes | Maintained locally in each client |
| Cluster Manager | Monitors health, manages topology, coordinates membership | Typically 3-5 instances for HA |
| Replicas | Provide fault tolerance by storing copies on multiple nodes | Configurable replication factor (typically 3) |

This architecture handles all our requirements:
- **Fast access:** Sub-millisecond lookups from in-memory hash tables
- **Massive scale:** 1,600 nodes holding 100 TB, handling millions of operations per second
- **High availability:** Replication ensures data survives node failures, automatic failover keeps the system running

# 5. Database Design
Wait, database design for an in-memory cache? The term might seem odd, but we still need to think carefully about how data is organized in memory. 
The data structures we choose affect everything from lookup speed to memory efficiency to how we handle eviction.

## 5.1 In-Memory Storage
Unlike a traditional database that writes to disk, a cache keeps everything in RAM. This is what gives us sub-millisecond latency. But memory is expensive and finite, so we need to be smart about how we use it.

#### Primary Hash Table
The core data structure is a hash table. When a GET request arrives, we compute the hash of the key, look up the bucket, and return the value. This gives us **O(1)** average-case lookup time, exactly what we need for a cache.
Modern implementations use techniques like open addressing with Robin Hood hashing or cuckoo hashing to minimize memory overhead and handle collisions efficiently.
Trees give O(log n) lookup, which is fine for databases but too slow for a cache. The whole point is to be faster than the database. We do not need range queries or ordered iteration, so the hash table's random access is perfect.

## 5.2 Persistence Options
Should a cache persist data to disk? It depends on your use case.
| Mode | How It Works | Best For |
| --- | --- | --- |
| No Persistence | Data lives only in memory. When the node restarts, cache is empty | Pure caching where data can be regenerated from the source |
| Snapshots | Periodically dump the entire dataset to disk | Warm restarts, reducing cache warmup time after maintenance |
| Write-Ahead Log | Log every write operation. Replay on restart | When cache data is hard to regenerate or serves as primary storage |

For most caching use cases, no persistence is fine. The cache can be repopulated from the database. Snapshots are useful for large caches where a cold start would overwhelm the database. Write-ahead logs are rarely needed for pure caches but are essential when the cache is also serving as a database (like Redis often does).

## 5.3 Cache Entry Structure
Each entry in the cache contains more than just the key and value. We need metadata to handle expiration, eviction, and debugging.
| Field | Type | Size | Purpose |
| --- | --- | --- | --- |
| key | byte[] | 4B + key length | The lookup identifier (max 250 bytes) |
| value | byte[] | 4B + value length | The cached data (max 1 MB) |
| created_at | int64 | 8B | When the entry was created (for debugging) |
| expires_at | int64 | 8B | When the entry expires (-1 for never) |
| last_accessed | int64 | 8B | Last access time (for LRU eviction) |
| flags | int32 | 4B | Compression flag, serialization format, etc. |

#### Memory overhead calculation:
About 13% of memory goes to overhead. This is acceptable. Trying to optimize further would add complexity without meaningful benefit.

## 5.4 Secondary Indexes
Beyond the primary hash table, each node maintains two additional structures for efficient operations:

#### Expiration Index
A sorted data structure (typically a min-heap or sorted set) ordered by expiration time. This lets us efficiently find and remove expired entries without scanning the entire hash table.
A background thread periodically pops entries from the front of this structure and removes expired keys. This is much more efficient than scanning all keys.

#### LRU List
A doubly-linked list for tracking access order. When memory pressure requires eviction, we remove entries from the tail (least recently used). When a key is accessed, we move it to the head.
The combination of hash table (fast lookup), expiration index (efficient TTL), and LRU list (smart eviction) gives us everything we need for a high-performance cache.
# 6. Design Deep Dive
The high-level design gives us a working system, but the devil is in the details. In an interview, this is where you demonstrate depth of understanding. 
We will explore six critical topics that can make or break a distributed cache: data partitioning, eviction policies, cache consistency, replication strategies, handling hot keys, and security.
These are the areas where real-world systems have learned hard lessons, and understanding them will set you apart.

## 6.1 Data Partitioning with Consistent Hashing
We touched on consistent hashing earlier, but let us go deeper. How you partition data across nodes affects everything: load distribution, scaling operations, and what happens when nodes fail.

### Why Simple Hashing Falls Apart
The obvious approach is modular hashing: `node = hash(key) % num_nodes`. It is simple and distributes keys evenly. The problem shows up when your cluster changes.
Adding just one node to a 10-node cluster causes approximately 90% of keys to map to different nodes. You would need to move almost all your data. During this migration, your cache hit rate plummets, and the database gets hammered with requests. This is why simple hashing only works for static clusters that never change.

### How Consistent Hashing Solves This
Consistent hashing uses a different mental model. Instead of thinking about nodes as numbered buckets, imagine a circular ring with positions from 0 to some large number (typically 2^32 - 1). Both nodes and keys get positions on this ring based on their hash values.
To find which node owns a key:
1. Compute `hash(key)` to get the key's position on the ring
2. Walk clockwise from that position until you hit a node
3. That node owns the key

The magic happens when nodes change. If you add a node, it takes a position on the ring and only "steals" keys from the node that was previously responsible for that section. Instead of moving 90% of keys, you move roughly 1/N of them.

### Virtual Nodes: Fixing the Distribution Problem
There is a catch with basic consistent hashing. If you have only a few nodes, they might cluster on one side of the ring, creating an uneven distribution. One node might handle 40% of keys while another handles 10%.
The solution is virtual nodes. Instead of placing each physical node at one position, we create many "virtual" positions for each node:
With 100+ virtual nodes per physical node, the positions are scattered around the ring, giving near-uniform distribution. Redis Cluster uses this approach with 16,384 hash slots.
**Trade-off:** More virtual nodes means more metadata to store and transmit. Each client needs to know the full ring topology. With 1,600 physical nodes and 100 virtual nodes each, that is 160,000 entries, which is still manageable (a few megabytes).

### Alternative: Fixed Hash Slots (Redis Approach)
Redis Cluster takes a slightly different approach. Instead of a continuous hash ring, it defines exactly 16,384 hash slots:
Each node is assigned a range of slots. Node A might own slots 0-5000, Node B slots 5001-10000, and so on. When you add a node, you manually (or automatically) reassign some slots from existing nodes to the new one.
| Approach | Pros | Cons |
| --- | --- | --- |
| Consistent Hashing | Automatic rebalancing, works with any cluster size | More complex, requires ring topology propagation |
| Hash Slots | Simple to understand, easy manual control | Fixed slot count (16,384), requires explicit slot assignment |

For very large clusters (thousands of nodes), consistent hashing with virtual nodes is the standard choice. For smaller clusters where operational simplicity matters, hash slots work well.

## 6.2 Cache Eviction Policies
Memory is finite. When the cache fills up and a new entry needs space, something has to go. The question is: what do we evict? This decision happens millions of times per second in a busy cache, and getting it wrong tanks your hit rate.
The ideal eviction policy removes entries that will not be accessed again while keeping entries that will be needed soon. Of course, predicting the future is hard, so we use heuristics based on past access patterns.

### LRU: The Go-To Choice
LRU (Least Recently Used) is the most common eviction policy. The intuition is simple: if you have not used something in a while, you probably do not need it.

#### How it works:
1. Keep entries in a doubly-linked list ordered by access time
2. On every access, move the entry to the head of the list
3. When eviction is needed, remove entries from the tail

The combination of a hash table (for O(1) lookup) and a doubly-linked list (for O(1) reordering) gives us constant-time operations.
**The problem:** Moving entries to the head on every access is expensive. At a million operations per second, that is a million pointer updates per second. For read-heavy workloads, this overhead adds up.

### Approximated LRU: The Practical Choice
Redis solved this with approximated LRU. Instead of maintaining a perfect access order, it samples randomly and makes a good-enough decision.

#### How it works:
1. Each entry stores a timestamp of its last access (8 bytes of overhead)
2. When eviction is needed, randomly sample N keys (default: 5)
3. Evict the key with the oldest access time among the samples
4. Repeat until enough memory is freed

This sounds crude, but it works surprisingly well. With just 5 samples, you get about 90% of the benefit of true LRU. Bump it to 10 samples and you are at 99%. The beauty is that reads are now free since you are just updating a timestamp, not rearranging a linked list.

### Other Eviction Strategies
| Policy | How It Works | When to Use |
| --- | --- | --- |
| LFU (Least Frequently Used) | Track access count, evict lowest | Stable workloads with clear hot/cold separation |
| TTL-based | Evict expired entries first | Time-sensitive data like sessions or tokens |
| Random | Pick random entries to evict | When simplicity matters more than hit rate |
| FIFO | Evict oldest entries first | Streaming data where order matters |

**LFU** sounds appealing since frequently accessed data should stay in cache. But it has a cold start problem: new entries have zero or low counts and get evicted immediately. LFU also adapts slowly when access patterns change.
**TTL-based eviction** is not really a choice. You want it in addition to LRU/LFU. Expired data should not consume memory, period.

### Recommendation for Production
Use **approximated LRU with mandatory TTL**. Here is why:
1. **Approximated LRU** gives 95%+ of true LRU's hit rate with O(1) read operations
2. **TTL** ensures data freshness and provides a safety net against memory leaks
3. The combination handles both access-pattern-based eviction and time-based cleanup

## 6.3 Cache Consistency and Invalidation
There is a famous quote in computer science: "There are only two hard things in computer science: cache invalidation and naming things." The quote is funny because it is painfully true. Keeping cached data in sync with the source of truth is genuinely difficult.
When you update a user's email in the database, the cached copy of their profile is now wrong. How long can you tolerate that? A few milliseconds? A few seconds? It depends on the application. Showing a stale email address is annoying but harmless. Showing stale inventory counts can lead to overselling.

### The Fundamental Trade-off
You cannot have perfect consistency without giving up some performance. Every consistency strategy sits somewhere on this spectrum:

### Cache-Aside Pattern
Cache-aside (also called "lazy loading") is the most common pattern because it is simple and flexible. The application is responsible for managing the cache explicitly.
**On read:** Check the cache first. If it is there, return it. If not, fetch from database, store in cache, and return.
**On write:** Update the database first, then invalidate (delete) the cache entry. The next read will repopulate the cache with fresh data.
**Why delete instead of update?** Deleting is simpler and avoids race conditions. Consider this scenario:
1. Request A reads user from DB (version 1)
2. Request B updates user in DB (version 2)
3. Request B updates cache with version 2
4. Request A updates cache with version 1 (stale!)

By deleting instead of updating, the next reader always gets fresh data from the database.

### Write-Through: Strongest Consistency
In write-through caching, every write goes to both cache and database. The cache is always fresh.
**The cost:** Write latency increases because you are waiting for both cache and database writes to complete. For write-heavy workloads, this can be a significant penalty.
**When to use it:** When you absolutely need cached data to be fresh and you have a read-heavy workload where the write latency penalty is acceptable.

### Write-Behind: Performance over Safety
Write-behind (or write-back) flips the priority. Writes go to the cache immediately and return success. The database is updated asynchronously in the background.
**The benefit:** Ultra-low write latency. The application does not wait for the database.
**The risk:** If the cache node fails before flushing to the database, you lose data. This is only acceptable when losing some writes is tolerable (analytics, logs) or when you have other durability mechanisms.

### Invalidation Across a Distributed Cache
With data replicated across multiple cache nodes, invalidation gets complicated. When a user profile changes, you need to invalidate it on every node that might have a copy.

#### Option 1: Delete from all replicas
On write, the application explicitly deletes the key from all cache nodes. This is simple but requires knowing all nodes and introduces latency proportional to the number of nodes.

#### Option 2: Pub/Sub invalidation
Use a message broker to broadcast invalidation events:
Each cache node subscribes to the invalidation channel. When a message arrives, the node deletes the local copy. This scales better than direct invalidation but introduces latency (the time for the message to propagate).

#### Option 3: Short TTLs as a safety net
Even with explicit invalidation, set short TTLs on cached data. This guarantees that stale data eventually expires, even if invalidation messages are lost or delayed.

### Practical Recommendation
For most applications, use **cache-aside with short TTLs**:
1. Application manages cache explicitly (simple, no magic)
2. Invalidate on writes (immediate freshness for the common case)
3. Short TTLs (safety net for edge cases)

If you need cross-node invalidation, add pub/sub on top. But start simple since many applications work fine with TTL-based eventual consistency.
| Pattern | Consistency | Latency | Complexity | Use When |
| --- | --- | --- | --- | --- |
| Cache-Aside | Eventual | Low | Low | Default choice |
| Write-Through | Strong | Higher | Medium | Reads >> Writes, freshness critical |
| Write-Behind | Eventual | Lowest | High | Can tolerate data loss |
| TTL-only | Eventual | Lowest | Lowest | Staleness is acceptable |

## 6.4 High Availability and Replication
When a cache node goes down, something bad happens. All the keys that lived on that node are suddenly missing. If that node held 1% of your data, you now have 1% more cache misses. Those misses hit your database. If your database was already at 80% capacity because the cache was absorbing most of the load, that extra 1% might be enough to push it over the edge.
This is the "thundering herd" problem. A cache failure causes a spike in database load, which causes slower responses, which causes timeouts, which causes retries, which causes more load. Things cascade. Production goes down. Pages get sent.
The solution is **replication**. Store each key on multiple nodes so that when one fails, others can pick up the slack.

### Replication Strategy: Primary with Replicas
The most common approach is primary-replica replication. Each key has one primary node (for writes) and N-1 replica nodes (for reads and failover).

#### How it works:
1. All writes go to the primary node
2. Primary replicates changes to replicas asynchronously
3. Reads can go to primary or any replica (trading freshness for latency)
4. If primary fails, a replica is promoted

Waiting for all replicas to acknowledge every write would add significant latency. For a cache, eventual consistency between replicas is acceptable.

### Quorum-Based Consistency
If you need stronger guarantees, you can use quorum-based replication. The idea is to require a minimum number of nodes to agree before a read or write is considered successful.
With N replicas, you configure:
- **W** = number of nodes that must acknowledge a write
- **R** = number of nodes that must respond to a read

The rule is: if **W + R > N**, you get strong consistency because at least one node in every read will have the latest write.
Common configurations:
- **N=3, W=2, R=2**: Strong consistency, tolerates 1 failure
- **N=3, W=1, R=1**: Fastest, but may read stale data
- **N=3, W=3, R=1**: Always consistent reads, but writes block on all nodes

For a cache where speed matters more than perfect consistency, N=3, W=1, R=1 is often the right choice. You get fast operations and can tolerate failures, accepting that reads might occasionally be stale.

### Detecting Node Failures
Before you can failover, you need to know a node is down. There are two common approaches:
**Heartbeat-based detection:** A central cluster manager pings each node every second. If a node misses 3 consecutive heartbeats (3 seconds), it is marked as failed.
**Gossip protocol:** Nodes share health information with each other. Each node periodically picks random peers and exchanges its view of the cluster. Failed nodes are detected when no one has heard from them recently.
Gossip is more resilient (no single point of failure) but slower (information takes time to propagate). Heartbeats are faster but require a reliable cluster manager.

### Recovery After Failure
When a failed node comes back online, it is out of sync. Its data is stale (or completely gone if it lost its disk). How does it catch up?
**Option 1: Full sync.** Copy all data from a healthy replica. Simple but slow for large datasets.
**Option 2: Partial sync.** If the node was logging writes (write-ahead log), it can request just the operations it missed since the failure. Much faster for short outages.
**Option 3: Lazy loading.** Start empty and repopulate on demand as requests come in. This spreads the load over time but means higher miss rates initially.
Most production systems use a combination: attempt partial sync if possible, fall back to full sync if the gap is too large, and always allow lazy loading as a final fallback.

## 6.5 Handling Hot Keys
In any popular application, some data is accessed far more than others. A celebrity's profile, a viral tweet, a flash sale product, these "hot keys" can receive orders of magnitude more traffic than average keys. And here is the problem: consistent hashing maps each key to exactly one node.
If key "taylor_swift:profile" gets 100,000 requests per second while average keys get 10 requests per second, the node hosting Taylor Swift's profile is drowning while other nodes sit idle. The hot node's latency spikes, affecting all keys on that node, not just the celebrity one.

### Solution 1: Local Caching (L1 Cache)
The simplest solution is to not hit the distributed cache at all for hot keys. Keep a small local cache on each application server.

#### How it works:
1. Each app server maintains a small in-process cache (maybe 100 MB)
2. Before hitting the distributed cache, check the local cache
3. Use very short TTLs (1-5 seconds) to limit staleness
4. Hot keys naturally stay in L1 because they are accessed frequently

**Why it works:** If you have 100 application servers and a key is requested 100,000 times per second, each server sees about 1,000 requests per second for that key. With a 1-second TTL on L1 cache, only 100 requests per second actually hit the distributed cache (one per server per second). You just reduced load by 1000x.
Staleness. With 1-second TTLs, readers might see data up to 1 second old. For most applications, this is fine. For real-time bidding or stock tickers, it might not be.

### Solution 2: Read Replicas for Hot Keys
Instead of putting the hot key on one node, spread it across many nodes.

#### How it works:
1. Monitor access patterns to detect hot keys
2. When a key exceeds a threshold (say, 1,000 req/s), replicate it to N additional nodes
3. Route reads for hot keys to a random replica
4. Writes still go to the primary, which propagates to replicas

The hard part is detection. You need real-time monitoring of access patterns, which adds overhead. Some systems skip detection and just replicate the keys they know will be hot (product pages during a sale, celebrity profiles).

### Solution 3: Key Splitting
If you know a key will be hot in advance, you can split it into multiple keys:
The application randomly picks a suffix (0-9) for each read, spreading requests across 10 different cache nodes.
**The catch:** Writes become complicated. You need to update all 10 keys atomically, or accept that some reads might see stale data briefly.

### Practical Recommendation
Start with **local caching (L1)**. It is simple, effective, and solves 90% of hot key problems with no distributed coordination.
If L1 is not enough (keys too large, staleness not acceptable), add **hot key detection and replication**. But only invest in this if you actually have the problem, since most applications never get famous enough to need it.
| Solution | Complexity | Effectiveness | When to Use |
| --- | --- | --- | --- |
| Local Cache (L1) | Low | High | First line of defense |
| Read Replicas | Medium | High | When L1 is not enough |
| Key Splitting | Medium | Medium | Known hot keys |

## 6.6 Security Considerations
A cache often holds sensitive data: user sessions, API tokens, personally identifiable information, cached database queries. If someone gains unauthorized access to your cache, they can read this data, modify it, or delete it to cause outages.

### Defense in Depth
Security is not one thing you do. It is layers of protection that work together.
**Network isolation:** The cache should live in a private network (VPC) with no direct internet access. Only your application servers should be able to reach it.
**Authentication:** Require credentials to connect. Redis supports password authentication (AUTH command) and TLS client certificates. Do not run an unauthenticated cache in production.
**Encryption in transit:** Use TLS for all connections, both client-to-cache and cache-node-to-cache-node. This prevents eavesdropping on the network.
**Access control:** If your cache supports it, implement read/write permissions. Maybe your analytics service only needs read access while your API service needs both.

### Common Attack Patterns
Two cache-specific attacks are worth knowing:

#### Cache Penetration
An attacker repeatedly requests keys that do not exist. Each request misses the cache and hits the database. With enough requests, the database gets overwhelmed.
**Defense:** Cache negative results. When a key is not found in the database, cache a "null" marker with a short TTL (30-60 seconds). Subsequent requests for the same nonexistent key hit the cache instead of the database.

#### Cache Stampede
A popular cached item expires. Suddenly, thousands of requests simultaneously discover the cache miss and all try to regenerate the cached value from the database. The database cannot handle the spike.
**Defense:** Implement locking or probabilistic early expiration. With locking, only one request regenerates the cache while others wait. With probabilistic early expiration, some requests refresh the cache slightly before the TTL expires, preventing the thundering herd.
# References
- [Redis Documentation](https://redis.io/documentation) - Comprehensive guide to Redis architecture and features.
- [Memcached Wiki](https://github.com/memcached/memcached/wiki) - Technical details on Memcached design.
- [Consistent Hashing Paper](https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf) - Original paper by Karger et al.
- [Amazon ElastiCache Best Practices](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/BestPractices.html) - Production caching patterns from AWS.

# Quiz

## Design Distributed Cache Quiz
What is the primary purpose of using a distributed cache in front of a primary database?