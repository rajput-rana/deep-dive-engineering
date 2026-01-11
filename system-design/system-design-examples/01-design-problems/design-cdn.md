# Design a Content Delivery Network (CDN)

## What is a CDN?

A Content Delivery Network (CDN) is a globally distributed network of servers that caches and delivers content to users from locations geographically close to them.
The core idea is to reduce latency by serving content from edge servers instead of the origin server. When a user in Tokyo requests an image from a website hosted in New York, the CDN serves it from a nearby edge server in Asia instead of fetching it across the Pacific Ocean.
**Popular Examples:** Cloudflare, Akamai, Amazon CloudFront, Fastly
This system design problem tests your understanding of **caching**, **distributed systems**, **DNS, networking,** and **global-scale infrastructure**.
Lets start by clarifying the requirements.
In this chapter, we will explore the **high-level design of a CDN**.
# 1. Clarifying Requirements
Before sketching architecture diagrams, we need to understand what we are building. A CDN can serve many purposes, from delivering static images to streaming live video to accelerating dynamic API responses. The scope significantly affects our design decisions.
Here is an example of how a discussion between the candidate and the interviewer might unfold:
**Candidate:** "What type of content should the CDN serve? Static only, or also dynamic content?"
**Interviewer:** "Focus primarily on static content like images, videos, CSS, and JavaScript files. We can discuss dynamic content caching as an extension."
**Candidate:** "What is the expected scale in terms of requests per second and total storage?"
**Interviewer:** "Assume we need to handle 10 million requests per second globally, with 100 TB of cached content."
**Candidate:** "How fresh does the content need to be? What are the cache invalidation requirements?"
**Interviewer:** "Most content can be cached for hours or days. We need support for on-demand cache invalidation that propagates globally within 30 seconds."
**Candidate:** "Should we support multiple origin server types, or focus on a specific protocol?"
**Interviewer:** "Support HTTP/HTTPS origins. The CDN should work with any web server as the origin."
**Candidate:** "What are the latency requirements for cache hits?"
**Interviewer:** "Cache hits should be served in under 50ms for 99% of requests, regardless of user location."
After gathering the details, we can summarize the key system requirements.

## 1.1 Functional Requirements
Based on the discussion, here are the core capabilities our CDN must provide:
- **Content Caching:** Cache static content (images, videos, CSS, JS) at edge locations worldwide.
- **Content Delivery:** Serve cached content to users from the nearest edge server.
- **Origin Fetch:** Retrieve content from origin servers on cache misses.
- **Cache Invalidation:** Support on-demand purging of cached content globally.
- **SSL/TLS Support:** Serve content over HTTPS with custom domain certificates.

## 1.2 Non-Functional Requirements
Beyond features, these are the qualities that make our CDN production-ready:
- **Low Latency:** Cache hits should complete in under 50ms at the 99th percentile, regardless of user location.
- **High Availability:** Target 99.99% uptime for content delivery
- **Global Scale:** Handle 10 million requests per second distributed across all edge locations.
- **Fast Propagation:** Cache invalidations must reach all edge servers within 30 seconds.
- **Fault Tolerance:** Continue serving content even when some edge servers or regions fail.

# 2. Back-of-the-Envelope Estimation
Before diving into the architecture, let's run some numbers to understand the scale we are dealing with. These estimates will inform decisions about server capacity, network requirements, and storage architecture.

### 2.1 Traffic Distribution
Starting with our global traffic figure of 10 million requests per second, we need to think about how this distributes across our infrastructure.

#### Points of Presence (PoPs)
Major CDN providers operate 200-300 PoPs worldwide. Let's assume we have 200 PoPs distributed across continents based on population and internet usage:
If we distribute traffic evenly across PoPs (though in practice it is not even), each PoP handles:
In reality, traffic concentrates in major metropolitan areas. A PoP in Tokyo or London might handle 200,000 requests per second, while a PoP in a smaller city handles 10,000. We design for peak capacity in major locations.

### 2.2 Cache Hit Ratio
The cache hit ratio determines how much traffic reaches the origin server. A well-tuned CDN achieves 90-99% cache hit ratios for static content.
Let's target a 95% cache hit ratio:
That is still 500,000 origin requests per second globally. This is why we need a shielding layer (which we will discuss later) to consolidate these requests and protect customer origins.

### 2.3 Bandwidth Requirements
Bandwidth determines our network infrastructure requirements. The numbers here are substantial.
Assuming an average response size of 100 KB (a mix of small CSS files and larger images):
That is 8 terabits per second of outbound bandwidth globally. Distributed across 200 PoPs:
Major PoPs in cities like Tokyo or New York might need 100+ Gbps capacity during peak hours. This explains why CDN providers invest heavily in network infrastructure and peering relationships.

