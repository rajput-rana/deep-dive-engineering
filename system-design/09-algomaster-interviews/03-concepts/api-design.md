# API Design for System Design Interviews

In almost every system design interview, you’re expected to define the APIs for the system you’re designing.
This is especially true for **product-style questions** (payments, ride hailing, e-commerce), where the API is the primary interface between clients, services, and users.
The depth of API design varies by interviewer. Some will be satisfied with a handful of endpoints and clean request/response shapes. Others will push further: idempotency, pagination, error models, auth, versioning, rate limits, and how your API holds up under real-world edge cases.
A good API shows you understand how clients will actually use the system, what data must flow between components, how to handle failures gracefully, and how to design for change without breaking existing users.
> APIs are contracts. Once published, they're hard to change without breaking clients.

In this chapter, we'll cover what you need to know about API design for interviews: REST fundamentals, GraphQL, RPC/gRPC, resource naming, request/response patterns, pagination and filtering, rate limiting, versioning, authentication, error handling, and practical examples that look like real production APIs.
Most of this chapter focuses on REST, since it’s the most common style in real-world systems and the default expectation in most system design interviews.
# 1. REST Fundamentals
**REST (Representational State Transfer)** is the API style you'll encounter most often, both in interviews and in production systems. Before we get into specific techniques, it helps to understand what REST actually asks of us.

### Core Concepts
REST treats everything as a **resource**, any entity your system manages: users, orders, products, messages. Each resource has a unique identifier (URI), a representation (usually JSON), and a set of standard operations (HTTP methods).
This might seem obvious, but the discipline of thinking in resources shapes how you design everything else. Instead of asking "what actions can users take?", you ask "what things exist in my system, and what can be done to them?"

### HTTP Methods
Each HTTP method has a specific purpose and behavior:
| Method | Purpose | Idempotent | Safe |
| --- | --- | --- | --- |
| GET | Retrieve a resource | Yes | Yes |
| POST | Create a new resource | No | No |
| PUT | Replace a resource entirely | Yes | No |
| PATCH | Partially update a resource | No | No |
| DELETE | Remove a resource | Yes | No |

Two properties matter here: 
- **Idempotent** means calling the operation multiple times produces the same result as calling it once. 
- **Safe** means it doesn't modify server state.

Understanding idempotency is particularly important. If a client's network connection drops during a PUT request, they can safely retry it. The server will end up in the same state whether the first request succeeded or not. POST doesn't have this guarantee, which is why we use idempotency keys (more on that later).

### Statelessness
REST APIs are stateless, meaning each request must contain all the information needed to process it. The server doesn't remember previous requests.
This constraint exists for good reason. When the server maintains no session state, any server instance can handle any request. Load balancers can route traffic freely. Servers can crash and recover without losing context. Scaling becomes a matter of adding more instances rather than synchronizing state between them.
# 2. GraphQL
While REST organizes APIs around resources and HTTP methods, **GraphQL** takes a fundamentally different approach. It gives clients a query language to request exactly the data they need.
Facebook developed GraphQL in 2012 to solve problems they encountered building mobile apps. Mobile clients needed to minimize network requests and avoid fetching unnecessary data. REST's fixed response structures made this difficult.

### Core Concepts
GraphQL has three main operation types:
| Operation | Purpose |
| --- | --- |
| Query | Read data |
| Mutation | Write data (create, update, delete) |
| Subscription | Real-time updates via WebSocket |

Instead of multiple endpoints, GraphQL exposes a single endpoint (typically `/graphql`) that accepts queries describing what data the client wants.

### Schema Definition
GraphQL APIs are defined by a schema that specifies types and their relationships:
The `!` means non-nullable. The schema serves as both documentation and a contract, clients can introspect it to discover available operations.

### Request and Response
GraphQL requests can use either GET or POST:
Responses always have the same structure:
If errors occur, they appear in the `errors` array alongside any partial data that could be resolved.

