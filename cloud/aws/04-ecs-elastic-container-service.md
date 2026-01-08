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

## 🏗️ ECS Architecture

<div align="center">

### Core Components

| Component | Description | Purpose |
|:---:|:---:|:---:|
| **Cluster** | Logical grouping of infrastructure | Organize resources |
| **Task Definition** | Container blueprint | Define what to run |
| **Task** | Running container instance | Actual running container |
| **Service** | Maintains desired count | Auto-scaling and availability |
| **Container Instance** | EC2 instance running ECS agent | Host for containers (EC2 launch type) |

</div>

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      ECS Cluster                         │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Task Definition                     │   │
│  │  - Container image                              │   │
│  │  - CPU/Memory requirements                      │   │
│  │  - Environment variables                        │   │
│  │  - Networking mode                             │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                              │
│                          ▼                              │
│  ┌──────────────────────────────────────────────────┐   │
│  │                  ECS Service                     │   │
│  │  - Desired count: 3                             │   │
│  │  - Load balancer                                │   │
│  │  - Auto-scaling                                 │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                              │
│                          ▼                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    Task 1    │  │    Task 2    │  │    Task 3    │  │
│  │  (Container) │  │  (Container) │  │  (Container) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  Launch Type: EC2 or Fargate                            │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Launch Types

### EC2 Launch Type

<div align="center">

**Run containers on EC2 instances you manage**

| Aspect | Details |
|:---:|:---:|
| **Control** | Full control over instances |
| **Cost** | Pay for EC2 instances |
| **Management** | You manage instances |
| **Scaling** | Manual or auto-scaling |
| **Use Case** | Need specific instance types, custom AMIs |

</div>

**Characteristics:**
- You provision and manage EC2 instances
- ECS agent runs on instances
- Full control over instance types, AMIs, networking
- Can use Reserved Instances or Spot Instances
- More cost-effective for steady workloads
- You're responsible for patching and maintenance

**When to Use:**
- Need specific instance types or configurations
- Want to use Reserved Instances for cost savings
- Need custom AMIs or kernel parameters
- Have existing EC2 infrastructure
- Need GPU instances

### Fargate Launch Type

<div align="center">

**Serverless containers - no EC2 instances to manage**

| Aspect | Details |
|:---:|:---:|
| **Control** | AWS manages infrastructure |
| **Cost** | Pay per task (CPU/memory) |
| **Management** | Fully managed by AWS |
| **Scaling** | Automatic |
| **Use Case** | Simple container deployments |

</div>

**Characteristics:**
- No EC2 instances to manage
- AWS manages the infrastructure
- Pay only for running tasks
- Automatic scaling
- Simplified operations
- Higher cost per task than EC2

**When to Use:**
- Want serverless container experience
- Don't want to manage EC2 instances
- Simple container workloads
- Variable workloads
- Quick deployments

### Launch Type Comparison

<div align="center">

| Feature | EC2 Launch Type | Fargate |
|:---:|:---:|:---:|
| **Infrastructure Management** | You manage | AWS manages |
| **Cost Model** | Per instance | Per task |
| **Instance Types** | Full control | Limited options |
| **Scaling** | Manual/auto | Automatic |
| **Networking** | Full control | Simplified |
| **Best For** | Cost optimization, control | Simplicity, serverless |

</div>

---

## 📦 Task Definitions

<div align="center">

**Blueprint for your containers**

| Component | Description | Example |
|:---:|:---:|:---:|
| **Container Definitions** | Image, CPU, memory, ports | nginx:latest, 512 CPU, 1024 MB |
| **Task Role** | IAM role for tasks | Access S3, DynamoDB |
| **Network Mode** | Bridge, host, awsvpc | awsvpc for Fargate |
| **Volumes** | Data persistence | EFS, EBS |
| **Environment Variables** | Container configuration | DATABASE_URL |

</div>

### Task Definition Components

**Container Definitions:**
```json
{
  "name": "web-container",
  "image": "nginx:latest",
  "cpu": 512,
  "memory": 1024,
  "portMappings": [
    {
      "containerPort": 80,
      "protocol": "tcp"
    }
  ],
  "environment": [
    {
      "name": "ENV",
      "value": "production"
    }
  ],
  "logConfiguration": {
    "logDriver": "awslogs",
    "options": {
      "awslogs-group": "/ecs/my-app",
      "awslogs-region": "us-east-1"
    }
  }
}
```

