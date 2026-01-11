# Design Flash Sale System

## What is a Flash Sale System?

A flash sale system enables e-commerce platforms to sell limited inventory at discounted prices during a short time window, typically lasting minutes to hours.
The core challenge is handling extreme traffic spikes where millions of users compete for a few thousand items simultaneously. Unlike regular e-commerce, flash sales create a thundering herd problem where traffic can spike 100x or more within seconds of the sale starting.
**Popular Examples:** Amazon Lightning Deals, Flipkart Big Billion Days, Alibaba Singles' Day
What makes flash sales particularly interesting is the asymmetry of outcomes. Out of 5 million purchase attempts, only 10,000 might succeed. That means 99.8% of requests result in failure, either due to sold-out inventory or system protection mechanisms. 
The architecture must be optimized for this reality: rejecting requests cheaply and quickly is just as important as processing successful orders.
This system design problem tests your ability to handle extreme concurrency, prevent overselling, ensure fairness, and maintain system stability under load.
In this chapter, we will explore the **high-level design of a flash sale system**.
Lets start by clarifying the requirements:
# 1. Clarifying Requirements
Before starting the design, it's important to ask thoughtful questions to uncover hidden assumptions, clarify ambiguities, and define the system's scope more precisely.
Here is an example of how a discussion between the candidate and the interviewer might unfold:
**Candidate:** "What is the expected scale? How many concurrent users and items per flash sale?"
**Interviewer:** "We need to support 10 million concurrent users competing for 10,000 items in a single flash sale event."
**Candidate:** "How long does a typical flash sale last, and how many sales happen per day?"
**Interviewer:** "Each sale lasts 30 minutes to 2 hours. We run about 10 flash sales per day, but they don't overlap."
**Candidate:** "Should users be able to reserve items before completing payment, or is it first-come-first-served at checkout?"
**Interviewer:** "Users should be able to add items to cart and have a 10-minute window to complete payment. If they don't pay, the item goes back to inventory."
**Candidate:** "How do we handle fairness? Should we prevent bots and ensure real users get a fair chance?"
**Interviewer:** "Yes, we need basic bot protection and rate limiting. We want to give legitimate users a fair chance."
**Candidate:** "What happens if the sale starts and our systems are overwhelmed? What's the acceptable failure mode?"
**Interviewer:** "The system should remain available. It's better to show 'sold out' than to crash. We cannot oversell under any circumstances."
After gathering the details, we can summarize the key system requirements.

## 1.1 Functional Requirements
- **Browse Flash Sale:** Users can view upcoming and active flash sale items with prices, discounts, and remaining inventory.
- **Place Order:** Users can attempt to purchase flash sale items when the sale is active.
- **Inventory Reservation:** When a user initiates checkout, inventory is temporarily reserved for a payment window (e.g., 10 minutes).
- **Payment Processing:** Complete the purchase within the reservation window.
- **Order Confirmation:** Notify users of successful or failed orders.

## 1.2 Non-Functional Requirements
Beyond features, we need to consider the qualities that make the system production-ready:
- **High Availability:** The system must remain available during peak load (99.99% uptime).
- **No Overselling:** Inventory must never go negative. This is a hard constraint.
- **Low Latency:** Order placement should complete within 500ms at p99.
- **Scalability:** Handle 10 million concurrent users and 100,000+ requests per second.
- **Fairness:** Legitimate users should have a fair chance; bots and abuse should be mitigated.

# 2. Back-of-the-Envelope Estimation
Before diving into the architecture, let us run some quick calculations to understand the scale we are dealing with. These numbers will guide our design decisions, particularly around caching, queuing, and database selection.

### 2.1 Traffic Estimates
Flash sale traffic patterns are unlike anything else in e-commerce. Instead of gradual growth, we see a near-instantaneous spike when the sale starts.

#### The Thundering Herd
Starting with the numbers from our requirements discussion:
- Concurrent users at sale start: **10 million**
- Users attempting to buy within first 10 seconds: **5 million** (50% of users have fast fingers and good internet)
- Peak QPS = 5,000,000 requests / 10 seconds = **500,000 QPS**

To put this in perspective, that is roughly 10x the traffic Twitter handles during major events. All of it hitting the "buy" button simultaneously.

#### After the Spike
Here is the crucial insight: the traffic does not disappear after items sell out. Users keep refreshing, retrying, and hoping for inventory to return from abandoned carts. We need to handle this "rejection traffic" cheaply.

### 2.2 Success vs Failure Ratio
Let us think about the outcomes of all those requests:
| Metric | Value | Notes |
| --- | --- | --- |
| Total purchase attempts | 5,000,000 | In first 10 seconds |
| Available inventory | 10,000 | Limited supply |
| Successful reservations | 10,000 | Best case |
| Failed attempts | 4,990,000 | 99.8% of requests |

This ratio is staggering. For every 500 purchase attempts, only 1 succeeds. The remaining 499 get a "sold out" response.
**Design Implication:** Our system must be optimized for the failure case. Returning "sold out" should be as cheap and fast as possible, ideally without hitting the database at all.

### 2.3 Storage Estimates
Compared to traffic, storage requirements are modest:
| Component | Size | Calculation |
| --- | --- | --- |
| Event metadata | ~500 bytes | Sale name, times, configuration |
| Item details | ~1 KB per item | Price, description, limits |
| Order records | ~500 bytes each | User, item, status, timestamps |
| Reservation records | ~200 bytes each | Temporary reservation tracking |

**Per flash sale event:**
With 10 events per day and 30-day retention, we need roughly 5 GB of storage. This is trivial for modern databases.
**Key Insight:** Storage is not the bottleneck here. The challenge is handling concurrent writes to a single inventory counter. Ten thousand threads all trying to decrement the same number at the same time, that is where things get interesting.

