# 🏗️ Terraform

<div align="center">

**Infrastructure as Code: define and manage infrastructure declaratively**

[![Terraform](https://img.shields.io/badge/Terraform-IaC-blue?style=for-the-badge)](./)
[![Infrastructure](https://img.shields.io/badge/Infrastructure-as%20Code-green?style=for-the-badge)](./)
[![Automation](https://img.shields.io/badge/Automation-Declarative-orange?style=for-the-badge)](./)

*Master Terraform: provision and manage infrastructure with code*

</div>

---

## 🎯 What is Terraform?

<div align="center">

**Terraform is an Infrastructure as Code (IaC) tool that lets you define and provision infrastructure using declarative configuration files.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **📝 Infrastructure as Code** | Define infrastructure in code |
| **🔄 Declarative** | Describe desired state, not steps |
| **📦 Providers** | Plugins for cloud/platform APIs |
| **🗂️ State** | Tracks current infrastructure |
| **🔄 Plan** | Preview changes before applying |
| **✅ Apply** | Create/update infrastructure |

**Mental Model:** Think of Terraform like a blueprint - you describe what infrastructure you want, and Terraform figures out how to build it.

</div>

---

## 🏗️ Why Terraform Matters

<div align="center">

### Problems Terraform Solves

| Problem | Without Terraform | With Terraform |
|:---:|:---:|
| **Manual Setup** | Error-prone, slow | Automated, repeatable |
| **Inconsistent Environments** | Different configs | Same code everywhere |
| **No Version Control** | Can't track changes | Infrastructure in Git |
| **Drift** | Manual changes diverge | State tracks reality |
| **Documentation** | Outdated docs | Code is documentation |

### Benefits

| Benefit | Description |
|:---:|:---:|
| **Version Control** | Infrastructure in Git |
| **Reproducibility** | Same code = same infrastructure |
| **Consistency** | Dev, staging, prod identical |
| **Collaboration** | Code review for infrastructure |
| **Disaster Recovery** | Recreate from code |

</div>

---

## 🏗️ Core Concepts

<div align="center">

### Infrastructure as Code (IaC)

**Define infrastructure in code files**

**Benefits:**
- ✅ Version controlled
- ✅ Repeatable
- ✅ Testable
- ✅ Documented
- ✅ Reviewable

---

### Declarative vs Imperative

| Approach | Description | Example |
|:---:|:---:|:---:|
| **Declarative** | Describe desired state | "I want 3 servers" |
| **Imperative** | Describe steps | "Create server 1, then 2, then 3" |

**Terraform is declarative** - you describe what you want, Terraform figures out how.

---

### Providers

**Plugins that interact with cloud/platform APIs**

| Provider | Purpose | Example |
|:---:|:---:|:---:|
| **AWS** | Amazon Web Services | EC2, S3, RDS |
| **GCP** | Google Cloud Platform | Compute Engine, GKE |
| **Azure** | Microsoft Azure | Virtual Machines, AKS |
| **Kubernetes** | Kubernetes clusters | Pods, Services |
| **Docker** | Docker containers | Containers, images |

</div>

---

## 📝 Terraform Configuration

<div align="center">

### Basic Terraform File

```hcl
# Configure provider
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Define resource
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    Name = "WebServer"
  }
}

# Output
output "instance_ip" {
  value = aws_instance.web.public_ip
}
```

---

### Key Elements

| Element | Purpose | Example |
|:---:|:---:|:---:|
| **terraform block** | Configure Terraform | Provider requirements |
| **provider** | Configure provider | AWS, GCP, Azure |
| **resource** | Define infrastructure | EC2 instance, S3 bucket |
| **variable** | Input parameters | `var.instance_type` |
| **output** | Return values | IP addresses, IDs |
| **module** | Reusable components | VPC module |

</div>

---

## 🔄 Terraform Workflow

<div align="center">

### Standard Workflow

```
terraform init    → Initialize Terraform
terraform plan    → Preview changes
terraform apply   → Create/update infrastructure
terraform destroy → Remove infrastructure
```

---

### Commands Explained

| Command | Purpose | When to Use |
|:---:|:---:|:---:|
| **terraform init** | Initialize workspace | First time, new providers |
| **terraform plan** | Preview changes | Before applying |
| **terraform apply** | Apply changes | Create/update infrastructure |
| **terraform destroy** | Remove infrastructure | Cleanup, testing |
| **terraform validate** | Check syntax | Before planning |
| **terraform fmt** | Format code | Code formatting |

</div>

---

## 🗂️ State Management

<div align="center">

### What is State?

**Terraform state tracks the current state of your infrastructure**

**Why State Matters:**
- Maps configuration to real resources
- Tracks resource dependencies
- Enables updates and deletions
- Prevents duplicate resources

---

### State Storage Options

| Option | Description | Use Case |
|:---:|:---:|:---:|
| **Local** | File on disk | Development, single user |
| **Remote** | Shared storage | Team collaboration |
| **S3 + DynamoDB** | AWS backend | AWS infrastructure |
| **Terraform Cloud** | Managed service | Teams, CI/CD |

---

### State Best Practices

| Practice | Why |
|:---:|:---:|
| **Remote state** | Team collaboration |
| **State locking** | Prevent conflicts |
| **State encryption** | Security |
| **Backup state** | Disaster recovery |

</div>

---

## 📦 Modules

<div align="center">

### What are Modules?

**Reusable Terraform configurations**

**Benefits:**
- ✅ Reusability
- ✅ Abstraction
- ✅ Organization
- ✅ Testing

---

### Module Example

**Module Structure:**
```
modules/
  vpc/
    main.tf
    variables.tf
    outputs.tf
```

**Using Module:**
```hcl
module "vpc" {
  source = "./modules/vpc"
  
  vpc_cidr = "10.0.0.0/16"
  environment = "production"
}
```

</div>

---

## 🎯 Use Cases

<div align="center">

### When to Use Terraform

| Use Case | Description |
|:---:|:---:|
| **Multi-cloud** | Manage multiple clouds |
| **Infrastructure Versioning** | Track infrastructure changes |
| **Disaster Recovery** | Recreate from code |
| **Environment Parity** | Dev = Staging = Prod |
| **Team Collaboration** | Code review infrastructure |

### When NOT to Use Terraform

| Scenario | Alternative |
|:---:|:---:|
| **Simple, one-time setup** | Manual or cloud console |
| **Very dynamic infrastructure** | May need imperative tools |
| **Legacy systems** | May not have providers |

</div>

---

## ⚖️ Terraform vs Alternatives

<div align="center">

### Infrastructure as Code Tools

| Tool | Type | Best For |
|:---:|:---:|:---:|
| **Terraform** | Declarative, multi-cloud | Multi-cloud, complex |
| **CloudFormation** | AWS-native | AWS-only |
| **Ansible** | Configuration management | Configuration, not provisioning |
| **Pulumi** | Code-based IaC | Developers prefer code |
| **CDK** | Cloud-specific | AWS, Azure, GCP |

---

### Terraform vs CloudFormation

| Aspect | Terraform | CloudFormation |
|:---:|:---:|:---:|
| **Cloud Support** | Multi-cloud | AWS only |
| **Language** | HCL | JSON/YAML |
| **State Management** | Explicit | Implicit |
| **Community** | Large | AWS-focused |

</div>

---

## 💡 Best Practices

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Version control** | Track changes |
| **Use modules** | Reusability |
| **Remote state** | Team collaboration |
| **State locking** | Prevent conflicts |
| **Plan before apply** | Review changes |
| **Tag resources** | Organization |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Local state in team** | Conflicts | Remote state |
| **Hardcode values** | Inflexible | Use variables |
| **No state locking** | Conflicts | Enable locking |
| **Manual changes** | Drift | Only change via Terraform |

</div>

---

## 🎓 For Engineering Leaders

<div align="center">

### Key Questions to Ask

| Question | Why It Matters |
|:---:|:---:|
| **Are we using IaC?** | Infrastructure management |
| **What's our state strategy?** | Team collaboration |
| **How do we handle secrets?** | Security |
| **What's our module strategy?** | Reusability |
| **How do we test infrastructure?** | Quality assurance |

### Decision Points

| Decision | Consideration |
|:---:|:---:|
| **Terraform vs Cloud-native** | Multi-cloud vs single cloud |
| **Remote state location** | Security, access |
| **Module organization** | Reusability, maintenance |

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **Terraform Purpose** | Infrastructure as Code |
| **Declarative** | Describe desired state |
| **State** | Tracks current infrastructure |
| **Providers** | Connect to cloud/platform APIs |
| **Benefits** | Version control, reproducibility, consistency |

**💡 Remember:** Terraform enables infrastructure to be managed like code - versioned, reviewed, and reproducible.

</div>

---

<div align="center">

**Master Terraform for infrastructure automation! 🚀**

*Define and manage infrastructure with code for consistency and reproducibility.*

</div>