**Key Fields:**
- **Image:** Docker image to use
- **CPU:** CPU units (1024 = 1 vCPU)
- **Memory:** Memory in MB
- **Port Mappings:** Container ports to expose
- **Environment Variables:** Configuration
- **Log Configuration:** CloudWatch Logs integration

### Task Roles vs Execution Roles

<div align="center">

**Understanding IAM roles in ECS**

| Role Type | Purpose | Used For |
|:---:|:---:|:---:|
| **Task Role** | Permissions for running containers | Application access (S3, DynamoDB) |
| **Execution Role** | Permissions for ECS agent | Pull images, write logs |

</div>

**Task Role:**
- Assumed by containers at runtime
- Used by application code
- Access AWS services (S3, DynamoDB, etc.)
- Defined in task definition

**Execution Role:**
- Used by ECS agent
- Pull container images from ECR
- Write logs to CloudWatch
- Required for Fargate

---

## ⚙️ Services

<div align="center">

**Maintain desired number of tasks**

| Feature | Description |
|:---:|:---:|
| **Desired Count** | Number of tasks to maintain |
| **Load Balancing** | Distribute traffic |
| **Auto Scaling** | Scale based on metrics |
| **Service Discovery** | DNS-based discovery |
| **Deployment** | Rolling updates, blue/green |

</div>

### Service Configuration

**Basic Service:**
- Maintains desired number of tasks
- Restarts failed tasks
- Distributes tasks across availability zones
- Integrates with load balancers

**Advanced Features:**
- **Auto Scaling:** Scale based on CPU, memory, or custom metrics
- **Service Discovery:** Automatic DNS registration
- **Deployment Configuration:** Rolling updates, blue/green deployments
- **Health Checks:** Container and load balancer health checks

### Service Types

**Replica Service:**
- Maintains desired count of tasks
- Distributes across AZs
- Best for stateless applications

**Daemon Service:**
- One task per instance (EC2 launch type)
- Runs on every instance in cluster
- Best for monitoring, logging agents

---

## 🏗️ Clusters

<div align="center">

**Logical grouping of infrastructure**

| Cluster Type | Description | Use Case |
|:---:|:---:|:---:|
| **EC2 Cluster** | EC2 instances | EC2 launch type |
| **Fargate Cluster** | Serverless | Fargate launch type |
| **External Cluster** | On-premises | Hybrid deployments |

</div>

### Cluster Configuration

**Capacity Providers:**
- **EC2:** Traditional EC2 instances
- **Fargate:** Serverless containers
- **Fargate Spot:** Cost-optimized Fargate
- **Auto Scaling Groups:** Custom capacity

**Cluster Settings:**
- Container Insights: Enhanced monitoring
- CloudWatch Container Insights: Detailed metrics
- Service Connect: Service mesh capabilities

---

## 🌐 Networking

### Network Modes

<div align="center">

**How containers connect to network**

| Mode | Description | Launch Type |
|:---:|:---:|:---:|
| **awsvpc** | Each task gets ENI | Fargate, EC2 |
| **bridge** | Docker bridge network | EC2 only |
| **host** | Host network | EC2 only |
| **none** | No networking | EC2 only |

</div>

**awsvpc Mode:**
- Each task gets its own ENI
- Full VPC integration
- Security groups per task
- Required for Fargate
- Best for production

**bridge Mode:**
- Docker bridge networking
- Port mappings required
- Shared network namespace
- EC2 launch type only
- Legacy mode

### Service Discovery

<div align="center">

**DNS-based service discovery**

| Feature | Description |
|:---:|:---:|
| **Namespace** | Service discovery namespace |
| **Service Registry** | Automatic DNS registration |
| **Health Checks** | DNS health checks |
| **Load Balancing** | DNS-based load balancing |

</div>

**How It Works:**
1. Create service discovery namespace
2. Configure service with service discovery
3. Tasks automatically register DNS names
4. Other services resolve DNS names
5. Automatic health checking

---

## 📊 Auto Scaling

<div align="center">

**Scale services based on demand**

| Metric | Description | Use Case |
|:---:|:---:|:---:|
| **CPU Utilization** | Average CPU usage | General scaling |
| **Memory Utilization** | Average memory usage | Memory-intensive apps |
| **ALB Request Count** | Requests per target | Request-based scaling |
| **Custom Metrics** | Application metrics | Custom scaling logic |

</div>

### Auto Scaling Configuration

**Target Tracking:**
- Maintain target metric value
- Automatic scaling up/down
- Simple configuration
- Best for most use cases

