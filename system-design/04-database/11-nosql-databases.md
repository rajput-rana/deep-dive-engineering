# 🗃️ NoSQL Databases

<div align="center">

**Flexible, scalable database systems for modern applications**

[![NoSQL](https://img.shields.io/badge/NoSQL-Flexible-blue?style=for-the-badge)](./)
[![Scalable](https://img.shields.io/badge/Scalable-Horizontal-green?style=for-the-badge)](./)
[![Schema-Less](https://img.shields.io/badge/Schema--Less-Flexible-orange?style=for-the-badge)](./)

*Master NoSQL databases: types, use cases, data modeling, and when to choose NoSQL over SQL*

</div>

---

## 🎯 What is NoSQL?

<div align="center">

**NoSQL (Not Only SQL) is a category of database management systems designed for large-scale data storage and massively-parallel, high-performance data processing across distributed architectures.**

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **🔓 Schema-Less** | Flexible data models, no predefined schema |
| **🌐 Horizontal Scaling** | Scale by adding servers (distributed) |
| **⚡ High Performance** | Optimized for specific use cases |
| **📊 Flexible Data Models** | Documents, key-value, columns, graphs |
| **🔄 Eventual Consistency** | Prioritizes availability over strong consistency |

**Mental Model:** Think of NoSQL as flexible filing systems that can grow horizontally, unlike rigid SQL databases that require predefined structures.

**💡 Why NoSQL Exists:**
- Modern applications (social, interactive, data-heavy) need faster, larger data access
- RDBMS limitations: Not horizontally scalable by default
- Single-server deployments hit scaling limits
- Need for flexible schemas in rapidly evolving applications

</div>

---

## 🏗️ NoSQL vs SQL Databases

<div align="center">

### Fundamental Differences

| Aspect | SQL Databases | NoSQL Databases |
|:---:|:---:|:---:|
| **Data Model** | Table-based (rows/columns) | Document, key-value, column, graph |
| **Schema** | Fixed schema, defined upfront | Flexible, schema-less |
| **Relationships** | Foreign keys, JOINs | Embedding, references, or no JOINs |
| **Scalability** | Vertical (scale up), complex horizontal | Horizontal (scale out) |
| **ACID** | Full ACID support | Eventual consistency (some support ACID) |
| **Query Language** | SQL (standardized) | Database-specific APIs |
| **Best For** | Structured data, complex relationships | Unstructured data, rapid development |

### When to Choose NoSQL

| Scenario | Why NoSQL |
|:---:|:---:|
| **Rapid Development** | Flexible schema, faster iteration |
| **Large-Scale Data** | Horizontal scaling |
| **Unstructured Data** | No fixed schema required |
| **High Write Throughput** | Optimized for writes |
| **Distributed Systems** | Built for distributed architectures |
| **Real-Time Analytics** | Fast reads, eventual consistency acceptable |

### When to Choose SQL

| Scenario | Why SQL |
|:---:|:---:|
| **Complex Relationships** | JOINs, foreign keys |
| **ACID Requirements** | Strong consistency needed |
| **Structured Data** | Fixed schema works |
| **Complex Queries** | SQL power, aggregations |
| **Small to Medium Scale** | Vertical scaling sufficient |

</div>

---

## 📊 Types of NoSQL Databases

<div align="center">

### 1. Key-Value Stores

**Simple key-value pairs**

| Characteristic | Description |
|:---:|:---:|
| **Data Model** | Key → Value mapping |
| **Complexity** | Simplest NoSQL type |
| **Use Cases** | Caching, session storage, configuration |
| **Examples** | Redis, DynamoDB, Riak |

**Example:**
```javascript
// Redis
SET user:123 "{name: 'John', age: 30}"
GET user:123
```

**Best For:**
- ✅ Caching
- ✅ Session management
- ✅ User profiles
- ✅ Configuration settings
- ✅ Real-time analytics

---

### 2. Document Stores

**JSON-like documents with nested structures**

| Characteristic | Description |
|:---:|:---:|
| **Data Model** | Documents (JSON/BSON) |
| **Structure** | Nested objects, arrays |
| **Use Cases** | Content management, catalogs, user profiles |
| **Examples** | MongoDB, CouchDB, Couchbase |

**Example:**
```javascript
// MongoDB
{
  _id: ObjectId("..."),
  name: "John Doe",
  email: "john@example.com",
  address: {
    street: "123 Main St",
    city: "New York"
  },
  hobbies: ["reading", "coding"]
}
```

**Best For:**
- ✅ Content management systems
- ✅ Product catalogs
- ✅ User profiles
- ✅ Blogging platforms
- ✅ Rapid prototyping

---

### 3. Column-Family Stores (Wide-Column)

**Columns organized into column families**

| Characteristic | Description |
|:---:|:---:|
| **Data Model** | Rows × Column families |
| **Structure** | Sparse, wide tables |
| **Use Cases** | Time-series, analytics, IoT |
| **Examples** | Cassandra, HBase, ScyllaDB |

**Example:**
```
Row Key: user_123
Column Family: profile
  name: "John"
  email: "john@example.com"
Column Family: activity
  2024-01-15: "logged_in"
  2024-01-16: "purchased"
```

**Best For:**
- ✅ Time-series data
- ✅ Analytics workloads
- ✅ IoT sensor data
- ✅ High write throughput
- ✅ Large-scale distributed systems

---

### 4. Graph Databases

**Nodes and relationships**

| Characteristic | Description |
|:---:|:---:|
| **Data Model** | Nodes, edges, properties |
| **Structure** | Graph structure |
| **Use Cases** | Social networks, recommendations, fraud detection |
| **Examples** | Neo4j, Amazon Neptune, ArangoDB |

**Example:**
```
(User:John)-[:FRIENDS_WITH]->(User:Jane)
(User:John)-[:LIKES]->(Post:123)
(User:Jane)-[:FOLLOWS]->(User:John)
```

**Best For:**
- ✅ Social networks
- ✅ Recommendation engines
- ✅ Fraud detection
- ✅ Knowledge graphs
- ✅ Network analysis

</div>

---

## 🎯 CAP Theorem

<div align="center">

### Understanding CAP

**CAP Theorem: In a distributed system, you can only guarantee two out of three:**

| Component | Description |
|:---:|:---:|
| **Consistency (C)** | All nodes see same data simultaneously |
| **Availability (A)** | System remains operational |
| **Partition Tolerance (P)** | System continues despite network failures |

### CAP Trade-offs

| Choice | Description | Examples |
|:---:|:---:|:---:|
| **CP** | Consistency + Partition Tolerance | MongoDB (with strong consistency), HBase |
| **AP** | Availability + Partition Tolerance | Cassandra, DynamoDB, CouchDB |
| **CA** | Consistency + Availability | Traditional SQL (single node) |

**💡 Key Insight:** Partition tolerance is mandatory in distributed systems, so you choose between Consistency and Availability.

### NoSQL and CAP

| NoSQL Type | Typical CAP Choice | Why |
|:---:|:---:|:---:|
| **Key-Value** | AP or CP | Depends on configuration |
| **Document** | AP (default) | Prioritizes availability |
| **Column-Family** | AP | Optimized for availability |
| **Graph** | CP or AP | Depends on implementation |

**Example:**
- **Cassandra (AP):** Prioritizes availability, eventual consistency
- **MongoDB (CP):** Can enforce consistency, may sacrifice availability
- **Redis (CP):** Strong consistency, may be unavailable during partitions

</div>

---

## 📐 Data Modeling in NoSQL

<div align="center">

### Key Principles

| Principle | Description | SQL Equivalent |
|:---:|:---:|:---:|
| **Denormalization** | Duplicate data for performance | Normalization |
| **Embedding** | Store related data together | JOINs |
| **References** | Link documents with IDs | Foreign keys |
| **Query-Driven** | Model based on access patterns | Schema-first |

### Embedding vs Referencing

**Embedding (Denormalization):**

```javascript
// User with embedded addresses
{
  _id: ObjectId("user123"),
  name: "John",
  addresses: [
    { type: "home", street: "123 Main St" },
    { type: "work", street: "456 Oak Ave" }
  ]
}
```

**✅ Use When:**
- One-to-few relationships
- Data accessed together
- Atomic updates needed
- Read-heavy workloads

**Referencing:**

```javascript
// User document
{
  _id: ObjectId("user123"),
  name: "John",
  order_ids: [ObjectId("order1"), ObjectId("order2")]
}

// Order document
{
  _id: ObjectId("order1"),
  user_id: ObjectId("user123"),
  total: 100
}
```

**✅ Use When:**
- One-to-many, many-to-many
- Large arrays
- Data changes independently
- Document size limits

### Data Modeling Best Practices

| Practice | Description |
|:---:|:---:|
| **Understand Access Patterns** | Model for how data is queried |
| **Denormalize Strategically** | Trade storage for performance |
| **Consider Document Size** | MongoDB: 16MB limit |
| **Optimize for Reads** | Most systems are read-heavy |
| **Plan for Sharding** | Design shard keys early |

</div>

---

## ⚖️ Advantages & Disadvantages

<div align="center">

### ✅ Advantages

| Advantage | Description | Impact |
|:---:|:---:|:---:|
| **Flexibility** | Schema-less, rapid development | Faster iteration |
| **Scalability** | Horizontal scaling | Handle large datasets |
| **Performance** | Optimized for specific use cases | Fast reads/writes |
| **Cost-Effective** | Commodity hardware | Lower infrastructure cost |
| **Developer-Friendly** | JSON-like structures | Easier for developers |

### ❌ Disadvantages

| Disadvantage | Description | Impact |
|:---:|:---:|:---:|
| **Eventual Consistency** | Not immediately consistent | May read stale data |
| **No Standardization** | Different APIs per database | Learning curve |
| **Limited JOINs** | Complex relationships harder | Application-level joins |
| **Maturity** | Newer than SQL | Fewer tools, less support |
| **ACID Limitations** | Not all support full ACID | Consistency trade-offs |

### Trade-offs Summary

| Aspect | SQL | NoSQL |
|:---:|:---:|:---:|
| **Consistency** | Strong | Eventual |
| **Scalability** | Vertical | Horizontal |
| **Flexibility** | Fixed schema | Flexible schema |
| **Complexity** | JOINs, transactions | Simpler operations |
| **Maturity** | Decades old | Relatively new |

</div>

---

## 🔄 Consistency Models

<div align="center">

### Strong Consistency

**All nodes see same data immediately after write**

| Characteristic | Description |
|:---:|:---:|
| **Guarantee** | Immediate consistency |
| **Trade-off** | Lower availability |
| **Use Case** | Financial transactions, critical data |
| **Example** | MongoDB with write concern "majority" |

**Example:**
```javascript
// MongoDB with strong consistency
db.orders.insertOne(
  { user_id: 123, total: 100 },
  { writeConcern: { w: "majority" } }
)
```

---

### Eventual Consistency

**Updates propagate to all nodes over time**

| Characteristic | Description |
|:---:|:---:|
| **Guarantee** | Consistency eventually |
| **Trade-off** | May read stale data |
| **Use Case** | Social feeds, analytics |
| **Example** | Cassandra, DynamoDB |

**How It Works:**
1. Write to one node
2. Replicate asynchronously
3. All nodes eventually consistent
4. May read stale data during replication

**💡 Key Insight:** Eventual consistency prioritizes availability and partition tolerance over immediate consistency.

</div>

---

## 📈 Scaling NoSQL Databases

<div align="center">

### Horizontal Scaling Strategies

**Relational DBs don't scale horizontally by default, so you combine patterns:**

| Pattern | Description | Use Case |
|:---:|:---:|:---:|
| **Read Replicas** | Scale reads | Read-heavy workloads |
| **Sharding** | Scale writes and data size | Write-heavy, large datasets |
| **Partitioning** | Manageability | Large collections/tables |

### Sharding Strategies

| Strategy | Description | Example |
|:---:|:---:|:---:|
| **Range Sharding** | Partition by value range | User IDs 1-1000 → Shard 1 |
| **Hash Sharding** | Partition by hash | Hash(user_id) % num_shards |
| **Directory-Based** | Lookup table | Metadata service |

**Shard Key Selection:**
- ✅ High cardinality (many unique values)
- ✅ Even distribution
- ✅ Used in queries
- ❌ Avoid monotonic (dates, auto-increment)

### Cross-Shard Operations

**Challenges:**
- ❌ Cross-shard JOINs are expensive
- ❌ Cross-shard transactions are complex
- ❌ Strong consistency harder to achieve

**Solutions:**
- ✅ Handle at application layer
- ✅ Denormalize data
- ✅ Accept eventual consistency
- ✅ Use distributed transactions (if supported)

</div>

---

## 🎯 Use Cases

<div align="center">

### Ideal NoSQL Scenarios

| Use Case | Why NoSQL | Database Type |
|:---:|:---:|:---:|
| **Social Media** | Flexible user profiles, feeds | Document, Graph |
| **E-commerce** | Product catalogs, varying attributes | Document |
| **Real-Time Analytics** | Fast writes, eventual consistency | Column-Family |
| **Content Management** | Flexible content structure | Document |
| **IoT/Sensor Data** | Time-series, high write volume | Column-Family |
| **Caching** | Fast key-value access | Key-Value |
| **Recommendations** | Complex relationships | Graph |
| **Session Storage** | Temporary data, fast access | Key-Value |

### Industry Examples

| Industry | Use Case | Database |
|:---:|:---:|:---:|
| **Social Media** | User feeds, relationships | MongoDB, Neo4j |
| **E-commerce** | Product catalogs, inventory | MongoDB, DynamoDB |
| **Gaming** | Leaderboards, sessions | Redis, MongoDB |
| **IoT** | Sensor data, telemetry | Cassandra, InfluxDB |
| **Finance** | Real-time analytics | Cassandra, Redis |

</div>

---

## 🔧 Common Operations

<div align="center">

### Key-Value Store (Redis)

**Connect and Set:**
```javascript
const redis = require('redis');
const client = redis.createClient();

client.set('user:123', JSON.stringify({
  name: 'John',
  age: 30
}));

client.get('user:123', (err, value) => {
  console.log(JSON.parse(value));
});
```

---

### Document Store (MongoDB)

**Insert Document:**
```javascript
db.users.insertOne({
  name: "John Doe",
  age: 30,
  email: "john@example.com",
  city: "New York"
});
```

**Find Documents:**
```javascript
// Find all
db.users.find({});

// Find with condition
db.users.find({ age: { $gt: 25 } });

// Find one
db.users.findOne({ email: "john@example.com" });
```

**Update Document:**
```javascript
db.users.updateOne(
  { name: "John Doe" },
  { $set: { age: 31 } }
);
```

**Delete Document:**
```javascript
db.users.deleteOne({ name: "John Doe" });
```

**Aggregation:**
```javascript
db.orders.aggregate([
  { $group: { 
    _id: "$customerId", 
    total: { $sum: "$amount" } 
  } },
  { $sort: { total: -1 } }
]);
```

**Join ($lookup):**
```javascript
db.orders.aggregate([
  {
    $lookup: {
      from: "customers",
      localField: "customerId",
      foreignField: "_id",
      as: "customerDetails"
    }
  }
]);
```

---

### Column-Family Store (Cassandra)

**Create Table:**
```cql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name text,
  age int,
  email text
);
```

**Insert Data:**
```cql
INSERT INTO users (id, name, age, email)
VALUES (uuid(), 'John Doe', 30, 'john@example.com');
```

**Query:**
```cql
SELECT * FROM users WHERE id = ?;
```

---

### Graph Database (Neo4j)

**Create Nodes and Relationships:**
```cypher
// Create nodes
CREATE (u1:User {name: 'John'})
CREATE (u2:User {name: 'Jane'})

// Create relationship
CREATE (u1)-[:FRIENDS_WITH]->(u2)

// Query
MATCH (u1:User)-[:FRIENDS_WITH]->(u2:User)
RETURN u1, u2;
```

</div>

---

## 🔍 Indexing in NoSQL

<div align="center">

### Index Types

| Database Type | Index Support | Example |
|:---:|:---:|:---:|
| **Document** | Single, compound, text, geospatial | MongoDB indexes |
| **Key-Value** | Limited (key-based) | Redis sorted sets |
| **Column-Family** | Primary key, secondary indexes | Cassandra indexes |
| **Graph** | Node/edge properties | Neo4j indexes |

### Importance

| Aspect | Description |
|:---:|:---:|
| **Performance** | Faster data retrieval |
| **Query Optimization** | Supports efficient queries |
| **Trade-offs** | Increased storage, write overhead |

**Example (MongoDB):**
```javascript
// Create index
db.users.createIndex({ email: 1 });

// Compound index
db.orders.createIndex({ userId: 1, date: -1 });

// Text index
db.articles.createIndex({ content: "text" });
```

</div>

---

## 🔄 Data Migration: SQL to NoSQL

<div align="center">

### Migration Process

| Step | Description | Details |
|:---:|:---:|:---:|
| **1. Analyze** | Understand SQL schema | Tables, relationships, constraints |
| **2. Choose NoSQL** | Select appropriate type | Based on use case |
| **3. Design Schema** | Redesign for NoSQL | Denormalize, embed vs reference |
| **4. Extract** | Export SQL data | CSV, JSON format |
| **5. Transform** | Convert to NoSQL format | Restructure documents |
| **6. Load** | Import to NoSQL | Database-specific tools |
| **7. Validate** | Verify data integrity | Compare counts, spot checks |
| **8. Update App** | Modify application code | New drivers, queries |
| **9. Test** | Thorough testing | Functionality, performance |
| **10. Deploy** | Go live | Monitor transition |

### Key Challenges

| Challenge | Solution |
|:---:|:---:|
| **Schema Redesign** | Denormalize, embed related data |
| **JOINs** | Denormalize or application-level joins |
| **Transactions** | Use NoSQL transactions or application logic |
| **Data Types** | Map SQL types to NoSQL types |
| **Relationships** | Embed or reference based on access patterns |

</div>

---

## 🎓 Interview Questions & Answers

<div align="center">

### Fundamental Questions

| Question | Answer |
|:---:|:---:|
| **What is NoSQL?** | Category of databases for large-scale, distributed data storage with flexible schemas |
| **How does NoSQL differ from SQL?** | Schema-less, horizontal scaling, flexible data models vs fixed schema, vertical scaling |
| **What are the 4 types of NoSQL?** | Key-value, Document, Column-family, Graph |
| **Explain CAP theorem** | Can only guarantee 2 of 3: Consistency, Availability, Partition Tolerance |
| **What is eventual consistency?** | Updates propagate over time; all nodes eventually consistent |
| **What is strong consistency?** | All nodes see same data immediately after write |

---

### Technical Questions

| Question | Answer |
|:---:|:---:|
| **How do you model data in NoSQL?** | Denormalize, embed related data, optimize for access patterns |
| **Embedding vs Referencing?** | Embed for one-to-few, access together; Reference for one-to-many, independent changes |
| **What is sharding?** | Distribute data across multiple servers for scalability |
| **How do you handle relationships?** | Embedding, references, or application-level joins |
| **What is indexing in NoSQL?** | Data structures to improve query performance |
| **How do you scale NoSQL?** | Horizontal scaling via sharding, read replicas |

---

### Practical Questions

| Question | Answer |
|:---:|:---:|
| **When to use NoSQL?** | Large-scale data, flexible schema, rapid development, horizontal scaling |
| **When to use SQL?** | Complex relationships, ACID requirements, structured data |
| **How to migrate SQL to NoSQL?** | Analyze schema, redesign, extract-transform-load, validate, update app |
| **How to handle JOINs?** | Denormalize data, use $lookup (MongoDB), or application-level joins |
| **How to ensure consistency?** | Use write concerns, transactions (if supported), or accept eventual consistency |

</div>

---

## 🚀 Best Practices

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Understand access patterns** | Model for how data is queried |
| **Denormalize strategically** | Trade storage for performance |
| **Design shard keys early** | Avoid costly re-sharding |
| **Use appropriate indexes** | Optimize query performance |
| **Plan for eventual consistency** | Design for eventual consistency |
| **Monitor performance** | Identify bottlenecks early |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Over-normalize** | Too many queries | Denormalize |
| **Ignore shard keys** | Hot shards | Design good shard keys |
| **No indexes** | Slow queries | Create appropriate indexes |
| **Expect strong consistency** | Availability issues | Accept eventual consistency |
| **Cross-shard operations** | Performance issues | Denormalize or avoid |

</div>

---

## 📊 Comparison Matrix

<div align="center">

### NoSQL Database Comparison

| Database | Type | CAP | Best For | Example Use Case |
|:---:|:---:|:---:|:---:|:---:|
| **MongoDB** | Document | AP/CP | Flexible schemas | Content management |
| **Redis** | Key-Value | CP | Caching, sessions | Real-time leaderboards |
| **Cassandra** | Column-Family | AP | Time-series, analytics | IoT sensor data |
| **Neo4j** | Graph | CP | Relationships | Social networks |
| **DynamoDB** | Key-Value | AP | Serverless, AWS | Web applications |
| **CouchDB** | Document | AP | Offline-first | Mobile apps |

</div>

---

## 💡 Key Takeaways

<div align="center">

### Summary

| Concept | Key Point |
|:---:|:---:|
| **NoSQL Types** | Key-value, Document, Column-family, Graph |
| **Scaling** | Horizontal scaling via sharding |
| **Consistency** | Eventual consistency for availability |
| **Data Modeling** | Denormalize, embed, optimize for queries |
| **CAP Theorem** | Choose between Consistency and Availability |
| **Use Cases** | Large-scale, flexible schema, rapid development |

**💡 Remember:** NoSQL doesn't mean "no SQL" - it means "Not Only SQL". Choose the right tool for the job.

</div>

---

<div align="center">

**Master NoSQL databases for scalable, flexible data storage! 🚀**

*NoSQL databases enable modern applications to scale horizontally and handle diverse data types efficiently.*

</div>

