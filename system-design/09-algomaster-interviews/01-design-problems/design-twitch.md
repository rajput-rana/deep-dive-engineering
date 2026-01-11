# Design Twitch

## What is Twitch?

Twitch is a live streaming platform where content creators broadcast video in real-time to viewers around the world. Viewers can watch streams, interact through live chat, follow their favorite streamers, and subscribe for exclusive benefits.
The platform handles millions of concurrent viewers watching thousands of live streams simultaneously. Each stream involves real-time video ingestion from the broadcaster, transcoding into multiple quality levels, and distribution to viewers globally, all while maintaining a synchronized live chat experience.
**Popular Examples:** Twitch.tv, YouTube Live, Facebook Gaming, Kick
In this chapter, we will explore the **high-level design of a live streaming platform like Twitch**.
This problem combines several challenging aspects: real-time video processing, high-fanout content delivery, and low-latency chat systems.
Let's start by clarifying the requirements:
# 1. Clarifying Requirements
Before diving into the design, it's important to ask thoughtful questions to uncover hidden assumptions, clarify ambiguities, and define the system's scope more precisely.
Here is an example of how a discussion between the candidate and the interviewer might unfold:
**Candidate:** "What is the expected scale? How many concurrent viewers and active streamers should we support?"
**Interviewer:** "Let's design for 5 million concurrent viewers watching around 100,000 active streams at peak times."
**Candidate:** "Should viewers be able to watch past broadcasts, or only live streams?"
**Interviewer:** "Yes, streams should be automatically recorded and available as VODs (Video on Demand) after the broadcast ends."
**Candidate:** "What video quality options should we support?"
**Interviewer:** "We need adaptive bitrate streaming with multiple quality levels: 1080p, 720p, 480p, and 360p."
**Candidate:** "Is live chat a core requirement, and what latency is acceptable for it?"
**Interviewer:** "Yes, live chat is critical. Messages should be delivered to all viewers within 500ms."
**Candidate:** "Do we need to support features like subscriptions, donations, or clips?"
**Interviewer:** "Subscriptions and basic monetization are in scope. Clips (short highlights) can be considered out of scope for now."
**Candidate:** "What latency is acceptable between the broadcaster and viewers?"
**Interviewer:** "We should target under 10 seconds of end-to-end latency for a good interactive experience."
After gathering the details, we can summarize the key system requirements.

## 1.1 Functional Requirements
Based on the discussion, here are the core features our system must support:
- **Live Streaming:** Streamers can broadcast live video to viewers in real-time.
- **Video Playback:** Viewers can watch live streams with adaptive quality based on their connection.
- **Live Chat:** Viewers can send and receive chat messages during a live stream.
- **VOD Recording:** Streams are automatically recorded and available for playback after the broadcast ends.
- **Follow/Subscribe:** Users can follow streamers for free or subscribe for paid benefits.

## 1.2 Non-Functional Requirements
Beyond features, we need to consider the qualities that make the system production-ready:
- **Low Latency:** End-to-end video latency under 10 seconds; chat latency under 500ms.
- **High Availability:** The system must be highly available (99.99% uptime).
- **Scalability:** Support millions of concurrent viewers and thousands of concurrent streamers.
- **Global Reach:** Viewers worldwide should experience low-latency video delivery.
- **Reliability:** No frames should be lost during broadcast; VODs must be durable.

# 2. Back-of-the-Envelope Estimation
Before diving into architecture, let's run some quick calculations to understand the scale we are dealing with. These numbers will help us identify which components need the most attention and where we should invest in optimization.

### 2.1 Traffic Assumptions
Starting with the numbers from our requirements discussion:
- **Concurrent viewers:** 5 million at peak
- **Active streams:** 100,000 at peak
- **Average viewers per stream:** 50 (though the distribution is highly skewed)
- **Source video bitrate:** 6 Mbps (1080p from streamers)
- **Output qualities:** 1080p (6 Mbps), 720p (3 Mbps), 480p (1.5 Mbps), 360p (800 Kbps)
- **Chat participation:** About 1% of viewers send messages, averaging 1 message per minute when active

### 2.2 Video Bandwidth
This is where the numbers get interesting. Let's calculate bandwidth requirements separately for ingest (streams coming in) and egress (streams going out to viewers).

#### Ingest Bandwidth (Streamers to Platform):
600 Gbps is substantial but manageable. A well-provisioned data center can handle this, and we will distribute ingest servers across multiple regions.

#### Egress Bandwidth (Platform to Viewers):
Here is where live streaming gets expensive. Assuming viewers receive an average of 3 Mbps (a mix of quality levels):
15 terabits per second is massive. This is why CDNs are not just nice to have, they are essential. No single company operates enough infrastructure to serve this directly. We will rely heavily on CDN providers who specialize in global video delivery.
The 25:1 ratio between egress and ingest bandwidth illustrates a fundamental truth about live streaming: the real challenge is not accepting video, it is distributing it.

## 2.3 Chat Throughput
Chat traffic is bursty. During calm moments, chat might be quiet. During exciting plays or funny moments, messages flood in.

#### Steady state:
833 writes per second seems manageable, but the challenge is in message delivery, not message receipt.

#### Message fanout:
When someone sends a chat message, it needs to reach everyone in that stream's chat room. For a popular streamer with 100,000 viewers:
If that streamer's chat gets 10 messages per second, we need to deliver 1 million messages per second just for one chat room. This fanout problem is the central challenge of building chat at scale.

