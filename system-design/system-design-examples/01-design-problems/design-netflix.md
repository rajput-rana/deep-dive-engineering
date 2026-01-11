# Design Netflix

#### 
Netflix is a video streaming platform that allows users to watch movies, TV shows, and documentaries on demand. Users can browse a vast content library, stream videos in real-time, and receive personalized recommendations based on their viewing history.
The platform handles millions of concurrent users streaming video content simultaneously, making it one of the most demanding distributed systems in production today. Netflix must deliver high-quality video with minimal buffering while adapting to varying network conditions and device capabilities.
**Popular Examples:** Netflix, Amazon Prime Video, Disney+, Hulu, HBO Max
What makes Netflix particularly interesting from a system design perspective is the combination of challenges it must solve simultaneously. Unlike a text-based service where a request returns kilobytes of data, a single Netflix stream delivers gigabytes of video content over hours.
The system must handle massive bandwidth requirements, adapt video quality in real-time based on network conditions, protect premium content with digital rights management, and somehow make the experience feel instantaneous to the user.
This problem touches on many fundamental concepts: **video encoding** and **adaptive bitrate streaming**, **content delivery networks**, **recommendation systems**, and handling **massive scale**.
In this chapter, we will explore the **high-level design of Netflix**.
Lets start by clarifying the requirements:
# 1. Clarifying Requirements
Before sketching architecture diagrams, we need to understand what we are actually building. 
Here is how a requirements discussion might unfold in an interview:
**Candidate:** "What is the expected scale? How many users and concurrent streams should we support?"
**Interviewer:** "Let's design for 200 million registered users with 10 million concurrent streams at peak."
**Candidate:** "Should we focus on live streaming or video-on-demand (VOD)?"
**Interviewer:** "Focus on video-on-demand. Live streaming is out of scope."
**Candidate:** "What video quality levels should we support?"
**Interviewer:** "Support multiple resolutions from 480p to 4K, with adaptive bitrate streaming."
**Candidate:** "Should we design the recommendation system as well? That is a big part of the Netflix experience."
**Interviewer:** "Yes, include a high-level design for personalized recommendations. You do not need to go deep into ML algorithms."
**Candidate:** "Should we handle content upload and transcoding?"
**Interviewer:** "Yes, but focus more on the streaming side. Content upload is done by content partners, not end users."
**Candidate:** "What about offline downloads?"
**Interviewer:** "Good to mention, but not the primary focus. Prioritize online streaming."
After gathering the details, we can summarize the key system requirements.

## 1.1 Functional Requirements
- **Content Ingestion:** Content partners can upload raw video files.
- **Content Catalog:** Users can browse and search the content library.
- **Video Streaming:** Users can stream videos with adaptive quality based on network conditions.
- **Personalized Recommendations:** The system recommends content based on user preferences and viewing history.
- **User Profiles:** A single account can have multiple profiles, each with its own viewing history, preferences, and recommendations.
- **Watch Progress:** The system tracks where users left off in each video, enabling seamless resume across devices.

## 1.2 Non-Functional Requirements
- **High Availability:** The system must be highly available (99.99% uptime).
- **Low Latency:** Video playback should start within 2-3 seconds.
- **Scalability:** Support 10 million concurrent streams globally.
- **Adaptive Quality:** Seamlessly adjust video quality based on network bandwidth.
- **Global Reach:** Low latency streaming for users worldwide.

# 2. Back-of-the-Envelope Estimation
Before diving into architecture, let's run some calculations to understand the scale we are dealing with. These numbers will guide our decisions around storage, bandwidth, and infrastructure.

### 2.1 Users and Traffic
Starting with the numbers from our requirements:
**User Base**
- Registered users: 200 million
- Daily active users: 100 million (50% of registered users)
- Peak concurrent streams: 10 million

**Viewing Patterns**
- Average watch time per session: 1 hour
- Average sessions per day: 150 million (some users watch multiple times)

These numbers tell us something important: at any given moment during peak hours, about 10% of daily active users are simultaneously streaming video. That is a lot of concurrent connections to maintain.

### 2.2 Content Library
Let's estimate storage requirements for the video library:
**Content Volume**
- Total titles: 15,000 (movies and TV show episodes)
- Average video duration: 45 minutes
- Total content hours: 15,000 × 0.75 hours = 11,250 hours

**Storage Per Title**
Here is where it gets interesting. A single movie is not stored once, it is stored many times in different formats:
| Quality | Bitrate | Storage for 45 min |
| --- | --- | --- |
| 480p | 1 Mbps | ~340 MB |
| 720p | 3 Mbps | ~1 GB |
| 1080p | 5 Mbps | ~1.7 GB |
| 4K | 15 Mbps | ~5 GB |

But we also need multiple codec formats (H.264 for compatibility, H.265 for efficiency, VP9 for web), multiple audio tracks (different languages, Dolby Atmos), and subtitle files. When you add it all up:
That is 750 terabytes just for video content, not counting metadata, user data, or logs. And this content needs to be replicated across CDN edge locations worldwide.

### 2.3 Bandwidth Estimation
This is where Netflix scale becomes mind-boggling:
**Per-Stream Bandwidth**
- Average streaming bitrate: 5 Mbps (HD quality)
- 4K streams: 15-25 Mbps

**Peak Aggregate Bandwidth**
To put that in perspective, 50 Pbps is more bandwidth than most countries' entire internet infrastructure. This is why Netflix built its own CDN, no third-party provider could handle this economically.
Of course, this traffic is distributed across thousands of CDN edge servers worldwide. Each edge server handles a fraction of the total load, serving users in its geographic region.

### 2.4 Metadata and API Traffic
While video bandwidth dominates, we also have significant API traffic:
**Browsing and Discovery**
- Home page loads per day: ~150 million
- Search queries per day: ~50 million
- Metadata API calls: ~500,000 QPS at peak

