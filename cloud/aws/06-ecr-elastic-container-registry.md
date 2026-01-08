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
| **🔒 Lifecycle Policy** | Automatic image cleanup |
| **🔐 Image Scanning** | Vulnerability detection |

**Mental Model:** Think of ECR as Docker Hub on AWS - you push Docker images to repositories, tag them with versions, and pull them when deploying to ECS, EKS, or EC2.

</div>

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

</div>

---

## 📦 Repositories

<div align="center">

**Different repository configurations**

| Type | Description | Use Case |
|:---:|:---:|:---:|
| **Private** | Accessible only to your account | Production images |
| **Public** | Publicly accessible | Open source images |
| **Encrypted** | Encryption at rest | Sensitive images |

</div>

---

## 🖼️ Image Management

<div align="center">

**Push and pull Docker images**

| Operation | Description |
|:---:|:---:|
| **Push** | Upload images to ECR |
| **Pull** | Download images from ECR |
| **Tag** | Version images |

</div>

**Basic Workflow:**
1. Authenticate Docker with ECR
2. Tag image with ECR repository URL
3. Push image to ECR
4. Pull image when deploying

**Image Tagging:**
- Use semantic versioning (v1.0.0, v1.1.0)
- Tag with `latest` for most recent
- Include git commit hash
- Tag by environment (prod, dev)

---

## 🔐 Security

<div align="center">

**Security features**

| Feature | Description |
|:---:|:---:|
| **IAM Authentication** | AWS IAM users/roles |
| **Image Scanning** | Vulnerability detection |
| **Encryption** | At-rest encryption |

</div>

**Image Scanning:**
- Detects vulnerabilities in images
- Uses CVE database
- Provides severity ratings
- Can block deployments based on findings

**Encryption:**
- All images encrypted by default
- AES-256 encryption
- Optional KMS encryption

---

## 🔄 Lifecycle Policies

<div align="center">

**Automated image management**

| Policy Type | Description |
|:---:|:---:|
| **Expire Untagged** | Delete untagged images |
| **Expire by Count** | Keep N most recent |
| **Expire by Age** | Delete after X days |

</div>

**Benefits:**
- Automatic cleanup
- Cost optimization
- Repository management

---

## 💰 Pricing

<div align="center">

**ECR pricing model**

| Component | Cost |
|:---:|:---:|
| **Storage** | $0.10 per GB/month |
| **Data Transfer** | Standard AWS pricing |
| **Basic Scanning** | Free |

</div>

**Cost Optimization:**
- Use lifecycle policies
- Delete unused images
- Enable image scanning

---

## 🔗 Integration

<div align="center">

**ECR integrates with AWS services**

| Service | Integration |
|:---:|:---:|
| **ECS** | Pull images for tasks |
| **EKS** | Pull images for pods |
| **Lambda** | Container images |
| **EC2** | Pull images for instances |

</div>

---

## 💡 Best Practices

<div align="center">

| Practice | Description |
|:---:|:---:|
| **Use Lifecycle Policies** | Automatic cleanup |
| **Enable Image Scanning** | Security |
| **Use Semantic Versioning** | Image tagging |
| **Use IAM Roles** | Secure access |
| **Monitor Storage** | Cost optimization |

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

</div>

---

<div align="center">

**Master ECR for container image management! 🚀**

*Store, manage, and deploy Docker container images securely on AWS.*

</div>
