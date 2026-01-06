# Authentication

**Authentication answers: "Who are you?"**

Authentication is the process of verifying the identity of a user, service, or system. It's the first line of defense in security—most breaches start here.

## Table of Contents

- **[01. Authentication Overview](./01-authentication-overview.md)** - Introduction to authentication methods
- **[02. Username & Password](./02-username-password.md)** - Traditional authentication, HTTP Basic Auth
- **[03. API Keys](./03-api-keys.md)** - Simple app authentication
- **[04. Bearer Tokens](./04-bearer-tokens.md)** - Token transport mechanism
- **[05. JWT](./05-jwt.md)** ⭐ - Self-contained tokens (most important)
- **[06. OAuth 2.0](./06-oauth2.md)** ⭐ - Delegated authorization framework
- **[07. Certificates & mTLS](./07-certificates-mtls.md)** 🔐 - Strongest security
- **[08. HMAC Signatures](./08-hmac-signatures.md)** - Signature-based authentication
- **[09. OpenID Connect](./09-openid-connect.md)** - Identity layer on OAuth
- **[10. SSO](./10-sso.md)** - Single Sign-On
- **[11. MFA](./11-mfa.md)** - Multi-Factor Authentication
- **[12. Passwordless](./12-passwordless.md)** - WebAuthn, Passkeys

## Quick Reference

### By Scenario
- **Public API** → API Key
- **Internal microservices** → JWT + mTLS
- **External SaaS** → OAuth 2.0
- **Machine-to-machine** → OAuth Client Credentials
- **Legacy systems** → Username + Password
- **Banking/Payments** → Certificates

### By Use Case
- **Humans logging in** → Username/Password, OAuth, SSO
- **Simple apps** → API Key
- **Scalable identity** → JWT
- **Delegated access** → OAuth
- **App identity** → Client Secret
- **Strongest security** → Certificates

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

## Security Considerations

### Password Security
- ✅ Use strong password policies
- ✅ Hash passwords (bcrypt, argon2)
- ✅ Implement account lockout
- ❌ Never log passwords

### Token Security
- ✅ Use short-lived tokens
- ✅ Implement token refresh
- ✅ Validate token signatures
- ✅ Use HTTPS for token transmission

### Session Security
- ✅ Use secure cookies (HttpOnly, Secure, SameSite)
- ✅ Implement session timeout
- ✅ Regenerate session IDs

## Common Vulnerabilities

1. **Weak Passwords** - Easily guessable
2. **Password Reuse** - Same password across services
3. **Session Hijacking** - Stolen session tokens
4. **Brute Force Attacks** - Automated password guessing
5. **Credential Stuffing** - Using leaked credentials

## Best Practices

- Implement MFA for sensitive accounts
- Use passwordless authentication when possible
- Implement rate limiting on login attempts
- Log all authentication events
- Monitor for suspicious login patterns
- Use secure password reset flows

## Related Topics

- **[Authorization](../02-authorization/)** - What users can do after authentication
- **[Secrets Management](../../02-secrets-management/)** - Managing authentication credentials
- **[Application Security](../../04-application-security/)** - Secure authentication implementation
