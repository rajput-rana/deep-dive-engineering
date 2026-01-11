# Design Instagram

## What is Instagram?

[Instagram](https://www.instagram.com/) is a social media platform focused on sharing photos and short videos. Users can upload media, apply filters, add captions, follow other users, and engage through likes, comments, and direct messages.
Over time, it has expanded to include features such as stories, reels, live streaming, and recommendations.
In this chapter, we will walk through the **high-level design of a photo-sharing platform like Instagram.**
While Instagram supports a wide range of features including direct messaging, Reels, and Stories, this article will primarily focus on **the core functionality of photo and video sharing**.
Let’s start by clarifying the requirements.
# 1. Requirement Clarification
Before diving into the design, lets outline the functional and non-functional requirements.

### Functional Requirements
1. Users can **upload** photos and videos.
2. Users can add **captions** to their posts.
3. Users can **follow/unfollow** other users.
4. Users can **like**, **share**, and **comment** on posts.
5. Support for multiple images/videos in a single post (carousel).
6. Users can view a **personalized** **feed** consisting of posts from accounts they follow.
7. Users can **search** by username and hashtag.

#### Out of Scope
1. Direct messaging.
2. Short-form video content (Reels).
3. Push Notifications for likes, comments, and follows.

### Non Functional Requirements
1. **Low Latency: **The feed should load fast (~100ms).
2. **High Availability: **The system should be available 24/7 with minimal downtime.
3. **Eventual Consistency: **A slight delay in users seeing the latest posts from accounts they follow is acceptable.
4. **High Scalability: **Handle millions of concurrent users and billions of posts.
5. **High Durability: **The uploaded photos/videos shouldn’t be lost.

# 2. Capacity Estimation

### User Base
- **Total Monthly Active Users (MAUs):** 2 billion
- **Daily Active Users (DAUs):** → **500 million users/day**

### Estimating Read & Write Requests

#### Post Uploads (Writes)
- 100M media uploads/day
- Each upload generates metadata writes (DB + cache)
- **Total write requests:** 100M uploads + 100M metadata writes = 200M writes/day

#### Feed Reads
- Assume an average user scrolls through 100 posts per session
- 500 million DAUs × 100 posts viewed = 50B feed requests/day
- Assuming 80% of feed reads are served from cache, backend reads = 10B DB reads/day

### Estimating Storage Requirements

#### Assumptions
- 20% of DAUs (100M) upload media every day
- 80% of uploads are photos, 20% are videos
- **Average photo size:** 1MB
- **Average video size:** 10 MB

#### Daily Storage Calculation
- **Photos:** (100M × 80%) × 1 MB = 80 TB/day
- **Videos:** (100M × 20%) × 10 MB = 200 TB/day
- **Total storage per day:** 280 TB/day

#### Database Storage
- **Metadata per post:** ~500 bytes (caption, timestamp, author, engagement counts)
- **Total posts in a year:** 100M × 365 = 36B posts
- **Metadata storage per year:** 90 TB/year

#### Caching Requirements
- **Hot cache size:** Store recent & popular 1 billion posts
- Assume each cached post takes 2 KB (post data + engagement counts)
- Cache size = 2 TB for active posts (Redis/Memcached)

# 3. High Level Design

### Components:

#### 1. Clients (Web, Mobile)
- Users interact with the platform via web browsers or mobile apps.
- The client applications handle video playback, user interactions (likes, comments), and UI rendering.
- They communicate with backend services through an **API Gateway** or **Load Balancer**.

#### 2. Load Balancer / API Gateway
- Acts as the single entry point for all client requests.
- Distributes incoming traffic across multiple service instances to ensure **high availability** and **scalability**.
- Enforces **rate limiting**, **authentication**, and **authorization** before forwarding requests to downstream services.

#### 3. User Service
- Stores and manages **user authentication, profile data, and social connections** (follow/unfollow).

#### 4. Post Service
- Handles **photo/video uploads** and stores metadata (caption, user info, timestamps).
- Coordinates the upload of media files from users device to **Object Storage (e.g., AWS S3)** and updates metadata in a **database**.
- Uses a message queue (e.g., **Kafka) to notify the Feed Service** when a new post is created.

#### 5. Feed Service
- Precomputes and stores user feeds in a high-performance cache (e.g., Redis, Memcached) to enable fast retrieval.
- Queries the database if a feed is not cached.

#### 6. Engagement Service
- Manages **likes, comments, and shares**.
- Writes engagement data to a high-throughput database asynchronously via a message queue.

#### 7. Search Service
- Allows users to search for other users, hashtags, and posts.
- Uses **Elasticsearch** to index and retrieve data quickly.
- Supports **autocomplete and full-text search** for improved user experience.

#### 8. Message Queue
- Decouples services and ensures event-driven processing.
- Notifies the** Feed Service** of new posts.
- Updates engagement data asynchronously.

#### 9. Object Storage & CDN
- Photos/videos are stored in a distributed object Storage (S3, Google Cloud Storage).
- A **CDN (Cloudflare, AWS CloudFront)** ensures fast delivery globally.

# 4. Database Design
A large-scale content platform like Instagram requires handling both **structured data** (e.g., user accounts, post metadata) and **unstructured/semistructured data** (e.g., photos, videos, search indexes).
Typically, you’ll combine multiple database solutions to handle different workloads.
Given the requirements, we will use a **relational database (e.g., PostgreSQL, MySQL)** for structured data and a **NoSQL database (Cassandra, DynamoDB, or Elasticsearch)** for feed storage and search indexing.


``
```m# 4.1 Relational Database for Structured Data
Given the structured nature of user profiles and posts metadata, a relational database (like **PostgreSQL** or **MySQL**) is often well-suited.
- **Users Table: **Stores user account details.
- **Posts Table: **Stores metadata related to posts.
- **Media Table: **Stores photo/video metadata, but not the actual files.
- **Comments Table: **Stores post comments.
- **Shares Table: **Stores post shares.
- **Followers Table: **Maintains the follow/unfollow relationship. Stores engagement score from followers to help with ranking posts in the feed.
    CDNNode --> Mobile
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
        S1[Decouples Service]
        S2[Feed Service]
        S3[independent Service]
        S4[backend Service]
        S5[Search Service]
    end

    subgraph Data Storage
        DBCassandra[Cassandra]
        DBPostgreSQL[PostgreSQL]
        DBMySQL[MySQL]
    end

    subgraph Caching Layer
        CacheRedis[Redis]
        CacheMemcached[Memcached]
    end

    subgraph Message Queue
        QueueKafka[Kafka]
        QueueRabbitMQ[RabbitMQ]
    end

    subgraph Object Storage
        StorageObjectStorage[Object Storage]
        StorageS3[S3]
        StorageobjectStorage[object Storage]
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
    S1 --> CacheMemcached
    S1 --> QueueKafka
    S1 --> QueueRabbitMQ
    S2 --> DBCassandra
    S2 --> DBPostgreSQL
    S2 --> CacheRedis
    S2 --> CacheMemcached
    S2 --> QueueKafka
    S2 --> QueueRabbitMQ
    S3 --> DBCassandra
    S3 --> DBPostgreSQL
    S3 --> CacheRedis
    S3 --> CacheMemcached
    S3 --> QueueKafka
    S3 --> QueueRabbitMQ
    S4 --> DBCassandra
    S4 --> DBPostgreSQL
    S4 --> CacheRedis
    S4 --> CacheMemcached
    S4 --> QueueKafka
    S4 --> QueueRabbitMQ
    S5 --> DBCassandra
    S5 --> DBPostgreSQL
    S5 --> CacheRedis
    S5 --> CacheMemcached
    S5 --> QueueKafka
    S5 --> QueueRabbitMQ
    S1 --> StorageObjectStorage
    S1 --> StorageS3
    S1 --> StorageobjectStorage
    S1 --> Storageobjectstorage
    StorageObjectStorage --> CDNNode
    StorageS3 --> CDNNode
    StorageobjectStorage --> CDNNode
    Storageobjectstorage --> CDNNode
    CDNNode --> Web
    CDNNode --> Mobile



## 4.2 NoSQL Databases for High-Volume Data
While relational databases are ideal for structured data, they struggle with high-velocity writes and large scale distributed workloads. NoSQL databases like **Cassandra, DynamoDB, or Redis** provide horizontal scalability and high availability.
To reduce **feed generation latency**, a **denormalized feed table** stores precomputed timelines:
- Updated **asynchronously** via **Kafka** when a user posts.
- Cached **in Redis for quick retrieval**.

#### Using Graph Databases for Social Connections
To support complex relationship queries, such as mutual friends, suggested followers, and influencer ranking, we can use a **graph database** like Neo4j or Amazon Neptune.
They efficiently model follower-following relationships with nodes and edges.
**Example Query: "People You May Know"**
This allows **real-time friend suggestions** without complex SQL joins.

## 4.3 Search Indexes
To support fast and scalable search queries, we can leverage **Elasticsearch**, a distributed, real-time search engine optimized for full-text searches.
Each user profile and post metadata can be stored as a document in an Elasticsearch index, allowing quick lookups and advanced filtering.
**Example: Storing User Data in Elasticsearch**
To support trending hashtags and keyword searches, we can store **hashtags** in a separate Elasticsearch index.
**Example:**

## 4.4 Media Storage
Instagram handles **petabytes of photos/videos**, requiring a **durable and low-latency storage solution**.
A **distributed object storage system**, such as **Amazon S3**, is well-suited for storing media files. It supports **pre-signed URLs**, enabling users to upload media directly without routing through application servers, reducing load and latency.
To ensure **high durability**, media files are stored in multiple replicas across different data centers, protecting against data loss.
To further optimize read latency, content can be cached closer to users using a **Content Delivery Network (CDN)** like **Cloudflare or Amazon CloudFront**. This reduces load times and improves the user experience, especially for frequently accessed media.
# 5. API Design

### 5.1 Get User Profile
**Response:**

### 5.2 Follow a User

### 5.3 Create a New Post
**Form Data:**
**Response:**

### 5.4 Get a Post by ID
**Response:**

### 5.5 Get User Feed
**Response:**

### 5.6 Like a Post

### 5.7 Comment on a Post

### 5.8 Get Comments for a Post
**Response:**

### 5.9 Search Users
**Response:**
# 6. Design Deep Dive

## 6.1 Photo/Video Upload
1. **User Initiates the Upload**
2. **API Gateway Handles the Request**
3. **Post Service Generates a Pre-signed URL**
4. **Client Uploads Media to Object Storage**
5. **Post Service Saves Metadata in the Database**
6. **Kafka Publishes a "New Post" Event**

## 6.2 Newsfeed Generation
Since users follow both normal users and celebrities, the system must mix posts efficiently.

### Fan-out-on-write (Push Model) for Normal Users
For **normal users** with a manageable number of followers, we use **fan-out-on-write**, meaning posts are **pushed** to followers’ feeds at the time of posting.

#### How It Works
1. User A posts a new photo/video.
2. The Post Service sends an event to Kafka, notifying the Feed Service.
3. The Feed Service identifies the users followers (e.g., 500 followers).
4. The post is immediately inserted into each follower’s timeline, stored in Redis (hot cache).
5. When followers open their feeds, posts are instantly available, ensuring low-latency reads.

**Example: LPUSH - Add Post to Followers’ Feeds**
- User `12345` (John Doe) posts a new photo
- He has 500 followers
- The Feed Service pushes this post to all 500 followers' feeds

Here, John's post is pushed to the feeds of followers `56789`, `67890`, and `78901`, along with 497 other followers.
**Example: Fetching a User’s Feed (LRANGE - Get Recent Posts)**
**Benefits**:
- Super-fast reads since followers' feeds are pre-loaded.
- Works efficiently for small and medium-sized accounts.

**Challenges**:
- Becomes inefficient for users with millions of followers (e.g., celebrities).
- Writing a post requires copying it to potentially millions of timelines, leading to high write amplification.

### Fan-out-on-read (Pull Model) for Celebrities
For **celebrities and influencers**, where a single post may need to reach **millions of followers**, preloading into every follower’s feed is impractical.
Instead, a **fan-out-on-read (pull model)** is used.

#### How It Works
1. When a user requests their newsfeed, the Feed Service dynamically retrieves:
2. The system merges both types of posts in real-time before serving the feed.

**Benefits**:
- Avoids massive write operations, keeping the system scalable.
- Ensures fresh data when users request feeds.

**Challenges**:
- Slightly higher read latency than the push model.
- Requires caching optimization to reduce database lookups.

## 6.3 Search

### Indexing New Content
1. **A New Post/User is Created**
2. **Search Service Updates Elasticsearch Index**

### Search Request
1. **User Initiates a Search Request**
2. **Search Service Queries Elasticsearch**
3. **Elasticsearch Returns Results**
4. **Search Results are Cached in Redis**

## 6.4 Like, Comments and Shares
The **Engagement Service **processes like, comment and share requests.
It sends a Kafka event to update the DB asynchronously.
**Like event:**
**Share event:**
**Comment event:**
To optimize the latency for popular posts, we can cache like / share count and top comments.
# 7. Addressing Scalability, Availability and Durability

## 7.1 Scalability
Scalability ensures the system can handle increasing load without degrading performance.

#### Horizontal Scaling (Scale Out)
- Use distributed databases (Cassandra, DynamoDB) to distribute data across nodes.
- Deploy multiple instances of services behind a load balancer to handle user requests.

#### Sharding
- Implement sharding to split large datasets.
- User Data → Shard by `user_id mod N`
- Posts → Shard by `post_id mod N`
- Followers Table → Shard by `follower_id mod N`

#### Microservices Architecture
- Break the system into independent services (e.g., Feed Service, Post Service, User Service) to improve maintainability and scalability.
- Use message queues (Kafka, RabbitMQ) to handle high-throughput operations asynchronously (e.g., processing notifications, updates, and feed generation).

## 7.2 Availability
Availability ensures that Instagram remains accessible 24/7, even in the face of failures. Given its global user base, the platform must achieve atleast 99.99% uptime.

#### Redundancy & Replication
- Maintain replicated databases across multiple regions (e.g., PostgreSQL replicas, Cassandra multi-region clusters).
- Deploy multiple application servers across different availability zones (AZs).

#### Failover Mechanisms
- Use automatic failover in databases (e.g., leader-follower setup in PostgreSQL, multi-leader Cassandra clusters).
- Implement circuit breakers to gracefully degrade service if a dependency fails.

## 7.3 Durability
Durability ensures that data—especially user-generated content (photos, videos, comments, likes)—is never lost, even in case of system failures.

#### Distributed Object Storage
- Store media in Amazon S3 / Google Cloud Storage, which replicates data across multiple locations to prevent loss.

#### Database Replication & Backups
- Use multi-region replication (Cassandra, DynamoDB, PostgreSQL replicas) for disaster recovery.
- Perform regular backups to prevent accidental data loss.

#### Write-Ahead Logging (WAL) & Event Sourcing
- Implement WAL in databases to ensure changes are recorded before committing.
- Use event sourcing to log user actions (e.g., new posts, likes) and rebuild state if necessary.

# Quiz

## Design Instagram Quiz
Which component is primarily responsible for serving photos/videos quickly to users worldwide?