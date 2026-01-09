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

## 🚀 Dockerizing an Application

<div align="center">

### Step-by-Step Process

**How to containerize your application**

| Step | Action | Description |
|:---:|:---:|:---:|
| **1️⃣** | Create Dockerfile | Define image build instructions |
| **2️⃣** | Create .dockerignore | Exclude unnecessary files |
| **3️⃣** | Build image | `docker build -t myapp .` |
| **4️⃣** | Test locally | `docker run -p 3000:3000 myapp` |
| **5️⃣** | Push to registry | `docker push myapp:latest` |

</div>

### Example: Dockerizing a Node.js App

**1. Create Dockerfile:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

**2. Create .dockerignore:**
```
node_modules
npm-debug.log
.git
.env
*.md
```

**3. Build and Run:**
```bash
# Build image
docker build -t myapp:latest .

# Run container
docker run -d -p 3000:3000 --name myapp myapp:latest

# Test
curl http://localhost:3000
```

### Key Considerations

<div align="center">

| Consideration | Description |
|:---:|:---:|
| **Base Image** | Choose appropriate base (alpine for smaller size) |
| **Dependencies** | Install only what's needed |
| **Ports** | Expose necessary ports |
| **Environment** | Use environment variables for config |
| **Data Persistence** | Use volumes for persistent data |

</div>

---

## 💾 Docker Volumes

<div align="center">

### What are Docker Volumes?

**Persistent storage for containers - data survives container removal**

| Concept | Description |
|:---:|:---:|
| **Volume** | Named storage managed by Docker |
| **Bind Mount** | Mount host directory into container |
| **tmpfs Mount** | In-memory storage (Linux only) |

**Mental Model:** Think of volumes like external hard drives - your container can read/write data to volumes, and the data persists even if you delete the container.

</div>

---

### Volume Types

<div align="center">

**Three types of volumes**

| Type | Description | Use Case |
|:---:|:---:|:---:|
| **Named Volumes** | Managed by Docker | Production data, databases |
| **Bind Mounts** | Host directory | Development, config files |
| **Anonymous Volumes** | Temporary, unnamed | Temporary data |

</div>

**Named Volumes:**
- Managed by Docker
- Stored in Docker's directory
- Best for production
- Example: Database data

**Bind Mounts:**
- Mount host directory
- Direct access to host filesystem
- Best for development
- Example: Source code mounting

**Anonymous Volumes:**
- Created automatically
- Removed when container removed
- Temporary storage
- Example: Cache directories

---

### Volume Commands

<div align="center">

**Managing volumes**

| Command | Purpose | Example |
|:---:|:---:|:---:|
| **docker volume create** | Create named volume | `docker volume create mydata` |
| **docker volume ls** | List volumes | `docker volume ls` |
| **docker volume inspect** | Inspect volume | `docker volume inspect mydata` |
| **docker volume rm** | Remove volume | `docker volume rm mydata` |
| **docker volume prune** | Remove unused volumes | `docker volume prune` |

</div>

---

### Using Volumes

<div align="center">

**Mount volumes in containers**

| Method | Syntax | Example |
|:---:|:---:|:---:|
| **Named Volume** | `-v volume_name:/path` | `-v mydata:/data` |
| **Bind Mount** | `-v /host/path:/container/path` | `-v ./app:/app` |
| **Anonymous Volume** | `-v /container/path` | `-v /tmp` |

</div>

**Examples:**

**Named Volume:**
```bash
# Create volume
docker volume create db_data

# Use volume
docker run -d -v db_data:/var/lib/postgresql/data postgres:14
```

**Bind Mount:**
```bash
# Mount host directory
docker run -d -v /host/app:/app myapp

# Mount current directory
docker run -d -v $(pwd):/app myapp
```

**Multiple Volumes:**
```bash
docker run -d \
  -v db_data:/var/lib/postgresql/data \
  -v ./config:/etc/postgresql \
  postgres:14
```

---

### Volume Use Cases

<div align="center">

**When to use volumes**

