# 📄 MongoDB - Document Database

<div align="center">

**Flexible, schema-less document storage**

[![MongoDB](https://img.shields.io/badge/MongoDB-Document-green?style=for-the-badge)](https://www.mongodb.com/)
[![NoSQL](https://img.shields.io/badge/NoSQL-Flexible-blue?style=for-the-badge)](./)
[![JSON](https://img.shields.io/badge/JSON-Native-orange?style=for-the-badge)](./)

*Master document database design, aggregation, and scaling strategies*

</div>

---

## 🎯 What is MongoDB?

<div align="center">

**MongoDB is a NoSQL document database that stores data in flexible, JSON-like documents called BSON.**

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **📄 Document-Oriented** | Data stored as documents (BSON) |
| **🔓 Schema-Less** | Flexible schema, no fixed structure |
| **🌐 Horizontal Scaling** | Built-in sharding support |
| **⚡ High Performance** | Indexed queries, in-memory operations |
| **🔄 Rich Queries** | Complex queries, aggregations, text search |

**Mental Model:** Think of MongoDB as a filing cabinet where each document is a folder containing related information.

</div>

---

## 🏗️ Core Concepts

<div align="center">

### MongoDB Architecture

| Component | Description | SQL Equivalent |
|:---:|:---:|:---:|
| **Database** | Container for collections | Database |
| **Collection** | Group of documents | Table |
| **Document** | Single record (BSON) | Row |
| **Field** | Key-value pair in document | Column |
| **Index** | Data structure for fast lookups | Index |
| **Shard** | Horizontal partition | Partition |

### Document Structure

**JSON-like Document:**
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30,
  "address": {
    "street": "123 Main St",
    "city": "New York",
    "zip": "10001"
  },
  "hobbies": ["reading", "coding", "traveling"],
  "created_at": ISODate("2024-01-15T10:30:00Z")
}
```

**Key Features:**
- **Nested documents** - Objects within documents
- **Arrays** - Lists of values
- **Mixed types** - Different data types in same collection

</div>

---

## 📊 Data Modeling

<div align="center">

### Design Patterns

| Pattern | Description | Use Case |
|:---:|:---:|:---:|
| **Embedded** | Store related data in one document | One-to-few relationships |
| **Referenced** | Store references (ObjectIds) | One-to-many, many-to-many |
| **Hybrid** | Combine embedded and referenced | Complex relationships |

### Embedded Pattern

**✅ Good for:** One-to-few, data accessed together

```json
{
  "_id": ObjectId("..."),
  "user_id": 123,
  "name": "John",
  "addresses": [
    {"type": "home", "street": "123 Main St"},
    {"type": "work", "street": "456 Oak Ave"}
  ]
}
```

**Pros:** Single query, atomic updates  
**Cons:** Document size limit (16MB), harder to query nested data

---

### Referenced Pattern

**✅ Good for:** One-to-many, many-to-many, large collections

```json
// User document
{
  "_id": ObjectId("user123"),
  "name": "John",
  "order_ids": [ObjectId("order1"), ObjectId("order2")]
}

// Order document
{
  "_id": ObjectId("order1"),
  "user_id": ObjectId("user123"),
  "total": 100
}
```

**Pros:** No document size limit, easier to query  
**Cons:** Multiple queries, application-level joins

---

### When to Embed vs Reference

| Scenario | Choice | Reason |
|:---:|:---:|:---:|
| **One-to-few** | Embed | Access together, atomic updates |
| **One-to-many** | Reference | Avoid large documents |
| **Many-to-many** | Reference | Complex relationships |
| **Frequently accessed together** | Embed | Reduce queries |
| **Large arrays** | Reference | Avoid document size limit |

</div>

---

## 🔍 Querying MongoDB

<div align="center">

### Basic Queries

**Find Documents:**
```javascript
// Find all users
db.users.find()

// Find with condition
db.users.find({ age: { $gte: 18 } })

// Find one
db.users.findOne({ email: "john@example.com" })
```

**Query Operators:**

| Operator | Description | Example |
|:---:|:---:|:---:|
| **$eq** | Equal | `{ age: { $eq: 30 } }` |
| **$gt, $gte** | Greater than | `{ age: { $gt: 18 } }` |
| **$lt, $lte** | Less than | `{ age: { $lt: 65 } }` |
| **$in** | In array | `{ status: { $in: ["active", "pending"] } }` |
| **$and, $or** | Logical operators | `{ $or: [{age: 30}, {status: "active"}] }` |
| **$exists** | Field exists | `{ email: { $exists: true } }` |
| **$regex** | Pattern matching | `{ name: { $regex: /^John/ } }` |

---

### Aggregation Pipeline

**Powerful data processing:**

```javascript
db.orders.aggregate([
  // Stage 1: Match orders from last month
  { $match: { date: { $gte: lastMonth } } },
  
  // Stage 2: Group by user
  { $group: {
    _id: "$user_id",
    total_spent: { $sum: "$total" },
    order_count: { $sum: 1 }
  }},
  
  // Stage 3: Sort by total spent
  { $sort: { total_spent: -1 } },
  
  // Stage 4: Limit top 10
  { $limit: 10 }
])
```

**Common Aggregation Stages:**

| Stage | Purpose | Example |
|:---:|:---:|:---:|
| **$match** | Filter documents | `{ $match: { status: "active" } }` |
| **$group** | Group and aggregate | `{ $group: { _id: "$category", total: { $sum: "$price" } } }` |
| **$project** | Select fields | `{ $project: { name: 1, email: 1 } }` |
| **$sort** | Sort results | `{ $sort: { created_at: -1 } }` |
| **$limit** | Limit results | `{ $limit: 10 }` |
| **$lookup** | Join collections | `{ $lookup: { from: "users", localField: "user_id", foreignField: "_id", as: "user" } }` |
| **$unwind** | Deconstruct array | `{ $unwind: "$tags" }` |

</div>

---

## ⚡ Indexing Strategies

<div align="center">

### Index Types

| Index Type | Description | Use Case |
|:---:|:---:|:---:|
| **Single Field** | Index on one field | `db.users.createIndex({ email: 1 })` |
| **Compound** | Index on multiple fields | `db.orders.createIndex({ user_id: 1, date: -1 })` |
| **Multikey** | Index on array fields | `db.products.createIndex({ tags: 1 })` |
| **Text** | Full-text search | `db.articles.createIndex({ content: "text" })` |
| **Geospatial** | Location-based queries | `db.places.createIndex({ location: "2dsphere" })` |
| **TTL** | Auto-delete after time | `db.sessions.createIndex({ expires_at: 1 }, { expireAfterSeconds: 3600 })` |
| **Partial** | Index subset of documents | `db.users.createIndex({ email: 1 }, { partialFilterExpression: { active: true } })` |

### Index Best Practices

| Practice | Why |
|:---:|:---:|
| **Index frequently queried fields** | Faster queries |
| **Index fields in sort operations** | Avoid in-memory sorts |
| **Compound indexes: equality first, then range** | Optimal index usage |
| **Use explain() to analyze queries** | Identify missing indexes |
| **Monitor index usage** | Remove unused indexes |

**Index Direction:**
- `1` = Ascending
- `-1` = Descending
- Order matters for compound indexes!

</div>

---

## 🔄 Transactions & Consistency

<div align="center">

### ACID Support

**MongoDB 4.0+ supports multi-document ACID transactions**

```javascript
const session = client.startSession();
try {
  session.startTransaction();
  
  await usersCollection.updateOne(
    { _id: userId },
    { $inc: { balance: -100 } },
    { session }
  );
  
  await ordersCollection.insertOne(
    { user_id: userId, total: 100 },
    { session }
  );
  
  await session.commitTransaction();
} catch (error) {
  await session.abortTransaction();
} finally {
  session.endSession();
}
```

### Consistency Models

| Model | Description | Use Case |
|:---:|:---:|:---:|
| **Strong Consistency** | Read-after-write consistency | Critical operations |
| **Eventual Consistency** | Replica sets, eventual sync | Read replicas |
| **Causal Consistency** | Causal relationships preserved | Related operations |

**⚠️ Trade-off:** Strong consistency vs. performance

</div>

---

## 📈 Scaling MongoDB

<div align="center">

### Replication (Replica Sets)

**High availability and data redundancy**

| Role | Description |
|:---:|:---:|
| **Primary** | Handles all writes |
| **Secondaries** | Read replicas, automatic failover |
| **Arbiter** | Vote-only member (no data) |

**Benefits:**
- ✅ Automatic failover
- ✅ Read scaling
- ✅ Data redundancy

---

### Sharding

**Horizontal scaling across multiple servers**

| Component | Description |
|:---:|:---:|
| **Shard** | Data partition (replica set) |
| **Config Server** | Metadata and routing |
| **Mongos** | Query router |

**Sharding Strategies:**

| Strategy | Description | Best For |
|:---:|:---:|:---:|
| **Range Sharding** | Partition by value range | Sequential data |
| **Hash Sharding** | Partition by hash of shard key | Even distribution |
| **Zoned Sharding** | Custom partition ranges | Geographic data |

**Shard Key Selection:**
- ✅ High cardinality (many unique values)
- ✅ Even distribution
- ✅ Used in most queries
- ❌ Avoid: Monotonic (date, auto-increment)

</div>

---

## 🎯 Use Cases

<div align="center">

### ✅ Ideal Use Cases

| Use Case | Why MongoDB |
|:---:|:---:|
| **Content Management** | Flexible schema for articles, blogs |
| **User Profiles** | Varying user attributes |
| **Product Catalogs** | Different product types |
| **Real-Time Analytics** | Fast aggregations |
| **Mobile Apps** | JSON-native, flexible schema |
| **IoT Data** | Time-series, sensor data |
| **Social Networks** | Complex relationships, feeds |

---

### ❌ When NOT to Use

| Scenario | Better Alternative |
|:---:|:---:|
| **Complex Transactions** | Relational databases |
| **Strict Schema** | SQL databases |
| **Simple Key-Value** | Redis |
| **Graph Relationships** | Neo4j |
| **Heavy Analytics** | Data warehouses |

</div>

---

## 🔐 Security Best Practices

<div align="center">

### Security Measures

| Practice | Description | Implementation |
|:---:|:---:|:---:|
| **Authentication** | User credentials | SCRAM-SHA-256 |
| **Authorization** | Role-based access | RBAC, custom roles |
| **Encryption at Rest** | Encrypt data on disk | WiredTiger encryption |
| **Encryption in Transit** | TLS/SSL | Enable TLS |
| **Network Security** | Firewall rules | Whitelist IPs |
| **Audit Logging** | Track access | Enable audit logs |

### Role-Based Access Control

```javascript
// Create role
db.createRole({
  role: "readWriteUsers",
  privileges: [
    { resource: { db: "app", collection: "users" }, actions: ["find", "insert", "update"] }
  ],
  roles: []
})

// Grant role to user
db.grantRolesToUser("app_user", ["readWriteUsers"])
```

</div>

---

## 💡 Design Patterns & Best Practices

<div align="center">

### ✅ Best Practices

| Practice | Why |
|:---:|:---:|
| **Design for queries** | Optimize for actual access patterns |
| **Use appropriate data types** | ObjectId for references, Date for dates |
| **Index strategically** | Balance query speed vs. write performance |
| **Limit document size** | Stay under 16MB, prefer references for large data |
| **Use aggregation for complex queries** | More efficient than application-level processing |
| **Monitor performance** | Use explain(), profiler, slow query logs |

---

### ❌ Anti-Patterns

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Massive embedded arrays** | Document size limit | Use references |
| **Too many collections** | Overhead | Consolidate related data |
| **Missing indexes** | Slow queries | Index frequently queried fields |
| **Over-indexing** | Slow writes | Index only what's needed |
| **N+1 queries** | Performance bottleneck | Use $lookup or batch queries |
| **Storing files in documents** | Size limit | Use GridFS |

</div>

---

## 🔧 MongoDB Operations

<div align="center">

### CRUD Operations

**Create:**
```javascript
// Insert one
db.users.insertOne({ name: "John", email: "john@example.com" })

// Insert many
db.users.insertMany([
  { name: "John", email: "john@example.com" },
  { name: "Jane", email: "jane@example.com" }
])
```

**Read:**
```javascript
// Find with projection
db.users.find({ age: { $gte: 18 } }, { name: 1, email: 1 })

// Find with pagination
db.users.find().skip(10).limit(10).sort({ created_at: -1 })
```

**Update:**
```javascript
// Update one
db.users.updateOne(
  { email: "john@example.com" },
  { $set: { age: 31 } }
)

// Update many
db.users.updateMany(
  { status: "inactive" },
  { $set: { status: "active" } }
)

// Upsert (insert if not exists)
db.users.updateOne(
  { email: "john@example.com" },
  { $set: { name: "John Doe" } },
  { upsert: true }
)
```

**Delete:**
```javascript
// Delete one
db.users.deleteOne({ email: "john@example.com" })

// Delete many
db.users.deleteMany({ status: "inactive" })
```

</div>

---

## 🎓 Interview Questions

<div align="center">

### Expert-Level Questions

| Question | Key Points |
|:---:|:---:|
| **Design a database for a social media app** | Users, Posts, Comments (embedded vs referenced), Likes, Follows, Timeline generation |
| **How do you handle high write throughput?** | Sharding, write concern, batch inserts, connection pooling |
| **Design a database for an e-commerce site** | Products (varying attributes), Orders, Users, Inventory |
| **How do you ensure data consistency?** | Transactions, write concern, read concern, replica sets |
| **How do you optimize slow queries?** | Explain plan, indexes, aggregation pipeline, query patterns |
| **Design a database for a blog platform** | Articles, Authors, Categories, Tags, Comments (nested) |
| **How do you scale MongoDB?** | Replica sets, sharding, read preferences, connection pooling |

</div>

---

## 🚀 Performance Optimization

<div align="center">

### Query Optimization

| Technique | Description | Impact |
|:---:|:---:|:---:|
| **Use Indexes** | Index frequently queried fields | 10-100x faster |
| **Use Projection** | Select only needed fields | Reduce network transfer |
| **Use Aggregation** | Server-side processing | Faster than app-level |
| **Batch Operations** | Bulk writes | Reduce round trips |
| **Connection Pooling** | Reuse connections | Lower latency |
| **Read Preferences** | Route reads to secondaries | Distribute load |

### Monitoring & Profiling

```javascript
// Enable profiling (slow queries > 100ms)
db.setProfilingLevel(1, { slowms: 100 })

// View profiled queries
db.system.profile.find().sort({ ts: -1 }).limit(5)

// Explain query
db.users.find({ email: "john@example.com" }).explain("executionStats")
```

**Key Metrics:**
- **executionTimeMillis** - Query execution time
- **totalDocsExamined** - Documents scanned
- **totalKeysExamined** - Index keys examined
- **stage** - Query execution stage

</div>

---

## 📚 Advanced Features

<div align="center">

### Advanced Capabilities

| Feature | Description | Use Case |
|:---:|:---:|:---:|
| **Change Streams** | Real-time data changes | Event sourcing, notifications |
| **GridFS** | Store large files | Files > 16MB |
| **Text Search** | Full-text search | Search functionality |
| **Geospatial Queries** | Location-based queries | Nearby places, mapping |
| **Time-Series Collections** | Optimized for time-series | IoT, metrics |
| **Views** | Virtual collections | Simplified queries |

### Change Streams Example

```javascript
const changeStream = db.orders.watch([
  { $match: { "operationType": "insert" } }
]);

changeStream.on("change", (change) => {
  console.log("New order:", change.fullDocument);
});
```

</div>

---

## 🔄 Backup & Recovery

<div align="center">

### Backup Strategies

| Strategy | Description | Tools |
|:---:|:---:|:---:|
| **mongodump** | Logical backup | Native tool |
| **File System Snapshot** | Physical backup | LVM, EBS snapshots |
| **Continuous Backup** | Real-time backup | MongoDB Atlas, Ops Manager |
| **Point-in-Time Recovery** | Restore to timestamp | Oplog replay |

### Recovery Scenarios

| Scenario | Strategy |
|:---:|:---:|
| **Data corruption** | Restore from backup |
| **Accidental deletion** | Oplog replay |
| **Hardware failure** | Restore to new server |
| **Disaster recovery** | Replicate to different region |

</div>

---

## 🎯 MongoDB vs Relational Databases

<div align="center">

### Comparison

| Aspect | MongoDB | SQL Databases |
|:---:|:---:|:---:|
| **Schema** | Flexible, schema-less | Fixed schema |
| **Relationships** | References, embedded | Foreign keys, JOINs |
| **Scaling** | Horizontal (sharding) | Vertical, read replicas |
| **Transactions** | Multi-document (4.0+) | Full ACID support |
| **Queries** | Document queries, aggregation | SQL, JOINs |
| **Best For** | Flexible data, rapid development | Structured data, complex relationships |

**💡 Choose MongoDB when:** You need flexibility, horizontal scaling, and JSON-native storage.

</div>

---

<div align="center">

**Master MongoDB for flexible document storage! 🚀**

*MongoDB excels at handling flexible schemas and horizontal scaling.*

</div>