## 2.4 Storage Estimates
VOD storage accumulates quickly when you are recording hundreds of thousands of streams daily.
2.5 petabytes per day is substantial. We will need tiered storage strategies: hot storage for recent VODs that viewers are actively watching, warm storage for older content, and cold archival for streams that are rarely accessed.
| Time Period | Storage Added | Cumulative | Notes |
| --- | --- | --- | --- |
| 1 Day | 2.5 PB | 2.5 PB | All in hot storage |
| 1 Month | 75 PB | 75 PB | Mix of hot and warm |
| 1 Year | 900 PB | 900 PB | Mostly cold with tiered access |

### 2.5 Key Insights from Estimation
These calculations reveal several important design implications:
1. **Egress bandwidth dominates:** The 15 Tbps egress requirement means CDNs are essential infrastructure, not an optimization.
2. **Chat fanout is the hard problem:** High message rates combined with large chat rooms create a multiplicative challenge.
3. **Storage requires tiering:** 2.5 PB daily growth mandates intelligent storage policies. We cannot afford to keep everything on hot storage.
4. **Popular streamers create hot spots:** The power law distribution of viewership means some streams need orders of magnitude more resources than average.

# 3. Core APIs
With our requirements and scale understood, let's define the API contract. Our platform needs APIs for three main capabilities: managing streams, watching video, and participating in chat.

### 3.1 Start Stream

#### Endpoint: POST /streams
When a streamer clicks "Go Live" in their streaming software, this endpoint provisions everything needed for the broadcast. It returns the ingest endpoint where video should be sent and a stream key for authentication.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| title | string | Yes | Stream title shown to viewers |
| category | string | No | Category like "Just Chatting" or a specific game |
| user_id | string | Yes | Authenticated streamer's ID |

#### Example Request:

#### Success Response (201 Created):
The response includes everything the streamer needs: a unique stream ID for tracking, a secret stream key they paste into their software, and the RTMP endpoint to connect to.

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 401 Unauthorized | Not authenticated | Missing or invalid authentication token |
| 403 Forbidden | Banned from streaming | User has been suspended from broadcasting |
| 429 Too Many Requests | Rate limited | Too many stream start attempts in short period |

### 3.2 Get Stream Playback

#### Endpoint: GET /streams/{stream_id}/playback
When a viewer clicks on a stream, their player needs to know where to fetch the video. This endpoint returns playback information including the manifest URL for adaptive streaming.

#### Path Parameters:
| Parameter | Type | Description |
| --- | --- | --- |
| stream_id | string | The unique identifier for the stream |

#### Success Response (200 OK):
The playback URL points to an HLS manifest that lists all available quality levels. The player will automatically select the best quality based on the viewer's bandwidth.

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 404 Not Found | Stream does not exist | Invalid stream_id or stream never existed |
| 410 Gone | Stream ended | Stream is offline and VOD is not yet ready |

The distinction between 404 and 410 helps clients show appropriate messages. A 404 might say "Stream not found" while a 410 could say "Stream ended, VOD coming soon."

### 3.3 Send Chat Message

#### Endpoint: POST /streams/{stream_id}/chat
Viewers send chat messages through this endpoint. The message goes through validation, moderation checks, and then gets distributed to all other viewers.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| user_id | string | Yes | Sender's authenticated user ID |
| message | string | Yes | Message content (max 500 characters) |

#### Example Request:

#### Success Response (201 Created):

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 429 Too Many Requests | Rate limited | Sending messages too quickly |
| 403 Forbidden | Cannot chat | User is banned, muted, or chat is subscriber-only |
| 400 Bad Request | Invalid message | Message too long, contains prohibited content |

### 3.4 Subscribe to Chat

#### Endpoint: WebSocket /streams/{stream_id}/chat/subscribe
For receiving chat messages in real-time, viewers establish a WebSocket connection. This is more efficient than polling and enables sub-second message delivery.

#### Connection Flow:

#### Message Format (Server to Client):
The connection stays open for the duration of the viewer's session, receiving a continuous stream of chat messages.
# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complex diagram upfront, we will build the design incrementally, starting with the simplest possible approach and adding components as we encounter challenges.
Our system needs to handle four fundamental operations:
1. **Video Ingest:** Accept live video from streamers
2. **Video Processing:** Convert video into multiple quality levels
3. **Video Delivery:** Distribute video to millions of viewers globally
4. **Live Chat:** Enable real-time messaging during streams

The architecture naturally separates into two major subsystems: a **video pipeline** that handles the heavy media processing, and a **chat system** that handles real-time messaging. These systems interact (chat needs to know about active streams) but can scale independently.
Let's build each component step by step.

## 4.1 Requirement 1: Video Ingest
The video pipeline begins when a streamer clicks "Go Live." Their streaming software (OBS, Streamlabs, etc.) establishes a connection to our platform and begins sending video frames. This is the entry point to our entire system.

### Components for Video Ingest

#### Stream Router
The stream router is the first thing streamers connect to. Using GeoDNS (geographic DNS routing), it directs each streamer to the nearest available ingest server. A streamer in London gets routed to EU-West ingest servers, while a streamer in Tokyo gets routed to Asia-Pacific servers.
Why does geographic proximity matter? Video streams are sensitive to network latency and packet loss. A streamer in Australia sending video across the Pacific Ocean to US servers would experience noticeable delays and dropped frames. By placing ingest servers close to streamers, we get the video into our network quickly where we can then transport it over optimized backbone connections.

