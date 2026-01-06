# SSO (Single Sign-On)

**What it is:** One login for multiple applications.

**One-line:** Login once, access many apps without re-authenticating.

## How SSO Works

```
1. User logs in to Identity Provider
   ↓
2. User accesses Application A
   ↓
3. Application A redirects to Identity Provider
   ↓
4. Identity Provider sees user is logged in
   ↓
5. Identity Provider issues token
   ↓
6. User accesses Application A (no re-login)
   ↓
7. User accesses Application B
   ↓
8. Same flow - no re-login needed
```

## SSO Protocols

### SAML (Security Assertion Markup Language)
- XML-based
- Enterprise SSO
- Heavy, legacy
- **Use Cases:** Corporate SSO, Enterprise integrations

### OIDC (OpenID Connect)
- Modern, JSON-based
- Built on OAuth 2.0
- **Use Cases:** Modern SSO, Cloud applications

## Benefits

- ✅ **User convenience** - Login once
- ✅ **Reduced password fatigue** - Fewer passwords
- ✅ **Centralized identity** - One source of truth
- ✅ **Easier management** - Centralized user management
- ✅ **Better security** - Centralized security controls

## Architecture

```
┌─────────┐
│  User   │
└────┬────┘
     │
     ▼
┌──────────────┐
│ Identity     │ ← SSO Provider
│ Provider     │
│ (IdP)        │
└──────┬───────┘
       │
   ┌───┴───┬────────┬────────┐
   │       │        │        │
   ▼       ▼        ▼        ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐
│App1│ │App2│ │App3│ │App4│
└────┘ └────┘ └────┘ └────┘
```

## Common SSO Providers

- **Google Workspace** - OIDC/SAML
- **Microsoft Azure AD** - OIDC/SAML
- **Okta** - OIDC/SAML
- **Auth0** - OIDC
- **AWS SSO** - SAML

## Best Practices

- ✅ Use OIDC for modern implementations
- ✅ Implement proper session management
- ✅ Use secure token storage
- ✅ Implement logout across all apps
- ✅ Monitor SSO usage

## When to Use

- ✅ Enterprise environments
- ✅ Multiple related applications
- ✅ User convenience priority
- ✅ Centralized identity management
- ❌ Single application (overkill)

## Related Topics

- **[OAuth 2.0](./06-oauth2.md)** - Foundation for modern SSO
- **[OpenID Connect](./09-openid-connect.md)** - Identity layer for SSO
- **[Authorization](../02-authorization/)** - What users can do after SSO

