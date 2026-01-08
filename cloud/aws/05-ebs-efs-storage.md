# 💾 EBS & EFS - Block and File Storage

<div align="center">

**Persistent block storage and shared file storage for EC2**

[![EBS](https://img.shields.io/badge/EBS-Block%20Storage-blue?style=for-the-badge)](./)
[![EFS](https://img.shields.io/badge/EFS-File%20Storage-green?style=for-the-badge)](./)
[![Storage](https://img.shields.io/badge/Storage-Persistent-orange?style=for-the-badge)](./)

*Master EBS and EFS: persistent block storage and shared file systems*

</div>

---

## 🎯 EBS - Elastic Block Store

<div align="center">

**EBS provides persistent block storage volumes for EC2 instances.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **💾 Volume** | Persistent block storage |
| **📸 Snapshot** | Point-in-time backup |
| **🔗 Attachment** | Attach to EC2 instance |
| **📊 Types** | gp3, gp2, io1, io2, st1, sc1 |
| **🌍 Availability** | Single AZ (within region) |

**Mental Model:** Think of EBS like an external hard drive - you attach it to your computer (EC2 instance), store data on it, and it persists even if you turn off the computer.

</div>

---

## 💾 EBS Volume Types

<div align="center">

### Volume Type Comparison

| Type | Description | IOPS | Throughput | Use Case |
|:---:|:---:|:---:|:---:|:---:|
| **gp3** | General purpose SSD | 3,000-16,000 | 125-1,000 MB/s | Most workloads |
| **gp2** | General purpose SSD (legacy) | 3-16,000 | 128-250 MB/s | General purpose |
| **io1/io2** | Provisioned IOPS SSD | Up to 64,000 | Up to 1,000 MB/s | Databases |
| **st1** | Throughput optimized HDD | 500 | 500 MB/s | Big data, data warehouses |
| **sc1** | Cold HDD | 250 | 250 MB/s | Infrequent access |

---

### Choosing Volume Type

| Workload | Recommended Type |
|:---:|:---:|
| **Boot volumes** | gp3 |
| **General applications** | gp3 |
| **Databases** | io1/io2 (high IOPS) |
| **Big data** | st1 |
| **Archive** | sc1 |

</div>

---

## 📸 EBS Snapshots

<div align="center">

### What are Snapshots?

**Point-in-time backup of EBS volume**

| Feature | Description |
|:---:|:---:|
| **Incremental** | Only changed blocks saved |
| **Cross-Region** | Copy to other regions |
| **Encrypted** | Can encrypt snapshots |
| **Lifecycle** | Automated snapshot management |

---

### Snapshot Best Practices

| Practice | Why |
|:---:|:---:|
| **Regular snapshots** | Data protection |
| **Cross-region copies** | Disaster recovery |
| **Automated snapshots** | Consistency |
| **Tag snapshots** | Organization |

</div>

---

## 🌐 EFS - Elastic File System

<div align="center">

### What is EFS?

**Managed NFS file system for EC2 instances**

| Characteristic | Description |
|:---:|:---:|
| **📁 Shared Storage** | Multiple EC2 instances access |
| **🌍 Multi-AZ** | Available across AZs |
| **📈 Scalable** | Grows automatically |
| **💰 Pay-per-use** | Pay for storage used |

**Mental Model:** Think of EFS like a network drive - multiple computers (EC2 instances) can access the same files simultaneously, like a shared folder.

</div>

---

## 🏗️ EFS Performance Modes

<div align="center">

### Performance Modes

| Mode | Description | Use Case |
|:---:|:---:|
| **General Purpose** | Low latency | Web servers, content management |
| **Max I/O** | Higher throughput | Big data, analytics |

---

### Throughput Modes

| Mode | Description | Use Case |
|:---:|:---:|
| **Bursting** | Baseline + burst | Variable workloads |
| **Provisioned** | Consistent throughput | Steady workloads |

---

### Storage Classes

| Class | Description | Use Case |
|:---:|:---:|
| **Standard** | Frequently accessed | Active data |
| **Infrequent Access (IA)** | Lower cost | Less frequently accessed |

</div>

---

## ⚖️ EBS vs EFS

<div align="center">

### Comparison

| Aspect | EBS | EFS |
|:---:|:---:|:---:|
| **Type** | Block storage | File storage |
| **Access** | Single instance | Multiple instances |
| **Availability** | Single AZ | Multi-AZ |
| **Use Case** | Database, boot volumes | Shared files, web content |
| **Performance** | Low latency | Network latency |
| **Cost** | Per GB/month | Per GB/month + requests |

---

### When to Use Each

| Scenario | Use |
|:---:|:---:|
| **Database storage** | EBS |
| **Boot volumes** | EBS |
| **Shared web content** | EFS |
| **Multiple instances need same files** | EFS |
| **High IOPS needed** | EBS (io1/io2) |

</div>

---

## 💡 Best Practices

<div align="center">

### ✅ EBS Best Practices

| Practice | Why |
|:---:|:---:|
| **Right-size volumes** | Cost optimization |
| **Use gp3 for most cases** | Best price/performance |
| **Enable encryption** | Security |
| **Regular snapshots** | Data protection |
| **Monitor performance** | CloudWatch metrics |

---

### ✅ EFS Best Practices

| Practice | Why |
|:---:|:---:|
| **Use for shared storage** | Multiple instances |
| **Choose right performance mode** | Latency vs throughput |
| **Use IA class for old data** | Cost optimization |
| **Mount in multiple AZs** | High availability |

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **EBS Purpose** | Block storage for single instance |
| **EFS Purpose** | File storage for multiple instances |
| **EBS Types** | gp3, io1/io2, st1, sc1 |
| **Snapshots** | Incremental backups |
| **Choose Based On** | Single vs multiple instance access |

**💡 Remember:** Use EBS for single-instance block storage, EFS for shared file storage across multiple instances.

</div>

---

<div align="center">

**Master EBS and EFS for persistent storage! 🚀**

*Choose the right storage solution: EBS for block storage, EFS for shared file storage.*

</div>

