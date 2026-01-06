# SAML (Security Assertion Markup Language)

**What it is:** XML-based authentication and authorization protocol for enterprise SSO.

**Full form:** SAML = Security Assertion Markup Language

## SAML Characteristics

| Attribute | Value |
|-----------|-------|
| **Data Format** | XML |
| **Transport** | Browser redirects + POST |
| **Token** | SAML Assertion |
| **Auth Flow** | Browser-based |
| **Mobile/API Support** | Poor |
| **Typical Users** | Enterprises |

## SAML Components

### Key Terms

| Term | Description |
|------|-------------|
| **Entity ID** | Unique identifier for SP or IdP |
| **ACS (Assertion Consumer Service)** | Endpoint where IdP sends SAML response |
| **Start URL** | URL where SSO flow begins |
| **SAML Assertion** | XML token containing user identity |

## SAML Authentication Flow (SP-Initiated)

```
1. User tries to access App (SP)
   ↓
2. SP redirects browser to IdP
   ↓
3. User authenticates at IdP
   ↓
4. IdP creates SAML Assertion
   ↓
5. Assertion is signed (and sometimes encrypted)
   ↓
6. Browser POSTs assertion to ACS
   ↓
7. SP validates:
   - Signature
   - Issuer
   - Audience
   - Time conditions
   ↓
8. User session created in SP
```

## SAML Assertion Contains

- **User identity** (NameID, email)
- **Attributes** (roles, groups)
- **Auth time, expiry**
- **Issuer info**

## SAML Configuration

### What SP Provides to IdP

| Field | Description |
|-------|-------------|
| Entity ID | Unique identifier of SP |
| ACS URL | Where IdP sends assertion |
| Certificate | To verify SP requests (optional) |
| NameID format | email / username |
| Attributes expected | email, firstName, role |

**Usually shared via SAML Metadata XML URL.**

### What IdP Provides to SP

| Field | Description |
|-------|-------------|
| IdP Entity ID | IdP identifier |
| SSO URL | Login endpoint |
| Certificate | Used to verify assertions |
| Logout URL | (Optional) |

## SAML Security

- ✅ **XML Digital Signatures** - X.509 certificates
- ✅ **Short-lived assertions** - Expiry protection
- ✅ **Replay protection** - Timestamps and assertion IDs
- ✅ **Audience restriction** - Entity ID validation
- ✅ **TLS encryption** - HTTPS transport

## What SP Validates

SP must validate:
- ✅ XML signature using IdP certificate
- ✅ Issuer matches IdP Entity ID
- ✅ Audience = SP Entity ID
- ✅ Recipient = ACS URL
- ✅ Time validity (NotBefore, NotOnOrAfter)
- ✅ Replay protection (Assertion ID)

## SAML vs OIDC

| Feature | SAML | OIDC |
|---------|------|------|
| **Format** | XML | JSON |
| **Transport** | Browser POST | REST |
| **Token** | Assertion | JWT |
| **Validation** | XML Signature | JWT Signature |
| **Mobile/API** | Poor | Excellent |
| **Complexity** | Higher | Lower |

## Common Interview Questions

**Q: Where is the SAML assertion sent?**
→ To ACS URL via HTTP POST

**Q: Can SAML be used without browser?**
→ No (practically)

**Q: What happens if SAML assertion is stolen?**
→ Limited impact due to short expiry, audience restriction, signature validation, and TLS prevents interception

**Q: Why do enterprises still use SAML?**
→ Legacy systems, existing IdP setups, compliance requirements, vendor lock-ins

**Q: Can you implement multi-tenant SSO with SAML?**
→ Yes. Typically by mapping tenant → IdP, tenant-specific metadata, tenant-specific Entity IDs

## Best Practices

- ✅ Use tenant-specific ACS URLs
- ✅ Provide metadata URL
- ✅ Keep Entity ID immutable
- ✅ Log assertion failures clearly
- ✅ Keep ACS stateless
- ✅ Rotate certificates regularly

## When to Use

- ✅ Legacy enterprise systems
- ✅ Existing SAML IdP setups
- ✅ Compliance requirements
- ✅ Corporate SSO
- ❌ New implementations (prefer OIDC)
- ❌ Mobile applications
- ❌ API-first architectures

## Related Topics

- **[SSO](./10-sso.md)** - Single Sign-On concept
- **[OIDC](./09-openid-connect.md)** - Modern alternative
- **[SLO](./14-slo.md)** - Single Logout

