# API Design

**Reference:** [AlgoMaster - API Design](https://algomaster.io/learn/system-design-interviews/api-design)

## Problem / Concept Overview

API design defines how clients interact with your system. Well-designed APIs are intuitive, consistent, and scalable. Poor API design leads to confusion, breaking changes, and developer frustration.

## Key Ideas

### RESTful Principles

1. **Resource-Based URLs**
   ```
   GET    /users/123          # Get user
   POST   /users               # Create user
   PUT    /users/123           # Update user
   DELETE /users/123           # Delete user
   ```

2. **HTTP Methods**
   - GET: Read (idempotent, safe)
   - POST: Create (not idempotent)
   - PUT: Update/Replace (idempotent)
   - PATCH: Partial update (idempotent)
   - DELETE: Remove (idempotent)

3. **Status Codes**
   - 200: Success
   - 201: Created
   - 400: Bad Request
   - 401: Unauthorized
   - 404: Not Found
   - 500: Server Error

## Design Principles

### 1. Consistency
- Use consistent naming (camelCase or snake_case)
- Consistent error format
- Consistent pagination

### 2. Versioning
```
/api/v1/users
/api/v2/users
```
- Allows evolution without breaking clients
- Deprecate old versions gradually

### 3. Pagination
```
GET /users?page=1&limit=20
GET /users?offset=0&limit=20
GET /users?cursor=abc123&limit=20
```
- Cursor-based preferred for large datasets
- Prevents performance issues

### 4. Filtering & Sorting
```
GET /users?status=active&sort=created_at&order=desc
```
- Flexible querying
- Use query parameters, not path

### 5. Error Handling
```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User with ID 123 does not exist",
    "details": {}
  }
}
```
- Consistent error format
- Meaningful error codes
- Include context

## Why It Matters

**Developer Experience:** Good APIs are easy to understand and use, reducing integration time.

**Maintainability:** Well-designed APIs are easier to evolve without breaking changes.

**Performance:** Efficient API design reduces unnecessary requests and data transfer.

**Adoption:** Intuitive APIs get adopted faster.

## Real-World Examples

**Stripe API:** Clean, consistent, well-documented—industry standard.

**GitHub API:** RESTful, versioned, comprehensive documentation.

**Twitter API:** Evolved through versions, learned from mistakes.

**AWS APIs:** Consistent across services, though complex.

## Tradeoffs

### REST vs GraphQL
- **REST:** Simple, cacheable, standard
- **GraphQL:** Flexible queries, single endpoint, over-fetching prevention

### REST vs gRPC
- **REST:** Human-readable, HTTP-based, simple
- **gRPC:** High performance, type-safe, streaming support

### JSON vs XML
- **JSON:** Lightweight, easy to parse, modern standard
- **XML:** Verbose, more features, legacy systems

## API Patterns

### 1. Collection Pattern
```
GET    /users              # List
POST   /users              # Create
GET    /users/123          # Get one
PUT    /users/123          # Update
DELETE /users/123          # Delete
```

### 2. Nested Resources
```
GET /users/123/posts       # User's posts
POST /users/123/posts      # Create post for user
```

### 3. Actions
```
POST /users/123/activate
POST /orders/456/cancel
```

## Security Considerations

1. **Authentication:** API keys, OAuth, JWT
2. **Authorization:** Role-based access control
3. **Rate Limiting:** Prevent abuse
4. **Input Validation:** Sanitize inputs
5. **HTTPS:** Encrypt in transit

## Documentation

Essential elements:
- **Overview:** What the API does
- **Authentication:** How to authenticate
- **Endpoints:** All available endpoints
- **Request/Response Examples:** Real examples
- **Error Codes:** All possible errors
- **Rate Limits:** Usage restrictions

**Tools:** OpenAPI/Swagger, Postman, ReadMe

## Performance Optimization

1. **Field Selection:** Allow clients to request specific fields
   ```
   GET /users?fields=id,name,email
   ```

2. **Compression:** Gzip responses
3. **Caching:** Cache headers (ETag, Last-Modified)
4. **Batching:** Batch operations when possible
5. **Pagination:** Always paginate large results

## Versioning Strategies

1. **URL Versioning:** `/api/v1/users`
2. **Header Versioning:** `Accept: application/vnd.api+json;version=1`
3. **Query Parameter:** `/api/users?version=1`

**URL versioning is most common**—simple and explicit.

## Common Mistakes

1. **Inconsistent Naming:** Mix camelCase and snake_case
2. **Poor Error Messages:** Generic "Error" without details
3. **No Versioning:** Breaking changes affect all clients
4. **Over-fetching:** Returning too much data
5. **Under-fetching:** Requiring multiple requests
6. **No Pagination:** Returning huge lists
7. **Insecure:** No authentication/authorization

## Interview Tips

When designing APIs:
1. Identify resources and operations
2. Design RESTful endpoints
3. Define request/response schemas
4. Consider versioning strategy
5. Address error handling
6. Discuss security and rate limiting
7. Consider performance (pagination, caching)

