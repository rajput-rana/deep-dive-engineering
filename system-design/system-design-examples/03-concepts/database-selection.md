# Choosing the Right Database in a System Design Interview

"What database should we use?"
This question comes up in every system design interview. And most candidates give weak answers like "We will use PostgreSQL because it is reliable" or "Let's use MongoDB because it scales well."
These answers miss the point entirely.
Database selection is not about picking your favorite technology. It is about matching data requirements to database capabilities. 
The right database for a messaging app is not the right database for an analytics pipeline. The right database for a payment system is not the right database for a social feed.
Interviewers ask about databases because your choice reveals how well you understand data requirements, trade-offs, and system constraints. A candidate who picks the right database and explains why demonstrates real engineering judgment.
In this chapter, you will learn:
- How to analyze data requirements before choosing a database
- The major database categories and when to use each
- A decision framework for system design interviews
- Real examples with database recommendations
- Common mistakes and how to avoid them

# Why Database Choice Matters
Database selection affects nearly every aspect of your system:
**Performance:** Different databases have different read/write characteristics. A database optimized for writes might struggle with complex reads.
**Scalability:** Some databases scale vertically, others horizontally. Your choice determines how you grow.
**Consistency:** Databases offer different consistency guarantees. Your choice affects data correctness and user experience.
**Availability:** Some databases prioritize availability, others consistency. You cannot have both during failures.
**Development velocity:** Schema flexibility, query capabilities, and tooling affect how fast you can build.
**Operational complexity:** Some databases are easy to operate, others require specialized knowledge.
A poor database choice can cripple your system. I have seen teams spend months migrating because they picked the wrong database early. In an interview, picking the wrong database and not being able to justify it signals inexperience.
# Understanding Data Requirements First
Before picking a database, you must understand your data. Ask these questions:

### 1. What is the Data Structure?
Is your data highly structured with well-defined schemas? Or is it flexible and evolving?
| Characteristic | Database Implication |
| --- | --- |
| Fixed schema, clear relationships | Relational databases work well |
| Flexible schema, evolving structure | Document databases fit better |
| Key-value pairs | Key-value stores are optimal |
| Graph relationships | Graph databases excel |

**Example:** User profiles with name, email, and address have a clear structure. Relational databases work well. Product catalogs with varying attributes per product type benefit from flexible schemas.

### 2. What are the Access Patterns?
How will you read and write data? This is often the most important question.
| Access Pattern | Database Consideration |
| --- | --- |
| Point lookups by key | Key-value stores, any database with good indexing |
| Complex queries with joins | Relational databases |
| Full-text search | Search engines (Elasticsearch) |
| Time-series data | Time-series databases |
| Real-time analytics | Columnar databases, OLAP systems |
| Graph traversals | Graph databases |

**Example:** A social feed reads tweets by user ID and time, a pattern that works well with sorted key-value stores. A reporting dashboard runs complex aggregations, which suits columnar databases.

### 3. What Scale Do We Need?
Scale affects database choice significantly.
| Scale | Consideration |
| --- | --- |
| Thousands of records | Almost any database works |
| Millions of records | Need good indexing, may need read replicas |
| Billions of records | Need sharding, distributed databases |
| Petabytes of data | Need specialized distributed systems |

**Example:** A small business CRM with 10,000 customers can use SQLite. A social network with 500 million users needs a distributed database with sharding.

### 4. What Consistency is Required?
This determines your options significantly.
| Requirement | Options |
| --- | --- |
| Strong consistency (ACID) | Relational databases, some distributed databases (Spanner, CockroachDB) |
| Eventual consistency acceptable | Most NoSQL databases, better availability and performance |
| Causal consistency | Some distributed databases |

**Example:** A banking system transferring money between accounts needs strong consistency. A social media likes counter can tolerate eventual consistency.

### 5. What are the Relationships?
How entities relate to each other affects database choice.
| Relationship Type | Consideration |
| --- | --- |
| Simple foreign keys | Relational databases handle well |
| Complex many-to-many | Consider denormalization or graph databases |
| Deep graph traversals | Graph databases are optimal |
| No relationships, independent entities | Document or key-value stores |

**Example:** A friends-of-friends query (2-hop traversal) is manageable in relational databases. A "6 degrees of separation" query (6-hop traversal) needs a graph database.
# Major Database Categories
Let me walk through the main database categories, when to use each, and specific technologies.

### Relational Databases (RDBMS)
Relational databases store data in tables with predefined schemas. They enforce ACID properties and support complex queries with SQL.