### Advantages
**No over-fetching or under-fetching.** Clients get exactly the fields they request, nothing more. A mobile app can request minimal data while a web dashboard requests everything.
**Single request for related data.** Instead of making three REST calls to get a user, their posts, and their followers, one GraphQL query handles it all.
**Strong typing and introspection.** The schema is self-documenting. Development tools can provide autocomplete and validation before requests are sent.
**Easier API evolution.** Adding new fields doesn't break existing clients since they only receive fields they request. Deprecation is explicit in the schema.

### Disadvantages
**Complexity.** GraphQL requires more infrastructure: schema definition, resolvers, query parsing, and often caching layers. REST's simplicity is valuable for straightforward APIs.
**Caching challenges.** REST leverages HTTP caching naturally since each URL represents a resource. GraphQL's single endpoint and POST requests make HTTP caching ineffective. You need application-level caching instead.
**N+1 query problem.** Naive implementations can trigger many database queries. If you fetch 10 users and each user's posts, that's potentially 11 queries (1 for users, 10 for posts). Data loaders and batching solve this but add complexity.
**Security concerns.** Clients can request deeply nested data or expensive computations. You need query complexity analysis and depth limiting to prevent abuse.

### When to Use GraphQL
| Scenario | GraphQL Fit |
| --- | --- |
| Mobile apps needing minimal data | Strong |
| Dashboards with varied data needs | Strong |
| Public APIs with diverse clients | Strong |
| Simple CRUD applications | Weak |
| Real-time streaming data | Moderate |
| File uploads | Weak |

GraphQL shines when clients have varied data requirements and network efficiency matters. For simple APIs where every client needs the same data, REST is often simpler.
# 3. RPC and gRPC
**RPC (Remote Procedure Call)** treats API calls like local function calls. Instead of thinking in resources and HTTP methods, you think in procedures: `createUser()`, `getOrdersByUserId()`, `processPayment()`.

### RPC Philosophy
REST asks "what resources exist?" RPC asks "what operations can I perform?"
This maps more naturally to how developers think about their code. Services expose functions, and clients call them.

### gRPC
**gRPC** is Google's modern RPC framework that has become the standard for service-to-service communication. It uses Protocol Buffers (protobuf) for serialization and HTTP/2 for transport.

### Protocol Buffers
Protobuf is a binary serialization format that's smaller and faster than JSON. You define your service and messages in `.proto` files:
The protobuf compiler generates client and server code in your language of choice. Type safety is enforced at compile time.

### gRPC Communication Patterns
gRPC supports four communication patterns:
**Unary RPC** is the simplest, one request, one response:
**Server streaming** returns multiple responses to a single request:
The server sends users one at a time. Useful for large result sets or real-time updates.
**Client streaming** sends multiple requests before receiving a response:
Useful for file uploads or batching data.
**Bidirectional streaming** allows both sides to send streams:
Both client and server can send messages independently. Ideal for chat applications or real-time collaboration.

### Advantages
**Performance.** Protobuf is 3-10x smaller than JSON and faster to parse. HTTP/2 multiplexes requests over a single connection and supports header compression.
**Strong contracts.** The `.proto` file is the single source of truth. Generated code ensures type safety across languages.
**Streaming support.** Built-in support for all streaming patterns makes real-time features straightforward.
**Code generation.** Clients and servers are generated automatically, reducing boilerplate and preventing drift between implementations.
**Deadlines and cancellation.** gRPC has built-in support for request deadlines and cancellation propagation across services.

### Disadvantages
**Browser support.** Browsers can't make gRPC calls directly since they don't expose HTTP/2 primitives. You need gRPC-Web, a proxy that translates between browser-friendly requests and gRPC.
**Not human-readable.** Binary protobuf payloads can't be inspected easily. Debugging requires tooling to decode messages.
**Learning curve.** Protobuf syntax, code generation pipelines, and gRPC concepts take time to learn.
**Limited ecosystem.** REST and JSON have universal support. gRPC tooling is excellent but less ubiquitous.

### When to Use gRPC
| Scenario | gRPC Fit |
| --- | --- |
| Internal microservices | Strong |
| Low-latency requirements | Strong |
| Polyglot environments | Strong |
| Browser clients | Weak |
| Public APIs | Weak |
| Simple integrations | Weak |

