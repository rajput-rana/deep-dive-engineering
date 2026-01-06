# OAuth 2.0 ⭐ EXTERNAL INTEGRATIONS

**What it is:** A framework for getting tokens **without sharing passwords**.

**One-line:** A delegation framework - "Let this app access my data, without giving my password."

## OAuth 2.0 Players

| Role | Meaning |
|------|---------|
| **Resource Owner** | User |
| **Client** | App requesting access |
| **Auth Server** | Issues tokens |
| **Resource Server** | API |

## How OAuth Works (Simplified)

```
1. Client asks Auth Server
   ↓
2. User approves
   ↓
3. Auth Server issues access token
   ↓
4. Client calls API using token
```

## OAuth Token Format

Usually a **JWT Bearer token**:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Common OAuth Flows

### 1. Authorization Code Flow
**For:** User login, web apps
**How:** Redirect → User approves → Code exchange → Token

### 2. Client Credentials Flow
**For:** Machine-to-machine, server-to-server
**How:** Client authenticates → Gets token directly

### 3. Refresh Token Flow
**For:** Long-lived access
**How:** Use refresh token → Get new access token

## Why OAuth is Complex?

- Multiple flows
- Refresh tokens
- Scopes
- Redirects
- Token management

## Why OAuth is Worth It?

- ✅ Secure (no password sharing)
- ✅ Industry standard
- ✅ Fine-grained permissions (scopes)
- ✅ Third-party safe

## Configuration Requirements

| Field | Why |
|-------|-----|
| Base URL | API endpoint |
| Authorization URL | Where user/app is authenticated |
| Token URL | Where access tokens are issued |
| Client ID | Identifies your application |
| Client Secret | Authenticates your application |
| Scopes | What access is requested |
| Grant Type | `authorization_code` / `client_credentials` |
| Redirect URI | Where auth server redirects (auth code flow) |
| Token Expiry | How long token is valid |
| Refresh Token | Used to renew access |

## OAuth 2.0 Components Explained

### Client ID
- **Public identifier** of the application
- Not secret, can be exposed

### Client Secret
- **Confidential key** used to authenticate the client
- Must be kept secret
- Used in server-to-server flows

### Scopes
- Permissions that limit access
- Examples: `read:orders`, `write:orders`
- Specified during authorization request

### Access Token
- Short-lived token to access resources
- Included in API requests
- Usually expires in minutes/hours

### Refresh Token
- Long-lived token to obtain new access tokens
- Stored securely
- Used when access token expires

## OAuth Flows in Detail

### Authorization Code Flow (User Login)

```
1. Client redirects user to Auth Server
   ↓
2. User logs in and approves
   ↓
3. Auth Server redirects back with code
   ↓
4. Client exchanges code for token
   ↓
5. Client uses token to access API
```

**Use Cases:** "Login with Google", User-consent APIs

### Client Credentials Flow (Machine-to-Machine)

```
1. Client authenticates with client_id + client_secret
   ↓
2. Auth Server issues access token
   ↓
3. Client uses token to access API
```

**Use Cases:** Server-to-server, Background jobs, Internal services

### PKCE (Proof Key for Code Exchange)

**What it is:** Extra security layer on Authorization Code flow

**Why:** Prevents code theft (especially for mobile/SPA)

**Additional Fields:**
- Code Verifier (random secret)
- Code Challenge (hashed verifier)
- Code Challenge Method (S256)

**Use Cases:** Mobile apps, SPA (React, Angular), Public clients

## Security Considerations

- ✅ **Use HTTPS** - Encrypt all communication
- ✅ **Validate redirect URIs** - Prevent open redirect attacks
- ✅ **Secure client secrets** - Never expose in public clients
- ✅ **Use PKCE** - For public clients (mobile, SPA)
- ✅ **Short-lived tokens** - Minimize exposure window
- ✅ **State parameter** - Prevent CSRF attacks

## Common Interview Questions

**Q: JWT vs OAuth?**
- JWT = token format
- OAuth = token issuing framework
- OAuth often issues JWT tokens

**Q: Why OAuth for external APIs?**
- No password sharing
- Scoped access
- Industry standard
- User consent

**Q: Why not API keys?**
- No fine-grained permissions
- Poor security
- Hard to revoke

## Best Practices

- ✅ Use Authorization Code flow for user login
- ✅ Use Client Credentials for server-to-server
- ✅ Use PKCE for public clients
- ✅ Implement refresh token rotation
- ✅ Validate all tokens
- ✅ Use appropriate scopes
- ❌ Never expose client secrets in public clients
- ❌ Never skip redirect URI validation

## When to Use

- ✅ External APIs
- ✅ SaaS integrations
- ✅ "Login with Google/Facebook"
- ✅ Third-party access
- ✅ User-delegated access
- ❌ Simple internal APIs (use API keys or JWT)

## Related Topics

- **[JWT](./05-jwt.md)** - Token format often used with OAuth
- **[OpenID Connect](./09-openid-connect.md)** - Identity layer on OAuth
- **[Authorization](../02-authorization/)** - What users can do after authentication