#### When to Use
- Data has clear structure and relationships
- You need ACID transactions
- Complex queries with joins are common
- Data integrity is critical
- Schema is relatively stable

#### When NOT to Use
- Massive scale requiring horizontal sharding (though solutions exist)
- Highly flexible or evolving schemas
- Simple key-value access patterns
- Real-time analytics on huge datasets

#### Popular Options
| Database | Best For |
| --- | --- |
| PostgreSQL | General purpose, complex queries, extensibility, JSONB support |
| MySQL | Web applications, read-heavy workloads |
| Oracle | Enterprise, complex transactions |
| SQL Server | Microsoft ecosystem, enterprise |

#### Example Use Cases
- **Payment systems:** Transactions must be ACID compliant
- **E-commerce orders:** Complex relationships between users, orders, products
- **User management:** Structured user data with authentication
- **Inventory management:** Need accurate counts and constraints

"I would use PostgreSQL for the user and order data. We need ACID transactions for payments, the schema is well-defined, and we need to query orders by user, date, and status. PostgreSQL handles these requirements well and is operationally mature."

### Document Databases
Document databases store data as semi-structured documents (usually JSON). They offer flexible schemas and horizontal scaling.

#### When to Use
- Schema is flexible or evolving
- Data is naturally document-shaped
- Hierarchical data that would require many joins in SQL
- Need horizontal scaling
- Development speed matters

#### When NOT to Use
- Complex transactions across documents
- Many-to-many relationships requiring joins
- Strict schema enforcement needed
- Complex analytical queries

#### Popular Options
| Database | Best For |
| --- | --- |
| MongoDB | General purpose document storage, flexible queries |
| Couchbase | Mobile sync, caching, flexible documents |
| Amazon DocumentDB | MongoDB-compatible, managed AWS service |

#### Example Use Cases
- **Content management:** Articles with varying metadata
- **Product catalogs:** Products with different attributes
- **User profiles:** Flexible user preferences and settings
- **Event logging:** Semi-structured event data

"For the product catalog, I would use MongoDB. Each product type has different attributes, so the flexible schema helps. Products are typically fetched by ID or category, which MongoDB handles well. We can embed product variants within the document to avoid joins."

### Key-Value Stores
Key-value stores are the simplest database type. They store data as key-value pairs and excel at fast lookups.

#### When to Use
- Simple get/set operations by key
- Caching
- Session storage
- Real-time counters and leaderboards
- Need extremely low latency

#### When NOT to Use
- Complex queries
- Relationships between data
- Secondary indexes needed
- Range queries on non-key fields

#### Popular Options
| Database | Best For |
| --- | --- |
| Redis | Caching, sessions, real-time data, pub/sub, rich data structures |
| Memcached | Simple caching, distributed cache |
| Amazon DynamoDB | Managed key-value/document hybrid, serverless |
| Aerospike | High throughput, low latency at scale |

#### Example Use Cases
- **Session storage:** Fast user session lookups
- **Caching:** Cache database query results or API responses
- **Rate limiting:** Track request counts per user/IP
- **Leaderboards:** Sorted sets for rankings

"For session storage, I would use Redis. Sessions are accessed by session ID, which is a perfect key-value pattern. Redis provides sub-millisecond latency and supports TTL for automatic session expiration. It also gives us atomic operations for session updates."

### Wide-Column Stores
Wide-column stores organize data into rows and dynamic columns. They excel at handling massive scale and high write throughput.

#### When to Use
- Massive scale (billions of rows)
- High write throughput
- Time-series data
- Known access patterns
- Distributed across regions

#### When NOT to Use
- Complex queries with aggregations
- Frequent schema changes
- Ad-hoc queries
- Strong consistency requirements

#### Popular Options
| Database | Best For |
| --- | --- |
| Apache Cassandra | Write-heavy workloads, multi-region, linear scaling |
| HBase | Hadoop integration, analytics on big data |
| ScyllaDB | Cassandra-compatible with better performance |
| Google Bigtable | Managed wide-column store on GCP |

#### Example Use Cases
- **Time-series data:** IoT sensor readings, metrics
- **Messaging:** Chat message history
- **Activity feeds:** User activity streams
- **Logging:** High-volume log storage

"For message storage in our chat application, I would use Cassandra. We have write-heavy workloads since every message is a write. Messages are accessed by conversation ID and timestamp, which fits Cassandra's partition key design. It also handles our multi-region requirement for low-latency access globally."

### Graph Databases
Graph databases store nodes and relationships as first-class citizens. They excel at traversing connections.

