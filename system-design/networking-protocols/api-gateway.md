# API Gateway

## Summary

An API Gateway is a single entry point that acts as a reverse proxy to accept all API calls, aggregate the services required to fulfill them, and return the appropriate result. It handles cross-cutting concerns like authentication, rate limiting, routing, and monitoring, simplifying client interactions with microservices.

## Key Concepts

### The Problem: Direct Client-Microservice Communication

**Without API Gateway:**
```
┌─────────┐
│ Client  │
└────┬────┘
     │
     ├──► POST /users (User Service)
     ├──► GET /orders (Order Service)
     ├──► POST /payments (Payment Service)
     └──► GET /products (Product Service)

Issues:
- Client needs to know all service endpoints
- Each service handles auth, rate limiting separately
- Complex client code
- No centralized monitoring
```

**With API Gateway:**
```
┌─────────┐
│ Client  │
└────┬────┘
     │
     │ Single entry point
     ▼
┌──────────────┐
│ API Gateway  │
└──────┬───────┘
       │
   ┌───┴───┬────┬────────┐
   │       │    │        │
   ▼       ▼    ▼        ▼
┌────┐ ┌────┐ ┌────┐  ┌────┐
│User│ │Ord │ │Pay │  │Prod│
│Svc │ │Svc │ │Svc │  │Svc │
└────┘ └────┘ └────┘  └────┘

Benefits:
- Single endpoint for client
- Centralized auth, rate limiting
- Simplified client code
- Unified monitoring
```

## Why API Gateway Matters

**Simplified Client:** Clients interact with one endpoint instead of multiple services.

**Cross-Cutting Concerns:** Centralized handling of authentication, rate limiting, logging.

**Service Abstraction:** Hides internal service structure from clients.

**Load Balancing:** Distributes requests across service instances.

**Protocol Translation:** Converts between different protocols (HTTP, gRPC, WebSocket).

## Core Functions

### 1. Request Routing

Routes requests to appropriate backend services based on URL path, headers, or other criteria.

**Example:**
```
GET /api/users/123
  → Routes to User Service

POST /api/orders
  → Routes to Order Service
```

**Diagram:**
```
Request: GET /api/users/123
         │
         ▼
┌──────────────┐
│ API Gateway  │
│   Router     │
└──────┬───────┘
       │
       │ Match: /api/users/*
       ▼
┌──────────────┐
│ User Service │
└──────────────┘
```

### 2. Authentication & Authorization

Validates API keys, JWT tokens, OAuth tokens before forwarding requests.

**Flow:**
```
Request with JWT Token
         │
         ▼
┌──────────────┐
│ API Gateway  │
│   Auth       │
└──────┬───────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
Valid   Invalid
  │       │
  │       └──► 401 Unauthorized
  │
  ▼
Forward to Service
```

### 3. Rate Limiting

Controls request rate per client, API key, or IP address.

**Example:**
```
Client A: 100 requests/minute
Client B: 50 requests/minute

Exceeds limit → 429 Too Many Requests
```

### 4. Request/Response Transformation

Modifies requests/responses:
- Add/remove headers
- Transform data formats
- Aggregate multiple service responses

**Example:**
```
Client Request:
GET /api/user-profile/123

API Gateway:
1. Calls User Service → GET /users/123
2. Calls Order Service → GET /orders?user_id=123
3. Aggregates responses
4. Returns combined result
```

### 5. Load Balancing

Distributes requests across multiple instances of a service.

**Diagram:**
```
Request → API Gateway
            │
            ▼
      Load Balancer
            │
    ┌───────┼───────┐
    │       │       │
    ▼       ▼       ▼
┌────┐  ┌────┐  ┌────┐
│Svc1│  │Svc2│  │Svc3│
└────┘  └────┘  └────┘
```

### 6. Monitoring & Logging

Tracks API usage, performance metrics, errors.

**Metrics:**
- Request rate
- Response times
- Error rates
- Latency percentiles

## Architecture Patterns

### Simple API Gateway

```
┌─────────┐
│ Client  │
└────┬────┘
     │
     ▼
┌──────────────┐
│ API Gateway  │
└──────┬───────┘
       │
   ┌───┴───┬────┬────────┐
   │       │    │        │
   ▼       ▼    ▼        ▼
┌────┐ ┌────┐ ┌────┐  ┌────┐
│Svc1│ │Svc2│ │Svc3│  │Svc4│
└────┘ └────┘ └────┘  └────┘
```

### API Gateway with Service Mesh

```
┌─────────┐
│ Client  │
└────┬────┘
     │
     ▼
┌──────────────┐
│ API Gateway  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Service Mesh │
│  (Istio)     │
└──────┬───────┘
       │
   ┌───┴───┬────┬────────┐
   │       │    │        │
   ▼       ▼    ▼        ▼
┌────┐ ┌────┐ ┌────┐  ┌────┐
│Svc1│ │Svc2│ │Svc3│  │Svc4│
└────┘ └────┘ └────┘  └────┘
```

## Real-World Examples

### AWS API Gateway
- Fully managed API gateway service
- Integrates with Lambda, EC2, other AWS services
- Handles authentication, rate limiting, caching

### Kong
- Open-source API gateway
- Plugin architecture
- Supports authentication, rate limiting, logging

### NGINX
- Can function as API gateway
- Reverse proxy with routing capabilities
- High performance

### Netflix Zuul
- API gateway for microservices
- Request routing, filtering, monitoring
- Used in Netflix's microservices architecture

## Tradeoffs

### Advantages
- ✅ Simplified client code
- ✅ Centralized cross-cutting concerns
- ✅ Service abstraction
- ✅ Unified monitoring
- ✅ Protocol translation

### Disadvantages
- ❌ Single point of failure (needs redundancy)
- ❌ Additional network hop (latency)
- ❌ Potential bottleneck
- ❌ Additional complexity

## Design Considerations

### When to Use API Gateway

**Good for:**
- Microservices architecture
- Multiple clients (web, mobile, third-party)
- Need for centralized auth/rate limiting
- Service abstraction required

**Not ideal for:**
- Simple monolithic applications
- Direct service-to-service communication
- Very low latency requirements

### High Availability

**Avoid SPOF:**
- Multiple API Gateway instances
- Load balancer in front
- Health checks and auto-scaling

**Diagram:**
```
┌─────────┐
│ Clients │
└────┬────┘
     │
     ▼
┌──────────────┐
│Load Balancer │
└──────┬───────┘
       │
   ┌───┴───┬────┬────┐
   │       │    │    │
   ▼       ▼    ▼    ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐
│GW1 │ │GW2 │ │GW3 │ │GW4 │
└────┘ └────┘ └────┘ └────┘
```

### Caching

**API Gateway can cache responses:**
- Reduce backend load
- Improve response times
- Cache invalidation strategies

**Example:**
```
GET /api/products
  → Check cache
  → If hit: Return cached response
  → If miss: Call service, cache response
```

## Interview Hints

When discussing API Gateway:
1. Explain the problem it solves (microservices complexity)
2. Describe core functions (routing, auth, rate limiting)
3. Discuss architecture patterns
4. Address high availability (avoid SPOF)
5. Compare with alternatives (direct communication, service mesh)
6. Give real-world examples

## Conclusion

API Gateway is a critical component in microservices architecture, providing a single entry point that simplifies client interactions, centralizes cross-cutting concerns, and enables better monitoring and management of distributed systems.

