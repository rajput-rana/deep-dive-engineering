# DynamoDB Deep Dive for System Design Interviews

When Amazon needed a database that could handle Prime Day, they built DynamoDB. In 2023, DynamoDB processed over 89 million requests per second during peak traffic, powering the shopping carts, inventory checks, and order processing that make the world's largest shopping event possible. 
DynamoDB achieves this scale through a fundamentally different approach than traditional databases. 
Instead of optimizing for flexible queries, it optimizes for predictable performance at any scale. Instead of normalizing data, it requires you to design your schema around your access patterns. These trade-offs are not limitations to work around. They are the source of DynamoDB's power.
But this power comes with responsibility. Choose DynamoDB for the wrong workload, and you will fight the database instead of leveraging it. Model your data incorrectly, and you will hit hot partitions that throttle your entire application.
This chapter covers the practical DynamoDB knowledge that matters in system design interviews: data modeling, capacity planning, and patterns for solving common problems like hot partitions and transactions.

### DynamoDB Architecture Overview
Application servers talk to DynamoDB through an optional **DAX cluster** (DynamoDB Accelerator). DAX is an in-memory, managed cache that can serve repeated reads with microsecond latency. On a cache miss (or for writes), DAX forwards the request to DynamoDB.
Inside DynamoDB, the **Request Router** receives each operation and routes it to the correct **storage partition** based on the item’s partition key. 
DynamoDB spreads data across many partitions so it can scale throughput and storage horizontally. As your table grows or traffic increases, DynamoDB can add/split partitions behind the scenes (you don’t manage nodes).
Each partition is replicated across multiple **Availability Zones** (AZ-1/AZ-2/AZ-3 replicas in the diagram). This multi-AZ replication provides high availability and durability: if an AZ or individual storage host fails, DynamoDB can continue serving traffic from other replicas.
Net effect:
- **Partitioning** gives horizontal scale (more partitions → more parallel throughput).
- **Replication across AZs** gives resilience (no single-machine or single-AZ failure takes the table down).
- **DAX** (when used) reduces read latency and offloads repetitive read traffic, which is especially useful for hot keys and read-heavy workloads.

# 1. When to Choose DynamoDB
Every database makes trade-offs. DynamoDB traded query flexibility for predictable performance at any scale. Understanding exactly where this trade-off pays off, and where it costs you, is essential for making defensible database choices in interviews.

### 1.1 Choose DynamoDB When You Have

#### Known access patterns
This is the fundamental requirement. DynamoDB forces you to design your schema around how you will query data, not around data relationships. 
If you can enumerate your access patterns upfront, perhaps because you are building a well-understood system like a shopping cart or session store, DynamoDB rewards this clarity with exceptional performance. If you are still discovering how users will query the data, this rigidity becomes a liability.

#### High scale requirements
DynamoDB was built for Amazon's scale. It handles millions of requests per second without performance degradation because its architecture partitions data automatically across many nodes. 
The same design that serves ten requests per second serves ten million, without you managing any infrastructure.

#### Low latency needs
DynamoDB provides single-digit millisecond response times at any scale. This is not an aspirational SLA; it is the operational reality. Add DAX (DynamoDB Accelerator) and you get microsecond latency for repeated reads. 
For applications where latency directly impacts user experience or revenue, this predictability matters.

#### Key-value or simple query patterns
DynamoDB excels at primary key lookups and range queries within a partition. Get a user by ID? Instant. Get all orders for a user in the last month? Efficient. But complex aggregations, ad-hoc queries, or operations requiring data from multiple partitions? These fight against DynamoDB's architecture.

#### Variable or unpredictable traffic
On-demand capacity mode scales instantly with traffic, handling Black Friday spikes without pre-provisioning. You pay per request rather than for reserved capacity, trading some cost efficiency for operational simplicity.

#### Operational simplicity as a priority
DynamoDB is fully managed. No servers to patch, no storage to provision, no replication to configure. For teams that want to focus on application logic rather than database operations, this abstraction is valuable.

