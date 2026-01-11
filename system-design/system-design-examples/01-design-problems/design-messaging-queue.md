# Design a Distributed Message Queue

## What is a Distributed Message Queue?

A distributed message queue is a system that enables asynchronous communication between services by storing and forwarding messages from producers to consumers across multiple servers.
The core idea is to decouple producers (who send messages) from consumers (who process them), allowing both sides to operate independently and at different speeds. Messages are persisted in the queue until they are consumed, providing reliability and fault tolerance.
**Popular Examples:** Apache Kafka, Amazon SQS, RabbitMQ, Apache Pulsar, Google Pub/Sub
This problem touches on many distributed systems fundamentals: partitioning for scale, replication for fault tolerance, ordering guarantees, and the subtle differences between delivery semantics.
In this article, we will explore the **high-level design of a distributed message queue**.
Let's start by clarifying the requirements.
# 1. Clarifying Requirements
Before starting the design, it's important to ask thoughtful questions to uncover hidden assumptions, clarify ambiguities, and define the system's scope more precisely.
Here is an example of how a discussion between the candidate and the interviewer might unfold:
**Candidate:** "What is the expected message volume? How many messages per second should the system handle?"
**Interviewer:** "Let's aim for 1 million messages per second at peak load."
**Candidate:** "What is the average message size?"
**Interviewer:** "Messages are typically 1-10 KB, with an average of 2 KB."
**Candidate:** "How long should messages be retained in the queue?"
**Interviewer:** "Messages should be retained for at least 7 days, even after being consumed, to support replay."
**Candidate:** "What delivery guarantees are required? At-most-once, at-least-once, or exactly-once?"
**Interviewer:** "At-least-once delivery is required. The system should never lose messages."
**Candidate:** "Do we need strict message ordering?"
**Interviewer:** "Ordering should be guaranteed within a partition or topic, but not globally across all messages."
**Candidate:** "Should we support consumer groups where multiple consumers can share the workload?"
**Interviewer:** "Yes, consumer groups are a core requirement for horizontal scaling."
After gathering the details, we can summarize the key system requirements.

## 1.1 Functional Requirements
- **Produce Messages:** Producers can send messages to a specified topic.
- **Consume Messages:** Consumers can read messages from a topic, either individually or as part of a consumer group.
- **Message Retention:** Messages are retained for a configurable period (default 7 days), even after being consumed.
- **Consumer Groups:** Multiple consumers can form a group to share the processing load of a topic.
- **Message Replay:** Consumers can re-read messages from any point in the retention window.

## 1.2 Non-Functional Requirements
Beyond features, we need to consider the qualities that make the system production-ready:
- **High Throughput:** Support 1 million messages per second.
- **Low Latency:** End-to-end latency (produce to consume) under 100ms at p99.
- **Durability:** No message loss. Messages must be persisted before acknowledging to the producer.
- **High Availability:** The system must remain operational even when some nodes fail (99.99% availability).
- **Scalability:** Support horizontal scaling of both producers and consumers.
- **Ordering:** Guarantee message ordering within a partition.

# 2. Back-of-the-Envelope Estimation
Before diving into the design, let us run some quick calculations to understand the scale we are dealing with. These numbers will guide our architectural decisions, particularly around storage, partitioning, and hardware provisioning.
The scale of a distributed message queue is fundamentally different from most systems. While a typical web application might handle thousands of requests per second, we are targeting a million messages per second. This three-orders-of-magnitude difference demands a different approach to almost everything.

### 2.1 Traffic Estimates
Starting with the numbers from our requirements discussion:

#### Message Volume
To put this in perspective, 43 billion messages per day is roughly 500,000 messages every second, continuously. If each message were a grain of rice, we would be processing about 100 tons of rice every day.

### 2.2 Storage Estimates
Each message needs to store not just the payload, but also metadata for routing and retrieval:

#### Component Breakdown:
- **Payload:** Average 2 KB (as specified in requirements)
- **Metadata:** Offset (8 bytes), timestamp (8 bytes), key (variable, ~50 bytes avg), headers (~30 bytes), CRC checksum (4 bytes) = roughly 100 bytes

This gives us approximately 2.1 KB per message. Now let us project storage over time:
| Time Period | Messages | Raw Storage | With 3x Replication |
| --- | --- | --- | --- |
| 1 Day | 43 billion | ~90 TB | ~270 TB |
| 1 Week | 300 billion | ~630 TB | ~1.9 PB |
| 1 Month | 1.3 trillion | ~2.7 PB | ~8.1 PB |

A few observations from these numbers:
1. **Storage is massive:** Even one week of retention requires nearly 2 petabytes with replication. This is not a "throw it on a few servers" problem.
2. **Replication multiplies everything:** Our 3x replication factor triples storage requirements. This is the price we pay for durability and high availability.
3. **Cleanup is essential:** Without the 7-day retention limit, storage would grow indefinitely. The cleanup mechanism is not just a nice-to-have, it is essential for operational viability.

### 2.3 Throughput Estimates
Let us calculate the raw I/O throughput the system must handle:

#### Write Path:

#### Read Path:
**Total I/O:** 6.3 + 6.3 = 12.6 GB/sec or approximately 100 Gbps

### 2.4 Key Insights
These estimates reveal several important design implications:
1. **Partitioning is mandatory:** No single server can handle 1M messages/sec. We need to split the load across many brokers and partitions.
2. **Sequential I/O is critical:** Random disk I/O tops out at a few hundred MB/sec. To achieve 2+ GB/sec writes, we must use append-only logs that enable sequential I/O.
3. **Network is a bottleneck:** 100 Gbps is significant. We need to think carefully about network topology and consider compression.
4. **Storage tiering matters:** Keeping 2 PB on SSDs would cost millions. We need a strategy that balances performance with cost, likely using SSDs for recent data and HDDs or cloud storage for older segments.