### 2.4 Storage Requirements
Our total cacheable content is 100 TB, but we do not replicate everything everywhere. Content popularity follows a power-law distribution: a small percentage of content receives most of the traffic.

#### Tiered Replication Strategy:
| Content Tier | Size | Replication | Total Storage |
| --- | --- | --- | --- |
| Hot (top 10%) | 10 TB | All 200 PoPs | 2 PB |
| Warm (next 30%) | 30 TB | Regional shields (10) | 300 TB |
| Cold (bottom 60%) | 60 TB | On-demand caching | Variable |

This tiered approach means popular content is everywhere (fast), while long-tail content is cached on-demand (efficient storage use).

### 2.5 Cache Invalidation Scale
Finally, let's size the invalidation system:
This is manageable with a good pub/sub system, but the challenge is ensuring all 200 PoPs receive and process the invalidation within our 30-second SLA.

### 2.6 Key Insights
These estimates reveal several important design implications:
1. **Traffic is highly distributed:** No single server or even single PoP handles a majority of traffic. The architecture must be inherently distributed.
2. **Cache hit ratio is critical:** The difference between 90% and 99% hit ratio is a 10x difference in origin load. Investing in cache efficiency pays dividends.
3. **Network is the constraint:** At these scales, bandwidth is expensive and potentially limiting. Compression and efficient protocols matter.
4. **Storage requires tiering:** We cannot replicate everything everywhere. Smart content placement based on popularity is essential.

# 3. Core APIs
With requirements and scale understood, let's define the API contract. 
A CDN has two distinct interfaces: the content delivery path that serves end users, and the management APIs that customers use to configure and control their CDN behavior.

### 3.1 Content Delivery
This is the primary interface, handling billions of requests daily. When a user's browser requests an asset, this API serves it.

#### Endpoint: GET /{path}
The path maps to content on the customer's origin server. The CDN acts as a transparent proxy, caching responses and serving them to subsequent requesters.

#### Request Headers:
| Header | Required | Description |
| --- | --- | --- |
| Host | Yes | The customer's domain (e.g., cdn.example.com). This identifies which customer configuration to use |
| Accept-Encoding | No | Compression formats the client supports (gzip, br). Enables serving compressed versions |
| If-None-Match | No | ETag from a previous response. Enables conditional requests to save bandwidth |
| If-Modified-Since | No | Timestamp from a previous response. Alternative to ETag for conditional requests |

#### Response Headers:
The response includes standard HTTP headers plus CDN-specific ones for debugging and cache control:
The `X-Cache` header is particularly useful. A value of `HIT` means the content was served from cache. `MISS` means we fetched from origin (or shield). This helps customers debug caching behavior.

#### Response Codes:
| Code | Meaning | When It Occurs |
| --- | --- | --- |
| 200 OK | Content served successfully | Normal cache hit or successful origin fetch |
| 304 Not Modified | Content unchanged since last request | Client sent valid If-None-Match or If-Modified-Since |
| 404 Not Found | Content does not exist at origin | Origin returned 404, CDN passes through |
| 502 Bad Gateway | Origin server unreachable | Network issues between CDN and origin |
| 504 Gateway Timeout | Origin server too slow | Origin did not respond within timeout |

### 3.2 Cache Invalidation
When customers update content at their origin, they need to purge stale copies from all edge caches.