### 1.2 When DynamoDB Is Not the Right Fit
Understanding DynamoDB's limitations matters as much as knowing its strengths. Proposing DynamoDB for the wrong problem signals inexperience.

#### Complex queries and joins
DynamoDB has no JOIN operation. If your application frequently needs to combine data from multiple entity types based on complex relationships, you will either make multiple round trips (adding latency) or denormalize aggressively (adding complexity and storage cost). Relational databases handle these patterns more naturally.

#### Ad-hoc analytics and exploration
DynamoDB is optimized for known queries, not data exploration. If analysts need to ask questions you did not anticipate, or if you need aggregations across the entire dataset, DynamoDB will be slow and expensive. Export to S3 and query with Athena, or use a purpose-built analytics database.

#### Unknown or evolving access patterns
If you cannot enumerate your access patterns during design, DynamoDB's schema rigidity becomes painful. Adding a new access pattern often requires a new Global Secondary Index (GSI) with its own cost and capacity, or re-architecting the table. Relational databases handle schema evolution more gracefully.

#### Strong consistency as the default
DynamoDB reads are eventually consistent by default. Strongly consistent reads are available but cost twice as much and only work against the primary table, not GSIs. If your application requires strong consistency for most reads, this cost adds up, and the eventual consistency of GSIs may be unacceptable.

#### Small, simple workloads
For a simple application with modest traffic, DynamoDB's learning curve and cost structure may not be justified. A single PostgreSQL instance is simpler to understand, cheaper at low scale, and more flexible for evolving requirements.

### 1.3 Common Interview Systems Using DynamoDB
| System | Why DynamoDB Works |
| --- | --- |
| URL Shortener | Simple key-value lookup, high read volume |
| Shopping Cart | Per-user data, session-like access patterns |
| Gaming Leaderboard | Sorted data within partitions, high write throughput |
| User Sessions | TTL for automatic expiration, low latency |
| IoT Telemetry | High write throughput, time-series with TTL |
| Social Feed | Per-user feeds, append-heavy writes |

**In practice:** When proposing DynamoDB in an interview, connect your choice to specific requirements. For a shopping cart system, mention that per-user partitioning aligns with access patterns and TTL handles cart expiration automatically. 
For a gaming leaderboard, explain that sort keys enable efficient range queries within a partition. The strength of the answer comes from matching DynamoDB's specific capabilities to the problem's specific needs.
# 2. Data Modeling Fundamentals
If you approach DynamoDB with relational database thinking, you will fail. The mental model is fundamentally different. Relational databases are optimized for flexibility: normalize your data, and the query optimizer will figure out how to answer whatever questions you ask. DynamoDB inverts this: decide what questions you will ask, then design your data to answer them efficiently.
This inversion is not a limitation to overcome. It is the architectural choice that enables DynamoDB's performance guarantees. Understanding this model deeply, not just knowing the rules but understanding why they exist, is what demonstrates real expertise in interviews.

### 2.1 Think Access Patterns First
The hardest part of DynamoDB design is not the syntax or the API. It is training yourself to think queries-first rather than data-first.

### 2.2 Primary Key Design
The primary key is the most consequential design decision you will make. It determines how DynamoDB distributes data across partitions, which queries execute efficiently, and whether your system will scale smoothly or hit throttling walls. Get it wrong, and you may need to migrate your entire table to fix it.
DynamoDB offers two primary key types, each with different capabilities:
**Partition Key Only (Simple)**
**Partition Key + Sort Key (Composite)**

### 2.3 Choosing the Right Partition Key
DynamoDB distributes data and throughput across partitions based on the partition key. If one partition key value receives disproportionate traffic, that partition becomes a bottleneck regardless of your total provisioned capacity. This is the infamous "hot partition" problem.
A good partition key has high cardinality (many distinct values) and even access distribution (no single value dominates traffic).
| Partition Key | Cardinality | Distribution | Rating |
| --- | --- | --- | --- |
| user_id | High (millions) | Even | Good |
| status ('active'/'inactive') | Low (2 values) | Uneven | Bad |
| date | Medium | Can spike | Risky |
| device_id + date | High | Even | Good |

