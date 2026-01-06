# 🔀 Database Sharding

<div align="center">

**Partition databases horizontally across multiple machines**

[![Sharding](https://img.shields.io/badge/Sharding-Horizontal-blue?style=for-the-badge)](./)
[![Scaling](https://img.shields.io/badge/Scaling-Distributed-green?style=for-the-badge)](./)
[![Performance](https://img.shields.io/badge/Performance-Optimized-orange?style=for-the-badge)](./)

*Master database sharding strategies, shard key selection, and horizontal scaling patterns*

</div>

---

## 🎯 What is Sharding?

<div align="center">

**Sharding partitions a database into smaller, independent pieces (shards) distributed across multiple servers. When a single database can't handle the load, sharding enables horizontal scaling.**

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **🔀 Horizontal Partitioning** | Data split across multiple databases |
| **📊 Independent Shards** | Each shard operates independently |
| **⚡ Distributed Load** | Workload spread across servers |
| **🌐 Scalability** | Add more shards to scale |
| **🛡️ Fault Isolation** | One shard failure doesn't affect others |

**Mental Model:** Think of sharding as dividing a large library into multiple smaller libraries, each containing a subset of books, making it easier to manage and access.

</div>

---

## 🏗️ Sharding Architecture

<div align="center">

### Architecture Pattern

```
┌─────────┐
│   App   │
└────┬────┘
     │
     ▼
┌──────────────┐
│Shard Router  │  ← Routes queries to correct shard
└──────┬───────┘
       │
   ┌───┴───┬────┬────┐
   │       │    │    │
   ▼       ▼    ▼    ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐
│Sh1 │ │Sh2 │ │Sh3 │ │Sh4 │  ← Each shard is independent
└────┘ └────┘ └────┘ └────┘
```

### Components

| Component | Role | Description |
|:---:|:---:|:---:|
| **Application** | Client | Makes database requests |
| **Shard Router** | Coordinator | Routes queries to correct shard |
| **Shards** | Data Storage | Independent databases with subset of data |
| **Config Server** | Metadata | Stores shard mapping (optional) |

</div>

---

## 📊 Sharding Strategies

<div align="center">

### 1. Range-Based Sharding

**Partition data by value ranges**

```
Shard 1: User IDs 1-1M
Shard 2: User IDs 1M-2M
Shard 3: User IDs 2M-3M
```

| Aspect | Description |
|:---:|:---:|
| **How It Works** | Assign ranges of values to shards |
| **Pros** | Simple to implement, easy range queries |
| **Cons** | Can cause hotspots, uneven distribution |
| **Use Case** | Sequential data, time-based data |

**Example:**
```sql
-- Shard 1 handles users 1-1,000,000
SELECT * FROM users WHERE user_id BETWEEN 1 AND 1000000;

-- Shard 2 handles users 1,000,001-2,000,000
SELECT * FROM users WHERE user_id BETWEEN 1000001 AND 2000000;
```

**⚠️ Challenge:** Hotspots if data is not evenly distributed across ranges.

---

### 2. Hash-Based Sharding

**Partition data using hash function**

```
Shard = hash(user_id) % num_shards
```

| Aspect | Description |
|:---:|:---:|
| **How It Works** | Hash shard key, modulo number of shards |
| **Pros** | Even distribution, no hotspots |
| **Cons** | Hard to add/remove shards, no range queries |
| **Use Case** | Even distribution needed, no range queries |

**Example:**
```python
def get_shard(user_id, num_shards):
    shard_id = hash(user_id) % num_shards
    return f"shard_{shard_id}"
```

**💡 Improvement:** Use consistent hashing to minimize data movement when adding/removing shards.

---

### 3. Directory-Based Sharding

**Use lookup table to map keys to shards**

```
Lookup table: user_id → shard_id
```

| Aspect | Description |
|:---:|:---:|
| **How It Works** | Maintain lookup table mapping keys to shards |
| **Pros** | Flexible, easy rebalancing |
| **Cons** | Lookup table becomes bottleneck, single point of failure |
| **Use Case** | Dynamic sharding, frequent rebalancing |

**Example:**
```python
# Lookup table
shard_mapping = {
    "user_123": "shard_1",
    "user_456": "shard_2",
    "user_789": "shard_1"
}

def get_shard(user_id):
    return shard_mapping[user_id]
```

**💡 Optimization:** Cache lookup table, use distributed cache for high availability.

---

### 4. Geographic Sharding

**Partition data by geographic location**

```
US users → Shard 1
EU users → Shard 2
Asia users → Shard 3
```

| Aspect | Description |
|:---:|:---:|
| **How It Works** | Assign shards based on geographic region |
| **Pros** | Low latency (data closer to users), data locality |
| **Cons** | Uneven distribution possible, cross-region queries |
| **Use Case** | Global applications, location-based services |

**Example:**
```python
def get_shard(user_location):
    if user_location in ["US", "CA", "MX"]:
        return "shard_us"
    elif user_location in ["UK", "DE", "FR"]:
        return "shard_eu"
    else:
        return "shard_asia"
```

**Real-World:** Uber shards by city/region for location-based queries.

</div>

---

## 🎯 Why Sharding Matters

<div align="center">

### Key Benefits

| Benefit | Description | Impact |
|:---:|:---:|:---:|
| **📈 Scalability** | Single database hits limits (connection pool, I/O, storage) | Distribute load across servers |
| **⚡ Performance** | Smaller databases = faster queries, better indexing | Improved query performance |
| **💰 Cost** | Use commodity hardware instead of expensive vertical scaling | Lower infrastructure costs |
| **🛡️ Fault Isolation** | One shard failure doesn't affect others | Better availability |
| **🌐 Geographic Distribution** | Data closer to users | Lower latency |

### When Single Database Fails

**Limitations:**
- ❌ Connection pool exhaustion
- ❌ I/O bottlenecks
- ❌ Storage limits
- ❌ CPU/memory constraints
- ❌ Single point of failure

**Solution:** Sharding distributes load and eliminates single point of failure.

</div>

---

## 🌍 Real-World Examples

<div align="center">

### Industry Implementations

| Company | Sharding Strategy | Details |
|:---:|:---:|:---:|
| **Instagram** | User ID sharding | Each shard handles millions of users |
| **Uber** | Geographic sharding | Sharded by city/region for location-based queries |
| **Facebook** | Hash-based sharding | User ID hash, handles billions of users |
| **MongoDB** | Automatic sharding | Built-in sharding support with automatic balancing |
| **Amazon** | Multi-dimensional | Customer ID, product ID, geographic region |

**Key Learnings:**
- Choose shard key based on access patterns
- Consider geographic distribution for global apps
- Use hash-based for even distribution
- Implement automatic rebalancing

</div>

---

## ⚖️ Trade-offs

<div align="center">

### ✅ Advantages

| Advantage | Description |
|:---:|:---:|
| **Horizontal Scaling** | Add more shards to scale, not limited by single server |
| **Better Performance** | Smaller datasets per shard = faster queries |
| **Fault Isolation** | One shard failure doesn't bring down entire system |
| **Cost-Effective** | Use commodity hardware instead of expensive vertical scaling |
| **Geographic Distribution** | Data closer to users reduces latency |

### ❌ Disadvantages

| Disadvantage | Description |
|:---:|:---:|
| **Complex Implementation** | Requires careful design and operational overhead |
| **Cross-Shard Queries** | Expensive or impossible, requires application-level joins |
| **Rebalancing Difficulty** | Adding/removing shards requires data migration |
| **Operational Complexity** | More servers to manage, monitor, and maintain |
| **Transaction Complexity** | ACID transactions across shards are complex |

</div>

---

## 🚧 Challenges & Solutions

<div align="center">

### 1. Cross-Shard Queries

**Problem:** Joins across shards are expensive or impossible.

**Solutions:**

- **Denormalize Data:** Duplicate data across shards to avoid joins
- **Application-Level Joins:** Fetch from multiple shards, join in application
- **Avoid Cross-Shard Queries:** Design schema to minimize cross-shard operations
- **Read Replicas:** Use replicas for cross-shard reads

**Example:**
```python
# Instead of cross-shard join
# Fetch user from shard_1
user = get_from_shard(user_id, "shard_1")

# Fetch orders from shard_2
orders = get_from_shard(user_id, "shard_2")

# Join in application
user_with_orders = {**user, "orders": orders}
```

---

### 2. Rebalancing

**Problem:** Adding/removing shards requires data migration.

**Solutions:**

- **Consistent Hashing:** Minimal data movement when adding/removing shards
- **Gradual Migration:** Move data incrementally, not all at once
- **Double-Write During Migration:** Write to both old and new shards
- **Automated Rebalancing:** Use tools like MongoDB's automatic balancer

**Migration Strategy:**
```
1. Add new shard
2. Start double-writing to old and new shards
3. Gradually migrate data
4. Update routing logic
5. Stop writing to old shard
6. Complete migration
```

---

### 3. Hotspots

**Problem:** Uneven distribution causes some shards to be overloaded.

**Solutions:**

- **Better Shard Key Selection:** Choose keys with high cardinality and even distribution
- **Monitor and Rebalance:** Track shard sizes and query distribution
- **Sub-Sharding:** Shard within shard for hot data
- **Dynamic Rebalancing:** Automatically move data from hot shards

**Example:**
```python
# Bad: Status field (few values)
shard = hash(status) % num_shards  # Only 3-4 shards used

# Good: User ID (many unique values)
shard = hash(user_id) % num_shards  # Even distribution
```

---

### 4. Transactions

**Problem:** ACID transactions across shards are complex.

**Solutions:**

- **Two-Phase Commit:** Slow and complex, but provides ACID guarantees
- **Saga Pattern:** Eventual consistency, better performance
- **Design to Avoid:** Structure data to minimize cross-shard transactions
- **Compensating Transactions:** Rollback via compensating actions

**Saga Pattern Example:**
```
1. Start transaction on Shard 1
2. Start transaction on Shard 2
3. If Shard 2 fails, compensate Shard 1
4. Eventually consistent across shards
```

</div>

---

## 🔑 Shard Key Selection

<div align="center">

### Good Shard Keys

| Characteristic | Description | Example |
|:---:|:---:|:---:|
| **High Cardinality** | Many unique values | User ID, Order ID |
| **Even Distribution** | Values spread evenly | Hash of user ID |
| **Used in Queries** | Enables single-shard queries | User ID for user queries |
| **Stable** | Doesn't change frequently | User ID (rarely changes) |
| **Query Pattern Match** | Aligns with access patterns | Geographic region for location queries |

**Examples:**
- ✅ User ID (high cardinality, even distribution)
- ✅ Geographic region (good for location-based apps)
- ✅ Customer ID (stable, used in queries)

---

### Bad Shard Keys

| Characteristic | Description | Example |
|:---:|:---:|:---:|
| **Low Cardinality** | Few unique values | Status field (active/inactive) |
| **Skewed Distribution** | Values cluster together | Timestamp (creates hotspots) |
| **Frequently Changing** | Values change often | Last login time |
| **Not Used in Queries** | Requires cross-shard queries | Random UUID not in WHERE clause |

**Examples:**
- ❌ Status field (bad - only 2-3 values)
- ❌ Timestamp (bad - creates hotspots, sequential)
- ❌ Email domain (bad - skewed distribution)

---

### Shard Key Selection Checklist

- [ ] High cardinality (many unique values)
- [ ] Even distribution across shards
- [ ] Used in WHERE clauses (enables single-shard queries)
- [ ] Stable (doesn't change frequently)
- [ ] Aligns with access patterns
- [ ] Avoids hotspots

</div>

---

## 🎨 Design Considerations

<div align="center">

### When to Shard

| Scenario | Indicator | Action |
|:---:|:---:|:---:|
| **Load Capacity** | Single database can't handle load | Consider sharding |
| **Storage Limits** | Database size approaching limits | Plan sharding |
| **Read Replicas Insufficient** | Read replicas not solving write bottleneck | Implement sharding |
| **Geographic Distribution** | Need data closer to users | Geographic sharding |
| **Cost Optimization** | Vertical scaling too expensive | Horizontal scaling via sharding |

**Decision Flow:**
```
1. Optimize database (indexes, queries)
2. Add read replicas
3. Implement caching
4. Consider vertical scaling
5. If still insufficient → Shard
```

---

### Alternatives to Consider First

| Alternative | Description | When to Use |
|:---:|:---:|:---:|
| **Read Replicas** | Scale reads, not writes | Read-heavy workloads |
| **Caching** | Reduce database load | Frequently accessed data |
| **Vertical Scaling** | Add more power to server | Limited by hardware |
| **Database Optimization** | Indexing, query optimization | Before scaling |

**💡 Rule of Thumb:** Shard only after exhausting other optimization options.

---

### Sharding vs Partitioning

| Aspect | Partitioning | Sharding |
|:---:|:---:|:---:|
| **Scope** | Within single database | Across multiple databases |
| **Location** | Same server | Different servers |
| **Complexity** | Lower | Higher |
| **Scalability** | Limited | Unlimited |
| **Use Case** | Logical separation | Physical distribution |

**Key Difference:** Sharding = Partitioning + Distribution

</div>

---

## 📊 Monitoring & Metrics

<div align="center">

### Key Metrics to Monitor

| Metric | Description | Why It Matters |
|:---:|:---:|:---:|
| **Shard Size** | Data size per shard | Plan rebalancing, detect hotspots |
| **Query Distribution** | Queries per shard | Ensure even load distribution |
| **Cross-Shard Queries** | Queries spanning multiple shards | Minimize these for performance |
| **Replication Lag** | Delay in replica sync | Ensure data consistency |
| **Shard Health** | Uptime, error rates | Detect failing shards early |

### Monitoring Tools

| Tool | Purpose |
|:---:|:---:|
| **Database Monitoring** | Track shard performance, query patterns |
| **Load Balancers** | Monitor request distribution |
| **Custom Dashboards** | Visualize shard metrics |
| **Alerting Systems** | Notify on anomalies |

**Best Practices:**
- Monitor shard sizes continuously
- Alert on uneven query distribution
- Track cross-shard query percentage
- Set up automated rebalancing triggers

</div>

---

## 🎓 Interview Tips

<div align="center">

### Key Points to Cover

When discussing sharding in interviews:

1. **Justify Need:** Explain why sharding is needed (after other optimizations)
2. **Choose Shard Key:** Select appropriate shard key with justification
3. **Select Strategy:** Choose sharding strategy (range, hash, directory, geographic)
4. **Address Rebalancing:** Explain how to add/remove shards
5. **Handle Cross-Shard Queries:** Discuss solutions for cross-shard operations
6. **Consider Alternatives:** Mention alternatives tried before sharding

### Common Interview Questions

| Question | Key Points |
|:---:|:---:|
| **When would you shard?** | After optimizing, read replicas, caching, vertical scaling |
| **How do you choose shard key?** | High cardinality, even distribution, used in queries |
| **How do you handle cross-shard queries?** | Denormalize, application-level joins, avoid when possible |
| **How do you rebalance?** | Consistent hashing, gradual migration, double-write |
| **What are the trade-offs?** | Scalability vs complexity, performance vs operational overhead |

</div>

---

## 💡 Best Practices

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Choose shard key carefully** | Affects performance and distribution |
| **Monitor shard sizes** | Detect hotspots early |
| **Plan for rebalancing** | Inevitable as data grows |
| **Minimize cross-shard queries** | Expensive operations |
| **Use consistent hashing** | Easier rebalancing |
| **Design for single-shard queries** | Better performance |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Shard too early** | Unnecessary complexity | Optimize first |
| **Poor shard key** | Hotspots, uneven distribution | Choose high cardinality key |
| **Ignore rebalancing** | Hotspots, performance issues | Plan rebalancing strategy |
| **Many cross-shard queries** | Performance degradation | Denormalize or redesign |
| **No monitoring** | Undetected issues | Set up comprehensive monitoring |

</div>

---

## 🔄 Rebalancing Strategies

<div align="center">

### Consistent Hashing

**Minimize data movement when adding/removing shards**

| Strategy | Description | Data Movement |
|:---:|:---:|:---:|
| **Standard Hashing** | hash(key) % num_shards | High (all data) |
| **Consistent Hashing** | Hash ring, virtual nodes | Low (only affected keys) |

**Benefits:**
- ✅ Minimal data movement
- ✅ Easy to add/remove shards
- ✅ Better load distribution

---

### Gradual Migration

**Move data incrementally**

| Step | Action |
|:---:|:---:|
| **1** | Add new shard |
| **2** | Start double-writing |
| **3** | Migrate data in batches |
| **4** | Update routing |
| **5** | Stop old shard writes |
| **6** | Complete migration |

**Benefits:**
- ✅ No downtime
- ✅ Gradual load increase
- ✅ Easy rollback

</div>

---

## 🎯 Summary

<div align="center">

### Key Takeaways

| Concept | Key Point |
|:---:|:---:|
| **Sharding Purpose** | Horizontal scaling when single database insufficient |
| **Sharding Strategies** | Range, Hash, Directory, Geographic |
| **Shard Key** | High cardinality, even distribution, used in queries |
| **Challenges** | Cross-shard queries, rebalancing, hotspots, transactions |
| **When to Shard** | After optimizing, read replicas, caching, vertical scaling |
| **Best Practice** | Monitor, plan rebalancing, minimize cross-shard queries |

**💡 Remember:** Sharding is a powerful scaling technique, but comes with complexity. Use it when other optimizations are insufficient.

</div>

---

<div align="center">

**Master database sharding for horizontal scalability! 🚀**

*Sharding enables systems to scale beyond single database limitations by distributing data across multiple independent shards.*

</div>