#### When to Use
- Data is highly connected
- Traversing relationships is a core use case
- Relationship properties matter
- Need to find paths or patterns in connections

#### When NOT to Use
- Simple CRUD operations
- Aggregations and analytics
- Data is not naturally connected
- Scale requirements exceed graph database capacity

#### Popular Options
| Database | Best For |
| --- | --- |
| Neo4j | General purpose graph, Cypher query language |
| Amazon Neptune | Managed graph on AWS |
| ArangoDB | Multi-model including graph |
| JanusGraph | Distributed graph, scales horizontally |

#### Example Use Cases
- **Social networks:** Friends, followers, connections
- **Recommendation engines:** "People who bought X also bought Y"
- **Fraud detection:** Finding suspicious patterns in transactions
- **Knowledge graphs:** Entity relationships

"For the 'People You May Know' feature, I would use Neo4j. We need to find friends-of-friends, which is a 2-hop traversal. Neo4j handles this efficiently with its native graph storage. In a relational database, this would require expensive self-joins on a large table."

### Search Engines
Search engines are optimized for full-text search and complex queries on text data.

#### When to Use
- Full-text search
- Fuzzy matching, typo tolerance
- Faceted search and filtering
- Log analysis and monitoring
- Search suggestions and autocomplete

#### When NOT to Use
- Primary data storage (use as secondary index)
- Transactional data
- Simple key-value lookups
- Strong consistency requirements

#### Popular Options
| Database | Best For |
| --- | --- |
| Elasticsearch | Full-text search, logging, analytics |
| Apache Solr | Enterprise search |
| Algolia | Managed search-as-a-service |
| Meilisearch | Lightweight, fast search |

#### Example Use Cases
- **Product search:** Search across product names, descriptions
- **Log analysis:** Querying application logs
- **Autocomplete:** Search suggestions as users type

"For product search, I would add Elasticsearch as a secondary index. The primary product data lives in PostgreSQL, but we sync to Elasticsearch for search. Elasticsearch gives us fuzzy matching for typos, faceted filtering by category and price, and relevance scoring."

### Time-Series Databases
Time-series databases are optimized for storing and querying timestamped data.

#### When to Use
- Metrics and monitoring data
- IoT sensor data
- Financial data with timestamps
- Need efficient time-range queries

#### When NOT to Use
- General application data
- Complex relationships
- Transaction processing

#### Popular Options
| Database | Best For |
| --- | --- |
| InfluxDB | Metrics, monitoring, IoT |
| TimescaleDB | PostgreSQL extension for time-series |
| Prometheus | Metrics and alerting |
| Amazon Timestream | Managed time-series on AWS |

#### Example Use Cases
- **Application metrics:** CPU, memory, request latency
- **IoT:** Sensor readings over time
- **Financial:** Stock prices, trading data

"For storing application metrics, I would use InfluxDB or TimescaleDB. We are writing millions of data points per second, and queries are always time-bounded like 'show me CPU usage for the last hour'. Time-series databases have optimized storage and query engines for this pattern."
# The Decision Framework
Use this framework in interviews to guide your database selection.

### Step-by-Step Decision Process
**Step 1: Identify the data requirements**
- What is the data structure?
- What are the access patterns?
- What scale do we need?
- What consistency is required?

**Step 2: Eliminate options that do not fit**
- Need ACID? Eliminate pure NoSQL options
- Need horizontal scaling? Eliminate single-node-only options
- Need graph queries? Eliminate non-graph databases

**Step 3: Compare remaining options**
- Consider operational complexity
- Consider team familiarity
- Consider cloud provider offerings

**Step 4: Make and justify your choice**
- State the decision clearly
- Explain why it fits the requirements
- Acknowledge trade-offs

# Using Multiple Databases
Modern systems often use multiple databases. This is called **polyglot persistence**.

### When to Use Multiple Databases
- Different data types have fundamentally different requirements
- One database cannot satisfy all access patterns efficiently
- Specific features require specialized databases (search, graph)

### Considerations
| Benefit | Trade-off |
| --- | --- |
| Optimized for each use case | Increased operational complexity |
| Better performance per workload | Data synchronization challenges |
| Independent scaling | Consistency across databases |

### Data Synchronization Patterns
**Change Data Capture (CDC):** Capture changes from the primary database and propagate to secondary stores.
**Dual Writes:** Write to multiple databases from the application. Risk of inconsistency if one write fails.
**Event-Driven:** Publish events on changes, consumers update their databases.

### In an Interview
"I am recommending a polyglot approach here. PostgreSQL is our source of truth for user and order data because we need transactions. Redis caches frequently accessed data for low latency. Elasticsearch powers search, synced via CDC from PostgreSQL. This adds complexity, but the performance benefits justify it at our scale."
# Common Mistakes to Avoid

