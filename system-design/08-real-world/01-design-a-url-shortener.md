# Design a URL Shortener

// (// 

## Summary

Design a system like bit.ly or TinyURL that converts long URLs into short, shareable links. This is a classic system design problem that tests understanding of scalability, hashing, and database design.

## Requirements

### Functional Requirements
- Shorten long URLs
- Redirect short URLs to original
- Custom URLs (optional)
- Analytics (click tracking)
- URL expiration (optional)

### Non-Functional Requirements
- High availability
- Low latency redirects
- Scalability (billions of URLs)
- 6-7 character short URLs

## Capacity Estimation

**Assumptions:**
- 100M URLs/month
- 10:1 read/write ratio
- URLs stored for 5 years

**Storage:**
- 100M × 12 × 5 = 6B URLs
- ~500 bytes per URL = 3TB storage

**Traffic:**
- Writes: 100M/30/24/3600 = ~39 URLs/sec
- Reads: 390 URLs/sec

## High-Level Design

```
┌─────────┐
│ Client  │
└────┬────┘
     │
     ▼
┌──────────────┐
│ API Server   │
└──────┬───────┘
       │
   ┌───┴───┬────────┐
   │       │        │
   ▼       ▼        ▼
┌────┐ ┌────┐  ┌────┐
│Hash│ │DB  │  │Cache│
│Svc │ │    │  │     │
└────┘ └────┘ └────┘
```

## Key Components

### 1. URL Encoding

**Base62 Encoding:**
- Characters: a-z, A-Z, 0-9
- 6 characters = 62^6 = 56.8 billion URLs
- Simple, URL-safe

**Hash Function:**
- MD5/SHA256 of long URL
- Take first 6 characters
- Handle collisions (append counter)

### 2. Database Schema

```sql
short_url (PK)
long_url
created_at
expires_at
user_id
click_count
```

### 3. Caching Strategy

- Cache popular URLs (80/20 rule)
- Redis for hot URLs
- TTL based on popularity

## Detailed Design

### Shortening Flow

```
1. Client sends long URL
2. Check if already exists (hash lookup)
3. If exists, return existing short URL
4. If not, generate new short URL
5. Store in database
6. Return short URL
```

### Redirect Flow

```
1. Client requests short URL
2. Check cache first
3. If cache miss, query database
4. Update click count
5. Return 301 redirect to long URL
6. Cache for future requests
```

## Scaling Strategies

### Database Sharding

**Shard by short URL:**
- Hash short URL → shard ID
- Even distribution
- No cross-shard queries

### Caching

- Cache 20% hottest URLs
- Reduces database load by 80%
- Use CDN for global distribution

### Load Balancing

- Multiple API servers
- Round-robin or least connections
- Health checks

## Tradeoffs

### Hash Collisions

**Problem:** Two URLs might hash to same short URL.

**Solutions:**
1. Check database before storing
2. If collision, append counter
3. Use longer hash (7-8 chars)

### Database Choice

**SQL:**
- ✅ ACID transactions
- ✅ Easy analytics
- ❌ Scaling challenges

**NoSQL:**
- ✅ Better scalability
- ✅ Flexible schema
- ❌ Eventual consistency

**Recommendation:** Start with SQL, migrate to NoSQL at scale.

## Interview Hints

When designing URL shortener:
1. Clarify requirements (custom URLs, expiration, analytics)
2. Estimate capacity (storage, traffic)
3. Design encoding scheme (Base62)
4. Handle collisions
5. Discuss scaling (sharding, caching)
6. Address edge cases (malicious URLs, rate limiting)
// (// 

