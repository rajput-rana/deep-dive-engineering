# Design News Aggregator

A news aggregator is a platform that collects news articles from multiple sources and presents them in a unified, personalized feed for users.
The core idea is to save users the hassle of visiting dozens of individual news websites by bringing all relevant content to one place. The system must continuously crawl or receive content from publishers, deduplicate similar stories, rank them by relevance, and serve personalized feeds to millions of users.
**Popular Examples:** Google News, Flipboard, Apple News, Feedly, Reddit (for link aggregation)
This system design problem touches on many interesting challenges: web crawling at scale, content deduplication using hashing or embeddings, real-time trend detection, personalization algorithms, and handling traffic spikes during breaking news events. 
There's no single "right" answer, which makes it perfect for exploring trade-offs.
In this chapter, we will explore the **high-level design of a news aggregator**.
Lets start by clarifying the requirements:
# 1. Clarifying Requirements
Before jumping into architecture diagrams, we need to understand what we're actually building. 
A "news aggregator" can mean many things. Are we building something like Google News that covers everything, or a niche aggregator focused on tech? Should the feed be the same for everyone, or personalized? How fast does content need to appear after it's published?
These questions shape every design decision that follows. Here's how a requirements discussion might unfold in an interview:
**Candidate:** "What is the expected scale? How many users and how many news sources should the system support?"
**Interviewer:** "Let's design for 100 million daily active users and 50,000 news sources (publishers, blogs, RSS feeds)."
**Candidate:** "Should the feed be personalized for each user, or is it the same for everyone?"
**Interviewer:** "Each user should get a personalized feed based on their interests and reading history."
**Candidate:** "How fresh should the content be? Do we need real-time updates for breaking news?"
**Interviewer:** "News should appear within a few minutes of publication. Breaking news should surface faster, within 30 seconds to 1 minute."
**Candidate:** "Should users be able to follow specific topics or sources?"
**Interviewer:** "Yes, users should be able to subscribe to topics (like Technology, Sports) and specific publishers."
**Candidate:** "Do we need to handle duplicate articles? The same story often appears on multiple sites."
**Interviewer:** "Yes, deduplication is important. Similar articles about the same story should be grouped together."
**Candidate:** "What about content moderation? Should we filter spam or low-quality sources?"
**Interviewer:** "Basic quality filtering is required, but assume we have a separate team handling detailed moderation. Focus on the aggregation and delivery aspects."
This conversation reveals several important constraints that will influence our design. Let's formalize these into requirements.

## 1.1 Functional Requirements
Based on the discussion, here are the core features the system must support:
- **Personalized Feed:** Generate a personalized news feed for each user based on their interests, subscriptions, and reading history.
- **Content Ingestion:** Continuously fetch and index news articles from 50,000+ sources.
- **Topic/Source Subscription:** Allow users to follow specific topics and news sources.
- **Article Deduplication:** Group similar articles covering the same story together.
- **Search:** Allow users to search for articles by keywords.
- **Breaking News:** Surface trending and breaking news quickly (within 1 minute).

## 1.2 Non-Functional Requirements
Beyond features, we need to consider the qualities that make the system production-ready:
- **High Availability:** The system must be highly available (99.99% uptime).
- **Low Latency:** Feed generation should complete within 200ms (p99).
- **Scalability:** Support 100 million DAU with peak traffic during major news events.
- **Freshness:** New articles should appear in feeds within 2-5 minutes of publication, breaking news within 1 minute.

# 2. Back-of-the-Envelope Estimation
Before diving into the design, let's run some quick calculations to understand the scale we're dealing with. These numbers will guide our architectural decisions, particularly around how we handle the massive asymmetry between content ingestion (relatively low volume) and feed serving (extremely high volume).

### 2.1 Traffic Estimates
Let's start with the numbers from our requirements discussion.

#### Content Ingestion (Write Traffic)
We have 50,000 news sources, and let's assume each publishes about 20 articles per day on average. Some major publishers might publish 100+ articles daily, while smaller blogs might post once a week, so this averages out.
During major news events, multiple sources publish rapidly. Assuming a 5x spike factor:
This is relatively modest. The ingestion side of our system is not the bottleneck.

#### Feed Serving (Read Traffic)
Now for the interesting part. With 100 million daily active users, each refreshing their feed about 10 times per day (morning check, lunch break, evening scroll, etc.):
During breaking news events, everyone opens their news app at once. With a 3x spike factor:
The key insight here is the **read-to-write ratio of nearly 1000:1**. For every article we ingest, we serve it to thousands of users. This tells us we need to invest heavily in caching and optimize aggressively for read performance.

### 2.2 Storage Estimates
Each article needs to store metadata for display and ranking. Here's a breakdown:
| Component | Size | Notes |
| --- | --- | --- |
| Article ID | 16 bytes | UUID or Snowflake ID |
| Title | 100 bytes | Average headline length |
| Summary/snippet | 500 bytes | First paragraph or generated summary |
| Original URL | 200 bytes | Link to source article |
| Source ID, category | 50 bytes | Foreign keys and enum |
| Timestamps | 16 bytes | Published, ingested |
| Metadata (images, author) | 200 bytes | Thumbnail URL, author name |
| Total | ~1.1 KB | Per article |

#### Article Storage Growth:

