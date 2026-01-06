# ☸️ Kubernetes

<div align="center">

**Container orchestration: manage containers at scale**

[![Kubernetes](https://img.shields.io/badge/Kubernetes-Orchestration-blue?style=for-the-badge)](./)
[![K8s](https://img.shields.io/badge/K8s-Container%20Orchestrator-green?style=for-the-badge)](./)
[![Production](https://img.shields.io/badge/Production-Scale-orange?style=for-the-badge)](./)

*Master Kubernetes: pods, services, deployments, and production container management*

</div>

---

## 🎯 What is Kubernetes?

<div align="center">

**Kubernetes (K8s) is an open-source container orchestration platform for automating deployment, scaling, and management of containerized applications.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **☸️ Pod** | Smallest deployable unit (one or more containers) |
| **🔗 Service** | Network access to pods |
| **📦 Deployment** | Manages pod replicas |
| **📊 Namespace** | Virtual cluster for resource isolation |
| **🎯 Node** | Worker machine (VM or physical) |
| **👑 Cluster** | Set of nodes running Kubernetes |

**Mental Model:** Think of Kubernetes as a conductor for an orchestra - it manages many containers (musicians) to work together harmoniously, ensuring they're in the right place, healthy, and scaled appropriately.

</div>

---

## 🏗️ Why Kubernetes Matters

<div align="center">

### Problems Kubernetes Solves

| Problem | Without K8s | With K8s |
|:---:|:---:|:---:|
| **Scaling** | Manual scaling | Auto-scaling |
| **High Availability** | Manual failover | Automatic recovery |
| **Rolling Updates** | Downtime | Zero-downtime deployments |
| **Resource Management** | Manual allocation | Automatic scheduling |
| **Service Discovery** | Manual configuration | Automatic discovery |

### Benefits

| Benefit | Description |
|:---:|:---:|
| **Auto-scaling** | Scale based on demand |
| **Self-healing** | Restart failed containers |
| **Rolling Updates** | Zero-downtime deployments |
| **Service Discovery** | Automatic networking |
| **Resource Management** | Efficient resource usage |

</div>

---

## 🏗️ Core Components

<div align="center">

### Architecture Overview

```
┌─────────────────────────────────────┐
│         Control Plane                │
│  (API Server, etcd, Scheduler)      │
└─────────────────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                    │
┌───▼───┐          ┌───▼───┐
│ Node 1│          │ Node 2│
│ Pods  │          │ Pods  │
└───────┘          └───────┘
```

---

### Key Components

| Component | Role | Description |
|:---:|:---:|:---:|
| **API Server** | Control plane | Entry point for all operations |
| **etcd** | Control plane | Key-value store for cluster state |
| **Scheduler** | Control plane | Assigns pods to nodes |
| **Controller Manager** | Control plane | Manages controllers |
| **Kubelet** | Node | Agent running on each node |
| **kube-proxy** | Node | Network proxy on each node |

</div>

---

## 📦 Core Resources

<div align="center">

### 1. Pods

**Smallest deployable unit**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: nginx:latest
    ports:
    - containerPort: 80
```

**Characteristics:**
- One or more containers
- Shared network and storage
- Ephemeral (can be recreated)

---

### 2. Services

**Network access to pods**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

**Service Types:**

| Type | Description | Use Case |
|:---:|:---:|:---:|
| **ClusterIP** | Internal only | Internal services |
| **NodePort** | Expose on node IP | Development |
| **LoadBalancer** | Cloud load balancer | Production |
| **ExternalName** | External service | External APIs |

---

### 3. Deployments

**Manage pod replicas**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: nginx:latest
```

**Features:**
- Replica management
- Rolling updates
- Rollback capability
- Health checks

---

### 4. Namespaces

**Resource isolation**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
```

**Common Namespaces:**

| Namespace | Purpose |
|:---:|:---:|
| **default** | Default namespace |
| **kube-system** | System components |
| **production** | Production workloads |
| **staging** | Staging workloads |

</div>

---

## 🎯 Common Operations

<div align="center">

### Essential kubectl Commands

| Command | Purpose | Example |
|:---:|:---:|:---:|
| **kubectl get** | List resources | `kubectl get pods` |
| **kubectl create** | Create resource | `kubectl create deployment myapp` |
| **kubectl apply** | Apply configuration | `kubectl apply -f deploy.yaml` |
| **kubectl delete** | Delete resource | `kubectl delete pod my-pod` |
| **kubectl describe** | Describe resource | `kubectl describe pod my-pod` |
| **kubectl logs** | View logs | `kubectl logs my-pod` |
| **kubectl exec** | Execute command | `kubectl exec -it my-pod -- sh` |

---

### Common Workflows

**Deploy Application:**
```bash
# Create deployment
kubectl create deployment myapp --image=nginx:latest

# Scale deployment
kubectl scale deployment myapp --replicas=3

# Expose service
kubectl expose deployment myapp --port=80 --type=LoadBalancer

# Check status
kubectl get pods,services,deployments
```

</div>

---

## 🔄 Scaling & Updates

<div align="center">

### Horizontal Pod Autoscaler (HPA)

**Auto-scale based on metrics**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

### Rolling Updates

**Zero-downtime deployments**

```bash
# Update image
kubectl set image deployment/myapp myapp=nginx:1.21

# Check rollout status
kubectl rollout status deployment/myapp

# Rollback if needed
kubectl rollout undo deployment/myapp
```

</div>

---

## 🎯 Use Cases

<div align="center">

### When to Use Kubernetes

| Use Case | Description |
|:---:|:---:|
| **Microservices** | Manage many services |
| **High Availability** | Need uptime guarantees |
| **Auto-scaling** | Variable traffic |
| **Multi-cloud** | Portability across clouds |
| **Complex Deployments** | Rolling updates, canaries |

### When NOT to Use Kubernetes

| Scenario | Alternative |
|:---:|:---:|
| **Simple apps** | Docker Compose |
| **Small teams** | Managed services |
| **Low traffic** | Serverless, simpler solutions |
| **Legacy apps** | May need refactoring |

</div>

---

## ⚖️ Kubernetes vs Alternatives

<div align="center">

### Orchestration Platforms

| Platform | Description | Best For |
|:---:|:---:|:---:|
| **Kubernetes** | Industry standard | Production, scale |
| **Docker Swarm** | Docker's orchestrator | Simpler setups |
| **Nomad** | HashiCorp's orchestrator | Multi-cloud |
| **ECS** | AWS managed | AWS-only |
| **GKE** | Google managed | GCP ecosystem |

### Managed vs Self-Managed

| Option | Pros | Cons |
|:---:|:---:|:---:|
| **Managed (EKS, GKE, AKS)** | Less ops overhead | Less control, cost |
| **Self-Managed** | Full control | High ops overhead |

</div>

---

## 💡 Best Practices

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Use Deployments** | Not bare pods |
| **Set resource limits** | Prevent resource exhaustion |
| **Use namespaces** | Organize resources |
| **Health checks** | Liveness and readiness probes |
| **Use ConfigMaps/Secrets** | Configuration management |
| **Monitor everything** | Observability |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Bare pods** | No self-healing | Use Deployments |
| **No resource limits** | Resource exhaustion | Set limits |
| **Secrets in YAML** | Security risk | Use Secrets |
| **No health checks** | Unhealthy pods | Add probes |

</div>

---

## 🎓 For Engineering Leaders

<div align="center">

### Key Questions to Ask

| Question | Why It Matters |
|:---:|:---:|
| **Do we need Kubernetes?** | Complexity vs benefits |
| **Managed or self-managed?** | Cost vs control |
| **What's our scaling strategy?** | Cost optimization |
| **How do we handle secrets?** | Security compliance |
| **What's our monitoring?** | Observability |

### Decision Points

| Decision | Consideration |
|:---:|:---:|
| **K8s vs simpler solutions** | Complexity vs needs |
| **Managed vs self-managed** | Team expertise, cost |
| **On-prem vs cloud** | Compliance, cost |

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **Kubernetes Purpose** | Container orchestration at scale |
| **Pods** | Smallest deployable unit |
| **Services** | Network access to pods |
| **Deployments** | Manage pod replicas |
| **Benefits** | Auto-scaling, self-healing, rolling updates |

**💡 Remember:** Kubernetes is powerful but complex. Use it when you need orchestration at scale, not for simple applications.

</div>

---

<div align="center">

**Master Kubernetes for production-scale container management! 🚀**

*Orchestrate containers with auto-scaling, self-healing, and zero-downtime deployments.*

</div>

