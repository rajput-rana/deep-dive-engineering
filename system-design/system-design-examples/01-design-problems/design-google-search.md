# Design Google Search

A web search engine is a system that crawls the internet, indexes web pages, and returns relevant results in response to user queries. It enables users to find information across billions of web pages in milliseconds.
The core challenge is scale. The web contains hundreds of billions of pages, users expect results in under 500 milliseconds, and the content is constantly changing. A search engine must continuously discover new pages, understand their content, determine their importance, and serve relevant results to millions of concurrent users.
**Popular Examples:** Google Search, Bing, DuckDuckGo, Baidu, Yandex
What makes this problem fascinating from a system design perspective is its breadth. It is arguably one of the most comprehensive system design problems you can encounter.
Building a search engine touches on nearly every area of distributed systems: web crawling at massive scale, distributed storage for petabytes of data, information retrieval algorithms, machine learning for ranking, and low-latency serving infrastructure. 
In this chapter, we will explore the **high-level design of a web search engine like Google Search**.
Let's start by clarifying the requirements:
# 1. Clarifying Requirements
Before diving into architecture, we need to understand what we are actually building. 
A web search engine can mean different things to different people. Are we building a general-purpose search engine like Google, or a specialized search for a particular domain? How fresh do the results need to be? What latency is acceptable? These questions shape every decision we make.
Let's walk through a typical requirements discussion you might have in an interview:
**Candidate:** "What is the scale we're designing for? How many web pages and how many queries?"
**Interviewer:** "Assume we need to index 100 billion web pages and handle 100,000 search queries per second at peak."
**Candidate:** "How fresh does the index need to be? Should we reflect changes to popular sites quickly?"
**Interviewer:** "Popular and frequently changing pages should be re-crawled within hours. Less important pages can be updated weekly or monthly."
**Candidate:** "What latency is acceptable for search results?"
**Interviewer:** "Results should be returned within 500 milliseconds at the 99th percentile, including network latency."
**Candidate:** "Should we support advanced features like spell correction, autocomplete, or personalization?"
**Interviewer:** "Spell correction and basic autocomplete are expected. Personalization is nice-to-have but not required for this discussion."
**Candidate:** "How do we handle malicious content, spam, or low-quality pages?"
**Interviewer:** "The system should have mechanisms to detect and demote spam. Quality signals are important for ranking."
**Candidate:** "Do we need to support different content types like images, videos, or news?"
**Interviewer:** "Focus on web page search. Assume other verticals like images and videos are separate systems."
This conversation reveals several key constraints. We need to handle massive scale (100 billion pages, 100K QPS), provide fast responses (under 500ms), keep popular content fresh (hours, not days), and maintain quality despite the web's noisy nature. Let's formalize these into requirements.

## 1.1 Functional Requirements
Based on our discussion, here are the core capabilities our search engine must provide:
- **Web Crawling:** Continuously discover and fetch web pages from across the internet.
- **Indexing:** Process crawled pages and build a searchable index.
- **Query Processing:** Parse user queries and retrieve relevant documents.
- **Ranking:** Order results by relevance using content and link-based signals.
- **Spell Correction:** Suggest corrections for misspelled queries.
- **Snippet Generation:** Show relevant excerpts from matching pages.

## 1.2 Non-Functional Requirements
Beyond features, we need to think about the qualities that make the system production-ready at Google scale:
- **Low Latency:** p99 query latency under 500ms.
- **High Throughput:** Handle 100,000 queries per second at peak.
- **Freshness:** Popular pages re-indexed within hours, others within days/weeks.
- **Scalability:** Index 100+ billion web pages.
- **High Availability:** 99.99% uptime for the search serving layer.
- **Spam Resistance:** Detect and demote low-quality or malicious content.

# 2. Back-of-the-Envelope Estimation
Before designing the architecture, let's do some quick math to understand the scale we are dealing with. These numbers will guide our decisions about storage, caching, and infrastructure. They also help us sanity-check our design as we go.

### 2.1 Web Page Storage
Let's start with the raw data we need to store.

#### Crawled Content:
We are indexing 100 billion web pages. The average web page, once we strip out boilerplate and compress the HTML, is about 100 KB. Some pages are tiny (a few KB), while others are large (several MB), but 100 KB is a reasonable average.
Ten petabytes is a lot, but not unmanageable for a company operating at this scale. This data lives in a distributed file system, partitioned across thousands of machines.

#### Index Size:
The inverted index, which maps terms to documents, is more compact than the raw data. After processing and compression, it is typically 20-30% of the raw content size.
But we do not store just one copy. We need replication for durability and multiple copies in different data centers for low-latency global serving.