#### Ingest Servers
These servers are the first to receive the streamer's video. They speak RTMP (Real-Time Messaging Protocol), the industry standard protocol that all major streaming software supports.
When a streamer connects, the ingest server:
1. Authenticates the connection using the stream key
2. Validates the video format (codec, resolution, bitrate)
3. Begins forwarding video frames to the transcoding pipeline
4. Sends health metrics to the control plane so we know the stream is active

Ingest servers are relatively simple but must be highly reliable. If an ingest server crashes mid-stream, the broadcast drops for that streamer. We deploy multiple ingest servers in each region and implement automatic failover.

### The Ingest Flow in Action
Let's trace through what happens when a streamer starts broadcasting:
1. **DNS Resolution:** The streamer's software resolves `live.twitch.example` and gets directed to their nearest ingest server based on IP geolocation.
2. **RTMP Handshake:** The software establishes an RTMP connection and sends the stream key. This is a secret token that proves the streamer's identity.
3. **Authentication:** The ingest server calls the Auth Service to validate the stream key. This confirms the user is allowed to stream and is not banned.
4. **Stream Creation:** A record is created in the database marking this stream as live. This makes the stream discoverable to viewers.
5. **Video Forwarding:** Once authenticated, every video frame from the streamer is forwarded to the transcoding pipeline for processing.

The ingest server acts as a bridge between the unpredictable public internet and our controlled internal network.

## 4.2 Requirement 2: Video Processing (Transcoding)
Raw video from streamers arrives in various formats and qualities. One streamer might send 4K at 20 Mbps, another might send 720p at 3 Mbps. Some use modern codecs like H.265, others use H.264. 
We need to normalize this variety and produce consistent output that works for all viewers. More importantly, we need to create multiple quality levels. A viewer on a fast home connection wants 1080p, but a viewer on mobile data might only be able to handle 360p. 
Adaptive bitrate streaming solves this by giving the player multiple options to choose from.

### Components for Transcoding

#### Message Queue
Between the ingest servers and transcoders, we place a message queue. This decoupling is important for several reasons:
- **Handling bursts:** When many streamers go live simultaneously, the queue absorbs the spike while transcoders catch up.
- **Fault tolerance:** If a transcoder crashes, the video frames in the queue are not lost. Another transcoder picks them up.
- **Backpressure:** If transcoders are overloaded, the queue signals this back to ingest servers rather than dropping frames silently.

We use a high-throughput queue like Apache Kafka or Amazon Kinesis that can handle hundreds of thousands of messages per second.

#### Transcoding Service
This is a cluster of GPU-enabled servers that do the heavy lifting of video encoding. Each transcoder pulls raw video segments from the queue and produces multiple outputs.
The transcoding process involves:
1. **Decoding** the incoming video (H.264 or H.265 to raw frames)
2. **Scaling** to different resolutions (1080p → 720p → 480p → 360p)
3. **Encoding** each resolution at the appropriate bitrate
4. **Segmenting** the output into small chunks for HLS delivery

Modern GPUs can encode multiple streams in real-time using hardware acceleration (NVENC on NVIDIA cards). A single GPU can typically handle 10-20 simultaneous transcoding jobs depending on the output complexity.

### Transcoding Pipeline Details
Each transcoder produces HLS (HTTP Live Streaming) output. HLS breaks video into small segments (typically 2-6 seconds each) and generates a playlist file (manifest) that lists all available segments.
**Transcoding Output Example:**
For a single stream, the transcoder produces the following files:
| Quality | Resolution | Bitrate | Segment Size (4s) |
| --- | --- | --- | --- |
| Source | 1920x1080 | 6 Mbps | ~3 MB |
| High | 1280x720 | 3 Mbps | ~1.5 MB |
| Medium | 854x480 | 1.5 Mbps | ~750 KB |
| Low | 640x360 | 800 Kbps | ~400 KB |

The manifest file `master.m3u8` lists all quality levels:
The player reads this manifest, sees what quality options are available, and selects the highest quality that works with the viewer's current bandwidth.

## 4.3 Requirement 3: Video Delivery
With millions of viewers watching simultaneously, we need an efficient way to get video from our transcoding infrastructure to viewers around the world. This is where the 15 Tbps egress bandwidth we calculated earlier becomes a real engineering challenge.
The solution is a **Content Delivery Network (CDN)**. Instead of serving all video from our origin servers, we cache video segments at edge locations close to viewers. When a viewer in Tokyo requests a segment, they get it from a Tokyo edge server, not from our US data center.

### Components for Video Delivery

#### Origin Servers
These are the authoritative source for all video content. Transcoders write segments here, and CDN edge servers fetch segments from here when they do not have them cached.
Origin servers store:
- Live stream segments (temporary, deleted after stream ends)
- HLS manifests for each stream and quality level
- VOD content (permanently, with tiered storage)

#### Content Delivery Network (CDN)
The CDN is a globally distributed network of edge servers that cache video content close to viewers. When a viewer requests a segment:
1. The request goes to the nearest CDN edge server
2. If the edge has the segment cached, it returns it immediately (cache hit)
3. If not cached, the edge fetches from origin, caches it, then returns it (cache miss)

