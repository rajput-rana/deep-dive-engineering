# Identity, Authentication & Authorization (IAM)

Identity and Access Management (IAM) is the foundation of security. Most breaches start here, not crypto.

## Overview

IAM answers two critical questions:
1. **Authentication:** Who are you? (Identity verification)
2. **Authorization:** What can you do? (Permission management)

## Table of Contents

### 🔐 01. Authentication
- **[01. JWT (JSON Web Tokens)](./01-authentication/01-jwt.md)** - Token-based authentication
- **[02. Passwords & Hashing](./01-authentication/02-passwords-hashing.md)** - Password security, hashing algorithms
- **[03. MFA (Multi-Factor Authentication)](./01-authentication/03-mfa.md)** - TOTP, SMS, hardware keys
- **[04. SSO (Single Sign-On)](./01-authentication/04-sso.md)** - SAML, OIDC
- **[05. OAuth2](./01-authentication/05-oauth2.md)** - OAuth2 flows and patterns
- **[06. Passwordless](./01-authentication/06-passwordless.md)** - WebAuthn, passkeys

### 🛡️ 02. Authorization
- **[01. RBAC (Role-Based Access Control)](./02-authorization/01-rbac.md)** - Role-based permissions
- **[02. ABAC (Attribute-Based Access Control)](./02-authorization/02-abac.md)** - Attribute-based permissions
- **[03. Least Privilege](./02-authorization/03-least-privilege.md)** - Principle of least privilege
- **[04. Fine-Grained Permissions](./02-authorization/04-fine-grained-permissions.md)** - Granular access control

### 🔧 03. Service Identity
- **[01. mTLS (Mutual TLS)](./03-service-identity/01-mtls.md)** - Mutual authentication for services
- **[02. SPIFFE / SPIRE](./03-service-identity/02-spiffe-spire.md)** - Secure Production Identity Framework
- **[03. Service Accounts](./03-service-identity/03-service-accounts.md)** - Service-to-service authentication

## Authentication vs Authorization

**Authentication (AuthN):**
- Verifies identity
- Answers: "Who are you?"
- Examples: Login, password verification, MFA

**Authorization (AuthZ):**
- Grants permissions
- Answers: "What can you do?"
- Examples: RBAC, ABAC, access control lists

## Common Patterns

### Token-Based Authentication
- JWT tokens
- OAuth2 access tokens
- API keys

### Session-Based Authentication
- Server-side sessions
- Cookie-based
- Stateful authentication

### Federated Identity
- SSO across organizations
- SAML federation
- OIDC federation

## Best Practices

### Authentication
- ✅ Use strong password policies
- ✅ Implement MFA
- ✅ Use secure password hashing (bcrypt, argon2)
- ✅ Implement account lockout policies
- ✅ Use HTTPS for all authentication

### Authorization
- ✅ Follow least privilege principle
- ✅ Use RBAC or ABAC appropriately
- ✅ Regular access reviews
- ✅ Audit all access decisions
- ✅ Implement fine-grained permissions

### Service Identity
- ✅ Use mTLS for service-to-service communication
- ✅ Rotate service credentials regularly
- ✅ Use SPIFFE/SPIRE for dynamic identity
- ✅ Never share service accounts

## Related Topics

- **[02. Secrets Management](../02-secrets-management/)** - Managing API keys and credentials
- **[03. Data Security](../03-data-security-privacy/)** - Protecting data based on identity
- **[04. Application Security](../04-application-security/)** - Secure authentication implementation