# 3. Core APIs
With our requirements and scale understood, let us define the API contract. A message queue's API is deceptively simple on the surface, but the details matter for correctness, performance, and usability.
We will design a RESTful API with four core operations: sending messages, consuming messages, committing offsets, and managing topics. Let us walk through each one.

### 3.1 Send Message

#### Endpoint: POST /topics/{topic_name}/messages
This is how producers push messages into the queue. The endpoint accepts one or more messages and returns confirmation once they are durably stored.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| messages | array | Yes | Array of message objects to send |
| messages[].key | string | No | Partition key. Messages with the same key go to the same partition, preserving order |
| messages[].value | string | Yes | The actual message payload |
| messages[].headers | object | No | Key-value metadata attached to the message |

The partition key deserves special attention. If you are sending order events, you might use the order ID as the key. This ensures all events for a single order (created, paid, shipped) land in the same partition and are processed in order. Without a key, messages are distributed round-robin across partitions for load balancing.

#### Example Request:

#### Success Response (200 OK):
The response includes the partition and offset where the message was written. This information is valuable for debugging and for implementing exactly-once semantics on the producer side.

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 404 Not Found | Topic does not exist | The specified topic has not been created |
| 413 Payload Too Large | Message exceeds size limit | Message body exceeds configured maximum (typically 1-10 MB) |
| 503 Service Unavailable | No available brokers | The partition leader is down and no replica can take over |

### 3.2 Consume Messages

#### Endpoint: GET /topics/{topic_name}/messages
This is how consumers pull messages from the queue. Unlike traditional message queues that "pop" messages, our system uses a pull model where consumers request messages and track their own progress.

#### Request Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| consumer_group | string | Yes | Identifier for the consumer group. Determines partition assignment and offset tracking |
| max_messages | integer | No | Maximum number of messages to return (default: 100) |
| timeout_ms | integer | No | Long-polling timeout. The server holds the connection until messages are available or timeout expires |

Long-polling is a key optimization here. Instead of consumers hammering the server with requests when the queue is empty, they can set a timeout (say, 5 seconds) and the server will hold the connection until new messages arrive.

#### Success Response (200 OK):
Each message includes its partition and offset, which the consumer uses when committing progress.

### 3.3 Commit Offset

#### Endpoint: POST /topics/{topic_name}/offsets
After processing messages, consumers commit their progress so they do not reprocess the same messages after a restart.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| consumer_group | string | Yes | The consumer group identifier |
| offsets | object | Yes | Map of partition number to committed offset |

#### Example Request:
Notice that offsets are committed per partition. A consumer might be assigned multiple partitions and can commit progress independently for each.
**When to commit?** This is a critical design decision on the consumer side:
- **Commit before processing:** Lowest latency, but message loss if consumer crashes mid-processing
- **Commit after processing:** No message loss, but duplicate processing if consumer crashes after processing but before committing
- **Batch commits:** Commit every N messages or every T seconds for a balance of performance and safety

### 3.4 Create Topic

#### Endpoint: POST /topics
Creates a new topic with specified configuration. This is typically an admin operation, not something producers do on the fly.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| name | string | Yes | Unique topic name |
| partitions | integer | Yes | Number of partitions. More partitions enable more parallelism |
| replication_factor | integer | Yes | Number of replicas per partition. Higher values increase durability |
| retention_ms | long | No | How long to retain messages (default: 7 days) |

#### Example Request:
Choosing the right number of partitions is important. Too few limits parallelism. Too many creates overhead and can cause uneven load distribution. A common rule of thumb is to start with 2-3x the expected number of consumers.
# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complex diagram upfront, we will build the design incrementally, starting with the simplest solution and adding components as we encounter challenges. This mirrors how you would approach the problem in an interview.
Our system needs to handle three fundamental operations:
1. **Message Production:** Accepting messages from producers and storing them durably
2. **Message Storage:** Persisting messages across failures and replicating for fault tolerance
3. **Message Consumption:** Delivering messages to consumers in the right order with progress tracking

The challenge is doing all three at the scale we discussed: a million messages per second, with strong durability guarantees and low latency. Let us see how each requirement shapes our design.
Let us build this architecture step by step, starting with message production.


When a producer calls `POST /topics/orders/messages`, several things need to happen behind the scenes. The message needs to reach the right server, get written to the right partition, be persisted durably, and be replicated before we can acknowledge success. Let us introduce the components we need.

### Components for Message Production

#### Broker
The broker is the workhorse of our system. Think of it as a specialized server optimized for receiving, storing, and serving messages. Each broker handles a subset of the total traffic, and we scale by adding more brokers.
A broker's responsibilities include:
- Accepting incoming messages from producers
- Persisting messages to disk before acknowledging
- Serving messages to consumers on request
- Replicating data to follower brokers
- Participating in leader election when other brokers fail

#### Topics and Partitions
A topic is a logical channel for related messages. The "orders" topic might contain all order-related events across your e-commerce platform. But a single topic cannot live on a single broker, that would limit throughput to what one machine can handle.
This is where partitions come in. Each topic is divided into multiple partitions, and each partition is an independent, ordered, append-only log of messages. Partitions are the unit of parallelism in our system.
Why are partitions so important?
1. **Horizontal scaling:** More partitions means more machines can share the load
2. **Parallel consumption:** Multiple consumers can read different partitions concurrently
3. **Ordering within partition:** Messages in a partition are strictly ordered by offset
4. **Isolation:** A slow partition does not block others

