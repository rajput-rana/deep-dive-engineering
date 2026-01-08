# ☸️ EKS - Elastic Kubernetes Service

<div align="center">

**Managed Kubernetes on AWS: deploy, manage, and scale containerized applications**

[![EKS](https://img.shields.io/badge/EKS-Kubernetes-blue?style=for-the-badge)](./)
[![K8s](https://img.shields.io/badge/K8s-Orchestration-green?style=for-the-badge)](./)
[![Managed](https://img.shields.io/badge/Managed-AWS-orange?style=for-the-badge)](./)

*Master EKS: run Kubernetes clusters on AWS without managing control plane*

</div>

---

## 🎯 What is EKS?

<div align="center">

**Amazon EKS (Elastic Kubernetes Service) is a managed Kubernetes service that makes it easy to run Kubernetes on AWS without needing to install and operate your own Kubernetes control plane.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **☸️ Kubernetes** | Container orchestration platform |
| **🏗️ Cluster** | Kubernetes cluster (control plane + nodes) |
| **🎛️ Control Plane** | Kubernetes API server (managed by AWS) |
| **💻 Worker Nodes** | EC2 instances running pods |
| **📦 Pods** | Smallest deployable unit |
| **⚙️ Deployments** | Manage pod replicas |
| **🌐 Services** | Network abstraction for pods |

**Mental Model:** Think of EKS as Kubernetes-as-a-Service - AWS manages the Kubernetes control plane (API server, etcd, scheduler), and you manage the worker nodes where your containers run.

</div>

---

## 🏗️ EKS Architecture

<div align="center">

### Core Components

| Component | Description | Managed By |
|:---:|:---:|:---:|
| **Control Plane** | Kubernetes API server | AWS |
| **etcd** | Cluster state database | AWS |
| **Worker Nodes** | EC2 instances running pods | You |
| **Node Groups** | Group of worker nodes | You |
| **VPC** | Network isolation | You |
| **CNI Plugin** | Container networking | AWS VPC CNI |

</div>

### Kubernetes Architecture Reference

<div align="center">

**EKS runs standard Kubernetes, so understanding Kubernetes architecture is essential.**

For the official Kubernetes architecture diagram and detailed component explanations, see the **[Kubernetes Architecture Documentation](https://kubernetes.io/docs/concepts/architecture/)**.

The Kubernetes architecture consists of:
- **Control Plane Components:** kube-apiserver, etcd, kube-scheduler, kube-controller-manager
- **Node Components:** kubelet, kube-proxy, container runtime
- **Addons:** DNS, Web UI, monitoring, logging, network plugins

</div>

### EKS Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    EKS Control Plane                        │
│              (Managed by AWS - Multi-AZ)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ API Server   │  │   etcd       │  │  Scheduler   │    │
│  │ (us-east-1a) │  │ (us-east-1b) │  │ (us-east-1c) │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ kubectl / API calls
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Worker Nodes (EC2)                        │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Node Group 1 (us-east-1a)               │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │   Pod    │  │   Pod    │  │   Pod    │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Node Group 2 (us-east-1b)               │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │   Pod    │  │   Pod    │  │   Pod    │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Fargate Profile (Optional)               │   │
│  │  ┌──────────┐  ┌──────────┐                          │   │
│  │  │   Pod    │  │   Pod    │                          │   │
│  │  └──────────┘  └──────────┘                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 EKS Features

<div align="center">

**What AWS manages vs what you manage**

| Component | Managed By | Details |
|:---:|:---:|:---:|
| **Control Plane** | AWS | API server, etcd, scheduler |
| **High Availability** | AWS | Multi-AZ control plane |
| **Updates** | AWS | Kubernetes version updates |
| **Worker Nodes** | You | EC2 instances or Fargate |
| **Networking** | You | VPC, subnets, security groups |
| **Applications** | You | Deployments, services, pods |

</div>

### Key Benefits

**Managed Control Plane:**
- AWS manages Kubernetes control plane
- High availability across multiple AZs
- Automatic updates and patches
- No need to manage etcd, API server

**Kubernetes Compatibility:**
- Standard Kubernetes API
- Works with kubectl and Kubernetes tools
- Compatible with Kubernetes ecosystem
- Supports Helm charts

**AWS Integration:**
- IAM for authentication
- VPC for networking
- CloudWatch for monitoring
- ECR for container images

---

## 🏗️ Cluster Components

### Control Plane

<div align="center">

**Managed Kubernetes control plane**

| Component | Description | Managed By |
|:---:|:---:|:---:|
| **API Server** | Kubernetes API endpoint | AWS |
| **etcd** | Cluster state database | AWS |
| **Scheduler** | Pod scheduling logic | AWS |
| **Controller Manager** | Cluster controllers | AWS |

</div>

**Characteristics:**
- Highly available across 3 AZs
- Automatic backups
- AWS manages updates
- Standard Kubernetes API
- Endpoint URL: `https://<cluster-id>.eks.<region>.amazonaws.com`

### Worker Nodes

<div align="center">

**EC2 instances running your workloads**

| Component | Description |
|:---:|:---:|
| **Node Groups** | Managed group of EC2 instances |
| **Self-Managed Nodes** | EC2 instances you manage |
| **Fargate** | Serverless containers |

</div>

**Node Types:**

**Managed Node Groups:**
- AWS manages node lifecycle
- Automatic updates
- Integrated with Auto Scaling
- Easier to manage

**Self-Managed Nodes:**
- Full control over nodes
- Custom AMIs
- More flexibility
- More management overhead

**Fargate:**
- Serverless containers
- No node management
- Pay per pod
- Limited customization

---

## 📦 Kubernetes Resources

### Pods

<div align="center">

**Smallest deployable unit**

| Concept | Description |
|:---:|:---:|
| **Pod** | One or more containers sharing network/storage |
| **Container** | Docker container |
| **Init Containers** | Run before main containers |
| **Sidecar** | Helper container in same pod |

</div>

**Pod Lifecycle:**
- Pending → Running → Succeeded/Failed
- Ephemeral (can be recreated)
- Share network namespace
- Share storage volumes

### Deployments

<div align="center">

**Manage pod replicas**

| Feature | Description |
|:---:|:---:|
| **Replicas** | Desired number of pods |
| **Rolling Update** | Gradual pod replacement |
| **Rollback** | Revert to previous version |
| **Scaling** | Scale up/down replicas |

</div>

**Deployment Strategy:**
- **Rolling Update:** Gradual replacement (default)
- **Recreate:** Terminate old, create new
- **Blue/Green:** Deploy new version, switch traffic

### Services

<div align="center">

**Network abstraction for pods**

| Service Type | Description | Use Case |
|:---:|:---:|:---:|
| **ClusterIP** | Internal cluster IP | Internal communication |
| **NodePort** | Port on each node | External access (dev/test) |
| **LoadBalancer** | AWS load balancer | Production external access |
| **ExternalName** | External service alias | External services |

</div>

**Service Types:**

**ClusterIP:**
- Internal cluster IP
- Only accessible within cluster
- Default service type

**NodePort:**
- Exposes service on each node
- Port range: 30000-32767
- Not recommended for production

**LoadBalancer:**
- Creates AWS load balancer (ALB/NLB)
- External access
- Production-ready
- Integrates with AWS services

---

## 🌐 Networking

### VPC CNI Plugin

<div align="center">

**AWS VPC Container Network Interface**

| Feature | Description |
|:---:|:---:|
| **Pod IPs** | Pods get VPC IP addresses |
| **Security Groups** | Apply to pods |
| **ENI Limits** | Limited by instance type |
| **IP Address Management** | Automatic IP allocation |

</div>

**How It Works:**
- Each pod gets VPC IP address
- Pods can use security groups
- Direct VPC integration
- No NAT required for VPC communication

**ENI Limits:**
- Instance type determines ENI limit
- Each pod uses one ENI
- Plan node capacity accordingly

### Network Policies

<div align="center">

**Control pod-to-pod communication**

| Policy Type | Description |
|:---:|:---:|
| **Ingress** | Incoming traffic rules |
| **Egress** | Outgoing traffic rules |
| **Namespace** | Isolate by namespace |
| **Pod Selector** | Target specific pods |

</div>

**Use Cases:**
- Isolate namespaces
- Restrict pod communication
- Implement micro-segmentation
- Compliance requirements

---

## 🔐 Security

### Authentication & Authorization

<div align="center">

**IAM integration with Kubernetes RBAC**

| Component | Description |
|:---:|:---:|
| **IAM Authenticator** | IAM-based authentication |
| **RBAC** | Role-based access control |
| **Service Accounts** | Pod identity |
| **IRSA** | IAM Roles for Service Accounts |

</div>

**IAM Integration:**
- Use IAM for cluster access
- Map IAM users/roles to Kubernetes users
- Integrate with AWS IAM policies
- No separate Kubernetes user management

**RBAC (Role-Based Access Control):**
- Roles: Permissions in namespace
- ClusterRoles: Cluster-wide permissions
- RoleBindings: Bind roles to users
- ServiceAccounts: Pod identity

### IAM Roles for Service Accounts (IRSA)

<div align="center">

**Grant pods AWS permissions**

| Component | Description |
|:---:|:---:|
| **Service Account** | Kubernetes service account |
| **IAM Role** | AWS IAM role |
| **OIDC Provider** | EKS cluster OIDC endpoint |
| **Annotation** | Link role to service account |

</div>

**How It Works:**
1. Create IAM role with permissions
2. Create OIDC provider for cluster
3. Trust relationship between role and OIDC
4. Annotate service account with role ARN
5. Pods assume role automatically

**Benefits:**
- No need for access keys
- Fine-grained permissions
- Automatic credential rotation
- Audit trail in CloudTrail

### Pod Security

<div align="center">

**Secure pod execution**

| Practice | Description |
|:---:|:---:|
| **Security Context** | Pod/container security settings |
| **Pod Security Policies** | Cluster-wide security policies |
| **Secrets Management** | Use Secrets Manager |
| **Network Policies** | Control network access |

</div>

**Best Practices:**
- Run containers as non-root
- Use read-only root filesystem
- Limit capabilities
- Use secrets from Secrets Manager
- Apply network policies
- Scan container images

---

## 📊 Monitoring & Logging

### CloudWatch Integration

<div align="center">

**Comprehensive observability**

| Feature | Description |
|:---:|:---:|
| **Container Insights** | Enhanced metrics |
| **CloudWatch Logs** | Centralized logging |
| **Metrics** | Cluster and pod metrics |
| **Alarms** | Automated alerts |

</div>

**Container Insights:**
- Cluster-level metrics
- Node-level metrics
- Pod-level metrics
- Performance insights

**CloudWatch Logs:**
- Fluent Bit daemon set
- Centralized log aggregation
- Log groups per namespace
- Log retention policies

### Prometheus & Grafana

<div align="center">

**Popular monitoring stack**

| Component | Description |
|:---:|:---:|
| **Prometheus** | Metrics collection |
| **Grafana** | Visualization |
| **Node Exporter** | Node metrics |
| **kube-state-metrics** | Kubernetes metrics |

</div>

**Setup Options:**
- Self-managed Prometheus
- AWS Managed Service for Prometheus
- Grafana Cloud
- Third-party solutions

---

## 🔄 Cluster Management

### Creating a Cluster

<div align="center">

**Cluster creation options**

| Method | Description |
|:---:|:---:|
| **AWS Console** | Web UI |
| **AWS CLI** | Command line |
| **eksctl** | Official CLI tool |
| **Terraform** | Infrastructure as code |
| **CloudFormation** | AWS templates |

</div>

**Using eksctl (Recommended):**
```bash
eksctl create cluster \
  --name my-cluster \
  --region us-east-1 \
  --nodegroup-name workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 5
```

**Using AWS CLI:**
```bash
aws eks create-cluster \
  --name my-cluster \
  --role-arn arn:aws:iam::123456789012:role/eks-service-role \
  --resources-vpc-config subnetIds=subnet-123,subnet-456
```

### Updating Clusters

<div align="center">

**Keeping clusters up to date**

| Component | Update Method |
|:---:|:---:|
| **Kubernetes Version** | AWS manages control plane |
| **Node AMI** | Update node groups |
| **Add-ons** | Update via console/CLI |
| **Worker Nodes** | Rolling update |

</div>

**Update Process:**
1. Update control plane (AWS managed)
2. Update node groups (rolling update)
3. Update add-ons
4. Test applications
5. Monitor for issues

---

## 🎯 Node Groups

### Managed Node Groups

<div align="center">

**AWS-managed worker nodes**

| Feature | Description |
|:---:|:---:|
| **Lifecycle Management** | AWS manages nodes |
| **Auto Scaling** | Integrated with ASG |
| **Updates** | Automatic AMI updates |
| **Launch Templates** | Customize node configuration |

</div>

**Benefits:**
- Less operational overhead
- Automatic updates
- Integrated scaling
- Easier management

**Limitations:**
- Limited customization
- AWS-managed AMI
- Less control

### Self-Managed Nodes

<div align="center">

**Full control over nodes**

| Feature | Description |
|:---:|:---:|
| **Custom AMIs** | Your own AMI |
| **Full Control** | Complete customization |
| **Instance Types** | Any EC2 instance type |
| **Management** | You manage lifecycle |

</div>

**Benefits:**
- Full customization
- Custom AMIs
- More control
- Cost optimization options

**Limitations:**
- More operational overhead
- Manual updates
- More complex

### Fargate

<div align="center">

**Serverless containers**

| Feature | Description |
|:---:|:---:|
| **No Nodes** | No EC2 instances |
| **Pay Per Pod** | Pay for running pods |
| **Automatic Scaling** | Scale automatically |
| **Simplified** | Less management |

</div>

**When to Use:**
- Simple workloads
- Don't want node management
- Variable workloads
- Cost-effective for small scale

**Limitations:**
- Limited customization
- No DaemonSets
- No privileged containers
- Higher cost at scale

---

## 🔧 Add-ons

<div align="center">

**Extended cluster functionality**

| Add-on | Description | Purpose |
|:---:|:---:|:---:|
| **VPC CNI** | Networking plugin | Pod networking |
| **CoreDNS** | DNS server | Service discovery |
| **kube-proxy** | Network proxy | Service routing |
| **EBS CSI Driver** | Storage driver | EBS volumes |
| **EFS CSI Driver** | Storage driver | EFS volumes |

</div>

**Common Add-ons:**
- **VPC CNI:** Default networking plugin
- **CoreDNS:** Cluster DNS
- **kube-proxy:** Service proxy
- **EBS CSI Driver:** EBS volume support
- **EFS CSI Driver:** EFS volume support
- **AWS Load Balancer Controller:** ALB/NLB integration

---

## 💰 Pricing

<div align="center">

**EKS pricing model**

| Component | Cost |
|:---:|:---:|
| **Control Plane** | $0.10 per hour ($73/month) |
| **Worker Nodes** | EC2 instance pricing |
| **Fargate** | Per pod pricing |
| **Data Transfer** | Standard AWS pricing |

</div>

**Control Plane:**
- $0.10 per hour
- ~$73 per month
- Per cluster
- Includes high availability

**Worker Nodes:**
- Pay for EC2 instances
- Can use Reserved Instances
- Can use Spot Instances
- Right-size for cost optimization

**Fargate:**
- Pay per pod (CPU + memory)
- No control plane charge
- More expensive than EC2 at scale

---

## 🎯 Use Cases

<div align="center">

| Use Case | Description | Why EKS |
|:---:|:---:|:---:|
| **Microservices** | Containerized microservices | Kubernetes orchestration |
| **CI/CD** | Build and deployment pipelines | Kubernetes-native tools |
| **Multi-Cloud** | Kubernetes portability | Standard Kubernetes |
| **Complex Workloads** | Stateful applications | Kubernetes features |
| **Enterprise** | Large-scale deployments | Managed control plane |

</div>

---

## 💡 Best Practices

<div align="center">

| Practice | Description |
|:---:|:---:|
| **Use Managed Node Groups** | Less operational overhead |
| **Enable IRSA** | Secure AWS access from pods |
| **Use Network Policies** | Control pod communication |
| **Enable Container Insights** | Enhanced monitoring |
| **Use Fargate for Simple Workloads** | Serverless option |
| **Right-Size Nodes** | Cost optimization |
| **Use Spot Instances** | Cost savings for fault-tolerant workloads |
| **Implement RBAC** | Secure cluster access |
| **Use Secrets Manager** | Secure secret management |
| **Enable VPC Flow Logs** | Network visibility |

</div>

---

## 🔗 Related Services

<div align="center">

| Service | Purpose | Integration |
|:---:|:---:|:---:|
| **ECR** | Container registry | Store images |
| **ALB/NLB** | Load balancing | Ingress controller |
| **CloudWatch** | Monitoring | Metrics and logs |
| **IAM** | Access control | Authentication |
| **VPC** | Networking | Cluster networking |
| **Secrets Manager** | Secrets | Secure configuration |

</div>

---

## 📚 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **Control Plane** | AWS manages Kubernetes control plane |
| **Worker Nodes** | You manage EC2 instances or use Fargate |
| **Networking** | VPC CNI for pod networking |
| **Security** | IAM + RBAC + IRSA |
| **Monitoring** | CloudWatch Container Insights |
| **Cost** | Control plane + worker nodes |
| **Management** | Use eksctl or Terraform |

**💡 Remember:** EKS provides managed Kubernetes control plane. You manage worker nodes and applications. Use managed node groups for simplicity or self-managed for control.

</div>

---

<div align="center">

**Master EKS for Kubernetes on AWS! 🚀**

*Deploy, manage, and scale containerized applications with Amazon EKS.*

</div>

