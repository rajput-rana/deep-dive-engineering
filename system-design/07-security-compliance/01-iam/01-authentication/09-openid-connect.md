# OpenID Connect (OIDC)

**What it is:** Identity layer on top of OAuth 2.0

**Key Difference:** OAuth = access, OIDC = identity

## OAuth vs OIDC

| Aspect | OAuth 2.0 | OpenID Connect |
|--------|-----------|----------------|
| **Purpose** | Access delegation | Identity verification |
| **Token** | Access token | ID token + Access token |
| **Focus** | What can you access? | Who are you? |
| **Use Case** | API access | User login, SSO |

## OIDC Components

### ID Token
- **JWT token** containing user identity
- Claims: `sub`, `email`, `name`, `picture`
- Signed by identity provider

### Access Token
- Same as OAuth access token
- Used to access APIs

### UserInfo Endpoint
- Returns user profile information
- Accessed with access token

## How OIDC Works

```
1. Client requests authentication
   ↓
2. User authenticates with Identity Provider
   ↓
3. Identity Provider issues ID token + Access token
   ↓
4. Client validates ID token
   ↓
5. Client knows user identity
```

## ID Token Example

```json
{
  "iss": "https://accounts.google.com",
  "sub": "123456789",
  "aud": "client-id",
  "email": "user@example.com",
  "name": "John Doe",
  "picture": "https://...",
  "iat": 1709913600,
  "exp": 1709917200
}
```

## Use Cases

- ✅ SSO (Single Sign-On)
- ✅ Enterprise identity
- ✅ "Login with Google/Facebook"
- ✅ Multi-tenant applications
- ✅ User profile access

## Best Practices

- ✅ Validate ID token signature
- ✅ Check issuer (iss) and audience (aud)
- ✅ Verify expiration (exp)
- ✅ Use nonce to prevent replay attacks
- ✅ Cache ID tokens appropriately

## When to Use

- ✅ User authentication
- ✅ SSO implementations
- ✅ When you need user identity
- ✅ Enterprise identity management
- ❌ Machine-to-machine (use OAuth Client Credentials)

## Related Topics

- **[OAuth 2.0](./06-oauth2.md)** - Foundation of OIDC
- **[JWT](./05-jwt.md)** - ID tokens are JWTs
- **[SSO](./10-sso.md)** - Single Sign-On

