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

**MongoDB is the most popular open-source, document-oriented NoSQL database, holding over 45% of the NoSQL market share.**

MongoDB stores data in flexible BSON format (Binary JSON), enabling faster and more efficient storage and retrieval compared to rigid relational databases.

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **📄 Document-Oriented** | Data stored as documents (BSON) |
| **🔓 Schema-Less** | Flexible schema, no fixed structure |
| **🌐 Horizontal Scaling** | Built-in sharding support |
| **⚡ High Performance** | Indexed queries, in-memory operations |
| **🔄 Rich Queries** | Complex queries, aggregations, text search |

**Mental Model:** Think of MongoDB as a filing cabinet where each document is a folder containing related information.

**💡 Why MongoDB Exists:**
- Modern applications (social, interactive, data-heavy) require faster, larger data access
- RDBMS limitations: Not horizontally scalable, single-server deployments hit scaling limits
- NoSQL databases: More scalable and higher performing for big data workloads

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

---

### BSON (Binary JSON)

**BSON is MongoDB's internal storage format**

| Aspect | Description |
|:---:|:---:|
| **Format** | Binary-encoded serialization of JSON |
| **Purpose** | Efficient storage and traversal |
| **Advantages** | Faster than text JSON, supports more data types |
| **Storage Engine** | WiredTiger (default) stores collections as files on disk |

**BSON Extends JSON:**
- ✅ Supports dates, binary data, ObjectId
- ✅ More efficient storage space
- ✅ Faster scan speed
- ✅ Type preservation

**Supported Data Types:**
- String, Number (int, long, double, Decimal128)
- Boolean, Date, Array, Object/Embedded Document
- ObjectId, Null, Binary Data
- Regular Expression, Timestamp, Code/JavaScript

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
| **Hashed** | Hash-based index | Sharding, even distribution |

**TTL Index Example:**
```javascript
// Remove documents 1 hour after createdAt
db.sessions.createIndex({ "createdAt": 1 }, { expireAfterSeconds: 3600 })
```

**Geospatial Index Types:**
- **2d** - Flat geometries (legacy)
- **2dsphere** - Spherical geometries (recommended)

**Example:**
```javascript
db.places.createIndex({ location: "2dsphere" })
db.places.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [-73.97, 40.77] },
      $maxDistance: 5000
    }
  }
})
```

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

### Write Concern

**Write Concern = Level of acknowledgment for write operations**

| Level | Description | Use Case |
|:---:|:---:|:---:|
| **acknowledged** | Default, primary confirms | General writes |
| **unacknowledged** | No acknowledgment | Fire-and-forget |
| **journaled** | Written to journal | Durability required |
| **majority** | Majority of replica set | High durability |
| **w: N** | N nodes must confirm | Custom durability |

**Example:**
```javascript
db.orders.insertOne(
  { user_id: 123, total: 100 },
  { writeConcern: { w: "majority", wtimeout: 5000 } }
)
```

**💡 Trade-off:** Higher write concern = Better durability but higher latency

### Consistency Models

| Model | Description | Use Case |
|:---:|:---:|:---:|
| **Strong Consistency** | Read-after-write consistency | Critical operations |
| **Eventual Consistency** | Replica sets, eventual sync | Read replicas |
| **Causal Consistency** | Causal relationships preserved | Related operations |

**⚠️ Trade-off:** Strong consistency vs. performance

### Journaling

**Write-Ahead Logging for Data Durability**

| Aspect | Description |
|:---:|:---:|
| **Purpose** | Crash recovery, data integrity |
| **How** | Records changes to journal before applying to data files |
| **Recovery** | Replay journal after crash |
| **Impact** | Additional I/O operations, slight performance overhead |

**💡 Insight:** Journaling ensures data durability but can impact performance due to additional I/O.

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

**How It Works:**
- Primary receives all write operations
- Secondaries replicate primary's data
- Automatic election if primary fails
- Read operations can be served by secondaries

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

**Hashed Sharding Keys:**

**Use Case:** Fields with monotonically increasing values (timestamps, IDs)

**Example:**
```javascript
db.collection.createIndex({ _id: "hashed" });
sh.shardCollection("mydb.mycollection", { _id: "hashed" });
```

**Benefits:**
- ✅ Even data distribution
- ✅ Avoids hot shards
- ✅ Better for sequential values

**Shard Key Selection:**
- ✅ High cardinality (many unique values)
- ✅ Even distribution
- ✅ Used in most queries
- ❌ Avoid: Monotonic (date, auto-increment)

