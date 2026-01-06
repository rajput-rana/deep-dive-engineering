# Authentication Overview

**Authentication = "How does the API know who you are and what you're allowed to do?"**

Authentication is the process of verifying identity. The proof can be:
- A secret (password, API key)
- A token (JWT, OAuth token)
- A certificate (mTLS)
- A signature (HMAC)
- A network-level identity (VPC, IP whitelist)

## Authentication Methods by Scenario

| Scenario | Common Choice | Why |
|----------|--------------|-----|
| Public API | API Key | Simple, easy to implement |
| Internal microservices | JWT + mTLS | Stateless, scalable, secure |
| External SaaS integration | OAuth 2.0 | Industry standard, secure delegation |
| Machine-to-machine | OAuth Client Credentials | App-level identity |
| Legacy systems | Username + Password | Traditional approach |
| Banking / Payments | Certificates | Strongest security |

## One-Line Summary

- **Username/Password** → Humans
- **API Key** → Simple apps
- **JWT** → Scalable identity
- **OAuth** → Delegated, external access
- **Client Secret** → App identity
- **Certificates** → Strongest security

## Authentication Proof Types

### Something You Know
- Password
- API key
- Client secret

### Something You Have
- Token (JWT, OAuth)
- Certificate
- Hardware key

### Something the Auth Server Issued
- OAuth access token
- JWT token
- Session token

## Token Formats Comparison

| Token Format | Self-Contained | DB Call Needed | Revocation | Common |
|--------------|---------------|----------------|------------|--------|
| **Opaque** | ❌ | ✅ | Easy | ✅ |
| **JWT** | ✅ | ❌ | Hard | ✅✅ |
| **Reference** | ❌ | ✅ | Easy | ✅ |
| **PASETO** | ✅ | ❌ | Hard | 🔸 |
| **Macaroon** | ✅ | ❌ | Medium | 🔸 |

**Key Takeaway:** Bearer is just the transport. The token format can be anything. Most real systems use JWT or opaque/reference tokens.

## Related Topics

- **[02. Username & Password](./02-username-password.md)** - Traditional authentication
- **[03. API Keys](./03-api-keys.md)** - Simple app authentication
- **[04. Bearer Tokens](./04-bearer-tokens.md)** - Token transport mechanism
- **[05. JWT](./05-jwt.md)** - Self-contained tokens
- **[06. OAuth 2.0](./06-oauth2.md)** - Delegated authorization framework
- **[07. Certificates & mTLS](./07-certificates-mtls.md)** - Certificate-based authentication
- **[08. HMAC Signatures](./08-hmac-signatures.md)** - Signature-based authentication

