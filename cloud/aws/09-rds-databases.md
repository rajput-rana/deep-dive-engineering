# 🗄️ RDS - Relational Databases

<div align="center">

**Managed relational databases: MySQL, PostgreSQL, SQL Server, Oracle, MariaDB**

[![RDS](https://img.shields.io/badge/RDS-Managed%20Database-blue?style=for-the-badge)](./)
[![Database](https://img.shields.io/badge/Database-Relational-green?style=for-the-badge)](./)
[![High Availability](https://img.shields.io/badge/HA-Multi--AZ-orange?style=for-the-badge)](./)

*Master RDS: managed relational databases with high availability, backups, and scaling*

</div>

---

## 🎯 What is RDS?

<div align="center">

**RDS (Relational Database Service) is a managed database service supporting MySQL, PostgreSQL, SQL Server, Oracle, and MariaDB.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **🗄️ Database Instance** | Managed database server |
| **🔄 Multi-AZ** | High availability deployment |
| **📖 Read Replicas** | Read scaling |
| **💾 Automated Backups** | Point-in-time recovery |
| **📊 Monitoring** | CloudWatch integration |
| **🔒 Encryption** | At-rest and in-transit |

**Mental Model:** Think of RDS like a managed database server - AWS handles patching, backups, and scaling, so you focus on your application.

</div>

---

## 🗄️ Supported Engines

<div align="center">

### Database Engines

| Engine | Version | Use Case |
|:---:|:---:|:---:|
| **MySQL** | 5.7, 8.0 | Web applications, WordPress |
| **PostgreSQL** | 11-15 | Complex queries, JSON support |
| **SQL Server** | 2017-2022 | Enterprise applications |
| **Oracle** | 19c, 21c | Enterprise applications |
| **MariaDB** | 10.3-10.11 | MySQL alternative |
| **Aurora** | MySQL/PostgreSQL compatible | High performance |

---

### Choosing an Engine

| Factor | Consideration |
|:---:|:---:|
| **Application Requirements** | What does app need? |
| **Performance** | Aurora for high performance |
| **Cost** | MySQL/MariaDB cheapest |
| **Features** | PostgreSQL most features |
| **Compatibility** | Existing database type |

</div>

---

## 🏗️ Instance Types

<div align="center">

### Instance Classes

| Class | Description | Use Case |
|:---:|:---:|:---:|
| **db.t3** | Burstable performance | Development, testing |
| **db.t4g** | ARM-based burstable | Cost-effective |
| **db.m5** | General purpose | Production workloads |
| **db.r5** | Memory optimized | In-memory databases |
| **db.x1** | Memory optimized (large) | Very large databases |

---

### Instance Sizes

| Size | vCPUs | Memory | Use Case |
|:---:|:---:|:---:|:---:|
| **small** | 1-2 | 2-4 GB | Small applications |
| **large** | 2-4 | 8-16 GB | Medium applications |
| **xlarge** | 4-8 | 16-32 GB | Large applications |
| **2xlarge** | 8-16 | 32-64 GB | Very large applications |

</div>

---

## 🔄 High Availability

<div align="center">

### Multi-AZ Deployment

**Synchronous replication to standby in different AZ**

| Benefit | Description |
|:---:|:---:|
| **Automatic Failover** | < 60 seconds |
| **Data Durability** | Synchronous replication |
| **High Availability** | 99.95% SLA |
| **Maintenance** | No downtime |

---

### How Multi-AZ Works

```
Primary (us-east-1a) ←→ Standby (us-east-1b)
     ↓                        ↓
  Writes              Synchronous Replication
```

**Failover Process:**

1. Primary fails
2. DNS switches to standby
3. Standby becomes primary
4. New standby created

**💡 Automatic, < 60 seconds downtime.**

</div>

---

## 📖 Read Replicas

<div align="center">

### What are Read Replicas?

**Asynchronous copies for read scaling**

| Benefit | Description |
|:---:|:---:|
| **Read Scaling** | Distribute read traffic |
| **Cross-Region** | Global read scaling |
| **Disaster Recovery** | Can promote to primary |
| **Performance** | Reduce load on primary |

---

### Read Replica Configuration

| Setting | Description |
|:---:|:---:|
| **Same Region** | Low latency |
| **Cross-Region** | Global distribution |
| **Multi-AZ** | High availability |
| **Promotion** | Can become standalone |

**💡 Use for read-heavy workloads.**

</div>

---

## 💾 Backups

<div align="center">

### Automated Backups

**Automated daily backups with point-in-time recovery**

| Feature | Description |
|:---:|:---:|
| **Daily Backups** | During backup window |
| **Point-in-Time Recovery** | Restore to any second |
| **Retention** | 1-35 days |
| **Storage** | Free up to instance size |

---

### Manual Snapshots

**On-demand backups**

| Feature | Description |
|:---:|:---:|
| **On-Demand** | Create anytime |
| **Retention** | Until deleted |
| **Cross-Region** | Copy to other regions |
| **Cost** | Pay for storage |

---

### Backup Best Practices

| Practice | Why |
|:---:|:---:|
| **Enable automated backups** | Point-in-time recovery |
| **Test restores** | Verify backups work |
| **Cross-region snapshots** | Disaster recovery |
| **Appropriate retention** | Balance cost and recovery |

</div>

---

## 🔒 Security

<div align="center">

### Encryption

| Type | Description | Use Case |
|:---:|:---:|:---:|
| **At Rest** | Encrypt data on disk | Compliance, security |
| **In Transit** | SSL/TLS encryption | Secure connections |
| **KMS** | AWS KMS encryption keys | Key management |

---

### Network Security

**Best Practices:**
- Deploy in private subnets (VPC)
- Use Security Groups to control access
- Disable public access for security

For comprehensive VPC networking, subnets, Security Groups, and network security details, see **[VPC Networking Guide](./11-vpc-networking.md)**.

---

### Authentication

| Method | Description |
|:---:|:---:|
| **Database Credentials** | Username/password |
| **IAM Database Authentication** | IAM users/roles |
| **Secrets Manager** | Rotate credentials |

</div>

---

## 📊 Monitoring

<div align="center">

**RDS integrates with CloudWatch for comprehensive monitoring and Performance Insights for database-specific metrics.**

**Key Metrics:**
- CPU Utilization, Database Connections
- Free Storage Space, Read/Write IOPS
- Network throughput, Replication lag

**Performance Insights:**
- Query performance analysis
- Wait event identification
- Database bottleneck detection

For comprehensive CloudWatch monitoring, metrics, logs, alarms, and dashboards, see **[CloudWatch Monitoring Guide](./15-cloudwatch-monitoring.md)**.

</div>

---

## 🎯 Use Cases

<div align="center">

### When to Use RDS

| Use Case | Description |
|:---:|:---:|
| **Web Applications** | MySQL, PostgreSQL |
| **Enterprise Applications** | SQL Server, Oracle |
| **Content Management** | WordPress, Drupal |
| **E-commerce** | Transactional databases |

### When NOT to Use RDS

| Scenario | Alternative |
|:---:|:---:|
| **NoSQL needed** | DynamoDB |
| **Very large scale** | Aurora, DynamoDB |
| **Simple key-value** | DynamoDB |
| **Graph database** | Neptune |

</div>

---

## 💡 Best Practices

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Use Multi-AZ** | High availability |
| **Enable automated backups** | Data protection |
| **Use read replicas** | Read scaling |
| **Monitor performance** | CloudWatch, Performance Insights |
| **Encrypt sensitive data** | Security |
| **Deploy in private subnets** | Security |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Single AZ** | No redundancy | Multi-AZ |
| **No backups** | Data loss risk | Enable backups |
| **Public access** | Security risk | Private subnets |
| **Over-provisioning** | Wasted cost | Right-size instances |

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **RDS Purpose** | Managed relational databases |
| **Multi-AZ** | High availability, automatic failover |
| **Read Replicas** | Read scaling, cross-region |
| **Backups** | Automated + manual snapshots |
| **Security** | Encryption, VPC, security groups |

**💡 Remember:** RDS handles database management so you can focus on your application. Use Multi-AZ for production, read replicas for scaling reads.

</div>

---

<div align="center">

**Master RDS for managed databases! 🚀**

*Deploy and manage relational databases with RDS - high availability, backups, and scaling included.*

</div>

