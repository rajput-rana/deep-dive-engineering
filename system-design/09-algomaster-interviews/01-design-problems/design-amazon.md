# Design E-commerce Store like Amazon

Amazon is an e-commerce platform that allows users to browse products, add items to their cart, and complete purchases online.
At its core, Amazon connects buyers with products through a seamless shopping experience. It handles everything from product discovery and search to checkout and order fulfillment. The platform serves hundreds of millions of users, hosts millions of products from various sellers, and processes billions of transactions annually.
**Other Popular Examples:** eBay, Alibaba, Flipkart
This system design problem covers a wide range of distributed systems concepts including search, inventory management, payment processing, and handling traffic spikes.
In this chapter, we will explore the **high-level design of an e-commerce platform like Amazon**.
Lets start by clarifying the requirements:
# 1. Clarifying Requirements
E-commerce sounds straightforward on the surface: show products, let users buy them. But the requirements can vary dramatically. 
Are we building for a niche marketplace with thousands of products, or a platform with hundreds of millions of SKUs? Do we need to handle flash sales where inventory sells out in seconds? 
These questions fundamentally shape our architecture.
Here is how a requirements discussion might unfold in an interview:
**Candidate:** "What is the expected scale of the platform? How many users and products should we support?"
**Interviewer:** "Let's design for 100 million daily active users and 100 million products in the catalog."
**Candidate:** "What are the core features we need to support?"
**Interviewer:** "Focus on product browsing, search, cart management, checkout, and order tracking. We don't need to design the seller portal or warehouse management."
**Candidate:** "Should we handle inventory management and prevent overselling?"
**Interviewer:** "Yes, this is critical. We need to ensure users cannot purchase items that are out of stock, especially during high-traffic events."
**Candidate:** "Do we need to support flash sales or promotional events that cause traffic spikes?"
**Interviewer:** "Yes, the system should handle 10x normal traffic during events like Prime Day or Black Friday."
**Candidate:** "What about payments? Should we design the payment processing system?"
**Interviewer:** "Assume we integrate with external payment processors. Focus on ensuring payment reliability and order consistency."
**Candidate:** "What latency and availability targets should we aim for?"
**Interviewer:** "Search and product pages should load within 200ms. The system should be highly available with 99.99% uptime."
After gathering the details, we can summarize the key system requirements.

## 1.1 Functional Requirements
Based on the discussion, here are the features our system must support:
- **Product Catalog:** Users can browse and view product details including images, descriptions, prices, and reviews.
- **Search:** Users can search for products by keywords and filter by category, price, ratings, etc.
- **Shopping Cart:** Users can add, update, and remove items from their cart.
- **Checkout and Orders:** Users can complete purchases and track order status.
- **Inventory Management:** The system must track stock levels and prevent overselling.

## 1.2 Non-Functional Requirements
Beyond features, we need to consider the qualities that make the system production-ready:
- **High Availability:** The system must be highly available (99.99% uptime).
- **Low Latency:** Search and product pages should load within 200ms (p99).
- **Scalability:** Must handle 100M DAU and scale to 10x traffic during peak events.
- **Consistency:** Inventory and orders must be strongly consistent to prevent overselling.
- **Durability:** Order and payment data must never be lost.

# 2. Back-of-the-Envelope Estimation
Before diving into architecture, let's run some numbers to understand what we are dealing with. These estimates will guide our decisions about caching, database selection, and scaling strategies.

### 2.1 Traffic Estimates
Starting with the numbers from our requirements discussion:

#### Read Traffic (Product Views and Searches)
If each of our 100 million daily active users views an average of 20 product pages per session (browsing, comparing, reading reviews), we get:
That is a substantial read load. For context, 23,000 QPS means our system handles about 23,000 product page requests every second, even on a normal day.

#### Write Traffic (Orders)
Not everyone who browses makes a purchase. If roughly 2% of daily active users complete an order:
Order writes are much lower volume than reads, but they require stronger consistency guarantees. A single order involves inventory updates, payment processing, and multiple database writes.

#### Cart Operations
Cart activity falls somewhere between browsing and purchasing. Users add items, change quantities, and remove products as they shop:

### 2.2 Storage Estimates
Let's think about what we need to store and how much space it requires:
| Data Type | Calculation | Storage |
| --- | --- | --- |
| Product metadata | 100M products × 10KB | ~1 TB |
| Product images | 100M × 5 images × 500KB | ~250 TB |
| Orders (1 year) | 2M/day × 2KB × 365 days | ~1.5 TB |
| User data | 500M users × 1KB | ~500 GB |

#### Product Catalog (~1 TB metadata + 250 TB images):
Each product has structured data (name, description, price, seller info, attributes) that averages around 10KB. With 100 million products, that is about 1 TB for metadata alone.
Images are the real storage hog. Five product images per product at 500KB each means 250 TB of image data. This is why product images always live in object storage (S3, CloudFront) rather than in our primary database.

#### Orders (~1.5 TB per year):
Order records are relatively small (order ID, user ID, items, totals, timestamps, shipping info) at around 2KB each. At 2 million orders per day, we accumulate about 1.5 TB of order data annually.

#### User Data (~500 GB):
User profiles, addresses, payment methods, and preferences. With 500 million registered users at roughly 1KB each, this is manageable at around 500 GB.

