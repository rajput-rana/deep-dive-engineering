# Design Live Comments

#### What are Live Comments?
Live comments are a feature often used in streaming platforms, sports apps, and social media events where users can post and view comments in real time as an event unfolds.
For example, during a live football match or a concert stream, thousands or even millions of viewers may send comments simultaneously, which appear instantly for all participants.
In this chapter, we will aim to design a **low-latency, scalable live comment system** that allows thousands or even millions of users to exchange messages in real time during a live event.
Key challenges include:
- **Latency:** Messages must be delivered in near real-time.
- **Fanout:** A single message needs to be broadcast to millions of subscribers simultaneously.
- **Ordering:** Comments should appear in a logical, roughly chronological order.

Let’s begin by clarifying the requirements.
# 1. Clarifying Requirements
Before diving into the design, let's narrow down the scope of the problem. Here’s an example of how a discussion between candidate and interviewer might flow:
**Candidate:** “Should users only post text comments, or do we also need to support images, emojis, or reactions?”
**Interviewer:** “For now, only short text-based comments. Reactions or media attachments can be ignored.”
**Candidate:** “Do comments need to be delivered in real-time to all viewers?”
**Interviewer:** “Yes, the experience should feel live. Ideally under 500 ms from publish to delivery.”
**Candidate:** “Do we need to support playback after the live event ends like showing comments alongside recorded video?”
**Interviewer:** “Yes. Playback is in scope. Users watching later should see the comments synchronized with the original timeline.”
**Candidate:** “Can users reply to comments or have threaded conversations?”
**Interviewer:** “No. No replies or threads. Just a flat stream of comments.”
**Candidate:** “What about comment moderation like spam filtering, profanity, abuse detection?”
**Interviewer:** “Assume moderation already exists. You can treat it as out of scope.”
**Candidate:** “For ordering, do we need strict global time ordering across distributed regions?”
**Interviewer:** “No. Exact strict ordering is not require. We just need roughly correct chronological order that feels consistent to the user.”
After clarifying the requirements, we can summarize the functional and non-functional requirements.

## 1.1 Functional Requirements
- **Post Comments:** Users can post short, text-based comments during a live event.
- **Real-Time Viewing:** Users can view new comments posted by others in real-time.
- **Playback:** Users can replay the stream with synchronized comments (time-aligned with the video) after the event ends.

#### Out of Scope:
- **Reactions:** Users can react (like, heart, etc.) to comments.
- **Replies: **Users can reply to comments.
- **Moderation: **The system must filter spam, and other undesirable content.

## 1.2 Non-Functional Requirements
- **High Scalability:** Support millions of concurrent viewers and thousands of new comments per second.
- **Low Latency:** Deliver comments to clients within sub-second latency (< 500 ms ideally).
- **Reliability & Durability:** Once accepted, a comment should never be lost even during failures.
- **Ordering:** Comments should appear in approximately the order they were sent. Strict ordering is difficult in a distributed system, but we should aim for a consistent experience.
- **Eventual Consistency: **Small ordering differences or delays are acceptable as long as the user experience remains smooth.

# 2. Scale Estimation
Before designing the system, let’s estimate the scale we need to support.

#### Assumptions:
- **Concurrent viewers**: **5 million**. This reflects a peak load during major live events (e.g., sports finals, global product launches).
- **Active commenters**: **1% of viewers (≈50,000 users)**. Most users are passive viewers; only a small fraction actively comment.
- **Comment rate per user**: **1 comment every 10 seconds** during periods of high activity.
- **Average comment size**: **150 bytes**. This includes the comment text plus metadata (user ID, timestamp, event ID).

#### Throughput Estimation
- **Incoming comments per second** = 50,000 users × (1/10) = **5,000 comments/sec**
- **Outgoing fanout** = 5,000 comments/sec × 5,000,000 recipients = **25 billion message deliveries/sec.** This massive number is the core challenge and will be handled via a distributed fanout architecture, not a single process.

