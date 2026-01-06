# What is an API?

**Reference:** [AlgoMaster - What is an API](https://algomaster.io/learn/system-design/what-is-an-api)

## Summary

An API (Application Programming Interface) defines how different software components interact. It's a contract that specifies what requests can be made, how to make them, and what responses to expect.

## Key Concepts

### API Types

1. **REST API**
   - HTTP-based
   - Stateless
   - Resource-oriented
   - JSON/XML responses

2. **GraphQL API**
   - Single endpoint
   - Client specifies data needed
   - Type-safe
   - Reduces over-fetching

3. **gRPC API**
   - Protocol buffers
   - High performance
   - Type-safe
   - Streaming support

4. **SOAP API**
   - XML-based
   - WSDL definitions
   - Enterprise-focused
   - More verbose

### API Components

1. **Endpoint:** URL where API is accessed
2. **Method:** HTTP verb (GET, POST, PUT, DELETE)
3. **Headers:** Metadata (authentication, content-type)
4. **Body:** Request data (for POST/PUT)
5. **Response:** Data returned by API

## Why It Matters

**Integration:** Enables different systems to communicate.

**Abstraction:** Hides implementation details from consumers.

**Reusability:** Same API used by multiple clients.

**Scalability:** APIs enable microservices architecture.

## Real-World Examples

**Twitter API:** Allows developers to access Twitter data.

**Stripe API:** Payment processing for applications.

**Google Maps API:** Location services integration.

**AWS APIs:** Cloud service management.

**GitHub API:** Repository and user management.

## API Design Principles

### 1. RESTful Design
- Use HTTP methods correctly
- Resource-based URLs
- Stateless
- Cacheable responses

### 2. Versioning
- `/api/v1/users`
- `/api/v2/users`
- Allows evolution without breaking clients

### 3. Documentation
- Clear endpoint descriptions
- Request/response examples
- Error codes
- Authentication methods

### 4. Error Handling
- Consistent error format
- Meaningful error messages
- Appropriate HTTP status codes

## Tradeoffs

### REST vs GraphQL

**REST:**
- ✅ Simple, standard
- ✅ Cacheable
- ✅ Easy to understand
- ❌ Over-fetching
- ❌ Multiple requests

**GraphQL:**
- ✅ Flexible queries
- ✅ Single endpoint
- ✅ Type-safe
- ❌ Complex caching
- ❌ Learning curve

### REST vs gRPC

**REST:**
- ✅ Human-readable
- ✅ Browser-friendly
- ✅ Simple
- ❌ Lower performance
- ❌ Verbose

**gRPC:**
- ✅ High performance
- ✅ Streaming
- ✅ Type-safe
- ❌ Browser limitations
- ❌ More complex

## Design Considerations

### Security

1. **Authentication:** API keys, OAuth, JWT
2. **Authorization:** Role-based access
3. **Rate Limiting:** Prevent abuse
4. **HTTPS:** Encrypt in transit
5. **Input Validation:** Sanitize inputs

### Performance

1. **Caching:** Cache responses
2. **Pagination:** Limit response size
3. **Compression:** Gzip responses
4. **CDN:** Distribute static content

### Monitoring

1. **Metrics:** Request rate, latency, errors
2. **Logging:** Request/response logging
3. **Alerting:** Error rate thresholds
4. **Analytics:** Usage patterns

## Interview Hints

When discussing APIs:
1. Explain what APIs are and why they matter
2. Compare different API types (REST, GraphQL, gRPC)
3. Discuss design principles
4. Address security and performance
5. Give real-world examples

## Reference

[AlgoMaster - What is an API](https://algomaster.io/learn/system-design/what-is-an-api)