#### User Data:
Each user has preferences (subscribed topics, followed sources, blocked sources) and reading history. Estimating about 1 KB per user on average:
These numbers are manageable. The storage requirements are modest compared to systems that store full article content or user-generated media.

### 2.3 Key Insights from Our Estimates
A few observations that will guide our design:
1. **Read-heavy workload (1000:1):** Caching is not optional, it's essential. Most feed requests should be served without hitting the database.
2. **Modest ingestion rate:** 12 QPS is easy to handle. We have room for complex processing (ML categorization, embedding generation, deduplication) without becoming a bottleneck.
3. **Breaking news spikes:** Both reads and writes can spike during major events. We need auto-scaling and circuit breakers to handle sudden load.
4. **Reasonable storage:** 400 GB/year for articles is manageable. We don't need exotic storage solutions, but we should think about archiving old content.

# 3. Core APIs
With our requirements and scale understood, let's define the API contract. A news aggregator has a focused set of endpoints: get the personalized feed, view article details, manage preferences, and search. Let's walk through each one.

### 3.1 Get Personalized Feed

#### Endpoint: GET /feed
This is the primary endpoint users interact with. It returns a personalized stream of articles tailored to the user's interests, subscriptions, and reading history.

#### Request Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| page_token | string | No | Cursor for pagination. Enables infinite scroll. |
| limit | integer | No | Number of articles to return (default: 20, max: 50) |
| category | string | No | Filter by category (e.g., "technology", "sports") |

#### Example Request:

#### Success Response (200 OK):
The `similar_count` field indicates how many other sources covered this story. Users can tap to see alternative sources.

#### Error Cases:
| Status Code | Meaning |
| --- | --- |
| 401 Unauthorized | User not authenticated |
| 429 Too Many Requests | Rate limit exceeded |

### 3.2 Get Article Details

#### Endpoint: GET /articles/{article_id}
When a user taps on an article, this endpoint returns full details including similar articles from other sources.

#### Path Parameters:
| Parameter | Type | Description |
| --- | --- | --- |
| article_id | string | Unique identifier for the article |

#### Success Response (200 OK):

#### Error Cases:
| Status Code | Meaning |
| --- | --- |
| 404 Not Found | Article does not exist or has been removed |

### 3.3 Update User Preferences

#### Endpoint: PUT /users/preferences
Allows users to manage their subscriptions and personalization settings.

#### Request Body:
| Parameter | Type | Description |
| --- | --- | --- |
| topics | string[] | Topic IDs to follow (e.g., ["technology", "sports"]) |
| sources | string[] | Source IDs to follow |
| blocked_sources | string[] | Sources to exclude from feed |
| language | string | Preferred content language |

#### Example Request:

#### Success Response (200 OK):

### 3.4 Search Articles

#### Endpoint: GET /search
Allows users to search for articles by keywords, with optional filters.

#### Request Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| query | string | Yes | Search query string |
| from_date | string | No | Filter articles published after this date (ISO 8601) |
| sources | string[] | No | Limit search to specific sources |
| limit | integer | No | Number of results (default: 20) |

#### Example Request:

#### Success Response (200 OK):
The `relevance_score` indicates how well the article matches the search query, useful for explaining ranking to users.
# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complex diagram upfront, we'll build the design incrementally, starting with the simplest components and adding complexity as we encounter challenges. This mirrors how you would approach the problem in an interview.
Our system has two fundamentally different paths:
1. **Write Path (Content Ingestion):** Fetch articles from thousands of sources, process them, and store them for later retrieval. This runs at a modest 12 QPS on average.
2. **Read Path (Feed Serving):** Generate personalized feeds for millions of users. This handles 1000x more traffic at 11,500 QPS average.

The massive asymmetry between these paths shapes our entire design. The write path can afford complex processing (ML categorization, embedding generation, deduplication) because it's low volume. The read path needs aggressive caching and optimization because every millisecond counts when you're serving 35,000 requests per second at peak.
Let's build each path step by step.


The first challenge is getting articles into our system. With 50,000 sources publishing 1 million articles per day, we need a reliable, scalable ingestion pipeline. Some sources offer clean RSS feeds, others have APIs, and some require HTML scraping. Breaking news needs to surface quickly, while niche blogs can be crawled less frequently.

### Components for Content Ingestion
Let me introduce each component and explain why we need it.

#### Crawler Service
This is the front door of our system. The Crawler Service is responsible for fetching content from external news sources. It's essentially a fleet of workers that constantly poll sources for new content.
What makes this tricky is the variety of sources. Major publishers like Reuters might offer a clean JSON API. Tech blogs typically have RSS feeds. Smaller sites might require HTML scraping. The crawler needs to handle all of these, while respecting rate limits and robots.txt directives to avoid getting blocked.
The service maintains a priority queue of sources to crawl. High-priority sources (major publishers, known for breaking news) get crawled every 1-2 minutes. Lower-priority sources might be checked every 30-60 minutes. This adaptive scheduling ensures we catch breaking news quickly without wasting resources polling inactive blogs.

#### Message Queue (Kafka)
Why not send articles directly from the crawler to the processor? Decoupling these stages with Kafka gives us several benefits.
First, it handles traffic spikes gracefully. When a major news event breaks, dozens of sources publish simultaneously. Kafka buffers this burst while processors work through it at a steady pace.
Second, it enables independent scaling. We might need 10 crawlers but only 5 processors, or vice versa. With Kafka in between, each tier can scale based on its own needs.
Third, it provides reliability. If a processor crashes, messages wait in Kafka until another processor picks them up. No data is lost.