### 2.4 Bandwidth Estimates
Most of the bandwidth goes to serving the flash sale page, not processing orders:
This is why CDN caching is essential. Without it, our origin servers would need to push 50 GB/s, which is impractical. With a CDN serving 95% of page loads from edge cache, origin bandwidth drops to 2.5 GB/s, still significant but manageable.

### 2.5 Key Design Implications
These estimates reveal several critical design decisions:
1. **Reject early, reject cheaply:** 99.8% of requests will fail. We need to detect "sold out" at the edge, before requests reach our databases.
2. **Cache aggressively:** Static content (sale page, product images) must be served from CDN. Even the inventory count can be cached with short TTL.
3. **Optimize for writes:** The real bottleneck is concurrent inventory updates. This is a distributed systems problem, not a storage problem.
4. **Plan for graceful degradation:** At 500,000 QPS, even a 1% error rate means 5,000 errors per second. Users need clear feedback, not cryptic timeouts.

# 3. Core APIs
With our requirements and scale understood, let us define the API contract. The flash sale system needs three core endpoints: browsing sale details, placing orders, and completing payment.

### 3.1 Get Flash Sale Details

#### Endpoint: GET /flash-sales/{sale_id}
This is the most frequently called endpoint. Users refresh this page constantly before and during the sale, watching the countdown timer and checking inventory. It must be heavily cached and extremely fast.

#### Path Parameters:
| Parameter | Type | Description |
| --- | --- | --- |
| sale_id | string | Unique identifier for the flash sale event |

#### Example Response (200 OK):

#### Caching Strategy:
The `remaining_quantity` field creates an interesting challenge. We want to show users accurate inventory counts, but we cannot query the database on every request. The solution is to cache aggressively with short TTL:
- CDN cache: 1-2 seconds during active sale
- Application cache: 500ms
- Users see slightly stale counts, but this is acceptable

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 404 Not Found | Sale does not exist | Invalid sale_id |
| 429 Too Many Requests | Rate limited | User refreshing too aggressively |

### 3.2 Place Order

#### Endpoint: POST /flash-sales/{sale_id}/orders
This is the critical endpoint where the magic happens. When a user clicks "Buy Now", this endpoint must atomically check inventory, reserve the item, and return a result, all in milliseconds.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| item_id | string | Yes | The item to purchase |
| quantity | integer | Yes | Number of items (usually 1, max 2) |

#### Example Request:

#### Success Response (201 Created):
The response includes a `reservation_expires_at` timestamp. The user has until this time to complete payment. After that, the reservation expires and the item returns to inventory.

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 409 Conflict | Cannot fulfill | Item sold out, or user already purchased this item |
| 400 Bad Request | Invalid request | Sale not active, quantity exceeds limit |
| 429 Too Many Requests | Rate limited | Too many purchase attempts from this user |

The 409 response includes a reason code to help the user understand what happened:
Or for duplicate purchases:

### 3.3 Complete Payment

#### Endpoint: POST /orders/{order_id}/pay
Once a user has a reservation, they have a limited time window to complete payment. This endpoint processes the payment and confirms the order.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| payment_token | string | Yes | Tokenized payment method from payment provider |
| payment_method | string | Yes | Type of payment (credit_card, wallet, etc.) |

#### Example Request:

#### Success Response (200 OK):

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 410 Gone | Reservation expired | Payment window (10 minutes) has passed |
| 402 Payment Required | Payment failed | Card declined, insufficient funds, etc. |
| 404 Not Found | Order not found | Invalid order_id |

When a reservation expires (410 Gone), the inventory is automatically returned to the pool. The user would need to go back and try to reserve again, but by then, the item is likely sold out.

### 3.4 API Design Considerations
A few design decisions worth noting:
**Idempotency:** The Place Order endpoint is not naturally idempotent. If a user double-clicks, they might create two reservations. We handle this by checking if the user already has a reservation for this item and returning the existing reservation instead of creating a new one.
**Rate Limiting:** We apply aggressive rate limits on the Place Order endpoint:
- 1 request per second per user
- 10 requests per minute per user
- Requests beyond this get 429 responses

**Response Times:** We target these latencies:
- Get Flash Sale: p99 < 50ms (mostly served from cache)
- Place Order: p99 < 500ms (includes inventory check and reservation)
- Complete Payment: p99 < 2s (includes external payment gateway)

# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complex diagram upfront, we will build the design incrementally, starting with the simplest possible solution and adding components as we encounter challenges. This mirrors how you would approach the problem in an interview.
Our system must satisfy three core requirements:
1. **Handle Traffic Spikes:** Millions of users hitting the system simultaneously at sale start
2. **Prevent Overselling:** Ensure inventory never goes negative despite concurrent purchases
3. **Process Orders:** Reserve inventory, accept payment, and confirm orders

The key insight that will guide our design is this: most requests during a flash sale will fail. Out of 5 million purchase attempts, only 10,000 will succeed. That means 99.8% of requests should result in a "sold out" response.
This changes how we think about the architecture. Instead of optimizing for successful orders (which are rare), we should optimize for rejecting requests early and cheaply. If we can detect "sold out" at the edge without hitting our databases, we dramatically reduce load on our critical systems.
Each layer in this funnel filters out requests, so only legitimate purchase attempts that have a chance of succeeding reach our database. Let us build this architecture step by step.

