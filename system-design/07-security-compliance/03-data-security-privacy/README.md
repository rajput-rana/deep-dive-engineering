# Data Security & Privacy

Protecting data throughout its lifecycle: classification, encryption, tokenization, masking, and privacy compliance.

## Data Lifecycle

```
Create → Store → Use → Share → Archive → Delete
```

## Table of Contents

### Data Classification
- **[01. Data Classification](./01-data-classification.md)** - PII, PHI, PCI classification

### Encryption & Hashing
- **[02. Encryption at Rest](./02-encryption-at-rest.md)** - Database encryption, disk encryption, application-level encryption
- **[03. Encryption in Transit](./03-encryption-in-transit.md)** - TLS/SSL, HTTPS, mTLS
- **[04. Hashing](./04-hashing.md)** - Cryptographic hashing, password hashing, HMAC
- **[05. Encryption Fundamentals](./05-encryption-fundamentals.md)** - Symmetric vs asymmetric, algorithms, key management

### Data Protection
- **[06. Tokenization](./06-tokenization.md)** - Tokenizing sensitive data
- **[07. Data Masking](./07-data-masking.md)** - Masking data for non-production

### Privacy
- **[08. GDPR Compliance](./08-gdpr-compliance.md)** - General Data Protection Regulation
- **[09. Data Residency](./09-data-residency.md)** - Geographic data storage requirements
- **[10. Consent Management](./10-consent-management.md)** - User consent tracking

## Data Classification

### PII (Personal Identifiable Information)
- Names, addresses, phone numbers
- Email addresses, SSNs
- **Protection:** Encryption, access controls

### PHI (Protected Health Information)
- Medical records, health information
- **Regulation:** HIPAA
- **Protection:** Strict access controls, encryption

### PCI (Payment Card Industry)
- Credit card numbers, CVV
- **Regulation:** PCI DSS
- **Protection:** Tokenization, encryption

## Encryption Strategies

### Encryption at Rest
- Database encryption (TDE, column-level)
- File system encryption
- Object storage encryption
- **Key Management:** Centralized key management

### Encryption in Transit
- TLS/SSL for network communication
- HTTPS for web traffic
- VPN for remote access
- **Best Practice:** TLS 1.2+ only

## Data Protection Techniques

### Tokenization
- Replace sensitive data with tokens
- Tokens are meaningless without mapping
- **Use Cases:** Payment processing, PII protection

### Data Masking
- Hide sensitive data in non-production
- Preserve data format
- **Use Cases:** Development, testing, analytics

### Secure Deletion
- Cryptographic erasure
- Multiple overwrites
- **Compliance:** GDPR right to be forgotten

## Privacy Regulations

### GDPR (General Data Protection Regulation)
- **Right to be forgotten** - Data deletion
- **Right to access** - Data portability
- **Consent management** - Explicit consent
- **Data breach notification** - 72-hour notification

### HIPAA (Health Insurance Portability and Accountability Act)
- Protected health information
- Minimum necessary standard
- Access controls and audit logs

### PCI DSS (Payment Card Industry Data Security Standard)
- Payment card data protection
- Network segmentation
- Regular security assessments

## Data Retention Policies

- Define retention periods by data type
- Automatic deletion after retention
- Archive old data securely
- Compliance with regulations

## Best Practices

### Data Classification
- ✅ Classify all data
- ✅ Label sensitive data
- ✅ Apply appropriate controls
- ✅ Regular classification reviews

### Encryption
- ✅ Encrypt sensitive data at rest
- ✅ Use TLS for all data in transit
- ✅ Manage encryption keys securely
- ✅ Use strong encryption algorithms

### Access Control
- ✅ Least privilege access
- ✅ Regular access reviews
- ✅ Audit data access
- ✅ Monitor data usage

### Privacy
- ✅ Implement consent management
- ✅ Respect user privacy rights
- ✅ Data minimization
- ✅ Purpose limitation

## Related Topics

- **[IAM](../01-iam/)** - Access control for data
- **[Secrets Management](../02-secrets-management/)** - Encryption key management
- **[Compliance](../07-compliance-governance-risk/)** - Regulatory compliance

