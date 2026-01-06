# Caching

**Reference:** [AlgoMaster - Caching](https://algomaster.io/learn/system-design/caching)

## Problem / Concept Overview

Caching stores frequently accessed data in fast memory to reduce latency and database load. It's one of the most effective performance optimizations—often providing 10-100x speedup.

## Key Ideas

### Cache Patterns

1. **Cache-Aside (Lazy Loading)**
   ```
   Read: Check cache → If miss, read DB → Store in cache
   Write: Write to DB → Invalidate cache
   ```
   - Simple, works with any cache
   - Cache miss penalty on first request

2. **Write-Through**
   ```
   Write: Write to cache → Write to DB (synchronously)
   ```
   - Cache always consistent
   - Higher write latency

3. **Write-Back (Write-Behind)**
   ```
   Write: Write to cache → Write to DB asynchronously
   ```
   - Fast writes
   - Risk of data loss if cache fails

4. **Refresh-Ahead**
   ```
   Proactively refresh cache before expiration
   ```
   - Reduces cache misses
   - Wastes resources if data not accessed

## Cache Levels

```
┌─────────┐
│ Browser │  ← Client-side cache
└────┬────┘
     │
     ▼
┌─────────┐
│   CDN   │  ← Edge cache
└────┬────┘
     │
     ▼
┌─────────┐
│  App    │  ← Application cache
└────┬────┘
     │
     ▼
┌─────────┐
│Database │
└─────────┘
```

## Why It Matters

**Performance:** Memory access is 100x faster than disk, 1000x faster than network.

**Cost Reduction:** Reduce database load → fewer database instances needed.

**Scalability:** Cache handles read traffic, databases handle writes.

**User Experience:** Faster page loads improve engagement and conversions.

## Real-World Examples

**Facebook:** Memcached handles billions of requests/day, reduces database load by 99%.

**Twitter:** Redis caches timelines, reducing database queries dramatically.

**Amazon:** Multi-layer caching (browser, CDN, application) for product pages.

**Netflix:** Caches video metadata and recommendations globally.

## Tradeoffs

### In-Memory Cache (Redis, Memcached)
- **Pros:** Extremely fast, simple
- **Cons:** Limited size, data lost on restart

### Distributed Cache
- **Pros:** Scales horizontally, fault-tolerant
- **Cons:** Network latency, consistency challenges

### Cache-Aside vs Write-Through
- **Cache-Aside:** Better for read-heavy, simpler
- **Write-Through:** Better consistency, higher write cost

## Cache Invalidation Strategies

1. **TTL (Time-To-Live)**
   - Simple, automatic expiration
   - May serve stale data

2. **Explicit Invalidation**
   - Invalidate on updates
   - Requires tracking what to invalidate

3. **Versioning**
   - Include version in cache key
   - Update version on change
   - Old versions expire naturally

## Cache Replacement Policies

When cache is full, which items to evict?

- **LRU (Least Recently Used):** Evict least recently accessed
- **LFU (Least Frequently Used):** Evict least frequently accessed
- **FIFO (First In First Out):** Simple but not optimal
- **Random:** Simple but unpredictable

**LRU is most common**—works well for temporal locality.

## Design Considerations

### What to Cache
- ✅ Frequently accessed data
- ✅ Expensive computations
- ✅ Database query results
- ✅ Session data
- ❌ Frequently changing data
- ❌ User-specific sensitive data (carefully)

### Cache Size
- Too small: High miss rate
- Too large: Memory waste, slower eviction
- Rule of thumb: 20% of working set

### Cache Warming
- Pre-populate cache on startup
- Reduces cold start penalty

## Common Pitfalls

1. **Cache Stampede:** Many requests miss cache simultaneously
   - Solution: Lock on miss, single request fetches

2. **Thundering Herd:** All requests hit expired cache
   - Solution: Stagger expiration times

3. **Cache Penetration:** Queries for non-existent data
   - Solution: Cache negative results with short TTL

4. **Cache Avalanche:** Many keys expire simultaneously
   - Solution: Randomize TTL values

## Monitoring

Key metrics to track:
- **Hit Rate:** Percentage of requests served from cache (target: >80%)
- **Miss Rate:** Cache misses per second
- **Latency:** Cache operation time
- **Memory Usage:** Cache size and eviction rate

## Interview Tips

When discussing caching:
1. Identify cacheable data (read-heavy, expensive queries)
2. Choose cache location (browser, CDN, application, database)
3. Select eviction policy (LRU most common)
4. Discuss invalidation strategy
5. Address consistency vs performance tradeoff

