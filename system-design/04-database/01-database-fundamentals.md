# Database Fundamentals

A comprehensive guide to database concepts, techniques, and best practices for system design.

## Table of Contents

1. [ACID Transactions](#1-acid-transactions)
2. [SQL vs NoSQL](#2-sql-vs-nosql)
3. [Indexing](#3-indexing)
4. [Sharding](#4-sharding)
5. [Vertical Partitioning](#5-vertical-partitioning)
6. [Sharding vs Partitioning](#6-sharding-vs-partitioning)
7. [Replication](#7-replication)
8. [Connection Pooling](#8-connection-pooling)
9. [Denormalization](#9-denormalization)
10. [Data Compression](#10-data-compression)

---

## 1. ACID Transactions

### Summary

ACID is an acronym for four key properties that define a database transaction: **Atomicity, Consistency, Isolation, and Durability**. These properties ensure reliable and consistent database operations, especially critical for financial systems, e-commerce, and any application requiring data integrity.

### What is a Database Transaction?

A transaction is a sequence of one or more operations (inserts, updates, deletes) that the database treats as **one single action**. It either fully succeeds or fully fails, with no in-between states.

**Example: Bank Transfer**
```
Transaction:
1. Deduct $100 from Account A
2. Add $100 to Account B

Either both succeed or both fail.
```

### The Four ACID Properties

#### Atomicity

**Definition:** A transaction executes as a single, indivisible unit. It either fully succeeds (commits) or fully fails (rolls back).

**Key Point:** If any part fails, the entire transaction is rolled back.

**Example:**
```
BEGIN TRANSACTION
  UPDATE accounts SET balance = balance - 100 WHERE id = 'A'
  UPDATE accounts SET balance = balance + 100 WHERE id = 'B'
COMMIT

If second UPDATE fails → Both changes rolled back
```

**Implementation:**
- **Transaction Logs (WAL):** Every operation recorded before applying
- **Commit/Rollback:** Changes only permanent after COMMIT

**Diagram:**
```
Transaction Start
     │
     ├──► Operation 1 (Recorded in log)
     ├──► Operation 2 (Recorded in log)
     ├──► Operation 3 (Recorded in log)
     │
     ├──► All succeed? ──Yes──► COMMIT ──► Changes permanent
     │                          │
     └──► No ───────────────────┴──► ROLLBACK ──► Changes undone
```

#### Consistency

**Definition:** A transaction brings the database from one valid state to another valid state. All integrity constraints are satisfied.

**Constraints:**
- Primary key constraints (no duplicates)
- Foreign key constraints (related records exist)
- Check constraints (age can't be negative)
- Business rules (stock can't go negative)

**Example:**
```
Constraint: stock_quantity >= 0

Transaction: Order 10 items when stock = 8
→ Would result in stock = -2
→ Violates constraint
→ Transaction ROLLBACK
```

**Implementation:**
- Database schema constraints
- Triggers and stored procedures
- Application-level validation

#### Isolation

**Definition:** Concurrent transactions don't interfere with each other. Each transaction sees a consistent view of data.

**Isolation Levels:**

1. **Read Uncommitted**
   - Allows dirty reads
   - Lowest isolation, rarely used

2. **Read Committed**
   - Prevents dirty reads
   - Allows non-repeatable reads
   - Most common default

3. **Repeatable Read**
   - Prevents dirty reads and non-repeatable reads
   - May allow phantom reads

4. **Serializable**
   - Highest isolation
   - Prevents all anomalies
   - Most expensive

**Concurrency Anomalies:**

**Dirty Read:**
```
Transaction A reads data modified by Transaction B (not committed)
If B rolls back → A has invalid data
```

**Non-Repeatable Read:**
```
Transaction A reads row → Transaction B updates it → A reads again → Different value
```

**Phantom Read:**
```
Transaction A queries → Transaction B inserts matching row → A queries again → New row appears
```

**Implementation:**
- **Locking:** Pessimistic concurrency control
- **MVCC:** Multi-version concurrency control (optimistic)
- **Snapshot Isolation:** Point-in-time view

#### Durability

**Definition:** Once a transaction commits, changes persist even after crashes, power failures, or system restarts.

**Implementation:**
- **Write-Ahead Logging (WAL):** Changes logged before applying
- **Replication:** Data copied to multiple locations
- **Backups:** Regular full/incremental backups

**Diagram:**
```
Transaction Commit
     │
     ├──► Write to WAL (durable storage)
     ├──► Mark as committed
     ├──► Apply to data files
     │
     └──► If crash → Use WAL to recover
```

### Why ACID Matters

**Data Integrity:** Ensures database never in invalid state.

**Reliability:** Critical operations complete or fully rollback.

**Consistency:** All constraints always satisfied.

**Durability:** Committed data never lost.

---

## 2. SQL vs NoSQL

### Summary

SQL (relational) and NoSQL (non-relational) databases differ fundamentally in data models, schemas, scalability, and use cases. Choosing between them depends on your application's requirements.

### Key Differences

#### 1. Data Model

**SQL (Relational):**
- Data stored in **tables** (rows and columns)
- Relationships via **foreign keys**
- Structured, normalized data

**Example:**
```sql
Users Table:
id | name  | email
1  | John  | john@example.com
2  | Jane  | jane@example.com

Orders Table:
id | user_id | amount
1  | 1       | 100
2  | 1       | 200
```

**NoSQL (Non-Relational):**
- **Key-Value:** Simple key-value pairs (Redis)
- **Document:** JSON-like documents (MongoDB)
- **Column:** Column families (Cassandra)
- **Graph:** Nodes and edges (Neo4j)

**Example (Document):**
```json
{
  "user_id": 1,
  "name": "John",
  "email": "john@example.com",
  "orders": [
    {"id": 1, "amount": 100},
    {"id": 2, "amount": 200}
  ]
}
```

#### 2. Schema

**SQL:**
- **Fixed schema** defined before data insertion
- Schema changes require migrations
- Strict data types

**NoSQL:**
- **Flexible schema** - can vary per document
- Schema changes easier
- Dynamic structure

#### 3. Scalability

**SQL:**
- **Vertical scaling** (scale up)
- Limited horizontal scaling
- Complex to scale across machines

**NoSQL:**
- **Horizontal scaling** (scale out)
- Designed for distributed systems
- Easier to add nodes

**Diagram:**
```
SQL Scaling:
┌─────────────┐
│   Database  │
│  (Bigger)   │ ← Vertical
└─────────────┘

NoSQL Scaling:
┌────┐ ┌────┐ ┌────┐ ┌────┐
│Node│ │Node│ │Node│ │Node│ ← Horizontal
└────┘ └────┘ └────┘ └────┘
```

#### 4. Query Language

**SQL:**
- **Structured Query Language (SQL)**
- Standardized syntax
- Complex queries with JOINs

**Example:**
```sql
SELECT u.name, SUM(o.amount) as total
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.id;
```

**NoSQL:**
- **Varies by database type**
- Document queries (MongoDB)
- Key lookups (Redis)
- Less standardized

**Example (MongoDB):**
```javascript
db.users.aggregate([
  { $lookup: { from: "orders", ... } },
  { $group: { _id: "$name", total: { $sum: "$orders.amount" } } }
])
```

#### 5. Transaction Support

**SQL:**
- **Full ACID transactions**
- Multi-row transactions
- Strong consistency

**NoSQL:**
- **Limited transaction support**
- Often eventual consistency
- Some support ACID (MongoDB 4.0+)

#### 6. Performance

**SQL:**
- Optimized for complex queries
- JOINs can be slow at scale
- Better for analytical queries

**NoSQL:**
- Optimized for simple operations
- Faster reads/writes
- Better for high-throughput

#### 7. Use Cases

**SQL Best For:**
- Financial systems
- E-commerce (orders, inventory)
- Applications requiring complex queries
- Strong consistency requirements
- Relational data

**NoSQL Best For:**
- Social media feeds
- Real-time applications
- Big data analytics
- Content management
- High write throughput

### Comparison Table

| Aspect | SQL | NoSQL |
|--------|-----|-------|
| Data Model | Relational (tables) | Non-relational (various) |
| Schema | Fixed | Flexible |
| Scalability | Vertical | Horizontal |
| Query Language | SQL | Varies |
| Transactions | Full ACID | Limited |
| Consistency | Strong | Eventual (often) |
| Use Case | Complex queries | High throughput |

---

## 3. Indexing

### Summary

Indexing is a data structure technique that speeds up data retrieval operations at the cost of additional storage and slower writes. Think of it like a book's index—instead of reading every page, you look up the index to find the right page quickly.

### Key Concepts

#### Index Types

1. **Primary Index:** On primary key (automatically created)
2. **Secondary Index:** On non-primary columns
3. **Composite Index:** On multiple columns
4. **Covering Index:** Contains all columns needed for query

#### Index Data Structures

**B-Tree Index:**
- Balanced tree structure
- O(log n) lookup
- Good for range queries
- Most common type

**Hash Index:**
- Hash table structure
- O(1) lookup
- Only equality queries
- No range queries

**Bitmap Index:**
- Bitmap per value
- Good for low-cardinality columns
- Efficient for AND/OR operations

### Performance Impact

**Without Index:**
```
Full table scan: O(n)
1M rows = 1M operations
```

**With Index:**
```
Index lookup: O(log n)
1M rows = ~20 operations
Speedup: 50,000x
```

### What to Index

**Good candidates:**
- Frequently queried columns
- Foreign keys
- Columns in WHERE clauses
- Columns in JOIN conditions
- Columns in ORDER BY

**Avoid:**
- Rarely queried columns
- Frequently updated columns
- Very small tables
- Low-cardinality columns (unless bitmap)

### Design Considerations

- **Over-indexing:** Too many indexes slow down writes
- **Under-indexing:** Missing indexes on frequently queried columns
- **Composite Index Order:** Most selective column first
- **Monitor Usage:** Remove unused indexes

**For detailed information:** See [`indexing.md`](./indexing.md)

---

## 4. Sharding

### Summary

Sharding partitions a database horizontally across multiple machines (shards). Each shard contains a subset of data, enabling horizontal scaling when a single database can't handle the load.

### Sharding Strategies

1. **Range-Based:** Partition by value ranges
   - Simple, but can cause hotspots

2. **Hash-Based:** `hash(key) % num_shards`
   - Even distribution
   - Hard to add/remove shards

3. **Directory-Based:** Lookup table maps key → shard
   - Flexible, easy rebalancing
   - Lookup table bottleneck

4. **Geographic:** Partition by location
   - Low latency
   - Uneven distribution possible

### Challenges

1. **Cross-Shard Queries:** Expensive joins across shards
2. **Rebalancing:** Adding/removing shards requires migration
3. **Hotspots:** Uneven distribution
4. **Transactions:** ACID transactions across shards complex

### Shard Key Selection

**Good shard keys:**
- High cardinality
- Even distribution
- Used in queries
- Doesn't change frequently

**Bad shard keys:**
- Low cardinality
- Skewed distribution
- Frequently changing
- Not used in queries

**For detailed information:** See [`sharding.md`](./sharding.md)

---

## 5. Vertical Partitioning

### Summary

Vertical partitioning splits a table by columns, storing different columns in separate tables or databases. This reduces the amount of data read per query and can improve performance.

### How It Works

**Original Table:**
```
Users Table:
id | name | email | bio | profile_pic | created_at | last_login
```

**After Vertical Partitioning:**
```
Users_Core Table:
id | name | email | created_at

Users_Profile Table:
id | bio | profile_pic

Users_Activity Table:
id | last_login | login_count
```

**Diagram:**
```
┌─────────────────────┐
│   Original Table     │
│  (All Columns)       │
└──────────┬───────────┘
           │
    ┌──────┴──────┬──────────────┐
    │             │              │
    ▼             ▼              ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│  Core   │ │ Profile │ │Activity │
│ Columns │ │ Columns │ │ Columns │
└─────────┘ └─────────┘ └─────────┘
```

### Benefits

- **Reduced I/O:** Read only needed columns
- **Better Caching:** Frequently accessed columns cached separately
- **Parallel Processing:** Different partitions on different servers
- **Security:** Sensitive columns isolated

### Use Cases

- **Hot/Cold Data:** Frequently vs rarely accessed columns
- **Security:** Separate sensitive data
- **Performance:** Reduce table size for faster queries
- **Storage:** Store large columns (BLOBs) separately

### Tradeoffs

**Advantages:**
- ✅ Faster queries (less data to read)
- ✅ Better cache utilization
- ✅ Security isolation

**Disadvantages:**
- ❌ JOINs required to reconstruct full row
- ❌ More complex queries
- ❌ Schema changes affect multiple tables

---

## 6. Sharding vs Partitioning

### Summary

Sharding and partitioning are related but distinct concepts. Understanding the difference helps choose the right data distribution strategy.

### Partitioning

**Definition:** Dividing a database into smaller, more manageable pieces **within a single database**.

**Types:**
- **Horizontal Partitioning:** Split by rows (same as sharding, but within one DB)
- **Vertical Partitioning:** Split by columns

**Example:**
```
Single Database:
Partition 1: Users 1-1M
Partition 2: Users 1M-2M
Partition 3: Users 2M-3M
```

**Diagram:**
```
┌─────────────────┐
│   Database       │
│                  │
│ ┌────┐ ┌────┐   │
│ │P1  │ │P2  │   │ ← Partitions
│ └────┘ └────┘   │
│                  │
└─────────────────┘
```

### Sharding

**Definition:** Partitioning data **across multiple databases/servers**.

**Example:**
```
Shard 1 (Server 1): Users 1-1M
Shard 2 (Server 2): Users 1M-2M
Shard 3 (Server 3): Users 2M-3M
```

**Diagram:**
```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Server1 │     │ Server2 │     │ Server3 │
│  Shard1 │     │  Shard2 │     │  Shard3 │
└─────────┘     └─────────┘     └─────────┘
```

### Key Differences

| Aspect | Partitioning | Sharding |
|--------|-------------|----------|
| Location | Within single database | Across multiple databases |
| Scalability | Limited (single server) | High (multiple servers) |
| Complexity | Lower | Higher |
| Cross-partition queries | Easier | Harder |
| Use Case | Performance optimization | Horizontal scaling |

### When to Use

**Partitioning:**
- Large tables within single database
- Performance optimization
- Manageability

**Sharding:**
- Single database can't handle load
- Need horizontal scaling
- Geographic distribution

### Relationship

**Sharding = Partitioning + Distribution**

Sharding is essentially horizontal partitioning across multiple machines.

---

## 7. Replication

### Summary

Database replication creates copies of data across multiple database servers. It improves availability, enables read scaling, and provides disaster recovery.

### Replication Types

#### Master-Slave (Primary-Replica)

- One master handles writes
- Multiple slaves handle reads
- Asynchronous replication
- Simple, common pattern

**Diagram:**
```
Write: ──► Master ──► Replicate ──► Slave 1
                                    Slave 2
                                    Slave 3

Read:  ──► Slave 1, 2, or 3
```

#### Master-Master (Multi-Master)

- Multiple masters handle writes
- Bidirectional replication
- More complex, conflict resolution needed
- Higher availability

**Diagram:**
```
Master 1 ◄─────► Master 2
   │                │
   └────────────────┘
   Bidirectional replication
```

### Synchronous vs Asynchronous

**Synchronous:**
- Real-time replication
- Strong consistency
- Higher latency

**Asynchronous:**
- Delayed replication
- Better performance
- Eventual consistency

### Benefits

- **High Availability:** If master fails, slave takes over
- **Read Scaling:** Distribute read traffic
- **Disaster Recovery:** Replicas in different regions
- **Performance:** Read-heavy workloads benefit

**For detailed information:** See [`database-replication.md`](./database-replication.md)

---

## 8. Connection Pooling

### Summary

Connection pooling maintains a cache of database connections that can be reused across multiple requests. Instead of creating a new connection for each request, connections are reused, significantly improving performance.

### The Problem: Creating Connections is Expensive

**Without Connection Pooling:**
```
Request 1: Create connection → Query → Close connection
Request 2: Create connection → Query → Close connection
Request 3: Create connection → Query → Close connection

Each connection creation: ~100-200ms overhead
```

**With Connection Pooling:**
```
Request 1: Get connection from pool → Query → Return to pool
Request 2: Get connection from pool → Query → Return to pool
Request 3: Get connection from pool → Query → Return to pool

Connection reuse: ~1ms overhead
```

### How It Works

**Connection Pool:**
```
┌─────────────────┐
│ Connection Pool  │
│                  │
│ ┌─────────────┐ │
│ │ Connection1 │ │
│ │ Connection2 │ │
│ │ Connection3 │ │
│ │ Connection4 │ │
│ │ Connection5 │ │
│ └─────────────┘ │
│                  │
│ Max: 10          │
│ Active: 5        │
│ Idle: 5          │
└─────────────────┘
```

**Flow:**
```
Application Request
     │
     ▼
┌──────────────┐
│ Get Connection│
│  from Pool    │
└──────┬───────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
Available  Not Available
   │           │
   │           ▼
   │      Wait or Create
   │           │
   └───────────┘
       │
       ▼
   Execute Query
       │
       ▼
   Return Connection
   to Pool
```

### Configuration Parameters

- **Min Pool Size:** Minimum connections maintained
- **Max Pool Size:** Maximum connections allowed
- **Connection Timeout:** Max wait time for connection
- **Idle Timeout:** Time before idle connection closed
- **Max Lifetime:** Maximum connection age

### Benefits

- **Performance:** Reuse connections (100x faster)
- **Resource Efficiency:** Limit total connections
- **Scalability:** Handle more concurrent requests
- **Stability:** Prevent connection exhaustion

### Implementation Examples

**Java (HikariCP):**
```java
HikariConfig config = new HikariConfig();
config.setMaximumPoolSize(10);
config.setMinimumIdle(5);
HikariDataSource dataSource = new HikariDataSource(config);
```

**Python (SQLAlchemy):**
```python
engine = create_engine(
    'postgresql://...',
    pool_size=10,
    max_overflow=20
)
```

### Design Considerations

- **Pool Size:** Balance between performance and resources
- **Connection Leaks:** Ensure connections returned to pool
- **Health Checks:** Validate connections before use
- **Monitoring:** Track pool usage and connection stats

---

## 9. Denormalization

### Summary

Denormalization is the process of intentionally adding redundant data to a database to improve read performance. It trades storage space and write complexity for faster queries.

### Normalization vs Denormalization

**Normalized Database (3NF):**
```
Users Table:
id | name | email

Orders Table:
id | user_id | amount

To get user name with order:
→ JOIN required
```

**Denormalized Database:**
```
Orders Table:
id | user_id | user_name | amount

To get user name with order:
→ No JOIN needed (faster)
```

**Diagram:**
```
Normalized:
┌────────┐     ┌────────┐
│ Users  │────►│ Orders │
│        │     │        │
│ name   │     │amount  │
└────────┘     └────────┘
   JOIN required

Denormalized:
┌──────────────┐
│   Orders     │
│              │
│ user_name    │ ← Redundant but faster
│ amount       │
└──────────────┘
   No JOIN needed
```

### Why Denormalize?

**Read Performance:**
- Eliminates JOINs
- Faster queries
- Better for read-heavy workloads

**Use Cases:**
- Analytics and reporting
- Read-heavy applications
- NoSQL databases (often denormalized by design)
- Caching strategies

### Denormalization Patterns

#### 1. Duplicate Columns

Store frequently accessed columns in multiple tables.

**Example:**
```
Orders Table:
id | user_id | user_name | user_email | amount

User name/email duplicated in Orders table
→ Faster order queries
→ No JOIN to Users table
```

#### 2. Precomputed Aggregates

Store calculated values instead of computing on-the-fly.

**Example:**
```
Users Table:
id | name | total_orders | total_spent

Instead of:
SELECT COUNT(*), SUM(amount) FROM orders WHERE user_id = X

Just read: total_orders, total_spent
```

#### 3. Flattened Hierarchies

Store hierarchical data in flat structure.

**Example:**
```
Products Table:
id | name | category_id | category_name | parent_category_name

Instead of JOINing through category hierarchy
```

### Tradeoffs

**Advantages:**
- ✅ Faster reads (no JOINs)
- ✅ Simpler queries
- ✅ Better for analytics

**Disadvantages:**
- ❌ More storage space
- ❌ Data redundancy
- ❌ Update complexity (update multiple places)
- ❌ Risk of inconsistency

### When to Denormalize

**Good for:**
- Read-heavy workloads
- Analytics and reporting
- Performance-critical queries
- NoSQL databases

**Avoid when:**
- Write-heavy workloads
- Data consistency critical
- Storage is expensive
- Complex update logic

### Design Considerations

- **Update Strategy:** How to keep denormalized data consistent
- **Tradeoff Analysis:** Performance gain vs storage/update cost
- **Selective Denormalization:** Denormalize only hot paths
- **Monitoring:** Track consistency and performance

---

## 10. Data Compression

### Summary

Data compression reduces the storage space required for data by encoding it more efficiently. It's essential for reducing storage costs, improving I/O performance, and enabling faster data transfer.

### Why Compress Data?

**Benefits:**
- **Storage Savings:** Reduce storage costs by 50-90%
- **I/O Performance:** Less data to read/write
- **Network Transfer:** Faster data transfer
- **Memory Usage:** More data fits in cache

**Tradeoffs:**
- **CPU Overhead:** Compression/decompression costs
- **Latency:** Slight delay for compression

### Compression Types

#### 1. Lossless Compression

**Definition:** Original data can be perfectly reconstructed.

**Use Cases:**
- Database data
- Text files
- Source code
- Any data where accuracy is critical

**Algorithms:**
- **GZIP:** General-purpose compression
- **LZ4:** Fast compression/decompression
- **Zstandard (ZSTD):** Good balance of speed and ratio
- **Snappy:** Fast, moderate compression

#### 2. Lossy Compression

**Definition:** Some data loss acceptable for higher compression.

**Use Cases:**
- Images (JPEG)
- Video (MPEG)
- Audio (MP3)
- Analytics data (approximations OK)

### Database Compression

#### Row-Level Compression

Compress individual rows or blocks of rows.

**Example:**
```
Uncompressed Row:
id=12345, name="John Smith", email="john.smith@example.com"

Compressed Row:
[12345][John Smith][john.smith@example.com]
→ Removed redundant spaces, shorter encoding
```

#### Column-Level Compression

Compress columns separately (better for columnar databases).

**Example:**
```
Column: [1, 1, 1, 2, 2, 3, 3, 3]
Compressed: Run-length encoding
→ [(1,3), (2,2), (3,3)]
```

#### Table-Level Compression

Compress entire tables or partitions.

**Example:**
```
Large table partitioned by date
→ Each partition compressed separately
→ Old partitions highly compressed
```

### Compression Strategies

#### 1. Compress at Rest

**When:** Data stored on disk

**How:**
- Database-level compression
- File system compression
- Storage-level compression

**Benefits:**
- Storage savings
- Backup size reduction

#### 2. Compress in Transit

**When:** Data transferred over network

**How:**
- HTTP compression (gzip)
- Database protocol compression
- Message queue compression

**Benefits:**
- Faster transfer
- Reduced bandwidth

#### 3. Compress in Memory

**When:** Data in application memory

**How:**
- Compressed data structures
- Compressed caches

**Benefits:**
- More data in cache
- Better memory utilization

### Real-World Examples

**PostgreSQL:**
- TOAST (The Oversized-Attribute Storage Technique)
- Compresses large values automatically

**MySQL:**
- InnoDB compression
- Page-level compression

**Columnar Databases:**
- Parquet format (columnar + compression)
- Excellent compression ratios

**Backup Systems:**
- Compressed backups (gzip, bzip2)
- Reduce backup storage by 80-90%

### Design Considerations

**When to Compress:**
- Large datasets
- Archive/old data
- Network transfer
- Storage cost sensitive

**When Not to Compress:**
- Frequently accessed hot data
- CPU-bound systems
- Real-time requirements

**Compression Levels:**
- **Fast:** Quick compression, moderate ratio
- **Balanced:** Good speed and ratio
- **Maximum:** Best ratio, slower

### Performance Impact

**Storage:**
- 50-90% reduction typical
- Depends on data type and algorithm

**I/O:**
- Less data read/written
- Faster for I/O-bound workloads

**CPU:**
- Compression: 10-30% CPU overhead
- Decompression: 5-15% CPU overhead

**Net Effect:**
- Usually positive for I/O-bound systems
- May be negative for CPU-bound systems

---

## Conclusion

Understanding these database fundamentals is essential for designing scalable, performant, and reliable systems. Each technique addresses specific challenges:

- **ACID Transactions:** Ensure data integrity
- **SQL vs NoSQL:** Choose the right database type
- **Indexing:** Optimize query performance
- **Sharding:** Scale horizontally
- **Partitioning:** Optimize within single database
- **Replication:** Improve availability and read performance
- **Connection Pooling:** Improve connection efficiency
- **Denormalization:** Optimize read performance
- **Compression:** Reduce storage and improve I/O

The key is understanding tradeoffs and choosing the right combination of techniques for your specific use case.

