# Secrets Management

**Never hardcode secrets. Most breaches involve exposed secrets.**

Secrets management is critical for protecting sensitive information like API keys, database passwords, certificates, and encryption keys.

## What Are Secrets?

- **API Keys** - Third-party service credentials
- **Database Passwords** - Database connection credentials
- **Certificates** - TLS/SSL certificates
- **Encryption Keys** - Data encryption keys
- **Tokens** - Access tokens, refresh tokens
- **Service Account Credentials** - Service-to-service authentication

## Best Practices

### ✅ Do's
- **Never hardcode** secrets in code
- **Use central vault** (AWS KMS, HashiCorp Vault, Azure Key Vault)
- **Short-lived secrets** - Rotate frequently
- **Automatic rotation** - Automate secret rotation
- **Encrypt at rest** - Encrypt secrets in storage
- **Audit access** - Log all secret access
- **Least privilege** - Grant minimum access needed

### ❌ Don'ts
- **Never commit secrets to Git** - Use .gitignore
- **Don't share secrets** via email or chat
- **Don't log secrets** - Mask in logs
- **Don't use default secrets** - Change defaults immediately
- **Don't store in environment variables** - Use secret management tools

## 🚩 Red Flags

**Secrets in Git:**
- Committed API keys
- Hardcoded passwords
- Exposed credentials in repositories
- **Solution:** Use secret scanning tools, rotate exposed secrets immediately

## Secret Management Solutions

### Cloud Providers
- **AWS:** Secrets Manager, KMS, Parameter Store
- **Azure:** Key Vault, Managed Identities
- **GCP:** Secret Manager, Cloud KMS

### Open Source
- **HashiCorp Vault** - Comprehensive secrets management
- **Sealed Secrets** - Kubernetes-native secrets
- **SOPS** - Secrets OPerationS (encrypted files)

### CI/CD Integration
- **GitHub Secrets** - Repository secrets
- **GitLab CI/CD Variables** - Protected variables
- **Jenkins Credentials** - Credential management

## Secret Lifecycle

```
Create → Store → Access → Rotate → Revoke
```

### 1. Create
- Generate strong secrets
- Use cryptographically secure random generators
- Set expiration dates

### 2. Store
- Encrypt at rest
- Use secure vault
- Implement access controls

### 3. Access
- Audit all access
- Use least privilege
- Monitor access patterns

### 4. Rotate
- Regular rotation schedule
- Automatic rotation when possible
- Zero-downtime rotation

### 5. Revoke
- Immediate revocation on compromise
- Clean up unused secrets
- Document revocation process

## Secret Types

### Static Secrets
- Database passwords
- API keys
- Certificates
- **Rotation:** Manual or scheduled

### Dynamic Secrets
- Temporary credentials
- Short-lived tokens
- **Rotation:** Automatic, on-demand

## Implementation Patterns

### Application Integration
```python
# Bad: Hardcoded secret
api_key = "sk_live_1234567890"

# Good: Retrieve from vault
api_key = vault.get_secret("api/stripe/key")
```

### Environment Variables (Limited Use)
```bash
# Only for local development
export DB_PASSWORD=$(vault read -field=password db/creds)
```

### Secret Injection
- Kubernetes Secrets
- Environment variable injection
- Volume mounts
- Init containers

## Security Considerations

### Encryption
- Encrypt secrets at rest
- Encrypt secrets in transit
- Use strong encryption algorithms

### Access Control
- Role-based access
- Audit logs
- Time-bound access
- IP restrictions

### Monitoring
- Monitor secret access
- Alert on unusual patterns
- Track secret usage
- Detect exposed secrets

## Incident Response

If secrets are exposed:
1. **Rotate immediately** - Change all exposed secrets
2. **Revoke access** - Invalidate compromised credentials
3. **Investigate** - Determine scope of exposure
4. **Notify** - Inform affected parties
5. **Document** - Record incident and remediation

## Related Topics

- **[IAM](../01-iam/)** - Identity and access management
- **[Application Security](../04-application-security/)** - Secure secret handling in code
- **[Compliance](../07-compliance-governance-risk/)** - Compliance requirements for secrets

