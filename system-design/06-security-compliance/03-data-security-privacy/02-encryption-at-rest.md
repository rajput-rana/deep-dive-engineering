# Encryption at Rest

**What it is:** Protects data when stored on disks, databases, backups, object storage, and logs.

**Goal:** Confidentiality - ensure stored data cannot be read without proper keys.

## Where Data Lives

- **Disks** - Server storage
- **Databases** - Data files, backups
- **Backups** - Snapshots, archives
- **Object Storage** - S3, Azure Blob, GCP Storage
- **Logs** - Application logs, audit logs

## Common Ways to Encrypt at Rest

### 1. Full Disk Encryption (FDE)

Encrypts entire disk.

**Examples:**
- Linux LUKS
- BitLocker
- Cloud-managed disk encryption (EBS, Azure Disk)

**Pros:**
- ✅ Easy to implement
- ✅ Transparent to applications

**Cons:**
- ❌ No per-table or per-user control
- ❌ DB admins can still access decrypted data

### 2. File-Level Encryption

Encrypt specific files.

**Examples:**
- Encrypted file systems
- Application-level encryption

### 3. Database Encryption

#### a) Transparent Data Encryption (TDE)

Database automatically encrypts data files.

**Examples:**
- MySQL TDE
- PostgreSQL TDE (via extensions)
- Oracle TDE
- SQL Server TDE

**Pros:**
- ✅ Simple
- ✅ Transparent to applications

**Cons:**
- ❌ DB admins can still access decrypted data
- ❌ No fine-grained control

#### b) Column-Level Encryption

Only sensitive columns encrypted.

**Example:**
```
credit_card → encrypted
name → plaintext
```

**Pros:**
- ✅ Fine-grained control
- ✅ Only sensitive data encrypted

**Cons:**
- ❌ Querying & indexing harder
- ❌ More complex implementation

### 4. Application-Level Encryption (Most Secure)

App encrypts before storing data.

**Flow:** `App → encrypt → DB`

**Pros:**
- ✅ DB never sees plaintext
- ✅ Maximum security
- ✅ Fine-grained control

**Cons:**
- ❌ Key management complexity
- ❌ Harder debugging & search

**Use Cases:** PII, secrets, identity data

## Encryption Algorithms for At Rest

### Symmetric Encryption (Standard)

**AES-256-GCM** (Recommended)
- Industry standard
- Authenticated encryption (encryption + integrity)
- Fast and secure

**AES-256-CBC**
- ⚠️ Needs MAC for integrity
- Use AES-GCM instead when possible

**ChaCha20-Poly1305**
- Alternative to AES
- Faster on mobile devices
- Secure AEAD

## Key Management

### Key Management Systems (KMS)

**Examples:**
- AWS KMS
- GCP KMS
- Azure Key Vault
- HashiCorp Vault

### Envelope Encryption (Industry Standard)

**How it works:**
```
Data → encrypted by Data Key
Data Key → encrypted by Master Key (KMS)
```

**Benefits:**
- ✅ Fast
- ✅ Secure
- ✅ Scalable

**Used by:**
- AWS S3
- DynamoDB
- RDS
- Kafka

### Key Rotation

- **Automatic** (preferred)
- **Manual**
- **Versioned keys**

📌 **Note:** Data usually not re-encrypted—only data keys are rotated.

## Real-World Examples

### S3 / Object Storage

**Three Encryption Modes:**

1. **SSE-S3** (Server-Side Encryption)
   - AWS manages keys
   - AES-256
   - Simple but less control

2. **SSE-KMS** (Recommended)
   - Keys stored in KMS
   - Audit, rotation, IAM control
   - Enterprise-grade

3. **Client-Side Encryption**
   - App encrypts before upload
   - Maximum security
   - Operational complexity

### Databases (RDS)

**Options:**
- **TDE** - Entire DB encrypted
- **Column-Level** - Only PII fields
- **Application-Level** - Encrypt before insert (best)

**Backups & Replicas:**
- Encrypted automatically if DB is encrypted
- Snapshot encryption uses same KMS key

### Kafka

**Encryption Options:**

1. **Disk Encryption** (Most common)
   - EBS / persistent disk encryption
   - Managed by cloud provider
   - ✅ Easy
   - ❌ Broker admins can read plaintext

2. **Application-Level Encryption** (Best for PII)
   - Producer encrypts payload before sending
   - ✅ Kafka sees ciphertext only
   - ❌ Harder debugging & search

### Redis

**Encryption Options:**

1. **Disk Encryption** - Encrypt RDB/AOF via disk encryption
2. **Application-Level Encryption** - Encrypt sensitive values before caching

📌 **Note:** Redis itself does not encrypt values

**Best Practices:**
- Do not store plaintext secrets
- Prefer short TTLs
- Encrypt session tokens

### Logs (Often Missed ❗)

**Why logs are sensitive:**
- Tokens
- User IDs
- PII
- Stack traces

**Encryption:**
- Disk encryption
- Encrypted log storage (S3, ELK)

**Best Practices:**
- ✅ Mask sensitive fields
- ✅ Avoid logging secrets
- ✅ Encrypt logs at rest
- ✅ Restrict log access

## Best Practices

- ✅ Use AES-256-GCM for authenticated encryption
- ✅ Centralize keys in KMS
- ✅ Implement automatic key rotation
- ✅ Use envelope encryption for scalability
- ✅ Encrypt backups same as primary data
- ✅ Use application-level encryption for PII
- ❌ Never hardcode keys
- ❌ Never use ECB mode
- ❌ Never roll your own crypto

## Common Interview Questions

**Q: How do you encrypt user PII?**
- App-level AES-256
- Keys in KMS
- Column-level encryption
- Audit access

**Q: What happens if DB is breached?**
- Data is encrypted
- Keys not in DB
- Attacker gets ciphertext only

**Q: How do you handle key rotation?**
- Automatic rotation via KMS
- Versioned keys
- Data keys rotated, data not re-encrypted

## Related Topics

- **[Encryption in Transit](./03-encryption-in-transit.md)** - Protecting data during transfer
- **[Key Management](../../02-secrets-management/)** - Managing encryption keys
- **[Data Classification](./01-data-classification.md)** - Identifying sensitive data

