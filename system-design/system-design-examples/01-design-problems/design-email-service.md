# Design Email Service (like Gmail)

## What is an Email Service?

An email service is a platform that enables users to send, receive, store, and manage electronic messages over the internet.
At its core, an email service must handle the reliable delivery of messages between users, store emails for future access, support attachments, and provide search capabilities.
Modern email services also include spam filtering, labels/folders for organization, and synchronization across multiple devices.
**Popular Examples:** Gmail, Outlook, Yahoo Mail, ProtonMail
In this chapter, we will explore the **high-level design of an email service like Gmail**.
This problem combines multiple complex subsystems: messaging protocols, distributed storage, full-text search, and spam detection.
Lets start by clarifying the requirements:
# 1. Clarifying Requirements
Before starting the design, it's important to ask thoughtful questions to uncover hidden assumptions, clarify ambiguities, and define the system's scope more precisely.
Here is an example of how a discussion between the candidate and the interviewer might unfold:
**Candidate:** "What is the expected scale? How many users and emails per day should we support?"
**Interviewer:** "Let's design for 1 billion users with 100 million daily active users. Each user sends about 10 emails and receives about 40 emails per day on average."
**Candidate:** "Should we support attachments? If yes, what's the maximum size?"
**Interviewer:** "Yes, attachments are required. Let's limit them to 25 MB per email, similar to Gmail."
**Candidate:** "Do we need to support email search? How fast should it be?"
**Interviewer:** "Yes, users should be able to search their emails by sender, subject, and body content. Search results should appear within 1-2 seconds."
**Candidate:** "Should we support multiple devices and real-time synchronization?"
**Interviewer:** "Yes, users access email from web, mobile, and desktop clients. All should stay in sync."
**Candidate:** "Do we need spam filtering and virus scanning?"
**Interviewer:** "Yes, spam detection is critical. We should block or filter spam before it reaches the inbox."
**Candidate:** "What about features like labels, folders, and threaded conversations?"
**Interviewer:** "Labels and folders are important. Threaded conversations (grouping related emails) would be nice to have."
After gathering the details, we can summarize the key system requirements.

## 1.1 Functional Requirements
- **Send Email:** Users can compose and send emails to one or multiple recipients (To, CC, BCC).
- **Receive Email:** Users can receive emails from other users and external email providers.
- **Email Storage:** Store emails reliably with support for folders/labels (Inbox, Sent, Drafts, Spam, Trash).
- **Attachments:** Support file attachments up to 25 MB per email.
- **Search:** Users can search emails by sender, recipient, subject, and body content.
- **Sync Across Devices:** Changes (read/unread, delete, move) sync across all devices in real-time.

## 1.2 Non-Functional Requirements
- **High Availability:** The system must be highly available (99.99% uptime). Email is mission-critical for users.
- **Durability:** Zero data loss. Once an email is delivered, it must never be lost.
- **Low Latency:** Sending an email should complete within 2-3 seconds. Search results should appear within 1-2 seconds.
- **Scalability:** Handle billions of emails per day with 1 billion users.
- **Security:** Protect against spam, phishing, and malware. Support encryption in transit and at rest.

# 2. Back-of-the-Envelope Estimation
Before diving into the design, let's run some quick calculations to understand the scale we are dealing with. These numbers will guide our architectural decisions, particularly around storage, queuing, and database selection.

### 2.1 Traffic Estimates
Starting with the numbers from our requirements discussion:
**Email Volume**
We have 100 million daily active users. Each user sends about 10 emails and receives about 40 emails per day.
The 4:1 ratio between received and sent makes sense. Most received emails are automated: newsletters, notifications, marketing emails, and unfortunately, spam that makes it through filters.
**Queries Per Second (QPS)**
Let's convert daily volumes to QPS:
These are substantial numbers. We will need a robust queuing system to handle traffic spikes, especially during business hours when email activity peaks.
**Additional Operations**
Users do not just send and receive emails. They also fetch their inbox, search, and perform various actions:

### 2.2 Storage Estimates
Each email consists of metadata, content, and potentially attachments. Let's break down the storage requirements:
**Component Breakdown:**
- **Metadata:** Sender, recipients, timestamps, flags, labels, message IDs = roughly 2 KB
- **Email body and headers:** Varies widely, but average around 50 KB (includes HTML formatting)
- **Attachments:** About 20% of emails have attachments. Average attachment size is 500 KB. This contributes 0.2 × 500 KB = 100 KB to the average.

This gives us approximately 150 KB per email on average.
**Storage Growth:**
| Time Period | Total Emails | Storage Required | Notes |
| --- | --- | --- | --- |
| 1 Day | 4 billion | ~600 TB | Massive daily ingestion |
| 1 Month | 120 billion | ~18 PB | Need tiered storage |
| 1 Year | 1.5 trillion | ~220 PB | Archive old data |

A few observations from these numbers:
1. **Storage is massive:** 220 PB per year is not trivial. We need tiered storage where recent emails are on fast storage (SSD) and older emails move to cheaper cold storage.
2. **Attachments dominate:** Even though only 20% of emails have attachments, they contribute significantly to storage. Deduplication can help since many users receive the same attachment (like company newsletters).
3. **Per-user storage:** With 1 billion users and 220 PB, that is roughly 220 GB per user on average. But storage is heavily skewed. Most users have a few GB, while power users might have 50+ GB.

