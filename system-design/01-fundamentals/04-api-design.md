# 🔌 API Design

<div align="center">

**Design intuitive, consistent, and scalable APIs**

[![API Design](https://img.shields.io/badge/API-Design-blue?style=for-the-badge)](./)
[![HTTP](https://img.shields.io/badge/HTTP-Foundations-green?style=for-the-badge)](./)
[![REST](https://img.shields.io/badge/REST-Architecture-orange?style=for-the-badge)](./)

*Master API design principles, HTTP foundations, and best practices*

</div>

---

## 🎯 What is an API?

<div align="center">

**API (Application Programming Interface) is a contract that allows two systems to communicate.**

### API Analogy

| Component | Description |
|:---:|:---:|
| **Menu** | What you can request |
| **Protocol** | How you request it |
| **Response Format** | What you get back |

### Communication Patterns

| Pattern | Description | Example |
|:---:|:---:|:---:|
| **Frontend → Backend** | Web app to server | React app → Node.js API |
| **Service → Service** | Microservices communication | Order service → Payment service |
| **Mobile app → Cloud** | Mobile to backend | iOS app → AWS API |
| **Internal → External** | Partner integrations | Your system → Stripe API |

**Mental Model:** Think of an API as a waiter in a restaurant - you tell them what you want (request), they communicate with the kitchen (server), and bring back your order (response).

</div>

---

## 🎯 Why APIs Exist

<div align="center">

### Without APIs

| Problem | Impact |
|:---:|:---:|
| **Tight Coupling** | Systems directly dependent on each other |
| **Direct DB Access** | Security vulnerabilities |
| **Hard to Scale** | Monolithic dependencies |
| **Security Nightmares** | Exposed internal structures |

### With APIs

| Benefit | Impact |
|:---:|:---:|
| **Loose Coupling** | Independent system evolution |
| **Versioning** | Backward compatibility |
| **Security Boundaries** | Controlled access |
| **Independent Evolution** | Teams work independently |

</div>

---

## 📊 Types of APIs

<div align="center">

### API Categories

| Type | Description | Use Case |
|:---:|:---:|:---:|
| **Internal** | Used within organization | Microservices, internal tools |
| **Public** | Open to external users | Public APIs, developer platforms |
| **Partner** | Restricted access | B2B integrations, partner APIs |
| **Composite** | Combine multiple APIs | API gateways, aggregators |
| **Streaming** | Event-based | Kafka, WebSockets, real-time |

</div>

---

## 🌐 HTTP & Web Foundations

<div align="center">

### HTTP Basics (Non-Negotiable)

**HTTP is:**

- **Stateless** - Each request is independent
- **Request/Response based** - Client requests, server responds
- **Text-based** - Human-readable protocol

### HTTP Request Structure

```
METHOD /path HTTP/1.1
Headers
Body
```

**Example:**
```
GET /users/123 HTTP/1.1
Host: api.example.com
Authorization: Bearer token123
Accept: application/json
```

---

### HTTP Methods (Semantics Matter)

| Method | Meaning | Idempotent | Safe |
|:---:|:---:|:---:|:---:|
| **GET** | Read | ✅ Yes | ✅ Yes |
| **POST** | Create | ❌ No | ❌ No |
| **PUT** | Replace | ✅ Yes | ❌ No |
| **PATCH** | Partial update | ⚠️ Usually | ❌ No |
| **DELETE** | Remove | ✅ Yes | ❌ No |
| **HEAD** | Metadata | ✅ Yes | ✅ Yes |
| **OPTIONS** | Capability discovery | ✅ Yes | ✅ Yes |

**⚠️ Expert Rule:** Method semantics ≠ just convention → affects caching, proxies, security.

---

### HTTP Status Codes (Critical)

| Code | Meaning | Use Case |
|:---:|:---:|:---:|
| **200** | OK | Successful GET, PUT, PATCH |
| **201** | Created | Successful POST |
| **204** | No Content | Successful DELETE |
| **400** | Bad Request | Invalid request format |
| **401** | Unauthorized | Missing/invalid auth |
| **403** | Forbidden | Auth OK, no permission |
| **404** | Not Found | Resource doesn't exist |
| **409** | Conflict | Resource conflict |
| **422** | Validation error | Invalid data |
| **429** | Rate limited | Too many requests |
| **500** | Server error | Internal server error |
| **503** | Service unavailable | Service down |

**💡 Experts design APIs around correct status codes.**

---

### Headers (Often Ignored, Extremely Powerful)

| Header | Purpose | Example |
|:---:|:---:|:---:|
| **Authorization** | Authentication | `Bearer token123` |
| **Content-Type** | Request format | `application/json` |
| **Accept** | Response format | `application/json` |
| **Cache-Control** | Caching directives | `max-age=3600` |
| **ETag** | Cache validation | `"abc123"` |
| **X-Request-ID** | Request tracing | `uuid` |

**Headers Enable:**

- ✅ Security (authentication, authorization)
- ✅ Caching (performance optimization)
- ✅ Tracing (debugging, monitoring)
- ✅ Versioning (API evolution)

</div>

---

## 🎨 Design Principles

<div align="center">

### Core Principles

| Principle | Description | Example |
|:---:|:---:|:---:|
| **Consistency** | Uniform naming, error format | camelCase or snake_case consistently |
| **Versioning** | Allow evolution without breaking | `/api/v1/users` → `/api/v2/users` |
| **Pagination** | Limit response size | `?page=1&limit=20` |
| **Error Handling** | Consistent error format | Structured error responses |
| **Documentation** | Clear, comprehensive docs | OpenAPI/Swagger |

---

### 1. Consistency

**Naming Conventions:**

- Use consistent naming (camelCase or snake_case)
- Consistent error format across all endpoints
- Consistent pagination approach

**Example:**
```json
// Consistent error format
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User with ID 123 does not exist",
    "details": {}
  }
}
```

---

### 2. Versioning

**Strategies:**

| Strategy | Pros | Cons | Example |
|:---:|:---:|:---:|:---:|
| **URL** | Simple, explicit | Ugly URLs | `/api/v1/users` |
| **Header** | Clean URLs | Harder to discover | `Accept: application/vnd.api+json;version=1` |
| **Query Param** | Easy | Not REST-pure | `/api/users?version=1` |

**Best Practice:** Header or URL versioning.

---

### 3. Pagination

**Approaches:**

| Type | Description | Example |
|:---:|:---:|:---:|
| **Offset-based** | Page number + limit | `?page=1&limit=20` |
| **Cursor-based** | Token-based | `?cursor=abc123&limit=20` |

**💡 Best Practice:** Cursor-based pagination for large datasets (stable sorting).

---

### 4. Filtering & Sorting

**Query Parameters:**

```
GET /users?status=active&sort=created_at&order=desc
GET /users?age_min=18&age_max=65
```

**Rules:**

- Use query parameters, not path
- Support multiple filters
- Ensure stable sorting

---

### 5. Error Handling

**Structured Error Response:**

```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User with ID 123 does not exist",
    "details": {
      "field": "id",
      "value": "123"
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

**Best Practices:**

- Consistent error format
- Meaningful error codes
- Include context
- Appropriate HTTP status codes

</div>

---

## 🎯 Why API Design Matters

<div align="center">

### Key Benefits

| Benefit | Description | Impact |
|:---:|:---:|:---:|
| **Developer Experience** | Easy to understand and use | Faster integration |
| **Maintainability** | Easier to evolve | Fewer breaking changes |
| **Performance** | Efficient design | Reduced requests, data transfer |
| **Adoption** | Intuitive APIs | Faster adoption |

</div>

---

## 🌍 Real-World Examples

<div align="center">

### Industry Standards

| API | Why It's Great | Key Features |
|:---:|:---:|:---:|
| **Stripe API** | Clean, consistent, well-documented | Industry standard |
| **GitHub API** | RESTful, versioned | Comprehensive documentation |
| **Twitter API** | Evolved through versions | Learned from mistakes |
| **AWS APIs** | Consistent across services | Though complex |

</div>

---

## 🔐 Security Considerations

<div align="center">

### Security Layers

| Layer | Description | Implementation |
|:---:|:---:|:---:|
| **Authentication** | Who are you? | API keys, OAuth, JWT |
| **Authorization** | What can you do? | RBAC, ABAC, policies |
| **Rate Limiting** | Prevent abuse | Quotas, throttling |
| **Input Validation** | Sanitize inputs | Schema validation |
| **HTTPS** | Encrypt in transit | TLS/SSL |

### Threat Model

**APIs are attacked via:**

- Credential theft
- Broken auth
- Injection attacks
- Excessive data exposure
- DoS attacks
- Abuse

**💡 Design against these upfront.**

</div>

---

## 📚 Documentation

<div align="center">

### Essential Elements

| Element | Description |
|:---:|:---:|
| **Overview** | What the API does |
| **Authentication** | How to authenticate |
| **Endpoints** | All available endpoints |
| **Request/Response Examples** | Real examples |
| **Error Codes** | All possible errors |
| **Rate Limits** | Usage restrictions |

**Tools:** OpenAPI/Swagger, Postman, ReadMe

</div>

---

## ⚡ Performance Optimization

<div align="center">

### Optimization Strategies

| Strategy | Description | Example |
|:---:|:---:|:---:|
| **Field Selection** | Request specific fields | `?fields=id,name,email` |
| **Compression** | Gzip responses | `Content-Encoding: gzip` |
| **Caching** | Cache headers | `ETag`, `Last-Modified` |
| **Batching** | Batch operations | Multiple operations in one request |
| **Pagination** | Limit response size | Always paginate large results |

</div>

---

## ⚖️ API Patterns Comparison

<div align="center">

### REST vs GraphQL vs gRPC

| Aspect | REST | GraphQL | gRPC |
|:---:|:---:|:---:|:---:|
| **Endpoints** | Many | One | Many |
| **Over-fetching** | Yes | No | No |
| **Caching** | Easy | Hard | Limited |
| **Complexity** | Simple | Complex | Medium |
| **Performance** | Good | Good | Excellent |
| **Type Safety** | No | Yes | Yes |

**💡 Choose based on use case, not ideology.**

</div>

---

## 🚫 Common Mistakes

<div align="center">

### Anti-Patterns

| Mistake | Problem | Solution |
|:---:|:---:|:---:|
| **Inconsistent Naming** | Mix camelCase and snake_case | Choose one, stick to it |
| **Poor Error Messages** | Generic "Error" | Detailed, actionable errors |
| **No Versioning** | Breaking changes | Version from start |
| **Over-fetching** | Too much data | Field selection |
| **Under-fetching** | Multiple requests | Batch operations |
| **No Pagination** | Huge lists | Always paginate |
| **Insecure** | No auth/authz | Security first |

</div>

---

## 🎓 Interview Tips

<div align="center">

### Key Points to Cover

When designing APIs:

1. **Identify Resources** - What are the main entities?
2. **Design RESTful Endpoints** - Use HTTP methods correctly
3. **Define Schemas** - Request/response structures
4. **Consider Versioning** - Plan for evolution
5. **Address Errors** - Consistent error handling
6. **Discuss Security** - Auth, authz, rate limiting
7. **Consider Performance** - Pagination, caching, compression

</div>

---

## 🔗 Related Topics

<div align="center">

| Topic | Description | Link |
|:---:|:---:|:---:|
| **[REST APIs](./05-rest-apis.md)** | RESTful API design | [Explore →](./05-rest-apis.md) |
| **[GraphQL](./06-graphql.md)** | GraphQL API design | [Explore →](./06-graphql.md) |

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **API Purpose** | Contract for system communication |
| **HTTP Foundation** | Master HTTP methods, status codes, headers |
| **Design Principles** | Consistency, versioning, error handling |
| **Security** | Authentication, authorization, rate limiting |
| **Performance** | Caching, pagination, compression |

**💡 Remember:** Good API design is about developer experience, maintainability, and scalability.

</div>

---

<div align="center">

**Master API design for scalable, maintainable systems! 🚀**

*Well-designed APIs enable seamless integration, independent evolution, and better developer experience.*

</div>
