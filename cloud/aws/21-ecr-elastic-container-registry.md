# 📦 ECR - Elastic Container Registry

<div align="center">

**Fully managed Docker container registry: store, manage, and deploy container images**

[![ECR](https://img.shields.io/badge/ECR-Container%20Registry-blue?style=for-the-badge)](./)
[![Docker](https://img.shields.io/badge/Docker-Images-green?style=for-the-badge)](./)
[![Security](https://img.shields.io/badge/Security-Scanning-orange?style=for-the-badge)](./)

*Master ECR: store and manage Docker container images securely on AWS*

</div>

---

## 🎯 What is ECR?

<div align="center">

**Amazon ECR (Elastic Container Registry) is a fully managed Docker container registry that makes it easy to store, manage, and deploy Docker container images.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **📦 Repository** | Container for Docker images |
| **🖼️ Image** | Docker container image |
| **🏷️ Tag** | Image version identifier |
| **📋 Manifest** | Image metadata |
| **🔐 Registry** | Collection of repositories |
| **🔒 Lifecycle Policy** | Automatic image cleanup |

**Mental Model:** Think of ECR as Docker Hub on AWS - you push Docker images to repositories, tag them with versions, and pull them when deploying to ECS, EKS, or EC2.

</div>

---

## 🏗️ ECR Architecture

<div align="center">

### Core Components

| Component | Description | Purpose |
|:---:|:---:|:---:|
| **Registry** | Your ECR account | Container for all repositories |
| **Repository** | Container for images | Organize images by application |
| **Image** | Docker image | Container image |
| **Tag** | Image version | Version identifier |
| **Manifest** | Image metadata | Image configuration |

</div>

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    ECR Registry                         │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │           Repository: my-app                     │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐     │   │
│  │  │ Image    │  │ Image    │  │ Image    │     │   │
│  │  │ v1.0.0   │  │ v1.1.0   │  │ latest   │     │   │
│  │  └──────────┘  └──────────┘  └──────────┘     │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │           Repository: web-server                  │   │
│  │  ┌──────────┐  ┌──────────┐                     │   │
│  │  │ Image    │  │ Image    │                     │   │
│  │  │ v2.0.0   │  │ latest   │                     │   │
│  │  └──────────┘  └──────────┘                     │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  Push ←─────────── Docker Client ───────────→ Pull      │
│                                                          │
│  Integrates with: ECS, EKS, EC2, Lambda                │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Features

<div align="center">

**ECR capabilities**

| Feature | Description | Benefit |
|:---:|:---:|:---:|
| **Image Storage** | Store Docker images | Centralized registry |
| **Image Scanning** | Vulnerability scanning | Security |
| **Lifecycle Policies** | Automatic cleanup | Cost optimization |
| **IAM Integration** | Access control | Security |
| **Encryption** | At-rest encryption | Data protection |
| **Replication** | Cross-region replication | High availability |

</div>

### Image Scanning

<div align="center">

**Automated vulnerability scanning**

| Scan Type | Description |
|:---:|:---:|
| **Basic Scanning** | Free, common vulnerabilities |
| **Enhanced Scanning** | Comprehensive, CVE database |
| **On Push** | Automatic on image push |
| **Manual** | On-demand scanning |

</div>

**Scanning Features:**
- Detects vulnerabilities in images
- Uses Common Vulnerabilities and Exposures (CVE) database
- Provides severity ratings
- Generates scan reports
- Can block deployments based on findings

### Lifecycle Policies

<div align="center">

**Automated image management**

| Policy Rule | Description | Use Case |
|:---:|:---:|:---:|
| **Expire Untagged** | Delete untagged images | Cleanup old images |
| **Expire by Count** | Keep N most recent | Limit repository size |
| **Expire by Age** | Delete images older than X days | Archive old versions |

</div>

**Benefits:**
- Automatic cleanup
- Cost optimization
- Repository management
- Prevents storage bloat

---

## 📦 Repositories

### Repository Types

<div align="center">

**Different repository configurations**

| Type | Description | Use Case |
|:---:|:---:|:---:|
| **Private** | Accessible only to your account | Production images |
| **Public** | Publicly accessible | Open source images |
| **Encrypted** | Encryption at rest | Sensitive images |

</div>

### Creating Repositories

**Using AWS Console:**
1. Navigate to ECR
2. Click "Create repository"
3. Enter repository name
4. Configure settings (scanning, encryption)
5. Create repository

**Using AWS CLI:**
```bash
aws ecr create-repository \
  --repository-name my-app \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256
```

**Using Terraform:**
```hcl
resource "aws_ecr_repository" "my_app" {
  name                 = "my-app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}
```

---

## 🖼️ Image Management

### Pushing Images

<div align="center">

**Push Docker images to ECR**

| Step | Command | Description |
|:---:|:---:|:---:|
| **1** | `aws ecr get-login-password` | Get authentication token |
| **2** | `docker login` | Authenticate Docker |
| **3** | `docker tag` | Tag image |
| **4** | `docker push` | Push to ECR |

</div>

**Complete Workflow:**
```bash
# 1. Get login token
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com

# 2. Tag image
docker tag my-app:latest \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest

# 3. Push image
docker push \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
```

### Pulling Images

<div align="center">

**Pull images from ECR**

| Step | Command | Description |
|:---:|:---:|:---:|
| **1** | `aws ecr get-login-password` | Get authentication token |
| **2** | `docker login` | Authenticate Docker |
| **3** | `docker pull` | Pull image |

</div>

**Pull Workflow:**
```bash
# Authenticate
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com

# Pull image
docker pull \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
```

### Image Tagging

<div align="center">

**Tag strategies**

| Strategy | Description | Example |
|:---:|:---:|:---:|
| **Semantic Versioning** | Version numbers | v1.0.0, v1.1.0 |
| **Latest** | Most recent | latest |
| **Git Commit** | Commit hash | abc1234 |
| **Environment** | Environment name | prod, dev |

</div>

**Best Practices:**
- Use semantic versioning
- Tag with `latest` for most recent
- Include git commit hash
- Tag by environment
- Avoid mutable tags in production

---

## 🔐 Security

### Authentication

<div align="center">

**Access control methods**

| Method | Description | Use Case |
|:---:|:---:|:---:|
| **IAM** | AWS IAM users/roles | AWS services |
| **Repository Policies** | Repository-level access | Cross-account access |
| **Public Repositories** | Public access | Open source |

</div>

**IAM Authentication:**
- Use IAM users/roles
- Attach ECR policies
- Integrates with AWS services
- Standard AWS security model

**Repository Policies:**
- Fine-grained access control
- Cross-account access
- Public repository access
- JSON policy documents

### Encryption

<div align="center">

**Encryption options**

| Type | Description | Key Management |
|:---:|:---:|:---:|
| **AES-256** | AWS-managed encryption | AWS KMS |
| **KMS** | Customer-managed keys | Your KMS key |

</div>

**Encryption at Rest:**
- All images encrypted by default
- AES-256 encryption
- Optional KMS encryption
- Compliant with security standards

### Image Scanning

<div align="center">

**Vulnerability detection**

| Scan Type | Coverage | Cost |
|:---:|:---:|:---:|
| **Basic** | Common vulnerabilities | Free |
| **Enhanced** | Comprehensive CVE database | Per scan |

</div>

**Scanning Process:**
1. Push image to ECR
2. Automatic scan (if enabled)
3. Generate scan report
4. View vulnerabilities
5. Fix and re-push

**Scan Results:**
- CVE IDs
- Severity levels (CRITICAL, HIGH, MEDIUM, LOW)
- Package information
- Remediation guidance

---

## 💰 Pricing

<div align="center">

**ECR pricing model**

| Component | Cost |
|:---:|:---:|
| **Storage** | $0.10 per GB/month |
| **Data Transfer** | Standard AWS pricing |
| **Basic Scanning** | Free |
| **Enhanced Scanning** | Per scan pricing |

</div>

**Storage Pricing:**
- First 500 MB/month: Free
- Additional storage: $0.10 per GB/month
- Based on actual storage used
- Charged per repository

**Data Transfer:**
- Inbound: Free
- Outbound: Standard AWS data transfer pricing
- Between AWS services: Free (same region)

**Cost Optimization:**
- Use lifecycle policies
- Delete unused images
- Use image scanning to identify issues early
- Replicate only when needed

---

## 🔄 Lifecycle Policies

<div align="center">

**Automated image management**

| Policy Type | Description | Example |
|:---:|:---:|:---:|
| **Expire Untagged** | Delete untagged images | Cleanup old images |
| **Expire by Count** | Keep N most recent | Keep last 10 images |
| **Expire by Age** | Delete after X days | Delete after 30 days |

</div>

### Lifecycle Policy Example

```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Keep last 10 images",
      "selection": {
        "tagStatus": "tagged",
        "tagPrefixList": ["v"],
        "countType": "imageCountMoreThan",
        "countNumber": 10
      },
      "action": {
        "type": "expire"
      }
    },
    {
      "rulePriority": 2,
      "description": "Delete untagged images older than 1 day",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countUnit": "days",
        "countNumber": 1
      },
      "action": {
        "type": "expire"
      }
    }
  ]
}
```

**Policy Rules:**
- **Expire Untagged:** Delete images without tags
- **Expire by Count:** Keep N most recent images
- **Expire by Age:** Delete images older than X days
- **Tag Prefix Matching:** Apply to specific tags

---

## 🌍 Replication

<div align="center">

**Cross-region image replication**

| Feature | Description | Use Case |
|:---:|:---:|:---:|
| **Replication** | Copy images to other regions | Multi-region deployments |
| **Automatic** | Replicate on push | Always in sync |
| **Manual** | On-demand replication | As needed |

</div>

**Replication Benefits:**
- Faster image pulls (local region)
- High availability
- Disaster recovery
- Compliance requirements

**Replication Configuration:**
- Configure replication rules
- Select target regions
- Automatic or manual replication
- Per-repository configuration

---

## 🔗 Integration

### ECS Integration

<div align="center">

**Using ECR with ECS**

| Component | Integration |
|:---:|:---:|
| **Task Definition** | Specify ECR image |
| **Execution Role** | Pull images from ECR |
| **Service** | Deploy from ECR |

</div>

**ECS Task Definition:**
```json
{
  "containerDefinitions": [
    {
      "name": "my-app",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest",
      "cpu": 512,
      "memory": 1024
    }
  ]
}
```

### EKS Integration

<div align="center">

**Using ECR with EKS**

| Component | Integration |
|:---:|:---:|
| **Deployment** | Specify ECR image |
| **Service Account** | IRSA for ECR access |
| **Pod** | Pull from ECR |

</div>

**Kubernetes Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      containers:
      - name: my-app
        image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
```

### Lambda Integration

<div align="center">

**Using ECR with Lambda**

| Feature | Description |
|:---:|:---:|
| **Container Images** | Lambda supports container images |
| **ECR Images** | Use ECR images for Lambda |
| **Larger Images** | Up to 10 GB images |

</div>

**Lambda Container Image:**
- Use ECR images for Lambda functions
- Support for larger images
- Custom runtime environments
- Dockerfile-based deployments

---

## 💡 Best Practices

<div align="center">

| Practice | Description |
|:---:|:---:|
| **Use Lifecycle Policies** | Automatic cleanup |
| **Enable Image Scanning** | Security |
| **Use Semantic Versioning** | Image tagging |
| **Tag with Latest** | Most recent version |
| **Use IAM Roles** | Secure access |
| **Enable Encryption** | Data protection |
| **Monitor Storage** | Cost optimization |
| **Use Replication** | Multi-region deployments |

</div>

---

## 📚 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **Repositories** | Organize images by application |
| **Image Scanning** | Detect vulnerabilities |
| **Lifecycle Policies** | Automatic cleanup |
| **IAM Integration** | Secure access |
| **Encryption** | Data protection |
| **Pricing** | Storage + data transfer |
| **Integration** | Works with ECS, EKS, Lambda |

**💡 Remember:** ECR is your Docker registry on AWS. Use lifecycle policies for cost optimization, enable scanning for security, and integrate with ECS/EKS for deployments.

</div>

---

## 🔗 Related Services

<div align="center">

| Service | Purpose | Integration |
|:---:|:---:|:---:|
| **ECS** | Container orchestration | Pull images |
| **EKS** | Kubernetes | Pull images |
| **Lambda** | Serverless compute | Container images |
| **IAM** | Access control | Authentication |
| **KMS** | Key management | Encryption |

</div>

---

<div align="center">

**Master ECR for container image management! 🚀**

*Store, manage, and deploy Docker container images securely on AWS.*

</div>