#### Endpoint: POST /purge

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| urls | string[] | Yes* | Specific URLs to purge (e.g., ["/images/logo.png", "/css/main.css"]) |
| pattern | string | Yes* | Wildcard pattern for bulk purge (e.g., /images/*, *.js) |
| tags | string[] | Yes* | Cache tags to purge (e.g., ["product-123", "homepage"]) |

*At least one of `urls`, `pattern`, or `tags` is required.

#### Example Request:

#### Success Response (202 Accepted):
We return 202 (Accepted) rather than 200 because purging is asynchronous. The purge begins immediately, but propagating to all 200 PoPs takes time. The `purge_id` lets customers check status.

#### Error Responses:
| Code | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Invalid request | Malformed URL pattern, missing required fields |
| 401 Unauthorized | Authentication failed | Invalid or missing API key |
| 429 Too Many Requests | Rate limit exceeded | Customer exceeding their purge quota |

### 3.3 Purge Status
Customers can check whether a purge has completed across all PoPs.

#### Endpoint: GET /purge/{purge_id}

#### Success Response (200 OK):
The `status` field transitions through states: `pending` → `propagating` → `completed`. If something goes wrong, it may show `partial_failure` with details about which PoPs failed.

### 3.4 API Design Considerations
A few decisions worth noting:
**Authentication:** The purge API requires authentication (API keys or OAuth), but the content delivery API does not since end users should access content without credentials. Rate limiting on the delivery API is IP-based.
**Idempotency:** Purging the same URL twice is safe. The second purge simply finds nothing to delete or re-deletes the same content. This simplifies retry logic for customers.
**Wildcards vs Tags:** Wildcard patterns (`/images/*`) are intuitive but require the CDN to scan all cached URLs. Cache tags are more efficient because they are indexed, but require the origin to set tags via response headers. We support both to give customers flexibility.
# 4. High-Level Design
Now we get to the heart of the system. Rather than presenting a complex diagram upfront, we will build the architecture incrementally, addressing one requirement at a time. This mirrors how you would explain the design in an interview and makes the reasoning behind each component clear.
Our CDN needs to accomplish three core objectives:
1. **Route users to the nearest edge server** to minimize latency
2. **Serve content from cache** when available
3. **Fetch from origin** on cache misses and populate the cache

The first challenge is fundamental: when a user types a URL, how do we get their request to a server close to them rather than our origin server on another continent?


```mermaid
graph TB
    subgraph Clients
        Web[Web Browser]
        Mobile[Mobile App]
    end

    subgraph Load Balancing
        LB[Load Balancer]
    end

    subgraph Message Queue
        QueueKafka[Kafka]
    end

    subgraph CDN
        CDN[Content Delivery Network]
    end

    Web --> LB
    Mobile --> LB
    CDN --> Web
    CDN --> Mobile
```




```mermaid
graph TB
    subgraph Clients
        Web[Web Browser]
        Mobile[Mobile App]
    end

    subgraph Load Balancing
        LB[Load Balancer]
    end

    subgraph Message Queue
        QueueKafka[Kafka]
    end

    subgraph CDN
        CDN[Content Delivery Network]
    end

    Web --> LB
    Mobile --> LB
    CDN --> Web
    CDN --> Mobile
```




```mermaid
graph TB
    subgraph Clients
        Web[Web Browser]
        Mobile[Mobile App]
    end

    subgraph Load Balancing
        LB[Load Balancer]
    end

    subgraph Message Queue
        QueueKafka[Kafka]
    end

    subgraph CDN
        CDN[Content Delivery Network]
    end

    Web --> LB
    Mobile --> LB
    CDN --> Web
    CDN --> Mobile
```



## 4.1 Requirement 1: Route Users to the Nearest Edge Server
This is the foundation of CDN performance. If we cannot get users to nearby servers, nothing else matters. Let's explore how this works.
When a user's browser requests , the first step is DNS resolution. The browser needs to convert `cdn.example.com` into an IP address. This is our opportunity to direct the user to an optimal edge server.

### DNS-Based Routing
The traditional approach is geo-aware DNS. Our authoritative DNS server (the one that "owns" our CDN's domain) returns different IP addresses based on where the request originates.

#### How it works:
1. The user's browser queries their local DNS resolver for `cdn.example.com`.
2. The resolver contacts our authoritative DNS server.
3. Our DNS server examines the resolver's IP address (or the EDNS Client Subnet extension, which reveals the user's actual subnet).
4. Based on geolocation databases, we determine the user is in Tokyo.
5. We return the IP address of our Tokyo PoP.
6. The browser connects directly to Tokyo.

This approach works well and is universally compatible. Every client on the internet uses DNS, so there is no special software required. We can also incorporate health information: if the Tokyo PoP is down, we return the next-closest healthy PoP instead.
The drawback is DNS caching. To reduce DNS query load, resolvers cache responses based on TTL (time-to-live). If we set a 60-second TTL and the Tokyo PoP fails, users with cached DNS entries continue trying to connect to a dead server for up to 60 seconds. Shorter TTLs mean faster failover but higher DNS query volume.

### Anycast Routing
There is another approach that elegantly solves the failover problem: anycast. With anycast, every edge server advertises the same IP address to the internet's routing infrastructure.

#### How it works:
1. All our edge servers globally advertise the same IP address (say, `203.0.113.1`) via BGP (Border Gateway Protocol).
2. Internet routers see multiple paths to this IP address and select the shortest path based on network topology.
3. Traffic automatically flows to the nearest PoP.
4. If a PoP fails and stops advertising the route, traffic instantly shifts to the next-nearest PoP.

The beauty of anycast is that failover happens at the network layer, not the application layer. There are no DNS TTLs to wait out. When a server fails, BGP route withdrawal happens in seconds, and traffic reroutes automatically.
The downside is complexity. Running BGP requires expertise and coordination with upstream network providers. It is also less flexible: you cannot easily make routing decisions based on server load or content availability since the routing happens in network hardware, not your software.

### Which Should We Use?
In practice, major CDN providers use both. Cloudflare, for example, uses anycast for their edge servers (fast failover) and DNS-based routing for their origin shield layer (more control). This hybrid approach gives us the best of both worlds.
For our design, we will use anycast for edge servers and DNS for regional shields.

## 4.2 Requirement 2: Serve Content from Cache
Once users reach an edge server, we need to serve their requested content quickly. This is where the caching architecture becomes critical.
An edge server is essentially a high-performance caching proxy. When a request arrives, the server checks if the requested content exists in its cache. If it does (a "cache hit"), the response is immediate. If not (a "cache miss"), we need to fetch the content from upstream.

### Edge Server Architecture
Each edge server maintains a multi-tiered cache to balance speed and capacity:
**L1: Memory Cache (RAM)**
The fastest tier holds the hottest content. A typical edge server has 64-128 GB of RAM dedicated to caching. Access time is sub-millisecond. At our 50,000 requests per second per PoP load, the vast majority of requests should hit L1.
**L2: SSD Cache**
Content that does not fit in memory but is still popular lives on SSDs. Modern NVMe drives provide 2-4 TB of storage with single-digit millisecond access times. This tier handles the "warm" content that is requested frequently but not frequently enough for RAM.
**L3: HDD Cache**
For large files like videos, we use high-capacity HDDs. Access is slower (10-20ms seek time) but storage is cheap. A video file might be 1 GB, and we cannot keep many of those in RAM.

### Cache Key Design
Every cached item needs a unique identifier. The cache key determines when two requests can share a cached response.
A typical cache key looks like:
For example:
The `Vary` header is particularly important. If the origin returns `Vary: Accept-Encoding`, it means the response differs based on whether the client accepts compression. We need to cache separate versions for gzip, brotli, and uncompressed responses, or we will serve incorrect content to some users.

### The Cache Hit Flow
Let's trace through a cache hit scenario:
1. The request arrives at the edge server.
2. The server computes the cache key from the URL and relevant headers.
3. It checks L1 (memory) first. If found, we are done.
4. The response goes back to the user with `X-Cache: HIT` header.
5. Total latency: typically 10-30ms including network round-trip.

For a cache miss, the flow continues to L2, L3, and eventually upstream. But the goal is to minimize misses through smart caching policies and content pre-positioning.

## 4.3 Requirement 3: Fetch from Origin on Cache Miss
When content is not in the local cache, we need to retrieve it. But fetching directly from the customer's origin server creates problems at scale.
Consider what happens without any intermediate layer. We have 200 edge PoPs, each caching independently. When a new piece of content is requested:
- Each PoP experiences a cache miss
- Each PoP fetches from the origin server
- The origin receives 200 nearly simultaneous requests for the same content

For popular new content, this multiplies quickly. If a homepage is purged and 100,000 users across all PoPs request it in the next second, the origin might receive 200 × thousands of requests instead of a manageable trickle.

### The Solution: Regional Shield (Mid-Tier Cache)
We add an intermediate caching layer between edge servers and the origin. Regional shields are larger, shared caches that serve multiple edge PoPs.

#### How shields work:
1. Edge server in Tokyo receives a cache miss.
2. Instead of going directly to origin, Tokyo queries the Asia Shield in Singapore.
3. If the shield has the content (likely, since it aggregates requests from all Asian PoPs), it responds immediately.
4. Only shield misses reach the origin server.

This dramatically reduces origin load. If our edge cache hit ratio is 95% and our shield hit ratio is 95% of misses:
The shield also implements request coalescing. When multiple edge servers request the same content simultaneously, the shield makes a single origin request and serves all waiting requests from the response.

### The Complete Cache Miss Flow
The user experiences slightly higher latency for cache misses (origin round-trip instead of edge response), but subsequent requests from any PoP in the region will hit the shield cache.

## 4.4 Putting It All Together
Now that we have addressed each requirement individually, let's see the complete architecture. We will also add the control plane components that we have alluded to but not yet discussed.

### Component Responsibilities
Let's summarize what each component does:
| Component | Responsibility | Key Characteristics |
| --- | --- | --- |
| Authoritative DNS | Route users to nearest healthy edge server | Geo-aware responses, health integration, low TTLs |
| Edge Servers (PoPs) | Cache and serve content to end users | Multi-tier cache, TLS termination, 200 locations worldwide |
| Regional Shields | Consolidate cache misses, protect origin | Larger cache, request coalescing, 5-10 locations |
| Customer Origin | Host the original content | Customer-controlled, any HTTP/HTTPS server |
| Configuration Distribution | Push config changes to all PoPs | Routing rules, cache policies, SSL certificates |
| Cache Invalidation | Propagate purge requests globally | Sub-30-second propagation, acknowledgment tracking |
| Health Monitoring | Detect and route around failures | Active probes, passive monitoring, alerting |

The data plane (how content flows) is now clear. The control plane ensures configuration is consistent across all PoPs and that we can respond to customer actions (like purge requests) quickly.
# 5. Database Design
A CDN's storage needs are unusual compared to typical web applications. The primary "database" is the distributed cache itself, holding terabytes of content across hundreds of locations. But we also need persistent storage for configuration, operational metadata, and analytics.

## 5.1 What We Need to Store
Let's categorize our storage needs:
**Cached Content (Ephemeral):** This is the core of the CDN, files cached at edge servers. It is ephemeral by nature: content expires, gets purged, or is evicted when space is needed. We do not use traditional databases for this; it is file-based storage managed by the caching proxy.
**Configuration Data (Persistent):** Customer settings must be consistent, durable, and accessible from every PoP. This includes domain mappings, origin URLs, cache TTL overrides, and SSL certificates.
**Operational Metadata:** Purge requests need tracking to ensure global propagation. Access logs record every request for billing and debugging. Metrics power dashboards and alerting.

## 5.2 Configuration Store
For configuration, we need strong consistency (a configuration change must take effect everywhere), fast reads (config is checked on every request), and global distribution (all 200 PoPs need access).
A distributed key-value store like **etcd** or **Consul** fits well here. These systems provide:
- Strong consistency via Raft consensus
- Watch mechanisms for real-time updates
- Hierarchical key namespaces
- Built-in replication

### Cache Invalidation Log
We need to track purge requests for SLA compliance and debugging:
| Field | Type | Description |
| --- | --- | --- |
| purge_id | String (PK) | Unique identifier for the purge request |
| customer_id | String (FK) | Customer who initiated the purge |
| patterns | JSON | URLs, wildcards, or tags to purge |
| status | Enum | pending, propagating, completed, failed |
| pops_acked | Integer | Count of PoPs that have acknowledged |
| pops_total | Integer | Total PoPs that need to acknowledge |
| created_at | Timestamp | When the purge was initiated |
| completed_at | Timestamp | When all PoPs acknowledged (nullable) |

This log allows us to answer questions like "Did purge X complete within SLA?" and "Which PoPs are slow to acknowledge purges?"

## 5.3 Analytics Storage
High-volume analytics data needs different storage than configuration:
**Access Logs:** Every request generates a log entry. At 10 million requests per second, that is 864 billion log entries per day. We use append-only log storage like Kafka for ingestion, then process into columnar stores like ClickHouse or BigQuery for querying.
**Time-Series Metrics:** Request counts, latencies, cache hit ratios, bandwidth. Time-series databases like InfluxDB or Prometheus handle this well, with downsampling for older data.
**Real-Time Dashboards:** Aggregated metrics for customer dashboards. Pre-computed and cached, updated every few seconds.
The key insight is that analytics data is write-heavy and read patterns are aggregated. We optimize for ingestion throughput and accept eventual consistency for queries.
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often probe deeper into specific challenges. 
In this section, we will explore the trickiest aspects of CDN design: routing strategies, cache invalidation, handling thundering herds, multi-tier caching, TLS management, and security.

## 6.1 Request Routing Strategies
We touched on routing earlier, but let's go deeper. Routing users to the optimal edge server is foundational to CDN performance, and there are multiple valid approaches with different trade-offs.

### Approach 1: DNS-Based Routing
DNS-based routing is the traditional approach. When a user queries DNS for your CDN domain, the authoritative DNS server returns the IP of a nearby, healthy edge server.

#### How location detection works:
The authoritative DNS server receives queries from the user's DNS resolver, not directly from the user. It determines location by:
1. Looking up the resolver's IP address in a geolocation database (MaxMind, IP2Location)
2. Using EDNS Client Subnet (ECS) if available, which includes the user's actual subnet

ECS is more accurate since the resolver might be far from the user (e.g., using Google DNS from Tokyo still queries Google's resolver in the US). With ECS, the query includes information like "client is in 203.0.0.0/16" so we can route appropriately.

#### Pros:
- Universal compatibility with all clients
- Can incorporate sophisticated logic (health, load, cost)
- Easy to implement and debug

#### Cons:
- DNS caching delays failover (must wait for TTL expiration)
- Resolver location may not match user location
- Limited routing granularity

### Approach 2: Anycast Routing
Anycast flips the problem around. Instead of returning different IPs based on location, every edge server advertises the same IP address. The network itself routes traffic to the nearest server.

#### How it works:
Each PoP advertises the same IP prefix (e.g., `203.0.113.0/24`) to its upstream network providers via BGP. Internet routers maintain routing tables showing multiple paths to this prefix and select the shortest path based on AS (Autonomous System) hop count.
When a user in Tokyo sends a packet to `203.0.113.1`, their ISP's router consults its routing table, sees that the Tokyo PoP is the shortest path, and forwards the packet there.

#### Why failover is instant:
If the Tokyo PoP fails and stops advertising its BGP routes, routers globally update their tables within seconds. Traffic automatically shifts to the next-nearest PoP (perhaps Singapore or Seoul). There is no DNS TTL to wait out.

#### Pros:
- Instant failover (no DNS caching issues)
- Routing based on actual network topology, not just geography
- Simpler for clients (single IP address)
- Inherent DDoS resilience (attack traffic distributed across PoPs)

#### Cons:
- Requires BGP expertise and network provider coordination
- Coarse-grained control (cannot route based on server load or content)
- TCP session issues during route changes (connections may break)

### Approach 3: HTTP Redirect Routing
A third option uses application-layer redirects. All DNS queries resolve to a global load balancer, which examines each request and redirects to the optimal edge server.

#### Pros:
- Fine-grained control (can route based on content type, A/B tests, real-time load)
- Immediate effect (no caching at any layer)
- Can incorporate request-level information (cookies, headers)

#### Cons:
- Additional round-trip latency for every request (the redirect)
- Global load balancer becomes a potential bottleneck and single point of failure
- Does not work well for non-browser clients that do not follow redirects

### Which Should We Use?
Here is a comparison table:
| Strategy | Latency | Failover Speed | Flexibility | Complexity |
| --- | --- | --- | --- | --- |
| DNS-Based | Low | 30-60s (TTL) | Medium | Low |
| Anycast | Lowest | Seconds | Low | High |
| HTTP Redirect | Higher (+1 RTT) | Instant | Highest | Medium |

#### Recommendation for our CDN:
Use a hybrid approach, which is what major providers like Cloudflare do:
- **Anycast for edge servers:** Fast failover, automatic load distribution, DDoS resilience
- **DNS for shields:** More control over regional routing, simpler operations

This gives us fast, resilient routing to edge servers where latency matters most, with more controllable routing to shields where we can tolerate DNS delays.

## 6.2 Cache Invalidation
Cache invalidation is famously one of the "two hard problems in computer science" (along with naming things and off-by-one errors). In a CDN context, it is particularly challenging because we need to invalidate across 200+ globally distributed servers within 30 seconds.

### The Challenge
When a customer purges content, several things need to happen:
1. The purge request reaches our control plane
2. We identify all matching cache entries (by URL, pattern, or tag)
3. We notify all 200 PoPs to delete the matching entries
4. Each PoP acknowledges completion
5. We confirm to the customer that the purge is done

All within 30 seconds, reliably, even if some PoPs are temporarily unreachable.

### Approach 1: Push-Based Invalidation
The control plane actively pushes purge commands to all edge servers.

#### How it works:
1. Customer calls `POST /purge` with URLs or patterns
2. Control plane validates the request and writes to a message queue
3. Each PoP has a subscriber consuming from the queue
4. PoPs delete matching cache entries and send acknowledgments
5. Control plane aggregates acknowledgments and updates status

#### Implementation details:
We use a message queue like Kafka for reliable delivery. Each PoP subscribes to a topic partitioned by customer ID. This ensures:
- At-least-once delivery (messages retry until acknowledged)
- Ordering within a customer (purge A before purge B)
- Scalability (each PoP only consumes its relevant messages)

#### Handling unreachable PoPs:
If a PoP is temporarily disconnected, messages queue up. When it reconnects, it processes the backlog. This may exceed our 30-second SLA temporarily, but the purge eventually completes.
For PoPs that are down for extended periods, we mark them unhealthy in DNS so they stop receiving traffic. When they recover, they start with empty caches (safest approach).

#### Pros:
- Predictable latency (messages propagate quickly)
- Reliable delivery via queue semantics
- Easy to monitor (track acknowledgments)

#### Cons:
- Requires robust messaging infrastructure
- Broadcast fan-out to 200+ subscribers

### Approach 2: Pull-Based Invalidation
Edge servers periodically poll for new invalidation instructions.

#### How it works:
1. Customer calls `POST /purge`, control plane writes to an append-only invalidation log
2. Each PoP maintains a version cursor (e.g., "last seen entry #42")
3. Every 5 seconds, PoPs query for entries newer than their cursor
4. PoPs process new entries, delete matching cache entries, update cursor

#### Pros:
- Simpler infrastructure (no pub/sub system needed)
- Resilient to network issues (PoPs catch up when reconnected)
- Lower control plane load (serving reads, not broadcasts)

#### Cons:
- Higher latency (worst case: poll interval + processing time)
- Polling overhead even when no purges exist

### Approach 3: Cache Tags for Efficient Bulk Invalidation
Both approaches above work well for specific URLs. But what if a customer wants to purge "all images for product 123"? They would need to know every URL, which is impractical.
Cache tags solve this by indexing content at cache time:

#### How it works:
1. Origin includes `Cache-Tag` header in responses (e.g., `Cache-Tag: product-123, homepage`)
2. CDN stores content and indexes by tags
3. To purge, customer sends `POST /purge {"tags": ["product-123"]}`
4. CDN looks up tag index, finds all matching URLs, deletes them

#### Pros:
- Efficient bulk purges without URL enumeration
- Flexible organization (tag by product, page type, version, deployment)
- Origin controls tagging logic

#### Cons:
- Requires origin modification to set tags
- Additional storage for tag indexes

### Recommendation
Use **push-based invalidation** as the primary mechanism with **cache tags** for bulk operations:
1. Purge requests go to a Kafka topic
2. Each PoP consumes messages and processes immediately
3. Acknowledgments flow back for status tracking
4. Tags enable efficient pattern-based purges

This combination handles both specific URL purges (fast, simple) and bulk invalidations (efficient, scalable).

## 6.3 Handling Thundering Herd
A thundering herd occurs when many simultaneous requests for uncached content overwhelm the origin. This commonly happens after cache invalidation or when new content suddenly becomes popular.

### The Problem
Consider this scenario:
1. A homepage is purged from all caches
2. 100,000 users request it simultaneously across all PoPs
3. Each PoP sees a cache miss and fetches from origin
4. Origin receives 100,000 concurrent requests
5. Origin becomes overloaded and either slows down or crashes

Even with shields, if 50 edges per shield all miss simultaneously, we have 4 shields × thousands of requests hitting origin.

### Solution 1: Request Coalescing
When multiple requests arrive for the same uncached content, only one request goes to the origin. Others wait for the first to complete.

#### How it works:
1. First request for `/image.jpg` arrives, cache miss
2. Edge marks this URL as "in-flight" and starts origin fetch
3. Second request arrives, sees "in-flight" flag, joins wait queue
4. Requests 3 through N also join the queue
5. Origin response arrives, cache populated
6. All waiting requests served from the fresh cache entry

#### Implementation considerations:
- Use a lock or semaphore keyed by cache key
- Set a timeout for waiting (do not wait forever if origin is slow)
- Handle origin failures gracefully (all waiters get errors)
- Works best at the shield layer (consolidates across PoPs)

#### Pros:
- Dramatic reduction in origin load (N requests become 1)
- Waiting requests get fast responses (cache is warm)

#### Cons:
- First request experiences full origin latency
- Complexity in handling timeouts and failures

### Solution 2: Stale-While-Revalidate
Serve expired content immediately while fetching fresh content in the background.

#### How it works:
HTTP `Cache-Control` supports this pattern:
This means:
- Content is fresh for 1 hour (3600 seconds)
- For the next 24 hours (86400 seconds), serve stale while refreshing
- After 25 hours total, content is truly expired

#### Pros:
- Zero latency impact for users (always served from cache)
- Origin load smoothed out (background refreshes spread over time)

#### Cons:
- Users may see slightly stale content
- Not suitable for content that must be fresh (prices, inventory)

### Solution 3: Probabilistic Early Expiration
Randomize cache expiration times to prevent synchronized expiration.
Instead of all cache entries expiring at exactly the same time:

#### Pros:
- Smooths out refresh traffic over time
- Simple to implement
- Works well for non-coordinated caching

#### Cons:
- Some users experience refresh slightly earlier than necessary
- Does not help with explicit cache purges

### Recommendation
Implement all three strategies in layers:
1. **Request coalescing** at shield layer (primary defense)
2. **Stale-while-revalidate** for content that tolerates staleness
3. **Probabilistic early expiration** to smooth natural TTL refreshes

This multi-layered approach protects origins from both sudden traffic spikes and gradual cache expiration waves.

## 6.4 Multi-Tier Caching (Origin Shield)
We introduced shields earlier, but let's explore the architecture in more depth. Shielding is one of the most impactful optimizations in CDN design.

### The Problem Without Shields
With 200 edge PoPs caching independently:
- Cache miss at each PoP = up to 200 simultaneous origin requests
- New content deployment = thundering herd to origin
- Origin must scale for worst-case: all PoPs missing simultaneously

### How Shields Change the Game
Regional shields aggregate cache misses from multiple edge PoPs:

#### Benefits quantified:
Let's trace the math for 100 requests to new content:
That is a 100x reduction in origin load for this scenario.

#### Cache hit ratio improvement:
Shields also improve effective cache hit ratio. Consider content requested 10 times per hour globally:

### Shield Placement Strategy
Place shields in major internet exchange points to minimize latency to edge PoPs while maintaining proximity to origins:
| Shield Location | Serves | Latency to Edges |
| --- | --- | --- |
| Virginia (US East) | Americas East, South America | 10-50ms |
| Oregon (US West) | Americas West | 10-30ms |
| Amsterdam | Europe, Middle East, Africa | 10-40ms |
| Singapore | Southeast Asia, Oceania | 10-40ms |
| Tokyo | Northeast Asia | 10-30ms |

Fewer shields (5-10 globally) mean larger aggregate caches and better hit ratios. More shields reduce latency to edges but fragment the cache.

### Trade-offs

#### Pros:
- Dramatically reduces origin load (10-100x)
- Higher effective cache hit ratio
- Request coalescing at a central point
- Simpler origin infrastructure requirements

#### Cons:
- Additional infrastructure cost
- One more network hop for cache misses (+10-50ms)
- Shields become critical failure points (require redundancy)

## 6.5 SSL/TLS at the Edge
Modern CDNs must serve content over HTTPS. This requires careful handling of SSL certificates and TLS termination.

### TLS Termination: Where Should It Happen?

#### Edge Termination (Preferred):
TLS handshake happens with the nearby edge server. The connection between edge and origin can be HTTP (for trusted internal networks) or a separate TLS connection.
- Faster: TLS handshake with nearby server instead of distant origin
- Cacheable: Edge can decrypt, cache, and serve content
- Trade-off: Edge servers need access to private keys

#### Pass-Through:
Edge acts as a TCP proxy, forwarding encrypted traffic to origin without decrypting.
- Secure: Private keys never leave origin
- Limitation: Cannot cache (content is encrypted)
- Limited: Loses most CDN benefits

For a CDN, edge termination is essential. We need to decrypt content to cache it.

### Certificate Management
For customers using custom domains (`cdn.customer.com`), the CDN needs their SSL certificates.

#### Option 1: Customer-Provided Certificates
Customer uploads certificate and private key through the management portal.
- Simple for customers with existing certificates
- CDN must securely store and distribute private keys to all PoPs
- Customer responsible for renewal

#### Option 2: CDN-Managed Certificates (Let's Encrypt)
CDN automatically provisions and renews certificates:
- No customer action needed after initial setup
- Automatic renewal (Let's Encrypt certificates expire in 90 days)
- CDN handles all complexity

### Private Key Protection
Private keys at edge servers are high-value targets. Several protection strategies exist:
**Hardware Security Modules (HSMs):** Store keys in tamper-resistant hardware. Keys never exist in memory as plain text.
**Keyless SSL:** Private key operations happen at a central, secure location. Edge servers send data to be signed without seeing the key.
**Short-Lived Certificates:** Reduce window of exposure if a key is compromised by using certificates valid for hours, not months.

## 6.6 DDoS Protection and Security
CDNs sit in front of customer infrastructure, making them natural points for security enforcement. The massive global presence of a CDN also makes it inherently resilient to volumetric attacks.

### Absorbing Volumetric Attacks
A DDoS attack might generate 1 Tbps of traffic. Without a CDN, this would overwhelm most origins. With a CDN:
**Why CDNs absorb attacks effectively:**
1. **Bandwidth capacity:** Major CDNs have 100+ Tbps of aggregate capacity across all PoPs
2. **Geographic distribution:** Attack traffic spreads across many PoPs, each handling a fraction
3. **Anycast:** Attack traffic routes to nearest PoP, naturally distributing load
4. **Edge caching:** Many attack requests hit cache and never reach origin

### Rate Limiting
Protect origins from excessive requests, whether malicious or accidental:
Implementation uses token bucket or sliding window algorithms at the edge. Requests exceeding limits receive `429 Too Many Requests` with a `Retry-After` header.

### Web Application Firewall (WAF)
Inspect requests for malicious patterns:
- SQL injection: `'; DROP TABLE users; --`
- Cross-site scripting: `<script>alert('xss')</script>`
- Path traversal: `../../../../etc/passwd`
- Known CVE exploit signatures

WAF rules run at the edge, blocking attacks before they reach the origin. The trade-off is added latency for request inspection, typically a few milliseconds.

### Bot Detection
Distinguish legitimate users from bots:
- **JavaScript challenges:** Bots often cannot execute JavaScript
- **Fingerprinting:** Browser characteristics, Canvas rendering
- **Behavioral analysis:** Request patterns, mouse movements
- **CAPTCHA:** For suspicious traffic

This protects against scraping, credential stuffing, and inventory hoarding.

### Security Architecture Summary
Each layer filters a category of threats:
1. Anycast distributes volumetric attacks
2. Rate limiting stops abuse and accidental overload
3. WAF blocks application-layer exploits
4. Bot detection filters automated attacks

The origin sees only clean, legitimate traffic.
# References
- [How Cloudflare's Global Anycast Network Works](https://www.cloudflare.com/learning/cdn/glossary/anycast-network/) - Understanding anycast routing in CDNs.
- [Fastly's Real-Time CDN](https://www.fastly.com/products/cdn) - Modern CDN design with instant purging.
- [RFC 7234: HTTP Caching](https://tools.ietf.org/html/rfc7234) - Official HTTP caching specification.
- [Varnish Cache Architecture](https://varnish-cache.org/docs/trunk/users-guide/vcl.html) - Understanding caching proxy internals.

# Quiz

## Design CDN Quiz
In a CDN, what is the primary reason to serve content from edge servers instead of the origin?