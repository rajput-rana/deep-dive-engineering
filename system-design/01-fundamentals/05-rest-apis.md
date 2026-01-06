# 🌐 REST APIs

<div align="center">

**Representational State Transfer - Resource-oriented API architecture**

[![REST](https://img.shields.io/badge/REST-Architecture-blue?style=for-the-badge)](./)
[![HTTP](https://img.shields.io/badge/HTTP-Methods-green?style=for-the-badge)](./)
[![Resource](https://img.shields.io/badge/Resource--Oriented-Design-orange?style=for-the-badge)](./)

*Master RESTful API design, HTTP semantics, and resource-oriented architecture*

</div>

---

## 🎯 What is REST?

<div align="center">

**REST = Representational State Transfer**

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **Architectural Style** | Not a protocol or standard |
| **Resource-Oriented** | Focus on resources, not actions |
| **Stateless** | Each request is independent |
| **Cacheable** | Responses can be cached |
| **Uniform Interface** | Consistent HTTP methods |

**💡 Important:** REST is an architectural design style for APIs, while HTTP is the communication protocol. REST defines how APIs should behave, HTTP defines communication rules.

</div>

---

## 🏗️ REST Constraints

<div align="center">

### Core Constraints

| Constraint | Description | Impact |
|:---:|:---:|:---:|
| **Client-Server Separation** | Clear separation of concerns | Independent evolution |
| **Statelessness** | No server-side session state | Scalability |
| **Cacheable Responses** | Responses marked as cacheable | Performance |
| **Uniform Interface** | Consistent HTTP methods | Simplicity |
| **Layered System** | Multiple layers allowed | Flexibility |
| **Code on Demand** | Optional - executable code | Advanced feature |

**⚠️ If you violate these → not RESTful.**

</div>

---

## 📊 Resources (Core REST Concept)

<div align="center">

### Resource-Oriented Design

**REST is resource-oriented, not action-oriented.**

| ❌ Bad (Action-Oriented) | ✅ Good (Resource-Oriented) |
|:---:|:---:|
| `POST /createUser` | `POST /users` |
| `POST /getUserDetails` | `GET /users/{id}` |
| `POST /deleteUser` | `DELETE /users/{id}` |

### Resource Naming Rules

| Rule | Description | Example |
|:---:|:---:|:---:|
| **Use Nouns** | Resources are things, not actions | `/users`, `/orders` |
| **Use Plural** | Collections are plural | `/users` not `/user` |
| **Use Hierarchy** | Nested resources | `/users/{id}/orders/{orderId}` |

**Example:**
```
GET    /users              # List users
POST   /users              # Create user
GET    /users/123          # Get user
PUT    /users/123          # Update user
DELETE /users/123          # Delete user

GET    /users/123/orders   # User's orders
POST   /users/123/orders   # Create order for user
```

</div>

---

## 🔄 HTTP Methods & CRUD Operations

<div align="center">

### Method Mapping

| HTTP Method | CRUD Operation | Description | Idempotent | Safe |
|:---:|:---:|:---:|:---:|:---:|
| **GET** | Read | Retrieve resource | ✅ Yes | ✅ Yes |
| **POST** | Create | Create new resource | ❌ No | ❌ No |
| **PUT** | Update/Replace | Replace entire resource | ✅ Yes | ❌ No |
| **PATCH** | Partial Update | Update specific fields | ⚠️ Usually | ❌ No |
| **DELETE** | Delete | Remove resource | ✅ Yes | ❌ No |

---

### 1. GET Method

**Purpose:** Read (retrieve) a representation of a resource

**Example:**
```
GET /users/123
```

**Response:**
- Success: `200 OK` with resource data
- Error: `404 NOT FOUND` or `400 BAD REQUEST`

---

### 2. POST Method

**Purpose:** Create new resources

**Example:**
```
POST /users
{
  "name": "Anjali",
  "email": "gfg@example.com"
}
```

**Response:**
- Success: `201 Created` with Location header
- Error: `400 BAD REQUEST` or `409 CONFLICT`

**⚠️ Note:** POST is neither safe nor idempotent.

---

### 3. PUT Method

**Purpose:** Update or create resource (replace entire resource)

**Example:**
```
PUT /users/123
{
  "name": "Anjali",
  "email": "gfg@example.com"
}
```

**Characteristics:**
- Replaces entire resource
- Must send full data
- Idempotent
- Creates if doesn't exist

---

### 4. PATCH Method

**Purpose:** Partially update a resource

**Example:**
```
PATCH /users/123
{
  "email": "new.email@example.com"
}
```

**Characteristics:**
- Updates only specified fields
- Only sends changes
- Not always idempotent

---

### PUT vs PATCH

| Aspect | PUT | PATCH |
|:---:|:---:|:---:|
| **Scope** | Entire resource | Specific fields |
| **Data Required** | Full resource | Only changes |
| **Idempotent** | Yes | Usually |
| **Use Case** | Replace entire profile | Update email only |

---

### 5. DELETE Method

**Purpose:** Delete a resource

**Example:**
```
DELETE /users/123
```

**Response:**
- Success: `200 OK` or `204 No Content`
- Error: `404 NOT FOUND`

</div>

---

## 🔄 Idempotency (Expert Topic)

<div align="center">

### What is Idempotency?

**Idempotent = Multiple calls → Same result**

| Method | Idempotent | Why |
|:---:|:---:|:---:|
| **GET** | ✅ Yes | Reading doesn't change state |
| **PUT** | ✅ Yes | Replacing with same data = same result |
| **DELETE** | ✅ Yes | Deleting twice = same result |
| **POST** | ❌ No | Creates new resource each time |

### Why It Matters

| Scenario | Impact |
|:---:|:---:|
| **Retries** | Safe to retry idempotent operations |
| **Network Failures** | Can retry without side effects |
| **Distributed Systems** | Prevents duplicate operations |

### Idempotency Keys

**For Non-Idempotent Operations:**

```
POST /orders
Idempotency-Key: uuid-12345
{
  "product_id": 456,
  "quantity": 2
}
```

**💡 Used heavily in payments APIs.**

</div>

---

## 📄 Pagination, Filtering, Sorting

<div align="center">

### Pagination

**Offset-Based:**
```
GET /users?page=2&limit=20
```

**Cursor-Based (Preferred for Large Datasets):**
```
GET /users?cursor=abc123&limit=20
```

**Benefits of Cursor-Based:**
- ✅ Stable sorting
- ✅ Better performance
- ✅ No skipped/duplicate results

---

### Filtering

**Query Parameters:**
```
GET /users?status=active
GET /users?age_min=18&age_max=65
GET /users?department=Engineering&role=Developer
```

---

### Sorting

**Sort Parameter:**
```
GET /users?sort=createdAt:desc
GET /users?sort=name:asc,createdAt:desc
```

**💡 Experts ensure stable sorting and cursor-based pagination for large datasets.**

</div>

---

## 🔄 Versioning Strategies

<div align="center">

### Versioning Approaches

| Strategy | Pros | Cons | Example |
|:---:|:---:|:---:|:---:|
| **URL** | Simple, explicit | Ugly URLs | `/api/v1/users` |
| **Header** | Clean URLs | Harder to discover | `Accept: application/vnd.api+json;version=1` |
| **Query Param** | Easy | Not REST-pure | `/api/users?version=1` |

**Best Practice:** Header or URL versioning.

**Example:**
```
GET /api/v1/users
Accept: application/vnd.api+json;version=1
```

</div>

---

## 🏗️ REST API Features

<div align="center">

### Core Features

| Feature | Description | Benefit |
|:---:|:---:|:---:|
| **Stateless** | Each request contains all info | Scalability |
| **Client-Server** | Clear separation | Independent evolution |
| **Cacheable** | Responses marked cacheable | Performance |
| **Uniform Interface** | Consistent HTTP methods | Simplicity |
| **Layered System** | Multiple layers allowed | Flexibility |

</div>

---

## 💻 Building a REST API

<div align="center">

### Node.js & Express Example

**Step 1: Setup**
```javascript
const express = require('express');
const app = express();
const port = 3000;

app.use(express.json());
```

**Step 2: Define Routes**
```javascript
// GET - List users
app.get('/users', (req, res) => {
    res.json({ message: 'Returning list of users' });
});

// POST - Create user
app.post('/users', (req, res) => {
    const newUser = req.body;
    res.status(201).json({ message: 'User created', user: newUser });
});

// GET - Get user by ID
app.get('/users/:id', (req, res) => {
    const userId = req.params.id;
    res.json({ message: `Returning user ${userId}` });
});

// PUT - Update user
app.put('/users/:id', (req, res) => {
    const userId = req.params.id;
    const updatedUser = req.body;
    res.json({ message: `User ${userId} updated`, updatedUser });
});

// DELETE - Delete user
app.delete('/users/:id', (req, res) => {
    const userId = req.params.id;
    res.status(204).send();
});
```

**Step 3: Start Server**
```javascript
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
```

</div>

---

## 🌍 Real-World Examples

<div align="center">

### REST API Applications

| Industry | Use Case | Example |
|:---:|:---:|:---:|
| **Social Media** | Third-party integrations | Facebook, Twitter, Instagram APIs |
| **E-Commerce** | Product management, payments | Stripe, Shopify APIs |
| **Geolocation** | GPS tracking, location services | Google Maps API |
| **Weather** | Weather data | OpenWeatherMap API |

</div>

---

## ⚖️ REST vs GraphQL

<div align="center">

### Comparison

| Aspect | REST | GraphQL |
|:---:|:---:|:---:|
| **Endpoints** | Many | One |
| **Over-fetching** | Yes | No |
| **Under-fetching** | Yes | No |
| **Caching** | Easy | Hard |
| **Complexity** | Simple | Complex |
| **Monitoring** | Easy | Hard |
| **Security** | Easier | Risky if misused |

**💡 Experts choose per use case, not ideology.**

### When to Use REST

- ✅ Simple data requirements
- ✅ Well-established data models
- ✅ Need easy caching
- ✅ Public APIs
- ✅ Simple CRUD operations

</div>

---

## 🔐 Security Best Practices

<div align="center">

### Security Layers

| Layer | Description | Implementation |
|:---:|:---:|:---:|
| **Authentication** | Who are you? | API keys, OAuth, JWT |
| **Authorization** | What can you do? | RBAC, ABAC |
| **Rate Limiting** | Prevent abuse | Quotas, throttling |
| **Input Validation** | Sanitize inputs | Schema validation |
| **HTTPS** | Encrypt in transit | TLS/SSL |

</div>

---

## 📊 API Patterns

<div align="center">

### Common Patterns

**1. Collection Pattern:**
```
GET    /users              # List
POST   /users              # Create
GET    /users/123          # Get one
PUT    /users/123          # Update
DELETE /users/123          # Delete
```

**2. Nested Resources:**
```
GET  /users/123/posts      # User's posts
POST /users/123/posts      # Create post for user
```

**3. Actions (When Needed):**
```
POST /users/123/activate
POST /orders/456/cancel
```

**💡 Use actions sparingly - prefer resource updates.**

</div>

---

## 🎓 Interview Tips

<div align="center">

### Key Points to Cover

When discussing REST APIs:

1. **Explain REST Constraints** - Client-server, stateless, cacheable, uniform interface
2. **Resource Design** - Use nouns, plural, hierarchy
3. **HTTP Methods** - Correct semantics, idempotency
4. **Versioning** - Strategy and implementation
5. **Error Handling** - Consistent format, status codes
6. **Security** - Authentication, authorization, rate limiting

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **REST Definition** | Architectural style, not protocol |
| **Resource-Oriented** | Focus on resources, not actions |
| **HTTP Semantics** | Methods have meaning beyond convention |
| **Idempotency** | Critical for retries and distributed systems |
| **Versioning** | Plan for evolution from start |

**💡 Remember:** REST is about resource-oriented design with proper HTTP semantics.

</div>

---

<div align="center">

**Master REST APIs for scalable, maintainable web services! 🚀**

*RESTful APIs provide a simple, standard way to build web services that scale.*

</div>

