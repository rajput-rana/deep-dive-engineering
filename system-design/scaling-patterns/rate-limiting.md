# Rate Limiting

## Summary

Rate limiting controls the rate of requests sent or received by a system. It prevents abuse, ensures fair resource usage, and protects systems from being overwhelmed by too many requests. Rate limiting is essential for maintaining system stability and providing quality service to all users.

## Key Concepts

### What is Rate Limiting?

Rate limiting restricts the number of requests a client can make within a specific time window.

**Example:**
```
API allows: 100 requests per minute per user

User makes 101st request in same minute
→ Request rejected
→ Returns: 429 Too Many Requests
```

### Why Rate Limiting Matters

**Prevent Abuse:** Stop malicious users from overwhelming the system.

**Fair Resource Usage:** Ensure all users get fair access.

**Cost Control:** Limit API usage to control infrastructure costs.

**System Stability:** Protect backend services from overload.

**Quality of Service:** Maintain performance for legitimate users.

## Rate Limiting Algorithms

### 1. Fixed Window (Simple)

**How it works:**
- Divide time into fixed windows (e.g., 1 minute)
- Count requests in current window
- Reset counter at window start

**Example:**
```
Limit: 100 requests/minute

Window 1 (00:00-00:59): 100 requests allowed
Window 2 (01:00-01:59): Counter resets, 100 requests allowed
```

**Diagram:**
```
Time: 00:00 ──────────── 01:00 ──────────── 02:00
      │                    │                    │
      │ Window 1           │ Window 2           │ Window 3
      │ Counter: 0         │ Counter: 0         │ Counter: 0
      │                    │                    │
      │ Requests: 50       │ Requests: 75       │
      │ Counter: 50        │ Counter: 75        │
```

**Problem:** Burst at window boundary
```
00:59:59 → 100 requests
01:00:00 → Counter resets → 100 more requests
Result: 200 requests in 2 seconds!
```

### 2. Sliding Window Log

**How it works:**
- Maintain log of request timestamps
- Count requests within sliding window
- Remove old entries outside window

**Example:**
```
Limit: 100 requests/minute
Current time: 01:00:30

Log entries:
- 00:59:45 (within window)
- 00:59:50 (within window)
- ...
- 01:00:25 (within window)

Count: 95 requests
Allow: Yes (under limit)
```

**Diagram:**
```
Sliding Window (1 minute):
         │
    ┌────┴────┐
    │  Window │
    └────┬────┘
         │
   00:30 │ 01:30
    ─────┼─────
         │
    Requests in window: 45
    Limit: 100
    Status: Allow
```

**Advantages:**
- ✅ Accurate rate limiting
- ✅ No burst at boundaries

**Disadvantages:**
- ❌ Memory intensive (stores all timestamps)
- ❌ More complex

### 3. Sliding Window Counter

**How it works:**
- Divide window into smaller sub-windows
- Count requests in each sub-window
- Calculate weighted average for current window

**Example:**
```
1-minute window divided into 6 sub-windows (10 seconds each)

Current time: 01:00:35
Sub-windows:
- 00:50-01:00: 20 requests
- 01:00-01:10: 15 requests (current)

Weighted count: (20 × 0.5) + 15 = 25 requests
Limit: 100
Status: Allow
```

**Advantages:**
- ✅ More memory efficient than sliding log
- ✅ Better than fixed window (reduces bursts)

**Disadvantages:**
- ❌ Less accurate than sliding log
- ❌ More complex than fixed window

### 4. Token Bucket

**How it works:**
- Bucket has capacity (max tokens)
- Tokens added at fixed rate
- Request consumes token
- If bucket empty, request rejected

**Example:**
```
Bucket capacity: 100 tokens
Refill rate: 10 tokens/second

Request arrives:
- If tokens available → Consume token, allow
- If bucket empty → Reject
```

**Diagram:**
```
Token Bucket:
┌─────────────┐
│   Bucket    │
│  Capacity:  │
│    100      │
│             │
│ Tokens: 75  │ ◄── Refill: +10/sec
└──────┬──────┘
       │
   Request ──┐
       │     │
       ▼     ▼
   Consume 1 token
   Tokens: 74
```

**Advantages:**
- ✅ Allows bursts (if tokens available)
- ✅ Smooth rate limiting
- ✅ Memory efficient

**Disadvantages:**
- ❌ More complex than fixed window

### 5. Leaky Bucket

**How it works:**
- Bucket has capacity
- Requests added to bucket
- Requests processed at fixed rate
- If bucket full, request rejected