**In practice:** When discussing partition key design, explain your reasoning about cardinality and distribution. For a user-facing application, user_id typically works well because users generate roughly similar traffic. 
For an IoT system with a few high-volume devices, device_id alone creates hot partitions; adding a time component (device_id#2024-01) distributes writes across partitions. This kind of reasoning demonstrates that you understand the underlying mechanics, not just the rules.
# 3. Access Patterns and Single-Table Design
Single-table design is DynamoDB's most distinctive and controversial pattern. The idea sounds wrong at first: store users, orders, and products in the same table? But the reasoning becomes clear once you understand DynamoDB's constraints and goals.
The pattern emerges from a simple observation: DynamoDB has no JOIN operation, and network round trips are expensive. If fetching a user's profile and their recent orders requires two separate queries, you pay latency twice. If you can design your data so both come back in a single query, you pay once.

### 3.1 Why Single-Table Design?
The trade-off is between schema clarity and query efficiency. Multi-table design is easier to understand but requires multiple round trips. Single-table design is harder to understand but minimizes latency.

### 3.2 Single-Table Design Pattern
The key insight is that DynamoDB does not care what data your partition contains. It just efficiently retrieves items that share a partition key. By using generic attribute names (PK, SK) and type prefixes, you can store different entity types together and retrieve related data in a single query.
Use generic attribute names (PK, SK) and overload them with prefixes:
**Supported Access Patterns:**

### 3.3 Global Secondary Index (GSI) for Additional Access Patterns
GSIs let you query by different attributes. Think of them as alternative views of your data.
**GSI Design Patterns:**
| Pattern | Use Case | GSI Key Design |
| --- | --- | --- |
| Inverted Index | Query from either direction | Swap PK and SK |
| Sparse Index | Query only items with attribute | Only items with GSI key are indexed |
| GSI Overloading | Multiple entity queries | Use type prefix in GSI PK |

GSIs are powerful but not free. Each GSI replicates data, consuming storage and write capacity. More importantly, GSIs are eventually consistent, meaning reads might return stale data. 
When discussing GSIs in interviews, demonstrate awareness of these trade-offs. Explain that you would add a GSI for an essential access pattern like "find all orders by product," but you would not add GSIs speculatively. The cost compounds, and each GSI adds another dimension to capacity planning.
# 4. Capacity Modes and Throughput Planning
DynamoDB charges based on capacity, either reserved in advance or consumed on demand. Understanding these modes is essential for both cost estimation and architectural decisions. In interviews, demonstrating that you can estimate capacity requirements and choose the appropriate mode shows operational maturity.

### 4.1 Provisioned Capacity Mode
In provisioned mode, you commit to a specific throughput level, measured in Read Capacity Units (RCUs) and Write Capacity Units (WCUs). You pay for this capacity whether you use it or not, but the per-unit cost is lower than on-demand.
**Capacity Unit Definitions:**
**Example Calculation:**
**Auto Scaling:** Provisioned mode supports auto scaling within min/max bounds. Good for predictable traffic patterns with some variation.

### 4.2 On-Demand Capacity Mode
DynamoDB automatically scales to handle any traffic level. You pay per request.
**Pricing:**
- Read: $0.25 per million read request units
- Write: $1.25 per million write request units

**Best For:**
- Unpredictable traffic
- New applications with unknown load
- Spiky workloads (flash sales, viral content)

### 4.3 Choosing Between Modes
| Factor | Provisioned | On-Demand |
| --- | --- | --- |
| Traffic Pattern | Predictable | Unpredictable/Spiky |
| Cost Optimization | Lower for steady load | Higher but simpler |
| Scaling Speed | Auto scaling has lag | Instant |
| Capacity Planning | Required | Not needed |
| Best For | Production with known patterns | Dev/test, new apps, spiky |

# 5. Handling Hot Partitions
Hot partitions are DynamoDB's most common production issue. You provision 10,000 WCUs, monitor shows you are using only 8,000, yet requests are being throttled. The culprit is almost always uneven access distribution: one partition key is receiving more traffic than its share of the total capacity.
Understanding hot partitions, both how to prevent them and how to solve them when they occur, demonstrates the operational depth that interviewers value.

### 5.1 What Causes Hot Partitions?
DynamoDB distributes capacity evenly across partitions. If you have 10,000 WCUs and 10 partitions, each partition gets roughly 1,000 WCUs. If one partition key receives 8,000 writes per second while others receive minimal traffic, that partition will be throttled despite abundant total capacity.

### 5.2 Solutions for Hot Partitions
**Solution 1: Write Sharding**
Add a random suffix to the partition key to spread writes across multiple partitions.
**Trade-off:** Reads must query all shards and aggregate results.
**Solution 2: Caching with DAX**
For read-heavy hot keys, put DAX (in-memory cache) in front of DynamoDB.
**Solution 3: Time-Based Partitioning**
For time-series data, include time in the partition key.

### 5.3 Adaptive Capacity
DynamoDB has built-in **adaptive capacity** that automatically redistributes throughput to hot partitions. However, it is not instant and should not be relied upon as the primary solution.
# 6. DynamoDB Transactions
For years, DynamoDB's lack of transactions was a significant limitation. You could update individual items atomically, but updating multiple items together required application-level coordination. DynamoDB transactions, introduced in 2018, changed this by providing ACID guarantees across multiple items and even multiple tables.
Understanding when transactions are appropriate, and when they are overkill, demonstrates nuanced judgment about consistency trade-offs.

### 6.1 Transaction Operations
DynamoDB transactions come in two forms: TransactWriteItems for atomic writes and TransactGetItems for consistent reads.
**TransactWriteItems** atomically writes up to 100 items. Either all operations succeed, or none do. This is essential for operations where partial completion would leave data in an inconsistent state.
**TransactGetItems:** Atomically read up to 100 items with a consistent snapshot.

### 6.2 Transaction Capacity Cost
Transactions consume **2x the capacity** of non-transactional operations.

### 6.3 Transaction Limitations
| Limitation | Value |
| --- | --- |
| Max items per transaction | 100 |
| Max total size | 4 MB |
| Scope | Single region |
| Supported operations | Put, Update, Delete, ConditionCheck |

### 6.4 When to Use Transactions
**In practice:** Transactions are powerful but expensive. For single-item updates that need consistency guarantees, conditional writes (UpdateItem with ConditionExpression) provide atomicity without the 2x cost. 
Reserve transactions for true multi-item atomicity: balance transfers that must update two accounts together, order placement that must update inventory and create an order record, or any operation where partial completion would corrupt your data model.
# 7. Time-to-Live (TTL)
Many applications store data that should not live forever: user sessions, shopping carts, temporary tokens, IoT readings beyond a retention window. Without automatic expiration, you need background jobs to scan and delete old data, consuming capacity and adding operational complexity.
TTL solves this elegantly. DynamoDB automatically deletes expired items at no extra cost, no write capacity consumed, no cleanup jobs to maintain.

### 7.1 How TTL Works
You designate an attribute as the TTL attribute. DynamoDB continuously scans for items where this attribute (a Unix timestamp) is in the past, and deletes them automatically.

### 7.2 TTL Characteristics
**Deletion timing:** Items are typically deleted within 48 hours of expiration. Not immediate, not guaranteed.
**No capacity consumption:** TTL deletions are free and do not count against your WCUs.
**Streams integration:** TTL deletions can trigger DynamoDB Streams for downstream processing.

### 7.3 TTL Use Cases
| Use Case | TTL Strategy |
| --- | --- |
| User sessions | Set TTL to session timeout (e.g., 24 hours) |
| Shopping carts | Set TTL to cart abandonment window (e.g., 7 days) |
| Temporary tokens | Set TTL to token expiration |
| IoT data retention | Set TTL to retention period (e.g., 90 days) |
| Cache entries | Set TTL to cache duration |

**In practice:** TTL is a design decision, not just a feature. When designing systems with session data, shopping carts, or any expiring content, mention TTL proactively. Explain that it eliminates cleanup job complexity and reduces storage costs automatically. 
Also mention that deletion is not immediate (up to 48 hours), so queries should filter on the TTL attribute to avoid returning logically-expired items that have not been physically deleted yet.
# 8. DAX (DynamoDB Accelerator)
DynamoDB delivers single-digit millisecond latency, which is excellent for most applications. But some use cases need more: real-time gaming, high-frequency trading interfaces, or applications where every millisecond of latency affects user experience or revenue.
DAX is an in-memory cache designed specifically for DynamoDB. It drops read latency from milliseconds to microseconds for cached items, while requiring minimal code changes since it is API-compatible with DynamoDB.

### 8.1 How DAX Works
DAX operates as a cluster between your application and DynamoDB. Your application connects to DAX instead of DynamoDB directly. DAX handles caching transparently: cache hits return immediately, cache misses fetch from DynamoDB and populate the cache.

### 8.2 DAX vs ElastiCache
| Feature | DAX | ElastiCache (Redis) |
| --- | --- | --- |
| Integration | DynamoDB-native | General purpose |
| API changes | Minimal (drop-in) | Requires code changes |
| Caching logic | Automatic | Application-managed |
| Write-through | Supported | Manual implementation |
| Latency | Microseconds | Milliseconds |
| Use case | DynamoDB reads | Flexible caching |

### 8.3 When to Use DAX
**Good fit:**
- Read-heavy workloads with repeated access to same items
- Microsecond latency requirements
- Existing DynamoDB tables needing performance boost

**Poor fit:**
- Write-heavy workloads (cache invalidation overhead)
- Strongly consistent reads required (DAX only supports eventual)
- Complex caching logic needed

**In practice:** DAX makes sense when you have read-heavy access patterns hitting the same items repeatedly. Product catalog pages viewed thousands of times, user profile lookups for popular users, or gaming leaderboards queried constantly are good candidates. 
But DAX only supports eventual consistency, so it is unsuitable for use cases requiring strongly consistent reads. Also note that DAX adds infrastructure cost and complexity, so it should be justified by specific latency requirements rather than added by default.
# 9. DynamoDB vs Other Databases
Interviewers frequently ask why you chose DynamoDB over alternatives. The answer should not be "it is what AWS provides" or "it is what I know." Instead, demonstrate understanding of how different databases make different trade-offs, and why DynamoDB's trade-offs align with your specific requirements.

### 9.1 DynamoDB vs Cassandra
Both are distributed NoSQL databases designed for high availability and horizontal scaling. The fundamental difference is operational model: DynamoDB is fully managed, Cassandra is self-managed (or managed by third parties like DataStax).
| Aspect | DynamoDB | Cassandra |
| --- | --- | --- |
| Management | Fully managed | Self-managed or managed |
| Pricing | Pay per capacity | Infrastructure cost |
| Consistency | Tunable (eventual/strong) | Tunable (more options) |
| Query language | API-based | CQL (SQL-like) |
| Scaling | Automatic | Manual (add nodes) |
| Multi-DC | Global Tables (managed) | Native (flexible) |
| Best for | AWS-native, operational simplicity | Multi-cloud, fine control |

**Choose DynamoDB:** When you want operational simplicity and are on AWS.
**Choose Cassandra:** When you need multi-cloud, on-premise, or fine-grained tuning.

### 9.2 DynamoDB vs MongoDB
| Aspect | DynamoDB | MongoDB |
| --- | --- | --- |
| Data model | Key-value, document | Document (flexible) |
| Query capability | Limited (PK + SK + filters) | Rich (aggregations, joins) |
| Schema | Rigid around keys | Flexible |
| Scaling | Automatic partitioning | Sharding (manual config) |
| Transactions | Multi-item (limited) | Multi-document (rich) |
| Best for | Known access patterns | Flexible queries, prototyping |

**Choose DynamoDB:** When you have well-defined access patterns and need auto-scaling.
**Choose MongoDB:** When you need flexible querying or are still discovering access patterns.

### 9.3 DynamoDB vs PostgreSQL
| Aspect | DynamoDB | PostgreSQL |
| --- | --- | --- |
| Type | NoSQL | Relational |
| Queries | Key-based | Full SQL |
| Joins | Not supported | Native |
| Scale | Horizontal (automatic) | Vertical (manual sharding) |
| Schema | Flexible | Strict |
| Consistency | Eventual (default) | Strong (ACID) |
| Best for | High scale, simple queries | Complex queries, transactions |

**Choose DynamoDB:** When scale and simplicity trump query flexibility.
**Choose PostgreSQL:** When you need complex queries, joins, or strong consistency.
# Summary
DynamoDB excels when you have well-defined access patterns, need predictable low-latency at any scale, and value operational simplicity over query flexibility. The depth of understanding you demonstrate about DynamoDB's architecture and trade-offs signals to interviewers that you can make sound database decisions under real-world constraints.

#### Design around access patterns
This is not optional guidance; it is the fundamental DynamoDB principle. List your access patterns before designing your schema. Each pattern should map to an efficient operation: a GetItem, a Query with a specific partition key and sort key range, or a carefully designed GSI. If you cannot express your access patterns this way, DynamoDB may not be the right choice.

#### Partition key choice determines scalability
High cardinality and even access distribution are essential. A poor partition key creates hot partitions that throttle your application regardless of provisioned capacity. When discussing designs, explain why your partition key distributes load evenly and what you would do if a hot partition emerged.

#### GSIs extend access patterns at a cost
Each GSI replicates data, consumes additional write capacity, and provides only eventual consistency. Add them for essential access patterns that the base table cannot support, not speculatively. Explain the trade-off when proposing a GSI.

#### Capacity modes reflect operational maturity
Provisioned mode with auto-scaling suits predictable workloads and offers lower per-unit costs. On-demand mode suits unpredictable or spiky workloads and eliminates capacity planning. Demonstrate that you can estimate capacity requirements and choose the appropriate mode.

#### Transactions enable multi-item atomicity
Use them for operations where partial completion would corrupt data: balance transfers, inventory-and-order updates, or any multi-entity consistency requirement. Use conditional writes for single-item atomicity at lower cost.

#### TTL eliminates cleanup complexity
For session data, shopping carts, tokens, or any expiring content, TTL handles expiration automatically without consuming write capacity or requiring cleanup jobs.

#### DAX addresses specific latency requirements
When milliseconds matter and you have read-heavy, repeat-access patterns, DAX drops latency to microseconds. But it only supports eventual consistency and adds infrastructure complexity.
When you propose DynamoDB in an interview, the strength of your answer lies not in claiming DynamoDB is always the best choice, but in articulating exactly why it fits this particular problem, what trade-offs you are accepting, and how you would operate it as requirements evolve.
# References
- [Amazon DynamoDB Developer Guide](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/) - Official AWS documentation covering all DynamoDB features
- [DynamoDB Book by Alex DeBrie](https://www.dynamodbbook.com/) - Comprehensive guide to DynamoDB data modeling
- [AWS re:Invent 2023: Advanced DynamoDB Design Patterns](https://www.youtube.com/watch?v=6yqfmXiZTlM) - Deep dive into single-table design and access patterns
- [Amazon DynamoDB Paper (2022)](https://www.usenix.org/conference/atc22/presentation/elhemali) - Technical paper on DynamoDB internals
- [Choosing the Right DynamoDB Partition Key](https://aws.amazon.com/blogs/database/choosing-the-right-dynamodb-partition-key/) - AWS best practices for partition key design

# Quiz

## DynamoDB Quiz
What is the primary architectural reason DynamoDB can scale throughput horizontally?