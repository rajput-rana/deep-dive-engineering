# Consistent Hashing

## Summary

Consistent hashing is a distributed hashing technique that efficiently distributes data across multiple nodes (servers, caches, databases) in a way that minimizes data movement when nodes are added or removed. Unlike traditional hashing (`Hash(key) mod N`), consistent hashing ensures only a small fraction of keys need reassignment when the number of nodes changes.

Popularized by Amazon's Dynamo paper, it's now fundamental in distributed databases like DynamoDB, Cassandra, and ScyllaDB.

## The Problem with Traditional Hashing

### Traditional Approach: `Hash(key) mod N`

**How it works:**
- Hash the request key (e.g., user IP address)
- Use modulo operation: `Hash(key) mod N` where N = number of servers
- Route request to the assigned server

**Example with 5 servers:**
```
User IP: 192.168.1.100
Hash(192.168.1.100) = 12345
12345 mod 5 = 0 → Route to Server S0

User IP: 192.168.1.101
Hash(192.168.1.101) = 12346
12346 mod 5 = 1 → Route to Server S1
```

**Diagram:**
```
Traditional Hashing:
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│   S0    │  │   S1    │  │   S2    │  │   S3    │  │   S4    │
└─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘
    │            │            │            │            │
    └────────────┴────────────┴────────────┴────────────┘
              Hash(key) mod 5
```

### The Problem: Adding/Removing Servers

**Scenario 1: Adding Server S5**

When you add a new server, you must change from `mod 5` to `mod 6`:

```
Before (mod 5):
Hash(key) mod 5 → Server assignment

After (mod 6):
Hash(key) mod 6 → Server assignment

Result: MOST keys get reassigned to different servers!
```

**Diagram:**
```
Before: 5 servers (mod 5)
┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐
│ S0 │ │ S1 │ │ S2 │ │ S3 │ │ S4 │
└────┘ └────┘ └────┘ └────┘ └────┘

After: 6 servers (mod 6)
┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐
│ S0 │ │ S1 │ │ S2 │ │ S3 │ │ S4 │ │ S5 │
└────┘ └────┘ └────┘ └────┘ └────┘ └────┘
  ✗      ✗      ✗      ✗      ✗      ✓
(Most keys reassigned)
```

**Problems:**
- Massive rehashing
- Session loss
- Cache invalidation
- Performance degradation

**Scenario 2: Removing Server S4**

When a server fails, you change from `mod 5` to `mod 4`:

```
Before: Hash(key) mod 5
After:  Hash(key) mod 4

Result: MOST keys get reassigned!
```

**Diagram:**
```
Before: 5 servers
┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐
│ S0 │ │ S1 │ │ S2 │ │ S3 │ │ S4 │
└────┘ └────┘ └────┘ └────┘ └────┘
                                ✗ (fails)

After: 4 servers
┌────┐ ┌────┐ ┌────┐ ┌────┐
│ S0 │ │ S1 │ │ S2 │ │ S3 │
└────┘ └────┘ └────┘ └────┘
  ✗      ✗      ✗      ✗
(Most keys reassigned)
```

## How Consistent Hashing Works

Consistent hashing uses a **circular hash space** (hash ring) where both nodes and keys are mapped to positions.

**Key Property:** When nodes change, only `k/n` keys need reassignment (where k = total keys, n = total nodes).

### Constructing the Hash Ring

**Hash Space:**
- Large, fixed hash space: `0` to `2^32 - 1` (32-bit hash)
- Circular structure (wraps around)

**Diagram:**
```
Hash Ring (0 to 2^32-1):
        0
        │
    ┌───┴───┐
    │       │
    │       │
    └───┬───┘
    2^32-1
```

### Placing Servers on the Ring

Each server is assigned a position by computing `Hash(server_id)`.

**Example with 5 servers:**
```
S0 → Hash("S0") → Position 100
S1 → Hash("S1") → Position 500
S2 → Hash("S2") → Position 1000
S3 → Hash("S3") → Position 2000
S4 → Hash("S4") → Position 3000
```

