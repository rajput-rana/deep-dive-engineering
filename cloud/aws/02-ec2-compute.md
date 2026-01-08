# 💻 EC2 - Elastic Compute Cloud

<div align="center">

**Virtual servers in the cloud: instances, AMIs, and auto-scaling**

[![EC2](https://img.shields.io/badge/EC2-Compute-blue?style=for-the-badge)](./)
[![Instances](https://img.shields.io/badge/Instances-Virtual%20Servers-green?style=for-the-badge)](./)
[![Scaling](https://img.shields.io/badge/Scaling-Auto%20Scaling-orange?style=for-the-badge)](./)

*Master EC2: launch, configure, and scale virtual servers in AWS*

</div>

---

## 🎯 What is EC2?

<div align="center">

**EC2 (Elastic Compute Cloud) provides resizable virtual servers (instances) in the cloud.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **🖥️ Instance** | Virtual server |
| **🖼️ AMI** | Amazon Machine Image (template) |
| **💾 Instance Types** | CPU, memory, storage combinations |
| **🔑 Key Pairs** | SSH access credentials |
| **🔒 Security Groups** | Firewall rules |
| **📊 Auto Scaling** | Automatic scaling based on demand |

**Mental Model:** Think of EC2 like renting a computer in the cloud - you choose the hardware specs, operating system, and configuration, then launch it on-demand.

</div>

---

## 🏗️ EC2 Instance Types

<div align="center">

### Instance Families

| Family | Use Case | Characteristics |
|:---:|:---:|:---:|
| **General Purpose (M, T)** | Web servers, small databases | Balanced CPU, memory, network |
| **Compute Optimized (C)** | High-performance computing | High CPU-to-memory ratio |
| **Memory Optimized (R, X)** | In-memory databases, analytics | High memory-to-CPU ratio |
| **Storage Optimized (I, D)** | Data warehousing, big data | High storage I/O |
| **Accelerated Computing (P, G)** | Machine learning, graphics | GPUs, FPGAs |

---

### Instance Naming

**Format:** `family.generation.size`

**Example:** `t3.medium`
- `t` = General purpose burstable
- `3` = Third generation
- `medium` = Size

---

### Instance Sizes

| Size | vCPUs | Memory (GiB) | Use Case |
|:---:|:---:|:---:|:---:|
| **nano** | 1 | 0.5 | Testing, low traffic |
| **small** | 1 | 2 | Small applications |
| **medium** | 2 | 4 | Medium applications |
| **large** | 2 | 8 | Production workloads |
| **xlarge** | 4 | 16 | High-performance |

</div>

---

## 🖼️ Amazon Machine Images (AMIs)

<div align="center">

### What is an AMI?

**Template for creating EC2 instances**

| Component | Description |
|:---:|:---:|
| **Operating System** | Linux, Windows, macOS |
| **Applications** | Pre-installed software |
| **Configuration** | Settings, permissions |
| **Block Device Mapping** | Root volume configuration |

---

### AMI Types

| Type | Description | Use Case |
|:---:|:---:|:---:|
| **Public AMIs** | AWS or community | Quick start |
| **Custom AMIs** | Your own images | Standardized deployments |
| **Marketplace AMIs** | Third-party software | Licensed software |

---

### Creating Custom AMIs

**Benefits:**

- ✅ Faster instance launches
- ✅ Consistent configuration
- ✅ Pre-installed software
- ✅ Compliance requirements

**Process:**

1. Launch instance from base AMI
2. Configure and install software
3. Create AMI from instance
4. Use AMI for new instances

</div>

---

## 💰 EC2 Pricing Models

<div align="center">

**EC2 offers multiple pricing options to optimize costs based on your workload patterns.**

| Model | Description | Savings | Use Case |
|:---:|:---:|:---:|:---:|
| **On-Demand** | Pay per hour/second | None | Variable workloads |
| **Reserved Instances** | 1-3 year commitment | Up to 72% | Steady workloads |
| **Savings Plans** | Flexible commitment | Up to 72% | Predictable usage |
| **Spot Instances** | Bid on spare capacity | Up to 90% | Flexible, fault-tolerant |
| **Dedicated Hosts** | Physical server | Premium | Compliance, licensing |

**Quick Tips:**
- **On-Demand:** No commitment, highest flexibility
- **Reserved:** Best for steady 24/7 workloads
- **Spot:** Up to 90% savings, can be interrupted
- **Savings Plans:** Flexibility with commitment benefits

For comprehensive cost optimization strategies, detailed pricing comparisons, and decision frameworks, see **[AWS Cost Optimization Guide](./20-cost-optimization.md)** and **[Cloud Cost Optimization Guide](../cloud-cost-optimization-guide.md)**.

</div>

---

## 🔐 Security Groups

<div align="center">

**Security Groups are virtual firewalls that control inbound and outbound traffic for EC2 instances.**

**Key Characteristics:**
- **Stateful:** Return traffic automatically allowed
- **Default Deny:** All traffic denied by default
- **Instance-Level:** Applied to EC2 instances
- **Multiple Groups:** Instance can belong to multiple security groups

**Common Rules:**
- SSH (port 22) from office IP
- HTTP (port 80) from internet
- HTTPS (port 443) from internet
- Database ports from application security group

**Best Practice:** Reference security groups (not IPs) for dynamic, flexible rules.

For comprehensive Security Groups details including NACLs, VPC integration, and advanced networking, see **[VPC Networking Guide](./11-vpc-networking.md)**.

</div>

---

## 📊 Auto Scaling

<div align="center">

### What is Auto Scaling?

**Automatically adjust number of EC2 instances based on demand**

| Benefit | Description |
|:---:|:---:|
| **Cost Optimization** | Scale down when not needed |
| **High Availability** | Replace unhealthy instances |
| **Performance** | Scale up during traffic spikes |

---

### Auto Scaling Components

| Component | Description |
|:---:|:---:|
| **Launch Template** | Instance configuration |
| **Auto Scaling Group** | Collection of instances |
| **Scaling Policies** | When to scale |
| **Health Checks** | Instance health monitoring |

---

### Scaling Policies

| Policy | Description | Use Case |
|:---:|:---:|:---:|
| **Target Tracking** | Maintain target metric | CPU utilization |
| **Step Scaling** | Scale by steps | Gradual scaling |
| **Simple Scaling** | Single scaling action | Simple scenarios |

**Example:**
```
Scale out when CPU > 70%
Scale in when CPU < 30%
```

</div>

---

## 💾 Storage for EC2

<div align="center">

**EC2 instances use EBS volumes for persistent block storage.**

For detailed information about EBS volume types, snapshots, performance, and best practices, see **[EBS & EFS Storage Guide](./08-ebs-efs-storage.md)**.

**Quick Reference:**
- **EBS:** Persistent block storage attached to EC2 instances
- **EFS:** Shared file storage accessible by multiple EC2 instances
- **Instance Store:** Ephemeral storage (lost on instance stop)

</div>

---

## 🎯 Use Cases

<div align="center">

### When to Use EC2

| Use Case | Description |
|:---:|:---:|
| **Web Applications** | Host web servers |
| **Databases** | Run database servers |
| **Development/Testing** | Dev/test environments |
| **Batch Processing** | Large-scale processing |
| **High-Performance Computing** | Scientific computing |

### When NOT to Use EC2

| Scenario | Alternative |
|:---:|:---:|
| **Simple APIs** | Lambda (serverless) |
| **Static websites** | S3 + CloudFront |
| **Container workloads** | ECS, EKS |
| **Managed databases** | RDS |

</div>

---

## 💡 Best Practices

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Use Auto Scaling** | Cost optimization, availability |
| **Multi-AZ deployment** | High availability |
| **Use appropriate instance types** | Cost optimization |
| **Enable detailed monitoring** | Performance insights |
| **Configure EBS volumes properly** | Storage performance and cost |
| **Tag instances** | Cost tracking, organization |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Over-provisioning** | Wasted cost | Right-size instances |
| **Single AZ** | No redundancy | Multi-AZ |
| **No monitoring** | Unknown issues | CloudWatch |
| **Public SSH access** | Security risk | Use VPN/bastion |

</div>

---

## 🎓 For Engineering Leaders

<div align="center">

### Key Questions to Ask

| Question | Why It Matters |
|:---:|:---:|
| **What's our instance strategy?** | Cost optimization |
| **Do we use Auto Scaling?** | Cost and availability |
| **What's our backup strategy?** | Disaster recovery |
| **How do we monitor instances?** | Performance, cost |
| **What's our multi-AZ setup?** | High availability |

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **EC2 Purpose** | Virtual servers in the cloud |
| **Instance Types** | Choose based on workload |
| **Pricing** | On-demand, Reserved, Spot |
| **Auto Scaling** | Automatic capacity management |
| **Security Groups** | Virtual firewall |

**💡 Remember:** EC2 is flexible but requires management. Use Auto Scaling, right-size instances, and deploy across multiple AZs for production workloads.

</div>

---

<div align="center">

**Master EC2 for scalable cloud compute! 🚀**

*Launch, configure, and scale virtual servers with EC2 for flexible cloud computing.*

</div>