### 2.3 Key Insights
These numbers reveal several important architectural implications:
1. **Extremely read-heavy workload:** With roughly 1000 reads for every write (order), we should invest heavily in caching. Most product page requests should never hit the database.
2. **Images dominate storage:** Product images account for 99% of storage. Storing them separately in object storage with CDN delivery is essential, not optional.
3. **Peak traffic is the real challenge:** The system needs to handle 230,000 QPS during flash sales. Designing for average load would result in failures during the moments that matter most.
4. **Orders require special care:** While order volume is low compared to reads, each order involves multiple services (inventory, payment, notifications) and requires strong consistency. This is where most complexity lies.

# 3. Core APIs
With our requirements and scale understood, let's define the API contract. An e-commerce platform needs APIs that support the complete user journey: discovering products, managing the cart, and completing purchases.
Let's walk through each endpoint in detail.

### 3.1 Search Products

#### Endpoint: GET /products/search
This is the most frequently called endpoint. Users search, browse, and filter until they find what they want. Performance here directly impacts conversion rates.

#### Request Parameters:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| query | string | Yes | Search keywords (e.g., "wireless headphones") |
| category | string | No | Filter by category ID |
| min_price | number | No | Minimum price filter |
| max_price | number | No | Maximum price filter |
| min_rating | number | No | Minimum average rating (1-5) |
| sort_by | enum | No | Sort by: relevance, price_asc, price_desc, rating, newest |
| page | integer | No | Page number for pagination (default: 1) |
| limit | integer | No | Results per page (default: 20, max: 100) |

#### Example Request:

#### Success Response (200 OK):
The response includes just enough information to render search results. Full product details require a separate API call when the user clicks on a product.

### 3.2 Get Product Details

#### Endpoint: GET /products/{product_id}
When a user clicks on a product, we need to show everything: full description, all images, reviews summary, pricing details, and availability.

#### Success Response (200 OK):
**Error Responses:**
| Status Code | Meaning |
| --- | --- |
| 404 Not Found | Product ID does not exist |

### 3.3 Add to Cart

#### Endpoint: POST /cart/items
When a user clicks "Add to Cart," we need to validate that the product exists and has sufficient stock before adding it.

#### Request Body:

#### Success Response (200 OK):

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Invalid input | Quantity <= 0 or invalid product_id format |
| 404 Not Found | Product does not exist | Product ID not in catalog |
| 409 Conflict | Insufficient stock | Requested quantity exceeds available inventory |

Notice we return a `409 Conflict` for stock issues, not a `400`. The request itself is valid; the conflict is with the current state of inventory. This distinction helps clients handle errors appropriately.

### 3.4 Create Order (Checkout)

#### Endpoint: POST /orders
This is the most critical endpoint. It must coordinate inventory reservation, payment processing, and order creation atomically. If any step fails, the entire operation should be rolled back cleanly.

#### Request Body:

#### Success Response (201 Created):

#### Error Responses:
| Status Code | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Invalid input | Missing required fields |
| 402 Payment Required | Payment failed | Card declined or payment processor error |
| 409 Conflict | Inventory conflict | Item went out of stock during checkout |
| 503 Service Unavailable | Temporary failure | Payment service or inventory service unreachable |

The `402` and `409` errors require different user experiences. A `402` means "try a different payment method," while a `409` means "sorry, someone else bought the last one."

### 3.5 Get Order Status

#### Endpoint: GET /orders/{order_id}
Users want to track their order from confirmation through delivery. This endpoint provides the current status and any available tracking information.

#### Success Response (200 OK):

### 3.6 API Design Considerations
A few design decisions worth noting:
**Idempotency for Orders:** Creating an order should be idempotent to handle network retries safely. We achieve this by requiring an `Idempotency-Key` header. If the same key is submitted twice, we return the cached response from the first request instead of creating a duplicate order.
**Pagination:** Search results use cursor-based pagination for large result sets. Page numbers work fine for reasonable sizes, but cursor-based pagination performs better when users browse deep into results.
**Error Format:** All errors follow a consistent structure with an error code, human-readable message, and optional field-level details for validation errors. This makes client-side error handling predictable.
# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complex diagram upfront, we will build the design incrementally, starting with the simplest requirement and adding complexity as needed. This mirrors how you would explain the design in an interview.
Our system needs to handle three fundamental operations:
1. **Product Discovery:** Users search for products and view product details.
2. **Cart Management:** Users build their shopping cart over a session.
3. **Order Processing:** Users complete purchases reliably.

The traffic patterns for these operations are vastly different. Product discovery handles 23,000+ QPS with mostly read operations. Cart management is read-write at around 5,800 QPS. Order processing is write-heavy but low volume at just 23 QPS.
This asymmetry suggests we should **separate read and write paths** and optimize each independently.
Let's build out the architecture one requirement at a time.

## 4.1 Requirement 1: Product Discovery
Users need to search for products and view product details. This is the highest-traffic operation, handling over 23,000 requests per second. The vast majority of users are browsing, not buying, so optimizing this path has the biggest impact on user experience.

### Components Needed
Let's introduce the components we need to make product discovery work.

#### Product Service
This service owns the product catalog. It manages product metadata, pricing, seller information, and availability status. When you click on a product, the Product Service fetches and assembles all the information you see on the product detail page.
The service is stateless, meaning any instance can handle any request. All state lives in the database and cache layers. This makes horizontal scaling straightforward: just add more instances behind the load balancer.