### 2.2 Crawling Bandwidth
The crawler needs to continuously fetch new pages and refresh existing ones. Let's estimate the required crawl rate.
We want to refresh about 1 billion pages per day (a mix of frequently and infrequently changing pages). Some pages we crawl every few hours, others once a month, but on average this works out to about 1 billion pages daily.
At 100 KB per page:
That is about 9.2 Gbps of sustained inbound traffic just for crawling. This requires significant network infrastructure and distributed crawling across many machines and geographic locations.

### 2.3 Query Traffic
Now let's look at the serving side. This is where latency matters most.

#### Query Volume:
For context, Google reportedly handles over 8.5 billion searches per day, so our 4.3 billion is a reasonable simplified estimate.

#### Response Size:
A typical search response includes 10 results, each with a title, URL, and snippet. Plus some metadata and related searches. Call it roughly 10-20 KB per response.

### 2.4 Hardware Estimation
Let's estimate how many machines we need for the serving layer.
If each serving node can handle 1,000 QPS (assuming adequate caching of hot queries), we need:
This is per region. For global coverage with low latency, we might have 5-10 regions, each with its own set of serving nodes and a copy of the index. That is 500-1,000 serving nodes globally.
For index storage, we need thousands of machines to hold petabytes of data. The index is sharded across these machines, with each machine holding a portion of the overall index.

### 2.5 Key Insights from Estimation
These numbers reveal several important design implications:
1. **Storage is the primary challenge for indexing.** Petabytes of data require distributed storage and careful partitioning strategies.
2. **Crawling is a continuous, bandwidth-intensive operation.** We need hundreds of crawling machines distributed globally to achieve the required refresh rates.
3. **Query serving must be highly optimized.** 100K QPS with sub-500ms latency requires aggressive caching, efficient index structures, and careful system tuning.
4. **Global distribution is necessary.** To serve users worldwide with low latency, we need copies of the index in multiple data centers.

# 3. Core APIs
A search engine exposes several APIs for different use cases. Let's define the core endpoints that power the user-facing search experience.

### 3.1 Web Search

#### Endpoint: GET /search
This is the primary API that powers the search experience. When you type a query and hit enter, this endpoint handles the request.

#### Request Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| q | string | Yes | The search query string (e.g., "best programming languages 2024") |
| start | integer | No | Offset for pagination. Default is 0 (first page) |
| num | integer | No | Number of results to return. Default is 10, max is 100 |
| lang | string | No | Preferred language for results (e.g., "en", "es", "zh") |
| safe | enum | No | Safe search filter level: "off", "moderate", or "strict" |

#### Example Request:

#### Example Response:
The response includes several useful fields beyond just the results. The `corrected_query` field tells the user if we automatically corrected their spelling. The `search_time_ms` shows how fast we processed the query. And `related_searches` helps users refine their query if they did not find what they were looking for.

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Invalid query | Empty query or invalid parameter values |
| 429 Too Many Requests | Rate limited | User exceeded their query quota |
| 503 Service Unavailable | System overload | Search infrastructure is temporarily overwhelmed |

### 3.2 Autocomplete Suggestions

#### Endpoint: GET /suggest
As users type in the search box, we show suggestions to help them complete their query faster. This needs to be fast (under 100ms) because we call it on every keystroke.

#### Request Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| q | string | Yes | Partial query string (what the user has typed so far) |
| num | integer | No | Number of suggestions to return. Default is 10 |
| lang | string | No | Language preference for suggestions |

#### Example Request:

#### Example Response:
Autocomplete suggestions are typically based on popular queries that start with the user's prefix. The system might also consider the user's search history (if logged in) and trending topics.

### 3.3 Spell Check

#### Endpoint: GET /spellcheck
This endpoint suggests corrections for potentially misspelled queries. In practice, spell checking is often integrated into the main search endpoint, but having it as a separate API is useful for testing and specialized applications.

#### Example Request:

#### Example Response:
The confidence score indicates how certain we are about the correction. A high confidence might trigger automatic correction ("Showing results for programming languages"), while a lower confidence might just offer a suggestion ("Did you mean: programming languages?").
# 4. High-Level Design
With requirements clarified and APIs defined, let's design the system architecture. A web search engine is complex, so rather than presenting everything at once, we will build it incrementally. This approach mirrors how you would tackle the problem in an interview and makes it easier to understand how the pieces fit together.
At the highest level, a search engine consists of three major subsystems:
1. **Crawling** explores the web to discover and download pages. It is like sending out millions of scouts to continuously map the internet.
2. **Indexing** processes the raw HTML from crawling and builds searchable data structures. This is where we transform a chaotic pile of web pages into an organized library.
3. **Serving** handles user queries in real-time, searches the index, ranks results, and returns them within milliseconds.

