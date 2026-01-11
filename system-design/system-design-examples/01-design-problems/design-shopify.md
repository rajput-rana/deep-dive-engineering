# Design Shopify

## What is Shopify?

Shopify is a multi-tenant e-commerce platform that enables merchants to create online stores, manage products, process orders, and accept payments without building infrastructure from scratch.
The core idea is to abstract away the complexity of running an online business. Merchants focus on their products and customers while Shopify handles storefronts, inventory, checkout, payments, and order fulfillment behind the scenes.
**Popular Examples:** [Shopify](https://www.shopify.com/), [BigCommerce](https://www.bigcommerce.com/), [WooCommerce](https://woocommerce.com/), [Magento](https://business.adobe.com/products/magento/magento-commerce.html)
This system design problem covers multi-tenancy, inventory management, payment processing, and handling traffic spikes during flash sales. It tests your ability to design a system that balances consistency (inventory, payments) with high availability (storefronts).
In this chapter, we will explore the **high-level design of an e-commerce platform like Shopify**.
Let's start by clarifying the requirements:
# 1. Clarifying Requirements
Before starting the design, it's important to ask thoughtful questions to uncover hidden assumptions, clarify ambiguities, and define the system's scope more precisely.
Here is an example of how a discussion between the candidate and the interviewer might unfold:
**Candidate:** "What is the expected scale? How many merchants and how much traffic should we support?"
**Interviewer:** "Let's design for 1 million active merchants, 100 million products total, and 10 million orders per day."
**Candidate:** "Should we focus on the merchant-facing admin panel or the customer-facing storefront?"
**Interviewer:** "Focus primarily on the customer-facing storefront, but include basic merchant capabilities for product and order management."
**Candidate:** "Do we need to handle payment processing ourselves, or can we integrate with payment gateways like Stripe?"
**Interviewer:** "Integrate with external payment gateways. We don't need to build payment infrastructure from scratch."
**Candidate:** "How should we handle inventory? Is it critical to prevent overselling?"
**Interviewer:** "Yes, preventing overselling is critical. Customers should never be able to purchase items that are out of stock."
**Candidate:** "Do we need to support flash sales with traffic spikes?"
**Interviewer:** "Yes, the system should handle sudden traffic spikes, like 10x normal traffic during sales events."
**Candidate:** "What about shipping and fulfillment?"
**Interviewer:** "Focus on order creation and status tracking. Actual shipping logistics is out of scope."
After gathering the details, we can summarize the key system requirements.

## 1.1 Functional Requirements
- **Store Management:** Merchants can create and customize their online stores.
- **Product Catalog:** Merchants can add, update, and organize products with variants (size, color).
- **Inventory Management:** Track stock levels and prevent overselling.
- **Shopping Cart:** Customers can add items to cart and modify quantities.
- **Checkout & Payments:** Process orders and integrate with payment gateways.
- **Order Management:** Track order status from placement to delivery.

## 1.2 Non-Functional Requirements
Beyond features, we need to think about the qualities that make the system production-ready:
- **High Availability:** Storefronts must be available 99.99% of the time. Downtime means lost revenue for merchants.
- **Low Latency:** Product pages should load in under 200ms (p99). Cart and checkout under 500ms.
- **Scalability:** Handle 10x traffic spikes during flash sales without degradation.
- **Strong Consistency for Critical Operations:** Inventory decrements and payment processing must be strongly consistent to prevent overselling and double charges.
- **Multi-Tenancy:** Efficiently support millions of merchants on shared infrastructure while maintaining data isolation.

# 2. Back-of-the-Envelope Estimation
Before designing the architecture, let's understand the scale we are dealing with. These numbers will guide our decisions about database choices, caching strategies, and infrastructure sizing. Even rough estimates help identify potential bottlenecks before we build anything.

### 2.1 Traffic Estimates
Starting with the numbers from our requirements discussion, let's work through the math.

#### Order Volume (Write Traffic)
We expect 10 million orders per day. Converting to queries per second:
But orders are not evenly distributed. Most shopping happens during business hours and evenings. During peak hours, we might see 3x the average load:
During flash sales (Black Friday, product drops), traffic can spike 10x above normal peaks:
That is 3,500 concurrent checkout attempts per second during the most intense moments. Each checkout involves inventory checks, payment processing, and order creation, all operations that need strong consistency.

#### Storefront Browsing (Read Traffic)
For every order placed, many more customers are browsing products. A typical conversion rate in e-commerce is around 2-3%, meaning roughly 100 product views for every purchase. Let's use a 100:1 read-to-write ratio:
That is a lot of read traffic. The good news is that product data changes infrequently, making it highly cacheable. With proper CDN and Redis caching, most of these requests never hit our databases.

### 2.2 Storage Estimates
Let's break down what we need to store and how much space it requires.

#### Product Data
Each product has metadata (name, description, price, variants) plus references to images stored separately:

#### Product Images
Images are large but stored in object storage (S3/GCS), not our primary database:

#### Order Data
Orders accumulate over time and include items, shipping details, and payment references:
After a few years, order data becomes substantial. We will need strategies like archiving old orders to cheaper storage.

#### Inventory Data
Relatively small since it is just counts per product variant:
| Data Type | Size | Growth Rate | Storage Type |
| --- | --- | --- | --- |
| Product metadata | 500 GB | Slow (new products) | PostgreSQL |
| Product images | 250 TB | Slow | Object storage (S3) |
| Orders | 7.3 TB/year | Steady | PostgreSQL + Archive |
| Inventory | 30 GB | Slow | PostgreSQL/Redis |
| Shopping carts | ~50 GB | Ephemeral | Redis |

### 2.3 Bandwidth Estimates
Understanding bandwidth helps us size our network and CDN:
The read bandwidth during flash sales (potentially 17.5 GB/s at 10x peak) is substantial. This is why CDN caching is essential. With a 95% CDN cache hit rate, origin bandwidth drops to a manageable 875 MB/s.

### 2.4 Key Insights
These estimates reveal several important design implications:
1. **Massively read-heavy:** With 100:1 read-to-write ratio, we should invest heavily in caching. The CDN and Redis will handle the vast majority of requests.
2. **Flash sales are the real challenge:** Normal traffic is quite manageable. The 10x spike during flash sales is where systems fail. We need to design for the peak, not the average.
3. **Inventory is the bottleneck:** During flash sales, thousands of customers might try to buy the same limited-quantity item. The inventory system becomes a single point of contention that needs special attention.
4. **Storage is manageable:** Even at scale, our storage requirements (500 GB for products, 7.3 TB/year for orders) are well within what modern databases can handle. Object storage handles the bulk (images).

# 3. Core APIs
With requirements and scale understood, let's define the API contracts. An e-commerce platform serves two distinct user types, merchants who manage their stores and customers who shop, so we need APIs for both.
We will design RESTful APIs that are intuitive and follow standard conventions. Let's walk through the key endpoints.

### 3.1 Create Product

#### Endpoint: POST /api/stores/{store_id}/products
This endpoint allows merchants to add new products to their catalog. Products can have multiple variants (like size and color combinations), each with its own inventory.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| name | string | Yes | Product name (max 200 characters) |
| description | string | Yes | Rich text description |
| base_price | integer | Yes | Price in cents (e.g., 2999 for $29.99) |
| currency | string | No | ISO currency code (defaults to store currency) |
| variants | array | No | List of variant objects with attributes, price adjustments, and SKUs |
| inventory_count | integer | Yes | Initial stock quantity (for products without variants) |
| images | array | No | URLs of product images |
| category_id | string | No | Category for organization |

#### Example Request:

#### Success Response (201 Created):

#### Error Responses:
| Status | Meaning | Common Causes |
| --- | --- | --- |
| 400 Bad Request | Invalid input | Missing required fields, negative price, duplicate SKUs |
| 401 Unauthorized | Not authenticated | Missing or invalid auth token |
| 403 Forbidden | Not authorized | Token valid but not for this store |
| 404 Not Found | Store not found | Invalid store_id |

### 3.2 Get Product

#### Endpoint: GET /api/stores/{store_id}/products/{product_id}
Retrieves product details for display on the storefront. This is the most frequently called endpoint since customers browse products far more often than they purchase.

#### Query Parameters:
| Parameter | Type | Description |
| --- | --- | --- |
| include_inventory | boolean | Include real-time stock levels (default: false for performance) |

#### Success Response (200 OK):
Note that we expose `in_stock` as a boolean rather than exact quantities. This prevents competitors from tracking inventory levels and provides a simpler experience for most use cases.

### 3.3 Add to Cart

#### Endpoint: POST /api/cart/items
Adds a product (or specific variant) to the customer's shopping cart. The cart is identified either by a session cookie for guest users or by user ID for logged-in customers.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| store_id | string | Yes | The store being shopped |
| product_id | string | Yes | Product to add |
| variant_id | string | Conditional | Required if product has variants |
| quantity | integer | Yes | Number of items (positive integer) |

#### Example Request:

#### Success Response (200 OK):

#### Error Responses:
| Status | Meaning | Common Causes |
| --- | --- | --- |
| 400 Bad Request | Invalid input | Quantity less than 1, missing variant for variant product |
| 404 Not Found | Product not found | Invalid product_id or variant_id |
| 409 Conflict | Inventory conflict | Requested quantity exceeds available stock |

The 409 response is important. When inventory is insufficient, we tell the customer immediately rather than letting them discover the problem at checkout. This provides a better experience and reduces abandoned carts.

### 3.4 Checkout

#### Endpoint: POST /api/checkout
This is the critical endpoint that turns a cart into an order. It orchestrates inventory reservation, payment processing, and order creation, all in a reliable, atomic manner.

#### Request Body:
| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| cart_id | string | Yes | The shopping cart to checkout |
| shipping_address | object | Yes | Delivery address with street, city, state, postal_code, country |
| payment_method | string | Yes | Payment token from frontend (Stripe, PayPal, etc.) |
| billing_address | object | No | If different from shipping (defaults to shipping address) |

#### Example Request:

#### Success Response (201 Created):

#### Error Responses:
| Status | Meaning | When It Occurs |
| --- | --- | --- |
| 400 Bad Request | Invalid input | Missing fields, malformed address |
| 402 Payment Required | Payment failed | Card declined, insufficient funds |
| 409 Conflict | Inventory issue | Items no longer available in requested quantities |
| 422 Unprocessable | Validation failed | Cart expired, store suspended |

The 402 and 409 errors are the most common during checkout. For 409 (inventory issues), we return details about which items are problematic so the customer can adjust their cart rather than starting over.

### 3.5 Get Order

#### Endpoint: GET /api/orders/{order_id}
Retrieves order details and current status. Both customers and merchants need this endpoint, though they see slightly different views.

#### Success Response (200 OK):
The status history provides a complete timeline of the order's lifecycle, which helps with both customer support and debugging.

### 3.6 API Design Considerations
A few decisions worth noting:
**Prices in cents:** We store and transmit all monetary values in the smallest currency unit (cents for USD). This avoids floating point precision issues that plague e-commerce systems. $29.99 is stored as 2999.
**Idempotency for checkout:** The checkout endpoint should be idempotent. If a customer double-clicks the "Place Order" button, we should not create two orders. We achieve this with idempotency keys, a unique token submitted with each checkout attempt that lets us deduplicate requests.
**Cart scoped to store:** Each shopping cart is scoped to a single store. Customers shopping across multiple stores have separate carts. This simplifies checkout and matches the mental model of shopping at different stores.
# 4. High-Level Design
Now we get to the interesting part: designing the system architecture. Rather than presenting a complex diagram upfront and hoping it makes sense, we will build the design incrementally. 
We will start with the simplest possible solution and add components as we encounter specific challenges. This mirrors how you would approach the problem in an interview and makes the reasoning behind each component clear.
Our e-commerce platform needs to handle three fundamentally different operations:
1. **Storefront Browsing:** Customers viewing products, searching, and comparing. This is read-heavy, latency-sensitive, and highly cacheable.
2. **Inventory Management:** Tracking what is in stock and preventing overselling. This requires strong consistency and atomic operations.
3. **Checkout Processing:** Taking carts through payment and creating orders. This involves multiple systems, external dependencies, and needs careful failure handling.

The read-to-write ratio (100:1) tells us something important: browsing traffic vastly exceeds purchase traffic. This means our architecture should prioritize fast reads, even if writes are slightly more complex. Caching will be our primary tool for read performance.
Notice how the read path has multiple caching layers. Most requests should be served from the CDN or Redis, with only a small fraction reaching the database. The write path is more direct since every order matters and must be recorded reliably.
Let's build this architecture step by step.


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
        S1[Reconciliation Service]
        S2[dedicated Service]
        S3[Inventory Service]
        S4[the Service]
        S5[core Service]
    end

    subgraph Data Storage
        DBelasticsearch[elasticsearch]
        DBElasticsearch[Elasticsearch]
        DBPostgreSQL[PostgreSQL]
    end

    subgraph Caching Layer
        CacheRedis[Redis]
    end

    subgraph Message Queue
        QueueKafka[Kafka]
    end

    subgraph Object Storage
        Storageobjectstorage[object storage]
        StorageObjectStorage[Object Storage]
        StorageObjectstorage[Object storage]
        StorageS3[S3]
    end

    subgraph CDN
        CDN[Content Delivery Network]
    end

    Web --> LB
    Mobile --> LB
    LB --> S1
    LB --> S2
    LB --> S3
    LB --> S4
    LB --> S5
    S1 --> DBelasticsearch
    S1 --> DBElasticsearch
    S1 --> CacheRedis
    S1 --> QueueKafka
    S2 --> DBelasticsearch
    S2 --> DBElasticsearch
    S2 --> CacheRedis
    S2 --> QueueKafka
    S3 --> DBelasticsearch
    S3 --> DBElasticsearch
    S3 --> CacheRedis
    S3 --> QueueKafka
    S4 --> DBelasticsearch
    S4 --> DBElasticsearch
    S4 --> CacheRedis
    S4 --> QueueKafka
    S5 --> DBelasticsearch
    S5 --> DBElasticsearch
    S5 --> CacheRedis
    S5 --> QueueKafka
    S1 --> Storageobjectstorage
    S1 --> StorageObjectStorage
    S1 --> StorageObjectstorage
    S1 --> StorageS3
    Storageobjectstorage --> CDN
    StorageObjectStorage --> CDN
    StorageObjectstorage --> CDN
    StorageS3 --> CDN
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

    subgraph Application Services
        S1[dedicated Service]
        S2[External Service]
        S3[Stateless Service]
        S4[Product Service]
        S5[Application Service]
    end

    subgraph Data Storage
        DBelasticsearch[elasticsearch]
        DBPostgreSQL[PostgreSQL]
        DBElasticsearch[Elasticsearch]
    end

    subgraph Caching Layer
        CacheRedis[Redis]
    end

    subgraph Message Queue
        QueueKafka[Kafka]
    end

    subgraph Object Storage
        StorageObjectStorage[Object Storage]
        StorageS3[S3]
        Storageobjectstorage[object storage]
        StorageObjectstorage[Object storage]
    end

    subgraph CDN
        CDN[Content Delivery Network]
    end

    Web --> LB
    Mobile --> LB
    LB --> S1
    LB --> S2
    LB --> S3
    LB --> S4
    LB --> S5
    S1 --> DBelasticsearch
    S1 --> DBPostgreSQL
    S1 --> CacheRedis
    S1 --> QueueKafka
    S2 --> DBelasticsearch
    S2 --> DBPostgreSQL
    S2 --> CacheRedis
    S2 --> QueueKafka
    S3 --> DBelasticsearch
    S3 --> DBPostgreSQL
    S3 --> CacheRedis
    S3 --> QueueKafka
    S4 --> DBelasticsearch
    S4 --> DBPostgreSQL
    S4 --> CacheRedis
    S4 --> QueueKafka
    S5 --> DBelasticsearch
    S5 --> DBPostgreSQL
    S5 --> CacheRedis
    S5 --> QueueKafka
    S1 --> StorageObjectStorage
    S1 --> StorageS3
    S1 --> Storageobjectstorage
    S1 --> StorageObjectstorage
    StorageObjectStorage --> CDN
    StorageS3 --> CDN
    Storageobjectstorage --> CDN
    StorageObjectstorage --> CDN
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

    subgraph Application Services
        S1[Order Service]
        S2[Cart Service]
        S3[these Service]
        S4[the Service]
        S5[Stateless Service]
    end

    subgraph Data Storage
        DBPostgreSQL[PostgreSQL]
        DBElasticsearch[Elasticsearch]
        DBelasticsearch[elasticsearch]
    end

    subgraph Caching Layer
        CacheRedis[Redis]
    end

    subgraph Message Queue
        QueueKafka[Kafka]
    end

    subgraph Object Storage
        Storageobjectstorage[object storage]
        StorageObjectstorage[Object storage]
        StorageObjectStorage[Object Storage]
        StorageS3[S3]
    end

    subgraph CDN
        CDN[Content Delivery Network]
    end

    Web --> LB
    Mobile --> LB
    LB --> S1
    LB --> S2
    LB --> S3
    LB --> S4
    LB --> S5
    S1 --> DBPostgreSQL
    S1 --> DBElasticsearch
    S1 --> CacheRedis
    S1 --> QueueKafka
    S2 --> DBPostgreSQL
    S2 --> DBElasticsearch
    S2 --> CacheRedis
    S2 --> QueueKafka
    S3 --> DBPostgreSQL
    S3 --> DBElasticsearch
    S3 --> CacheRedis
    S3 --> QueueKafka
    S4 --> DBPostgreSQL
    S4 --> DBElasticsearch
    S4 --> CacheRedis
    S4 --> QueueKafka
    S5 --> DBPostgreSQL
    S5 --> DBElasticsearch
    S5 --> CacheRedis
    S5 --> QueueKafka
    S1 --> Storageobjectstorage
    S1 --> StorageObjectstorage
    S1 --> StorageObjectStorage
    S1 --> StorageS3
    Storageobjectstorage --> CDN
    StorageObjectstorage --> CDN
    StorageObjectStorage --> CDN
    StorageS3 --> CDN
    CDN --> Web
    CDN --> Mobile
```



## 4.1 Requirement 1: Serving Storefronts
When a customer visits a store, they browse product catalogs, view product details, search for items, and compare options. This is the highest traffic component of our system. We need sub-200ms response times and near-perfect availability since every slow page load costs sales.

### Components for the Storefront
Let's introduce the components we need to serve storefronts efficiently.

#### CDN (Content Delivery Network)
A CDN is a network of servers distributed around the world. When a customer in Tokyo requests a product page, instead of traveling all the way to our origin server in Virginia, the request goes to a nearby CDN edge node.
The CDN serves two purposes for us. First, it caches and delivers static assets, product images, CSS, and JavaScript, from edge locations close to users. Second, it can cache API responses for product data, dramatically reducing load on our origin servers.
For storefronts, the CDN is essential. Product images are the heaviest assets (often megabytes per page), and serving them from edge locations makes pages feel snappy regardless of where the customer is located.

#### Storefront Service
This is our application layer for read operations. When a customer browses products, views details, or searches, the Storefront Service handles the request.
The service is stateless, meaning any instance can handle any request. This makes horizontal scaling straightforward. We can run dozens of instances behind a load balancer and add more as traffic grows.
The service's primary job is to fetch product data (from cache or database), assemble the response, and return it. For search queries, it may also communicate with a dedicated search index.

#### Redis Cache
For requests that miss the CDN (API calls for product data, authenticated requests, personalized content), we have a second layer of caching using Redis.
Redis sits in our data center and provides sub-millisecond latency. We cache product details, category listings, and store configuration. With a well-designed cache strategy, 90%+ of requests can be served without touching the database.

#### Product Database
The source of truth for product information. We use PostgreSQL here because products have complex relationships (product → variants → images → categories) and we need flexible querying capabilities.
The database handles cache misses and write operations from merchants updating their catalogs. With proper indexing and read replicas, it can handle substantial load, but our goal is to minimize database hits through aggressive caching.

### Flow: Viewing a Product Page
Let's trace what happens when a customer clicks on a product:
Let's walk through each step:
1. **Request arrives at CDN:** The customer navigates to `store.myshop.com/products/tshirt-123`. The CDN serves static assets (images, CSS, JavaScript) from the nearest edge location.
2. **API request forwarded:** The product data API request cannot be fully cached at CDN (it may include real-time inventory), so it goes to our origin.
3. **Load balancer routes:** The load balancer picks a healthy Storefront Service instance based on current load.
4. **Redis cache check:** The service first checks Redis for the product data. About 95% of requests find the data in cache and return immediately.
5. **Database fallback:** On a cache miss, the service queries PostgreSQL, retrieves the product with its variants and images, then populates the cache before responding.
6. **Response sent:** The product JSON is returned to the customer's browser, which renders the page.

The beauty of this setup is that popular products stay in cache, and most requests never touch the database. During a flash sale, the same product might be viewed by thousands of customers, but the database only sees a handful of requests.

## 4.2 Requirement 2: Managing Inventory
Now we get to one of the trickiest parts of e-commerce: inventory management. When a customer adds items to their cart or completes checkout, we must ensure the inventory count is accurate. Selling an item that is out of stock (overselling) is one of the worst customer experiences in e-commerce.
The challenge is that inventory operations need strong consistency while handling high concurrency. During a flash sale, thousands of customers might try to buy the same limited-quantity item simultaneously. If ten items are in stock, exactly ten customers should succeed, not nine, not eleven.

### Components for Inventory Management

#### Inventory Service
A dedicated service for all inventory operations. By isolating inventory logic into its own service, we can apply specialized techniques for consistency and performance without affecting other parts of the system.
The Inventory Service handles four main operations:
- **Check availability:** Is this product in stock?
- **Reserve inventory:** Hold items temporarily when added to cart
- **Commit reservation:** Permanently decrement stock when order is placed
- **Release reservation:** Free held items if the cart expires or checkout fails

#### Cart Service
Manages shopping cart state for customers. The cart is ephemeral data, typically stored in Redis with a time-to-live (TTL). Each cart is associated with either a session (for guest users) or a user ID (for logged-in customers).
When items are added to the cart, the Cart Service coordinates with the Inventory Service to ensure the items are actually available. This early check prevents the frustrating experience of completing checkout only to discover the item is sold out.

#### Inventory Database
We keep inventory data in a separate database from products. Why? Because inventory has very different access patterns:
- Products are read-heavy with infrequent updates
- Inventory is write-heavy with constant updates during active shopping

By separating them, we can optimize each independently. The inventory database needs to handle high write concurrency with strong consistency, PostgreSQL with row-level locking works well here.

### Flow: Adding to Cart with Inventory Reservation
When a customer adds an item to their cart, we do not just update the cart. We also reserve the inventory to prevent overselling:
Let's trace through the flow:
1. **Customer adds item:** The customer clicks "Add to Cart" on a product page.
2. **Cart Service requests reservation:** Before adding to the cart, the Cart Service calls the Inventory Service to reserve the requested quantity.
3. **Atomic check and reserve:** The Inventory Service performs an atomic database operation. It checks if `available_stock - reserved >= requested_quantity`. If yes, it increments the `reserved` count. This happens in a transaction to prevent race conditions.
4. **Track reservation expiry:** Reservations are not permanent. We set a TTL (typically 15 minutes) in Redis. If the customer abandons their cart, the reservation expires and the inventory becomes available again.
5. **Update cart:** Only after successful reservation does the Cart Service add the item to the customer's cart in Redis.
6. **Confirm to customer:** The customer sees the item in their cart, knowing it is genuinely reserved for them.

Some systems wait until checkout to check inventory. This leads to a poor experience. Customers fill their cart, proceed to checkout, enter payment details, and then discover the item is sold out. By reserving at add-to-cart time, we catch the problem early and can suggest alternatives.
The trade-off is complexity. We need to track reservations, handle expirations, and manage the reservation pool. But for a system focused on preventing overselling, this is the right approach.

## 4.3 Requirement 3: Processing Checkouts
Checkout is where everything comes together. A customer's browsing journey culminates in a button click that triggers a complex dance of validations, external API calls, and state changes. Getting this right is critical since a failed checkout means lost revenue and a frustrated customer.
The checkout process involves multiple steps that must complete reliably:
1. Validate the cart (items still available, prices correct)
2. Process payment through an external gateway
3. Create the order record
4. Commit inventory (convert reservations to permanent decrements)
5. Trigger post-order actions (emails, merchant notifications)

The tricky part is handling failures at any step. What if payment succeeds but order creation fails? What if the database is briefly unavailable? We need to design for reliability without creating duplicate orders or charging customers twice.

### Components for Checkout

#### Checkout Service
The orchestrator of the checkout flow. It coordinates between Cart, Inventory, Payment, and Order services to complete a purchase.
The Checkout Service is responsible for maintaining transactional integrity across these services. If payment succeeds, the order must be created. If order creation fails, we need a strategy to recover. This is one of the most complex services in our system.

#### Payment Gateway Integration
We integrate with external payment providers (Stripe, PayPal, Square) rather than building our own payment infrastructure. These providers handle the complexities of credit card processing, PCI compliance, fraud detection, and bank integrations.
Our integration follows a two-phase pattern:
1. **Authorize:** Verify the card and reserve funds (but do not charge yet)
2. **Capture:** Actually charge the card after the order is confirmed

This two-phase approach gives us flexibility. If inventory confirmation fails after authorization, we can void the authorization instead of processing a refund.

#### Order Service
Manages the order lifecycle from creation through fulfillment. When a checkout succeeds, the Order Service creates the order record with all relevant details: items, prices, shipping address, and payment reference.
The Order Service also tracks order status as it progresses through fulfillment: pending → processing → shipped → delivered.

#### Message Queue (Kafka)
Not every action needs to complete before we respond to the customer. Sending confirmation emails, notifying merchants, and triggering fulfillment workflows can happen asynchronously.
Kafka provides reliable message delivery with at-least-once semantics. We publish an "order created" event after successful checkout, and various consumers pick it up: the email service, the merchant notification service, the analytics pipeline, and the fulfillment system.

### Flow: Complete Checkout Process
Let's walk through this flow step by step:
**1. Customer initiates checkout:** The customer clicks "Place Order" after entering shipping address and payment details. The frontend tokenizes the payment information (using Stripe.js or similar) so we never see the actual card number.
**2. Validate cart:** The Checkout Service fetches the cart and validates it. Are the items still available? Are the prices current? Is the cart still within the reservation window?
**3. Confirm inventory:** We double-check with the Inventory Service that reservations are still valid. In most cases they are (the customer is checking out within the 15-minute window), but edge cases exist.
**4. Process payment:** This is the critical external call. We send the payment token to the payment gateway and wait for authorization. If the card is declined, we stop here and inform the customer.
**5. Create order:** With payment confirmed, we create the order record. This includes a reference to the payment ID, all cart items with their prices, shipping details, and the calculated totals.
**6. Commit inventory:** We convert the temporary reservations into permanent decrements. The items are now sold, not just reserved.
**7. Publish event:** An "order.created" event goes to Kafka. Downstream consumers handle confirmation emails, merchant notifications, and other post-order tasks.
**8. Return confirmation:** The customer sees their order confirmation with an order ID and estimated delivery date.
**Handling Failures**
What if something fails after payment but before order creation? This is a critical scenario. We handle it with idempotency and reconciliation:
- Each checkout attempt has a unique idempotency key
- If order creation fails, we retry with the same key
- The payment gateway deduplicates charges based on this key
- A background reconciliation job catches any discrepancies between payments and orders

## 4.4 Putting It All Together
Now that we have designed the individual components, let's step back and see the complete architecture. We have also added the Product Service (for merchant product management) and background workers for cleanup and reconciliation tasks.
The architecture follows a layered approach, with each layer having specific responsibilities:
**Client Layer:** Users interact with our system through web browsers, mobile apps, or merchant admin panels. From our infrastructure perspective, they are all HTTP clients.
**Edge Layer:** The CDN sits at the edge, close to users geographically. It caches static assets and can cache API responses. The API Gateway handles authentication, rate limiting, and request validation before passing requests to the application layer.
**Application Layer:** Our core services are stateless and horizontally scalable. Each service owns a specific domain: Storefront for reading, Product for catalog management, Inventory for stock, Cart for shopping sessions, Checkout for purchase flow, and Order for lifecycle management.
**Cache Layer:** Redis provides low-latency access to frequently requested data. We cache products, sessions, cart state, and inventory counts here.
**Storage Layer:** Each domain has its own database optimized for its access patterns. Product images and large assets live in object storage.
**External Services:** Payment processing is handled by external providers. This keeps us out of the PCI compliance burden.
**Messaging Layer:** Kafka enables asynchronous processing. Post-order tasks like emails and notifications happen without blocking the checkout response.
**Background Workers:** The Cleanup Service handles expired reservations and cart cleanup. The Reconciliation Service ensures payments and orders stay in sync.

### Component Responsibilities
| Component | Primary Responsibility | Scaling Strategy |
| --- | --- | --- |
| CDN | Global edge caching, DDoS protection | Managed service (auto-scales) |
| Load Balancer | Traffic distribution, health checks | Managed service or active-passive pair |
| API Gateway | Auth, rate limiting, request validation | Horizontal (add instances) |
| Storefront Service | Read product data, serve pages | Horizontal (stateless) |
| Product Service | Merchant catalog management | Horizontal (stateless) |
| Inventory Service | Stock tracking, reservations | Horizontal with careful DB access |
| Cart Service | Shopping cart state | Horizontal (stateless, Redis-backed) |
| Checkout Service | Orchestrate purchase flow | Horizontal (stateless) |
| Order Service | Order lifecycle management | Horizontal (stateless) |
| Redis Cache | Hot data caching | Redis Cluster (add nodes) |
| PostgreSQL | Persistent storage | Read replicas, then sharding |
| Object Storage | Images, large assets | Managed service (auto-scales) |
| Kafka | Event streaming | Add partitions and brokers |
| Background Workers | Cleanup, reconciliation | Single instance with leader election |

This architecture handles our requirements well. The CDN and Redis cache absorb most read traffic. Stateless services scale horizontally. Inventory and payment operations maintain strong consistency where needed. Asynchronous processing keeps the critical path fast.
# 5. Database Design
With the high-level architecture in place, let's zoom into the data layer. Choosing the right databases and designing efficient schemas are critical decisions that affect performance, scalability, and operational complexity. E-commerce systems have varied data needs: product catalogs need flexible schemas, inventory needs strong consistency, and orders need durability.

## 5.1 Choosing the Right Database
The database choice is not one-size-fits-all. Different parts of our system have fundamentally different requirements. Let's think through each data domain.

### Product Catalog
Products need to support complex queries: searching by name, filtering by category, sorting by price, and handling flexible attributes (a t-shirt has size and color, a laptop has RAM and storage). The workload is heavily read-biased since customers browse far more than merchants update.

#### Access patterns:
- Search products by keyword
- Filter by category, price range, attributes
- Retrieve product with all variants and images
- Update product details (infrequent)

**Our choice:** PostgreSQL for the primary store with Elasticsearch for search. PostgreSQL handles the relational aspects (product → variants → images) while Elasticsearch provides fast full-text search and faceted filtering. Changes in PostgreSQL are synced to Elasticsearch through change data capture.

### Inventory
Inventory is the trickiest data domain. We need strong consistency for atomic updates and high write concurrency during flash sales. If 100 customers try to buy the last 10 items, exactly 10 should succeed.

#### Access patterns:
- Check available quantity for a variant
- Reserve quantity atomically
- Commit or release reservations
- Handle thousands of concurrent updates during sales

**Our choice:** PostgreSQL with row-level locking for the source of truth. We also cache inventory in Redis for fast reads, with Lua scripts for atomic reserve operations during flash sales.

### Orders
Orders are the permanent record of transactions. They need strong durability (never lose an order) and support complex queries for reporting. The pattern is write-heavy initially (new orders), then read-heavy (order history, merchant reports).

#### Access patterns:
- Create order with multiple items
- Update order status
- Query orders by customer, store, date range
- Generate reports and analytics

**Our choice:** PostgreSQL for its ACID guarantees and rich query capabilities. Order data is critical, so we prioritize durability over speed. Read replicas handle reporting queries without affecting the primary.

### Shopping Carts
Carts are ephemeral. They exist for minutes to hours, are modified frequently, and can tolerate some data loss (worst case, the customer rebuilds their cart). Speed matters more than durability here.

#### Access patterns:
- Read cart contents
- Add/remove/update items
- Calculate totals
- Expire abandoned carts

**Our choice:** Redis for its speed and built-in TTL support. Cart data is stored as JSON with a session or user ID as the key. If Redis loses data, the impact is minimal compared to losing orders.
| Data Domain | Primary Need | Choice | Reasoning |
| --- | --- | --- | --- |
| Products | Flexible schema, complex queries | PostgreSQL + Elasticsearch | Relational structure + search |
| Inventory | Strong consistency, atomic ops | PostgreSQL + Redis | ACID for truth, Redis for speed |
| Orders | Durability, complex relations | PostgreSQL | Never lose an order |
| Carts | Speed, ephemeral data | Redis | In-memory, TTL support |

## 5.2 Database Schema
Let's design the schema for our PostgreSQL databases. We have separate logical databases for products/stores, inventory, and orders, though in practice they might share a physical PostgreSQL cluster with schema separation.

### Stores Table
The foundation of our multi-tenant system. Each merchant has one or more stores, and all other data is scoped to a store.
| Field | Type | Description |
| --- | --- | --- |
| store_id | UUID (PK) | Unique identifier for the store |
| merchant_id | UUID (FK) | Owner of the store |
| name | VARCHAR(255) | Store display name |
| domain | VARCHAR(255) UNIQUE | Custom domain (mystore.shopify.com) |
| settings | JSONB | Configuration: theme, currency, timezone, shipping zones |
| created_at | TIMESTAMPTZ | When the store was created |

The `settings` field uses JSONB for flexibility. Different stores need different configurations, and JSONB lets us add new settings without schema migrations.

### Products Table
The product catalog. Each product belongs to a store and can have multiple variants.
| Field | Type | Description |
| --- | --- | --- |
| product_id | UUID (PK) | Unique identifier |
| store_id | UUID (FK) | Owning store |
| name | VARCHAR(255) | Product name |
| description | TEXT | Rich text description |
| base_price | INTEGER | Price in cents |
| category_id | UUID (FK) | Category for organization |
| attributes | JSONB | Flexible product attributes (material, brand, etc.) |
| status | ENUM | 'active', 'draft', 'archived' |
| created_at | TIMESTAMPTZ | Creation time |
| updated_at | TIMESTAMPTZ | Last modification |

**Key indexes:**
The composite indexes support our common query patterns: listing products by store, filtering by category, and searching by keywords.

### Product Variants Table
Products with options (size, color) have multiple variants. Each variant is a purchasable unit with its own SKU and inventory.
| Field | Type | Description |
| --- | --- | --- |
| variant_id | UUID (PK) | Unique identifier |
| product_id | UUID (FK) | Parent product |
| sku | VARCHAR(100) UNIQUE | Stock keeping unit |
| attributes | JSONB | Variant attributes: {"size": "M", "color": "Blue"} |
| price_modifier | INTEGER | Price adjustment from base (can be negative) |
| image_url | VARCHAR(500) | Variant-specific image |

The `price_modifier` allows variants to have different prices. A large size might cost $5 more, represented as `price_modifier: 500`.

### Inventory Table
Tracks stock levels with support for reservations. This table is critical for preventing overselling.
| Field | Type | Description |
| --- | --- | --- |
| variant_id | UUID (PK) | Product variant (1:1 relationship) |
| total_stock | INTEGER | Total inventory count |
| reserved | INTEGER | Items currently reserved in carts |
| version | INTEGER | Optimistic locking version number |
| updated_at | TIMESTAMPTZ | Last update time |

**Available stock calculation:** `available = total_stock - reserved`
The `version` field enables optimistic locking. When updating, we check that the version has not changed:
If another transaction updated the row, `version` will not match and no rows will be affected. The application can then retry.

### Orders Table
The permanent record of purchases. Monetary values are stored in cents to avoid floating-point issues.
| Field | Type | Description |
| --- | --- | --- |
| order_id | UUID (PK) | Unique identifier |
| store_id | UUID (FK) | Store that received the order |
| customer_id | UUID (FK) | Customer who placed the order |
| status | ENUM | 'pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled' |
| subtotal | INTEGER | Sum of item prices (cents) |
| tax | INTEGER | Tax amount (cents) |
| shipping | INTEGER | Shipping cost (cents) |
| total | INTEGER | Final charged amount (cents) |
| shipping_address | JSONB | Delivery address |
| payment_id | VARCHAR(255) | Reference to payment gateway transaction |
| created_at | TIMESTAMPTZ | Order placement time |
| updated_at | TIMESTAMPTZ | Last status update |

**Key indexes:**
The partial index on `status` only includes active orders, keeping the index small and fast for the common case of finding orders that need action.

### Order Items Table
Links orders to the variants that were purchased. We denormalize `unit_price` because product prices may change after the order is placed.
| Field | Type | Description |
| --- | --- | --- |
| order_item_id | UUID (PK) | Unique identifier |
| order_id | UUID (FK) | Parent order |
| variant_id | UUID (FK) | What was purchased |
| quantity | INTEGER | How many |
| unit_price | INTEGER | Price per item at time of order (cents) |
| total_price | INTEGER | quantity × unit_price (cents) |

The `unit_price` captures the historical price. If a merchant changes a product's price later, existing orders are not affected.
# 6. Design Deep Dive
The high-level architecture gives us a solid foundation, but system design interviews often go deeper into specific challenges. 
In this section, we will explore the trickiest parts of our design: multi-tenancy, preventing overselling, handling flash sales, payment processing, cart management, and search. These topics distinguish a good answer from a great one.

## 6.1 Multi-Tenant Architecture
Multi-tenancy is fundamental to Shopify's business model. A single platform serves millions of merchants, each with their own store, products, and customers. From the outside, each store looks independent. Behind the scenes, they share infrastructure.
This creates an interesting tension. We want to share resources (for cost efficiency) while keeping data isolated (for security and performance). A bug should never let one merchant see another's data, and one merchant's Black Friday sale should not slow down another merchant's store.
Let's explore the three main approaches to multi-tenancy and understand when each makes sense.

### Approach 1: Shared Database, Shared Schema
The simplest approach: all merchants share the same database tables. Every record includes a `store_id` column that identifies its owner.

#### How it works:
Every query includes a `store_id` filter:
This pattern extends to all tables: products, orders, customers, inventory. The application layer (or database middleware) enforces that queries always include the appropriate store filter.
**Pros:**
- **Simple operations:** One database to backup, monitor, and maintain.
- **Cost-efficient:** Resources shared across all tenants, no per-merchant overhead.
- **Instant onboarding:** Creating a new store is just inserting a row, takes milliseconds.
- **Easy cross-tenant queries:** For platform-wide analytics and reporting.

**Cons:**
- **Noisy neighbor problem:** One merchant's traffic spike can impact others sharing the same database resources.
- **Query discipline required:** Every query must include the tenant filter. A missing filter is a security breach waiting to happen.
- **Schema changes affect everyone:** Cannot customize the schema for specific merchants.

### Approach 2: Shared Database, Separate Schemas
Each merchant gets their own database schema (namespace) within a shared database instance.

#### How it works:
The application routes queries to the appropriate schema based on the incoming request's store identifier.
**Pros:**
- **Better isolation:** Schemas provide logical separation. A missing WHERE clause cannot leak data.
- **Simpler queries:** No need for store_id in every query since the schema provides context.
- **Per-tenant customization:** Can add custom columns or indexes for specific merchants.

**Cons:**
- **Schema sprawl:** Managing millions of schemas adds operational complexity.
- **Migration challenges:** Schema changes must be applied to every tenant's schema individually.
- **Database limits:** Many databases have practical limits on the number of schemas.

### Approach 3: Database Per Tenant
Each merchant gets their own database instance.

#### How it works:
A connection router or service mesh directs traffic to the appropriate database based on the incoming request.
**Pros:**
- **Complete isolation:** No risk of data leakage. Each merchant is a completely separate island.
- **Independent scaling:** High-traffic stores get dedicated resources. One store's success does not impact others.
- **Compliance friendly:** Easier to meet data residency requirements (store in specific regions) and GDPR deletion requests.

**Cons:**
- **Expensive:** Each database has overhead (memory, connections, management).
- **Operational complexity:** Managing millions of databases requires significant automation.
- **Slow onboarding:** Provisioning a new database can take minutes rather than milliseconds.

### Comparison and Recommendation
| Model | Data Isolation | Cost Efficiency | Operational Complexity | Best For |
| --- | --- | --- | --- | --- |
| Shared Schema | Low (app-enforced) | Excellent | Low | 95% of merchants |
| Separate Schemas | Medium | Good | Medium | Merchants needing customization |
| Database Per Tenant | Complete | Poor | High | Enterprise, compliance needs |

#### Recommendation: Use a hybrid approach.
Most merchants (small to medium stores) go into the shared schema tier. This keeps costs low and operations simple. When a merchant grows and needs more isolation (or is willing to pay for it), we migrate them to separate schemas or dedicated resources.
For the shared schema tier, we shard by `store_id` to distribute load across multiple database clusters. This prevents any single database from becoming a bottleneck while maintaining the simplicity of shared infrastructure.

## 6.2 Inventory Management and Preventing Overselling
Preventing overselling is arguably the most critical technical requirement for an e-commerce platform. When 1,000 customers try to buy the last 10 items during a flash sale, exactly 10 should succeed. Not 9. Not 11. Exactly 10.
Getting this wrong has real consequences. Overselling means telling customers their order is cancelled, which destroys trust. Underselling means leaving money on the table. Both outcomes hurt the merchant.

### The Race Condition Problem
Let's understand why this is hard. Consider a hot product with 10 items in stock:
Without careful handling, both customers read "10 available", both proceed to checkout, and both updates set stock to 9. One item is oversold.
Now imagine this happening with 100 concurrent requests during a flash sale. The problem compounds rapidly.

### Approach 1: Pessimistic Locking
The straightforward solution: lock the inventory row so only one transaction can modify it at a time.

#### How it works:
The `FOR UPDATE` clause acquires an exclusive lock. Other transactions trying to update the same row must wait until the lock is released.
**Pros:**
- **Guaranteed consistency:** Only one transaction modifies inventory at a time. No race conditions possible.
- **Simple logic:** The mental model is straightforward: lock, check, update, unlock.

**Cons:**
- **Poor performance:** Under high concurrency, requests queue up waiting for locks. A flash sale could serialize thousands of requests.
- **Deadlock risk:** If a cart contains multiple products and transactions acquire locks in different orders, deadlocks can occur.
- **Doesn't scale:** The lock becomes a global bottleneck for hot products.

**When to use:** Low-traffic stores where simplicity trumps performance. Not suitable for flash sales.

### Approach 2: Optimistic Locking with Version Number
Instead of locking upfront, optimistic locking detects conflicts at commit time using a version number.

#### How it works:
The key insight: if the version changed between read and update, another transaction modified the row. Our update affects zero rows, and we know to retry.
**Pros:**
- **No blocking:** Transactions do not wait for locks. Multiple reads can happen concurrently.
- **Better throughput:** Higher concurrency than pessimistic locking.
- **Detects conflicts:** Version mismatch clearly indicates a concurrent modification.

**Cons:**
- **Retry overhead:** High contention causes many retries. In a flash sale, 99% of attempts might fail on the first try.
- **Still serialized:** Hot products become serialization points. The database row is still the bottleneck.

**When to use:** Medium-traffic scenarios where some contention is expected but not extreme.

### Approach 3: Reservation System with TTL
This is the approach most e-commerce platforms use. Instead of decrementing stock at checkout time, we reserve inventory when items are added to cart.

#### How it works:
The inventory table tracks both total stock and reserved quantity:
A background job runs periodically to release expired reservations (carts that were abandoned).
**Pros:**
- **Fair ordering:** First to add to cart gets the item. No surprises at checkout.
- **Better UX:** Customers know immediately if an item is available. No checkout failures due to stock issues.
- **Handles abandonment:** Reservations auto-expire, returning inventory to the pool.

**Cons:**
- **Complexity:** Must track reservations, handle expiry, and manage the background cleanup job.
- **Cart hoarding risk:** Malicious users could reserve items without buying. Mitigate with rate limiting and short TTLs.

**When to use:** Most e-commerce systems. This is the standard approach for good reason.

### Approach 4: Redis + Lua for Flash Sales
For extreme traffic scenarios (flash sales with millions of concurrent users), even PostgreSQL with reservations may struggle. The solution: move the hot path to Redis.

#### How it works:
Redis Lua scripts execute atomically, letting us implement check-and-decrement in a single operation:
Redis handles the high-frequency inventory checks during the sale. A background process syncs Redis state back to PostgreSQL for durability.
**Pros:**
- **Blazing fast:** In-memory operations with single-digit millisecond latency.
- **Atomic guarantees:** Lua scripts execute atomically, no race conditions.
- **Horizontal scaling:** Shard by product ID across Redis instances for even more throughput.

**Cons:**
- **Durability concerns:** Redis is primarily in-memory. A crash could lose recent data. Mitigate with Redis persistence (RDB/AOF) and fast sync to PostgreSQL.
- **Operational complexity:** Now you're running two systems that must stay in sync.

**When to use:** Flash sales, product drops, and other extreme traffic events. Use alongside PostgreSQL, not as a replacement.

### Summary and Recommendation
| Approach | Consistency | Throughput | Complexity | Best For |
| --- | --- | --- | --- | --- |
| Pessimistic Locking | Strong | Poor | Low | Low traffic, simple systems |
| Optimistic Locking | Strong | Medium | Medium | Moderate traffic |
| Reservation + TTL | Strong | Good | Medium | Standard e-commerce |
| Redis + Lua | Eventually consistent | Excellent | High | Flash sales |

#### Recommendation: Use a layered approach
For normal traffic, use PostgreSQL with the reservation system. It provides strong consistency and handles typical e-commerce load well.
For flash sales and high-traffic events, route inventory checks through Redis with Lua scripts. Keep PostgreSQL as the source of truth with asynchronous sync. This gives you the best of both worlds: consistency for normal operations and performance when you need it most.

## 6.3 Handling Flash Sales and Traffic Spikes
Flash sales are the ultimate stress test for an e-commerce platform. In seconds, traffic can spike 10-100x as everyone tries to buy the same limited items simultaneously. Product pages, inventory checks, and checkout requests all surge together. If the system cannot handle it, merchants lose sales and customers lose trust.
The challenge is not just handling the load but handling it fairly. When 100,000 people want 1,000 items, 99,000 must be told "sold out" while exactly 1,000 get to purchase. The system cannot crash, and it cannot oversell.
Let's explore strategies to handle this gracefully.

### Strategy 1: Virtual Queue for Checkout
Instead of letting all checkout requests hit the backend simultaneously, put customers in a virtual queue.
**How it works:**
1. Customer clicks "Buy Now" on the flash sale item
2. Instead of processing immediately, the request enters a queue
3. Customer sees a waiting room: "You are in line, position #4,523"
4. Backend workers process the queue in order at a sustainable rate
5. When the customer's turn arrives (or items sell out), they are notified

**Pros:**
- **Fair ordering:** True first-come, first-served. No luck involved.
- **Prevents overload:** Backend processes at whatever rate it can sustain.
- **Better UX than errors:** Waiting is frustrating but better than seeing error pages.

**Cons:**
- **Latency:** Checkout is no longer instant. Customers may wait minutes.
- **Complexity:** Requires queue infrastructure, waiting room UI, and notification system.

**When to use:** Limited-quantity flash sales where fairness matters more than speed.

### Strategy 2: Rate Limiting and Admission Control
Protect the backend by limiting how many requests can enter the system at once.

#### How it works:
Implement using a token bucket, semaphore, or distributed rate limiter (Redis-based).
**Pros:**
- **Protects backend:** Prevents resource exhaustion. Database connections, memory, and CPU stay within limits.
- **Simple implementation:** Most API gateways support rate limiting out of the box.

**Cons:**
- **Poor UX:** Rejected users must retry manually. Feels like a lottery.
- **Not fair:** Users with faster connections or better timing get through. Does not reward "first in line."

**When to use:** As a safety net alongside other strategies. Should not be the only mechanism for flash sales.

### Strategy 3: Pre-warming and Auto-scaling
Prepare the system before the sale starts rather than reacting after traffic arrives.

#### How it works:
1. **Cache warming:** Load flash sale products into Redis and CDN before the sale starts
2. **Pre-scale:** Spin up additional service instances and database read replicas
3. **Static rendering:** Pre-generate product pages, serve entirely from CDN
4. **Dedicated infrastructure:** Route flash sale traffic to isolated servers to protect regular traffic

**Pros:**
- **Reduces real-time load:** Most read traffic served from cache and CDN. Database barely touched.
- **Predictable performance:** Resources are already provisioned when traffic arrives.
- **Protects other merchants:** Flash sale traffic hits dedicated infrastructure.

**Cons:**
- **Cost:** Over-provisioning resources for a short event is expensive.
- **Requires planning:** Must know sale timing in advance. Does not help with unexpected viral moments.

**When to use:** Always. This is baseline preparation for any flash sale, combined with other strategies.

### Strategy 4: Lottery System
For extremely limited items (10 units for 100,000 interested buyers), a first-come-first-served model creates a stampede. A lottery can be fairer.

#### How it works:
1. **Registration window:** Sale opens for registration (e.g., 10 minutes). Users sign up to express interest.
2. **Random selection:** After the window closes, randomly select winners equal to inventory count.
3. **Exclusive checkout:** Winners receive a time-limited link to complete their purchase.
4. **Waitlist:** Non-winners join a waitlist in case winners do not complete checkout.

**Pros:**
- **Fair:** Everyone has an equal chance, regardless of connection speed or timing. Users in different time zones are not disadvantaged.
- **Eliminates stampede:** No rush to be first. Traffic spreads over the registration window.
- **Prevents bots:** Can include CAPTCHA and rate limiting during registration.

**Cons:**
- **Different UX:** Some users expect first-come-first-served and find lotteries frustrating.
- **Winner no-shows:** Must handle unclaimed reservations with a waitlist system.

**When to use:** Extremely limited drops (limited edition sneakers, exclusive merch) where fairness is paramount.

### Combining Strategies: The Layered Approach
Real systems use multiple strategies together:

#### Recommendation:
1. **Before sale:** Pre-warm caches, pre-scale infrastructure, pre-render pages to CDN
2. **During sale:**
3. **Graceful degradation:** Disable non-essential features (reviews, recommendations, wishlists) during peak to focus resources on checkout
4. **For extreme cases:** Consider a lottery system for very limited items

## 6.4 Payment Processing
Payment processing is where real money moves, and mistakes are costly. Double-charging a customer damages trust. Missing a payment means lost revenue. A security breach can be catastrophic. This is one area where "eventually consistent" is not acceptable.

### The Failure Modes
Payments can fail at multiple points, and each requires different handling:
Consider this nightmare scenario:
1. Customer clicks "Pay"
2. We send the charge request to Stripe
3. Stripe successfully charges the card
4. Before we receive the response, our server crashes
5. Customer sees an error and clicks "Pay" again
6. Result: Customer charged twice

Or the opposite: we think payment failed, so we do not create the order. But the payment actually succeeded. The customer is charged but never receives their product.

### Idempotency: The Foundation
The key to safe payment processing is idempotency. The same request, no matter how many times it is sent, should produce the same result.

#### How it works:
1. For each checkout attempt, generate a unique `idempotency_key` (typically a UUID)
2. Before processing, check if this key was already processed
3. If yes, return the cached result without re-charging
4. If no, process the payment and cache the result

Notice that we pass the idempotency key to the payment gateway too. Stripe, PayPal, and other providers support idempotency keys. If we accidentally send the same request twice, they will not double-charge.

### Two-Phase Payments: Authorize, Then Capture
For better control over the payment flow, separate authorization (reserving funds) from capture (actually charging).
**Flow:**
1. **Authorize:** Verify the card is valid and reserve funds. The customer sees a "pending" charge but is not actually billed.
2. **Inventory check:** Confirm items are available
3. **Capture or Void:**

**Why this matters:**
- **Flexibility:** We can cancel before actually charging the customer
- **Better inventory sync:** Only charge if we can fulfill the order
- **Avoid refunds:** Voiding an authorization is instant and free. Refunds can take days and may incur fees.

### Handling Different Failure Types
Different failures require different responses:
| Failure | What Happened | How to Handle |
| --- | --- | --- |
| Card declined | Invalid card, insufficient funds, expired | Show error, let customer try another card |
| Network timeout | Connectivity issue with gateway | Check payment status with gateway, retry if not processed |
| Gateway error | Payment provider is down | Queue for retry, notify customer of delay |
| Fraud detected | Suspicious transaction pattern | Block transaction, flag for review |
| 3D Secure required | Bank wants extra verification | Redirect customer to bank's auth page |

For network timeouts, never assume the payment failed. Always check the status with the gateway before retrying:

### Payment State Machine
Track every payment through well-defined states with timestamps:
Store every state transition with timestamp, user, and reason. This audit trail is essential for:
- Customer support: "What happened to my payment?"
- Financial reconciliation: Matching payments with orders
- Dispute resolution: Evidence for chargebacks
- Debugging: Understanding what went wrong

### Payment Record Schema
The `payment_events` table creates an append-only log of everything that happened to each payment. Never delete from this table.

## 6.5 Cart Management
Shopping carts seem simple at first glance, but they involve interesting design decisions around storage, state management, cross-device sync, and handling the transition from guest to logged-in user.
A cart is interesting because it sits at the boundary between ephemeral and persistent. It is not as permanent as an order, but losing a cart is frustrating for users. The right design depends on your priorities.

### Storage Options

#### Option 1: Server-Side (Redis)
Store the cart in Redis, keyed by session ID or user ID.
**Pros:**
- **Persistent:** Cart survives browser refresh, tab close, or even browser restart
- **Cross-device:** User starts on phone, continues on laptop. Same cart.
- **Inventory validation:** Server can check stock before adding items
- **Analytics:** Track cart abandonment and conversion

**Cons:**
- **Server load:** Every cart operation hits Redis
- **Session management:** Must link anonymous sessions to logged-in users
- **Latency:** Network round-trip for every cart view

#### Option 2: Client-Side (LocalStorage)
Store the cart entirely in the browser's local storage. No server interaction until checkout.
**Pros:**
- **Zero server load:** Cart operations are instant, no network needed
- **Works offline:** User can browse and add to cart without connectivity
- **Privacy:** Cart data never leaves the device until checkout

**Cons:**
- **Device-specific:** Cart on phone is invisible from laptop
- **Stale data:** Prices and inventory may have changed since item was added
- **Limited space:** LocalStorage has ~5MB limit per domain
- **Lost on clear:** Users who clear browser data lose their cart

#### Option 3: Hybrid Approach
Best of both worlds: client-side for guest users, server-side for logged-in users.
- **Guest users:** Cart stored in LocalStorage. Fast, no account required.
- **Logged-in users:** Cart stored in Redis. Persistent, cross-device.
- **On login:** Merge the LocalStorage cart into the server cart.

This is what most e-commerce platforms do. It minimizes friction for guests while providing the best experience for registered users.

### Cart Merging on Login
When a guest user logs in, they might have two carts:
1. **Session cart:** Items added while browsing as a guest
2. **Account cart:** Items saved from a previous logged-in session

What should happen?
| Strategy | Behavior | When to Use |
| --- | --- | --- |
| Replace | Account cart overwrites session cart | Almost never, loses recent items |
| Merge, sum quantities | Combine items, add quantities together | Good default |
| Merge, keep max | Combine items, take the higher quantity | Prevents accidental duplicates |
| Prompt user | Show both carts, let user choose | Complex products or high-value items |

**Our recommendation:** Merge with summed quantities, but cap at available inventory. If the user had 2 of an item in their guest cart and 3 in their account cart, they get 5 (or the max available, whichever is lower).

### Cart Expiration
Carts cannot live forever. Abandoned carts hold inventory reservations that should be released. Expired carts also consume storage.
**Expiration policy:**
- **Guest carts:** 24-48 hours TTL
- **Logged-in carts:** 7-30 days TTL
- **TTL refresh:** Extend TTL on any cart activity (add, remove, view)

Implementation with Redis:
A background job should periodically clean up carts that are about to expire and release their inventory reservations.

## 6.6 Search and Product Discovery
When a customer visits a store with thousands of products, they need to find what they want quickly. Good search is the difference between a sale and a bounce. Customers expect to type "blue shirt", make a typo like "bleu shrit", and still find the right product.
Building e-commerce search is challenging because it must be fast (sub-100ms), relevant (right products first), forgiving (handle typos), and scoped (only show products from this store).

### Architecture
The pattern is straightforward: use a dedicated search engine alongside the primary database.
PostgreSQL remains the source of truth for product data. When a merchant updates a product, the change flows through CDC (Change Data Capture, using tools like Debezium) to Elasticsearch. Search queries hit Elasticsearch directly, never touching PostgreSQL.

### Search Features

#### Full-Text Search
Search across multiple fields: product name, description, category, tags, and attributes.
The `^3` boost means matches in the `name` field are weighted 3x higher than matches in other fields. This puts exact product name matches at the top.

#### Fuzzy Matching (Typo Tolerance)
Customers make typos. "Sheos" should still find "Shoes".
Elasticsearch's fuzzy matching uses edit distance (how many character changes needed to match). "AUTO" adjusts tolerance based on word length.

#### Faceted Search
Show counts per category, price range, brand, size, and color. Let customers refine their search.

#### Relevance Ranking
Not all matches are equal. Relevance ranking determines which products appear first.
Factors to consider:
- **Text match quality:** Exact phrase matches > partial matches
- **Popularity:** Best-selling products ranked higher
- **Recency:** Newer products may get a boost
- **Stock status:** In-stock items ranked above out-of-stock
- **Merchant preferences:** Allow merchants to pin certain products

### Multi-Tenant Search
Every search must be scoped to the current store. A customer on Store A should never see products from Store B.
The `filter` clause enforces tenant isolation. Using `filter` instead of `must` for these conditions improves performance since filters are cached and do not affect relevance scoring.
**Index Strategy Options:**
| Strategy | Approach | Pros | Cons |
| --- | --- | --- | --- |
| Single index | All products in one index, filter by store_id | Simple to manage, efficient for small stores | Large stores may impact others |
| Index per store | Each store gets its own index | Complete isolation, custom analyzers per store | Management overhead at scale |
| Sharded by store | Single index, routing by store_id | Good balance of isolation and simplicity | Requires careful shard configuration |

**Recommendation:** Start with a single index and `store_id` filtering. If specific stores grow large enough to cause noisy neighbor problems, migrate them to dedicated indices.

### Search Index Schema
The `name` field has both text (for full-text search) and keyword (for exact match and sorting) sub-fields. The `attributes` field stores variant data but is not indexed for search (just returned in results).
# References
- [Shopify Engineering Blog](https://shopify.engineering/) - Real-world insights from Shopify's engineering team
- [Designing Data-Intensive Applications](https://dataintensive.net/) - Foundational concepts for distributed systems
- [Stripe API Documentation](https://stripe.com/docs/api) - Payment integration patterns and best practices
- [Elasticsearch: The Definitive Guide](https://www.elastic.co/guide/en/elasticsearch/guide/current/index.html) - Search implementation details

# Quiz

## Design Shopify Quiz
In a Shopify-like platform, which operation most strongly requires strong consistency to meet the requirement 'never oversell'?