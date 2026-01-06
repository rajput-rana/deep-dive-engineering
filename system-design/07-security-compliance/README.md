# 🔐 Security & Compliance

<div align="center">

**Comprehensive security and compliance documentation**

[![Topics](https://img.shields.io/badge/Topics-50%2B-blue?style=for-the-badge)](./)
[![Security](https://img.shields.io/badge/Security-First-red?style=for-the-badge)](./)

*Most breaches start with Identity, not crypto.*

</div>

---

## 🎯 Security Landscape Overview

<div align="center">

```
Identity → Secrets → Data → App → Infra → Logs → Incidents → Compliance
```

**🔑 Key Principle:** Most breaches start with Identity, not cryptography.

</div>

---

## 📚 Table of Contents

<div align="center">

| Section | Topics | Description | Link |
|:---:|:---:|:---:|:---:|
| **🔐 01. IAM** | 25+ Topics | Identity, Authentication & Authorization | [Explore →](./01-iam/) |
| **🔑 02. Secrets Management** | - | API keys, DB passwords, Certificates | [Explore →](./02-secrets-management/) |
| **🛡️ 03. Data Security & Privacy** | 5 Topics | Encryption, Tokenization, GDPR | [Explore →](./03-data-security-privacy/) |
| **🔒 04. Application Security** | - | OWASP Top 10, Secure coding | [Explore →](./04-application-security/) |
| **🌐 05. Infrastructure & Network** | - | VPCs, Firewalls, Zero Trust | [Explore →](./05-infrastructure-network-security/) |
| **📊 06. Monitoring & Incident Response** | - | SIEM, IDS/IPS, Audit logs | [Explore →](./06-monitoring-logging-incident-response/) |
| **✅ 07. Compliance & Governance** | - | SOC 2, ISO 27001, PCI DSS, HIPAA | [Explore →](./07-compliance-governance-risk/) |
| **🚀 08. Secure SDLC** | - | DevSecOps, Threat modeling | [Explore →](./08-secure-sdlc/) |

</div>

---

## 🛡️ Security Principles

<div align="center">

| Principle | Description |
|:---:|:---:|
| **🛡️ Defense in Depth** | Multiple layers of security controls |
| **🔐 Least Privilege** | Grant minimum permissions necessary |
| **🚫 Zero Trust** | Never trust, always verify |
| **🔒 Fail Secure** | System defaults to secure state on failure |
| **🏗️ Security by Design** | Security built in from the start |

</div>

---

## 🎯 Common Attack Vectors

<div align="center">

| # | Attack Vector | Description |
|:---:|:---:|:---:|
| **1** | **Broken Authentication** | Weak passwords, session hijacking |
| **2** | **Injection Attacks** | SQL injection, NoSQL injection, XSS |
| **3** | **Broken Access Control** | Unauthorized access to resources |
| **4** | **Security Misconfiguration** | Default credentials, exposed configs |
| **5** | **Vulnerable Components** | Outdated libraries with known vulnerabilities |

</div>

---

## 📖 Quick Reference

<div align="center">

### Authentication Methods

| Method | Description | Use Case |
|:---:|:---:|:---:|
| **Passwords & Hashing** | bcrypt, argon2 | User authentication |
| **MFA** | TOTP, SMS, hardware keys | Enhanced security |
| **SSO** | SAML, OIDC | Enterprise authentication |
| **OAuth2** | OAuth2 flows | Third-party access |
| **Passwordless** | WebAuthn, passkeys | Modern authentication |

### Authorization Models

| Model | Description | Use Case |
|:---:|:---:|:---:|
| **RBAC** | Role-Based Access Control | Role-based permissions |
| **ABAC** | Attribute-Based Access Control | Fine-grained permissions |
| **Least Privilege** | Minimum necessary access | Security best practice |
| **Fine-grained** | Granular permissions | Resource-level control |

### Secrets Best Practices

<div align="center">

| ✅ Do | ❌ Don't |
|:---:|:---:|
| Never hardcode secrets | Commit secrets to Git |
| Use central vault (KMS, Vault) | Share secrets via email/chat |
| Short-lived secrets | Use default secrets |
| Automatic rotation | Store in environment variables |
| Encrypt at rest | Log secrets |

</div>

</div>

---

## 📋 OWASP Top 10 (2021)

<div align="center">

| # | Vulnerability | Description |
|:---:|:---:|:---:|
| **1** | Broken Access Control | Unauthorized access |
| **2** | Cryptographic Failures | Weak encryption |
| **3** | Injection | SQL, NoSQL, XSS injection |
| **4** | Insecure Design | Design flaws |
| **5** | Security Misconfiguration | Default configs |
| **6** | Vulnerable Components | Outdated libraries |
| **7** | Authentication Failures | Weak authentication |
| **8** | Data Integrity Failures | Untrusted data |
| **9** | Logging Failures | Insufficient logging |
| **10** | SSRF | Server-Side Request Forgery |

</div>

---

## ✅ Compliance Frameworks

<div align="center">

| Framework | Description | Industry |
|:---:|:---:|:---:|
| **SOC 2** | Service Organization Control 2 | Cloud services |
| **ISO 27001** | Information Security Management | International |
| **PCI DSS** | Payment Card Industry Standard | Payments |
| **HIPAA** | Health Insurance Portability Act | Healthcare |
| **GDPR** | General Data Protection Regulation | EU data protection |

</div>

---

## 🎓 Learning Path

<div align="center">

### Recommended Study Order

| Step | Topic | Why |
|:---:|:---:|:---:|
| **1️⃣** | [IAM](./01-iam/) | Foundation of security |
| **2️⃣** | [Secrets Management](./02-secrets-management/) | Protect sensitive data |
| **3️⃣** | [Application Security](./04-application-security/) | Secure your code |
| **4️⃣** | [Infrastructure Security](./05-infrastructure-network-security/) | Secure infrastructure |
| **5️⃣** | [Monitoring & Compliance](./06-monitoring-logging-incident-response/) | Detect & respond |

</div>

---

## 🔗 Related Sections

<div align="center">

| Section | Description | Link |
|:---:|:---:|:---:|
| **Fundamentals** | System design basics | [01. Fundamentals](../01-fundamentals/) |
| **Networking** | HTTPS, TLS | [04. Networking](../04-networking-protocols/) |
| **Architectures** | Secure architecture patterns | [06. Architectures](../06-architectures/) |

</div>

---

<div align="center">

**Build secure systems from the ground up! 🔐**

</div>