These subsystems operate somewhat independently but are connected through data pipelines. The crawler feeds pages to the indexer, and the indexer produces the data structures that the serving layer uses. Let's design each one.


The crawler's job seems simple: download web pages. But at the scale of the entire web, this becomes a fascinating engineering challenge. How do you politely crawl billions of pages without overwhelming individual websites? How do you decide which pages to crawl first? How do you discover new pages?

### Components Needed
Let's think about what components we need for web crawling.

#### URL Frontier
The URL frontier is the brain of the crawler. It is a sophisticated queue that decides which URLs to crawl next. Unlike a simple FIFO queue, it must balance multiple competing concerns: priority (important pages first), freshness (recently changed pages need recrawling), and politeness (do not overwhelm any single website).
Think of it as the crawler's to-do list, but one that constantly re-prioritizes based on changing circumstances. A breaking news story might push a news site's homepage to the front of the queue, while a dusty corporate FAQ page waits patiently for its monthly refresh.

#### Fetcher
The fetcher is the workhorse that actually downloads pages. It makes HTTP requests, follows redirects, handles timeouts and errors, and extracts the raw HTML. At 11,500 pages per second, we need many fetchers running in parallel across many machines.
The fetcher must also be a good citizen of the web. It reads robots.txt files to know which pages it is allowed to crawl, respects crawl-delay directives, and uses an appropriate User-Agent header so websites can identify our crawler.

#### DNS Resolver
Every URL contains a hostname that needs to be resolved to an IP address before we can connect. At our crawl rate, we are doing thousands of DNS lookups per second. Using the standard system resolver would be far too slow.
Instead, we run our own high-performance DNS resolution infrastructure with aggressive caching. Once we resolve example.com, we cache that result and reuse it for the next thousand pages we crawl from that domain.

#### Content Store
After fetching a page, we need somewhere to put it before processing. The content store is temporary storage for raw crawled content. It holds the HTML, HTTP headers, and crawl metadata until the indexing pipeline picks it up.
This store needs to handle high write throughput (11,500 pages/second) and support efficient batch reads for the indexing pipeline. A distributed message queue or a distributed file system works well here.

### The Crawling Flow
Here is how these components work together to crawl a web page:
Let me walk you through this flow:
1. **URL Selection:** The URL Frontier selects the next URL to crawl based on priority and politeness constraints. High-priority pages (like news homepages) get crawled frequently, while low-priority pages wait their turn.
2. **DNS Resolution:** Before connecting, we resolve the hostname to an IP address. Our DNS resolver checks its cache first, only querying upstream servers for unknown hosts.
3. **Page Fetching:** The fetcher connects to the web server, sends an HTTP GET request, and receives the HTML response. It handles redirects, retries on transient failures, and respects robots.txt rules.
4. **Content Storage:** The raw HTML, along with metadata like crawl timestamp and HTTP headers, goes into the content store. This data will be processed by the indexing pipeline.
5. **Link Extraction:** We parse the HTML to find all the links on the page. Each link is a potential new page to crawl.
6. **URL Discovery:** New URLs are added back to the URL Frontier. The frontier deduplicates them against known URLs and assigns initial priorities.

### Politeness: Being a Good Web Citizen
Crawlers must be "polite" to avoid overwhelming web servers. Imagine if we sent 1,000 requests per second to a small blog, it would take down their server. Good crawlers limit their impact.
The URL frontier enforces politeness by grouping URLs by domain and maintaining a minimum delay between requests to the same host. If we last crawled example.com at 10:00:00, we wait until at least 10:00:01 before crawling another page from that domain.
This means we cannot just pull URLs from a single queue. We need separate queues per domain, and we select the next URL from whichever domain's delay has expired and has the highest priority URL waiting.


    S1 --> DBPostgreSQL