## 4.1 Handling Traffic Spikes
The first challenge is absorbing the initial traffic spike without overwhelming our backend systems. When 5 million users click "Buy Now" within 10 seconds, we cannot simply forward all those requests to our order processing service. That would be 500,000 QPS hitting a system that can probably handle 10,000 QPS at best.
The solution is to build multiple layers of protection, each designed to filter out traffic before it reaches the critical path.
Let us walk through each component and understand why it exists.

### Components for Traffic Management

#### CDN (Content Delivery Network)
The CDN is our first line of defense. When users load the flash sale page, they are downloading product images, HTML, CSS, and JavaScript. Without a CDN, every page load would hit our origin servers.
During a flash sale, users refresh the page constantly, waiting for the countdown to hit zero. A CDN caches this static content at edge locations around the world, so a user in Mumbai gets their content from a nearby edge node rather than from our data center in Virginia. This reduces origin load by 90% or more.
The CDN also provides DDoS protection. If someone tries to overwhelm our system with traffic, the CDN's distributed infrastructure absorbs much of the attack.

#### Load Balancer
The load balancer distributes incoming requests across multiple API Gateway instances. It performs health checks to route traffic away from unhealthy servers and ensures no single server becomes overwhelmed.
During flash sales, we scale up the number of API Gateway instances. The load balancer automatically distributes traffic across all available instances.

#### API Gateway
Every request enters through the API Gateway. Think of it as the bouncer at a nightclub, checking IDs and turning away troublemakers before they get inside.
The gateway handles authentication, so we know who is making each request. It validates that requests are well-formed. Most importantly, it enforces rate limits, preventing any single user from hammering the system.

#### Rate Limiter
The rate limiter is the key to protecting our backend. It tracks how many requests each user has made recently and rejects requests that exceed the limit.
For flash sales, we might allow 1 purchase attempt per second per user. This sounds restrictive, but it is enough for legitimate users, you cannot click a button faster than once per second anyway. What it blocks is bots that can send hundreds of requests per second.

#### Request Queue
Even after all the filtering above, we might still have more valid requests than our Order Service can process. The queue acts as a buffer, accepting requests quickly and processing them at a sustainable rate.
Think of it like the line at a popular restaurant. Everyone gets a spot in line, but the kitchen only serves dishes at a pace it can handle. The alternative would be chaos in the kitchen.

### The Traffic Flow
Here is what happens step by step:
1. **Page Load:** Users load the flash sale page. The CDN serves static content from edge cache in milliseconds. Our origin servers never see this traffic.
2. **Purchase Request:** When the sale starts, users click "Buy Now". The request goes through the CDN to our load balancer (CDNs do not cache POST requests).
3. **Gateway Processing:** The API Gateway authenticates the user and checks rate limits. If the user is spamming requests, they get a 429 (Too Many Requests) response immediately. No further processing needed.
4. **Queue Buffering:** Valid requests go into the queue. The user gets a 202 (Accepted) response immediately, meaning "we got your request and we are working on it."
5. **Order Processing:** The Order Service pulls requests from the queue at a controlled rate, say 10,000 per second. This is the rate our inventory system can handle reliably.

This design means the thundering herd never directly hits our database. Most requests are either served from cache, rejected by rate limiting, or buffered in the queue. Only a controlled stream reaches the Order Service.

## 4.2 Preventing Overselling
Now we arrive at the most critical requirement: ensuring we never sell more items than we have. This sounds simple, but it is surprisingly difficult when thousands of concurrent requests are trying to decrement the same inventory counter.
Imagine this scenario: we have 1 item left, and 100 requests arrive simultaneously. Each request checks the inventory, sees "1 available", and proceeds to decrement. If these checks and decrements are not atomic, we could end up selling 100 units of something we only have 1 of.
This is why we need atomic operations. The check and decrement must happen as a single indivisible operation that no other request can interrupt.

### Components for Inventory Management

#### Inventory Service
This is a dedicated microservice responsible for managing real-time inventory counts. It tracks three states for each item:
- **Available:** Items that can be purchased right now
- **Reserved:** Items that someone is in the process of buying (payment pending)
- **Sold:** Items that have been successfully purchased

The Inventory Service exposes a single critical operation: atomic reservation. Given an item and quantity, it either reserves the item and returns success, or returns "sold out" immediately.

#### Redis as the Inventory Counter
We use Redis as our real-time inventory store for two key reasons:
1. **Speed:** Redis operations complete in microseconds, compared to milliseconds for database queries. When handling 100,000+ requests per second, this difference matters enormously.
2. **Atomic Operations:** Redis supports Lua scripts that execute atomically. No other operation can run between the check and the decrement.

The inventory counter in Redis is simple:

#### PostgreSQL for Durability
While Redis handles the hot path (inventory checks and decrements), PostgreSQL stores the durable record of orders and reservations. If Redis restarts, we can rebuild the inventory counter from the database.

### The Reservation Flow
Here is the critical insight: when items are sold out, we do not touch the database at all. The "sold out" response comes directly from Redis, which means we can reject 99.8% of requests with a sub-millisecond Redis check.
Let us walk through the happy path:
1. **Request Arrives:** The Order Service receives a purchase request from the queue. It calls the Inventory Service with the item_id, quantity, and user_id.
2. **Atomic Check-and-Decrement:** The Inventory Service executes a Lua script in Redis. This script checks if enough inventory exists and decrements it atomically. If there are 100 items left and we request 1, the script decrements to 99 and returns success.
3. **Create Reservation:** With inventory secured in Redis, we create a reservation record in PostgreSQL. This record includes the order details and an expiration timestamp (10 minutes from now).
4. **Return Success:** The user gets back a reservation confirmation with a payment URL. They have 10 minutes to complete payment.