#### Partition Assignment
When a producer sends a message, we need to decide which partition receives it. There are two strategies:
1. **With partition key:** Hash the key to determine the partition. This ensures messages with the same key (like all events for user-123) always go to the same partition, preserving their order.
2. **Without partition key:** Distribute messages round-robin across partitions for even load balancing. Order is not preserved across messages.

### The Message Production Flow
Here is how all these components work together when a producer sends a message:
Let us walk through this step by step:
1. **Request arrives at load balancer:** The producer sends a message with key "user-123". The load balancer routes to any broker since producers talk to any broker in modern implementations.
2. **Broker determines partition:** The receiving broker calculates `hash("user-123") mod 3 = 1`, so this message belongs to partition 1. If this broker is not the leader for partition 1, it forwards the request to the correct leader.
3. **Message is appended to log:** The partition leader appends the message to its local log file. This is a sequential write, which is very fast on both HDDs and SSDs.
4. **Replication (covered in detail later):** The message is replicated to follower brokers. Depending on the ack setting, we may wait for followers before acknowledging.
5. **Offset returned to producer:** Once durably stored (and optionally replicated), the broker returns the offset where the message was written. The producer can use this for debugging or for implementing exactly-once semantics.


    S4 --> QueueKafka
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
        S1[between Service]
        S2[coordinator Service]
        S3[503 Service]
        S4[queue Service]
    end

    subgraph Data Storage
        DBPostgreSQL[PostgreSQL]
        DBCassandra[Cassandra]
        DBMongoDB[MongoDB]
    end

    subgraph Caching Layer
        CacheRedis[Redis]
    end

    subgraph Message Queue
        QueueKafka[Kafka]
        QueueSQS[SQS]
        Queuekafka[kafka]
        QueueRabbitMQ[RabbitMQ]
        Queuesqs[sqs]
    end

    Web --> LB
    Mobile --> LB
    LB --> S1
    LB --> S2
    LB --> S3
    LB --> S4
    S1 --> DBPostgreSQL
    S1 --> DBCassandra
    S1 --> CacheRedis
    S1 --> QueueKafka
    S1 --> QueueSQS
    S1 --> Queuekafka
    S1 --> QueueRabbitMQ
    S1 --> Queuesqs
    S2 --> DBPostgreSQL
    S2 --> DBCassandra
    S2 --> CacheRedis
    S2 --> QueueKafka
    S2 --> QueueSQS
    S2 --> Queuekafka
    S2 --> QueueRabbitMQ
    S2 --> Queuesqs
    S3 --> DBPostgreSQL
    S3 --> DBCassandra
    S3 --> CacheRedis
    S3 --> QueueKafka
    S3 --> QueueSQS
    S3 --> Queuekafka
    S3 --> QueueRabbitMQ
    S3 --> Queuesqs
    S4 --> DBPostgreSQL
    S4 --> DBCassandra
    S4 --> CacheRedis
    S4 --> QueueKafka
    S4 --> QueueSQS
    S4 --> Queuekafka
    S4 --> QueueRabbitMQ
    S4 --> Queuesqs



## 4.2 Requirement 2: Durable Message Storage
We promised "no message loss" in our requirements. That is a bold promise when you are dealing with machines that can crash, disks that can fail, and networks that can partition. How do we ensure that once a producer receives an acknowledgment, that message will survive any single (or even multiple) component failures?
The answer lies in how we store and replicate data.

### The Append-Only Log
At the heart of every partition is an append-only log. Unlike a database where data can be updated or deleted, a message queue only ever appends new messages to the end of the log. This simple constraint has profound implications for performance.
Why is append-only so powerful?
1. **Sequential writes:** Disk drives, especially HDDs, are dramatically faster at sequential writes than random writes. A single HDD can write 100+ MB/sec sequentially but only a few MB/sec randomly. By always appending, we get predictable, high throughput.
2. **Natural ordering:** Each message gets the next offset in sequence. Offset 1000 was definitely written before offset 1001. No need for timestamps or ordering logic.
3. **Simple replication:** To replicate, followers just copy the log from the leader. No complex synchronization needed.
4. **Crash recovery:** If a broker crashes mid-write, we simply truncate any partially written message. The log remains valid.

### Segment Files
A single massive log file would be impractical. We would need to read through gigabytes of data to find a single message, and cleanup would be impossible without rewriting the entire file.
Instead, we split each partition's log into segment files:
Each segment has a maximum size (typically 1 GB). Once a segment fills up, we create a new one and start writing there. The old segment becomes immutable.
This segmentation enables several important capabilities:
- **Fast lookups:** Index files map offsets to byte positions, enabling O(1) message retrieval
- **Efficient cleanup:** Expired segments can be deleted entirely, no rewriting needed
- **Parallel I/O:** Different consumers reading different offsets can hit different segments

### Replication for Fault Tolerance
Storing data on one machine is not enough. Disks fail. Machines crash. Data centers lose power. To survive these failures, every partition is replicated across multiple brokers.
We use a leader-follower model:
- **Leader:** One replica handles all reads and writes for the partition. This simplifies consistency since there is a single source of truth.
- **Followers:** Other replicas continuously pull new messages from the leader. They do not serve client requests directly but stand ready to take over if the leader fails.
- **In-Sync Replicas (ISR):** Followers that are caught up with the leader. Only ISR members can be elected as the new leader, ensuring no data loss during failover.

When the leader fails, one of the in-sync followers is promoted to leader. Producers and consumers discover the new leader through metadata and continue operating with minimal disruption.
We will explore replication in much more detail in the deep dive section, including acknowledgment modes and the trade-offs between consistency and availability.

