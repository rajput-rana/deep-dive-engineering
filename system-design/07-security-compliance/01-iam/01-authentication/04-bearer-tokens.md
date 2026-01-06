# Bearer Token Authentication

**What "Bearer" means:** Whoever **bears** (has) the token is trusted.

## How It Looks

```http
GET /api/resource
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Is Bearer an Auth System?

❌ **No** - Bearer is only a **token transport mechanism**.

JWT and OAuth tokens are usually sent as Bearer tokens.

## Token Types Used with Bearer

- **JWT tokens** - Self-contained, signed
- **OAuth tokens** - Issued by authorization server
- **Opaque tokens** - Reference tokens stored on server
- **Custom tokens** - Any token format

## Why HTTPS is Mandatory

If token is stolen, attacker can impersonate you.

**Without HTTPS:**
- Token visible in network traffic
- Man-in-the-middle attacks possible
- Token theft leads to account takeover

**With HTTPS:**
- Encrypted transmission
- Token protected in transit

## Static Bearer Token

**What it is:** Pre-issued token used directly (not obtained via OAuth)

### Configuration Requirements

| Field | Why |
|-------|-----|
| Base URL | API endpoint |
| Access Token | Secret token |
| Auth Header Name | Usually `Authorization` |
| Token Prefix | `Bearer` |

### Example
```http
Authorization: Bearer static-token-abc123
```

## Best Practices

- ✅ Always use HTTPS
- ✅ Use short-lived tokens
- ✅ Implement token refresh
- ✅ Validate token on every request
- ❌ Never log tokens
- ❌ Never expose tokens in URLs

## When to Use

- ✅ Always when using tokens
- ✅ Token-based authentication
- ⚠️ Never without HTTPS

