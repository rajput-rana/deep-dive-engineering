# Username & Password Authentication

**What it is:** Client sends username and password to prove identity.

## How It Works

### Request Format
```http
POST /login
Content-Type: application/json

{
  "username": "rana",
  "password": "secret123"
}
```

### Server Validation
1. Server hashes password
2. Compares with database
3. If valid → success (returns token/session)

## Where Used

- ✅ Human login
- ✅ Admin dashboards
- ✅ Legacy APIs
- ❌ Service-to-service integration

## Why It's Bad for APIs

- Password sent frequently (every request)
- Hard to rotate
- No scoped access
- If leaked → full account compromise

## HTTP Basic Authentication

**What it is:** Username + password encoded in Base64

### Request Format
```http
GET /api/resource
Authorization: Basic dXNlcjpwYXNz
```

**Decoded:** `user:pass` → Base64 encoded

### Where Used
- Legacy APIs
- Internal tools
- Simple integrations

### Important Notes
- ⚠️ **Must use HTTPS** (otherwise credentials exposed)
- No session or token
- Credentials sent with every request

## Best Practices

- ✅ Use strong password policies
- ✅ Hash passwords (bcrypt, argon2)
- ✅ Use HTTPS only
- ✅ Implement account lockout
- ✅ Rate limit login attempts
- ❌ Never log passwords
- ❌ Never send passwords via email

## When to Use

- ✅ Humans logging in
- ✅ Admin interfaces
- ❌ Service-to-service integration
- ❌ Public APIs

