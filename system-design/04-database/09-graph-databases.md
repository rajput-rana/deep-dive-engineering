# 🕸️ Graph Databases - Neo4j

<div align="center">

**Store and query connected data efficiently**

[![Graph](https://img.shields.io/badge/Graph-Database-purple?style=for-the-badge)](https://neo4j.com/)
[![Neo4j](https://img.shields.io/badge/Neo4j-Native-green?style=for-the-badge)](./)
[![Relationships](https://img.shields.io/badge/Relationships-First-blue?style=for-the-badge)](./)

*Master graph databases for relationship-heavy data and complex traversals*

</div>

---

## 🎯 What is a Graph Database?

<div align="center">

**A graph database stores data as nodes (entities) and relationships (connections) with properties, optimized for relationship queries.**

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **🕸️ Relationship-First** | Relationships are first-class citizens |
| **🔗 Connected Data** | Optimized for traversing relationships |
| **📊 Graph Model** | Nodes, relationships, properties |
| **⚡ Fast Traversals** | O(1) relationship access |
| **🌐 Complex Queries** | Pattern matching, path finding |
| **🔍 Graph Algorithms** | Shortest path, centrality, community detection |

**Mental Model:** Think of a graph database as a social network - entities (people) connected by relationships (friendships) with properties (names, ages).

</div>

---

## 🏗️ Core Concepts

<div align="center">

### Graph Model

| Component | Description | Example |
|:---:|:---:|:---:|
| **Node (Vertex)** | Entity in the graph | Person, Product, Post |
| **Relationship (Edge)** | Connection between nodes | FRIENDS_WITH, PURCHASED, LIKES |
| **Property** | Key-value pair on nodes/relationships | name: "John", since: 2020 |
| **Label** | Category/type of node | Person, Company, Product |
| **Direction** | Relationship direction | Person → LIKES → Post |

### Simple Graph Example

```
(Person:John) -[:FRIENDS_WITH {since: 2020}]-> (Person:Jane)
(Person:John) -[:LIKES]-> (Post:123)
(Person:Jane) -[:LIKES]-> (Post:123)
(Post:123) -[:HAS_TAG]-> (Tag:Tech)
```

**Visual Representation:**
```
    John ──FRIENDS_WITH──> Jane
     │                      │
     │                      │
    LIKES                 LIKES
     │                      │
     └──────────┐           │
                │           │
              Post:123 <────┘
                │
             HAS_TAG
                │
              Tag:Tech
```

</div>

---

## 📊 Data Modeling

<div align="center">

### Modeling Principles

| Principle | Description | Example |
|:---:|:---:|:---:|
| **Nodes for Entities** | Real-world objects | Person, Product, Order |
| **Relationships for Connections** | How entities relate | PURCHASED, FOLLOWS, CONTAINS |
| **Properties for Attributes** | Data about entities | name, price, date |
| **Labels for Categories** | Group similar nodes | Person, Company, Product |
| **Relationship Types** | Categorize relationships | FRIENDS_WITH, WORKS_AT |

---

### Common Patterns

**1. Social Network:**
```
(Person) -[:FOLLOWS]-> (Person)
(Person) -[:LIKES]-> (Post)
(Person) -[:COMMENTED_ON]-> (Post)
```

**2. E-commerce:**
```
(Person) -[:PURCHASED]-> (Product)
(Product) -[:BELONGS_TO]-> (Category)
(Product) -[:SIMILAR_TO]-> (Product)
```

**3. Knowledge Graph:**
```
(Person) -[:KNOWS]-> (Person)
(Person) -[:WORKS_AT]-> (Company)
(Company) -[:LOCATED_IN]-> (City)
```

---

### When to Use Graph Model

| Scenario | Why Graph |
|:---:|:---:|
| **Complex Relationships** | Many relationships between entities |
| **Relationship Queries** | "Find friends of friends" |
| **Path Finding** | Shortest path, recommendations |
| **Network Analysis** | Social networks, dependencies |
| **Hierarchical Data** | Trees, organizational charts |
| **Recommendations** | Based on relationships |

</div>

---

## 🔍 Cypher Query Language

<div align="center">

### Basic Cypher Syntax

**Cypher = Graph query language (like SQL for graphs)**

**Pattern Matching:**
```cypher
// Find all people
MATCH (p:Person)
RETURN p

// Find person by name
MATCH (p:Person {name: "John"})
RETURN p

// Find friends of John
MATCH (john:Person {name: "John"})-[:FRIENDS_WITH]->(friend:Person)
RETURN friend.name
```

---

### Common Patterns

**1. Simple Match:**
```cypher
MATCH (p:Person)
WHERE p.age > 25
RETURN p.name, p.age
```

**2. Relationship Traversal:**
```cypher
// One hop
MATCH (a:Person)-[:FRIENDS_WITH]->(b:Person)
RETURN a, b

// Multiple hops
MATCH (a:Person)-[:FRIENDS_WITH*2]->(c:Person)
RETURN a, c

// Variable length
MATCH (a:Person)-[:FRIENDS_WITH*1..3]->(b:Person)
RETURN a, b
```

**3. Path Finding:**
```cypher
// Shortest path
MATCH path = shortestPath(
  (start:Person {name: "John"})-[*]-(end:Person {name: "Jane"})
)
RETURN path
```

**4. Aggregations:**
```cypher
MATCH (p:Person)-[:PURCHASED]->(pr:Product)
RETURN p.name, count(pr) as purchase_count
ORDER BY purchase_count DESC
```

---

### Advanced Patterns

**1. Pattern Matching:**
```cypher
// Find mutual friends
MATCH (a:Person {name: "John"})-[:FRIENDS_WITH]->(mutual:Person)<-[:FRIENDS_WITH]-(b:Person {name: "Jane"})
RETURN mutual.name
```

**2. Optional Match:**
```cypher
// Left outer join equivalent
MATCH (p:Person)
OPTIONAL MATCH (p)-[:LIKES]->(post:Post)
RETURN p.name, post.title
```

**3. Creating Nodes:**
```cypher
CREATE (p:Person {name: "John", age: 30})
RETURN p
```

**4. Creating Relationships:**
```cypher
MATCH (a:Person {name: "John"}), (b:Person {name: "Jane"})
CREATE (a)-[:FRIENDS_WITH {since: 2024}]->(b)
```

</div>

---

## 🎯 Use Cases

<div align="center">

### ✅ Ideal Use Cases

| Use Case | Why Graph Database |
|:---:|:---:|
| **Social Networks** | Friend relationships, recommendations |
| **Recommendation Engines** | "Users who bought X also bought Y" |
| **Fraud Detection** | Detect suspicious patterns |
| **Knowledge Graphs** | Wikipedia, semantic web |
| **Network Analysis** | IT infrastructure, dependencies |
| **Master Data Management** | Complex entity relationships |
| **Identity & Access Management** | User permissions, roles |

---

### Real-World Examples

| Company | Use Case |
|:---:|:---:|
| **LinkedIn** | Professional network, recommendations |
| **Facebook** | Social graph, friend suggestions |
| **eBay** | Product recommendations |
| **Walmart** | Supply chain optimization |
| **NASA** | Knowledge management |

</div>

---

## ⚡ Graph Algorithms

<div align="center">

### Built-in Algorithms

| Algorithm | Description | Use Case |
|:---:|:---:|
| **Shortest Path** | Find shortest path between nodes | Routing, recommendations |
| **PageRank** | Importance/centrality | Influencer detection |
| **Community Detection** | Find clusters | Group detection |
| **Centrality** | Node importance | Key influencers |
| **Similarity** | Node similarity | Recommendations |
| **Clustering** | Group similar nodes | Segmentation |

---

### PageRank Example

**Find influential users:**
```cypher
CALL gds.pageRank.stream('social-graph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC
LIMIT 10
```

---

### Shortest Path Example

**Find connection path:**
```cypher
MATCH (start:Person {name: "John"}), (end:Person {name: "Jane"})
CALL gds.shortestPath.dijkstra.stream('social-graph', {
  sourceNode: start,
  targetNode: end
})
YIELD path
RETURN path
```

</div>

---

## 🏢 Neo4j Architecture

<div align="center">

### Neo4j Components

| Component | Description |
|:---:|:---:|
| **Core** | Native graph storage engine |
| **Cypher** | Query language |
| **Graph Data Science** | Algorithms library |
| **Bloom** | Visualization tool |
| **APOC** | Procedures library |

---

### Storage Model

**Neo4j uses:**
- **Node Store** - Stores nodes
- **Relationship Store** - Stores relationships
- **Property Store** - Stores properties
- **Indexes** - Fast lookups

**Key Feature:** Relationships stored as doubly-linked lists
- O(1) relationship traversal
- No JOINs needed

</div>

---

## 📈 Performance Optimization

<div align="center">

### Indexing Strategies

| Index Type | Description | Use Case |
|:---:|:---:|
| **Node Index** | Index node properties | Fast node lookup |
| **Relationship Index** | Index relationship properties | Fast relationship lookup |
| **Composite Index** | Multiple properties | Multi-property queries |
| **Full-Text Index** | Text search | Search functionality |

**Create Index:**
```cypher
CREATE INDEX person_name_index FOR (p:Person) ON (p.name)
CREATE INDEX person_email_index FOR (p:Person) ON (p.email)
```

---

### Query Optimization

| Technique | Description | Impact |
|:---:|:---:|
| **Use Indexes** | Index frequently queried properties | Faster lookups |
| **Limit Path Length** | Restrict relationship depth | Faster traversals |
| **Use Parameters** | Parameterized queries | Query plan caching |
| **Profile Queries** | Analyze query execution | Identify bottlenecks |
| **Batch Operations** | Process in batches | Better performance |

**Profile Query:**
```cypher
PROFILE MATCH (p:Person)-[:FRIENDS_WITH*2]->(friend:Person)
RETURN friend.name
```

**Key Metrics:**
- **DbHits** - Database operations (lower is better)
- **Rows** - Result rows
- **Estimated Rows** - Query planner estimate

</div>

---

## 🔄 Data Modeling Best Practices

<div align="center">

### ✅ Best Practices

| Practice | Why |
|:---:|:---:|
| **Model for queries** | Optimize for actual access patterns |
| **Use appropriate relationship types** | Clear semantics |
| **Add properties to relationships** | Store relationship metadata |
| **Use labels effectively** | Group similar nodes |
| **Index frequently queried properties** | Faster lookups |
| **Avoid deep traversals** | Limit path length |

---

### ❌ Anti-Patterns

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Too many node types** | Over-complexity | Consolidate similar nodes |
| **Deep traversals** | Performance issues | Limit depth, use algorithms |
| **Missing indexes** | Slow queries | Index frequently queried properties |
| **Over-normalization** | Too many relationships | Balance normalization |
| **Storing large data** | Memory issues | Store references, use external storage |

</div>

---

## 🎓 Interview Questions

<div align="center">

### Expert-Level Questions

| Question | Key Points |
|:---:|:---:|
| **Design a social network** | Users, friendships, posts, likes, recommendations |
| **Design a recommendation system** | User-item relationships, collaborative filtering, graph algorithms |
| **Design a fraud detection system** | Transaction graph, pattern detection, anomaly detection |
| **How do you optimize graph queries?** | Indexing, query profiling, limiting depth, caching |
| **Design a knowledge graph** | Entities, relationships, properties, semantic queries |
| **How do you handle large graphs?** | Sharding, partitioning, distributed graph databases |
| **Design a network monitoring system** | Infrastructure graph, dependency tracking, impact analysis |

</div>

---

## 🔐 Security & Access Control

<div align="center">

### Security Features

| Feature | Description | Implementation |
|:---:|:---:|:---:|
| **Authentication** | User credentials | Native, LDAP, Kerberos |
| **Authorization** | Role-based access | RBAC, property-based |
| **Encryption** | Data encryption | Encryption at rest, in transit |
| **Audit Logging** | Track access | Enable audit logs |
| **Field-Level Security** | Property access control | Restrict property access |

### Role-Based Access

```cypher
// Create role
CREATE ROLE reader
GRANT MATCH ON GRAPH * TO reader

// Grant role to user
GRANT ROLE reader TO user1
```

</div>

---

## 🔄 Graph Database vs Relational Database

<div align="center">

### Comparison

| Aspect | Graph Database | Relational Database |
|:---:|:---:|:---:|
| **Relationships** | First-class citizens | Foreign keys, JOINs |
| **Query Complexity** | Simple for relationships | Complex JOINs |
| **Traversal Performance** | O(1) relationship access | O(n) JOINs |
| **Schema** | Flexible | Fixed schema |
| **Use Case** | Relationship-heavy | Structured data |
| **Scalability** | Horizontal (Neo4j Enterprise) | Vertical, read replicas |

### When to Choose Graph

**Choose Graph When:**
- ✅ Many relationships between entities
- ✅ Complex relationship queries
- ✅ Path finding, recommendations
- ✅ Network analysis
- ✅ Relationship traversal is primary operation

**Choose Relational When:**
- ✅ Structured data with fixed schema
- ✅ Complex aggregations
- ✅ ACID transactions critical
- ✅ Simple relationships

</div>

---

## 💡 Common Patterns

<div align="center">

### 1. Friend Recommendations

```cypher
// Find friends of friends (not already friends)
MATCH (user:Person {id: $userId})-[:FRIENDS_WITH]->(friend:Person)-[:FRIENDS_WITH]->(suggestion:Person)
WHERE NOT (user)-[:FRIENDS_WITH]->(suggestion)
  AND user <> suggestion
RETURN suggestion, count(*) AS mutual_friends
ORDER BY mutual_friends DESC
LIMIT 10
```

---

### 2. Product Recommendations

```cypher
// Users who bought X also bought Y
MATCH (user:Person)-[:PURCHASED]->(product1:Product {id: $productId})
MATCH (user)-[:PURCHASED]->(product2:Product)
WHERE product1 <> product2
MATCH (other:Person)-[:PURCHASED]->(product2)
WHERE other <> user
RETURN product2, count(DISTINCT other) AS recommendation_score
ORDER BY recommendation_score DESC
LIMIT 10
```

---

### 3. Shortest Path

```cypher
// Find shortest path between two people
MATCH path = shortestPath(
  (start:Person {name: "John"})-[*]-(end:Person {name: "Jane"})
)
RETURN path, length(path) AS path_length
```

---

### 4. Community Detection

```cypher
// Find communities using Louvain algorithm
CALL gds.louvain.stream('social-graph')
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).name AS name, communityId
ORDER BY communityId, name
```

</div>

---

## 🚀 Scaling Graph Databases

<div align="center">

### Scaling Strategies

| Strategy | Description | Trade-offs |
|:---:|:---:|:---:|
| **Vertical Scaling** | More resources per server | Limited by hardware |
| **Read Replicas** | Distribute read load | Eventual consistency |
| **Sharding** | Partition graph | Complex, relationship challenges |
| **Federation** | Multiple databases | Application-level complexity |

**Challenges:**
- Relationships span shards
- Cross-shard queries expensive
- Maintaining graph integrity

**Neo4j Enterprise:**
- Causal clustering
- Read replicas
- Horizontal scaling (limited)

</div>

---

## 📊 Graph Database Comparison

<div align="center">

### Popular Graph Databases

| Database | Type | Best For | Key Features |
|:---:|:---:|:---:|:---:|
| **Neo4j** | Native graph | General purpose | Cypher, GDS library |
| **Amazon Neptune** | Managed graph | AWS ecosystem | Gremlin, SPARQL |
| **ArangoDB** | Multi-model | Flexible data | Graph + Document |
| **TigerGraph** | Native graph | Large-scale | GSQL, distributed |
| **Dgraph** | Distributed graph | Scalability | GraphQL API |

### Neo4j Highlights

- **Cypher** - Intuitive query language
- **Graph Data Science** - Built-in algorithms
- **Mature Ecosystem** - Tools, drivers, community
- **Visualization** - Bloom for exploration

</div>

---

## 🎯 Database Design for Graphs

<div align="center">

### Design Process

| Step | Description |
|:---:|:---:|
| **1. Identify Entities** | What are the nodes? |
| **2. Identify Relationships** | How do entities connect? |
| **3. Define Properties** | What data do nodes/relationships have? |
| **4. Design for Queries** | Optimize for access patterns |
| **5. Add Indexes** | Index frequently queried properties |
| **6. Test Performance** | Profile queries, optimize |

---

### Example: Social Network Design

**Nodes:**
- Person (properties: name, email, age)
- Post (properties: content, created_at)
- Group (properties: name, description)

**Relationships:**
- FRIENDS_WITH (properties: since, status)
- LIKES (properties: created_at)
- POSTED (properties: created_at)
- MEMBER_OF (properties: joined_at, role)

**Indexes:**
- Person.name
- Person.email
- Post.created_at

</div>

---

## 🔄 Migration from Relational

<div align="center">

### Migration Strategy

| Step | Description |
|:---:|:---:|
| **1. Analyze Relationships** | Identify foreign keys, JOINs |
| **2. Map to Graph Model** | Tables → Nodes, Foreign Keys → Relationships |
| **3. Extract Relationships** | Convert JOINs to relationships |
| **4. Migrate Data** | ETL process |
| **5. Validate** | Compare results |
| **6. Optimize** | Add indexes, optimize queries |

**Example Migration:**
```sql
-- Relational
SELECT u.name, o.total
FROM users u
JOIN orders o ON u.id = o.user_id
```

```cypher
-- Graph
MATCH (u:User)-[:PLACED]->(o:Order)
RETURN u.name, o.total
```

</div>

---

<div align="center">

**Master graph databases for relationship-heavy data! 🚀**

*Graph databases excel at modeling and querying complex relationships that would require expensive JOINs in relational databases.*

</div>