For live streaming, cache hit rates are typically very high because:
- Many viewers request the same segment within seconds of each other
- Segments are small (a few MB) so many fit in cache
- The manifest tells players about new segments, creating predictable access patterns

#### Playback Service
This service generates personalized playback URLs for viewers and handles authentication for subscription-only content.
When a viewer wants to watch a stream, the Playback Service:
1. Verifies the viewer is allowed to watch (public stream? subscriber-only?)
2. Generates a signed URL that grants temporary access to the CDN
3. Returns the URL along with available quality options

### The Video Delivery Flow
Let's trace through what happens when a viewer starts watching a stream:
1. **Playback URL Request:** The viewer's browser or app calls our API to get the playback URL for the stream.
2. **Manifest Fetch:** The player fetches the master manifest from the CDN, which lists all available quality levels.
3. **Quality Selection:** The player analyzes available bandwidth and selects an appropriate quality level to start with.
4. **Continuous Segment Fetching:** The player enters a loop where it fetches new segments every few seconds. As long as segments arrive before the current playback position catches up, the video plays smoothly.
5. **Adaptive Bitrate Switching:** If network conditions change (bandwidth drops), the player can switch to a lower quality mid-stream to prevent buffering.

### Cache Behavior and TTLs
Getting cache settings right is crucial for live streaming:
**Manifests need short TTLs:** The manifest tells the player which segments exist. For a live stream, new segments are created every few seconds. If we cache the manifest for too long, viewers will not discover new segments and their stream will freeze.
**Segments can have long TTLs:** Once a segment is created, it never changes. We can cache segments for hours or even days. This maximizes cache hit rates and minimizes origin load.

## 4.4 Requirement 4: Live Chat
Video is only half of the Twitch experience. The other half is the live chat where viewers react to the action, share jokes, and feel part of a community. Building chat at Twitch scale is its own challenge, with different requirements than the video pipeline.
The key challenge is **fanout**. When one viewer sends a message in a stream with 100,000 viewers, that single message needs to be delivered to 100,000 connected clients within 500 milliseconds. Traditional request-response APIs do not work well here since we need to push messages to clients in real-time.

### Components for Live Chat

#### Chat Gateway
The Chat Gateway maintains persistent WebSocket connections with viewers. Unlike HTTP where each request is independent, WebSocket connections stay open for the entire viewing session, allowing the server to push messages to clients at any time.
Each Chat Gateway instance manages thousands of concurrent WebSocket connections. The gateway handles:
- Connection lifecycle (connect, disconnect, reconnect)
- Message serialization and transmission
- Connection health monitoring (heartbeats)

#### Chat Service
This is the brain of the chat system. It processes incoming messages and decides where they should go.
When a message arrives, the Chat Service:
1. Validates the message (length, content, rate limits)
2. Checks user permissions (is the user banned? is chat in subscriber-only mode?)
3. Applies moderation (blocked words, suspicious patterns)
4. Persists the message for VOD chat replay
5. Publishes the message for delivery to all viewers

#### Pub/Sub System
The Pub/Sub system (like Redis Pub/Sub or Apache Kafka) distributes messages across multiple Chat Gateway instances. When a message is published, every gateway subscribed to that stream's chat room receives it and forwards it to their connected viewers.
This enables horizontal scaling: we can add more Chat Gateway instances to handle more connections, and the Pub/Sub system ensures they all receive the messages they need.

### The Chat Message Flow
1. **Message Submission:** Viewer A sends a chat message through their WebSocket connection to Chat Gateway 1.
2. **Processing:** The gateway forwards the message to the Chat Service, which validates it, checks permissions, and applies moderation rules.
3. **Publication:** The Chat Service publishes the message to the Pub/Sub system on the channel for this stream's chat room.
4. **Distribution:** All Chat Gateway instances subscribed to this channel receive the message.
5. **Delivery:** Each gateway forwards the message to all viewers connected to it who are watching this stream. The original sender (Viewer A) also receives the message, confirming it was accepted.

### Chat System Architecture
The Message Store (Cassandra) persists chat messages for two purposes:
1. **VOD Chat Replay:** When viewers watch recorded VODs, they can see the original chat synchronized with the video
2. **Moderation History:** Moderators can review past messages when investigating reports

## 4.5 Putting It All Together
Now that we have designed both the video pipeline and chat system, let's step back and see the complete architecture. These systems run in parallel, sharing some infrastructure (like the metadata database) but scaling independently.

### Component Responsibilities Summary
| Component | Purpose | Scaling Strategy |
| --- | --- | --- |
| Stream Router | Direct streamers to nearest ingest | GeoDNS (managed service) |
| Ingest Servers | Accept RTMP streams, authenticate | Horizontal per region |
| Message Queue | Buffer between ingest and transcoding | Kafka partitions |
| Transcoders | Convert video to multiple qualities | Horizontal (GPU instances) |
| Origin Storage | Store segments and manifests | Object storage (auto-scales) |
| CDN | Distribute video globally | Managed service (auto-scales) |
| Chat Gateway | Manage WebSocket connections | Horizontal (connection-based) |
| Chat Service | Process and route messages | Horizontal (stateless) |
| Pub/Sub | Distribute messages to gateways | Redis Cluster |