And the sad path (which is actually the common path):
1. **Request Arrives:** Same as above.
2. **Atomic Check Fails:** The Lua script sees that inventory is 0 (or less than requested quantity). It immediately returns -1 without modifying anything.
3. **Return Sold Out:** The Inventory Service returns "sold out" to the Order Service. No database write happens.

This asymmetry is intentional. The common case (sold out) is fast and cheap. The rare case (successful reservation) involves a database write, but that is fine because it happens at most 10,000 times per sale.

## 4.3 Processing Orders and Payments
Once a user has successfully reserved an item, the hard part is done, or is it? The user now has 10 minutes to complete payment. During this window, several things can happen:
- The user pays successfully, and the order is confirmed
- The user's payment fails (insufficient funds, wrong card details)
- The user abandons the purchase and the reservation expires

Each of these scenarios requires different handling, and we need to ensure that inventory is always correctly accounted for.

### Components for Payment Processing

#### Payment Service
This service handles the integration with external payment providers like Stripe, PayPal, or Adyen. Payment processing is one of those things you should never build yourself, the fraud detection, PCI compliance, and card network integrations are complex enough to warrant using a specialized provider.
The Payment Service:
- Accepts payment tokens from the client (the actual card details never touch our servers)
- Calls the payment gateway to charge the customer
- Handles the various response scenarios (success, decline, timeout, fraud block)
- Updates order status and triggers notifications

#### Notification Service
When a purchase succeeds, users want confirmation immediately. The Notification Service handles:
- Push notifications to mobile apps
- Email confirmations
- SMS alerts (especially important in regions where email is less common)
- Real-time updates via WebSocket if the user is still on the page

#### Timeout Handler
This background worker is crucial for inventory management. It runs continuously, checking for reservations that have expired without payment.
When a reservation expires:
1. Increment the inventory counter in Redis (return the item to available stock)
2. Update the order status in PostgreSQL to "expired"
3. Optionally notify the user that they missed their window

Without this component, abandoned reservations would permanently lock up inventory.

### The Payment Flow
Let us walk through each scenario:

#### Successful Payment
1. User submits payment within the 10-minute window
2. We verify the reservation still exists and has not expired
3. Payment Service charges the customer via the payment gateway
4. On success, we update the order status to "confirmed"
5. Notification Service sends email and push notification
6. User sees confirmation page with order number

#### Failed Payment
1. User submits payment, but the card is declined
2. Payment gateway returns an error (insufficient funds, fraud block, etc.)
3. We release the inventory back to Redis (INCR operation)
4. Order status updated to "payment_failed"
5. User gets a clear error message and can try a different payment method
6. If they do not retry before expiration, the Timeout Handler cleans up

#### Abandoned Reservation (Timeout)
1. User gets distracted, closes the browser, or has second thoughts
2. The 10-minute timer expires
3. Timeout Handler finds the expired reservation in its periodic scan
4. Inventory is released back to Redis
5. Order status updated to "expired"
6. The item is now available for other users

This last scenario is important for fairness. Without timeout handling, scalpers could reserve all inventory and hold it hostage indefinitely.

## 4.4 Putting It All Together
Now that we have designed each piece, let us step back and see the complete architecture. What started as three requirements (handle traffic, prevent overselling, process orders) has evolved into a layered system where each component has a clear responsibility.
The architecture follows a layered approach, with each layer handling specific concerns:
**Client Layer:** Users interact through web browsers or mobile apps. From our perspective, they all look the same, just HTTP requests.
**Edge Layer:** The CDN caches static content and absorbs read traffic. The Load Balancer distributes requests across multiple gateway instances.
**Gateway Layer:** The API Gateway handles authentication and basic validation. The Rate Limiter protects against abuse and ensures fair access.
**Processing Layer:** The Request Queue buffers traffic spikes. The Order Service orchestrates the purchase flow. The Inventory Service manages stock levels atomically. The Payment Service handles external payment processing. The Notification Service keeps users informed.
**Data Layer:** Redis stores real-time inventory counters for microsecond access. PostgreSQL provides durable storage for orders and reservations.
**Background Workers:** The Timeout Handler continuously monitors for expired reservations and releases inventory back to the pool.

### Component Responsibilities Summary
| Component | Primary Responsibility | Scaling Strategy |
| --- | --- | --- |
| CDN | Static content, edge caching, DDoS protection | Managed service (auto-scales) |
| Load Balancer | Traffic distribution, health checks | Managed service |
| API Gateway | Authentication, validation, routing | Horizontal (add instances) |
| Rate Limiter | Abuse prevention, fair access | Distributed with Redis |
| Request Queue | Traffic buffering, backpressure | Kafka/SQS (partitioned) |
| Order Service | Order orchestration, business logic | Horizontal (stateless) |
| Inventory Service | Atomic inventory operations | Horizontal with Redis sharding |
| Payment Service | Payment gateway integration | Horizontal (stateless) |
| Notification Service | User communications | Horizontal (async) |
| Redis | Real-time inventory counters | Redis Cluster |
| PostgreSQL | Order persistence, transactions | Primary + replicas |
| Timeout Handler | Reservation cleanup | Leader election (single active) |

This architecture handles our requirements well: the CDN and Rate Limiter absorb most traffic, Redis enables atomic inventory operations, and the queue prevents the thundering herd from overwhelming our database.
# 5. Database Design
With the high-level architecture in place, let us zoom into the data layer. Choosing the right database and designing an efficient schema are critical decisions that affect everything from inventory accuracy to query performance.

## 5.1 Choosing the Right Database
The database choice for a flash sale system is interesting because we need to balance several competing concerns.

