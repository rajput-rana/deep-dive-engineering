# 🚀 DynamoDB - NoSQL Database

<div align="center">

**Managed NoSQL database: fast, scalable, serverless**

[![DynamoDB](https://img.shields.io/badge/DynamoDB-NoSQL-blue?style=for-the-badge)](./)
[![Serverless](https://img.shields.io/badge/Serverless-Managed-green?style=for-the-badge)](./)
[![Performance](https://img.shields.io/badge/Performance-Single%20Digit%20ms-orange?style=for-the-badge)](./)

*Master DynamoDB: tables, items, streams, and scalable NoSQL database design*

</div>

---

## 🎯 What is DynamoDB?

<div align="center">

**DynamoDB is a fully managed NoSQL database service providing fast, predictable performance with seamless scalability.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **📊 Table** | Collection of items |
| **📄 Item** | Collection of attributes |
| **🔑 Primary Key** | Partition key or partition + sort key |
| **⚡ Streams** | Change data capture |
| **🌍 Global Tables** | Multi-region replication |
| **💰 On-Demand** | Pay per request |

**Mental Model:** Think of DynamoDB like a super-fast, infinitely scalable spreadsheet - you can store and retrieve data in milliseconds, and it automatically scales to handle any amount of traffic.

</div>

---

## 🏗️ Data Model

<div align="center">

### Table Structure

```
Table: Users
├── Item 1
│   ├── Partition Key: user_id = "123"
│   ├── Sort Key: timestamp = "2024-01-01"
│   ├── name = "John"
│   └── email = "john@example.com"
└── Item 2
    ├── Partition Key: user_id = "456"
    └── ...
```

---

### Primary Key Types

| Type | Description | Use Case |
|:---:|:---:|:---:|
| **Partition Key Only** | Simple key | User ID, Product ID |
| **Partition + Sort Key** | Composite key | User ID + Timestamp |

**Example:**
```
Partition Key: user_id
Sort Key: order_date
→ Query all orders for a user, sorted by date
```

</div>

---

## ⚡ Performance

<div align="center">

### Performance Characteristics

| Metric | Value |
|:---:|:---:|
| **Latency** | Single-digit milliseconds |
| **Throughput** | Millions of requests/second |
| **Scalability** | Automatic, unlimited |
| **Consistency** | Eventually consistent or strongly consistent |

---

### Capacity Modes

| Mode | Description | Use Case |
|:---:|:---:|:---:|
| **Provisioned** | Set read/write capacity | Predictable workloads |
| **On-Demand** | Pay per request | Variable workloads |

---

### Read Consistency

| Type | Description | Cost |
|:---:|:---:|:---:|
| **Eventually Consistent** | Default, may see stale data | 1 read capacity unit |
| **Strongly Consistent** | Always latest data | 2 read capacity units |

</div>

---

## 🔄 DynamoDB Streams

<div align="center">

### What are Streams?

**Time-ordered sequence of item changes**

| Use Case | Description |
|:---:|:---:|
| **Change Data Capture** | Track all changes |
| **Event-Driven Architecture** | Trigger Lambda functions |
| **Replication** | Sync to other systems |
| **Analytics** | Real-time analytics |

---

### Stream Record Types

| Type | Description |
|:---:|:---:|
| **INSERT** | New item created |
| **MODIFY** | Item updated |
| **REMOVE** | Item deleted |

**💡 Enable streams for event-driven architectures.**

</div>

---

## 🌍 Global Tables

<div align="center">

### Multi-Region Replication

**Automatically replicate tables across regions**

| Benefit | Description |
|:---:|:---:|
| **Global Performance** | Low latency worldwide |
| **Disaster Recovery** | Automatic failover |
| **High Availability** | Multi-region redundancy |

---

### How It Works

```
Region 1 (us-east-1) ←→ Region 2 (eu-west-1)
     ↓                        ↓
  Writes              Automatic Replication
```

**💡 Eventually consistent across regions.**

</div>

---

## 💰 Pricing

<div align="center">

### Pricing Model

| Component | Description | Cost |
|:---:|:---:|:---:|
| **Storage** | Per GB/month | $0.25/GB |
| **Provisioned Capacity** | Read/Write units | $0.00013 per RCU |
| **On-Demand** | Pay per request | $1.25 per million writes |

---

### Cost Optimization

| Strategy | Savings |
|:---:|:---:|
| **On-Demand for variable** | Pay only for usage |
| **Provisioned for steady** | Lower cost |
| **DAX for caching** | Reduce read costs |
| **TTL for cleanup** | Reduce storage |

</div>

---

## 🎯 Data Modeling

<div align="center">

### Design Principles

| Principle | Description |
|:---:|:---:|
| **Access Patterns First** | Design for queries |
| **Single Table Design** | Store related data together |
| **Denormalization** | Duplicate data for performance |
| **GSI for Queries** | Global Secondary Indexes |

---

### Common Patterns

| Pattern | Description |
|:---:|:---:|
| **One-to-Many** | Partition key + sort key |
| **Many-to-Many** | Adjacency list pattern |
| **Time-Series** | Partition by time, sort by timestamp |

</div>

---

## 🔍 Querying

<div align="center">

### Query Operations

| Operation | Description | Use Case |
|:---:|:---:|:---:|
| **GetItem** | Get single item | By primary key |
| **Query** | Query by partition key | With optional sort key filter |
| **Scan** | Scan entire table | Avoid if possible |
| **BatchGetItem** | Get multiple items | Efficient bulk reads |

---

### Global Secondary Index (GSI)

**Alternative access pattern**

| Benefit | Description |
|:---:|:---:|
| **Different Partition Key** | Query by different attribute |
| **Query Performance** | Fast queries |
| **Cost** | Additional storage and capacity |

**Example:**
```
Table: Users (partition: user_id)
GSI: EmailIndex (partition: email)
→ Query users by email
```

</div>

---

## 🎯 Use Cases

<div align="center">

### When to Use DynamoDB

| Use Case | Description |
|:---:|:---:|
| **High-Traffic Applications** | Millions of requests/second |
| **Serverless Applications** | Lambda integration |
| **Real-Time Applications** | Low latency required |
| **Gaming** | Leaderboards, user data |
| **IoT** | Device data, telemetry |

### When NOT to Use DynamoDB

| Scenario | Alternative |
|:---:|:---:|
| **Complex queries** | RDS, DocumentDB |
| **Analytics** | Redshift, Athena |
| **Small scale** | RDS may be cheaper |
| **ACID transactions** | RDS |

</div>

---

## 💡 Best Practices

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Design for access patterns** | Performance |
| **Use composite keys** | Flexible queries |
| **Enable streams** | Event-driven architecture |
| **Use TTL** | Automatic cleanup |
| **Monitor metrics** | CloudWatch |
| **Use on-demand for variable** | Cost optimization |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Scan operations** | Slow, expensive | Use Query |
| **Hot partitions** | Throttling | Better key design |
| **Over-provisioning** | Wasted cost | Right-size capacity |
| **No indexes** | Slow queries | Use GSI |

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **DynamoDB Purpose** | Fast, scalable NoSQL database |
| **Performance** | Single-digit millisecond latency |
| **Capacity Modes** | Provisioned or on-demand |
| **Streams** | Change data capture |
| **Design** | Access patterns first |

**💡 Remember:** DynamoDB excels at high-scale, low-latency applications. Design for your access patterns, not relational database patterns.

</div>

---

<div align="center">

**Master DynamoDB for scalable NoSQL! 🚀**

*Build fast, scalable applications with DynamoDB - serverless, managed, and performant.*

</div>

