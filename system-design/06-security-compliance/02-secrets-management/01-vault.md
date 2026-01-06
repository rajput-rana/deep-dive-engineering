# 🔐 HashiCorp Vault - Expert Guide

<div align="center">

**Master Vault: secrets management, encryption, and dynamic credentials**

[![Vault](https://img.shields.io/badge/Vault-Secrets-blue?style=for-the-badge)](./)
[![Dynamic](https://img.shields.io/badge/Dynamic-Credentials-green?style=for-the-badge)](./)
[![Encryption](https://img.shields.io/badge/Encryption-As%20a%20Service-orange?style=for-the-badge)](./)

*Comprehensive guide to HashiCorp Vault: architecture, secrets engines, and best practices*

</div>

---

## 🎯 Vault Fundamentals

<div align="center">

### What is HashiCorp Vault?

**HashiCorp Vault is a secrets management tool that secures, stores, and tightly controls access to tokens, passwords, certificates, API keys, and other secrets.**

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **🔐 Secrets Management** | Centralized secrets storage |
| **🔄 Dynamic Secrets** | Short-lived, on-demand credentials |
| **🔒 Encryption as a Service** | Encrypt/decrypt data |
| **📊 Audit Logging** | Complete audit trail |
| **🌐 Multi-Cloud** | Works across cloud providers |

**Mental Model:** Think of Vault like a highly secure bank vault - it stores your secrets (passwords, keys, certificates), provides controlled access, generates new credentials on demand, and keeps a complete audit log of who accessed what and when.

</div>

---

## 📚 Core Concepts

<div align="center">

### Q1: What is HashiCorp Vault and why is it used?

**A:** HashiCorp Vault is a secrets management platform that provides secure storage, dynamic secret generation, encryption services, and comprehensive audit logging.

**Why Use Vault:**

1. **Centralized Secrets:** Single source of truth for secrets
2. **Dynamic Secrets:** Generate short-lived credentials
3. **Encryption:** Encrypt/decrypt data without storing keys
4. **Access Control:** Fine-grained access policies
5. **Audit Trail:** Complete audit logging
6. **Rotation:** Automatic secret rotation

**Key Benefits:**
- ✅ Secure secrets storage
- ✅ Dynamic credential generation
- ✅ Encryption as a service
- ✅ Access control and policies
- ✅ Complete audit trail
- ✅ Secret rotation

---

### Q2: What are the core concepts of Vault?

**A:**

**Core Concepts:**

1. **Secrets Engines:**
   - Storage backends for secrets
   - Examples: KV, AWS, Database, PKI

2. **Auth Methods:**
   - How users/apps authenticate
   - Examples: Token, AppRole, AWS, Kubernetes

3. **Policies:**
   - Define access permissions
   - HCL or JSON format

4. **Tokens:**
   - Authentication tokens
   - Root token, service tokens

5. **Leases:**
   - Time-bound access
   - Automatic revocation

**Architecture:**
```
Client → Auth Method → Token → Policy → Secrets Engine → Secret
```

---

### Q3: What are Vault secrets engines?

**A:**

**Secrets Engines:**

| Engine | Purpose | Use Case |
|:---:|:---:|:---:|
| **KV (Key-Value)** | Static secrets storage | API keys, passwords |
| **AWS** | Dynamic AWS credentials | Temporary AWS access |
| **Database** | Dynamic DB credentials | Short-lived DB passwords |
| **PKI** | Certificate management | TLS certificates |
| **Transit** | Encryption as a service | Encrypt/decrypt data |
| **Consul** | Consul secrets | Consul tokens |
| **SSH** | SSH key signing | SSH access |

**KV Engine Example:**
```bash
# Enable KV engine
vault secrets enable -path=secret kv-v2

# Write secret
vault kv put secret/app/api-key key=abc123

# Read secret
vault kv get secret/app/api-key
```

**Database Engine Example:**
```bash
# Enable database engine
vault secrets enable database

# Configure database
vault write database/config/postgresql \
  plugin_name=postgresql-database-plugin \
  connection_url="postgresql://{{username}}:{{password}}@localhost:5432/mydb" \
  allowed_roles="readonly"

# Create role
vault write database/roles/readonly \
  db_name=postgresql \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';" \
  default_ttl=1h \
  max_ttl=24h

# Generate dynamic credentials
vault read database/creds/readonly
```

---

### Q4: What are Vault authentication methods?

**A:**

**Auth Methods:**

| Method | Use Case | Description |
|:---:|:---:|:---:|
| **Token** | Initial setup | Root/service tokens |
| **AppRole** | Applications | Role-based auth |
| **AWS** | AWS resources | IAM-based auth |
| **Kubernetes** | K8s pods | Service account auth |
| **LDAP** | Enterprise | LDAP integration |
| **OIDC** | SSO | OpenID Connect |
| **GitHub** | CI/CD | GitHub tokens |

**AppRole Example:**
```bash
# Enable AppRole
vault auth enable approle

# Create role
vault write auth/approle/role/myapp \
  token_policies="myapp-policy" \
  token_ttl=1h \
  token_max_ttl=4h

# Get role ID
vault read auth/approle/role/myapp/role-id

# Get secret ID
vault write -f auth/approle/role/myapp/secret-id

# Login
vault write auth/approle/login \
  role_id=<role-id> \
  secret_id=<secret-id>
```

---

### Q5: What are Vault policies?

**A:**

**Policies:**

- Define what users/apps can access
- Written in HCL (HashiCorp Configuration Language)
- Attached to tokens or auth methods

**Policy Example:**
```hcl
# myapp-policy.hcl
path "secret/data/myapp/*" {
  capabilities = ["read"]
}

path "database/creds/readonly" {
  capabilities = ["read"]
}

path "transit/encrypt/myapp" {
  capabilities = ["update"]
}
```

**Apply Policy:**
```bash
# Write policy
vault policy write myapp-policy myapp-policy.hcl

# Attach to token
vault token create -policy=myapp-policy
```

**Capabilities:**
- `create` - Create new resources
- `read` - Read data
- `update` - Update data
- `delete` - Delete data
- `list` - List paths
- `sudo` - Root-level access

---

### Q6: What are dynamic secrets in Vault?

**A:**

**Dynamic Secrets:**

- Generated on-demand
- Short-lived (TTL)
- Automatically revoked
- Never stored in Vault

**Benefits:**
- ✅ No long-lived credentials
- ✅ Automatic rotation
- ✅ Reduced attack surface
- ✅ Audit trail

**Example - AWS Dynamic Secrets:**
```bash
# Enable AWS secrets engine
vault secrets enable aws

# Configure AWS
vault write aws/config/root \
  access_key=AKIA... \
  secret_key=...

# Create role
vault write aws/roles/s3-readonly \
  credential_type=iam_user \
  policy_document=-<<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject"],
    "Resource": ["arn:aws:s3:::mybucket/*"]
  }]
}
EOF

# Generate dynamic credentials
vault read aws/creds/s3-readonly
# Returns: access_key, secret_key (valid for TTL)
```

---

### Q7: What is Vault Transit engine?

**A:**

**Transit Engine:**

- Encryption as a service
- Encrypt/decrypt without storing keys
- Key rotation support
- Multiple algorithms

**Use Cases:**
- Encrypt application data
- Encrypt database fields
- Key rotation
- Encryption at rest

**Example:**
```bash
# Enable transit
vault secrets enable transit

# Create encryption key
vault write -f transit/keys/myapp-key

# Encrypt data
vault write transit/encrypt/myapp-key plaintext=$(echo "sensitive-data" | base64)

# Decrypt data
vault write transit/decrypt/myapp-key ciphertext="vault:v1:..."

# Rotate key
vault write -f transit/keys/myapp-key/rotate
```

**Application Integration:**
```python
import hvac

client = hvac.Client(url='http://vault:8200')
client.token = 'my-token'

# Encrypt
encrypt_response = client.secrets.transit.encrypt_data(
    name='myapp-key',
    plaintext='sensitive-data'
)
ciphertext = encrypt_response['data']['ciphertext']

# Decrypt
decrypt_response = client.secrets.transit.decrypt_data(
    name='myapp-key',
    ciphertext=ciphertext
)
plaintext = decrypt_response['data']['plaintext']
```

---

### Q8: What is Vault PKI engine?

**A:**

**PKI Engine:**

- Certificate management
- Generate TLS certificates
- Certificate signing
- Automatic rotation

**Example:**
```bash
# Enable PKI
vault secrets enable pki

# Set CA certificate
vault write pki/root/generate/internal \
  common_name="example.com" \
  ttl=87600h

# Configure URLs
vault write pki/config/urls \
  issuing_certificates="http://vault:8200/v1/pki/ca" \
  crl_distribution_points="http://vault:8200/v1/pki/crl"

# Create role
vault write pki/roles/example-dot-com \
  allowed_domains="example.com" \
  allow_subdomains=true \
  max_ttl="720h"

# Generate certificate
vault write pki/issue/example-dot-com \
  common_name="app.example.com" \
  ttl="24h"
```

---

### Q9: How does Vault handle secret rotation?

**A:**

**Rotation Strategies:**

1. **Manual Rotation:**
   - Update secrets manually
   - Use `vault kv put`

2. **Automatic Rotation:**
   - Dynamic secrets (auto-rotated)
   - Transit keys (rotate command)

3. **Database Rotation:**
   - Rotate root credentials
   - Update connection strings

**Database Rotation Example:**
```bash
# Rotate root credentials
vault write -force database/rotate-root/postgresql

# New credentials generated automatically
# Old credentials revoked
```

**Transit Key Rotation:**
```bash
# Rotate encryption key
vault write -f transit/keys/myapp-key/rotate

# Old key still works for decryption
# New key used for encryption
```

---

### Q10: What is Vault unsealing?

**A:**

**Vault Sealing:**

- Vault starts sealed (encrypted)
- Cannot read/write secrets when sealed
- Requires unseal keys to unseal

**Unseal Process:**

1. **Initialization:**
   - Generate unseal keys
   - Generate root token

2. **Unsealing:**
   - Provide unseal keys (threshold)
   - Vault becomes operational

**Example:**
```bash
# Initialize Vault
vault operator init -key-shares=5 -key-threshold=3

# Unseal (need 3 of 5 keys)
vault operator unseal <key1>
vault operator unseal <key2>
vault operator unseal <key3>

# Vault is now unsealed
```

**Auto-Unseal:**
- Use cloud KMS (AWS KMS, Azure Key Vault)
- Automatic unsealing
- No manual key entry

---

### Q11: What is Vault HA (High Availability)?

**A:**

**HA Configuration:**

- Multiple Vault nodes
- Shared storage backend
- Active/standby mode
- Automatic failover

**Storage Backends:**
- Consul
- etcd
- DynamoDB
- PostgreSQL
- Cloud storage

**Example - Consul Backend:**
```hcl
storage "consul" {
  address = "127.0.0.1:8500"
  path    = "vault/"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_cert_file = "/path/to/cert.pem"
  tls_key_file  = "/path/to/key.pem"
}

api_addr = "https://vault.example.com:8200"
cluster_addr = "https://vault.example.com:8201"
```

---

### Q12: What are Vault best practices?

**A:**

**Best Practices:**

1. **Never Use Root Token:**
   - Create service tokens
   - Use auth methods
   - Rotate root token

2. **Use Policies:**
   - Least privilege
   - Separate policies per app
   - Regular policy reviews

3. **Enable Audit Logging:**
   - Log all operations
   - Secure audit logs
   - Monitor access

4. **Use Dynamic Secrets:**
   - Prefer dynamic over static
   - Short TTLs
   - Automatic rotation

5. **Secure Storage:**
   - Encrypt storage backend
   - Use TLS
   - Network isolation

6. **Monitor Vault:**
   - Health checks
   - Metrics
   - Alerts

**Example - Secure Setup:**
```bash
# Disable root token
vault token revoke -self

# Create admin policy
vault policy write admin admin-policy.hcl

# Create admin token
vault token create -policy=admin -ttl=1h

# Enable audit logging
vault audit enable file file_path=/var/log/vault_audit.log
```

---

### Q13: How to integrate Vault with applications?

**A:**

**Integration Methods:**

1. **Vault Agent:**
   - Sidecar container
   - Auto-authentication
   - Secret injection

2. **Vault SDK:**
   - Application libraries
   - Direct API calls
   - Token management

3. **Environment Variables:**
   - Inject secrets
   - Startup scripts
   - Init containers

**Vault Agent Example:**
```hcl
# agent.hcl
pid_file = "/tmp/vault-agent.pid"

vault {
  address = "http://vault:8200"
}

auto_auth {
  method "kubernetes" {
    mount_path = "auth/kubernetes"
    config = {
      role = "myapp"
    }
  }
  sink "file" {
    config = {
      path = "/tmp/vault-token"
    }
  }
}

template {
  source      = "/etc/secrets/api-key.ctmpl"
  destination = "/etc/secrets/api-key"
}
```

**Application Integration:**
```python
import hvac
import os

# Initialize client
client = hvac.Client(url=os.getenv('VAULT_ADDR'))
client.token = open('/tmp/vault-token').read()

# Read secret
secret = client.secrets.kv.v2.read_secret_version(path='myapp/api-key')
api_key = secret['data']['data']['key']

# Use secret
use_api_key(api_key)
```

---

### Q14: What is Vault performance tuning?

**A:**

**Performance Optimization:**

1. **Caching:**
   - Enable response caching
   - Reduce API calls
   - Faster responses

2. **Connection Pooling:**
   - Reuse connections
   - Reduce overhead

3. **Batch Operations:**
   - Batch secret reads
   - Reduce round trips

4. **Storage Backend:**
   - Choose fast backend
   - Optimize storage

**Enable Caching:**
```hcl
cache {
  use_auto_auth_token = true
}

listener "tcp" {
  address = "127.0.0.1:8200"
  tls_disable = true
}
```

---

### Q15: What are Vault security considerations?

**A:**

**Security Best Practices:**

1. **Network Security:**
   - Use TLS
   - Network isolation
   - Firewall rules

2. **Access Control:**
   - Least privilege
   - Regular audits
   - Policy reviews

3. **Audit Logging:**
   - Enable audit logs
   - Secure logs
   - Monitor access

4. **Secret Management:**
   - Use dynamic secrets
   - Rotate regularly
   - Monitor usage

5. **High Availability:**
   - HA setup
   - Backup strategy
   - Disaster recovery

**Security Checklist:**
- ✅ TLS enabled
- ✅ Root token secured
- ✅ Audit logging enabled
- ✅ Policies configured
- ✅ Dynamic secrets used
- ✅ Regular backups
- ✅ Monitoring enabled

---

## 🎯 Advanced Topics

<div align="center">

### Vault Patterns

**Secrets Patterns:**
- Static secrets (KV)
- Dynamic secrets (AWS, Database)
- Encryption as a service (Transit)

**Authentication Patterns:**
- AppRole for applications
- Kubernetes for pods
- AWS IAM for EC2

**Deployment Patterns:**
- Standalone
- HA with Consul
- Cloud-managed (Vault Cloud)

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **Vault Purpose** | Centralized secrets management |
| **Dynamic Secrets** | Short-lived, on-demand credentials |
| **Secrets Engines** | KV, AWS, Database, PKI, Transit |
| **Auth Methods** | Token, AppRole, Kubernetes, AWS |
| **Policies** | Define access permissions |

**💡 Remember:** Vault provides centralized secrets management with dynamic credentials, encryption services, and comprehensive audit logging. Use dynamic secrets when possible, implement least privilege policies, and enable audit logging for security.

</div>

---

<div align="center">

**Master Vault for secure secrets management! 🚀**

*From architecture to implementation - comprehensive guide to HashiCorp Vault.*

</div>