#### What we need to store:
- Flash sale event metadata (small, rarely changes)
- Item inventory counts (small, but updated thousands of times per second)
- Order records (medium size, write-heavy during sales)
- User purchase history (for enforcing per-user limits)

#### How we access the data:
- Inventory checks need microsecond latency (Redis)
- Order creation needs ACID transactions (SQL)
- Post-sale analytics need complex queries (SQL)

#### Why a hybrid approach?
The key insight is that different data has different access patterns:
- **Inventory counters** are hit hundreds of thousands of times per second. They need sub-millisecond access. Redis is perfect for this.
- **Order records** need durability and transaction support. If the system crashes, we cannot lose confirmed orders. PostgreSQL provides ACID guarantees.
- **User purchase history** needs to be checked atomically with inventory reservation to enforce per-user limits. This can live in either store, but Redis is faster during the sale.

This separation is common in high-traffic systems. Redis handles the hot path where speed is critical, while PostgreSQL provides durability and supports the business operations that happen before and after the sale.

## 5.2 Database Schema
Let us design the PostgreSQL schema. We have four main tables:

### Flash Sales Table
Stores metadata about each flash sale event.
| Field | Type | Description |
| --- | --- | --- |
| sale_id | UUID (PK) | Unique identifier for the flash sale |
| name | VARCHAR(255) | Display name ("Summer Phone Launch") |
| start_time | TIMESTAMP | When the sale begins (UTC) |
| end_time | TIMESTAMP | When the sale ends (UTC) |
| status | ENUM | One of: upcoming, active, ended |
| created_at | TIMESTAMP | When the sale was created |

This table is small and rarely changes. The only write during a sale is updating the status from "upcoming" to "active" to "ended".

### Flash Sale Items Table
Stores the products available in each sale with their pricing and inventory.
| Field | Type | Description |
| --- | --- | --- |
| item_id | UUID (PK) | Unique identifier for this sale item |
| sale_id | UUID (FK) | Reference to the flash sale |
| product_id | UUID | Reference to the main product catalog |
| original_price | DECIMAL(10,2) | Regular price before discount |
| sale_price | DECIMAL(10,2) | Flash sale discounted price |
| total_quantity | INTEGER | Total inventory allocated for this sale |
| reserved_quantity | INTEGER | Currently reserved (awaiting payment) |
| sold_quantity | INTEGER | Successfully sold and paid |
| per_user_limit | INTEGER | Maximum quantity per user (typically 1-2) |

Note that `reserved_quantity` and `sold_quantity` in this table are not the source of truth during the sale. Redis holds the real-time counts. These fields are updated asynchronously and used for reconciliation and reporting.

### Orders Table
The heart of our data model, storing every order attempt.
| Field | Type | Description |
| --- | --- | --- |
| order_id | UUID (PK) | Unique order identifier |
| user_id | UUID (FK) | User who placed the order |
| item_id | UUID (FK) | Flash sale item being purchased |
| quantity | INTEGER | Number of units (usually 1) |
| status | ENUM | One of: reserved, confirmed, expired, payment_failed, cancelled |
| total_amount | DECIMAL(10,2) | Total payment amount |
| reserved_at | TIMESTAMP | When inventory was reserved |
| expires_at | TIMESTAMP | Deadline for payment |
| confirmed_at | TIMESTAMP | When payment completed (nullable) |

**Indexes:**
The partial index on `expires_at` only includes reserved orders, keeping the index small and fast for the Timeout Handler.

### User Purchase History Table
Tracks what each user has already bought, enabling per-user limit enforcement.
| Field | Type | Description |
| --- | --- | --- |
| user_id | UUID (PK) | User identifier |
| item_id | UUID (PK) | Flash sale item |
| quantity_purchased | INTEGER | Total quantity successfully purchased |
| last_purchase_at | TIMESTAMP | Most recent purchase time |

The composite primary key (user_id, item_id) ensures fast lookups when checking if a user has already purchased an item.

#### Why a separate table?
We could query the orders table for this information, but that query would be expensive during a flash sale. Having a denormalized table with exactly the data we need makes the per-user limit check fast.
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often go deeper into specific technical challenges. In this section, we will explore the trickiest aspects of flash sale systems: preventing overselling, managing traffic spikes, ensuring fairness, handling timeouts, and scaling the system.
These topics distinguish a good system design answer from a great one. Let us dig in.

## 6.1 Preventing Overselling with Atomic Operations
We touched on this earlier, but let us go deeper. Preventing overselling is not just important, it is existential. If we sell 10,001 units of a 10,000-unit inventory, someone does not get their item. That creates refund requests, angry customers, and potential legal issues.
The challenge is concurrency. When 10,000 requests arrive within a second, all trying to decrement the same counter, we need to ensure that exactly 10,000 succeed and the rest fail.
A good solution must ensure three things:
1. **Atomicity:** The check ("is inventory > 0?") and the decrement ("inventory -= 1") must happen as a single indivisible operation
2. **Consistency:** No race conditions, ever. Two requests cannot both think they got the last item
3. **Performance:** We need to handle 100,000+ checks per second without breaking a sweat

Let us explore three approaches, from simple to sophisticated.

### Approach 1: Database-Level Locking
The most straightforward approach is to use database transactions with row-level locks.

#### How It Works
The `FOR UPDATE` clause acquires an exclusive lock on the row. While this transaction holds the lock, no other transaction can modify the same row. This guarantees that our check-and-decrement happens atomically.
**Pros**
- Strong consistency guaranteed by the database
- Simple to implement and understand
- Works correctly out of the box

**Cons**
- All requests for the same item serialize on a single row, creating a bottleneck
- At 100,000+ QPS, the database becomes overwhelmed
- Each request waits for disk I/O and lock acquisition, adding latency

