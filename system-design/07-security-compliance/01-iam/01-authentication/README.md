# Authentication

**Authentication answers: "Who are you?"**

Authentication is the process of verifying the identity of a user, service, or system. It's the first line of defense in security—most breaches start here.

## Table of Contents

- **[01. JWT (JSON Web Tokens)](./01-jwt.md)** - Token-based authentication
- **[02. Passwords & Hashing](./02-passwords-hashing.md)** - Password security, hashing algorithms (bcrypt, argon2)
- **[03. MFA (Multi-Factor Authentication)](./03-mfa.md)** - TOTP, SMS, hardware keys
- **[04. SSO (Single Sign-On)](./04-sso.md)** - SAML, OIDC
- **[05. OAuth2](./05-oauth2.md)** - OAuth2 flows and patterns
- **[06. Passwordless](./06-passwordless.md)** - WebAuthn, passkeys

## Authentication Methods

### 1. Password-Based Authentication
- Traditional username/password
- Requires secure password hashing
- Vulnerable to brute force attacks
- **Best Practice:** Use strong hashing (bcrypt, argon2)

### 2. Multi-Factor Authentication (MFA)
- Something you know (password)
- Something you have (phone, hardware key)
- Something you are (biometrics)
- **Types:** TOTP, SMS, hardware keys (FIDO2)

### 3. Single Sign-On (SSO)
- One login for multiple applications
- **Protocols:** SAML, OIDC
- Reduces password fatigue
- Centralized identity management

### 4. OAuth2
- Delegated authorization
- **Flows:** Authorization Code, Client Credentials, Device Flow
- Used for third-party access
- Industry standard for API access

### 5. Passwordless Authentication
- **WebAuthn / Passkeys**
- Biometric authentication
- Hardware security keys
- More secure than passwords

## Authentication Flow

```
User → Authentication Request → Identity Provider
                                    ↓
                            Verify Credentials
                                    ↓
                            Generate Token/Session
                                    ↓
                            Return to Application
```

## Security Considerations

### Password Security
- ✅ Use strong password policies (length, complexity)
- ✅ Hash passwords (never store plaintext)
- ✅ Use salt with hashing
- ✅ Implement account lockout
- ❌ Never log passwords
- ❌ Never send passwords via email

### Token Security
- ✅ Use short-lived tokens
- ✅ Implement token refresh
- ✅ Validate token signatures
- ✅ Use HTTPS for token transmission
- ❌ Don't store tokens in localStorage (XSS risk)

### Session Security
- ✅ Use secure cookies (HttpOnly, Secure, SameSite)
- ✅ Implement session timeout
- ✅ Regenerate session IDs
- ✅ Validate session on each request

## Common Vulnerabilities

1. **Weak Passwords** - Easily guessable passwords
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
- Implement account recovery mechanisms

## Related Topics

- **[Authorization](../02-authorization/)** - What users can do after authentication
- **[Secrets Management](../../02-secrets-management/)** - Managing authentication credentials
- **[Application Security](../../04-application-security/)** - Secure authentication implementation

