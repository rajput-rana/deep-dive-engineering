# Idempotency

## Summary

Idempotency is a property of operations where performing the same operation multiple times produces the same result as performing it once. In distributed systems, idempotency is crucial for handling retries, network failures, and ensuring data consistency.

## Key Concepts

### What is Idempotency?

**Definition:** An operation is idempotent if performing it multiple times has the same effect as performing it once.

**Mathematical Example:**
```
f(f(x)) = f(x)

Example: Absolute value
abs(abs(-5)) = abs(-5) = 5
```

**HTTP Example:**
```
GET /users/123 (idempotent)
- Call 1: Returns user data
- Call 2: Returns same user data
- Call 3: Returns same user data

Result: Same every time
```

## Why Idempotency Matters

**Network Failures:** Retries don't cause duplicate operations.

**Distributed Systems:** Handles duplicate messages gracefully.

**Data Consistency:** Prevents duplicate records, double charges.

**User Experience:** Safe to retry failed operations.

## Idempotent HTTP Methods

### Idempotent Methods

**GET:** Always idempotent
```
GET /users/123
→ Returns same data every time
```

**PUT:** Idempotent (replaces resource)
```
PUT /users/123 {name: "John"}
→ First call: Creates/updates user
→ Second call: Same result (replaces)
```

**DELETE:** Idempotent
```
DELETE /users/123
→ First call: Deletes user
→ Second call: User already deleted (same result)
```

**HEAD:** Idempotent (like GET but headers only)

### Non-Idempotent Methods

**POST:** Not idempotent
```
POST /users {name: "John"}
→ First call: Creates user with ID 1
→ Second call: Creates user with ID 2 (different result!)
```

**PATCH:** May not be idempotent (depends on implementation)

## Implementing Idempotency

### 1. Idempotency Keys

**How it works:**
- Client generates unique idempotency key
- Sends with request
- Server stores key with result
- Duplicate requests return same result

**Flow:**
```
Request 1:
POST /payments
Idempotency-Key: abc123
→ Process payment
→ Store: abc123 → Payment ID 456
→ Return: Payment ID 456

Request 2 (duplicate):
POST /payments
Idempotency-Key: abc123
→ Check: abc123 exists
→ Return: Payment ID 456 (same result)
```

**Diagram:**
```
Client                    Server
  │                         │
  │ POST /payments          │
  │ Idempotency-Key: abc123 │
  │────────────────────────>│
  │                         │
  │                         │ Check: abc123 exists?
  │                         │ No → Process payment
  │                         │ Store: abc123 → Result
  │                         │
  │ Payment ID: 456         │
  │<────────────────────────│
  │                         │
  │ (Retry - duplicate)     │
  │ POST /payments          │
  │ Idempotency-Key: abc123 │
  │────────────────────────>│
  │                         │
  │                         │ Check: abc123 exists?
  │                         │ Yes → Return stored result
  │                         │
  │ Payment ID: 456         │
  │<────────────────────────│
  │ (Same result!)          │
```

### 2. Natural Idempotency

Some operations are naturally idempotent by design.

**Example: Set Operations**
```
PUT /users/123 {email: "john@example.com"}
→ First call: Sets email
→ Second call: Sets email (same result)
```

**Example: Delete Operations**
```
DELETE /users/123
→ First call: Deletes user
→ Second call: User already deleted (same result)
```

### 3. Conditional Requests

Use conditional headers to make operations idempotent.

**ETag Example:**
```
GET /users/123
→ Returns ETag: "abc123"

PUT /users/123
If-Match: "abc123"
→ Only updates if ETag matches
→ Prevents overwriting concurrent updates
```

## Idempotency Patterns

### 1. Idempotent Create

**Problem:** POST creates duplicate resources.

**Solution:** Use idempotency key or check existence.

**Example:**
```python
def create_user(idempotency_key, user_data):
    # Check if already processed
    if idempotency_key in processed_keys:
        return get_stored_result(idempotency_key)
    
    # Check if user already exists
    if user_exists(user_data.email):
        return get_existing_user(user_data.email)
    
    # Create user
    user = create_new_user(user_data)
    store_result(idempotency_key, user)
    return user
```

