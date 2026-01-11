# Design Real-Time Gaming Leaderboard

## What is a Real-Time Leaderboard?

A real-time leaderboard is a ranking system that displays participants ordered by their scores and pushes live updates to all viewers as scores change. Unlike traditional leaderboards that refresh periodically, real-time leaderboards show ranking changes within milliseconds of a score update.
The core challenge is maintaining accurate rankings while simultaneously broadcasting updates to millions of connected viewers. When a participant scores, the system must update the ranking, determine which positions changed, and notify all relevant clients, all within a tight latency budget.
**Popular Examples:** leaderboards in online games, fitness apps, or platforms like Kaggle competitions.
What makes this problem interesting from a system design perspective is the **fan-out** challenge. 
A single score update might need to reach millions of connected viewers. If 10 updates happen per second and each one affects 8 million viewers watching the top 100, you are looking at 80 million messages per second. That is not a problem you can brute-force with bigger servers.
This system design problem combines several fundamental concepts: efficient ranking data structures, real-time communication, massive fan-out patterns, and consistency challenges under high concurrency.
In this chapter, we will dive into the **high-level design of a real-time leaderboard system.**
Let’s begin by clarifying the requirements.
# 1. Clarifying Requirements
Before starting the design, it's important to ask thoughtful questions to uncover hidden assumptions, clarify ambiguities, and define the system's scope more precisely.
Here is an example of how a discussion between the candidate and the interviewer might unfold:
**Candidate:** "What is the expected scale? How many participants and concurrent viewers should the system handle?"
**Interviewer:** "Let's design for 1 million active participants who can update scores, and 10 million concurrent viewers watching the leaderboard. During peak events like tournaments, expect 10,000 score updates per second."
**Candidate:** "How quickly should viewers see ranking changes after a score update?"
**Interviewer:** "Updates should be visible within 500 milliseconds. This is critical for maintaining the 'live' experience."
**Candidate:** "Should all viewers see the entire leaderboard, or just specific portions?"
**Interviewer:** "Viewers typically watch the top 100 rankings. Some viewers also want to track a specific participant's position. We should support both use cases."
**Candidate:** "Do we need to handle multiple simultaneous leaderboards, like different game modes or regional competitions?"
**Interviewer:** "Yes, the system should support thousands of concurrent leaderboards. Each tournament or event creates its own leaderboard."
**Candidate:** "How do we handle ties when two participants have the same score?"
**Interviewer:** "The participant who achieved the score first should rank higher."
**Candidate:** "Should we persist historical rankings, or is current state sufficient?"
**Interviewer:** "We need to persist final rankings after events end, but during live events, durability can be eventual. Losing a few seconds of data during a failure is acceptable if we can recover quickly."
After gathering the details, we can summarize the key system requirements.

## 1.1 Functional Requirements
Based on the discussion, here are the core features our system must support:
- **Submit Score:** Participants can submit score updates during an active event.
- **Get Leaderboard:** Fetch the current top N rankings for a leaderboard.
- **Subscribe to Updates:** Viewers can subscribe to receive real-time ranking changes.
- **Get Participant Rank:** Retrieve a specific participant's current rank and score.
- **Track Participant:** Subscribe to updates for a specific participant's position changes.

The distinction between subscription types is important. A viewer watching the top 100 needs updates when any position in that range changes. A viewer tracking their friend at rank 50,000 only cares when that specific person moves. This difference has significant implications for our fan-out strategy.

## 1.2 Non-Functional Requirements
Beyond features, we need to consider the qualities that make the system production-ready:
- **Real-Time Updates:** Ranking changes must reach viewers within 500ms of the score update.
- **High Availability:** The system must be highly available (99.99% uptime) during live events.
- **Scalability:** Handle 10,000 score updates/second and 10 million concurrent WebSocket connections.
- **Low Latency:** Score submissions acknowledged within 50ms, leaderboard fetches within 100ms.
- **Consistency:** All viewers should see the same ranking order (no split-brain scenarios).
- **Graceful Degradation:** If real-time push fails, clients should fall back to polling.

# 2. Back-of-the-Envelope Estimation
Before diving into the architecture, let's run some quick calculations to understand the scale we are dealing with. These numbers will guide our design decisions, particularly around the fan-out strategy and infrastructure requirements.

### 2.1 Traffic Estimates
Let's start with the numbers from our requirements discussion and work through what they mean in practice.

#### Write Traffic (Score Updates)
During peak events like tournament finals, we expect 10,000 score updates per second. During calmer periods, perhaps 1,000 per second. Each update is relatively small (participant ID, score, timestamp), but the downstream impact is significant: every update potentially triggers rank recalculation and broadcasting.

#### Read Traffic (Leaderboard Queries and Subscriptions)
The read side is where things get interesting. We have 10 million concurrent viewers, each maintaining a WebSocket connection. Based on typical usage patterns, roughly 80% of viewers (8 million) watch the top 100 rankings, while 20% (2 million) track specific participants.