### 2.3 Bandwidth Estimates
Bandwidth determines how much data flows through our system:
Peak bandwidth could be 3x these numbers. We need network infrastructure that can handle 20+ GB/s sustained, with headroom for spikes.

### 2.4 Key Design Implications
These estimates reveal several important design decisions:
1. **Asynchronous processing is essential:** With 35,000+ peak send QPS, we cannot process emails synchronously. A message queue decouples submission from delivery.
2. **Tiered storage architecture:** We cannot keep 220 PB on SSD. Recent emails go on hot storage, older emails migrate to cold storage automatically.
3. **Search is a separate concern:** Searching across 1.5 trillion emails requires dedicated search infrastructure. The primary database cannot handle this.
4. **Caching is critical:** With 50,000 inbox fetch QPS, caching recent emails in memory dramatically reduces database load.

# 3. Core APIs
With our requirements and scale understood, let's define the API contract. Email APIs need to handle composing, sending, fetching, searching, and managing emails. 
Let's walk through the core endpoints.

### 3.1 Send Email

#### Endpoint: POST /api/v1/emails/send
This is the primary endpoint for composing and sending emails. It accepts the message content and recipient information, validates everything, and queues the email for delivery.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| to | string[] | Yes | List of recipient email addresses |
| cc | string[] | No | Carbon copy recipients (visible to all) |
| bcc | string[] | No | Blind carbon copy (hidden from others) |
| subject | string | Yes | Email subject line (max 998 characters per RFC) |
| body | object | Yes | Contains text (plain text) and html (rich formatting) |
| attachments | string[] | No | List of attachment IDs from prior uploads |
| reply_to_message_id | string | No | ID of email being replied to (for threading) |

#### Example Request:

#### Success Response (202 Accepted):
We return 202 (Accepted) rather than 201 (Created) because the email is queued for delivery, not yet delivered. The client can poll or receive a webhook when delivery completes.

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Invalid input | Malformed email addresses, empty subject/body |
| 413 Payload Too Large | Size exceeded | Total attachments exceed 25 MB |
| 429 Too Many Requests | Rate limited | User exceeded sending quota |
| 401 Unauthorized | Not authenticated | Missing or invalid auth token |

### 3.2 Fetch Emails (List Inbox)

#### Endpoint: GET /api/v1/emails
Retrieves a paginated list of emails from a specified folder. This is the most frequently called endpoint since users constantly check their inbox.

#### Query Parameters:
| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| folder | string | inbox | One of: inbox, sent, drafts, spam, trash, archive |
| label | string | - | Filter by user-defined label |
| page_token | string | - | Cursor for pagination |
| limit | int | 50 | Number of emails to return (max 100) |

#### Success Response (200 OK):
Notice we return a `snippet` (first ~100 characters of the body) rather than the full content. This keeps the response small for inbox listing. The full body is fetched separately when the user opens an email.

### 3.3 Get Email Details

#### Endpoint: GET /api/v1/emails/{email_id}
Returns the complete content of a specific email, including the full body and attachment metadata.

#### Success Response (200 OK):
The `download_url` for attachments is a time-limited signed URL that allows direct download from object storage without going through our API servers.

### 3.4 Search Emails

#### Endpoint: GET /api/v1/emails/search
Enables powerful search across all of a user's emails using a query language similar to Gmail's.

#### Query Parameters:
| Parameter | Type | Description |
| --- | --- | --- |
| query | string | Search query with optional operators |
| page_token | string | Cursor for pagination |
| limit | int | Number of results (default 20, max 50) |

#### Supported Search Operators:
| Operator | Example | Description |
| --- | --- | --- |
| from: | from:alice@example.com | Emails from specific sender |
| to: | to:bob@example.com | Emails to specific recipient |
| subject: | subject:invoice | Subject contains word |
| has:attachment | has:attachment | Emails with attachments |
| after: | after:2024/01/01 | Emails after date |
| before: | before:2024/06/30 | Emails before date |
| is:unread | is:unread | Unread emails only |
| label: | label:work | Emails with specific label |
| "exact phrase" | "quarterly report" | Exact phrase match |

#### Example Request:

#### Success Response:
The response includes `relevance_score` and `highlights` to help users understand why each result matched. Results are ordered by relevance, not just date.

### 3.5 Upload Attachment

#### Endpoint: POST /api/v1/attachments/upload
Uploads a file before associating it with an email. This allows users to attach files while composing without losing them if the browser crashes.

#### Request:
- Content-Type: `multipart/form-data`
- Body: File binary data

#### Success Response (201 Created):
Uploaded attachments are temporary until attached to a sent email. The `expires_at` field indicates when orphaned uploads will be cleaned up (typically 24 hours).