The architecture has clear separation of concerns:
- The **video pipeline** (top half) handles the compute-intensive work of transcoding and the bandwidth-intensive work of delivery.
- The **chat system** (bottom) handles the connection-intensive work of maintaining millions of WebSockets and the fanout-intensive work of message distribution.

Both systems share the metadata database for stream information and user data, but they scale independently based on their specific bottlenecks.
# 5. Database Design
With the high-level architecture in place, let's zoom into the data layer. Our platform has diverse storage needs that call for different database technologies.

## 5.1 Choosing the Right Databases
Different access patterns demand different storage solutions. Forcing everything into a single database type leads to either poor performance or excessive complexity. 
Let's match our data to the right storage technology.
| Data Type | Storage Solution | Reasoning |
| --- | --- | --- |
| Users, Streams, Subscriptions | PostgreSQL | Complex queries, transactions, relational integrity between entities |
| Chat Messages | Cassandra | High write throughput, time-series access pattern, horizontal scaling |
| Video Segments | S3/Object Storage | Cost-effective for large binary files, built-in CDN integration |
| Real-Time Metrics | Redis | Sub-millisecond access, pub/sub for chat, TTL for ephemeral data |

### Why PostgreSQL for Metadata?
User profiles, stream metadata, and subscriptions have complex relationships. A user has many streams, streams have many viewers, viewers have subscriptions to streamers. These relationships benefit from:
- **Foreign key constraints** ensuring referential integrity
- **Transactions** for operations like "subscribe and charge payment"
- **Flexible querying** for analytics and search

PostgreSQL handles these requirements well and has excellent tooling for operations.

### Why Cassandra for Chat?
Chat messages have different characteristics:
- **Very high write volume:** 833 writes per second in steady state, much higher during spikes
- **Simple access pattern:** Always query by stream_id and time range
- **No complex relationships:** Messages do not join with other tables

Cassandra excels at this workload. Its log-structured storage handles high write throughput, and partitioning by stream_id distributes load across nodes.

### Why Object Storage for Video?
Video segments are large (hundreds of KB to several MB), write-once, and accessed sequentially. Object storage like S3 provides:
- **Infinite scale** without capacity planning
- **Low cost** per GB stored
- **Built-in durability** (11 nines on S3)
- **Direct CDN integration** for efficient delivery

## 5.2 Database Schema
Let's define the schema for our relational data.

### Users Table (PostgreSQL)
Stores account information for all platform users, both streamers and viewers.
| Field | Type | Description |
| --- | --- | --- |
| user_id | UUID (PK) | Unique user identifier |
| username | VARCHAR(50) | Display name, unique across platform |
| email | VARCHAR(255) | Login email, unique |
| password_hash | VARCHAR(255) | bcrypt hash of password |
| is_partner | BOOLEAN | Whether user is a partnered streamer (revenue sharing) |
| created_at | TIMESTAMP | Account creation time |

**Indexes:**
- Primary key on `user_id` for direct lookups
- Unique index on `username` for profile URLs
- Unique index on `email` for login

### Streams Table (PostgreSQL)
Tracks each broadcast session from start to finish.
| Field | Type | Description |
| --- | --- | --- |
| stream_id | UUID (PK) | Unique identifier for this broadcast |
| user_id | UUID (FK) | Streamer's user ID |
| title | VARCHAR(255) | Stream title shown to viewers |
| category_id | UUID (FK) | Game or category being streamed |
| status | ENUM | Current status: 'live', 'ended', 'processing' |
| started_at | TIMESTAMP | When stream went live |
| ended_at | TIMESTAMP | When stream ended (null if still live) |
| viewer_count | INTEGER | Peak concurrent viewers |
| vod_url | VARCHAR(500) | URL to recorded VOD after processing |

**Indexes:**
- Primary key on `stream_id`
- Index on `(user_id, started_at DESC)` for "recent streams by user"
- Index on `(status, viewer_count DESC)` for "top live streams"
- Index on `(category_id, status)` for "live streams in category"

### Subscriptions Table (PostgreSQL)
Tracks paid relationships between viewers and streamers.
| Field | Type | Description |
| --- | --- | --- |
| subscription_id | UUID (PK) | Unique subscription identifier |
| subscriber_id | UUID (FK) | User who subscribed |
| streamer_id | UUID (FK) | Streamer receiving subscription |
| tier | INTEGER | Subscription tier (1, 2, or 3) |
| started_at | TIMESTAMP | When subscription began |
| expires_at | TIMESTAMP | When subscription lapses if not renewed |
| is_gift | BOOLEAN | Whether this was gifted by another user |

**Indexes:**
- Primary key on `subscription_id`
- Unique index on `(subscriber_id, streamer_id)` for checking if subscribed
- Index on `(streamer_id, expires_at)` for listing active subscribers

### Chat Messages (Cassandra)
Chat messages use a different schema optimized for time-series access.
| Field | Type | Description |
| --- | --- | --- |
| stream_id | UUID | Stream this message belongs to (partition key) |
| timestamp | TIMESTAMP | When message was sent (clustering key) |
| message_id | UUID | Unique message identifier |
| user_id | UUID | Sender's user ID |
| message | TEXT | Message content |
| badges | LIST<TEXT> | Badges displayed at time of message |