**Diagram:**
```
Hash Ring:
        0
        │
    ┌───┴───┐
    │  S0   │ Position 100
    │       │
    │  S1   │ Position 500
    │       │
    │  S2   │ Position 1000
    │       │
    │  S3   │ Position 2000
    │       │
    │  S4   │ Position 3000
    └───┬───┘
    2^32-1
```

### Mapping Keys to Servers

When a key is added:
1. Compute `Hash(key)` to get position on ring
2. Move **clockwise** around ring
3. Assign to **first server** encountered

**Example:**
```
Key: User IP 192.168.1.100
Hash(192.168.1.100) = 150

Move clockwise from position 150:
- Next server: S1 (at position 500)
- Assign key to S1
```

**Diagram:**
```
Hash Ring:
        0
        │
    ┌───┴───┐
    │  S0   │ 100
    │       │
    │ Key   │ 150 ──┐
    │       │       │ Clockwise
    │  S1   │ 500 ◄─┘ (assigned here)
    │       │
    │  S2   │ 1000
    │       │
    │  S3   │ 2000
    │       │
    │  S4   │ 3000
    └───┬───┘
```

**Rule:** If key's hash falls directly on a node's position, it belongs to that node.

## Adding a New Server

**Scenario:** Add Server S5

**Process:**
1. Compute `Hash("S5")` → Position 750
2. S5 falls between S1 (500) and S2 (1000)
3. S5 takes over keys between S1 and S5
4. Only keys in this range need reassignment

**Diagram:**
```
Before:
        0
        │
    ┌───┴───┐
    │  S0   │ 100
    │       │
    │  S1   │ 500
    │       │
    │  S2   │ 1000
    │       │
    │  S3   │ 2000
    │       │
    │  S4   │ 3000
    └───┬───┘

After adding S5:
        0
        │
    ┌───┴───┐
    │  S0   │ 100
    │       │
    │  S1   │ 500
    │       │
    │  S5   │ 750 ◄── NEW
    │       │
    │  S2   │ 1000
    │       │
    │  S3   │ 2000
    │       │
    │  S4   │ 3000
    └───┬───┘

Keys between S1 (500) and S5 (750):
- Previously assigned to S2
- Now assigned to S5
- Only small fraction reassigned!
```

**Result:** Only `k/n` keys need reassignment (much better than traditional hashing).

## Removing a Node

**Scenario:** Server S4 fails

**Process:**
1. S4 at position 3000 is removed
2. Keys previously assigned to S4
3. Reassigned to next server clockwise (S0, wrapping around)
4. Only keys mapped to S4 need to move

**Diagram:**
```
Before:
        0
        │
    ┌───┴───┐
    │  S0   │ 100
    │       │
    │  S1   │ 500
    │       │
    │  S2   │ 1000
    │       │
    │  S3   │ 2000
    │       │
    │  S4   │ 3000
    └───┬───┘

After removing S4:
        0
        │
    ┌───┴───┐
    │  S0   │ 100 ◄── Takes S4's keys
    │       │
    │  S1   │ 500
    │       │
    │  S2   │ 1000
    │       │
    │  S3   │ 2000
    │       │
    │  S4   │ ✗ (removed)
    └───┬───┘

Keys between S3 (2000) and S0 (100):
- Previously assigned to S4
- Now assigned to S0
- Only S4's keys reassigned!
```

**Result:** Minimal data movement compared to traditional hashing.

## Virtual Nodes (VNodes)

### Problem with Basic Consistent Hashing

**Issues:**
- Uneven data distribution
- Hot spots when servers cluster together
- Sudden load shift when server removed

**Example:**
```
Without Virtual Nodes:
S1 → Position 10
S2 → Position 50
S3 → Position 90

If S1 fails → All keys go to S2 (overload!)
```

**Diagram:**
```
Basic Consistent Hashing:
        0
        │
    ┌───┴───┐
    │  S1   │ 10
    │       │
    │  S2   │ 50
    │       │
    │  S3   │ 90
    └───┬───┘

S1 fails → All keys → S2 (overload!)
```

### Solution: Virtual Nodes

Each physical server is assigned **multiple positions** (virtual nodes) on the hash ring.

**How it works:**
- Each server hashed multiple times to different positions
- Request assigned to next virtual node clockwise
- Request routed to physical server associated with virtual node