This approach works fine for low-traffic systems, but it does not scale for flash sales.

### Approach 2: Redis Atomic Decrement
Redis is an in-memory data store that can execute operations in microseconds. More importantly, Redis supports Lua scripts that execute atomically, meaning no other operation can run in the middle of our script.

#### How It Works
First, before the sale starts, we load inventory counts into Redis:
Then we use a Lua script that checks availability and decrements in a single atomic operation:
We execute this script with:
If the script returns >= 0, the reservation succeeded. If it returns -1, the item is sold out.

#### Why Lua scripts?
Redis processes commands sequentially, but a naive approach using separate GET and DECRBY commands could still race:
Lua scripts are different. Redis executes the entire script atomically, so no other command can run between the GET and DECRBY inside our script.
**Pros**
- Operations complete in microseconds (vs milliseconds for database)
- Lua scripts guarantee atomicity without locks
- Single Redis instance handles 100,000+ operations per second

**Cons**
- Redis data is in-memory, so we need persistence (AOF/RDB) and replication for durability
- We must keep Redis and the database in sync, adding complexity

### Approach 3: Two-Phase Reservation (Recommended)
The best approach combines Redis for speed with PostgreSQL for durability. We get the microsecond performance of Redis for the hot path, with the ACID guarantees of PostgreSQL for the durable record.

#### How It Works
**Phase 1: Fast Reservation in Redis (Synchronous)**
1. User submits purchase request
2. Execute Lua script to atomically check and decrement inventory in Redis
3. If successful, immediately return a reservation ID to the user
4. If Redis shows sold out, reject immediately without touching the database

**Phase 2: Durable Persistence (Asynchronous)**
1. After returning success to the user, write the reservation to PostgreSQL asynchronously
2. If the database write fails, increment Redis inventory back (rollback)
3. A background job periodically reconciles Redis with the database to catch any drift

#### Why this works:
The critical insight is that the user does not need to wait for the database write. As long as Redis has recorded the inventory decrement, the item is reserved. The database write can happen in the background without affecting user-perceived latency.
If we crash after the Redis decrement but before the database write, we have a problem: inventory is decremented in Redis but no order exists in the database. The reconciliation job catches this by comparing Redis inventory with the sum of reservations and sales in the database, and adjusting Redis if needed.

#### Example Workflow
The user sees success in 2ms. The database write happens 50ms later, completely transparent to the user.
**Pros**
- Combines Redis speed with PostgreSQL durability
- User gets sub-millisecond response for the critical path
- Even if async writes lag, inventory is protected in Redis
- Can recover from inconsistencies through reconciliation

**Cons**
- More complex than either approach alone
- Need to handle sync failures and edge cases
- Database may lag behind Redis briefly (eventual consistency)

### Which Approach Should You Choose?
| Strategy | Latency | Throughput | Durability | Complexity | Best For |
| --- | --- | --- | --- | --- | --- |
| Database Locking | High | Low | High | Low | Low-traffic systems |
| Redis Atomic | Very Low | Very High | Medium | Medium | Read-heavy workloads |
| Two-Phase | Very Low | Very High | High | High | Production flash sales |

**Recommendation:** Use the Two-Phase approach for any serious flash sale system. The added complexity is worth it for the combination of speed and durability. Redis handles the hot path where every millisecond matters, while PostgreSQL provides the durable record you need for order fulfillment.

## 6.2 Handling Traffic Spikes
We discussed traffic management at a high level earlier. Now let us go deeper into the specific strategies and their trade-offs.
The core problem is the thundering herd. At exactly midnight when the sale starts, millions of users who have been staring at a countdown timer all click simultaneously. This creates a traffic spike that can be 100x normal load, concentrated into a few seconds.
Without proper handling, this spike crashes databases, overwhelms application servers, and leaves users with timeout errors instead of a clean "sold out" message.
Let us explore four strategies that work together to tame this beast.

### Strategy 1: Request Queuing with Backpressure
Instead of letting all requests hit your services simultaneously, buffer them in a queue and process at a sustainable rate.

#### How It Works
1. Incoming requests are pushed to a message queue (Kafka, SQS, RabbitMQ)
2. Order Service consumers pull from the queue at a fixed rate (50,000/sec)
3. If the queue exceeds capacity, new requests are rejected with a clear error

Users receive an immediate 202 Accepted ("Processing your request...") while their request waits in the queue.
**Pros**
- Protects backend services from overload
- No data loss since requests are buffered, not dropped
- System degrades gracefully under extreme load

**Cons**
- Adds latency while requests wait in queue
- Users might wait several seconds only to learn the item sold out

### Strategy 2: Early Rejection with Sold-Out Cache
Here is a key insight: once an item sells out, there is no point processing any more purchase requests for it. Every subsequent request will fail anyway. So why let those requests reach our Order Service at all?

#### How It Works
1. Maintain a "sold out" flag in Redis for each item
2. The API Gateway checks this flag before queuing any purchase request
3. If the item is sold out, return immediately without hitting backend services

When the Inventory Service decrements inventory to 0, it sets the sold-out flag:

#### Impact
Once an item sells out (say 10 seconds into the sale), the remaining 4.99 million requests are rejected at the edge in microseconds. They never reach the queue, never hit the Order Service, never touch Redis inventory, and never query the database.
This is why we said earlier that optimizing for the failure case is critical. The sold-out cache turns a 500,000 QPS problem into a 10,000 QPS problem.

