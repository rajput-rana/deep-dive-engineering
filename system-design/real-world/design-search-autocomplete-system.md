# Design a Search Autocomplete System

**Reference:** [AlgoMaster - Design Search Autocomplete System](https://algomaster.io/learn/system-design/design-search-autocomplete-system)

## Summary

Design a system like Google's search suggestions that provides real-time autocomplete suggestions as users type. This requires handling millions of queries, low latency, and intelligent ranking.

## Requirements

### Functional Requirements
- Return top K suggestions as user types
- Suggestions update with each keystroke
- Handle typos and partial matches
- Support multiple languages

### Non-Functional Requirements
- Response time < 100ms
- Handle millions of queries/day
- High availability
- Suggestions ranked by relevance

## Capacity Estimation

**Assumptions:**
- 10M daily active users
- Average 10 searches/user/day
- 100M searches/day
- Average query length: 20 characters

**Traffic:**
- QPS: 100M / 86400 = ~1,200 QPS
- Peak: 3x average = 3,600 QPS

**Storage:**
- 1B unique queries
- Average 20 chars = 20 bytes
- Total: ~20GB (compressed)

## High-Level Design

```
┌─────────┐
│ Client  │
└────┬────┘
     │
     ▼
┌──────────────┐
│ API Gateway  │
└──────┬───────┘
       │
   ┌───┴───┬────────┐
   │       │        │
   ▼       ▼        ▼
┌────┐ ┌────┐  ┌────┐
│Trie│ │Rank│  │Cache│
│    │ │Svc │  │     │
└────┘ └────┘ └────┘
```

## Key Components

### 1. Trie Data Structure

**Why Trie:**
- Fast prefix matching
- O(m) search time (m = prefix length)
- Efficient memory usage

**Structure:**
```
        root
       /  |  \
      t   a   h
     /    |    \
    o     u     e
   /      |      \
  p       t       l
 /        |        \
s        o         l
         |
         c
         |
         o
```

### 2. Ranking Service

**Ranking Factors:**
- Query frequency
- Recency
- User location
- User history
- Click-through rate

**Algorithm:**
- Weighted scoring
- Machine learning models
- A/B testing for improvement

### 3. Caching Strategy

- Cache popular prefixes
- Redis for hot queries
- TTL: 1-24 hours
- Cache top 10 suggestions per prefix

## Detailed Design

### Query Flow

```
1. User types "face"
2. Query Trie for "face" prefix
3. Get all matching queries
4. Rank by frequency/relevance
5. Return top K suggestions
6. Cache results
```

### Data Collection

```
1. Log all search queries
2. Aggregate by query string
3. Calculate frequency, CTR
4. Update Trie periodically
5. Update ranking model
```

## Scaling Strategies

### Trie Optimization

**Challenges:**
- Large memory footprint
- Slow updates

**Solutions:**
1. **Compressed Trie:** Reduce memory
2. **Sharding:** Split by first character
3. **Read Replicas:** Scale reads

### Caching

- Cache top prefixes (80/20 rule)
- CDN for global distribution
- In-memory cache per server

### Database

- Store query statistics
- Update asynchronously
- Batch updates

## Tradeoffs

### Trie vs Database

**Trie:**
- ✅ Fast lookups
- ✅ Prefix matching
- ❌ Memory intensive
- ❌ Slow updates

**Database:**
- ✅ Flexible queries
- ✅ Easy updates
- ❌ Slower lookups
- ❌ Complex prefix queries

**Hybrid:** Use Trie for hot data, database for cold data.

### Real-time vs Batch Updates

**Real-time:**
- ✅ Always fresh
- ❌ High cost
- ❌ Complex

**Batch Updates:**
- ✅ Cost-effective
- ✅ Simpler
- ❌ Stale data

**Recommendation:** Batch updates (hourly/daily) with real-time for trending.

## Interview Hints

When designing autocomplete:
1. Clarify requirements (K suggestions, languages, typos)
2. Estimate capacity (QPS, storage)
3. Choose data structure (Trie)
4. Design ranking algorithm
5. Discuss caching strategy
6. Address scaling (sharding, updates)

## Reference

[AlgoMaster - Design Search Autocomplete System](https://algomaster.io/learn/system-design/design-search-autocomplete-system)

