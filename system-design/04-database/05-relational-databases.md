# 🗄️ Relational Databases (SQL)

<div align="center">

**The foundation of structured data storage**

[![SQL](https://img.shields.io/badge/SQL-Relational-blue?style=for-the-badge)](./)
[![ACID](https://img.shields.io/badge/ACID-Compliant-green?style=for-the-badge)](./)
[![Transactions](https://img.shields.io/badge/Transactions-Supported-orange?style=for-the-badge)](./)

*Master relational database design, normalization, and optimization*

</div>

---

## 🎯 What is a Relational Database?

<div align="center">

**A relational database organizes data into tables (relations) with rows and columns, using SQL to query and manipulate data.**

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **📊 Structured Data** | Data organized in tables with fixed schema |
| **🔗 Relationships** | Tables linked via foreign keys |
| **✅ ACID Properties** | Atomicity, Consistency, Isolation, Durability |
| **📝 SQL Language** | Standardized query language |
| **🔒 Strong Consistency** | Immediate consistency guarantees |

</div>

---

## 🏗️ Core Concepts

<div align="center">

### Database Components

| Component | Description | Example |
|:---:|:---:|:---:|
| **Table** | Collection of rows and columns | `users`, `orders`, `products` |
| **Row (Tuple)** | Single record in a table | One user with id=1 |
| **Column (Attribute)** | Field in a table | `email`, `name`, `created_at` |
| **Primary Key** | Unique identifier for each row | `user_id` |
| **Foreign Key** | Reference to another table's primary key | `order.user_id` → `users.id` |
| **Index** | Data structure for fast lookups | Index on `email` column |
| **Constraint** | Rules enforcing data integrity | NOT NULL, UNIQUE, CHECK |

</div>

---

## 📐 Database Design Principles

<div align="center">

### Normalization

**Normalization reduces data redundancy and improves data integrity.**

| Normal Form | Description | Key Rule |
|:---:|:---:|:---:|
| **1NF** | Each column contains atomic values | No repeating groups |
| **2NF** | 1NF + no partial dependencies | All non-key attributes depend on full primary key |
| **3NF** | 2NF + no transitive dependencies | No non-key attribute depends on another non-key attribute |
| **BCNF** | 3NF + every determinant is a candidate key | Stronger than 3NF |
| **4NF** | BCNF + no multi-valued dependencies | Handles multi-valued attributes |
| **5NF** | 4NF + no join dependencies | Project-join normal form |

**💡 Trade-off:** Higher normalization reduces redundancy but may require more joins.

---

### Denormalization

**Denormalization intentionally introduces redundancy for performance.**

| When to Denormalize | Why |
|:---:|:---:|
| **Read-Heavy Workloads** | Reduce join operations |
| **Reporting Systems** | Pre-computed aggregations |
| **Performance Critical** | Faster queries at cost of storage |

**⚠️ Trade-off:** Faster reads vs. data redundancy and update complexity.

</div>

---

## 🔑 ACID Properties

<div align="center">

### The Foundation of Relational Databases

| Property | Description | Example |
|:---:|:---:|:---:|
| **A - Atomicity** | All or nothing | Transfer: debit + credit both succeed or both fail |
| **C - Consistency** | Valid state transitions | Account balance never negative |
| **I - Isolation** | Concurrent transactions don't interfere | Two transfers don't corrupt each other |
| **D - Durability** | Committed changes persist | Survives crashes |

### Isolation Levels

| Level | Description | Dirty Read | Non-Repeatable Read | Phantom Read |
|:---:|:---:|:---:|:---:|:---:|
| **READ UNCOMMITTED** | Lowest isolation | ✅ Possible | ✅ Possible | ✅ Possible |
| **READ COMMITTED** | Default in many DBs | ❌ No | ✅ Possible | ✅ Possible |
| **REPEATABLE READ** | Consistent reads | ❌ No | ❌ No | ✅ Possible |
| **SERIALIZABLE** | Highest isolation | ❌ No | ❌ No | ❌ No |

**💡 Higher isolation = Better consistency but lower concurrency**

</div>

---

## 📊 SQL Fundamentals

<div align="center">

### Core SQL Operations

| Operation | SQL Keyword | Purpose |
|:---:|:---:|:---:|
| **Create** | `CREATE TABLE` | Define table structure |
| **Read** | `SELECT` | Query data |
| **Update** | `UPDATE` | Modify existing rows |
| **Delete** | `DELETE` | Remove rows |
| **Join** | `JOIN`, `INNER JOIN`, `LEFT JOIN` | Combine tables |
| **Aggregate** | `GROUP BY`, `HAVING`, `COUNT`, `SUM` | Summarize data |
| **Filter** | `WHERE`, `LIKE`, `IN`, `BETWEEN` | Conditionally select |

### Common SQL Patterns

**Basic Query:**
```sql
SELECT column1, column2
FROM table_name
WHERE condition
ORDER BY column1 DESC
LIMIT 10;
```

**Join Example:**
```sql
SELECT u.name, o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id
WHERE o.status = 'completed';
```

**Aggregation:**
```sql
SELECT user_id, COUNT(*) as order_count, SUM(total) as total_spent
FROM orders
GROUP BY user_id
HAVING COUNT(*) > 5;
```

</div>

---

## 🎯 Database Design Patterns

<div align="center">

### Common Design Patterns

| Pattern | Description | Use Case |
|:---:|:---:|:---:|
| **One-to-One** | One row in Table A → One row in Table B | User → UserProfile |
| **One-to-Many** | One row in Table A → Many rows in Table B | User → Orders |
| **Many-to-Many** | Many rows in Table A ↔ Many rows in Table B | Users ↔ Products (via Orders) |
| **Self-Referencing** | Table references itself | Employee → Manager (Employee) |
| **Hierarchical** | Tree structure | Categories, Comments (threaded) |
| **Audit Pattern** | Track changes over time | Created_at, Updated_at, Version |

### Many-to-Many Implementation

**Junction Table Pattern:**
```sql
-- Users table
CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100));

-- Products table
CREATE TABLE products (id INT PRIMARY KEY, name VARCHAR(100));

-- Junction table
CREATE TABLE user_products (
    user_id INT REFERENCES users(id),
    product_id INT REFERENCES products(id),
    PRIMARY KEY (user_id, product_id)
);
```

</div>

---

## ⚡ Performance Optimization

<div align="center">

### Indexing Strategies

| Index Type | Description | Best For |
|:---:|:---:|:---:|
| **B-Tree Index** | Balanced tree structure | Most common, range queries |
| **Hash Index** | Hash table | Equality lookups only |
| **Composite Index** | Multiple columns | Multi-column WHERE clauses |
| **Partial Index** | Index subset of rows | Filtered queries |
| **Covering Index** | Includes all query columns | Avoid table lookups |

**💡 Index Trade-offs:**
- ✅ Faster reads
- ❌ Slower writes (index maintenance)
- ❌ Additional storage

---

### Query Optimization

| Technique | Description | Impact |
|:---:|:---:|:---:|
| **Use Indexes** | Index frequently queried columns | 10-1000x faster |
| **Avoid SELECT *** | Select only needed columns | Reduce data transfer |
| **Use LIMIT** | Limit result set size | Faster queries |
| **Optimize JOINs** | Join on indexed columns | Faster joins |
| **Use EXPLAIN** | Analyze query execution plan | Identify bottlenecks |
| **Avoid N+1 Queries** | Use JOINs or batch queries | Reduce round trips |

### EXPLAIN Plan Example

```sql
EXPLAIN SELECT u.name, o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id
WHERE u.email = 'user@example.com';
```

**Key Metrics:**
- **Rows examined** - Should be minimized
- **Index usage** - Look for "Using index"
- **Join type** - Prefer "Index" over "Full table scan"

</div>

---

## 🔄 Transactions

<div align="center">

### Transaction Management

**Transaction = Unit of work that must be atomic**

```sql
BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT; -- or ROLLBACK on error
```

### Transaction Properties

| Property | Implementation |
|:---:|:---:|
| **Atomicity** | All statements succeed or all fail |
| **Consistency** | Database constraints enforced |
| **Isolation** | Isolation level determines visibility |
| **Durability** | WAL (Write-Ahead Logging) ensures persistence |

### Deadlocks

**Deadlock = Two transactions waiting for each other**

**Prevention:**
- Acquire locks in consistent order
- Use shorter transactions
- Use lower isolation levels when possible

**Detection:**
- Database detects and rolls back one transaction

</div>

---

## 🏢 Popular Relational Databases

<div align="center">

### Database Comparison

| Database | Type | Best For | Key Features |
|:---:|:---:|:---:|:---:|
| **PostgreSQL** | Open-source | Complex queries, JSON support | Advanced features, extensible |
| **MySQL** | Open-source | Web applications | Fast, widely used |
| **SQL Server** | Commercial | Enterprise Windows apps | Integration with Microsoft stack |
| **Oracle** | Commercial | Enterprise applications | High performance, advanced features |
| **SQLite** | Embedded | Mobile apps, small projects | Lightweight, file-based |

### PostgreSQL Highlights

- **JSON/JSONB support** - Document-like queries
- **Full-text search** - Built-in text search
- **Array types** - Native array support
- **Custom types** - User-defined types
- **Extensions** - PostGIS, pg_trgm, etc.

### MySQL Highlights

- **Performance** - Optimized for read-heavy workloads
- **Replication** - Master-slave replication
- **Partitioning** - Table partitioning support
- **Storage engines** - InnoDB, MyISAM options

</div>

---

## 📈 Scaling Relational Databases

<div align="center">

### Vertical Scaling (Scale Up)

**Add more resources to single server**

| Resource | Impact |
|:---:|:---:|
| **CPU** | Faster query processing |
| **RAM** | Larger buffer pool, more caching |
| **SSD** | Faster I/O operations |

**Limits:** Hardware constraints, cost

---

### Horizontal Scaling (Scale Out)

**Add more database servers**

| Strategy | Description | Trade-offs |
|:---:|:---:|:---:|
| **Read Replicas** | Multiple read-only copies | Eventual consistency |
| **Sharding** | Partition data across servers | Complex queries, joins |
| **Partitioning** | Split tables by range/hash | Application complexity |

**Challenges:**
- Cross-shard queries
- Maintaining consistency
- Rebalancing data

</div>

---

## 🔐 Security Best Practices

<div align="center">

### Security Measures

| Practice | Description | Implementation |
|:---:|:---:|:---:|
| **Encryption at Rest** | Encrypt data on disk | TDE (Transparent Data Encryption) |
| **Encryption in Transit** | Encrypt network traffic | TLS/SSL |
| **Access Control** | Role-based permissions | GRANT/REVOKE statements |
| **Parameterized Queries** | Prevent SQL injection | Prepared statements |
| **Audit Logging** | Track database access | Enable audit logs |
| **Regular Backups** | Data recovery | Automated backup strategy |

### SQL Injection Prevention

**❌ Vulnerable:**
```sql
SELECT * FROM users WHERE email = '$email';
-- If email = "admin@example.com' OR '1'='1"
```

**✅ Safe (Parameterized):**
```sql
SELECT * FROM users WHERE email = ?;
-- Parameter: "admin@example.com' OR '1'='1"
-- Treated as literal string
```

</div>

---

## 🎓 Database Design Interview Questions

<div align="center">

### Expert-Level Questions

| Question | Key Points |
|:---:|:---:|
| **Design a database for Twitter** | Users, Tweets, Follows (many-to-many), Likes, Retweets, Timeline generation |
| **How do you handle high write throughput?** | Write replicas, async replication, eventual consistency, sharding |
| **Design a database for an e-commerce site** | Products, Users, Orders, OrderItems, Payments, Inventory |
| **How do you ensure data consistency across shards?** | Distributed transactions, eventual consistency, saga pattern |
| **Design a database for a messaging app** | Users, Conversations, Messages, Read receipts, Typing indicators |
| **How do you optimize slow queries?** | EXPLAIN plan, indexes, query rewriting, denormalization |
| **Design a database for a ride-sharing app** | Drivers, Riders, Rides, Locations, Ratings, Payments |

</div>

---

## 💡 Common Patterns & Anti-Patterns

<div align="center">

### ✅ Best Practices

| Practice | Why |
|:---:|:---:|
| **Normalize first, denormalize later** | Start with clean design, optimize as needed |
| **Use appropriate data types** | Storage efficiency, validation |
| **Index foreign keys** | Faster joins |
| **Use transactions for related operations** | Maintain consistency |
| **Design for queries** | Optimize for actual access patterns |

---

### ❌ Anti-Patterns

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Over-normalization** | Too many joins, slow queries | Strategic denormalization |
| **Under-normalization** | Data redundancy, inconsistency | Normalize to 3NF |
| **Missing indexes** | Slow queries | Index frequently queried columns |
| **Too many indexes** | Slow writes | Index only what's needed |
| **N+1 queries** | Performance bottleneck | Use JOINs or batch queries |
| **Storing JSON in text** | No querying, no validation | Use JSON/JSONB type |

</div>

---

## 🔄 Backup & Recovery

<div align="center">

### Backup Strategies

| Strategy | Description | Recovery Time |
|:---:|:---:|:---:|
| **Full Backup** | Complete database copy | Slowest restore |
| **Incremental Backup** | Changes since last backup | Faster restore |
| **Differential Backup** | Changes since last full backup | Medium restore |
| **Point-in-Time Recovery** | Restore to specific timestamp | Fastest restore |

### Recovery Scenarios

| Scenario | Strategy |
|:---:|:---:|
| **Data corruption** | Restore from backup |
| **Accidental deletion** | Point-in-time recovery |
| **Hardware failure** | Restore to new server |
| **Disaster recovery** | Replicate to different region |

</div>

---

## 📚 Advanced Topics

<div align="center">

### Advanced Features

| Feature | Description | Use Case |
|:---:|:---:|:---:|
| **Stored Procedures** | Pre-compiled SQL code | Complex business logic |
| **Triggers** | Automatic actions on events | Audit logging, validation |
| **Views** | Virtual tables | Simplify queries, security |
| **Materialized Views** | Pre-computed views | Expensive aggregations |
| **Full-Text Search** | Text search capabilities | Search functionality |
| **Window Functions** | Row-level calculations | Rankings, running totals |

### Window Functions Example

```sql
SELECT 
    user_id,
    order_date,
    total,
    SUM(total) OVER (PARTITION BY user_id ORDER BY order_date) as running_total,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date DESC) as recent_order_rank
FROM orders;
```

</div>

---

## 🎯 When to Use Relational Databases

<div align="center">

### ✅ Ideal Use Cases

| Use Case | Why SQL |
|:---:|:---:|
| **Structured Data** | Tables with fixed schema |
| **ACID Requirements** | Financial transactions, critical data |
| **Complex Queries** | JOINs, aggregations, reporting |
| **Relationships** | Foreign keys, referential integrity |
| **Consistency** | Strong consistency requirements |
| **Mature Ecosystem** | Tools, ORMs, expertise |

---

### ❌ When NOT to Use

| Scenario | Better Alternative |
|:---:|:---:|
| **Unstructured Data** | Document databases (MongoDB) |
| **High Write Throughput** | NoSQL databases |
| **Simple Key-Value** | Redis, DynamoDB |
| **Graph Relationships** | Graph databases (Neo4j) |
| **Time-Series Data** | Time-series databases (InfluxDB) |

</div>

---

## 🚀 Getting Started

<div align="center">

### Learning Path

| Step | Topic | Resource |
|:---:|:---:|:---:|
| **1️⃣** | SQL Basics | Learn SELECT, INSERT, UPDATE, DELETE |
| **2️⃣** | Database Design | Normalization, relationships |
| **3️⃣** | Advanced SQL | JOINs, subqueries, window functions |
| **4️⃣** | Performance | Indexing, query optimization |
| **5️⃣** | Transactions | ACID, isolation levels |
| **6️⃣** | Scaling | Replication, sharding |

</div>

---

<div align="center">

**Master relational databases for structured data storage! 🚀**

*Relational databases remain the gold standard for structured data with ACID guarantees.*

</div>