### Strategy 3: Lottery System for Fairness
First-come-first-served sounds fair, but is it really? In practice, "first-come" often means "whoever has the fastest internet and most sophisticated automation wins."
A lottery system levels the playing field. Instead of rewarding speed, it rewards luck, which is at least democratically distributed.

#### How It Works
1. Open a registration window 5-15 minutes before the sale
2. Users register their interest in specific items
3. At sale start, randomly select 10,000 winners from the pool of registrants
4. Winners receive a purchase token valid for 10 minutes
5. Non-winners receive a notification immediately

**Pros**
- Fair to all users, luck-based not speed-based
- Spreads load over time since not everyone clicks at the same moment
- Defeats bots because random selection negates any speed advantage

**Cons**
- Different user experience that some may find less exciting
- Requires building registration and selection systems
- Winners might forget to use their token

Companies like Nike use this approach (they call it "draws") for limited-edition sneaker releases.

### Strategy 4: Virtual Waiting Room
When traffic exceeds what your system can handle, show users a waiting room page instead of error messages. This is more honest and less frustrating than mysterious timeouts.

#### How It Works
1. When incoming traffic exceeds a threshold, redirect users to a waiting room page
2. The waiting room displays queue position and estimated wait time
3. Users are admitted to the main site as capacity becomes available
4. A token system tracks position and prevents queue-jumping

#### The User Experience
Instead of seeing a blank page or error, users see:
This is transparent, professional, and much less frustrating than mystery errors.
**Pros**
- Users understand what is happening and how long they will wait
- Infrastructure is protected with controlled admission
- Much better UX than error pages or timeouts

**Cons**
- Requires additional infrastructure for queue management
- Users still have to wait, which is never fun

Services like Cloudflare Waiting Room and AWS offer managed solutions for this.

### Combining Strategies
In practice, you use multiple strategies together:
1. **Virtual Waiting Room** provides a good user experience during extreme spikes
2. **Rate Limiting** protects against abuse and ensures fair access
3. **Request Queuing** smooths out load on backend services
4. **Sold-Out Cache** rejects doomed requests before they waste resources
5. **Lottery System** is an option for limited, high-demand items where fairness is paramount

## 6.3 Ensuring Fairness and Preventing Abuse
Flash sales attract the worst of the internet: bots, scalpers, and bad actors. If legitimate users never win because bots buy out inventory in milliseconds, they stop coming back. Fairness is not just an ethical consideration; it is a business requirement.
Let us examine the threats and how to counter them.

### Threat 1: Bots and Automated Scripts
Professional scalpers use sophisticated bots that can submit thousands of purchase requests per second. While a human is still processing that the countdown reached zero, a bot has already made 500 purchase attempts.

#### Mitigations
**Rate Limiting:** The first line of defense. Limit requests per user and per IP address:
- 1 purchase attempt per item per user
- 10 requests per second per IP address
- 100 requests per minute per user account

**CAPTCHA at Checkout:** Require CAPTCHA verification for purchase attempts during flash sales. Modern "invisible" CAPTCHAs only challenge users when behavior is suspicious, minimizing friction for legitimate users.
**Device Fingerprinting:** Track device characteristics (browser version, plugins, screen resolution, timezone) to identify bot patterns. Multiple accounts from the same device fingerprint trigger additional verification.
**Behavioral Analysis:** Bots behave differently than humans:
- Requests arriving faster than human reaction time (< 100ms after sale starts)
- Identical request patterns across multiple accounts
- Missing mouse movements, scroll events, or other human interaction signals
- Perfect timing on every click

Machine learning models can score sessions based on these patterns and block or challenge suspicious ones.

### Threat 2: Account Farming
Scalpers create hundreds of accounts to bypass per-user limits. Each account buys the maximum allowed, then the scalper resells at markup.

#### Mitigations
**Phone Verification:** Require SMS verification for flash sale participation. Limit one phone number per account. This makes account farming expensive since each account needs a unique phone number.
**Purchase History Requirements:** Only allow accounts with prior purchase history to participate. For example, require at least one order in the past 30 days. This prevents freshly-created bot accounts from participating.
**Payment Method Limits:** Limit how many accounts can use the same credit card. If 50 accounts all use the same Visa ending in 4242, that is suspicious.
**Address Validation:** Multiple accounts shipping to the same address is a red flag.

### Threat 3: Network-Level Attacks
Some attackers do not want to buy anything. They want to crash your system so legitimate users cannot buy either. This might be a competitor, or just someone who enjoys chaos.

#### Mitigations
**CDN and DDoS Protection:** Use CDN providers (Cloudflare, Akamai, AWS CloudFront) with built-in DDoS protection. Their globally distributed edge network absorbs attack traffic before it reaches your infrastructure.
**Geographic Rate Limiting:** If your user base is primarily in North America and Europe, apply stricter limits on traffic from regions where you have few customers.
**Progressive Throttling:** Automatically increase rate limiting severity as overall traffic increases beyond normal thresholds. If traffic is 10x normal, tighten limits by 10x.

## 6.4 Reservation Timeout and Inventory Recovery
When a user reserves an item but does not complete payment, we have a problem. The inventory is locked (so no one else can buy it), but it is not actually sold. If the user abandons the purchase, we need to release that inventory back to the pool.

### The Problem
Consider this timeline:
User A reserved the last item at 10:00:00 and has until 10:10:00 to pay. User B arrives at 10:05:00, wants the item, but sees "sold out." User A abandons at 10:08:00 without paying. The item sits reserved until 10:10:00, then finally gets released. By then, User B has left.
We need a way to release inventory promptly when reservations expire. Let us explore three approaches.

### Solution 1: Background Job Polling
The simplest approach: run a background job that periodically scans for expired reservations.

