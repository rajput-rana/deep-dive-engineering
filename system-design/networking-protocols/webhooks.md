# Webhooks

## Summary

Webhooks are HTTP callbacks that allow one application to notify another application about events in real-time. Instead of polling for updates, webhooks enable event-driven communication where the source application pushes data to a destination URL when an event occurs.

## Key Concepts

### Webhook vs Polling

**Polling (Traditional Approach):**
```
Client: "Do you have updates?"
Server: "No"
[Wait 5 seconds]
Client: "Do you have updates?"
Server: "No"
[Wait 5 seconds]
Client: "Do you have updates?"
Server: "Yes, here's the data"
```

**Webhook (Event-Driven):**
```
Event occurs → Server immediately sends data to client's URL
No waiting, no repeated requests
```

### How Webhooks Work

**Basic Flow:**
1. Client registers a webhook URL with the service
2. Event occurs in the service
3. Service makes HTTP POST request to registered URL
4. Client receives and processes the event

**Diagram:**
```
┌─────────┐                    ┌─────────┐
│ Service │                    │ Client  │
│  (API)  │                    │  App    │
└────┬────┘                    └────┬────┘
     │                              │
     │ 1. Register webhook URL      │
     │─────────────────────────────>│
     │    POST /webhooks            │
     │    { url: "https://..." }    │
     │                              │
     │                              │
     │ 2. Event occurs              │
     │    (e.g., payment received)  │
     │                              │
     │ 3. Send HTTP POST            │
     │─────────────────────────────>│
     │    POST https://client.com/  │
     │    { event: "payment", ... } │
     │                              │
     │                              │
     │ 4. Process event             │
     │                              │
```

## Why Webhooks Matter

**Real-Time Updates:** Instant notifications instead of polling delays.

**Efficiency:** Reduces unnecessary requests and server load.

**Event-Driven Architecture:** Enables reactive, event-driven systems.

**Better User Experience:** Immediate updates for users.

## Real-World Examples

### Payment Processing (Stripe)
- **Event:** Payment completed
- **Webhook:** Notifies your server immediately
- **Use Case:** Update order status, send confirmation email

### GitHub
- **Event:** Code pushed, pull request created
- **Webhook:** Triggers CI/CD pipelines
- **Use Case:** Automated testing and deployment

### Slack
- **Event:** Message posted, user joined
- **Webhook:** Integrate with external services
- **Use Case:** Custom notifications, automation

### Email Services (SendGrid, Mailgun)
- **Event:** Email delivered, bounced, opened
- **Webhook:** Track email status
- **Use Case:** Update user records, analytics

## Webhook Implementation

### 1. Registering a Webhook

**Client registers webhook URL:**
```http
POST /api/webhooks
Content-Type: application/json

{
  "url": "https://myapp.com/webhooks/payment",
  "events": ["payment.completed", "payment.failed"],
  "secret": "webhook_secret_key"
}
```

**Response:**
```json
{
  "id": "wh_123456",
  "url": "https://myapp.com/webhooks/payment",
  "status": "active"
}
```

### 2. Receiving Webhooks

**Webhook payload example:**
```http
POST https://myapp.com/webhooks/payment
Content-Type: application/json
X-Webhook-Signature: sha256=abc123...

{
  "event": "payment.completed",
  "data": {
    "payment_id": "pay_123",
    "amount": 1000,
    "currency": "USD",
    "customer_id": "cus_456"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 3. Webhook Security

**Signature Verification:**
```
Service calculates: HMAC-SHA256(payload, secret)
Sends in header: X-Webhook-Signature

Client verifies:
1. Calculate HMAC-SHA256(received_payload, secret)
2. Compare with X-Webhook-Signature
3. If match → Authentic, process
4. If mismatch → Reject
```

**Diagram:**
```
Service Side:
Payload + Secret → HMAC-SHA256 → Signature
                              │
                              ▼
                    X-Webhook-Signature header

Client Side:
Received Payload + Secret → HMAC-SHA256 → Calculated Signature
                                              │
                                              ▼
                                    Compare with header
                                    If match → Process
                                    If not → Reject