gRPC excels for internal service communication where you control both ends, performance matters, and you want strong typing. For public APIs or browser clients, REST or GraphQL are better choices.
# 4. REST vs GraphQL vs gRPC
Each API style has its place. Here's how to choose:
| Factor | REST | GraphQL | gRPC |
| --- | --- | --- | --- |
| Best for | Public APIs, CRUD | Mobile apps, varied clients | Internal services |
| Data format | JSON | JSON | Protobuf (binary) |
| Performance | Good | Good | Excellent |
| Browser support | Native | Native | Requires proxy |
| Learning curve | Low | Medium | High |
| Caching | HTTP caching | Application-level | Application-level |
| Streaming | Limited | Subscriptions | Built-in |
| Tooling | Universal | Good | Excellent (typed) |

### Decision Framework

#### Choose REST when:
- Building a public API that needs broad compatibility
- The API is straightforward CRUD operations
- You want to leverage HTTP caching
- Team familiarity matters

#### Choose GraphQL when:
- Clients have diverse data requirements
- Network efficiency is critical (mobile apps)
- You want to avoid API versioning
- Frontend teams want more control over data fetching

#### Choose gRPC when:
- Building internal microservices
- Low latency is critical
- You need streaming (real-time data, file transfers)
- Strong typing across languages is valuable

### Hybrid Approaches
Many systems use multiple styles:
The API gateway handles external concerns (rate limiting, auth, caching) and translates to gRPC for efficient internal communication. This gives you the best of both worlds, a friendly public API and performant internal services.
# 5. Resource Naming and URL Structure
Good URL design makes your API intuitive. Developers should be able to guess endpoints without reading documentation.
Here are the conventions that make that possible.

### Use Nouns, Not Verbs
Resources are things, not actions. The HTTP method already tells us the action, so the URL should just identify what we're acting on.
This convention exists because it keeps the API predictable. Once developers learn that `/users` is the users collection, they can guess that `GET /users/123` retrieves a specific user without being told.

### Use Plural Nouns
Stick with plural nouns for collections. This avoids awkward inconsistencies.
Even when retrieving a single resource, use the plural form. `/users/123` reads as "from the users collection, get the one with ID 123."

### Represent Hierarchies with Nesting
When resources have parent-child relationships, reflect that in the URL structure.
There's a limit to how deep you should nest. More than 2-3 levels becomes unwieldy and harder to work with. When you find yourself going deeper, consider flattening the hierarchy.
The question to ask is: does this resource only make sense in the context of its parent? An order item might only exist within an order, so nesting makes sense. But a review might be a first-class entity that can be fetched independently.

### URL Structure Pattern
**Examples:**

### Use Hyphens for Readability
When resource names contain multiple words, use hyphens.
With clean URLs established, **what should requests and responses look like?**
# 6. Request and Response Design
With URLs established, let's look at what goes inside the requests and responses.

### Request Body Structure
For POST and PUT requests, keep the JSON structure clean and minimal:
One common mistake is including the ID in the request body when creating a resource. The server generates IDs, so the client shouldn't provide them.

### Response Body Structure
Always return the created or updated resource in the response. This saves the client from making an extra GET request to see the result, including any server-generated fields like `id` or `created_at`.

### HTTP Status Codes
Status codes communicate what happened without the client needing to parse the response body. Use them precisely:
| Code | Meaning | When to Use |
| --- | --- | --- |
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST that creates a resource |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid request syntax or parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource state conflict (e.g., duplicate) |
| 422 | Unprocessable Entity | Valid syntax but invalid data |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side failure |

The distinction between 400 and 422 trips people up. 400 means the request was malformed (invalid JSON, missing required fields). 422 means the request was well-formed but the data doesn't make sense (email already taken, invalid date range).