**Watch Progress Updates**
- Progress updates: Every 30 seconds per active stream
- At 10 million concurrent streams: ~330,000 updates per second

This API traffic is handled by our backend services, separate from video delivery. The key insight is that metadata requests are small (kilobytes) but frequent, while video requests are massive (gigabytes) but handled by CDN.

### 2.5 Key Insights
These estimates reveal several important design implications:
1. **Video bandwidth dwarfs everything else.** API traffic is a rounding error compared to video delivery. We need a specialized content delivery strategy.
2. **Storage is substantial but manageable.** 750 TB is large but not extreme. The challenge is replicating this content to edge locations worldwide.
3. **Transcoding is computationally expensive.** Converting raw uploads into dozens of format/quality combinations requires significant compute resources.
4. **CDN is not optional.** Serving 50 Pbps from origin servers is physically impossible. We must cache content at the edge.

# 3. Core APIs
With requirements and scale understood, let's define the API contract. Netflix's API covers three main areas: content discovery, playback control, and user interactions.
We will design a RESTful API with endpoints for each major operation. Let's walk through the most important ones.

### 1. Get Content Catalog

#### Endpoint: GET /catalog
This is the most frequently called endpoint. Every time a user opens the app or scrolls the home page, this endpoint assembles personalized content rows.
**Request Parameters:**
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| user_id | string | Yes | The user's account identifier |
| profile_id | string | Yes | The specific profile within the account |
| page_token | string | No | Pagination token for infinite scroll |
| device_type | string | No | Device info for format selection (tv, mobile, web) |

**Example Response:**
The response is personalized for each profile. The recommendation service determines which rows to show and in what order. Notice how "Continue Watching" includes progress information so the UI can show a progress bar.
**Error Responses:**
| Status | Meaning |
| --- | --- |
| 401 Unauthorized | Invalid or missing authentication token |
| 404 Not Found | Profile does not exist |
| 429 Too Many Requests | Rate limit exceeded |

### 2. Get Video Playback URL

#### Endpoint: GET /playback/{content_id}
This is the critical path for video streaming. When a user presses play, this endpoint returns everything the client needs to start streaming.
**Request Parameters:**
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| content_id | path | Yes | The unique identifier for the content |
| profile_id | query | Yes | The profile requesting playback |
| device_type | query | No | Device capabilities for format selection |
| preferred_audio | query | No | Preferred audio language |

**Example Response:**
The response includes the streaming manifest URL, a list of CDN edge servers ranked by proximity, DRM license information, and the position to resume from. The client uses this to initialize the video player.
**Error Responses:**
| Status | Meaning |
| --- | --- |
| 403 Forbidden | Content not available in user's region, or subscription does not include this content |
| 429 Too Many Requests | Concurrent stream limit exceeded for subscription tier |

The 429 error for concurrent streams is particularly important. If a user's subscription allows 2 simultaneous streams and they try to start a third, we return this error with a helpful message.

### 3.3 Update Watch Progress

#### Endpoint: POST /progress
Clients call this endpoint periodically (every 30-60 seconds) to save the user's position in the video. This enables the "Continue Watching" feature.
**Request Body:**
**Response:** `200 OK` with empty body on success.
This is a fire-and-forget operation. The client does not wait for confirmation before continuing playback. We use the session_id to deduplicate updates and handle out-of-order delivery.

### 3.4 Search Content

#### Endpoint: GET /search
Full-text search across the content catalog with personalized ranking.
**Request Parameters:**
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| query | string | Yes | The search term |
| profile_id | string | Yes | For personalized result ranking |
| limit | integer | No | Maximum results (default 20) |

**Example Response:**
Search matches against title, description, cast, director, and genre. Results are ranked by relevance and personalized based on the user's viewing history.
# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complex diagram upfront, we will build the design incrementally, starting with the simplest components and adding complexity as we address each requirement. This mirrors how you would approach the problem in an interview.
Our system needs to handle three core operations:
1. **Content Ingestion:** Process raw video uploads into streaming-ready formats
2. **Content Discovery:** Help users find content through browsing, search, and recommendations
3. **Video Streaming:** Deliver video content globally with adaptive quality

The key insight that shapes our entire architecture is this: video streaming is fundamentally different from typical web requests. A normal API call might transfer a few kilobytes. A video stream transfers gigabytes over hours. 
This asymmetry means we need specialized infrastructure for video delivery that operates differently from our application services.
Notice how the video streaming path (bottom) bypasses our application servers entirely. Users fetch video directly from CDN edge servers. This is critical: if 10 million concurrent streams had to route through our application layer, we would need impossibly large server farms.
Let's build each part of this architecture step by step.


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
        S1[scale Service]
        S2[upload Service]
        S3[smaller Service]
        S4[Transcoding Service]
        S5[based Service]
    end

    subgraph Data Storage
        DBElasticsearch[Elasticsearch]
        DBCassandra[Cassandra]
        DBPostgreSQL[PostgreSQL]
    end

    subgraph Caching Layer
        CacheRedis[Redis]
    end

    subgraph Message Queue
        QueueSQS[SQS]
        QueueKafka[Kafka]
    end

    subgraph Object Storage
        Storageobjectstorage[object storage]
    end

    subgraph CDN
        CDN[Content Delivery Network]
    end

    Web --> LB
    Mobile --> LB
    LB --> S1
    LB --> S2
    LB --> S3
    LB --> S4
    LB --> S5
    S1 --> DBElasticsearch
    S1 --> DBCassandra
    S1 --> CacheRedis
    S1 --> QueueSQS
    S1 --> QueueKafka
    S2 --> DBElasticsearch
    S2 --> DBCassandra
    S2 --> CacheRedis
    S2 --> QueueSQS
    S2 --> QueueKafka
    S3 --> DBElasticsearch
    S3 --> DBCassandra
    S3 --> CacheRedis
    S3 --> QueueSQS
    S3 --> QueueKafka
    S4 --> DBElasticsearch
    S4 --> DBCassandra
    S4 --> CacheRedis
    S4 --> QueueSQS
    S4 --> QueueKafka
    S5 --> DBElasticsearch
    S5 --> DBCassandra
    S5 --> CacheRedis
    S5 --> QueueSQS
    S5 --> QueueKafka
    S1 --> Storageobjectstorage
    Storageobjectstorage --> CDN
    CDN --> Web
    CDN --> Mobile