#### Search Service
Product search is complex enough that it deserves its own service. The Search Service handles keyword queries, applies filters, ranks results by relevance, and returns paginated results.
Behind the scenes, it queries Elasticsearch, which maintains a search index of all products. Elasticsearch excels at full-text search with filters, exactly what we need for "wireless headphones under $100 with 4+ stars."

#### CDN (Content Delivery Network)
Product images are the heaviest assets on any e-commerce page. Loading them from our origin servers would be slow and expensive. Instead, images are served from CDN edge nodes distributed globally.
When a user in Tokyo views a product, the images load from a nearby edge location rather than traveling across the Pacific. This reduces latency from hundreds of milliseconds to tens of milliseconds.

#### Cache Layer (Redis)
Between the CDN and the database, we place a Redis cache. It stores:
- Popular product details (hot products get requested repeatedly)
- Recent search results (common searches like "iPhone case" happen thousands of times)
- Session data for cart management

With a good cache hit ratio (targeting 90%+), most requests never touch the database.

### The Search Flow in Action
Let's trace what happens when a user searches for "wireless headphones".
Here is the step-by-step flow:
1. **Request arrives at Load Balancer:** The user's search request first hits our load balancer, which distributes traffic across multiple API Gateway instances.
2. **API Gateway handles common concerns:** The gateway validates the request format, checks rate limits, and routes the request to the Search Service. By handling these concerns at the edge, we keep application services focused on business logic.
3. **Search Service checks cache:** Before querying Elasticsearch, we check Redis for cached results. Common searches ("iPhone case", "laptop stand") are repeated thousands of times daily. Why query Elasticsearch again when we have fresh results in memory?
4. **Cache miss triggers Elasticsearch query:** If the cache does not have results, we query Elasticsearch. The query includes the search terms, any filters the user applied, and sorting preferences. Elasticsearch returns ranked results within 20-50ms.
5. **Results returned to user:** The Search Service formats the response (product IDs, names, prices, ratings, thumbnail URLs) and returns it through the gateway. We also populate the cache for future identical queries.
6. **Images load from CDN:** The client renders the search results page and requests product thumbnails. These requests go directly to the CDN, not our application servers.

### The Product Detail Flow
When a user clicks on a product from the search results, we need to show the complete product page:
The flow is straightforward:
1. **Check Redis first:** Most popular products are cached. A cache hit returns the product in under 1ms.
2. **Database fallback:** On cache miss, we query the product database. This is slower (20-50ms) but acceptable for cold products.
3. **Populate cache on miss:** After fetching from the database, we write the product to cache with an appropriate TTL (time-to-live). Future requests will hit the cache.
4. **Images from CDN:** Product images load separately from the CDN. They are usually cached at edge nodes, so latency is minimal.

**Why separate the metadata and image requests?** Images are large (hundreds of KB each) and change rarely. Product metadata is small (a few KB) but includes dynamic data like price and availability. Separating them lets us cache each optimally.

## 4.2 Requirement 2: Cart Management
The shopping cart is where browsing becomes buying intent. Users add items, change quantities, and remove products as they shop. This happens at around 5,800 QPS, placing cart management between the high-volume read path and the low-volume order path.
Cart operations have an interesting characteristic: they need to be fast (users expect instant feedback when clicking "Add to Cart"), but they also need to persist across sessions. If a user adds items on their laptop and later opens their phone, they expect to see the same cart.

### Additional Components Needed

#### Cart Service
A dedicated service for managing shopping carts. It handles:
- Adding, updating, and removing items
- Validating that products exist and are available
- Persisting cart state for logged-in users
- Managing guest carts with session-based storage

The Cart Service is a bridge between the read path (showing the cart) and the write path (modifying the cart). It needs to be both fast and durable.

#### Inventory Service
We need to check inventory when users add items to their cart. Nobody wants to build a cart of items only to discover at checkout that they are all out of stock.
The Inventory Service tracks stock levels across all products and warehouses. It can answer "is this product in stock?" in milliseconds.

### The Add to Cart Flow
Let's trace what happens when a user clicks "Add to Cart":
Here is what is happening step by step:
1. **Validate inventory:** Before adding anything, we check with the Inventory Service that the product exists and has sufficient stock. This prevents users from adding unavailable items.
2. **Store in Redis:** The cart itself lives in Redis for fast access. Redis gives us sub-millisecond operations, which is important since cart views happen frequently (users check their cart multiple times during a shopping session).
3. **Persist for logged-in users:** For authenticated users, we asynchronously persist the cart to a database. This enables cross-device cart sync. The async write means we do not slow down the response, but we accept a small risk of data loss if Redis fails before the persist completes.
4. **Return updated cart:** The response includes the complete cart state: all items, quantities, and the updated subtotal.

**A critical design decision: we do not reserve inventory at this stage.**
It might seem logical to reserve stock when items are added to cart. But consider the implications: users add items to carts and then abandon them 70% of the time. If we reserved inventory for every cart add, popular items would show "out of stock" even though most of that reserved inventory will be released when carts are abandoned.
Instead, we only check availability (a read operation) when adding to cart. Actual reservation happens during checkout, which we will discuss next.

### Handling Guest Users
Not all shoppers are logged in. Guest users still need carts that persist through their session.
For guests, we:
1. Generate a temporary cart ID and store it in a cookie
2. Keep the cart in Redis with a reasonable TTL (24-48 hours)
3. Offer to merge the guest cart with their account cart if they log in