### Headers
Headers carry metadata about the request and response, not business data. Keep business data in the body.
The `X-Request-ID` header deserves special mention. When a client includes a request ID, echo it back in the response. This makes debugging distributed systems much easier, as you can trace a request across multiple services.
# 7. Pagination
When a collection grows large, you can't return everything at once. Pagination splits results into manageable chunks. The challenge is doing this efficiently and consistently.

### Offset-Based Pagination
The simplest approach. The client specifies how many items to skip (offset) and how many to return (limit).
**Response:**
Offset pagination is easy to understand and lets users jump to any page. But it has two problems that become serious at scale.
First, it gets slow. When you request `offset=10000`, the database must scan and skip 10,000 rows before returning the next 20. This becomes expensive as datasets grow.
Second, it produces inconsistent results. If someone adds a new user while you're paging through the list, you might see the same user twice or miss one entirely. For many applications this is fine, but for financial data or audit logs, it's not.

### Cursor-Based Pagination
Cursor pagination solves both problems by using an opaque token that marks your position in the result set.
**Response:**
The cursor encodes whatever information the server needs to efficiently fetch the next page, typically the ID or timestamp of the last item. The client treats it as an opaque string and just passes it back.
Cursor pagination is efficient because instead of "skip 10,000 rows", the query becomes "get rows where id > 10000 limit 20". Databases handle this query the same way whether you're on page 1 or page 1000.
The tradeoff is that clients can't jump to arbitrary pages. You have to traverse sequentially. This works well for infinite scroll interfaces but not for traditional page-numbered navigation.

### Keyset Pagination
A variant of cursor pagination that makes the cursor transparent, using the last item's sort key directly.
This gives you the efficiency of cursor pagination while keeping the API more explicit. The downside is that clients need to understand what field to use as the key.

#### When to Use Which:
| Use Case | Recommended |
| --- | --- |
| Small datasets (<10K items) | Offset |
| Large datasets | Cursor/Keyset |
| UI with page numbers | Offset |
| Infinite scroll | Cursor |
| Real-time feeds | Cursor |

For most interview scenarios, cursor-based pagination is the safer choice. It scales better and handles concurrent modifications gracefully.
# 8. Filtering, Sorting, and Searching
Pagination gets data in manageable chunks. Filtering, sorting, and searching help clients get the right data.

### Filtering
Allow clients to narrow results using query parameters. Keep the syntax simple and predictable.
Here are the common filter patterns you'll use:
The key principle is consistency. If one endpoint uses `created_after`, all endpoints should use that same convention for date filtering. Clients shouldn't have to guess whether it's `after`, `from`, `since`, or `start_date`.

### Sorting
Use a `sort` parameter with field names. A common convention is to prefix with `-` for descending order.
Some APIs use a more explicit syntax:
Either approach works. The single-parameter version is more compact; the explicit version is clearer for developers new to the API.

### Searching
Full-text search across multiple fields is typically exposed through a `q` or `search` parameter:
For field-specific search, be explicit about what you're matching:

