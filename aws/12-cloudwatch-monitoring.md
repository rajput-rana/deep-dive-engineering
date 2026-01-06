# 📊 CloudWatch - Monitoring & Logging

<div align="center">

**Monitor AWS resources: metrics, logs, and alarms**

[![CloudWatch](https://img.shields.io/badge/CloudWatch-Monitoring-blue?style=for-the-badge)](./)
[![Metrics](https://img.shields.io/badge/Metrics-Real--Time-green?style=for-the-badge)](./)
[![Logs](https://img.shields.io/badge/Logs-Centralized-orange?style=for-the-badge)](./)

*Master CloudWatch: monitor resources, collect logs, and set up alarms*

</div>

---

## 🎯 What is CloudWatch?

<div align="center">

**CloudWatch monitors AWS resources and applications, collecting metrics, logs, and events.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **📊 Metrics** | Data points over time |
| **📝 Logs** | Application/system logs |
| **🚨 Alarms** | Automated actions on thresholds |
| **📈 Dashboards** | Visualize metrics |
| **🔍 Insights** | Query logs |
| **⚡ Events** | Event-driven automation |

**Mental Model:** Think of CloudWatch like a health monitoring system for your AWS resources - it tracks vital signs (metrics), keeps records (logs), and alerts you when something's wrong (alarms).

</div>

---

## 📊 Metrics

<div align="center">

### What are Metrics?

**Data points representing resource performance**

| Metric Type | Description | Example |
|:---:|:---:|:---:|
| **Default Metrics** | Automatic AWS metrics | EC2 CPU, S3 requests |
| **Custom Metrics** | Your application metrics | Application errors, custom KPIs |
| **High-Resolution** | 1-second granularity | Real-time monitoring |

---

### Common Metrics

| Service | Metrics |
|:---:|:---:|
| **EC2** | CPUUtilization, NetworkIn, NetworkOut |
| **S3** | BucketSize, NumberOfObjects |
| **RDS** | CPUUtilization, DatabaseConnections |
| **Lambda** | Invocations, Duration, Errors |

**💡 Metrics stored for 15 months.**

</div>

---

## 📝 Logs

<div align="center">

### What are Logs?

**Application and system logs**

| Log Source | Description |
|:---:|:---:|
| **CloudWatch Logs** | Application logs |
| **VPC Flow Logs** | Network traffic |
| **Route 53 Logs** | DNS queries |
| **Lambda Logs** | Function execution logs |

---

### Log Groups and Streams

| Concept | Description |
|:---:|:---:|
| **Log Group** | Container for logs |
| **Log Stream** | Sequence of log events |

**Example:**
```
Log Group: /aws/lambda/my-function
├── Log Stream: 2024/01/15/[LATEST]abc123
└── Log Stream: 2024/01/15/[LATEST]def456
```

</div>

---

## 🚨 Alarms

<div align="center">

### What are Alarms?

**Automated actions when metrics cross thresholds**

| Action | Description |
|:---:|:---:|
| **SNS Notification** | Send alert |
| **Auto Scaling** | Scale resources |
| **EC2 Actions** | Stop/terminate instances |

---

### Alarm States

| State | Description |
|:---:|:---:|
| **OK** | Within threshold |
| **ALARM** | Threshold breached |
| **INSUFFICIENT_DATA** | Not enough data |

**💡 Set up alarms for critical metrics.**

</div>

---

## 📈 Dashboards

<div align="center">

### What are Dashboards?

**Visualize metrics in custom dashboards**

| Feature | Description |
|:---:|:---:|
| **Custom Widgets** | Graphs, numbers, text |
| **Multiple Metrics** | Combine metrics |
| **Auto-Refresh** | Real-time updates |

**💡 Create dashboards for key metrics.**

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **CloudWatch Purpose** | Monitor AWS resources |
| **Metrics** | Performance data |
| **Logs** | Application/system logs |
| **Alarms** | Automated actions |
| **Dashboards** | Visualize metrics |

**💡 Remember:** CloudWatch is essential for observability. Monitor metrics, collect logs, and set up alarms for proactive issue detection.

</div>

---

<div align="center">

**Master CloudWatch for AWS observability! 🚀**

*Monitor resources, collect logs, and set up alarms with CloudWatch.*

</div>