This approach balances user experience (no login required to shop) with resource management (guest carts expire if abandoned).

## 4.3 Requirement 3: Order Processing
This is where the rubber meets the road. Everything we have built, the product discovery, the cart management, culminates in checkout. A user is ready to exchange money for goods. The stakes are high: a failed checkout loses a sale, a double charge destroys trust, and overselling creates logistics nightmares.
Order processing only handles about 23 QPS on average, far less than product discovery. But each request involves multiple services that must coordinate perfectly. This is where distributed systems complexity really shows up.

### Additional Components Needed

#### Order Service
The Order Service is the orchestrator of checkout. It does not do much itself, but it coordinates multiple other services in the correct sequence:
1. Verify the cart is valid
2. Reserve inventory
3. Process payment
4. Create the order record
5. Trigger downstream processing

The key challenge is handling partial failures. What if inventory is reserved but payment fails? What if payment succeeds but the order database is down? We need compensating actions for every failure scenario.

#### Payment Service
The Payment Service integrates with external payment processors (Stripe, PayPal, bank APIs). It handles:
- Initiating payment transactions
- Processing payment failures and retries
- Ensuring idempotency (never double-charge a customer)
- Managing payment method validation

This service wraps the complexity of external payment APIs and provides a consistent interface to the Order Service.

#### Message Queue (Kafka/SQS)
Not everything needs to happen synchronously during checkout. Once the order is confirmed, we need to:
- Send a confirmation email
- Notify the warehouse to pick and pack
- Update analytics
- Trigger loyalty point calculations

These can all happen asynchronously. A message queue lets us decouple order creation from downstream processing, making checkout faster and more reliable.

### The Checkout Flow
Checkout is a multi-step process where each step depends on the previous one succeeding. Let's trace through it:
Let's break down each step:

#### Step 1: Reserve Inventory
Before charging the customer, we need to ensure the items are actually available. The Inventory Service reserves the requested quantities, temporarily removing them from available stock. If any item cannot be reserved (out of stock), we abort immediately and return an error.
The reservation has a TTL, typically 10-15 minutes. If checkout is not completed in that time, the reservation expires and stock becomes available again. This prevents abandoned checkouts from blocking inventory.

#### Step 2: Process Payment
With inventory reserved, we attempt to charge the customer. The Payment Service sends the request to the external payment processor and waits for confirmation.
Payment can fail for many reasons: insufficient funds, expired card, fraud detection. If payment fails, we need to release the inventory reservation before returning an error to the user.

#### Step 3: Create Order Record
Payment succeeded. Now we create the order record in our database. This includes:
- Order ID and status
- User information
- All line items with prices at time of purchase
- Shipping address
- Payment reference

This is a critical write. If it fails after payment succeeded, we are in an awkward state. We have charged the customer but have no record of what they bought. We handle this with idempotency keys and retry logic.

#### Step 4: Confirm and Publish
With the order recorded, we:
1. Tell the Inventory Service to convert the reservation into an actual deduction
2. Publish an `OrderCreated` event to the message queue

The message queue triggers downstream processing: sending confirmation emails, notifying fulfillment systems, updating analytics. None of this blocks the checkout response.

### Handling Failures
The checkout flow has multiple failure points. Here is how we handle each:
| Failure Point | Compensating Action |
| --- | --- |
| Inventory reservation fails | Return error immediately (nothing to clean up) |
| Payment fails | Release inventory reservation |
| Order creation fails | Refund payment, release inventory |
| Event publishing fails | Log for retry, order is still valid |

The key principle is that each step has a compensating action that undoes it. This is the Saga pattern in action, which we will explore more in the deep dive section.

## 4.4 Putting It All Together
Now that we have designed each component individually, let's step back and see the complete architecture. This diagram shows how all the pieces fit together to handle the user journey from browsing to purchase.
The architecture follows a layered approach, with each layer having specific responsibilities:
**Client Layer:** Users interact with the system through web browsers or mobile apps. From our backend perspective, they look the same, just HTTP requests.
**Edge Layer:** The CDN serves static assets (images, JavaScript, CSS) from edge locations close to users. The load balancer distributes API traffic across multiple gateway instances.
**Gateway Layer:** The API Gateway handles cross-cutting concerns: authentication, rate limiting, request validation, and routing. It is the single entry point for all API requests.
**Application Services:** Each service owns a specific domain:
- **Search Service:** Handles product search queries
- **Product Service:** Serves product catalog data
- **Cart Service:** Manages shopping carts
- **Order Service:** Orchestrates the checkout flow
- **Inventory Service:** Tracks stock levels and reservations
- **Payment Service:** Processes payments

**Async Processing:** Kafka decouples order creation from downstream processing. Notification Service sends emails, Fulfillment Service coordinates with warehouses.
**Data Layer:** Each service has its own data store optimized for its access patterns. Elasticsearch for search, PostgreSQL for orders, Redis for caching.

### Component Summary
| Component | Purpose | Scaling Strategy |
| --- | --- | --- |
| CDN | Serve static assets globally | Managed service (auto-scales) |
| Load Balancer | Distribute traffic | Managed service |
| API Gateway | Auth, routing, rate limiting | Horizontal (add instances) |
| Search Service | Product search with filters | Horizontal (stateless) |
| Product Service | Serve product catalog | Horizontal (stateless) |
| Cart Service | Manage shopping carts | Horizontal (stateless) |
| Order Service | Orchestrate checkout | Horizontal (stateless) |
| Inventory Service | Track stock levels | Horizontal with careful coordination |
| Payment Service | Process payments | Horizontal (stateless) |
| Elasticsearch | Search index | Cluster with shards |
| Redis | Caching and sessions | Cluster with replicas |
| PostgreSQL | Orders and products | Primary + read replicas |
| Kafka | Event streaming | Cluster with partitions |