**Primary Key:** `(stream_id, timestamp)`
This design partitions messages by stream and orders them by time within each partition. The query "get messages for stream X between time A and B" is extremely efficient since it reads from a single partition in sorted order.
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often go deeper into specific components. In this section, we will explore the trickiest parts of our design: streaming protocols, handling hot partitions, scaling chat, VOD recording, global distribution, and fault tolerance.
These are the topics that distinguish a good system design answer from a great one.

## 6.1 Video Streaming Protocols
The choice of streaming protocol significantly impacts latency, compatibility, and scalability. Let's understand the options and their trade-offs.

### Understanding the Protocol Landscape

### HLS (HTTP Live Streaming)
HLS is the most widely deployed streaming protocol, developed by Apple and now supported everywhere.
**How it works:**
The transcoder breaks video into small segments (typically 2-10 seconds each) and generates a playlist file (manifest) listing all available segments. The player fetches the manifest, picks a quality level, then downloads segments one by one as they become available.
**Advantages:**
- **Universal compatibility:** Works on every browser, mobile OS, smart TV, and streaming device
- **CDN-friendly:** Standard HTTP requests cache beautifully at CDN edges
- **Adaptive bitrate:** Players automatically switch quality based on available bandwidth
- **Robust:** Missing a segment causes a brief glitch, not a complete failure

**Disadvantages:**
- **Higher latency:** Segments must be completely encoded before delivery, adding 10-30 seconds of delay
- **Segment boundaries:** Quality switching can only happen at segment boundaries

### Low-Latency HLS (LL-HLS)
Apple's extension to HLS that dramatically reduces latency while maintaining compatibility.
**How it works:**
Instead of waiting for complete segments, LL-HLS introduces "partial segments" (parts). The server can push parts to the CDN as soon as they are encoded, and players can request parts before the full segment is ready.
**Advantages:**
- **Low latency:** Achieves 2-5 second delay, close to real-time
- **Backwards compatible:** Falls back to regular HLS for older players
- **Still CDN-friendly:** Parts are still HTTP objects that can be cached

**Disadvantages:**
- **More complex:** Both server and player need to understand partial segments
- **Higher request rate:** More HTTP requests per second (one per part instead of one per segment)
- **Tighter timing:** Less buffer means less tolerance for network hiccups

### WebRTC
Originally designed for video conferencing, WebRTC provides the lowest possible latency.
**How it works:**
WebRTC establishes peer-to-peer or peer-to-server connections using UDP. Video frames are sent immediately after encoding, without waiting for segment boundaries. The protocol handles packet loss through selective retransmission.
**Advantages:**
- **Sub-second latency:** As close to real-time as technically possible
- **Bidirectional:** Supports two-way communication (useful for interactive features)

**Disadvantages:**
- **Poor scalability:** Each viewer needs a separate connection. Serving 100,000 viewers requires 100,000 connections
- **No CDN caching:** Cannot use traditional HTTP caching infrastructure
- **Less robust:** UDP packet loss can cause visible artifacts

### Which Protocol Should We Choose?
| Protocol | Latency | Scalability | Best For |
| --- | --- | --- | --- |
| HLS | 10-30s | Excellent | VOD, casual live viewing |
| LL-HLS | 2-5s | Very Good | Interactive live streams |
| WebRTC | <1s | Poor | Small audiences, conferencing |

**For Twitch-scale streaming, LL-HLS is the right choice.** It provides latency low enough for meaningful viewer-streamer interaction while scaling to millions of concurrent viewers through standard CDN infrastructure.
We use regular HLS as a fallback for older devices that do not support LL-HLS, accepting higher latency for broader compatibility.

## 6.2 Handling Popular Streams (Hot Partitions)
One of the most challenging aspects of building a live streaming platform is the "hot streamer" problem. When a popular streamer with millions of followers goes live, the sudden influx of viewers creates extreme load on specific parts of our system.

### Understanding the Problem
Consider what happens when a streamer with 500,000 concurrent viewers goes live:
This creates several challenges:
1. **Origin server overload:** If every request went to origin, we would need massive origin capacity for just one stream
2. **CDN cache stampedes:** When a new segment is created, thousands of requests arrive before the cache is populated
3. **Database hot spots:** The stream metadata row gets hammered with read requests

### Solution 1: Aggressive CDN Caching
The first line of defense is ensuring that CDN caches are effective.
**Strategy:**
Configure CDN with stream-aware caching policies. Even though live segments are fresh content, we can cache them for short periods (2-4 seconds). During that window, thousands of requests can be served from cache.
This header tells the CDN:
- Cache the segment for 2 seconds
- If a request arrives after 2 seconds, serve the stale content while fetching a fresh copy
- This prevents the "thundering herd" where everyone waits for a fresh fetch

**Result:** Only 1 request per segment reaches origin, regardless of how many viewers there are.

### Solution 2: Origin Shielding
Even with good caching, CDN edges around the world will all have cache misses at roughly the same time (when a new segment is created). Origin shielding adds a caching layer between edge and origin.
**How it works:**
1. All edge servers route their cache misses to a "shield" server instead of directly to origin
2. The shield consolidates identical requests. If 50 edges miss simultaneously, the shield makes one request to origin
3. The shield caches the response and serves all waiting edge requests

This reduces origin traffic by another order of magnitude.

### Solution 3: Request Coalescing
When multiple requests arrive for the same uncached content, we want only one actual fetch to happen.
**Implementation:**
This prevents duplicate fetches even when requests arrive milliseconds apart.

