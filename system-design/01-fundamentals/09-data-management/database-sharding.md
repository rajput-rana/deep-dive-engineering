# Database Sharding

// (// 

## Problem / Concept Overview

Sharding partitions a database into smaller, independent pieces (shards) distributed across multiple servers. When a single database can't handle the load, sharding enables horizontal scaling.

## Key Ideas

### Sharding Strategies

1. **Range-Based Sharding**
   ```
   Shard 1: User IDs 1-1M
   Shard 2: User IDs 1M-2M
   Shard 3: User IDs 2M-3M
   ```
   - Simple to implement
   - Can cause hotspots (uneven distribution)

2. **Hash-Based Sharding**
   ```
   Shard = hash(user_id) % num_shards
   ```
   - Even distribution
   - Hard to add/remove shards (requires rehashing)

3. **Directory-Based Sharding**
   ```
   Lookup table: user_id → shard_id
   ```
   - Flexible, easy to rebalance
   - Lookup table becomes bottleneck

4. **Geographic Sharding**
   ```
   US users → Shard 1
   EU users → Shard 2
   ```
   - Low latency (data closer to users)
   - Uneven distribution possible

## Architecture Pattern

```
┌─────────┐
│  App    │
└────┬────┘
     │
     ▼
┌──────────────┐
│ Shard Router │
└──────┬───────┘
       │
   ┌───┴───┬────┬────┐
   │       │    │    │
   ▼       ▼    ▼    ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐
│Sh1 │ │Sh2 │ │Sh3 │ │Sh4 │
└────┘ └────┘ └────┘ └────┘
```

## Why It Matters

**Scalability:** Single database hits limits (connection pool, I/O, storage). Sharding distributes load.

**Performance:** Smaller databases = faster queries, better indexing.

**Cost:** Use commodity hardware instead of expensive vertical scaling.

**Fault Isolation:** One shard failure doesn't affect others.

## Real-World Examples

**Instagram:** Sharded by user ID, each shard handles millions of users.

**Uber:** Sharded by city/region for location-based queries.

**Facebook:** Sharded by user ID hash, handles billions of users.

**MongoDB:** Built-in sharding support with automatic balancing.

## Tradeoffs

### Advantages
- ✅ Horizontal scaling
- ✅ Better performance (smaller datasets)
- ✅ Fault isolation
- ✅ Cost-effective (commodity hardware)

### Disadvantages
- ❌ Complex to implement
- ❌ Cross-shard queries expensive/impossible
- ❌ Rebalancing difficult
- ❌ Operational complexity

## Challenges

### 1. Cross-Shard Queries
**Problem:** Joins across shards are expensive.

**Solutions:**
- Denormalize data (duplicate across shards)
- Application-level joins (fetch from multiple shards, join in app)
- Avoid cross-shard queries in design

### 2. Rebalancing
**Problem:** Adding/removing shards requires data migration.

**Solutions:**
- Use consistent hashing (minimal data movement)
- Gradual migration
- Double-write during migration

### 3. Hotspots
**Problem:** Uneven distribution causes some shards to be overloaded.

**Solutions:**
- Better shard key selection
- Monitor and rebalance
- Sub-sharding (shard within shard)

### 4. Transactions
**Problem:** ACID transactions across shards are complex.

**Solutions:**
- Two-phase commit (slow, complex)
- Saga pattern (eventual consistency)
- Design to avoid cross-shard transactions

## Shard Key Selection

**Good shard keys:**
- High cardinality (many unique values)
- Even distribution
- Used in queries (enables single-shard queries)
- Doesn't change frequently

**Bad shard keys:**
- Low cardinality (few unique values)
- Skewed distribution
- Frequently changing
- Not used in queries

**Examples:**
- ✅ User ID (good)
- ✅ Geographic region (good for location-based apps)
- ❌ Status field (bad - few values)
- ❌ Timestamp (bad - creates hotspots)

## Design Considerations

### When to Shard
- Single database can't handle load
- Database size approaching limits
- Read replicas not sufficient
- Need geographic distribution

### Alternatives to Consider First
1. **Read Replicas:** Scale reads, not writes
2. **Caching:** Reduce database load
3. **Vertical Scaling:** Add more power (limited)
4. **Database Optimization:** Indexing, query optimization

### Sharding vs Partitioning
- **Partitioning:** Within single database (logical separation)
- **Sharding:** Across multiple databases (physical separation)
- Sharding is partitioning + distribution

## Monitoring

Key metrics:
- **Shard Size:** Monitor growth, plan rebalancing
- **Query Distribution:** Ensure even load
- **Cross-Shard Queries:** Minimize these
- **Replication Lag:** If using replicas per shard

## Interview Tips

When discussing sharding:
1. Justify why sharding is needed (after other optimizations)
2. Choose appropriate shard key
3. Discuss rebalancing strategy
4. Address cross-shard query challenges
5. Consider alternatives (read replicas, caching)