This architecture handles our requirements well: the CDN and Redis absorb most read traffic, the stateless services scale horizontally, and the message queue enables reliable async processing. The separation of concerns means we can scale each component independently based on its specific bottlenecks.
# 5. Database Design
With the high-level architecture in place, let's zoom into the data layer. Choosing the right databases and designing efficient schemas are critical decisions that affect performance, scalability, and operational complexity.

## 5.1 Choosing the Right Databases
An e-commerce platform has several distinct data types, each with different access patterns and consistency requirements. Using one database for everything would force uncomfortable trade-offs. Instead, we use specialized databases for each use case.
Let's think through each data type:

#### Product Catalog: NoSQL (DynamoDB or MongoDB)
Products have wildly different attributes depending on their category. A laptop has processor specs, RAM, and screen size. A t-shirt has size, color, and material. A book has author, ISBN, and page count. Trying to fit all this into rigid relational tables leads to either sparse tables full of NULLs or complex EAV (Entity-Attribute-Value) patterns.
NoSQL databases handle this naturally. Each product is a document with whatever attributes it needs. The schema is flexible by design.
Products are also read-heavy (23,000 QPS) and write-light (sellers update products occasionally). NoSQL databases scale reads horizontally with ease.

#### Orders: SQL (PostgreSQL)
Orders are the opposite of products. They have a predictable structure: order header, line items, payment reference, shipping details. The relationships between orders, users, and products are natural to model relationally.
More importantly, orders require ACID transactions. When we create an order, we need to:
- Insert the order record
- Insert all line items
- Update inventory
- Record the payment

These operations must all succeed or all fail. PostgreSQL's transaction guarantees handle this cleanly.

#### Inventory: SQL with Redis assist
Inventory needs strong consistency. We cannot have two checkouts both thinking they got the last item. PostgreSQL's row-level locking gives us this guarantee.
During flash sales, however, thousands of requests hit the same inventory row simultaneously. Even with good indexes, this creates contention. For extreme cases, we use Redis as a fast counter in front of PostgreSQL, which we will discuss in the deep dive.

#### Search: Elasticsearch
Product search requires full-text capabilities that relational databases do not handle well. Queries like "wireless noise cancelling headphones under $200" need:
- Full-text matching across multiple fields
- Fuzzy matching for typos
- Filtering on numeric ranges
- Sorting by relevance score

Elasticsearch is purpose-built for exactly this. It maintains an inverted index of products and returns ranked results in milliseconds.

## 5.2 Database Schema
Now let's define the schema for each data store.

### Products Table (NoSQL)
Since we are using a document database, each product is a flexible document. Here is the typical structure:
The `attributes` field is a flexible map that varies by category. Electronics have specs, clothing has sizes, books have authors. The document model handles this variation naturally.

#### Access patterns supported:
- Get product by ID (primary key lookup)
- List products by category (GSI on category_id)
- List products by seller (GSI on seller_id)

### Inventory Table (PostgreSQL)
Inventory tracks stock across multiple warehouses. A product might have 50 units in the East Coast warehouse and 30 in the West Coast warehouse.
| Field | Type | Description |
| --- | --- | --- |
| product_id | VARCHAR(50) | Product identifier |
| warehouse_id | VARCHAR(50) | Warehouse location |
| available_qty | INTEGER | Available for purchase |
| reserved_qty | INTEGER | Reserved during checkout |
| version | INTEGER | For optimistic locking |
| updated_at | TIMESTAMP | Last modification time |

**Primary Key:** (product_id, warehouse_id)
The composite primary key allows us to track inventory per-warehouse while still efficiently querying total stock for a product.
The `version` column enables optimistic locking. When updating inventory, we include the version in the WHERE clause:
If another transaction modified the row first, this update affects zero rows, and we know to retry.

### Orders Table (PostgreSQL)
Orders need to capture everything about a purchase at the moment it happened, including prices (which may change later) and shipping details.
| Field | Type | Description |
| --- | --- | --- |
| order_id | VARCHAR(50) PK | Unique order identifier |
| user_id | VARCHAR(50) | Customer who placed the order |
| status | ENUM | pending, confirmed, processing, shipped, delivered, cancelled |
| subtotal | DECIMAL(10,2) | Sum of line item prices |
| tax | DECIMAL(10,2) | Tax amount |
| shipping_fee | DECIMAL(10,2) | Shipping cost |
| total | DECIMAL(10,2) | Final amount charged |
| shipping_address_id | VARCHAR(50) | Reference to address |
| payment_id | VARCHAR(50) | Payment transaction reference |
| idempotency_key | VARCHAR(100) | For duplicate prevention |
| created_at | TIMESTAMP | Order placement time |
| updated_at | TIMESTAMP | Last status change |

**Indexes:**
- `user_id` for order history queries
- `created_at` for time-based queries and analytics
- `idempotency_key` (unique) for duplicate prevention

