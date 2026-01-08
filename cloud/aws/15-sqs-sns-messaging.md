# 📨 SQS & SNS - Messaging Services

<div align="center">

**Decouple applications: queues and notifications**

[![SQS](https://img.shields.io/badge/SQS-Queues-blue?style=for-the-badge)](./)
[![SNS](https://img.shields.io/badge/SNS-Notifications-green?style=for-the-badge)](./)
[![Messaging](https://img.shields.io/badge/Messaging-Decoupled-orange?style=for-the-badge)](./)

*Master SQS and SNS: message queues and pub/sub messaging*

</div>

---

## 🎯 SQS - Simple Queue Service

<div align="center">

**SQS is a fully managed message queuing service for decoupling applications.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **📨 Queue** | Message container |
| **📄 Message** | Data to process |
| **👁️ Visibility Timeout** | Hide message after read |
| **🔄 Dead Letter Queue** | Failed messages |
| **⚡ FIFO** | First-in-first-out |

**Mental Model:** Think of SQS like a post office box - messages are delivered to the queue, and workers pick them up and process them asynchronously.

</div>

---

## 📊 Queue Types

<div align="center">

### Standard vs FIFO

| Aspect | Standard | FIFO |
|:---:|:---:|:---:|
| **Ordering** | Best-effort | Strict order |
| **Duplicates** | At-least-once | Exactly-once |
| **Throughput** | Unlimited | 3,000/second |
| **Use Case** | High throughput | Order matters |

---

### When to Use Each

| Scenario | Use |
|:---:|:---:|
| **High throughput** | Standard |
| **Order matters** | FIFO |
| **No duplicates** | FIFO |
| **Simple queuing** | Standard |

</div>

---

## 📨 SNS - Simple Notification Service

<div align="center">

**SNS is a pub/sub messaging service for fanout messaging.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **📢 Topic** | Communication channel |
| **👥 Subscribers** | Endpoints receiving messages |
| **📤 Publisher** | Sends messages |
| **🔄 Fanout** | One message to many |

**Mental Model:** Think of SNS like a radio station - one broadcast (message) reaches all listeners (subscribers) simultaneously.

</div>

---

## 🎯 Use Cases

<div align="center">

### SQS Use Cases

| Use Case | Description |
|:---:|:---:|
| **Async Processing** | Decouple producers/consumers |
| **Work Queues** | Task distribution |
| **Buffer** | Smooth traffic spikes |

### SNS Use Cases

| Use Case | Description |
|:---:|:---:|
| **Notifications** | Email, SMS alerts |
| **Fanout** | One message to many |
| **Event Distribution** | Event-driven architecture |

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **SQS Purpose** | Message queuing |
| **SNS Purpose** | Pub/sub messaging |
| **SQS Types** | Standard (high throughput), FIFO (ordered) |
| **SNS Fanout** | One message to many subscribers |
| **Use Together** | SNS → SQS for fanout to queues |

**💡 Remember:** Use SQS for queuing, SNS for notifications and fanout. Combine them for event-driven architectures.

</div>

---

<div align="center">

**Master SQS and SNS for decoupled architectures! 🚀**

*Use SQS for message queuing and SNS for pub/sub messaging to build scalable, decoupled applications.*

</div>