### 2.2 The Fan-out Challenge
This is where the math gets scary. Let's work through a worst-case scenario.
Not every score update affects the top 100. Most score updates happen somewhere in the middle or bottom of the rankings. But during an intense competition, updates to the top 100 are frequent. Let's assume 100 of our 10,000 peak updates per second affect the top 100.
Eight hundred million messages per second. That is the core challenge of this system. A single server sending messages at 10,000/second would take 22 hours to deliver one second's worth of updates. Clearly, we need a different approach.
This calculation reveals why naive designs fail and why we will need hierarchical fan-out, message batching, and smart subscription segmentation.

### 2.3 Storage Estimates
Storage requirements are surprisingly modest compared to the fan-out challenge. Each leaderboard entry needs to store:
| Component | Size | Description |
| --- | --- | --- |
| Participant ID | 16 bytes | UUID or similar identifier |
| Score | 8 bytes | 64-bit integer for large scores |
| Timestamp | 8 bytes | For tie-breaking |
| Metadata | ~32 bytes | Display name reference, avatar ID |
| Total | ~64 bytes | Per leaderboard entry |

Now let's project storage growth:
64 GB fits comfortably in a Redis cluster. Even with 10,000 concurrent events (a stretch goal), we are looking at 640 GB, still manageable with modern infrastructure. Storage is not our bottleneck.

### 2.4 Bandwidth Estimates
Let's calculate the bandwidth required for broadcasting updates:
80 GB/second is substantial. For context, a 10 Gbps network connection handles ~1.25 GB/second. We would need roughly 64 such connections just for broadcasting, not counting overhead. This confirms that we need distributed infrastructure across many servers.