### Order Items Table (PostgreSQL)
Each order contains one or more line items. We store the price at time of purchase because product prices change.
| Field | Type | Description |
| --- | --- | --- |
| order_item_id | VARCHAR(50) PK | Unique line item ID |
| order_id | VARCHAR(50) FK | Parent order |
| product_id | VARCHAR(50) | Product purchased |
| product_name | VARCHAR(255) | Name at time of purchase |
| quantity | INTEGER | Units purchased |
| unit_price | DECIMAL(10,2) | Price per unit at purchase time |
| subtotal | DECIMAL(10,2) | quantity × unit_price |

**Index:** `order_id` for fetching order details
We denormalize `product_name` into this table so order history displays correctly even if the product is later renamed or deleted.
This schema supports our core operations efficiently while maintaining data integrity for the most critical business data: orders and inventory.
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often go deeper into specific components. 
In this section, we will explore the trickiest parts of our design: building an effective search system, preventing overselling during high-traffic events, handling flash sales gracefully, and ensuring orders are processed reliably.

## 6.1 Product Search and Ranking
Search is where most users start their shopping journey. A user types "wireless headphones" and expects to see relevant products in under 200ms. If the results are slow or irrelevant, they leave.
What makes e-commerce search challenging? Unlike web search where you are finding documents, product search needs to:
- Match user intent to product attributes
- Apply multiple filters simultaneously
- Rank by both relevance and business value
- Handle typos, synonyms, and vague queries

Let's explore how to build this.

### Search Architecture
We use Elasticsearch as the search engine. It maintains an inverted index of products, allowing fast full-text queries with filters. But Elasticsearch is just the engine. The real work is in what we index and how we rank.
The architecture separates indexing from querying. Products are indexed asynchronously via a Change Data Capture (CDC) pipeline. When a product is created or updated in the database, the change is captured, streamed through Kafka, and indexed into Elasticsearch. This decoupling means database updates are not blocked by search indexing.

### What We Index
Each product document in Elasticsearch contains:
**Searchable fields** (full-text analyzed):
- Product name and title
- Description and features
- Category names
- Brand name

**Filterable fields** (exact match):
- Price (for range queries)
- Category ID
- Rating (for >= queries)
- Stock status
- Seller ID

**Ranking signals** (used in scoring):
- Sales count (last 30 days)
- Click-through rate
- Conversion rate
- Review count

### Ranking: Beyond Text Matching
Simple text matching is not enough. A user searching for "headphones" should not see obscure products just because they have "headphones" mentioned many times. The ranking function combines multiple signals:
**Text Relevance (BM25):** How well does the product match the query? Matches in the title are weighted higher than matches in the description. A product called "Sony Wireless Headphones" scores higher for "wireless headphones" than a product with that phrase buried in the description.
**Popularity Signals:** Products that sell well and have high click-through rates are probably good matches for similar queries. We incorporate recent sales, CTR from search results, and conversion rates.
**Business Rules:** Sponsored products get a boost (sellers pay for placement). Products with Prime eligibility might be boosted for Prime members. In-stock products rank above out-of-stock.
**Personalization:** A user who frequently buys Sony products might see Sony headphones ranked higher. Someone who always filters by "under $50" might see budget options first.
The final score is a weighted combination of these factors. The exact weights are tuned based on A/B testing and business goals.

### Handling Typos and Synonyms
Users make typos. They search for "wirless headphones" or "headpones". Elasticsearch handles this with fuzzy matching, finding terms within a small edit distance of the query.
Users also use different words for the same thing. "Phone" should match "mobile", "cell phone", and "smartphone". We configure synonym dictionaries in the analyzer.
Autocomplete suggestions help too. As the user types "wire", we suggest "wireless headphones", guiding them to common queries and reducing typos.

### Keeping the Index Fresh
When a seller updates a product price, users should see the new price in search results. But we do not want every product update to block on Elasticsearch indexing.
We use Change Data Capture (CDC) with Debezium. It watches the database transaction log and streams changes to Kafka. A separate indexer service consumes these events and updates Elasticsearch.
This creates a small delay (typically 1-5 seconds) between database update and search index update. For most purposes, this is acceptable. Price changes do not need to be instant in search results. If real-time accuracy is critical, we can bypass the cache for specific queries.

## 6.2 Inventory Management and Preventing Overselling
Few things frustrate customers more than completing checkout only to receive an email saying "sorry, that item is now out of stock." Preventing overselling is not just about accuracy; it is about trust.
The challenge becomes severe during flash sales. Imagine 10,000 users trying to buy the last 100 units of a hot product. If we naively check stock and then decrement it in two separate operations, we create a race condition. Multiple users see "100 in stock," all proceed to checkout, and we end up selling 500 units we do not have.
Let's explore four approaches to this problem, each with different trade-offs.

### Approach 1: Pessimistic Locking
The straightforward approach: lock the inventory row before updating it. No one else can read or modify that row until we release the lock.
**Pros:**
- Simple to understand and implement
- Guarantees consistency; impossible to oversell

**Cons:**
- Creates contention when many users want the same item
- Lock wait times increase under load
- Risk of deadlocks when orders contain multiple items

Pessimistic locking works fine for normal traffic, but it becomes a bottleneck during flash sales. When thousands of requests try to lock the same row, they queue up, and checkout latency suffers.

### Approach 2: Optimistic Locking with Version
Instead of locking upfront, we try the update and detect if someone else modified the row first. We use a version number that increments with each update.
**Pros:**
- No blocking; higher throughput under normal conditions
- Scales well when conflicts are rare