```




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
        S1[Stateless Service]
        S2[DRM Service]
        S3[appropriate Service]
        S4[application Service]
        S5[Application Service]
    end

    subgraph Data Storage
        DBCassandra[Cassandra]
        DBPostgreSQL[PostgreSQL]
        DBElasticsearch[Elasticsearch]
    end

    subgraph Caching Layer
        CacheRedis[Redis]
    end

    subgraph Message Queue
        QueueSQS[SQS]
        QueueKafka[Kafka]
    end

    subgraph Object Storage
        StorageObjectStorage[Object Storage]
        StorageS3[S3]
        Storageobjectstorage[object storage]
    end

    subgraph CDN
        CDN[Content Delivery Network]
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
    S1 --> QueueSQS
    S1 --> QueueKafka
    S2 --> DBCassandra
    S2 --> DBPostgreSQL
    S2 --> CacheRedis
    S2 --> QueueSQS
    S2 --> QueueKafka
    S3 --> DBCassandra
    S3 --> DBPostgreSQL
    S3 --> CacheRedis
    S3 --> QueueSQS
    S3 --> QueueKafka
    S4 --> DBCassandra
    S4 --> DBPostgreSQL
    S4 --> CacheRedis
    S4 --> QueueSQS
    S4 --> QueueKafka
    S5 --> DBCassandra
    S5 --> DBPostgreSQL
    S5 --> CacheRedis
    S5 --> QueueSQS
    S5 --> QueueKafka
    S1 --> StorageObjectStorage
    S1 --> StorageS3
    S1 --> Storageobjectstorage
    StorageObjectStorage --> CDN
    StorageS3 --> CDN
    Storageobjectstorage --> CDN
    CDN --> Web
    CDN --> Mobile
```




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
        S1[stateless Service]
        S2[Search Service]
        S3[DRM Service]
        S4[recommendation Service]
        S5[Upload Service]
    end

    subgraph Data Storage
        DBCassandra[Cassandra]
        DBElasticsearch[Elasticsearch]
        DBPostgreSQL[PostgreSQL]
    end

    subgraph Caching Layer
        CacheRedis[Redis]
    end

    subgraph Message Queue
        QueueSQS[SQS]
        QueueKafka[Kafka]
    end

    subgraph Object Storage
        Storageobjectstorage[object storage]
        StorageObjectStorage[Object Storage]
        StorageS3[S3]
    end

    subgraph CDN
        CDN[Content Delivery Network]
    end

    Web --> LB
    Mobile --> LB
    LB --> S1
    LB --> S2
    LB --> S3
    LB --> S4
    LB --> S5
    S1 --> DBCassandra
    S1 --> DBElasticsearch
    S1 --> CacheRedis
    S1 --> QueueSQS
    S1 --> QueueKafka
    S2 --> DBCassandra
    S2 --> DBElasticsearch
    S2 --> CacheRedis
    S2 --> QueueSQS
    S2 --> QueueKafka
    S3 --> DBCassandra
    S3 --> DBElasticsearch
    S3 --> CacheRedis
    S3 --> QueueSQS
    S3 --> QueueKafka
    S4 --> DBCassandra
    S4 --> DBElasticsearch
    S4 --> CacheRedis
    S4 --> QueueSQS
    S4 --> QueueKafka
    S5 --> DBCassandra
    S5 --> DBElasticsearch
    S5 --> CacheRedis
    S5 --> QueueSQS
    S5 --> QueueKafka
    S1 --> Storageobjectstorage
    S1 --> StorageObjectStorage
    S1 --> StorageS3
    Storageobjectstorage --> CDN
    StorageObjectStorage --> CDN
    StorageS3 --> CDN
    CDN --> Web
    CDN --> Mobile
