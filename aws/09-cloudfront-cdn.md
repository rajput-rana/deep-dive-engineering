# 🌐 CloudFront - Content Delivery Network

<div align="center">

**Global content delivery: faster, secure content distribution**

[![CloudFront](https://img.shields.io/badge/CloudFront-CDN-blue?style=for-the-badge)](./)
[![CDN](https://img.shields.io/badge/CDN-Global-green?style=for-the-badge)](./)
[![Performance](https://img.shields.io/badge/Performance-Low%20Latency-orange?style=for-the-badge)](./)

*Master CloudFront: distribute content globally with low latency and high performance*

</div>

---

## 🎯 What is CloudFront?

<div align="center">

**CloudFront is a Content Delivery Network (CDN) that delivers content globally with low latency and high transfer speeds.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **🌍 Distribution** | CloudFront configuration |
| **📍 Edge Locations** | Servers worldwide (400+ locations) |
| **🎯 Origin** | Source of content (S3, EC2, etc.) |
| **💾 Cache** | Store content at edge locations |
| **🔒 SSL/TLS** | HTTPS encryption |
| **⚡ TTL** | Time-to-live for cached content |

**Mental Model:** Think of CloudFront like a global network of local libraries - instead of going to the main library (origin), you get books (content) from the nearest branch (edge location), making it much faster.

</div>

---

## 🏗️ How CloudFront Works

<div align="center">

### Request Flow

```
User Request → Edge Location → Cache Check
                    ↓
              Cache Hit? → Return Cached Content
                    ↓
              Cache Miss? → Fetch from Origin → Cache → Return
```

---

### Edge Locations

| Location Type | Description | Use Case |
|:---:|:---:|:---:|
| **Edge Locations** | Cache content | Content delivery |
| **Regional Edge Caches** | Larger cache | Less popular content |

**💡 400+ edge locations worldwide.**

</div>

---

## 🎯 Origins

<div align="center">

### Origin Types

| Origin | Description | Use Case |
|:---:|:---:|:---:|
| **S3 Bucket** | Static content | Websites, images, videos |
| **EC2 Instance** | Dynamic content | Applications |
| **ELB** | Load balancer | Multiple instances |
| **API Gateway** | APIs | REST APIs |
| **Custom Origin** | Any HTTP server | External sources |

---

### Origin Configuration

| Setting | Description |
|:---:|:---:|
| **Origin Domain** | Source of content |
| **Origin Path** | Path prefix |
| **Origin Shield** | Additional caching layer |
| **Custom Headers** | Add headers to origin requests |

</div>

---

## 💾 Caching

<div align="center">

### Cache Behavior

**Control how CloudFront caches content**

| Behavior | Description | Use Case |
|:---:|:---:|:---:|
| **Cache Based on** | Headers, query strings, cookies | Custom caching |
| **TTL** | How long to cache | Balance freshness vs performance |
| **Compress** | Gzip compression | Reduce bandwidth |

---

### Cache Invalidation

**Remove content from cache before TTL expires**

| Method | Description | Cost |
|:---:|:---:|:---:|
| **Invalidation** | Remove specific paths | First 1000 free/month |
| **Versioning** | Use query strings | Free |
| **TTL Expiration** | Wait for TTL | Free |

**💡 Use versioning (query strings) instead of invalidation when possible.**

</div>

---

## 🔒 Security

<div align="center">

### SSL/TLS

**HTTPS encryption for secure content delivery**

| Feature | Description |
|:---:|:---:|
| **Default Certificate** | *.cloudfront.net |
| **Custom Certificate** | Your domain (ACM) |
| **SSL/TLS Versions** | TLS 1.2, 1.3 |
| **Minimum Protocol** | Enforce TLS version |

---

### Access Control

| Method | Description | Use Case |
|:---:|:---:|:---:|
| **Signed URLs** | Time-limited access | Private content |
| **Signed Cookies** | Cookie-based access | Private websites |
| **Origin Access Identity** | Restrict S3 access | S3 bucket protection |
| **WAF** | Web Application Firewall | DDoS protection |

</div>

---

## ⚡ Performance Features

<div align="center">

### Optimization Features

| Feature | Description | Benefit |
|:---:|:---:|:---:|
| **HTTP/2** | Modern protocol | Faster, multiplexing |
| **HTTP/3** | QUIC protocol | Even faster |
| **Compression** | Gzip/Brotli | Smaller files |
| **Field-Level Encryption** | Encrypt sensitive fields | Security |

---

### Real-Time Metrics

**Monitor CloudFront performance**

| Metric | Description |
|:---:|:---:|
| **Requests** | Number of requests |
| **Data Transfer** | Bytes transferred |
| **Cache Hit Ratio** | % served from cache |
| **Error Rate** | 4xx, 5xx errors |

</div>

---

## 💰 Pricing

<div align="center">

### Cost Components

| Component | Description | Cost |
|:---:|:---:|:---:|
| **Data Transfer Out** | Per GB | $0.085/GB (first 10 TB) |
| **HTTP/HTTPS Requests** | Per 10,000 | $0.0075 |
| **Invalidation** | Per path | First 1000 free/month |

---

### Cost Optimization

| Strategy | Savings |
|:---:|:---:|
| **Higher cache hit ratio** | Less origin requests |
| **Compression** | Less data transfer |
| **Regional restrictions** | Reduce costs |

</div>

---

## 🎯 Use Cases

<div align="center">

### When to Use CloudFront

| Use Case | Description |
|:---:|:---:|
| **Static Websites** | S3 + CloudFront |
| **API Acceleration** | API Gateway + CloudFront |
| **Video Streaming** | Media delivery |
| **Global Applications** | Low latency worldwide |
| **Security** | DDoS protection, WAF |

### When NOT to Use CloudFront

| Scenario | Alternative |
|:---:|:---:|
| **Single region** | Direct origin access |
| **Very dynamic content** | May not benefit |
| **Small traffic** | May not be cost-effective |

</div>

---

## 💡 Best Practices

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Use appropriate TTL** | Balance freshness vs cache hits |
| **Enable compression** | Reduce bandwidth |
| **Use custom domains** | Brand consistency |
| **Monitor cache hit ratio** | Performance optimization |
| **Use signed URLs for private** | Security |
| **Enable WAF** | Security protection |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Too short TTL** | Low cache hit ratio | Increase TTL |
| **No compression** | Higher costs | Enable compression |
| **Public sensitive data** | Security risk | Use signed URLs |

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **CloudFront Purpose** | Global content delivery |
| **Edge Locations** | 400+ locations worldwide |
| **Caching** | Store content at edge |
| **Origins** | S3, EC2, API Gateway, etc. |
| **Security** | SSL/TLS, signed URLs, WAF |

**💡 Remember:** CloudFront accelerates content delivery globally. Use appropriate TTLs, enable compression, and leverage caching for best performance.

</div>

---

<div align="center">

**Master CloudFront for global content delivery! 🚀**

*Deliver content globally with low latency using CloudFront CDN.*

</div>

