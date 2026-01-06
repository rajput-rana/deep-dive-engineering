# Security & Compliance

Comprehensive security and compliance documentation covering the full security landscape: Identity → Secrets → Data → App → Infra → Logs → Incidents → Compliance.

## Security Landscape Overview

```
Identity → Secrets → Data → App → Infra → Logs → Incidents → Compliance
```

**Most breaches start with Identity, not crypto.**

## Table of Contents

### 🔐 01. Identity, Authentication & Authorization (IAM)
- **[01. Authentication](./01-iam/01-authentication/)** - Who are you? Passwords, MFA, SSO, OAuth2, Passwordless
- **[02. Authorization](./01-iam/02-authorization/)** - What can you do? RBAC, ABAC, Least privilege
- **[03. Service Identity](./01-iam/03-service-identity/)** - mTLS, SPIFFE/SPIRE, Service accounts

### 🔑 02. Secrets Management
- **[02. Secrets Management](./02-secrets-management/)** - API keys, DB passwords, Certificates, Encryption keys

### 🛡️ 03. Data Security & Privacy
- **[03. Data Security & Privacy](./03-data-security-privacy/)** - Data lifecycle, Encryption, Tokenization, Privacy (GDPR)

### 🔒 04. Application Security (AppSec)
- **[04. Application Security](./04-application-security/)** - Secure coding, OWASP Top 10, Dependency security

### 🌐 05. Infrastructure & Network Security
- **[05. Infrastructure & Network Security](./05-infrastructure-network-security/)** - Network security, Host security, Container/K8s security

### 📊 06. Monitoring, Logging & Incident Response
- **[06. Monitoring, Logging & Incident Response](./06-monitoring-logging-incident-response/)** - Detection, Logging, Incident response

### ✅ 07. Compliance, Governance & Risk (GRC)
- **[07. Compliance, Governance & Risk](./07-compliance-governance-risk/)** - SOC 2, ISO 27001, PCI DSS, HIPAA, GDPR

### 🚀 08. Secure SDLC (Shift Left)
- **[08. Secure SDLC](./08-secure-sdlc/)** - DevSecOps, Threat modeling, Secure CI/CD

## Security Principles

### Defense in Depth
Multiple layers of security controls to protect against threats.

### Least Privilege
Grant minimum permissions necessary for users and services.

### Zero Trust
Never trust, always verify—verify every request.

### Fail Secure
System defaults to secure state on failure.

### Security by Design
Security built into the system from the start, not bolted on.

## Common Attack Vectors

1. **Broken Authentication** - Weak passwords, session hijacking
2. **Injection Attacks** - SQL injection, NoSQL injection, XSS
3. **Broken Access Control** - Unauthorized access to resources
4. **Security Misconfiguration** - Default credentials, exposed configs
5. **Vulnerable Components** - Outdated libraries with known vulnerabilities

## Quick Reference

### Authentication Methods
- Passwords & hashing (bcrypt, argon2)
- MFA (TOTP, SMS, hardware keys)
- SSO (SAML, OIDC)
- OAuth2 flows
- Passwordless (WebAuthn, passkeys)

### Authorization Models
- RBAC (Role-Based Access Control)
- ABAC (Attribute-Based Access Control)
- Least privilege principle
- Fine-grained permissions

### Secrets Best Practices
- ✅ Never hardcode secrets
- ✅ Use central vault (KMS, Vault)
- ✅ Short-lived secrets
- ✅ Automatic rotation
- ❌ Never commit secrets to Git

### OWASP Top 10 (2021)
1. Broken Access Control
2. Cryptographic Failures
3. Injection
4. Insecure Design
5. Security Misconfiguration
6. Vulnerable & Outdated Components
7. Identification & Authentication Failures
8. Software & Data Integrity Failures
9. Logging & Monitoring Failures
10. Server-Side Request Forgery (SSRF)

## Compliance Frameworks

- **SOC 2** - Service Organization Control 2
- **ISO 27001** - Information Security Management
- **PCI DSS** - Payment Card Industry Data Security Standard
- **HIPAA** - Health Insurance Portability and Accountability Act
- **GDPR** - General Data Protection Regulation

## Related Sections

- **[01. Fundamentals](../01-fundamentals/)** - System design basics
- **[04. Networking Protocols](../04-networking-protocols/)** - HTTPS, TLS
- **[06. Design Patterns](../06-architectures/)** - Secure architecture patterns

## Learning Path

1. **Start with IAM:** Understand authentication and authorization
2. **Secrets Management:** Learn to protect sensitive data
3. **Application Security:** Secure your code (OWASP Top 10)
4. **Infrastructure Security:** Secure your infrastructure
5. **Monitoring & Compliance:** Detect and respond to threats
