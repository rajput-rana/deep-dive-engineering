# 🚀 Apache Kafka

<div align="center">

**Distributed, durable, high-throughput event streaming platform**

[![Kafka](https://img.shields.io/badge/Apache-Kafka-orange?style=for-the-badge)](https://kafka.apache.org/)
[![Throughput](https://img.shields.io/badge/Throughput-Millions%2Fsec-green?style=for-the-badge)](./)
[![Durability](https://img.shields.io/badge/Durability-Replayable-blue?style=for-the-badge)](./)

*Kafka is not just a queue, pub/sub, or streaming platform. It's an append-only, replicated, distributed commit log.*

</div>

---

## 🎯 What is Kafka?

<div align="center">

**Apache Kafka is a distributed, durable, high-throughput event log.**

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **📝 Append-Only Log** | Immutable, ordered sequence of events |
| **🔄 Replicated** | Data replicated across multiple brokers |
| **📈 High Throughput** | Millions of messages per second |
| **💾 Durable** | Messages persisted to disk |
| **🔁 Replayable** | Consumers can read data multiple times |

**Mental Model:** Think of Kafka as Netflix (consumer decides when to watch) vs TV (you just watch, no control)

</div>

---

## ⚡ Throughput vs Latency

<div align="center">

### 🚚 Simple Analogy

| Metric | Analogy | Description |
|:---:|:---:|:---:|
| **Throughput** | How many boxes a highway can carry per hour | Work per unit time |
| **Latency** | How long one box takes to reach destination | Time for one operation |

### Kafka's Trade-off

<div align="center">

**Kafka optimizes throughput, not minimal latency.**

| Capability | Typical Performance |
|:---:|:---:|
| **Single Broker** | Hundreds of MB/sec |
| **Cluster** | Multiple GB/sec |
| **Latency** | Usually tens of milliseconds (not microseconds) |

**💡 Key Insight:** *"Kafka trades ultra-low latency for extremely high throughput and durability."*

</div>

</div>

---

## 🏗️ Core Concepts

<div align="center">

### Essential Building Blocks

| Concept | Description | Key Point |
|:---:|:---:|:---:|
| **📨 Producer** | Services producing events | Writes to Kafka topics |
| **📋 Topic** | Named log of events | Logical category for messages |
| **📦 Partition** | Ordered, append-only log | Unit of parallelism & ordering |
| **👥 Consumer** | Subscribes to topics | Processes events one at a time |
| **👨‍👩‍👧‍👦 Consumer Group** | Multiple consumers sharing load | Kafka distributes load automatically |
| **🖥️ Broker** | Kafka server node | Stores partitions, manages replication |
| **🔄 Streams** | Continuous data flow | Aggregations, joins, transformations |

</div>

---

## 📦 Partitions: The Most Important Concept

<div align="center">

### What is a Partition?

**A partition is Kafka's unit of parallelism and ordering—an immutable, ordered log that enables scalability and fault tolerance.**

### Simple Mental Model

```
Topic = folder
Partition = file inside the folder (ordered line by line)
```

### Example Structure

```
Topic: orders
 ├─ Partition 0 → order-1, order-4, order-7
 ├─ Partition 1 → order-2, order-5
 └─ Partition 2 → order-3, order-6
```

</div>

---

## 🔑 Key Properties of Partitions

<div align="center">

| Property | Description | Implication |
|:---:|:---:|:---:|
| **📝 Ordered** | Messages in a partition are strictly ordered | Ordering guaranteed only within partition |
| **🔢 Sequential Offsets** | Each message has a sequential ID | Consumers track position via offset |
| **🖥️ Leader-Based** | One broker hosts leader, others replicate | Fault tolerance via replication |
| **⚖️ Parallelism** | Each partition processed independently | More partitions = more parallelism |

**⚠️ Critical Rule:** *Kafka guarantees ordering ONLY within a partition, not globally.*

</div>

---

## 🎯 How Kafka Assigns Messages to Partitions

<div align="center">

### Case 1: Message Has a Key (Most Important)

**Formula:**
```
partition = hash(key) % number_of_partitions
```

**Result:**
- Same key → always same partition
- Guarantees ordering for that key

**Example:**
```
key = userId=123 → always Partition 2
```

**✅ Use When:**
- Ordering matters (orders, payments, user events)

---

### Case 2: No Key Provided

**Strategy:**
- Round-robin (default modern clients)
- Or sticky partitioning (batch-friendly)

**Result:**
- Even distribution
- No ordering guarantee

**✅ Use When:**
- Ordering doesn't matter
- Throughput is priority

---

### Case 3: Custom Partitioner

**Custom Logic:**
- Route VIP customers to specific partitions
- Geo-based routing

**⚠️ Trade-off:**
- Risk of hot partitions
- More operational complexity

</div>

---

## 📊 Partitioning Strategy Guide

<div align="center">

### How Many Partitions Should You Create?

| Factor | Consideration |
|:---:|:---:|
| **📈 Throughput** | More partitions → higher parallelism |
| **👥 Consumers** | Max parallel consumers = number of partitions |
| **🔢 Ordering Needs** | Ordering guaranteed only within partition |
| **📅 Future Growth** | Over-provision slightly; increasing later affects key ordering |
| **🖥️ Broker Limits** | Too many partitions increase broker load |

**✅ Rule of Thumb:** Start with `max(expected consumers) × (2–3)` and adjust based on throughput and growth.

</div>

---

## ⚠️ Can You Change Partition Count?

<div align="center">

| Action | Allowed? | Impact |
|:---:|:---:|:---:|
| **Increase Partitions** | ✅ Yes | Key → partition mapping changes |
| **Decrease Partitions** | ❌ No | Must create new topic |

### What Happens When Partitions Increase?

**Existing Records:**
- Ordering preserved within original partitions

**After Increase:**
- Key → partition mapping changes (hash mod N)
- Same key may go to different partition
- **Global key ordering breaks across old vs new records**

**✅ Mitigation:**
- Use custom partitioner that keeps old mapping stable
- Avoid increasing partitions for topics requiring strict per-key ordering

</div>

---

## 🚨 Common Partition Pitfalls

<div align="center">

| Pitfall | Cause | Mitigation |
|:---:|:---:|:---:|
| **🔥 Hot Partitions** | Skewed keys (e.g., userId=1 very active) | Better key design, key salting, custom partitioning |
| **🔄 Changing Partition Count** | Key → partition mapping changes | Over-provision early (but not too much) |
| **📊 Too Many Partitions** | Metadata overhead, slower rebalances | Create only as many as needed |

### Why Too Many Partitions Hurt Performance

| Issue | Impact |
|:---:|:---:|
| **Metadata Overhead** | Each partition consumes broker memory, file handles, CPU |
| **Controller Pressure** | Slower broker leader elections |
| **Rebalance Cost** | Slower consumer rebalances |
| **Operational Complexity** | Network & disk become bottlenecks |

**💡 Typical Guidance:**
- **10–100 partitions:** Most production topics
- **1000+ partitions:** Only for very high throughput or very large consumer fleets

</div>

---

## 👥 Consumer Groups & Scaling

<div align="center">

### Core Rule

**One partition can be consumed by only one consumer in a consumer group**

### Scaling Scenarios

| Scenario | Partitions | Consumers | Result |
|:---:|:---:|:---:|:---:|
| **❌ Too Few** | 3 | 10 | Only 3 active, 7 idle |
| **✅ Balanced** | 10 | 10 | Max parallelism, ideal throughput |
| **⚠️ Too Many** | 1000 | 20 | Consumers overloaded, expensive rebalances |

**💡 Key Insight:** *"Add consumers" does NOT increase throughput beyond partition count.*

</div>

---

## 🎯 Partitioning Trade-offs (Interview Gold)

<div align="center">

| Goal | Partition Choice | Trade-off |
|:---:|:---:|:---:|
| **Max Ordering** | Fewer partitions + key | Lower parallelism |
| **Max Throughput** | More partitions | Less ordering guarantee |
| **Easy Ops** | Moderate partitions | Balance of both |
| **Fast Rebalances** | Fewer partitions | Less parallelism |

**💡 Bottom Line:** Partitioning is a balance between ordering guarantees, parallelism, and operational complexity.

</div>

---

## 🖥️ Brokers & Clusters

<div align="center">

### Broker

**A broker is one Kafka server (one running Kafka instance).**

**What a broker does:**
- Stores topic partitions on disk
- Accepts writes from producers
- Serves reads to consumers
- Manages replication for its partitions

---

### Cluster

**A cluster is a group of brokers working together.**

**What a cluster provides:**
- **Scalability** - Data spread across brokers
- **Fault Tolerance** - Replicas on different brokers
- **High Availability** - Leader election on failure

**Example:**
```
Multiple brokers acting as one distributed Kafka system
```

</div>

---

## ⚡ Why Kafka Achieves High Throughput

<div align="center">

### Key Techniques

| Technique | How It Helps |
|:---:|:---:|
| **📝 Sequential Disk Writes** | Avoids random IO (very fast) |
| **💾 OS Page Cache** | Leverages operating system caching |
| **📦 Batching Messages** | Producers send batches, not single messages |
| **🚀 Zero-Copy Transfer** | Uses sendfile for efficient data transfer |
| **⚖️ Partitioned Parallelism** | Each partition processed independently |
| **🔽 Pull-Based Consumers** | Consumers control pace → no backpressure collapse |

**💡 Trade-off:** Kafka's high throughput comes at cost of higher latency than in-memory queues.

</div>

---

## 🔄 Data Flow in Kafka

<div align="center">

### Producer → Kafka Flow

| Step | Description |
|:---:|:---:|
| **1️⃣** | Producer serializes message |
| **2️⃣** | Chooses partition (key or round-robin) |
| **3️⃣** | Appends to leader partition |
| **4️⃣** | Replicas copy it |
| **5️⃣** | ACK returned based on config |

---

### Consumer → Kafka Flow

| Step | Description |
|:---:|:---:|
| **1️⃣** | Consumer polls |
| **2️⃣** | Fetches batch of messages |
| **3️⃣** | Processes messages |
| **4️⃣** | Commits offsets (sync/async) |

</div>

---

## ✅ Delivery Semantics

<div align="center">

### Three Delivery Guarantees

| Semantics | Offset Commit | Pros | Cons |
|:---:|:---:|:---:|:---:|
| **At-Most-Once** | Before processing | Fast | Data loss possible |
| **At-Least-Once** | After processing (DEFAULT) | No data loss | Duplicates possible |
| **Exactly-Once** | With transactions | No loss, no duplicates | Requires idempotent producers, transactions |

**💡 Key Insight:** *"Kafka provides exactly-once within Kafka, but end-to-end exactly-once requires downstream cooperation."*

</div>

---

## 🔥 Producer Challenges & Solutions

<div align="center">

### Common Issues

| Challenge | Why It Happens | Mitigation |
|:---:|:---:|:---:|
| **🔥 Duplicate Messages** | Producer retries after timeout, ACK lost | Enable idempotent producer (`enable.idempotence=true`) |
| **🔄 Message Ordering Breaks** | Multiple partitions, multiple producers | Use message key, ensure same key → same partition |
| **💥 Message Loss** | `acks=1` or `acks=0`, leader dies before replication | Use `acks=all`, `min.insync.replicas=2` |

### Producer Configuration

| Config | Options | Recommendation |
|:---:|:---:|:---:|
| **acks** | `0`, `1`, `all` | `all` for durability |
| **retries** | Number | Enable with backoff |
| **idempotence** | `true`/`false` | `true` to prevent duplicates |

</div>

---

## 🔥 Consumer Challenges & Solutions

<div align="center">

### Common Issues

| Challenge | Why It Happens | Mitigation |
|:---:|:---:|:---:|
| **⚡ Rebalancing Storms** | Consumer joins/leaves, deployments, GC pauses | Cooperative rebalancing, static group membership, longer session timeouts |
| **🔄 Duplicate Processing** | Crash after processing but before offset commit | Idempotent consumers, deduplication at sink, exactly-once with transactions |
| **🐌 Slow Consumers (LAG)** | Heavy processing, too few consumers, hot partitions | Increase partitions, scale consumers, parallelize processing |

### Consumer Lag

**Formula:**
```
Lag = latest offset − consumer offset
```

**Causes:**
- Heavy processing
- Too few consumers
- Hot partitions

**Solutions:**
- Increase partitions
- Scale consumers
- Parallelize processing

</div>

---

## 💾 Storage & Retention

<div align="center">

### Key Point

**Kafka does NOT delete after consume.**

### Retention Policies

| Policy Type | Configuration | Description |
|:---:|:---:|:---:|
| **Time-Based** | `retention.ms` | Delete messages older than X time |
| **Size-Based** | `retention.bytes` | Delete when topic exceeds size |
| **Compaction** | `cleanup.policy=compact` | Keep latest value per key |

### Default Retention

**7 days** (`log.retention.hours = 168`)

Can also be size-based (`log.retention.bytes`)

Topic-level config overrides broker default

---

### Log Compaction (Advanced)

**Keeps latest value per key.**

**Use Cases:**
- User profile state
- Config updates

**Trade-off:**
- No full history
- More disk IO

</div>

---

## 🔐 Security in Kafka

<div align="center">

### Three Pillars of Security

| Pillar | Purpose | Tool |
|:---:|:---:|:---:|
| **🔒 Encryption** | Protect data in transit | TLS |
| **👤 Authentication** | Identity verification | SASL / mTLS |
| **🛡️ Authorization** | Access control | ACLs |
| **🚦 Protection** | Throttling | Quotas |

---

### A. Encryption - TLS

**Purpose:**
- Encrypts data in transit
- Prevents eavesdropping & MITM attacks

**Where Used:**
- Client ↔ Broker
- Broker ↔ Broker

**Config (Broker):**
```properties
listeners=SSL://:9093
ssl.keystore.location=/path/kafka.keystore.jks
ssl.keystore.password=***
ssl.truststore.location=/path/kafka.truststore.jks
```

---

### B. Authentication - SASL / mTLS

**SASL Mechanisms:**

| Mechanism | Description | Use Case |
|:---:|:---:|:---:|
| **PLAIN** | Username + password | Simple, needs TLS |
| **SCRAM** | Salted Challenge Response | Stronger than PLAIN |
| **GSSAPI** | Kerberos | Enterprise SSO |

**mTLS:**
- Client cert = identity
- No username/password
- `ssl.client.auth=required`

---

### C. Authorization - ACLs

**Resources:**
- Topic
- Consumer Group
- Cluster
- Transactional ID

**Operations:**
- READ, WRITE, CREATE, DELETE, DESCRIBE

**Example:**
```bash
kafka-acls.sh --add \
  --allow-principal User:app1 \
  --operation Read \
  --topic orders
```

---

### D. Quotas (DoS Protection)

**Prevent noisy tenants:**
```properties
producer_byte_rate=1048576
consumer_byte_rate=1048576
```

</div>

---

## 💰 Kafka Cost Considerations

<div align="center">

### Core Cost Drivers

| Driver | Description | Impact |
|:---:|:---:|:---:|
| **🖥️ Brokers** | VM/instance size, number of brokers | Compute cost |
| **💾 Storage** | Disk size, retention period, replication factor | Storage cost |
| **🌐 Network** | Producer traffic, replication traffic, cross-AZ/region | Network cost |
| **⚙️ Operations** | Zookeeper/KRaft, monitoring, backups | Ops cost |

### Simple Cost Model

```
Cost ≈ (Brokers × Size × Hours)
     + (Storage × Replication × Retention)
     + Network
     + Ops
```

---

### 🔴 Biggest Cost Killers

| Killer | Impact |
|:---:|:---:|
| **High Replication Factor** | Multiplies storage cost |
| **Long Retention** | Increases storage needs |
| **Too Many Partitions** | Increases metadata overhead |
| **Large Message Size** | Increases network & storage |
| **Cross-AZ/Region Traffic** | Expensive network costs |

---

### ✅ Cost Optimization Levers

| Lever | Action | Benefit |
|:---:|:---:|:---:|
| **Retention** | Use `retention.hours` + `retention.bytes` | Control storage growth |
| **Replication** | Prod: 3, Non-prod: 1–2 | Reduce storage multiplier |
| **Partitions** | Avoid "just in case" partitions | Reduce metadata overhead |
| **Message Size** | Keep < 1 MB, externalize blobs | Reduce network & storage |
| **Quotas** | Per-tenant limits | Prevent runaway costs |

</div>

---

## 🎯 Kafka vs Alternatives

<div align="center">

### Kafka vs RabbitMQ

| Feature | Kafka | RabbitMQ |
|:---:|:---:|:---:|
| **Model** | Pull-based | Push-based |
| **Storage** | Persistent log | Message queue |
| **Replay** | Replayable | No replay |
| **Throughput** | High throughput | Low latency |
| **Use Case** | Event streaming | Task queues |

---

### Kafka vs Pulsar

| Feature | Kafka | Pulsar |
|:---:|:---:|:---:|
| **Maturity** | Mature ecosystem | Newer |
| **Model** | Simpler mental model | Separate compute/storage |
| **Multi-tenancy** | Good | Better |
| **Use Case** | Event streaming | Event streaming |

</div>

---

## 🎓 Interview Questions & Answers

<div align="center">

### Top 10 Tough Questions

| Question | Strong Answer |
|:---:|:---:|
| **Can Kafka lose data?** | Yes, depending on configuration. Kafka trades availability for durability based on settings like `acks`, ISR, and leader election |
| **How do you ensure ordering?** | By using keys so related messages go to the same partition |
| **What happens during consumer rebalance?** | Partitions are revoked and reassigned, causing temporary pause and potential duplicate processing |
| **Can two consumers read same message?** | Yes, if they are in different consumer groups |
| **Why not infinite partitions?** | Metadata overhead, rebalancing cost, OS limits |
| **What's the default retention?** | 7 days (`log.retention.hours = 168`) |
| **Ideal message size?** | Best practice: < 1 MB. Ideal: 10 KB – 100 KB |
| **How does Kafka achieve high throughput?** | Sequential disk writes, batching, zero-copy transfer, partitioned parallelism |
| **What's the difference between Kafka and a queue?** | Kafka is a distributed, replicated, ordered log where consumers track their own position. Messages aren't deleted after consumption |
| **How do you achieve exactly-once?** | Idempotent producer + transactions + read-process-write in one transaction |

</div>

---

## 📋 Configuration Best Practices

<div align="center">

### Producer Configuration

| Config | Recommended Value | Why |
|:---:|:---:|:---:|
| `acks` | `all` | Strongest durability |
| `enable.idempotence` | `true` | Prevent duplicates |
| `retries` | `3` (or higher) | Handle transient failures |
| `batch.size` | `16384` (16 KB) | Balance latency vs throughput |

---

### Consumer Configuration

| Config | Recommended Value | Why |
|:---:|:---:|:---:|
| `auto.offset.reset` | `earliest` or `latest` | Define behavior on first read |
| `enable.auto.commit` | `false` | Manual control for exactly-once |
| `max.poll.records` | `500` | Balance processing vs rebalance time |
| `session.timeout.ms` | `30000` (30s) | Balance detection vs false positives |

---

### Broker Configuration

| Config | Recommended Value | Why |
|:---:|:---:|:---:|
| `log.retention.hours` | `168` (7 days) | Reasonable default retention |
| `min.insync.replicas` | `2` | Durability guarantee |
| `unclean.leader.election.enable` | `false` | Prevent data loss |
| `num.network.threads` | `8` | Handle concurrent requests |

</div>

---

## 🚀 When to Use Kafka

<div align="center">

### ✅ Kafka Wins When:

| Scenario | Why Kafka |
|:---:|:---:|
| **📊 Massive Volume** | Millions of events per second |
| **⏱️ Slight Delay Acceptable** | Optimized for throughput, not latency |
| **💾 Durability Matters** | Messages persisted to disk |
| **🔁 Replayability Needed** | Consumers can read multiple times |
| **🔄 Temporal Decoupling** | Producer doesn't care when consumer reads |
| **🌐 Spatial Decoupling** | Producer doesn't know consumers |
| **📈 Scalability Required** | Horizontal scaling via partitions |

---

### ❌ Kafka May Not Be Ideal When:

| Scenario | Why Not Kafka |
|:---:|:---:|
| **⚡ Ultra-Low Latency** | Kafka has tens of milliseconds latency |
| **📨 Request-Response** | Kafka is event-driven, not request-response |
| **💬 Simple Queuing** | RabbitMQ might be simpler |
| **🔢 Small Scale** | Overhead not worth it for small systems |

</div>

---

## 🎯 Mental Model to Remember

<div align="center">

### Key Insight

**Kafka is NOT a queue.**

**Kafka IS:** A distributed, replicated, ordered log where consumers track their own position.

### Simple Analogy

| System | Analogy | Control |
|:---:|:---:|:---:|
| **Kafka** | Netflix | Consumer decides when to watch |
| **Traditional Queue** | TV | You just watch, no control |

### Core Philosophy

1. **Append-Only Log** - Immutable, ordered sequence
2. **Consumer-Controlled** - Consumers pull, Kafka never pushes
3. **Replayable** - Read data multiple times
4. **Partitioned** - Unit of parallelism and ordering
5. **Durable** - Messages persisted, not deleted after consumption

</div>

---

## 📚 Additional Resources

<div align="center">

| Resource | Description |
|:---:|:---:|
| **[Official Kafka Documentation](https://kafka.apache.org/documentation/)** | Complete Kafka documentation |
| **[Confluent Platform](https://www.confluent.io/)** | Enterprise Kafka platform |
| **[Kafka Streams](https://kafka.apache.org/documentation/streams/)** | Stream processing library |

</div>

---

<div align="center">

**Master Kafka for high-throughput event streaming! 🚀**

*Remember: Kafka trades ultra-low latency for extremely high throughput and durability.*

</div>

