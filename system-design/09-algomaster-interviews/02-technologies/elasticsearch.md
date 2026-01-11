# Elasticsearch Deep Dive for System Design Interviews

When a system design problem involves search, Elasticsearch is often the first technology that comes up. From powering e-commerce product search to aggregating billions of log events, Elasticsearch has become the default choice for search-heavy applications.
But knowing that Elasticsearch exists is not enough. Interviewers want to see that you understand **when** it makes sense (and when it does not), **how** its distributed architecture works under the hood, and **what** trade-offs you are making by choosing it. This deeper understanding separates candidates who can recite features from those who can actually design systems.
This chapter covers the practical knowledge you need: core concepts like inverted indexes and mappings, cluster architecture and shard distribution, query optimization patterns, and scaling strategies for both reads and writes.
By the end, you will be able to confidently propose Elasticsearch when appropriate, design efficient schemas and queries, and discuss its limitations honestly.

### Elasticsearch Architecture Overview
Client applications (App Server 1..N) send all requests (indexing and search) to a **coordinating node**. The coordinating node is the cluster’s entry point: it parses the request, figures out which shards are involved, fans the work out to the right data nodes, and then merges results before returning the response.
Elasticsearch separates responsibilities inside the cluster:
- **Master nodes (M1–M3)** form a quorum and manage the **cluster state**: index metadata, shard placement, node membership, and allocation decisions. They do not serve the bulk of query/index traffic. Their job is to keep the cluster organized and consistent from a control-plane perspective.
- **Data nodes (D1–D3)** store the actual index shards. Each index is split into **primary shards (P0, P1, P2)** and **replica shards (R0, R1, R2)** distributed across nodes for both scale and availability.

The dotted “Cluster State” link indicates that data nodes rely on the masters for the latest routing/allocation information. 
**Net effect:** coordinating nodes handle request routing and result merging, master nodes manage cluster metadata and shard allocation, and data nodes execute searches and store/replicate shards for performance and resilience.
# 1. When to Choose Elasticsearch
Every technology choice in a system design interview requires justification. Elasticsearch is powerful, but it is also operationally complex and adds moving parts to your architecture.
Understanding when it genuinely solves a problem versus when simpler alternatives exist shows mature engineering judgment.

### 1.1 Where Elasticsearch Excels
Elasticsearch was built for search, and that remains its core strength. If your system needs to find relevant results from large amounts of unstructured text, Elasticsearch provides the building blocks: tokenization breaks text into searchable terms, stemming handles word variations (running, ran, runs), fuzzy matching tolerates typos, and relevance scoring ranks results by how well they match the query.
Beyond basic search, Elasticsearch handles several related use cases well:
**Log and event analytics** is perhaps its most common deployment. The ELK stack (Elasticsearch, Logstash, Kibana) has become the industry standard for aggregating logs from distributed systems and making them searchable. When you need to query across millions of log entries to debug a production issue, Elasticsearch delivers.
**Autocomplete and suggestions** require matching partial input against a large corpus in real-time. Features like completion suggesters and edge n-grams make this straightforward.
**Faceted search** powers the filter sidebars you see on e-commerce sites. Show all laptops, then let users narrow by brand, price range, screen size, and rating. Elasticsearch handles both the filtering and the count aggregations for each facet.
**Real-time analytics** over large datasets is possible because aggregations run directly on the indexed data. Dashboards can show live metrics without pre-computing everything.
**Geospatial search** is built in. Finding restaurants within 5 miles or stores in a bounding box requires no additional infrastructure.

### 1.2 When Elasticsearch Is the Wrong Choice
Knowing when not to use a technology is just as important as knowing when to use it. Elasticsearch has real limitations that you should acknowledge in interviews.

#### Never use it as your primary data store
Elasticsearch is not a database in the traditional sense. It lacks ACID transactions, and during failures or split-brain scenarios, data can be lost. Always keep your source of truth in a proper database (PostgreSQL, MySQL, DynamoDB) and sync to Elasticsearch for search.