## 4.3 Requirement 3: Message Consumption
Now for the other side of the equation: getting messages out. The consumption model is where message queues differ most from each other. Some use push (broker sends messages to consumers), others use pull (consumers request messages). Some delete messages after delivery, others retain them. Our design uses a pull model with retained messages, similar to Kafka.

### Consumer Groups
The simplest consumption model is one consumer reading from one topic. But at scale, a single consumer cannot keep up with a million messages per second. We need a way to parallelize consumption.
This is where consumer groups come in. A consumer group is a set of consumers that work together to consume a topic. The key insight is that each partition is assigned to exactly one consumer in the group.
In this example, Consumer 1 reads from partitions 0 and 1, while Consumer 2 reads from partitions 2 and 3. If we add a third consumer, partitions would be redistributed. If Consumer 2 crashes, its partitions would be reassigned to Consumer 1.
This design has important implications:
1. **Maximum parallelism = number of partitions:** You cannot have more active consumers than partitions. Extra consumers just sit idle.
2. **Ordering within partition:** Since each partition goes to exactly one consumer, that consumer sees messages in order.
3. **Independent consumer groups:** Multiple groups can consume the same topic independently. An analytics group and an alerting group can each maintain their own offset.

### Offset Management
Unlike traditional queues that delete messages after delivery, our system retains messages for the configured retention period. Consumers track their progress using offsets, essentially a bookmark saying "I have processed up to message N."
Offsets are stored durably so that after a restart, the consumer can resume from where it left off. There are two common approaches:
1. **Internal topic:** Store offsets in a special compacted topic (like Kafka's `__consumer_offsets`). This keeps everything within the message queue system.
2. **External store:** Store offsets in ZooKeeper, Redis, or a database. This can be simpler but adds another dependency.

### The Coordinator
With consumers joining, leaving, and crashing, someone needs to keep track of who is responsible for which partition. This is the coordinator's job.
The coordinator:
- **Tracks membership:** Consumers send periodic heartbeats. If heartbeats stop, the consumer is considered dead.
- **Assigns partitions:** When the group membership changes, the coordinator calculates a new partition assignment.
- **Triggers rebalance:** Notifies consumers to stop reading their current partitions and pick up new assignments.

### The Consumption Flow
Here is how everything works together when a consumer reads messages:
Let us trace through the flow:
1. **Consumer joins group:** The consumer contacts the coordinator and joins the "order-processor" group.
2. **Partition assignment:** The coordinator assigns partitions 0 and 1 to this consumer based on the current membership.
3. **Fetch committed offset:** The consumer retrieves its last committed offset for each partition from the offset store.
4. **Poll messages:** The consumer fetches messages from the partition leader, starting at its last committed offset.
5. **Process and commit:** After processing a batch of messages, the consumer commits its new offset. This checkpoints progress.
6. **Failure handling:** If the consumer crashes, the coordinator detects missed heartbeats and reassigns its partitions to other consumers in the group.

## 4.4 Putting It All Together
Now that we have designed each piece individually, let us step back and see the complete architecture. We have also added a metadata store that we have not explicitly discussed: this is where topic configurations, partition assignments, and cluster membership are stored.
The architecture follows a layered approach, with each layer having specific responsibilities:
**Client Layer:** Producers send messages to the cluster, and consumer groups pull messages from partitions. Both interact with the system through well-defined APIs.
**Gateway Layer:** The load balancer distributes incoming connections across brokers. In practice, clients often connect directly to specific brokers for partition-aware routing, but the load balancer handles initial discovery.
**Broker Cluster:** This is where the work happens. Each broker manages a set of partition replicas. Notice that partition 0's leader is on Broker 1, while partition 1's leader is on Broker 2. This distributes the load across brokers.
**Coordination Layer:** The coordinator service manages cluster metadata, consumer group membership, and partition assignments. It relies on a metadata store (often ZooKeeper, etcd, or an internal Raft-based store) for consistency.

### Component Responsibilities
| Component | Primary Responsibility | Scaling Strategy |
| --- | --- | --- |
| Broker | Receive, store, and serve messages | Horizontal (add brokers, redistribute partitions) |
| Topic | Logical message channel | N/A (organizational construct) |
| Partition | Unit of parallelism and ordering | Increase partition count for more parallelism |
| Producer | Send messages to topics | Horizontal (add producers, partition key distributes load) |
| Consumer | Read messages from partitions | Horizontal (add consumers up to partition count) |
| Consumer Group | Coordinate parallel consumption | Add consumers within the group |
| Coordinator | Manage membership and assignments | Leader election for HA, typically single active |
| Replication | Maintain data copies for fault tolerance | Configure replication factor per topic |

### Data Flow Summary
**Write Path:**
1. Producer sends message with optional partition key
2. Load balancer routes to any broker
3. Broker determines target partition and forwards to partition leader
4. Leader appends to log, replicates to followers
5. After acknowledgment policy is satisfied, responds to producer

**Read Path:**
1. Consumer joins consumer group
2. Coordinator assigns partitions to consumer
3. Consumer fetches last committed offset
4. Consumer polls messages from partition leaders
5. After processing, consumer commits new offset

# 5. Database Design
With the high-level architecture in place, let us zoom into the data layer. The storage design of a message queue is fundamentally different from a typical web application. We are not dealing with users and orders that need relational queries. We are dealing with a firehose of messages that need to be written fast, read sequentially, and cleaned up efficiently.

## 5.1 Why Not a Traditional Database?
Before diving into our storage design, let us address the obvious question: why not just use PostgreSQL or MongoDB?
The access patterns are completely different:
| Characteristic | Traditional Database | Message Queue |
| --- | --- | --- |
| Write pattern | Random inserts, updates, deletes | Append-only |
| Read pattern | Random queries by various keys | Sequential reads by offset |
| Consistency | Strong ACID transactions | Single-writer per partition |
| Indexing | Multiple indexes for flexible queries | Simple offset-based lookup |
| Throughput goal | Thousands of ops/sec | Millions of ops/sec |

A relational database would add overhead we do not need: transaction management, lock contention, index maintenance on every write. A NoSQL database like Cassandra could work but adds unnecessary complexity for what is fundamentally an append-only log.
This is why every major message queue (Kafka, Pulsar, RabbitMQ) implements its own storage engine. The append-only log pattern is so simple and efficient that a custom implementation outperforms general-purpose databases by orders of magnitude.

## 5.2 Storage Architecture
Our storage has two distinct parts: the message logs (where the actual messages live) and metadata (topic configurations, consumer offsets, cluster state).

### Message Storage
Messages are stored in append-only log files, one set per partition. We discussed segment files earlier. Here is the detailed layout:

### Metadata Storage
Metadata is a different beast. It needs strong consistency (we cannot have two brokers thinking they are the leader for the same partition) and it is relatively small but frequently accessed.
Options include:
- **ZooKeeper:** Traditional choice, battle-tested but operationally complex
- **etcd:** Modern alternative, simpler but similar purpose
- **Internal Raft:** Kafka 3.0+ uses KRaft, eliminating ZooKeeper dependency

## 5.3 Data Structures
Even though we use file-based storage for messages, we need well-defined schemas for both message records and metadata.

### Message Record Format
Each message in the log is stored with a fixed header followed by variable-length content:
| Field | Type | Description |
| --- | --- | --- |
| offset | Long (8 bytes) | Unique, monotonically increasing ID within partition |
| timestamp | Long (8 bytes) | When the message was produced (milliseconds since epoch) |
| key_length | Int (4 bytes) | Length of the key in bytes (-1 if null) |
| key | Bytes (variable) | Optional partition key |
| value_length | Int (4 bytes) | Length of the payload |
| value | Bytes (variable) | Actual message content |
| headers | Bytes (variable) | Optional key-value metadata |
| crc | Int (4 bytes) | CRC32 checksum for integrity verification |

The CRC is critical. Disks can have silent corruption, and we need to detect it before serving bad data to consumers.

### Topic Metadata
Stored in the coordinator's metadata store:
| Field | Type | Description |
| --- | --- | --- |
| topic_name | String | Unique topic identifier (primary key) |
| partition_count | Integer | Number of partitions (can increase, never decrease) |
| replication_factor | Integer | Number of replicas per partition |
| retention_ms | Long | How long to keep messages (default: 7 days) |
| cleanup_policy | Enum | "delete" (remove old) or "compact" (keep latest per key) |
| created_at | Timestamp | When the topic was created |

### Consumer Offset Record
Stored in an internal compacted topic (`__consumer_offsets`) or external store:
| Field | Type | Description |
| --- | --- | --- |
| group_id | String | Consumer group identifier |
| topic | String | Topic name |
| partition | Integer | Partition number |
| offset | Long | Last committed offset |
| metadata | String | Optional consumer-provided metadata |
| commit_timestamp | Timestamp | When this offset was committed |

The combination of (group_id, topic, partition) forms the primary key. This allows each consumer group to track its progress independently for each partition.

### Partition Assignment
The coordinator maintains the current state of partition assignments:
| Field | Type | Description |
| --- | --- | --- |
| topic | String | Topic name |
| partition | Integer | Partition number |
| leader_broker | Integer | Broker ID currently serving as leader |
| replica_brokers | Array[Int] | All broker IDs holding replicas |
| isr | Array[Int] | Broker IDs of in-sync replicas |
| leader_epoch | Long | Increments on each leader change (prevents stale reads) |

The ISR (In-Sync Replica) set is particularly important. Only brokers in the ISR are eligible to become leader, ensuring no data loss during failover.
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often go deeper into specific components. 
In this section, we will explore the trickiest parts of our design: delivery semantics, ordering guarantees, replication strategies, consumer group rebalancing, performance optimization, and message retention.
These are the topics that distinguish a good system design answer from a great one.

## 6.1 Message Delivery Semantics
"Will my message get delivered?" seems like a simple question, but the answer is surprisingly nuanced. The guarantees a message queue provides about delivery are called its "delivery semantics," and they represent one of the most important trade-offs in distributed systems.
There are three levels of guarantees, each with different implications for your application.

### At-Most-Once Delivery
This is the "fire and forget" approach. The producer sends a message and immediately moves on without waiting for confirmation. The message might get lost if the broker crashes before persisting it, but it will never be delivered more than once.

#### When it makes sense:
Think about metrics collection. If you are sending CPU usage samples every second, losing one sample is not a big deal. You have 59 other samples that minute. The simplicity and speed of at-most-once is worth the occasional loss.

#### When it does not make sense:
If you are processing payment confirmations, losing even one message means a customer paid but never got their order. That is unacceptable.
| Aspect | Implication |
| --- | --- |
| Latency | Lowest (no round-trip for ACK) |
| Throughput | Highest (fire and forget) |
| Data safety | Possible loss |
| Implementation | Simplest |

### At-Least-Once Delivery
This is the most common choice for production systems. The producer waits for acknowledgment before considering the message sent. If acknowledgment is lost or times out, the producer retries. This guarantees the message gets delivered, but it might be delivered more than once.
The key insight is that duplicates can happen at multiple points:
1. **Producer retries:** If the ACK is lost, the producer retries, causing a duplicate in the broker
2. **Consumer crashes:** If the consumer processes a message but crashes before committing its offset, it will reprocess that message after restart

#### Handling duplicates:
Your consumers must be idempotent, meaning processing the same message twice should have the same effect as processing it once. Common techniques:
- Use a unique message ID and check if you have seen it before
- Use database constraints (e.g., unique order_id prevents duplicate inserts)
- Design operations to be naturally idempotent (e.g., "set balance to $100" vs "add $100 to balance")

| Aspect | Implication |
| --- | --- |
| Latency | Medium (one round-trip for ACK) |
| Throughput | High (batching still possible) |
| Data safety | No loss |
| Consumer complexity | Must handle duplicates |

### Exactly-Once Delivery
This is the holy grail: each message delivered exactly once, with no loss and no duplication. It sounds simple but is surprisingly hard to achieve in a distributed system.
The challenge is that "exactly once" requires coordination across network boundaries. If a network partition happens mid-transaction, both sides might think they succeeded or failed, leading to duplicates or losses.

#### How modern systems achieve it:
**Producer side: Idempotent writes**
Each producer gets a unique ID. Each message includes a sequence number. The broker tracks the latest sequence per producer and rejects duplicates.
**Consumer side: Transactional processing**
The consumer processes messages and commits offsets atomically within a transaction:
If any step fails, everything rolls back. The message will be redelivered and processed again.
| Aspect | Implication |
| --- | --- |
| Latency | Highest (transaction overhead) |
| Throughput | Lower (less batching) |
| Data safety | Strongest |
| Implementation | Complex |

### Which Should You Choose?
| Semantic | Data Loss | Duplicates | Best For |
| --- | --- | --- | --- |
| At-Most-Once | Possible | Never | Metrics, logs, non-critical events |
| At-Least-Once | Never | Possible | Most applications (with idempotent consumers) |
| Exactly-Once | Never | Never | Financial transactions, critical data |

#### Recommendation
Start with at-least-once delivery and design your consumers to be idempotent. This covers 90% of use cases with reasonable complexity. Only invest in exactly-once if you have strict regulatory requirements or the cost of duplicates is truly unacceptable.

## 6.2 Message Ordering Guarantees
Ordering matters more than you might initially think. Consider a banking application where a user deposits $100, then withdraws $150. If the withdrawal is processed first, it fails due to insufficient funds. If the deposit is processed first, both succeed. Same messages, different order, completely different outcome.
The challenge is that ordering and parallelism are fundamentally at odds. Perfect global ordering means processing one message at a time. Maximum parallelism means abandoning ordering entirely. Most systems choose a middle ground.

### Partition-Level Ordering
This is the sweet spot for most applications. Messages with the same partition key are guaranteed to be in order, but messages across different partitions can be processed in parallel.
The magic is in the partition key. By using user ID as the key, all events for user-123 go to partition 0 and are processed in sequence. Events for user-456 go to partition 1 and can be processed concurrently by a different consumer.
**Choosing the right partition key:**
| Use Case | Partition Key | Why |
| --- | --- | --- |
| User events | User ID | All actions for one user stay ordered |
| Order processing | Order ID | All updates to one order stay ordered |
| IoT sensors | Device ID | All readings from one device stay ordered |
| Financial transactions | Account ID | All transactions for one account stay ordered |

### Global Ordering
Sometimes you truly need every message processed in sequence across the entire topic. This requires using a single partition, which means only one consumer can process messages.
**When global ordering makes sense:**
- Audit logs that must be perfectly sequential
- Database replication streams (like MySQL binlog)
- Single-writer scenarios with low volume

The throughput penalty is severe. With one partition, you are limited to what one consumer can handle, typically a few thousand messages per second instead of millions.

### Handling Out-of-Order Edge Cases
Even with partition-level ordering, there are edge cases where messages might appear out of order:
1. **Consumer rebalancing:** When partitions move between consumers, there can be a brief window where ordering is disrupted
2. **Retries with failures:** If a message fails processing and is retried while newer messages succeed, order is broken
3. **Multiple partitions for same key:** If partition count changes, key-to-partition mapping changes

#### Defensive strategies:
1. **Include sequence numbers:** Each message carries its expected position. Consumers can detect and handle gaps.
2. **Idempotent operations:** Design your processing to be safe regardless of order when possible.
3. **Event timestamps:** Include creation timestamps and sort before processing if order is critical.

### Summary
| Ordering Level | Parallelism | Throughput | Use Case |
| --- | --- | --- | --- |
| None | Maximum | Highest | Independent events, metrics |
| Per-partition | Proportional to partitions | High | Most applications |
| Global | None (1 consumer) | Limited | Audit logs, strict sequences |

#### Recommendation
Use partition-level ordering with well-designed keys. Most business requirements that seem to need global ordering can actually be satisfied with per-entity ordering.

## 6.3 Data Replication and Fault Tolerance
Storing data on a single machine is a recipe for disaster. Hard drives fail. Servers crash. Data centers lose power. To build a system that survives these failures, we need to replicate data across multiple machines, ideally in different failure domains.
But replication introduces its own challenges. How do we keep replicas in sync? What happens when they diverge? How do we balance durability with performance? These questions are at the heart of distributed systems design.

### Leader-Follower Replication
Our system uses leader-follower replication, where one replica is designated the "leader" and handles all reads and writes, while other replicas ("followers") continuously copy data from the leader.

#### Why leader-follower?
The alternative is multi-leader or leaderless replication, where any replica can accept writes. This allows higher write throughput but introduces consistency challenges. With leader-follower, the leader is the single source of truth, making conflict resolution trivial.

### In-Sync Replicas (ISR)
Not all followers are equal. Some might be caught up with the leader. Others might be lagging due to network issues or slow disks. We call the set of replicas that are fully caught up the "In-Sync Replicas" or ISR.
A replica is considered in-sync if:
1. It has fetched all messages up to the leader's current offset
2. It has sent a heartbeat within the configured timeout (typically 10-30 seconds)

ISR membership is dynamic. A slow follower drops out of the ISR. Once it catches up, it rejoins. This allows the system to maintain strong guarantees while tolerating temporary slowdowns.

### Acknowledgment Modes
The producer can choose how many replicas must confirm a write before it is considered successful. This is the classic trade-off between durability and latency.
| Setting | Durability | Latency | When to Use |
| --- | --- | --- | --- |
| acks=0 | Lowest (may lose) | Lowest | Metrics, logs where loss is acceptable |
| acks=1 | Medium (leader only) | Low | Good balance for most cases |
| acks=all | Highest (all ISR) | Higher | Critical data, financial transactions |

For production systems handling important data, we recommend `acks=all` combined with `min.insync.replicas=2`. This ensures that even if one replica fails immediately after the write, the data survives on at least one other replica.

### Leader Election
When a leader fails, the system must elect a new one. This is where the ISR set becomes critical.
The election process:
1. **Detection:** The coordinator notices the leader has stopped sending heartbeats
2. **Selection:** Any in-sync replica can become the new leader (they all have the same data)
3. **Promotion:** The chosen follower switches to leader mode
4. **Notification:** Producers and consumers are notified to use the new leader

#### The unclean leader election dilemma
What if all ISR members fail simultaneously? The system faces a choice:
- **Wait for ISR recovery:** The partition is unavailable until an in-sync replica comes back. No data loss, but downtime.
- **Promote an out-of-sync replica:** The partition is available immediately, but messages that were only on ISR members are lost.

This is a classic CAP theorem trade-off. Most systems default to waiting for ISR recovery, prioritizing consistency over availability. Some allow configuring "unclean leader election" for use cases where availability is more important than data integrity.

### Summary
| Setting | Durability | Latency | Availability |
| --- | --- | --- | --- |
| acks=0 | Lowest | Lowest | Highest |
| acks=1 | Medium | Low | High |
| acks=all | Highest | Highest | Depends on ISR |

**Recommendation:** Use **acks=all** with **min.insync.replicas=2** for production systems where data loss is unacceptable.

## 6.4 Consumer Group Rebalancing
Consumer group rebalancing is one of those things that works invisibly when everything is fine, but becomes very visible when it goes wrong. When consumers join, leave, or crash, the system must redistribute partitions among the remaining consumers. This redistribution is called rebalancing.
The challenge is doing this without losing messages or processing them twice. Let us explore how it works.

### When Rebalancing Occurs
The most common triggers are consumers joining (scaling up) and consumers crashing (detected via missed heartbeats). In production, you want to minimize rebalances because they temporarily pause consumption.

### Rebalancing Strategies
There are two main approaches, and the difference matters a lot for large consumer groups.

#### Eager Rebalancing (Stop-the-World)
In eager rebalancing, when any change occurs, all consumers stop processing, revoke all their partitions, and wait for new assignments. It is simple but disruptive.
The problem is clear: when C3 joins, C1 and C2 stop processing even though they might not give up any partitions. For a large group with 50 consumers, this stop-the-world pause affects everyone.

#### Incremental Cooperative Rebalancing
A smarter approach only moves the partitions that actually need to move. Consumers that are not affected continue processing throughout.

### Partition Assignment Strategies
Once we know which partitions need to be assigned, how do we decide who gets what?
| Strategy | How It Works | Best For |
| --- | --- | --- |
| Range | Divide partitions sequentially | Simple cases, sorted topics |
| Round-Robin | Distribute evenly one by one | Even load distribution |
| Sticky | Minimize changes from previous | Stable groups, minimize disruption |

### Minimizing Rebalance Impact
In production, you want to minimize both the frequency and duration of rebalances:
1. **Use static membership:** Assign each consumer a persistent ID. If a consumer restarts with the same ID, it gets its old partitions back without triggering a full rebalance.
2. **Tune heartbeat settings:** Longer heartbeat intervals reduce false positives (consumer marked dead when it is just slow) but increase detection time for actual failures.
3. **Graceful shutdowns:** When stopping a consumer, call the leave-group API instead of just killing the process. This triggers an immediate rebalance instead of waiting for heartbeat timeout.
4. **Right-size your groups:** More consumers than partitions means idle consumers. Too few means overloaded consumers. Match your consumer count to your partition count.

| Strategy | Disruption | Complexity | Best For |
| --- | --- | --- | --- |
| Eager | High (all stop) | Low | Small groups, simple setups |
| Cooperative | Low (partial) | Medium | Large groups, production |
| Sticky | Lowest | Medium | Stable groups |

**Our recommendation:** Use incremental cooperative rebalancing with sticky assignment. The slightly higher complexity is worth the dramatically reduced disruption in production.

## 6.5 Handling High Throughput
A million messages per second is not something you achieve by accident. It requires optimization at every layer of the stack, from how producers batch messages to how the operating system manages disk I/O. Let us explore the techniques that make this possible.

### Producer-Side Optimizations
The producer is often the bottleneck if not configured properly. Three key optimizations make the difference.

#### Batching
Sending messages one at a time means one network round-trip per message. At a million messages per second, that is a million round-trips, clearly impossible.
Instead, producers accumulate messages in memory and send them in batches:
The trade-off is latency: messages wait in the batch buffer until either the batch fills or a timeout expires. For most use cases, 5-10ms of added latency is acceptable for 100x better throughput.

#### Compression
Text-based messages (JSON, XML) compress well. A 2 KB message might compress to 500 bytes, reducing network bandwidth by 75%.
| Algorithm | Compression Ratio | CPU Cost | Best For |
| --- | --- | --- | --- |
| None | 1.0x | None | Already compressed data |
| Snappy | 2-3x | Low | Balance of speed and ratio |
| LZ4 | 2-3x | Low | Speed-critical workloads |
| GZIP | 4-5x | High | Bandwidth-constrained networks |

For most use cases, LZ4 or Snappy provide the best trade-off. GZIP compresses better but the CPU overhead can actually hurt throughput.

#### Async Sending
Producers do not wait for each message to be acknowledged. They send messages asynchronously and process acknowledgments in batches:
This hides network latency and allows the producer to saturate the network connection.

### Broker-Side Optimizations
Brokers handle the heavy lifting. Several optimizations make high throughput possible.

#### Sequential I/O
The append-only log design is not just about simplicity. It is about I/O performance.
A single HDD can write 100 MB/sec randomly but 500+ MB/sec sequentially. SSDs are less affected but still benefit. By always appending, we get predictable, high throughput.

#### Zero-Copy Transfer
When a consumer reads messages, the traditional path involves multiple copies:
The `sendfile()` system call skips the user-space copy entirely, reducing CPU usage by 50% or more for read-heavy workloads.

#### Page Cache
Rather than implementing our own caching layer, we let the operating system handle it:
- Writes go to the OS page cache first, then to disk asynchronously
- Frequently read data stays in memory automatically
- The OS manages cache size dynamically based on available RAM
- Data survives broker restarts (warm cache)

This is simpler than a custom cache and often performs better because the OS has more visibility into memory pressure.

#### Horizontal Partitioning
Perhaps the most important optimization: more partitions means more parallelism.
Each partition can be on a different disk, a different broker, even a different data center. Linear scaling through partitioning is how Kafka and similar systems achieve millions of messages per second.

### Consumer-Side Optimizations
Consumers can also become bottlenecks. Three techniques help:
1. **Parallel consumption:** Multiple consumers in a group process different partitions concurrently
2. **Prefetching:** Consumers fetch messages ahead of what they are processing, hiding network latency
3. **Batched commits:** Commit offsets every N messages or T seconds instead of after each message

### Summary
| Layer | Optimization | Impact |
| --- | --- | --- |
| Producer | Batching | 10-100x fewer network calls |
| Producer | Compression | 2-5x less bandwidth |
| Broker | Sequential I/O | 100-1000x faster writes |
| Broker | Zero-copy | 50% less CPU usage |
| Broker | Partitioning | Linear scalability |
| Consumer | Parallel consumption | Linear with partition count |

## 6.6 Message Retention and Cleanup
We calculated earlier that 7 days of messages at our scale requires nearly 2 petabytes of storage. Without cleanup, that number would grow indefinitely. Retention policies determine when and how messages are deleted.
There are three approaches, each suited to different use cases.

### Time-Based Retention
The most common policy: delete messages older than a configured duration. Our requirements specify 7 days, which is typical for event streams.

#### How it works:
The system does not delete individual messages. Instead, it operates on segment files:
A background cleaner thread periodically scans segment files. Each segment has a maximum timestamp (from its last message). If all messages in a segment are older than the retention period, the entire segment file is deleted.
This approach is efficient because deleting a file is a single filesystem operation, regardless of how many messages it contains.

### Size-Based Retention
Sometimes you care more about storage budget than age. Size-based retention deletes the oldest segments when the partition exceeds a size limit.
This is useful when:
- Storage is constrained or expensive
- Message rate is unpredictable
- You want a hard cap on disk usage

### Compaction
Compaction is fundamentally different from deletion. Instead of removing old messages, it keeps only the latest value for each unique key.
This is perfect for changelog topics where you want to reconstruct the current state of a system. A compacted topic can serve as a "snapshot" that new consumers can read to catch up quickly.

### The Cleanup Process
Cleanup runs continuously in the background:
1. A log cleaner thread scans partitions
2. For time/size retention: identifies expired segment files and deletes them
3. For compaction: reads segment files, builds a map of key to latest offset, rewrites a new segment with only the latest values
4. Updates index files to reflect changes

The key insight is that cleanup operates on immutable segment files. The active segment (currently receiving writes) is never touched by cleanup.

### Summary
| Policy | When to Use | Storage Behavior |
| --- | --- | --- |
| Time-based | Event streams, logs, auditing | Predictable growth, hard age limit |
| Size-based | Budget-constrained, variable load | Hard storage cap |
| Compaction | Changelogs, state snapshots | Depends on key cardinality |

Most production deployments use time-based retention with a default of 7 days. Compaction is added for specific topics that need state reconstruction.
# References
- [Kafka: a Distributed Messaging System for Log Processing](https://www.microsoft.com/en-us/research/wp-content/uploads/2017/09/Kafka.pdf) - Original Kafka paper from LinkedIn
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/) - Comprehensive guide on Kafka architecture
- [Amazon SQS Developer Guide](https://docs.aws.amazon.com/sqs/index.html) - AWS's managed queue service documentation
- [The Log: What every software engineer should know](https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying) - Jay Kreps' foundational article on logs
- [RabbitMQ vs Kafka](https://www.confluent.io/blog/kafka-fastest-messaging-system/) - Comparison of messaging paradigms

# Quiz

## Design Messaging Queue Quiz
What is the primary purpose of a distributed message queue in system design?