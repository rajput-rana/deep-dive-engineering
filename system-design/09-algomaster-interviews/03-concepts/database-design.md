# Database Design for System Design Interviews

In every system design interview, you'll face the question: "How would you store this data?"
How you answer reveals a lot. The database layer is where many promising architectures fall apart. You can have perfectly designed APIs, elegant microservices, and beautifully orchestrated containers, but if your database can't keep up with your workload, none of that matters.
The database is often the hardest component to change later and the most expensive to get wrong.
> The database is often the bottleneck. Design it wrong, and no amount of application-layer optimization will save you.

Database design in interviews isn't about memorizing SQL syntax or reciting the differences between PostgreSQL and MySQL. 
It's about understanding trade-offs: consistency vs availability, read performance vs write performance, simplicity vs scalability. Every choice has consequences, and interviewers want to see that you understand what those consequences are.
In this chapter, we'll cover everything you need to know: SQL vs NoSQL, schema design, normalization, indexing, partitioning, sharding, replication, consistency models, transactions, query optimization, and real-world examples that tie everything together.
# 1. SQL vs NoSQL
The first decision you'll face is whether to use a relational database or something else. This choice ripples through your entire architecture, so it's worth understanding what you're trading off.

### Relational Databases (SQL)
Relational databases store data in tables with rows and columns. Relationships between entities are defined through foreign keys, and the database enforces these relationships for you.
PostgreSQL, MySQL, and Oracle are the most common examples.
The strength of relational databases lies in their guarantees. ACID transactions mean you can update multiple tables atomically. Foreign keys prevent orphaned records. Constraints enforce business rules at the data layer. When you need to run ad-hoc queries across your data, SQL gives you the expressive power to do so.
The weakness is scaling. Relational databases traditionally scale vertically, meaning you buy bigger servers. Horizontal scaling (spreading data across multiple machines) is possible but adds complexity. Schema changes on large tables can be painful, sometimes requiring hours of downtime or careful migration strategies.

### Non-Relational Databases (NoSQL)
NoSQL is an umbrella term for databases that don't use the relational model. Different types are optimized for different access patterns.
**Document Stores (MongoDB, DynamoDB)** store data as JSON-like documents. Related data can be embedded together, which makes reads fast when you fetch an entire entity at once.
**Key-Value Stores (Redis, DynamoDB)** are the simplest model: a key maps to a value. Extremely fast for lookups when you know the key, but limited in query capability.
**Wide-Column Stores (Cassandra, HBase)** organize data into rows with dynamic columns. They're designed for high write throughput and work well for time-series data.
**Graph Databases (Neo4j, Amazon Neptune)** model data as nodes and edges. They excel at traversing relationships, which makes them ideal for social networks and recommendation engines.
The strength of NoSQL databases is **horizontal scaling**. They're designed from the ground up to distribute data across many machines. Schema flexibility means you can evolve your data model without migrations.
The weakness is the loss of relational guarantees. Transactions typically work within a single document or partition. Complex queries that would be a simple JOIN in SQL become application-level logic. Eventual consistency means you might read stale data.

### Decision Framework
The choice isn't about which technology is "better." It's about which trade-offs align with your requirements.
| Factor | Choose SQL | Choose NoSQL |
| --- | --- | --- |
| Data structure | Well-defined, relational | Flexible, evolving |
| Consistency | Critical (banking, inventory) | Eventual is acceptable |
| Query patterns | Complex, ad-hoc queries | Simple, known patterns |
| Scale | Moderate (single server OK) | Massive (distributed) |
| Transactions | Multi-row transactions needed | Single-document operations |

In practice, most large systems use both. Different parts of the system have different requirements, and you pick the right tool for each job.

#### Common pairings in real systems:
- User profiles: PostgreSQL (relational, ACID)
- Session data: Redis (fast key-value)
- Activity feeds: Cassandra (high write throughput)
- Product catalog: MongoDB (flexible schema)
- Social connections: Neo4j (graph relationships)

# 2. Schema Design Principles
Once you've chosen a database, you need to structure your data within it. Good schema design makes queries fast, keeps data consistent, and makes future changes manageable.

