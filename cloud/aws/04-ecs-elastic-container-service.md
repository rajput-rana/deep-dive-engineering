# 🐳 ECS - Elastic Container Service

<div align="center">

**Fully managed container orchestration: run Docker containers at scale**

[![ECS](https://img.shields.io/badge/ECS-Containers-blue?style=for-the-badge)](./)
[![Docker](https://img.shields.io/badge/Docker-Orchestration-green?style=for-the-badge)](./)
[![Fargate](https://img.shields.io/badge/Fargate-Serverless-orange?style=for-the-badge)](./)

*Master ECS: deploy, manage, and scale containerized applications on AWS*

</div>

---

## 🎯 What is ECS?

<div align="center">

**Amazon ECS (Elastic Container Service) is a fully managed container orchestration service that makes it easy to run, stop, and manage Docker containers on AWS.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **🐳 Container** | Docker container running your application |
| **📦 Task Definition** | Blueprint for your containers |
| **🚀 Task** | Running instance of a task definition |
| **⚙️ Service** | Maintains desired number of tasks |
| **🏗️ Cluster** | Logical grouping of resources |
| **💻 Launch Type** | EC2 or Fargate |

**Mental Model:** Think of ECS as a container management system - you define what containers to run (task definitions), how many to run (services), and where to run them (clusters), and ECS handles the orchestration.

</div>

---

## 🚀 Launch Types

### EC2 Launch Type

<div align="center">

**Run containers on EC2 instances you manage**

| Aspect | Details |
|:---:|:---:|:---:|
| **Control** | Full control over instances |
| **Cost** | Pay for EC2 instances |
| **Management** | You manage instances |
| **Use Case** | Need specific instance types, custom AMIs |

</div>

**When to Use:**
- Need specific instance types or configurations
- Want to use Reserved Instances for cost savings
- Need custom AMIs or kernel parameters
- Need GPU instances

### Fargate Launch Type

<div align="center">

**Serverless containers - no EC2 instances to manage**

| Aspect | Details |
|:---:|:---:|:---:|
| **Control** | AWS manages infrastructure |
| **Cost** | Pay per task (CPU/memory) |
| **Management** | Fully managed by AWS |
| **Use Case** | Simple container deployments |

</div>

**When to Use:**
- Want serverless container experience
- Don't want to manage EC2 instances
- Simple container workloads
- Variable workloads

### Launch Type Comparison

<div align="center">

| Feature | EC2 Launch Type | Fargate |
|:---:|:---:|:---:|
| **Infrastructure Management** | You manage | AWS manages |
| **Cost Model** | Per instance | Per task |
| **Best For** | Cost optimization, control | Simplicity, serverless |

</div>

---

## 📦 Task Definitions

<div align="center">

**Blueprint for your containers**

| Component | Description |
|:---:|:---:|
| **Container Image** | Docker image to use |
| **CPU/Memory** | Resource requirements |
| **Port Mappings** | Container ports to expose |
| **Environment Variables** | Container configuration |
| **Task Role** | IAM role for tasks (access AWS services) |
| **Execution Role** | IAM role for ECS agent (pull images, write logs) |

</div>

**Key Fields:**
- **Image:** Docker image (from ECR)
- **CPU:** CPU units (1024 = 1 vCPU)
- **Memory:** Memory in MB
- **Port Mappings:** Container ports to expose
- **Environment Variables:** Configuration
- **Log Configuration:** CloudWatch Logs integration

---

## ⚙️ Services

<div align="center">

**Maintain desired number of tasks**

| Feature | Description |
|:---:|:---:|
| **Desired Count** | Number of tasks to maintain |
| **Load Balancing** | Distribute traffic |
| **Auto Scaling** | Scale based on metrics |
| **Deployment** | Rolling updates |

</div>

**Service Features:**
- Maintains desired number of tasks
- Restarts failed tasks
- Distributes tasks across availability zones
- Integrates with load balancers
- Supports auto-scaling based on CPU, memory, or custom metrics

---

## 🏗️ Clusters

<div align="center">

**Logical grouping of infrastructure**

| Cluster Type | Description | Use Case |
|:---:|:---:|:---:|
| **EC2 Cluster** | EC2 instances | EC2 launch type |
| **Fargate Cluster** | Serverless | Fargate launch type |

</div>

**Capacity Providers:**
- **EC2:** Traditional EC2 instances
- **Fargate:** Serverless containers
- **Fargate Spot:** Cost-optimized Fargate

---

## 🌐 Networking

<div align="center">

**How containers connect to network**

| Mode | Description | Launch Type |
|:---:|:---:|:---:|
| **awsvpc** | Each task gets ENI | Fargate, EC2 |
| **bridge** | Docker bridge network | EC2 only |
| **host** | Host network | EC2 only |

</div>

**awsvpc Mode (Recommended):**
- Each task gets its own ENI
- Full VPC integration
- Security groups per task
- Required for Fargate
- Best for production

For comprehensive VPC networking details, see **[VPC Networking Guide](./11-vpc-networking.md)**.

---

## 📊 Auto Scaling

<div align="center">

**Scale services based on demand**

| Metric | Description |
|:---:|:---:|
| **CPU Utilization** | Average CPU usage |
| **Memory Utilization** | Average memory usage |
| **ALB Request Count** | Requests per target |
| **Custom Metrics** | Application metrics |

</div>

**Scaling Policies:**
- **Target Tracking:** Maintain target metric value
- **Step Scaling:** Scale based on metric thresholds
- **Scheduled Scaling:** Scale at specific times

---

## 🔐 Security

<div align="center">

**Security best practices**

| Practice | Description |
|:---:|:---:|
| **Task Roles** | Least privilege IAM roles |
| **Security Groups** | Network-level security |
| **Secrets Management** | Use Secrets Manager |
| **Image Scanning** | Scan container images |
| **Network Isolation** | Use private subnets |

</div>

**IAM Roles:**
- **Task Role:** Permissions for application (access S3, DynamoDB, etc.)
- **Execution Role:** Permissions for ECS agent (pull images, write logs)

---

## 📈 Monitoring

<div align="center">

**ECS integrates with CloudWatch for monitoring**

| Feature | Description |
|:---:|:---:|
| **Container Insights** | Enhanced metrics |
| **CloudWatch Logs** | Centralized logging |
| **Metrics** | CPU, memory, network |

</div>

For comprehensive CloudWatch monitoring details, see **[CloudWatch Monitoring Guide](./15-cloudwatch-monitoring.md)**.

---

## 💰 Pricing

<div align="center">

**ECS pricing model**

| Launch Type | Cost |
|:---:|:---:|
| **EC2** | Pay for EC2 instances |
| **Fargate** | Pay per task (CPU + memory) |

</div>

**Cost Optimization:**
- Use Reserved Instances for EC2 launch type
- Use Fargate Spot for cost savings
- Right-size CPU and memory
- Use auto-scaling

---

## 🎯 Use Cases

<div align="center">

| Use Case | Description | Launch Type |
|:---:|:---:|:---:|
| **Web Applications** | Stateless web apps | Fargate or EC2 |
| **Microservices** | Containerized services | Fargate |
| **Batch Processing** | Scheduled jobs | EC2 with Spot |
| **CI/CD** | Build and test pipelines | EC2 |

</div>

---

## 💡 Best Practices

<div align="center">

| Practice | Description |
|:---:|:---:|
| **Right-Size Resources** | Match CPU/memory to needs |
| **Use Fargate for Simplicity** | When you don't need EC2 control |
| **Enable Auto Scaling** | Scale based on demand |
| **Use Task Roles** | Least privilege access |
| **Enable Container Insights** | Enhanced monitoring |

</div>

---

## 🔗 Related Services

<div align="center">

| Service | Purpose | Integration |
|:---:|:---:|:---:|
| **ECR** | Container registry | Store images |
| **ALB/NLB** | Load balancing | Distribute traffic |
| **CloudWatch** | Monitoring | Metrics and logs |
| **IAM** | Access control | Task and execution roles |
| **VPC** | Networking | Network isolation |

</div>

---

## 📚 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **Launch Types** | EC2 for control, Fargate for simplicity |
| **Task Definitions** | Blueprint for containers |
| **Services** | Maintain desired count |
| **Auto Scaling** | Scale based on metrics |
| **Networking** | awsvpc mode for production |

**💡 Remember:** ECS simplifies container orchestration. Choose Fargate for simplicity or EC2 for cost optimization and control.

</div>

---

<div align="center">

**Master ECS for containerized applications! 🚀**

*Deploy, manage, and scale Docker containers with AWS ECS.*

</div>
