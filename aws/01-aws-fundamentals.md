# 🌍 AWS Fundamentals

<div align="center">

**AWS basics: regions, availability zones, accounts, and core concepts**

[![AWS](https://img.shields.io/badge/AWS-Fundamentals-blue?style=for-the-badge)](./)
[![Cloud](https://img.shields.io/badge/Cloud-Computing-green?style=for-the-badge)](./)
[![Basics](https://img.shields.io/badge/Basics-Foundation-orange?style=for-the-badge)](./)

*Master AWS fundamentals: understand regions, availability zones, accounts, and core services*

</div>

---

## 🎯 What is AWS?

<div align="center">

**Amazon Web Services (AWS) is a comprehensive cloud computing platform offering over 200 services for computing, storage, databases, networking, and more.**

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **☁️ Cloud Computing** | On-demand computing resources |
| **💰 Pay-as-you-go** | Pay only for what you use |
| **🌍 Global Infrastructure** | Data centers worldwide |
| **📈 Scalable** | Scale up or down as needed |
| **🔒 Secure** | Enterprise-grade security |

**Mental Model:** Think of AWS as a massive data center in the cloud - you can rent computing power, storage, databases, and other services instead of buying and maintaining your own hardware.

</div>

---

## 🌍 Global Infrastructure

<div align="center">

### Regions

**Geographic areas with multiple data centers**

| Concept | Description | Example |
|:---:|:---:|:---:|
| **Region** | Geographic area | us-east-1 (N. Virginia) |
| **Availability Zone (AZ)** | Isolated data center | us-east-1a, us-east-1b |
| **Edge Locations** | CDN endpoints | CloudFront locations |

**Key Points:**

- ✅ Choose region based on latency, compliance, cost
- ✅ Resources are region-specific (not global)
- ✅ Some services are global (IAM, Route 53)
- ✅ Data doesn't leave region unless you move it

---

### Availability Zones (AZs)

**Isolated data centers within a region**

| Characteristic | Description |
|:---:|:---:|
| **Isolation** | Separate power, networking, facilities |
| **Low Latency** | Connected via high-speed fiber |
| **High Availability** | Deploy across AZs for redundancy |
| **Minimum** | At least 2 AZs per region |

**Best Practice:** Deploy across multiple AZs for high availability.

</div>

---

## 💳 AWS Accounts

<div align="center">

### Account Structure

| Component | Description | Use Case |
|:---:|:---:|:---:|
| **Root Account** | Master account | Initial setup |
| **IAM Users** | Individual users | Team members |
| **IAM Roles** | Temporary credentials | Services, EC2 |
| **Organizations** | Multiple accounts | Enterprise |

---

### Account Best Practices

| Practice | Why |
|:---:|:---:|
| **Enable MFA** | Security |
| **Use IAM users/roles** | Don't use root |
| **Organizations** | Multi-account management |
| **Billing alerts** | Cost control |
| **CloudTrail** | Audit logging |

</div>

---

## 💰 Pricing Model

<div align="center">

### Pricing Principles

| Principle | Description |
|:---:|:---:|
| **Pay-as-you-go** | Pay for what you use |
| **Pay less when you reserve** | Reserved instances |
| **Pay less by using more** | Volume discounts |
| **Pay less as AWS grows** | Prices decrease over time |

---

### Pricing Components

| Component | Description | Example |
|:---:|:---:|:---:|
| **Compute** | Per hour/second | EC2 instances |
| **Storage** | Per GB/month | S3 storage |
| **Data Transfer** | Per GB | Outbound data |
| **Requests** | Per request | API calls |

---

### Cost Optimization

| Strategy | Description | Savings |
|:---:|:---:|:---:|
| **Reserved Instances** | 1-3 year commitment | Up to 72% |
| **Savings Plans** | Flexible commitment | Up to 72% |
| **Spot Instances** | Interruptible capacity | Up to 90% |
| **Right-sizing** | Match instance to workload | 10-40% |

</div>

---

## 🎯 Core Services Overview

<div align="center">

### Service Categories

| Category | Services | Purpose |
|:---:|:---:|:---:|
| **💻 Compute** | EC2, Lambda, ECS, EKS | Run applications |
| **💾 Storage** | S3, EBS, EFS, Glacier | Store data |
| **🗄️ Database** | RDS, DynamoDB, ElastiCache | Managed databases |
| **🌐 Networking** | VPC, CloudFront, Route 53 | Network infrastructure |
| **🔐 Security** | IAM, KMS, Secrets Manager | Security & compliance |
| **📊 Monitoring** | CloudWatch, CloudTrail | Observability |
| **🚀 Serverless** | Lambda, API Gateway, Step Functions | Serverless architecture |
| **🔄 DevOps** | CodePipeline, CodeBuild | CI/CD |

</div>

---

## 🔐 Security & Compliance

<div align="center">

### Shared Responsibility Model

**AWS vs Customer Responsibilities**

| Responsibility | AWS | Customer |
|:---:|:---:|:---:|
| **Infrastructure** | ✅ AWS | ❌ Customer |
| **Operating System** | ❌ AWS | ✅ Customer |
| **Application** | ❌ AWS | ✅ Customer |
| **Data** | ❌ AWS | ✅ Customer |
| **Configuration** | ❌ AWS | ✅ Customer |

**💡 AWS secures the cloud, you secure what's in the cloud.**

---

### Compliance

| Standard | Description |
|:---:|:---:|
| **SOC 2** | Security, availability, processing integrity |
| **ISO 27001** | Information security management |
| **PCI DSS** | Payment card industry |
| **HIPAA** | Healthcare data |
| **GDPR** | European data protection |

</div>

---

## 📊 Service Limits

<div align="center">

### Default Limits

| Service | Default Limit | Can Increase? |
|:---:|:---:|:---:|
| **EC2 Instances** | 20 per region | ✅ Yes (support ticket) |
| **S3 Buckets** | 100 per account | ✅ Yes |
| **VPCs** | 5 per region | ✅ Yes |
| **Elastic IPs** | 5 per region | ✅ Yes |
| **IAM Roles** | 1000 per account | ✅ Yes |

**💡 Most limits can be increased via support ticket.**

</div>

---

## 🎯 AWS Well-Architected Framework

<div align="center">

### Six Pillars

| Pillar | Description | Focus |
|:---:|:---:|:---:|
| **Operational Excellence** | Run and monitor systems | Processes, automation |
| **Security** | Protect data and systems | IAM, encryption, compliance |
| **Reliability** | Recover from failures | Multi-AZ, backups |
| **Performance Efficiency** | Use resources efficiently | Right-sizing, caching |
| **Cost Optimization** | Eliminate unnecessary costs | Reserved instances, monitoring |
| **Sustainability** | Environmental impact | Efficient resource usage |

</div>

---

## 💡 Best Practices

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Use multiple AZs** | High availability |
| **Enable CloudTrail** | Audit logging |
| **Set up billing alerts** | Cost control |
| **Use IAM properly** | Security |
| **Tag resources** | Organization, cost tracking |
| **Enable MFA** | Security |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Use root account** | Security risk | Use IAM users/roles |
| **Single AZ deployment** | No redundancy | Multi-AZ |
| **No monitoring** | Unknown issues | CloudWatch |
| **No cost tracking** | Budget overruns | Billing alerts |

</div>

---

## 🎓 For Engineering Leaders

<div align="center">

### Key Questions to Ask

| Question | Why It Matters |
|:---:|:---:|
| **What regions do we use?** | Latency, compliance, cost |
| **What's our multi-AZ strategy?** | High availability |
| **How do we manage costs?** | Budget control |
| **What's our security posture?** | Compliance, risk |
| **How do we track usage?** | Cost optimization |

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **Regions** | Geographic areas with multiple AZs |
| **Availability Zones** | Isolated data centers for redundancy |
| **Pay-as-you-go** | Pay only for what you use |
| **Shared Responsibility** | AWS secures cloud, you secure in cloud |
| **Well-Architected** | Six pillars for best practices |

**💡 Remember:** AWS is a global infrastructure platform. Choose regions wisely, deploy across AZs, and follow the Well-Architected Framework.

</div>

---

<div align="center">

**Master AWS fundamentals for cloud success! 🚀**

*Understand AWS global infrastructure, pricing, and core concepts to build on AWS effectively.*

</div>