| Use Case | Volume Type | Example |
|:---:|:---:|:---:|
| **Database Data** | Named volume | PostgreSQL data directory |
| **Development Code** | Bind mount | Mount source code |
| **Configuration Files** | Bind mount | Mount config directory |
| **Logs** | Named volume or bind mount | Application logs |
| **Cache** | Anonymous volume | Temporary cache |

</div>

**Best Practices:**
- Use named volumes for production data
- Use bind mounts for development
- Don't mount sensitive host directories
- Use volumes for databases
- Clean up unused volumes regularly

---

## 💻 Docker Commands

<div align="center">

### Image Commands

| Command | Purpose | Example |
|:---:|:---:|:---:|
| **docker build** | Build image from Dockerfile | `docker build -t myapp:latest .` |
| **docker images** | List all images | `docker images` |
| **docker rmi** | Remove image | `docker rmi myapp:latest` |
| **docker pull** | Pull image from registry | `docker pull nginx:latest` |
| **docker push** | Push image to registry | `docker push myapp:latest` |
| **docker tag** | Tag an image | `docker tag myapp:latest myapp:v1.0` |
| **docker inspect** | Inspect image details | `docker inspect myapp:latest` |

---

### Container Commands

| Command | Purpose | Example |
|:---:|:---:|:---:|
| **docker run** | Run container | `docker run -d -p 3000:3000 myapp` |
| **docker ps** | List running containers | `docker ps` |
| **docker ps -a** | List all containers | `docker ps -a` |
| **docker stop** | Stop running container | `docker stop container_id` |
| **docker start** | Start stopped container | `docker start container_id` |
| **docker restart** | Restart container | `docker restart container_id` |
| **docker rm** | Remove container | `docker rm container_id` |
| **docker rm -f** | Force remove running container | `docker rm -f container_id` |
| **docker exec** | Execute command in container | `docker exec -it container sh` |
| **docker logs** | View container logs | `docker logs container_id` |
| **docker logs -f** | Follow logs | `docker logs -f container_id` |
| **docker inspect** | Inspect container details | `docker inspect container_id` |
| **docker stats** | Show container resource usage | `docker stats` |

---

### Common Run Options

| Option | Purpose | Example |
|:---:|:---:|:---:|
| **-d** | Run in detached mode | `docker run -d myapp` |
| **-p** | Map port | `docker run -p 3000:3000 myapp` |
| **-e** | Set environment variable | `docker run -e VAR=value myapp` |
| **-v** | Mount volume | `docker run -v /host:/container myapp` |
| **--name** | Name container | `docker run --name myapp myapp` |
| **-it** | Interactive terminal | `docker run -it myapp sh` |
| **--rm** | Remove when stopped | `docker run --rm myapp` |

---

### Common Workflows

**Build and Run:**
```bash
# Build image
docker build -t myapp:latest .

# Run container in background
docker run -d -p 3000:3000 --name myapp myapp:latest

# View logs
docker logs myapp

# Execute command in container
docker exec -it myapp sh

# Stop container
docker stop myapp

# Remove container
docker rm myapp
```

**Image Management:**
```bash
# Pull image
docker pull nginx:latest

# Tag image
docker tag myapp:latest myregistry/myapp:v1.0

# Push to registry
docker push myregistry/myapp:v1.0

# Remove image
docker rmi myapp:latest
```

**Cleanup:**
```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a
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

**Tool for defining and running multi-container Docker applications**

| Concept | Description |
|:---:|:---:|
| **docker-compose.yml** | YAML file defining services, networks, volumes |
| **Service** | Container definition |
| **Network** | Communication between containers |
| **Volume** | Persistent data storage |

**Mental Model:** Think of Docker Compose like a blueprint for your entire application stack - define all services, their relationships, and configuration in one file, then start everything with one command.

</div>

---

### docker-compose.yml Structure

<div align="center">

**Basic structure**

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - db
    volumes:
      - ./app:/app
  
  db:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: myapp
    volumes:
      - db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  db_data:

networks:
  default:
    driver: bridge
```

</div>

---

### Key Compose Concepts

<div align="center">

**Service Configuration**