### 3.6 API Design Considerations
A few design decisions worth noting:
**Pagination:** We use cursor-based pagination (`page_token`) rather than offset-based (`page=2`). This handles the case where new emails arrive while the user is paginating, ensuring they do not miss messages or see duplicates.
**Idempotency:** The send endpoint should be idempotent to handle network retries. If a client submits the same request twice (same `idempotency_key` in headers), we return the same response without sending duplicate emails.
**Batch Operations:** For efficiency, we could add batch endpoints like `POST /api/v1/emails/batch/read` to mark multiple emails as read in one request. This reduces round trips when users select multiple messages.
# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complex diagram upfront, we will build the design incrementally, starting with the simplest flow and adding components as we encounter challenges. This mirrors how you would approach the problem in an interview.
Our email system needs to handle several distinct operations:
1. **Sending Emails:** Accept a message from a user and deliver it to the recipient.
2. **Receiving Emails:** Accept messages from external email servers and deliver to local users.
3. **Storing and Retrieving:** Store emails durably and fetch them quickly.
4. **Searching:** Enable fast full-text search across millions of emails.
5. **Syncing:** Keep email state synchronized across all devices in real-time.

Unlike typical web applications that only use HTTP, email systems rely on specialized protocols. SMTP handles the actual transmission of emails between servers, while IMAP and POP3 allow clients to retrieve emails. Understanding these protocols is essential for designing the system.
Let's build this architecture step by step, starting with sending emails.


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
        S1[Indexing Service]
        S2[Application Service]
        S3[sync Service]
        S4[Email Service]
        S5[Stateless Service]
    end

    subgraph Data Storage
        DBElasticsearch[Elasticsearch]
    end

    subgraph Caching Layer
        CacheRedis[Redis]
    end

    subgraph Message Queue
        QueueKafka[Kafka]
    end

    subgraph Object Storage
        StorageObjectstorage[Object storage]
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
    S1 --> DBElasticsearch
    S1 --> CacheRedis
    S1 --> QueueKafka
    S2 --> DBElasticsearch
    S2 --> CacheRedis
    S2 --> QueueKafka
    S3 --> DBElasticsearch
    S3 --> CacheRedis
    S3 --> QueueKafka
    S4 --> DBElasticsearch
    S4 --> CacheRedis
    S4 --> QueueKafka
    S5 --> DBElasticsearch
    S5 --> CacheRedis
    S5 --> QueueKafka
    S1 --> StorageObjectstorage
    S1 --> Storageobjectstorage
    S1 --> StorageObjectStorage
    S1 --> StorageS3
    StorageObjectstorage --> CDN
    Storageobjectstorage --> CDN
    StorageObjectStorage --> CDN
    StorageS3 --> CDN
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
        S2[Managed Service]
        S3[application Service]
        S4[Email Service]
        S5[sync Service]
    end

    subgraph Data Storage
        DBElasticsearch[Elasticsearch]
    end

    subgraph Caching Layer
        CacheRedis[Redis]
    end

    subgraph Message Queue
        QueueKafka[Kafka]
    end

    subgraph Object Storage
        StorageObjectStorage[Object Storage]
        StorageS3[S3]
        Storageobjectstorage[object storage]
        StorageObjectstorage[Object storage]
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
    S1 --> CacheRedis
    S1 --> QueueKafka
    S2 --> DBElasticsearch
    S2 --> CacheRedis
    S2 --> QueueKafka
    S3 --> DBElasticsearch
    S3 --> CacheRedis
    S3 --> QueueKafka
    S4 --> DBElasticsearch
    S4 --> CacheRedis
    S4 --> QueueKafka
    S5 --> DBElasticsearch
    S5 --> CacheRedis
    S5 --> QueueKafka
    S1 --> StorageObjectStorage
    S1 --> StorageS3
    S1 --> Storageobjectstorage
    S1 --> StorageObjectstorage
    StorageObjectStorage --> CDN
    StorageS3 --> CDN
    Storageobjectstorage --> CDN
    StorageObjectstorage --> CDN
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
        S1[Application Service]
        S2[Indexing Service]
        S3[Managed Service]
        S4[sync Service]
        S5[email Service]
    end

    subgraph Data Storage
        DBElasticsearch[Elasticsearch]
    end

    subgraph Caching Layer
        CacheRedis[Redis]
    end

    subgraph Message Queue
        QueueKafka[Kafka]
    end

    subgraph Object Storage
        StorageObjectstorage[Object storage]
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
    S1 --> DBElasticsearch
    S1 --> CacheRedis
    S1 --> QueueKafka
    S2 --> DBElasticsearch
    S2 --> CacheRedis
    S2 --> QueueKafka
    S3 --> DBElasticsearch
    S3 --> CacheRedis
    S3 --> QueueKafka
    S4 --> DBElasticsearch
    S4 --> CacheRedis
    S4 --> QueueKafka
    S5 --> DBElasticsearch
    S5 --> CacheRedis
    S5 --> QueueKafka
    S1 --> StorageObjectstorage
    S1 --> Storageobjectstorage
    S1 --> StorageObjectStorage
    S1 --> StorageS3
    StorageObjectstorage --> CDN
    Storageobjectstorage --> CDN
    StorageObjectStorage --> CDN
    StorageS3 --> CDN
    CDN --> Web
    CDN --> Mobile
