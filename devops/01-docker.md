# 🐳 Docker

<div align="center">

**Containerization fundamentals: package and deploy applications consistently**

[![Docker](https://img.shields.io/badge/Docker-Containers-blue?style=for-the-badge)](./)
[![Containers](https://img.shields.io/badge/Containers-Isolation-green?style=for-the-badge)](./)
[![Deployment](https://img.shields.io/badge/Deployment-Consistency-orange?style=for-the-badge)](./)

*Master Docker: containers, images, and consistent deployments*

</div>

---

## 🎯 What is Docker?

<div align="center">

**Docker is a platform for developing, shipping, and running applications using containerization.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **📦 Container** | Lightweight, isolated environment for applications |
| **🖼️ Image** | Read-only template for creating containers |
| **📝 Dockerfile** | Instructions to build an image |
| **🔗 Container Registry** | Store and share images (Docker Hub, ECR, GCR) |

**Mental Model:** Think of Docker like shipping containers - your application runs in a standardized container that works the same way on any machine (dev, staging, production).

</div>

---

## 🏗️ Why Docker Matters

<div align="center">

### Problems Docker Solves

| Problem | Without Docker | With Docker |
|:---:|:---:|:---:|
| **"Works on my machine"** | Environment differences | Consistent environments |
| **Dependency Conflicts** | Different versions needed | Isolated dependencies |
| **Deployment Complexity** | Manual setup, errors | Automated, repeatable |
| **Resource Usage** | Full VMs per app | Shared OS, efficient |

### Benefits

| Benefit | Description |
|:---:|:---:|
| **Consistency** | Same environment everywhere |
| **Isolation** | Apps don't interfere with each other |
| **Portability** | Run anywhere Docker runs |
| **Efficiency** | Less overhead than VMs |
| **Scalability** | Easy to scale horizontally |

</div>

---

## 🏗️ Core Concepts

<div align="center">

### Container vs Virtual Machine

| Aspect | Container | Virtual Machine |
|:---:|:---:|:---:|
| **OS** | Shares host OS | Full OS per VM |
| **Size** | MBs | GBs |
| **Startup** | Seconds | Minutes |
| **Isolation** | Process-level | Hardware-level |
| **Overhead** | Low | High |

**💡 Containers are lighter and faster than VMs.**

---

### Image vs Container

| Concept | Description | Analogy |
|:---:|:---:|:---:|
| **Image** | Template/blueprint | Class definition |
| **Container** | Running instance | Object instance |

**Example:**
```
Image: nginx:latest (template)
Container: Running nginx server (instance)
```

</div>

---

## 📝 Dockerfile Basics

<div align="center">

### What is a Dockerfile?

**Instructions to build a Docker image**

### Basic Dockerfile Structure

```dockerfile
# Base image
FROM node:18-alpine

# Working directory
WORKDIR /app

# Copy files
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Run command
CMD ["node", "server.js"]
```

### Common Instructions

| Instruction | Purpose | Example |
|:---:|:---:|:---:|
| **FROM** | Base image | `FROM python:3.9` |
| **WORKDIR** | Set working directory | `WORKDIR /app` |
| **COPY** | Copy files | `COPY . .` |
| **RUN** | Execute command | `RUN npm install` |
| **EXPOSE** | Document port | `EXPOSE 3000` |
| **CMD** | Default command | `CMD ["python", "app.py"]` |

---

### Best Practices

| Practice | Why |
|:---:|:---:|
| **Use multi-stage builds** | Smaller final images |
| **Layer caching** | Faster rebuilds |
| **Minimize layers** | Smaller images |
| **Use .dockerignore** | Exclude unnecessary files |
| **Non-root user** | Security |

</div>

---

## 💻 Docker Commands

<div align="center">

### Essential Commands

| Command | Purpose | Example |
|:---:|:---:|:---:|
| **docker build** | Build image | `docker build -t myapp .` |
| **docker run** | Run container | `docker run -p 3000:3000 myapp` |
| **docker ps** | List running containers | `docker ps` |
| **docker images** | List images | `docker images` |
| **docker stop** | Stop container | `docker stop container_id` |
| **docker rm** | Remove container | `docker rm container_id` |
| **docker exec** | Execute in container | `docker exec -it container sh` |
| **docker logs** | View logs | `docker logs container_id` |

---

### Common Workflows

**Build and Run:**
```bash
# Build image
docker build -t myapp:latest .

# Run container
docker run -d -p 3000:3000 --name myapp myapp:latest

# View logs
docker logs myapp

# Stop container
docker stop myapp
```

</div>

---

## 🎯 Use Cases

<div align="center">

### When to Use Docker

| Use Case | Description |
|:---:|:---:|
| **Microservices** | Isolate services |
| **CI/CD** | Consistent build environments |
| **Development** | Match production environment |
| **Scaling** | Easy horizontal scaling |
| **Multi-cloud** | Portability across clouds |

### When NOT to Use Docker

| Scenario | Alternative |
|:---:|:---:|
| **Windows GUI apps** | Virtual machines |
| **Legacy monolithic apps** | May need refactoring |
| **Very small projects** | Overhead may not be worth it |

</div>

---

## 🏗️ Docker Compose

<div align="center">

### What is Docker Compose?

**Tool for defining and running multi-container applications**

### docker-compose.yml Example

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - db
  
  db:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: password
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

### Benefits

| Benefit | Description |
|:---:|:---:|
| **Multi-container** | Define entire stack |
| **Networking** | Containers communicate |
| **Volumes** | Persistent data |
| **One Command** | `docker-compose up` |

</div>

---

## ⚖️ Docker vs Alternatives

<div align="center">

### Container Runtimes

| Tool | Description | Use Case |
|:---:|:---:|:---:|
| **Docker** | Most popular | General purpose |
| **Podman** | Rootless containers | Security-focused |
| **containerd** | Low-level runtime | Kubernetes |

### Container Orchestration

| Tool | Description | Use Case |
|:---:|:---:|:---:|
| **Docker Swarm** | Docker's orchestrator | Simple orchestration |
| **Kubernetes** | Industry standard | Production scale |
| **Nomad** | HashiCorp's orchestrator | Multi-cloud |

**💡 Docker for containers, Kubernetes for orchestration.**

</div>

---

## 💡 Best Practices

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Use official base images** | Security, maintenance |
| **Tag images properly** | Version control |
| **Keep images small** | Faster pulls, less storage |
| **Use multi-stage builds** | Smaller final images |
| **Scan for vulnerabilities** | Security |
| **Use .dockerignore** | Faster builds |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Run as root** | Security risk | Use non-root user |
| **Include secrets** | Security risk | Use secrets management |
| **Large images** | Slow pulls | Optimize layers |
| **Latest tag** | Unpredictable | Use version tags |

</div>

---

## 🎓 For Engineering Leaders

<div align="center">

### Key Questions to Ask

| Question | Why It Matters |
|:---:|:---:|
| **Are we containerizing?** | Consistency, portability |
| **What's our image strategy?** | Security, maintenance |
| **How do we handle secrets?** | Security compliance |
| **What's our registry?** | Image management |
| **How do we scan images?** | Security vulnerabilities |

### Decision Points

| Decision | Consideration |
|:---:|:---:|
| **Docker vs VMs** | Resource efficiency vs isolation |
| **Docker Compose vs K8s** | Complexity vs features |
| **Image registry** | Cost, security, compliance |

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **Docker Purpose** | Consistent, portable application packaging |
| **Containers** | Lightweight, isolated environments |
| **Images** | Templates for containers |
| **Dockerfile** | Instructions to build images |
| **Benefits** | Consistency, isolation, portability |

**💡 Remember:** Docker solves "works on my machine" by ensuring consistent environments everywhere.

</div>

---

<div align="center">

**Master Docker for consistent deployments! 🚀**

*Containerize applications for portability and consistency across environments.*

</div>