**Example:**
```
Bucket capacity: 100 requests
Processing rate: 10 requests/second

Request arrives:
- If bucket has space → Add to bucket
- If bucket full → Reject
```

**Diagram:**
```
Leaky Bucket:
┌─────────────┐
│   Bucket    │
│  Capacity:  │
│    100      │
│             │
│ Requests: 50│
└──────┬──────┘
       │
       │ Leak: 10 req/sec
       ▼
   Process requests
```

**Advantages:**
- ✅ Smooth output rate
- ✅ Prevents bursts

**Disadvantages:**
- ❌ Doesn't allow bursts (unlike token bucket)

## Rate Limiting Strategies

### 1. Per-User Rate Limiting

Limit requests per user/API key.

**Example:**
```
User A: 100 requests/minute
User B: 100 requests/minute
```

**Use Case:** API keys, authenticated users

### 2. Per-IP Rate Limiting

Limit requests per IP address.

**Example:**
```
IP 192.168.1.100: 50 requests/minute
IP 192.168.1.101: 50 requests/minute
```

**Use Case:** Public APIs, DDoS protection

### 3. Global Rate Limiting

Limit total requests across all clients.

**Example:**
```
Total API: 10,000 requests/minute
```

**Use Case:** Protect backend services

### 4. Tiered Rate Limiting

Different limits for different user tiers.

**Example:**
```
Free tier: 100 requests/minute
Premium tier: 1,000 requests/minute
Enterprise: Unlimited
```

## Implementation Approaches

### 1. In-Memory (Single Server)

**How:**
- Store counters in memory (Redis, Memcached)
- Fast lookups
- Simple implementation

**Limitation:** Doesn't work across multiple servers

**Example:**
```python
# Redis
redis.incr(f"rate_limit:{user_id}:{window}")
if count > limit:
    return 429
```

### 2. Distributed (Multiple Servers)

**How:**
- Use distributed cache (Redis Cluster)
- Shared state across servers
- Consistent rate limiting

**Example:**
```
Server 1 ──┐
           ├──► Redis Cluster
Server 2 ──┤    (Shared counters)
           │
Server 3 ──┘
```

### 3. Client-Side Rate Limiting

**How:**
- Client tracks its own rate
- Reduces server load
- Not secure (can be bypassed)

**Use Case:** Good user experience, but not for security

## Rate Limit Headers

**Standard Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1609459200
```

**429 Response:**
```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1609459200
Retry-After: 60
```

## Real-World Examples

### Twitter API
- Rate limits per endpoint
- Different limits for different operations
- Headers show remaining requests

### Stripe API
- Rate limits per API key
- Different limits for test/live mode
- 429 responses with retry information

### GitHub API
- Rate limits per user/IP
- OAuth apps have higher limits
- Headers indicate rate limit status

### Cloudflare
- DDoS protection via rate limiting
- Per-IP limits
- Configurable thresholds

## Design Considerations

### Choosing an Algorithm

**Fixed Window:**
- Simple, memory efficient
- Good for low-precision needs
- Suffers from boundary bursts

**Sliding Window:**
- Accurate, smooth limiting
- More memory intensive
- Good for precise control

**Token Bucket:**
- Allows bursts
- Smooth rate limiting
- Good for variable traffic

**Leaky Bucket:**
- Smooth output rate
- No bursts allowed
- Good for constant processing

### Rate Limit Configuration

**Factors to consider:**
- Expected traffic patterns
- Backend capacity
- User tiers
- Cost constraints

**Example Configuration:**
```yaml
rate_limits:
  free_tier:
    limit: 100
    window: 1 minute
  premium_tier:
    limit: 1000
    window: 1 minute
  enterprise:
    limit: unlimited
```

### Handling Rate Limit Exceeded

**Strategies:**
1. Return 429 with Retry-After header
2. Queue request for later processing
3. Graceful degradation
4. Notify user of limit

## Interview Hints

When discussing rate limiting:
1. Explain why it's needed (abuse prevention, stability)
2. Describe different algorithms (fixed window, sliding window, token bucket)
3. Discuss tradeoffs (accuracy vs memory)
4. Address distributed rate limiting
5. Explain rate limit headers
6. Give real-world examples

## Conclusion

Rate limiting is essential for protecting systems from abuse and ensuring fair resource usage. By choosing the right algorithm (fixed window, sliding window, token bucket) and implementing it correctly (distributed caching, proper headers), you can maintain system stability while providing quality service to all users.

