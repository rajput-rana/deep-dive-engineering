# 💾 S3 - Simple Storage Service

<div align="center">

**Object storage: store and retrieve any amount of data**

[![S3](https://img.shields.io/badge/S3-Object%20Storage-blue?style=for-the-badge)](./)
[![Storage](https://img.shields.io/badge/Storage-Scalable-green?style=for-the-badge)](./)
[![Durability](https://img.shields.io/badge/Durability-99.999999999-orange?style=for-the-badge)](./)

*Master S3: buckets, objects, versioning, lifecycle policies, and best practices*

</div>

---

## 🎯 What is S3?

<div align="center">

**S3 (Simple Storage Service) is object storage for storing and retrieving any amount of data at any time.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **🪣 Bucket** | Container for objects (globally unique name) |
| **📄 Object** | File + metadata (up to 5 TB) |
| **🔑 Key** | Object identifier (path-like) |
| **🌍 Region** | Geographic location |
| **🔒 Versioning** | Keep multiple versions |
| **📊 Lifecycle** | Automatic transitions |

**Mental Model:** Think of S3 like a massive filing cabinet in the cloud - you organize files (objects) into drawers (buckets), and can retrieve them anytime from anywhere.

</div>

---

## 🏗️ S3 Architecture

<div align="center">

### Bucket Structure

```
Bucket: my-app-bucket
├── images/
│   ├── photo1.jpg (key: images/photo1.jpg)
│   └── photo2.jpg (key: images/photo2.jpg)
├── data/
│   └── file.csv (key: data/file.csv)
└── logs/
    └── app.log (key: logs/app.log)
```

---

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **Flat Structure** | No true folders (prefixes) |
| **Unlimited Objects** | No limit on objects |
| **99.999999999% Durability** | 11 nines |
| **99.99% Availability** | SLA |
| **Global Namespace** | Bucket names must be unique |

</div>

---

## 💾 Storage Classes

<div align="center">

### Storage Class Comparison

| Class | Use Case | Durability | Availability | Cost |
|:---:|:---:|:---:|:---:|:---:|
| **Standard** | Frequently accessed | 99.999999999% | 99.99% | Highest |
| **Intelligent-Tiering** | Unknown access patterns | 99.999999999% | 99.99% | Automatic optimization |
| **Standard-IA** | Infrequently accessed | 99.999999999% | 99.9% | Lower |
| **One Zone-IA** | Non-critical, infrequent | 99.5% | 99.5% | Lower |
| **Glacier Instant Retrieval** | Archive, instant access | 99.999999999% | 99.9% | Very low |
| **Glacier Flexible Retrieval** | Archive, flexible retrieval | 99.999999999% | 99.99% | Very low |
| **Glacier Deep Archive** | Long-term archive | 99.999999999% | 99.99% | Lowest |

---

### When to Use Each

| Storage Class | Best For |
|:---:|:---:|
| **Standard** | Active data, websites, applications |
| **Intelligent-Tiering** | Unknown access patterns |
| **Standard-IA** | Backup, disaster recovery |
| **Glacier Instant** | Archive with instant access |
| **Glacier Flexible** | Archive, can wait minutes/hours |
| **Glacier Deep Archive** | Long-term archive, can wait 12 hours |

</div>

---

## 🔄 Versioning

<div align="center">

### What is Versioning?

**Keep multiple versions of objects**

| Feature | Description |
|:---:|:---:|
| **Multiple Versions** | Keep all versions |
| **Delete Protection** | Delete markers instead of deletion |
| **MFA Delete** | Require MFA for deletion |
| **Cost** | Pay for all versions |

---

### Versioning States

| State | Description |
|:---:|:---:|
| **Unversioned** | Default (no versioning) |
| **Enabled** | Keep all versions |
| **Suspended** | Stop creating new versions |

**Example:**
```
photo.jpg (version 1) - 1 MB
photo.jpg (version 2) - 1.2 MB
photo.jpg (version 3) - 1.5 MB
```

**All versions stored, pay for all.**

</div>

---

## 📊 Lifecycle Policies

<div align="center">

### What are Lifecycle Policies?

**Automatically transition objects between storage classes**

### Common Transitions

| Rule | Description | Example |
|:---:|:---:|:---:|
| **Transition** | Move to different class | Standard → Glacier after 90 days |
| **Expiration** | Delete objects | Delete logs after 365 days |
| **Abort Multipart** | Clean up incomplete uploads | Delete after 7 days |

---

### Lifecycle Policy Example

```json
{
  "Rules": [
    {
      "Id": "Move to Glacier",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ]
    },
    {
      "Id": "Delete old logs",
      "Status": "Enabled",
      "Expiration": {
        "Days": 365
      }
    }
  ]
}
```

</div>

---

## 🔐 Security

<div align="center">

### Access Control

| Method | Description | Use Case |
|:---:|:---:|:---:|
| **Bucket Policies** | JSON policies for bucket | Public access, cross-account |
| **ACLs** | Legacy access control | Simple permissions |
| **IAM Policies** | User/role permissions | Fine-grained control |
| **Pre-signed URLs** | Temporary access | Time-limited access |

---

### Encryption

| Type | Description | Use Case |
|:---:|:---:|:---:|
| **SSE-S3** | S3-managed keys | Default encryption |
| **SSE-KMS** | KMS-managed keys | Audit, control |
| **SSE-C** | Customer-provided keys | Full control |
| **Client-Side** | Encrypt before upload | Maximum security |

---

### Public Access

**Block Public Access Settings:**

- ✅ Block all public access (recommended)
- ✅ Block public ACLs
- ✅ Block public policies
- ✅ Block cross-account public access

**💡 Default: All public access blocked.**

</div>

---

## 🌐 S3 Website Hosting

<div align="center">

### Static Website Hosting

**Host static websites from S3**

**Configuration:**

1. Enable static website hosting
2. Set index document (index.html)
3. Set error document (error.html)
4. Configure bucket policy for public read

**URL Format:**
```
http://bucket-name.s3-website-region.amazonaws.com
```

**💡 Use CloudFront for HTTPS and custom domain.**

</div>

---

## 📊 Performance

<div align="center">

### Request Rates

| Operation | Performance |
|:---:|:---:|
| **PUT/COPY/POST/DELETE** | 3,500 requests/second |
| **GET/HEAD** | 5,500 requests/second |

**💡 Can request higher limits if needed.**

---

### Transfer Acceleration

**Faster uploads using CloudFront edge locations**

| Benefit | Description |
|:---:|:---:|
| **Faster Uploads** | Uses CloudFront network |
| **Global Reach** | Closest edge location |
| **Cost** | Additional transfer cost |

**Use When:** Uploading from distant locations

</div>

---

## 💰 Pricing

<div align="center">

### Cost Components

| Component | Description | Example |
|:---:|:---:|:---:|
| **Storage** | Per GB/month | $0.023/GB (Standard) |
| **Requests** | Per request | $0.005 per 1,000 PUT |
| **Data Transfer** | Outbound data | $0.09/GB (first 10 TB) |
| **Storage Management** | Lifecycle, analytics | Varies |

---

### Cost Optimization

| Strategy | Savings |
|:---:|:---:|
| **Lifecycle Policies** | Move to cheaper classes |
| **Intelligent-Tiering** | Automatic optimization |
| **Compression** | Reduce storage size |
| **Delete Old Data** | Reduce storage |

</div>

---

## 🎯 Use Cases

<div align="center">

### Common Use Cases

| Use Case | Description |
|:---:|:---:|
| **Backup & Archive** | Data backup, long-term storage |
| **Static Websites** | Host static sites |
| **Data Lakes** | Big data storage |
| **Media Storage** | Images, videos, files |
| **Log Storage** | Application logs |
| **Disaster Recovery** | Backup and recovery |

</div>

---

## 💡 Best Practices

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Use lifecycle policies** | Cost optimization |
| **Enable versioning** | Data protection |
| **Use appropriate storage class** | Cost optimization |
| **Enable encryption** | Security |
| **Use bucket policies** | Access control |
| **Enable CloudTrail** | Audit logging |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Public buckets** | Security risk | Block public access |
| **No versioning** | Data loss risk | Enable versioning |
| **Standard for archive** | High cost | Use Glacier |
| **No lifecycle policies** | Accumulating costs | Set up policies |

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **S3 Purpose** | Object storage for any data |
| **Storage Classes** | Choose based on access patterns |
| **Versioning** | Keep multiple versions |
| **Lifecycle Policies** | Automatic cost optimization |
| **Security** | Encryption, access control |

**💡 Remember:** S3 is durable, scalable, and cost-effective. Use lifecycle policies and appropriate storage classes to optimize costs.

</div>

---

<div align="center">

**Master S3 for scalable object storage! 🚀**

*Store and retrieve any amount of data with S3 - durable, scalable, and cost-effective.*

</div>

