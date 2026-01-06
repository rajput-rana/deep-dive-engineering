# Hashing

**What it is:** One-way function that converts data of any length into fixed-length output.

**Key distinction:** Hashing is **irreversible** - you cannot get the original data back.

## Hashing vs Encryption

| Aspect | Encryption | Hashing |
|--------|------------|---------|
| **Reversible** | ✅ Yes | ❌ No |
| **Needs Key** | ✅ Yes | ❌ No |
| **Purpose** | Protect data | Verify data |
| **Use Case** | Confidentiality | Integrity, passwords |

## Cryptographic Hash Properties

### Core Properties (Interview Critical)

| Property | Meaning |
|----------|---------|
| **Preimage Resistance** | Can't find input from hash |
| **Second Preimage Resistance** | Can't find another input with same hash |
| **Collision Resistance** | Can't find two inputs with same hash |

### Hash Characteristics

- **Fixed-length output** - Same size regardless of input
- **One-way** - Cannot reverse
- **Avalanche effect** - Small change → huge output change

**Example:**
```
hash("hello") → 2cf24dba5...
hash("Hello") → 185f8db322...
```

## Hashing Algorithms

### MD5 ❌ (Broken)

**Basics:**
- Output: 128-bit
- Very fast

**Why it's broken:**
- Collisions are trivial
- Same hash can be generated for different inputs

📌 **Never use MD5 for security**

✅ Still okay for non-security checksums (rare)

### SHA-1 ❌ (Broken)

**Basics:**
- Output: 160-bit
- Stronger than MD5

**Why it's broken:**
- Practical collision attacks exist (Google SHAttered)

📌 **Deprecated everywhere**

### SHA-256 ✅ (Most Common)

**Basics:**
- Part of SHA-2 family
- Output: 256-bit
- Secure

**Where it's used:**
- TLS certificates
- Blockchain
- File integrity
- Digital signatures
- Password hashing (with salt + stretching)

**Why it's trusted:**
- No known collisions
- Computationally infeasible to break

### SHA-512

**Basics:**
- 512-bit output
- Faster on 64-bit CPUs
- Used in high-security contexts

## Password Hashing (Special Case)

### ❌ Don't Do This

```python
password_hash = SHA256(password)
```

**Why?**
- Too fast
- Vulnerable to GPU attacks
- No salt
- No key stretching

### ✅ Correct Password Hashing

**Use slow, salted KDFs (Key Derivation Functions):**

**bcrypt**
- Designed for passwords
- Slow by design
- Salted automatically

**Argon2** (Best)
- Winner of Password Hashing Competition
- Resistant to GPU attacks
- Configurable memory/time costs

**PBKDF2**
- Older standard
- Still secure
- Used in many systems

**Example:**
```python
hash = Argon2(password + salt)
```

### Why Passwords Should Be Hashed, Not Encrypted

**Encryption:**
- Reversible
- Needs key
- If key leaked → all passwords exposed

**Hashing:**
- Irreversible
- No key needed
- Only need to verify match

📌 **Passwords should never be encrypted, only hashed** - we don't need to know what the password is, only if it matches.

## MAC, HMAC & Authenticated Encryption

### MAC (Message Authentication Code)

**Ensures:**
- Data integrity
- Authenticity

**Use when:** You need to verify data hasn't been tampered with

### HMAC

**What it is:** Hash + secret key

**Formula:** `HMAC(key, message)`

**Used when:**
- You don't encrypt
- You only verify integrity
- API authentication
- Webhook signatures

### Authenticated Encryption (Best Practice)

**What it is:** Encryption + integrity in one step

**Use:**
- AES-GCM
- ChaCha20-Poly1305

**Avoid:**
- DIY combinations
- AES-CBC without MAC

## Common Use Cases

### 1. Password Storage
- Use: bcrypt, Argon2, PBKDF2
- Never: MD5, SHA-256 directly

### 2. File Integrity
- Use: SHA-256
- Verify: Downloads, backups

### 3. Digital Signatures
- Use: SHA-256 + RSA/ECC
- Verify: Certificates, code signing

### 4. API Authentication
- Use: HMAC-SHA256
- Verify: Webhook signatures, API keys

### 5. Blockchain
- Use: SHA-256
- Purpose: Block hashing, proof of work

## Best Practices

- ✅ Use SHA-256 for general hashing
- ✅ Use Argon2/bcrypt for passwords
- ✅ Always use salt for passwords
- ✅ Use HMAC for integrity verification
- ✅ Use authenticated encryption (AES-GCM)
- ❌ Never use MD5 or SHA-1
- ❌ Never hash passwords with raw SHA-256
- ❌ Never skip salt for passwords

## Common Interview Questions

**Q: Why not use SHA-256 directly for passwords?**
- Too fast → vulnerable to brute force
- No salt → vulnerable to rainbow tables
- Use Argon2/bcrypt instead

**Q: What's the difference between hashing and encryption?**
- Hashing: One-way, irreversible, no key
- Encryption: Two-way, reversible, needs key

**Q: When would you use HMAC?**
- API authentication
- Webhook signatures
- Integrity verification without encryption

## Algorithms Cheat Sheet

| Purpose | Algorithm |
|---------|-----------|
| **General Hashing** | SHA-256 |
| **Password Hashing** | Argon2 (best), bcrypt, PBKDF2 |
| **HMAC** | HMAC-SHA256 |
| **File Integrity** | SHA-256 |
| **Digital Signatures** | SHA-256 + RSA/ECC |

## Related Topics

- **[Encryption at Rest](./02-encryption-at-rest.md)** - Protecting stored data
- **[Encryption in Transit](./03-encryption-in-transit.md)** - Protecting data in transit
- **[Password Security](../01-iam/01-authentication/02-username-password.md)** - Password best practices