#### Skip it for simple key-value lookups
If your access pattern is just "get document by ID," you are adding unnecessary complexity. Redis or DynamoDB will be faster and simpler.

#### Think twice if you have heavy update workloads
Elasticsearch is optimized for append-heavy patterns. Under the hood, it uses immutable segments, so an "update" actually means deleting the old document and indexing a new one. Frequent updates to the same documents cause segment fragmentation and force expensive merge operations.

#### Do not expect strong consistency
Elasticsearch is eventually consistent by design. After indexing a document, there is a delay (typically one second) before it appears in search results. If your application requires immediate read-after-write consistency, this is a fundamental mismatch.

#### Avoid it for complex relational queries
While Elasticsearch supports nested objects and parent-child relationships, it is not designed for the kind of multi-table joins that relational databases handle efficiently.

#### Question whether you need it for small datasets
If you have a few million records and moderate query volume, PostgreSQL with GIN indexes for full-text search might be sufficient. The operational overhead of running an Elasticsearch cluster is not free.

### 1.3 Common Interview Systems Using Elasticsearch
| System | Why Elasticsearch Works |
| --- | --- |
| E-commerce Search | Full-text search, faceted filtering, autocomplete |
| Log Analytics | High ingestion rate, time-based queries, aggregations |
| Content Search | Relevance ranking, highlighting, multi-language support |
| Autocomplete | Completion suggesters, edge n-grams |
| Geospatial Search | Geo queries, distance filtering, bounding box |
| Metrics Dashboard | Real-time aggregations, time-series data |
| Recommendation Engine | More-like-this queries, vector similarity |

**In interviews:** When proposing Elasticsearch, connect specific features to your requirements. 
Saying "we need search, so Elasticsearch" is weak. Saying "we need full-text search with typo tolerance, faceted filtering for the sidebar, and aggregations for the filter counts, all of which Elasticsearch provides natively" shows you understand both the problem and the tool.
# 2. Core Concepts
Before diving into queries and scaling, you need to understand how Elasticsearch organizes and stores data. These concepts form the foundation for everything that follows, from schema design decisions to query optimization strategies.

### 2.1 Documents and Indices
Everything in Elasticsearch starts with documents. A **document** is a JSON object representing a single record, whether that is a product, a log entry, or a user profile.
Documents are grouped into **indices**. An index is a collection of documents that share similar characteristics, roughly analogous to a table in a relational database. The key difference is that Elasticsearch indices do not require a fixed schema upfront, though defining one explicitly is strongly recommended for production use.

### 2.2 Mappings
While Elasticsearch can infer field types automatically (dynamic mapping), relying on this in production leads to problems. A field that looks like a date might get mapped as text. A numeric ID might become a number when you wanted a keyword. Explicit mappings give you control over how each field is indexed and searched.

### 2.3 Field Types
| Type | Use Case | Indexed For |
| --- | --- | --- |
| text | Full-text search | Analyzed, tokenized |
| keyword | Exact matches, aggregations | Not analyzed |
| integer, float, long | Numeric data | Range queries |
| date | Timestamps | Range and date math |
| boolean | True/false flags | Filtering |
| geo_point | Latitude/longitude | Geo queries |
| nested | Arrays of objects | Preserves object boundaries |
| object | JSON objects | Flattened internally |

### 2.4 Text vs Keyword
This distinction is one of the most important concepts in Elasticsearch, and understanding it will help you design better schemas. The choice between text and keyword determines whether a field is analyzed (broken into tokens) or stored exactly as-is.
**Text fields** go through an analysis pipeline. The analyzer breaks the text into individual tokens, lowercases them, and may apply stemming or other transformations.
This means a search for "brown" will match the document, even though the original text was "Quick Brown Fox."
**Keyword fields** store the exact value without any processing.
A search for "brown" will not match. Only a search for the exact string "Quick Brown Fox" will.
The right choice depends on how you need to query the field:
| Scenario | Field Type | Reason |
| --- | --- | --- |
| Product description | text | Users search with partial words |
| Category filter | keyword | Exact match for filtering/aggregation |
| Email address | keyword | Always exact match |
| Article body | text | Full-text search |
| Status field | keyword | Limited set of exact values |
| User search query | text | Needs tokenization |