#### How It Works
**Pros**
- Simple to implement and understand
- Works reliably for most cases
- Easy to monitor and debug

**Cons**
- Delay between expiration and release (up to 30-60 seconds)
- Batch processing can cause load spikes when many reservations expire together

### Solution 2: Redis TTL with Keyspace Notifications
Redis can automatically expire keys and notify listeners when that happens. We can use this to trigger immediate inventory release.

#### How It Works
When the key expires after 600 seconds, Redis publishes an event. A listener process catches the event and releases inventory immediately.
**Pros**
- Real-time release at exact expiration time
- No polling needed
- Lower latency than background job

**Cons**
- Redis keyspace notifications are best-effort and can be missed under load
- Need a backup mechanism (like the background job) to catch missed events

### Solution 3: Delayed Message Queue (Recommended)
Schedule a message to be delivered exactly when the reservation expires. Message queues are built for reliable delivery, so this is more robust than Redis notifications.

#### How It Works
When creating a reservation at 10:00:00:
When the message arrives at 10:10:00, the handler checks if the order is still in "reserved" status. If yes, release the inventory. If the user already paid, the status will be "confirmed" and we simply ignore the message.
**Pros**
- Precise timing without polling
- Reliable delivery with message queue guarantees (SQS, RabbitMQ)
- Handles high volume of expirations efficiently

**Cons**
- Requires message queue that supports delayed delivery

### Which Approach Should You Choose?
| Strategy | Precision | Complexity | Reliability |
| --- | --- | --- | --- |
| Background Job | Low (30-60s delay) | Low | High |
| Redis TTL + Events | High | Medium | Medium |
| Delayed Queue | High | Medium | High |

**Our Recommendation:** Use the Delayed Message Queue as your primary mechanism for precise, reliable expiration handling. Keep a background job running as a safety net to catch any edge cases where the delayed message was lost or never enqueued.

## 6.5 Scaling the Order Service
Everything we have discussed so far assumes the Order Service can handle the load. But what happens when a single instance is not enough? Let us explore how to scale horizontally.

### Horizontal Scaling with Partitioning
The Order Service is stateless (all state lives in Redis and PostgreSQL), so we can run multiple instances. But we need to be careful about how requests are distributed.

#### How It Works
1. Deploy multiple Order Service instances
2. Route requests based on item_id hash: `instance = hash(item_id) % num_instances`
3. Each instance handles a subset of items

#### Why Partition by Item?
All requests for the same item go to the same instance. This provides better cache locality and prevents the thundering herd from spreading across all instances. If "Phone X" sells out, only one instance deals with the spike, while others continue serving other items normally.

#### Benefits
- Each instance handles fewer items, reducing contention
- Horizontal scaling by adding more instances
- Item-level isolation: problems with one item do not affect others

### Redis Cluster for Inventory
A single Redis instance can handle 100,000+ operations per second, but for larger scale or redundancy, use Redis Cluster.
Redis Cluster automatically shards data across multiple nodes. Each inventory key (`inventory:item_123`) is assigned to a specific shard based on its hash slot. This distributes the write load across multiple Redis primaries.

### Read Replicas for Availability Display
The flash sale page shows inventory counts for all items. These reads do not need to be perfectly accurate. A 1-second old count is fine for display purposes.
This pattern offloads read traffic to replicas while keeping the critical write path on the primary.

### Aggressive Sold-Out Caching
Once an item sells out, that status is unlikely to change (except briefly if reservations expire). We can cache this aggressively at every layer:
1. **Redis:** Set `soldout:item_123 = true` with long TTL
2. **Application Cache:** Cache locally in each service instance
3. **CDN Edge:** Push sold-out status to edge locations
4. **Client:** JavaScript can cache and show "Sold Out" without server round-trip

This converts the most common request (sold-out check for a sold-out item) into the cheapest possible operation: a local cache hit that never leaves the user's browser.
# Summary
Designing a flash sale system requires balancing several competing concerns: handling extreme traffic spikes, preventing overselling through atomic operations, ensuring fairness against bots, and processing payments reliably.
The key architectural decisions we made:
1. **Multi-layer traffic filtering:** CDN, rate limiting, queuing, and sold-out caching work together to reduce load at each layer
2. **Redis for the hot path:** Atomic Lua scripts provide microsecond inventory checks without race conditions
3. **Two-phase reservation:** Combine Redis speed with PostgreSQL durability for the best of both worlds
4. **Background cleanup:** Delayed message queues handle reservation timeouts precisely
5. **Defense in depth:** Multiple strategies for bot prevention and fair access

The most important insight is that 99.8% of requests will fail. Optimizing for fast, cheap failure is just as important as optimizing for successful purchases. When you design with this in mind, the architecture naturally evolves toward early rejection and aggressive caching.
# References
- [Designing Data-Intensive Applications](https://dataintensive.net/) - Martin Kleppmann's book covering distributed systems fundamentals
- [Redis Lua Scripting](https://redis.io/docs/interact/programmability/eval-intro/) - Official Redis documentation on atomic Lua scripts
- [How We Built a 10x Faster Flash Sale System](https://engineering.shopify.com/blogs/engineering/flash-sales-at-scale) - Shopify's engineering blog on flash sale architecture
- [Handling Flash Sales at Alibaba](https://www.alibabacloud.com/blog/how-alibaba-handled-the-biggest-online-shopping-festival_593973) - Alibaba's approach to Singles' Day traffic
- [Rate Limiting Strategies](https://stripe.com/blog/rate-limiters) - Stripe's blog on implementing rate limiters

# Quiz

## Design Flash Sale Quiz
In a flash sale, which design choice best prevents overselling under extreme concurrency?