**💡 Horizontal Scalability:** MongoDB achieves horizontal scalability through sharding, where data is partitioned across multiple shards (replica sets), allowing the system to handle large datasets and high-throughput operations.

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

**Enable Authentication:**
```javascript
// Start MongoDB with --auth or set in config
security:
  authorization: enabled
```

**Create User:**
```javascript
db.createUser({
  user: "admin",
  pwd: "password",
  roles: [{ role: "userAdminAnyDatabase", db: "admin" }]
});
```

**Create Role:**
```javascript
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

// Find one
db.users.findOne({ email: "john@example.com" })
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

---

### Advanced Query Examples

**Find employees in Engineering department:**
```javascript
db.employees.find({ department: "Engineering" })
```

**Find highest salary:**
```javascript
db.employees.find().sort({ salary: -1 }).limit(1)
```

**Count by department:**
```javascript
db.employees.aggregate([
  { $group: { _id: "$department", count: { $sum: 1 } } }
])
```

**Average salary by department:**
```javascript
db.employees.aggregate([
  { $group: { 
    _id: "$department", 
    averageSalary: { $avg: "$salary" } 
  } },
  { $sort: { averageSalary: -1 } }
])
```

</div>

---

## 🎓 Interview Questions

<div align="center">

### Expert-Level Questions

| Question | Key Points |
|:---:|:---:|
| **How does MongoDB differ from relational databases?** | Document model, schema flexibility, relationships (embedding/referencing), horizontal scaling, query language |
| **Explain document and collection** | Document = JSON-like object (BSON), Collection = group of documents (like table) |
| **How does MongoDB store data internally?** | BSON format, WiredTiger storage engine, files on disk |
| **What is the role of _id?** | Unique identifier, default primary key, helps indexing |
| **Explain replica sets** | Primary + secondaries, automatic failover, read scaling |
| **What is sharding?** | Distribute data across servers, horizontal scaling, automatic balancing |
| **Design a database for a social media app** | Users, Posts, Comments (embedded vs referenced), Likes, Follows, Timeline generation |
| **How do you handle high write throughput?** | Sharding, write concern, batch inserts, connection pooling |
| **Design a database for an e-commerce site** | Products (varying attributes), Orders, Users, Inventory |
| **How do you ensure data consistency?** | Transactions, write concern, read concern, replica sets, journaling |
| **How do you optimize slow queries?** | Explain plan, indexes, aggregation pipeline, query patterns, projections |
| **How do you scale MongoDB?** | Replica sets, sharding, read preferences, connection pooling |
| **What are aggregation pipelines?** | Multi-stage data processing, $match, $group, $sort stages |
| **Explain write concern** | Level of acknowledgment, durability vs performance trade-off |
| **What are TTL indexes?** | Auto-delete documents after time, session data, logs |
| **What is GridFS?** | Store large files, splits into chunks, files > 16MB |
| **How do you handle transactions?** | Multi-document ACID transactions, sessions, commit/abort |
| **What are Change Streams?** | Real-time change notifications, event-driven architectures |
| **How do you implement full-text search?** | Text indexes, $text operator, relevance scoring |
| **How do you monitor performance?** | Profiling, explain(), index analysis, resource monitoring |

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
| **Index Hints** | Force specific index | Optimize query plans |
| **Query Analysis** | Use explain() method | Identify bottlenecks |

### Monitoring & Profiling

**Enable Profiling:**
```javascript
// Profile slow queries (> 100ms)
db.setProfilingLevel(1, { slowms: 100 })

// View profiled queries
db.system.profile.find().sort({ ts: -1 }).limit(5)
```

**Explain Query:**
```javascript
db.users.find({ email: "john@example.com" }).explain("executionStats")
```

**Key Metrics:**
- **executionTimeMillis** - Query execution time
- **totalDocsExamined** - Documents scanned
- **totalKeysExamined** - Index keys examined
- **stage** - Query execution stage

**Optimization Strategies:**
- ✅ Create indexes for query patterns
- ✅ Use projections to limit fields
- ✅ Optimize aggregation pipeline stages
- ✅ Analyze query execution plans
- ✅ Review and optimize indexes

### Troubleshooting Performance

| Issue | Diagnosis | Solution |
|:---:|:---:|:---:|
| **Slow Queries** | Check explain() plan | Add indexes |
| **High CPU** | Monitor resource usage | Optimize queries, scale |
| **Memory Pressure** | Check working set | Add RAM, optimize indexes |
| **Disk I/O** | Monitor disk usage | Add indexes, optimize queries |

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
| **Capped Collections** | Fixed-size collections | Logging, caching |
| **Map-Reduce** | Complex aggregations | Data processing |

### Change Streams

**Listen for real-time changes to collections, databases, or clusters**

```javascript
const changeStream = db.orders.watch([
  { $match: { "operationType": "insert" } }
]);