**Cons:**
- High retry rates during flash sales
- Some users may experience "starvation" (never winning the race)

Optimistic locking trades contention for retries. It works well for regular shopping but can degrade during high-concurrency events.

### Approach 3: Reservation Pattern with TTL
This approach acknowledges that checkout is a multi-step process. Instead of decrementing inventory immediately, we reserve it temporarily. The user has a window (say, 10 minutes) to complete payment. If they succeed, the reservation becomes a sale. If they abandon or timeout, the reservation is released.
A background job periodically releases expired reservations:
**Pros:**
- Fair: first-come, first-served semantics
- Users know the item is reserved for them
- Prevents abandoned carts from blocking inventory indefinitely

**Cons:**
- More complex implementation
- Requires background job for cleanup
- TTL tuning is important (too short frustrates users, too long wastes inventory)

### Approach 4: Redis-Based Counter for Flash Sales
For extreme concurrency (thousands of requests per second for the same item), even the database becomes a bottleneck. Redis can handle this with atomic operations.
Redis handles 100,000+ operations per second on a single instance. The DECR operation is atomic, so there is no race condition. We sync the Redis counter back to PostgreSQL asynchronously.
**Pros:**
- Extremely fast (sub-millisecond response)
- Handles massive concurrency without contention

**Cons:**
- Redis is not durable by default; need persistence strategy
- Adds complexity to keep Redis and PostgreSQL in sync
- Only practical for known high-demand items

### Which Approach to Choose?
| Scenario | Recommended Approach |
| --- | --- |
| Normal shopping | Optimistic locking with version |
| Limited stock items | Reservation pattern with TTL |
| Flash sales (pre-planned) | Redis counter with async DB sync |
| Mixed traffic | Reservation by default, Redis for flagged "hot" items |

In practice, you might use multiple approaches. Normal products use optimistic locking. When a flash sale is scheduled, you pre-load that product's inventory into Redis and route traffic there.

## 6.3 Handling Flash Sales and Traffic Spikes
Flash sales are the ultimate stress test for an e-commerce platform. In a matter of seconds, traffic can spike from 10,000 QPS to 500,000 QPS. Everyone wants the same limited-stock item at the exact same moment. The system that handled normal shopping just fine suddenly buckles under 50x the load.
The challenge is not just handling more traffic; it is handling concentrated traffic. During a regular day, requests spread across millions of products. During a flash sale, they all pile onto a handful of hot items.
Let's explore strategies to survive these events.

### The Multi-Layered Defense
No single technique handles flash sales. You need defenses at every layer:

### Strategy 1: Request Queuing
Instead of letting all requests hit the checkout flow simultaneously, queue them and process at a controlled rate.
When a flash sale starts, enable "queue mode" for hot products. Incoming purchase requests go to a Kafka topic. Worker processes consume from the queue at a rate the backend can handle. Users see real-time updates: "You are in line. Position: 1,234. Estimated wait: 3 minutes."
This protects the backend from overload while maintaining fairness. The first users to click get served first.
**Trade-off:** Users experience higher latency, but they get a clear indication of their position rather than a cryptic error page or timeout.

### Strategy 2: Rate Limiting at Multiple Levels
Even before requests reach the queue, we limit how many requests each user can make.
**At the API Gateway:**
- 10 requests per second per authenticated user
- 5 requests per second per IP for anonymous users
- Return `429 Too Many Requests` when exceeded

**At the service level:**
- Circuit breakers that trip when error rates spike
- Bulkheads that isolate flash sale traffic from normal shopping

Users who refresh frantically do not gain an advantage. The system stays stable for everyone.

### Strategy 3: Pre-computed Inventory Tokens
For planned flash sales where we know the exact inventory (say, 1,000 units of a limited edition product), we can pre-generate purchase tokens.
**Before the sale:**
1. Generate 1,000 unique tokens
2. Store them in a Redis set

**During the sale:**
If a user gets a token, they can proceed to checkout. No token means sold out. This is O(1), handles massive concurrency, and physically cannot oversell since there are exactly as many tokens as items.
**Trade-off:** Only works for pre-planned sales with known inventory. Cannot handle dynamic inventory adjustments.

### Strategy 4: CDN and Static Caching
The product page itself can be cached at the CDN edge. Most of the page content (images, descriptions, reviews) does not change during the sale.
For inventory status, use a short TTL (30 seconds) or show approximate counts: "Almost sold out!" instead of "3 remaining." This reduces origin hits while keeping users informed.

### Strategy 5: Graceful Degradation
When the system is under extreme load, shed non-essential work:
- Disable personalized recommendations (show static "popular items" instead)
- Serve cached search results (slightly stale is better than timing out)
- Simplify product pages (fewer images, no reviews section)
- Queue non-urgent operations (analytics events, email notifications)

The core purchase flow stays responsive while everything else temporarily degrades.

### Flash Sale Architecture
Putting it together, here is how traffic flows during a flash sale:
The CDN absorbs page views. Rate limiting caps per-user request rates. The queue buffers the surge. Workers process at a sustainable pace. Redis handles the inventory check. PostgreSQL only sees the rate of successful orders, not the rate of incoming requests.

## 6.4 Order Processing and Reliability
A customer clicks "Place Order" and expects exactly one thing to happen: their order goes through successfully, they are charged once, and their items ship. Sounds simple, but behind the scenes, we are coordinating multiple systems that can each fail independently.
Consider what happens if:
- Inventory is reserved, but payment fails
- Payment succeeds, but the order database write fails
- Everything succeeds, but the confirmation email never sends

