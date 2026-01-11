# Design Tinder

A dating app is a location-based social platform that connects people looking for romantic relationships by showing them potential matches nearby and letting them express interest through a simple swipe mechanism.
The core idea is straightforward: users create profiles, the app shows them other users based on preferences and location, and when two people both express interest (swipe right), they "match" and can start chatting.
**Popular Examples:** [Tinder](https://tinder.com), [Bumble](https://bumble.com), [Hinge](https://hinge.co), OkCupid
The scale of modern dating apps is staggering. Tinder alone processes billions of swipes per day and has made over 75 billion matches since launch. Designing a system that can handle this load while keeping interactions feeling instant requires thoughtful architecture decisions at every layer.
This system design problem combines several interesting challenges: location-based queries, real-time matching, recommendation systems, and messaging infrastructure.
In this chapter, we will explore the **high-level design of a dating app**.
Let's start by clarifying the requirements:
# 1. Clarifying Requirements
Before diving into architecture diagrams, we need to understand exactly what we are building. Dating apps can range from simple swipe-and-match services to complex platforms with video calls, virtual dates, and AI-powered compatibility scoring. The scope we define here will shape every decision that follows.
In an interview, you should never assume you know what the interviewer wants. Ask questions to uncover the real requirements. Here is how that conversation might unfold:
**Candidate:** "What is the expected scale? How many users and daily active users should we support?"
**Interviewer:** "Let's aim for 50 million total users with 10 million daily active users."
**Candidate:** "What are the core features we need to support? Just swiping and matching, or also messaging?"
**Interviewer:** "We need profile creation, swiping (like/pass), matching when both users like each other, and basic messaging between matches."
**Candidate:** "How should we determine which profiles to show users? Just location-based, or should we consider other factors?"
**Interviewer:** "Start with location-based recommendations within a user-defined radius. Consider age and gender preferences too. Advanced ML-based recommendations are nice-to-have."
**Candidate:** "Should matches be notified in real-time when a mutual like happens?"
**Interviewer:** "Yes, real-time notifications are important for engagement. Users should know immediately when they get a match."
**Candidate:** "What about premium features like seeing who liked you, unlimited swipes, or boost?"
**Interviewer:** "Those are nice-to-have. Focus on the core free experience first."
**Candidate:** "Any specific latency or availability requirements?"
**Interviewer:** "The app should be highly available. Swipe actions and profile loading should feel instant, under 200ms."
This conversation reveals several important constraints that will shape our design. Let us formalize these into functional and non-functional requirements.

## 1.1 Functional Requirements
Based on our discussion, here are the core features our system must support:
- **Profile Management:** Users can create, update, and view profiles with photos, bio, and preferences.
- **Discovery:** Users can view potential matches based on location, age, and gender preferences.
- **Swiping:** Users can like (swipe right) or pass (swipe left) on profiles.
- **Matching:** When two users mutually like each other, they become a match.
- **Messaging:** Matched users can send and receive messages.
- **Real-time Notifications:** Users receive instant notifications for new matches and messages.

## 1.2 Non-Functional Requirements
Beyond features, we need to think about the qualities that make the system production-ready:
- **High Availability:** The system must be highly available (e.g., 99.9%).
- **Low Latency:** Swipe actions and profile loading should complete in under 200ms.
- **Scalability:** Should handle 10 million daily active users with millions of swipes per day.
- **Location Accuracy:** Recommendations should accurately reflect user proximity within the specified radius.
- **Data Consistency:** When a match happens, both users must be notified. We cannot have situations where one person sees a match and the other does not.

# 2. Back-of-the-Envelope Estimation
Before diving into architecture, let us run some quick calculations to understand the scale we are dealing with. These numbers will guide our decisions about databases, caching, and infrastructure.

### 2.1 Traffic Estimates
Starting with the numbers from our requirements discussion:

#### Swipe Traffic (Writes)
With 10 million daily active users each making about 100 swipes per day, we are looking at:
But traffic is not uniform throughout the day. Dating app usage peaks in the evening hours, typically between 7 PM and 10 PM, when people are relaxing after work. During these peak windows, we can expect 3x the average load:

#### Profile Views (Reads)
Every swipe requires loading a profile to display. Users also browse profiles they have already seen, view their matches, and check chat history. Assuming a 1.5:1 read-to-write ratio:

#### Match Creation
Not every right swipe results in a match. Based on industry data, roughly 50% of swipes are "likes" (right swipes), and about 5% of those result in mutual matches:
25 million matches per day is significant. Each match triggers notifications to two users and creates a new conversation thread.

### 2.2 Storage Estimates
Let us break down what we need to store for each component:

#### Profile and Photo Storage
| Component | Size per User | 50M Users Total |
| --- | --- | --- |
| Profile metadata | ~2 KB | 100 GB |
| Photos (5 per user) | ~2.5 MB | 125 TB |
| Preferences | ~500 bytes | 25 GB |

Photos dominate storage by a wide margin. This tells us that photo storage needs its own strategy, likely object storage with CDN distribution, rather than living in our primary database.

#### Activity Storage (1 Year Retention)
| Data Type | Size per Record | Daily Volume | 1 Year Total |
| --- | --- | --- | --- |
| Swipes | ~100 bytes | 1B/day | 36.5 TB |
| Matches | ~200 bytes | 25M/day | 1.8 TB |
| Messages | ~500 bytes | ~100M/day (estimated) | 18 TB |

Swipe data accumulates quickly. At 36.5 TB per year, we need to think carefully about retention policies. Do we really need to keep every swipe forever? Probably not. A 90-day rolling window for swipe history might be sufficient, since its primary use is filtering out already-swiped profiles.

### 2.3 Key Insights
These estimates reveal several important design implications:
1. **Write-heavy workload:** Unlike read-heavy systems like content platforms, dating apps have substantial write traffic. 35,000 swipes per second at peak is not trivial.
2. **Photos need special handling:** 125 TB of photos cannot live in a database. We need object storage (S3, GCS) with CDN distribution.
3. **Swipe data is ephemeral:** The main purpose of swipe records is to prevent showing the same profile twice. We do not need to keep them forever.
4. **Matches and messages are the valuable data:** These represent actual connections and conversations. They need durable storage with strong consistency.
5. **Peak traffic matters:** Our system needs to handle 3x average load during evening peak hours. Auto-scaling and caching become essential.

# 3. Core APIs
With our requirements and scale understood, let us define the API contract. The API is the interface between our mobile apps and backend services, so getting it right matters for both usability and performance.
We will design a RESTful API with four main endpoint groups. Here is an overview of the core operations:
Let us walk through each endpoint.

### 3.1 Create/Update Profile

#### Endpoint: PUT /users/{user_id}/profile
This is typically the first API a new user calls after registration. It creates or updates their dating profile with all the information other users will see.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| name | string | Yes | Display name shown on profile |
| bio | string | No | Short description (max 500 characters) |
| photos | array | Yes | Array of photo URLs (1-6 photos) |
| birth_date | date | Yes | Used for age calculation and filtering |
| gender | enum | Yes | User's gender identity |
| preferences | object | Yes | Contains age_range, gender_preference, max_distance_km |

#### Example Request:

#### Success Response (200 OK):

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Invalid input | Missing required fields, invalid age, malformed data |
| 401 Unauthorized | Auth required | Missing or invalid authentication token |
| 413 Payload Too Large | Content too big | Photos exceed size limits |

### 3.2 Get Recommendations

#### Endpoint: GET /recommendations
This is the most frequently called endpoint in the entire system. Every time a user opens the app to swipe, they need a fresh batch of profiles to browse. The quality of these recommendations directly impacts user engagement.

#### Query Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| latitude | float | Yes | User's current latitude |
| longitude | float | Yes | User's current longitude |
| limit | int | No | Number of profiles to return (default: 20, max: 50) |

#### Success Response (200 OK):
We include `remaining_count` so the app can show users how many potential matches are available in their area. The `next_refresh_at` field tells the client when new profiles might be available (after running recommendation algorithms or when new users join).

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 401 Unauthorized | Auth required | Missing authentication |
| 429 Too Many Requests | Rate limited | Free users exceeded their daily recommendation quota |

### 3.3 Swipe Action

#### Endpoint: POST /swipes
This endpoint records a user's decision to like or pass on a profile. It is where the magic happens: if this swipe creates a mutual match, the response includes the match details so the app can immediately show the "It's a Match!" screen.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| target_user_id | string | Yes | The user being swiped on |
| action | enum | Yes | Either like or pass |

#### Example Request:

#### Success Response (201 Created):
When `is_match` is false, the `match` field is omitted. The client only shows the match celebration when both users have liked each other.

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Invalid input | Invalid user ID or action |
| 409 Conflict | Duplicate swipe | Already swiped on this user |
| 429 Too Many Requests | Rate limited | Free user exceeded daily swipe limit |

### 3.4 Send Message

#### Endpoint: POST /matches/{match_id}/messages
Once two users match, they can start chatting. This endpoint handles sending messages within a conversation.

#### Path Parameters:
| Parameter | Type | Description |
| --- | --- | --- |
| match_id | string | The unique identifier for the match/conversation |

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| content | string | Yes | Message text (max 1000 characters) |

#### Example Request:

#### Success Response (201 Created):
The `status` field indicates whether the message has been delivered to the recipient's device. If the recipient is offline, status would be `sent` until they come online.

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 403 Forbidden | Not authorized | User is not part of this match, or match was unmatched |
| 404 Not Found | Match missing | Match ID does not exist |

### 3.5 API Design Considerations
A few design decisions worth highlighting:
**Authentication:** All endpoints require authentication via JWT tokens. The user ID is extracted from the token rather than passed in the request body, preventing users from impersonating others.
**Rate Limiting:** Free users have limits on swipes per day (typically 100) and recommendations fetched per hour. Premium users get higher or unlimited quotas. Rate limiting is enforced at the API gateway level.
**Idempotency:** The swipe endpoint is idempotent. If a user somehow sends the same swipe twice, the second request returns 409 Conflict rather than creating a duplicate record.
**Pagination:** For endpoints returning lists (matches, messages, recommendations), we use cursor-based pagination with a `cursor` query parameter for efficient iteration through large result sets.
# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complex diagram upfront, we will build the design incrementally, starting with the simplest possible solution and adding components as we encounter challenges. This mirrors how you would approach the problem in an interview.
Our system needs to handle four fundamental operations:
1. **Profile Management:** Creating and updating user profiles with photos
2. **Discovery:** Finding potential matches based on location and preferences
3. **Matching:** Detecting when two users have mutually liked each other
4. **Messaging:** Enabling real-time chat between matched users

What makes a dating app architecturally interesting is that these operations have very different characteristics. Profile updates are infrequent but photos are large. Discovery queries are read-heavy but require complex geospatial filtering. Match detection must be instant and handle race conditions. Messaging needs real-time delivery with persistent storage.
Let us visualize the two main paths through our system:
The write path handles swipes and messages, which need to be recorded reliably. The read path handles profile views and recommendations, where caching can dramatically reduce database load. Let us build this architecture step by step.


Users need to create profiles with photos, bio, and preferences before they can start swiping. While this seems like a straightforward CRUD operation, there is one important wrinkle: photos.
Photos are large binary files, often 1-2 MB each, and users upload 5-6 of them. Storing photos in a database would bloat it unnecessarily and make queries slower. We need a separate strategy for media.

### Components for Profile Management

#### Profile Service
This service handles all profile-related operations: creation, updates, and retrieval. It validates input (checking that users are old enough, that bio text is not inappropriate), stores metadata in the database, and returns complete profile objects to clients.
The Profile Service is stateless. Any instance can handle any request, making horizontal scaling straightforward.

#### Media Service
Handles photo uploads separately from profile data. When a user selects a photo, the client uploads it directly to object storage using a pre-signed URL (avoiding the need to route large files through our backend). The Media Service then processes the photo, generating multiple resolutions:
- **Thumbnail (100px):** For match lists and notifications
- **Medium (400px):** For the swipe card preview
- **Full (1200px):** For detailed profile view

All versions are stored in object storage and served through a CDN for low-latency global access.
**Why separate photo upload from profile creation?** If photo processing fails (corrupted image, wrong format), it should not prevent the user from saving their bio and preferences. The client can retry photo uploads independently.

### The Profile Creation Flow
Let us trace through what happens when a new user creates their profile:
1. **Photo upload:** The client requests a pre-signed upload URL from the Media Service. This URL allows direct upload to S3 without routing through our servers, saving bandwidth and reducing latency.
2. **Photo processing:** Once the upload completes, the client notifies the Media Service to process the photo. The service downloads it, validates it is a real image (not malware disguised as a photo), resizes it to multiple dimensions, and stores all versions in S3.
3. **CDN URLs:** The Media Service returns CDN URLs for each photo resolution. These URLs are what the client will include in the profile data.
4. **Profile creation:** The client sends the complete profile (name, bio, preferences, photo URLs) to the Profile Service via the API Gateway. The service validates the data and inserts it into the database.
5. **Serving photos:** When other users view this profile, photos are served from CDN edge nodes, typically within 20-50ms regardless of where the viewer is located.


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
        S1[Media Service]
        S2[Managed Service]
        S3[other Service]
        S4[throughput Service]
        S5[Messaging Service]
    end

    subgraph Data Storage
        DBPostgreSQL[PostgreSQL]
        DBDynamoDB[DynamoDB]
        DBCassandra[Cassandra]
    end

    subgraph Caching Layer
        CacheRedis[Redis]
    end

    subgraph Message Queue
        QueueKafka[Kafka]
    end

    subgraph Object Storage
        StorageS3[S3]
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
    S1 --> DBPostgreSQL
    S1 --> DBDynamoDB
    S1 --> CacheRedis
    S1 --> QueueKafka
    S2 --> DBPostgreSQL
    S2 --> DBDynamoDB
    S2 --> CacheRedis
    S2 --> QueueKafka
    S3 --> DBPostgreSQL
    S3 --> DBDynamoDB
    S3 --> CacheRedis
    S3 --> QueueKafka
    S4 --> DBPostgreSQL
    S4 --> DBDynamoDB
    S4 --> CacheRedis
    S4 --> QueueKafka
    S5 --> DBPostgreSQL
    S5 --> DBDynamoDB
    S5 --> CacheRedis
    S5 --> QueueKafka
    S1 --> StorageS3
    S1 --> Storageobjectstorage
    StorageS3 --> CDNNode
    Storageobjectstorage --> CDNNode
    CDNNode --> Web
    CDNNode --> Mobile



## 4.2 Requirement 2: Discovery
This is the heart of the dating app experience. When a user opens the app, they want to see a stack of potential matches: people who are nearby, within their age preference, match their gender preference, and have not already been swiped on.
The challenge is that this query is expensive. We need to find users within a geographic radius (geospatial query), filter by multiple criteria (age, gender, preferences), exclude thousands of already-swiped profiles (set difference), and rank the results (recommendation algorithm). Doing this naively would hammer the database.

### Components for Discovery

#### Recommendation Service
The orchestrator of the discovery flow. It coordinates with other services to build a personalized feed of profiles for each user.
The Recommendation Service does not just return random nearby users. It ranks candidates based on factors like profile completeness, recent activity (showing active users over dormant ones), and potentially compatibility signals. We will explore the ranking algorithm in the deep dive section.

#### Location Service
Handles all location-related operations. When a user opens the app, their location is updated. When they request recommendations, we need to find other users within their specified radius.
Efficiently querying "find all users within 50 km of this point" across millions of users requires specialized data structures. The Location Service maintains a geospatial index (we will discuss the options in the deep dive: geohashing, PostGIS, Redis GEO).

#### Redis Cache
Recommendation queries are expensive, but most users do not move far between sessions. We cache recommendation results in Redis with a short TTL (5-10 minutes). If a user has not moved significantly, we serve cached results instead of recomputing.
We also cache individual profiles since the same popular profiles appear in many users' recommendations. And we store each user's "already swiped" set in Redis for fast filtering.

### The Recommendation Flow
Let us walk through this step by step:
1. **Request arrives:** The client sends the user's current location (latitude, longitude) and requests recommendations.
2. **Check cache first:** Before doing any expensive work, we check if we have cached recommendations for this user at this approximate location. If so, we return them immediately.
3. **Find nearby users:** On a cache miss, we query the Location Service. This returns a list of user IDs within the specified radius, typically hundreds or thousands of candidates.
4. **Filter candidates:** We remove users who do not match preferences (wrong age, wrong gender), users who have already been swiped on (using the Redis set), and users who have blocked this user or been blocked by them.
5. **Rank and select:** From the remaining candidates, we rank by our recommendation algorithm and select the top N (typically 20-50 profiles).
6. **Fetch profiles:** We batch-fetch profile data, checking the cache first and falling back to the database for any cache misses.
7. **Cache and return:** We cache the recommendation results (with the user's approximate location as part of the key) and return the profiles to the client.

## 4.3 Requirement 3: Swiping and Matching
This is where the magic happens. When a user swipes right, we need to:
1. Record the swipe action
2. Check if the other person has already swiped right on them
3. If yes, create a match and notify both users instantly

The tricky part is making this fast and reliable. With 35,000 swipes per second at peak, we cannot afford slow database queries on the critical path. And match detection must be atomic: if two users swipe right on each other at nearly the same time, we need to detect the match exactly once, not zero times or twice.

### Components for Matching

#### Swipe Service
Records swipe actions and detects matches. This is a high-throughput service that needs to handle 35K writes per second at peak.
The key insight is that we only care about the most recent swipe between two users. If User A swipes left on User B, then later swipes right, only the right swipe matters. This means we can use a simple key-value model: the key is `(swiper, target)` and the value is the action.

#### Notification Service
When a match is detected, we need to notify both users immediately. The Notification Service handles multiple delivery channels:
- **WebSocket:** For users who have the app open, we push the match notification in real-time
- **Push notification:** For users who have the app in background or closed, we send a mobile push notification
- **In-app queue:** We also store the notification so users see it when they next open the app

### The Match Detection Flow
Let us break this down:
1. **User A swipes right on User B:** The swipe arrives at the Swipe Service.
2. **Check for existing like:** Before recording anything, we check Redis to see if User B has already liked User A. This is a single O(1) lookup.
3. **Match detected:** If User B already liked User A, we have a match. We immediately:
4. **No match yet:** If User B has not liked User A, we store User A's like in Redis (so future swipes from User B will detect the match) and persist it to the database asynchronously.

**Why Redis for match detection?** The database would work, but Redis gives us sub-millisecond lookups. For a feature that users experience 100 times per session, shaving off latency makes the app feel snappier.
**Handling race conditions:** What if User A and User B swipe right on each other at exactly the same time? Both requests check Redis, both find no existing like, both store their likes, and no match is detected. This is a classic race condition.
We solve this with Redis atomic operations. Instead of separate read and write operations, we use a single SETNX (set if not exists) or Lua script that atomically checks and updates. If the check fails (the other like already exists), we know a match should be created.

## 4.4 Requirement 4: Messaging
Once two users match, they can start chatting. The messaging system needs to feel like any modern chat app: messages should arrive instantly when both users are online, and the conversation should persist so users can pick up where they left off.
This is a classic chat system design problem, but with one simplification: we only need to support 1-on-1 conversations between matched users, not group chats.

### Components for Messaging

#### Messaging Service
The core service that handles message operations. Before accepting any message, it validates that the sender and recipient are actually matched. This prevents spam from users who somehow bypass the UI.
The Messaging Service stores messages persistently and handles delivery logic. If the recipient is online, deliver immediately. If offline, queue a push notification.

#### WebSocket Gateway
Maintains persistent connections with clients for real-time bidirectional communication. When a user opens the app, they establish a WebSocket connection. This connection stays open while the app is active, allowing us to push messages without the client polling.
The WebSocket Gateway is stateful: it needs to know which users are connected to which server instances. We use Redis to maintain a mapping of user IDs to WebSocket server instances. When a message needs to be delivered, we look up where the recipient is connected and route it there.

#### Message Database
Messages need to be stored durably. We use a database optimized for time-series data (like Cassandra or ScyllaDB), where the partition key is the match ID and messages are ordered by timestamp. This makes retrieving conversation history efficient.

### The Messaging Flow
Here is how a message flows through the system:
1. **Sender types a message:** The message is sent over the existing WebSocket connection to the WebSocket Gateway.
2. **Validation:** The Messaging Service verifies that the sender and recipient are actually matched. This prevents edge cases where a user somehow sends a message to someone they are not matched with.
3. **Persistence:** The message is written to the database immediately. Even if delivery fails, the message is safe.
4. **Recipient lookup:** We check Redis to see if the recipient has an active WebSocket connection. If so, we know which WebSocket Gateway instance they are connected to.
5. **Real-time delivery:** If the recipient is online, we route the message through their WebSocket connection. They see it instantly. The client sends an acknowledgment back, and we update the message status to "delivered."
6. **Offline handling:** If the recipient is not connected, we queue a push notification. When they open the app later, they will fetch unread messages from the database.

**Handling reconnection:** Mobile connections are unreliable. Users go through tunnels, switch from WiFi to cellular, or close the app temporarily. The WebSocket Gateway handles graceful reconnection, and when a user reconnects, we fetch any messages that arrived while they were offline.

## 4.5 Putting It All Together
Now that we have designed each requirement individually, let us step back and see the complete architecture. We have a layered system where each layer has a specific responsibility:

### Layer Responsibilities
**Client Layer:** The mobile app runs on iOS and Android. It handles the UI, local caching of profiles for smooth swiping, and maintains connections for real-time features.
**Edge Layer:** Three components sit at the edge of our infrastructure:
- **CDN** serves photos globally with low latency
- **API Gateway** handles authentication, rate limiting, and request routing
- **WebSocket Gateway** maintains persistent connections for messaging and notifications

**Application Layer:** Six microservices handle the core business logic:
- **Profile Service** manages user profiles and preferences
- **Recommendation Service** generates personalized profile feeds
- **Location Service** handles geospatial queries
- **Swipe Service** records swipes and detects matches
- **Messaging Service** handles chat between matched users
- **Notification Service** delivers push notifications

**Cache Layer:** Redis serves multiple purposes: caching profiles, storing pending likes for match detection, tracking user connections, and maintaining the geospatial index.
**Storage Layer:** Different databases for different access patterns:
- **PostgreSQL** for profiles (relational data with complex queries)
- **Cassandra** for swipes and messages (high write throughput, time-series data)
- **S3** for photos (cheap, durable object storage)

### Component Responsibilities Summary
| Component | Primary Responsibility | Scaling Strategy |
| --- | --- | --- |
| API Gateway | Auth, rate limiting, routing | Horizontal (stateless) |
| WebSocket Gateway | Real-time connections | Horizontal with Redis coordination |
| Profile Service | Profile CRUD | Horizontal (stateless) |
| Recommendation Service | Personalized discovery | Horizontal with cached results |
| Location Service | Geospatial queries | Redis GEO cluster |
| Swipe Service | Record swipes, detect matches | Horizontal with Redis |
| Messaging Service | Chat persistence, delivery | Horizontal (stateless) |
| Notification Service | Push notifications | Queue-based, auto-scaling |
| CDN | Photo delivery | Managed service (auto-scales) |
| Redis Cluster | Caching, pub/sub, geo | Add shards |
| PostgreSQL | Profile storage | Read replicas, then sharding |
| Cassandra | Swipes, messages | Add nodes |

# 5. Database Design
With the high-level architecture in place, let us zoom into the data layer. Choosing the right databases and designing efficient schemas are critical decisions that affect performance, scalability, and operational complexity.

## 5.1 Choosing the Right Database
The database choice is not one-size-fits-all. Different parts of our system have different access patterns, and we should pick the right tool for each job.
Let us think through each data type:
**User Profiles** are read-heavy (every recommendation loads multiple profiles) and have a well-defined schema that benefits from relational constraints. We query primarily by user_id but also need to filter by age, gender, and location. PostgreSQL is a good fit here. It handles our read volume easily, supports complex queries when needed, and has mature tooling for backups and replication.
**Swipes** are write-heavy with over a billion per day. Each swipe is a simple record: who swiped whom and what action. We need to query "has User B swiped on User A?" for match detection. Cassandra or DynamoDB excel at this workload. They handle high write throughput, and the access pattern is a simple key-value lookup.
**Messages** are append-only time-series data. We write new messages constantly and read them ordered by timestamp within a conversation. Cassandra is ideal: we partition by match_id so all messages for a conversation are stored together, and use a time-based clustering key for ordering.
**Location Data** requires geospatial indexing with frequent updates. Users move around, and we need sub-second radius queries. Redis with its built-in GEO commands provides in-memory speed for both updates and queries.

### The Hybrid Approach
Given these patterns, we use multiple databases:
| Data Type | Database | Why |
| --- | --- | --- |
| Profiles, Preferences | PostgreSQL | Complex queries, ACID transactions, relational integrity |
| Swipes | Cassandra | High write throughput, simple key-value lookups |
| Messages | Cassandra | Time-series data, ordered by timestamp |
| Locations | Redis GEO | In-memory speed, built-in geospatial indexing |
| Caching | Redis | Profile cache, pending likes, connection tracking |

## 5.2 Database Schema
Here is the entity relationship overview:

### Users Table (PostgreSQL)
This is the core table storing profile information for all users.
| Field | Type | Description |
| --- | --- | --- |
| user_id | UUID (PK) | Unique identifier, generated on signup |
| email | VARCHAR(255) | Login email, must be unique |
| name | VARCHAR(100) | Display name shown on profile |
| bio | TEXT | Short bio (max 500 chars, validated at app level) |
| birth_date | DATE | For calculating age during filtering |
| gender | ENUM | User's gender identity |
| photos | JSONB | Array of CDN URLs for profile photos |
| created_at | TIMESTAMP | Account creation time |
| last_active | TIMESTAMP | Last activity, for showing "active today" badges |

**Indexes:**
- Primary key on `user_id`
- Unique index on `email`
- Index on `last_active` for filtering by recent activity

### Preferences Table (PostgreSQL)
Stores each user's matching preferences. Separated from the Users table to keep profile data lean (preferences are only needed during recommendation generation, not profile viewing).
| Field | Type | Description |
| --- | --- | --- |
| user_id | UUID (PK, FK) | References the users table |
| min_age | INTEGER | Minimum age they want to see |
| max_age | INTEGER | Maximum age they want to see |
| gender_preference | ENUM[] | Array of genders they are interested in |
| max_distance_km | INTEGER | How far they are willing to look |

### Swipes Table (Cassandra)
Records every swipe action. This is our highest-volume table at 1 billion writes per day.
| Field | Type | Description |
| --- | --- | --- |
| swiper_id | UUID | Partition key: the user doing the swiping |
| swiped_id | UUID | Clustering key: the user being swiped on |
| action | VARCHAR | "like" or "pass" |
| created_at | TIMESTAMP | When the swipe happened |

**Why this schema?** The partition key `swiper_id` means all of a user's swipes are stored together. The clustering key `swiped_id` allows efficient lookup of "did I swipe on this person?" To check if User B swiped on User A (for match detection), we need a reverse lookup. We maintain this in Redis rather than creating a secondary index.

### Matches Table (PostgreSQL)
Stores confirmed matches. Lower volume than swipes (25 million per day) and needs relational queries like "show me all my matches with profile details."
| Field | Type | Description |
| --- | --- | --- |
| match_id | UUID (PK) | Unique identifier for the match |
| user_id_1 | UUID (FK) | First user (we always store lower UUID first for consistency) |
| user_id_2 | UUID (FK) | Second user |
| created_at | TIMESTAMP | When the match was created |
| status | ENUM | "active" or "unmatched" (if one user unmatches) |

**Indexes:**
- Index on `user_id_1` and `user_id_2` separately (to find matches for either user)
- Composite index on `(user_id_1, status)` and `(user_id_2, status)` for filtering active matches

### Messages Table (Cassandra)
Stores all chat messages. Optimized for the common access pattern: "fetch the last N messages in this conversation."
| Field | Type | Description |
| --- | --- | --- |
| match_id | UUID | Partition key: which conversation |
| message_id | TIMEUUID | Clustering key: time-based UUID for ordering |
| sender_id | UUID | Who sent the message |
| content | TEXT | The message text |
| created_at | TIMESTAMP | When it was sent (redundant with TIMEUUID but explicit) |
| read_at | TIMESTAMP | Null until recipient reads, then timestamp |

**Why TIMEUUID?** The clustering key uses TIMEUUID (a time-based UUID) which provides both uniqueness and natural chronological ordering. Messages within a partition are stored in time order, making "fetch latest 50 messages" a simple range scan.
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often go deeper into specific components. In this section, we will explore the trickiest parts of our design: efficiently finding nearby users, detecting matches at scale, delivering real-time notifications, preventing abuse, and handling traffic spikes.
These are the topics that distinguish a good system design answer from a great one.

## 6.1 Location-Based Discovery
Finding nearby users sounds simple until you think about the scale. We have 50 million users spread across the globe, and every recommendation request needs to find users within a specific radius, filter them by preferences, and exclude already-swiped profiles.
A naive approach of calculating the distance to all 50 million users on every request would take minutes, not milliseconds. We need smarter data structures.

### The Problem
When a user requests recommendations, we need to find all users who:
- Are within the user's specified radius (say, 50 km)
- Match the user's gender and age preferences
- Have not been swiped on by this user yet
- Have the requester's gender in their own preferences (mutual interest)

Each filtering step dramatically reduces the candidate pool, but the first step (geographic filtering) is the most expensive. Let us explore how to make it fast.

### Approach 1: Geohashing
Geohashing converts a 2D coordinate (lat, long) into a single string that represents a rectangular area on Earth.

#### How It Works
1. **Encoding:** The Earth is recursively divided into grid cells. Each additional character in the geohash represents a finer subdivision.
2. **Proximity Property:** Locations with similar geohashes are geographically close. Nearby locations often share the same prefix.
3. **Querying:** To find users within a radius:

#### Implementation
Store users with their geohash prefix:
Create an index on `geohash_6` and query:

#### Pros
- **Fast lookups:** Index-based queries, no distance calculations in the database.
- **Scalable:** Works well with sharding (shard by geohash prefix).
- **Simple implementation:** Just string prefix matching.

#### Cons
- **Edge cases:** Users near cell boundaries might miss nearby users in adjacent cells.
- **Fixed precision:** Need to query multiple precision levels for different radius sizes.
- **Uneven distribution:** Some geohash cells might have many more users than others.

### Approach 2: Spatial Databases (PostGIS, MongoDB Geospatial)
Use database-native geospatial indexing with specialized data structures like R-trees.

#### How It Works
1. Store locations as native geospatial types (POINT, GEOGRAPHY).
2. Create a spatial index on the location column.
3. Use built-in functions for radius queries.

#### Pros
- **Accurate:** Native distance calculations, no edge case issues.
- **Flexible:** Supports complex spatial queries (polygons, routes).
- **Optimized:** R-tree indexes are highly efficient for spatial queries.

#### Cons
- **Database dependency:** Ties you to specific database technologies.
- **Scaling complexity:** Harder to shard than geohash-based approaches.
- **Index maintenance:** Spatial indexes can be expensive to maintain with frequent updates.

### Approach 3: Redis Geospatial
Redis provides built-in geospatial indexing using sorted sets with geohash scores.

#### How It Works

#### Pros
- **Extremely fast:** In-memory operations, sub-millisecond queries.
- **Simple API:** Built-in commands for common operations.
- **Perfect for real-time:** Great for frequently updating locations.

#### Cons
- **Memory constraints:** All data must fit in RAM.
- **Limited filtering:** Can't combine spatial query with complex filters in one operation.
- **No persistence guarantees:** Need separate persistent storage.

### Comparing the Approaches
Each approach has trade-offs. Here is how they stack up:
| Approach | Latency | Accuracy | Scaling | Best For |
| --- | --- | --- | --- | --- |
| Geohashing | Very fast | Good (with neighbors) | Excellent (shardable) | Large-scale, sharded systems |
| PostGIS/R-tree | Fast | Excellent | Moderate | Complex spatial queries |
| Redis GEO | Extremely fast | Good | Good (cluster) | Real-time, high-frequency updates |

### Recommendation: Hybrid Approach
For a dating app at scale, we combine approaches to get the best of each:

#### The flow works like this:
1. **Redis GEO for geographic filtering:** When a user requests recommendations, we query Redis with their coordinates and radius. Redis returns user IDs of everyone within range in under a millisecond.
2. **In-memory preference filtering:** We check each candidate against the user's preferences (age range, gender). This uses cached preference data, also in Redis.
3. **Exclude already-swiped users:** We maintain a Redis set of user IDs this person has already swiped on. A simple set difference removes them from consideration.
4. **Fetch profiles:** For the remaining candidates, we fetch full profile data from our cache or PostgreSQL if not cached.
5. **Rank and return:** We apply our recommendation algorithm to rank candidates and return the top 20.

This hybrid approach gives us sub-100ms response times even with millions of users, and it scales horizontally by adding more Redis nodes.

## 6.2 Match Detection at Scale
When a user swipes right, we need to instantly check if the other person has also swiped right. This sounds simple, but with 35,000 swipes per second at peak, the naive approach of querying the database on every swipe becomes a bottleneck.
The challenge is not just speed. We also need to handle race conditions. What if two users swipe right on each other at the exact same moment? We need to detect the match exactly once, not zero times (both checks happen before either write) or twice (both detect a match).

### The Problem
When User A swipes right on User B:
1. Record A's swipe.
2. Check if B has already swiped right on A.
3. If yes, create a match and notify both users.
4. All of this should happen in under 200ms.

### Approach 1: Synchronous Database Check
The simplest approach: on every right swipe, query the database for the reverse swipe.

#### Pros
- Simple to implement.
- Strong consistency (always checks current state).

#### Cons
- Two database operations per swipe.
- High latency under load.
- Database becomes bottleneck at scale.

### Approach 2: Redis-Based Match Detection
Use Redis for fast, in-memory match detection.

#### How It Works
For each user, maintain a set of users who have liked them:
If a match is found:
1. Create the match record (async write to database).
2. Remove entries from the liked_by sets.
3. Trigger notifications.

#### Implementation Flow

#### Pros
- **Ultra-fast:** Single Redis operation for match detection.
- **Scalable:** Redis handles millions of operations per second.
- **Memory efficient:** Only stores "pending" likes, not all swipes.

#### Cons
- **Data loss risk:** Redis data can be lost on failure before DB sync.
- **Eventual consistency:** Small window where swipe might not be recorded.

### Approach 3: Write-Behind Pattern with Kafka
For high reliability and scale, use an event-driven architecture.

#### How It Works
1. Swipe action published to Kafka topic.
2. Match detection service consumes events.
3. Service maintains an in-memory cache of pending likes.
4. Matches are detected and persisted asynchronously.

#### Pros
- **Highly scalable:** Kafka handles massive throughput.
- **Reliable:** Events are persisted and can be replayed.
- **Decoupled:** Services can scale independently.

#### Cons
- **Latency:** Added hop through Kafka (10-50ms).
- **Complexity:** More infrastructure to manage.
- **Eventual consistency:** Matches might have slight delay.

### Recommendation
For most dating apps, **Approach 2 (Redis-based)** provides the best balance:
- Fast enough for real-time match detection (< 10ms).
- Simple to implement and operate.
- Scales to millions of users.

Add write-ahead logging or Kafka for durability if data loss is unacceptable.
| Approach | Latency | Scalability | Complexity | Best For |
| --- | --- | --- | --- | --- |
| Database Check | 50-100ms | Moderate | Low | MVP, low traffic |
| Redis-Based | 1-5ms | High | Medium | Most apps |
| Kafka Event-Driven | 20-50ms | Very High | High | Massive scale, strong durability needs |

## 6.3 Real-Time Notifications
When a match happens, both users should be notified instantly. This is the "magic moment" that makes dating apps exciting. A delay of even a few seconds can diminish the thrill of seeing "It's a Match!" on your screen.
But notification delivery is not straightforward. Users might be actively using the app (deliver via WebSocket), have the app in background (push notification), or be offline entirely (queue for later). We need to handle all these cases gracefully.

### Requirements
- **Latency:** Notification delivered within 1 second of match
- **Reliability:** Notifications should never be lost, even if delivery is delayed
- **Multi-channel:** Support in-app, push notifications, and potentially email

### Approach 1: Polling
The client periodically asks the server for new notifications.

#### Pros
- Simple to implement.
- Works through firewalls and proxies.
- No persistent connection overhead.

#### Cons
- High latency (depends on poll interval).
- Wasteful (most polls return nothing).
- Poor user experience for real-time features.

### Approach 2: WebSocket
Maintain a persistent bidirectional connection between client and server.

#### How It Works
1. Client establishes WebSocket connection on app open.
2. Server maintains a mapping of user_id to WebSocket connection.
3. When a match occurs, server pushes notification through the socket.

#### Connection Management

#### Pros
- **Instant delivery:** Sub-second latency.
- **Efficient:** No polling overhead.
- **Bidirectional:** Can also use for real-time chat.

#### Cons
- **Connection overhead:** Each user holds a connection.
- **Complexity:** Need to handle reconnection, load balancing.
- **Mobile challenges:** Connections drop when app is backgrounded.

### Approach 3: Server-Sent Events (SSE)
A lighter alternative to WebSocket for one-way server-to-client communication.

#### Pros
- Simpler than WebSocket.
- Works over HTTP (better proxy support).
- Auto-reconnection built into the protocol.

#### Cons
- One-way only (server to client).
- Not supported in all environments.

### Push Notifications for Offline Users
When users are offline, rely on platform push notifications (APNs for iOS, FCM for Android).

### Recommendation
Use a **hybrid approach**:
1. **WebSocket** for in-app real-time notifications when app is active.
2. **Push notifications** (FCM/APNs) for offline users.
3. **Notification queue** (Redis or Kafka) to ensure reliability.

The flow:
1. Match event triggers notification.
2. Notification service checks if user is online (WebSocket connection exists).
3. If online: deliver via WebSocket.
4. If offline: queue push notification.
5. Store notification in database for history/deduplication.

## 6.4 Preventing Abuse and Ensuring Safety
Dating apps are prime targets for abuse. Spammers use them to distribute links. Scammers create fake profiles to manipulate lonely users. Bots swipe on everyone to farm matches. And some users harass others with unwanted messages.
A robust system must protect users from all of these while not creating so much friction that legitimate users give up. It is a delicate balance.

### Rate Limiting
The first line of defense is limiting how fast users can perform actions.
**Swipe Limits:**
- Free users: 100 swipes per day.
- Premium users: Unlimited or higher limit.

**Implementation (Redis):**
**Message Limits:**
- Limit messages per conversation per hour.
- Limit new conversations initiated per day.

### Bot and Fake Account Detection
Detect automated or fake accounts:
**Signals:**
- **Behavioral:** Swipe patterns (too fast, too uniform), message patterns.
- **Device:** Multiple accounts from same device, suspicious device fingerprints.
- **Content:** Stock photos, duplicate bios, suspicious links in messages.

**Implementation:**
1. **ML-based scoring:** Train models on known fake accounts.
2. **Rule-based filters:** Block obvious spam patterns.
3. **Human review queue:** Flag suspicious accounts for manual review.
4. **Photo verification:** Optional selfie verification to prove authenticity.

### Blocking and Reporting
Users must be able to protect themselves:
**Block:**
- Blocked user cannot see the blocker's profile.
- Cannot send messages.
- Existing match is hidden.

**Report:**
- Captures context (screenshots, message history).
- Queues for human review.
- Patterns of reports trigger automatic action.

### Data Privacy
- **Location privacy:** Never expose exact coordinates. Use fuzzy locations (within X km).
- **Profile visibility controls:** Let users hide profile temporarily.
- **Data export/deletion:** GDPR compliance, user can request all data or deletion.

## 6.5 Handling High Traffic During Peak Hours
Dating app usage is not uniform throughout the day. Usage peaks dramatically in the evening (7-10 PM local time) when people are relaxing after work, and again on weekends. During these windows, traffic can spike to 3-5x the average.
If we provision infrastructure for peak load 24/7, we waste money during off-peak hours. If we provision for average load, we crash during peaks. The solution is auto-scaling: dynamically adding and removing capacity based on demand.

### Auto-Scaling
Modern cloud platforms make auto-scaling straightforward. We configure rules that add or remove instances based on metrics:
- **CPU/Memory based:** Scale when resource usage exceeds threshold.
- **Request count based:** Scale when QPS exceeds threshold.
- **Queue depth based:** Scale workers when message queue grows.

### Caching Strategy
Aggressive caching reduces database load during peaks:
**Profile Cache (Redis):**
- TTL: 5 minutes for active users, 1 hour for inactive.
- Invalidation: On profile update.

**Recommendation Cache:**
- Cache the recommendation queue per user.
- Pre-compute recommendations during off-peak hours.
- Invalidate when user changes location significantly.

**CDN for Photos:**
- All profile photos served through CDN.
- Multiple edge locations for global low-latency.

### Graceful Degradation
When systems are overloaded, degrade non-critical features:
1. **Reduce recommendation quality:** Show cached/pre-computed results instead of real-time personalized.
2. **Delay non-critical notifications:** Batch and delay email notifications.
3. **Limit expensive features:** Temporarily disable "see who liked you" for free users.
4. **Circuit breakers:** Fail fast on struggling services, return cached data.

### Database Read Replicas
Scale read capacity with replicas:
- **Primary:** Handles all writes.
- **Replicas:** Handle read queries (profile views, recommendation queries).
- **Routing:** Application directs reads to replicas, writes to primary.

For recommendation queries that can tolerate slight staleness, read from replicas. For match detection (needs latest swipe data), read from primary or Redis.