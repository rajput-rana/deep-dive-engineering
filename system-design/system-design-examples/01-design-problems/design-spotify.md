# Design Spotify

## What is Spotify?

[Spotify](https://open.spotify.com/) is a music streaming platform that allows users to search, discover, and listen to millions of songs and podcasts on demand. It provides personalized recommendations, curated playlists, offline downloads, and features like shuffle, repeat, and cross-device syncing.
Users can follow artists, share playlists, and explore trending or new releases.
With over **600 million** monthly active users (MAU) and **200 million** paid users, Spotify is the most popular music streaming platform in the world.
**Other Popular Examples:** [Apple Music](https://www.apple.com/apple-music/), [Amazon Music](https://music.amazon.com), [YouTube Music](https://music.youtube.com)
This system design problem touches on several fundamental concepts: content delivery at global scale, real-time streaming protocols, search infrastructure, recommendation systems, and high availability architecture.
In this chapter, we will walk through the **high-level design of a music streaming platform like Spotify.**
Let’s begin by clarifying the requirements.
# 1. Requirements Gathering
Before jumping into architecture diagrams, we need to understand what we are building. 
Music streaming might seem straightforward, but the requirements can vary significantly. Are we designing for millions or hundreds of millions of users? Do we need to support offline playback? How sophisticated should the recommendation engine be? These questions shape our design decisions.
Here is how a requirements discussion might unfold in an interview:
**Candidate:** "How many users should the system support, and what does daily usage look like?"
**Interviewer:** "Let's design for 500 million total users, with about 200 million daily active users. On an average day, we see around 1 billion streams."
**Candidate:** "That's substantial scale. A billion streams per day means we are dealing with serious CDN and bandwidth requirements. Should I focus primarily on music, or do we need to handle podcasts and other audio formats as well?"
**Interviewer:** "Focus on music streaming for now. Podcasts have different characteristics like longer duration and less repeat listening, so you can mention them but don't need to design for them in detail."
**Candidate:** "Understood. What about the user experience around playback? I am thinking about latency requirements and whether users can download content for offline listening."
**Interviewer:** "Latency is critical. Users expect to hear audio within 200ms of pressing play. As for offline playback, yes, that's an important feature for premium subscribers, especially for people with limited data plans or unreliable connectivity."
**Candidate:** "Personalization is a big part of what makes these services sticky. Should I include the recommendation system in the design, or treat it as out of scope?"
**Interviewer:** "Cover the high-level approach to recommendations, though you don't need to dive deep into the ML algorithms."
**Candidate:** "One more question: should I design the content ingestion pipeline, meaning how artists upload music to the platform?"
**Interviewer:** "That's a separate system entirely. Focus on the consumer-facing streaming experience."
This conversation reveals several important constraints that will influence our design. Let's formalize these into functional and non-functional requirements.

## 1.1 Functional Requirements
Based on our discussion, here are the core features our system must support:
- **Search:** Users can search for songs, albums, artists, and playlists. Search must be fast (under 100ms) and handle typos, partial matches, and multiple languages.
- **Stream Music:** Users can play any song on-demand with minimal latency. The system should handle quality adaptation based on network conditions.
- **Playlist Management:** Users can create, edit, delete, and share playlists. Playlists can contain thousands of songs and be collaborative.
- **Personalized Recommendations:** The system provides personalized recommendations based on listening history, liked songs, and contextual signals like time of day.
- **Offline Playback:** Premium users can download songs and playlists for offline listening, with appropriate DRM protection.

## 1.2 Non-Functional Requirements
Beyond features, we need to consider the qualities that make the system production-ready:
- **High Availability:** The system should target 99.99% uptime (roughly 52 minutes of downtime per year). Users expect music to be accessible whenever they want it, and outages are highly visible.
- **Low Latency:** Playback should start within 200ms of pressing play. Once playing, buffering should be rare even on variable network conditions.
- **Scalability:** The system must handle 1 billion+ streams per day across 200 million daily active users, with traffic patterns that spike during commute hours and weekends.
- **Global Reach:** Users expect low latency regardless of location. This requires edge infrastructure and CDN presence across major regions.
- **Durability:** User data like playlists, liked songs, and listening history must never be lost. Losing a user's carefully curated playlist would be unacceptable.

# 2. Back-of-the-Envelope Estimation
Before diving into the design, let's run some quick calculations to understand the scale we are dealing with. These numbers will guide our architectural decisions, particularly around CDN infrastructure, storage, and database selection.

### 2.1 Traffic Estimates
Starting with the numbers from our requirements discussion:

#### Streaming Traffic
We expect 1 billion streams per day. Let's convert this to queries per second (QPS):
Traffic is rarely uniform throughout the day. Music streaming sees significant spikes during morning and evening commutes, lunch breaks, and weekends. During peak hours, we might see 3x the average load:

#### Metadata Traffic
Every stream request triggers additional metadata lookups: song info, artist details, album art URLs, lyrics. Users also browse, search, and load playlists. This metadata traffic is typically 5-10x higher than the stream traffic:
These numbers are significant. At peak, we are handling over 300,000 requests per second across all services. This is why we need aggressive caching at multiple layers.

### 2.2 Storage Estimates
Music streaming has an interesting storage profile: a large catalog of audio files that rarely changes, combined with user data that grows continuously.

#### Audio Files (The Big One)
The audio catalog is where most of the storage goes:
- Total songs in catalog: 100 million songs
- Each song stored in multiple quality levels (64, 96, 160, 320 kbps)
- Average total size per song across all qualities: ~10 MB

One petabyte is substantial but manageable with object storage services like S3. The key insight is that this data is mostly static. Songs don't change once uploaded, which makes caching highly effective.

#### Metadata
Song metadata is relatively small but needs to be fast:
| Data Type | Estimate | Notes |
| --- | --- | --- |
| Song metadata | 100M × 2 KB = 200 GB | Title, artist, album, duration, genre |
| Artist profiles | 10M × 5 KB = 50 GB | Bio, images, discography |
| Album data | 20M × 3 KB = 60 GB | Track lists, artwork, release info |

This comfortably fits in memory for caching, which is important for the response times we need.

#### User Data
User data grows continuously and needs different handling:
| Data Type | Estimate | Notes |
| --- | --- | --- |
| User profiles | 500M × 2 KB = 1 TB | Preferences, settings, subscription |
| Playlists | 500M × 5 KB = 2.5 TB | Average user has 5-10 playlists |
| Listening history | 500M × 8 KB = 4 TB | Last 6 months of plays |

### 2.3 Bandwidth Estimates
Bandwidth is where music streaming gets expensive. Each stream transfers significant data:
Five petabytes per day of bandwidth is massive. At typical cloud egress rates ($0.05-0.09 per GB), this would cost millions per month without optimization. This is exactly why CDN infrastructure is not optional for music streaming. It is essential for both performance and cost control.

### 2.4 Key Insights
These estimates reveal several important design implications:
1. **CDN is critical:** With 5 PB of daily bandwidth, serving from origin is financially and technically impractical. Most streams must be served from edge caches.
2. **Read-heavy workload:** For every song uploaded (which happens through a separate pipeline), there are millions of plays. We should invest heavily in caching and optimize for read performance.
3. **Metadata fits in memory:** At 200 GB, song metadata can be cached aggressively. This enables the sub-100ms response times users expect.
4. **Audio storage is static:** Unlike user-generated content platforms, the audio catalog changes slowly. This makes CDN caching straightforward.
5. **User data is the scaling challenge:** While audio files are large but static, user listening history grows continuously and drives database scaling decisions.

# 3. Core APIs
With our requirements and scale understood, let's define the API contract. A music streaming service needs APIs for search, playback, playlist management, and recommendations. Let's walk through each one.

### 3.1 Search

#### Endpoint: GET /search
This is the entry point for discovery. Users type a query and expect relevant songs, artists, albums, and playlists back within milliseconds.

#### Request Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| query | string | Yes | The search term (e.g., "bohemian rhapsody", "queen") |
| type | string | No | Filter by type: "song", "artist", "album", "playlist". Default: all types |
| limit | integer | No | Number of results per type. Default: 20 |
| offset | integer | No | Pagination offset for results |

#### Example Response (200 OK):

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Invalid input | Empty query or malformed parameters |
| 429 Too Many Requests | Rate limited | Too many searches in short period |

### 3.2 Get Stream URL

#### Endpoint: GET /songs/{song_id}/stream
This is the critical path for playback. Instead of streaming audio directly through our API servers, we return a signed URL that points to a CDN edge server. This approach offloads bandwidth from our application tier and ensures users get audio from a server close to them.

#### Path Parameters:
| Parameter | Type | Description |
| --- | --- | --- |
| song_id | string | The unique identifier for the song |

#### Query Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| quality | string | No | Preferred quality: "low" (96kbps), "medium" (160kbps), "high" (320kbps) |

#### Example Response (200 OK):
The signed URL includes an authentication token and expiration time. This prevents URL sharing (the token is tied to the user) and limits the window for unauthorized access.

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 401 Unauthorized | Not authenticated | Missing or invalid auth token |
| 403 Forbidden | Access denied | Song unavailable in user's region, or subscription does not allow this quality |
| 404 Not Found | Song not found | Invalid song_id |

### 3.3 Create Playlist

#### Endpoint: POST /playlists
Creates a new playlist for the authenticated user.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| name | string | Yes | Playlist name (max 100 characters) |
| description | string | No | Playlist description |
| is_public | boolean | No | Whether the playlist is publicly visible. Default: true |

#### Example Request:

#### Example Response (201 Created):

### 3.4 Add Songs to Playlist

#### Endpoint: POST /playlists/{playlist_id}/songs
Adds one or more songs to an existing playlist. Songs are added at the end of the playlist by default.

#### Request Body:
The optional `position` parameter allows inserting songs at a specific index. If omitted, songs are appended.

#### Example Response (200 OK):

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 403 Forbidden | Not owner | User does not own the playlist |
| 404 Not Found | Not found | Playlist or one of the songs does not exist |

### 3.5 Get Recommendations

#### Endpoint: GET /recommendations
Returns personalized song recommendations based on the user's listening history and optional seed inputs.

#### Query Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| seed_songs | string | No | Comma-separated song IDs to base recommendations on |
| seed_artists | string | No | Comma-separated artist IDs |
| limit | integer | No | Number of recommendations (1-100). Default: 20 |

#### Example Response (200 OK):
The `reason` field provides transparency about why each song was recommended, which helps users understand and trust the recommendations.
# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complex diagram upfront, we will build the design incrementally, starting with the core user journey (streaming music) and adding components as we address each requirement. This mirrors how you would approach the problem in an interview.
Our system needs to handle four core operations:
1. **Stream Music:** Play any song with sub-200ms latency
2. **Search:** Find songs, artists, and albums instantly
3. **Manage Playlists:** Create, edit, and share playlists
4. **Get Recommendations:** Surface personalized music discovery

The system is heavily read-intensive. For every song added to the catalog (which happens through a separate ingestion pipeline), there are millions of streams. This read-to-write asymmetry means we should optimize aggressively for read performance, and caching will be essential at every layer.
Let's visualize the two primary paths through our system:
Notice how the stream path separates the control plane (getting a signed URL) from the data plane (actual audio delivery via CDN). This separation is key to handling billions of streams without our API servers becoming a bottleneck.
Let's build this architecture step by step.


This is the core functionality. When a user taps play, audio must start within 200ms. Once playing, buffering should be rare even on variable network conditions. Let's design for this critical path first.
When a user clicks play on a song, several things need to happen:
1. Validate the user has permission to play this song (subscription, region)
2. Generate a secure, time-limited URL for the audio file
3. Return the URL so the client can fetch audio directly from a CDN edge server
4. Track the play for analytics and royalty calculations

Let's introduce the components we need to make this work.

### Components for Streaming

#### API Gateway
Every request enters through the API Gateway. Think of it as the front door to our system, handling concerns that are common across all requests.
The gateway terminates SSL connections, validates request format, enforces rate limits, authenticates users via tokens, and routes requests to the appropriate backend service. By handling these cross-cutting concerns at the edge, we keep our application services focused on business logic.

#### Playback Service
This service handles the critical decision: should this user be allowed to play this song? It checks:
- Is the user authenticated with a valid session?
- Does their subscription tier allow the requested quality (320kbps is premium-only)?
- Is the song available in the user's geographic region (licensing varies by country)?
- Has the user exceeded any rate limits?

If all checks pass, the service generates a signed URL that grants temporary access to the audio file on the CDN. The URL includes an authentication token and expiration time, typically 15-30 minutes. This prevents URL sharing and limits the window for unauthorized access.

#### Content Delivery Network (CDN)
This is where the magic happens for low-latency playback. A CDN is a network of edge servers distributed globally. When a user in Tokyo requests audio, instead of fetching from our origin in Virginia, they get it from a nearby edge server.
For popular songs (think Taylor Swift's latest release), the audio is already cached at edge locations worldwide. The CDN can serve millions of concurrent streams without touching our origin servers. This is essential given our bandwidth estimates of 5 PB per day.

#### Object Storage
The actual audio files live in object storage (S3, Google Cloud Storage, or Azure Blob). Files are organized by song ID and quality level:
Each song exists in multiple quality levels to support adaptive bitrate streaming and different subscription tiers.

### The Streaming Flow in Action
Let's trace through this step by step:
1. **Client requests playback:** The user taps play. The client sends a request to our API Gateway with the song ID and the user's auth token.
2. **Gateway validates and routes:** The API Gateway verifies the token is valid, checks rate limits, and forwards the request to the Playback Service with the user's context.
3. **Playback Service checks entitlements:** The service looks up the song metadata (often from cache) and verifies the user can play this song. Premium-only songs require a premium subscription. Some songs are not available in certain countries due to licensing.
4. **Generate signed URL:** If all checks pass, the service generates a signed URL. This URL includes a cryptographic signature that proves the user was authorized at this moment. The signature expires after 15-30 minutes.
5. **Client fetches audio from CDN:** The client now has a URL pointing to a CDN edge server. It fetches the audio directly, bypassing our API entirely. This is crucial for scale.
6. **CDN serves or fetches:** If the song is popular, it's already cached at the edge. If not, the CDN fetches from origin (S3), caches it, and serves. Either way, the audio streams to the client.

**Why this design works:** By separating the control plane (authorization and URL generation) from the data plane (audio delivery), we can handle billions of streams. Our API servers handle lightweight authorization requests while the heavy lifting of audio delivery is handled by CDN infrastructure designed for exactly this purpose.


    CDNNode --> Mobile
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
        S1[This Service]
        S2[Search Service]
        S3[storage Service]
        S4[The Service]
        S5[application Service]
    end

    subgraph Data Storage
        DBCassandra[Cassandra]
        DBPostgreSQL[PostgreSQL]
        DBelasticsearch[elasticsearch]
    end

    subgraph Caching Layer
        CacheRedis[Redis]
    end

    subgraph Message Queue
        QueueKafka[Kafka]
    end

    subgraph Object Storage
        StorageS3[S3]
        StorageObjectStorage[Object Storage]
        Storageobjectstorage[object storage]
    end

    subgraph CDNLayer
        CDNNode[Content Delivery Network]
    end

    Web --> LB
    Mobile --> LB
    LB --> S1
    LB --> S2
    LB --> S3
    LB --> S4
    LB --> S5
    S1 --> DBCassandra
    S1 --> DBPostgreSQL
    S1 --> CacheRedis
    S1 --> QueueKafka
    S2 --> DBCassandra
    S2 --> DBPostgreSQL
    S2 --> CacheRedis
    S2 --> QueueKafka
    S3 --> DBCassandra
    S3 --> DBPostgreSQL
    S3 --> CacheRedis
    S3 --> QueueKafka
    S4 --> DBCassandra
    S4 --> DBPostgreSQL
    S4 --> CacheRedis
    S4 --> QueueKafka
    S5 --> DBCassandra
    S5 --> DBPostgreSQL
    S5 --> CacheRedis
    S5 --> QueueKafka
    S1 --> StorageS3
    S1 --> StorageObjectStorage
    S1 --> Storageobjectstorage
    StorageS3 --> CDNNode
    StorageObjectStorage --> CDNNode
    Storageobjectstorage --> CDNNode
    CDNNode --> Web
    CDNNode --> Mobile



## 4.2 Requirement 2: Music Search
Users need to find any song instantly. They type "bohemian" and expect to see Queen's Bohemian Rhapsody appear within milliseconds. Search must be fast (under 100ms), handle typos ("bohemain"), partial matches, and return results ranked by relevance.

### Components for Search

#### Search Service
This service handles all search queries. It does not query the primary database directly. Instead, it queries a dedicated search index optimized for text matching.
The Search Service parses queries, handles autocomplete requests, applies filters, and ranks results based on relevance and popularity. It also caches frequent queries since many users search for the same popular songs and artists.

#### Elasticsearch Cluster
We use Elasticsearch (or a similar search engine like OpenSearch) for full-text search. Elasticsearch is purpose-built for this use case:
- **Inverted indexes** enable fast text matching across 100 million songs
- **Fuzzy matching** handles typos ("bohemain" matches "bohemian")
- **Relevance scoring** ranks results by how well they match the query
- **Horizontal scalability** allows us to add nodes as the catalog grows

The search index contains denormalized data: song titles, artist names, album names, genres, and popularity scores. When a new song is added to the catalog, an indexing pipeline updates Elasticsearch.

### The Search Flow in Action
**Why cache search results?** Popular searches are repeated constantly. "Taylor Swift", "Drake", and "Bohemian Rhapsody" are searched thousands of times per minute. Caching these results for even a few minutes dramatically reduces load on Elasticsearch.

## 4.3 Requirement 3: Playlist Management
Users create playlists to organize their music. A playlist can contain anywhere from a few songs to thousands. Users expect to add songs instantly and have changes sync across all their devices.

### Components for Playlists

#### Playlist Service
Manages all playlist CRUD operations. Key responsibilities:
- Create, update, and delete playlists
- Add and remove songs (maintaining order)
- Handle collaborative playlists where multiple users can edit
- Manage sharing and privacy settings

#### Playlist Database
We need a database that handles:
- High read volume (users constantly load their playlists)
- Reasonable write volume (adding/removing songs)
- Efficient queries by user_id (show me all my playlists)
- Efficient ordering (songs have a position in the playlist)

We will discuss the specific database choice in the Database Design section.

### The Playlist Flow in Action
The cache invalidation is important: when a user adds a song on their phone, the change must appear immediately when they open the app on their laptop. By invalidating the cache, we ensure the next request fetches fresh data.

## 4.4 Requirement 4: Personalized Recommendations
This is what makes modern streaming services sticky. Users expect the app to know their taste and surface music they will love but haven't discovered yet. Features like "Discover Weekly" and "Daily Mix" drive significant engagement.
Recommendations combine two fundamentally different patterns: batch processing (generating recommendations offline) and real-time serving (delivering them instantly when requested).

### Components for Recommendations

#### ML Pipeline (Offline)
This batch processing system runs periodically (daily or weekly) to:
- Aggregate listening history across all users
- Train collaborative filtering models (users who liked X also liked Y)
- Generate user taste profiles from audio features
- Pre-compute personalized recommendations for each user

The pipeline produces recommendations that are stored and ready to serve. This is how features like "Discover Weekly" work: they are generated once per week and cached.

#### Feature Store
Stores computed features about users and songs:
- User taste vectors (what genres, moods, tempos they prefer)
- Song embeddings (numerical representations of audio characteristics)
- Contextual features (what users listen to in the morning vs evening)

#### Recommendation Service
Serves recommendations in real-time. For most requests, it simply fetches pre-computed recommendations from cache. For seed-based recommendations ("songs similar to X"), it may compute results on the fly using the feature store.

### The Recommendation Flow in Action
The key insight is that most recommendations are pre-computed. "Discover Weekly" is generated once per week for each user. When a user opens the app, we simply fetch their pre-computed playlist from cache. This approach allows us to use sophisticated ML models that would be too slow to run in real-time.

## 4.5 Putting It All Together
Now that we have designed each requirement, let's step back and see the complete architecture:
The architecture follows a layered approach, with each layer having a specific responsibility:
**Client Layer:** Users access the service through mobile apps, web browsers, or desktop applications. From our perspective, they all look the same: HTTP requests with authentication tokens.
**Edge Layer:** The CDN handles audio delivery at the edge, close to users geographically. The load balancer distributes API traffic across gateway instances.
**Gateway Layer:** The API Gateway handles authentication, rate limiting, and request routing. It is the single entry point for all API traffic.
**Application Layer:** Stateless services implement the business logic. Each service is independently deployable and horizontally scalable.
**Cache Layer:** Redis provides low-latency access to frequently requested data: song metadata, user sessions, search results, and pre-computed recommendations.
**Data Layer:** Different databases for different access patterns: Elasticsearch for search, relational databases for metadata and playlists, and potentially Cassandra for high-write-volume data like listening history.
**ML Infrastructure:** Offline pipelines train models and generate recommendations. The feature store provides fast access to user and song features.

### Component Responsibilities
| Component | Primary Responsibility | Scaling Strategy |
| --- | --- | --- |
| CDN | Audio delivery, edge caching | Managed service (auto-scales) |
| Load Balancer | Traffic distribution | Managed service |
| API Gateway | Auth, rate limiting, routing | Horizontal (stateless) |
| Playback Service | Stream authorization, URL signing | Horizontal (stateless) |
| Search Service | Query parsing, result ranking | Horizontal (stateless) |
| Playlist Service | Playlist CRUD operations | Horizontal (stateless) |
| Recommendation Service | Serve personalized content | Horizontal (stateless) |
| Elasticsearch | Full-text search | Add nodes to cluster |
| Redis Cluster | Hot data caching | Add nodes, shard by key |
| Databases | Persistent storage | Read replicas, sharding |
| Object Storage | Audio files | Managed (infinite scale) |

This architecture handles our requirements well: the CDN absorbs audio streaming traffic, the cache layer handles most read traffic, and the stateless services scale horizontally for everything else.
# 5. Database Design
With the high-level architecture in place, let's zoom into the data layer. Choosing the right database and designing an efficient schema are critical decisions that affect performance, scalability, and operational complexity.

## 5.1 Choosing the Right Databases
Music streaming has diverse data with very different access patterns. Song metadata needs complex queries and relationships. Playlists need fast reads by user. Listening history is append-heavy with billions of writes. No single database excels at all of these.
This is where polyglot persistence shines: using different databases for different data types, each optimized for its specific access pattern.
Let's think through why each data type maps to a specific database:

#### Song Metadata: PostgreSQL
Song, artist, and album data has natural relationships: songs belong to albums, albums belong to artists, artists can collaborate on songs. A relational database handles these relationships well with foreign keys and joins.
We need complex queries: find all songs by this artist, find albums released in this year, get the top 50 songs in this genre. PostgreSQL's rich query language handles this naturally.
The catalog (100 million songs) changes slowly and fits comfortably in a single database with read replicas. No need for the complexity of sharding.

#### Search Index: Elasticsearch
We already discussed this: full-text search, fuzzy matching, relevance scoring. Elasticsearch is purpose-built for these requirements. It sits alongside PostgreSQL, receiving updates when the catalog changes.

#### Playlists: Cassandra
Playlist access patterns are user-centric: show me all my playlists, load this specific playlist, add a song to this playlist. These queries always include a user_id, making it a perfect partition key.
Cassandra excels here because:
- It partitions data by user, so all of a user's playlists are on the same node
- Reads and writes within a partition are fast
- It scales horizontally as user count grows
- It handles high write throughput for active playlist editing

#### User Sessions and Recommendations: Redis
Session data (is this user logged in?) and pre-computed recommendations need sub-millisecond reads. Redis keeps this data in memory and handles millions of reads per second.
Redis also supports TTLs natively, which is perfect for session expiration and recommendation refresh cycles.

#### Listening History: Cassandra
This is the highest-write-volume data in the system. With 1 billion streams per day, we are writing 11,500+ events per second. Cassandra handles this write throughput while still supporting efficient reads by user (show me my recent listening history).
The partition key is user_id, and the clustering key is listened_at timestamp (descending). This means we can efficiently query "last 100 songs this user played" without scanning the entire table.

### Database Choice Summary
| Data Type | Database | Key Reasoning |
| --- | --- | --- |
| Song Metadata | PostgreSQL | Complex relationships, rich queries, stable catalog |
| Search Index | Elasticsearch | Full-text search, fuzzy matching, relevance scoring |
| Playlists | Cassandra | User-partitioned, high read/write throughput |
| User Sessions | Redis | Sub-millisecond reads, TTL support |
| Listening History | Cassandra | High write volume, time-series access pattern |
| Recommendations | Redis | Pre-computed, needs instant reads |

## 5.2 Database Schema
Now let's design the schema for each data store.

### Songs Table (PostgreSQL)
This is the heart of our catalog. Each row represents one song.
| Field | Type | Description |
| --- | --- | --- |
| song_id | UUID (PK) | Unique identifier for the song |
| title | VARCHAR(255) | Song title |
| artist_id | UUID (FK) | Reference to artists table |
| album_id | UUID (FK) | Reference to albums table |
| duration_ms | INTEGER | Song duration in milliseconds |
| release_date | DATE | When the song was released |
| genres | VARCHAR[] | Array of genre tags |
| audio_path | VARCHAR(500) | Path to audio in object storage (e.g., "songs/abc123/") |
| play_count | BIGINT | Total play count (updated periodically) |
| created_at | TIMESTAMP | When the record was created |

**Indexes:**

### Artists Table (PostgreSQL)
| Field | Type | Description |
| --- | --- | --- |
| artist_id | UUID (PK) | Unique identifier for the artist |
| name | VARCHAR(255) | Artist name |
| bio | TEXT | Artist biography |
| image_url | VARCHAR(500) | Profile image URL on CDN |
| monthly_listeners | INTEGER | Current monthly listener count (updated daily) |
| verified | BOOLEAN | Whether artist is verified |
| created_at | TIMESTAMP | When the record was created |

### Playlists Table (Cassandra)
Cassandra tables are designed around query patterns. Our primary queries are:
- Get all playlists for a user
- Get a specific playlist by ID
- Get songs in a playlist

The partition key is `user_id`, so all of a user's playlists are on the same node. The clustering key orders playlists by creation date (newest first).

### Playlist Songs Table (Cassandra)
The partition key is `playlist_id`, and songs are ordered by position. This makes loading a playlist efficient: one query returns all songs in order.

### User Listening History Table (Cassandra)
With this schema, we can efficiently query "last 50 songs user X played" since data is partitioned by user and ordered by timestamp.
**Why Cassandra handles the write volume:** With 200 million DAU and an average of 5 songs per session, we are writing 1 billion events per day. Cassandra distributes this across nodes and handles writes without locks, achieving the throughput we need.
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often go deeper into specific components. In this section, we will explore the trickiest parts of our design: audio streaming architecture, search infrastructure, personalization, scaling strategies, and offline playback.
These are the topics that distinguish a good system design answer from a great one.

## 6.1 Audio Streaming Architecture
Delivering audio with low latency and high quality is the core technical challenge. A user clicks play and expects music within 200ms. Once playing, there should be no buffering even when network conditions change. Let's explore how to achieve this at scale.

### Audio File Preparation
Before a song can be streamed, it goes through an ingestion pipeline that prepares it for delivery:

#### Step 1: Transcoding
The original high-quality audio (often WAV or FLAC from the label) is converted to multiple quality levels:
| Quality | Bitrate | File Size (4 min song) | Target Users |
| --- | --- | --- | --- |
| Very High | 320 kbps | ~10 MB | Premium users on WiFi |
| High | 160 kbps | ~5 MB | Standard quality |
| Normal | 96 kbps | ~3 MB | Low bandwidth/data saver |
| Low | 24 kbps | ~720 KB | Extreme data saver |

Multiple quality levels enable adaptive streaming: if network conditions degrade, the client can switch to a lower quality mid-song rather than buffering.

#### Step 2: Chunking
Each quality variant is split into small chunks, typically 5-10 seconds each. A 4-minute song becomes roughly 24-48 chunks per quality level.
Why chunk? Several reasons:
- **Faster start:** The client only needs the first chunk to start playing, not the entire file
- **Efficient seeking:** Jumping to 2:30 means fetching just that chunk, not everything before it
- **Quality switching:** The client can switch quality on chunk boundaries without audible artifacts
- **Better caching:** Individual chunks can be cached and evicted independently

#### Step 3: DRM Encryption
Each chunk is encrypted for digital rights management. The client decrypts on playback using a license key tied to the user's subscription. This prevents users from extracting and redistributing audio files.

### Streaming Protocol Options
There are several ways to deliver audio to clients. Let's compare the approaches:

#### Approach 1: Progressive Download
The simplest approach: the client requests the complete audio file and downloads it sequentially.
**Pros:**
- Simple to implement with standard HTTP
- Works everywhere

**Cons:**
- Cannot adapt quality mid-stream
- Seeking to the middle requires downloading everything before it (or range requests)
- No graceful handling of network changes

#### Approach 2: HTTP Live Streaming (HLS) or DASH
The modern standard for adaptive streaming. Audio is pre-chunked, and a manifest file describes available qualities and chunk URLs.
**How it works:**
1. Client fetches the manifest file listing all available quality levels and chunk URLs
2. Based on measured bandwidth, client selects a quality level
3. Client downloads chunks sequentially, measuring download speed
4. If bandwidth changes, client switches quality at the next chunk boundary

**Pros:**
- Adapts to changing network conditions
- Efficient seeking (jump to any chunk)
- Works well with CDN caching (chunks are small, static files)
- Industry standard with wide client support

**Cons:**
- More complex than progressive download
- Slight overhead from manifest requests

#### Approach 3: Custom Protocol
Spotify uses a proprietary streaming protocol optimized specifically for music. Key optimizations include:
- **Predictive buffering:** Pre-fetches the next song while the current one is playing
- **Gapless playback:** No silence between tracks in an album
- **Multiple connections:** Uses parallel connections for redundancy
- **Stutter-free algorithms:** Prioritizes playback continuity over quality

#### Recommendation for interviews
Use HLS/DASH as your answer. It's well understood, handles the core requirements (adaptive streaming, CDN compatibility), and is what most new streaming services would choose. Mention that mature services like Spotify have evolved custom protocols for specialized optimizations.

### CDN Caching Strategy
With 5 PB of daily bandwidth, CDN caching is essential for both cost and latency. But not all songs are equal: some are played millions of times per day, while others might be played once per year.

#### The Pareto Effect in Music
Music consumption follows an extreme power law:
- The top 1% of songs account for roughly 90% of all streams
- The top 10% covers 99%+ of streams
- The remaining 90% of the catalog (the "long tail") is rarely accessed

This distribution makes caching highly effective. Taylor Swift's latest single is requested millions of times per day and should be cached at every edge location. An obscure jazz recording from the 1960s might be requested once per month and can stay at origin.

#### Cache Warming Strategies:
1. **New releases:** When an anticipated album drops (Beyonce, Taylor Swift), pre-push it to all edge locations before the release time
2. **Trending content:** Monitor stream velocity and proactively cache songs that are gaining momentum
3. **Predictive caching:** When a user starts a playlist, pre-cache upcoming songs at their nearest edge
4. **Geographic patterns:** Songs popular in specific regions (K-pop in Korea, Reggaeton in Latin America) are prioritized at regional caches

#### Cache Headers:
For audio chunks, we set long cache times since content never changes:
The `immutable` directive tells browsers and CDNs that the content will never change, eliminating conditional requests.

## 6.2 Search and Discovery
Search is how users find music. They type a few letters and expect to see relevant results instantly, even if they misspell the artist name or only remember part of the song title. Search must be fast (under 100ms), forgiving of errors, and smart about ranking.

### Search Index Architecture
We do not query the primary database for search. Instead, we maintain a dedicated search index using Elasticsearch (or OpenSearch). This separation allows us to optimize each system for its specific workload.

#### What Gets Indexed:
| Field | Source | Notes |
| --- | --- | --- |
| Song titles | Song metadata | Primary search target |
| Artist names | Artist table | Includes aliases and collaborations |
| Album names | Album table | Including compilation names |
| Lyrics | Lyrics service | For "search by lyric" feature |
| Genres and moods | Tagging system | "upbeat pop", "chill electronic" |

#### Index Structure:
Elasticsearch uses inverted indexes, mapping terms to the documents containing them:
When a user searches "bohemian rhapsody", Elasticsearch finds documents matching both terms and ranks them by relevance.

### Handling Typos and Fuzzy Matching
Users frequently misspell artist and song names. "Ariana Grandi", "Tylor Swift", "bohemain rapsody" should all return correct results.
Elasticsearch provides several mechanisms:
1. **Fuzzy queries:** Allow for character edits (insertions, deletions, substitutions). "bohemain" with edit distance 1 matches "bohemian".
2. **Phonetic matching:** "Cue" sounds like "Queue". Phonetic analyzers (Soundex, Metaphone) index words by how they sound.
3. **N-gram tokenization:** Index partial words for autocomplete. "bohe" matches "bohemian" because we index ["b", "bo", "boh", "bohe", "bohem", ...].

### Search Ranking
Raw text matching is not enough. When searching "queen", users probably want the legendary rock band, not every song with "queen" in the title. We rank results using multiple signals:
| Signal | Weight | Description |
| --- | --- | --- |
| Text relevance | High | Exact matches rank higher than partial matches |
| Popularity | High | Monthly listeners, total streams, trending velocity |
| Personalization | Medium | Boost artists the user has listened to before |
| Recency | Low | New releases get a small boost |

The weights are tuned based on user behavior data. If users consistently click the 3rd result, something is wrong with the ranking.

### Autocomplete
As users type, we show suggestions in real-time. This requires extremely low latency (under 50ms) because users are actively typing and waiting.

#### Implementation:
1. Index names with edge n-grams: "taylor" becomes ["t", "ta", "tay", "tayl", "taylo", "taylor"]
2. Use Elasticsearch's completion suggester, optimized for prefix matching
3. Return top 5-10 suggestions sorted by popularity
4. Client-side debouncing (100ms) prevents excessive requests while typing

## 6.3 Personalization and Recommendations
Personalization is what makes Spotify addictive. When you open the app and "Discover Weekly" has exactly the kind of music you love but have never heard, it feels like magic. That magic is the result of sophisticated recommendation systems running at massive scale.

### Understanding User Taste
The recommendation system learns user preferences from multiple signals, each providing different information:
| Signal | Type | Strength | Notes |
| --- | --- | --- | --- |
| Liked songs | Explicit | Very strong | User clicked heart, clear preference |
| Added to playlist | Explicit | Strong | Deliberate curation |
| Listening history | Implicit | Medium | What they play repeatedly |
| Skip behavior | Implicit | Medium | Skipping within 30 seconds indicates dislike |
| Listen duration | Implicit | Weak | Full song = engagement, partial = maybe skip |
| Time of day | Context | Weak | Morning playlists differ from night |

### Recommendation Approaches
There are several approaches to generating recommendations, each with trade-offs:

#### Approach 1: Collaborative Filtering
The core idea: users with similar taste like similar songs. If you and I both love the same 50 songs, and you love a song I have not heard, I will probably like it too.
**How it works:**
1. Build a sparse matrix of user-song interactions (plays, likes, skips)
2. Use matrix factorization (ALS, SVD) to find latent factors
3. Each user and song becomes a vector in latent space
4. Predict preference as the dot product of user and song vectors

**Pros:**
- Discovers unexpected recommendations ("users like you also like...")
- No need for content analysis

**Cons:**
- Cold start problem: new users and new songs have no interaction data
- Computationally expensive: the matrix has billions of entries

#### Approach 2: Content-Based Filtering
The idea: recommend songs similar to what the user already likes, based on the songs' characteristics.
**How it works:**
1. Extract audio features from songs: tempo (BPM), energy, acousticness, danceability, valence (happiness)
2. Convert each song into an embedding (vector representation)
3. Find songs with similar embeddings to what the user likes

**Pros:**
- Works for new songs (they have audio features even without play data)
- Explainable: "we recommend this because it has similar energy to songs you like"

**Cons:**
- Can create filter bubbles (only recommends similar-sounding music)
- Requires audio analysis infrastructure

#### Approach 3: Hybrid (What Spotify Actually Uses)
Real systems combine multiple approaches:
The ensemble layer learns how to weight each model's predictions. For new users, content-based gets more weight. For users with rich history, collaborative filtering dominates.

### Batch vs Real-Time Recommendations
Different recommendation features have different latency requirements:
| Feature | Compute Time | Refresh Rate | Infrastructure |
| --- | --- | --- | --- |
| Discover Weekly | Hours | Weekly | Spark batch jobs |
| Daily Mix | Hours | Daily | Spark batch jobs |
| "Because you listened to..." | <100ms | Per request | Model serving + feature store |
| Radio (similar to current song) | <100ms | Per request | Nearest neighbor search |

**Batch recommendations** (Discover Weekly) run offline using full model training. They are pre-computed for every user and stored in Redis for instant serving.
**Real-time recommendations** use pre-trained models with real-time features. When you finish a song, we query the model with your current session context to suggest the next song.

### Recommendation System Architecture
1. **Event collection:** Every play, skip, and like flows through Kafka
2. **Stream processing:** Real-time features are computed (current session, recent plays)
3. **Batch processing:** Heavy model training runs on Spark, retraining weekly
4. **Feature store:** Central repository for all user and song features
5. **Model serving:** Trained models are deployed for real-time inference
6. **Caching:** Pre-computed recommendations (Discover Weekly) are stored in Redis

## 6.4 Handling Scale and High Availability
With 200 million daily active users and 1 billion streams per day, the system must be designed for extreme scale. Equally important, it must stay up. Users expect music to be available 24/7, and outages are highly visible on social media.

### Horizontal Scaling
The key to horizontal scaling is keeping services stateless. When a service stores no state locally, you can add or remove instances without coordination.
**All our application services are stateless:**
- Playback Service: stateless, any instance can handle any request
- Search Service: stateless, queries Elasticsearch
- Playlist Service: stateless, reads/writes to Cassandra
- Recommendation Service: stateless, fetches from cache or feature store

#### Auto-scaling with Kubernetes:
We use Horizontal Pod Autoscaler (HPA) to automatically add capacity:
| Metric | Target | Action |
| --- | --- | --- |
| CPU utilization | 70% | Add pods when exceeded |
| Request latency (p99) | 100ms | Add pods if latency spikes |
| Request queue depth | 100 | Add pods if queue builds up |

During peak hours (evening commute, weekends), the system automatically scales up. During low-traffic periods (3 AM), it scales down to save costs.

### Database Scaling
Different databases scale differently:

#### Cassandra (Playlists, Listening History):
Cassandra scales horizontally by adding nodes. Data is automatically rebalanced across the cluster using consistent hashing.
Each user's data lives on a subset of nodes (replication factor = 3). Reads and writes for a user hit the same nodes, making operations efficient.

#### PostgreSQL (Song Metadata):
For the song catalog, we use read replicas rather than sharding:
- One primary handles writes (song additions, metadata updates)
- Multiple read replicas handle read traffic
- Writes are infrequent (new songs added daily, not per-second)
- 100 million songs fits comfortably in a well-indexed PostgreSQL instance

#### Elasticsearch (Search):
Elasticsearch scales by adding nodes to the cluster. Indexes are automatically sharded across nodes.

### Multi-Layer Caching
Caching is essential at every layer to handle our traffic:
| Layer | What's Cached | TTL | Hit Rate |
| --- | --- | --- | --- |
| Client | Recently played, user preferences | 1 hour | Very high |
| CDN | Audio files, album art, static assets | 24+ hours | 80-90% |
| Redis | Song metadata, recommendations, sessions | 5-15 min | 90%+ |
| Database | Query results in buffer pool | Automatic | 95%+ |

With these cache layers, only a tiny fraction of requests reach the primary databases.

### High Availability

#### Multi-Region Deployment:
We deploy in multiple geographic regions with active-active configuration:
- Users are routed to the nearest region via DNS-based load balancing
- Each region can handle its traffic independently
- If one region fails, traffic is automatically routed to remaining regions
- Data is replicated across regions (eventually consistent for playlists, synchronous for critical user data)

#### Graceful Degradation:
When components fail, the system should degrade gracefully rather than crash entirely:
| Component | If It Fails | Fallback |
| --- | --- | --- |
| Recommendation Service | Home page shows generic playlists | Serve cached "top hits" |
| Search Service | Search is temporarily unavailable | Show recently played |
| Playlist Service | Cannot modify playlists | Read from cache (read-only mode) |
| CDN | Slower audio delivery | Fall back to origin |

The most important invariant: **playback should always work**. Users can tolerate degraded recommendations, but not being able to play music is a critical failure.

### Rate Limiting
Protection against abuse and accidental overload:
| Endpoint | Limit | Notes |
| --- | --- | --- |
| Stream requests | 100/min per user | Prevents bot abuse |
| Search requests | 30/min per user | Prevents scraping |
| Playlist writes | 60/min per user | Prevents spam |
| API (unauthenticated) | 10/min per IP | Prevents anonymous abuse |

Rate limits are enforced at the API Gateway using Redis-backed counters with sliding window algorithm.

## 6.5 Offline Playback
Premium users can download songs for offline listening. This is essential for users on flights, subways, or in areas with poor connectivity. But it introduces unique challenges: we are giving users permanent copies of copyrighted content that we need to protect and eventually revoke.

### Download Architecture
The download flow is similar to streaming, but the client stores the content locally instead of playing it immediately:

### The Download Flow in Detail
1. **User initiates download:** User marks a playlist for offline access
2. **Entitlement check:** Download Service verifies:
3. **License generation:** For each song, we generate an encrypted license tied to:
4. **Download:** Client downloads encrypted audio files from CDN
5. **Local storage:** Audio and licenses are stored in encrypted local storage

### DRM and Content Protection
Downloaded files must be protected from piracy. If users could extract and share downloaded MP3s, the entire licensing model would collapse.

#### Encryption:
Audio files are encrypted using industry-standard DRM systems:
- **Widevine** (Android, Chrome)
- **FairPlay** (iOS, Safari)
- **PlayReady** (Windows)

The decryption keys are stored in secure hardware (when available) and never exposed to the application layer.

#### License Expiration:
Downloaded content does not last forever. Licenses expire after 30 days of offline use. When the device comes online, it must check with the License Server to renew. If the user's subscription has lapsed, renewal fails and downloaded content becomes unplayable.

#### Device Management:
| Limit | Value | Reason |
| --- | --- | --- |
| Max devices per account | 5 | Prevent account sharing abuse |
| Max downloads per device | 10,000 songs | Storage sanity |
| Offline validity | 30 days | Periodic subscription verification |

### Storage Management on Device
The client is responsible for managing downloaded content:
- **Quality selection:** Users choose download quality (affects storage)
- **Storage tracking:** Show users how much storage is used
- **Smart cleanup:** Automatically remove songs that have not been played offline in 60+ days, oldest downloads first when storage is low

## 6.6 Royalty Calculation and Playback Tracking
Every stream must be tracked accurately for royalty payments to artists and labels. This is not just a feature; it's a legal and financial requirement. Billions of dollars flow from Spotify to rights holders based on stream counts.

### What Counts as a Stream?
Not every play counts as a stream for royalty purposes:
| Condition | Counts as Stream? | Why |
| --- | --- | --- |
| Played 30+ seconds | Yes | Industry standard threshold |
| Played < 30 seconds | No | Prevents gaming with short plays |
| Automated/bot playback | No | Detected and filtered |
| User actively listening | Yes | Normal usage |
| Background audio with no engagement | Maybe | Complex rules apply |

The 30-second threshold is an industry standard. Playing 29 seconds and skipping does not count. Playing 30 seconds and then skipping does count.

### Playback Event Pipeline
We need to capture every play event, process it at scale, and aggregate for royalty calculation:

### Event Flow in Detail
1. **Client emits events:** The app sends events for key playback moments:
2. **Event collection:** Events are batched and sent to our Event Collector API. We use batching to reduce network overhead and handle intermittent connectivity.
3. **Kafka for durability:** Events flow into Kafka, providing durability and buffering. If downstream systems are slow, Kafka absorbs the backlog without losing data.
4. **Stream processing:** A Flink or Spark Streaming job processes events in near-real-time:
5. **Fraud detection:** ML models flag suspicious patterns before counting streams
6. **Analytics and royalties:** Valid streams are written to analytics databases and fed into the royalty calculation pipeline

### Fraud Detection
Stream manipulation is a real problem. Bad actors try to inflate stream counts to earn royalties fraudulently. We detect and filter these:

#### Detection signals:
| Signal | Description | Indicates |
| --- | --- | --- |
| Loop behavior | Same song played 100+ times | Bot or manipulation |
| Geographic impossibility | User in Tokyo, then NYC 5 minutes later | Account compromise |
| Device fingerprint | Virtual machine, emulator, automation | Bot farm |
| No diversity | Only plays one artist, no browsing | Targeted manipulation |
| Payment anomalies | Many streams but subscription always fails | Stolen credentials |

Detected fraud is flagged, excluded from royalty calculations, and investigated. Repeat offenders have accounts suspended.

### Royalty Calculation
Stream data feeds into the royalty system that determines artist payments. The calculation is complex and varies by contract, but the basic model is:
1. **Pool model:** Total subscription revenue forms a pool
2. **Stream share:** Each artist's streams as a percentage of total streams
3. **Payment:** Artist receives their percentage of the revenue pool

This happens monthly, processing billions of stream records to determine millions of payments.
# References
- [Spotify Engineering Blog](https://engineering.atspotify.com/) - Insights into Spotify's engineering decisions and architecture
- [How Spotify Uses ML for Personalization](https://engineering.atspotify.com/2021/12/how-spotify-uses-ml-to-create-the-future-of-personalization/) - Deep dive into Spotify's recommendation systems
- [HTTP Live Streaming Documentation](https://developer.apple.com/documentation/http-live-streaming) - Apple's official HLS specification
- [Cassandra Data Modeling Guide](https://cassandra.apache.org/doc/latest/cassandra/developing/data-modeling/index.html) - Best practices for designing Cassandra schemas
- [Elasticsearch Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html) - Search infrastructure fundamentals

# Quiz

## Design Spotify Quiz
To meet a “play starts within ~200ms” goal globally, which approach is most directly effective for delivering audio bytes quickly?