# Design Stock Exchange

## What is a Stock Exchange?

A stock exchange is a centralized marketplace where buyers and sellers trade financial instruments like stocks, bonds, and derivatives. It acts as an intermediary that matches buy orders with sell orders to facilitate trades.
The core function of a stock exchange is **price discovery**, determining the fair market price of a security based on supply and demand. When a buyer's price meets or exceeds a seller's price, a trade is executed.
**Popular Examples:** NYSE (New York Stock Exchange), NASDAQ, SENSEX, Binance (for crypto)
What makes stock exchange design fascinating from a systems perspective is the extreme demands it places on every component. 
We are not talking about "fast" in the way most web applications mean it. Professional traders measure latency in microseconds, and a delay of even a few milliseconds can mean the difference between a profitable trade and a missed opportunity. 
The system must process hundreds of thousands of orders per second while maintaining perfect fairness, meaning orders must be processed in exactly the order they were received, with no exceptions.
This problem tests your ability to design systems with **ultra-low latency**, **high throughput**, **strong consistency**, and **fairness guarantees**.
In this chapter, we will explore the **high-level design of a stock exchange system**.
Let's start by clarifying the requirements:
# 1. Clarifying Requirements
Before starting the design, it's important to ask thoughtful questions to uncover hidden assumptions, clarify ambiguities, and define the system's scope more precisely.
In an interview setting, this is where you demonstrate that you think before you code. Here is how a requirements discussion might unfold:
**Candidate:** "What is the expected scale? How many orders per second should the system handle?"
**Interviewer:** "The system should handle around 100,000 orders per second during peak trading hours."
**Candidate:** "What types of orders should we support? Market orders, limit orders, or both?"
**Interviewer:** "Let's focus on limit orders and market orders. Stop orders and other complex order types are out of scope."
**Candidate:** "What latency requirements do we have for order matching?"
**Interviewer:** "Order matching should happen within 10 milliseconds for p99. We want to be competitive with modern exchanges."
**Candidate:** "Should we support after-hours trading or just regular market hours?"
**Interviewer:** "Let's focus on regular market hours only, say 9:30 AM to 4:00 PM."
**Candidate:** "Do we need to distribute real-time market data to external consumers?"
**Interviewer:** "Yes, we need to publish real-time price updates, order book snapshots, and trade executions."
**Candidate:** "What about risk management features like position limits or circuit breakers?"
**Interviewer:** "Basic risk checks are required, like validating sufficient funds. Circuit breakers for extreme price movements would be good to discuss."
This conversation reveals the scope of our system. Let's formalize these into clear requirements.

## 1.1 Functional Requirements
Based on the discussion, here are the core capabilities our system must support:
- **Order Placement:** Users can place buy and sell orders (market and limit orders).
- **Order Matching:** Match buy orders with sell orders based on price-time priority.
- **Trade Execution:** Execute matched trades and update account balances.
- **Order Cancellation:** Users can cancel their pending orders.
- **Market Data Distribution:** Distribute real-time price quotes, order book updates, and trade executions.

## 1.2 Non-Functional Requirements
- **Low Latency:** Order matching must happen within 10ms (p99).
- **High Throughput:** Handle 100,000 orders per second during peak hours.
- **Strong Consistency:** No double-spending, no duplicate trades, exact order priority preserved.
- **High Availability:** 99.99% uptime during trading hours.
- **Fairness:** Orders must be processed in strict price-time priority order.
- **Durability:** All trades must be persisted and recoverable.

# 2. Back-of-the-Envelope Estimation
Before diving into system components, let's run some quick calculations to understand the scale we are dealing with. These numbers will guide our decisions about storage, network capacity, and system architecture.

### 2.1 Order Volume
Starting with the numbers from our requirements discussion:

#### Peak Order Rate
Our target is 100,000 orders per second during peak trading hours. Let's put this in context with daily volumes:
In practice, traffic is not uniform. Peak periods occur at market open (9:30 AM), around lunch (when European markets close), and before market close (4:00 PM). Realistically, average load is about 20-30% of peak, giving us approximately **500 million orders per day**.

### 2.2 Trade Volume
Not every order results in an immediate trade. Limit orders often sit in the order book waiting for a matching price. Based on typical exchange statistics:
Each trade involves two orders (one buy, one sell), so 30,000 trades per second at peak means updating 60,000 order states per second. This is the write load our database must handle.

### 2.3 Market Data Volume
Market data distribution is where the numbers get interesting. Every trade and order book change generates events that need to reach thousands of subscribers.
That last number is staggering. We cannot send 1.2 billion individual messages per second using traditional unicast networking. This is why exchanges use specialized distribution techniques like multicast and hierarchical fan-out, which we will discuss in the deep dive.

### 2.4 Storage Requirements
Let's estimate how much data we need to store. Each order contains:
| Field | Size | Notes |
| --- | --- | --- |
| Order ID | 16 bytes | UUID or similar unique identifier |
| User ID | 16 bytes | Trader's account identifier |
| Symbol | 8 bytes | Stock ticker (e.g., "AAPL") |
| Side, Type | 2 bytes | Buy/Sell, Market/Limit |
| Price | 8 bytes | Decimal with 8 decimal places |
| Quantity | 8 bytes | Number of shares |
| Timestamps | 16 bytes | Created, updated times |
| Status, metadata | 26 bytes | Order state, sequence numbers |

**Total: ~100 bytes per order**
| Time Period | Orders | Storage | Notes |
| --- | --- | --- | --- |
| 1 Day | 500 million | ~50 GB | Hot storage needed |
| 1 Month | 15 billion | ~1.5 TB | Warm storage |
| 1 Year | 180 billion | ~18 TB | Cold storage, compressed |

For trades, each record is slightly larger (~150 bytes, including references to both orders), adding approximately 8 TB per year.
These storage numbers are manageable for modern infrastructure. The bigger challenge is not capacity but throughput: writing 30,000+ records per second requires careful database design.

