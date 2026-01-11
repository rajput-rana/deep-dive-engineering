# Design Pastebin

## What is Pastebin?

Pastebin is a web service that allows users to store and share plain text or code snippets over the internet through unique URLs.
The core idea is simple: a user pastes text content, the system generates a unique key, and anyone with that key can retrieve the original content.
It serves as a quick way to share logs, code snippets, configuration files, or any text-based content without needing file attachments or direct messaging.
**Popular Examples:** [pastebin.com](https://pastebin.com/), [GitHub Gist](https://gist.github.com/), [Hastebin](https://hastebin.com/)
What makes Pastebin interesting from a system design perspective is the asymmetry between writes and reads. Most users create a few pastes but share them with many people. 
A single viral paste might be viewed millions of times. This read-heavy pattern, combined with content that ranges from a few bytes to several megabytes, creates interesting design challenges.
This system design problem touches on several fundamental concepts: **unique ID generation**, **storage optimization**, **caching strategies**, and **handling content expiration**.
In this chapter, we will walk through the **high-level design of a Pastebin service**.
Let’s begin by clarifying the requirements.
# 1. Clarifying Requirements
Before starting the design, it's important to ask thoughtful questions to uncover hidden assumptions, clarify ambiguities, and define the system's scope more precisely.
Here is how a requirements discussion might unfold in an interview:
**Candidate:** "What is the expected scale? How many new pastes per day and how many reads?"
**Interviewer:** "Let's aim for 1 million new pastes per day with a 10:1 read-to-write ratio."
**Candidate:** "What is the maximum size of a single paste?"
**Interviewer:** "Let's limit each paste to 10 MB to prevent abuse, but the average paste is around 10 KB."
**Candidate:** "Should pastes support expiration?"
**Interviewer:** "Yes, users should be able to set an expiration time. Pastes without expiration should have a default expiry of 1 year."
**Candidate:** "Do we need to support different visibility levels like public, private, or unlisted?"
**Interviewer:** "Yes, support public (discoverable), unlisted (accessible via link only), and private (requires authentication)."
**Candidate:** "Do we need syntax highlighting or the ability to specify the programming language?"
**Interviewer:** "Syntax highlighting is nice-to-have. Focus on the core storage and retrieval functionality first."
**Candidate:** "Should we support editing existing pastes?"
**Interviewer:** "No, pastes are immutable once created. Users can create new versions if needed."
This conversation reveals several important constraints that will influence our design. Let's formalize these into functional and non-functional requirements.

## 1.1 Functional Requirements
Based on the discussion, here are the core features system must support:
- **Create Paste:** Users can submit text content (up to 10 MB) and receive a unique URL to access it.
- **Read Paste:** Anyone with the URL can retrieve the paste content.
- **Expiration:** Pastes can have a custom expiration time or use the default (1 year).
- **Visibility Settings:** Support public, unlisted, and private pastes.
- **Custom URLs:** Optionally allow users to choose custom aliases for their pastes, subject to availability.

## 1.2 Non-Functional Requirements
Beyond features, we need to consider the qualities that make the system production-ready:
- **High Availability:** The system must be highly available (99.99% uptime).
- **Low Latency:** Paste retrieval must be fast (p99 < 100ms).
- **Scalability:** Handle millions of reads and writes per day.
- **Durability:** Once created, pastes must not be lost until they expire.

# 2. Back-of-the-Envelope Estimation
Before diving into the design, let's run some quick calculations to understand the scale we are dealing with. These numbers will guide our architectural decisions, particularly around storage, caching, and database selection.

### 2.1 Traffic Estimates
Starting with the numbers from our requirements discussion:

##### Write Traffic (Paste Creation)
We expect 1 million new pastes per day. Let's convert this to queries per second (QPS):
Traffic is rarely uniform throughout the day. During peak hours (business hours, especially when developers are debugging production issues), we might see 3x the average load:

##### Read Traffic (Paste Retrieval)
With a 10:1 read-to-write ratio, we have about 10 million reads per day:
These numbers are modest by internet standards. A single well-configured server could handle this load, but we will design for horizontal scaling to ensure availability and handle growth.

### 2.2 Storage Estimates
Each paste consists of three components: a unique key, the content itself, and metadata. Let's break down the storage requirements:

##### Component Breakdown:
- **Paste key:** 8 alphanumeric characters = 8 bytes
- **Content:** Average 10 KB (though it can range from a few bytes to 10 MB)
- **Metadata:** User ID (36 bytes), timestamps (16 bytes), visibility flag (1 byte), title (up to 255 bytes), language hint (50 bytes), content path reference (255 bytes) = roughly 500 bytes

This gives us approximately 10.5 KB per paste on average. Now let's project storage growth over time:
| Time Period | Total Pastes | Storage Required | Notes |
| --- | --- | --- | --- |
| 1 Day | 1 million | ~10.5 GB | Easily fits in memory |
| 1 Month | 30 million | ~315 GB | Single database instance |
| 1 Year | 365 million | ~3.8 TB | May need archiving strategy |
| 5 Years | 1.8 billion | ~19 TB | Distributed storage required |

A few observations from these numbers:
1. **Storage is manageable:** Even at 5 years, 19 TB is not extreme for modern infrastructure. Object storage services like S3 handle petabytes routinely.
2. **Expiration helps:** Since pastes expire (default 1 year), we will not accumulate indefinitely. After the first year, expired pastes will be cleaned up, and storage will plateau.
3. **Content dominates:** The paste content (10 KB average) is 95% of the storage. This suggests we should optimize content storage separately from metadata.

### 2.3 Bandwidth Estimates
Bandwidth determines how much data flows through our system:
Even peak bandwidth of 3.6 MB/s is trivial for modern networks. A standard 1 Gbps network connection can handle 125 MB/s, giving us roughly 35x headroom.
However, bandwidth becomes more interesting when we consider caching. If a paste goes viral and receives 100,000 views in an hour, that is 28 QPS for a single paste. Serving this from origin would waste resources, which is why CDN caching is essential.

### 2.4 Key Insights
These estimates reveal several important design implications:
1. **Read-heavy workload:** With 10x more reads than writes, we should invest heavily in caching and optimize for fast retrieval.
2. **Modest compute requirements:** The QPS numbers are low enough that compute is not our bottleneck. Focus on storage and caching.
3. **Storage architecture matters:** Separating small pastes (inline in database) from large pastes (object storage) can optimize both cost and performance.
4. **Expiration is a feature, not just cleanup:** By removing expired content, we keep storage costs predictable and databases performant.

# 3. Core APIs
With our requirements and scale understood, let's define the API contract. Pastebin's API is straightforward, but getting the details right matters for usability and extensibility.
We will design a RESTful API with three core endpoints: create, read, and delete. Let's walk through each one.

### 3.1 Create Paste

#### Endpoint: POST /pastes
This is the primary endpoint users interact with. It accepts the text content along with optional configuration and returns a shareable URL.

##### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| content | string | Yes | The text content to store (max 10 MB) |
| title | string | No | A descriptive title for the paste |
| language | string | No | Programming language hint for syntax highlighting (e.g., "python", "java", "sql") |
| expiry_duration | string | No | How long until the paste expires. Accepts formats like "1h", "7d", "6m", "1y". Defaults to "1y" |
| visibility | enum | No | One of "public", "unlisted", or "private". Defaults to "unlisted" |
| custom_key | string | No | User-chosen key for the URL (subject to availability) |

**Example Request:**
**Success Response (201 Created):**
The response includes both the raw key and the full URL for convenience. The client can display either depending on context.

##### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Invalid input | Content is empty, exceeds 10 MB, or malformed expiry duration |
| 401 Unauthorized | Authentication required | Creating a private paste without being logged in |
| 409 Conflict | Key collision | Requested custom_key is already taken |
| 429 Too Many Requests | Rate limited | User exceeded their paste creation quota |

### 3.2 Get Paste

#### Endpoint: GET /pastes/{paste_key}
This endpoint retrieves a paste by its unique key. It is the most frequently called endpoint, so performance is critical.

##### Path Parameters:
| Parameter | Type | Description |
| --- | --- | --- |
| paste_key | string | The unique identifier for the paste (e.g., "abc12345") |

##### Success Response (200 OK):
We include `content_size` in the response so clients can display this information without computing it themselves.

##### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 404 Not Found | Paste does not exist | The key was never created or has been deleted |
| 410 Gone | Paste expired | The paste existed but has passed its expiration time |
| 403 Forbidden | Access denied | Private paste accessed by someone other than the owner |

The distinction between 404 and 410 is intentional. A 410 tells the client that the resource existed but is no longer available, which can be useful for caching and user messaging.

### 3.3 Delete Paste

#### Endpoint: DELETE /pastes/{paste_key}
Allows paste owners to remove their content before the scheduled expiration.

##### Request Headers:
| Header | Required | Description |
| --- | --- | --- |
| Authorization | Yes | Bearer token for owner authentication |

##### Success Response (200 OK):

##### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 404 Not Found | Paste does not exist | The key was never created or already deleted |
| 401 Unauthorized | Missing authentication | No authorization header provided |
| 403 Forbidden | Not the owner | Authenticated user does not own this paste |

### 3.4 API Design Considerations
A few design decisions worth noting:
**Idempotency:** The GET endpoint is naturally idempotent. For DELETE, we return success even if the paste was already deleted (idempotent behavior). This simplifies client retry logic.
**Content-Type:** We return `application/json` for metadata. For the raw content (if needed for download), we could add a separate endpoint like `GET /pastes/{paste_key}/raw` that returns `text/plain`.
**Pagination:** We have not included a "list pastes" endpoint in the core API. If needed for user dashboards, we would add `GET /users/{user_id}/pastes` with cursor-based pagination.
# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complex diagram upfront, we will build the design incrementally, starting with the simplest possible solution and adding components as we encounter challenges. This mirrors how you would approach the problem in an interview.
Our system needs to handle two fundamental operations:
1. **Paste Creation:** Accept text content and return a unique, shareable URL.
2. **Paste Retrieval:** Given a URL, return the stored content quickly and reliably.

The read-to-write ratio (10:1) tells us something important: we will have 10 times more people viewing pastes than creating them. This means our architecture should prioritize fast reads, even if it means writes are slightly slower. Caching will be our friend here.


When a user clicks "Create Paste," several things need to happen behind the scenes:
1. Accept the content and validate it (size limits, rate limits)
2. Generate a unique key that will become part of the URL
3. Store the content somewhere durable
4. Save metadata for later retrieval
5. Return the shareable URL to the user

Let's introduce the components we need to make this work.

### Components for Paste Creation

#### API Gateway
Every request enters through the API Gateway. Think of it as the front door to our system, handling concerns that are common across all requests.
The gateway terminates SSL connections, validates that requests are well-formed, enforces rate limits to prevent abuse, and routes requests to the appropriate backend service. By handling these cross-cutting concerns at the edge, we keep our application services focused on business logic.

#### Paste Service
This is the brain of our operation for paste creation. It orchestrates the entire workflow: validating input, requesting a unique key, storing content, saving metadata, and assembling the response.
We want this service to be stateless so we can run multiple instances behind a load balancer. All state lives in the database and storage layer, making horizontal scaling straightforward.

#### Key Generation Service
Generating unique, short keys is trickier than it might seem. The keys need to be:
- Short enough to share easily (8 characters is our target)
- Unique across all pastes (no collisions)
- Unpredictable (so users cannot guess other paste URLs)

We will explore key generation strategies in detail in the deep dive section, but for now, think of this as a service that hands out unique keys on demand.

#### Metadata Database
Stores everything about a paste except the actual content: the key, who created it, when it was created, when it expires, visibility settings, and a pointer to where the content lives.
We need fast lookups by key (the primary use case) and efficient queries by expiration time (for cleanup). A relational database like PostgreSQL fits well here.

#### Object Storage
The actual paste content lives in object storage (S3, Google Cloud Storage, or similar). Why separate it from the database?
- Object storage is cheaper per gigabyte
- It handles large files (up to 10 MB) without bloating the database
- Built-in durability (11 nines on S3)
- Easy integration with CDNs for caching

This separation of metadata and content is a common pattern in systems that handle user-generated content.

### The Create Flow in Action
Here is how all these components work together when a user creates a paste:
Let's walk through this step by step:
1. **Request arrives at API Gateway:** The client sends a POST request with the paste content and optional metadata. The gateway validates the request format and checks rate limits for the user's IP or account.
2. **Paste Service takes over:** Once validated, the request moves to the Paste Service. It performs business-level validation, like checking that the content is not empty and does not exceed the 10 MB limit.
3. **Key generation:** The service requests a unique key. The Key Generation Service returns something like "abc12345", guaranteed to be unique.
4. **Content storage:** The paste content is written to object storage. We use the key as part of the storage path (e.g., `s3://paste-bucket/abc12345`). This operation must succeed before we proceed.
5. **Metadata storage:** With the content safely stored, we insert a row into the metadata database containing the key, user ID, timestamps, visibility, and the path to the content in object storage.
6. **Response:** The full URL is assembled and returned to the client. The user can now share this link with anyone.

If content storage fails, we have nothing to save metadata about. If metadata storage fails after content is written, we have orphaned content (wasteful but not incorrect). A cleanup job can later find and remove orphaned objects. This ordering makes our system more resilient to partial failures.


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
        S1[intelligence Service]
        S2[storage Service]
        S3[web Service]
        S4[The Service]
        S5[application Service]
    end

    subgraph Data Storage
        DBPostgreSQL[PostgreSQL]
        DBDynamoDB[DynamoDB]
        DBCassandra[Cassandra]
    end

    subgraph Caching Layer
        CacheRedis[Redis]
    end

    subgraph Object Storage
        StorageS3[S3]
        Storageobjectstorage[object storage]
        StorageObjectstorage[Object storage]
        Storages3[s3]
        StorageObjectStorage[Object Storage]
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
    S2 --> DBPostgreSQL
    S2 --> DBDynamoDB
    S2 --> CacheRedis
    S3 --> DBPostgreSQL
    S3 --> DBDynamoDB
    S3 --> CacheRedis
    S4 --> DBPostgreSQL
    S4 --> DBDynamoDB
    S4 --> CacheRedis
    S5 --> DBPostgreSQL
    S5 --> DBDynamoDB
    S5 --> CacheRedis
    S1 --> StorageS3
    S1 --> Storageobjectstorage
    S1 --> StorageObjectstorage
    S1 --> Storages3
    S1 --> StorageObjectStorage
    StorageS3 --> CDNNode
    Storageobjectstorage --> CDNNode
    StorageObjectstorage --> CDNNode
    Storages3 --> CDNNode
    StorageObjectStorage --> CDNNode
    CDNNode --> Web
    CDNNode --> Mobile



## 4.2 Requirement 2: Paste Retrieval
Now for the more interesting path, the read path. This is where our 10:1 read-to-write ratio means we need to be clever about performance.
When someone clicks a paste link, we need to:
1. Look up the paste key
2. Check if the paste exists and has not expired
3. Verify the user has permission to view it (for private pastes)
4. Return the content as quickly as possible

The naive approach would be to hit the database for every request. But with 115 QPS on average (and potentially much higher for viral pastes), we want most requests to be served without touching the database at all. This is where caching comes in.

### Additional Components for Reading

#### CDN (Content Delivery Network)
A CDN is a network of servers distributed around the world. When a user in Tokyo requests a paste, instead of traveling all the way to our origin server in Virginia, the request goes to a nearby CDN edge node.
For public and unlisted pastes (which do not require authentication), the CDN can cache the entire response. A popular paste might be served directly from edge nodes thousands of times before the CDN needs to check with our origin server again.
The CDN also protects our origin from traffic spikes. If a paste suddenly goes viral on social media, the CDN absorbs most of the load.

#### Redis Cache
For requests that miss the CDN (either because the cache expired, the paste is private, or the user is in a region without nearby edge nodes), we have a second layer of caching using Redis.
Redis is an in-memory data store with sub-millisecond latency. We use it to cache paste content and metadata so that even cache misses at the CDN can be served quickly without hitting the database.
The cache key is simply the paste key, and the value contains both metadata and content (for small pastes) or metadata with a flag indicating the content is in object storage.

### The Read Flow in Action
Let's trace through the different scenarios:

#### Best case: CDN hit
The request hits a CDN edge node that has the paste cached. Response time is typically under 50ms, often under 20ms. The user gets their content almost instantly, and our origin servers never see the request. This should be the common case for popular, public pastes.

#### Second best: Redis hit
The CDN cache has expired or this is the first request from a particular region. The request reaches our origin, but the Paste Service finds the content in Redis. Response time is typically 50-100ms. We still avoid the database.

#### Cache miss: Full round trip
Neither cache has the content. We query the metadata database to get paste information, check that it has not expired and the user has permission, then fetch the content from object storage (if it is too large to be stored inline in the database). We populate the Redis cache before returning so subsequent requests are faster.

### Cache Headers and TTLs
Getting cache behavior right requires careful thought about TTLs (time-to-live):
**CDN cache:** We set `Cache-Control: public, max-age=3600` for public and unlisted pastes, allowing caching for up to 1 hour. Private pastes get `Cache-Control: private, no-cache` since they require authentication.
**Redis cache:** We cache for longer (up to 24 hours) but always check expiration in our application logic before serving. The TTL is set to the minimum of 24 hours or the paste's remaining lifetime.
**What about paste expiration?** A paste might expire while cached. That's fine since we always check the expiration timestamp before serving content. If a cached paste has expired, we return 410 Gone and remove it from the cache.

## 4.3 Putting It All Together
Now that we have designed both the write and read paths, let's step back and see the complete architecture. We have also added one more component that we have not discussed yet: the Cleanup Service for handling expired pastes.
The architecture follows a layered approach, with each layer having a specific responsibility:
**Client Layer:** Users interact with our system through web browsers, mobile apps, or programmatic API clients. From our perspective, they all look the same, just HTTP requests.
**Edge Layer:** The CDN sits at the edge, close to users geographically. It caches responses and protects our origin from traffic spikes.
**Gateway Layer:** The API gateway handles authentication, rate limiting, and request validation before passing requests to the application layer.
**Application Layer:** The Paste Service contains our core business logic. It is stateless and horizontally scalable. The Key Generation Service is a specialized component for generating unique keys.
**Cache Layer:** Redis provides low-latency access to frequently requested pastes, reducing load on the database and object storage.
**Storage Layer:** PostgreSQL stores metadata with proper indexing. Object storage holds the actual paste content, separated for cost and performance optimization.
**Background Workers:** The Cleanup Service runs periodically to remove expired pastes, reclaiming storage and keeping the database clean.
This architecture handles our requirements well: the CDN and Redis cache absorb most read traffic, the stateless Paste Service scales horizontally for writes, and the storage layer provides durability without breaking the bank.
# 5. Database Design
With the high-level architecture in place, let's zoom into the data layer. Choosing the right database and designing an efficient schema are critical decisions that affect performance, scalability, and operational complexity.

## 5.1 SQL vs NoSQL
The database choice is not always obvious. Let's think through our access patterns and requirements:
**What we need to store:**
- Hundreds of millions of paste records over the system's lifetime
- Each record has metadata (key, user, timestamps, visibility) and content (a few bytes to 10 MB)

**How we access the data:**
- Most reads are point lookups by paste_key (the primary use case)
- We need to list pastes by user_id for user dashboards
- We need to query by expiry_date for cleanup jobs
- We need to filter by visibility for public paste listings

**Consistency requirements:**
- Users should see their paste immediately after creation (strong consistency for writes)
- Slightly stale reads are acceptable for listing queries

Given these requirements, we have a choice to make for both metadata and content storage.

#### Metadata: PostgreSQL
For metadata, a relational database like PostgreSQL is a good fit.
PostgreSQL gives us:
- **Indexes on multiple fields:** We can efficiently query by paste_key, user_id, or expiry_date
- **Strong consistency:** Users see their paste immediately after creation
- **Mature operations tooling:** Backups, replication, monitoring are well-understood
- **Flexible schema:** Easy to add new fields as requirements evolve

Could we use a NoSQL database like DynamoDB or Cassandra? Yes, but the benefits (extreme scale, eventual consistency) don't match our needs. Our query patterns are varied enough that a relational database is simpler to work with.

#### Content: Object Storage
For the actual paste content, object storage (S3, GCS, Azure Blob) is the clear winner:
- **Cost:** Object storage costs around $0.02/GB/month, compared to $0.10-0.20/GB for database storage
- **Size handling:** Databases struggle with rows containing megabytes of data. Object storage is designed for it
- **Durability:** S3 offers 99.999999999% (11 nines) durability
- **CDN integration:** Object storage integrates seamlessly with CDNs for edge caching

The key insight is that paste content is opaque to our database, just a blob of text. We do not need to query it, join it with other tables, or update parts of it. Object storage is perfect for this use case.

### The Hybrid Approach
We use both: PostgreSQL for metadata and object storage for content. This separation is a common pattern in systems that handle user-generated content.

## 5.2 Database Schema
With our database choices made, let's design the schema. We have two main tables: Users and Pastes.

#### 1. Pastes Table
This is the heart of our schema. Each row represents one paste.
| Field | Type | Description |
| --- | --- | --- |
| paste_key | VARCHAR(16) | Primary key. The unique 8-character key that appears in URLs |
| user_id | UUID | Foreign key to Users table. Nullable for anonymous pastes |
| title | VARCHAR(255) | Optional human-readable title |
| language | VARCHAR(50) | Language hint for syntax highlighting (e.g., "python", "javascript") |
| content_path | VARCHAR(255) | Path to content in object storage (e.g., "s3://bucket/abc12345") |
| content_size | INTEGER | Size of content in bytes. Used for display and validation |
| content_inline | TEXT | For small pastes (< 64 KB), we store content inline to avoid an extra hop |
| visibility | ENUM | One of 'public', 'unlisted', 'private' |
| created_at | TIMESTAMP | When the paste was created (with timezone) |
| expires_at | TIMESTAMP | When the paste expires (with timezone) |

This is an optimization. Small pastes (the majority) are stored inline in the database, requiring only one read operation. Large pastes are stored in object storage, referenced by content_path. The application logic checks which field is populated and retrieves content accordingly.
**Indexes:**
- Primary Key: `paste_key`
- Index on `user_id` for listing user's pastes
- Index on `expires_at` for cleanup queries
- Index on `visibility, created_at` for public paste listings

#### 2. Users Table
Stores account information for registered users.
| Field | Type | Description |
| --- | --- | --- |
| user_id | VARCHAR(36) (PK) | Unique identifier for the user |
| email | VARCHAR(255) | User's email address |
| username | VARCHAR(50) | Display name |
| password_hash | VARCHAR(255) | Hashed password |
| created_at | TIMESTAMP | Account creation time |

This is a minimal user table. A production system would likely include email verification status, subscription tier for rate limits, and other account-related fields.
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often go deeper into specific components. 
In this section, we will explore the trickiest parts of our design: generating unique keys, storing content efficiently, caching for performance, handling expiration, preventing abuse, and scaling the system.

## 6.1 Unique Key Generation
Every paste needs a unique key that becomes part of its URL. This sounds simple, but generating good keys at scale is surprisingly nuanced. Let's think about what "good" means here:
- **Unique:** No two pastes can share the same key, ever
- **Short:** Users share these URLs, so shorter is better (8 characters is our target)
- **Unpredictable:** Users should not be able to guess other paste URLs by incrementing a counter
- **Scalable:** Key generation should not become a bottleneck as we add more servers

There are several approaches to this problem, each with different trade-offs. Let's explore three common strategies.

### Approach 1: Random Key Generation
The simplest approach is to generate a random string for each paste and check if it already exists.

#### How It Works
We generate an 8-character string using Base62 encoding (lowercase a-z, uppercase A-Z, and digits 0-9). Before using it, we check the database to ensure no paste already has this key. If there is a collision, we generate a new random string and try again.
It gives us 62 possible characters per position. With 8 characters, we have 62^8 = 218 trillion possible combinations. At 1 million new pastes per day, it would take over 600,000 years to exhaust this key space. Collisions are theoretically possible but vanishingly rare.

#### Pros:
- Simple to implement using standard libraries
- Keys are unpredictable, so users cannot enumerate other pastes
- No coordination needed between servers, each generates independently

#### Cons:
- Requires a database lookup for every paste creation (to check for collisions)
- Needs retry logic for the rare collision case
- As the database grows, collision probability increases (though it remains very low)

### Approach 2: Pre-Generated Key Pool
Instead of generating keys on-demand and hoping for no collisions, we can generate them in advance and store them in a pool. When a paste is created, we simply grab an unused key from the pool.

#### How It Works
A background service (the Key Generation Service) pre-generates millions of unique keys and stores them in a dedicated database table. Each key has a flag indicating whether it has been used. 
When a paste is created, we fetch an unused key using an atomic database operation that also marks it as used in the same transaction.
**Keys Table Schema:**
The background service monitors the pool size and generates more keys when inventory drops below a threshold, say 1 million unused keys.
**Pros:**
- Guaranteed uniqueness without collision checking
- Fast and predictable, just a database fetch with no retry logic
- Decouples key generation from paste creation

**Cons:**
- Additional infrastructure to maintain (the key pool and generation service)
- Storage overhead for unused keys (though minimal, about 8 bytes per key)
- Need to handle concurrency carefully when multiple servers fetch keys

#### Handling Concurrency
Multiple Paste Service instances will be trying to grab keys simultaneously. We need to prevent two instances from getting the same key. There are several approaches:
**1. Atomic UPDATE:** Use a single SQL statement that selects and updates atomically:
**2. Batch allocation:** Each server fetches a batch of keys (say, 1000) into memory. This reduces database contention and is faster for high-throughput scenarios.
**3. Server-specific ranges:** Assign different key prefixes to different servers. Server 1 generates keys starting with "a", Server 2 with "b", and so on. This eliminates contention entirely.

### Approach 3: Distributed ID Generation (Snowflake-like)
For very large scale systems, we can use a distributed ID generator similar to Twitter's Snowflake. This approach generates unique IDs without any coordination between servers.

#### How It Works
Each ID is a 64-bit integer assembled from three components:
- **Timestamp (41 bits):** Milliseconds since a custom epoch. 41 bits gives us about 69 years of timestamps.
- **Worker ID (10 bits):** A unique identifier for each server. Supports up to 1,024 different servers.
- **Sequence (12 bits):** A counter that increments within the same millisecond. Allows 4,096 IDs per millisecond per server.

Each server can generate 4,096 unique IDs per millisecond independently, without checking a database or coordinating with other servers. The 64-bit integer is then Base62 encoded to create a URL-friendly string (about 11 characters).

#### Pros:
- Globally unique without any coordination or database lookups
- Roughly time-sortable, which can be useful for debugging
- Massive throughput: 4 million+ IDs per second per server

#### Cons:
- Clock drift can cause issues (servers must use NTP for synchronized time)
- Slightly longer keys (11 characters vs 8)
- Requires assigning and managing worker IDs, which adds operational complexity

### Which Approach Should You Choose?
Each strategy has its sweet spot. Here is how they compare:
| Strategy | Uniqueness | Throughput | Operational Complexity | Key Length |
| --- | --- | --- | --- | --- |
| Random Keys | Check on each creation | Low-medium | Simple | 8 chars |
| Key Pool | Guaranteed | High | Medium | 8 chars |
| Snowflake | Guaranteed | Very high | Higher | 11 chars |

#### Recommendation:
For a Pastebin-scale system (millions of pastes per day), the **Pre-Generated Key Pool** offers the best trade-off. It gives us guaranteed uniqueness, short keys, and good performance without the complexity of distributed clock synchronization.
If we were building something at Twitter or Discord scale with billions of operations per day, Snowflake would be worth the added complexity. For most applications, the key pool is the right choice.

## 6.2 Content Storage Strategy
Paste content is highly variable. Most pastes are tiny, just a few lines of code. But users can also upload log files or data dumps that approach our 10 MB limit.
How do we handle this variability efficiently?

### The Problem with Storing Everything in the Database
The naive approach is to store all content in a TEXT column in PostgreSQL. This works, but creates several issues at scale:
- **Database bloat:** Large pastes inflate the database size, making backups slower and more expensive
- **Query performance:** Reading and writing large rows ties up database connections longer
- **Cost:** Database storage is 5-10x more expensive than object storage
- **Memory pressure:** Large rows can cause issues with PostgreSQL's shared buffers

We need a smarter approach that handles the common case (small pastes) efficiently while not breaking for large pastes.

### The Hybrid Storage Approach
The solution is to store content differently based on size:
This is a pragmatic choice. Below 64 KB, the overhead of a second network call to S3 is not worth it. Above 64 KB, the database bloat and connection holding time become noticeable. The exact threshold can be tuned based on your workload.

### Small Pastes: Inline Storage
For pastes under 64 KB (which is roughly 95% of all pastes based on typical usage patterns), we store the content directly in the database alongside the metadata.
**Benefits:**
- Single read operation: metadata and content in one query
- Lowest possible latency since everything is in the database
- Simpler code path for the common case

### Large Pastes: Object Storage
For the remaining 5% of pastes that exceed 64 KB, we store the content in object storage (S3, GCS, or Azure Blob) and keep only a reference in the database.
**Benefits:**
- Cost-effective: object storage costs pennies per GB
- Unlimited scale: object stores are designed for massive files
- Built-in durability: S3 offers 11 nines of durability
- CDN integration: direct serving from S3/CloudFront is possible

#### Implementation Details
Our pastes table has two content-related columns:
The read logic is straightforward:
For writes, the logic decides based on content size:

### Compression for Large Content
Text compresses well. A 1 MB log file might compress to 200 KB with GZIP, saving both storage costs and transfer time.
| Algorithm | Compression Ratio | CPU Cost | Best For |
| --- | --- | --- | --- |
| GZIP | 60-80% reduction | Moderate | Storage optimization |
| LZ4 | 40-60% reduction | Very low | Speed-sensitive reads |
| Zstandard | 70-85% reduction | Moderate | Best of both worlds |

We compress content before storing in object storage and decompress on read. The content_path includes a flag indicating the compression algorithm used (or "none").
For inline content in the database, we typically skip compression since the overhead is not worth it for small content and PostgreSQL's TOAST mechanism handles large values automatically.

## 6.3 Caching Strategy
With 10 reads for every write, caching is not optional. It is essential. A well-designed caching strategy can serve 90%+ of requests without touching the database, dramatically reducing latency and infrastructure costs.
Let's think about caching in layers, from the edge (closest to users) to the origin (our database).
Each layer catches a portion of requests, so only a small percentage reach the database. Here is how they work together:
| Layer | Latency | Expected Hit Rate | Serves |
| --- | --- | --- | --- |
| CDN Edge | 10-50ms | 70-80% | Public/unlisted pastes in hot regions |
| Redis | ~1ms | 15-20% | Private pastes, cache misses at edge |
| Database | ~20ms | 5-10% | Cold pastes, first access |

### Layer 1: CDN (Content Delivery Network)
The CDN is our first line of defense. When a paste is requested, the CDN checks if it has a cached copy at the edge location closest to the user. If it does, the response is served without ever reaching our origin servers.

#### What gets cached at the CDN?
Public and unlisted pastes can be cached because they do not require authentication. We set appropriate HTTP headers:
Private pastes get different headers that prevent CDN caching:

#### Why the CDN matters:
A user in Singapore requesting a paste gets their response from a Singapore edge node in ~20ms instead of waiting ~200ms for a round trip to our Virginia data center. For popular pastes, this also means our origin sees a fraction of the actual traffic.

### Layer 2: Redis Application Cache
For requests that miss the CDN (private pastes, cold content, or first requests after cache expiry), we check Redis before hitting the database.
Redis sits in our data center, providing sub-millisecond latency. We cache the complete paste response, including metadata and content (for small pastes).

#### Why set a maximum TTL of 24 hours?
Even if a paste does not expire for a year, we do not want to cache it forever. Fresh data from the database ensures we catch any edge cases where cache and database diverge. The 24-hour window is a reasonable balance.

#### Redis Cluster for scale:
As traffic grows, a single Redis instance may not be enough. We can shard across multiple Redis nodes using consistent hashing on the paste key. This distributes both memory and query load.

### Layer 3: Database
The database is our source of truth. When both cache layers miss, we query PostgreSQL. For inline content, we get everything in one query. For large content stored in S3, we need a second fetch.
PostgreSQL also has its own buffer cache (shared_buffers) that keeps frequently accessed pages in memory. This provides an additional layer of caching at the database level.

### Cache Invalidation
Here is where Pastebin has a nice advantage: **pastes are immutable**. Once created, the content never changes. This makes cache invalidation trivial:
1. **On paste creation:** No cache to invalidate since the key is new
2. **On paste deletion:** Remove from Redis and issue a CDN purge request
3. **On paste expiration:** TTL-based eviction handles this automatically

The only tricky case is deletion. We need to actively remove the paste from Redis and tell the CDN to purge it. Most CDN providers offer purge APIs, though they may take a few seconds to propagate globally.

### Cache Warming
For newly created pastes that we expect to be accessed immediately (the user is about to share the link), we can proactively populate the Redis cache right after creation. This ensures the first request is fast.
This adds a small amount of latency to the create operation but provides a better experience for the first viewer.

## 6.4 Handling Paste Expiration
Expiration is a core feature of Pastebin. When a paste expires, two things need to happen:
1. The paste must become inaccessible immediately (users get a "gone" error)
2. The storage must eventually be reclaimed (cleanup)

These are two separate concerns with different timing requirements. Let's look at each.

### Real-Time Expiration Enforcement
When a user requests a paste, we must check if it has expired before serving content. This check happens on every request, regardless of whether the data comes from cache or database.
The check is simple: compare the `expires_at` timestamp with the current time. If expired, return HTTP 410 (Gone) instead of the content.
We cannot rely solely on cache TTLs or background cleanup jobs. A paste might be cached with a 1-hour TTL but expire in 30 minutes. Or the cleanup job might not have run yet. The only way to guarantee correct behavior is to check on every read.
This adds negligible overhead since we already have the metadata loaded (either from cache or database).

### Background Cleanup
Expired pastes need to be removed to reclaim storage. This is not urgent, it just needs to happen eventually. A background job handles this.

#### The cleanup process:
For each batch:
1. Delete content from S3 (if content_path is not null)
2. Delete the row from PostgreSQL
3. Remove from Redis cache (in case it is still cached)
4. Repeat until no more expired pastes

Deleting millions of rows in a single transaction would lock the database and impact live traffic. Processing in batches of 1,000 keeps each transaction small and allows the database to handle regular queries between batches.
**Soft deletes for safety:**
Instead of immediately deleting rows, consider setting a `deleted_at` timestamp first:
A second job hard-deletes rows where `deleted_at` is more than 7 days old. This provides a recovery window if something goes wrong.

### Cache TTL Alignment
When caching a paste, we need to ensure the cache entry expires before or with the paste itself. Otherwise, we could serve expired content from cache.
This way, the cache entry expires at the same time as the paste, and subsequent requests hit the origin where they get the proper 410 response.

## 6.5 Rate Limiting and Abuse Prevention
Pastebin services are attractive targets for abuse. Spammers use them to host phishing links. Malware authors distribute payloads. Bots create thousands of pastes for SEO manipulation. 
Without proper safeguards, our service could quickly become unusable or, worse, a vector for harm.
Let's look at the defenses we need.

### Rate Limiting
Rate limiting controls how many requests a user can make in a given time window. Different user types get different limits based on their trust level.
| User Type | Paste Creation | Paste Reading | Identifier |
| --- | --- | --- | --- |
| Anonymous | 10/hour | 100/hour | IP address |
| Registered | 100/hour | 1,000/hour | User ID |
| Premium | 1,000/hour | Unlimited | User ID |

Creating pastes consumes storage and requires write operations. Reading is much cheaper, especially when served from cache. We can afford to be more generous with read limits.

#### Implementation with Redis:
We use Redis to track request counts using a sliding window algorithm. For each user and action type, we maintain a counter:
When a request comes in:
1. Increment the counter
2. If the count exceeds the limit, reject with HTTP 429 (Too Many Requests)
3. Include `Retry-After` header to tell the client when they can try again

### Content Moderation
Rate limiting stops volume-based abuse, but we also need to catch malicious content.

#### Automated Checks (on paste creation):
- **Size validation:** Reject content over 10 MB
- **Spam detection:** Check against known spam patterns and URLs
- **Malware scanning:** For binary content or suspicious scripts
- **Link analysis:** Flag pastes with known phishing domains

#### User Reporting:
Automated systems miss things. We need a way for users to flag problematic content:
- "Report" button on paste pages
- Reports go to a moderation queue
- Repeated violations lead to account suspension
- Legal takedown requests (DMCA, etc.) get priority handling

### Bot Prevention
Anonymous paste creation is a prime target for bots. We use CAPTCHA to verify that the request is from a human.

#### When to require CAPTCHA:
- All anonymous paste creations
- After hitting 50% of the rate limit
- When request patterns look automated (same content, rapid succession)
- From IP addresses with poor reputation

Modern CAPTCHA services like reCAPTCHA v3 or Cloudflare Turnstile can provide invisible protection for most users while only challenging suspicious traffic.

### IP Reputation
Some IP addresses are known bad actors. We can use threat intelligence services to check:
- Is this IP from a known hosting provider often used for abuse?
- Has this IP been reported for spam recently?
- Is this IP part of a botnet?

High-risk IPs get stricter rate limits and more aggressive CAPTCHA challenges.

## 6.6 Scaling the System
Our initial design handles the expected load of 1 million pastes per day. But what happens when the service grows 10x or 100x? Let's think through how each component scales.

### Scaling the Application Layer
The Paste Service is stateless, meaning any instance can handle any request. This makes horizontal scaling straightforward.

#### How to scale:
- Add more Paste Service instances behind the load balancer
- Use auto-scaling based on CPU utilization (target ~70%) or request queue depth
- Each new instance adds capacity linearly

#### When to scale:
- CPU utilization consistently above 70%
- Response latency increasing beyond acceptable thresholds
- Request queue building up

### Scaling the Database
The database is often the first bottleneck in read-heavy systems. We address this in stages.

#### Stage 1: Read Replicas
Most of our queries are reads (fetching pastes). We can offload these to read replicas while the primary handles writes.
Reads can tolerate slight staleness (replication lag is usually under 100ms), so eventual consistency is acceptable here. This scales read capacity linearly with the number of replicas.

#### Stage 2: Sharding (if needed)
If write volume becomes a bottleneck (unlikely for Pastebin at most scales), we can shard the database by paste_key.
- Use consistent hashing to map keys to shards
- Each shard handles a subset of the key space
- Adds complexity but enables horizontal write scaling

For our expected scale of 1 million pastes/day, a single primary with replicas should be sufficient for years.

### Scaling the Cache Layer
Redis can be scaled in two ways:
**Vertical scaling:** Use larger instances with more memory. Simple but has limits.
**Horizontal scaling:** Deploy Redis Cluster, which automatically partitions data across nodes.
Redis Cluster uses hash slots to distribute keys. Adding nodes rebalances the data automatically. The cluster also handles failover if a node goes down.

### Managed Services Handle Their Own Scaling
Some components in our architecture scale automatically:
| Component | Scaling Approach | Our Responsibility |
| --- | --- | --- |
| Object Storage (S3/GCS) | Fully managed, infinite scale | Pay for what we use |
| CDN (CloudFront/Fastly) | Global edge network, auto-scales | Configure cache policies |
| Load Balancer (ALB/NLB) | Managed, scales with traffic | Monitor and adjust limits |

The key insight is that most scaling is straightforward when you design stateless services and use managed storage. The database is usually the limiting factor, but read replicas handle read-heavy workloads well.
# References
- [AWS S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html) - Performance optimization and design patterns for object storage
- [Twitter Snowflake](https://blog.twitter.com/engineering/en_us/a/2010/announcing-snowflake) - The original post on Twitter's distributed ID generation system
- [Rate Limiting Strategies](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/) - Cloudflare's deep dive into counting and rate limiting at scale
- [PostgreSQL Replication](https://www.postgresql.org/docs/current/high-availability.html) - Official documentation on PostgreSQL's replication and high availability features

# Quiz

## Design Pastebin Quiz
In a Pastebin-like service, what is the primary reason to use a short unique key in the URL instead of a sequential numeric ID?