#### Storage Estimation
- **Storage rate:** 5,000 comments/sec × 150 bytes/comment = **0.75 MB/sec**.
- **Storage per day:** 0.75 MB/sec × 86,400 seconds/day ≈ **65 GB/day**.
- **Storage per month (for playback):** 65 GB/day × 30 days ≈ **~2 TB/month**.

# 3. API Design
For this system, we need to design two distinct interfaces: one for writing (posting a new comment) and one for reading (receiving new comments in real-time).

## 3.1 Write API
The write path can be handled with a simple, stateless HTTP endpoint. This keeps the logic for ingesting comments separate from the complex world of real-time connections.

#### Endpoint
`POST /v1/streams/{stream_id}/comments`
This RESTful endpoint allows a client to submit a new comment to a specific live stream.
**Method:** `POST`
**URL Parameter: **
- `stream_id` (UUID): The unique identifier for the live stream.

**Headers:**
- `Authorization: Bearer <JWT_TOKEN>`: Ensures the request is from an authenticated user.
- `Content-Type: application/json`: Specifies the format of the request body.

#### Request (JSON)
The client sends a JSON payload with the comment's content and some useful metadata.
- `text`: The actual comment content.
- `client_ts`: The client-side timestamp. This is useful for debugging and understanding the perceived end-to-end latency from the user's perspective.
- `meta`: An optional object for analytics or client-specific logic.

**Responses:**
- ✅** **`202 Accepted`: This is the ideal success response. It tells the client, "We've received your comment and will process it." It doesn't wait for the comment to be written to the database or broadcasted, allowing us to respond to the client immediately and keep the write path incredibly fast.
- ❌ `400 Bad Request`: Sent if the request body is malformed (e.g., the `text` field is missing or too long).
- ❌ `401 Unauthorized`: The provided JWT is missing, invalid, or expired.
- ❌ `429 Too Many Requests`: The user or their IP address has exceeded the rate limit (e.g., posting too many comments in a short period).

## 3.2 Read API
Now for the real challenge: how do we efficiently push comments out to millions of connected viewers?
A standard request-response model won't work. Let's explore the three main approaches.

### Approach 1 (Bad): HTTP Polling

### Approach 2 (Good): WebSockets

### Approach 3 (Great): Server-Sent Events (SSE)
Here's a summary of communication options:
| Protocol | Use Case | Pros | Cons |
| --- | --- | --- | --- |
| WebSockets | Persistent, bi-directional connection | Full-duplex, low latency, efficient | Requires connection management, stateful |
| Server-Sent Events (SSE) | Unidirectional server-to-client updates | Lightweight, auto-reconnect, HTTP-based | Unidirectional, limited browser support |
| HTTP Long Polling | Simple fallback for older clients | Works everywhere, simple to implement | High overhead, not truly real-time |

### Why choose SSE over WebSockets for the read path?
Even though WebSockets are more flexible, the read path in our system is strictly **one-directional** — the server broadcasts, clients listen. That’s exactly what SSE is built for.
Here's why SSE wins for our use case:
1. **Simplicity and Standard HTTP:** No special protocol or handshake is required. Works through proxies, CDNs, load balancers.
2. **Automatic reconnection built-in:** The browser’s `EventSource` will retry automatically if the connection drops (e.g., mobile networks).
3. **Native cursor resume:** Using the `Last-Event-ID` header, the client resumes from where it left off without extra logic.

### SSE Endpoint Definition

#### Endpoint
`GET /v1/streams/{stream_id}/comments/subscribe`
- The client connects to this endpoint to start receiving events.
- The server must respond with the `Content-Type: text/event-stream` header to signal that this is an SSE connection.
- The server will keep the connection open, pushing new comment events as they arrive from the message broker.