### Start with Entities and Relationships
Before writing any SQL, sketch out the core entities in your system and how they relate to each other. This is the foundation everything else builds on.
A user places many orders (one-to-many). Each order contains many order items (one-to-many). Each product can appear in many order items (one-to-many). Getting these relationships right is critical because they determine how you'll join tables and what indexes you'll need.

### Define Primary Keys
Every table needs a unique identifier. The choice of ID type matters more than people realize, especially at scale.
**Auto-increment IDs** are simple and compact:
They work well for single-server setups, but become problematic in distributed systems. If you have multiple database nodes, they'll generate conflicting IDs unless you coordinate, which adds latency and complexity.
**UUIDs** solve the coordination problem:
Any node can generate a UUID without coordination, and collisions are statistically impossible. The downsides are size (16 bytes vs 4 bytes) and randomness. Random IDs scatter writes across the B-tree index, which hurts write performance and cache efficiency.
**ULIDs and Snowflake IDs** offer the best of both worlds:
These are time-ordered and globally unique. The time component means sequential inserts land near each other in the index. The uniqueness component prevents collisions across nodes. For new systems at scale, this is usually the right choice.

### Define Relationships with Foreign Keys
Foreign keys enforce referential integrity at the database level:
With this constraint in place, the database prevents you from creating an order for a non-existent user. It also prevents you from deleting a user who has orders (unless you specify cascade behavior). These constraints catch bugs that would otherwise corrupt your data.

### Choose Appropriate Data Types
Use the smallest type that fits your data. Smaller types mean more rows fit in memory, better cache utilization, and faster queries.
| Data | Type | Why |
| --- | --- | --- |
| Age | SMALLINT | 0-32767 range, 2 bytes |
| Price | DECIMAL(10,2) | Exact precision for money |
| Email | VARCHAR(255) | Variable length, reasonable max |
| UUID | UUID | Native type, 16 bytes |
| JSON data | JSONB | Indexed JSON in PostgreSQL |
| Timestamps | TIMESTAMPTZ | Always include timezone |
| Booleans | BOOLEAN | Not TINYINT or CHAR(1) |

For money, always use DECIMAL, never floating point. Floating point arithmetic introduces rounding errors that accumulate over time. A customer who sees $99.99999999 on their receipt will not be happy.

### Add Constraints
Constraints enforce business rules at the data layer, which is more reliable than enforcing them only in application code:
The `NOT NULL` prevents missing data. The `UNIQUE` prevents duplicate emails. The `CHECK` constraints prevent invalid values. If application code has a bug, the database catches it before bad data gets persisted.
# 3. Normalization and Denormalization
Normalization and denormalization represent opposite approaches to organizing data. Understanding when to use each is one of the most important database design skills.

### Normalization
Normalization eliminates data redundancy by splitting data into multiple related tables, where each fact is stored exactly once.
Consider an unnormalized orders table:
| order_id | user_name | user_email | product_name | price |
| --- | --- | --- | --- | --- |
| 1 | Alice | alice@example.com | Laptop | 999 |
| 2 | Alice | alice@example.com | Mouse | 49 |
| 3 | Bob | bob@example.com | Laptop | 999 |

This structure has problems. Alice's email is stored multiple times. If she changes her email, you need to update every row where she appears. The laptop price is duplicated. If the price changes, some orders might show the old price and others the new one. This is how data inconsistencies creep in.
**Normalized design:**
Now each fact is stored in exactly one place. If Alice changes her email, you update one row in the users table. The change is immediately reflected everywhere.
The formal normal forms (1NF, 2NF, 3NF, BCNF) have precise definitions, but the practical goal is simple: eliminate redundancy so that updates only need to touch one place.

### Denormalization
Denormalization intentionally adds redundancy to improve read performance. It's not laziness or ignorance of normalization, it's a deliberate trade-off.
Consider the query to get a user's order history with product details:
This requires joining three tables. At scale, with millions of orders, these JOINs become expensive. If this query runs thousands of times per second on your hot path, you have a problem.
**Denormalized solution:** Store the product name and price directly in the orders table:
Now the query is a simple single-table scan:
No JOINs, no cross-table lookups. The query is faster and puts less load on the database.
The cost is complexity. When a product name changes, you might need to update it in multiple places (or accept that old orders show the old name, which is sometimes actually desirable for order history). Your write path becomes more complex because you're maintaining redundant copies.