**Multi-field mapping** gives you the best of both worlds. When you need to both search within a field and aggregate on it, define it as text with a keyword sub-field:
Now you can search on `category` and aggregate on `category.raw`.

### 2.5 Inverted Index
The inverted index is the data structure that makes Elasticsearch fast at full-text search. If you have used an index at the back of a textbook, you already understand the concept: instead of scanning every page to find where "photosynthesis" appears, you look it up in the index and jump directly to the relevant pages.
Elasticsearch works the same way. When you index a document, it analyzes the text into tokens and records which documents contain each token.
When you search for "brown fox," Elasticsearch looks up both terms in the inverted index, finds that "brown" appears in documents 1 and 3 while "fox" appears in documents 1 and 2, and intersects these lists to find document 1 as the best match.
This structure enables several key capabilities:
- **Fast term lookup**: Finding which documents contain a term is O(1), not O(n) where n is the number of documents.
- **Efficient boolean operations**: AND, OR, and NOT queries become set intersections and unions on posting lists.
- **Phrase queries**: The inverted index also stores position information, so Elasticsearch can verify that terms appear adjacent to each other.

Understanding the inverted index also explains one of Elasticsearch's limitations. Because segments are immutable, updates are actually delete-then-reinsert operations. Frequent updates to the same documents are expensive because they create new segments that eventually need to be merged.
# 3. Cluster Architecture
Unlike databases that were later retrofitted for distribution, Elasticsearch was built as a distributed system from the start. This means horizontal scaling and high availability are native capabilities, not afterthoughts. Understanding how the cluster works helps you design for reliability and make informed capacity planning decisions.

### 3.1 Nodes and Clusters
An Elasticsearch **cluster** is a collection of nodes that work together to store data and serve queries. The cluster automatically distributes data across nodes and handles node failures. Each cluster has a unique name, and nodes use this name to discover and join the cluster.
A **node** is a single Elasticsearch instance. In production, you typically run one node per server or container. Nodes can be assigned different roles based on their responsibilities:
| Role | Responsibility |
| --- | --- |
| Master | Cluster management, index creation, shard allocation |
| Data | Stores data, executes searches and aggregations |
| Ingest | Pre-processes documents before indexing |
| Coordinating | Routes requests, aggregates results |
| ML | Machine learning jobs (paid feature) |

**Production setup:**
- 3 dedicated master nodes (for quorum)
- Multiple data nodes (based on data volume)
- Optional coordinating nodes (for query-heavy workloads)

### 3.2 Shards and Replicas
Sharding is how Elasticsearch scales horizontally. Instead of storing all documents of an index on a single node, Elasticsearch splits the index into multiple **primary shards** and distributes them across data nodes.
When you index a document, Elasticsearch hashes the document ID (or a custom routing value) and uses that hash to determine which shard receives the document. This ensures even distribution across shards.
**Replica shards** are copies of primary shards that serve two purposes: high availability (if a node fails, the replica can be promoted to primary) and read scaling (queries can be served by either primary or replica).
**Shard routing formula:**
There are a few critical facts about shards that come up frequently in interviews:
- **Primary shard count is fixed at index creation.** You cannot add more primary shards to an existing index without reindexing. This is why capacity planning matters.
- **Replica count can be changed dynamically.** Adding replicas only requires copying existing data, so you can scale read capacity on the fly.
- **Each shard is a self-contained Lucene index.** This is why there is overhead per shard (memory, file handles, segment merging).
- **More shards enable parallelism but add overhead.** There is no free lunch. Choose shard count based on expected data size, not just "more is better."

### 3.3 Shard Sizing Guidelines
| Factor | Recommendation |
| --- | --- |
| Shard size | 10-50 GB per shard |
| Shards per node | < 20 shards per GB of heap |
| Total shards | Avoid small shards (overhead) |
| Growth planning | Slightly overshoot for growth |