### 2.5 Key Insights
These estimates highlight several important design implications:
1. **Order processing is the bottleneck.** At 100,000 orders per second, we have 10 microseconds per order on average. Every unnecessary operation adds latency.
2. **Market data fan-out is massive.** We cannot solve this with brute force. Specialized distribution mechanisms are essential.
3. **Storage throughput matters more than capacity.** 18 TB per year is modest, but sustaining 30,000 writes per second requires distributed databases or careful partitioning.
4. **Peak load drives capacity planning.** Average load is 25% of peak, but we must handle 100% without degradation when the market gets volatile.

# 3. Core APIs
With our requirements and scale understood, let's define the API contract. Stock exchanges have two distinct API styles: request-response APIs for order management, and streaming APIs for market data. Let's walk through each one.

### 3.1 Place Order

#### Endpoint: POST /orders
This is the primary endpoint traders use to submit orders. The response tells them immediately whether their order was accepted and, importantly, whether it was filled right away.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| user_id | string | Yes | Unique identifier of the trader's account |
| symbol | string | Yes | Stock symbol (e.g., "AAPL", "GOOGL", "MSFT") |
| side | enum | Yes | "BUY" or "SELL" |
| type | enum | Yes | "MARKET" (execute at best price) or "LIMIT" (execute only at specified price or better) |
| quantity | integer | Yes | Number of shares to trade |
| price | decimal | Conditional | Required for limit orders. The maximum price for buys, minimum price for sells |

#### Example Request:

#### Success Response (201 Created):
The response includes fill information because a limit order might match immediately against existing orders in the book. In this example, the trader wanted 100 shares and got 50 immediately at $150.20 (better than their limit of $150.25). The remaining 50 shares are now resting in the order book.

#### Error Responses:
| Status Code | Meaning | Example Scenario |
| --- | --- | --- |
| 400 Bad Request | Invalid parameters | Negative quantity, missing required field |
| 403 Forbidden | Risk check failed | Insufficient funds, position limit exceeded |
| 503 Service Unavailable | Exchange unavailable | Market closed, trading halted |

### 3.2 Cancel Order

#### Endpoint: DELETE /orders/{order_id}
Traders need to cancel orders quickly when market conditions change. This endpoint is latency-sensitive because a filled order cannot be cancelled.

#### Path Parameters:
| Parameter | Type | Description |
| --- | --- | --- |
| order_id | string | The unique identifier of the order to cancel |

#### Success Response (200 OK):

#### Error Responses:
| Status Code | Meaning | Example Scenario |
| --- | --- | --- |
| 404 Not Found | Order does not exist | Invalid order ID, already fully executed |
| 409 Conflict | Cannot cancel | Order already filled or previously cancelled |
| 403 Forbidden | Not authorized | Trying to cancel another user's order |

The `409 Conflict` response is important. There is a race condition between an order being filled and a cancel request arriving. The exchange must handle this gracefully since the trader might send a cancel request milliseconds after their order was filled.

### 3.3 Get Order Book

#### Endpoint: GET /orderbook/{symbol}
Returns a snapshot of the current order book for a given symbol. This is useful for traders who want to see market depth before placing orders.

#### Path Parameters:
| Parameter | Type | Description |
| --- | --- | --- |
| symbol | string | Stock symbol (e.g., "AAPL") |

#### Query Parameters:
| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| depth | integer | 10 | Number of price levels to return on each side |

#### Success Response (200 OK):
The bids are sorted highest-first (best bid at top), and asks are sorted lowest-first (best ask at top). The spread between the best bid ($150.00) and best ask ($150.05) is 5 cents in this example.

### 3.4 Subscribe to Market Data

#### Endpoint: WS /market-data/{symbol}
For real-time market data, we use WebSockets instead of polling. Clients open a persistent connection and receive updates as they happen.

#### Message Types:
| Type | Description | Example |
| --- | --- | --- |
| TRADE | A trade was executed | Price: $150.02, Quantity: 100, Time: 10:30:00.789 |
| BOOK_UPDATE | Order book changed | Bid at $150.00 increased by 200 shares |
| QUOTE | Best bid/ask changed | New best bid: $150.01, New best ask: $150.04 |

#### Example Trade Message:

#### Example Quote Message:
Market data subscriptions are the highest-volume API in the system. A single trade might trigger quote updates for thousands of connected clients. This fan-out challenge is one of the key design considerations we will address in the deep dive.
# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complex diagram upfront, we will build the design incrementally, starting with the simplest possible solution and adding components as we encounter challenges. This mirrors how you would approach the problem in an interview.
Our system needs to handle three fundamental operations:
1. **Order Management:** Accept orders from traders, validate them, and route them for matching.
2. **Order Matching:** The heart of the exchange. Match buy and sell orders using strict price-time priority.
3. **Market Data Distribution:** Publish real-time updates to thousands of subscribers.

The key insight is that these three operations have very different performance characteristics. Order management can tolerate some latency (tens of milliseconds is fine for validation). Order matching must be blazingly fast (microseconds). Market data has massive fan-out (one event becomes millions of deliveries). We need to design each path accordingly.
Let's build this architecture step by step, starting with order management.


When a trader clicks "Buy" or "Sell" in their trading app, the order begins a journey through several systems before it reaches the matching engine. This path needs to be fast, but more importantly, it needs to be correct. An invalid order that reaches the matching engine could cause serious problems.
Let's think about what needs to happen:
1. Verify the trader is who they claim to be (authentication)
2. Check that the order parameters are valid (non-negative quantity, valid symbol, etc.)
3. Verify the trader has sufficient funds or shares (risk check)
4. Record the order for audit purposes
5. Forward the order to the matching engine

Each of these steps requires its own component. Let's introduce them one by one.

### Components for Order Management

