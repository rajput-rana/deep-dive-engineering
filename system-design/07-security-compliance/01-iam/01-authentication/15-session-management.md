# Session Management

**What it is:** Managing user sessions after authentication.

**Purpose:** Maintain user state across requests without re-authenticating.

## Session Types

### Server-Side Sessions

**How it works:**
- Session stored on server
- Client receives session ID (cookie)
- Server looks up session on each request

**Pros:**
- ✅ Server controls session lifecycle
- ✅ Easy revocation
- ✅ Can store sensitive data server-side

**Cons:**
- ❌ Requires shared storage (Redis, DB)
- ❌ DB lookup per request
- ❌ Scaling challenges

### Client-Side Sessions (JWT)

**How it works:**
- Session data in token (JWT)
- Client stores token
- Server validates token (no DB lookup)

**Pros:**
- ✅ Stateless
- ✅ Scalable
- ✅ No shared storage needed

**Cons:**
- ❌ Hard to revoke
- ❌ Token size limits
- ❌ Can't change session data until expiry

## Session Security

### Secure Cookies

**Attributes:**
- `HttpOnly` - Not accessible via JavaScript (prevents XSS)
- `Secure` - HTTPS only
- `SameSite` - CSRF protection
- `Domain` - Cookie scope

**Example:**
```
Set-Cookie: sessionId=abc123; HttpOnly; Secure; SameSite=Strict
```

### Session ID Security

- ✅ Use cryptographically secure random generators
- ✅ Long enough (128+ bits)
- ✅ Regenerate on login
- ✅ Regenerate on privilege escalation

## Session Lifecycle

```
1. User authenticates
   ↓
2. Server creates session
   ↓
3. Session ID sent to client (cookie)
   ↓
4. Client sends session ID with requests
   ↓
5. Server validates session
   ↓
6. Session expires or user logs out
```

## Session Expiration

### Time-Based Expiration

- **Absolute timeout** - Session expires after X minutes
- **Idle timeout** - Session expires after inactivity
- **Sliding expiration** - Extends on activity

### Best Practices

- ✅ Short session timeouts (15-30 minutes)
- ✅ Idle timeout (5-15 minutes)
- ✅ Clear session on logout
- ✅ Monitor session usage

## Session Storage

### In-Memory (Not Recommended)

- ❌ Lost on server restart
- ❌ Doesn't scale across servers

### Database

- ✅ Persistent
- ✅ Can query sessions
- ❌ Performance overhead

### Redis (Recommended)

- ✅ Fast
- ✅ Scalable
- ✅ TTL support
- ✅ Distributed

## Common Vulnerabilities

### Session Fixation

**Attack:** Attacker forces victim to use known session ID

**Prevention:**
- Regenerate session ID on login
- Don't accept session IDs from URL

### Session Hijacking

**Attack:** Attacker steals session ID

**Prevention:**
- HTTPS only
- Secure cookies
- IP validation (optional)
- User agent validation (optional)

### Session Replay

**Attack:** Reusing old session

**Prevention:**
- Short expiration
- Timestamp validation
- Nonce/token rotation

## Best Practices

- ✅ Use secure cookies
- ✅ Implement session timeout
- ✅ Regenerate session IDs on login
- ✅ Store sessions in Redis
- ✅ Log session events
- ✅ Monitor for anomalies
- ❌ Don't store sensitive data in cookies
- ❌ Don't use predictable session IDs

## Related Topics

- **[JWT](./05-jwt.md)** - Stateless session alternative
- **[Authentication](./README.md)** - User authentication
- **[OAuth 2.0](./06-oauth2.md)** - Token-based sessions