**Example calculation:**

### 3.4 Document Routing
By default, Elasticsearch routes documents to shards based on a hash of the document ID. This provides even distribution but means that documents for the same customer, tenant, or category end up scattered across all shards.
Custom routing lets you co-locate related documents on the same shard:
With this approach, all orders for `customer_456` land on the same shard. When you later query for that customer's orders, the query only needs to hit one shard instead of all of them.
**The benefit** is reduced scatter-gather overhead. Instead of querying all shards and merging results, you query a single shard directly.
**The trade-off** is potential data skew. If one customer has far more orders than others, their shard becomes a hot spot. You also must remember to include the routing parameter in every operation, or documents will land in the wrong place.

### 3.5 Write and Read Flow
**Write flow:**
1. Client sends document to coordinating node
2. Coordinating node routes to primary shard
3. Primary indexes document, forwards to replicas
4. Replicas acknowledge
5. Primary acknowledges to coordinating node

**Read flow:**
1. Query phase: Each shard returns matching document IDs and scores
2. Fetch phase: Coordinating node fetches actual documents from relevant shards
3. Results merged and returned

# 4. Indexing and Analysis
The quality of your search results depends heavily on how you analyze text. A user searching for "running shoes" should match products described as "runner's footwear." This kind of intelligent matching does not happen automatically. It requires thoughtful analyzer configuration.

### 4.1 Analysis Pipeline
When Elasticsearch indexes a text field, the text passes through an analysis pipeline that transforms it into searchable tokens:
Each stage serves a specific purpose:
| Component | Purpose | Example |
| --- | --- | --- |
| Character Filters | Pre-process raw text before tokenization | Strip HTML tags, replace accented characters |
| Tokenizer | Split text into individual tokens | Standard tokenizer splits on whitespace and punctuation |
| Token Filters | Modify, add, or remove tokens | Lowercase, stem words, add synonyms, remove stop words |

The same pipeline runs at query time, which is why the query "Running" matches a document containing "run." Both are analyzed to the same token.

### 4.2 Built-in Analyzers
Elasticsearch provides several pre-configured analyzers for common use cases.
**Standard Analyzer** (the default) handles most Western languages well:
It uses grammar-based tokenization (recognizing word boundaries) and lowercases everything. Punctuation is stripped, and the result is searchable tokens.
**English Analyzer** goes further with language-specific processing:
Stemming reduces words to their root form ("running" becomes "run"), so a search for "runs" matches "running." It also removes common English stop words like "the," "is," and "a."
**Keyword Analyzer** does no tokenization at all:
The entire input becomes a single token. This is useful when you want exact matching, like for product SKUs or status codes.

### 4.3 Custom Analyzers
When built-in analyzers do not meet your needs, you can assemble custom ones from components. This is common when you need domain-specific synonyms or special tokenization rules.

### 4.4 Autocomplete with Edge N-grams
Autocomplete is one of the most common search features, and it requires a specific indexing strategy. When a user types "lap," you want to match "laptop" instantly. Edge n-grams make this possible by indexing prefixes of each term:
The key insight here is using **different analyzers for indexing and searching**. At index time, edge n-grams create prefixes like "la," "lap," "lapt." At search time, you use the standard analyzer so that the query "lap" remains as "lap" (not further broken into "l," "la"). This way, "lap" matches the indexed token "lap" directly.

