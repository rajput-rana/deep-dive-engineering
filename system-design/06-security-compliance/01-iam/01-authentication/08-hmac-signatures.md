# HMAC / Signature-Based Authentication

**What it is:** Request is signed using shared secret.

**How it looks:** `X-Signature: sha256(...)`

## How It Works

```
1. Client creates request
   ↓
2. Client signs request with secret key
   ↓
3. Client sends request + signature
   ↓
4. Server verifies signature
   ↓
5. Request allowed if signature valid
```

## Request Format

```http
POST /api/webhook
X-Signature: sha256(secret + request_body + timestamp)
X-Timestamp: 1700000000
Content-Type: application/json

{
  "event": "payment.completed",
  "data": {...}
}
```

## Why Use Signatures?

- ✅ **Prevents tampering** - Request can't be modified
- ✅ **Time-bound** - Timestamp prevents replay attacks
- ✅ **No shared secrets in request** - Only signature
- ✅ **Proves authenticity** - Only holder of secret can sign

## Configuration Requirements

| Field | Why |
|-------|-----|
| Base URL | API endpoint |
| API Key / Access Key | Identifier |
| Secret Key | Used to sign |
| Signature Algorithm | HMAC-SHA256 |
| Timestamp Header | Replay protection |
| Nonce (optional) | Uniqueness |
| Signed Headers List | Validation |

## Used By

- AWS APIs (AWS Signature Version 4)
- Webhooks (GitHub, Stripe)
- Payment gateways
- API integrations requiring integrity

## Best Practices

- ✅ Include timestamp in signature
- ✅ Validate timestamp (reject old requests)
- ✅ Use strong hash algorithms (SHA-256+)
- ✅ Sign all important headers
- ✅ Include nonce for additional security
- ❌ Don't include secret in signature calculation documentation

## When to Use

- ✅ Webhooks
- ✅ API integrations requiring integrity
- ✅ Payment processing
- ✅ High-security APIs
- ❌ Simple APIs (overkill)

