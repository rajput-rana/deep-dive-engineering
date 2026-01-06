# Database Sharding

**Reference:** [AlgoMaster - Sharding](https://algomaster.io/learn/system-design/sharding)

## Summary

Sharding partitions a database horizontally across multiple machines (shards). Each shard contains a subset of data, enabling horizontal scaling when a single database can't handle the load.

## Key Concepts

### Sharding Strategies

1. **Range-Based Sharding**
   ```
   Shard 1: IDs 1-1M
   Shard 2: IDs 1M-2M
   Shard 3: IDs 2M-3M
   ```
   - Simple to implement
   - Can cause hotspots
   - Easy range queries

2. **Hash-Based Sharding**
   ```
   Shard = hash(key) % num_shards
   ```
   - Even distribution
   - Hard to add/remove shards
   - No range queries

3. **Directory-Based Sharding**
   ```
   Lookup: key → shard_id
   ```
   - Flexible
   - Easy rebalancing
   - Lookup table bottleneck

4. **Geographic Sharding**
   ```
   US → Shard 1
   EU → Shard 2
   ```
   - Low latency
   - Data locality
   - Uneven distribution possible

## Why It Matters

**Scalability:** Single database hits limits (connections, I/O, storage). Sharding distributes load.

**Performance:** Smaller databases = faster queries, better indexing.

**Cost:** Commodity hardware instead of expensive vertical scaling.

**Fault Isolation:** One shard failure doesn't affect others.

## Real-World Examples

**Instagram:** Sharded by user ID, handles billions of users.

**Uber:** Sharded by city/region for location-based queries.

**Facebook:** Hash-based sharding by user ID.

**MongoDB:** Built-in automatic sharding.

## Architecture Pattern

```
┌─────────┐
│   App   │
└────┬────┘
     │
     ▼
┌──────────────┐
│Shard Router  │
└──────┬───────┘
       │
   ┌───┴───┬────┬────┐
   │       │    │    │
   ▼       ▼    ▼    ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐
│Sh1 │ │Sh2 │ │Sh3 │ │Sh4 │
└────┘ └────┘ └────┘ └────┘
```

## Tradeoffs

### Advantages
- ✅ Horizontal scaling
- ✅ Better performance (smaller datasets)
- ✅ Fault isolation
- ✅ Cost-effective

### Disadvantages
- ❌ Complex implementation
- ❌ Cross-shard queries expensive
- ❌ Rebalancing difficult
- ❌ Operational complexity

## Challenges

### 1. Cross-Shard Queries
**Problem:** Joins across shards are expensive.

**Solutions:**
- Denormalize data
- Application-level joins
- Avoid cross-shard queries

### 2. Rebalancing
**Problem:** Adding/removing shards requires migration.

**Solutions:**
- Consistent hashing
- Gradual migration
- Double-write during migration

### 3. Hotspots
**Problem:** Uneven distribution overloads some shards.

**Solutions:**
- Better shard key selection
- Monitor and rebalance
- Sub-sharding

### 4. Transactions
**Problem:** ACID transactions across shards are complex.

**Solutions:**
- Two-phase commit (slow)
- Saga pattern (eventual consistency)
- Design to avoid cross-shard transactions

## Shard Key Selection

**Good shard keys:**
- High cardinality
- Even distribution
- Used in queries
- Doesn't change frequently

**Bad shard keys:**
- Low cardinality
- Skewed distribution
- Frequently changing
- Not used in queries

## Design Considerations

### When to Shard
- Single database can't handle load
- Database size approaching limits
- Read replicas not sufficient
- Need geographic distribution

### Alternatives First
1. Read replicas
2. Caching
3. Vertical scaling
4. Database optimization

## Interview Hints

When discussing sharding:
1. Justify need (after other optimizations)
2. Choose shard key
3. Select sharding strategy
4. Address rebalancing
5. Handle cross-shard queries

## Reference

[AlgoMaster - Sharding](https://algomaster.io/learn/system-design/sharding)