### 4.5 Indexing Best Practices
When indexing large amounts of data, a few optimizations can dramatically improve throughput.
**Use the bulk API instead of single-document indexing.** Each individual index request has network overhead. The bulk API batches thousands of operations into a single request:
Batch sizes of 1,000 to 5,000 documents typically work well, but profile with your specific document size.
**Increase the refresh interval during bulk loads.** By default, Elasticsearch refreshes the index every second, making new documents searchable. During initial data loading, this frequent refresh is wasteful:
For very large initial loads, you can disable refresh entirely with `-1` and manually refresh after the load completes.
**Disable replicas during bulk load.** Replicas multiply write work since every document must be written to both primary and replica shards:
Re-enable replicas after the bulk load finishes. Elasticsearch will copy the data to the new replicas.
**Use index templates for consistent configuration.** When you have multiple indices (like time-based log indices), templates ensure they all get the same settings and mappings:
# 5. Query DSL
Elasticsearch's Query DSL (Domain Specific Language) is how you express search queries. It is a JSON-based syntax that lets you combine full-text search, exact matching, filtering, and scoring in flexible ways. Knowing the major query types and when to use each is essential for both interviews and real implementations.

### 5.1 Query Types Overview

### 5.2 Full-Text Queries
Full-text queries analyze the search text the same way documents were analyzed at index time. This is how "wireless mouse" matches a product description that says "2.4GHz wireless optical mouse."
**Match Query** is the workhorse of full-text search:
Elasticsearch analyzes "wireless mouse" into tokens, then finds documents containing any of those tokens. Results are ranked by relevance, with documents containing both terms scoring higher than those with just one.
**Match Phrase** requires terms to appear in exact order and adjacent positions:
This will match "wireless mouse" but not "wireless optical mouse" (terms not adjacent) or "mouse wireless" (wrong order).
**Multi-Match** searches across multiple fields at once:
The `^3` boosts the name field, so matches in the product name score 3x higher than matches in the description. The `type` parameter controls how scores from different fields are combined: `best_fields` takes the highest-scoring field, `most_fields` sums all field scores, and `cross_fields` treats all fields as one big field.

### 5.3 Term-Level Queries
Unlike full-text queries, term-level queries look for exact values without any analysis. Use these for keyword fields, numbers, dates, and booleans.
**Term Query** matches an exact value:
This looks for the exact string "active" in the status field. If you accidentally use a term query on a text field, it will likely fail because the indexed tokens are lowercase while your query is not analyzed.
**Range Query** finds values within bounds:
Works for numbers, dates, and even strings (lexicographic comparison).
**Terms Query** is like SQL's IN clause:
Matches documents where the category is either "electronics" or "computers."

### 5.4 Boolean Queries
Real queries almost always combine multiple conditions. The `bool` query is how you express AND, OR, and NOT logic:
This query means: find laptops (must match "laptop" in name), that are in stock and under $1000 (filters), preferably featured (should), but not discontinued (must_not).
| Clause | Effect | Scoring |
| --- | --- | --- |
| must | Required, contributes to score | Yes |
| filter | Required, no scoring (faster) | No |
| should | Optional, boosts score if matched | Yes |
| must_not | Excluded | No |

The distinction between `must` and `filter` is critical for performance. Both require the condition to match, but `must` computes relevance scores while `filter` does not. Since filters skip scoring, they can be cached and reused across queries.
**Rule of thumb:** Use `filter` for yes/no conditions (in stock? price under $100? category equals X?) and `must` for relevance-based matching (does the description match the search terms?).

### 5.5 Fuzzy and Prefix Queries
**Fuzzy Query (typo tolerance):**
- AUTO: 0 edits for 1-2 chars, 1 edit for 3-5 chars, 2 edits for 5+ chars

**Prefix Query:**

### 5.6 Relevance Scoring
Elasticsearch ranks results by relevance using the BM25 algorithm. Understanding scoring helps you tune search quality and explain your ranking decisions in interviews.
BM25 scoring considers three main factors:
- **TF (Term Frequency)**: A document mentioning "laptop" five times is likely more relevant than one mentioning it once.
- **IDF (Inverse Document Frequency)**: Common words like "the" add little value. Rare terms like "ThinkPad" are more discriminating.
- **Field length normalization**: Finding "laptop" in a 5-word product name is more significant than finding it in a 500-word description.

