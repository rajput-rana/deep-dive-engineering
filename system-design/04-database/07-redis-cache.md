# ⚡ Redis - In-Memory Cache & Key-Value Store

<div align="center">

**Blazing-fast in-memory data structure store**

[![Redis](https://img.shields.io/badge/Redis-In--Memory-red?style=for-the-badge)](https://redis.io/)
[![Cache](https://img.shields.io/badge/Cache-Ultra%20Fast-orange?style=for-the-badge)](./)
[![Key-Value](https://img.shields.io/badge/Key--Value-Simple-blue?style=for-the-badge)](./)

*Master Redis caching strategies, data structures, and performance optimization*

</div>

---

## 🎯 What is Redis?

<div align="center">

**Redis (Remote Dictionary Server) is an in-memory data structure store used as a database, cache, and message broker.**

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **⚡ In-Memory** | Data stored in RAM for ultra-fast access |
| **🔑 Key-Value Store** | Simple key-value data model |
| **📊 Rich Data Structures** | Strings, Lists, Sets, Hashes, Sorted Sets |
| **🚀 High Performance** | Sub-millisecond latency |
| **🔄 Persistence Options** | RDB snapshots, AOF logging |
| **🌐 Distributed** | Redis Cluster, Sentinel for HA |

**Mental Model:** Think of Redis as a super-fast hash table in memory that can persist to disk.

</div>

---

## 🏗️ Core Concepts

<div align="center">

### Redis Architecture

| Component | Description |
|:---:|:---:|
| **Key** | Unique identifier (string) |
| **Value** | Data associated with key (various types) |
| **TTL** | Time-to-live (expiration) |
| **Database** | Logical separation (0-15 by default) |
| **Memory** | All data stored in RAM |
| **Persistence** | Optional disk storage |

### Key Naming Conventions

**Best Practices:**
```
user:123:profile          # User profile
session:abc123           # Session data
product:456:views        # Product views counter
cache:api:users:list     # API response cache
```

**Pattern:** `object:id:field` or `namespace:key`

</div>

---

## 📊 Data Structures

<div align="center">

### 1. Strings

**Simple key-value pairs**

```redis
SET user:123:name "John Doe"
GET user:123:name
# Returns: "John Doe"

SET user:123:visits 0
INCR user:123:visits
# Increments to 1

SET user:123:email "john@example.com" EX 3600
# Sets with 1 hour expiration
```

**Use Cases:**
- ✅ Caching simple values
- ✅ Counters
- ✅ Session storage
- ✅ Feature flags

---

### 2. Hashes

**Field-value pairs within a key**

```redis
HSET user:123 name "John" email "john@example.com" age 30
HGET user:123 name
# Returns: "John"

HGETALL user:123
# Returns all fields and values

HINCRBY user:123 age 1
# Increment age by 1
```

**Use Cases:**
- ✅ User profiles
- ✅ Object attributes
- ✅ Shopping carts

**Advantages:**
- Atomic operations on multiple fields
- Memory efficient for objects

---

### 3. Lists

**Ordered collection of strings**

```redis
LPUSH notifications:user:123 "New message"
LPUSH notifications:user:123 "Friend request"
LRANGE notifications:user:123 0 -1
# Returns: ["Friend request", "New message"]

RPOP notifications:user:123
# Remove and return rightmost element
```

**Use Cases:**
- ✅ Message queues
- ✅ Activity feeds
- ✅ Recent items

**Operations:**
- `LPUSH/RPUSH` - Add to left/right
- `LPOP/RPOP` - Remove from left/right
- `LRANGE` - Get range of elements
- `LLEN` - Get length

---

### 4. Sets

**Unordered collection of unique strings**

```redis
SADD tags:product:456 "electronics" "gadgets" "smartphone"
SMEMBERS tags:product:456
# Returns: ["electronics", "gadgets", "smartphone"]

SADD tags:product:789 "electronics" "accessories"
SINTER tags:product:456 tags:product:789
# Returns: ["electronics"] (intersection)
```

**Use Cases:**
- ✅ Tags
- ✅ Unique identifiers
- ✅ Set operations (union, intersection)

**Operations:**
- `SADD` - Add members
- `SMEMBERS` - Get all members
- `SINTER` - Intersection
- `SUNION` - Union
- `SDIFF` - Difference

---

### 5. Sorted Sets

**Ordered collection with scores**

```redis
ZADD leaderboard 1000 "player1"
ZADD leaderboard 1500 "player2"
ZADD leaderboard 800 "player3"

ZREVRANGE leaderboard 0 2 WITHSCORES
# Returns top 3 players with scores
```

**Use Cases:**
- ✅ Leaderboards
- ✅ Time-series data
- ✅ Priority queues
- ✅ Ranking systems

**Operations:**
- `ZADD` - Add with score
- `ZRANGE` - Get range (ascending)
- `ZREVRANGE` - Get range (descending)
- `ZRANK` - Get rank
- `ZSCORE` - Get score

---

### 6. Bitmaps

**Bit-level operations**

```redis
SETBIT user:123:login:2024-01-15 1
GETBIT user:123:login:2024-01-15 1
# Returns: 1 (logged in)

BITCOUNT user:123:login:2024-01-15
# Count active bits (login days)
```

**Use Cases:**
- ✅ User activity tracking
- ✅ Feature flags
- ✅ Analytics

---

### 7. HyperLogLog

**Approximate unique count**

```redis
PFADD visitors:2024-01-15 "user1" "user2" "user3"
PFCOUNT visitors:2024-01-15
# Returns approximate unique count
```

**Use Cases:**
- ✅ Unique visitor counting
- ✅ Cardinality estimation
- ✅ Analytics

**Advantages:**
- Memory efficient (12KB per HyperLogLog)
- Approximate but accurate enough

---

### 8. Streams

**Log-like data structure**

```redis
XADD orders * user_id 123 product_id 456 total 99.99
XREAD STREAMS orders 0
# Read from stream
```

**Use Cases:**
- ✅ Event sourcing
- ✅ Message queues
- ✅ Activity logs

</div>

---

## ⚡ Caching Strategies

<div align="center">

### Cache-Aside (Lazy Loading)

**Application manages cache**

```
1. Check cache
2. If miss → Query database
3. Store in cache
4. Return data
```

**Pros:** Simple, cache only what's accessed  
**Cons:** Cache miss penalty, potential stale data

---

### Write-Through

**Write to cache and database simultaneously**

```
1. Write to cache
2. Write to database
3. Return success
```

**Pros:** Cache always consistent  
**Cons:** Write latency (both operations)

---

### Write-Back (Write-Behind)

**Write to cache, database write is async**

```
1. Write to cache
2. Return success
3. Async write to database
```

**Pros:** Low write latency  
**Cons:** Risk of data loss, complexity

---

### Refresh-Ahead

**Proactively refresh cache before expiration**

```
1. Check TTL
2. If near expiration → Refresh in background
3. Return cached data
```

**Pros:** Reduces cache misses  
**Cons:** Wastes resources if data not accessed

</div>

---

## 🔄 Expiration & Eviction

<div align="center">

### TTL (Time-To-Live)

**Automatic expiration**

```redis
SET key "value" EX 3600        # Expires in 3600 seconds
SET key "value" PX 3600000    # Expires in 3600000 milliseconds
EXPIRE key 3600                # Set expiration on existing key
TTL key                        # Check remaining time
```

**Use Cases:**
- ✅ Session data
- ✅ Temporary data
- ✅ Rate limiting

---

### Eviction Policies

**When memory limit reached:**

| Policy | Description | Use Case |
|:---:|:---:|:---:|
| **noeviction** | Return errors on write | Critical data |
| **allkeys-lru** | Evict least recently used | General caching |
| **allkeys-lfu** | Evict least frequently used | Long-term caching |
| **allkeys-random** | Evict random keys | No access pattern |
| **volatile-lru** | Evict LRU with expiration | Mixed data |
| **volatile-ttl** | Evict shortest TTL | Time-based data |

**Configuration:**
```redis
maxmemory 2gb
maxmemory-policy allkeys-lru
```

</div>

---

## 🔐 Persistence Options

<div align="center">

### RDB (Redis Database Backup)

**Point-in-time snapshots**

| Aspect | Description |
|:---:|:---:|
| **Format** | Binary snapshots |
| **Frequency** | Configurable (save points) |
| **Recovery** | Fast (load entire dataset) |
| **Data Loss** | Up to last save point |

**Configuration:**
```redis
save 900 1      # Save if 1 key changed in 900 seconds
save 300 10     # Save if 10 keys changed in 300 seconds
save 60 10000   # Save if 10000 keys changed in 60 seconds
```

---

### AOF (Append-Only File)

**Log every write operation**

| Aspect | Description |
|:---:|:---:|
| **Format** | Text commands |
| **Frequency** | Every write (fsync configurable) |
| **Recovery** | Slower (replay commands) |
| **Data Loss** | Minimal (depends on fsync) |

**Fsync Options:**
- `always` - Every write (safest, slowest)
- `everysec` - Once per second (balanced)
- `no` - OS decides (fastest, risk of data loss)

**Configuration:**
```redis
appendonly yes
appendfsync everysec
```

---

### Hybrid Approach

**Use both RDB + AOF**

**Benefits:**
- ✅ RDB for fast recovery
- ✅ AOF for minimal data loss
- ✅ Best of both worlds

</div>

---

## 🌐 High Availability & Scaling

<div align="center">

### Redis Sentinel

**High availability and monitoring**

| Component | Role |
|:---:|:---:|
| **Master** | Handles writes |
| **Replicas** | Read replicas |
| **Sentinels** | Monitor and failover |

**Features:**
- ✅ Automatic failover
- ✅ Monitoring
- ✅ Notifications

---

### Redis Cluster

**Horizontal scaling**

| Feature | Description |
|:---:|:---:|
| **Sharding** | Data distributed across nodes |
| **Hash Slots** | 16384 slots distributed |
| **Replication** | Each shard has replicas |
| **Automatic Failover** | Replica promotes to master |

**Cluster Architecture:**
```
Node 1: Slots 0-5460 (Master) + Replica
Node 2: Slots 5461-10922 (Master) + Replica
Node 3: Slots 10923-16383 (Master) + Replica
```

**Key Routing:**
```
slot = CRC16(key) % 16384
```

</div>

---

## 🎯 Use Cases

<div align="center">

### ✅ Ideal Use Cases

| Use Case | Why Redis |
|:---:|:---:|
| **Caching** | Sub-millisecond latency |
| **Session Storage** | Fast access, TTL support |
| **Rate Limiting** | Atomic counters, TTL |
| **Leaderboards** | Sorted sets |
| **Real-Time Analytics** | Fast aggregations |
| **Message Queues** | Lists, Pub/Sub |
| **Feature Flags** | Fast lookups |
| **Counting** | Atomic operations |

---

### ❌ When NOT to Use

| Scenario | Better Alternative |
|:---:|:---:|
| **Large Datasets** | Disk-based databases |
| **Complex Queries** | SQL databases |
| **Permanent Storage** | Databases with persistence |
| **ACID Requirements** | Relational databases |

</div>

---

## 💡 Common Patterns

<div align="center">

### 1. Cache-Aside Pattern

```python
def get_user(user_id):
    # Check cache
    cached = redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    
    # Cache miss - query database
    user = db.query_user(user_id)
    
    # Store in cache
    redis.setex(f"user:{user_id}", 3600, json.dumps(user))
    
    return user
```

---

### 2. Rate Limiting

```python
def rate_limit(user_id, limit=100, window=3600):
    key = f"rate_limit:{user_id}"
    current = redis.incr(key)
    
    if current == 1:
        redis.expire(key, window)
    
    return current <= limit
```

---

### 3. Distributed Lock

```python
def acquire_lock(lock_key, timeout=10):
    identifier = str(uuid.uuid4())
    end = time.time() + timeout
    
    while time.time() < end:
        if redis.set(lock_key, identifier, nx=True, ex=timeout):
            return identifier
        time.sleep(0.001)
    
    return False

def release_lock(lock_key, identifier):
    pipe = redis.pipeline(True)
    while True:
        try:
            pipe.watch(lock_key)
            if pipe.get(lock_key) == identifier:
                pipe.multi()
                pipe.delete(lock_key)
                pipe.execute()
                return True
            pipe.unwatch()
            break
        except redis.WatchError:
            pass
    return False
```

---

### 4. Leaderboard

```python
def update_leaderboard(player_id, score):
    redis.zadd("leaderboard", {player_id: score})

def get_top_players(limit=10):
    return redis.zrevrange("leaderboard", 0, limit-1, withscores=True)
```

---

### 5. Session Storage

```python
def create_session(user_id):
    session_id = str(uuid.uuid4())
    redis.setex(f"session:{session_id}", 3600, user_id)
    return session_id

def get_session(session_id):
    return redis.get(f"session:{session_id}")
```

</div>

---

## ⚡ Performance Optimization

<div align="center">

### Best Practices

| Practice | Why |
|:---:|:---:|
| **Use pipelining** | Reduce round trips |
| **Use appropriate data structures** | Memory and performance |
| **Set TTLs** | Prevent memory bloat |
| **Monitor memory usage** | Prevent evictions |
| **Use connection pooling** | Reduce connection overhead |
| **Batch operations** | Reduce network calls |

### Pipelining Example

```python
# Without pipelining (3 round trips)
redis.set("key1", "value1")
redis.set("key2", "value2")
redis.set("key3", "value3")

# With pipelining (1 round trip)
pipe = redis.pipeline()
pipe.set("key1", "value1")
pipe.set("key2", "value2")
pipe.set("key3", "value3")
pipe.execute()
```

---

### Memory Optimization

| Technique | Description |
|:---:|:---:|
| **Use appropriate data types** | Hashes for objects, not JSON strings |
| **Compress large values** | Use compression for large strings |
| **Set TTLs** | Auto-expire unused data |
| **Monitor memory** | Use INFO memory command |
| **Use Redis Modules** | RedisTimeSeries, RedisJSON for efficiency |

</div>

---

## 🔐 Security Best Practices

<div align="center">

### Security Measures

| Practice | Description | Implementation |
|:---:|:---:|:---:|
| **Authentication** | Require password | `requirepass` in config |
| **Network Security** | Bind to specific IPs | `bind 127.0.0.1` |
| **TLS/SSL** | Encrypt connections | Enable TLS |
| **ACLs** | Access control lists | Define user permissions |
| **Disable Commands** | Remove dangerous commands | `rename-command FLUSHDB ""` |
| **Firewall Rules** | Restrict access | Whitelist IPs |

### ACL Example

```redis
# Create user with specific permissions
ACL SETUSER app_user on >password +get +set +hget +hset ~cache:*
```

</div>

---

## 🎓 Interview Questions

<div align="center">

### Expert-Level Questions

| Question | Key Points |
|:---:|:---:|
| **Design a distributed cache** | Redis Cluster, sharding, replication, eviction policies |
| **How do you implement rate limiting?** | Counters with TTL, sliding window, token bucket |
| **Design a session store** | Redis with TTL, session ID generation, distributed sessions |
| **How do you handle cache invalidation?** | TTL, cache tags, event-driven invalidation |
| **Design a leaderboard system** | Sorted sets, real-time updates, pagination |
| **How do you ensure cache consistency?** | Write-through, cache-aside, invalidation strategies |
| **Design a pub/sub system** | Redis Pub/Sub, channels, message patterns |

</div>

---

## 🔄 Pub/Sub (Publish/Subscribe)

<div align="center">

### Message Patterns

**Publish:**
```redis
PUBLISH notifications "User 123 logged in"
```

**Subscribe:**
```redis
SUBSCRIBE notifications
```

**Pattern Subscribe:**
```redis
PSUBSCRIBE notifications:*
```

**Use Cases:**
- ✅ Real-time notifications
- ✅ Event broadcasting
- ✅ Chat systems
- ✅ Cache invalidation

**Limitations:**
- ❌ No message persistence
- ❌ No message queuing
- ❌ No acknowledgment

**For persistent messaging:** Use Redis Streams or dedicated message queue

</div>

---

## 📊 Monitoring & Debugging

<div align="center">

### Key Metrics

| Metric | Command | What It Tells |
|:---:|:---:|:---:|
| **Memory Usage** | `INFO memory` | Current memory consumption |
| **Connected Clients** | `INFO clients` | Number of connections |
| **Commands Processed** | `INFO stats` | Throughput |
| **Keyspace** | `INFO keyspace` | Number of keys per database |
| **Replication** | `INFO replication` | Replica status |
| **Persistence** | `INFO persistence` | RDB/AOF status |

### Common Commands

```redis
INFO                    # Server information
MONITOR                 # Real-time command monitoring
SLOWLOG GET 10          # Get slow queries
CONFIG GET *            # Get all configuration
KEYS pattern            # Find keys (use SCAN in production)
```

**⚠️ Warning:** `KEYS` blocks the server. Use `SCAN` instead in production.

</div>

---

## 🚀 Redis vs Alternatives

<div align="center">

### Comparison

| Feature | Redis | Memcached | Database |
|:---:|:---:|:---:|:---:|
| **Data Structures** | Rich (Strings, Sets, etc.) | Simple (Strings only) | Tables |
| **Persistence** | Yes (RDB, AOF) | No | Yes |
| **Replication** | Yes | No | Yes |
| **Clustering** | Yes | No | Yes |
| **Latency** | Sub-millisecond | Sub-millisecond | Milliseconds |
| **Use Case** | Cache + Data Store | Pure Cache | Persistent Storage |

**💡 Choose Redis when:** You need rich data structures, persistence options, and high performance.

</div>

---

## 💡 Common Patterns & Anti-Patterns

<div align="center">

### ✅ Best Practices

| Practice | Why |
|:---:|:---:|
| **Use appropriate data structures** | Memory and performance efficiency |
| **Set TTLs** | Prevent memory bloat |
| **Use pipelining** | Reduce network round trips |
| **Monitor memory** | Prevent evictions and OOM |
| **Use connection pooling** | Reduce connection overhead |
| **Handle failures gracefully** | Fallback to database on cache miss |

---

### ❌ Anti-Patterns

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Storing large objects** | Memory pressure | Use object storage, store references |
| **No TTLs** | Memory bloat | Set appropriate TTLs |
| **Using KEYS in production** | Blocks server | Use SCAN instead |
| **Storing everything** | Memory exhaustion | Cache only hot data |
| **No eviction policy** | OOM errors | Configure maxmemory and policy |
| **Single Redis instance** | No HA | Use Sentinel or Cluster |

</div>

---

<div align="center">

**Master Redis for ultra-fast caching and data structures! 🚀**

*Redis is the go-to solution for high-performance caching and real-time applications.*

</div>