### Trade-offs
| Aspect | Normalized | Denormalized |
| --- | --- | --- |
| Storage | Less (no redundancy) | More (duplicated data) |
| Write complexity | Simple (one place) | Complex (multiple places) |
| Read complexity | JOINs required | Simple queries |
| Consistency | Easy to maintain | Risk of inconsistency |
| Best for | OLTP, write-heavy | OLAP, read-heavy |

#### When to denormalize:
- Read-heavy workloads (100:1 read/write ratio)
- Frequent expensive JOINs
- Known, stable query patterns
- Acceptable staleness

#### When to stay normalized:
- Write-heavy workloads
- Data consistency is critical
- Ad-hoc queries needed
- Schema still evolving

In practice, most systems use a mix. Core transactional data stays normalized. Read-heavy views and caches use denormalized structures. The key is being intentional about where you denormalize and understanding the maintenance burden it creates.
# 4. Indexing Strategies
Indexes are the single most important tool for query performance. A missing index can make a query 1000x slower. Understanding how indexes work and when to use them is essential.

### How Indexes Work
Without an index, the database must scan every row to find matches. This is called a full table scan.
An index is a separate data structure that maps column values to row locations. The most common type is the B-tree, which keeps values sorted and allows efficient lookups, range scans, and ordered retrieval.
The tree structure means you only need to examine log(n) nodes to find any value. For a million rows, that's about 20 comparisons instead of a million.

### Creating Indexes
Partial indexes are particularly useful when you frequently query a specific subset. An index on pending orders is much smaller than an index on all orders, which makes it faster to scan and update.

### Index Types
Different index types are optimized for different query patterns:
| Type | Use Case | Example |
| --- | --- | --- |
| B-Tree | Equality, range, sorting | WHERE age > 25 ORDER BY age |
| Hash | Equality only (rare) | WHERE id = 123 |
| GiST | Geometric, full-text | PostGIS spatial queries |
| GIN | Arrays, JSONB, full-text | WHERE tags @> '{sql}' |
| BRIN | Large sequential data | Time-series with timestamp ordering |

B-tree is the default and handles most cases. GIN is essential for JSONB columns and array searches. BRIN is useful for append-only data where values are naturally clustered (like timestamps in a log table).

### Composite Index Order Matters
For a composite index `(a, b, c)`, the index can help with queries that filter on:
- `WHERE a = 1`
- `WHERE a = 1 AND b = 2`
- `WHERE a = 1 AND b = 2 AND c = 3`

But it cannot help with:
- `WHERE b = 2` (leftmost column missing)
- `WHERE a = 1 AND c = 3` (gap in columns)

Think of it like a phone book sorted by last name, then first name. You can efficiently find everyone named "Smith", or everyone named "John Smith", but you can't efficiently find everyone named "John" without scanning the entire book.
**Rule of thumb:** Put equality columns before range columns. Put high-selectivity columns (many distinct values) before low-selectivity columns.

### Covering Indexes
When an index contains all columns needed by a query, the database can answer the query entirely from the index without touching the table. This is called a covering index or index-only scan.
The query never reads the main table, only the index. This can be significantly faster, especially for wide tables with many columns.

### Index Costs
Indexes are not free. Every index you add has costs:
- **Storage:** Each index consumes disk space, often 10-30% of the table size
- **Write overhead:** Every INSERT, UPDATE, or DELETE must update all relevant indexes
- **Maintenance:** Indexes can become fragmented and need periodic rebuilding

Don't index everything. Be strategic:
- Index columns that appear in WHERE, JOIN, and ORDER BY clauses
- Don't index low-selectivity columns (like boolean flags with 50/50 distribution)
- Remove indexes that aren't being used
- Use `EXPLAIN ANALYZE` to verify your indexes are actually being used

# 5. Partitioning and Sharding
When a single database server can't handle your data volume or query load, you need to split the data. Partitioning and sharding are two approaches to this problem, and understanding the difference matters.