**Boosting** lets you weight fields differently:
Matches in the name field contribute 3x more to the score than matches in the description.
**Function Score** incorporates non-text factors like popularity or recency:
This multiplies the text relevance score by a function of the popularity field. A mediocre text match on a very popular product might rank higher than a perfect text match on an obscure one.
# 6. Aggregations and Analytics
Aggregations let you compute summaries over your data: how many products in each category, average price per brand, order volume over time. They run alongside queries, so you can filter down to a subset of documents and then aggregate within that subset. This is what powers the filter counts on e-commerce sidebars and the charts in analytics dashboards.

### 6.1 Aggregation Types

### 6.2 Bucket Aggregations
Bucket aggregations group documents into buckets based on field values, ranges, or other criteria. Each bucket contains the documents that match its criteria, along with a document count.
**Terms Aggregation** is the foundation of faceted search:
Response:
**Range Aggregation:**
**Date Histogram:**

### 6.3 Metric Aggregations
While bucket aggregations group documents, metric aggregations calculate numerical values from document fields: sums, averages, minimums, maximums, and percentiles.
**Stats Aggregation** computes multiple metrics in one request:
Response:
**Cardinality (unique count):**

### 6.4 Nested Aggregations
The real power of aggregations comes from nesting them. You can bucket documents by category, then compute average price within each category, then further break down by price range:
This returns average price and price distribution per category.

### 6.5 Faceted Search Pattern
A typical e-commerce search page combines full-text search, filtering, and faceted navigation. Here is how it all comes together:
**Post-filter pattern:** There is a subtle UX problem with the query above. When a user filters by Dell, the brand aggregation also filters, showing only Dell. But users expect to see counts for all brands so they can click a different one.
The `post_filter` solves this by applying the filter after aggregations run:
Now the aggregation sees all laptops (showing counts for Dell, HP, Lenovo, etc.), while the actual results are filtered to only Dell products.
**In interviews:** Understanding post_filter demonstrates that you have actually built faceted search, not just read about it. Mention it when discussing e-commerce search: "I use post_filter for brand and category facets so users see counts for all options even when filters are active. This lets them easily switch between brands without clearing their filter first."
# 7. Scaling and Performance
Scaling questions are common in interviews because they test whether you understand the architecture well enough to reason about bottlenecks. Elasticsearch scales reads and writes differently, and knowing which lever to pull for which problem is essential.

### 7.1 Read Scaling
Read capacity scales by adding replicas. Each replica is a full copy of the data that can independently serve queries.
With two replicas, you have three copies of each shard (one primary, two replicas). Elasticsearch distributes incoming queries across all copies using adaptive replica selection, which routes to the replica with the lowest response time.
This provides near-linear read scaling: doubling replicas roughly doubles read capacity. The trade-off is storage cost (each replica consumes the same disk space as the primary) and write overhead (every document must be written to all replicas).

### 7.2 Write Scaling
Write capacity scales by adding primary shards, but there is a catch: **you must set the primary shard count at index creation time.** You cannot add more primary shards to an existing index without reindexing.
With 10 primary shards spread across 5 data nodes, writes distribute across multiple nodes and can proceed in parallel. More shards enable more write parallelism.
However, there is no free lunch. Each shard is a Lucene index with its own memory overhead, file handles, and segment merge operations. Too many small shards waste resources. The general guideline is shards between 10GB and 50GB each.

### 7.3 Performance Tuning
Beyond scaling hardware, several query-level optimizations can significantly improve performance.
**Use filter context for non-scoring queries.** As mentioned earlier, filter clauses skip scoring and can be cached:
The first time this runs, it computes the matching documents. Subsequent queries with the same filters reuse the cached result.
**Limit returned fields.** By default, Elasticsearch returns the entire `_source` document. If you only need a few fields for display, specify them:
This reduces network transfer and parsing overhead, especially for documents with large text fields.
**Handle pagination carefully.** The default `from`/`size` pagination works fine for the first few pages, but deep pagination is expensive:
To return results 10,000-10,020, Elasticsearch must fetch and sort 10,020 documents from each shard, merge them, and discard the first 10,000. For deep pagination, use `search_after` instead:
This uses the sort values from the last document of the previous page to efficiently fetch the next page.
**Use the scroll API for bulk exports.** When you need to process all matching documents (for a data export or migration), scroll maintains a consistent snapshot:
Use the returned scroll ID to fetch subsequent batches until the results are exhausted.