### Combining Everything
In practice: Filters, sorting, and pagination work together:
This returns the top 20 highest-rated electronics priced over $100, starting from the cursor position.
When designing these query parameters, think about what queries will be common. Make those easy. If your product catalog is always filtered by category and sorted by relevance, that should be the default behavior, not something clients have to specify every time.
# 9. Rate Limiting
Rate limiting protects your API from being overwhelmed, whether by accident (a bug in a client's code) or by design (a malicious actor). It also ensures fair usage so one client can't monopolize resources.

### Common Strategies
**Fixed Window** is the simplest approach. Count requests within fixed time periods, like 100 requests per minute.
Fixed window has an edge case: a client could send 100 requests at 12:00:59 and another 100 at 12:01:01, effectively getting 200 requests in 2 seconds. For many applications this is acceptable. When it's not, use sliding window.
**Sliding Window** smooths out this burst behavior by looking at a rolling time window instead of fixed boundaries.
**Token Bucket** takes a different approach. Tokens are added to a bucket at a fixed rate, and each request consumes a token. This naturally allows some burst capacity while limiting sustained throughput.
Token bucket is particularly useful when you want to allow occasional bursts but limit sustained load.

### Rate Limit Headers
Good APIs communicate their limits through response headers. This lets clients pace themselves without hitting limits.
When a client exceeds the limit, return a 429 status with a `Retry-After` header:

### Rate Limit Scopes
Different operations deserve different limits. A simple read is cheap; generating a complex report is expensive.
| Scope | Example Limit |
| --- | --- |
| Per IP | 100 req/min |
| Per User | 1000 req/min |
| Per API Key | 10000 req/min |
| Per Endpoint | Varies |

The exact numbers depend on your infrastructure and business needs, but the principle is to protect expensive operations more aggressively.
# 10. API Versioning
APIs evolve. Requirements change, you learn better ways to model things, and sometimes you make mistakes that need correcting. Versioning lets you make these changes without breaking existing clients.

### URL Path Versioning
The most common approach is putting the version in the URL path.
This is explicit and visible. When a developer looks at a request, they immediately know which version they're using. Load balancers and CDNs can route different versions to different backends. API documentation naturally organizes around versions.
The downside is that URLs change between versions, which can feel inelegant. In practice, this rarely matters.

### Header Versioning
Some APIs put the version in request headers, keeping URLs clean.
Or using a custom header:
This approach keeps URLs stable and lets you version individual resources independently. The downsides are that it's less visible (you can't tell the version from the URL alone) and harder to test casually in a browser.

### Query Parameter Versioning
This is easy to use but can cause caching issues, as proxies might not include query parameters in cache keys. It's also less conventional, which means developers might not expect it.

### When to Create a New Version
You need a new version for breaking changes:
- Removing fields from responses
- Changing field types (string to number)
- Changing field meanings
- Breaking changes to request format

You don't need a new version for:
- Adding new optional fields to responses
- Adding new endpoints
- Adding new optional request parameters

The key insight is that additive changes are usually safe. A well-written client ignores fields it doesn't recognize and doesn't send optional parameters it doesn't need.
For interviews, URL path versioning (`/v1/`, `/v2/`) is the standard recommendation. It's explicit, widely understood, and works well with infrastructure like load balancers and CDNs.
# 11. Authentication and Authorization
These two concepts are often confused. Authentication answers "who are you?" Authorization answers "what are you allowed to do?"

### Authentication (Who are you?)
**API Keys** are the simplest form. A token passed in a header identifies the caller.
API keys work well for server-to-server communication where you trust both ends. They're also common for public APIs that need to track usage or enforce rate limits per customer.
**Bearer Tokens (typically JWT)** encode user information directly in the token.
JWTs are useful because the server can verify the token without a database lookup. The token itself contains the user ID, roles, and expiration time, all cryptographically signed. This makes them popular for user authentication and microservices architectures.
**OAuth 2.0** is a framework for delegated authorization, the scenario where your app wants to access a user's data on another service.
OAuth is appropriate when you need third-party integrations or social login. It's more complex than API keys or JWTs, but it solves a different problem.

### Authorization (What can you do?)
Once you know who the caller is, you need to determine what they're allowed to do.
Several patterns exist for modeling permissions:
| Pattern | Description |
| --- | --- |
| Role-Based (RBAC) | Users have roles (admin, user, viewer) |
| Resource-Based | Permissions tied to specific resources |
| Attribute-Based (ABAC) | Complex rules based on attributes |

In practice, most systems use a combination. Role-based checks gate broad capabilities ("only admins can create users"), while resource-based checks ensure users can only access their own data.
One security consideration: when a user requests a resource they're not authorized to access, should you return 403 (Forbidden) or 404 (Not Found)? Returning 403 confirms the resource exists, which might leak information. If the resource's existence is sensitive, return 404 instead.
# 12. Error Handling
When things go wrong, your API should communicate clearly what happened and what the client can do about it. Consistency matters here. Developers shouldn't have to guess how errors are formatted.

### Error Response Structure
Use a consistent error format across all endpoints:
This structure gives clients everything they need: a machine-readable code for programmatic handling, a human-readable message for logging or display, field-level details for form validation, and a request ID for debugging.