### Partitioning (Single Database)
Partitioning divides a large table into smaller pieces that still live on the same server. The database manages the partitions transparently, so queries automatically target the right partition.
**Range Partitioning** divides data by ranges of a column value, typically time:
Queries that filter on `created_at` only scan the relevant partition. A query for 2024 data never touches the 2023 partition. This is called partition pruning.
**List Partitioning** divides data by discrete values:
**Hash Partitioning** distributes data evenly using a hash function:
Hash partitioning is useful when you don't have natural ranges but want even distribution.

### Sharding (Multiple Databases)
Sharding distributes data across multiple database servers. Unlike partitioning, each shard is a separate database instance with its own compute and storage.
Sharding gives you horizontal scalability. Each shard handles a fraction of the total load, and you can add more shards as you grow. But it comes with significant complexity: cross-shard queries, distributed transactions, and rebalancing challenges.

### Sharding Strategies
**Range-Based Sharding** assigns ranges of the shard key to each shard:
Range queries on the shard key can target a single shard. The downside is that ranges can become unbalanced. If recent users are more active, the newest shard gets more traffic.
**Hash-Based Sharding** uses a hash function to distribute data evenly:
This guarantees even distribution regardless of the key values. The downside is that range queries must hit all shards because related keys are scattered.
**Directory-Based Sharding** maintains a lookup table that maps keys to shards:
This gives maximum flexibility. You can move data between shards without changing the hash function. The downside is that the lookup table becomes a bottleneck and a single point of failure.

### Choosing a Shard Key
The shard key is the most important decision in a sharded architecture. A bad choice can leave you with hot shards, cross-shard queries everywhere, and no good options for fixing it.
**Good shard keys have:**
- High cardinality (many unique values)
- Even distribution across values
- Presence in most queries (so queries target one shard)

**Bad shard keys:**
- Low cardinality (few values, like country code)
- Time-based (recent data becomes a hot shard)
- Frequently changing values

| Use Case | Good Shard Key | Bad Shard Key |
| --- | --- | --- |
| Multi-tenant SaaS | tenant_id | created_at |
| Social network | user_id | country |
| E-commerce | user_id or order_id | status |

### Cross-Shard Queries
Sharding creates a fundamental problem: queries that don't filter on the shard key must hit every shard.
This scatter-gather pattern is expensive. Every query fans out to N shards, waits for all responses, and merges results.
**Solutions:**
- **Denormalize** to avoid cross-shard queries. Store product data in the order record.
- **Scatter-gather** when you must, but limit how often. Use for analytics, not hot paths.
- **Secondary indexes** in a search system like Elasticsearch that has a full view of the data.

# 6. Replication Patterns
Replication copies data across multiple servers. This serves two purposes: scaling reads by distributing them across replicas, and providing fault tolerance by having copies of data survive node failures.

### Single-Leader Replication
The most common pattern. One primary (leader) handles all writes. Replicas (followers) receive a stream of changes and serve reads.
The key question is when the primary acknowledges a write: before or after replicas confirm receipt.
**Synchronous replication** waits for at least one replica to confirm before acknowledging the write to the client. This guarantees no data loss if the primary crashes, but makes writes slower and ties availability to replica health.
**Asynchronous replication** acknowledges the write immediately and replicates in the background. Writes are fast, but if the primary crashes before replicating, those writes are lost. Replicas may also lag behind, serving stale data.
Most production systems use semi-synchronous: one replica is synchronous (for durability), others are asynchronous (for performance).

### Multi-Leader Replication
Multiple nodes can accept writes. This is primarily used for geo-distributed systems where you want writes to be fast for users in different regions.
The complexity comes from conflicts. If two leaders modify the same record simultaneously, you need a conflict resolution strategy:
- **Last-write-wins (LWW):** Use timestamps to pick a winner. Simple but can lose data.
- **Merge changes:** Use conflict-free replicated data types (CRDTs) that can automatically merge concurrent updates.
- **Application-level resolution:** Present conflicts to the application or user to resolve.

Multi-leader is powerful but complex. Use it when you need low-latency writes in multiple regions, not as a general scaling strategy.