changeStream.on("change", (change) => {
  console.log("New order:", change.fullDocument);
});
```

**Operations Captured:**
- ✅ Insert
- ✅ Update
- ✅ Replace
- ✅ Delete

**Use Cases:**
- Event-driven architectures
- Real-time notifications
- Cache invalidation
- Audit logging

---

### GridFS

**Store and retrieve large files (> 16MB)**

**How It Works:**
- Splits large files into chunks (255KB default)
- Stores chunks in `fs.chunks` collection
- Stores metadata in `fs.files` collection

**Example:**
```javascript
// Store file
const bucket = new GridFSBucket(db, { bucketName: 'files' });
fs.createReadStream('large-video.mp4')
  .pipe(bucket.openUploadStream('large-video.mp4'));

// Retrieve file
bucket.openDownloadStreamByName('large-video.mp4')
  .pipe(fs.createWriteStream('output.mp4'));
```

**Use Cases:**
- Videos, images, large datasets
- Efficient retrieval of file sections
- Files exceeding 16MB BSON limit

---

### Capped Collections

**Fixed-size collections that automatically overwrite oldest documents**

```javascript
db.createCollection("logs", { 
  capped: true, 
  size: 100000,  // Size in bytes
  max: 1000      // Max documents (optional)
});
```

**Characteristics:**
- ✅ Maintains insertion order
- ✅ Automatic oldest document removal
- ✅ High-performance inserts
- ✅ No updates that increase document size

**Use Cases:**
- Logging
- Caching recent data
- Monitoring data
- Recent activity feeds

---

### Full-Text Search

**Text indexes for searching string content**

```javascript
// Create text index
db.articles.createIndex({ content: "text", title: "text" });

// Search
db.articles.find({ 
  $text: { $search: "mongodb database" } 
});

// With relevance score
db.articles.find(
  { $text: { $search: "mongodb" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } });
```

**Features:**
- ✅ Multiple fields in one index
- ✅ Relevance scoring
- ✅ Language-specific stemming
- ✅ Case-insensitive search

---

### Map-Reduce

**Complex data aggregation paradigm**

**Two Phases:**
1. **Map** - Process each document, emit key-value pairs
2. **Reduce** - Process all values for each key, output result

**Example:**
```javascript
db.orders.mapReduce(
  // Map function
  function() {
    emit(this.category, this.price);
  },
  // Reduce function
  function(key, values) {
    return Array.sum(values);
  },
  // Options
  { out: "category_totals" }
);
```

**💡 Note:** Aggregation pipeline is preferred over Map-Reduce for most use cases (simpler, more efficient).

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

### Data Import/Export

**Import:**
```bash
mongoimport --db mydatabase --collection mycollection --file data.json
```

**Export:**
```bash
mongoexport --db mydatabase --collection mycollection --out data.json
```

**Formats Supported:**
- JSON
- CSV
- TSV

### Recovery Scenarios

| Scenario | Strategy |
|:---:|:---:|
| **Data corruption** | Restore from backup |
| **Accidental deletion** | Oplog replay |
| **Hardware failure** | Restore to new server |
| **Disaster recovery** | Replicate to different region |

**Best Practices:**
- ✅ Regular automated backups
- ✅ Test restore procedures
- ✅ Multiple backup locations
- ✅ Monitor backup success

</div>

---

## 🎯 MongoDB vs Relational Databases

<div align="center">

### Detailed Comparison

| Aspect | MongoDB | SQL Databases |
|:---:|:---:|:---:|
| **Data Model** | Document-oriented (JSON/BSON) | Table-based (rows/columns) |
| **Schema** | Flexible, schema-less | Fixed schema, defined upfront |
| **Relationships** | Embedding or referencing (no JOINs) | Foreign keys and JOINs |
| **Scalability** | Horizontal (sharding) | Vertical, horizontal is complex |
| **Transactions** | Multi-document (4.0+) | Full ACID support |
| **Queries** | Rich query language for documents | SQL for structured queries |
| **Best For** | Flexible data, rapid development | Structured data, complex relationships |

**Key Differences:**

**Data Model:**
- MongoDB: Documents with nested structures
- SQL: Tables with fixed columns

**Schema:**
- MongoDB: Documents can have different structures
- SQL: All rows follow same structure

**Relationships:**
- MongoDB: Embedding or references, no JOINs
- SQL: Foreign keys and JOINs

**Scalability:**
- MongoDB: Horizontal via sharding
- SQL: Vertical scaling, complex horizontal scaling

**💡 Choose MongoDB when:** You need flexibility, horizontal scaling, and JSON-native storage.

</div>

---

## 🏢 MongoDB Storage Engines

<div align="center">

### WiredTiger vs MMAPv1

| Feature | WiredTiger | MMAPv1 |
|:---:|:---:|:---:|
| **Concurrency** | Document-level concurrency | Collection-level concurrency |
| **Compression** | ✅ Supports data compression | ❌ No compression |
| **Performance** | Better for most workloads | Limited performance |
| **Journaling** | Write-ahead logging | Basic journaling |
| **Status** | Modern, default engine | Legacy, deprecated |

**WiredTiger (Default):**
- ✅ Document-level locking (better concurrency)
- ✅ Data compression (reduces storage)
- ✅ Better performance
- ✅ Advanced journaling

**💡 Recommendation:** Always use WiredTiger (default since MongoDB 3.2)

</div>

---

## 🛠️ MongoDB Tools

<div align="center">

### MongoDB Compass

**Graphical user interface (GUI) for MongoDB**

| Feature | Description |
|:---:|:---:|
| **Schema Visualization** | View data schema, field types, distributions |
| **Query Building** | Visual query interface |
| **Aggregation Pipeline** | Construct and run aggregations |
| **Index Management** | Create and manage indexes |
| **Performance Monitoring** | Monitor slow queries, resource utilization |
| **Data Validation** | Define schema validation rules |
| **Import/Export** | Import/export JSON/CSV files |

**Use Cases:**
- ✅ Data exploration
- ✅ Query development
- ✅ Index optimization
- ✅ Performance analysis

---

### MongoDB Atlas

**Fully managed cloud database service**

| Feature | Description |
|:---:|:---:|
| **Managed Service** | Infrastructure, backups, monitoring, upgrades |
| **Scalability** | Easy cluster scaling up/down |
| **Security** | Encryption, access controls, compliance |
| **Global Distribution** | Multi-region deployment |
| **Integrations** | Cloud service integrations |

**vs Self-Hosted:**

| Aspect | Atlas | Self-Hosted |
|:---:|:---:|:---:|
| **Management** | Fully managed | Manual |
| **Scaling** | Easy scaling | Manual scaling |
| **Backups** | Automated | Manual setup |
| **Monitoring** | Built-in | Third-party tools |
| **Cost** | Higher | Lower (but more ops) |

**💡 Choose Atlas when:** You want managed service, less operational overhead.

</div>

---

## 🚀 Production Deployment

<div align="center">

### Key Considerations

| Consideration | Description | Implementation |
|:---:|:---:|:---:|
| **Replication** | High availability | Replica sets |
| **Sharding** | Horizontal scaling | Shard clusters |
| **Backup & Recovery** | Data protection | Automated backups |
| **Security** | Authentication, encryption | RBAC, TLS |
| **Monitoring** | Performance tracking | Ops Manager, Cloud Manager |
| **Capacity Planning** | Resource allocation | Storage, memory, CPU |
| **Maintenance** | Updates, optimization | Regular maintenance |

**Production Checklist:**
- ✅ Replica sets configured
- ✅ Sharding implemented (if needed)
- ✅ Backup strategy in place
- ✅ Security enabled (auth, TLS)
- ✅ Monitoring configured
- ✅ Capacity planned
- ✅ Maintenance scheduled

</div>

---

## 🔄 Migration from Relational Database

<div align="center">

### Migration Process

| Step | Description | Details |
|:---:|:---:|:---:|
| **1. Schema Design** | Redesign for document model | Embedding vs referencing |
| **2. Data Export** | Export from SQL database | CSV, JSON format |
| **3. Data Transformation** | Transform to MongoDB schema | Restructure documents |
| **4. Data Import** | Import to MongoDB | mongoimport or scripts |
| **5. Validation** | Verify data consistency | Compare counts, validate |
| **6. Application Changes** | Update application code | MongoDB drivers |
| **7. Testing** | Thorough testing | Functionality, performance |
| **8. Go Live** | Deploy to production | Monitor transition |

**Key Challenges:**
- Schema redesign (normalized → denormalized)
- Relationship handling (JOINs → embedding/references)
- Data type conversions
- Application code changes

</div>

---

<div align="center">

**Master MongoDB for flexible document storage! 🚀**

*MongoDB excels at handling flexible schemas and horizontal scaling.*

</div>