### 7.4 Caching
Elasticsearch uses multiple caches to avoid redundant work.
**Query cache** stores filter results at the shard level. When you run a filter for `status = active`, the matching document set is cached. Subsequent queries with the same filter reuse this result without re-executing the filter. The cache is automatically invalidated when the index refreshes (new documents become visible).
**Request cache** stores entire search responses. This is useful for aggregation-heavy queries where the underlying data changes infrequently:
For dashboards showing metrics over historical data, the request cache can dramatically reduce load.
**Field data cache** enables sorting and aggregations on text fields by loading all unique values into memory. This is expensive and should generally be avoided. Use keyword fields for aggregations instead.

### 7.5 Monitoring Key Metrics
| Metric | Healthy Range | Action if Exceeded |
| --- | --- | --- |
| Search latency (p99) | < 200ms | Add replicas, optimize queries |
| Indexing latency | < 50ms | Increase refresh interval, bulk API |
| JVM heap usage | < 75% | Add nodes or increase heap |
| Disk usage | < 85% | Add nodes, delete old indices |
| Search queue | < 100 | Add coordinating nodes |

# 8. Index Management Strategies
For time-series data like logs and metrics, managing indices over time is as important as the queries themselves. A naive approach (one giant index that grows forever) leads to degraded performance, difficult maintenance, and no way to implement retention policies. The patterns in this section are standard practice for production log analytics systems.

### 8.1 Time-Based Indices
Instead of one ever-growing index, create a new index for each time period (typically daily):
This pattern provides several operational advantages:
- **Easy retention management.** Deleting a 90-day-old index is a single API call, far cheaper than deleting individual documents.
- **Optimized shard sizes.** Each daily index can be sized appropriately for that day's volume.
- **Faster date-filtered searches.** A query for today's logs only hits today's index, not the entire history.

### 8.2 Index Aliases
With time-based indices, your application would need to know which index to write to and which indices to read from. Aliases abstract this away:
Your application writes to `logs-write` (always the current index) and reads from `logs-read` (all indices). When a new day starts, you update the alias to point to the new index without changing application code.
**Rollover API** automates index creation based on conditions:
When any condition is met, Elasticsearch creates a new index and atomically switches the write alias to it. This ensures indices stay within optimal size bounds even if daily volume varies.

### 8.3 Index Lifecycle Management (ILM)
ILM automates the entire lifecycle of an index, from high-performance storage for recent data to archival and eventual deletion. This is essential for cost optimization in log analytics systems.

### 8.4 Reindex API
Modify existing data or migrate to new mappings:
**Use cases:**
- Change field mappings
- Split or merge indices
- Migrate to new analyzers

### 8.5 Snapshot and Restore
Backup indices to external storage:
Restore from snapshot:
# 9. Elasticsearch vs Other Databases
Interviewers often ask you to justify choosing Elasticsearch over alternatives or explain when you would choose something else. These comparisons help you make the right technology choice and defend it convincingly.

### 9.1 Elasticsearch vs PostgreSQL Full-Text Search
| Aspect | Elasticsearch | PostgreSQL FTS |
| --- | --- | --- |
| Setup complexity | Separate cluster | Built into DB |
| Scaling | Horizontal (native) | Vertical (manual sharding) |
| Query capabilities | Rich DSL, fuzzy, suggestions | GIN indexes, ts_query |
| Real-time | Near real-time (1s) | Immediate |
| Aggregations | Rich analytics | SQL aggregates |
| Operational overhead | Higher | Lower |

**Choose Elasticsearch:** High query volume, complex search features, large scale.
**Choose PostgreSQL FTS:** Simpler deployments, already using PostgreSQL, moderate search needs.