#### API Gateway
Every request enters through the API Gateway. Think of it as the front door to our exchange, handling concerns that are common across all requests.
The gateway authenticates requests using API keys or OAuth tokens, verifies that traders are allowed to submit orders, and enforces rate limits to prevent abuse or runaway algorithms from overwhelming the system. By handling these cross-cutting concerns at the edge, we keep our core services focused on business logic.

#### Order Management Service (OMS)
This is the brain of the order processing pipeline. The OMS validates order parameters (is this a real symbol? is the quantity positive?), coordinates with the Risk Service to ensure the trader can afford the order, persists the order to the database, and forwards valid orders to the matching engine.
The OMS also manages the order lifecycle. When an order is partially filled, the OMS updates the remaining quantity. When an order is cancelled, the OMS marks it as such. This state management is critical for traders who need to know the current status of their orders.

#### Risk Service
Before an order can be submitted, we need to verify that the trader can actually execute it. For buy orders, this means checking that they have enough cash. For sell orders, it means verifying they own the shares they want to sell.
The Risk Service maintains a real-time view of each trader's balances and positions. When a buy order comes in, it "reserves" the required funds so the same money cannot be used for multiple orders. When the order is filled, the reservation becomes an actual deduction.
This reservation model is critical for preventing double-spending. Without it, a trader with $10,000 could submit ten orders for $10,000 each, and all ten might match before we realize they did not have enough money.

#### Order Database
Stores all orders and their current state. We need this for several reasons: traders want to see their order history, regulators require audit trails, and we need to recover state if the OMS restarts.

### The Order Placement Flow
Let's trace through what happens when a trader submits an order:
Let's walk through this step by step:
1. **Request arrives at API Gateway:** The trader sends a POST request to buy 100 shares of AAPL at $150. The gateway validates their API key and ensures they have not exceeded their rate limit.
2. **OMS receives the order:** The Order Management Service validates the request parameters. Is "AAPL" a valid symbol? Is 100 a positive number? Is $150 a reasonable price? Basic sanity checks happen here.
3. **Risk check:** The OMS asks the Risk Service whether this trader can afford to buy $15,000 worth of stock. The Risk Service checks their cash balance, and if sufficient, reserves those funds so they cannot be used for another order.
4. **Persistence:** With the risk check passed, the OMS writes the order to the database. This ensures we have a durable record of every order, even if the system crashes moments later.
5. **Submit for matching:** The order is forwarded to the matching engine, where the real action happens. We will discuss this in detail in the next section.
6. **Response to trader:** The trader receives confirmation that their order was accepted, along with an order ID they can use to track its status.

**Why persist before matching?** If the matching engine crashes after receiving the order but before persisting the trade, we could lose track of the order entirely. By persisting first, we ensure that every order is recorded and can be recovered.


    S5 --> QueueKafka
