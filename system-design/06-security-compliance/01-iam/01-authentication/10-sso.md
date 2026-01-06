# SSO (Single Sign-On)

**What it is:** User authenticates once and gains access to multiple applications without logging in again.

**Core idea:** Authentication happens centrally; applications trust a central Identity Provider (IdP).

## How SSO Works

```
1. User logs into Identity Provider (IdP)
   ↓
2. User accesses Application A
   ↓
3. Application A redirects to IdP
   ↓
4. IdP sees user is logged in
   ↓
5. IdP issues token/assertion
   ↓
6. User accesses Application A (no re-login)
   ↓
7. User accesses Application B
   ↓
8. Same flow - no re-login needed
```

## SSO Components

| Component | Role |
|-----------|------|
| **User** | Human logging in |
| **Identity Provider (IdP)** | Authenticates user (Okta, Azure AD, Auth0) |
| **Service Provider (SP) / Relying Party (RP)** | Application user wants to access |
| **Trust Relationship** | Certificates/keys shared beforehand |

## Benefits

- ✅ **Better UX** - One login for all apps
- ✅ **Centralized security** - Security policies in one place
- ✅ **Easier user management** - Centralized user lifecycle
- ✅ **Reduced password fatigue** - Fewer passwords to remember
- ✅ **Better security** - Centralized security controls

## SSO Protocols

### SAML (Security Assertion Markup Language)
- XML-based
- Enterprise SSO
- Browser-based flows
- **Use Cases:** Legacy enterprise, corporate SSO

### OIDC (OpenID Connect)
- Modern, JSON-based
- Built on OAuth 2.0
- Mobile and API-friendly
- **Use Cases:** Modern SSO, SaaS applications, cloud apps

## SSO Flow Types

### SP-Initiated SSO
- User starts at application
- App redirects to IdP
- IdP authenticates and redirects back

### IdP-Initiated SSO
- User starts at IdP portal
- User selects application
- IdP sends assertion directly

## Common SSO Providers

- **Google Workspace** - OIDC/SAML
- **Microsoft Azure AD** - OIDC/SAML
- **Okta** - OIDC/SAML
- **Auth0** - OIDC
- **AWS SSO** - SAML

## Relationship: SSO, SAML, OIDC

| Term | Category |
|------|----------|
| **SSO** | Concept (behavior) |
| **SAML** | Protocol (how SSO is implemented) |
| **OIDC** | Protocol (how SSO is implemented) |

**SSO describes behavior; SAML/OIDC define how that behavior is implemented.**

## Best Practices

- ✅ Use OIDC for new implementations
- ✅ Implement proper session management
- ✅ Use secure token storage
- ✅ Support both SP-initiated and IdP-initiated flows
- ✅ Monitor SSO usage and failures

## When to Use

- ✅ Enterprise environments
- ✅ Multiple related applications
- ✅ User convenience priority
- ✅ Centralized identity management
- ❌ Single application (overkill)

## Related Topics

- **[SAML](./13-saml.md)** - XML-based SSO protocol
- **[OpenID Connect](./09-openid-connect.md)** - Modern SSO protocol
- **[SLO](./14-slo.md)** - Single Logout
- **[OAuth 2.0](./06-oauth2.md)** - Foundation for OIDC