### 2.5 Key Insights
These estimates reveal several important design implications:
1. **Fan-out is the bottleneck:** Storage and write throughput are manageable. The challenge is delivering updates to millions of viewers simultaneously. This shapes our entire architecture.
2. **Subscription type matters:** Updates to the top 100 are expensive (8M recipients each). Updates to rank 50,000 are cheap (only that user's trackers). We should optimize differently for each.
3. **Batching is essential:** Sending individual messages for every update is infeasible. Batching updates over short windows (50-100ms) can reduce message volume dramatically.
4. **Hierarchical distribution:** A single server cannot reach 8 million viewers quickly. We need multiple layers of fan-out to parallelize the delivery.

# 3. Core APIs
With our requirements and scale understood, let's define the API contract. Unlike a simple CRUD API, a real-time leaderboard has two distinct interaction patterns: synchronous HTTP requests for submissions and queries, and persistent WebSocket connections for live updates. Getting this interface right matters because clients will build their entire user experience around it.
Let's walk through each endpoint.

### 3.1 Submit Score

#### Endpoint: POST /v1/leaderboards/{leaderboard_id}/scores
This is the primary write endpoint. When a participant completes an action that affects their score, their client sends this request. The system records the score, recalculates rankings, and returns the participant's new position.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| participant_id | string | Yes | Unique identifier for the participant |
| score | integer | Yes | The new score value (absolute, not delta) |
| timestamp | integer | No | Client-side timestamp in milliseconds for tie-breaking. If omitted, server time is used |

#### Example Request:

#### Success Response (200 OK):
We return both the new rank and previous rank because this information is essential for client-side animations. That satisfying "rank up" animation needs to know where the participant started.

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Invalid input | Score is negative, participant_id is missing, or malformed request |
| 404 Not Found | Leaderboard not found | The leaderboard_id does not exist or the event has ended |
| 429 Too Many Requests | Rate limited | Participant exceeded their score submission quota (prevents spamming) |

### 3.2 Get Leaderboard

#### Endpoint: GET /v1/leaderboards/{leaderboard_id}/rankings
This is the primary read endpoint. When a viewer opens the leaderboard page, this is the first request their client makes to populate the initial view. Subsequent updates come through the WebSocket subscription, but this endpoint provides the starting state.

#### Query Parameters:
| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| limit | integer | No | 100 | Number of entries to return (max 1000) |
| offset | integer | No | 0 | Starting position for pagination |
| around | string | No | - | Participant ID to center the view around (returns entries above and below) |

#### Success Response (200 OK):
The `version` field is important. It is a monotonically increasing number that changes with every ranking update. Clients use this to detect missed updates when reconnecting after a disconnection, which we will discuss in the WebSocket section.

#### Error Response:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 404 Not Found | Leaderboard not found | The leaderboard_id does not exist |

### 3.3 Subscribe to Leaderboard Updates

#### WebSocket Endpoint: wss://api.example.com/v1/leaderboards/{leaderboard_id}/subscribe
This is where the real-time magic happens. Viewers establish a persistent WebSocket connection and specify what portion of the leaderboard they want to track. The server then pushes ranking changes as they occur.

#### Subscription Message (sent by client after connection):
For watching the top N rankings:
For tracking a specific participant:
The `since_version` parameter helps with reconnection. If a client disconnects and reconnects, they can provide the last version they saw. The server will send any missed updates, or tell the client to fetch a fresh snapshot if the gap is too large.

#### Update Message (pushed by server):
Notice that the message includes all positions that changed, not just the participant who scored. When Player456 moves from rank 5 to rank 3, Players 789 who were at ranks 3 and 4 get bumped down. The client needs this information to update all affected rows in the UI.

### 3.4 Get Participant Rank

#### Endpoint: GET /v1/leaderboards/{leaderboard_id}/participants/{participant_id}
A convenience endpoint for looking up a specific participant's position. This is useful when a viewer wants to see where their friend ranks without scanning through potentially millions of entries.

#### Success Response (200 OK):
The `neighbors` array shows participants immediately above and below. This gives context, helping viewers understand how close the competition is at their level.

### 3.5 API Design Considerations
A few design decisions worth noting:
**Absolute scores, not deltas:** We accept absolute scores rather than increments. This is intentional. If we accepted deltas (+100 points), we would need to track current score server-side and handle race conditions when multiple updates arrive simultaneously. Absolute scores are idempotent: if the same request is sent twice, the result is the same.
**Version numbers for consistency:** Every response includes a version number. This enables optimistic concurrency: clients can detect if they missed updates and recover gracefully.
**Unified update format:** Whether the server pushes an update or the client fetches the leaderboard, the data format for rankings is consistent. This simplifies client implementation.
# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complex diagram upfront, we will build the design incrementally, starting with the simplest possible solution and adding components as we encounter challenges. This mirrors how you would approach the problem in an interview.
Our system needs to handle three fundamental operations:
1. **Score Ingestion:** Accept score updates from participants and record them quickly
2. **Rank Computation:** Maintain accurate rankings as scores change
3. **Real-Time Broadcasting:** Push ranking changes to millions of connected viewers

The critical insight that shapes our entire architecture is this: **not every score update is equally expensive to broadcast**. A score change at rank 50,000 only matters to the handful of people tracking that specific participant. A change in the top 10 must reach 8 million viewers watching the top 100. This asymmetry drives our optimization strategy.
Notice how the write path is relatively straightforward: scores flow into Redis, which maintains the rankings. The challenge is the read path, where a single score update might need to fan out to millions of viewers. Let's build each path step by step.


When a participant submits a score, several things need to happen behind the scenes:
1. Validate the request (is this a real participant? is the event still active?)
2. Update the ranking data structure
3. Determine which positions changed (not just the scorer, but everyone who got bumped)
4. Publish an event so the broadcasting system can notify viewers
5. Return the new rank to the participant

Let's introduce the components we need to make this work.

### Components for Score Ingestion

#### API Gateway
Every request enters through the API Gateway. Think of it as the front door to our system. It handles concerns that are common across all requests: SSL termination, authentication, rate limiting, and routing to the appropriate backend service.
For score submissions, the gateway verifies that the participant is authenticated (they cannot submit scores for other players), checks rate limits (preventing spam submissions), and forwards valid requests to the Score Service.

#### Score Service
This is the brain of our write operations. It orchestrates the entire score submission workflow: validating input, updating Redis, computing rank changes, and publishing events.
We want this service to be stateless so we can run multiple instances behind the load balancer. All state lives in Redis, making horizontal scaling straightforward. If we need to handle more score submissions, we simply add more Score Service instances.

#### Redis Sorted Sets
Redis Sorted Sets are the heart of our ranking system. A sorted set stores members (participant IDs) with associated scores, automatically maintaining them in sorted order. This gives us exactly the operations we need:
| Operation | Redis Command | Complexity | Use Case |
| --- | --- | --- | --- |
| Update score | ZADD | O(log N) | Record a new score |
| Get rank | ZREVRANK | O(log N) | Find participant's position |
| Get top N | ZREVRANGE | O(log N + M) | Fetch leaderboard |
| Get score | ZSCORE | O(1) | Check current score |

With 1 million participants, O(log N) means about 20 operations to update a score and fetch the new rank. Redis handles this in microseconds.

### The Score Submission Flow
Let's walk through this step by step:
1. **Request arrives at API Gateway:** The participant sends a POST request with their score. The gateway validates the authentication token and checks rate limits.
2. **Score Service takes over:** Once validated, the request moves to the Score Service. It performs business-level validation, like checking that the event is still active and the score is within acceptable bounds.
3. **Get current rank:** Before updating, we fetch the participant's current rank. This is important because we need to know where they were to calculate which positions shifted.
4. **Update score:** The Score Service calls `ZADD leaderboard:123 15000 user_456` to update the score. Redis atomically updates the sorted set.
5. **Get new rank:** We fetch the new rank to see where the participant landed after the update.
6. **Compute affected positions:** If the participant moved from rank 5 to rank 3, then the participants who were at ranks 3 and 4 got bumped down to 4 and 5. We need to identify all affected positions for the broadcast.
7. **Publish event:** The Score Service publishes a `RankChangeEvent` to the Event Bus. This event contains the leaderboard ID, the affected rank range, and the details of all position changes.
8. **Return response:** Finally, we return the new rank to the participant so they can see their updated position immediately.

**Why fetch rank before and after the update?** We need to know the old rank to calculate the `delta` (positions gained/lost) and to determine which other participants were affected. This information is essential both for the API response and for the broadcast to viewers.


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
        S1[one Service]
        S2[single Service]
        S3[Leaderboard Service]
        S4[any Service]
        S5[out Service]
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



## 4.2 Requirement 2: Real-Time Broadcasting
Now for the more interesting part: the read path. This is the core differentiator from a traditional leaderboard. Instead of viewers constantly polling "has anything changed?", the system pushes updates to them as they happen. This requires maintaining persistent connections with millions of viewers and efficiently routing updates to the right recipients.

### Components for Real-Time Updates

#### WebSocket Gateway
The WebSocket Gateway is the bridge between our backend and the viewer's browser. It maintains persistent connections with millions of viewers, handles the WebSocket protocol (handshake, heartbeats, reconnection), and pushes updates to connected clients.
A single server can typically handle 100,000 to 1,000,000 WebSocket connections, depending on hardware and how much work happens per message. With 10 million viewers, we need a fleet of WebSocket Gateway servers.

#### Subscription Manager
When a viewer connects and says "I want to watch the top 100", we need to remember that. The Subscription Manager maintains this registry: which connections are subscribed to which leaderboards and what type of subscription they have.
This is essentially a mapping:
- `leaderboard:123:top_100` → [connection_1, connection_2, ... connection_8M]
- `leaderboard:123:track:user_456` → [connection_5, connection_99]

When a ranking change happens, we query this registry to find who needs to know.

#### Fan-out Service
The Fan-out Service is the coordinator. It consumes rank change events from the Event Bus, figures out which subscribers need each update, and routes the messages to the appropriate WebSocket Gateways.
This is where the 800 million messages/second challenge lives. A naive implementation would have a single service trying to send 8 million messages for each top-100 update, and it would immediately fall over. We will address this shortly.

#### Event Bus (Kafka)
The Event Bus decouples the write path from the read path. When the Score Service finishes processing a score update, it publishes an event and moves on. It does not wait for the broadcast to complete. The Fan-out Services consume these events asynchronously and handle the broadcasting.
This decoupling is important for two reasons: the Score Service can return quickly to the participant, and we can scale the fan-out infrastructure independently from the score ingestion infrastructure.

### The Broadcasting Flow
Let's trace through what happens when a score update triggers a broadcast:
1. **Event arrives:** The Fan-out Service receives a `RankChangeEvent` from the Event Bus. The event contains the leaderboard ID, the range of affected ranks (say, 3-5), and the details of what changed.
2. **Identify subscribers:** The Fan-out Service queries the Subscription Manager to find all connections that care about this update. This includes everyone watching the top 100 (since positions 3-5 are in that range) and anyone specifically tracking the affected participants.
3. **Route to gateways:** The connection IDs include information about which WebSocket Gateway owns each connection. The Fan-out Service sends the update payload to each relevant gateway.
4. **Push to viewers:** Each WebSocket Gateway takes the update and pushes it to its connected clients over their existing WebSocket connections.

### Why Subscription Types Matter
Not all subscriptions have the same fan-out cost:
| Subscription Type | Who Receives Updates | Typical Fan-out |
| --- | --- | --- |
| Top 100 | Anyone watching positions 1-100 | 8 million viewers |
| Track Participant | Friends following a specific person | 10-1000 viewers |
| Relative View | Viewers watching positions near their rank | 100-10,000 viewers |

This is why we designed different subscription types. A change at rank 5 is expensive (8 million recipients), but most changes happen outside the top 100 and only affect a handful of people tracking specific participants. By segmenting subscriptions, we can optimize the common case while still handling the expensive case correctly.

## 4.3 Requirement 3: Handling Massive Fan-out
We have talked about the 800 million messages per second problem. Now let's actually solve it. When a top 10 position changes, we need to notify 8 million viewers, and we need to do it in under 500 milliseconds. This is where naive designs fall apart.

### The Problem, Quantified
Let's do the math on why a single-server approach cannot work:
Even if we could send messages faster, a single server cannot push 8 million messages before the next update arrives. We need parallelism.

### Solution: Hierarchical Fan-out
The key insight is that fan-out does not have to happen all at once. Instead of one service sending to all clients, we use a tree structure where each level multiplies the distribution.

#### How it works:
1. **Level 0 (Event Source):** The Event Bus publishes the rank change event once. Multiple Fan-out Services consume this event in parallel.
2. **Level 1 (Fan-out Services):** Each Fan-out Service is responsible for a subset of WebSocket Gateways. When an event arrives, each Fan-out Service determines which of its gateways have affected subscribers and forwards the update.
3. **Level 2 (WebSocket Gateways):** Each gateway receives the update and broadcasts it to all relevant connections it manages. This is the most expensive step, but it happens in parallel across all gateways.

**Let's recalculate the latency:**
The magic is that each level fans out in parallel. We are not sending 8 million messages sequentially; we are sending 1 million messages each from 8 different servers simultaneously.

### Connection Router
When a viewer first connects, they need to be assigned to a WebSocket Gateway. The Connection Router handles this assignment, balancing several concerns:
- **Load balancing:** Distribute connections evenly across gateways
- **Geographic proximity:** Assign viewers to nearby gateways for lower latency
- **Subscription affinity:** When possible, group viewers watching the same leaderboard on the same gateway to simplify fan-out

The router returns a WebSocket URL pointing to the assigned gateway. The viewer's client connects directly to that gateway for all subsequent communication.

## 4.4 Putting It All Together
Now that we have designed each piece, let's step back and see the complete architecture. The system has two distinct traffic patterns: participants submitting scores through HTTP, and viewers receiving updates through WebSockets. These paths share some infrastructure (Redis, the Event Bus) but are otherwise independent.
The architecture follows a layered approach, with each layer having specific responsibilities:
**Client Layer:** Participants interact through HTTP APIs to submit scores. Viewers connect via WebSockets to receive real-time updates. The clients are fundamentally different: participants make occasional requests, while viewers maintain persistent connections.
**Edge Layer:** The API Gateway handles all HTTP traffic, providing authentication and rate limiting. The Connection Router directs new WebSocket connections to appropriate gateways based on load and geography.
**Application Layer:** The Score Service handles score submissions and ranking updates. The Leaderboard Service handles read queries (top N, participant lookup). The Subscription Manager tracks which connections care about which updates.
**Event Layer:** Kafka acts as the spine connecting the write path to the read path. Score updates flow in, rank change events flow out to the fan-out layer.
**Fan-out Layer:** Multiple Fan-out Services consume events in parallel and route updates to the appropriate WebSocket Gateways. This is where we handle the massive parallelism required to reach millions of viewers quickly.
**WebSocket Layer:** A fleet of WebSocket Gateways, each managing around 1 million connections, handles the actual delivery of updates to viewers.
**Storage Layer:** Redis stores live rankings using Sorted Sets, providing O(log N) updates and lookups. PostgreSQL stores historical data: final rankings after events end, audit logs of score changes for debugging.

### Component Responsibilities
| Component | Primary Responsibility | Scaling Strategy |
| --- | --- | --- |
| API Gateway | Auth, rate limiting, routing | Horizontal (stateless) |
| Connection Router | WebSocket assignment | Horizontal (stateless) |
| Score Service | Score updates, rank computation | Horizontal (stateless) |
| Leaderboard Service | Read queries | Horizontal (stateless) |
| Subscription Manager | Track subscriptions | Redis-backed, horizontal |
| Fan-out Service | Route updates to gateways | Horizontal (partitioned by leaderboard) |
| WebSocket Gateway | Client connections | Horizontal (~1M connections each) |
| Redis | Live rankings | Redis Cluster (sharded) |
| PostgreSQL | Historical data | Primary + read replicas |
| Kafka | Event streaming | Partitioned by leaderboard_id |

### Data Flow Summary
| Operation | Path | Latency Target |
| --- | --- | --- |
| Score Submit | Participant → API Gateway → Score Service → Redis | < 50ms |
| Get Rankings | Viewer -> API -> Leaderboard Service -> Redis | < 100ms |
| Subscribe | Viewer -> Router -> WS Gateway -> Subscription Manager | < 100ms |
| Push Update | Redis -> Event Bus -> Fan-out -> WS Gateway -> Viewer | < 500ms |

# 5. Database Design
With the high-level architecture in place, let's zoom into the data layer. A real-time leaderboard has an interesting storage challenge: during live events, we need sub-millisecond access to rankings, but after events end, we need to persist results for historical queries. This leads us to a two-tier storage strategy.

## 5.1 Storage Strategy
The key insight is that live rankings and historical records have fundamentally different access patterns:

#### Live Rankings (during events):
- Accessed thousands of times per second
- Must support O(log N) updates
- Need sub-millisecond latency
- Can tolerate some data loss on failure (eventual persistence is acceptable)

#### Historical Records (after events):
- Accessed occasionally for analysis
- Read-only once finalized
- Can tolerate higher latency
- Must be durable and consistent

This suggests a two-tier approach: Redis for hot data during live events, PostgreSQL for cold data after events complete.
When an event ends, we snapshot the final rankings from Redis to PostgreSQL, then free up the Redis memory for the next event. This keeps Redis lean (only active events) while maintaining a complete history in PostgreSQL.

## 5.2 Redis Schema
Redis stores four categories of data for our leaderboard system. Let's look at each and understand why we chose specific data structures.

### Leaderboard Rankings (Sorted Set)
The rankings themselves live in Redis Sorted Sets, the perfect data structure for leaderboards. Each sorted set stores all participants in a single leaderboard, with their scores as the sort key.
The composite score deserves explanation. Redis Sorted Sets only support numeric scores, but we need to handle ties where the first to achieve a score ranks higher. We solve this by encoding the timestamp into the fractional part of the score:
When two users have the same integer score, the one with the larger decimal (earlier timestamp) ranks higher. We will cover the encoding formula in the deep dive section.

### Leaderboard Metadata (Hash)
Each leaderboard has associated metadata stored in a Redis Hash:
The `version` field is particularly important. It increments with every ranking change and allows clients to detect missed updates. If a client reconnects and their local version is far behind the server version, they know to fetch a fresh snapshot.

### Subscription Registry (Sets)
The Subscription Manager needs to quickly answer: "Who is watching the top 100 of this leaderboard?" We use Redis Sets to store lists of connection IDs grouped by subscription type:
For participant tracking:
When a ranking change affects positions 3-5, we query `subscriptions:tournament_123:top:100` to find all viewers watching the top 100. The Set data type gives us O(1) membership operations and efficient iteration.

### Connection State (Hash)
Each WebSocket connection has associated state stored in a Redis Hash:
This allows any service to look up which gateway owns a connection and what subscription that connection has. It also supports detecting stale connections by checking the `last_heartbeat` timestamp.

## 5.3 PostgreSQL Schema
PostgreSQL serves as our durable storage layer for data that needs to persist beyond the lifetime of a single event. We have four main tables.

### Leaderboards Table
Stores configuration for each leaderboard event. This is the source of truth for event metadata, referenced by both the live system and historical queries.
| Field | Type | Description |
| --- | --- | --- |
| leaderboard_id | UUID (PK) | Unique identifier |
| name | VARCHAR(255) | Display name ("Spring Championship 2024") |
| type | VARCHAR(50) | Event type (tournament, daily_challenge, season) |
| status | VARCHAR(20) | Current state (active, paused, completed) |
| config | JSONB | Scoring rules, tie-breaking method, visibility settings |
| starts_at | TIMESTAMP | Event start time |
| ends_at | TIMESTAMP | Event end time |
| created_at | TIMESTAMP | Creation timestamp |

The `config` column uses JSONB to store flexible configuration that varies by event type. This avoids schema changes when we add new event types or scoring rules.

### Participants Table
Stores participant profiles. This table is shared across all leaderboards, so a participant can appear in many events.
| Field | Type | Description |
| --- | --- | --- |
| participant_id | UUID (PK) | Unique identifier |
| display_name | VARCHAR(100) | Name shown on leaderboards |
| avatar_url | VARCHAR(500) | Profile picture URL |
| metadata | JSONB | Additional data (team, region, etc.) |
| created_at | TIMESTAMP | Registration timestamp |

### Final Rankings Table
When an event completes, we snapshot the final standings from Redis into this table. This is the permanent record of who placed where.
| Field | Type | Description |
| --- | --- | --- |
| leaderboard_id | UUID (PK, part 1) | References Leaderboards table |
| rank | INTEGER (PK, part 2) | Final position (1 = winner) |
| participant_id | UUID | References Participants table |
| score | BIGINT | Final score |
| finalized_at | TIMESTAMP | When the ranking was locked |

The composite primary key `(leaderboard_id, rank)` ensures each position in each leaderboard is unique. We also index by `participant_id` to support queries like "show me all tournaments this user placed in".

### Score Events Table
An audit log of every score change. This supports debugging ("why did this user drop from rank 3 to rank 7?") and potentially replaying events if we need to recover from a failure.
| Field | Type | Description |
| --- | --- | --- |
| event_id | UUID (PK) | Unique event identifier |
| leaderboard_id | UUID | Which leaderboard |
| participant_id | UUID | Who scored |
| old_score | BIGINT | Score before update |
| new_score | BIGINT | Score after update |
| old_rank | INTEGER | Rank before update |
| new_rank | INTEGER | Rank after update |
| created_at | TIMESTAMP | When the update occurred |

This table grows quickly during active events (potentially 10,000 rows per second at peak). We use table partitioning by date to make cleanup efficient:
Dropping old partitions is fast, as it's just dropping a table rather than deleting millions of rows.
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often go deeper into specific components. In this section, we will explore the trickiest parts of our design: choosing the right update delivery mechanism, optimizing Redis operations, handling tie-breaking, managing massive fan-out, ensuring consistency, scaling WebSocket connections, and handling failures gracefully.
These are the topics that distinguish a good system design answer from a great one.

## 6.1 Real-Time Update Delivery Strategies
Before settling on WebSockets, let's consider all the options for delivering updates to viewers. Each approach has different trade-offs around latency, scalability, and implementation complexity.

### Approach 1: Polling (Simple but Inefficient)
Clients periodically request the latest leaderboard state.

#### How It Works

#### Pros
- **Simple:** No WebSocket infrastructure needed.
- **Stateless servers:** Easy to scale horizontally.
- **Works everywhere:** No firewall/proxy issues.

#### Cons
- **Wasteful:** Most polls return unchanged data.
- **Latency:** Updates delayed by polling interval.
- **Scalability:** 10M clients x 1 req/sec = 10M QPS (expensive).

#### Best For
Low-scale applications, fallback when WebSocket fails.

### Approach 2: Long Polling (Better Latency)
Client makes a request that server holds until data changes.

#### How It Works

#### Pros
- **Lower latency:** Updates delivered as soon as available.
- **Simpler than WebSocket:** Uses standard HTTP.
- **Firewall-friendly:** Works through HTTP proxies.

#### Cons
- **Connection overhead:** New TCP connection per update.
- **Server resources:** Holding connections consumes memory.
- **Timeout handling:** Complexity around reconnection.

#### Best For
Medium-scale applications, environments where WebSocket is blocked.

### Approach 3: WebSocket (Recommended for Real-Time)
Persistent bidirectional connection between client and server.

#### How It Works

#### Pros
- **Low latency:** Sub-100ms update delivery.
- **Efficient:** Single connection for all updates.
- **Bidirectional:** Server can push without client request.
- **Reduced overhead:** No repeated HTTP headers.

#### Cons
- **Stateful servers:** Must track connection state.
- **Connection management:** Heartbeats, reconnection logic.
- **Infrastructure:** Need WebSocket-aware load balancers.
- **Firewall issues:** Some networks block WebSocket.

#### Best For
High-scale real-time applications where latency matters.

### Approach 4: Server-Sent Events (SSE)
Server-to-client only streaming over HTTP.

#### How It Works

#### Pros
- **Simple:** Uses standard HTTP, auto-reconnects.
- **Firewall-friendly:** Looks like long HTTP request.
- **Browser-native:** Built-in EventSource API.

#### Cons
- **Unidirectional:** Client cannot send messages.
- **Connection limits:** Browsers limit concurrent SSE connections.
- **Less efficient:** HTTP overhead per message.

#### Best For
Simpler real-time needs, when WebSocket is problematic.

### Summary and Recommendation
| Strategy | Latency | Scalability | Complexity | Best For |
| --- | --- | --- | --- | --- |
| Polling | High (1s+) | Poor | Low | Fallback, low scale |
| Long Polling | Medium (100ms) | Medium | Medium | WebSocket-blocked envs |
| WebSocket | Low (<100ms) | High | High | Production real-time |
| SSE | Low (<100ms) | Medium | Low | Simple server push |

**Recommendation:** Use **WebSocket** as the primary mechanism for real-time updates. Implement **polling** as a fallback for clients that cannot establish WebSocket connections.

## 6.2 Efficient Ranking with Redis Sorted Sets
We mentioned Redis Sorted Sets earlier, but let's go deeper into why they are the perfect fit for leaderboards and how to use them effectively. The choice of data structure is critical here: a poor choice would make our system unusable at scale.

### Why Redis Sorted Sets?
A Sorted Set stores members (participant IDs) with associated scores, automatically maintaining them in sorted order. Internally, Redis uses a clever dual data structure: a skip list for maintaining order and a hash table for fast lookups by member.
The skip list is like a linked list with express lanes. To find a score or rank, you start at the top express lane and drop down levels as you get close to your target. This gives us O(log N) operations, which is fast enough for millions of participants.

#### Key Operations and Complexity
| Operation | Command | Complexity | Use Case |
| --- | --- | --- | --- |
| Add/Update score | ZADD | O(log N) | Score submission |
| Get rank | ZREVRANK | O(log N) | Participant lookup |
| Get top N | ZREVRANGE | O(log N + M) | Leaderboard fetch |
| Get score | ZSCORE | O(1) | Current score lookup |
| Count members | ZCARD | O(1) | Total participants |
| Get by score range | ZRANGEBYSCORE | O(log N + M) | Tier-based queries |

#### Example: Score Submission Flow

### Alternative: Database-Based Ranking
For comparison, here is how you would compute rank in SQL:
**Problems:**
- O(N) complexity, scanning potentially millions of rows
- Lock contention on concurrent updates
- Not suitable for real-time updates

### Scaling Redis for Large Leaderboards
A single Redis instance can handle approximately:
- 100,000+ operations per second
- 50-100 million members per sorted set

For larger scale:
| Scale | Solution |
| --- | --- |
| < 10M participants | Single Redis instance with replicas |
| 10M - 100M participants | Redis Cluster (shard by leaderboard_id) |
| > 100M participants | Segmented leaderboards (by score range) |

## 6.3 Handling Tie-Breaking
Here is a subtle problem that is easy to overlook: what happens when two participants have the same score? In a casual game this might not matter, but in a competitive tournament with prize money on the line, tie-breaking rules become critical.
Our requirement says the participant who achieved the score first should rank higher. But Redis Sorted Sets only support a single numeric score per member. How do we encode both the score and the timestamp into one number?

### The Challenge
Both users have the same score, but User B achieved it 2 seconds earlier. User B should rank higher, but if we just store `1000` for both, Redis has no way to distinguish them.

### Solution: Composite Score Encoding
Encode the timestamp into the score such that:
- Higher base score = better rank
- Earlier timestamp (for same base score) = better rank

#### Encoding Formula

#### Decoding for Display

### Alternative: Secondary Sort by Participant ID
For cases where timing does not matter:

### Recommendation
Use **timestamp-based tie-breaking** for competitive scenarios (tournaments, races) where timing matters. Use **ID-based tie-breaking** for casual scenarios where simplicity is preferred.

## 6.4 Fan-out Optimization Strategies
We have talked about hierarchical fan-out at the infrastructure level, but there are also algorithmic optimizations that can dramatically reduce the message volume. Let's explore the strategies that make the difference between a system that buckles under load and one that handles peak traffic gracefully.

### The Scale of the Problem
Let's revisit the math with realistic numbers:
Even with perfect parallelism, this is an enormous load. But here is the insight: most of those 80 million messages are identical. If 8 million people are watching the same leaderboard, they all get the same update. Can we exploit this?

### Strategy 1: Subscription Segmentation
Not all viewers need all updates. Segment subscriptions by what they are watching.
**Implementation:**

### Strategy 2: Delta Updates Instead of Full State
Send only what changed, not the entire leaderboard.
**Full State (Expensive):**
**Delta Update (Efficient):**
**Benefits:**
- 50x smaller messages
- Client only updates affected rows (better UX)
- Version number enables consistency checks

### Strategy 3: Update Batching
Instead of sending every individual update, batch updates within a time window.
**Trade-off:** Slight increase in latency (up to flush_interval) for significant reduction in message volume.

### Strategy 4: Hierarchical Broadcasting
Use multiple levels of fan-out to parallelize delivery.
Each level fans out 10x, keeping per-node load manageable.

### Summary of Fan-out Strategies
| Strategy | Latency Impact | Bandwidth Savings | Complexity |
| --- | --- | --- | --- |
| Subscription Segmentation | None | High (skip irrelevant) | Medium |
| Delta Updates | None | High (50x smaller) | Low |
| Update Batching | +100ms | Medium (fewer messages) | Low |
| Hierarchical Fan-out | None | N/A (parallelism) | High |

**Recommendation:** Implement all four strategies. They complement each other and are all necessary at scale.

## 6.5 Consistency and Ordering
Here is a problem that can make or break user trust: what happens when two score updates happen at almost the same instant? If viewers briefly see an incorrect ranking before it corrects itself, they lose confidence in the system. "Did I really see that? Was the leaderboard wrong?"
In a distributed system processing 10,000 updates per second, updates can arrive out of order or be processed by different servers simultaneously. We need to ensure that all viewers eventually see the same, correct ranking order.

### The Consistency Challenge
If viewer receives Server 1's update before Server 2's, they briefly see A at rank 1 when B should be rank 1.

### Solution 1: Single Writer Per Leaderboard
Route all updates for a leaderboard to the same Redis master and processing node.
**Pros:** Simple, guaranteed ordering **Cons:** Hot leaderboards bottleneck on one node

### Solution 2: Version Numbers
Each update increments a version number. Clients apply updates in order.
**Pros:** Handles out-of-order delivery **Cons:** Gaps may require full refresh

### Solution 3: Hybrid with Snapshot Fallback
If a client misses too many updates, fetch full state and resync.

### Recommendation
Use **version numbers** for ordering with **snapshot fallback** for recovery. This handles most cases efficiently while providing a safety net for edge cases.

## 6.6 Connection Management at Scale
Ten million simultaneous WebSocket connections is not something you can achieve with off-the-shelf configuration. Each connection consumes memory for the socket buffer, the SSL state (if using TLS), and any application-level state we associate with it. At 10-20 KB per connection, 10 million connections means 100-200 GB of memory just for connections, before we even store any leaderboard data.
Let's break down how to architect the WebSocket layer to handle this scale.

### Connection Distribution
The key is spreading connections across many servers. A well-tuned server can handle 500K to 1M WebSocket connections. For 10 million concurrent viewers, we need at least 10-20 WebSocket Gateway instances, plus redundancy for failures.
Each gateway runs on a high-memory server (16-32GB RAM for connection state).

### Heartbeat and Stale Connection Detection
Clients must send periodic heartbeats. Servers must detect and clean up dead connections.

### Graceful Reconnection
When a WebSocket Gateway restarts, clients must reconnect and resync:

### Load Shedding
During extreme load, protect the system by rejecting new connections or degrading to polling:

## 6.7 Failure Handling and Resilience
In a system this complex, failures are inevitable. Redis will occasionally become unreachable. WebSocket Gateways will crash. The Event Bus will hiccup. The question is not whether these failures will happen, but how the system behaves when they do.
A well-designed system degrades gracefully. When Redis fails, viewers might see slightly stale data, but they do not see errors. When a WebSocket Gateway crashes, clients reconnect transparently. The goal is to make failures invisible to users whenever possible, and minimally disruptive when they cannot be hidden.

### Redis Failure
**Scenario:** Redis master becomes unavailable
**Impact:** Cannot update or read rankings
**Mitigation:**
1. **Redis Sentinel/Cluster:** Automatic failover to replica
2. **Read from replica:** Serve slightly stale data during failover
3. **Queue writes:** Buffer score updates in Kafka until Redis recovers

### WebSocket Gateway Failure
**Scenario:** A gateway handling 1 million connections crashes
**Impact:** 1 million viewers temporarily disconnected
**Mitigation:**
1. **Client reconnection:** Exponential backoff to different gateway
2. **Connection state in Redis:** New gateway can restore subscriptions
3. **Stateless gateways:** Any gateway can serve any client

### Event Bus Failure
**Scenario:** Kafka becomes unavailable
**Impact:** Updates not reaching viewers
**Mitigation:**
1. **Direct push fallback:** Score Service pushes directly to gateways (higher latency)
2. **Client polling fallback:** Viewers fall back to polling endpoint
3. **Kafka replication:** Multi-region Kafka for durability

### Circuit Breaker Pattern
Prevent cascade failures by failing fast when downstream services are unhealthy:
# References
- [The WebSocket Protocol RFC 6455](https://datatracker.ietf.org/doc/html/rfc6455) - Official WebSocket specification for understanding the protocol
- [Skip Lists: A Probabilistic Alternative to Balanced Trees](https://15721.courses.cs.cmu.edu/spring2018/papers/08-oltpindexes1/pugh-skiplists-cacm1990.pdf) - The data structure powering Redis sorted sets
- [How Discord Stores Billions of Messages](https://discord.com/blog/how-discord-stores-billions-of-messages) - Scaling real-time communication infrastructure

# Quiz

## Design Real Time Leaderboard Quiz
What best distinguishes a real-time leaderboard from a traditional periodically refreshed leaderboard?