```



## 4.1 Requirement 1: Content Ingestion
Before users can watch anything, content must be uploaded, processed, and distributed. This is a write-heavy, batch-oriented workload that happens asynchronously, long before any user presses play.
The challenge here is that raw video files are enormous and unwieldy. A movie might arrive as a 100 GB master file in ProRes format. We need to convert this into dozens of variants: multiple resolutions (480p through 4K), multiple codecs (H.264, H.265, VP9), multiple audio tracks, and subtitles. 
The output might be 50 GB of encoded content per title.

### Components for Content Ingestion

#### Upload Service
Content partners interact with this service to submit new content. It handles authentication (verifying the partner has rights to upload), receives large file uploads (often using multipart uploads for reliability), and stores the raw file in temporary object storage.
The upload service is not particularly complex, but it needs to handle large files reliably. A 100 GB upload over a flaky connection should be resumable, not require starting over.

#### Job Queue
After upload completes, the service enqueues a transcoding job. We use a message queue (like SQS or Kafka) to decouple upload from processing. This way, the upload service can respond immediately while transcoding happens asynchronously.
The queue also provides natural load leveling. If many partners upload simultaneously, jobs queue up rather than overwhelming the transcoding workers.

#### Transcoding Workers
This is where the heavy computation happens. Transcoding workers are a fleet of machines (often GPU-accelerated) that convert raw video into streaming formats.
The interesting optimization here is parallelization. Rather than processing a movie sequentially, we split it into segments and encode them in parallel across many workers. A 2-hour movie split into 4-second segments gives us 1,800 segments. With enough workers, we can encode all quality variants in parallel, reducing total processing time from hours to minutes.

#### Quality Assurance
Before content goes live, automated checks verify the output:
- Audio/video sync is correct
- All quality levels are present
- Quality metrics (VMAF score) meet thresholds
- Subtitles are properly aligned

This catches encoding errors before they reach users.

### The Ingestion Flow in Action
Let's trace through what happens when a movie studio uploads new content:
1. **Upload:** The partner uploads the raw video file. This might take hours for large files, using resumable uploads to handle network issues.
2. **Job creation:** Once the upload completes, a transcoding job is created and added to the queue. The upload service returns success to the partner, the rest happens asynchronously.
3. **Parallel encoding:** Transcoding workers pick up the job, split the video into segments, and encode all variants in parallel. Each segment gets encoded at multiple bitrates (480p through 4K) and in multiple codecs.
4. **Quality checks:** Automated systems verify the output quality, check audio sync, and ensure all expected variants exist.
5. **Distribution:** Encoded content is stored in our origin servers and begins replicating to CDN edge locations worldwide. Popular content gets proactively pushed to more locations.
6. **Metadata update:** The content database is updated to mark the title as available. Now it can appear in the catalog and be played by users.

## 4.2 Requirement 2: Content Discovery
Users need to find content they want to watch. This happens through browsing the home page, searching, and receiving personalized recommendations. Unlike video streaming, this is traditional request-response traffic handled by our application services.

### Components for Content Discovery

#### API Gateway
Every request enters through the API Gateway, which handles authentication (validating JWT tokens), rate limiting (preventing abuse), and routing (directing requests to the appropriate service).
The gateway is the front door to our system. It terminates SSL, validates that requests are well-formed, and protects backend services from malicious traffic.

#### Catalog Service
Manages all content metadata: titles, descriptions, cast, genres, availability by region, and thumbnail URLs. When users browse the home page, the catalog service assembles the rows of content to display.
This service is read-heavy with relatively static data. Content metadata changes infrequently (maybe a new title is added daily), so aggressive caching works well.

#### Search Service
Provides full-text search over the content catalog. Users search by title, actor name, director, or genre. The service uses Elasticsearch for fast, relevant search results.
Search needs to handle typos, partial matches, and synonyms. A search for "Dicaprio" should find "DiCaprio" movies. This requires sophisticated text analysis and ranking.

#### Recommendation Service
The secret sauce of Netflix. This service generates personalized content rows for each user based on their viewing history, ratings, and behavior. It is the difference between a generic catalog and a personalized experience that feels like Netflix knows what you want.
We will explore the recommendation system in more detail in the deep dive section.

#### User Service
Manages user accounts, profiles, subscription status, and preferences. Each account can have multiple profiles (for family members), each with independent viewing history and recommendations.

### The Discovery Flow in Action
When a user opens the Netflix app:
1. **Authentication:** The API gateway validates the user's auth token and extracts their user/profile ID.
2. **Parallel fetching:** To minimize latency, the catalog service makes parallel calls to fetch content metadata and personalized recommendations.
3. **Recommendation generation:** The recommendation service queries viewing history and applies ML models to generate personalized content rows: "Because you watched X", "Trending in your area", etc.
4. **Assembly:** The catalog service combines recommendations with content metadata (thumbnails, titles, descriptions) into a response.
5. **Caching:** Heavily accessed metadata is cached in Redis to reduce database load.

The result is a personalized home page assembled in under 200ms.

## 4.3 Requirement 3: Video Streaming
This is the most critical and challenging requirement. When a user presses play, video must start within seconds and continue smoothly regardless of network conditions.
The fundamental challenge is scale. With 10 million concurrent streams at 5 Mbps each, we need to deliver 50 Petabits per second. No centralized infrastructure can handle this. 
The solution is a **Content Delivery Network (CDN)** that distributes content to edge servers worldwide, serving users from nearby locations.

### Components for Video Streaming

#### Playback Service
When a user presses play, this service handles the authorization and orchestration:
- Verify the user's subscription includes this content
- Check regional availability (some content is geo-restricted)
- Enforce concurrent stream limits (1, 2, or 4 streams based on subscription tier)
- Select optimal CDN edge servers based on user location
- Return the streaming manifest URL and CDN endpoints

The playback service does not touch video content at all. It just orchestrates access.

#### DRM Service
Premium content must be protected from piracy. The DRM (Digital Rights Management) service issues licenses that allow the client to decrypt video content.
When playback starts, the client requests a license from the DRM service. The service validates the user's entitlement and returns an encrypted license key. The video player uses this key to decrypt video segments as they are downloaded.
Different devices use different DRM systems: Widevine for Android and Chrome, FairPlay for iOS and Safari, PlayReady for Windows. We need to support all of them.

#### CDN Edge Servers
The workhorses of video delivery. These servers are deployed in data centers and ISP facilities worldwide, caching video content close to users.
When a user in Tokyo requests a video segment, it is served from a Tokyo edge server rather than traveling across the Pacific to our US data center. This reduces latency from hundreds of milliseconds to under 50ms.
Edge servers cache popular content proactively. When a new season of a hit show drops, we push it to edge locations before users request it.

#### Origin Storage
The source of truth for all encoded video content. When an edge server does not have a segment cached (a "cache miss"), it fetches from origin.
Origin storage is replicated across multiple regions for durability and availability. If one region goes down, edge servers can fetch from another.

### The Streaming Flow in Action
Let's trace through what happens when a user presses play:
1. **Authorization:** The client calls the playback service, which verifies the user can watch this content: valid subscription, content available in their region, not exceeding concurrent stream limit.
2. **Manifest delivery:** The service returns a manifest URL and a list of CDN servers ranked by proximity. The client fetches the manifest, which describes all available quality levels and segment URLs.
3. **DRM license:** The client requests a decryption license from the DRM service. This happens once per playback session.
4. **Segment fetching:** The client begins fetching video segments. It starts with a conservative quality level to ensure quick startup, then adjusts based on measured bandwidth.
5. **Adaptive streaming:** Throughout playback, the client monitors download speed and buffer level. If bandwidth drops, it switches to lower quality to avoid buffering. If bandwidth increases, it upgrades quality for a better picture.
6. **CDN caching:** Most segments are served from CDN cache. Only cache misses require fetching from origin, and the fetched content is cached for future requests.

The result is video that starts quickly and adapts seamlessly to network conditions.

## 4.4 Putting It All Together
Now that we have designed all three major components, let's see the complete architecture:

### Architecture Principles
Several key principles emerge from this design:
**Separation of concerns.** Metadata traffic (browsing, search, recommendations) flows through application services. Video traffic flows through CDN. These are completely separate data paths with different scaling characteristics.
**Edge-heavy design.** Video content is served from the edge, close to users. Only API calls and cache misses reach our data centers. This is the only way to achieve global scale.
**Stateless services.** Application services are stateless and horizontally scalable. State lives in the databases and caches, not in the service instances.
**Asynchronous processing.** Heavy operations like transcoding happen asynchronously. User-facing operations remain fast.

### Component Responsibilities
| Component | Primary Responsibility | Scaling Strategy |
| --- | --- | --- |
| API Gateway | Auth, rate limiting, routing | Horizontal (add instances) |
| Catalog Service | Content metadata, home page assembly | Horizontal + caching |
| Playback Service | Stream authorization, CDN selection | Horizontal (stateless) |
| Recommendation Service | Personalized suggestions | Horizontal + precomputation |
| Search Service | Full-text search | Elasticsearch cluster scaling |
| User Service | Profiles, preferences, auth | Horizontal + read replicas |
| Transcoding Service | Video encoding pipeline | Elastic compute (burst when needed) |
| DRM Service | License management | Horizontal |
| CDN Edge Servers | Video segment delivery | Add edge locations |
| Origin Storage | Source of truth for video | Multi-region replication |

This architecture handles our requirements: high availability through redundancy, low latency through edge delivery and caching, and scalability through horizontal scaling of stateless services.
# 5. Database Design
With the high-level architecture in place, let's zoom into the data layer. Choosing the right databases and designing efficient schemas are critical for performance at Netflix scale.

## 5.1 Polyglot Persistence
Netflix's data has diverse characteristics that call for different storage solutions. Rather than forcing everything into one database type, we use the right tool for each job.

#### Why Polyglot Persistence?
Consider viewing history. At 10 million concurrent streams with progress updates every 30 seconds, we are writing 330,000 records per second. A relational database would struggle with this write volume. But Cassandra, designed for high write throughput, handles it easily.
Meanwhile, content metadata needs complex queries (filter by genre, join with cast information, sort by release date). A relational database with proper indexing excels here, while Cassandra's query model would be limiting.
| Data Type | Database | Why This Choice |
| --- | --- | --- |
| User accounts, profiles | PostgreSQL | Transactional consistency, complex queries |
| Content metadata | PostgreSQL | Relational queries, referential integrity |
| Viewing history | Cassandra | High write throughput, time-series data |
| Search index | Elasticsearch | Full-text search, relevance ranking |
| Session data, hot cache | Redis | Sub-millisecond latency, TTL support |

## 5.2 Database Schema
Let's design the schemas for our primary data stores.

#### 1. Users Table (PostgreSQL)
Stores user account information.
| Field | Type | Description |
| --- | --- | --- |
| user_id | UUID (PK) | Unique identifier for the user |
| email | VARCHAR | User's email address |
| password_hash | VARCHAR | Hashed password |
| subscription_tier | ENUM | Basic, Standard, Premium |
| created_at | TIMESTAMP | Account creation time |
| region | VARCHAR | User's region for content availability |

#### 2. Profiles Table (PostgreSQL)
Stores user profiles within an account.
| Field | Type | Description |
| --- | --- | --- |
| profile_id | UUID (PK) | Unique identifier for the profile |
| user_id | UUID (FK) | Reference to user account |
| name | VARCHAR | Profile display name |
| avatar_url | VARCHAR | Profile picture URL |
| is_kids_profile | BOOLEAN | Kids profile flag |
| preferences | JSONB | Viewing preferences |

A single Netflix account can have up to 5 profiles. Each profile maintains independent viewing history and recommendations. The `is_kids_profile` flag triggers content filtering.

#### 3. Content Table (PostgreSQL)
Stores content metadata.
| Field | Type | Description |
| --- | --- | --- |
| content_id | UUID (PK) | Unique identifier for content |
| title | VARCHAR | Content title |
| description | TEXT | Content description |
| type | ENUM | Movie, Series, Episode |
| genre | VARCHAR[] | Array of genres |
| release_year | INTEGER | Year of release |
| duration_seconds | INTEGER | Content duration |
| maturity_rating | VARCHAR | Age rating |
| available_regions | VARCHAR[] | Regions where content is available |

#### 4. Viewing History Table (Cassandra)
For viewing history, we use Cassandra because it handles high write throughput and time-series data well.
| Field | Type | Description |
| --- | --- | --- |
| profile_id | UUID (PK) | Profile identifier |
| content_id | UUID (CK) | Content identifier |
| watched_at | TIMESTAMP (CK) | When the content was watched |
| progress_seconds | INTEGER | Watch progress |
| completed | BOOLEAN | Whether fully watched |

**Partition Key:** `profile_id` 
**Clustering Key:** `watched_at DESC, content_id`
The schema is optimized for the primary query: "Get recent viewing history for a profile, newest first." The clustering key orders by `watched_at DESC` so we can efficiently fetch the most recent entries.
With 10 million concurrent streams updating progress every 30 seconds, we need to handle 330,000 writes per second. Cassandra's architecture, where writes go to a commit log and memtable before being flushed to disk, makes it excellent for write-heavy workloads. The same write volume would overwhelm PostgreSQL.

#### 5. Video Assets Table (PostgreSQL)
Stores information about encoded video files.
| Field | Type | Description |
| --- | --- | --- |
| asset_id | UUID (PK) | Unique identifier for the asset |
| content_id | UUID (FK) | Reference to content |
| resolution | VARCHAR | 480p, 720p, 1080p, 4K |
| codec | VARCHAR | H.264, H.265, VP9 |
| bitrate_kbps | INTEGER | Video bitrate |
| storage_path | VARCHAR | Path in object storage |
| manifest_url | VARCHAR | Streaming manifest URL |

#### 6. Active Sessions (Redis)
We track active streaming sessions in Redis for concurrent stream limit enforcement.
When a user starts streaming, we add their device to this hash. The client sends heartbeats every 30 seconds to update `last_heartbeat`. If a session misses heartbeats for 2-3 minutes (client crash, network disconnect), the TTL eventually removes it.
Before allowing a new stream, we check this hash to count active sessions. If the count equals the subscription limit, we reject the new stream.
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often go deeper into specific components. 
In this section, we will explore the trickiest parts of our design: adaptive bitrate streaming, CDN architecture, the recommendation system, and handling concurrent stream limits.

## 6.1 Video Streaming and Adaptive Bitrate
Delivering video content efficiently is the core technical challenge for Netflix. Users have wildly varying network conditions: some are on gigabit fiber, others on spotty mobile connections. The same user might experience bandwidth fluctuations throughout a viewing session. 
How do we provide the best possible experience for everyone?
The answer is **Adaptive Bitrate Streaming (ABR)**. Rather than streaming at a fixed quality, the system continuously adapts based on network conditions.

### How Video Gets Prepared
The journey begins during content ingestion. A raw movie file arrives as a single, massive file, perhaps 100 GB of uncompressed video. The transcoding pipeline transforms this into a carefully structured set of files optimized for streaming.

#### Step 1: Segmentation
The video is split into small, independently playable segments, typically 4-10 seconds each. A 2-hour movie becomes about 1,800 segments. Each segment starts with a keyframe, making it possible to start playback from any segment without needing previous segments.

#### Step 2: Multi-Quality Encoding
Each segment is encoded at multiple quality levels. A typical encoding ladder might look like:
| Quality | Resolution | Bitrate | Target Use Case |
| --- | --- | --- | --- |
| Low | 480p | 800 kbps | Mobile on 3G |
| Medium | 720p | 1.5 Mbps | Mobile on WiFi |
| High | 1080p | 5 Mbps | Desktop, Smart TV |
| Ultra | 4K | 15 Mbps | 4K TVs, fast connections |

Each quality level gets its own directory of segments, all perfectly aligned so the player can switch between qualities at any segment boundary.

#### Step 3: Manifest Generation
A manifest file (MPD for DASH, M3U8 for HLS) describes all available quality levels and segment locations. The video player fetches this manifest first, then uses it to request individual segments.

### How Adaptive Streaming Works
Now comes the clever part. The video player does not just download segments blindly. It continuously monitors network conditions and buffer status, making intelligent decisions about which quality level to request next.

#### The Adaptation Algorithm
1. **Startup:** Begin with a conservative quality level (often 720p). The goal is to fill the buffer quickly and start playback within seconds.
2. **Continuous measurement:** After each segment download, measure the actual throughput. If a 4-second segment at 5 Mbps (2.5 MB) downloaded in 2 seconds, throughput is 10 Mbps.
3. **Buffer monitoring:** Track how many seconds of video are buffered ahead. A healthy buffer is 20-30 seconds. Below 10 seconds is concerning. Below 5 seconds is critical.
4. **Quality decisions:** Based on throughput and buffer status:
5. **Lookahead:** Smart algorithms consider not just current conditions but trends. If bandwidth has been declining for the last few segments, proactively reduce quality before the buffer runs out.

Segment length is a trade-off:
- **Shorter segments (2s):** Faster quality adaptation, but more HTTP requests (overhead) and less efficient encoding
- **Longer segments (10s):** More efficient encoding and fewer requests, but slower to adapt to network changes

Netflix uses about 4 seconds, balancing adaptation speed with encoding efficiency.

### The User Experience
When done well, adaptive streaming is invisible to users. They press play, video starts in a couple seconds, and quality gradually improves as the buffer builds. If they move to a different room with weaker WiFi, quality smoothly decreases rather than buffering. The experience feels like magic.
When done poorly, you get the dreaded buffering spinner or jarring quality jumps. The algorithms behind ABR represent decades of research and refinement.

## 6.2 Content Delivery Network (CDN) Architecture
With adaptive streaming working on the client side, we need infrastructure that can actually deliver those video segments at scale. This is where the CDN becomes critical.

### The Problem with Centralized Delivery
Imagine serving video from a single data center. A user in Tokyo requests a segment. The request travels across the Pacific to Virginia, the segment travels back. Round-trip latency: 200+ milliseconds. With 4-second segments, that is significant delay on every segment, making smooth playback impossible.
Now multiply by 10 million concurrent streams. The bandwidth requirements (50 Petabits/second) would overwhelm any single location. Centralized delivery simply does not work for video at scale.

### The CDN Solution
A CDN places servers at the "edge" of the network, close to users. Instead of fetching from origin, users fetch from nearby edge servers that cache content.

### CDN Architecture Options
There are two main approaches to CDN architecture:

#### Option 1: Third-Party CDN
Use commercial providers like Akamai, CloudFront, or Fastly. They operate global networks of edge servers and handle all the infrastructure complexity.
**Pros:**
- Quick to deploy
- Global coverage immediately
- No infrastructure investment
- Managed operations

**Cons:**
- Expensive at Netflix scale (bandwidth costs add up)
- Less control over caching behavior
- Dependent on provider's performance

**Best for:** Startups, medium-scale services, getting started quickly

#### Option 2: Custom CDN (Netflix Open Connect)
Build and operate your own CDN infrastructure. Netflix chose this path, deploying custom servers called Open Connect Appliances (OCAs) inside ISP networks worldwide.

##### How Open Connect Works:
1. **ISP Partnerships:** Netflix partners with ISPs to place OCA servers directly in their facilities. Over 1,000 ISPs worldwide host these servers.
2. **Proactive Caching:** Rather than waiting for users to request content, Netflix pushes popular content to OCAs during off-peak hours. When a new show drops, the first episode is already cached everywhere.
3. **Localized Traffic:** Video traffic stays within the ISP network. The user's request never leaves their ISP to reach Netflix, just travels to the OCA in the same facility.
4. **Steering:** Netflix's control plane directs users to the optimal OCA based on server load, content availability, and network conditions.

**Pros:**
- Extremely cost-effective at scale (Netflix saves billions annually)
- Lowest possible latency (content in same ISP facility)
- Full control over caching logic and server software
- ISPs benefit too (less inter-network traffic)

**Cons:**
- Massive upfront investment in hardware
- Complex ISP relationship management
- Operational overhead of thousands of servers
- Years to achieve global coverage

**Best for:** Hyper-scale services where CDN costs would be prohibitive

### CDN Server Selection
When a user presses play, how do we choose which CDN server should serve them?

#### Selection Factors:
1. **Geographic Proximity:** Start with servers physically close to the user. A server 50 miles away is better than 5,000 miles away.
2. **Network Topology:** Even better than geographic proximity is network proximity. A server in the same ISP network has lower latency than one requiring inter-network hops.
3. **Server Load:** An overloaded server provides poor performance. Balance requests across available servers.
4. **Content Availability:** Not all servers cache all content. Less popular content might only be on regional origin servers, not edge caches.
5. **Health Status:** Exclude servers that are experiencing issues or scheduled for maintenance.

The playback service scores available servers on these factors and returns a ranked list. The client tries the first server, falling back to alternates if it fails.

### Comparison Summary
| Approach | Setup Time | Cost at Scale | Latency | Control |
| --- | --- | --- | --- | --- |
| Third-Party CDN | Days | High | Medium | Low |
| Custom CDN | Years | Low | Lowest | Full |
| Hybrid | Months | Medium | Medium | Medium |

For an interview, acknowledge that Netflix uses Open Connect but note that third-party CDNs are a valid starting point for smaller services.

## 6.3 Recommendation System
Netflix attributes 80% of watched content to its recommendation system. Users do not search for most of what they watch. They browse personalized rows and click on suggestions. Getting recommendations right is crucial for engagement and retention.

### The Challenge
With 15,000 titles and millions of users, how do we predict which content each user will enjoy? The problem has several dimensions:
- **Cold start:** New users have no viewing history. What do we recommend?
- **Content diversity:** Recommendations should surface variety, not just more of the same
- **Temporal patterns:** What someone wants to watch changes by time of day, day of week
- **Freshness:** New content should be discoverable, not buried by established titles

### Recommendation Approaches
Let's explore three approaches, from simple to sophisticated.

#### Approach 1: Collaborative Filtering
The core idea: users who liked similar content in the past will like similar content in the future.
Build a matrix of users versus content (who watched what). Find users with similar patterns. Recommend content that similar users enjoyed but this user has not seen.
**Pros:**
- Can discover unexpected connections (people who liked A also liked B, even if A and B seem unrelated)
- Does not require content metadata

**Cons:**
- Cold start problem: new users and new content have no data
- Computationally expensive at scale (matrix operations on billions of cells)
- Popularity bias: tends to recommend popular content

#### Approach 2: Content-Based Filtering
Recommend content similar to what the user has already watched, based on content attributes.
Analyze content attributes: genre, actors, director, themes, mood, pacing. Build a user preference profile from their viewing history. Match against content with similar attributes.
**Pros:**
- Works for new users with even a little history
- New content can be recommended immediately (just needs metadata)
- Explainable: "Because you watched X"

**Cons:**
- Limited discovery (only recommends similar content)
- Filter bubble: users get stuck in narrow preferences
- Requires rich content metadata

#### Approach 3: Hybrid Deep Learning (Netflix's Actual Approach)
Combine multiple signals using deep neural networks. This is what Netflix actually uses, though simplified here.
**Signals Used:**
- Viewing history (what, when, how much)
- Search queries and results clicked
- Browsing behavior (rows scrolled, thumbnails hovered)
- Ratings and thumbs up/down
- Time of day and day of week
- Device type (TV watching differs from mobile)

#### Embedding Approach:
Users and content are represented as dense vectors (embeddings) in a high-dimensional space. Similar users cluster together. Similar content clusters together. Recommendations are content embeddings close to the user embedding.

#### Multiple Models:
Different models capture different patterns:
- Collaborative model: captures user-user similarities
- Content model: captures content attributes
- Sequential model: predicts what you will watch next based on recent history

#### Offline vs Online:
Heavy computation (training models, generating embeddings) happens offline in batch jobs. Online serving re-ranks pre-computed candidates based on real-time context.

### Comparison
| Approach | Cold Start | Discovery | Scalability | Explainability |
| --- | --- | --- | --- | --- |
| Collaborative | Poor | Good | Challenging | Low |
| Content-Based | Moderate | Limited | Good | High |
| Hybrid/Deep Learning | Good | Best | Complex | Low |

For interviews, describe the hybrid approach conceptually. Mention that offline batch processing generates candidates, while online serving handles real-time ranking and personalization.

## 6.4 Handling Concurrent Stream Limits
Netflix limits simultaneous streams based on subscription tier. A Basic plan might allow 1 stream, Standard allows 2, and Premium allows 4. Enforcing this at scale requires careful design.

### The Challenge
- Users can watch on multiple devices (TV, phone, laptop)
- Different subscription tiers have different limits
- Must enforce limits without adding latency to playback start
- Handle edge cases: app crashes, network disconnections, device switches

### Approach: Session-Based Tracking
We track active streaming sessions in Redis, with each account having a hash of active sessions.

#### How It Works:
1. **Playback Request:** When a user presses play, the playback service checks Redis for active sessions under this account.
2. **Limit Check:** Count active sessions. If under the subscription limit, proceed. If at the limit, return HTTP 429 with a message explaining which devices are streaming.
3. **Session Creation:** Create a new session record with device ID, content ID, and current timestamp. This is an atomic operation in Redis.
4. **Heartbeat:** While streaming, the client sends heartbeats every 30 seconds. Each heartbeat updates the session's last-seen timestamp.
5. **Session End:** When the user stops playback (pause, exit, complete), the client sends a stop signal and the session is deleted immediately.
6. **Crash Handling:** If the app crashes or loses network, no stop signal is sent. But heartbeats also stop. The session's TTL (5 minutes) eventually expires it, freeing the slot.

#### Redis Data Structure:

#### Handling Race Conditions:
What if two devices try to start the limit-reaching stream simultaneously? We need atomic operations.

#### Edge Cases:
| Scenario | Solution |
| --- | --- |
| App crash without stop event | Heartbeat timeout (2-3 min) frees slot |
| Network disconnect | Same as crash, heartbeat timeout |
| User switches content | Update existing session, no new slot needed |
| Simultaneous start requests | Use Redis atomic operations to prevent race conditions |

## 6.5 Video Transcoding Pipeline
Transcoding transforms raw video uploads into streaming-ready formats. This is a computationally intensive offline process that must be reliable and efficient.

### Pipeline Architecture

### Pipeline Stages

#### Stage 1: Validation
- Verify file integrity (not corrupted during upload)
- Check format compatibility (supported codec, container)
- Extract technical metadata (resolution, frame rate, audio tracks)
- Reject files that do not meet requirements

#### Stage 2: Analysis
- Scene detection: identify scene boundaries for optimal chunk points
- Content classification: animation vs live action (affects encoding settings)
- Audio analysis: identify language tracks, normalize levels

#### Stage 3: Chunking
- Split video at scene boundaries or fixed intervals
- Each chunk must start with a keyframe (IDR frame)
- Typical chunk size: 4 seconds
- Generate chunk manifest for workers

#### Stage 4: Distributed Encoding
This is the heavy lifting. Each chunk gets encoded at multiple quality levels.
**Encoding Ladder:**
| Resolution | Bitrate | Codec | Target |
| --- | --- | --- | --- |
| 480p | 800 kbps | H.264 | Mobile, low bandwidth |
| 720p | 1.5 Mbps | H.264 | Mobile, medium bandwidth |
| 1080p | 3 Mbps | H.264 | Compatibility |
| 1080p | 2 Mbps | H.265 | Efficient HD |
| 4K | 8 Mbps | H.265 | 4K TVs |
| 4K HDR | 12 Mbps | H.265 | Premium experience |

**Per-Title Encoding (Netflix Innovation):**
Rather than using the same encoding ladder for every title, Netflix analyzes each title's complexity. An animated show with simple backgrounds needs less bitrate than a complex action movie. Per-title encoding optimizes the bitrate ladder for each piece of content, saving bandwidth while maintaining quality.

#### Stage 5: Packaging
- Generate streaming manifests (DASH MPD, HLS M3U8)
- Apply DRM encryption (Widevine, FairPlay, PlayReady)
- Create subtitle tracks in WebVTT format
- Package audio tracks separately for multi-language support

#### Stage 6: Quality Assurance
- VMAF scoring: Netflix's video quality metric (target: > 80)
- Audio sync verification
- Thumbnail generation for browsing
- Playback testing on reference devices

### Scalability
The transcoding pipeline must handle variable load. When many titles arrive simultaneously (e.g., a studio uploads their quarterly catalog), we need to scale up. During quiet periods, we scale down to save costs.

#### Approach:
- Use container orchestration (Kubernetes) for elastic compute
- Priority queues: new releases get priority over catalog back-fill
- Spot/preemptible instances for cost optimization (transcoding can tolerate interruptions)
- Progress checkpointing for long-running encodes

# References
- [Netflix Tech Blog: Open Connect](https://netflixtechblog.com/how-netflix-works-with-isps-around-the-globe-to-deliver-a-great-viewing-experience-a7f6f5ca3fcd) - Deep dive into Netflix's custom CDN architecture
- [Netflix Recommendations: Beyond the 5 Stars](https://netflixtechblog.com/netflix-recommendations-beyond-the-5-stars-part-1-55838468f429) - Overview of Netflix's recommendation system architecture
- [HTTP Live Streaming (HLS) Specification](https://developer.apple.com/documentation/http_live_streaming) - Apple's adaptive streaming protocol
- [DASH Industry Forum](https://dashif.org/) - MPEG-DASH streaming standard
- [Per-Title Encode Optimization](https://netflixtechblog.com/per-title-encode-optimization-7e99442b62a2) - Netflix's approach to optimizing encoding per content