#### Mistake 1: Choosing Based on Popularity
"Let's use MongoDB because it is popular."
Popularity does not mean it fits your use case.
**Fix:** Always start with requirements. What are the access patterns? What consistency do we need? Then pick the database that fits.

#### Mistake 2: Over-Engineering with Multiple Databases
Adding five different databases to show off knowledge creates unnecessary complexity.
**Fix:** Start simple. One database might be enough. Only add databases when you have clear, distinct requirements.

#### Mistake 3: Ignoring Operational Complexity
Cassandra scales well but requires expertise to operate.
**Fix:** Consider your team's capabilities. Managed services (RDS, DynamoDB, Atlas) reduce operational burden.

#### Mistake 4: Defaulting to NoSQL for "Scale"
NoSQL databases scale horizontally, but that does not mean relational databases cannot scale.
**Fix:** Understand that PostgreSQL with read replicas, connection pooling, and proper indexing handles significant scale. Use NoSQL when you genuinely need its properties, not just for scale.

#### Mistake 5: Not Acknowledging Trade-offs
Every database has limitations.
**Fix:** When you pick a database, acknowledge what you are giving up. "MongoDB gives us schema flexibility, but we lose JOIN support and strong transactions across documents."

#### Mistake 6: Forgetting About Existing Infrastructure
If the company already uses PostgreSQL, adding MongoDB introduces operational overhead.
**Fix:** In interviews, ask about existing infrastructure. "Is there an existing database I should consider, or can we choose freely?"
# Quick Reference Table
Use this table as a starting point:
| Use Case | Primary Choice | Alternatives |
| --- | --- | --- |
| User accounts, transactions | PostgreSQL | MySQL, SQL Server |
| Product catalog (varying schema) | MongoDB | PostgreSQL with JSONB |
| Session storage, caching | Redis | Memcached, DynamoDB |
| High-write time-series | Cassandra | InfluxDB, TimescaleDB |
| Full-text search | Elasticsearch | Algolia, PostgreSQL FTS |
| Social graph | Neo4j | PostgreSQL (simple cases) |
| Real-time analytics | ClickHouse | BigQuery, Redshift |
| Chat messages | Cassandra | DynamoDB, ScyllaDB |
| File metadata | MongoDB | PostgreSQL |
| Leaderboards | Redis | DynamoDB |

# Key Takeaways
1. **Start with requirements, not technology.** Understand access patterns, scale, and consistency needs before picking a database.
2. **Know the categories.** Understand when to use relational, document, key-value, wide-column, and graph databases.
3. **Justify your choice.** Do not just name a database. Explain why it fits the requirements and what trade-offs you are accepting.
4. **Consider polyglot persistence.** Different data types may need different databases. This is common in large systems.
5. **Acknowledge trade-offs.** Every database has limitations. Show you understand them.
6. **Think about operations.** Managed services reduce complexity. Team familiarity matters.
7. **Start simple.** One well-chosen database is often enough. Add complexity only when justified.
8. **Match the interview level.** Junior candidates should show basic understanding. Senior candidates should discuss trade-offs in depth and consider operational aspects.

Database selection is not about memorizing which database to use for each problem. It is about understanding the properties of different databases and matching them to your requirements. With practice, this becomes intuitive.
In your next mock interview, pay special attention to how you discuss databases. Can you explain why you chose that database? Can you articulate the trade-offs? That is what interviewers are looking for.
# References
- [Designing Data-Intensive Applications by Martin Kleppmann](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/) - The definitive guide to understanding database internals and distributed data
- [Database Internals by Alex Petrov](https://www.oreilly.com/library/view/database-internals/9781492040330/) - Deep dive into how databases work under the hood
- [System Design Interview by Alex Xu](https://www.amazon.com/System-Design-Interview-insiders-Second/dp/B08CMF2CQF) - Practical examples of database selection in system design
- [MongoDB vs PostgreSQL](https://www.mongodb.com/compare/mongodb-postgresql) - Official comparison of document vs relational approaches
- [When to use Cassandra vs PostgreSQL](https://www.datastax.com/blog/when-use-cassandra-vs-postgresql) - Wide-column vs relational trade-offs
- [Neo4j Graph Database Documentation](https://neo4j.com/docs/) - Understanding graph database use cases

# Quiz

## Choosing the Right Database Quiz
A system must ensure money transfers never create or lose funds, even during failures. Which database category best fits the core ledger?