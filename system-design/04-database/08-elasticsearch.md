# 🔍 Elasticsearch - Search & Analytics Engine

<div align="center">

**Distributed search and analytics engine built on Apache Lucene**

[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-Search-yellow?style=for-the-badge)](https://www.elastic.co/elasticsearch/)
[![Lucene](https://img.shields.io/badge/Apache-Lucene-green?style=for-the-badge)](./)
[![Analytics](https://img.shields.io/badge/Analytics-Powerful-blue?style=for-the-badge)](./)

*Master Elasticsearch for full-text search, analytics, and real-time data exploration*

</div>

---

## 🎯 What is Elasticsearch?

<div align="center">

**Elasticsearch is a distributed, RESTful search and analytics engine capable of solving a growing number of use cases.**

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **🔍 Full-Text Search** | Powerful text search capabilities |
| **📊 Analytics** | Aggregations, metrics, visualizations |
| **🌐 Distributed** | Horizontal scaling across nodes |
| **⚡ Real-Time** | Near real-time search and indexing |
| **📈 Scalable** | Handles petabytes of data |
| **🔓 Schema-Less** | Flexible JSON document storage |

**Mental Model:** Think of Elasticsearch as Google for your data - fast, distributed, and powerful search capabilities.

</div>

---

## 🏗️ Core Concepts

<div align="center">

### Elasticsearch Architecture

| Component | Description | SQL Equivalent |
|:---:|:---:|:---:|
| **Cluster** | Collection of nodes | Database server |
| **Node** | Single server instance | Server instance |
| **Index** | Collection of documents | Database |
| **Type** | Logical category (deprecated in 7.x+) | Table (legacy) |
| **Document** | JSON object | Row |
| **Field** | Key-value pair | Column |
| **Shard** | Horizontal partition | Partition |
| **Replica** | Copy of shard | Replica |

### Document Structure

**JSON Document:**
```json
{
  "_id": "1",
  "_index": "products",
  "_source": {
    "name": "iPhone 15",
    "description": "Latest iPhone with advanced features",
    "price": 999,
    "category": "electronics",
    "tags": ["smartphone", "apple", "mobile"],
    "in_stock": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

</div>

---

## 📊 Indexing & Mapping

<div align="center">

### Index Creation

**Create Index:**
```json
PUT /products
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "name": { "type": "text" },
      "price": { "type": "double" },
      "category": { "type": "keyword" },
      "created_at": { "type": "date" }
    }
  }
}
```

---

### Data Types

| Type | Description | Use Case |
|:---:|:---:|:---:|
| **text** | Analyzed text | Full-text search |
| **keyword** | Exact match | Filtering, aggregations |
| **long, integer** | Numeric | Range queries |
| **double, float** | Decimal | Price, ratings |
| **boolean** | True/false | Flags |
| **date** | Date/time | Timestamps |
| **geo_point** | Latitude/longitude | Location search |
| **nested** | Nested objects | Complex objects |
| **object** | JSON object | Embedded documents |

**Key Difference:**
- **text** - Analyzed (tokenized, lowercased) for search
- **keyword** - Not analyzed (exact match) for filtering

---

### Mapping Example

```json
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "keyword": { "type": "keyword" }
        }
      },
      "price": { "type": "double" },
      "location": { "type": "geo_point" },
      "tags": { "type": "keyword" },
      "metadata": {
        "type": "object",
        "properties": {
          "author": { "type": "keyword" },
          "views": { "type": "long" }
        }
      }
    }
  }
}
```

**Multi-Field Mapping:**
- `title` - Analyzed for search
- `title.keyword` - Exact match for sorting/aggregations

</div>

---

## 🔍 Querying Elasticsearch

<div align="center">

### Basic Queries

**Match Query (Full-Text):**
```json
GET /products/_search
{
  "query": {
    "match": {
      "name": "iPhone"
    }
  }
}
```

**Term Query (Exact Match):**
```json
{
  "query": {
    "term": {
      "category": "electronics"
    }
  }
}
```

---

### Query Types

| Query Type | Description | Use Case |
|:---:|:---:|:---:|
| **match** | Full-text search | Search in text fields |
| **term** | Exact match | Filter by keyword |
| **range** | Range queries | Price, date ranges |
| **bool** | Boolean logic | Complex queries |
| **match_phrase** | Phrase matching | Exact phrase search |
| **multi_match** | Multiple fields | Search across fields |
| **fuzzy** | Fuzzy matching | Typos, variations |
| **prefix** | Prefix matching | Autocomplete |

---

### Bool Query (Most Powerful)

**Combine multiple queries:**

```json
{
  "query": {
    "bool": {
      "must": [
        { "match": { "name": "iPhone" } }
      ],
      "filter": [
        { "range": { "price": { "gte": 500, "lte": 1500 } } },
        { "term": { "in_stock": true } }
      ],
      "must_not": [
        { "term": { "category": "accessories" } }
      ],
      "should": [
        { "match": { "tags": "new" } }
      ],
      "minimum_should_match": 1
    }
  }
}
```

**Bool Clauses:**
- **must** - Must match (affects score)
- **filter** - Must match (no score impact)
- **must_not** - Must not match
- **should** - Should match (boosts score)

---

### Aggregations

**Powerful analytics:**

```json
{
  "aggs": {
    "categories": {
      "terms": { "field": "category", "size": 10 }
    },
    "avg_price": {
      "avg": { "field": "price" }
    },
    "price_ranges": {
      "range": {
        "field": "price",
        "ranges": [
          { "to": 100 },
          { "from": 100, "to": 500 },
          { "from": 500 }
        ]
      }
    }
  }
}
```

**Aggregation Types:**
- **terms** - Group by field values
- **avg, sum, min, max** - Metrics
- **date_histogram** - Time-based grouping
- **range** - Range buckets
- **nested** - Nested aggregations

</div>

---

## 📈 Indexing Strategies

<div align="center">

### Bulk Indexing

**Efficient batch operations:**

```json
POST /_bulk
{ "index": { "_index": "products", "_id": "1" } }
{ "name": "iPhone 15", "price": 999 }
{ "index": { "_index": "products", "_id": "2" } }
{ "name": "Samsung Galaxy", "price": 899 }
```

**Best Practices:**
- ✅ Use bulk API for multiple documents
- ✅ Optimal batch size: 1000-5000 documents
- ✅ Use appropriate refresh interval
- ✅ Monitor indexing rate

---

### Refresh & Flush

| Operation | Description | When |
|:---:|:---:|:---:|
| **Refresh** | Make documents searchable | After indexing |
| **Flush** | Write to disk | Periodically |
| **Force Merge** | Optimize segments | Maintenance |

**Refresh Settings:**
```json
PUT /products/_settings
{
  "index": {
    "refresh_interval": "30s"  // Default: 1s
  }
}
```

**Trade-off:** Lower refresh interval = Faster searchability but slower indexing

</div>

---

## 🌐 Sharding & Replication

<div align="center">

### Sharding Strategy

**Shard = Horizontal partition**

| Aspect | Description |
|:---:|:---:|
| **Primary Shards** | Data partition (fixed at index creation) |
| **Replica Shards** | Copies for HA and read scaling |
| **Shard Size** | Recommended: 20-50GB per shard |
| **Shard Count** | Consider: Data size, growth, queries |

**Shard Configuration:**
```json
PUT /products
{
  "settings": {
    "number_of_shards": 3,      // Primary shards
    "number_of_replicas": 1      // Replica shards
  }
}
```

**⚠️ Important:** Number of primary shards cannot be changed after index creation!

---

### Replication

**Benefits:**
- ✅ High availability
- ✅ Read scaling
- ✅ Data redundancy

**Replica Strategy:**
- **1 replica** - Can survive 1 node failure
- **2 replicas** - Can survive 2 node failures
- **More replicas** - Better read performance, more storage

</div>

---

## 🔍 Full-Text Search

<div align="center">

### Analyzers

**Text processing pipeline:**

| Analyzer | Description | Use Case |
|:---:|:---:|:---:|
| **standard** | Default analyzer | General text |
| **keyword** | No analysis | Exact match |
| **whitespace** | Split on whitespace | Simple tokenization |
| **simple** | Lowercase, split on non-letters | Basic text |
| **english** | English-specific | English text |
| **custom** | User-defined | Special requirements |

**Analysis Process:**
1. **Character Filters** - Clean text
2. **Tokenizer** - Split into tokens
3. **Token Filters** - Lowercase, stemming, etc.

---

### Custom Analyzer

```json
PUT /products
{
  "settings": {
    "analysis": {
      "analyzer": {
        "custom_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "stop", "snowball"]
        }
      }
    }
  }
}
```

---

### Relevance Scoring

**TF-IDF Algorithm (default):**

| Factor | Description |
|:---:|:---:|
| **Term Frequency (TF)** | How often term appears in document |
| **Inverse Document Frequency (IDF)** | How rare term is across corpus |
| **Field Length** | Shorter fields score higher |
| **Boost** | Manual relevance boost |

**Boosting Example:**
```json
{
  "query": {
    "bool": {
      "should": [
        { "match": { "title": { "query": "iPhone", "boost": 2.0 } } },
        { "match": { "description": "iPhone" } }
      ]
    }
  }
}
```

</div>

---

## 📊 Aggregations Deep Dive

<div align="center">

### Metrics Aggregations

**Single value metrics:**

```json
{
  "aggs": {
    "avg_price": { "avg": { "field": "price" } },
    "max_price": { "max": { "field": "price" } },
    "min_price": { "min": { "field": "price" } },
    "total_sales": { "sum": { "field": "sales" } },
    "price_stats": { "stats": { "field": "price" } }
  }
}
```

---

### Bucket Aggregations

**Group documents:**

```json
{
  "aggs": {
    "categories": {
      "terms": {
        "field": "category",
        "size": 10,
        "order": { "_count": "desc" }
      },
      "aggs": {
        "avg_price": { "avg": { "field": "price" } }
      }
    }
  }
}
```

**Nested Aggregations:**
- Group by category
- Then calculate avg price per category

---

### Date Histogram

**Time-based grouping:**

```json
{
  "aggs": {
    "sales_over_time": {
      "date_histogram": {
        "field": "created_at",
        "calendar_interval": "day"
      },
      "aggs": {
        "total_sales": { "sum": { "field": "sales" } }
      }
    }
  }
}
```

</div>

---

## 🎯 Use Cases

<div align="center">

### ✅ Ideal Use Cases

| Use Case | Why Elasticsearch |
|:---:|:---:|
| **Search Engines** | Full-text search, relevance scoring |
| **Log Analytics** | ELK stack (Elasticsearch, Logstash, Kibana) |
| **E-commerce Search** | Product search, filters, facets |
| **Analytics** | Real-time aggregations, dashboards |
| **Monitoring** | Metrics, alerting, visualization |
| **Content Discovery** | Recommendations, related content |
| **Geospatial Search** | Location-based queries |

---

### ❌ When NOT to Use

| Scenario | Better Alternative |
|:---:|:---:|
| **ACID Transactions** | Relational databases |
| **Simple Key-Value** | Redis, DynamoDB |
| **Complex Relationships** | Graph databases |
| **Frequent Updates** | Databases optimized for writes |
| **Small Dataset** | Traditional databases |

</div>

---

## ⚡ Performance Optimization

<div align="center">

### Index Optimization

| Technique | Description | Impact |
|:---:|:---:|:---:|
| **Appropriate Shards** | Right number of shards | Better distribution |
| **Refresh Interval** | Increase for bulk indexing | Faster indexing |
| **Force Merge** | Optimize segments | Better query performance |
| **Index Templates** | Consistent settings | Easier management |
| **Aliases** | Zero-downtime reindexing | Seamless updates |

---

### Query Optimization

| Technique | Description | Impact |
|:---:|:---:|:---:|
| **Use Filters** | Filter vs query | Faster (no scoring) |
| **Limit Fields** | `_source` filtering | Less data transfer |
| **Pagination** | `search_after` vs `from/size` | Better for deep pagination |
| **Routing** | Route to specific shard | Faster queries |
| **Caching** | Query result caching | Faster repeated queries |

**Filter vs Query:**
- **Filter** - Yes/No match (cached, no scoring)
- **Query** - Relevance scoring (not cached)

**Best Practice:** Use filters for exact matches, queries for relevance.

</div>

---

## 🔐 Security & Access Control

<div align="center">

### Security Features

| Feature | Description | Implementation |
|:---:|:---:|:---:|
| **Authentication** | User credentials | X-Pack Security |
| **Authorization** | Role-based access | RBAC, field-level security |
| **Encryption** | TLS/SSL | Encrypt in transit |
| **Audit Logging** | Track access | Enable audit logs |
| **IP Filtering** | Network security | Whitelist IPs |

### Role-Based Access

```json
PUT /_security/role/search_role
{
  "indices": [
    {
      "names": ["products"],
      "privileges": ["read"],
      "query": {
        "term": { "category": "electronics" }
      }
    }
  ]
}
```

</div>

---

## 🔄 Data Management

<div align="center">

### Index Lifecycle Management (ILM)

**Automated index management:**

| Phase | Description | Actions |
|:---:|:---:|:---:|
| **Hot** | Active indexing | Frequent writes |
| **Warm** | Read-only | Optimize, reduce replicas |
| **Cold** | Rarely accessed | Move to cheaper storage |
| **Delete** | No longer needed | Delete index |

**ILM Policy:**
```json
PUT /_ilm/policy/logs_policy
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": { "max_size": "50GB" }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "shrink": { "number_of_shards": 1 }
        }
      },
      "delete": {
        "min_age": "30d",
        "actions": { "delete": {} }
      }
    }
  }
}
```

---

### Reindexing

**Copy data between indices:**

```json
POST /_reindex
{
  "source": { "index": "products_old" },
  "dest": { "index": "products_new" }
}
```

**Use Cases:**
- ✅ Update mappings
- ✅ Change shard count
- ✅ Migrate data

</div>

---

## 🎓 Interview Questions

<div align="center">

### Expert-Level Questions

| Question | Key Points |
|:---:|:---:|
| **Design a search system** | Indexing strategy, sharding, relevance scoring, filters |
| **How do you handle high write throughput?** | Bulk API, refresh interval, sharding, routing |
| **Design a log analytics system** | ELK stack, index templates, ILM, retention |
| **How do you optimize slow queries?** | Explain API, filters vs queries, caching, routing |
| **Design an e-commerce search** | Faceted search, filters, sorting, autocomplete |
| **How do you ensure high availability?** | Replicas, cluster configuration, node roles |
| **Design a monitoring system** | Metrics collection, aggregations, alerting |

</div>

---

## 💡 Common Patterns & Best Practices

<div align="center">

### ✅ Best Practices

| Practice | Why |
|:---:|:---:|
| **Design for queries** | Optimize for actual access patterns |
| **Use appropriate data types** | text vs keyword, numeric types |
| **Index templates** | Consistent index settings |
| **Monitor cluster health** | Prevent issues |
| **Use aliases** | Zero-downtime operations |
| **ILM policies** | Automated index management |

---

### ❌ Anti-Patterns

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Too many shards** | Overhead, slow queries | Right-size shards |
| **Too few shards** | Limited scaling | Plan for growth |
| **Over-indexing** | Storage bloat | Index only what's needed |
| **Using queries for filters** | Slower performance | Use filters for exact matches |
| **Deep pagination** | Performance issues | Use search_after |
| **No refresh control** | Slow indexing | Adjust refresh interval |

</div>

---

## 🔄 Elasticsearch vs Alternatives

<div align="center">

### Comparison

| Feature | Elasticsearch | Solr | Database |
|:---:|:---:|:---:|:---:|
| **Full-Text Search** | ✅ Excellent | ✅ Excellent | ❌ Limited |
| **Analytics** | ✅ Powerful | ✅ Good | ✅ SQL aggregations |
| **Real-Time** | ✅ Near real-time | ✅ Near real-time | ✅ Real-time |
| **Scalability** | ✅ Horizontal | ✅ Horizontal | ⚠️ Vertical/Replicas |
| **Ecosystem** | ✅ ELK stack | ✅ SolrCloud | ✅ SQL ecosystem |
| **Use Case** | Search + Analytics | Search | Structured data |

**💡 Choose Elasticsearch when:** You need powerful full-text search, real-time analytics, and horizontal scaling.

</div>

---

## 🚀 Getting Started

<div align="center">

### Learning Path

| Step | Topic | Resource |
|:---:|:---:|:---:|
| **1️⃣** | Basic Concepts | Index, document, query |
| **2️⃣** | Mapping & Data Types | text vs keyword, mappings |
| **3️⃣** | Query DSL | match, bool, aggregations |
| **4️⃣** | Indexing | Bulk API, refresh, settings |
| **5️⃣** | Sharding & Replication | Cluster architecture |
| **6️⃣** | Performance | Optimization, monitoring |

</div>

---

<div align="center">

**Master Elasticsearch for powerful search and analytics! 🚀**

*Elasticsearch is the go-to solution for full-text search, log analytics, and real-time data exploration.*

</div>

