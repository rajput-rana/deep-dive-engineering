# 🛡️ Resilience Patterns - Expert Guide

<div align="center">

**Master resilience: Circuit Breaker, Retry, Rate Limiter, and Bulkhead patterns**

[![Resilience](https://img.shields.io/badge/Resilience-Fault%20Tolerance-blue?style=for-the-badge)](./)
[![Circuit Breaker](https://img.shields.io/badge/Circuit%20Breaker-Protection-green?style=for-the-badge)](./)
[![Retry](https://img.shields.io/badge/Retry-Resilience-orange?style=for-the-badge)](./)

*Comprehensive guide to resilience patterns: building fault-tolerant distributed systems*

</div>

---

## 🎯 Resilience Fundamentals

<div align="center">

### What is Resilience?

**Resilience is the ability of a system to handle failures gracefully and continue operating despite adverse conditions.**

### Key Resilience Patterns

| Pattern | Purpose | Use Case |
|:---:|:---:|:---:|
| **🔌 Circuit Breaker** | Prevent cascading failures | Failing downstream services |
| **🔄 Retry** | Handle transient failures | Network timeouts, temporary errors |
| **🚦 Rate Limiter** | Control request rates | API throttling, resource protection |
| **🚧 Bulkhead** | Isolate failures | Prevent resource exhaustion |

**Mental Model:** Think of resilience patterns like safety systems in a building - Circuit Breaker is like a fuse that trips to prevent damage, Retry is like trying the door again, Rate Limiter is like a turnstile controlling flow, and Bulkhead is like fire doors isolating sections.

</div>

---

## 🔌 Circuit Breaker Pattern

<div align="center">

### Q1: What is the Circuit Breaker pattern?

**A:** Circuit Breaker is a design pattern that prevents cascading failures by stopping requests to a failing service and allowing it to recover.

**How It Works:**

1. **Closed State:** Normal operation, requests pass through
2. **Open State:** Service failing, requests fail fast
3. **Half-Open State:** Testing if service recovered

**State Transitions:**
```
Closed → (failure threshold) → Open → (timeout) → Half-Open
  ↑                                                      ↓
  └────────────────── (success) ───────────────────────┘
```

**Benefits:**
- ✅ Prevents cascading failures
- ✅ Fast failure (no waiting for timeouts)
- ✅ Allows service recovery
- ✅ Protects downstream services

---

### Q2: How does Circuit Breaker work internally?

**A:**

**Key Components:**

1. **Failure Threshold:**
   - Number of failures before opening
   - Example: 5 failures in 60 seconds

2. **Timeout:**
   - How long to stay open
   - Example: 30 seconds

3. **Success Threshold:**
   - Successes needed to close
   - Example: 2 consecutive successes

**Example Implementation:**
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60, success_threshold=2):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        self.failure_count = 0
        self.success_count = 0
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = None
    
    def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
                self.success_count = 0
            else:
                raise CircuitBreakerOpenException("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
    
    def on_success(self):
        if self.state == 'HALF_OPEN':
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = 'CLOSED'
                self.failure_count = 0
        elif self.state == 'CLOSED':
            self.failure_count = 0
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
        elif self.state == 'HALF_OPEN':
            self.state = 'OPEN'
```

---

### Q3: What are the Circuit Breaker states?

**A:**

**Three States:**

1. **CLOSED (Normal):**
   - Requests pass through
   - Monitoring failures
   - Opens on threshold

2. **OPEN (Failing):**
   - Requests fail immediately
   - No calls to downstream
   - Auto-transitions after timeout

3. **HALF_OPEN (Testing):**
   - Testing recovery
   - Limited requests allowed
   - Closes on success, opens on failure

**State Diagram:**
```
         ┌─────────┐
         │ CLOSED  │ ← Normal operation
         └────┬────┘
              │ (failure threshold)
              ↓
         ┌─────────┐
         │  OPEN   │ ← Failing fast
         └────┬────┘
              │ (timeout)
              ↓
         ┌──────────┐
         │ HALF_OPEN│ ← Testing recovery
         └────┬─────┘
              │
    ┌─────────┴─────────┐
    │                   │
(success)          (failure)
    │                   │
    ↓                   ↓
CLOSED               OPEN
```

---

### Q4: How to configure Circuit Breaker?

**A:**

**Configuration Parameters:**

| Parameter | Description | Typical Value |
|:---:|:---:|:---:|
| **failureThreshold** | Failures before opening | 5 |
| **timeout** | Time in OPEN state (seconds) | 60 |
| **successThreshold** | Successes to close | 2 |
| **monitoringWindow** | Time window for failures | 60 seconds |
| **halfOpenMaxCalls** | Max calls in HALF_OPEN | 3 |

**Example Configuration:**
```yaml
circuitBreaker:
  failureThreshold: 5
  timeout: 60s
  successThreshold: 2
  monitoringWindow: 60s
  halfOpenMaxCalls: 3
```

**Resilience4j Example:**
```java
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50)  // 50% failure rate
    .waitDurationInOpenState(Duration.ofSeconds(60))
    .slidingWindowSize(10)  // Last 10 calls
    .minimumNumberOfCalls(5)  // Min calls before calculating
    .build();

CircuitBreaker circuitBreaker = CircuitBreaker.of("service", config);
```

---

### Q5: What are Circuit Breaker use cases?

**A:**

**Common Use Cases:**

1. **External API Calls:**
   - Third-party services
   - Prevent cascading failures
   - Fast failure

2. **Database Connections:**
   - Database failures
   - Connection pool exhaustion
   - Timeout protection

3. **Microservices:**
   - Service-to-service calls
   - Network failures
   - Service degradation

4. **Resource-Intensive Operations:**
   - Expensive computations
   - External dependencies
   - Rate limit protection

**Example - API Call:**
```python
circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

@circuit_breaker.call
def call_external_api(url):
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()

# Usage
try:
    data = call_external_api("https://api.example.com/data")
except CircuitBreakerOpenException:
    # Return cached data or default
    data = get_cached_data()
```

---

### Q6: What are Circuit Breaker best practices?

**A:**

**Best Practices:**

1. **Tune Thresholds:**
   - Based on service characteristics
   - Monitor and adjust
   - Balance between protection and availability

2. **Monitor Metrics:**
   - Failure rates
   - State transitions
   - Response times

3. **Fallback Strategies:**
   - Return cached data
   - Default values
   - Graceful degradation

4. **Logging:**
   - Log state transitions
   - Track failures
   - Alert on opens

5. **Testing:**
   - Test all states
   - Simulate failures
   - Verify recovery

**Example - With Fallback:**
```python
def get_user_data(user_id):
    try:
        return circuit_breaker.call(fetch_from_api, user_id)
    except CircuitBreakerOpenException:
        # Fallback to cache
        return get_cached_user_data(user_id)
    except Exception as e:
        # Other errors
        logger.error(f"Error fetching user: {e}")
        raise
```

---

## 🔄 Retry Pattern

<div align="center">

### Q7: What is the Retry pattern?

**A:** Retry pattern automatically retries failed operations, typically with exponential backoff, to handle transient failures.

**Why Retry:**

1. **Transient Failures:** Temporary network issues
2. **Temporary Unavailability:** Service restarting
3. **Rate Limiting:** Temporary throttling
4. **Timeout Errors:** Slow responses

**Key Concepts:**
- **Max Retries:** Maximum retry attempts
- **Backoff Strategy:** Delay between retries
- **Retryable Errors:** Which errors to retry

---

### Q8: What are retry strategies?

**A:**

**Retry Strategies:**

1. **Fixed Delay:**
   - Constant delay between retries
   - Simple but inefficient
   - Example: Wait 1 second between retries

2. **Exponential Backoff:**
   - Delay increases exponentially
   - Prevents overwhelming service
   - Example: 1s, 2s, 4s, 8s

3. **Linear Backoff:**
   - Delay increases linearly
   - Moderate approach
   - Example: 1s, 2s, 3s, 4s

4. **Jitter:**
   - Random variation in delay
   - Prevents thundering herd
   - Example: Exponential + random jitter

**Example - Exponential Backoff:**
```python
import time
import random

def exponential_backoff(base_delay=1, max_delay=60, max_retries=5):
    for attempt in range(max_retries):
        delay = min(base_delay * (2 ** attempt), max_delay)
        # Add jitter
        jitter = random.uniform(0, delay * 0.1)
        time.sleep(delay + jitter)
        yield attempt
```

---

### Q9: How to implement Retry pattern?

**A:**

**Implementation Approaches:**

1. **Simple Retry:**
```python
def retry(func, max_retries=3, delay=1):
    for attempt in range(max_retries):
        try:
            return func()
        except RetryableException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(delay)
    raise MaxRetriesExceeded()
```

2. **Exponential Backoff Retry:**
```python
def retry_with_backoff(func, max_retries=5, base_delay=1):
    for attempt in range(max_retries):
        try:
            return func()
        except RetryableException as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
    raise MaxRetriesExceeded()
```

3. **Decorator Pattern:**
```python
def retry(max_retries=3, backoff_strategy='exponential'):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RetryableException as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = calculate_delay(attempt, backoff_strategy)
                    time.sleep(delay)
            raise MaxRetriesExceeded()
        return wrapper
    return decorator

@retry(max_retries=5, backoff_strategy='exponential')
def call_api():
    response = requests.get("https://api.example.com")
    response.raise_for_status()
    return response.json()
```

---

### Q10: What errors should be retried?

**A:**

**Retryable Errors:**

1. **Network Errors:**
   - Connection timeout
   - Connection refused
   - DNS resolution failure

2. **HTTP Errors:**
   - 429 (Too Many Requests)
   - 500 (Internal Server Error)
   - 502 (Bad Gateway)
   - 503 (Service Unavailable)
   - 504 (Gateway Timeout)

3. **Transient Errors:**
   - Temporary unavailability
   - Service restarting
   - Rate limiting

**Non-Retryable Errors:**

1. **Client Errors:**
   - 400 (Bad Request)
   - 401 (Unauthorized)
   - 403 (Forbidden)
   - 404 (Not Found)

2. **Permanent Errors:**
   - Invalid credentials
   - Malformed request
   - Business logic errors

**Example:**
```python
def is_retryable_error(error):
    if isinstance(error, requests.exceptions.Timeout):
        return True
    if isinstance(error, requests.exceptions.ConnectionError):
        return True
    if hasattr(error, 'response'):
        status = error.response.status_code
        return status in [429, 500, 502, 503, 504]
    return False
```

---

### Q11: What is idempotency in retries?

**A:**

**Idempotency:**

- Operation can be safely retried
- Multiple calls have same effect as one
- Critical for retry patterns

**Idempotent Operations:**
- GET requests
- PUT requests (with same data)
- DELETE requests

**Non-Idempotent Operations:**
- POST requests (create)
- PATCH requests (partial update)

**Making Operations Idempotent:**

1. **Idempotency Keys:**
```python
def create_order(order_data, idempotency_key):
    # Check if order already exists
    existing = get_order_by_idempotency_key(idempotency_key)
    if existing:
        return existing  # Return existing order
    
    # Create new order
    return create_new_order(order_data, idempotency_key)
```

2. **Conditional Updates:**
```python
def update_user(user_id, data, version):
    # Only update if version matches
    user = get_user(user_id)
    if user.version != version:
        raise ConflictError("Version mismatch")
    
    return update_user_data(user_id, data, version + 1)
```

---

### Q12: What are retry best practices?

**A:**

**Best Practices:**

1. **Use Exponential Backoff:**
   - Prevents overwhelming service
   - Reduces load on failing service

2. **Add Jitter:**
   - Prevents thundering herd
   - Randomizes retry timing

3. **Set Max Retries:**
   - Avoid infinite retries
   - Fail fast after threshold

4. **Retry Only Transient Errors:**
   - Don't retry client errors
   - Don't retry permanent failures

5. **Implement Timeout:**
   - Total retry timeout
   - Prevent long waits

6. **Log Retries:**
   - Track retry attempts
   - Monitor retry patterns

**Example - Complete Retry Implementation:**
```python
class RetryPolicy:
    def __init__(self, max_retries=5, base_delay=1, max_delay=60, 
                 timeout=30, jitter=True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.timeout = timeout
        self.jitter = jitter
    
    def execute(self, func, *args, **kwargs):
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            # Check timeout
            if time.time() - start_time > self.timeout:
                raise RetryTimeoutError("Retry timeout exceeded")
            
            try:
                return func(*args, **kwargs)
            except RetryableException as e:
                if attempt == self.max_retries - 1:
                    raise MaxRetriesExceeded() from e
                
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                if self.jitter:
                    delay += random.uniform(0, delay * 0.1)
                
                time.sleep(delay)
                logger.info(f"Retry attempt {attempt + 1}/{self.max_retries}")
        
        raise MaxRetriesExceeded()
```

---

## 🚦 Rate Limiter Pattern

<div align="center">

### Q13: What is Rate Limiting?

**A:** Rate limiting controls the rate of requests to prevent overwhelming services and ensure fair resource usage.

**Why Rate Limit:**

1. **Protect Services:** Prevent overload
2. **Fair Usage:** Ensure fair resource distribution
3. **Cost Control:** Limit API costs
4. **Security:** Prevent abuse and DDoS

**Note:** See [Rate Limiting](./03-rate-limiting.md) for detailed coverage.

**Quick Reference:**

| Algorithm | Description | Use Case |
|:---:|:---:|:---:|
| **Token Bucket** | Tokens added at fixed rate | Burst handling |
| **Leaky Bucket** | Fixed output rate | Smooth traffic |
| **Fixed Window** | Requests per time window | Simple limiting |
| **Sliding Window** | Rolling time window | Accurate limiting |

---

### Q14: How does Rate Limiter work with Resilience?

**A:**

**Rate Limiter + Resilience:**

1. **Prevent Overload:**
   - Limit requests to failing service
   - Reduce load during recovery
   - Prevent cascading failures

2. **Graceful Degradation:**
   - Return 429 (Too Many Requests)
   - Queue requests
   - Retry with backoff

3. **Circuit Breaker Integration:**
   - Rate limit before circuit breaker
   - Reduce failures
   - Faster recovery

**Example:**
```python
rate_limiter = RateLimiter(requests_per_second=10)
circuit_breaker = CircuitBreaker()

def resilient_call(func):
    # Rate limit first
    if not rate_limiter.allow():
        raise RateLimitExceeded()
    
    # Then circuit breaker
    return circuit_breaker.call(func)
```

---

## 🚧 Bulkhead Pattern

<div align="center">

### Q15: What is the Bulkhead pattern?

**A:** Bulkhead pattern isolates resources to prevent failures in one area from affecting the entire system.

**Origin:** Named after ship bulkheads that isolate compartments to prevent sinking.

**Key Concept:**
- **Isolation:** Separate resource pools
- **Failure Containment:** Failures don't spread
- **Resource Limits:** Per-pool limits

**Benefits:**
- ✅ Prevents cascading failures
- ✅ Isolates resource exhaustion
- ✅ Better fault tolerance
- ✅ Improved availability

---

### Q16: How does Bulkhead work?

**A:**

**Bulkhead Implementation:**

1. **Thread Pool Isolation:**
   - Separate thread pools per service
   - Isolated execution
   - Prevents thread exhaustion

2. **Connection Pool Isolation:**
   - Separate connection pools
   - Per-service limits
   - Prevents connection exhaustion

3. **Resource Isolation:**
   - CPU, memory limits
   - Per-service quotas
   - Resource boundaries

**Example - Thread Pool Isolation:**
```python
from concurrent.futures import ThreadPoolExecutor

class BulkheadExecutor:
    def __init__(self):
        # Separate thread pools
        self.critical_pool = ThreadPoolExecutor(max_workers=10)
        self.normal_pool = ThreadPoolExecutor(max_workers=50)
        self.low_priority_pool = ThreadPoolExecutor(max_workers=20)
    
    def execute_critical(self, func, *args):
        return self.critical_pool.submit(func, *args)
    
    def execute_normal(self, func, *args):
        return self.normal_pool.submit(func, *args)
    
    def execute_low_priority(self, func, *args):
        return self.low_priority_pool.submit(func, *args)
```

---

### Q17: What are Bulkhead use cases?

**A:**

**Common Use Cases:**

1. **Microservices:**
   - Isolate service calls
   - Separate thread pools
   - Prevent cascading failures

2. **Database Connections:**
   - Separate pools per database
   - Isolate database failures
   - Prevent connection exhaustion

3. **External APIs:**
   - Separate pools per API
   - Isolate API failures
   - Prevent resource exhaustion

4. **Priority-Based Processing:**
   - High-priority pool
   - Low-priority pool
   - Ensure critical operations

**Example - Database Bulkhead:**
```python
class DatabaseBulkhead:
    def __init__(self):
        # Separate connection pools
        self.primary_pool = create_pool(max_connections=20)
        self.replica_pool = create_pool(max_connections=50)
        self.analytics_pool = create_pool(max_connections=10)
    
    def query_primary(self, query):
        return self.primary_pool.execute(query)
    
    def query_replica(self, query):
        return self.replica_pool.execute(query)
    
    def query_analytics(self, query):
        return self.analytics_pool.execute(query)
```

---

### Q18: How to implement Bulkhead pattern?

**A:**

**Implementation Strategies:**

1. **Thread Pool Bulkhead:**
```python
from concurrent.futures import ThreadPoolExecutor
import threading

class ThreadPoolBulkhead:
    def __init__(self, max_concurrent=10):
        self.semaphore = threading.Semaphore(max_concurrent)
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
    
    def execute(self, func, *args, **kwargs):
        if not self.semaphore.acquire(blocking=False):
            raise BulkheadFullException("Bulkhead is full")
        
        try:
            future = self.executor.submit(func, *args, **kwargs)
            return future
        finally:
            self.semaphore.release()
```

2. **Connection Pool Bulkhead:**
```python
class ConnectionPoolBulkhead:
    def __init__(self, max_connections=20):
        self.max_connections = max_connections
        self.connections = []
        self.lock = threading.Lock()
    
    def get_connection(self):
        with self.lock:
            if len(self.connections) >= self.max_connections:
                raise BulkheadFullException("Connection pool full")
            
            conn = self.create_connection()
            self.connections.append(conn)
            return conn
    
    def release_connection(self, conn):
        with self.lock:
            if conn in self.connections:
                self.connections.remove(conn)
                conn.close()
```

---

### Q19: What are Bulkhead best practices?

**A:**

**Best Practices:**

1. **Size Appropriately:**
   - Based on service capacity
   - Monitor and adjust
   - Balance isolation and efficiency

2. **Monitor Metrics:**
   - Pool utilization
   - Rejection rates
   - Wait times

3. **Handle Rejections:**
   - Graceful degradation
   - Fallback strategies
   - User-friendly errors

4. **Isolate by Priority:**
   - Critical operations
   - Normal operations
   - Background tasks

5. **Resource Limits:**
   - Per-pool limits
   - Total resource limits
   - Prevent exhaustion

**Example - Complete Bulkhead:**
```python
class ServiceBulkhead:
    def __init__(self, service_name, max_concurrent=10):
        self.service_name = service_name
        self.semaphore = threading.Semaphore(max_concurrent)
        self.metrics = {
            'active': 0,
            'rejected': 0,
            'completed': 0
        }
    
    def execute(self, func, *args, **kwargs):
        if not self.semaphore.acquire(blocking=False):
            self.metrics['rejected'] += 1
            raise BulkheadFullException(
                f"Bulkhead for {self.service_name} is full"
            )
        
        self.metrics['active'] += 1
        try:
            return func(*args, **kwargs)
        finally:
            self.metrics['active'] -= 1
            self.metrics['completed'] += 1
            self.semaphore.release()
```

---

## 🎯 Combining Resilience Patterns

<div align="center">

### Q20: How to combine resilience patterns?

**A:**

**Pattern Combination:**

**Recommended Order:**
```
Rate Limiter → Bulkhead → Retry → Circuit Breaker
```

**Why This Order:**

1. **Rate Limiter:** First line of defense
2. **Bulkhead:** Isolate resources
3. **Retry:** Handle transient failures
4. **Circuit Breaker:** Prevent cascading failures

**Example - Combined Pattern:**
```python
class ResilientService:
    def __init__(self):
        self.rate_limiter = RateLimiter(requests_per_second=10)
        self.bulkhead = ThreadPoolBulkhead(max_concurrent=5)
        self.retry_policy = RetryPolicy(max_retries=3)
        self.circuit_breaker = CircuitBreaker()
    
    def call(self, func, *args, **kwargs):
        # 1. Rate limit
        if not self.rate_limiter.allow():
            raise RateLimitExceeded()
        
        # 2. Bulkhead
        def execute():
            return self.bulkhead.execute(
                # 3. Retry
                lambda: self.retry_policy.execute(
                    # 4. Circuit breaker
                    lambda: self.circuit_breaker.call(func, *args, **kwargs)
                )
            )
        
        return execute()
```

---

### Q21: What are resilience pattern trade-offs?

**A:**

**Trade-offs:**

| Pattern | Pros | Cons |
|:---:|:---:|:---:|
| **Circuit Breaker** | Prevents cascading failures | May block healthy requests |
| **Retry** | Handles transient failures | Increases latency |
| **Rate Limiter** | Protects services | May reject valid requests |
| **Bulkhead** | Isolates failures | Resource overhead |

**Balancing:**

1. **Circuit Breaker:**
   - Tune thresholds carefully
   - Monitor state transitions
   - Use fallbacks

2. **Retry:**
   - Limit max retries
   - Use exponential backoff
   - Retry only transient errors

3. **Rate Limiter:**
   - Set appropriate limits
   - Handle 429 gracefully
   - Use sliding window

4. **Bulkhead:**
   - Size pools appropriately
   - Monitor utilization
   - Handle rejections

---

## 🎯 Real-World Examples

<div align="center">

### Q22: What are real-world resilience implementations?

**A:**

**Popular Libraries:**

1. **Resilience4j (Java):**
   - Circuit Breaker
   - Retry
   - Rate Limiter
   - Bulkhead

2. **Polly (.NET):**
   - Circuit Breaker
   - Retry
   - Timeout
   - Bulkhead

3. **Hystrix (Deprecated):**
   - Circuit Breaker
   - Fallback
   - Thread isolation

**Resilience4j Example:**
```java
// Circuit Breaker
CircuitBreaker circuitBreaker = CircuitBreaker.ofDefaults("service");

// Retry
Retry retry = Retry.ofDefaults("service");

// Rate Limiter
RateLimiter rateLimiter = RateLimiter.ofDefaults("service");

// Bulkhead
Bulkhead bulkhead = Bulkhead.ofDefaults("service");

// Combine
Supplier<String> supplier = () -> callService();
Supplier<String> decorated = Decorators.ofSupplier(supplier)
    .withCircuitBreaker(circuitBreaker)
    .withRetry(retry)
    .withRateLimiter(rateLimiter)
    .withBulkhead(bulkhead)
    .decorate();

String result = Try.ofSupplier(decorated)
    .recover(throwable -> "fallback")
    .get();
```

---

## 💡 Key Takeaways

<div align="center">

| Pattern | Key Point |
|:---:|:---:|
| **Circuit Breaker** | Prevents cascading failures, fast failure |
| **Retry** | Handles transient failures with backoff |
| **Rate Limiter** | Controls request rates, protects services |
| **Bulkhead** | Isolates failures, prevents resource exhaustion |

**💡 Remember:** Resilience patterns work together. Use Rate Limiter first, then Bulkhead for isolation, Retry for transient failures, and Circuit Breaker to prevent cascading failures. Monitor metrics and tune thresholds based on your service characteristics.

</div>

---

## 🔗 Related Topics

<div align="center">

| Topic | Description | Link |
|:---:|:---:|:---:|
| **Rate Limiting** | Detailed rate limiting algorithms | [Rate Limiting](./03-rate-limiting.md) |
| **Reliability** | System reliability concepts | [Reliability](./01-reliability.md) |
| **Availability** | High availability patterns | [Availability](./02-availability.md) |

</div>

---

<div align="center">

**Master resilience patterns for fault-tolerant systems! 🚀**

*From Circuit Breaker to Bulkhead - comprehensive guide to building resilient distributed systems.*

</div>

