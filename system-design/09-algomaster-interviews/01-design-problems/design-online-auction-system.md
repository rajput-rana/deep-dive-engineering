# Design Online Auction System

## What is an Online Auction System?

An online auction system is a platform where sellers list items for sale and buyers compete by placing bids within a specified time window. The highest bidder at the end of the auction wins the item.
The core challenge lies in handling concurrent bids, ensuring fair winner determination, and providing real-time updates to all participants. Unlike traditional e-commerce where prices are fixed, auctions introduce time-sensitive competition that requires careful handling of race conditions and precise timing.
**Popular Examples:** [eBay](https://www.ebay.com/), [Christie's Online](https://www.christies.com/), [Sotheby's](https://www.sothebys.com/), [Heritage Auctions](https://www.ha.com/)
This system design problem tests your understanding of **concurrency control**, **real-time communication**, **time-sensitive distributed operations**, and **consistency guarantees**.
In this chapter, we will explore the **high-level design of an online auction system**.
Lets start by clarifying the requirements:
# 1. Clarifying Requirements
Before starting the design, it's important to ask thoughtful questions to uncover hidden assumptions, clarify ambiguities, and define the system's scope more precisely.
Here is an example of how a discussion between the candidate and the interviewer might unfold:
**Candidate:** "What is the expected scale? How many concurrent auctions and bids per day?"
**Interviewer:** "Let's design for 1 million active auctions at any time and 50 million bids per day."
**Candidate:** "What type of auction format should we support? English auction (ascending bids), Dutch auction (descending price), or sealed-bid?"
**Interviewer:** "Focus on English auction, the most common format where bidders openly compete with ascending bids."
**Candidate:** "Should we support features like reserve prices, automatic bidding (proxy bids), or buy-it-now?"
**Interviewer:** "Yes, support reserve prices (minimum price seller will accept), proxy bidding (system bids on behalf of user up to their max), and buy-it-now as optional features."
**Candidate:** "How critical is real-time bid visibility? Can there be a slight delay in showing new bids?"
**Interviewer:** "Bids must be visible to all participants within 1-2 seconds. Real-time experience is crucial for competitive auctions."
**Candidate:** "What happens when an auction ends? Should we handle payment and fulfillment?"
**Interviewer:** "Focus on winner determination and notification. Assume payment and fulfillment are handled by separate services."
**Candidate:** "Should we implement anti-sniping measures to prevent last-second bidding?"
**Interviewer:** "Yes, this is important. Consider extending the auction if bids come in near the end."
After gathering the details, we can summarize the key system requirements.

## 1.1 Functional Requirements
- **Item Listing:** Sellers can create auction listings with item details, starting price, reserve price, and duration.
- **Bid Placement:** Buyers can place bids on active auctions. Bids must exceed the current highest bid by a minimum increment.
- **Proxy Bidding:** Users can set a maximum bid amount, and the system automatically places minimum necessary bids on their behalf.
- **Real-time Updates:** All participants should see bid updates in near real-time (within 1-2 seconds).
- **Auction Closure:** When time expires, the system determines the winner (highest bidder above reserve price).
- **Buy-It-Now:** (Optional) Buyers can purchase immediately at a fixed price, ending the auction.

## 1.2 Non-Functional Requirements
Beyond features, we need to consider the qualities that make the system production-ready:
- **High Availability:** The system must be highly available (99.99%), especially during auction end times.
- **Low Latency:** Bid placement should complete within 100ms. Real-time updates within 1-2 seconds.
- **Strong Consistency:** Bid ordering must be strictly consistent. No two users should see different "current highest bids."
- **Scalability:** Handle millions of concurrent auctions and tens of millions of bids per day.
- **Fairness:** Bids must be processed in the order they are received. No bid should be lost or incorrectly rejected.

The consistency and fairness requirements are particularly interesting because they create tension with availability and performance. We will see how to navigate these trade-offs as we design the system.
# 2. Back-of-the-Envelope Estimation
Before diving into architecture, let's run some numbers to understand the scale we are dealing with. These calculations will guide our decisions about database choice, caching strategy, and infrastructure sizing.

### 2.1 Traffic Estimates

#### Bid Traffic (Writes)
Starting with the numbers from our requirements: 50 million bids per day. Let's convert this to queries per second:
Traffic is never uniform. During peak hours, when popular auctions are ending and bidding activity intensifies, we might see 3x the average load:
But here is where auctions get interesting: they have extreme traffic spikes. When a high-profile auction (a celebrity memorabilia item, a rare collectible) enters its final minutes, thousands of users may try to bid simultaneously. During these moments, we might see **10,000+ QPS** bursts lasting a few minutes. Our system needs to handle these spikes without dropping bids.

#### Auction Views (Reads)
Users spend far more time browsing and watching auctions than actually placing bids. Assume a 50:1 read-to-write ratio, which accounts for page loads, bid history refreshes, search queries, and real-time auction monitoring:
This read-heavy workload suggests we should invest heavily in caching. Most of these reads are for auction details that do not change frequently, perfect candidates for aggressive caching.

### 2.2 Real-time Connection Estimates
One of the unique challenges of an auction system is real-time updates. Every user watching an auction needs to receive bid updates within 1-2 seconds.
50 million concurrent WebSocket connections is substantial. Each connection consumes memory (for connection state, buffers) and requires periodic heartbeats. We will need multiple WebSocket servers and a pub/sub system to fan out updates efficiently.

### 2.3 Storage Estimates
Let's estimate how much data we need to store.

#### Per Auction:
- Item metadata (title, description, seller info): ~2 KB
- Image URLs and references: ~500 bytes
- Bid history (average 20 bids × 100 bytes per bid): ~2 KB
- Auction state (current price, status, timestamps): ~200 bytes

Total per auction: approximately **5 KB**

#### Annual Growth:
Assuming 10 million new auctions per year (about 27,000 per day):
The bid history grows much faster than auction metadata. This is not surprising since a single auction can have hundreds of bids from different users.
| Data Type | Annual Volume | Notes |
| --- | --- | --- |
| Auction Metadata | ~50 GB | Relatively small, cacheable |
| Bid Records | ~1.8 TB | Append-only, grows fast |
| Images | Variable | Stored in object storage, not counted here |

### 2.4 Key Insights
These estimates reveal several important design implications:
1. **Read-heavy workload:** With a 50:1 read-to-write ratio, caching is essential. Most auction data changes infrequently between bids.
2. **Bursty traffic:** The spike during hot auction endings (10,000+ QPS) is 5-6x our peak steady-state. We need capacity headroom and graceful degradation.
3. **Real-time scale:** 50 million concurrent WebSocket connections requires distributed infrastructure and efficient pub/sub.
4. **Storage is manageable:** 2 TB per year for bids is well within the capacity of modern databases. Storage is not our primary constraint.

# 3. Core APIs
With our requirements and scale understood, let's define the API contract. The auction system needs endpoints for three main workflows: sellers creating listings, buyers placing bids, and everyone viewing auction details. 
Getting these interfaces right matters because they shape how clients interact with our system and influence backend design decisions.

### 3.1 Create Auction Listing

#### Endpoint: POST /auctions
This endpoint allows sellers to list an item for auction. The seller provides item details, pricing configuration, and timing information.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| title | string | Yes | Item title, displayed prominently to buyers |
| description | string | Yes | Detailed item description including condition, provenance, etc. |
| starting_price | decimal | Yes | Opening bid amount. The first bid must be at least this much |
| reserve_price | decimal | No | Minimum price the seller will accept. If not met, item does not sell |
| buy_now_price | decimal | No | Instant purchase price. Buyer can skip bidding entirely |
| end_time | timestamp | Yes | When the auction closes (must be in the future) |
| images | array | Yes | URLs of item photos (already uploaded via a separate media service) |
| category_id | integer | Yes | Category for browsing and search organization |

#### Example Request:

#### Success Response (201 Created):

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Invalid input | end_time in the past, negative price, missing required fields |
| 401 Unauthorized | Not authenticated | No valid session or token |
| 403 Forbidden | Not allowed to sell | User's account is suspended or unverified |

### 3.2 Place Bid

#### Endpoint: POST /auctions/{auction_id}/bids
This is the most critical endpoint in our system. When a user clicks "Place Bid," this is what gets called. The response must come back quickly, and the bid must be processed fairly even under high concurrency.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| amount | decimal | Yes | The bid amount (must exceed current price plus minimum increment) |
| max_amount | decimal | No | Maximum for proxy bidding. System bids on user's behalf up to this amount |

#### Example Request:
This user is bidding $155,000 but is willing to go up to $175,000 automatically if outbid.

#### Success Response (200 OK):
The `leading` field tells the user immediately whether they are winning. This is important for user experience since they should not have to refresh to find out.
**Possible `status` values:**
- `accepted`: Bid was placed successfully
- `outbid`: Your bid was placed but immediately outbid by a higher proxy bid
- `rejected`: Bid was too low or auction is closed

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Bid too low | Amount does not meet minimum increment over current price |
| 404 Not Found | Auction not found | Invalid auction_id |
| 409 Conflict | Race condition | Auction ended or state changed during processing |
| 410 Gone | Auction closed | Item already sold via buy-now or auction ended |

The distinction between 409 and 410 is intentional. A 409 suggests the user should retry (maybe with a higher amount), while a 410 means the opportunity has passed entirely.

### 3.3 Get Auction Details

#### Endpoint: GET /auctions/{auction_id}
Retrieves the current state of an auction. This is called frequently, both by users viewing auctions and by our own frontend polling for updates (as a fallback if WebSocket disconnects).

#### Success Response (200 OK):
Notice that `high_bidder_id` is anonymized. We do not reveal the actual user ID to prevent harassment or collusion. The user only sees something like "Bidder ***45" in the UI.

### 3.4 Get Bid History

#### Endpoint: GET /auctions/{auction_id}/bids
Returns the history of bids for transparency. Users can see how the price evolved over time.

#### Query Parameters:
| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| limit | integer | 50 | Number of bids to return |
| offset | integer | 0 | Pagination offset |

#### Success Response (200 OK):
Bids are returned in reverse chronological order (most recent first) since that is what users typically want to see.
# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complex diagram upfront, we will build the design incrementally, starting with the simplest components and adding complexity as we address each requirement. This mirrors how you would explain the design in an interview and makes the reasoning easier to follow.
Our system needs to handle four main operations:
1. **Item Listing:** Sellers create and manage auction listings
2. **Bid Processing:** Accept and validate bids with strong consistency
3. **Real-time Updates:** Push bid notifications to all watching users
4. **Auction Closure:** Determine winners when time expires

Before we dive in, let's recognize an important characteristic of our workload. The system has two very different traffic patterns that benefit from different optimizations:
**Bid placement** (the write path) requires strong consistency and low latency. When two people bid at the same time, we must process them in order and ensure everyone sees the same result. This path needs careful concurrency control.
**Auction browsing** (the read path) is much higher volume but can tolerate slightly stale data. If you see the bid count as 42 for a few seconds after it becomes 43, that is acceptable. This path benefits from aggressive caching.
This asymmetry suggests we should optimize these paths differently. Let's build the architecture piece by piece.

## 4.1 Requirement 1: Item Listing
Let's start with the simplest flow: a seller creating an auction listing. This is a straightforward CRUD operation, but it sets up the foundation that other components will build on.
When a seller wants to list an item, they need to provide details about the item, set pricing rules (starting price, optional reserve, optional buy-now), upload photos, and specify when the auction ends. Our system needs to validate this information, store it durably, and make it discoverable to potential buyers.

### Components Needed

#### API Gateway
Every request enters through the API Gateway. It handles concerns common to all requests: SSL termination, authentication, rate limiting, and request routing. By handling these at the edge, we keep our internal services focused on business logic.

#### Auction Service
This is the core service for managing auction lifecycle. It handles creation, updates, status changes, and cancellation. The service is intentionally stateless so we can run multiple instances behind a load balancer.
Key responsibilities:
- Validate listing details (ensuring prices are positive, end_time is in the future, required fields are present)
- Generate unique auction IDs
- Store auction metadata in the database
- Publish events for downstream systems (search indexing, notifications)
- Handle modifications (only allowed before any bids are placed)

#### Media Service
Handles image uploads separately from the auction creation flow. Sellers upload images first, receive CDN URLs, then include those URLs in their auction listing. This separation simplifies the main creation flow and allows for image processing (thumbnails, optimization) to happen asynchronously.

#### Search Index
An Elasticsearch or similar index that enables buyers to discover auctions. When an auction is created, we publish an event that the search system consumes to update its index.

### The Create Flow in Action
Let's walk through this step by step:
1. **Request arrives at API Gateway:** The seller sends a POST request with item details. The gateway authenticates the user and checks that they have not exceeded their rate limit for creating listings.
2. **Auction Service validates:** The service checks that all required fields are present, prices are sensible (starting price > 0, reserve >= starting, etc.), and the end time is in the future.
3. **Generate auction ID:** We create a unique identifier for this auction. This could be a UUID or a custom ID scheme (similar to the key generation we discussed for Pastebin).
4. **Store in database:** The auction record is inserted into PostgreSQL with status "active" (or "scheduled" if start_time is in the future).
5. **Publish for search:** We emit an event that the search indexer will pick up asynchronously. The auction becomes searchable within a few seconds.
6. **Return to seller:** The response includes the auction ID and URL. The seller can now share this link.

This is a clean, straightforward flow. The interesting complexity comes when we add bidding.

## 4.2 Requirement 2: Bid Processing
Now we reach the heart of the system. Bid processing is where auctions get interesting and where most of the complexity lives. This is not just about saving a record to a database. We need to:
- Validate that the bid exceeds the current price by the minimum increment
- Handle the case where two people bid at the exact same moment
- Process proxy bids (automatically bidding on behalf of users)
- Ensure that every user sees the same "current highest bid"
- Reject bids that arrive after the auction closes

Getting any of these wrong leads to disputes, lost trust, and potentially legal issues. A user who legitimately placed a winning bid must actually win. This is why we separate bid processing into its own service with its own carefully designed consistency guarantees.

### Why a Separate Bid Service?
We could handle bids in the Auction Service, but there are good reasons to separate them:
1. **Different consistency requirements:** Auction viewing can be eventually consistent and heavily cached. Bid processing must be strongly consistent.
2. **Different scaling patterns:** We might need to scale bid processing independently during hot auctions.
3. **Isolation of complexity:** The concurrency control logic for bids is complex. Keeping it isolated makes the code easier to reason about and test.
4. **Different latency profiles:** Bid placement has a strict 100ms target. Viewing an auction can tolerate slightly higher latency.

### Components Needed

#### Bid Service
A dedicated service for all bid operations. It handles validation, concurrency control, and bid placement.
Key responsibilities:
- Validate bids against current auction state
- Implement concurrency control (we will discuss strategies in the deep dive)
- Process proxy bidding logic
- Emit events for real-time updates and notifications

#### Concurrency Control Mechanism
When two bids arrive simultaneously for the same auction, we need a way to process them correctly. This could be optimistic locking, pessimistic locking, or partitioned processing. We will explore these options in detail in the deep dive section.

### The Bid Flow in Action
Let's trace through what happens when a user places a bid:
1. **Request arrives:** The bidder sends a POST request with their bid amount (and optionally a max_amount for proxy bidding).
2. **Fetch current state:** The Bid Service retrieves the auction's current state from the database. Critically, this read must be done in a way that prevents concurrent modifications, either by acquiring a lock or by using optimistic concurrency.
3. **Validate the bid:** Is the auction still active? Has it ended? Is the bid amount at least current_price plus the minimum increment? If the bid is for proxy bidding, is the max_amount higher than the current max proxy bid?
4. **Apply the bid:** If valid, we insert a new bid record and update the auction's current_price in the same transaction. This atomicity is crucial.
5. **Release lock and publish event:** Once the database transaction commits, we publish a bid_placed event to the event bus. This triggers real-time updates to watchers and notifications to the previous high bidder.
6. **Return response:** The bidder learns immediately whether they are now winning.

The tricky part is handling concurrent bids. What if Alice and Bob both try to bid $160 on an auction currently at $150? Only one can win. We will discuss the strategies for handling this in the deep dive section on concurrency control.

## 4.3 Requirement 3: Real-time Updates
Imagine you are watching an auction in its final minutes. Someone else places a bid. If you do not see that bid for 10 seconds, you might think you are still winning when you are not. Or worse, you might place a bid that is already lower than the current price. Real-time updates are essential for a competitive auction experience.
Our requirement is to push bid updates to all watchers within 1-2 seconds. With 50 million concurrent WebSocket connections across 1 million active auctions, this is a significant infrastructure challenge. Let's design the real-time update system.

### The Challenge
Traditional HTTP is request-response: the client asks, the server answers. For real-time updates, we need the server to push data to clients without waiting for a request. WebSockets provide this capability by maintaining a persistent connection between client and server.
But there is a complication. Users watching a particular auction might be connected to different WebSocket servers. When a bid is placed, how does the update reach all of them?
User A and B are connected to WebSocket Server 1, but User C is connected to Server 2. When a bid arrives, both servers need to know about it so they can notify their respective users.

### Components Needed

#### WebSocket Gateway
A fleet of servers that maintain persistent connections with clients. Each server handles 100K-500K connections (depending on hardware). Clients connect when they open an auction page and subscribe to updates for that auction.
Responsibilities:
- Accept WebSocket connections and manage their lifecycle
- Track which connections are interested in which auctions
- Receive events from the message broker and fan out to relevant clients
- Handle heartbeats and reconnection logic

#### Message Broker (Pub/Sub)
The glue that connects bid events to WebSocket servers. When a bid is placed, the Bid Service publishes an event. All WebSocket servers subscribed to that auction's channel receive the event and push to their connected clients.
We have several options here:
- **Redis Pub/Sub:** Simple, low latency, good for moderate scale
- **Kafka:** Higher throughput, message persistence, better for large scale
- **Managed services (AWS SNS/SQS, Google Pub/Sub):** Operational simplicity at scale

For our scale (50M connections, 580 bids/second average), Redis Pub/Sub or Kafka would work well.

### The Real-time Update Flow
Here is how it works:
1. **Bid is processed:** The Bid Service accepts a bid and commits it to the database.
2. **Event published:** The service publishes a `bid_placed` event to the message broker with the auction ID, new price, anonymized bidder ID, and timestamp.
3. **Fan out to WebSocket servers:** Every WebSocket server has subscribed to channels for the auctions their clients are watching. The broker delivers the event to all relevant servers.
4. **Push to clients:** Each WebSocket server looks up which of its connected clients are watching this auction and pushes the update to them.
5. **UI updates:** Clients receive the message and update their display: new current price, new bid count, and possibly a notification if they have been outbid.

### Fallback for Disconnected Clients
WebSocket connections can drop due to network issues. Clients should:
- Automatically attempt reconnection with exponential backoff
- Fall back to HTTP polling if WebSocket fails
- Request the current state on reconnect to catch any missed updates

The client should never assume its view is current. A "last updated" timestamp and periodic reconciliation ensure users see accurate information even if they miss a push notification.

## 4.4 Requirement 4: Auction Closure
Every auction has an end time. When that moment arrives, several things need to happen precisely:
1. No more bids should be accepted
2. The winner (if any) must be determined
3. All parties need to be notified: winner, seller, and losing bidders
4. The auction state must transition permanently to "ended" or "sold"

This sounds simple, but there is a subtle challenge: how do we know exactly when an auction ends? We have 1 million active auctions, each with its own end time. We cannot poll the database every second asking "has anything expired?" That would be too expensive.

### The Timing Challenge
Consider what happens in the final seconds of a popular auction. Bids are flying in. The end time arrives. What if a bid is "in flight" when the auction closes? Did it arrive in time or not?
We need a system that:
- Triggers closure at the right moment (within seconds of the end time)
- Handles "in-flight" bids gracefully
- Ensures exactly-once closure (an auction cannot close twice)
- Scales to millions of concurrent timers

### Components Needed

#### Scheduler Service
A dedicated service that tracks when auctions should close and triggers the closure process. We will discuss implementation strategies (polling, delay queues, timing wheels) in the deep dive.
Key responsibilities:
- Monitor active auctions for approaching end times
- Trigger closure at the right moment
- Handle anti-sniping extensions (adjust end time if late bids arrive)
- Retry failed closures

#### Notification Service
After an auction closes, we need to notify the relevant parties. This is a separate concern from the closure logic itself.
Responsibilities:
- Send winner notification with next steps (payment instructions, seller contact)
- Notify seller of sale completion (or no sale if reserve not met)
- Notify losing bidders that the auction has ended
- Handle notification preferences (email, push, SMS)

### The Closure Flow
Let's walk through what happens:
1. **Scheduler triggers:** The Scheduler Service detects that auction 123's end time has passed. It sends a closure request to the Auction Service.
2. **Lock and verify:** The Auction Service acquires a lock on the auction (to prevent concurrent closures) and verifies it is still in "active" status. If it is already closed, we return early.
3. **Handle in-flight bids:** Any bids that arrived before the end time but have not been processed yet should still be considered. We give a small grace period (a few seconds) for in-flight requests.
4. **Determine outcome:** Check if the highest bid meets or exceeds the reserve price.
5. **Notify parties:** Publish an `auction_closed` event that the Notification Service picks up. It sends appropriate messages to all parties.

### Anti-Sniping Extension
Remember our anti-sniping requirement? If a bid arrives in the final 5 minutes, we extend the auction by 5 minutes. This changes the closure logic slightly:
1. When a bid arrives, check if we are in the extension window
2. If so, extend the end_time
3. The Scheduler needs to update its timer for this auction

This prevents the frustrating experience of losing to a last-second bid you had no time to counter.

## 4.5 Putting It All Together
Now that we have designed each component, let's step back and see the complete architecture. This is the picture you would draw on a whiteboard at the end of the design discussion.
The architecture follows a layered approach, with each layer having a specific responsibility:
**Client Layer:** Users interact with our system through web browsers, mobile apps, or programmatic API clients. They establish two types of connections: HTTP for API calls (routed through CDN and Load Balancer) and WebSocket for real-time updates.
**Edge Layer:** The CDN caches static content and can cache read-only auction data. The Load Balancer distributes traffic across API Gateway instances, providing redundancy and scaling.
**Gateway Layer:** The API Gateway handles authentication, rate limiting, and request routing. The WebSocket Gateway maintains persistent connections for real-time updates.
**Application Layer:** This is where the business logic lives.
- **Auction Service:** Creates and manages auction listings, handles lifecycle operations
- **Bid Service:** Processes bids with concurrency control, the most critical service
- **Search Service:** Powers auction discovery and filtering
- **Notification Service:** Sends emails, push notifications, SMS to users
- **Scheduler Service:** Monitors end times and triggers auction closures

**Cache Layer:** Redis provides fast access to hot data: current prices, session state, and frequently accessed auction details.
**Message Layer:** The Message Broker (Kafka or Redis Pub/Sub) enables asynchronous communication. Bid events flow to WebSocket servers for real-time updates and to the Notification Service for alerts.
**Storage Layer:** PostgreSQL stores structured data (users, auctions, bids). Elasticsearch powers full-text search. Object Storage (S3) holds images and media.

### Component Responsibilities Summary
| Component | Purpose | Scaling Strategy |
| --- | --- | --- |
| API Gateway | Auth, rate limiting, routing | Horizontal (add instances) |
| WebSocket Gateway | Real-time updates | Horizontal with sticky sessions |
| Auction Service | Listing management, lifecycle | Horizontal (stateless) |
| Bid Service | Bid processing, concurrency | Horizontal with partitioning |
| Search Service | Discovery, filtering | Horizontal (read replicas) |
| Scheduler Service | Closure triggers | Leader election pattern |
| Notification Service | User notifications | Horizontal with queuing |
| PostgreSQL | Structured data | Primary + read replicas |
| Redis | Caching, pub/sub | Redis Cluster |
| Elasticsearch | Search index | Horizontal sharding |
| Message Broker | Event distribution | Kafka partitions or Redis Cluster |

This architecture handles our requirements: strong consistency for bids, real-time updates for watchers, reliable auction closure, and the ability to scale each component independently as traffic grows.
# 5. Database Design
With the high-level architecture in place, let's zoom into the data layer. The database choices we make here directly impact performance, consistency, and the complexity of our application code. For an auction system, getting the data model right is especially important because of the strong consistency requirements around bidding.

## 5.1 Choosing the Right Database
The database choice is not always obvious. Let's think through our access patterns and requirements:

#### What we need to store:
- Auction listings with metadata, pricing, and timing
- User accounts and profiles
- Bid history (potentially hundreds of bids per auction)
- Watchlist and user preferences

#### How we access the data:
- Primary pattern: lookup auction by ID (constant time)
- Bid processing: read current price, insert bid, update current price (must be atomic)
- Discovery: search auctions by category, price range, ending soon
- User dashboard: list user's auctions and bids

#### Consistency requirements:
- Bid processing must be strongly consistent: no lost updates, no incorrect current prices
- Auction viewing can tolerate slight staleness (eventually consistent reads are fine)

Let's evaluate our options:

### Why PostgreSQL for Core Data?
A relational database like PostgreSQL is well-suited for our core auction and bid data:
1. **ACID transactions:** We can update the auction's current price and insert a bid record in a single atomic transaction. This is critical for bid consistency.
2. **Strong consistency:** PostgreSQL guarantees that once a transaction commits, all subsequent reads see that data. No risk of two users seeing different "current prices."
3. **Flexible querying:** We can efficiently query by auction ID, user ID, category, price range, or end time with proper indexing.
4. **Mature operations:** Backup, replication, monitoring, and recovery are well-understood. PostgreSQL has decades of production hardening.

### Why Not NoSQL for Core Data?
Document databases like MongoDB or DynamoDB are tempting for their simplicity and horizontal scaling. But for auctions, they create challenges:
- **Consistency:** Most NoSQL databases offer eventual consistency by default. Achieving strong consistency requires careful configuration and often sacrifices performance.
- **Transactions:** Updating multiple documents atomically (auction + bid) is more complex in NoSQL.
- **Querying flexibility:** Document databases shine for single-document lookups but struggle with complex queries across relationships.

For our scale (50M bids/day, ~1M auctions), a well-configured PostgreSQL with read replicas handles the load comfortably. NoSQL would add complexity without clear benefits.

### Specialized Stores for Specialized Needs
We do use non-relational stores where they make sense:
- **Elasticsearch:** Powers auction search and discovery. Fast full-text search, faceted filtering, geolocation queries.
- **Redis:** Caches hot auction data. Reduces database load and provides sub-millisecond latency for frequently accessed auctions.
- **Object Storage (S3):** Stores auction images. Optimized for large binary files with global CDN distribution.

## 5.2 Database Schema
With PostgreSQL as our primary store, let's design the schema. We have four main tables: Users, Auctions, Bids, and Watchlist. The relationships are straightforward, but the details matter for performance.

### Users Table
Stores account information for all users (buyers and sellers).
| Field | Type | Description |
| --- | --- | --- |
| user_id | UUID (PK) | Unique identifier. UUID prevents enumeration attacks |
| email | VARCHAR(255) | Unique email for login and notifications |
| username | VARCHAR(100) | Display name shown on auctions and bids |
| password_hash | VARCHAR(255) | bcrypt hash of password |
| seller_rating | DECIMAL(3,2) | Average rating as seller (1.00-5.00) |
| buyer_rating | DECIMAL(3,2) | Average rating as buyer (1.00-5.00) |
| created_at | TIMESTAMP | Account creation time |

### Auctions Table
This is the heart of our schema. Each row represents one auction listing.
| Field | Type | Description |
| --- | --- | --- |
| auction_id | UUID (PK) | Unique identifier for the auction |
| seller_id | UUID (FK) | Who is selling this item |
| title | VARCHAR(200) | Item title shown in listings |
| description | TEXT | Full description with condition, history, etc. |
| category_id | INT (FK) | Category for browsing and search |
| starting_price | DECIMAL(12,2) | Opening bid amount |
| reserve_price | DECIMAL(12,2) | Minimum for valid sale (nullable, hidden from buyers) |
| buy_now_price | DECIMAL(12,2) | Instant purchase option (nullable) |
| current_price | DECIMAL(12,2) | Current highest bid |
| current_max_bid | DECIMAL(12,2) | Hidden max proxy bid (for proxy bidding logic) |
| bid_count | INT | Number of bids, for display |
| winner_id | UUID (FK) | Winning bidder (null until auction ends) |
| status | ENUM | 'draft', 'scheduled', 'active', 'ended', 'sold', 'cancelled' |
| start_time | TIMESTAMP | When bidding opens |
| end_time | TIMESTAMP | Current end time (may be extended for anti-sniping) |
| original_end_time | TIMESTAMP | Original scheduled end (before any extensions) |
| version | INT | For optimistic locking on concurrent updates |
| created_at | TIMESTAMP | When listing was created |

**Why `current_max_bid`?** This hidden field stores the highest proxy bid maximum. We need it to correctly process new bids against existing proxy bids, but we never expose it to users.
**Why `version`?** For optimistic locking. When updating the auction, we check that the version has not changed since we read it.
**Indexes:**

### Bids Table
Stores every bid ever placed. This is an append-only table since bids are never modified after creation.
| Field | Type | Description |
| --- | --- | --- |
| bid_id | UUID (PK) | Unique identifier for the bid |
| auction_id | UUID (FK) | Which auction this bid is for |
| bidder_id | UUID (FK) | Who placed the bid |
| amount | DECIMAL(12,2) | The visible bid amount |
| max_amount | DECIMAL(12,2) | User's maximum for proxy bidding (nullable) |
| is_proxy | BOOLEAN | True if this bid was auto-placed by proxy logic |
| status | ENUM | 'winning', 'outbid', 'cancelled' |
| created_at | TIMESTAMP | Precise timestamp for ordering |

**Indexes:**

### Watchlist Table
Simple many-to-many relationship tracking which users are watching which auctions.
| Field | Type | Description |
| --- | --- | --- |
| user_id | UUID (FK) | Who is watching |
| auction_id | UUID (FK) | What they are watching |
| created_at | TIMESTAMP | When they added it |

**Primary Key:** (user_id, auction_id) ensures no duplicate entries.
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often probe deeper into specific components. In this section, we will explore the trickiest parts of our design: handling concurrent bids, implementing proxy bidding, preventing sniping, scheduling auction closures, and scaling real-time updates.
These are the topics that distinguish a good answer from a great one. Understanding the trade-offs here shows you can reason about complex distributed systems.

## 6.1 Handling Concurrent Bids
This is arguably the most critical part of our system. Consider this scenario: an auction is at $100. Alice and Bob both see this price. They both click "Bid $110" at the exact same moment. What should happen?
Without proper handling, we risk:
- **Lost updates:** Both bids are "accepted" but only one is recorded. The other user thinks they are winning when they are not.
- **Invalid state:** The current price shows $110, but the database has inconsistent data.
- **Unfair ordering:** Bob's bid was processed first (due to server load), even though Alice clicked earlier.

A robust bid system must guarantee:
- **Atomicity:** Reading the current price, validating the bid, and updating the price happen as one indivisible unit.
- **Consistency:** At any moment, current_price equals the highest valid bid. Every user sees the same value.
- **Fairness:** If two bids arrive at the same price, the one that arrived first wins.

Let's explore three approaches to achieving these guarantees.

### Approach 1: Optimistic Locking
The idea behind optimistic locking is simple: assume conflicts are rare, and handle them when they happen rather than preventing them upfront.
Each auction has a `version` column that increments with every update. When processing a bid, we read the current version, do our validation, then attempt an update that will only succeed if the version has not changed.
**How It Works:**
**Pros:**
- No locking overhead during reads
- High throughput when conflicts are rare
- Simple implementation using standard SQL

**Cons:**
- Under high contention, many retries occur ("retry storm")
- Wasted computation: validation repeats on each retry
- Potentially unfair: faster clients can retry more times

**Best for:** Auctions with moderate bid frequency where conflicts are uncommon.

### Approach 2: Pessimistic Locking (SELECT FOR UPDATE)
The opposite philosophy: assume conflicts are likely, so prevent them by acquiring an exclusive lock before doing any work.
PostgreSQL's `SELECT FOR UPDATE` acquires a row-level lock that blocks other transactions from modifying (or locking) the same row until we commit or rollback.
**How It Works:**
**Pros:**
- Guaranteed consistency: no lost updates, no race conditions
- Predictable behavior: bids are processed one at a time, in order
- Simple reasoning: no retry logic needed

**Cons:**
- Reduced throughput: bids queue up waiting for the lock
- Lock contention: hot auctions become bottlenecks
- Deadlock risk: if multiple locks are needed, deadlocks can occur

**Best for:** High-value auctions where consistency is more important than throughput. Also useful for lower-traffic systems where contention is rare.

### Approach 3: Partition by Auction (Recommended)
This approach takes a different angle: instead of managing concurrent access to the database, we eliminate concurrency at the application layer. All bids for a specific auction are routed to a single processing node, which handles them sequentially.
Think of it like having dedicated checkout lanes at a store. Each auction gets its own lane, and bids line up in order. Different auctions can be processed in parallel (different lanes), but bids for the same auction are processed one at a time.
**How It Works:**
The key insight is that within each partition, bids are processed in FIFO order with no concurrency. This means no locks, no retries, and guaranteed fairness.
**Pros:**
- High throughput: different auctions processed in parallel across processors
- No distributed locks: single-threaded processing eliminates race conditions
- Fair ordering: FIFO queue guarantees first-in-first-served
- Scalable: add more partitions as load increases

**Cons:**
- Partition imbalance: a viral auction can overload its assigned processor
- Operational complexity: need to manage partition assignment and handle processor failures
- Single point of failure per partition: if a processor dies, its auctions are affected until failover

**Best for:** Large-scale production systems with many concurrent auctions.

### Choosing the Right Strategy
| Strategy | Throughput | Consistency | Complexity | Best For |
| --- | --- | --- | --- | --- |
| Optimistic Locking | Medium | Strong (with retries) | Low | Low-moderate traffic |
| Pessimistic Locking | Low (per auction) | Strong | Low | High-value auctions |
| Partition by Auction | High | Strong | Medium | Large-scale systems |

**Our Recommendation:** Use **Partition by Auction** as the primary approach for a production system. It provides the best balance of throughput, consistency, and fairness at scale.
For hot auctions that might overwhelm a single partition (celebrity memorabilia, limited editions), consider:
- Dedicated processing capacity for known high-profile auctions
- Rate limiting per user to prevent bid spam
- Queueing with capacity limits and backpressure

## 6.2 Proxy Bidding (Automatic Bidding)
Proxy bidding is one of the most user-friendly features of modern auction systems. Instead of requiring users to sit at their computers watching an auction, they can set a maximum amount they are willing to pay, and the system bids on their behalf.
The concept is simple: "I am willing to pay up to $500 for this item. Bid the minimum necessary to keep me winning, but never exceed $500." The system automatically responds to competing bids without user intervention.

### How Proxy Bidding Works
Let's walk through a complete example:

#### Step-by-step:
1. Auction for a rare book starts at $20.
2. **Alice** sets a proxy bid with max = $100. The system places a bid of $25 (current price + increment) on her behalf. Displayed price: $25, Alice is winning.
3. **Bob** bids $30. The system automatically responds with $35 for Alice (minimum to beat Bob). Displayed price: $35, Alice still winning.
4. **Bob** now sets his own proxy bid with max = $50. The system compares: Alice's max ($100) beats Bob's max ($50).
5. The price becomes $55 (Bob's max $50 + increment $5). Alice is winning at $55, even though her max is $100. Bob is notified he has been outbid.

### The Implementation Logic
Here is the core algorithm for processing a bid with proxy support:

### Key Design Decisions

#### Hiding Maximum Bids
The `current_max_bid` is never exposed to users. They only see:
- The current winning price
- Whether they are winning or outbid
- Their own maximum bid amount

If users could see others' maximum bids, they could game the system by bidding just $1 more. The hidden nature of proxy bids encourages users to bid their true value.

#### Tie Breaking
When two users set the same maximum:
- The earlier bid wins (first-in-first-out)
- The displayed price is set at the tied amount

This is fair because the first person to commit to that price gets priority.

#### Increment Calculation
The minimum bid increment typically scales with price to keep bidding manageable:
| Current Price | Minimum Increment |
| --- | --- |
| $0 - $50 | $1 |
| $50 - $100 | $2 |
| $100 - $500 | $5 |
| $500 - $1,000 | $10 |
| $1,000+ | $25 |

This prevents absurd situations where a $10,000 item climbs by $0.01 increments.

## 6.3 Anti-Sniping Mechanisms
If you have ever used eBay, you have probably experienced sniping: someone places a bid in the final seconds of an auction, and you have no time to respond. You watch helplessly as the item slips away.
Sniping is frustrating for most users, and it can actually reduce final sale prices. If bidders fear being sniped, they may not engage as actively during the auction, waiting to snipe themselves.

### The Sniping Problem
The sniper wins at $105. But if other bidders had time to respond, someone might have bid $110, $120, or more. The seller loses potential revenue, and other buyers feel cheated.

### Approach 1: Soft Close (Auto-Extension) - Recommended
The most common anti-sniping mechanism: if a bid is placed within the final N minutes, extend the auction by M minutes. This gives everyone a fair chance to respond.

#### How It Works:
**Pros:**
- Gives all bidders a fair chance to respond
- Often increases final sale price
- Simple to understand: "Bids in final 5 minutes extend the auction"

**Cons:**
- Auctions can run longer than the stated end time
- Must limit extensions to prevent indefinite auctions
- Need to communicate clearly ("Original end: 3:00 PM, Current end: 3:25 PM")

**Best for:** Most auction platforms, especially for high-value items.

### Approach 2: Rely on Proxy Bidding
Instead of extending time, let proxy bidding handle sniping naturally. If users set their true maximum upfront, a last-second bid simply triggers the proxy to respond.
**How it helps:**
- Even if someone snipes at 2:59:58 PM, your proxy bid responds instantly
- If the sniper's bid exceeds your max, you would not have won anyway
- Encourages users to think carefully about their true value

**Cons:**
- Does not help users who forget to set a proxy
- Some users prefer manual bidding and the thrill of competing

### Recommendation
Use **Soft Close (Auto-Extension)** as the primary mechanism with clear user communication:
1. Display both "Original end time" and "Current end time" prominently
2. Show a countdown that updates when extensions occur
3. Notify all watchers: "Auction extended by 5 minutes due to a late bid"
4. Cap extensions (e.g., maximum 12 extensions = 1 extra hour)

## 6.4 Auction Scheduling and Closure
Every auction has an end time. When that moment arrives, the system must close the auction and determine the winner. This sounds simple, but consider the scale: 1 million active auctions, each with its own end time, potentially changing due to anti-sniping extensions. How do we reliably trigger closure at the right moment?

### The Scheduling Challenge
We cannot just poll the database every second asking "which auctions have expired?" That would crush our database and still not be precise enough for auctions ending exactly when expected.
We need a system that:
- Triggers closure within seconds of the scheduled end time
- Handles millions of concurrent timers efficiently
- Adjusts when end times change (anti-sniping extensions)
- Ensures exactly-once closure (an auction must not close twice)

### Approach 1: Polling (Simple, Not Recommended)
The naive approach: a background worker periodically queries for expired auctions.
**Pros:** Simple to implement.
**Cons:**
- Latency: auctions might wait up to the polling interval to close
- Database load: scanning all active auctions every minute is expensive
- Does not scale well with millions of auctions

This might work for a small system, but it is not suitable for production scale.

### Approach 2: Delay Queues with Redis (Recommended)
A much better approach: use Redis sorted sets as a priority queue of upcoming closures, ordered by end time.
**How It Works:**
**Pros:**
- Precise timing (second-level accuracy)
- Efficient: only processes auctions that are actually ending
- Scales well: Redis sorted sets handle millions of entries
- Easy to update: ZADD replaces existing entries

**Cons:**
- Need to handle worker failures (maybe duplicate processing)
- Redis memory limits for very large auction counts

### Ensuring Exactly-Once Closure
Even with a good scheduling mechanism, we might trigger closure twice (worker retry, race condition). The closure logic must be idempotent: running it twice should produce the same result as running it once.
The key is the `WHERE status = 'active'` check combined with `FOR UPDATE`. If another worker already closed the auction, the SELECT returns no rows, and we exit early. The database transaction guarantees that only one worker can successfully close each auction.

## 6.5 Real-time Updates at Scale
When Alice places a bid, Bob (who is watching the same auction) needs to see that bid almost immediately. Not in 30 seconds, not when he refreshes the page, but within a second or two. This real-time feedback is what makes auctions exciting and competitive.
With 50 million concurrent WebSocket connections spread across 1 million active auctions, this is a significant infrastructure challenge. How do we efficiently route bid updates to only the users who care about them?

### The Message Routing Problem
When a bid is placed on auction #123:
1. We need to notify all 50 users watching that auction
2. These users are connected to different WebSocket servers
3. We should not bother the other 49,999,950 users

The naive approach of broadcasting every bid to every server is wasteful. At 580 bids per second, each server would receive 580 messages per second and discard 99% of them.

### Approach: Topic per Auction (Recommended)
The elegant solution is to treat each auction as a separate channel. WebSocket servers subscribe only to the auctions their clients are watching.
**Implementation with Redis Pub/Sub:**

#### Why this works well:
- Servers only receive messages for auctions they care about
- Subscription management is straightforward
- Redis Pub/Sub handles the fan-out efficiently
- Easy to scale by adding more WebSocket servers

### Connection Management at Scale
With 50 million connections, each WebSocket server might handle 100K-500K connections. We need efficient data structures to track who is watching what.
Each server maintains two in-memory maps:
1. **Forward map:** Given a connection, which auctions is it watching?
2. **Reverse map:** Given an auction, which connections are watching it?

When a message arrives for auction #123, the server looks up the reverse map and sends to all relevant connections in O(1) per connection.

### Graceful Degradation
WebSocket connections will drop. Networks are unreliable, phones go to sleep, browsers get closed. The system must handle this gracefully:
1. **Heartbeats:** Send periodic pings to detect dead connections
2. **Auto-reconnect:** Clients should reconnect automatically with exponential backoff
3. **State sync on reconnect:** When reconnecting, fetch current auction state to catch up on missed updates
4. **Fallback to polling:** If WebSocket fails repeatedly, fall back to HTTP polling (every 5-10 seconds)

The user should never see a completely stale auction. Even in degraded mode, they should get updates within 10-15 seconds.

## 6.6 Handling High-Profile Auctions
Not all auctions are equal. Most auctions have a handful of bidders and close quietly. But occasionally, an auction goes viral: a celebrity's memorabilia, a rare collectible, a historic artifact. These "hot" auctions create traffic patterns that can overwhelm even well-designed systems.
Consider what happens when a famous musician's guitar goes up for auction:
- 100,000+ people watching simultaneously
- Thousands of bids in the final minutes
- Media coverage driving traffic spikes
- Global audience across all time zones

Our partitioned architecture handles most auctions well, but a single hot auction can become a bottleneck since all its bids route to one processor.

### The Hotspot Problem
Processor 2 is overwhelmed while processors 1 and 3 sit idle. We need strategies to handle these spikes.

### Strategy 1: Dedicated Resources for Known Hot Auctions
When we know an auction will be hot (scheduled celebrity auction, high-value art), we can prepare:
- **Dedicated bid processor:** Assign a beefy server specifically for this auction
- **Pre-provisioned WebSocket capacity:** Spin up extra servers before the auction peaks
- **Separate read replicas:** Direct view traffic to dedicated database replicas

This works when we have advance notice, which we often do for high-profile items.

### Strategy 2: Rate Limiting
Even with dedicated resources, we need to prevent abuse:
This prevents a single user (or bot) from overwhelming the system while still allowing legitimate bidding activity.

### Strategy 3: Batched Updates for Viewers
When 100,000 people are watching an auction that receives 100 bids per second, we do not need to push every single bid. Watchers care about the current price and whether they are winning, not individual bid events.
Batching over 500ms windows can reduce message volume by 80%+ without meaningfully degrading the user experience. The countdown timer and current price are what matter most.

### Strategy 4: CDN Edge Caching for Read Traffic
Most users watching a hot auction are just spectators. They want to see the current price, not place bids. We can serve this read traffic from CDN edge nodes:
- Cache auction state with 1-2 second TTL
- Viewers get slightly stale data (acceptable)
- Bidders get fresh data directly from origin
- Reduces origin load by 90%+ for hot auctions

The tradeoff is acceptable: a viewer seeing "$150" for 1 second after it became "$155" is fine. The bidder who needs to make a decision needs fresh data, and they get it.
# Quiz

## Design Online Auction System Quiz
For bid placement, which data consistency approach best supports a fair, single “current highest bid” seen by all users?