```



## 4.1 Requirement 1: Sending Emails
When a user clicks "Send" on an email, several things need to happen. The message needs to be validated, stored in the sender's "Sent" folder, and then delivered to the recipient. The recipient could be another user on our platform (internal) or someone using a different provider like Yahoo or Outlook (external).

### Understanding SMTP
SMTP (Simple Mail Transfer Protocol) is the standard for sending emails between servers. It has been around since the 1980s and operates on port 25 for server-to-server communication or port 587 for client-to-server submission with authentication.
When you send an email, here is what happens at the protocol level:
The key insight is that email delivery is not instant. The recipient's server accepts the message and then delivers it to the user's mailbox. This can fail for various reasons (mailbox full, user does not exist, server down), which is why we need retry logic.

### Components for Sending Emails
Let me introduce each component:

#### API Gateway
Every request enters through the API Gateway, which handles cross-cutting concerns like SSL termination, authentication, rate limiting, and request validation. By centralizing these at the edge, we keep our application services focused on business logic.

#### API Server
The API server orchestrates the send flow. It validates the request (checking email addresses, size limits), stores the email in the sender's "Sent" folder, and publishes a delivery job to the message queue. The API server is stateless, allowing us to run multiple instances behind a load balancer.

#### Message Queue
Email delivery can take seconds or even minutes (if the recipient server is slow or requires retries). We do not want users waiting. The message queue decouples submission from delivery. The user gets an immediate response ("email queued"), and a background worker handles the actual delivery.

#### Outbound SMTP Service
This service picks up jobs from the queue and performs the actual SMTP delivery. It looks up the recipient's mail server via DNS (MX records), establishes an SMTP connection, and transmits the message. If delivery fails temporarily (server busy, rate limited), it retries with exponential backoff.

#### DNS Resolver
To send an email to , we need to find Gmail's mail servers. This is done by querying DNS for MX (Mail Exchanger) records. For `gmail.com`, this returns servers like `gmail-smtp-in.l.google.com`.

### The Send Flow Step by Step
Let me walk through this flow:
1. **User submits email:** The client sends a POST request with recipients, subject, body, and attachments.
2. **Validation:** The API server validates email addresses, checks that attachments do not exceed 25 MB, and verifies the user is not rate-limited.
3. **Storage:** The email body is stored in blob storage, and metadata (sender, recipients, timestamps) goes into the database. The email now appears in the sender's "Sent" folder.
4. **Queueing:** A delivery job is published to the message queue. The user receives a response immediately since we do not wait for delivery.
5. **SMTP Delivery:** A worker picks up the job, looks up the recipient's mail server, and attempts delivery via SMTP.
6. **Handling failures:** If delivery fails temporarily (server busy), the job is re-queued with exponential backoff. If it fails permanently (user does not exist), we generate a bounce notification to inform the sender.

**Why store before queueing?** If queueing fails, we have the email stored and can retry. If storage fails, we tell the user immediately. This ordering makes the system more resilient to partial failures.

## 4.2 Requirement 2: Receiving Emails
Our system needs to accept emails from external senders. When someone from Yahoo or Outlook sends an email to a user on our platform, their mail server connects to ours and delivers the message via SMTP.
This is where security becomes critical. Over 50% of all email traffic is spam. Without proper filtering, users' inboxes would be unusable.

### Additional Components for Receiving

#### Inbound SMTP Service
Listens on port 25 for incoming SMTP connections from other mail servers. When an external server connects, we verify the recipient exists, perform security checks, and either accept or reject the message.
**Authentication Verification (SPF/DKIM/DMARC)**
These protocols help verify that the sender is who they claim to be:
- **SPF (Sender Policy Framework):** Checks if the sending server is authorized to send for the domain
- **DKIM (DomainKeys Identified Mail):** Verifies a cryptographic signature to ensure the email was not tampered with
- **DMARC (Domain-based Message Authentication):** Combines SPF and DKIM with a policy for handling failures

Emails that fail authentication checks are likely spoofed and get flagged or rejected.

#### Spam Filter
Analyzes the email content, sender reputation, and patterns to determine if it is spam. This uses a combination of rule-based filtering and machine learning models trained on billions of emails.

#### Virus Scanner
Scans attachments for malware. Emails with detected viruses are quarantined or rejected outright.

### The Receive Flow Step by Step
Here is what happens when an external server delivers an email:
1. **SMTP handshake:** The external server connects and identifies itself. It specifies the sender (`MAIL FROM`) and recipient (`RCPT TO`).
2. **Recipient verification:** We check if the recipient exists in our system. If not, we reject immediately with "550 User not found."
3. **Receive content:** The external server transmits the email content (headers, body, attachments).
4. **Authentication:** We verify SPF, DKIM, and DMARC. Failures are logged and affect the spam score.
5. **Spam filtering:** The email passes through our spam filter. High-confidence spam goes to the Spam folder. Borderline cases are delivered with a warning.
6. **Virus scanning:** Attachments are scanned. Infected emails are quarantined.
7. **Storage:** Clean emails are stored. Metadata goes to the database, body and attachments to blob storage.
8. **Notification:** The sync service pushes a notification to all of the user's connected devices.

## 4.3 Requirement 3: Storing and Retrieving Emails
Users accumulate years of emails. A typical user might have 50,000 emails spanning a decade. Power users can have millions. We need to store these emails durably while enabling fast retrieval and organization via folders and labels.

### Storage Architecture
Emails have two distinct parts with different access patterns:
- **Metadata:** Small, frequently accessed, needs complex queries (filter by folder, label, date)
- **Content:** Large, accessed less frequently (only when user opens email), simple retrieval by ID

This suggests a hybrid storage approach:
**Metadata Database (CockroachDB/Spanner)**
Stores email headers and state. We need:
- Fast point lookups by email ID
- Efficient filtering by folder, label, read status
- Range queries by date for pagination
- Strong consistency for operations like "mark as read"

A distributed SQL database gives us the query flexibility of SQL with horizontal scalability.
**Blob Storage (Tiered)**
Email bodies and attachments go to object storage. We use tiered storage to optimize costs:
- **Hot tier:** Emails from the last 30 days on SSD-backed storage for fast access
- **Cold tier:** Older emails on cheaper HDD-based storage

The application transparently fetches from the appropriate tier based on email age.
**Cache Layer (Redis)**
Recent inbox data is cached in Redis. When a user opens their inbox, we first check the cache. This handles the common pattern of users repeatedly checking their inbox.

### The Fetch Flow
Two key optimizations here:
1. **List vs Detail:** When listing inbox, we return only metadata (sender, subject, snippet). The full body is fetched separately when the user opens an email. This keeps inbox loading fast.
2. **Caching:** Recently accessed emails are cached. Opening the same email twice does not hit the database.

## 4.4 Requirement 4: Search
Users expect to search through years of emails and find specific messages in seconds. Searching "from:alice invoice 2023" across 100,000 emails cannot be done with database queries. We need dedicated search infrastructure.

### Why Not Search the Database Directly?
SQL `LIKE '%keyword%'` queries are terrible for full-text search:
- Full table scan on every query
- No relevance ranking
- Cannot handle complex queries with multiple operators

With 1.5 trillion emails across all users, database-based search would be impossibly slow.

### Search Architecture

#### Elasticsearch Cluster
We use Elasticsearch, which is designed for full-text search at scale. Each email is indexed with:

#### Indexing Service
Processes new emails asynchronously and updates the search index. We use near-real-time indexing. New emails become searchable within a few seconds of delivery.

### Search Flow
The search process:
1. **Parse query:** Convert the user's query into Elasticsearch query DSL. Handle operators like `from:`, `to:`, `subject:`.
2. **Execute search:** Query Elasticsearch with the user's ID as a filter (users can only search their own emails).
3. **Fetch fresh metadata:** Search results might include emails whose metadata has changed (marked as read, moved). We fetch current metadata from the database.
4. **Return results:** Results are ranked by relevance, with recent emails getting a boost.

## 4.5 Requirement 5: Real-Time Sync
When a user reads an email on their phone, it should appear as read on their laptop within seconds. When they delete an email on their desktop, it should disappear from their tablet. This requires real-time synchronization across devices.

### Components for Real-Time Sync

#### WebSocket Gateway
Maintains persistent WebSocket connections with client devices. Unlike HTTP, WebSocket connections stay open, allowing the server to push updates to clients instantly.

#### Connection Registry (Redis)
Tracks which devices are connected and to which gateway server. When we need to notify a user, we look up their connected devices and route the message to the correct gateway servers.

#### Event Stream (Kafka)
All email operations (new email, read, delete, move) publish events to Kafka. The sync service consumes these events and broadcasts them to connected devices.

#### Sync Service
Orchestrates the sync process:
- Consumes events from the event stream
- Looks up connected devices for the affected user
- Publishes updates through the WebSocket gateway
- Handles offline sync when devices reconnect

### Sync Flow
When a user marks an email as read on their phone:
1. The phone sends the API request
2. The API updates the database and publishes an event
3. The sync service picks up the event
4. It looks up all connected devices for that user
5. It sends updates to all devices except the one that initiated the change
6. Other devices update their UI immediately

**Handling Offline Devices:**
When a device reconnects after being offline, it needs to catch up on missed changes. We track the last sync timestamp for each device. On reconnection, we send all changes since that timestamp.

## 4.6 Putting It All Together
Now let's step back and see the complete architecture with all components working together.
The architecture follows a layered approach with clear responsibilities:
**Client Layer:** Users interact through web browsers, mobile apps, or desktop clients. All clients use the same APIs.
**Edge Layer:** CDN caches static assets (JavaScript, CSS, images). Load balancer distributes traffic across gateway instances.
**Gateway Layer:** API Gateway handles HTTP requests with authentication and rate limiting. WebSocket Gateway maintains persistent connections for real-time sync.
**Application Services:** Stateless services that implement business logic. Each can scale horizontally.
**Processing Layer:** Message queue decouples operations. Spam and virus filters protect incoming emails.
**Storage Layer:** Metadata database for structured queries, blob storage for content, cache for performance, Elasticsearch for search.
**External Systems:** DNS for mail server discovery, communication with external email providers via SMTP.

### Component Responsibilities
| Component | Primary Responsibility | Scaling Strategy |
| --- | --- | --- |
| CDN | Static asset caching, DDoS protection | Managed service (auto-scales) |
| Load Balancer | Traffic distribution, health checks | Managed service |
| API Gateway | Auth, rate limiting, routing | Horizontal (add instances) |
| API Servers | Email operations, business logic | Horizontal (stateless) |
| Outbound SMTP | Email delivery to external servers | Horizontal with IP pooling |
| Inbound SMTP | Accept emails from external servers | Horizontal with MX records |
| Sync Service | Real-time device synchronization | Horizontal with partitioning |
| Spam Filter | Spam detection and filtering | Horizontal (stateless ML inference) |
| Message Queue | Async processing, event streaming | Partition-based (Kafka) |
| Metadata DB | Email metadata, user state | Read replicas, then sharding |
| Blob Storage | Email bodies, attachments | Managed service (auto-scales) |
| Elasticsearch | Full-text search | Cluster scaling (add nodes) |
| Redis Cache | Hot data caching, connection registry | Redis Cluster |

# 5. Database Design
With the high-level architecture in place, let's zoom into the data layer. The choice of database and schema design directly impacts query performance, scalability, and operational complexity.

## 5.1 Choosing the Right Database
Email systems have diverse data access patterns. Let's think through what we need:
**What we need to store:**
- Billions of emails across hundreds of millions of users
- Each email has metadata (~2 KB) and content (~50-150 KB)
- Users can have millions of emails accumulated over years

**How we access the data:**
- Point lookups by email ID (most common)
- List queries filtered by folder, label, read status
- Range queries by date for pagination
- Full-text search across email content

**Consistency requirements:**
- Strong consistency for user actions (mark as read, delete)
- Users should see changes immediately on the device that made them

Given these requirements, we use a hybrid approach:

### Why Distributed SQL for Metadata?
- **Complex queries:** Filter by folder, label, date range, read status, all in one query
- **Strong consistency:** ACID transactions for reliable state changes
- **Horizontal scaling:** CockroachDB/Spanner scale to petabytes while maintaining SQL semantics
- **Familiar:** SQL is well-understood, good tooling and ORM support

### Why Object Storage for Content?
- **Cost:** Object storage costs pennies per GB versus dollars for database storage
- **Scale:** S3/GCS handle petabytes without special configuration
- **Durability:** 99.999999999% (11 nines) durability
- **Simplicity:** Content is accessed by ID only. We do not need to query it.

## 5.2 Database Schema

### Users Table
Stores account information and tracks storage quotas.
| Field | Type | Description |
| --- | --- | --- |
| user_id | UUID (PK) | Unique identifier |
| email_address | VARCHAR (Unique) | User's primary email address |
| password_hash | VARCHAR | bcrypt hash of password |
| display_name | VARCHAR | Name shown to other users |
| storage_used | BIGINT | Current storage usage in bytes |
| storage_limit | BIGINT | Storage quota (e.g., 15 GB) |
| created_at | TIMESTAMP | Account creation time |

### Emails Table
The core table storing email metadata. Notice we do not store the body here. Just a reference to blob storage.
| Field | Type | Description |
| --- | --- | --- |
| email_id | UUID (PK) | Unique identifier |
| user_id | UUID (FK) | Owner of this email |
| thread_id | UUID (FK) | Conversation thread ID (self-reference) |
| folder | ENUM | inbox, sent, drafts, spam, trash, archive |
| from_address | VARCHAR | Sender's email address |
| to_addresses | VARCHAR[] | Array of recipient addresses |
| cc_addresses | VARCHAR[] | Array of CC addresses |
| subject | VARCHAR | Email subject line (indexed) |
| snippet | VARCHAR | First ~100 chars of body for preview |
| body_blob_id | VARCHAR | Reference to body in blob storage |
| has_attachments | BOOLEAN | Quick check without joining |
| is_read | BOOLEAN | Read/unread status |
| is_starred | BOOLEAN | Starred/important flag |
| received_at | TIMESTAMP | When email was received |
| created_at | TIMESTAMP | When record was created |

**Indexes:**

### Attachments Table
Stores attachment metadata. The actual files live in object storage.
| Field | Type | Description |
| --- | --- | --- |
| attachment_id | UUID (PK) | Unique identifier |
| email_id | UUID (FK) | Parent email |
| filename | VARCHAR | Original filename |
| content_type | VARCHAR | MIME type (application/pdf, image/jpeg) |
| size | BIGINT | File size in bytes |
| blob_id | VARCHAR | Reference in object storage |
| checksum | VARCHAR | SHA-256 hash for deduplication |

The `checksum` field enables deduplication. If two users receive the same attachment, we store it once.

### Labels Table
User-defined labels for organization.
| Field | Type | Description |
| --- | --- | --- |
| label_id | UUID (PK) | Unique identifier |
| user_id | UUID (FK) | Owner of the label |
| name | VARCHAR | Label name (e.g., "Work", "Personal") |
| color | VARCHAR | Display color (hex code) |
| created_at | TIMESTAMP | Creation time |

# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often go deeper into specific components. 
In this section, we will explore the trickiest parts: email delivery and protocols, spam detection, search infrastructure, attachment handling, and high availability.

## 6.1 Email Delivery and SMTP
Understanding how emails actually travel across the internet is fundamental. The process involves multiple servers and protocols, with many opportunities for failure.

### The Email Delivery Pipeline
When you send an email, it passes through several stages, each handled by different software components:
- **MUA (Mail User Agent):** Your email client (Gmail web, Outlook app, Apple Mail)
- **MSA (Mail Submission Agent):** Accepts emails from authenticated clients (port 587)
- **MTA (Mail Transfer Agent):** Routes and transfers emails between servers (port 25)
- **MDA (Mail Delivery Agent):** Places emails into the recipient's mailbox

### SMTP Conversation Example
Here is a simplified view of what happens at the protocol level when our server delivers an email to Gmail:

### Delivery Strategies
We have two main approaches for handling email delivery:
**Synchronous Delivery**
Attempt delivery immediately when the user clicks "Send."
| Pros | Cons |
| --- | --- |
| Simple implementation | Slow user experience (seconds wait) |
| Immediate feedback on failure | Blocks server resources |
|  | No automatic retry |

**Asynchronous Queue-Based Delivery (Recommended)**
Queue the email immediately and process in the background.
| Pros | Cons |
| --- | --- |
| Fast response (milliseconds) | No immediate delivery confirmation |
| Built-in retry mechanism | More complex implementation |
| Handles traffic spikes gracefully | Need to track delivery status |
| Better resource utilization |  |

### Handling Delivery Failures
Emails fail to deliver for many reasons. Our retry strategy must distinguish between temporary and permanent failures:
**Retry Schedule:**
| Attempt | Wait Time | Cumulative |
| --- | --- | --- |
| 1 | Immediate | 0 |
| 2 | 5 minutes | 5 min |
| 3 | 30 minutes | 35 min |
| 4 | 2 hours | 2h 35m |
| 5 | 8 hours | 10h 35m |
| 6 | 24 hours | 34h 35m |
| 7 (final) | 48 hours | 82h 35m |

After exhausting retries, we generate a bounce notification (Non-Delivery Report) to inform the sender that their email could not be delivered.

## 6.2 Spam Detection
Spam accounts for over 50% of global email traffic. Without robust spam detection, users' inboxes would be unusable. Our spam filter must catch malicious emails while minimizing false positives (blocking legitimate emails).

### Multi-Layer Spam Detection Pipeline
We use multiple layers of filtering, each catching different types of spam:

### Layer 1: Connection-Level Filtering
Before accepting the email content, we check the sender's reputation:
- **IP Blocklists:** Check against services like Spamhaus, Barracuda, and SpamCop
- **Rate Limiting:** Block IPs sending unusually high volumes
- **Reverse DNS:** Verify the sending server has valid PTR records
- **Greylisting:** Temporarily reject first-time senders (legitimate servers retry, spam bots often do not)

### Layer 2: Email Authentication
Verify the sender is authorized to send from their claimed domain:
**SPF (Sender Policy Framework):**
- The sending domain publishes a list of authorized servers in DNS
- We check if the sending IP is on that list
- Example: `v=spf1 include:_spf.google.com ~all`

**DKIM (DomainKeys Identified Mail):**
- The sender cryptographically signs the email
- We verify the signature using the public key in DNS
- Proves the email was not modified in transit

**DMARC (Domain-based Message Authentication):**
- Combines SPF and DKIM results
- Tells us what to do when checks fail (none, quarantine, reject)
- Provides reporting back to the domain owner

### Layer 3: Content Analysis
Analyze the email content for spam indicators:
- **Keyword matching:** Known spam phrases ("act now", "limited time", "click here")
- **URL analysis:** Check links against known phishing/malware databases
- **Attachment scanning:** Block dangerous file types (.exe, .bat, .scr)
- **HTML analysis:** Check for invisible text, deceptive links
- **Header analysis:** Look for forged or suspicious headers

### Layer 4: Machine Learning Classification
Modern spam filters use ML models trained on billions of emails:
**Features considered:**
- Sender reputation score and history
- Email structure (HTML/text ratio, image-to-text ratio)
- Link characteristics (shortened URLs, mismatched anchor text)
- Historical user interactions (do similar emails get marked as spam?)
- Content embeddings from language models

**Models commonly used:**
- **Logistic Regression:** Fast, interpretable, good baseline
- **Gradient Boosting:** Higher accuracy, handles many features well
- **Neural Networks:** Best accuracy, captures complex patterns

### Summary of Spam Detection Layers
| Layer | Techniques | Catches |
| --- | --- | --- |
| Connection | IP blocklists, rate limiting, greylisting | Botnets, known spammers |
| Authentication | SPF, DKIM, DMARC | Spoofed senders, phishing |
| Content | Keywords, URL scanning, attachment types | Scams, malware |
| ML Model | Behavioral patterns, content analysis | Sophisticated spam |

## 6.3 Email Search Architecture
Users expect to search through years of emails and find specific messages in seconds. With users potentially having millions of emails, this requires dedicated search infrastructure.

### Why Elasticsearch?
Elasticsearch is purpose-built for full-text search at scale:
- **Inverted indexes:** Maps terms to documents for fast lookups
- **Relevance scoring:** Ranks results by how well they match the query
- **Complex queries:** Supports operators, filters, and boolean logic
- **Horizontal scaling:** Distributes data across nodes automatically

### Index Design
Each email is indexed as a document with searchable fields:

### Search Query Translation
User queries are translated into Elasticsearch query DSL:
| User Query | Elasticsearch Query |
| --- | --- |
| invoice | Full-text search on all fields |
| from:alice | Term filter on from field |
| subject:meeting | Match on subject field |
| has:attachment | Filter where has_attachment = true |
| after:2024/01/01 | Range filter on received_at |
| "quarterly report" | Phrase match on all text fields |

### Indexing Strategy
**Near Real-Time Indexing:**
We use asynchronous indexing for better performance:
1. New email is stored in the database
2. An event is published to Kafka
3. Indexing workers consume events and update Elasticsearch
4. New emails become searchable within 1-5 seconds

### Performance Optimizations
**User-Based Sharding:** Partition the Elasticsearch index by user_id. Each search only needs to query one user's data, dramatically reducing search time.
**Field-Specific Analyzers:**
- Email addresses: Use keyword analyzer (exact match)
- Subject/body: Use standard analyzer with stemming
- Dates: Use date type for range queries

**Result Caching:** Cache frequent search queries in Redis. Many users search for the same things repeatedly ("from:boss", "is:unread").

## 6.4 Attachment Handling
Attachments are the largest component of email storage and pose unique security challenges.

### Storage Strategy
**Deduplication:**
Many users receive identical attachments (company newsletters, shared documents). We deduplicate by content hash:
1. Calculate SHA-256 hash of file content
2. Check if hash exists in storage
3. If yes, reference the existing blob (save storage)
4. If no, store the new blob

This typically saves 20-40% of attachment storage.
**Tiered Storage:**
Move old attachments to cheaper storage tiers:
| Age | Storage Tier | Access Latency | Cost |
| --- | --- | --- | --- |
| < 30 days | Hot (SSD) | < 50ms | $$$ |
| 30-365 days | Warm (HDD) | < 200ms | $$ |
| > 1 year | Cold (Glacier) | Minutes | $ |

### Security Measures
1. **Virus Scanning:** Scan all attachments with multiple antivirus engines
2. **File Type Blocking:** Block dangerous types (.exe, .bat, .js, .vbs)
3. **Size Limits:** Enforce 25 MB per email
4. **Signed URLs:** Use time-limited URLs for downloads
5. **Content-Type Verification:** Verify MIME type matches actual content (prevent disguised executables)

### Download Flow
We use signed URLs so clients download directly from object storage/CDN, avoiding load on our API servers for large file transfers.

## 6.5 High Availability and Disaster Recovery
Email is mission-critical infrastructure. Users depend on it for work, banking, and important notifications. We target 99.99% availability, meaning less than 53 minutes of downtime per year.

### Multi-Region Architecture
Deploy the email service across multiple geographic regions for redundancy:
**Within Region:**
- Multiple availability zones for server redundancy
- Synchronous replication for strong consistency
- Automatic failover for database primary

**Across Regions:**
- Asynchronous replication (< 1 second lag typically)
- Global DNS for geographic routing
- Manual or automated failover for regional disasters

### Failure Scenarios and Mitigations
| Failure | Impact | Mitigation | Recovery Time |
| --- | --- | --- | --- |
| Single server | None | Load balancer routes to healthy servers | Instant |
| Database primary | Brief pause | Automatic failover to replica | < 30 seconds |
| Single AZ | Reduced capacity | Traffic shifts to other AZs | Instant |
| Entire region | Regional outage | DNS failover to other regions | 1-5 minutes |
| Blob storage | Attachments unavailable | Multi-region replication | N/A (auto-healed) |

### Backup Strategy
1. **Continuous Backup:** Stream database changes to backup storage in near real-time
2. **Point-in-Time Recovery:** Ability to restore to any point in the last 30 days
3. **Daily Snapshots:** Full backups stored in a separate region
4. **Regular Testing:** Monthly disaster recovery drills to verify procedures work

### Monitoring and Alerting
Critical metrics to monitor:
| Metric | Warning Threshold | Critical Threshold |
| --- | --- | --- |
| Delivery queue depth | > 10,000 | > 50,000 |
| Send success rate | < 99% | < 95% |
| API error rate | > 0.5% | > 2% |
| P99 latency | > 2s | > 5s |
| Storage utilization | > 80% | > 90% |
| Spam filter accuracy | < 99% | < 95% |

Alert on-call engineers immediately for critical thresholds. Warning thresholds trigger investigation during business hours.
# References
- [RFC 5321 - Simple Mail Transfer Protocol](https://datatracker.ietf.org/doc/html/rfc5321) - The official SMTP specification
- [Email Authentication: SPF, DKIM and DMARC - Cloudflare](https://www.cloudflare.com/learning/email-security/dmarc-dkim-spf/) - Understanding email authentication protocols

# Quiz

## Design Gmail Quiz
In a Gmail-like system, which component is best suited to decouple the 'Send Email' API from downstream work like spam checks and recipient fan-out?