#### Example SSE Stream:
The data sent over an SSE connection is a simple, plain-text format. Here’s what a client would receive:
- `event: new_comment`: This names the event, allowing the client to have specific listeners for different types of messages (e.g., `new_comment`, `pinned_comment`, `delete_comment`).
- `data: {...}`: This line contains the actual JSON payload for the event. The client's `EventSource` listener will receive this data and can then render the new comment in the UI.

# 4. High-Level Design
Now that we've defined our APIs, let's sketch out the high-level architecture.
Our goal is to build a **low-latency, horizontally scalable, and resilient** system that can handle **millions of concurrent viewers**, **thousands of comments per second**, and deliver updates in **real time**.
At its core, the system revolves around **two primary data flows**:
1. **The Write Path:** How a new comment is ingested, processed, and stored.
2. **The Read Path:** How a new comment is broadcast (fanned out) to millions of viewers in real time.

Lets first discuss posting comment and then enhance the design to include reading as well.

## 3.1 Posting a Comment
Posting a comment is relatively straightforward since only **one user** is involved in this operation.
Let’s walk through the components and flow.

### Components Involved:

#### Client (Web/Mobile)
The user interface (UI) that allows users to post comments. Sends a new comment to the backend via HTTPS or WebSocket.

#### Load Balancer / API Gateway
The entry point for all requests. Handles TLS termination, authentication, rate limiting, and routing.

#### Comment Service
Handles the core application logic. Validates comments, assigns timestamps, persists data, and publishes the event to the message broker.

#### Database
A durable, scalable store for all comments (used later for playback). Given our write-heavy workload and need for scalability, a distributed NoSQL database like **Cassandra** or **Amazon DynamoDB** is a great fit.

#### Message Broker
The central hub for real-time distribution of comment stream to SSE gateways.

### Flow Summary:
1. A user hits "send." The client application fires a `POST`** request** to our API Gateway.
2. The API Gateway authenticates the user's token, checks for rate limits, and forwards the request to an available instance of the **Comment Service**.
3. The Comment Service:
4. Almost instantly, the Comment Service returns a `202 Accepted` response to the user. This makes the application *feel* instantaneous, as the user gets confirmation before the comment has even been broadcast to other viewers.

## 3.2 Receiving a Comment
The read path is where the **real-time magic** happens.
When a new comment arrives, it must be **fanned out** to potentially **millions of active viewers** connected to the live stream, all within a fraction of a second.
This is a **classic pub-sub fanout problem**, where the challenge lies in scaling concurrent connections, ensuring timely delivery, and avoiding bottlenecks.

#### Connection Gateway (SSE Servers)
The Connection Gateway is a dedicated fleet of servers whose sole responsibility is to **maintain long-lived client connections** for real-time delivery.
These servers do not handle business logic, database writes, or comment ingestion. They exist purely to **push events down to connected viewers** with minimal latency.
Because a single live stream may have millions of active viewers, the load must be **sharded across many gateway nodes**. Instead of one server attempting to push updates to all users, we partition the audience:
- Each SSE server maintains **persistent HTTP connections** (EventSource clients).
- Viewers of a single event are **spread across hundreds or thousands of gateway machines**.
- Each server is only responsible for a **few thousand to tens of thousands of connections**, keeping memory and CPU usage predictable.
- Gateways subscribe to only the topics (events/streams) they serve, they don’t receive irrelevant data.

### Sequence of Events (Read Flow):
1. The journey begins where the write path left off: a new comment message arrives on a topic in the **Message Broker**.
2. The broker, acting as a central distribution hub, immediately **fans out** this message to every consumer subscribed to that topic.
3. Who are the subscribers? Our fleet of **Connection Gateway (SSE) servers**. Each gateway is subscribed to the topics for the live streams its connected viewers are currently watching.
4. When a gateway server receives the new comment message, it iterates through the list of clients connected to that stream.
5. For each client, the gateway pushes the new comment down the open **SSE connection** as a `new_comment` event.
6. On the client-side, the browser's native `EventSource` API receives the event, parses the JSON data, and the UI instantly renders the new comment for the user to see.

