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

### Pricing Options

| Model | Description | Savings | Use Case |
|:---:|:---:|:---:|:---:|
| **On-Demand** | Pay per hour/second | None | Variable workloads |
| **Reserved Instances** | 1-3 year commitment | Up to 72% | Steady workloads |
| **Savings Plans** | Flexible commitment | Up to 72% | Predictable usage |
| **Spot Instances** | Bid on spare capacity | Up to 90% | Flexible, fault-tolerant |
| **Dedicated Hosts** | Physical server | Premium | Compliance, licensing |

---

### Reserved Instances Types

| Type | Description | Savings |
|:---:|:---:|:---:|
| **Standard** | No modifications | Up to 72% |
| **Convertible** | Can change instance type | Up to 54% |
| **Scheduled** | Reserved for specific time | Variable |

---

### Spot Instances

**Characteristics:**

- ⚠️ Can be interrupted with 2-minute notice
- 💰 Up to 90% cheaper
- ✅ Good for fault-tolerant workloads
- ✅ Batch processing, data analysis

**Best Practices:**

- Use Spot Fleet for availability
- Diversify across instance types
- Use Spot interruption notices

</div>

---

## 🔐 Security Groups

<div align="center">

### What are Security Groups?

**Virtual firewall controlling inbound/outbound traffic**

| Characteristic | Description |
|:---:|:---:|
| **Stateful** | Return traffic automatically allowed |
| **Default Deny** | All traffic denied by default |
| **Rules** | Allow specific traffic |
| **Multiple Groups** | Instance can have multiple |

---

### Security Group Rules

**Rule Components:**

| Component | Description | Example |
|:---:|:---:|:---:|
| **Type** | Protocol | SSH, HTTP, HTTPS |
| **Port** | Port number | 22, 80, 443 |
| **Source** | IP or security group | 0.0.0.0/0, sg-xxx |

**Example:**
```
Type: SSH
Port: 22
Source: 203.0.113.0/24 (your office IP)
```

---

### Best Practices

| Practice | Why |
|:---:|:---:|
| **Least privilege** | Only allow necessary traffic |
| **Reference security groups** | Not IPs (dynamic) |
| **Separate by tier** | Web, app, database tiers |
| **Regular review** | Remove unused rules |

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

## 💾 EBS Volumes

<div align="center">

### What is EBS?

**Elastic Block Store - persistent block storage for EC2**

| Characteristic | Description |
|:---:|:---:|
| **Persistent** | Data survives instance termination |
| **Attachable** | Can attach/detach volumes |
| **Backup** | Snapshots for backup |
| **Types** | gp3, gp2, io1, io2, st1, sc1 |

---

### EBS Volume Types

| Type | Description | Use Case |
|:---:|:---:|:---:|
| **gp3** | General purpose SSD | Most workloads |
| **gp2** | General purpose SSD (legacy) | General purpose |
| **io1/io2** | Provisioned IOPS SSD | High-performance databases |
| **st1** | Throughput optimized HDD | Big data, data warehouses |
| **sc1** | Cold HDD | Infrequent access |

---

### Snapshots

**Point-in-time backup of EBS volume**

| Feature | Description |
|:---:|:---:|
| **Incremental** | Only changed blocks saved |
| **Cross-Region** | Copy to other regions |
| **Encrypted** | Can encrypt snapshots |
| **Lifecycle** | Automated snapshot management |

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
| **Use EBS snapshots** | Backup and recovery |
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