**Step Scaling:**
- Scale based on metric thresholds
- Multiple scaling steps
- More control
- Complex scenarios

**Scheduled Scaling:**
- Scale at specific times
- Predictable workloads
- Business hours scaling

---

## 🔄 Deployment Strategies

### Rolling Update

<div align="center">

**Gradually replace old tasks with new**

| Step | Action |
|:---:|:---:|
| **1** | Start new tasks with new version |
| **2** | Wait for health checks |
| **3** | Stop old tasks |
| **4** | Repeat until all updated |

</div>

**Characteristics:**
- Zero downtime
- Gradual replacement
- Automatic rollback on failure
- Default deployment strategy

### Blue/Green Deployment

<div align="center">

**Deploy new version alongside old**

| Step | Action |
|:---:|:---:|
| **1** | Deploy new version (green) |
| **2** | Test green deployment |
| **3** | Switch traffic to green |
| **4** | Keep blue for rollback |

</div>

**Characteristics:**
- Instant rollback capability
- Full testing before switch
- Requires load balancer
- More complex setup

---

## 🔐 Security

### Task Security

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

**Best Practices:**
- Use task roles with least privilege
- Configure security groups properly
- Store secrets in Secrets Manager
- Scan images for vulnerabilities
- Use private subnets for tasks
- Enable VPC Flow Logs

### IAM Roles

**Task Role:**
- Permissions for application
- Access AWS services
- Defined in task definition

**Execution Role:**
- ECS agent permissions
- Pull images from ECR
- Write logs to CloudWatch

---

## 📈 Monitoring & Logging

### CloudWatch Integration

<div align="center">

**Comprehensive observability**

| Feature | Description |
|:---:|:---:|
| **Container Insights** | Enhanced metrics |
| **CloudWatch Logs** | Centralized logging |
| **Metrics** | CPU, memory, network |
| **Alarms** | Automated alerts |

</div>

**Container Insights:**
- Detailed task and container metrics
- Performance insights
- Cost allocation
- Requires CloudWatch agent

**CloudWatch Logs:**
- Centralized log aggregation
- Log groups per service
- Log retention policies
- Log filtering and search

### Key Metrics

**Task Metrics:**
- CPU utilization
- Memory utilization
- Network I/O
- Task count

**Service Metrics:**
- Running task count
- Desired task count
- Pending task count
- Service events

---

## 💰 Pricing

### EC2 Launch Type

<div align="center">

**Pay for EC2 instances**

| Component | Cost |
|:---:|:---:|
| **EC2 Instances** | Per instance pricing |
| **EBS Volumes** | Per GB storage |
| **Data Transfer** | Per GB transfer |
| **ECS Service** | Free |

</div>

**Cost Optimization:**
- Use Reserved Instances
- Use Spot Instances for fault-tolerant workloads
- Right-size instances
- Use auto-scaling

### Fargate Launch Type

<div align="center">

**Pay per task**

| Component | Pricing |
|:---:|:---:|
| **vCPU** | $0.04048 per vCPU-hour |
| **Memory** | $0.004445 per GB-hour |
| **Data Transfer** | Per GB transfer |

</div>

**Example:**
```
Task: 0.5 vCPU, 1 GB memory
Cost per hour: (0.5 × $0.04048) + (1 × $0.004445) = $0.02469/hour
Monthly (730 hours): ~$18.02
```

**Cost Optimization:**
- Right-size CPU and memory
- Use Fargate Spot (up to 70% savings)
- Scale down when not needed
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
| **Data Processing** | ETL workloads | EC2 |

</div>

---

## 💡 Best Practices

<div align="center">

| Practice | Description |
|:---:|:---:|
| **Right-Size Resources** | Match CPU/memory to needs |
| **Use Fargate for Simplicity** | When you don't need EC2 control |
| **Enable Auto Scaling** | Scale based on demand |
| **Use Service Discovery** | Simplify service communication |
| **Implement Health Checks** | Ensure task reliability |
| **Use Task Roles** | Least privilege access |
| **Enable Container Insights** | Enhanced monitoring |
| **Use Blue/Green Deployments** | Zero-downtime updates |

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
| **Security** | Use task roles and security groups |
| **Monitoring** | Enable Container Insights |

**💡 Remember:** ECS simplifies container orchestration. Choose Fargate for simplicity or EC2 for cost optimization and control.

</div>

---

<div align="center">

**Master ECS for containerized applications! 🚀**

*Deploy, manage, and scale Docker containers with AWS ECS.*

</div>