#### Content Processor Service
Raw crawled content is messy. The Content Processor transforms it into clean, structured data that our system can work with.
This is where the interesting work happens. The processor extracts metadata (title, summary, images, publish date), categorizes articles using ML classification models, computes content hashes for deduplication, and generates text embeddings for semantic similarity matching. Each of these steps enriches the article with information we'll use for feed generation and search.

#### Article Database
Stores the processed article metadata. We need fast lookups by article ID (for retrieving specific articles) and efficient queries by category and timestamp (for feed generation).

#### Search Index (Elasticsearch)
While the database handles structured queries, Elasticsearch powers our full-text search feature and enables complex filtering queries. When a user searches for "climate change policy," Elasticsearch finds relevant articles across millions of documents in milliseconds.

### The Ingestion Flow in Action
Here's how these components work together when a new article is published:
Let's trace through a specific example. Say TechCrunch publishes an article about a new iPhone:
The entire process, from TechCrunch publishing to the article being available in feeds, takes about 30 seconds to 2 minutes depending on crawl timing and processing load. For breaking news (which we detect separately), we can reduce this to under 30 seconds.


    CDNNode --> Mobile
```mermaid
graph TB
    subgraph Clients
        Web[Web Browser]
        Mobile[Mobile App]
    end

    subgraph Application Services
        S1[one Service]
        S2[Feed Service]
        S3[Every Service]
        S4[Preferences Service]
        S5[The Service]
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

    subgraph CDNLayer
        CDNNode[Content Delivery Network]
    end

    Web --> LB
    Mobile --> LB
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
    CDNNode --> Web
    CDNNode --> Mobile



## 4.2 Requirement 2: Feed Generation
Now for the more interesting path: generating personalized feeds for 100 million users. This is where the 1000:1 read-to-write ratio really matters. Every design decision here affects latency for millions of users.
The fundamental question is: **when do we assemble each user's feed?** There are three schools of thought.

### Feed Generation Strategies

#### Push Model (Fan-out on Write)
In this approach, we precompute feeds proactively. When a new article is published, the system immediately pushes it to the feeds of all interested users.
The upside is that feed reads are blazing fast. When a user opens the app, their feed is already sitting in storage, ready to serve. The downside is write amplification. If 50 million users follow "Technology," publishing one tech article means 50 million write operations. That's untenable at our scale.

#### Pull Model (Fan-out on Read)
The opposite approach is to compute feeds on-demand. When a user requests their feed, the system dynamically queries their subscribed sources and assembles the feed in real-time.
The upside is efficiency. No write amplification, and storage is minimal. The downside is latency. Each feed request requires multiple database queries and ranking computation, which could push response times above our 200ms target.

#### Hybrid Model (Our Choice)
Neither extreme works well for a news aggregator at scale. Instead, we use a hybrid approach that adapts based on content type and user behavior:
- **Trending/breaking news:** Push to active users' cached feeds immediately. When everyone's interested in the same story, precomputing makes sense.
- **Niche content:** Pull on demand. For a user's obscure interest in Slovenian politics, computing on-request is fine.
- **Active users:** Precompute feeds during off-peak hours so they're ready for the morning commute.
- **Inactive users:** Compute on-demand when they return to save storage.

This gives us the best of both worlds: fast reads for hot content without the write amplification nightmare.

### Components for Feed Serving

#### User Preferences Service
Stores and serves user subscription data. When the Feed Service needs to know what topics and sources a user follows, this service provides the answer in milliseconds.
Beyond explicit subscriptions, this service also tracks implicit signals: articles the user clicked, topics they linger on, sources they avoid. These signals feed into the personalization algorithm.

#### Feed Service
This is the core of the read path. The Feed Service takes a user request, figures out what articles they should see, ranks them, and returns a paginated response.
The service is stateless, meaning any instance can handle any request. All user state lives in the Preferences Service and cache. This makes horizontal scaling straightforward.

#### Feed Cache (Redis)
With 11,500 QPS average and 35,000 QPS peak, we cannot afford to hit the database for every request. Redis provides the caching layer that makes this feasible.
We cache two types of data:
- **User feeds:** Recently computed feeds for active users, indexed by user ID
- **Trending content:** Global trending articles that appear in many feeds, reducing redundant computation

A well-tuned cache should serve 80-90% of requests without touching the database.

### The Feed Generation Flow
Here's how these components work together when a user opens their news app:
Let's trace through both the cache hit and cache miss scenarios:
The cache hit path is the fast path, completing in under 50ms. The cache miss path is more expensive but still targets under 200ms. With a good cache hit rate, average latency stays well under our target.

## 4.3 Requirement 3: Breaking News and Trending Topics
When a major story breaks, like an election result, natural disaster, or celebrity news, users expect to see it immediately. Not in 5 minutes. Not even in 2 minutes. They want it now. This is where our 1-minute freshness requirement for breaking news comes into play.
The challenge is detecting when something is "breaking." We can't rely on sources to label their content as breaking news (they often overuse the term). Instead, we need to detect it automatically by observing patterns in our content stream.

### Detecting Breaking News
The Trend Detection Service monitors the velocity of incoming articles. Here's the key insight: when a major story breaks, multiple sources start covering it almost simultaneously. If we see 20 articles about "earthquake" from different sources within 5 minutes when the baseline is 1-2 per hour, that's breaking news.
The service maintains sliding windows of article counts per topic. When the count in a short window (5 minutes) significantly exceeds the longer-term average (24 hours), we flag it as trending or breaking.

### Components for Breaking News

#### Trend Detection Service
Analyzes the article stream in real-time to identify breaking stories. It tracks article velocity per topic, detects anomalies using statistical methods (or ML models), and triggers alerts when something significant is happening.

#### Breaking News Queue
A high-priority queue that bypasses normal processing. When a story is flagged as breaking, it gets pushed through a fast path that prioritizes speed over thoroughness. We might skip some enrichment steps to get it into feeds faster.

#### Push Notification Service
For truly major events, we can proactively notify users who have expressed interest in the topic. A user who follows "Sports" might get a push notification when their favorite team wins a championship.

### Breaking News Flow
Here's how breaking news propagates through the system:
The key insight is that we invalidate cached feeds when breaking news hits. This forces a cache miss on the next request, ensuring users see fresh content even if their cached feed is only 2 minutes old.

## 4.4 Putting It All Together
Now that we've built each component, let's step back and see the complete architecture. We have three major paths through the system:
1. **Content Ingestion:** Crawl → Process → Store
2. **Feed Serving:** Request → Cache/Compute → Respond
3. **Breaking News:** Detect → Invalidate → Push

### Component Summary
Let's recap what each component does and why we need it:
| Component | Purpose | Why We Need It |
| --- | --- | --- |
| Crawler Service | Fetches articles from 50K sources | Handles diverse source types (RSS, API, HTML) |
| Kafka | Buffers raw articles | Decouples crawling from processing, handles spikes |
| Content Processor | Extracts metadata, categorizes, deduplicates | Transforms raw content into structured, searchable data |
| Article Database | Stores processed article metadata | Fast lookups by ID, efficient range queries |
| Elasticsearch | Full-text search and filtering | Powers search feature and complex queries |
| Trend Detection | Identifies breaking news | Ensures breaking stories surface within 1 minute |
| Feed Service | Generates personalized feeds | Core business logic for the read path |
| Feed Cache (Redis) | Caches computed feeds | Enables 80-90% cache hit rate, sub-50ms responses |
| User Preferences | Stores subscriptions and history | Provides personalization signals |
| Push Notifications | Alerts users to breaking news | Proactive delivery for high-interest stories |

### Design Highlights
A few things worth noting about this architecture:
**Separation of concerns:** The ingestion path and serving path are completely independent. We can scale them separately and deploy changes without affecting each other.
**Multiple caching layers:** CDN caches at the edge, Redis caches at the application layer. Most requests never hit the database.
**Graceful degradation:** If Trend Detection fails, we still serve feeds, just without breaking news prioritization. If Redis fails, we compute feeds from the database (slower but functional).
**Horizontal scaling:** Every service except the database is stateless and can scale horizontally. The database can scale with read replicas and eventually sharding.
# 5. Database Design
With the high-level architecture in place, let's zoom into the data layer. The database choices and schema design significantly impact performance, scalability, and the complexity of our queries.

## 5.1 Choosing the Right Database
The database choice is not obvious for a news aggregator. We have multiple data types with different access patterns, and choosing a single database for everything would force trade-offs we'd rather avoid.
Let's think through our access patterns:
**Article lookups:** Primarily by ID (for specific article pages) or by category/timestamp (for feed generation). These are straightforward queries that most databases handle well.
**User preferences:** Each user has different subscriptions. Some follow 3 topics, others follow 50. The schema needs to be flexible.
**Feed generation:** Requires joining user preferences with articles, filtering by category/source, sorting by timestamp, and applying personalization. This is the most complex query pattern.
**Scale:** 100 million users and 1 million articles per day. This is significant but manageable.
**Consistency vs. Availability:** Users can tolerate slightly stale feed data (a few seconds), but the system must always be available. We lean toward availability.

### Our Database Strategy
Given these requirements, we use a polyglot persistence approach, picking the right tool for each job:
| Data Type | Database Choice | Reasoning |
| --- | --- | --- |
| Article metadata | DynamoDB or Cassandra | Fast key-value lookups, easy horizontal scaling, handles write volume |
| User preferences | DynamoDB | Flexible schema for varying subscriptions, fast reads |
| Search and filtering | Elasticsearch | Full-text search, complex queries on category/topic/timestamp |
| Feed cache | Redis | Sub-millisecond reads for precomputed feeds |

Why not just use PostgreSQL for everything? It could work at this scale, but NoSQL databases give us easier horizontal scaling and better write throughput. Elasticsearch gives us search capabilities that would be slow in a traditional database.

## 5.2 Database Schema
Let's look at each table and understand what we're storing and why.

### Articles Table
This is our primary data store for article metadata. Each row represents one ingested article.
| Field | Type | Description |
| --- | --- | --- |
| article_id | String (PK) | Unique identifier (Snowflake ID or UUID) |
| source_id | String | Foreign key to Sources table |
| title | String | Article headline |
| summary | String | First 500 characters or generated summary |
| url | String | Original article URL (for redirecting users) |
| image_url | String | Thumbnail image for feed display |
| category | String | Primary category: technology, sports, politics, etc. |
| topics | List<String> | More specific tags: ["AI", "OpenAI", "GPT"] |
| published_at | Timestamp | When the source published the article |
| ingested_at | Timestamp | When we indexed it (for freshness tracking) |
| content_hash | String | Hash for exact-match deduplication |
| cluster_id | String | Groups similar articles covering the same story |
| embedding | Vector | Semantic embedding for similarity search |

**Key indexes:**
- Primary key on `article_id` for fast lookups
- GSI on `category + published_at` for category-based feeds
- GSI on `source_id + published_at` for source-based feeds

The `cluster_id` is particularly important. When multiple sources cover the same story, they get grouped under the same cluster. The feed shows one representative article with an option to "see 12 other sources."

### Sources Table
Stores metadata about each news source we crawl. This table is relatively small (50,000 rows) and rarely changes.
| Field | Type | Description |
| --- | --- | --- |
| source_id | String (PK) | Unique identifier |
| name | String | Display name: "TechCrunch", "BBC News" |
| url | String | Homepage URL |
| rss_url | String | RSS feed URL (if available) |
| api_endpoint | String | API endpoint (if available) |
| category | String | Primary category |
| crawl_frequency_minutes | Integer | How often to poll (1-60 minutes) |
| quality_score | Float | Reliability score (0.0 to 1.0), used in ranking |
| is_active | Boolean | Whether we're currently crawling |
| last_crawled_at | Timestamp | For scheduling |

The `quality_score` is interesting. It's a combination of factors: how often the source produces accurate content, reader engagement metrics, and editorial reputation. This score influences how prominently we rank articles from this source.

### User Preferences Table
Stores explicit user preferences, the topics and sources they've chosen to follow.
| Field | Type | Description |
| --- | --- | --- |
| user_id | String (PK) | Unique user identifier |
| followed_topics | List<String> | ["technology", "sports", "business"] |
| followed_sources | List<String> | ["src_techcrunch", "src_espn"] |
| blocked_sources | List<String> | Sources user never wants to see |
| language | String | Preferred content language |
| updated_at | Timestamp | For cache invalidation |

This table is read-heavy. Every feed request needs the user's preferences. We keep it in DynamoDB for fast key-value lookups and cache aggressively in Redis.

### User Reading History Table
Tracks user interactions with articles. This powers the "avoid showing already-read articles" feature and provides implicit signals for personalization.
| Field | Type | Description |
| --- | --- | --- |
| user_id | String (PK) | User identifier |
| article_id | String (SK) | Article identifier |
| action | String | "read", "saved", "shared", "hidden" |
| timestamp | Timestamp | When the action occurred |
| dwell_time_seconds | Integer | How long they spent on the article |

The combination of `user_id` and `article_id` as the key allows efficient lookups: "has this user seen this article?"
We use TTL to automatically expire old history (e.g., after 30 days). Users don't need infinite history, and this keeps the table size manageable.
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often go deeper into specific components. In this section, we'll explore the trickiest parts of our design: how to detect duplicate stories, how to rank articles effectively, how to crawl at scale, and how to handle traffic spikes. These are the topics that distinguish a good system design answer from a great one.

## 6.1 Content Deduplication
Here's a problem unique to news aggregators: when Apple announces a new iPhone, every tech publication covers it. CNN, BBC, TechCrunch, The Verge, and 50 other sources all publish articles within hours. Without deduplication, a user following "Technology" would see essentially the same story 50 times in their feed.
A good deduplication system does four things:
1. Identifies articles covering the same underlying story
2. Groups them into a "story cluster"
3. Selects one representative article to show in the feed
4. Lets users see "12 other sources" if they want different perspectives

Let's explore three approaches, each with increasing sophistication.

### Approach 1: URL and Title Matching
The simplest approach: consider articles duplicates if they share the exact same URL or title.
**How it works:** When a new article arrives, compute a hash of its URL. Check if this hash exists in our database. If yes, it's a duplicate. Skip it.
**Why it works for some cases:** Syndicated content often uses the exact same URL. RSS feeds sometimes aggregate the same article from multiple sources.
**Why it fails for most cases:** Different outlets write their own articles with unique URLs and different headlines. "Apple unveils iPhone 16" and "New iPhone announced by Apple" are clearly about the same story, but exact matching won't catch them.
**Verdict:** Good as a first-pass filter, but not sufficient on its own.

### Approach 2: Content Fingerprinting (SimHash/MinHash)
Instead of exact matching, we can use locality-sensitive hashing to find articles with similar text content.

#### How it works:
1. Tokenize the article text into overlapping word sequences (called "shingles")
2. Compute a fingerprint using SimHash or MinHash algorithms
3. Compare fingerprints. If the Hamming distance is small, the articles are similar

**Pros:** Catches paraphrased content where wording differs but meaning is the same. Fast to compute and compare.
**Cons:** Requires tuning the similarity threshold. Too strict and you miss duplicates. Too loose and you falsely group unrelated articles. Also struggles with cross-language deduplication.

### Approach 3: Semantic Embeddings (Recommended)
The most sophisticated approach uses machine learning to understand what articles are about, not just what words they contain.

#### How it works:
1. Pass each article's title and first paragraph through an embedding model (Sentence-BERT, OpenAI embeddings, or similar)
2. Store the resulting vector in a vector database (Pinecone, Milvus, pgvector)
3. For each new article, find the k nearest neighbors by cosine similarity
4. If similarity exceeds a threshold (e.g., 0.85), cluster the articles together

**Example:**
**Pros:** Semantic understanding catches stories regardless of wording. Multilingual models work across languages. Can cluster at different granularities.
**Cons:** Higher latency (10-50ms per article for embedding generation). Requires ML infrastructure. More expensive to operate.

### Recommendation: Two-Stage Approach
For a production news aggregator, use both approaches in sequence:

#### Stage 1: Fast exact-match filter
- Hash the URL and title
- Check against existing hashes in Redis (sub-millisecond)
- Skip obvious duplicates immediately

#### Stage 2: Semantic clustering
- Generate embedding for articles that pass Stage 1
- Query vector database for similar articles
- Assign to existing cluster or create new one

This gives us speed for the common case (exact duplicates) and accuracy for the hard case (paraphrased content).
| Strategy | Speed | Accuracy | Best For |
| --- | --- | --- | --- |
| URL/Title Hash | < 1ms | Low | First-pass filter |
| SimHash/MinHash | ~5ms | Medium | Text-similar articles |
| Embeddings | 10-50ms | High | Semantic similarity |

## 6.2 Feed Ranking Algorithm
The simplest approach to building a news feed is reverse chronological order: show the newest articles first. This is what Twitter (X) used for years, and it's what some users still prefer. But for a news aggregator, chronological ordering has problems.
Consider a user who follows Technology, Sports, and Business. They open the app at 8 AM. If we just show newest-first, they might see 10 technology articles in a row (because tech blogs publish early). They'd miss the important business news from last night and the sports recap from yesterday's game. Worse, if we ingested a batch of articles at the same time, the ordering would be arbitrary.
A good ranking algorithm balances multiple factors: freshness, relevance to the user, source quality, and feed diversity. Let's break down each signal.

### The Ranking Signals

#### 1. Recency Score
News has a short shelf life. An article published 2 hours ago is usually more valuable than one from 12 hours ago. We apply time decay:
The decay function can be tuned. For breaking news, we might use exponential decay (very aggressive). For evergreen content like opinion pieces, linear decay works better.

#### 2. Relevance Score
How well does this article match what the user cares about? We combine three signals:
- **Topic match:** Does the article's category match the user's subscribed topics?
- **Source preference:** Is this from a source the user explicitly follows?
- **Historical similarity:** Has the user engaged with similar content before?

The historical similarity is particularly powerful. If a user consistently clicks on articles about "electric vehicles" within the Technology category, we boost EV articles even if they didn't explicitly subscribe to that topic.

#### 3. Quality Score
Not all sources are created equal. A well-researched Reuters article should rank higher than a clickbait aggregator that just rewrote Reuters' work.
The source quality rating comes from our Sources table (0.0 to 1.0). The engagement rate is how well this specific article is performing: clicks, read time, shares.

#### 4. Diversity Penalty
Without diversity controls, a feed can become monotonous. If the top 10 articles are all from TechCrunch about AI, that's a poor experience even for an AI enthusiast.
We apply a penalty when articles appear in sequence from the same source or topic:
This penalty is applied during the final ranking pass to spread out content.

#### 5. Trending Boost
When an article is getting a lot of attention across the platform, that's a signal that it might be interesting to users who haven't seen it yet.
We use logarithms to prevent viral articles from completely dominating the feed.

### The Combined Ranking Formula
All signals combine into a final score:
The weights are tuned through A/B testing. Different user segments might have different optimal weights. Power users who check the app every hour might prefer higher recency weight. Casual users who check once a day might prefer higher relevance weight.

### Two-Stage Ranking for Performance
Computing relevance and quality scores for millions of articles would be too slow. Instead, we use a two-stage approach:

#### Stage 1: Candidate Generation (Fast)
We query Elasticsearch with the user's subscribed topics and sources, filtered to articles from the last 24-48 hours. This returns 500-1000 candidates quickly because Elasticsearch is optimized for this exact query pattern.

#### Stage 2: Precision Ranking (Accurate)
Now we compute the full ranking formula for just 500-1000 articles instead of millions. We fetch user history, compute similarity scores, apply diversity rules, and return the top 20-50 articles.
This two-stage approach keeps p99 latency under 200ms while still delivering personalized, high-quality rankings.

## 6.3 Real-Time Content Ingestion
Crawling 50,000 sources is a balancing act. Crawl too aggressively, and sources block you. Crawl too conservatively, and you miss breaking news. Some sources publish 100 articles a day, others post once a week. Some have clean RSS feeds, others require scraping. Let's figure out how to do this efficiently.

### The Crawling Strategies
There are fundamentally two approaches to getting content: either we go fetch it (polling), or the source tells us when something new is available (push). Each has trade-offs.

#### Approach 1: Polling (Pull-Based)
The traditional approach: periodically check each source for new content.
**How it works:** Maintain a schedule for each source. A worker fetches the RSS feed or scrapes the homepage, compares with previously seen URLs, and queues new articles for processing.
**The challenge:** Finding the right crawl frequency. If we crawl CNN every minute, we might catch breaking news quickly. But if we also crawl 49,999 other sources every minute, that's 50,000 requests per minute, which is wasteful and likely to get us blocked.
**The solution is adaptive polling.** We track how often each source publishes and adjust our crawl frequency accordingly:
This reduces our request volume while ensuring we catch new content quickly from active sources.

#### Approach 2: WebSub/PubSubHubbub (Push-Based)
Some sources support push notifications. When they publish something new, they tell us immediately.
**How it works:** We subscribe to the source's WebSub hub. When the source publishes, the hub sends a notification to our callback URL. We immediately fetch and process the article.
**The upside:** Real-time updates. Articles arrive within seconds of publication, not minutes.
**The downside:** Limited adoption. Most sources don't support WebSub. And even those that do might have unreliable implementations. We need fallback polling anyway.

#### Approach 3: Hybrid (Recommended)
For a production system, we use all available methods:
| Method | Sources | Latency | Coverage |
| --- | --- | --- | --- |
| WebSub push | ~5% of sources that support it | Seconds | Limited |
| Direct API | Major publishers with partnerships | Seconds | Premium |
| Adaptive polling | Everything else | 1-30 min | Complete |

### Crawler Architecture
Here's how we structure the crawling system:

#### Key design decisions:
- **Priority queue sorted by next_crawl_time:** Sources due for crawling bubble to the top. Workers simply pop the next item and crawl it.
- **Per-source rate limiting:** Even if a source is due for crawling, we respect their robots.txt and rate limits. Getting blocked is worse than being slightly stale.
- **Exponential backoff on failures:** If a source returns errors, we back off exponentially (1 min, 2 min, 4 min...) to avoid hammering a struggling server.
- **Worker pool scaling:** During breaking news events, we can scale up workers to crawl more sources in parallel. Kubernetes autoscaling based on queue depth works well here.

## 6.4 Handling Traffic Spikes (Breaking News)
When major news breaks, whether it's an election result, a natural disaster, or a celebrity scandal, traffic patterns change dramatically. On a normal day, our news aggregator handles 11,500 QPS. When the news breaks, that can spike to 100,000 QPS or more. Everyone opens their news app at the same time.
This creates a perfect storm of challenges:
Let's look at strategies to handle each challenge.

### Strategy 1: Surge Capacity and Auto-Scaling
For predictable events (elections, Super Bowl, product launches), we pre-provision extra capacity. We know the traffic is coming, so we scale up beforehand.
For unexpected events, we need auto-scaling that reacts quickly:
The key is scaling out before the system becomes overwhelmed. Reactive scaling that waits until things are broken is too slow.

### Strategy 2: Circuit Breakers
When one service becomes overwhelmed, it can take down everything else in a cascade. Circuit breakers prevent this.

#### How it works:
- Normal state (closed): Requests pass through to the database
- High error rate detected (> 50%): Circuit opens
- Open state: Return cached response or degraded experience. Stop hitting the struggling database.
- After 30 seconds: Try a few requests. If they succeed, close the circuit.

This prevents a struggling database from receiving more load and allows it to recover.

### Strategy 3: Request Coalescing
During a traffic spike, many users request essentially the same data within milliseconds of each other. Request coalescing recognizes this and serves them with a single backend query.
This is particularly effective for "hot" content that everyone wants at the same time. Implementation involves short-lived locks and result sharing, similar to the "singleflight" pattern.

### Strategy 4: Graceful Degradation
When the system is overwhelmed despite all other measures, we intentionally reduce functionality to keep the core experience working.
| Load Level | What We Serve | What We Skip |
| --- | --- | --- |
| Normal | Full personalization, complete feed | Nothing |
| High | Cached feeds + breaking news overlay | Real-time ranking updates |
| Critical | Global trending feed only | All personalization |
| Emergency | Static "high traffic" page | Dynamic content |

The key insight is that during breaking news, everyone wants the same story anyway. A global trending feed is nearly as useful as a personalized one, but vastly cheaper to serve.

### Strategy 5: Edge Caching for Breaking News
Breaking news is the perfect candidate for CDN caching. Everyone wants the same content, and slight staleness (30 seconds) is acceptable.
| Content Type | CDN Cache TTL | Why |
| --- | --- | --- |
| Breaking news articles | 1-2 minutes | High demand, slight staleness OK |
| Trending topics list | 5 minutes | Changes slowly |
| Personalized feeds | No edge cache | Privacy concerns |
| Article images | 24 hours | Static content |

When we detect breaking news (via Trend Detection), we push it to CDN edge nodes proactively. This means the first user in Singapore gets a cache hit, not a cache miss that reaches our origin.

## 6.5 Personalization Without Sacrificing Privacy
Personalization makes news feeds more engaging, but it requires tracking user behavior. This creates tension. Users want relevant content without feeling like they're being surveilled. How do we balance these competing concerns?
The naive approach is to track everything: every article clicked, every second spent reading, every share and save. This enables precise personalization, but it also creates a detailed profile of each user's interests, political leanings, and habits. In an era of growing privacy awareness and regulations like GDPR, this approach is increasingly problematic.
Let's explore three approaches, from most private to most personalized.

### Approach 1: On-Device Personalization
Keep all user data on their device. The server never sees what articles they read.
**How it works:** The user tells the server their general interests ("technology", "sports"). The server returns the top articles in those categories. The device then re-ranks based on local reading history.
**Pros:** Maximum privacy. The server doesn't know which articles the user read.
**Cons:** Limited personalization quality since the device has no global signals. Also requires more client-side compute and storage.

### Approach 2: Anonymous Cohorts
Instead of tracking individual users, group them into anonymous cohorts based on general interest patterns.
**How it works:** We identify 100-1000 cohorts representing common interest patterns. Each user is assigned to a cohort based on their explicit subscriptions (not reading history). All users in a cohort receive the same feed candidates.
**Pros:** No individual tracking. A cohort of 10,000 users provides k-anonymity. Good personalization for common interest patterns.
**Cons:** Less precise than individual profiles. Users with unusual interest combinations get suboptimal recommendations.

### Approach 3: Differential Privacy
For features that require aggregated user behavior (trending topics, popular articles), we can use differential privacy to protect individuals while still learning from the crowd.
**How it works:** Before aggregating user actions (clicks, shares), we add calibrated noise to each user's contribution. The noise cancels out in aggregate but makes it impossible to identify any individual's behavior.
**Pros:** Mathematical privacy guarantees. Still enables useful aggregate signals.
**Cons:** Reduces signal quality. Doesn't help with individual personalization.

### Recommendation: Tiered Privacy
For a production news aggregator, we recommend a tiered approach that gives users control:
| Privacy Level | What We Track | Personalization Quality |
| --- | --- | --- |
| Anonymous | Nothing (device only) | Basic (category matching) |
| Cohort (default) | Subscription patterns | Good (cohort-based) |
| Full (opt-in) | Reading history | Excellent (individual) |

Users start at the Cohort level. They can opt down to Anonymous for maximum privacy, or opt up to Full for better recommendations. Critically, we make these options visible and easy to change, not buried in settings.

## 6.6 Search Implementation
While the personalized feed is the primary way users consume news, search is essential for finding specific stories. Maybe the user heard about a story from a friend and wants to read more. Maybe they want to research a topic for work. Maybe they're looking for an article they read last week but can't find in their feed.
Search for a news aggregator has some unique requirements compared to general web search:
- **Recency matters:** Yesterday's news about a topic is usually more relevant than last year's
- **Source filtering:** Users often want to search within specific sources
- **Freshness:** New articles should be searchable within minutes of ingestion

### Search Architecture

### Elasticsearch Index Design
We index article metadata optimized for the query patterns we expect:
A few notes on this design:
- **title.keyword:** The nested keyword field enables exact-match queries and aggregations
- **topics as keyword array:** Enables faceted search ("show me articles about AI, filtered by OpenAI")
- **quality_score and popularity_score:** Used in result ranking

### Search Features
**Full-text search:** The core feature. Match queries against title and summary using Elasticsearch's BM25 algorithm. We boost title matches over summary matches since titles are more signal-dense.
**Filters:** Users can narrow results by category, source, and date range. These are implemented as Elasticsearch filters, not queries, so they don't affect relevance scoring.
**Faceted search:** Show article counts by category and source alongside results. This helps users understand what's available and refine their search.
**Autocomplete:** As users type, suggest completions based on popular queries and trending topics. This is implemented using Elasticsearch's completion suggester with a separate index optimized for prefix matching.

### Search Ranking
Elasticsearch's default relevance ranking (BM25) is a good starting point, but news search needs additional signals:
This ensures that a mediocre article from today ranks higher than a perfect article from three months ago, reflecting how users typically want to find recent news.

### Example Search Query
Here's what an actual Elasticsearch query looks like for a user searching "AI regulation Europe":
The `title^2` boost means title matches count twice as much as summary matches. The filter restricts to articles from the last 7 days. The aggregations power the faceted search UI.
# References
- [RSS 2.0 Specification](https://www.rssboard.org/rss-specification) - Standard for content syndication feeds
- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html) - Full-text search implementation guide
- [WebSub W3C Recommendation](https://www.w3.org/TR/websub/) - Push-based content notification protocol

# Summary
Designing a news aggregator involves balancing several competing concerns: freshness vs. cost, personalization vs. privacy, accuracy vs. latency. Here are the key takeaways from our design:
1. **The system is fundamentally read-heavy (1000:1 ratio).** This means aggressive caching is essential, not optional. Most feed requests should never hit the database.
2. **Content ingestion is a multi-stage pipeline.** Crawl → Buffer (Kafka) → Process → Store → Index. Each stage scales independently.
3. **Feed generation uses a hybrid push/pull model.** Push breaking news to active users, pull niche content on demand. This balances write amplification against read latency.
4. **Deduplication requires semantic understanding.** URL hashing catches obvious duplicates, but embeddings are needed to group paraphrased articles about the same story.
5. **Breaking news requires special handling.** Trend detection, cache invalidation, and graceful degradation work together to handle 10-100x traffic spikes.
6. **Privacy and personalization can coexist.** Tiered privacy options let users choose their comfort level.

This design could be extended in many directions: adding video content, supporting multiple languages, implementing more sophisticated ML models for categorization, or building social features. But the core architecture provides a solid foundation for a production news aggregator.
# Quiz

## Design News Aggregator Quiz
In a news aggregator, why is the read path typically designed differently from the write path?