### 9.2 Elasticsearch vs Solr
| Aspect | Elasticsearch | Solr |
| --- | --- | --- |
| Architecture | Distributed-first | Added clustering later |
| API | REST/JSON native | Multiple formats |
| Real-time search | Yes | Soft commits |
| Analytics | Aggregations | Faceting |
| Ease of use | Simpler setup | More configuration |
| Community | Larger, more active | Mature, Apache |

**Choose Elasticsearch:** New projects, JSON-native, analytics focus.
**Choose Solr:** Existing Solr deployments, specific Solr features needed.

### 9.3 Elasticsearch vs Algolia
| Aspect | Elasticsearch | Algolia |
| --- | --- | --- |
| Deployment | Self-managed or Cloud | Fully managed only |
| Customization | Full control | Limited configuration |
| Latency | Depends on setup | Optimized globally |
| Cost | Infrastructure-based | Per-search pricing |
| Features | Full DSL | Typo-tolerance, ranking |

**Choose Elasticsearch:** Custom requirements, cost control at scale, analytics.
**Choose Algolia:** Fast implementation, global low latency, limited engineering resources.

### 9.4 Elasticsearch vs OpenSearch
| Aspect | Elasticsearch | OpenSearch |
| --- | --- | --- |
| License | Elastic License 2.0 | Apache 2.0 |
| Features | Latest features first | Fork, follows behind |
| Cloud | Elastic Cloud | AWS OpenSearch |
| Support | Elastic | AWS, community |

**Choose Elasticsearch:** Need latest features, Elastic Cloud integration.
**Choose OpenSearch:** AWS ecosystem, Apache license requirement.
# Summary
Elasticsearch appears frequently in system design interviews because search is a fundamental feature of most user-facing applications. To use it effectively in interviews, you need more than surface-level knowledge.
**Know when Elasticsearch is the right choice** and when it is not. It excels at full-text search, faceted navigation, autocomplete, and log analytics. It struggles as a primary data store, with heavy update workloads, or when you need strong consistency.

#### Understand the core data model
Documents are JSON objects stored in indices. Mappings define how fields are indexed. The inverted index is why search is fast. Text fields are analyzed into tokens, keyword fields are stored exactly.

#### Design clusters for reliability
Three dedicated master nodes prevent split-brain. Replicas provide high availability and read scaling. Shard sizing (10-50 GB per shard) balances parallelism with overhead.

#### Write effective queries
Match queries for full-text, term queries for exact values, bool queries to combine conditions. Use filter context for non-scoring conditions since filters are cached and faster.

#### Use aggregations for analytics
Terms aggregations power faceted search. Range and date_histogram aggregations enable dashboards. Post_filter lets you show all facet options while filtering results.

#### Scale based on the bottleneck
Add replicas to scale reads, add primary shards (at index creation) to scale writes. Profile before optimizing to identify whether you are CPU-bound, I/O-bound, or memory-bound.

#### Manage time-series data with ILM
Daily indices, hot/warm/cold tiers, and automated rollover and deletion. This pattern is essential for log analytics at scale.
When you propose Elasticsearch in an interview, connect specific features to your requirements and acknowledge the limitations. Demonstrating that you understand the trade-offs matters more than knowing every API parameter.
# References
- [Elasticsearch Official Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html) - Comprehensive guide covering all Elasticsearch features and APIs
- [Elasticsearch: The Definitive Guide](https://www.elastic.co/guide/en/elasticsearch/guide/current/index.html) - Classic book explaining Elasticsearch concepts in depth
- [Relevant Search](https://www.manning.com/books/relevant-search) - Manning book on building great search experiences with Elasticsearch and Solr
- [Designing Data-Intensive Applications](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/) - Martin Kleppmann's coverage of search systems and distributed architectures
- [Elasticsearch Engineering Blog](https://www.elastic.co/blog/category/engineering) - Real-world case studies and best practices from Elastic

# Quiz

## Elasticsearch Quiz
In a typical Elasticsearch cluster, which node role is primarily responsible for routing a client search request to the right shards and merging the results?