### Leaderless Replication
Any node can accept reads and writes. Cassandra and DynamoDB use this approach.
The client writes to multiple nodes and reads from multiple nodes. The magic is in the quorum: if you write to W nodes and read from R nodes, and W + R > N (total nodes), you're guaranteed to read at least one node that has the latest write.
This provides high availability. As long as enough nodes are up to form a quorum, the system keeps working. But it means you might read stale data if you don't reach a node with the latest write.

### Choosing a Pattern
| Pattern | Use Case | Trade-off |
| --- | --- | --- |
| Single-leader | Most applications | Simple, strong consistency, limited write scale |
| Multi-leader | Geo-distributed systems | Low latency worldwide, complex conflict resolution |
| Leaderless | High availability systems | Survives failures, eventually consistent |

For most applications, single-leader replication is the right choice. It's simpler to reason about and provides strong consistency. Only move to more complex patterns when you have specific requirements that demand them.
# 7. Consistency Models
Consistency determines what data clients see and when. In a single-server database, this is simple: you always see the latest write. In distributed systems, it gets complicated because data exists on multiple nodes, and those nodes can disagree.

### The Consistency Spectrum

### Strong Consistency
Every read returns the most recent write. It behaves as if there's only one copy of the data, even though there might be many.
Strong consistency is implemented through synchronous replication or consensus protocols like Paxos and Raft. The write isn't acknowledged until all (or a majority of) replicas have confirmed it.
The trade-off is performance and availability. Writes are slower because they wait for replicas. If the leader or enough replicas are down, the system can't accept writes (and sometimes reads). But you never see stale data.

### Eventual Consistency
Reads may return stale data, but if you stop writing and wait long enough, all replicas will converge to the same value.
This is what you get with asynchronous replication. The primary acknowledges the write immediately and replicates in the background. Replicas may lag by seconds or minutes.
The trade-off is predictability. You get lower latency and higher availability, but you can't guarantee what a read will return. For many applications, this is fine. A social media feed that's a few seconds behind is acceptable. A bank balance that's wrong is not.

### Read-Your-Writes Consistency
Users always see their own writes, even if other users see stale data.
This is weaker than strong consistency but much more intuitive for users. If I add an item to my cart, I should see it when I view my cart, even if the replica I'm reading from hasn't caught up yet.
Implementation typically involves routing a user's reads to the same node that handled their writes, or tracking write timestamps and waiting for replicas to catch up.

### Causal Consistency
If operation A happened before operation B (causally), everyone sees A before B. Concurrent operations (neither caused the other) can be seen in any order.
This preserves the logical order that makes sense to humans. You never see a reply before the message it's replying to. But concurrent, unrelated operations might appear in different orders to different users.

### Choosing Consistency Level
The right consistency level depends on what you're building:
| Use Case | Consistency | Why |
| --- | --- | --- |
| Bank accounts | Strong | Can't show wrong balance |
| Social feed | Eventual | Slight delay acceptable |
| Shopping cart | Read-your-writes | See your own items |
| Comments/Replies | Causal | Replies must appear after posts |
| Analytics dashboards | Eventual | Approximate is fine |

Many databases let you choose consistency per-query, giving you flexibility to use strong consistency where it matters and eventual consistency where performance matters more:
# 8. Transactions and ACID
Transactions group multiple operations into a single logical unit. Either all operations succeed, or none do. This is essential for maintaining data integrity when multiple operations must happen together.

