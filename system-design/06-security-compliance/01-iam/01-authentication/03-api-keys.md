# API Key Authentication

**What it is:** A long random string that identifies the calling application.

**Example:** `abc123-very-long-random-key-xyz789`

## How It Works

### Request Format
```http
GET /orders
x-api-key: abc123xyz
```

### Server Validation
1. Look up key in database
2. Check if active
3. Allow request

## What It Identifies

- ✅ The **application**
- ❌ NOT a user

## Why It's Popular

- Easy to implement
- Easy to understand
- No complex flows

## Problems

- ❌ No permissions per endpoint
- ❌ No user context
- ❌ If leaked → full access
- ❌ Hard to revoke (must update all clients)

## Configuration Requirements

| Field | Why |
|-------|-----|
| Base URL | API endpoint |
| API Key | Secret value |
| Auth Location | Header / Query / Cookie |
| Header Name | e.g. `x-api-key` |
| Query Param Name | If sent as query |

### Example Headers
```http
x-api-key: abc123xyz
# OR
Authorization: ApiKey abc123xyz
```

### Example Query Parameter
```
GET /api/resource?api_key=abc123xyz
```

## Best Practices

- ✅ Rotate keys regularly
- ✅ Use different keys per environment
- ✅ Monitor key usage
- ✅ Revoke compromised keys immediately
- ❌ Don't use for user authentication
- ❌ Don't commit keys to Git

## When to Use

- ✅ Public APIs
- ✅ Low-risk internal APIs
- ✅ Simple integrations
- ❌ Secure systems requiring user context
- ❌ Fine-grained permissions needed