### Error Codes
Define a set of error codes that map to HTTP status codes:
| Code | HTTP Status | Description |
| --- | --- | --- |
| VALIDATION_ERROR | 400 | Invalid input |
| UNAUTHORIZED | 401 | Missing/invalid auth |
| FORBIDDEN | 403 | Not allowed |
| NOT_FOUND | 404 | Resource doesn't exist |
| CONFLICT | 409 | State conflict |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |

The code gives clients a stable identifier to match against. HTTP status codes are useful but too coarse. The same 400 status might mean "invalid JSON" or "email already exists", and clients often need to distinguish between these.

### Error Messages
Include enough detail for developers to debug, but be careful about what you expose.
Never expose internal implementation details:
Stack traces, file paths, database errors, and SQL queries should never appear in API responses. They help attackers understand your system and don't help legitimate clients recover from errors.

### Idempotency Keys for Safe Retries
Network failures happen. When a client sends a POST request and the connection drops, did the server process it or not? Without additional mechanisms, the client has no safe way to retry.
Idempotency keys solve this. The client generates a unique key for each logical operation and includes it in the request:
The server stores this key along with the response. If the client retries with the same key, the server returns the stored response instead of processing the request again.
This is essential for any operation where duplicates would be harmful, payments, order creation, or sending notifications.
# 13. Putting It Together: Design Examples
Let's see how these principles combine in real API designs. These examples demonstrate the patterns you'd use in an interview.

### Example 1: Twitter(X)-like Feed API
The core resources are users, tweets, and the relationships between them.
Notice how the feed endpoint isn't nested under users. It's a computed view tailored to the authenticated user, not a simple collection. Also note that follow/unfollow use POST/DELETE on a sub-resource rather than a toggle endpoint.
The feed response uses cursor pagination since it's a real-time feed where new content appears constantly:

### Example 2: E-commerce Order API
E-commerce involves products, carts, orders, and payments.
The cart is singular (`/cart` not `/carts`) because each user has exactly one active cart.
Order creation uses an idempotency key because duplicate orders would be a serious problem:

### Example 3: Notification Service API
Notifications are simpler but illustrate a few useful patterns.
The `read-all` endpoint is an example of an action that doesn't map cleanly to CRUD operations. It's a bulk operation that affects many resources. Using POST with a descriptive name is the pragmatic solution.
The `meta` field with `unread_count` is a convenience that saves the client from making a separate request to get the badge count.
# 14. Interview Tips
In interviews, API design is usually a small part of the overall discussion, but it reveals how you think about the system from a client's perspective.

### How to Approach API Design in Interviews

#### Start with the core resources
Before drawing any endpoints, identify the main entities: users, orders, products, messages. This grounds the discussion in what the system actually manages.

#### Define the primary operations
For each resource, what can clients do? Most resources need at least list, get, create, update, and delete. Some need additional actions like "cancel order" or "mark as read."

#### Consider relationships
How do resources relate to each other? This determines nesting. A user's orders make sense at `/users/{id}/orders`. But order items might be better as `/orders/{id}/items` rather than deeply nested under users.

#### Think about scale early
If you're listing resources, you'll need pagination. If you're exposing public endpoints, you'll need rate limiting. Mentioning these proactively shows you think about production concerns.

#### Discuss trade-offs
Interviewers want to see your reasoning. Why cursor pagination over offset? Why REST instead of GraphQL? There are no universal right answers, but there are good reasons for each choice in specific contexts.
# Quick Reference
Here's a condensed reference for the patterns covered in this article.

### URL Structure

### Query Parameters

### Headers

### Status Codes
# References
- [REST API Design Best Practices](https://restfulapi.net/) - Comprehensive guide to REST principles
- [HTTP Status Codes](https://httpstatuses.com/) - Complete reference for HTTP status codes
- [Stripe API Reference](https://stripe.com/docs/api) - Excellent real-world API design example
- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines) - Enterprise API design standards
- [JSON:API Specification](https://jsonapi.org/) - Standardized JSON API format

# Quiz

## API Design Quiz
In REST, what does it mean to design the API around “resources”?