### ACID Properties
ACID is an acronym for the four guarantees that database transactions provide:
**Atomicity:** All operations in the transaction succeed, or all fail. There are no partial updates.
If the second update fails (maybe the target account doesn't exist), the first update is rolled back. Money doesn't disappear.
**Consistency:** The database moves from one valid state to another. All constraints are maintained.
**Isolation:** Concurrent transactions don't interfere with each other. Each transaction sees a consistent view of the data as if it were running alone.
**Durability:** Once a transaction commits, the data survives system crashes. The database writes to durable storage before acknowledging the commit.

### Isolation Levels
Full isolation (serializability) is expensive. Databases offer weaker isolation levels that trade correctness for performance:
| Level | Dirty Read | Non-Repeatable Read | Phantom Read |
| --- | --- | --- | --- |
| Read Uncommitted | Yes | Yes | Yes |
| Read Committed | No | Yes | Yes |
| Repeatable Read | No | No | Yes |
| Serializable | No | No | No |

**Dirty Read:** Seeing uncommitted changes from other transactions. If that transaction rolls back, you read data that never existed.
**Non-Repeatable Read:** Reading the same row twice in a transaction returns different values because another transaction modified it between reads.
**Phantom Read:** Running the same query twice returns different sets of rows because another transaction inserted or deleted rows.
Most applications use Read Committed (PostgreSQL default) or Repeatable Read (MySQL InnoDB default). Serializable is rarely used because of performance overhead, but it's the only level that guarantees complete correctness.

### Distributed Transactions
When transactions span multiple databases or services, you need coordination protocols.
**Two-Phase Commit (2PC)** coordinates commits across multiple participants:
2PC guarantees atomicity across participants, but it has problems. It's slow (multiple round trips), blocking (participants hold locks while waiting), and the coordinator is a single point of failure.
**Saga Pattern** takes a different approach. Instead of a distributed transaction, you run a series of local transactions, each with a compensating action:
Sagas are more complex to implement because you have to define compensating actions for each step, and handle the case where compensations themselves fail. But they scale better and don't require distributed locking.
# 9. Query Optimization
Slow queries are the most common database problem you'll encounter. A single slow query can bring down an entire application when it runs thousands of times per second. 
Here's how to identify and fix them.

### Use EXPLAIN ANALYZE
Before optimizing, you need to understand what the database is actually doing. `EXPLAIN ANALYZE` shows the query execution plan with actual timing:
This output tells a story. "Seq Scan" means the database is reading every row in the table. "Rows Removed by Filter: 99900" means it read 100,000 rows to find 100 matching ones. That's a 99.9% waste of effort.

#### Red flags to watch for:
- `Seq Scan` on large tables (usually means missing index)
- `Rows Removed by Filter` is high relative to rows returned
- `Nested Loop` with large tables on the inner side
- High `actual time` values

### Common Optimizations
**Add missing indexes** (the most common fix):
A 90x improvement from adding one index is common. This is usually the first thing to check.
**Avoid SELECT *** when you don't need all columns:
This matters especially when tables have large columns (TEXT, JSONB) that you don't need. Less data transferred means faster queries.
**Use LIMIT for pagination:**
**Avoid N+1 queries:**
The N+1 pattern is insidious because each individual query is fast, but the cumulative latency adds up. With 100 users and 10ms per query, you're spending a full second just on round trips.
**Use connection pooling:**
Database connections are expensive to establish. A connection pool maintains a set of open connections that can be reused across requests.

### Caching Strategies
For read-heavy workloads, caching can dramatically reduce database load:
**Read-through cache** checks the cache first, falls back to the database on miss:
**Write-through cache** updates the cache whenever you update the database:
The key consideration with caching is invalidation. When data changes, cached copies become stale. TTL-based expiration is simple but can serve stale data. Active invalidation is more complex but keeps caches fresh.
# 10. Design Examples
Let's see how these concepts come together in real interview scenarios. These examples demonstrate the kind of database design thinking interviewers want to see.

### Example 1: Twitter(X)-like Social Network

#### Requirements:
- Users post tweets
- Users follow other users
- Home timeline shows tweets from followed users
- High read volume (100:1 read/write)

#### Schema Design:
The interesting question is how to build the home timeline. This is where database design intersects with system design.
**Pull model (fan-out on read):** Query tweets from all followed users at read time.
This is simple and writes are fast, but reads become slow if you follow many users. The JOIN can be expensive.
**Push model (fan-out on write):** Pre-compute timelines. When a user posts, write to all followers' timelines.
Reads are now fast (just read one user's timeline), but writes are slow. If a celebrity with 10 million followers posts, you're writing 10 million rows.
**Recommendation:** Use a hybrid approach. Push for normal users, pull for celebrities. The exact threshold depends on your infrastructure.

### Example 2: E-commerce Order System

#### Requirements:
- Users browse products and place orders
- Accurate inventory tracking (no overselling)
- Complete order history

#### Schema Design:
Note the denormalization in `order_items`. We store the product name and price at the time of the order, not just a foreign key. This is intentional: if the product price changes later, the order history should still show what the customer actually paid.
**Inventory Handling:**
The tricky part is preventing overselling. Use an atomic update with a condition:
This works because the UPDATE is atomic. Even with concurrent requests, the database ensures only one succeeds in taking the last item.
**Sharding Strategy:** Shard orders by `user_id` so all of a user's orders are co-located. This makes "show my order history" queries fast.

### Example 3: Analytics/Time-Series Data

#### Requirements:
- Store billions of events
- Query by time ranges
- Aggregate metrics (count, sum, avg) for dashboards

#### Schema Design:
Time-based partitioning is essential here. Queries for "events in January" only scan the January partition. Old data can be archived or dropped by simply removing old partitions.

#### Pre-aggregation for dashboards:
Real-time aggregation over billions of rows is expensive. Pre-compute common aggregations:
Dashboard queries now hit the small aggregated table instead of scanning billions of raw events.
**Technology consideration:** For heavy time-series workloads, consider specialized databases like TimescaleDB or InfluxDB. They offer better compression, automatic partitioning, and optimized time-based queries.
# 11. Interview Tips
In interviews, database design questions reveal how you think about data, scale, and trade-offs. Here's what interviewers are looking for and how to approach common questions.

### What Interviewers Look For

#### Understand requirements before designing
Ask about read/write ratio, data volume, consistency needs, and query patterns. The right design for a read-heavy system is different from a write-heavy one.

#### Justify your choices
Don't just say "use PostgreSQL." Explain why it fits: you need ACID transactions, complex queries, and the data is relational. Show your reasoning.

#### Consider scale
What happens at 10x, 100x current load? A design that works at 1,000 QPS might fall apart at 100,000 QPS. Show awareness of scaling limits.

#### Know trade-offs
Every decision has pros and cons. Denormalization speeds reads but complicates writes. Sharding scales writes but complicates queries. Interviewers want to see that you understand both sides.

#### Think about failure
What if a node goes down? A data center fails? Network partitions occur? Resilience is part of database design.
# Quick Reference
Here's a condensed reference for the concepts covered in this chapter.

### Database Types
| Type | Examples | Best For |
| --- | --- | --- |
| SQL | PostgreSQL, MySQL | Structured data, ACID, complex queries |
| Document | MongoDB, DynamoDB | Flexible schema, JSON, horizontal scale |
| Key-Value | Redis, Memcached | Caching, sessions, simple lookups |
| Wide-Column | Cassandra, HBase | Time-series, high write throughput |
| Graph | Neo4j, Neptune | Relationships, social networks |

### Schema Checklist
- Primary key defined (UUID or Snowflake for distributed)
- Foreign keys for relationships
- Appropriate data types (smallest that fits)
- NOT NULL where required
- Indexes on WHERE, JOIN, ORDER BY columns
- Constraints for data integrity

### Scaling Patterns
| Direction | Techniques |
| --- | --- |
| Read scaling | Read replicas, caching (Redis), denormalization, CDN |
| Write scaling | Sharding, async processing (queues), batching |
| Both | Partitioning, connection pooling |

### Consistency Levels
| Level | Guarantees | Use Case |
| --- | --- | --- |
| Strong | Always latest write | Banking, inventory |
| Eventual | May see stale data | Social feeds, analytics |
| Read-your-writes | See own writes | Shopping cart, drafts |
| Causal | Preserve cause-effect | Comments, replies |

# References
- [Designing Data-Intensive Applications](https://dataintensive.net/) by Martin Kleppmann - Essential book for database internals
- [PostgreSQL Documentation](https://www.postgresql.org/docs/) - Comprehensive SQL reference
- [Use The Index, Luke](https://use-the-index-luke.com/) - Deep dive into database indexing
- [AWS Database Blog](https://aws.amazon.com/blogs/database/) - Real-world database architecture patterns
- [MongoDB Schema Design Patterns](https://www.mongodb.com/blog/post/building-with-patterns-a-summary) - NoSQL schema patterns

# Quiz

## Database Design Quiz
Which situation most strongly suggests choosing a relational database as the primary store?