# 4. Database and Messaging Layer Design
Live comments have two very different access patterns:
- **Hot path (live event):** sub-second writes and immediate fanout to active viewers; cursor-based reads for “latest N” comments.
- **Cold path (playback & analytics):** time-range queries long after the event ends; optimized for cost and scan efficiency.

To support both efficiently, we use a **tiered storage design + a durable pub/sub bus** that decouples ingestion from fanout.

## 4.1 Database Design
Once a comment is accepted, it must be written to persistent storage so that:
- playback viewers see an exact historical reconstruction,
- nothing is lost during node failures,
- analytics or moderation logic can run later.

Because our workloads involve **high write throughput (5K writes/sec+)** and **simple, predictable query patterns**, traditional relational databases do not scale cleanly here without manual sharding and overhead. We need a store that scales horizontally by design.
A **distributed NoSQL database** is a great choice. A wide-column store like **Apache Cassandra** or a managed equivalent like **Amazon DynamoDB** is purpose-built for this kind of relentless, high-volume data ingestion. They are designed to scale linearly and handle this workload efficiently.

### Schema Design
In NoSQL, you don't design your schema and then write queries; you design your schema *for* your queries. Our primary and most important query is:
`"Fetch all comments for a specific stream, sorted chronologically."`
To make this query incredibly fast, we will design our `comments` table with a composite primary key that aligns perfectly with this access pattern.
- **Partition Key:** `stream_id`. The partition key tells the database how to group and distribute data across the cluster. By using `stream_id`, we ensure that **all comments for the same live stream are physically stored together.** When we query for a stream, the database knows exactly which nodes to go to, avoiding a slow, full-database scan.
- **Clustering Key:** `timestamp`.Within each partition (for a given `stream_id`), the data will be **physically sorted on disk** by timestamp. This is a massive performance optimization. It means that when we fetch the comments, they are already in chronological order. The database doesn't need to perform an expensive sorting operation on the fly.

#### The comments Table Schema
| Column | Data Type | Description | Key Type |
| --- | --- | --- | --- |
| stream_id | UUID | The unique identifier for the live stream. | Partition Key |
| timestamp | TimeUUID or Timestamp | The server-side time the comment was created. Sorts the comments. | Clustering Key |
| comment_id | UUID | A unique identifier for the comment itself. | - |
| user_id | UUID | The ID of the user who posted the comment. | - |
| username | TEXT | The user's display name, denormalized here to avoid a join/lookup. | - |
| comment_text | TEXT | The actual content of the comment. | - |

## 4.2 Messaging Layer
While the database handles **durability**, it is **not fast enough for real-time fanout**. We need a **dedicated messaging system** to broadcast comments as soon as they're posted.

#### Why a Message Broker?
The message broker:
- Decouples producers (comment service) from consumers (connection gateways)
- Enables **horizontal fanout** to thousands of connected clients
- Adds **elasticity** and **fault isolation**

### Choosing the Right Message Broker
Let’s evaluate the popular options across three key dimensions: **latency**, **durability**, and **operational complexity**.
| Broker | Pros | Cons | Best For |
| --- | --- | --- | --- |
| Redis Pub/Sub | Ultra-low latency (in-memory)Simple API | No persistenceNo delivery guarantees | Ephemeral data (live chats) |
| Apache Kafka | Durable (disk-backed)ReplayableScale-out | Higher latencyOperationally heavy | Mission-critical event pipelines |
| Managed Pub/Sub (GCP/AWS) | ScalableDurableNo infrastructure ops | CostlyHigher cold-start latency | Moderate-scale, general use cases |

**The Verdict:** For the real-time path of live comments, **Redis Pub/Sub** is the ideal choice. Its "fire-and-forget" nature and in-memory speed provide the lowest possible latency. A single dropped comment in a fast-moving chat is an acceptable trade-off for the incredible performance it offers. Using Kafka here would be like using a cargo ship to deliver a pizza—it's too heavy-duty for what we need.