### Solution 4: Predictive Scaling
For truly popular streamers, we can anticipate the load and pre-provision resources.
**Signals for prediction:**
- Streamer's historical viewership patterns
- Current follower count and how many are online
- Scheduled events (tournaments, game releases, special streams)
- Social media activity (Twitter announcements tend to precede viewer spikes)

**Proactive actions:**
- Pre-warm CDN caches with the stream's first segment
- Allocate dedicated transcoding capacity
- Spin up additional chat gateway instances
- Alert on-call engineers for manual intervention if needed

### Summary: Defense in Depth
Handling hot partitions requires multiple layers of defense:
| Layer | Mechanism | Impact |
| --- | --- | --- |
| CDN Edge | Short TTL caching | Handles normal load |
| Origin Shield | Request consolidation | Reduces origin traffic 10-50x |
| Request Coalescing | Deduplicate in-flight requests | Prevents thundering herd |
| Predictive Scaling | Pre-provision for known events | Prevents surprise overload |

Each layer catches what the previous layer missed, ensuring popular streams do not bring down the platform.

## 6.3 Chat System Scaling
The chat system faces challenges fundamentally different from the video pipeline. While video is about bandwidth (moving large amounts of data), chat is about connections and fanout (delivering small messages to many recipients quickly).

### The Fanout Challenge Revisited
Let's be concrete about what "fanout" means:
A traditional approach where a single server handles all deliveries would need to push 1 million messages in 500ms, which is 2 million messages per second sustained. This is not feasible for a single server.

### Architecture: Sharded Chat Rooms
For large streams, we partition viewers across multiple logical shards, each served by dedicated Chat Gateway instances.
**How it works:**
1. When a viewer connects, they are assigned to a shard based on a hash of their user_id
2. Each shard has its own set of Chat Gateway instances
3. When a message comes in, it is duplicated to all shards
4. Each shard's gateways deliver to their subset of viewers

**Trade-offs:**
Viewers in different shards might see messages in slightly different orders due to network timing. For chat, this is acceptable since exact ordering does not matter for the user experience.

### Connection Management
Each Chat Gateway maintains thousands of WebSocket connections. Managing these connections efficiently is crucial.
**Connection lifecycle:**
**Heartbeats:**
WebSocket connections can silently die (network issues, client crashes). We detect this using heartbeats:
- Server sends a ping every 30 seconds
- Client must respond with pong within 10 seconds
- No response = connection considered dead, resources cleaned up

**Graceful degradation:**
For clients that cannot maintain WebSocket connections (corporate firewalls, certain mobile networks), we fall back to long polling:
- Client makes HTTP request
- Server holds the request open until a message arrives or timeout
- Client immediately makes another request after receiving response

Long polling has higher latency and overhead, but works through almost any network.

### Rate Limiting
Without rate limiting, a single malicious user could flood chat with thousands of messages per second, degrading the experience for everyone.
**Multi-level rate limiting:**
| Level | Limit | Purpose |
| --- | --- | --- |
| Per-user | 20 messages/minute | Prevent individual spam |
| Per-room | 10,000 messages/minute | Protect against coordinated attacks |
| Global | 1 million messages/minute | System protection |

**Implementation using Redis:**
This approach is efficient (O(1) per message), distributed (works across multiple Chat Service instances), and self-cleaning (keys expire automatically).

## 6.4 VOD Recording and Storage
Recording streams for later viewing is a core feature, but the storage requirements are substantial. 2.5 PB per day adds up quickly, requiring careful consideration of storage tiers and retention policies.

### Recording Architecture
During a live stream, video segments are written to origin storage for CDN delivery. The Recording Service collects these segments and assembles them into a cohesive VOD.
**Recording workflow:**
1. **During stream:** Segments are written to origin storage with short retention (hours)
2. **Stream ends:** Recording Service is notified, begins collecting all segments
3. **Assembly:** Segments are validated, ordered, and combined into a contiguous VOD
4. **Processing:** Generate thumbnails, chapter markers, and duration metadata
5. **Storage:** Write VOD to hot storage, make available to viewers

### Storage Tiering
Not all VODs are accessed equally. A stream from yesterday gets many views, while a stream from six months ago rarely does. We use tiered storage to optimize cost.
| Tier | Storage Type | Access Time | Cost | Content |
| --- | --- | --- | --- | --- |
| Hot | SSD/NVMe | <10ms | $$$ | Last 7 days of VODs |
| Warm | HDD | <100ms | $$ | 7-30 day old VODs |
| Cold | S3 Glacier | Minutes-hours | $ | 30+ day old VODs |

**Automatic tiering:**
A background job moves VODs between tiers based on age:
- New VOD → Hot storage
- After 7 days → Move to warm storage
- After 30 days → Move to cold storage

When a viewer requests a cold VOD, we initiate a restore (taking a few minutes) and notify them when it is ready.

### Quality Retention
Storing every quality level forever is wasteful since older VODs are rarely watched, and when they are, viewers often accept lower quality.
**Retention policy:**
This reduces long-term storage by 60-70% while maintaining reasonable quality for archived content.

### Chat Synchronization
VODs are more engaging when viewers can see the original chat. We store chat messages with stream timestamps, enabling synchronized playback.
The VOD player fetches chat messages in batches as the playback position advances, displaying them alongside the video.

