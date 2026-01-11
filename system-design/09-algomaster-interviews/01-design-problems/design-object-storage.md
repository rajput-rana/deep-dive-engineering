# Design Object Storage (like S3)

Object storage is a data storage architecture that manages data as discrete units called **objects**, rather than as files in a hierarchy or blocks on a disk. Each object contains the data itself, metadata describing the object, and a unique identifier.
Unlike traditional file systems that organize data in directories and subdirectories, object storage uses a flat namespace where every object is accessed via its unique key. This architecture enables massive scalability, as the system can store billions of objects without the limitations of hierarchical file systems.
**Popular Examples:** [Amazon S3](https://aws.amazon.com/s3/), [Google Cloud Storage](https://cloud.google.com/storage), [Azure Blob Storage](https://azure.microsoft.com/en-us/products/storage/blobs), [MinIO](https://min.io/)
This system design problem touches on so many fundamental concepts: distributed storage, data durability, consistency models, replication strategies, and large-scale data management.
The challenge is not just storing bytes, it is storing them reliably across hardware that will inevitably fail, at a scale that spans petabytes, while serving thousands of requests per second.
In this article, we will explore the **high-level design of an object storage system like Amazon S3**.
Let's start by clarifying the requirements:
# 1. Clarifying Requirements
Before starting the design, it's important to ask thoughtful questions to uncover hidden assumptions, clarify ambiguities, and define the system's scope more precisely.
Here is an example of how a discussion between the candidate and the interviewer might unfold:
**Candidate:** "What is the expected scale? How much data do we need to store?"
**Interviewer:** "Let's design for storing hundreds of petabytes of data, with billions of objects."
**Candidate:** "What are the typical object sizes we need to support?"
**Interviewer:** "Objects can range from a few bytes to several terabytes. Most objects are between 1 KB and 100 MB, but we should support large files up to 5 TB."
**Candidate:** "What durability guarantees do we need?"
**Interviewer:** "We need 99.999999999% (11 nines) durability. Data loss is unacceptable."
**Candidate:** "What consistency model should we provide?"
**Interviewer:** "Strong consistency for all operations. After a successful write, subsequent reads should return the latest data."
**Candidate:** "Should we support versioning of objects?"
**Interviewer:** "Yes, versioning is a required feature. Users should be able to retrieve previous versions of objects."
**Candidate:** "Do we need to organize objects into logical containers?"
**Interviewer:** "Yes, we need the concept of buckets to organize objects and apply policies."
After gathering the details, we can summarize the key system requirements.

## 1.1 Functional Requirements
Based on the discussion, here are the core features our system must support:
- **Create Bucket:** Users can create logical containers to organize their objects.
- **Upload Object:** Store an object with a unique key within a bucket.
- **Download Object:** Retrieve an object by its bucket and key.
- **Delete Object:** Remove an object from storage.
- **List Objects:** List objects within a bucket with optional prefix filtering.
- **Versioning:** Maintain multiple versions of objects.
- **Multipart Upload:** Support uploading large objects in parts.

## 1.2 Non-Functional Requirements
Beyond features, we need to consider the qualities that make the system production-ready:
- **High Durability:** 99.999999999% (11 nines) durability, meaning for 10 million objects, lose at most 1 object per 10,000 years.
- **High Availability:** 99.99% availability for read and write operations, which translates to roughly 52 minutes of downtime per year.
- **Scalability:** Scale to hundreds of petabytes and billions of objects.
- **Low Latency:** First-byte latency under 100ms for reads.
- **Strong Consistency:** Read-after-write consistency for all operations.

# 2. Back-of-the-Envelope Estimation
Before diving into the design, let's run some quick calculations to understand the scale we are dealing with. These numbers will guide our architectural decisions, particularly around storage infrastructure, network capacity, and database sizing.

### 2.1 Storage Estimates
Starting with storage, let's work with concrete numbers:
- **Total storage capacity:** 100 PB (100,000 TB). This is a realistic target for a large-scale object storage service.
- **Average object size:** 1 MB. In practice, object sizes follow a bimodal distribution: many small objects (configs, thumbnails) and fewer large objects (videos, backups). A 1 MB weighted average is reasonable.
- **Total objects:** 100 PB / 1 MB = **100 billion objects**

One hundred billion is a massive number. If we stored one object record per row in a database, we would need careful schema design and indexing to keep queries fast.

### 2.2 Traffic Estimates
Now let's estimate the request volume:

#### Write Traffic (Object Uploads)
Assuming 100 million new objects uploaded per day:
Traffic is never uniform. During peak hours, we might see 3x the average load:

#### Read Traffic (Object Downloads)
Object storage is typically read-heavy. With a 10:1 read-to-write ratio:

### 2.3 Bandwidth Estimates
Bandwidth is critical for object storage since we are moving large amounts of data:
360 GB/s of read bandwidth is substantial. This is roughly 2.9 Tbps (terabits per second). A single data center might struggle to handle this, which is why object storage systems distribute load across multiple regions and use CDN caching for hot objects.

### 2.4 Metadata Storage
Each object requires metadata to track its location, versions, and properties:
| Field | Size | Notes |
| --- | --- | --- |
| Bucket name | ~64 bytes | Limited to 63 characters |
| Object key | ~256 bytes | Can be up to 1024 characters |
| Version ID | ~32 bytes | UUID for each version |
| Size, timestamps, checksums | ~100 bytes | Content-Length, Last-Modified, ETag |
| Storage locations | ~50 bytes | Pointers to data chunks |
| Total | ~500 bytes | Per object version |

For 100 billion objects:
50 TB of metadata is manageable with a distributed database, but we need to think carefully about indexing and query patterns.

### 2.5 Replication and Raw Storage
To achieve 11 nines durability, we cannot store data in just one place. We need redundancy:

#### With 3-way replication:

#### With erasure coding (more efficient):
Erasure coding trades compute for storage efficiency. We will explore this trade-off in the deep dive section.

### 2.6 Key Insights
These estimates reveal several important design implications:
1. **Read-heavy workload:** With 10x more reads than writes, we should invest in caching and optimize for fast retrieval.
2. **Massive metadata:** 50 TB of metadata across 100 billion rows requires a distributed database with careful sharding.
3. **Bandwidth is the bottleneck:** 360 GB/s of peak read bandwidth cannot be served from a single location. Geographic distribution is essential.
4. **Durability requires redundancy:** Whether through replication or erasure coding, we need to store significantly more raw data than the logical data size.

# 3. Core APIs
With our requirements and scale understood, let's define the API contract. Object storage APIs follow REST conventions, using HTTP methods to indicate the operation type. The design is intentionally simple: buckets contain objects, objects are identified by keys, and every operation maps cleanly to a URL path.
We will design APIs for two categories: bucket operations (create, delete, configure) and object operations (upload, download, delete, list). Let's walk through each one.

### 3.1 Create Bucket

#### Endpoint: PUT /{bucket-name}
Buckets are the top-level containers for objects. Before storing any data, users must create a bucket. Bucket names are globally unique across the entire system, which means no two users anywhere can have a bucket with the same name.

#### Request Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| bucket-name | path | Yes | Globally unique name (3-63 chars, lowercase, alphanumeric and hyphens) |
| region | header | No | Geographic region where the bucket should be created |
| versioning | header | No | Enable versioning from the start (default: disabled) |

#### Success Response (200 OK):

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 409 Conflict | Name taken | Another user already owns a bucket with this name |
| 400 Bad Request | Invalid name | Name does not meet naming requirements |
| 403 Forbidden | Limit exceeded | User has reached their bucket quota |

### 3.2 Upload Object

#### Endpoint: PUT /{bucket-name}/{object-key}
This is the most frequently used endpoint for writing data. The object key can include "/" characters to simulate a folder structure, even though the storage is flat underneath.

#### Request Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| bucket-name | path | Yes | Target bucket name |
| object-key | path | Yes | Unique identifier within the bucket (up to 1024 chars) |
| Content-MD5 | header | No | Base64-encoded MD5 hash for server-side integrity check |
| Content-Type | header | No | MIME type of the object (e.g., "image/png") |
| x-amz-meta-* | header | No | Custom metadata as key-value pairs |

**Request Body:** The raw bytes of the object data.

#### Success Response (200 OK):
The ETag is typically the MD5 hash of the object, which clients can use to verify upload integrity. The VersionId is only returned if versioning is enabled on the bucket.

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 404 Not Found | Bucket missing | The specified bucket does not exist |
| 400 Bad Request | Too large | Object exceeds size limit for single upload (5 GB) |
| 403 Forbidden | Access denied | User lacks permission to write to this bucket |

### 3.3 Download Object

#### Endpoint: GET /{bucket-name}/{object-key}
Retrieves an object from storage. This endpoint supports partial downloads through range requests, which is essential for video streaming and resumable downloads.

#### Request Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| bucket-name | path | Yes | Bucket containing the object |
| object-key | path | Yes | The object's unique key |
| versionId | query | No | Retrieve a specific version instead of the latest |
| Range | header | No | Byte range for partial download (e.g., "bytes=0-999") |

#### Success Response (200 OK or 206 Partial Content):

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 404 Not Found | Object missing | Object or bucket does not exist |
| 416 Range Not Satisfiable | Bad range | Requested byte range exceeds object size |

### 3.4 Delete Object

#### Endpoint: DELETE /{bucket-name}/{object-key}
Removes an object from the bucket. The behavior differs based on versioning settings.

#### Request Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| bucket-name | path | Yes | Bucket containing the object |
| object-key | path | Yes | Object to delete |
| versionId | query | No | Delete a specific version (permanent deletion) |

#### Success Response (204 No Content):
When versioning is enabled and no version ID is specified, the system creates a "delete marker" instead of actually removing data. The object appears deleted to normal GET requests, but all previous versions remain accessible. To permanently delete, you must specify the version ID.

### 3.5 List Objects

#### Endpoint: GET /{bucket-name}?list-type=2
Lists objects in a bucket with optional filtering. This is how users browse their stored data and how applications discover objects matching a pattern.

#### Request Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| prefix | query | No | Filter to objects starting with this prefix |
| max-keys | query | No | Maximum objects to return (default: 1000, max: 1000) |
| continuation-token | query | No | Token for fetching the next page |
| delimiter | query | No | Character to group keys (typically "/" for folder simulation) |

#### Success Response (200 OK):
When `IsTruncated` is true, use `NextContinuationToken` to fetch the next page of results.

### 3.6 Multipart Upload APIs
For objects larger than 5 GB (or when you want parallel uploads), multipart upload breaks the object into smaller pieces. This requires three API calls: initiate, upload parts, and complete.

#### Initiate Multipart Upload: POST /{bucket-name}/{object-key}?uploads
Starts a new multipart upload session and returns an upload ID.
**Upload Part:** `PUT /{bucket-name}/{object-key}?partNumber={n}&uploadId={id}`
Uploads a single part (5 MB to 5 GB each). Parts can be uploaded in parallel and in any order.
| Parameter | Required | Description |
| --- | --- | --- |
| partNumber | Yes | Part number (1 to 10,000) |
| uploadId | Yes | The session ID from initiate |

Returns an ETag for the uploaded part.
**Complete Multipart Upload:** `POST /{bucket-name}/{object-key}?uploadId={id}`
Finalizes the upload by providing the list of parts and their ETags.
The system verifies all parts exist, concatenates them in order, and creates the final object. If any part is missing or ETags do not match, the request fails.
# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complex diagram upfront, we will build the design incrementally, starting with the simplest possible solution and adding components as we encounter challenges. This mirrors how you would approach the problem in an interview.
Our system needs to handle two fundamental paths:
1. **Write Path:** Accept object data, store it durably across multiple locations, and record metadata so we can find it later.
2. **Read Path:** Look up where an object lives, retrieve its data, and return it to the client as quickly as possible.

The fundamental insight that drives our architecture is that **metadata and data have fundamentally different characteristics**. Metadata is small (a few hundred bytes per object) but accessed on every single request. Data is large (potentially gigabytes per object) but only accessed when specifically requested. This separation allows us to optimize each path independently.
Notice the order: on writes, we store data before metadata. On reads, we fetch metadata before data. This ordering is intentional and ensures consistency, which we will explain as we dive deeper.
Let's build the architecture step by step, starting with the basic upload and download flows.

## 4.1 Requirement 1: Storing and Retrieving Objects
The most basic requirement is simple: store an object and get it back later. When a user uploads a file, we need to put the bytes somewhere safe. When they request it later, we need to find those bytes and return them. Let's introduce the components that make this work.

### Components for Basic Operations

#### API Gateway
Every request enters through the API Gateway. Think of it as the front door to our system, handling concerns that are common across all requests.
The gateway terminates SSL connections, validates that requests are well-formed, authenticates users, enforces rate limits to prevent abuse, and routes requests to the appropriate backend service. By handling these cross-cutting concerns at the edge, we keep our application services focused on their core responsibilities.

#### Metadata Service
This service manages everything we know about objects except the actual data. When you upload "photos/vacation.jpg", the Metadata Service records: which bucket it belongs to, its key, size, content type, when it was created, which version this is, and critically, where the actual bytes are stored.
Think of it as a sophisticated index. Given a bucket and key, it can tell you exactly which storage nodes hold the data. It also handles listing operations (show me all objects starting with "photos/") and versioning (give me version 3 of this object).

#### Data Service
While the Metadata Service tracks where things are, the Data Service actually moves bytes around. When you upload an object, the Data Service decides which storage nodes should hold the data, coordinates writing to multiple nodes for durability, and handles the complexity of chunking large objects.
On reads, once the Metadata Service tells us where the data lives, the Data Service fetches it from the appropriate storage nodes and streams it back to the client.

#### Storage Nodes
These are the workhorses of the system: physical or virtual machines with lots of disk space. Each storage node is responsible for a portion of the total data. It accepts write requests, persists data to local disks, serves read requests, and periodically reports its health and available capacity to the cluster management system.

### The Upload Flow
Here is how all these components work together when a user uploads an object:
Let's walk through this step by step:
1. **Request arrives at API Gateway:** The client sends `PUT /my-bucket/photos/vacation.jpg` with the image data. The gateway validates the request format, authenticates the user, and checks rate limits.
2. **Data Service takes over:** The request flows to the Data Service, which has two jobs: figure out where to store this data, and actually store it.
3. **Select storage nodes:** The Data Service consults the placement logic to choose which storage nodes should hold this object. It picks nodes in different failure domains (different racks, different availability zones) to maximize durability.
4. **Write to storage nodes:** The object data is written to multiple storage nodes in parallel. For a typical 3-way replication setup, the Data Service waits until at least 2 of the 3 nodes confirm successful writes before proceeding.
5. **Record metadata:** Only after the data is safely stored, the Data Service notifies the Metadata Service to record the object's location. This includes the bucket, key, size, checksum, storage node addresses, and timestamp.
6. **Return success:** Once metadata is committed, the client receives a success response with the ETag (checksum) of the uploaded object.

This ordering is crucial for consistency. If we wrote metadata first and then the data write failed, clients might discover an object (via list or get) that has no actual data. By writing data first, we ensure that any object discoverable through metadata actually exists.

### The Download Flow
Reading an object follows the reverse path:
1. **Request arrives:** The client sends `GET /my-bucket/photos/vacation.jpg`. The gateway authenticates and validates.
2. **Metadata lookup:** The Metadata Service queries its database with the bucket and key. It finds the record showing this object exists, is 2.5 MB, and has copies on storage nodes 7, 23, and 41.
3. **Fetch data:** The Data Service picks one of the healthy storage nodes (typically the closest or least loaded) and requests the object data.
4. **Stream response:** The data is streamed back through the gateway to the client. For large objects, this streaming approach avoids buffering the entire object in memory.

## 4.2 Requirement 2: Organizing Objects into Buckets
With billions of objects in the system, users need a way to organize their data. This is where buckets come in. A bucket is a logical container that groups related objects and provides a namespace for their keys. But buckets do more than just organization. They are also where we apply access policies, versioning settings, and lifecycle rules.
We need a dedicated component to manage bucket operations:

### The Bucket Service
This service handles the lifecycle of buckets: creation, configuration, and deletion. When a user creates a bucket named "my-photos", the Bucket Service first checks if that name is available globally. If it is, the service reserves the name and creates a bucket record.
Object storage URLs typically embed the bucket name (like `my-photos.s3.amazonaws.com`), so bucket names must be unique across all users worldwide. This is different from object keys, which only need to be unique within their bucket.

### How Buckets Organize Objects
Remember, the "/" in object keys is just a character like any other. The storage system sees "2024/vacation/beach.jpg" as a single flat key, not a directory hierarchy. But this naming convention is incredibly useful. When you list objects with `prefix="2024/vacation/"`, you get back just the objects that start with that prefix, creating the illusion of folder navigation.

### Creating a Bucket
The bucket creation flow is straightforward but must handle the global uniqueness constraint carefully:
1. **Request arrives:** Client sends `PUT /my-photos` to create a new bucket.
2. **Check availability:** The Bucket Service queries the global bucket registry to see if "my-photos" is taken. This registry must be strongly consistent because two simultaneous requests for the same name should not both succeed.
3. **Reserve the name:** If available, the service atomically reserves the name and creates the bucket record. This includes the owner's account ID, region, and default settings.
4. **Return success:** The client receives a confirmation with the bucket's endpoint URL.

## 4.3 Requirement 3: Ensuring Data Durability
Here is a sobering reality about storage systems: hardware fails constantly. At the scale we are building, disk failures are not exceptional events; they are daily occurrences. A data center with 10,000 drives, each with a 2% annual failure rate, will see roughly 200 disk failures per year, or more than one every two days.
If we stored each object on a single disk, data loss would be routine. To achieve our 11 nines durability target, we need redundancy. But not just any redundancy. The replicas must be placed strategically so that a single event (a power outage, a network failure, a natural disaster) cannot destroy all copies of the data.

### Components for Durability

#### Placement Service
This service answers a critical question: "I have some data to store. Which storage nodes should hold it?"
The answer is not random. The Placement Service considers failure domains, which are groups of components that can fail together. 
A rack is a failure domain because a single power distribution unit failure can take down all servers in it. An availability zone is a failure domain because it typically shares power, cooling, and network connectivity. A region is a failure domain because a regional disaster could affect all data centers in the area.
For maximum durability, the Placement Service ensures replicas are spread across different failure domains. If you have three replicas, they should ideally be in three different availability zones.

#### Replication Manager
Durability is not set-it-and-forget-it. When a storage node fails (and they do, regularly), the Replication Manager detects the under-replicated data and triggers re-replication to restore the desired redundancy level.
It continuously monitors the health of all data in the system, verifies checksums to detect silent corruption, and coordinates background repair processes. Think of it as the immune system of the storage cluster.

### Understanding Failure Domains
The hierarchy of failure domains looks like this:
- **Node level:** A single machine with its disks. Failures here are the most common (disk dies, OS crashes, network card fails).
- **Rack level:** Typically 20-40 servers sharing a top-of-rack switch and power distribution. A rack failure takes out all nodes in it.
- **Availability Zone (AZ):** A separate data center building with independent power and cooling. An AZ failure is rare but catastrophic for anything inside it.
- **Region:** Multiple AZs in a geographic area. Regional failures (natural disasters, political events) are extremely rare but possible.

The Placement Service uses this hierarchy to make intelligent decisions. For a standard 3-replica setup, it would place one copy in each of three different AZs. This ensures that even if an entire data center goes offline, two copies of the data remain accessible.

## 4.4 Putting It All Together
Now that we have designed each piece, let's step back and see the complete architecture. The system naturally divides into layers, each with a specific responsibility.

### Layer by Layer
**Client Layer:** Users interact with the system through web interfaces, SDKs, CLI tools, or directly via HTTP. From our perspective, they are all just HTTP requests.
**Edge Layer:** The load balancer distributes traffic across multiple API Gateway instances. The gateway handles authentication, rate limiting, and request validation before passing requests to the appropriate service.
**Control Plane:** These services manage the "brains" of the system. The Bucket Service handles bucket operations, the Metadata Service tracks object locations, the Placement Service decides where to put data, and the Replication Manager ensures durability is maintained over time.
**Data Plane:** The Data Service coordinates the actual movement of bytes between clients and storage nodes. It is optimized for high throughput data transfer.
**Storage Layer:** The actual bytes live here, distributed across storage nodes in multiple availability zones. Each node is a commodity server with lots of disk space.
**Metadata Storage:** A distributed database (we will discuss options in the next section) stores all bucket and object metadata with strong consistency guarantees.

### Component Summary
| Component | Primary Role | Key Properties |
| --- | --- | --- |
| Load Balancer | Traffic distribution | High availability, health checks |
| API Gateway | Request handling | Auth, rate limiting, validation |
| Bucket Service | Bucket management | Global namespace, configuration |
| Metadata Service | Object tracking | Location mapping, versioning |
| Placement Service | Storage decisions | Failure domain awareness |
| Data Service | Data movement | High throughput, streaming |
| Replication Manager | Durability maintenance | Background repair, health monitoring |
| Storage Nodes | Byte storage | Local disk management, checksums |
| Metadata DB | Persistent metadata | Strong consistency, high availability |

This architecture separates concerns cleanly. The control plane is optimized for low-latency metadata operations, while the data plane is optimized for high-throughput data transfer. Storage nodes are simple and focused, handling only local disk operations. The complexity of distributed coordination lives in the services above them.
# 5. Database Design
With the high-level architecture in place, let's zoom into the data layer. The database is the source of truth for all metadata. Choosing the right database and designing an efficient schema are critical decisions that affect performance, scalability, and operational complexity.

## 5.1 Choosing the Right Database
The database choice for object storage metadata is not obvious. Let's think through our requirements:

#### What we need to store:
- Hundreds of billions of object records over the system's lifetime
- Each record has metadata including key, size, timestamps, and storage locations
- Bucket configuration and access control policies

#### How we access the data:
- Most reads are point lookups by (bucket, key) combination, the primary use case
- We need to support prefix queries for listing objects (all objects starting with "photos/")
- We need strong consistency because users expect to see their objects immediately after upload
- The system must remain available even when individual nodes fail

#### The SQL vs NoSQL trade-off:
Given our requirements for strong consistency and prefix queries, a **distributed SQL database** like CockroachDB, TiDB, or Google Spanner is a solid choice. These databases provide the consistency guarantees we need while scaling horizontally across nodes. They support range scans efficiently, which is essential for listing objects by prefix.
Alternatively, a well-designed schema on DynamoDB can work. DynamoDB's strong consistency mode plus its query capabilities on sort keys can support our prefix listing requirements. The trade-off is less flexible queries and more careful schema design.
For this design, we will assume a distributed SQL database, but the schema translates to NoSQL with appropriate partition key choices.

## 5.2 Schema Design
Let's design the tables that store our metadata. The schema needs to support fast lookups, efficient listings, and the relationships between buckets, objects, and versions.

### Buckets Table
This table stores bucket configuration. Since bucket names are globally unique, we can use the name as the primary key.
| Field | Type | Description |
| --- | --- | --- |
| bucket_name | VARCHAR(63) PK | Globally unique identifier |
| owner_id | VARCHAR(64) | Account that owns the bucket |
| region | VARCHAR(32) | Geographic region |
| versioning_enabled | BOOLEAN | Whether versioning is active |
| created_at | TIMESTAMP | When the bucket was created |
| acl | JSON | Access control policies |
| lifecycle_rules | JSON | Object lifecycle configuration |

### Objects Table
This is the main table, storing metadata for every object. The composite primary key of (bucket_name, object_key, version_id) allows efficient lookups and prefix scans.
| Field | Type | Description |
| --- | --- | --- |
| bucket_name | VARCHAR(63) PK | Parent bucket |
| object_key | VARCHAR(1024) PK | Object identifier within bucket |
| version_id | VARCHAR(64) PK | Version identifier (UUID or "null" for unversioned) |
| is_latest | BOOLEAN | True if this is the current version |
| size | BIGINT | Object size in bytes |
| etag | VARCHAR(64) | MD5 or composite hash |
| content_type | VARCHAR(256) | MIME type |
| storage_class | VARCHAR(32) | STANDARD, INFREQUENT_ACCESS, ARCHIVE |
| data_locations | JSON | Array of chunk locations |
| created_at | TIMESTAMP | Upload timestamp |
| user_metadata | JSON | Custom user-defined headers |

**Indexes:**
The prefix index is critical for listing operations. When a user requests "list all objects starting with photos/2024/", we can use this index to efficiently find matching keys without scanning the entire bucket.

### Multipart Uploads Table
Tracks in-progress multipart upload sessions. These records are temporary but need to be durable in case of service restarts.
| Field | Type | Description |
| --- | --- | --- |
| upload_id | VARCHAR(64) PK | Unique session identifier |
| bucket_name | VARCHAR(63) | Target bucket |
| object_key | VARCHAR(1024) | Target object key |
| initiated_at | TIMESTAMP | When the upload started |
| parts | JSON | Array of uploaded parts with ETags |
| status | ENUM | ACTIVE, COMPLETED, ABORTED |

A cleanup job periodically removes stale uploads that have not completed within a configured timeout (typically 7 days).

### Storage Nodes Table
The Placement Service needs to know about all storage nodes in the cluster to make placement decisions.
| Field | Type | Description |
| --- | --- | --- |
| node_id | VARCHAR(64) PK | Unique node identifier |
| hostname | VARCHAR(256) | Network address |
| availability_zone | VARCHAR(32) | AZ for failure domain placement |
| rack_id | VARCHAR(32) | Rack for finer-grained placement |
| total_capacity_bytes | BIGINT | Total disk space |
| used_capacity_bytes | BIGINT | Currently used space |
| status | ENUM | HEALTHY, DEGRADED, OFFLINE |
| last_heartbeat | TIMESTAMP | Last health check |

The Replication Manager queries this table to find under-replicated data when nodes go offline.
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often go deeper into specific components. 
In this section, we will explore the trickiest parts of our design: how we organize data on disk, how we achieve extreme durability, how we maintain consistency in a distributed system, and how we handle the complexities of large file uploads.

## 6.1 Data Organization: Objects and Chunks
One question we have glossed over is: how do we actually store object bytes on disk? The naive answer is "just write them to a file," but this breaks down at scale in interesting ways.

### Why Simple File Storage Fails
Imagine storing each object as a single file on the storage node's file system. This seems straightforward, but consider what happens with billions of objects:
- **Small object inefficiency:** File systems allocate in blocks (typically 4KB). A 100-byte object wastes 3.9KB of its block. With billions of small objects, this waste is massive.
- **Metadata explosion:** File systems track every file in directory structures (inodes on Linux). With billions of files, the file system itself becomes the bottleneck. Operations like `ls` would take minutes.
- **Large file problems:** A 5TB video file is hard to work with. Replicating it takes hours. If part of it corrupts, we might have to re-replicate the entire thing.

### The Solution: Chunking and Aggregation
Object storage systems use two complementary strategies depending on object size:

#### For Large Objects: Chunking
We split large objects into fixed-size chunks, typically 64MB or 128MB each.
Why is this better?
- **Parallel operations:** Download chunks from different nodes simultaneously, saturating network bandwidth.
- **Efficient repair:** If one chunk is lost, only re-replicate that 64MB chunk, not the entire 5TB file.
- **Incremental uploads:** Multipart upload naturally maps to chunks. Each part becomes one or more chunks.

#### For Small Objects: Aggregation
We do the opposite for small objects. Instead of one file per object, we pack many small objects into a single large blob.
The metadata stores the blob ID, byte offset, and length for each small object. When you request Object B, the system reads bytes 100 through 51,399 from the blob file.
This solves the small object problems:
- No wasted block space since objects are packed tightly.
- Far fewer files for the file system to track.
- Writes are sequential, which is efficient for spinning disks.

### Chunk Placement Strategy
Each chunk (whether from a large object or a blob containing small objects) gets a unique identifier and is replicated across storage nodes:
The Placement Service ensures chunks are distributed across different failure domains. If a rack loses power, we still have copies in other racks. If an entire AZ goes down, we still have copies in other AZs.

## 6.2 Achieving 11 Nines Durability
Let's talk about what 11 nines durability actually means. With 99.999999999% durability, if you store 100 billion objects, you should expect to lose at most 1 object per year. That is an extraordinary guarantee. How do we deliver it?
The key insight is that durability is a statistical property that emerges from redundancy and repair speed. We need enough copies of the data that the probability of all copies failing simultaneously is vanishingly small. And when a copy does fail (because hardware always fails), we need to create a new copy before another failure occurs.

### Understanding the Math
Let's start with some baseline numbers:
- **Disk annual failure rate (AFR):** 2-4% (Google and Backblaze studies confirm this range)
- **Node failure rate:** 5-10% AFR when you include all failure modes (disk, memory, network, power)
- **AZ failure rate:** Very rare, maybe 0.1% per year for a brief outage

### Approach 1: Simple Replication
The straightforward approach is to store multiple copies. With 3-way replication across 3 AZs:
What is the probability of losing all 3 copies?
If each node has a 4% annual failure rate and failures are independent:
This gives us about 4-5 nines of durability. Better than a single copy, but nowhere near 11 nines.
The calculation above assumes failures happen at the same instant, which is unrealistic. In practice, we detect failures and re-replicate before the next failure. The real probability depends on the "window of vulnerability" during which data is under-replicated.

#### With fast repair:
If we detect failures within 1 hour and re-replicate within 24 hours, the window is small. The probability of two more failures during that 24-hour window is much lower than the annual probability. This pushes us toward 6-7 nines.

### Approach 2: Erasure Coding
Erasure coding achieves higher durability with less storage overhead. The idea is elegant: instead of storing complete copies, we store encoded fragments that can reconstruct the original data.

#### How it works:
We split the data into **k** data fragments and compute **m** parity fragments using mathematical transformations (typically Reed-Solomon codes). The magic is that we can recover the original data from any **k** of the **(k + m)** total fragments.

#### Example: Reed-Solomon (10, 4)
- Split data into 10 chunks of 64 MB each (640 MB total)
- Compute 4 parity chunks (256 MB additional)
- Total storage: 896 MB for 640 MB of data = 1.4x overhead
- Can tolerate losing ANY 4 of the 14 chunks

Compare this to 3-way replication:
- 3 copies of 640 MB = 1920 MB = 3x overhead
- Can only tolerate losing 2 of the 3 copies

#### Durability calculation:
With (10, 4) encoding across 14 independent storage nodes, we need to lose 5+ chunks simultaneously to lose data. If each node has 4% AFR:
That is well beyond 11 nines, even before accounting for repair processes.

### Trade-offs: Replication vs Erasure Coding
| Factor | 3x Replication | Erasure Coding (10,4) |
| --- | --- | --- |
| Storage overhead | 3x | 1.4x |
| Achievable durability | 6-7 nines | 11+ nines |
| Read latency | Lowest (any copy) | Higher (may need to reconstruct) |
| Write latency | Lower | Higher (compute parity) |
| Repair bandwidth | Low (copy 64 MB) | Higher (read 640 MB to repair one chunk) |
| CPU overhead | Minimal | Moderate (encoding/decoding) |
| Best for | Hot, latency-sensitive data | Cold, cost-sensitive data |

### The Tiered Strategy
In practice, object storage systems use both approaches based on access patterns:
- **Hot tier:** Recently uploaded or frequently accessed objects use replication for fastest reads.
- **Warm tier:** Objects not accessed for 30+ days transition to a hybrid approach.
- **Cold/Archive tier:** Rarely accessed objects use pure erasure coding for maximum cost efficiency.

Lifecycle policies automatically move objects between tiers based on access patterns.

## 6.3 Consistency Model
Strong consistency is one of our core requirements. After a successful upload, any subsequent read must return the new data. No stale reads, no "object not found" errors for objects that were just created. This sounds simple but is surprisingly tricky when data is spread across multiple nodes.

### Why Consistency is Challenging
Consider what happens during an upload:
1. Client uploads object data
2. Data Service writes to storage nodes A, B, and C
3. Metadata Service records the object in the database
4. Client receives success response

Now imagine another client tries to read immediately after. Several things could go wrong:
- **Replication lag:** Node C has not finished receiving the data yet
- **Metadata lag:** The read hits a database replica that has not received the update
- **Race condition:** The read request arrives before the metadata write completes

Any of these could cause the second client to get a "not found" error or stale data, even though the first client was told the upload succeeded.

### The Solution: Write Order and Quorums
We solve this with two mechanisms: careful ordering of operations and quorum-based acknowledgment.
**Write Order: Data Before Metadata**
The critical insight: we only write metadata after the data is safely stored on a quorum of nodes. This means any object discoverable through metadata definitely has its data available.

#### Quorum Writes
With 3 replicas, we wait for 2 (a majority) to acknowledge before proceeding. Why?
With W=2 (write quorum) and R=2 (read quorum), any read will overlap with at least one node that received the write. This is because W + R > N (2 + 2 > 3). The math guarantees that reads always see the latest successful write.

#### Strongly Consistent Metadata Database
The metadata database must also provide strong consistency. Distributed databases like CockroachDB or Spanner use consensus protocols (Raft or Paxos) to ensure that once a write is acknowledged, all subsequent reads see it.
This is non-negotiable. If the metadata database used eventual consistency, clients might create an object and then fail to find it when they immediately try to list bucket contents.

### Read-Your-Writes Guarantee
Even with the above mechanisms, there is one more edge case. What if a client uploads an object and then reads it so quickly that the read arrives at a different data center before replication completes?
We handle this with version tokens:
1. On successful write, return a version token (essentially a timestamp or sequence number)
2. Client includes this token in the next read request
3. The system ensures the read sees data at least as recent as that token

For most clients, this is transparent. SDKs track the token automatically and include it in subsequent requests.

## 6.4 Multipart Upload for Large Objects
Try uploading a 5TB video file over HTTP. Within minutes, something will go wrong: a network hiccup, a timeout, a proxy that cannot handle the stream. Even if the network is perfect, holding a 5TB file in memory while uploading is not practical for most clients.
Multipart upload solves this by breaking large uploads into manageable pieces that can be uploaded independently, in parallel, and resumed after failures.

### The Three Phases

#### Phase 1: Initiate
The client starts by requesting a new upload session:
The system creates a record in the multipart uploads table, reserving this upload ID. The client will use this ID for all subsequent part uploads.

#### Phase 2: Upload Parts
Now the client uploads the file in chunks. Each chunk is a "part" with a number from 1 to 10,000:
Parts can be uploaded:
- **In any order:** Part 47 can arrive before Part 1
- **In parallel:** Multiple parts uploading simultaneously
- **From different clients:** A distributed uploader can split the work
- **After failures:** If Part 23 fails, just retry Part 23

Each part must be at least 5 MB (except the last one) and at most 5 GB. When a part completes, the system returns an ETag that the client must remember for the final step.

#### Phase 3: Complete
Once all parts are uploaded, the client sends the completion request with the list of parts and their ETags:
The system verifies that all parts exist and the ETags match, then logically concatenates the parts into the final object. This "concatenation" is typically just updating metadata to point to all the parts in sequence, not actually copying data.

### What Happens If Something Goes Wrong?
**Part upload fails:** Just retry that part. Other parts are unaffected.
**Upload abandoned:** Incomplete uploads consume storage. The system needs cleanup mechanisms:
- Lifecycle policies that abort uploads after N days of inactivity
- Background garbage collection for orphaned parts

**Wrong ETag:** If the completion request has an incorrect ETag (perhaps the part was corrupted), the system rejects the completion. The client must re-upload that part.

### Why This Matters
The maximum object size with multipart upload is enormous:
AWS S3 limits objects to 5 TB, but the multipart protocol itself could support 50 TB. The practical benefits are:
- **Parallel upload:** Upload 10 parts simultaneously, 10x faster than sequential
- **Resumable:** Network dropped? Resume from where you left off
- **Checksummed:** Each part has its own ETag for integrity verification
- **Memory efficient:** Upload 100 MB at a time instead of loading 5 TB into memory

## 6.5 Data Integrity and Verification
Here is a troubling fact: bits can flip. Cosmic rays, electrical interference, firmware bugs, and aging storage media can all cause silent data corruption. At the scale of billions of objects, corruption is not a question of "if" but "when."
The problem is that corrupted data often looks perfectly normal. A JPEG with a flipped bit might render with a weird artifact. A database backup might restore successfully but have one wrong value. Without active verification, you would never know until it was too late.

### Defense in Depth: Checksums Everywhere
We protect against corruption by verifying data at every step of its journey:

#### On upload:
1. Client calculates MD5 and includes it in the `Content-MD5` header
2. Gateway verifies the received data matches the claimed MD5
3. Data Service calculates a checksum before writing to storage
4. Storage Node writes both the data and the checksum to disk

If any checksum fails, the upload is rejected immediately. We never store data we cannot verify.

#### Checksums we store:
- **CRC32 or xxHash:** Fast to compute, used for transfer verification and quick integrity checks
- **MD5 or SHA-256:** Stored permanently in metadata, returned as the ETag, used for long-term integrity audits

### Background Scrubbing
Checksums catch corruption at write time, but what about corruption that happens while data sits on disk? Bit rot is real, and the longer data sits, the more likely something will go wrong.
The solution is continuous background verification:
The scrubber runs continuously, reading data from disk, recalculating checksums, and comparing against stored values. When it finds a mismatch:
1. Mark the corrupt chunk as "unhealthy"
2. Fetch a known-good copy from another replica
3. Write the healthy data to a new location
4. Update metadata to point to the new copy
5. Delete the corrupt chunk

**How often to scrub?** A typical target is to verify all data every 2-4 weeks. At petabyte scale with thousands of disks, this means the scrubber is always busy, quietly reading and verifying in the background.

## 6.6 Garbage Collection and Deletion
When a user deletes an object, what happens to the bytes on disk? If we deleted them immediately, we would face several problems:
- A bug in our system could accidentally delete user data with no way to recover
- Concurrent operations become tricky (what if someone is reading while we are deleting?)
- Immediate deletion of scattered chunks is slow and inefficient

Instead, object storage systems use a deferred deletion approach with garbage collection.

### The Deletion Pipeline

#### Step 1: Logical Deletion
When a user calls DELETE on an object:
- The metadata record is marked as deleted (or a delete marker is created if versioning is enabled)
- The API returns success immediately
- The actual data remains on storage nodes untouched

To the user, the object is gone. GET requests return 404. But behind the scenes, the data is still there.

#### Step 2: Grace Period
We wait before actually removing data. This grace period (typically 24-48 hours, sometimes longer) serves several purposes:
- **Recovery from accidents:** An engineer who accidentally deleted the wrong bucket has time to realize and contact support
- **Consistency:** Ensures any in-flight reads complete before data disappears
- **Batching:** Accumulating deletions allows more efficient bulk cleanup

#### Step 3: Garbage Collection
A background process (the garbage collector) periodically scans for data that can be safely removed:
1. Find all chunks not referenced by any live object
2. Verify they have been unreferenced longer than the grace period
3. Delete the physical data from storage nodes
4. Update capacity counters

### Handling Versioned Objects
Versioning adds a layer of complexity. When you delete a versioned object, you are not really deleting anything. You are creating a special version called a "delete marker."
- GET requests see the delete marker and return 404
- All previous versions still exist and are accessible by version ID
- To restore, delete the delete marker
- To permanently remove, delete each version individually

This is powerful for audit trails and accidental deletion recovery, but it also means storage is not reclaimed until someone explicitly deletes the old versions.

## 6.7 Storage Classes and Lifecycle
Not all data is equal. Some objects are accessed multiple times per second, while others sit untouched for months. Treating them the same wastes money. Fast storage is expensive, and most data does not need to be fast.
Storage classes let users (and automated policies) choose the right trade-off between cost, access speed, and retrieval time for each object.

### The Storage Class Spectrum
| Storage Class | Access Latency | Storage Cost | Retrieval Cost | Best For |
| --- | --- | --- | --- | --- |
| Standard | Milliseconds | Highest | None | Active data, websites, APIs |
| Infrequent Access | Milliseconds | ~40% less | Small fee | Backups, older logs |
| Archive | Minutes to hours | ~80% less | Higher fee | Compliance, long-term storage |

### How They Differ Internally
**Standard Storage:**
- Data lives on SSDs or fast spinning disks
- 3-way replication for instant reads from any replica
- Metadata fully cached in memory
- Optimized for low latency and high throughput

**Infrequent Access:**
- Data on cheaper, slower HDDs
- Erasure coding instead of replication (lower storage overhead)
- Same access path as Standard (retrieval is still fast)
- Cost savings come from cheaper media and reduced redundancy overhead

**Archive:**
- Data may be on tape, cold HDDs, or even offline storage
- Highly aggressive erasure coding
- Retrieval requires "thawing": data is staged to faster storage before it can be read
- Optimized for cost, not speed

### Lifecycle Policies
Manually managing storage classes for millions of objects is impractical. Lifecycle policies automate the transitions:
A background service continuously evaluates objects against lifecycle rules:
1. Scan objects in each bucket
2. Check if any lifecycle rules apply based on age or other criteria
3. Transition objects to the specified storage class
4. Delete objects that have exceeded their retention period

For a bucket with a policy "move to Archive after 90 days," every object that reaches its 90th day is automatically transitioned. Users do not have to do anything.
This is how organizations manage cost at scale. Store everything in Standard initially for fast access. As data ages and access patterns decline, let lifecycle policies automatically move it to cheaper tiers.
# References
- [Amazon S3 Documentation](https://docs.aws.amazon.com/s3/) - Comprehensive guide to S3 features and best practices.
- [Building and Operating a Pretty Big Storage System (Facebook)](https://www.usenix.org/conference/fast21/presentation/pan) - Real-world blob storage at scale.
- [Windows Azure Storage Paper](https://sigops.org/s/conferences/sosp/2011/current/2011-Cascais/printable/11-calder.pdf) - Azure's storage architecture design.
- [Erasure Coding Explained](https://www.backblaze.com/blog/reed-solomon/) - Backblaze's practical guide to erasure coding.
- [Google File System Paper](https://static.googleusercontent.com/media/research.google.com/en//archive/gfs-sosp2003.pdf) - Foundational paper on distributed file systems.