| Directive | Purpose | Example |
|:---:|:---:|:---:|
| **build** | Build from Dockerfile | `build: .` or `build: ./path` |
| **image** | Use existing image | `image: nginx:latest` |
| **ports** | Port mappings | `ports: - "3000:3000"` |
| **environment** | Environment variables | `environment: - VAR=value` |
| **volumes** | Mount volumes | `volumes: - ./data:/app/data` |
| **depends_on** | Service dependencies | `depends_on: - db` |
| **networks** | Custom networks | `networks: - frontend` |
| **restart** | Restart policy | `restart: always` |

</div>

---

### Docker Compose Commands

<div align="center">

**Essential commands**

| Command | Purpose | Example |
|:---:|:---:|:---:|
| **docker compose up** | Start all services | `docker compose up` |
| **docker compose up -d** | Start in detached mode | `docker compose up -d` |
| **docker compose down** | Stop and remove containers | `docker compose down` |
| **docker compose ps** | List running services | `docker compose ps` |
| **docker compose logs** | View logs | `docker compose logs` |
| **docker compose logs -f** | Follow logs | `docker compose logs -f web` |
| **docker compose build** | Build images | `docker compose build` |
| **docker compose restart** | Restart services | `docker compose restart` |
| **docker compose stop** | Stop services | `docker compose stop` |
| **docker compose start** | Start stopped services | `docker compose start` |
| **docker compose exec** | Execute command | `docker compose exec web sh` |
| **docker compose pull** | Pull images | `docker compose pull` |
| **docker compose config** | Validate config | `docker compose config` |

</div>

---

### Common Use Cases

<div align="center">

**Multi-service applications**

| Use Case | Description |
|:---:|:---:|
| **Web + Database** | Web app with database |
| **Microservices** | Multiple services together |
| **Development** | Local development environment |
| **Testing** | Integration test environments |

</div>

**Example: Web Application Stack**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379

  db:
    image: postgres:14
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - db_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  db_data:
```

---

### Networking in Compose

<div align="center">

**Service communication**

| Feature | Description |
|:---:|:---:|
| **Default Network** | All services on same network |
| **Service Names** | Use service name as hostname |
| **Custom Networks** | Define separate networks |
| **Port Mapping** | Expose ports to host |

</div>

**How Services Communicate:**
- Services can reach each other by service name
- Example: `web` service can connect to `db` service using `db:5432`
- No need to expose database ports externally

---

### Volumes in Compose

<div align="center">

**Data persistence**

| Volume Type | Description | Use Case |
|:---:|:---:|:---:|
| **Named Volumes** | Managed by Docker | Database data |
| **Bind Mounts** | Host directory | Development code |
| **Anonymous Volumes** | Temporary volumes | Temporary data |

</div>

**Example:**
```yaml
services:
  app:
    volumes:
      - ./code:/app          # Bind mount (development)
      - app_data:/app/data   # Named volume (production)

volumes:
  app_data:
```

---

### Environment Variables

<div align="center">

**Configuration management**

| Method | Description | Example |
|:---:|:---:|:---:|
| **Inline** | Direct in compose file | `environment: - VAR=value` |
| **.env file** | External file | `environment: - VAR=${VAR}` |
| **env_file** | Load from file | `env_file: - .env` |

</div>

**Using .env file:**
```bash
# .env file
DATABASE_URL=postgres://user:pass@db:5432/mydb
API_KEY=secret123
```

```yaml
services:
  web:
    env_file:
      - .env
    environment:
      - NODE_ENV=production
```

---

### Best Practices

<div align="center">

| Practice | Description |
|:---:|:---:|
| **Use version 3.8+** | Latest features |
| **Use .env for secrets** | Don't commit secrets |
| **Use named volumes** | For production data |
| **Use depends_on** | Service dependencies |
| **Use restart policies** | Auto-restart on failure |
| **Separate dev/prod** | Different compose files |

</div>

---

### Docker Compose vs Docker Run

<div align="center">

**When to use each**

| Scenario | Use |
|:---:|:---:|
| **Single container** | `docker run` |
| **Multiple containers** | `docker compose` |
| **Quick testing** | `docker run` |
| **Development environment** | `docker compose` |
| **Production** | `docker compose` or orchestration |

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