```mermaid
graph TB
    subgraph Clients
        Web[Web Browser]
        Mobile[Mobile App]
    end

    subgraph Load Balancing
        LB[Load Balancer]
    end

    subgraph Application Services
        S1[503 Service]
    end

    subgraph Data Storage
        DBPostgreSQL[PostgreSQL]
        DBMySQL[MySQL]
    end

    Web --> LB
    Mobile --> LB
    LB --> S1
    S1 --> DBPostgreSQL
## 4.2 Subsystem 2: Indexing Pipeline
The crawling system gives us raw HTML. Now we need to transform that into something we can search. The indexing pipeline is where the magic of information retrieval happens.
Think about what we need to do: take billions of web pages full of HTML tags, advertisements, and navigation menus, and extract the meaningful content. Then organize that content so we can find relevant pages for any query in milliseconds.

### Components Needed

#### Document Processor
The document processor takes raw HTML and extracts searchable content. This involves stripping HTML tags, removing boilerplate (headers, footers, navigation), and identifying the actual content of the page.
It also extracts metadata: the page title, headings, publication date, author information, and any structured data embedded in the page. Different parts of the page have different importance, words in the title matter more than words buried in a footer.

#### Analyzer
The analyzer transforms raw text into searchable tokens. This is not as simple as splitting on spaces. Consider these challenges:
- "Programming" and "programming" should match the same queries (case normalization)
- "running", "runs", and "ran" are related to "run" (stemming)
- "the", "is", and "a" appear in almost every document and add noise (stopwords)
- "New York" is a single concept, not two separate words (phrases)

The analyzer handles all of this, producing a stream of normalized tokens ready for indexing.

#### Index Builder
The index builder takes the stream of tokens and constructs the inverted index. For each unique term, it records which documents contain that term, how many times, and where in the document it appears.
This is not a simple database insert. The index builder must handle massive throughput (millions of documents per hour), partition the index across thousands of machines, and optimize data structures for fast retrieval.

#### Link Analyzer
Web pages are connected by hyperlinks, and those links carry meaning. A page that is linked to by many other important pages is probably important itself. The link analyzer builds a graph of the web and computes authority scores like PageRank.
This is computationally expensive. Computing PageRank requires iterating over the entire link graph multiple times until scores converge. For 100 billion pages, this is a massive distributed computation that runs periodically (weekly or so).

### The Indexing Flow
Here is how a document flows through the indexing pipeline:
1. **Document Processing:** Raw HTML is pulled from the content store. The processor strips tags, removes boilerplate, extracts text content, and identifies the document structure (title, headings, body).
2. **Analysis:** The extracted text passes through the analyzer. Words are lowercased, stemmed to their root forms, and organized into tokens. Position information is preserved for phrase queries.
3. **Index Building:** Tokens are added to the inverted index. Each term maps to a posting list containing document IDs, term frequencies, and positions.
4. **Link Analysis:** Hyperlinks are extracted and added to the link graph. This feeds into the periodic PageRank computation.
5. **Document Storage:** The processed document content is stored for snippet generation during query time. This is a separate store from the index.

## 4.3 Subsystem 3: Search Serving
The serving layer is where everything comes together. A user types a query, and within 500 milliseconds, they see a list of relevant results. This requires careful orchestration of query processing, index lookup, ranking, and response assembly.

### Components Needed

#### Query Processor
The query processor is the first stop for user queries. It does the same analysis we did during indexing (tokenization, normalization, stemming) so that queries match indexed content.
But it does more than that. It expands queries with synonyms ("car" might also search for "automobile"). It detects and corrects spelling errors. It identifies query intent, is the user looking for a specific website (navigational), trying to learn something (informational), or wanting to buy something (transactional)?

#### Index Servers
Index servers hold portions of the inverted index in memory for fast access. At our scale, the full index does not fit on a single machine, so it is partitioned across thousands of servers.
Each index server is responsible for a shard of the document space. When a query comes in, every shard must be searched because any shard might contain relevant documents. This is a "scatter" operation, we send the query to all shards in parallel.

#### Aggregator
With thousands of shards each returning their top results, someone needs to combine them. The aggregator collects results from all index servers, merges them into a single ranked list, applies any final filters or re-ranking, and assembles the response.
The aggregator also handles failures gracefully. If one shard is slow or unavailable, we might return results from the other shards rather than failing the entire query. Users would rather see 95% of the web than wait forever for 100%.

#### Cache Layer
Search queries follow a power law distribution. A small percentage of queries account for a large percentage of traffic. "Facebook", "YouTube", "weather" are searched millions of times per day. Caching these hot queries can serve 30-50% of traffic without touching the index servers.

### The Serving Flow
Let's trace through a search query step by step:
1. **Load Balancing:** The query arrives at a load balancer, which distributes requests across query processors to spread the load evenly.
2. **Query Processing:** The query processor analyzes the query, applying the same tokenization and normalization as indexing. It may also expand the query with synonyms or correct spelling errors.
3. **Cache Check:** Before searching the index, we check if this exact query (or a normalized version) is in the cache. Popular queries like "weather" or "facebook login" will be cache hits.
4. **Scatter to Index Servers:** On a cache miss, the aggregator sends the query to all index shards in parallel. Each shard searches its portion of the index and returns the top-K results with scores.
5. **Gather and Merge:** The aggregator collects results from all shards, merges them into a single ranked list, and selects the global top-K.
6. **Snippet Generation:** For each result, we need to show a snippet of the page content. The snippet generator fetches the document and extracts a relevant passage containing the query terms.
7. **Response Assembly:** The final response is assembled with titles, URLs, snippets, and any additional information (related searches, knowledge panels, etc.) and returned to the user.

## 4.4 Putting It All Together
Now let's see how all three subsystems connect to form the complete search engine:
The data flow is clear: pages flow from the web through crawling, into the content store, through indexing, and into the index and document stores. Queries flow from users through the serving layer, which reads from those stores and returns results.
What is not shown in this diagram is the continuous nature of the system. Crawling never stops. The indexer continuously processes new content. Index servers periodically receive updated index shards. It is a constantly flowing pipeline, not a batch process.

### Component Summary
| Component | Purpose | Key Challenge |
| --- | --- | --- |
| URL Frontier | Manage crawl queue with priorities | Balance freshness, importance, and politeness |
| Fetchers | Download web pages | Handle scale (11K pages/sec) and failures |
| Document Processor | Extract content from HTML | Handle diverse, messy web pages |
| Index Builder | Construct inverted index | Build incrementally, handle updates |
| Link Analyzer | Compute PageRank scores | Process 100B+ node graph |
| Query Processor | Parse and expand queries | Sub-millisecond processing |
| Index Servers | Store and search index shards | Keep hot data in memory |
| Aggregator | Merge results from shards | Handle partial failures gracefully |
| Cache | Store popular query results | Achieve high hit rate |

# 5. Database Design
Unlike a typical web application with a few database tables, a search engine uses specialized data structures optimized for its unique access patterns. Let's explore what those look like.

## 5.1 Why Not Traditional Databases?
You might wonder: why not just store everything in PostgreSQL or MySQL? The answer comes down to scale and access patterns.
**Scale:** 100 billion documents cannot fit in any single database. We need to partition data across thousands of machines, which traditional databases do not handle well.
**Access patterns:** Search workloads are read-heavy and append-mostly. We rarely update existing documents. Traditional databases are optimized for transactional workloads with many updates.
**Data structures:** The core data structure for search is the inverted index, which maps terms to documents. This is not a relational table. Specialized index formats are far more efficient.
**Latency:** We need sub-millisecond lookups for hot data, which means keeping data in memory. Traditional databases assume disk-based storage.

## 5.2 Core Storage Components
A search engine uses several specialized storage systems, each optimized for its purpose.

### Inverted Index
This is the heart of the search engine. The inverted index maps every term to the documents containing it.
The structure has several components:
**Term Dictionary:** A sorted list of all unique terms, with pointers to their posting lists. This is typically stored in a compact trie or finite state transducer for memory efficiency.
**Posting Lists:** For each term, a list of documents containing that term. Each entry includes the document ID, term frequency, and often the positions where the term appears. Posting lists are compressed using techniques like variable-byte encoding.
**Skip Lists:** Large posting lists (for common terms) include skip pointers that allow fast intersection operations. If we are searching for "programming AND languages", skip lists help us efficiently find documents containing both terms.
Here is a simplified example:

### Document Store
While the inverted index tells us which documents match a query, we also need the actual content for snippet generation. The document store holds processed document content.
| Field | Type | Description |
| --- | --- | --- |
| doc_id | Long | Unique identifier assigned during indexing |
| url | String | Canonical URL of the page |
| title | String | Page title extracted during indexing |
| content | Text | Processed text content (stripped of HTML) |
| raw_html | Blob | Original HTML, compressed for storage |
| crawl_time | Timestamp | When the page was last crawled |
| page_rank | Float | Pre-computed authority score |

### URL Database
The crawler needs to track every URL it knows about: which have been crawled, when, and when to recrawl them.
| Field | Type | Description |
| --- | --- | --- |
| url_hash | Long | Hash of the URL for efficient lookup |
| url | String | Full URL |
| last_crawl | Timestamp | When last successfully crawled |
| next_crawl | Timestamp | When to crawl again |
| priority | Integer | Crawl priority based on importance |
| status | Enum | Success, error, robots blocked, etc. |

This database is massive (hundreds of billions of URLs) and needs to support both point lookups (has this URL been crawled?) and range scans (which URLs need crawling now?).

### Link Graph
The link structure of the web is stored separately for PageRank computation and anchor text analysis.
| Field | Type | Description |
| --- | --- | --- |
| source_doc_id | Long | Document containing the link |
| target_doc_id | Long | Document being linked to |
| anchor_text | String | Text of the hyperlink |

This graph has trillions of edges (100B pages × average of 50 links per page). PageRank computation iterates over this entire graph multiple times, making efficient storage and traversal critical.

## 5.3 Partitioning Strategy
With 100 billion documents, we need to spread data across many machines. How we partition matters a lot for query performance.

#### Document Partitioning (the standard approach):
Documents are assigned to shards based on a hash of the document ID:
Each shard contains a random subset of all documents. This means every shard has some documents for any term, so queries must be sent to ALL shards. The aggregator merges results from all shards.
This approach has several advantages:
- Load is naturally balanced across shards since documents are randomly distributed
- Adding more shards is straightforward, just redistribute some documents
- No hot spots since popular terms are spread across all shards

The downside is that every query touches every shard, but the parallelism makes this acceptable.

#### Term Partitioning (an alternative):
An alternative is to partition by term: all documents containing "programming" go to one shard, all documents containing "python" go to another.
This means single-term queries only need to touch one shard. But multi-term queries become complicated, and popular terms create hot spots. This approach is rarely used in practice for general web search.
**Recommendation:** Document partitioning is the industry standard. It is simpler, more predictable, and handles diverse query patterns well.
# 6. Design Deep Dive
Now that we have the high-level architecture, let's dive into the most interesting and challenging aspects of the design. These are the topics that distinguish a good system design from a great one.

## 6.1 Web Crawling at Scale
Crawling billions of pages presents unique challenges around discovery, freshness, and being a good citizen of the web. Let's explore how to build a crawler that handles these challenges.

### The URL Frontier: More Than Just a Queue
At first glance, the URL frontier seems like a simple priority queue. But at web scale, it becomes one of the most complex components in the system.
The frontier must balance three competing concerns:
**Priority:** Not all pages are equal. The homepage of a major news site should be crawled before a random personal blog. We assign priorities based on PageRank, domain authority, and expected change frequency.
**Freshness:** Pages change at different rates. A news homepage might update every few minutes, while a company's "About" page stays static for years. We need to recrawl frequently-changing pages more often.
**Politeness:** We cannot hammer any single server with requests. Even if example.com has 10,000 pages in our queue, we should only send one request per second to avoid overloading their server.
The frontier maintains separate queues for each domain. When selecting the next URL to crawl:
1. Find all hosts whose politeness delay has expired
2. Among those hosts, pick the one with the highest priority URL
3. Dequeue one URL from that host's queue
4. Update the delay tracker with the current time

This ensures we never violate politeness rules while still prioritizing important pages.

### Crawl Frequency: How Often to Revisit
Different pages need different refresh rates. Getting this right is crucial for freshness without wasting resources.
| Page Type | Example | Refresh Rate | Why |
| --- | --- | --- | --- |
| Breaking news | CNN homepage | Every 15 minutes | Users search for current events |
| Popular content | Wikipedia articles | Daily | Content changes regularly |
| Static pages | Corporate about pages | Weekly | Rarely changes |
| Deep archive | Old blog posts | Monthly | Almost never changes |

The crawler learns optimal frequencies over time. If we recrawl a page and find it unchanged multiple times, we increase the interval. If we find frequent changes, we decrease it. This adaptive approach allocates crawl budget efficiently.

### Handling Crawl Challenges
The web is messy. Crawlers must handle many edge cases.

#### Duplicate Detection:
The same content often exists at multiple URLs:
-  vs 
-  vs `example.com/page`
- `example.com/page` vs `example.com/page?utm_source=twitter`

We use URL canonicalization to normalize URLs and content fingerprinting (SimHash) to detect when different URLs serve identical content. This saves crawl budget and prevents duplicate results.

#### Spider Traps:
Some websites generate infinite URLs. Calendar pages, session IDs, and dynamic filters can create unbounded URL spaces:
We detect and avoid traps by limiting crawl depth per domain, detecting URL patterns that generate infinite variations, and monitoring pages crawled per domain.

#### Robots.txt:
Every well-behaved crawler respects robots.txt, a file that websites use to specify crawl rules:
We cache robots.txt for each domain and check it before every fetch. Pages marked as disallowed are skipped.

## 6.2 The Inverted Index at Web Scale
The inverted index is the core data structure that makes search fast. Building and serving one for 100 billion documents requires careful engineering.

### Index Structure Deep Dive
Let's look more closely at how the inverted index is structured:
Each posting list entry contains:
- **Document ID:** Which document contains the term
- **Term Frequency:** How many times the term appears (important for scoring)
- **Positions:** Where in the document (needed for phrase queries like "machine learning")
- **Field Information:** Whether the term appears in title, body, URL, or anchor text

Posting lists for common terms like "the" can contain billions of entries. Compression is essential. Variable-byte encoding, delta encoding of document IDs, and position deltas reduce storage significantly.

### Tiered Index Architecture
Not all index data needs the same access speed. We use a tiered approach to balance memory usage and latency:
**Tier 0 (Memory):** The most frequently accessed data lives in RAM. This includes posting lists for common query terms and the top documents by PageRank. About 5% of the index serves 80% of queries.
**Tier 1 (SSD):** Medium-frequency terms that do not fit in memory but are accessed often enough to warrant fast storage. SSDs provide microsecond-level access times.
**Tier 2 (HDD):** The long tail of rare terms. A query for an obscure term might take longer because we need to read from disk, but this is acceptable since such queries are infrequent.

### Incremental Index Updates
We cannot rebuild the entire index from scratch every time we crawl new pages. With 11,500 pages per second, we need incremental updates.

#### Segment-Based Indexing:
New documents are indexed into small segments. Periodically, we merge segments into larger ones:
Queries search all current segments and merge results. This approach avoids expensive full index rebuilds while keeping the index fresh.

#### Handling Deletions:
When a page is removed or updated, we do not immediately delete it from the index. Instead, we mark it as deleted in a bitmap. Queries filter out deleted documents. During segment merges, deleted documents are physically removed.

## 6.3 Ranking: Finding the Best Results
Finding pages that contain the query terms is the easy part. The hard part is putting them in the right order. For the query "programming languages", millions of pages match. How do we decide which 10 to show first?

### The Ranking Problem
Good ranking requires combining two types of signals:
**Query-Dependent Signals:** How well does this specific document match this specific query?
- Does the title contain the query terms?
- How many times do the terms appear?
- Are the terms close together in the document?
- Does the document topic match the query intent?

**Query-Independent Signals:** How authoritative or trustworthy is this document in general?
- How many other pages link to it?
- How authoritative are those linking pages?
- Is the domain generally trustworthy?
- Is the content fresh?

### PageRank: Measuring Authority
PageRank is Google's famous algorithm for measuring page importance based on links. The core insight is elegant: a page is important if important pages link to it.
The algorithm simulates a "random surfer" who browses the web by randomly clicking links. PageRank is the probability that the surfer is on any given page at equilibrium.
With probability d (0.85), the surfer follows a random link. With probability 1-d (0.15), they jump to a random page. This random jump prevents the algorithm from getting stuck in loops.
Computing PageRank for 100 billion pages is a massive distributed computation. The link graph is partitioned across thousands of machines, and the algorithm runs iteratively using MapReduce-style frameworks until scores converge (typically 50-100 iterations).

### BM25: Measuring Relevance
While PageRank measures authority, BM25 measures how well a document matches the query. It is a refinement of classic TF-IDF that handles term frequency saturation and document length normalization.
The key insights behind BM25:
**Term frequency saturation:** Seeing a term 10 times is not 10x better than seeing it once. The first few occurrences are most important.
**Length normalization:** Longer documents naturally contain more term occurrences. We normalize to avoid favoring long documents unfairly.
**Inverse document frequency:** Rare terms are more important. A document containing "quantum" is more relevant than one containing "the".

### Combining Signals with Learning to Rank
Modern search engines combine hundreds of signals using machine learning:
| Signal Category | Examples |
| --- | --- |
| Text relevance | BM25, phrase match, term proximity |
| Link authority | PageRank, inbound link count, anchor text |
| Freshness | Last modified date, crawl frequency |
| Content quality | Spam score, content length, readability |
| User behavior | Click-through rate, dwell time, bounce rate |
| Domain signals | Domain age, SSL certificate, trust metrics |

Rather than manually tuning weights for each signal, we train machine learning models on human-rated search results. The model learns which combinations of signals produce good rankings.
The training data comes from human raters who evaluate search results on a relevance scale. The model learns to predict these ratings from the extracted features.

## 6.4 Query Processing
Turning a user's raw query into ranked results involves several processing steps. Each step adds understanding and improves result quality.

### Understanding the Query

#### Tokenization and Normalization:
The query goes through the same analysis as indexed documents:
We lowercase, remove punctuation, and apply stemming (programming -> program) so that queries match indexed content.

#### Spell Correction:
Users make typos. Good spell correction dramatically improves the search experience.
Spell correction uses multiple techniques:
- Edit distance to dictionary words
- N-gram language models (likely sequences of words)
- Query logs (common corrections from past searches)

High-confidence corrections are applied automatically ("Showing results for programming languages"). Lower-confidence corrections are offered as suggestions ("Did you mean: programming languages?").

#### Query Expansion:
Adding synonyms and related terms helps find relevant pages that use different vocabulary:
Expansion must be careful. Too aggressive and we introduce noise. Too conservative and we miss relevant results.

#### Intent Classification:
Understanding what type of result the user wants helps tailor the response:
| Intent | Example | Response Strategy |
| --- | --- | --- |
| Navigational | "facebook login" | Rank facebook.com first |
| Informational | "how tall is mount everest" | Show knowledge panel with answer |
| Transactional | "buy iphone 15" | Show shopping results, price comparisons |

### Distributed Query Execution
With the index sharded across thousands of machines, query execution requires careful coordination.

#### Phase 1: Scatter
The query is sent to all index shards in parallel. Each shard searches its local index and returns the top-K results with scores.

#### Phase 2: Gather
The aggregator collects results from all shards and merges them into a single ranked list. We take the global top-K from the combined results.

#### Handling Slow or Failed Shards:
In a system with thousands of shards, some will occasionally be slow or unavailable. We use timeouts and partial results:
- Send query to all shards with a timeout (e.g., 200ms)
- After timeout, return results from shards that responded
- Mark results as potentially incomplete if shards timed out

Users would rather see 95% of results quickly than wait forever for 100%.

## 6.5 Caching Strategy
Caching is essential for achieving low latency at high throughput. Query distributions follow a power law, a small percentage of queries account for a large percentage of traffic.

### Query Result Cache
The most impactful cache stores complete results for popular queries:
Popular queries like "facebook", "youtube", and "weather" are searched millions of times daily. Caching their results avoids repeating expensive index lookups.
Cache hit rates of 30-50% are typical. The top 1% of queries account for roughly 30% of traffic.

### Posting List Cache
For cache misses, we can still speed up query execution by caching posting lists for frequent terms:
This is trickier because posting lists can be large (millions of entries for common terms). We cache selectively based on term frequency and list size.

### Cache Invalidation
Search results must stay reasonably fresh. We use TTL-based invalidation:
- Popular queries: 15-60 minute TTL
- Less popular queries: 1-24 hour TTL
- Breaking news terms: Very short TTL or event-based invalidation

For major events (elections, disasters), we may proactively invalidate caches to ensure fresh results.

## 6.6 Spam Detection and Quality
Without quality control, search results would be dominated by spam and low-quality content. SEO spammers are constantly trying to game rankings.

### Types of Web Spam
**Content Spam:**
- Keyword stuffing (repeating terms excessively)
- Hidden text (white text on white background)
- Scraped/duplicate content from other sites
- Auto-generated nonsense

**Link Spam:**
- Link farms (networks of sites linking to each other)
- Purchased links from high-authority sites
- Comment spam on blogs and forums
- Private Blog Networks (PBNs)

**Cloaking:**
- Showing different content to crawlers vs. users
- Detecting bot User-Agents and serving SEO-optimized content

### Detection Signals
We use many signals to identify low-quality content:
**Content Signals:**
- Content length and depth
- Unique content vs. duplicates
- Grammar and spelling quality
- Ad-to-content ratio
- Presence of structured data

**Link Signals:**
- Sudden spikes in inbound links
- Links from known spam sites
- Unnatural anchor text patterns
- Reciprocal link schemes

### Machine Learning for Spam Detection
Manual rules cannot keep up with spammers. We train classifiers on labeled examples:
1. Human raters label pages as spam or legitimate
2. Extract hundreds of features from content and links
3. Train ensemble classifiers (random forests, gradient boosting)
4. Apply to all crawled pages

The model outputs a spam probability. High-confidence spam is excluded from the index. Medium-confidence spam is demoted in rankings.

## Summary
| Topic | Key Takeaways |
| --- | --- |
| Web Crawling | URL frontier balances priority, freshness, and politeness. Handle duplicates and spider traps carefully. |
| Inverted Index | Tiered storage (memory/SSD/HDD) optimizes cost and latency. Incremental segment-based updates. |
| Ranking | Combine PageRank (authority) with BM25 (relevance). Use learning-to-rank with hundreds of signals. |
| Query Processing | Spell correction, query expansion, intent classification. Distributed scatter-gather execution. |
| Caching | Multi-level caching achieves 30-50% hit rate. TTL-based invalidation for freshness. |
| Spam Detection | Content and link analysis signals. ML classifiers trained on human-labeled data. |

## References
- [The Anatomy of a Large-Scale Hypertextual Web Search Engine](http://infolab.stanford.edu/~backrub/google.html) - The original Google paper by Brin and Page
- [Introduction to Information Retrieval](https://nlp.stanford.edu/IR-book/) - Stanford textbook covering search engine fundamentals
- [Web Search for a Planet: The Google Cluster Architecture](https://research.google/pubs/pub49/) - Google's distributed systems approach
- [The PageRank Citation Ranking: Bringing Order to the Web](http://ilpubs.stanford.edu:8090/422/) - Original PageRank paper

# Quiz

## Design Google Search Quiz
In a large-scale web search engine, what is the primary purpose of an inverted index?