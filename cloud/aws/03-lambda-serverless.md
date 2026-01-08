# 🚀 Lambda - Serverless Compute

<div align="center">

**Run code without managing servers: serverless functions**

[![Lambda](https://img.shields.io/badge/Lambda-Serverless-blue?style=for-the-badge)](./)
[![Functions](https://img.shields.io/badge/Functions-Event%20Driven-green?style=for-the-badge)](./)
[![Serverless](https://img.shields.io/badge/Serverless-No%20Servers-orange?style=for-the-badge)](./)

*Master Lambda: build serverless applications with event-driven functions*

</div>

---

## 🎯 What is Lambda?

<div align="center">

**AWS Lambda is a serverless compute service that runs code in response to events without provisioning or managing servers.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **⚡ Function** | Your code (runs on demand) |
| **🎯 Event Source** | What triggers the function |
| **⏱️ Execution Time** | Up to 15 minutes |
| **💾 Memory** | 128 MB to 10 GB |
| **💰 Pricing** | Pay per request and compute time |
| **🔄 Concurrency** | Up to 1000 concurrent executions |

**Mental Model:** Think of Lambda like a vending machine - you put in a coin (event), and it automatically dispenses what you need (executes function) without you managing the machine.

</div>

---

## 🏗️ How Lambda Works

<div align="center">

### Execution Model

```
Event → Lambda Function → Execution → Response
         (Your Code)
```

**Process:**

1. **Event Trigger** - Event occurs (API call, file upload, etc.)
2. **Function Invocation** - Lambda receives event
3. **Execution** - Code runs in isolated environment
4. **Response** - Returns result (if synchronous)

---

### Supported Languages

| Language | Runtime | Use Case |
|:---:|:---:|:---:|
| **Node.js** | 18.x, 20.x | JavaScript/TypeScript |
| **Python** | 3.9, 3.10, 3.11 | Data processing, ML |
| **Java** | 11, 17 | Enterprise applications |
| **C#** | .NET 6, 7 | .NET applications |
| **Go** | 1.x | High-performance |
| **Ruby** | 3.2 | Ruby applications |
| **Custom Runtime** | Any | Bring your own runtime |

</div>

---

## 🎯 Event Sources

<div align="center">

### Common Event Sources

| Source | Description | Use Case |
|:---:|:---:|:---:|
| **API Gateway** | HTTP requests | REST APIs |
| **S3** | Object events | Image processing, backups |
| **DynamoDB** | Stream events | Real-time processing |
| **SQS** | Queue messages | Async processing |
| **SNS** | Notifications | Fanout, alerts |
| **EventBridge** | Custom events | Event-driven architecture |
| **CloudWatch Events** | Scheduled | Cron jobs, automation |
| **Kinesis** | Streams | Real-time analytics |

---

### Invocation Types

| Type | Description | Use Case |
|:---:|:---:|:---:|
| **Synchronous** | Wait for response | API Gateway, CLI |
| **Asynchronous** | Fire and forget | S3, SNS |
| **Stream-based** | Process records | Kinesis, DynamoDB Streams |

</div>

---

## 💰 Lambda Pricing

<div align="center">

### Pricing Model

**Two Components:**

1. **Requests** - $0.20 per 1M requests
2. **Compute Time** - $0.0000166667 per GB-second

**Free Tier:**

- ✅ 1M free requests/month
- ✅ 400,000 GB-seconds compute time/month

---

### Cost Example

**Scenario:**
- 1M requests/month
- 512 MB memory
- 200ms average duration

**Calculation:**
```
Requests: 1M × $0.20/1M = $0.20
Compute: 1M × 0.5 GB × 0.2s × $0.0000166667 = $1.67
Total: $1.87/month
```

**💡 Very cost-effective for low to medium traffic.**

</div>

---

## ⚙️ Configuration

<div align="center">

### Function Configuration

| Setting | Description | Range |
|:---:|:---:|:---:|
| **Memory** | RAM allocation | 128 MB - 10 GB |
| **Timeout** | Max execution time | 1s - 15 minutes |
| **Environment Variables** | Configuration | Key-value pairs |
| **VPC** | Network configuration | VPC, subnets, security groups |
| **Reserved Concurrency** | Limit concurrent executions | 0 - Account limit |

---

### Memory and CPU

**Important:** CPU scales proportionally with memory

| Memory | vCPU Allocation |
|:---:|:---:|
| 128-3008 MB | 1 vCPU |
| 3009-1769 MB | 2 vCPU |
| 1770+ MB | Up to 6 vCPU |

**💡 More memory = more CPU power.**

</div>

---

## 🔄 Lambda Layers

<div align="center">

### What are Layers?

**Package dependencies separately from function code**

| Benefit | Description |
|:---:|:---:|
| **Smaller Deployments** | Code package smaller |
| **Reusability** | Share across functions |
| **Faster Updates** | Update layer, not function |
| **Size Limit** | Can exceed 50MB limit |

---

### Layer Structure

```
layer.zip
├── python/
│   └── lib/
│       └── package/
└── nodejs/
    └── node_modules/
```

**Max Size:** 250 MB (unzipped)

</div>

---

## 🔐 Security

<div align="center">

### Execution Role

**IAM role Lambda assumes when executing**

**Permissions Needed:**

- ✅ Access AWS services (S3, DynamoDB, etc.)
- ✅ Write CloudWatch Logs
- ✅ Access VPC resources (if configured)

---

### VPC Configuration

**When to Use:**
- Access private resources (RDS, ElastiCache)
- Access resources in VPC

**Considerations:**
- Cold starts slower (ENI creation)
- Additional cost (NAT Gateway)
- Timeout considerations

For comprehensive VPC networking details including subnets, security groups, and NAT Gateway configuration, see **[VPC Networking Guide](./11-vpc-networking.md)**.

</div>

---

## 📊 Best Practices

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Keep functions small** | Faster cold starts |
| **Use environment variables** | Configuration management |
| **Enable X-Ray** | Distributed tracing |
| **Set appropriate timeout** | Cost optimization |
| **Use layers** | Reusability, smaller packages |
| **Handle errors gracefully** | Retry logic, DLQ |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Long-running functions** | Timeout, cost | Use Step Functions |
| **Large packages** | Slow cold starts | Use layers |
| **Synchronous for async** | Blocking | Use async invocation |
| **No error handling** | Lost events | Use DLQ |

</div>

---

## 🎯 Use Cases

<div align="center">

### When to Use Lambda

| Use Case | Description |
|:---:|:---:|
| **API Backends** | REST APIs with API Gateway |
| **Event Processing** | S3, DynamoDB, Kinesis events |
| **Scheduled Tasks** | Cron jobs, automation |
| **Data Transformation** | ETL pipelines |
| **Real-time Processing** | Stream processing |

### When NOT to Use Lambda

| Scenario | Alternative |
|:---:|:---:|
| **Long-running tasks** | EC2, ECS |
| **Always-on services** | EC2, ECS |
| **Large applications** | Containers (ECS, EKS) |
| **Stateful applications** | EC2, ECS |

</div>

---

## 🔄 Cold Starts

<div align="center">

### What is a Cold Start?

**Delay when Lambda initializes execution environment**

| Phase | Description | Duration |
|:---:|:---:|:---:|
| **Init** | Create execution environment | 100-1000ms |
| **Invoke** | Execute function code | Function duration |

---

### Reducing Cold Starts

| Strategy | Impact |
|:---:|:---:|
| **Provisioned Concurrency** | Eliminates cold starts |
| **Smaller packages** | Faster initialization |
| **Keep functions warm** | Periodic invocations |
| **Use ARM architecture** | Lower cost, similar performance |

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **Lambda Purpose** | Serverless function execution |
| **Event-Driven** | Triggers from various sources |
| **Pricing** | Pay per request and compute time |
| **Cold Starts** | Initialization delay |
| **Best For** | Event-driven, short-running tasks |

**💡 Remember:** Lambda is perfect for event-driven, short-running tasks. Keep functions small, handle errors, and optimize for cold starts.

</div>

---

<div align="center">

**Master Lambda for serverless applications! 🚀**

*Build event-driven, serverless applications with Lambda - no servers to manage.*

</div>

