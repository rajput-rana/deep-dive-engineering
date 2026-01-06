# OAuth vs JWT

**Common confusion:** OAuth and JWT are often compared, but they solve different problems.

## Key Distinction

| Aspect | OAuth 2.0 | JWT |
|--------|-----------|-----|
| **What it is** | Authorization framework | Token format |
| **Purpose** | Delegated access | Self-contained token |
| **Relationship** | OAuth often issues JWT tokens | JWT is a token format |

## OAuth 2.0

**What it is:** Framework for getting tokens without sharing passwords

**Focus:** Authorization - "What can you access?"

**Components:**
- Authorization server
- Resource server
- Client
- Resource owner

**Token:** Usually JWT, but can be opaque

## JWT

**What it is:** Self-contained, signed token format

**Focus:** Token structure - "How is identity encoded?"

**Components:**
- Header
- Payload (claims)
- Signature

**Use:** Authentication, authorization, information exchange

## How They Work Together

**OAuth 2.0 often issues JWT tokens:**

```
1. OAuth flow obtains token
   ↓
2. Token is JWT format
   ↓
3. JWT contains user identity + permissions
   ↓
4. Client uses JWT for API calls
```

## Comparison Table

| Feature | OAuth 2.0 | JWT |
|---------|-----------|-----|
| **Type** | Protocol/Framework | Token Format |
| **Token Format** | JWT or Opaque | JWT only |
| **Flow** | Authorization Code, Client Credentials, etc. | No flow (just format) |
| **Use Case** | Delegated access, SSO | Stateless authentication |
| **Complexity** | Higher | Lower |

## When to Use What

### Use OAuth 2.0 When:

- ✅ External API access
- ✅ Third-party integrations
- ✅ User-delegated access
- ✅ SSO implementations
- ✅ Need authorization framework

### Use JWT When:

- ✅ Stateless authentication
- ✅ Microservices
- ✅ API authentication
- ✅ Information exchange
- ✅ Need self-contained token

## Common Misconceptions

### ❌ "OAuth vs JWT - which is better?"

**Reality:** They're not alternatives. OAuth is a framework, JWT is a token format. OAuth often uses JWT.

### ❌ "JWT replaces OAuth"

**Reality:** JWT is just a token format. OAuth provides the framework for obtaining and using tokens.

### ✅ Correct Understanding

**OAuth 2.0** = How to get tokens
**JWT** = Format of the token

## Real-World Example

**OAuth 2.0 Authorization Code Flow with JWT:**

```
1. User authorizes app (OAuth flow)
   ↓
2. Authorization server issues JWT token (JWT format)
   ↓
3. App uses JWT for API calls (JWT usage)
```

## Interview Answer

**Q: What's the difference between OAuth and JWT?**

**Answer:** "OAuth 2.0 is an authorization framework that defines how to obtain tokens, while JWT is a token format. OAuth often issues JWT tokens. OAuth solves the 'how to get access' problem, while JWT solves the 'how to encode identity' problem. They work together - OAuth provides the flow, JWT provides the token structure."

## Related Topics

- **[OAuth 2.0](./06-oauth2.md)** - Authorization framework
- **[JWT](./05-jwt.md)** - Token format
- **[OpenID Connect](./09-openid-connect.md)** - Identity layer on OAuth

