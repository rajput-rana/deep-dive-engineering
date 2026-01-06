# Encryption in Transit

**What it is:** Protects data while moving between systems.

**Goal:** Prevent MITM attacks, sniffing, and data interception.

## TLS (Transport Layer Security)

**This is the standard** for encryption in transit.

**Used in:**
- HTTPS
- gRPC
- Kafka
- Database connections
- Service-to-service communication

## How TLS Works (Simplified)

```
1. Client connects to server
   ↓
2. Server sends certificate (public key)
   ↓
3. Client verifies CA
   ↓
4. Key exchange (RSA / ECDHE)
   ↓
5. Session key created
   ↓
6. Data encrypted using symmetric AES
```

**Key Point:** TLS uses asymmetric for handshake, symmetric for data.

## TLS Variants

| Use Case | Protocol |
|----------|----------|
| Browser ↔ Server | HTTPS (TLS) |
| Service ↔ Service | mTLS |
| DB connections | TLS |
| Kafka | TLS |
| gRPC | TLS |

## Mutual TLS (mTLS)

**What it is:** Both client and server authenticate each other using certificates.

**Used in:**
- Zero Trust architectures
- Kubernetes
- Internal microservices
- High-security environments

**How it works:**
- Client presents certificate
- Server presents certificate
- Both verify each other
- Strong identity + encryption

**Benefits:**
- ✅ Strong authentication
- ✅ Encrypted communication
- ✅ Service identity verification

## TLS Algorithms

### Handshake (Asymmetric)
- **RSA** - Older, widely used
- **ECC (ECDHE)** - Preferred today (smaller keys, faster)

### Data Encryption (Symmetric)
- **AES-GCM** - Standard (encryption + integrity)
- **ChaCha20-Poly1305** - Alternative (faster on mobile)

### Hashing
- **SHA-256** - Certificate signatures, integrity

## Encryption in Transit by System

### Kafka

**Option 1: TLS**
- Encrypts producer ↔ broker ↔ consumer
- Uses standard TLS
- Protects against MITM, sniffing

**Option 2: mTLS**
- Client + broker both authenticate
- Common in enterprise clusters

### Databases (RDS)

**TLS between app ↔ DB**
- Mandatory in regulated setups
- Prevents interception
- Certificate-based authentication

### Redis

**TLS supported** (modern Redis)
- Or via stunnel / proxy
- App --TLS--> Redis

### Logs

**Encryption in Transit:**
- TLS to log collectors
- HTTPS / mTLS
- Prevents log interception

## Best Practices

- ✅ Use TLS 1.2+ only
- ✅ Prefer ECDHE for key exchange
- ✅ Use AES-GCM for data encryption
- ✅ Implement mTLS for service-to-service
- ✅ Validate certificates properly
- ✅ Monitor TLS connections
- ❌ Never use TLS 1.0 or 1.1
- ❌ Never skip certificate validation

## Common Interview Questions

**Q: How do you encrypt microservice traffic?**
- mTLS
- Short-lived certs
- Service identity

**Q: Why use mTLS instead of TLS?**
- Both sides authenticate
- Stronger security
- Zero Trust architecture

**Q: What's the difference between TLS and HTTPS?**
- HTTPS = HTTP over TLS
- TLS is the protocol
- HTTPS is the application

## Encryption at Rest vs In Transit

| Aspect | At Rest | In Transit |
|--------|---------|------------|
| **Goal** | Protect stored data | Protect moving data |
| **Common Algo** | AES-256-GCM | TLS (AES + RSA/ECC) |
| **Managed by** | Disk / DB / App | Network stack |
| **Threat** | Disk theft, DB access | MITM, sniffing |

## Related Topics

- **[Encryption at Rest](./02-encryption-at-rest.md)** - Protecting stored data
- **[mTLS](../01-iam/03-service-identity/01-mtls.md)** - Mutual TLS for services
- **[TLS/HTTPS](../04-communication-protocols/)** - Transport security