Each scenario requires a different recovery strategy. Getting this wrong means angry customers, lost revenue, and support tickets.

### The Saga Pattern
We cannot wrap everything in a distributed transaction. External payment processors do not support two-phase commit. Even if they did, holding locks across network calls would create unacceptable latency.
Instead, we use the Saga pattern: a sequence of local transactions where each step has a compensating action that undoes it if a later step fails.
| Step | Action | Compensation (if later step fails) |
| --- | --- | --- |
| 1 | Reserve inventory | Release reservation |
| 2 | Process payment | Refund payment |
| 3 | Create order record | Mark order as failed |
| 4 | Send confirmation | Retry async (no compensation needed) |

If payment fails in step 2, we execute compensation for step 1 (release inventory). If order creation fails in step 3, we execute compensations for steps 1 and 2 (release inventory, refund payment).
The key insight is that each local transaction is ACID, even though the overall saga is not. We achieve eventual consistency through compensations.

### Idempotency: Handling Retries Safely
Network failures happen. A request might time out even though the server processed it successfully. The client retries, and without proper handling, we might:
- Charge the customer twice
- Create duplicate orders
- Reserve inventory multiple times

The solution is idempotency keys. Every checkout request includes a client-generated UUID:
The server's logic:
If the same idempotency key comes in twice, we return the cached result from the first request. The client might not know their first request succeeded, but the retry gives them the same response without processing again.

### Order State Machine
Orders are not static. They progress through states as they are processed, shipped, and delivered. We model this as a finite state machine:
Each transition is:
- **Atomic:** State changes in a single database transaction
- **Logged:** We record who/what triggered the transition and when
- **Event-driven:** Transitions publish events that trigger notifications, analytics updates, and fulfillment actions

The state machine prevents invalid transitions (you cannot ship an order that was cancelled) and provides a clear audit trail for support inquiries.

## 6.5 Recommendation System
"Customers who bought this also bought..." These recommendation widgets generate a significant portion of e-commerce revenue. Amazon attributes 35% of its sales to recommendations. Even modest improvements in recommendation quality translate to millions in additional revenue.
In a system design interview, you probably will not design a full recommendation system, but understanding the high-level approach shows breadth.

### Types of Recommendations
Different recommendation types serve different purposes:
| Widget | What It Does | Where It Appears |
| --- | --- | --- |
| Frequently bought together | Items commonly purchased together | Product page |
| Customers also viewed | Items viewed by similar users | Product page |
| Based on your history | Personalized to past behavior | Homepage |
| Trending in category | Popular items right now | Category page |
| Recently viewed | Items user looked at | Homepage sidebar |

Each type has different data requirements and freshness needs.

### Architecture Overview
Recommendations involve two pipelines: an offline pipeline that trains models and computes candidates, and an online pipeline that serves recommendations in real-time.
**Offline Pipeline:** User events (views, purchases, searches) flow through Kafka to an event processor that extracts features and updates the feature store. Periodically, ML training jobs use this data to train recommendation models, which are stored for the online pipeline.
**Online Pipeline:** When a user views a product page, the recommendation service:
1. Retrieves pre-computed candidates from cache (fast)
2. Re-ranks candidates based on real-time context (user's current session)
3. Returns the top recommendations

This hybrid approach balances freshness (real-time re-ranking) with performance (pre-computed candidates).

### Algorithm Approaches
**Collaborative Filtering:** Find users with similar behavior and recommend what they liked. "Users who bought X also bought Y." Works well with sufficient data but struggles with new products (cold start).
**Content-Based Filtering:** Recommend items similar to what the user liked based on item attributes (category, brand, price range). Works for new users but can create filter bubbles.
**Hybrid Approaches:** Production systems combine both. Deep learning models create embeddings that capture both user behavior and item attributes, enabling nuanced recommendations.

### Performance Considerations
Recommendations appear on high-traffic pages. They need to be fast:
- **Cache aggressively:** Pre-compute recommendations for popular products and users
- **Load asynchronously:** Render the page first, then load recommendations via AJAX
- **Graceful fallback:** If personalization times out, show trending items instead

The recommendation widget should never block page rendering. Users came to see a product, not to wait for recommendations to load.

## Summary
We have covered a lot of ground in designing an e-commerce platform like Amazon. Let's recap the key challenges and solutions:

### Key Trade-offs to Discuss
In an interview, be prepared to discuss these trade-offs:
**Consistency vs. Availability:**
- Strong consistency for orders and inventory (cannot oversell)
- Eventual consistency for product catalog and search (slightly stale data is acceptable)

**Latency vs. Freshness:**
- Cache aggressively to hit our 200ms latency target
- Accept that cached data might be slightly stale (prices, reviews)
- Use short TTLs for inventory-related data

**Simplicity vs. Scalability:**
- Start with simple approaches (optimistic locking for inventory)
- Add complexity only when needed (Redis counters for flash sales)
- Each additional component adds operational overhead

**Cost vs. Performance:**
- More Redis instances and CDN nodes reduce latency but increase cost
- Pre-computed recommendations are faster but require batch infrastructure
- Right-size for your actual traffic, not theoretical maximums

The best system design answers acknowledge these trade-offs explicitly and justify the choices made based on the requirements.