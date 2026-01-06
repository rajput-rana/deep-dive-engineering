# JWT (JSON Web Token) ⭐ MOST IMPORTANT

**What it is:** A self-contained, signed token that contains identity + permissions.

## JWT Structure

A JWT has **3 parts** separated by dots:

```
xxxxx.yyyyy.zzzzz
```

### 1️⃣ Header
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```
- Algorithm used for signing
- Token type

### 2️⃣ Payload (Claims)
```json
{
  "sub": "user123",
  "role": "admin",
  "exp": 1710000000,
  "iat": 1709913600
}
```
- **sub** (subject) - User ID
- **role** - User role
- **exp** - Expiration time
- **iat** - Issued at time

### 3️⃣ Signature
- Used to verify token wasn't modified
- Signed with secret key or private key

## How JWT Authentication Works

```
1. User logs in
   ↓
2. Auth service issues JWT
   ↓
3. Client sends JWT with requests
   ↓
4. API verifies signature
   ↓
5. API reads claims (role, userId)
```

## Does API Call DB Every Time?

❌ **No** - JWT is **stateless**

- No session storage needed
- Token contains all necessary information
- Signature verification is enough

## Why JWT is Popular

- ✅ **Stateless** - No session storage
- ✅ **Fast** - No DB lookup
- ✅ **Scalable** - Works great for microservices
- ✅ **Portable** - Token works across services

## JWT Downsides

- ❌ **Hard to revoke** before expiry
- ❌ **Token size** is larger than opaque tokens
- ❌ **Must manage expiry** carefully
- ❌ **Claims can't change** until token expires

## Configuration Requirements

| Field | Why |
|-------|-----|
| Base URL | API endpoint |
| JWT Token | Signed identity token |
| Signing Algorithm | HS256 / RS256 |
| Public Key / Secret | For verification |
| Token Expiry | Security |
| Issuer (iss) | Trust check |
| Audience (aud) | Target validation |

**Note:** JWT is usually obtained via OAuth, not manually configured.

## Request Example

```http
GET /api/orders
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

## JWT vs Sessions

| Aspect | JWT | Sessions |
|--------|-----|----------|
| Storage | Client-side | Server-side |
| Scalability | ✅ Horizontal scaling easy | ❌ Needs shared storage |
| Performance | ✅ No DB lookup | ❌ DB lookup per request |
| Revocation | ❌ Hard | ✅ Easy |
| Token Size | ❌ Larger | ✅ Smaller |

## Best Practices

- ✅ Use short expiration times
- ✅ Implement refresh tokens
- ✅ Use RS256 for public APIs
- ✅ Validate signature and claims
- ✅ Check expiration (exp claim)
- ✅ Verify issuer (iss) and audience (aud)
- ❌ Don't store sensitive data in JWT
- ❌ Don't use JWT for session management if revocation needed

## When to Use

- ✅ Microservices
- ✅ Internal APIs
- ✅ Modern backends
- ✅ Stateless architectures
- ❌ When frequent revocation needed
- ❌ When token size matters (mobile)

## Common Interview Questions

**Q: Why JWT over sessions?**
- Stateless → horizontal scaling
- No shared session storage needed
- Works across microservices

**Q: How to revoke JWT?**
- Use short expiration + refresh tokens
- Maintain token blacklist (defeats statelessness)
- Use reference tokens instead

**Q: JWT vs OAuth?**
- JWT = token format
- OAuth = token issuing framework
- OAuth often issues JWT tokens

## Related Topics

- **[OAuth 2.0](./06-oauth2.md)** - Often issues JWT tokens
- **[Bearer Tokens](./04-bearer-tokens.md)** - Transport mechanism for JWT
- **[Authorization](../02-authorization/)** - Using JWT claims for authorization