```mermaid
graph TB
    subgraph Clients
        Web[Web Browser]
        Mobile[Mobile App]
    end

    subgraph Load Balancing
        LB[Load Balancer]
    end

    subgraph Application Services
        S1[503 Service]
        S2[Risk Service]
        S3[Management Service]
        S4[core Service]
        S5[dedicated Service]
    end

    subgraph Data Storage
        DBPostgreSQL[PostgreSQL]
    end

    subgraph Caching Layer
        CacheRedis[Redis]
    end

    subgraph Message Queue
        QueueKafka[Kafka]
    end

    Web --> LB
    Mobile --> LB
    LB --> S1
    LB --> S2
    LB --> S3
    LB --> S4
    LB --> S5
    S1 --> DBPostgreSQL
    S1 --> CacheRedis
    S1 --> QueueKafka
    S2 --> DBPostgreSQL
    S2 --> CacheRedis
    S2 --> QueueKafka
    S3 --> DBPostgreSQL
    S3 --> CacheRedis
    S3 --> QueueKafka
    S4 --> DBPostgreSQL
    S4 --> CacheRedis
    S4 --> QueueKafka
    S5 --> DBPostgreSQL
    S5 --> CacheRedis
    S5 --> QueueKafka



## 4.2 Requirement 2: Order Matching
This is the heart of the exchange, the component that actually brings buyers and sellers together. The matching engine must process orders with sub-millisecond latency while maintaining perfect fairness. If two traders submit orders at nearly the same time, the one who submitted first must be processed first. No exceptions.
This requirement has profound implications for the design. We cannot simply throw more servers at the problem, because distributing orders across multiple machines would break the strict ordering guarantee. The matching engine is where all the clever engineering happens.

### Components for Matching

#### Matching Engine
The matching engine is the crown jewel of the exchange. Its job sounds simple: take incoming orders, find matching orders on the opposite side, and execute trades. But doing this at 100,000 orders per second with microsecond latency is anything but simple.
The matching engine maintains an in-memory order book for each symbol. When a buy order arrives, it looks for sell orders at or below the buyer's price. When a sell order arrives, it looks for buy orders at or above the seller's price. If matches are found, trades are executed and both orders are updated.
Key design decisions make this possible:
- **Single-threaded processing:** Each symbol's order book is managed by a single thread. This eliminates the need for locks, which would add latency and complexity.
- **In-memory order book:** The entire order book lives in RAM. Hitting disk for every order would be far too slow.
- **Sequential processing:** Orders are processed one at a time in strict sequence order, guaranteeing fairness.

#### Sequencer
Before an order reaches the matching engine, it needs a sequence number. This number establishes the official order of events and is critical for both fairness and recovery.
Think about what happens if two orders arrive at exactly the same time on different network interfaces. Without a sequencer, there is no way to determine which one should be processed first. The sequencer solves this by assigning a monotonically increasing sequence number to each order. Order 1,000,001 always comes before order 1,000,002, regardless of network timing variations.
The sequence number also enables replay. If the matching engine crashes, we can rebuild its state by replaying all orders from a checkpoint. Without deterministic sequencing, replay might produce different results than the original run.

### Understanding Price-Time Priority
The matching algorithm is the soul of the exchange. It determines who gets matched with whom, and getting it wrong would be a regulatory nightmare. Most exchanges use **price-time priority**, also known as FIFO within price level.
The rules are simple:
1. **Price Priority:** Better prices always match first.
2. **Time Priority:** Among orders at the same price, whoever submitted first matches first.

Let's see how this works with a concrete example.

### Example: Matching a Market Order
Imagine the current order book for AAPL looks like this:
The **spread** is the gap between the best bid ($150.00) and the best ask ($150.50). This is where price discovery happens. Buyers want to pay as little as possible; sellers want to receive as much as possible. The spread represents that negotiation.
Now, a new order arrives: **BUY 250 shares at MARKET**. A market order means "fill my order at the best available price, whatever that is."
Here is how the matching engine processes it:
**Step 1:** The engine looks at the best ask (lowest sell price): $150.50 for 200 shares. Our buyer wants 250 shares, so we execute a trade for 200 shares at $150.50. The sell order at $150.50 is now fully filled and removed from the book. Our buy order still needs 50 more shares.
**Step 2:** The engine moves to the next best ask: $151.00 for 150 shares. We only need 50 shares, so we execute a trade for 50 shares at $151.00. The sell order at $151.00 is reduced from 150 shares to 100 shares remaining.
**Result:** Our buyer got 250 shares, with 200 at $150.50 and 50 at $151.00, for an average price of $150.70. Two trades were generated, and the order book has been updated.
Notice that the buyer paid a higher price for the last 50 shares. This is called **slippage**, and it's why large orders move the market. If you want to buy a million shares, you will work through multiple price levels and end up paying progressively higher prices.

### The Matching Flow
Here is how orders flow through the sequencer and matching engine:
Let's trace through the two scenarios:

#### Scenario 1: Order matches immediately
A market order or an aggressive limit order finds matching orders on the opposite side. The matching engine executes trades, records them in the trade database, and publishes events so market data subscribers know about the new trades and the changed order book.

#### Scenario 2: Order rests in the book
A limit order with a price that does not match any existing orders gets added to the order book. A buy order at $149 when the best ask is $150 will not match; it joins the bid side of the book, waiting for a seller to come along at $149 or lower. The engine publishes a book update so subscribers know the bid side has changed.
The matching engine never blocks waiting for the trade database or message queue. It processes orders as fast as possible, and persistence happens asynchronously. If the database is slow, trades queue up but matching continues. This design choice prioritizes latency over immediate durability, a trade-off we will revisit in the deep dive on fault tolerance.

## 4.3 Requirement 3: Market Data Distribution
Every time a trade executes or the order book changes, thousands of traders want to know about it. Market data distribution is how we get that information out to the world. This might sound like a simple "publish to subscribers" problem, but recall our earlier calculation: 120,000 events per second times 10,000 subscribers equals 1.2 billion message deliveries per second.
You cannot solve that with a simple pub/sub system. We need a specialized distribution architecture.

### Components for Market Data

#### Market Data Publisher
The Market Data Publisher sits between the matching engine and the outside world. It consumes the raw events from the matching engine (trade executed, order book changed, quote updated) and transforms them into market data messages.
The publisher also aggregates events. If the matching engine produces ten order book updates in the same millisecond, the publisher might combine them into a single message to reduce the fan-out burden. This batching adds a tiny bit of latency but dramatically reduces the message count.

#### Market Data Gateway
These are the servers that maintain persistent connections with clients. Each gateway handles thousands of WebSocket connections, receiving market data from the publisher and pushing it to connected clients.
The gateways are horizontally scalable: add more servers to handle more clients. They also handle subscription management, if a client only wants AAPL data, there is no point sending them GOOGL updates.

### The Market Data Flow
Here is what happens when a trade executes:
1. The matching engine publishes raw events to a message queue (Kafka is a common choice). The queue provides durability and allows multiple consumers.
2. The Market Data Publisher consumes events, formats them according to the market data protocol, and potentially aggregates multiple events into fewer messages.
3. The publisher pushes to all Market Data Gateways. Each gateway receives the same stream of events.
4. Each gateway pushes to its connected clients based on their subscriptions. A client subscribed to AAPL gets AAPL updates; a client subscribed to everything gets everything.

The key insight is that the expensive fan-out (one event to 10,000 clients) happens at the gateway layer, which is horizontally scalable. The matching engine only publishes each event once; it does not need to know how many subscribers exist.

## 4.4 Putting It All Together
Now that we have designed each subsystem, let's step back and see the complete architecture. We have also added a few supporting components we have not discussed yet: the Trade Database for persisting executed trades, and separate databases for orders and trades.
This architecture separates concerns cleanly. The critical path, from order submission to trade execution, flows through the center of the diagram. The matching engine sits at the heart, isolated from slow operations like database writes and market data distribution.

### Component Responsibilities
| Component | Primary Responsibility | Scaling Strategy |
| --- | --- | --- |
| API Gateway | Authentication, rate limiting | Horizontal (add instances) |
| Order Management | Order validation, lifecycle | Horizontal (stateless) |
| Risk Service | Balance checks, position limits | Horizontal with caching |
| Sequencer | Global ordering | Vertical (single leader) |
| Matching Engine | Order book, trade execution | Partition by symbol |
| Order Database | Order persistence, history | Sharding, read replicas |
| Trade Database | Trade persistence, audit | Time-based partitioning |
| Message Queue | Event distribution | Add partitions, brokers |
| Market Data Publisher | Event aggregation | Multiple consumers |
| Market Data Gateway | Client connections | Horizontal (add servers) |

Notice that the Sequencer and Matching Engine are the only components that cannot be trivially scaled horizontally. This is by design: the fairness requirement demands that all orders for a symbol flow through a single point for ordering. We will discuss how to scale these components in the deep dive.
# 5. Database Design
With the high-level architecture in place, let's zoom into the data layer. For a stock exchange, the database is not just a place to store data; it is a critical component that must support high write throughput, complex queries for regulatory reporting, and absolute correctness for financial transactions.

## 5.1 Choosing the Right Database
The choice between SQL and NoSQL databases is not always obvious. Let's think through our access patterns and requirements:

#### What we need to store:
- Orders with their full lifecycle (created, partially filled, filled, cancelled)
- Executed trades with references to both orders
- User accounts with cash balances
- User positions (which stocks they own)

#### How we access the data:
- Write 30,000+ trades per second at peak
- Query orders by user for account dashboards
- Query trades by time range for regulatory reporting
- Join orders and trades for audit purposes
- Update balances atomically during trade settlement

#### Consistency requirements:
- Trades must be durable immediately (regulatory requirement)
- Balances must be strongly consistent (no double-spending)
- Order state changes must be atomic

Given these requirements, a **relational database** is the right choice. Here is why:
**PostgreSQL for core data:** Orders, trades, accounts, and positions live in PostgreSQL. It provides the ACID guarantees we need, supports complex queries, and has excellent tooling for backup and replication.
**Redis for caching:** Order book snapshots, session data, and frequently accessed reference data (symbol lists, trading calendars) live in Redis for sub-millisecond access.
**Kafka for events:** Trade and order book events flow through Kafka for market data distribution and downstream processing.
**ClickHouse for analytics:** Historical trade data, time-series analysis, and regulatory reports run against ClickHouse, which is optimized for analytical queries over large datasets.

## 5.2 Database Schema
With our database choices made, let's design the schema. We have four main entities: Users, Orders, Trades, and financial state (Accounts and Positions).

### Orders Table
The orders table is the most heavily written table. Every order submission, fill update, and cancellation touches this table.
| Field | Type | Description |
| --- | --- | --- |
| order_id | UUID (PK) | Unique identifier for the order |
| user_id | UUID (FK) | Reference to the trader who placed the order |
| symbol | VARCHAR(10) | Stock symbol (e.g., "AAPL", "GOOGL") |
| side | ENUM | "BUY" or "SELL" |
| type | ENUM | "MARKET" or "LIMIT" |
| price | DECIMAL(18,8) | Limit price. Null for market orders. We use 8 decimal places to handle penny stocks and fractional trading |
| quantity | BIGINT | Total order quantity (number of shares) |
| filled_quantity | BIGINT | How many shares have been filled so far |
| status | ENUM | "PENDING", "PARTIALLY_FILLED", "FILLED", "CANCELLED" |
| sequence_number | BIGINT | The global sequence number assigned by the sequencer. Critical for replay and audit |
| created_at | TIMESTAMP | When the order was submitted |
| updated_at | TIMESTAMP | Last modification time |

**Indexes:**

### Trades Table
Every match produces a trade record. This table is append-only; trades are never updated or deleted.
| Field | Type | Description |
| --- | --- | --- |
| trade_id | UUID (PK) | Unique identifier for the trade |
| buy_order_id | UUID (FK) | Reference to the buy order |
| sell_order_id | UUID (FK) | Reference to the sell order |
| symbol | VARCHAR(10) | Stock symbol |
| price | DECIMAL(18,8) | Execution price |
| quantity | BIGINT | Number of shares traded |
| buyer_id | UUID | User ID of the buyer (denormalized for query efficiency) |
| seller_id | UUID | User ID of the seller |
| executed_at | TIMESTAMP | When the trade occurred |

We denormalize `buyer_id` and `seller_id` into the trades table even though they could be derived from the orders. This allows efficient queries like "show me all trades for user X" without joining to the orders table.

### Accounts Table
Tracks cash balances for each user. The "reserved" balance is critical for preventing double-spending.
| Field | Type | Description |
| --- | --- | --- |
| user_id | UUID (PK) | Unique identifier for the user |
| cash_balance | DECIMAL(18,2) | Available cash for trading |
| reserved_balance | DECIMAL(18,2) | Cash reserved for pending buy orders |
| updated_at | TIMESTAMP | Last balance change |

When a buy order is submitted, we move funds from `cash_balance` to `reserved_balance`. When the order fills, we deduct from `reserved_balance`. When the order is cancelled, we move funds back from `reserved_balance` to `cash_balance`. This two-column design prevents a trader from using the same money for multiple orders.

### Positions Table
Tracks stock holdings for each user.
| Field | Type | Description |
| --- | --- | --- |
| user_id | UUID (PK) | User identifier |
| symbol | VARCHAR(10) (PK) | Stock symbol. Combined with user_id forms the composite primary key |
| quantity | BIGINT | Number of shares owned |
| reserved_quantity | BIGINT | Shares reserved for pending sell orders |
| average_cost | DECIMAL(18,8) | Average purchase price (for P&L calculation) |
| updated_at | TIMESTAMP | Last position change |

The `reserved_quantity` works like `reserved_balance` for accounts: when a sell order is submitted, we reserve those shares so they cannot be sold twice.
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often go deeper into specific components. In this section, we will explore the trickiest parts of our design: the matching engine internals, sequencing for fairness, market data distribution at scale, risk management, fault tolerance, and scaling strategies.
These are the topics that distinguish a good system design answer from a great one. Let's dive in.

## 6.1 Matching Engine Design
The matching engine is the crown jewel of any exchange. Everything else, the APIs, the databases, the market data systems, exists to support this one component. The matching engine determines who trades with whom and at what price. Getting it wrong means unfair matches, lost money, and regulatory trouble.
Let's understand what makes matching engine design so challenging, and explore different approaches to building one.

### Design Goals
A well-designed matching engine must achieve several goals that often conflict with each other:
- **Ultra-low latency:** Process each order in microseconds. At 100,000 orders per second, we have 10 microseconds per order on average. Every memory allocation, every lock contention, every cache miss adds latency.
- **Strict fairness:** Price-time priority must be maintained perfectly. If trader A's order arrived before trader B's order at the same price, trader A must be matched first. Any deviation is a regulatory violation.
- **Deterministic behavior:** Given the same sequence of orders, the matching engine must produce exactly the same sequence of trades. This is essential for replay, auditing, and disaster recovery.
- **Zero data loss:** No order can be lost, duplicated, or processed out of sequence. Financial systems have no tolerance for "eventual consistency."

### Approach 1: Single-Threaded Event Loop
This is the most common approach used by high-performance exchanges, and for good reason. It sounds counterintuitive, why would a single thread be faster than many threads? But for this particular problem, single-threaded design wins.

#### How It Works
Each symbol (or group of symbols) has its own matching engine instance. Within that instance, a single thread processes orders one at a time in an infinite loop:
The loop never stops during trading hours. It pulls orders from the input queue, processes them against the order book, generates trades if matches are found, updates the order book, publishes events, and immediately moves to the next order.

#### Why Single-Threaded Wins
This seems backwards. We have servers with 128 cores, and we are using just one? Here is why it works:
**No locking overhead.** Multi-threaded designs require locks to protect shared data structures like the order book. Lock acquisition takes time. Lock contention causes threads to wait. Lock-free data structures are complex and still have synchronization overhead. A single thread needs no locks at all.
**Perfect cache locality.** The order book data structure lives in CPU cache (L1/L2). A single thread reading and writing to that cache has perfect locality. With multiple threads, cache lines bounce between cores (cache coherency protocol), causing delays. For latency-sensitive code, cache effects dominate.
**Deterministic by construction.** Orders go in one at a time, results come out in order. There is no possibility of race conditions, no "what if two threads grabbed the same order" scenarios. This makes debugging, testing, and replay trivial.
**Simplicity.** A single-threaded event loop is easy to reason about, easy to test, and easy to optimize. The code path is straightforward: read order, process order, output results. No concurrent programming bugs, no deadlocks, no subtle race conditions.

#### Order Book Data Structure
The order book is the data structure at the heart of the matching engine. It needs to support three operations efficiently:
- **Insert:** Add a new order at a price level
- **Cancel:** Remove a specific order from anywhere in the book
- **Match:** Find the best order on the opposite side to trade against

Here is how we structure it:

#### Two-level structure:
The order book has two levels. The outer level is a sorted map of price levels, sorted so the best price is easily accessible (highest price for bids, lowest for asks). We use a red-black tree or skip list here, giving O(log n) insertion and O(1) access to the best price.
The inner level is a FIFO queue of orders at each price level. Orders at the same price are matched in the order they arrived. We use a doubly linked list here, giving O(1) insertion at the tail and O(1) removal from anywhere (if we have a pointer to the order).

#### Best bid/ask pointers:
We maintain direct pointers to the best bid and best ask levels. This makes the most common operation, checking if a new order can match, an O(1) lookup instead of a tree traversal.

#### Order lookup map:
For cancellations, we need to find an order by ID quickly. We maintain a hash map from order_id to the order's location in the book. This makes cancel operations O(1) instead of searching through the entire book.

#### Trade-offs of Single-Threaded Design
**Pros:**
- Sub-microsecond matching latency is achievable
- No concurrency bugs, race conditions, or deadlocks
- Deterministic behavior makes testing and replay straightforward
- Simple code that is easy to optimize and maintain

**Cons:**
- Single point of failure: if the matching engine crashes, that symbol stops trading
- Limited by single-core performance: cannot use multiple CPUs for one symbol
- Scaling requires partitioning: each symbol (or symbol group) needs its own engine

### Approach 2: Partitioned Matching with Multiple Engines
When a single matching engine cannot handle all the load, or when you want fault isolation between symbols, you partition the workload across multiple engines.

#### How It Works
The key insight is that orders for different symbols are independent. An AAPL buy order never matches with a GOOGL sell order. So we can run separate matching engines for different symbols without breaking any matching rules.
A router sits in front of the matching engines and directs each order to the correct engine based on the symbol. The routing is deterministic: AAPL orders always go to Engine 1, JPM orders always go to Engine 2, and so on. We use consistent hashing so that adding or removing engines only requires moving a fraction of the symbols.

#### Trade-offs
**Pros:**
- Horizontal scalability: add more engines as volume grows
- Fault isolation: if Engine 2 crashes, AAPL and GOOGL keep trading normally
- Better hardware utilization: each engine runs on its own core/server

**Cons:**
- Added routing complexity: every order must be routed correctly
- Rebalancing overhead: adding/removing engines requires migrating symbols
- Operational complexity: more engines means more things to monitor and maintain

### Approach 3: LMAX Disruptor Pattern
The LMAX exchange, a UK-based foreign exchange trading platform, published a pattern called the "Disruptor" that achieves remarkable performance: 6 million transactions per second on a single thread. The key insight is eliminating all sources of latency jitter, including locks, garbage collection, and kernel calls.

#### How It Works
The Disruptor is built around a pre-allocated ring buffer. Instead of allocating new objects for each event (which triggers garbage collection), events are written into pre-existing slots in a circular array. Multiple consumers can read from the buffer without interfering with each other.
**Key techniques:**
- **Pre-allocation:** The ring buffer is allocated once at startup. No object creation during trading.
- **Mechanical sympathy:** Data structures are designed to match CPU cache line sizes (64 bytes), minimizing cache misses.
- **Memory barriers instead of locks:** Synchronization uses CPU memory barriers, which are faster than locks.
- **Single writer principle:** Only one producer writes to each slot, eliminating write contention.

#### Trade-offs
**Pros:**
- Eliminates garbage collection pauses entirely
- Achieves consistent sub-microsecond latency
- Throughput in the millions of operations per second

**Cons:**
- Significantly more complex to implement correctly
- Requires deep understanding of CPU architecture and memory models
- The original implementation is Java-specific; ports vary in quality

### Choosing the Right Approach
| Approach | Typical Latency | Throughput | Implementation Complexity | Best For |
| --- | --- | --- | --- | --- |
| Single-Threaded | Sub-microsecond | 100K+ orders/sec per symbol | Low | Most exchanges, startups |
| Partitioned | Microseconds | Millions orders/sec total | Medium | Large exchanges, many symbols |
| LMAX Disruptor | Sub-microsecond | Millions orders/sec | High | Ultra-high frequency trading |

#### Recommendation
Start with a single-threaded event loop per symbol. It is simple, fast, and correct. Partition across symbols as volume grows. Only consider the Disruptor pattern if you are building a world-class HFT venue and have engineers who deeply understand low-level systems programming.

## 6.2 Ensuring Fairness with Sequencing
Imagine two traders submit orders for the same stock at almost the same moment. Trader A sends their order a few milliseconds before Trader B. In a fair market, Trader A should be matched first. But what if Trader B has a faster network connection and their order arrives at the exchange before Trader A's order? Without proper sequencing, Trader B would be matched first, even though they acted second.
This is the fairness problem, and it is taken seriously by regulators. Exchanges must demonstrate that they process orders in a consistent, fair order. The solution is a sequencer.

### The Problem Without Sequencing
Here is what can go wrong:
1. Trader A sends order at T=0, arrives at T=5 (slow network).
2. Trader B sends order at T=2, arrives at T=3 (fast network).
3. Without sequencing, Trader B's order processes first even though A sent first.

This creates unfairness and regulatory issues.

### Approach 1: Gateway Timestamping
Assign timestamps at the API gateway when orders arrive.

#### How It Works
1. Order arrives at gateway.
2. Gateway assigns a timestamp (e.g., nanosecond precision).
3. Order is forwarded with timestamp attached.
4. Matching engine processes orders sorted by timestamp.

#### Pros
- Simple to implement.
- Fair based on arrival time at exchange boundary.

#### Cons
- Multiple gateways may have clock drift.
- Attackers could try to collocate near specific gateways.

### Approach 2: Central Sequencer
A dedicated service assigns strictly increasing sequence numbers.

#### How It Works
1. All orders flow through a central sequencer.
2. Sequencer assigns the next available sequence number.
3. Orders are forwarded to matching engines with sequence numbers.
4. Matching engines process orders in sequence order.

#### Pros
- **Strict ordering:** Deterministic, auditable sequence.
- **Regulatory compliance:** Clear audit trail of order priority.
- **Replay capability:** Can replay all events from any sequence number.

#### Cons
- **Single point of failure:** Sequencer unavailability halts all trading.
- **Potential bottleneck:** All orders must pass through one point.

### Approach 3: Distributed Sequencing
For higher availability, use a distributed consensus protocol.

#### How It Works
Use a consensus system like **Raft** or **Multi-Paxos** to agree on sequence numbers across multiple nodes:
1. Client sends order to any sequencer node.
2. Node proposes the order to the cluster.
3. Cluster reaches consensus on the sequence number.
4. Order is committed with agreed sequence number.

#### Pros
- **High availability:** Tolerates node failures (majority quorum).
- **Strong consistency:** All nodes agree on order sequence.

#### Cons
- **Higher latency:** Consensus requires multiple round trips (typically 2-5ms).
- **Complex operations:** Requires careful cluster management.

### Recommendation
Use a **primary sequencer with hot standby** for most exchanges:
1. Primary sequencer handles all sequencing.
2. All sequence assignments are replicated to standby synchronously.
3. If primary fails, standby takes over with no sequence gaps.

This provides sub-millisecond latency with high availability.

## 6.3 Handling High-Volume Market Data Distribution
The matching engine produces a stream of events: trades executed, orders added to the book, quotes changed. Thousands of traders, algorithmic systems, and data vendors want to receive these updates in real-time. Getting market data out quickly is not just a nice-to-have; it is a competitive advantage. Traders route orders to exchanges that give them faster information.
But the math is daunting. If we have 120,000 events per second and 10,000 subscribers, we need to deliver 1.2 billion messages per second. That is not something you solve with a simple "send to each subscriber in a loop." We need specialized distribution techniques.

### The Challenge
Let's quantify what we are dealing with:
- **High fanout:** Each update must reach 10,000+ subscribers simultaneously
- **Low latency:** Subscribers expect updates within single-digit milliseconds
- **Massive bandwidth:** 120,000 messages/sec × 10,000 subscribers = 1.2 billion message deliveries/sec

A naive implementation, looping through subscribers and sending each one a message, would take seconds. By that time, the data is stale and useless.

### Approach 1: Direct WebSocket Push
Each subscriber connects directly to a WebSocket server that pushes updates.

#### How It Works

#### Scaling Strategy
- **Horizontal scaling:** Add more WebSocket servers as clients grow.
- **Subscription routing:** Each server subscribes only to symbols its clients care about.
- **Connection limits:** Each server handles ~2,000-5,000 concurrent connections.

#### Pros
- Real-time, low latency.
- Simple client implementation.

#### Cons
- Expensive at scale (many servers needed).
- Each server must process all relevant messages.

### Approach 2: Hierarchical Distribution
Use a multi-tier architecture to reduce duplication of effort.

#### How It Works
1. **Message Queue:** Kafka or Kinesis receives all events once.
2. **Fan-out Layer:** Distribution servers consume from queue and push to edge servers.
3. **Edge Servers:** Located in different regions, close to clients.

#### Pros
- Efficient use of bandwidth (messages sent once to each tier).
- Geographic distribution reduces latency.

#### Cons
- Added latency from extra hops.
- More infrastructure to manage.

### Approach 3: Multicast/UDP
For ultra-low latency, use IP multicast within data centers.

#### How It Works
Instead of sending separate messages to each subscriber, send one message to a multicast group. All subscribers on the network receive it simultaneously.
**Typical setup:**
- One multicast stream per symbol or group of symbols.
- Clients join the multicast group for symbols they want.
- Single packet reaches all subscribers instantly.

#### Pros
- Lowest possible latency (single network transmission).
- Extremely efficient bandwidth usage.

#### Cons
- Only works within single network/data center.
- Requires specialized network infrastructure.
- UDP means no delivery guarantees (must handle packet loss).

### Recommendation
**Hybrid approach:**
1. Use **multicast** for premium co-located clients in the same data center.
2. Use **Kafka/Kinesis** for reliable distribution to regional edge servers.
3. Use **WebSocket** for retail clients connecting over the internet.

This provides optimal latency for professional traders while supporting retail clients at scale.

## 6.4 Risk Management and Circuit Breakers
Stock exchanges do not just match orders; they protect the market. Without safeguards, a single algorithmic bug could trigger a cascade of trades that wipes out billions in value. The 2010 "Flash Crash" saw the Dow Jones drop 1,000 points in minutes. The 2012 Knight Capital incident saw a firm lose $440 million in 45 minutes due to a software bug. Modern exchanges must have defenses against these scenarios.
Risk management happens at two levels: pre-trade checks that validate each order before it reaches the matching engine, and market-wide circuit breakers that halt trading when things go off the rails.

### Pre-Trade Risk Checks
Every order passes through a gauntlet of validations before it reaches the matching engine:
1. **Sufficient Funds:** Buy orders require enough cash balance.
2. **Sufficient Holdings:** Sell orders require enough share ownership.
3. **Position Limits:** Prevent any single trader from dominating a security.
4. **Order Size Limits:** Reject abnormally large orders (fat finger protection).
5. **Price Bands:** Reject orders too far from current market price.

### Circuit Breakers
Automatic trading halts when prices move too rapidly.

#### How They Work
**Level 1:** If price drops 7% from previous close, trading halts for 15 minutes.
**Level 2:** If price drops 13% from previous close, trading halts for 15 minutes.
**Level 3:** If price drops 20% from previous close, trading halts for remainder of day.

#### Implementation

### Limit Up/Limit Down (LULD)
More granular price bands that prevent trades outside acceptable ranges.
**How it works:**
- Calculate reference price (e.g., 5-minute average).
- Set price bands (e.g., +/- 5% for liquid stocks).
- Reject or queue orders outside the bands.
- Halt trading if price touches band for extended period.

## 6.5 Fault Tolerance and Recovery
What happens when the matching engine crashes? When a database goes down? When a network partition isolates part of your infrastructure? These questions keep exchange architects up at night. Financial systems require exceptional reliability, not just because downtime is expensive (though it is), but because inconsistency can be catastrophic. If the matching engine recovers with a different order book state than it had before the crash, traders might dispute their fills, and the exchange loses credibility.
The key to fault tolerance in exchanges is the combination of event sourcing, synchronous replication, and careful recovery procedures.

### Matching Engine Recovery
The matching engine's in-memory order book is transient. If the process crashes, that memory is gone. But we cannot lose any orders or trades. The solution is event sourcing: we treat the matching engine's state as a function of its inputs.

#### Event Sourcing Approach
1. **Log all inputs:** Every sequenced order is written to a durable log (Kafka, journal file).
2. **State is derived:** Order book state is computed by replaying the log.
3. **Periodic snapshots:** Periodically save order book state to reduce replay time.

**Recovery Process:**
1. Load latest snapshot (e.g., order book state at sequence 1,000,000)
2. Replay all events from sequence 1,000,001 to current
3. Resume processing new events

#### Why Event Sourcing?
- **Deterministic recovery:** Given same inputs, always reach same state.
- **Audit trail:** Complete history of all actions.
- **Point-in-time reconstruction:** Can rebuild state at any historical moment.

### Database Recovery
Use synchronous replication for critical data:
- **Primary database** handles all writes.
- **Synchronous replica** receives writes before primary acknowledges.
- On primary failure, promote replica with zero data loss.

### High Availability Architecture
**Key redundancy:**
- Multiple OMS instances behind load balancer.
- Sequencer with hot standby.
- Kafka cluster with replication factor 3.
- Database with synchronous replica.

## 6.6 Scalability Considerations
Our design handles 100,000 orders per second, but what if we need to handle 10x that? Or 100x? Scalability in exchange systems is tricky because some components (the sequencer, the matching engine for a single symbol) are inherently sequential. We cannot just add more servers and expect linear scaling.
The good news is that most components can scale horizontally, and even the sequential components can be partitioned. Here is how we scale each layer as volume grows.

### Horizontal Scaling Strategy
| Component | Scaling Approach |
| --- | --- |
| API Gateway | Add more instances behind load balancer |
| Order Management | Stateless, add instances as needed |
| Risk Service | Stateless, scale horizontally with caching |
| Sequencer | Vertical scaling (limited), or partition by symbol group |
| Matching Engine | Partition by symbol, one engine per symbol or group |
| Database | Shard by user_id (accounts), partition by time (trades) |
| Message Queue | Add Kafka partitions, more brokers |
| Market Data | Add edge servers, regional distribution |

### Database Partitioning
**Orders and Trades:** Partition by time (daily or monthly partitions). Enables efficient pruning of old data.
**Accounts and Positions:** Shard by user_id. Most queries are user-specific.

### Caching Strategy
- **Order book snapshots:** Cache in Redis for fast API responses.
- **User balances:** Cache with short TTL, invalidate on trades.
- **Symbol metadata:** Cache aggressively (rarely changes).

# References
- [The LMAX Architecture](https://martinfowler.com/articles/lmax.html) - Martin Fowler's explanation of LMAX Disruptor pattern
- [How Exchanges Work](https://www.investopedia.com/terms/s/stockmarket.asp) - Overview of stock exchange fundamentals
- [Raft Consensus Algorithm](https://raft.github.io/) - Understanding distributed consensus for sequencing
- [NYSE Market Model](https://www.nyse.com/market-model) - Real-world exchange architecture reference
- [Order Book Dynamics](https://web.stanford.edu/class/msande448/2018/Final/Reports/gr5.pdf) - Academic paper on order book implementation

# Quiz

## Design Stock Exchange Quiz
In a stock exchange, what is the primary purpose of the matching engine?