## 6.5 Global Distribution and Latency Optimization
A global platform must provide a good experience for viewers everywhere. A viewer in Singapore should not have noticeably worse latency than a viewer in San Francisco.

### Multi-Region Architecture
We deploy infrastructure in multiple regions, with each region handling local traffic:
| Region | Components | Purpose |
| --- | --- | --- |
| US East | Full stack + DB Primary | Primary region, handles global coordination |
| US West | Full stack + DB Replica | Redundancy, West Coast streamers/viewers |
| EU West | Ingest + Processing + Replica | European streamers and viewers |
| Asia Pacific | Ingest + Processing + Replica | Asian streamers and viewers |

### Ingest Optimization
The worst experience for streamers is dropped frames or disconnections. By placing ingest servers in every region, we minimize the distance video must travel over the public internet.
**Streamer in Tokyo without regional ingest:**
**Streamer in Tokyo with regional ingest:**
The video still gets processed centrally (for simplicity), but the critical first hop happens locally.

### Latency Budget Analysis
For our target of 10-second end-to-end latency, here is how the budget breaks down:
| Stage | Budget | Typical Actual | Notes |
| --- | --- | --- | --- |
| Capture + Encode | 2s | 1-2s | Streamer's hardware |
| Ingest Upload | 1s | 0.5-1s | Depends on streamer's connection |
| Transcoding | 2s | 1-2s | Segment length + processing |
| CDN Distribution | 1s | 0.2-0.5s | Edge cache propagation |
| Player Buffer | 4s | 2-4s | Trade-off: stability vs latency |
| Total | 10s | 5-10s | Typical range |

With LL-HLS and well-optimized infrastructure, most viewers experience 5-7 seconds of latency, comfortably under our target.

### Multi-CDN Strategy
Relying on a single CDN provider creates a single point of failure. We use multiple CDNs:
- **Primary CDN:** Handles majority of traffic (best price/performance)
- **Secondary CDN:** Failover and specific regions where primary is weak
- **Specialty CDN:** For regions with unique requirements (China, etc.)

Real-time monitoring detects CDN issues and automatically shifts traffic:
- Track error rates and latency per CDN per region
- If error rate exceeds threshold, route new viewers to secondary
- Gradual migration to avoid overwhelming secondary

## 6.6 Fault Tolerance and Recovery
Live streaming has zero tolerance for extended outages. When a stream drops, viewers leave and may not come back. Our architecture must handle failures gracefully.

### Stream Continuity
**Problem:** If an ingest server fails mid-stream, the broadcast drops.
**Solution: Redundant Ingest**
Advanced streaming software can send to multiple ingest points simultaneously:
If the primary connection fails:
1. Backup ingest detects it has the "freshest" data
2. Pipeline switches to backup feed
3. Transition is seamless since video was being received all along

### Transcoder Failure
**Problem:** A transcoding server crashes while processing a stream.
**Solution: Stateless transcoders + Durable queue**
Since transcoders are stateless (they process individual segments independently) and the message queue is durable:
1. Transcoder crashes
2. Unprocessed segments remain in queue
3. Other transcoders pick up the work
4. Viewers might see a brief quality reduction (missing some output qualities for a few seconds)

The stream continues with minimal visible impact.

### CDN Failure
**Problem:** A CDN provider experiences a major outage.
**Solution: Multi-CDN with health monitoring**
We continuously monitor CDN health:
- Synthetic requests to measure latency and error rate
- Real user monitoring (RUM) data from players
- CDN-provided status APIs

When issues are detected:
1. Stop routing new viewers to affected CDN
2. For existing viewers, player detects failures and retries from alternative source
3. Traffic gradually shifts to healthy CDN

### Database Failure
**Problem:** PostgreSQL primary becomes unavailable.
**Solution: Synchronous replication with automatic failover**
- Writes go to primary, synchronously replicated to standby
- Health monitor continuously checks primary
- If primary fails, standby is promoted to primary
- Application reconnects to new primary

**Trade-off:** Synchronous replication adds write latency (must wait for standby acknowledgment) but guarantees zero data loss.

### Graceful Degradation
Some failures can be handled by reducing functionality rather than failing entirely:
| Failure | Degradation |
| --- | --- |
| Chat service down | Viewers can still watch, chat disabled |
| Quality level unavailable | Player switches to available qualities |
| VOD service down | Live streams still work, VODs unavailable |
| Subscription service down | Premium features disabled, basic viewing works |

The principle: core functionality (watching live streams) should be the last thing to fail.
# References
- [HLS Authoring Specification](https://developer.apple.com/documentation/http-live-streaming/hls-authoring-specification-for-apple-devices) - Apple's official HLS specification and best practices
- [Low-Latency HLS](https://developer.apple.com/videos/play/wwdc2019/502/) - WWDC session explaining LL-HLS implementation
- [Scaling Twitch Chat](https://blog.twitch.tv/en/2022/04/26/twitch-engineering-an-introduction-and-overview/) - How Twitch handles chat at scale
- [Video Streaming Protocols Compared](https://www.wowza.com/blog/streaming-protocols) - Comparison of HLS, DASH, WebRTC, and other protocols
- [Building a CDN](https://www.akamai.com/resources/reference-architecture/content-delivery-network) - Akamai's reference architecture for content delivery

# Quiz

## Design Twitch Quiz
For a Twitch-like platform, what is the primary reason a CDN is essential?