```

## Webhook Best Practices

### 1. Idempotency

**Problem:** Webhooks may be delivered multiple times.

**Solution:** Use idempotency keys.

```json
{
  "event_id": "evt_123456",  // Unique event ID
  "event": "payment.completed",
  "data": {...}
}
```

**Client processing:**
```python
if event_already_processed(event_id):
    return 200  # Already handled
else:
    process_event(data)
    mark_as_processed(event_id)
```

### 2. Retry Logic

**Service should:**
- Retry failed webhook deliveries
- Use exponential backoff
- Have maximum retry attempts

**Retry Strategy:**
```
Attempt 1: Immediate
Attempt 2: After 1 minute
Attempt 3: After 5 minutes
Attempt 4: After 30 minutes
Attempt 5: After 2 hours
Max attempts: 5
```

### 3. Timeout Handling

**Client should:**
- Respond quickly (within 5 seconds)
- Process asynchronously if needed
- Return 200 OK immediately, process later

**Pattern:**
```
Receive webhook → Return 200 OK immediately
                → Queue for processing
                → Process asynchronously
```

### 4. Webhook Status Monitoring

**Track webhook delivery:**
- Success rate
- Failure reasons
- Retry attempts
- Delivery latency

**Dashboard:**
```
Webhook: payment.completed
Success Rate: 99.5%
Average Latency: 150ms
Failures: 5 (last 24h)
```

## Webhook vs Alternatives

### Webhooks vs Polling

| Aspect | Webhooks | Polling |
|--------|----------|---------|
| Latency | Real-time | Delayed (poll interval) |
| Efficiency | High (only on events) | Low (repeated requests) |
| Server Load | Low | High |
| Complexity | Medium | Low |
| Reliability | Requires retry logic | Simple |

### Webhooks vs WebSockets

| Aspect | Webhooks | WebSockets |
|--------|----------|------------|
| Connection | Stateless HTTP | Persistent connection |
| Direction | One-way (server→client) | Bidirectional |
| Use Case | Event notifications | Real-time chat, updates |
| Complexity | Lower | Higher |

## Common Webhook Patterns

### 1. Simple Notification
```
Event → POST to URL → Done
```

### 2. Request-Response Pattern
```
Event → POST to URL → Client processes → Returns result
```

### 3. Fan-Out Pattern
```
Event → Multiple webhook URLs → All clients notified
```

**Diagram:**
```
        Event Occurs
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌────────┐       ┌────────┐
│Client A│       │Client B│
│Webhook │       │Webhook │
└────────┘       └────────┘
```

## Design Considerations

### When to Use Webhooks

**Good for:**
- Event notifications
- Asynchronous processing
- Integrating third-party services
- Real-time updates
- Reducing polling overhead

**Not ideal for:**
- Synchronous operations requiring immediate response
- Very high-frequency events (consider message queues)
- Simple request-response patterns

### Webhook Endpoint Design

**Requirements:**
- Publicly accessible URL
- HTTPS (security)
- Fast response (return 200 quickly)
- Idempotent processing
- Signature verification

**Example Endpoint:**
```python
@app.route('/webhooks/payment', methods=['POST'])
def handle_payment_webhook():
    # 1. Verify signature
    if not verify_signature(request):
        return 400
    
    # 2. Check idempotency
    event_id = request.json['event_id']
    if is_duplicate(event_id):
        return 200  # Already processed
    
    # 3. Process asynchronously
    queue.enqueue(process_payment, request.json)
    
    # 4. Return immediately
    return 200
```

## Interview Hints

When discussing webhooks:
1. Explain the problem they solve (polling inefficiency)
2. Describe the flow (registration → event → POST)
3. Discuss security (signature verification)
4. Address reliability (retries, idempotency)
5. Compare with alternatives (polling, WebSockets)
6. Give real-world examples

## Conclusion

Webhooks enable efficient, event-driven communication between applications. By implementing proper security, retry logic, and idempotency handling, webhooks provide a scalable solution for real-time event notifications, reducing server load and improving user experience compared to traditional polling approaches.

