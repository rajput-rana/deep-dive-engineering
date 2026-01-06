# Encryption Fundamentals

**What it is:** Encryption converts plaintext → ciphertext using a key so that only authorized parties can read the data.

## Why We Encrypt

- ✅ **Confidentiality** (primary goal) - Protect data from unauthorized access
- ✅ **Integrity** - Detect tampering
- ✅ **Authentication** - Prove identity
- ✅ **Compliance** - GDPR, SOC2, HIPAA, PCI

## Three Dimensions of Encryption

Think in three dimensions for every component:

1. **Encryption in Transit** - TLS or mTLS
2. **Encryption at Rest** - Disk encryption, File encryption, DB encryption, column encryption
3. **Key Management** - KMS such as Vault

## Symmetric vs Asymmetric Encryption

### 🔹 Symmetric Encryption

**What it is:** Same key to encrypt and decrypt

**Characteristics:**
- Fast, efficient
- Used for data at rest and bulk data transfer

**Examples:**
- AES (Advanced Encryption Standard)
- ChaCha20

**Formula:** `plaintext + secret_key → ciphertext`

**Problem:** Key distribution

### 🔹 Asymmetric Encryption

**What it is:** Public key encrypts, private key decrypts

**Characteristics:**
- Slower, but solves key exchange
- Used mainly for key exchange, not bulk data

**Examples:**
- RSA
- ECC (Elliptic Curve Cryptography)

**Formula:** `plaintext + public_key → ciphertext`

📌 **Used mainly for key exchange, not bulk data**

## Symmetric Encryption Algorithms

### AES (Advanced Encryption Standard)

**Most important algorithm to know.**

| Key Size | Security |
|----------|----------|
| AES-128 | Secure |
| AES-256 | Standard |

### AES Modes (CRITICAL)

| Mode | Status |
|------|--------|
| **ECB** | ❌ Never |
| **CBC** | ⚠️ Needs MAC |
| **GCM** | ✅ Best |
| **CTR** | ⚠️ Needs MAC |

📌 **AES-GCM = encryption + integrity**

### ChaCha20-Poly1305

**Why it exists:**
- AES slow on devices without AES-NI
- Better for mobile

**Properties:**
- Stream cipher + MAC
- Secure AEAD
- Used in TLS, mobile apps

## Asymmetric Algorithms

### RSA

**Basics:**
- Public / Private key
- Key sizes: 2048+ bits

**Usage:**
- TLS handshakes
- Certificates
- Legacy systems

**Downsides:**
- Slow
- Large keys

### ECC (Elliptic Curve Cryptography)

**Why ECC is preferred:**

| Aspect | RSA | ECC |
|--------|-----|-----|
| **Key Size** | 2048-bit | 256-bit |
| **Speed** | Slow | Fast |
| **Security** | Same | Same |

**Used in:**
- Modern TLS
- Mobile
- Cloud-native systems

## Key Exchange

### Diffie-Hellman

**What it is:** Secure key exchange over insecure channel

**Modern:** ECDHE (TLS)

📌 **Enables perfect forward secrecy**

## Authenticated Encryption (IMPORTANT)

**What it is:** Encryption + integrity

**Use:**
- AES-GCM
- ChaCha20-Poly1305

**Avoid:**
- AES-CBC without MAC

## Cryptographic Design Patterns

### Problem → Tool Mapping

| Problem | Tool |
|--------|------|
| **Hide data** | Encryption |
| **Verify data hasn't changed** | Hash / MAC |
| **Prove identity / exchange keys** | Asymmetric crypto |

⚠️ **One algorithm never does everything well.**

## How This Maps to Real Systems

### TLS
- RSA/ECC → handshake
- ECDHE → key exchange
- AES-GCM → data encryption
- SHA-256 → hashing

### Databases
- AES-256 at rest
- TLS in transit

### Passwords
- Argon2 / bcrypt
- Never AES
- Never SHA-256 directly

## Enterprise Setup

**Typical Enterprise Setup:**

- ✅ TLS everywhere (internal + external)
- ✅ Disk encryption by default
- ✅ TDE for DB
- ✅ App-level encryption for PII
- ✅ KMS + envelope encryption
- ✅ mTLS for internal services

## Common Mistakes (Red Flags)

- ❌ Hardcoding keys
- ❌ Using ECB mode
- ❌ Rolling your own crypto
- ❌ No key rotation
- ❌ Encrypting passwords instead of hashing

## Algorithms Cheat Sheet

| Purpose | Algorithm |
|---------|-----------|
| **Symmetric Encryption** | AES-256-GCM (standard), ChaCha20-Poly1305 (mobile) |
| **Asymmetric** | RSA-2048+, ECC (preferred) |
| **Hashing** | SHA-256 |
| **Password Hashing** | bcrypt, Argon2, PBKDF2 |
| **Key Exchange** | ECDHE |

## Interview-Ready Summary

**"We encrypt data in transit using TLS/mTLS, and at rest using a combination of disk encryption, database TDE, and application-level AES-GCM encryption for sensitive data. Keys are centrally managed using KMS with envelope encryption and automatic rotation. Logs and backups are also encrypted and access controlled."**

## Related Topics

- **[Encryption at Rest](./02-encryption-at-rest.md)** - Protecting stored data
- **[Encryption in Transit](./03-encryption-in-transit.md)** - Protecting data in transit
- **[Hashing](./04-hashing.md)** - One-way data verification
- **[Key Management](../../02-secrets-management/)** - Managing encryption keys

