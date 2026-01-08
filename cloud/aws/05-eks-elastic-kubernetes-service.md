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

**Key Benefits:**
- AWS manages Kubernetes control plane
- High availability across multiple AZs
- Standard Kubernetes API (works with kubectl, Helm)
- AWS integration (IAM, VPC, CloudWatch, ECR)

---

## 🏗️ Worker Nodes

<div align="center">

**EC2 instances running your workloads**

| Node Type | Description | Use Case |
|:---:|:---:|:---:|
| **Managed Node Groups** | AWS manages lifecycle | Production workloads |
| **Self-Managed Nodes** | You manage lifecycle | Custom requirements |
| **Fargate** | Serverless containers | Simple workloads |

</div>

**Managed Node Groups:**
- AWS manages node lifecycle
- Automatic updates
- Integrated with Auto Scaling
- Easier to manage

**Fargate:**
- Serverless containers
- No node management
- Pay per pod
- Limited customization

---

## 🌐 Networking

<div align="center">

**VPC CNI Plugin for pod networking**

| Feature | Description |
|:---:|:---:|
| **Pod IPs** | Pods get VPC IP addresses |
| **Security Groups** | Apply to pods |
| **ENI Limits** | Limited by instance type |

</div>

**How It Works:**
- Each pod gets VPC IP address
- Pods can use security groups
- Direct VPC integration

For comprehensive VPC networking details, see **[VPC Networking Guide](./11-vpc-networking.md)**.

---

## 🔐 Security

<div align="center">

**IAM integration with Kubernetes RBAC**

| Component | Description |
|:---:|:---:|
| **IAM Authenticator** | IAM-based authentication |
| **RBAC** | Role-based access control |
| **IRSA** | IAM Roles for Service Accounts |

</div>

**IRSA (IAM Roles for Service Accounts):**
- Grant pods AWS permissions
- No access keys needed
- Fine-grained permissions
- Automatic credential rotation

**Best Practices:**
- Use IRSA for pod AWS access
- Implement RBAC for cluster access
- Use network policies for pod communication
- Scan container images

---

## 📊 Monitoring

<div align="center">

**EKS integrates with CloudWatch**

| Feature | Description |
|:---:|:---:|
| **Container Insights** | Enhanced metrics |
| **CloudWatch Logs** | Centralized logging |
| **Metrics** | Cluster and pod metrics |

</div>

For comprehensive CloudWatch monitoring details, see **[CloudWatch Monitoring Guide](./15-cloudwatch-monitoring.md)**.

---

## 🔧 Add-ons

<div align="center">

**Extended cluster functionality**

| Add-on | Purpose |
|:---:|:---:|
| **VPC CNI** | Pod networking |
| **CoreDNS** | Service discovery |
| **kube-proxy** | Service routing |
| **EBS CSI Driver** | EBS volumes |
| **EFS CSI Driver** | EFS volumes |

</div>

---

## 💰 Pricing

<div align="center">

**EKS pricing model**

| Component | Cost |
|:---:|:---:|
| **Control Plane** | $0.10 per hour ($73/month) |
| **Worker Nodes** | EC2 instance pricing |
| **Fargate** | Per pod pricing |

</div>

**Cost Optimization:**
- Use Reserved Instances for worker nodes
- Use Spot Instances for fault-tolerant workloads
- Right-size nodes
- Use Fargate for simple workloads

---

## 🎯 Use Cases

<div align="center">

| Use Case | Description |
|:---:|:---:|
| **Microservices** | Containerized microservices |
| **CI/CD** | Build and deployment pipelines |
| **Multi-Cloud** | Kubernetes portability |
| **Enterprise** | Large-scale deployments |

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
| **Right-Size Nodes** | Cost optimization |

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

**💡 Remember:** EKS provides managed Kubernetes control plane. You manage worker nodes and applications. Use managed node groups for simplicity.

</div>

---

<div align="center">

**Master EKS for Kubernetes on AWS! 🚀**

*Deploy, manage, and scale containerized applications with Amazon EKS.*

</div>
