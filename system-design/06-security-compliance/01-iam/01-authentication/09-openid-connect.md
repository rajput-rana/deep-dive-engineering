# OpenID Connect (OIDC)

**What it is:** Modern authentication layer on top of OAuth 2.0.

**Key difference:** OAuth = access, OIDC = identity

## OAuth vs OIDC

| Aspect | OAuth 2.0 | OpenID Connect |
|--------|-----------|---------------|
| **Purpose** | Access delegation | Identity verification |
| **Token** | Access token | ID token + Access token |
| **Focus** | What can you access? | Who are you? |
| **Use Case** | API access | User login, SSO |

## OIDC Characteristics

| Attribute | Value |
|-----------|-------|
| **Data Format** | JSON |
| **Transport** | REST / HTTPS |
| **Token** | JWT |
| **Mobile/API Support** | Excellent |
| **Complexity** | Lower than SAML |
| **Typical Users** | SaaS, consumer apps |

## OIDC Authentication Flow (Authorization Code)

```
1. App redirects user to IdP
   ↓
2. User authenticates at IdP
   ↓
3. IdP redirects back with authorization code
   ↓
4. App exchanges code for tokens:
   - ID Token
   - Access Token
   - (Optional) Refresh Token
   ↓
5. App validates ID Token
   ↓
6. Session created
```

## OIDC Tokens Explained

| Token | Purpose |
|-------|---------|
| **ID Token** | Proves who the user is |
| **Access Token** | Access APIs |
| **Refresh Token** | Get new tokens |

## ID Token Claims

```json
{
  "iss": "https://accounts.google.com",
  "sub": "109876543210",
  "aud": "client_abc123",
  "exp": 1766236800,
  "iat": 1766233200,
  "nonce": "n-0S6_WzA2Mj",
  "email": "user@example.com",
  "email_verified": true,
  "name": "John Doe"
}
```

**Key Claims:**
- **sub** → User ID
- **iss** → Issuer (IdP)
- **aud** → Client ID
- **exp** → Expiry
- **email, name** → User attributes

## Configuration Requirements

### SP (Client) Registers with IdP

| Field | Description |
|-------|-------------|
| Client ID | App identifier |
| Client Secret | App secret |
| Redirect URI | Callback URL |
| Scopes | `openid`, `email`, `profile` |

**Example Redirect URI:** `https://app.example.com/oauth/callback`

### IdP Provides to SP

| Field | Description |
|-------|-------------|
| Issuer URL | Identity of IdP |
| JWKS URL | Public keys for token validation |
| Authorization URL | Login endpoint |
| Token URL | Exchange code for tokens |

## What SP Validates

- ✅ JWT signature (using JWKS)
- ✅ `iss` matches IdP
- ✅ `aud` matches Client ID
- ✅ `exp` and `iat` (time validity)
- ✅ `nonce` (prevents replay)

## OIDC vs SAML

| Feature | SAML | OIDC |
|---------|------|------|
| **Protocol Age** | Older | Modern |
| **Format** | XML | JSON/JWT |
| **Mobile Support** | Poor | Excellent |
| **Debuggability** | Hard | Easy |
| **Token Validation** | XML signature | JWT signature |
| **Performance** | Heavier | Lightweight |
| **Recommended Today** | ❌ | ✅ |

**Rule of thumb:** Use OIDC unless you must support legacy enterprise IdPs.

## Common Interview Questions

**Q: Can OAuth be used for authentication?**
- OAuth is authorization, not authentication
- OIDC adds authentication on top of OAuth
- OAuth alone cannot tell who the user is

**Q: How does OIDC prevent token replay attacks?**
- Short token TTL
- `nonce` validation
- HTTPS only
- JWT signature verification
- Optional token binding

**Q: How do you validate a JWT ID Token?**
- Verify signature using IdP public key (JWKS)
- Check `iss` (issuer)
- Check `aud` (audience)
- Check `exp` and `nbf` (time validity)
- Validate `nonce`

**Q: Which protocol is better for microservices?**
- **OIDC** - JWTs are stateless, no XML parsing, better performance, easier service-to-service auth

## Best Practices

- ✅ Use Authorization Code flow with PKCE
- ✅ Validate all token claims
- ✅ Use short-lived ID tokens
- ✅ Implement refresh token rotation
- ✅ Use HTTPS for all communication
- ✅ Store tokens securely

## When to Use

- ✅ User authentication
- ✅ SSO implementations
- ✅ Modern SaaS applications
- ✅ Mobile applications
- ✅ Microservices
- ✅ When you need user identity
- ❌ Machine-to-machine (use OAuth Client Credentials)

## Related Topics

- **[OAuth 2.0](./06-oauth2.md)** - Foundation of OIDC
- **[JWT](./05-jwt.md)** - ID tokens are JWTs
- **[SSO](./10-sso.md)** - Single Sign-On
- **[SLO](./14-slo.md)** - Single Logout