### Topic Design
A **Pub/Sub system** uses **topics** to group messages logically. To avoid message collisions between live streams, each stream gets its own topic.
Our topic naming scheme will be simple and effective:
`comments:<stream_id>`
**Example:** For a stream with the ID `stream-1b2c3d4`, the topic will be:
`comments:stream-1b2c3d4`

### The Workflow:
1. When a user comments on that stream, the **Comment Service** will `PUBLISH` the comment message to this exact topic name in Redis.
2. Meanwhile, any **Connection Gateway** servers that have active viewers for this stream will `SUBSCRIBE` to this same topic.
3. Redis handles the fanout instantly, ensuring the message is delivered to the correct gateways for broadcasting to the end-users. This simple mapping is all that's needed to orchestrate the entire real-time flow.

# 5. Design Deep Dive

## 5.1 Fanout Optimization
When a stream has millions of viewers, a single publisher fanning out to thousands of WebSocket servers can become a bottleneck. We need to optimize this.

### Strategy 1: Topic-Based Subscription
Not every connection server needs every event.
Each gateway subscribes only to the **topics for the streams its clients care about**:
Each gateway maintains a local map of which users are connected to it, and which streams those users are watching.
- When the *first* user for `stream-123` connects to `Gateway-A`, `Gateway-A` subscribes to the `comments:stream-123` topic in Redis.
- When the *last* user for `stream-123` disconnects from `Gateway-A`, `Gateway-A` unsubscribes from that topic.

This dynamic subscription model ensures that messages are only sent to the servers that have active viewers for a particular stream. This dramatically reduces unnecessary network traffic and CPU load across our fleet.

### Strategy 2: Geo-Distributed Gateways and Regional Pub/Sub
Latency isn't just about processing time; it's about the speed of light. A user in Mumbai, India, connecting to a server in Virginia, USA, will always experience a noticeable delay due to the physical distance the data must travel.
We deploy our Connection Gateway servers in multiple geographic regions around the world (e.g., Mumbai, Singapore, Frankfurt, São Paulo). Using geo-DNS routing, users are automatically connected to the gateway closest to them.
Now, all these global gateways would still be talking to a single, central Redis instance in one region. A gateway in Mumbai would still have to wait for a message to travel from Virginia.
We introduce **regional Pub/Sub replicas**. The central Comment Service publishes to a durable, globally-aware message bus (like Apache Kafka or Google Cloud Pub/Sub). This central bus then replicates the message to read-only Redis instances in each region. The local Connection Gateways in Mumbai subscribe to the Mumbai Redis, not the one in Virginia. This keeps all high-frequency fanout traffic within the same geographic region, slashing latency.

### Strategy 3: Tiered Fanout (For Global Mega-Events)
For the largest events on Earth (e.g., a World Cup final, a new product launch) even a regional Redis instance can become overwhelmed. This is where we need a multi-layered approach to soften the blow.
Instead of a direct `Message Broker -> Gateway` flow, we introduce an intermediate layer of "Aggregators."
1. The **Comment Service** publishes a message once to a highly durable central bus (like Kafka).
2. A small number of **Regional Aggregator** services subscribe to this bus. Their only job is to receive this message.
3. Each Aggregator then re-publishes the message to the **Regional Redis Pub/Sub**.
4. Hundreds of local **Connection Gateways** subscribe to their regional Redis instance and perform the final fanout to clients.

### Strategy 4: Message Batching and Coalescing (The Last Mile)
Finally, we can optimize the connection between our gateway servers and the end-user's device. In a very active chat, dozens of comments might arrive every second. Sending each one as a separate SSE event is inefficient.
Sending 50 tiny messages per second creates significant overhead. Each message is wrapped in its own TCP/IP packets and requires the client's browser to wake up, parse the message, and re-render the UI 50 times. This can drain battery and lead to a choppy user experience, a phenomenon known as "render thrashing."
The Connection Gateway server buffers comments for a very short, imperceptible period (e.g., **100-200 milliseconds**). It then bundles all comments received during that window into a single JSON array and sends them as **one SSE event**.
We introduce a tiny amount of latency (100ms is invisible to the human eye) in exchange for a massive gain in efficiency. Instead of sending 50 tiny paper airplanes, we send one slightly larger box every quarter-second. This reduces network congestion, saves client CPU cycles, and leads to a smoother experience for the end-user.