**Example with 3 servers, 3 virtual nodes each:**
```
S1: VNode1 → Position 10
    VNode2 → Position 100
    VNode3 → Position 200

S2: VNode1 → Position 50
    VNode2 → Position 150
    VNode3 → Position 250

S3: VNode1 → Position 90
    VNode2 → Position 190
    VNode3 → Position 290
```

**Diagram:**
```
With Virtual Nodes (3 per server):
        0
        │
    ┌───┴───┐
    │ S1-V1 │ 10
    │       │
    │ S2-V1 │ 50
    │       │
    │ S3-V1 │ 90
    │       │
    │ S1-V2 │ 100
    │       │
    │ S2-V2 │ 150
    │       │
    │ S3-V2 │ 190
    │       │
    │ S1-V3 │ 200
    │       │
    │ S2-V3 │ 250
    │       │
    │ S3-V3 │ 290
    └───┬───┘

If S1 fails:
- Keys distributed among S2 and S3
- More even load distribution
```

**Benefits:**
- More even data distribution
- Better load balancing
- Improved fault tolerance
- Smoother redistribution on failures

## Implementation Overview

### Key Components

1. **Hash Ring:** Stores hash values → server mappings
2. **Virtual Nodes:** Multiple positions per server
3. **Sorted Keys:** Maintains sorted hash values for efficient lookup
4. **Server Set:** Tracks active physical servers

### Operations

**Adding a Server:**
- Generate multiple hash values (virtual nodes)
- Store in hash ring
- Maintain sorted order

**Removing a Server:**
- Delete server's hash values and virtual nodes
- Update sorted keys

**Getting a Server for Key:**
- Hash the key
- Find closest clockwise server using binary search
- Wrap around to first node if necessary

## Real-World Examples

### Amazon DynamoDB
- Uses consistent hashing for partition management
- Virtual nodes for even distribution
- Handles millions of requests efficiently

### Apache Cassandra
- Consistent hashing for data distribution
- Virtual nodes (vnodes) for load balancing
- Scales horizontally with minimal data movement

### Load Balancers
- Consistent hashing for sticky sessions
- Minimal reassignment when servers added/removed
- Better user experience

### Content Delivery Networks (CDNs)
- Consistent hashing for cache distribution
- Efficient cache invalidation
- Better cache hit rates

## Why It Matters

**Scalability:** Efficiently handles dynamic node additions/removals.

**Performance:** Minimizes data movement and cache invalidation.

**Reliability:** Better fault tolerance with virtual nodes.

**User Experience:** Reduces session loss and connection drops.

## Tradeoffs

### Advantages
- ✅ Minimal key reassignment (`k/n` keys)
- ✅ Efficient scaling (add/remove nodes)
- ✅ Better than traditional hashing
- ✅ Works well with virtual nodes

### Considerations
- ⚠️ Uneven distribution without virtual nodes
- ⚠️ Hot spots possible with basic implementation
- ⚠️ Requires sorted data structure for lookups

## Design Considerations

### When to Use Consistent Hashing

**Good for:**
- Distributed caching (Redis, Memcached)
- Load balancing with sticky sessions
- Distributed databases (DynamoDB, Cassandra)
- CDN cache distribution
- Systems with frequent node changes

**Not ideal for:**
- Small, static number of nodes
- Systems requiring strict ordering
- Simple hash-based routing (if nodes don't change)

### Virtual Nodes Configuration

- **More virtual nodes:** Better distribution, more memory
- **Fewer virtual nodes:** Less memory, potential uneven distribution
- **Typical:** 100-200 virtual nodes per physical server

## Interview Hints

When discussing consistent hashing:
1. Explain the problem with traditional hashing (`mod N`)
2. Describe the hash ring concept
3. Explain how keys map to servers (clockwise)
4. Discuss adding/removing nodes
5. Explain virtual nodes and their benefits
6. Compare with traditional hashing
7. Give real-world examples (DynamoDB, Cassandra)

## Conclusion

Consistent hashing is a fundamental technique for building scalable distributed systems. It solves the problem of efficient data distribution in dynamic environments where nodes are frequently added or removed. By using a hash ring and virtual nodes, it ensures minimal data movement and even load distribution, making it essential for modern distributed databases, caches, and load balancers.

