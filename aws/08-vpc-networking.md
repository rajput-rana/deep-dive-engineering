# 🌐 VPC - Virtual Private Cloud

<div align="center">

**Isolated network environment: subnets, routing, and security**

[![VPC](https://img.shields.io/badge/VPC-Networking-blue?style=for-the-badge)](./)
[![Network](https://img.shields.io/badge/Network-Isolated-green?style=for-the-badge)](./)
[![Security](https://img.shields.io/badge/Security-Private-orange?style=for-the-badge)](./)

*Master VPC: create isolated networks, configure routing, and secure your AWS resources*

</div>

---

## 🎯 What is VPC?

<div align="center">

**VPC (Virtual Private Cloud) is a logically isolated network environment in AWS where you can launch AWS resources.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **🌐 VPC** | Isolated network (like a data center) |
| **📍 Subnet** | Network segment within VPC |
| **🛣️ Route Table** | Routing rules for subnets |
| **🚪 Internet Gateway** | Internet access for VPC |
| **🔒 Security Group** | Virtual firewall |
| **🔐 NACL** | Network Access Control List |

**Mental Model:** Think of VPC like your own private data center network in the cloud - you control IP ranges, subnets, routing, and security.

</div>

---

## 🏗️ VPC Components

<div align="center">

### Core Components

| Component | Description | Purpose |
|:---:|:---:|:---:|
| **VPC** | Isolated network | Logical isolation |
| **Subnet** | Network segment | Organize resources |
| **Route Table** | Routing rules | Control traffic flow |
| **Internet Gateway** | Internet access | Public internet |
| **NAT Gateway** | Outbound internet | Private subnet internet |
| **Security Group** | Instance firewall | Inbound/outbound rules |
| **NACL** | Subnet firewall | Additional security layer |

---

### VPC Architecture

```
VPC (10.0.0.0/16)
├── Public Subnet (10.0.1.0/24)
│   ├── Internet Gateway
│   └── EC2 (Public)
├── Private Subnet (10.0.2.0/24)
│   ├── NAT Gateway
│   └── EC2 (Private)
└── Database Subnet (10.0.3.0/24)
    └── RDS (Private)
```

</div>

---

## 📍 Subnets

<div align="center">

### Subnet Types

| Type | Description | Use Case |
|:---:|:---:|:---:|
| **Public Subnet** | Route to Internet Gateway | Public-facing resources |
| **Private Subnet** | No direct internet | Application servers, databases |
| **Isolated Subnet** | No internet access | Databases, internal services |

---

### Subnet Best Practices

| Practice | Why |
|:---:|:---:|
| **Multi-AZ subnets** | High availability |
| **Separate tiers** | Web, app, database subnets |
| **Appropriate sizing** | Enough IPs for growth |
| **Private subnets** | Security |

</div>

---

## 🛣️ Routing

<div align="center">

### Route Tables

**Control traffic flow between subnets and internet**

| Destination | Target | Description |
|:---:|:---:|:---:|
| **10.0.0.0/16** | local | VPC internal traffic |
| **0.0.0.0/0** | igw-xxx | Internet Gateway (public) |
| **0.0.0.0/0** | nat-xxx | NAT Gateway (private) |

---

### Default Route Table

**Every VPC has a default route table**

- ✅ All subnets use default if not specified
- ✅ Can be modified
- ✅ Cannot be deleted

---

### Custom Route Tables

**Create route tables for specific subnets**

**Use Cases:**

- ✅ Public subnets → Internet Gateway
- ✅ Private subnets → NAT Gateway
- ✅ Isolated subnets → No internet

</div>

---

## 🚪 Internet Gateway

<div align="center">

### What is Internet Gateway?

**Horizontally scaled, redundant gateway for internet access**

| Characteristic | Description |
|:---:|:---:|
| **One per VPC** | Single Internet Gateway |
| **Highly Available** | Redundant, no single point of failure |
| **Public IPs** | Enables public IP addresses |
| **NAT** | Network Address Translation |

---

### Internet Gateway Setup

**Steps:**

1. Create Internet Gateway
2. Attach to VPC
3. Add route to route table (0.0.0.0/0 → igw)
4. Assign public IPs to instances

**💡 Enables public internet access.**

</div>

---

## 🔄 NAT Gateway

<div align="center">

### What is NAT Gateway?

**Network Address Translation for private subnets**

| Purpose | Description |
|:---:|:---:|
| **Outbound Internet** | Private instances access internet |
| **No Inbound** | Internet cannot initiate connections |
| **High Availability** | Deploy in each AZ |

---

### NAT Gateway vs NAT Instance

| Aspect | NAT Gateway | NAT Instance |
|:---:|:---:|:---:|
| **Managed** | ✅ AWS managed | ❌ You manage |
| **Availability** | ✅ Highly available | ⚠️ Single instance |
| **Performance** | ✅ Up to 45 Gbps | ⚠️ Instance dependent |
| **Cost** | 💰 Per hour + data | 💰 Instance cost |

**💡 Use NAT Gateway for production.**

</div>

---

## 🔒 Security Groups

<div align="center">

### What are Security Groups?

**Virtual firewall for EC2 instances**

| Characteristic | Description |
|:---:|:---:|
| **Stateful** | Return traffic automatically allowed |
| **Default Deny** | All traffic denied by default |
| **Instance Level** | Applied to instances |
| **Multiple Groups** | Instance can have multiple |

---

### Security Group Rules

| Rule | Description | Example |
|:---:|:---:|:---:|
| **Inbound** | Traffic to instance | Allow SSH from office IP |
| **Outbound** | Traffic from instance | Allow HTTPS to internet |

**Best Practice:** Reference security groups, not IPs.

</div>

---

## 🔐 Network ACLs (NACLs)

<div align="center">

### What are NACLs?

**Subnet-level firewall (stateless)**

| Characteristic | Description |
|:---:|:---:|
| **Stateless** | Must allow return traffic |
| **Subnet Level** | Applied to subnets |
| **Rule Numbers** | Evaluated in order |
| **Default Allow** | Default NACL allows all |

---

### NACL vs Security Group

| Aspect | NACL | Security Group |
|:---:|:---:|:---:|
| **Level** | Subnet | Instance |
| **Stateful** | ❌ No | ✅ Yes |
| **Default** | Allow all | Deny all |
| **Use Case** | Additional layer | Primary firewall |

**💡 Use Security Groups as primary, NACLs for additional layer.**

</div>

---

## 🎯 VPC Peering

<div align="center">

### What is VPC Peering?

**Connect two VPCs privately**

| Characteristic | Description |
|:---:|:---:|
| **Private Connection** | No internet, VPN, or gateway |
| **Same or Different Accounts** | Cross-account peering |
| **Same or Different Regions** | Cross-region peering |
| **Non-Transitive** | A→B and B→C doesn't mean A→C |

---

### Use Cases

| Use Case | Description |
|:---:|:---:|
| **Multi-VPC Architecture** | Connect VPCs |
| **Cross-Account** | Connect accounts |
| **Hub-and-Spoke** | Central VPC connects to others |

</div>

---

## 💡 Best Practices

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Use private subnets** | Security |
| **Multi-AZ deployment** | High availability |
| **Separate tiers** | Web, app, database subnets |
| **Use Security Groups** | Instance-level firewall |
| **NAT Gateway for private** | Outbound internet |
| **Monitor VPC Flow Logs** | Network visibility |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Public databases** | Security risk | Private subnets |
| **Single AZ** | No redundancy | Multi-AZ |
| **Hardcode IPs** | Inflexible | Use security groups |
| **No monitoring** | Unknown issues | VPC Flow Logs |

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **VPC Purpose** | Isolated network environment |
| **Subnets** | Organize resources by tier |
| **Internet Gateway** | Public internet access |
| **NAT Gateway** | Private subnet internet |
| **Security Groups** | Instance-level firewall |

**💡 Remember:** VPC provides network isolation and security. Use private subnets for databases, NAT Gateway for private internet access, and Security Groups for instance protection.

</div>

---

<div align="center">

**Master VPC for secure networking! 🚀**

*Create isolated, secure networks with VPC - control IP ranges, routing, and security.*

</div>