## 5.2 Stream Playback
A crucial feature of any modern streaming platform is the ability to replay an event with the chat synchronized, re-creating the excitement and commentary as it happened.
The core challenge of playback is **time synchronization**: how do we ensure that a comment that appeared exactly 15 minutes and 32 seconds into the live event appears at the exact same moment when a user is watching the recording?
A single, hour-long live event can accumulate hundreds of thousands of comments. Our first instinct might be to fetch all of them at once when the user presses play.

#### The Problem with "Fetch-All"
Attempting to download the entire chat history for a long stream would result in a massive initial data payload (potentially many megabytes). This would lead to long, frustrating load times and would be incredibly wasteful if the user only watches the first few minutes of the VOD.

#### The Solution: Paginated Chunking
The only scalable solution is for the client to fetch comments in small, manageable chunks as needed. As the user watches the video, the client application will request the next "page" of comments just before they are needed. This is a "just-in-time" delivery model.
To enable this chunking strategy, we need a dedicated, paginated RESTful API endpoint. This API will be the backbone of the playback feature.
**Endpoint:** `GET /v1/streams/{stream_id}/comments`
This endpoint is designed to fetch comments for a specific stream within a given time window.
**Query Parameters:**
- `start_time` (timestamp or integer offset in seconds): The beginning of the time window to fetch comments from, relative to the video's start. **(Required)**
- `duration` (integer, in seconds): The size of the time window. For example, `duration=180` would fetch 3 minutes worth of comments. **(Required)**
- `limit` (integer, optional): The maximum number of comments to return in one response, to prevent a single request from being too large during a comment spike.
- `pagination_token` (string, optional): For stateless pagination if the number of comments within the `duration` exceeds the `limit`.

**Example Request:** 
`GET /v1/streams/a1b2-c3d4/comments?start_time=900&duration=180` 
This request asks for all comments between the 15-minute mark (900 seconds) and the 18-minute mark (1080 seconds).
**Response Body:** The server returns a JSON object containing the comments for that time slice and, if necessary, a token to fetch the next page.

#### Client-Side Synchronization
Client application needs to perfectly time the appearance of each comment with the video playback.
**How it Works:**
1. **Initialization:** When the VOD page loads, the client immediately requests the first chunk of comments (e.g., for the 0-3 minute window). These comments are loaded into a temporary in-memory buffer.
2. **The Player Clock:** The video player provides a constantly updating clock (e.g., via a `timeupdate` event that fires several times a second). This clock is our "source of truth" for timing. Let's say the `player.currentTime` is `932.5` seconds.
3. **The Render Loop:** The client's synchronization logic runs in a loop. In each cycle, it:
4. **Proactive Buffering:** The client is always thinking ahead. When the video player's clock approaches the end of the current buffered chunk (e.g., at the 2.5-minute mark of a 3-minute chunk), it proactively fires off an API request for the *next* chunk (e.g., for the 3-6 minute window). This ensures there is always a buffer of upcoming comments ready to be displayed, preventing any stuttering in the chat playback.

#### Handling Pauses and Seeks
A user's interaction with the video player must be reflected in the chat playback.
- **On Pause:** The client simply stops its render loop. When the user hits play again, the loop resumes.
- **On Seek (Jumping on the Timeline):** This is a critical event. If a user jumps from the 15-minute mark to the 58-minute mark:

# Quiz

## Design Live Comments Quiz
For the read path of live comments, which communication approach best fits sub-second delivery to millions of viewers while keeping server push efficient?