### 2. Idempotent Update

**Problem:** Retries cause inconsistent updates.

**Solution:** Use version numbers or timestamps.

**Example:**
```python
def update_user(user_id, version, user_data):
    current_user = get_user(user_id)
    
    # Check version
    if current_user.version != version:
        return 409 Conflict  # Version mismatch
    
    # Update
    update_user_data(user_id, user_data)
    increment_version(user_id)
    return updated_user
```

### 3. Idempotent Delete

**Problem:** Multiple deletes cause errors.

**Solution:** Return success even if already deleted.

**Example:**
```python
def delete_user(user_id):
    if not user_exists(user_id):
        return 200 OK  # Already deleted
    
    delete_user(user_id)
    return 200 OK
```

## Real-World Examples

### Payment Processing (Stripe)

**Idempotency Key:**
```
POST /v1/charges
Idempotency-Key: abc123

First request: Creates charge
Duplicate request: Returns same charge
```

**Benefits:**
- Prevents double charges
- Safe to retry
- Handles network failures

### Database Operations

**UPSERT Pattern:**
```sql
INSERT INTO users (id, email, name)
VALUES (123, 'john@example.com', 'John')
ON CONFLICT (id) DO UPDATE
SET email = EXCLUDED.email,
    name = EXCLUDED.name;
```

**Result:** Idempotent - same result whether insert or update

### Message Queues

**At-Least-Once Delivery:**
- Messages may be delivered multiple times
- Idempotent processing ensures correct result
- Use message ID to detect duplicates

**Example:**
```python
def process_message(message_id, data):
    if already_processed(message_id):
        return  # Skip duplicate
    
    process_data(data)
    mark_as_processed(message_id)
```

## Idempotency vs Other Concepts

### Idempotency vs Commutativity

**Idempotency:** `f(f(x)) = f(x)`
- Same operation, same result

**Commutativity:** `f(a, b) = f(b, a)`
- Order doesn't matter

### Idempotency vs Safe Methods

**Idempotent:** Can be called multiple times safely
**Safe:** Doesn't modify server state (GET, HEAD)

**Relationship:**
- All safe methods are idempotent
- Not all idempotent methods are safe (PUT, DELETE modify state)

## Design Considerations

### When to Implement Idempotency

**Critical for:**
- Payment processing
- Order creation
- Resource creation
- State-changing operations
- Retry scenarios

**Less critical for:**
- Read operations (naturally idempotent)
- Stateless operations

### Idempotency Key Storage

**Options:**
- In-memory cache (Redis) - Fast, but lost on restart
- Database - Persistent, but slower
- Distributed cache - Best for distributed systems

**TTL Considerations:**
- How long to store idempotency keys?
- Depends on operation type
- Typical: 24 hours to 7 days

**Example:**
```python
# Redis with TTL
redis.setex(
    f"idempotency:{key}",
    86400,  # 24 hours
    result
)
```

### Handling Concurrent Requests

**Problem:** Two requests with same idempotency key arrive simultaneously.

**Solution:** Use distributed locks.

**Example:**
```python
def process_with_idempotency(key, operation):
    lock = acquire_lock(f"lock:{key}")
    try:
        if key in processed_keys:
            return get_stored_result(key)
        
        result = operation()
        store_result(key, result)
        return result
    finally:
        release_lock(lock)
```

## Interview Hints

When discussing idempotency:
1. Define idempotency clearly
2. Explain why it's important (retries, failures)
3. Give examples of idempotent operations
4. Discuss implementation (idempotency keys)
5. Address concurrent requests
6. Compare with related concepts

## Conclusion

Idempotency is essential for building reliable distributed systems. By implementing idempotency keys, using naturally idempotent operations, and handling concurrent requests properly, you can ensure that retries and duplicate requests don't cause data inconsistencies or duplicate operations.

