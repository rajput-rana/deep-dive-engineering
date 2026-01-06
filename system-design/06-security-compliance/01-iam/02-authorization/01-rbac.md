# 🔐 Role-Based Access Control (RBAC)

<div align="center">

**Manage permissions through roles, not individual users**

[![RBAC](https://img.shields.io/badge/RBAC-Most%20Common-blue?style=for-the-badge)](./)
[![Authorization](https://img.shields.io/badge/Authorization-Role--Based-green?style=for-the-badge)](./)
[![Security](https://img.shields.io/badge/Security-Access%20Control-orange?style=for-the-badge)](./)

*Master RBAC: role design, permission models, and implementation patterns*

</div>

---

## 🎯 What is RBAC?

<div align="center">

**RBAC manages permissions by assigning roles to users. Instead of granting permissions directly, users get roles, and roles have permissions. This simplifies access control in large systems.**

### Core Model

```
User → Role → Permissions → Resources
```

**Example:**
- **User:** Alice
- **Role:** Editor
- **Permissions:** read, write
- **Resources:** Articles, Comments

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **👥 Role-Based** | Permissions assigned to roles, not users |
| **📊 Scalable** | Manage permissions at scale |
| **🔒 Secure** | Principle of least privilege |
| **✅ Simple** | Easy to understand and implement |
| **📝 Auditable** | Easy to track who has access |

**💡 Mental Model:** Think of RBAC like job titles in a company - a "Manager" role has certain permissions, and anyone with that role gets those permissions automatically.

</div>

---

## 🏗️ Core Components

<div align="center">

### RBAC Components

| Component | Description | Example |
|:---:|:---:|:---:|
| **Users** | People or systems accessing resources | Alice, Bob, API service |
| **Roles** | Job functions or responsibilities | Admin, Editor, Viewer |
| **Permissions** | Actions on resources | read, write, delete |
| **Resources** | Objects being protected | Files, databases, APIs |

### Example Structure

```
User: Alice
  └── Role: Editor
      └── Permissions:
          - articles:read
          - articles:write
          - comments:read
          - comments:write
      └── Resources:
          - Articles collection
          - Comments collection
```

</div>

---

## 🎯 Why RBAC Matters

<div align="center">

### Key Benefits

| Benefit | Description | Impact |
|:---:|:---:|:---:|
| **📈 Scalability** | Managing permissions per user doesn't scale | Roles group users with similar needs |
| **🔧 Maintainability** | Change permissions in one place (role) | Affects all users with that role |
| **🛡️ Security** | Principle of least privilege | Users get minimum permissions needed |
| **📋 Compliance** | Easier to audit who has access to what | Compliance and governance |
| **⚡ Simplicity** | Easy to understand and implement | Faster development |

**Without RBAC:**
- ❌ Manage permissions for each user individually
- ❌ Difficult to scale
- ❌ Hard to maintain
- ❌ Complex audits

**With RBAC:**
- ✅ Manage permissions through roles
- ✅ Scales to thousands of users
- ✅ Easy to maintain
- ✅ Simple audits

</div>

---

## 🌍 Real-World Examples

<div align="center">

### Industry Implementations

| Platform | RBAC Implementation | Example Roles |
|:---:|:---:|:---:|
| **AWS IAM** | Roles for EC2 instances, Lambda functions, users | Administrator, PowerUser, ReadOnly |
| **GitHub** | Repository roles | Owner, Admin, Write, Read |
| **Google Workspace** | Roles for team members | Super Admin, Admin, User, Viewer |
| **Kubernetes** | RBAC for cluster access control | ClusterAdmin, Admin, Edit, View |
| **Salesforce** | Profiles and permission sets | System Administrator, Standard User |

**Key Learnings:**
- Roles align with job functions
- Hierarchical roles reduce duplication
- Regular access reviews essential
- Clear documentation critical

</div>

---

## 📊 RBAC Models

<div align="center">

### 1. Flat RBAC

**Simple, common model**

| Aspect | Description |
|:---:|:---:|
| **Structure** | Users assigned to roles, roles have permissions |
| **Complexity** | Simple |
| **Use Case** | Most applications |

**Example:**
```
User: Alice → Role: Editor → Permissions: [read, write]
User: Bob → Role: Viewer → Permissions: [read]
```

**Pros:**
- ✅ Simple to implement
- ✅ Easy to understand
- ✅ Fast permission checks

**Cons:**
- ❌ No role inheritance
- ❌ Can lead to role explosion

---

### 2. Hierarchical RBAC

**Roles inherit permissions from parent roles**

```
Admin (all permissions)
  └── Editor (read, write)
      └── Viewer (read)
```

| Aspect | Description |
|:---:|:---:|
| **Structure** | Roles inherit from parent roles |
| **Complexity** | Medium |
| **Use Case** | Organizations with clear hierarchy |

**Example:**
```
Admin inherits: [create, read, update, delete]
  └── Editor inherits: [read, update]
      └── Viewer inherits: [read]
```

**Pros:**
- ✅ Reduces duplication
- ✅ Natural hierarchy
- ✅ Easier role management

**Cons:**
- ❌ More complex to implement
- ❌ Can be confusing if hierarchy is deep

---

### 3. Constrained RBAC

**Adds constraints (separation of duties)**

| Aspect | Description |
|:---:|:---:|
| **Structure** | Roles with constraints |
| **Complexity** | High |
| **Use Case** | Financial, compliance requirements |

**Example:**
```
Constraint: User can't be both Accountant and Auditor
Constraint: User can't approve and execute same transaction
```

**Pros:**
- ✅ Enforces separation of duties
- ✅ Compliance support
- ✅ Security enhancement

**Cons:**
- ❌ Complex to implement
- ❌ Requires constraint engine

---

### 4. Symmetric RBAC

**Roles and permissions can be assigned to each other**

| Aspect | Description |
|:---:|:---:|
| **Structure** | Bidirectional role-permission assignment |
| **Complexity** | Very High |
| **Use Case** | Complex enterprise systems |

**Pros:**
- ✅ Maximum flexibility
- ✅ Complex permission models

**Cons:**
- ❌ Very complex
- ❌ Hard to reason about
- ❌ Rarely needed

</div>

---

## 🔑 Permission Models

<div align="center">

### 1. Resource-Based Permissions

**Permissions tied to specific resources**

```
Role: Editor
Permissions: 
  - articles:read
  - articles:write
  - comments:read
  - comments:write
```

**Format:** `resource:action`

**Example:**
```python
permissions = [
    "articles:read",
    "articles:write",
    "comments:read",
    "comments:write"
]
```

**Pros:**
- ✅ Clear resource-level control
- ✅ Easy to understand
- ✅ Good for REST APIs

---

### 2. Action-Based Permissions

**Permissions are actions, not resource-specific**

```
Role: Editor
Permissions:
  - read
  - write
  - delete
```

**Format:** `action`

**Example:**
```python
permissions = ["read", "write", "delete"]
```

**Pros:**
- ✅ Simple
- ✅ Reusable across resources

**Cons:**
- ❌ Less granular control
- ❌ Harder to restrict specific resources

---

### 3. Attribute-Based (ABAC)

**Context-aware permissions**

```
User.department == "Engineering" AND Resource.type == "Code"
```

**Format:** Policy-based rules

**Example:**
```python
if user.department == "Engineering" and resource.type == "Code":
    allow()
```

**Pros:**
- ✅ Very flexible
- ✅ Context-aware
- ✅ Fine-grained control

**Cons:**
- ❌ Complex to implement
- ❌ Harder to reason about
- ❌ Performance overhead

**💡 Note:** ABAC is more flexible than RBAC but also more complex. Consider hybrid RBAC + ABAC for complex scenarios.

</div>

---

## 💻 Implementation Patterns

<div align="center">

### Database Schema

**Core RBAC Tables:**

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE
);

-- Roles table
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE,
    description TEXT
);

-- Permissions table
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE,
    resource VARCHAR(255),
    action VARCHAR(255)
);

-- User-Role mapping
CREATE TABLE user_roles (
    user_id INT REFERENCES users(id),
    role_id INT REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);

-- Role-Permission mapping
CREATE TABLE role_permissions (
    role_id INT REFERENCES roles(id),
    permission_id INT REFERENCES permissions(id),
    PRIMARY KEY (role_id, permission_id)
);
```

---

### API Design

**RESTful RBAC APIs:**

```
GET    /users/{id}/roles              # Get user roles
POST   /users/{id}/roles              # Assign role to user
DELETE /users/{id}/roles/{role_id}    # Remove role from user

GET    /roles                         # List all roles
GET    /roles/{id}                    # Get role details
POST   /roles                         # Create role
PUT    /roles/{id}                    # Update role
DELETE /roles/{id}                    # Delete role

GET    /roles/{id}/permissions        # Get role permissions
POST   /roles/{id}/permissions        # Add permission to role
DELETE /roles/{id}/permissions/{perm_id} # Remove permission

GET    /permissions                   # List all permissions
```

---

### JWT Implementation

**JWT contains role:**

```json
{
  "userId": 123,
  "email": "alice@example.com",
  "role": "editor",
  "permissions": ["articles:read", "articles:write"]
}
```

**API checks:**

```python
def check_permission(user_role, required_permission):
    role_permissions = {
        "admin": ["*"],  # All permissions
        "editor": ["articles:read", "articles:write", "comments:read"],
        "viewer": ["articles:read"]
    }
    
    user_perms = role_permissions.get(user_role, [])
    
    if "*" in user_perms:
        return True
    
    return required_permission in user_perms
```

---

### Middleware Pattern

**Express.js Example:**

```javascript
const checkRole = (requiredRole) => {
  return (req, res, next) => {
    const userRole = req.user.role;
    
    if (userRole === requiredRole || userRole === 'admin') {
      next();
    } else {
      res.status(403).json({ error: 'Forbidden' });
    }
  };
};

// Usage
app.delete('/users/:id', checkRole('admin'), deleteUser);
```

</div>

---

## ⚖️ RBAC vs Alternatives

<div align="center">

### RBAC vs ACL (Access Control Lists)

| Aspect | RBAC | ACL |
|:---:|:---:|:---:|
| **Granularity** | Role-based | Per-resource |
| **Scalability** | Better at scale | Harder to manage |
| **Management** | Centralized | Distributed |
| **Use Case** | Most applications | Fine-grained control |

**ACL Example:**
```
File: document.pdf
  - user:alice → read, write
  - user:bob → read
```

**RBAC Example:**
```
Role: Editor → documents:read, documents:write
  - user:alice → Editor
  - user:bob → Viewer
```

---

### RBAC vs ABAC (Attribute-Based Access Control)

| Aspect | RBAC | ABAC |
|:---:|:---:|:---:|
| **Complexity** | Simple | Complex |
| **Flexibility** | Role-based | Context-aware |
| **Performance** | Fast | Slower |
| **Use Case** | Simple to medium | Complex rules |

**When to Use RBAC:**
- ✅ Most backend systems
- ✅ Internal tools
- ✅ Simple to medium complexity

**When to Use ABAC:**
- ✅ Fine-grained, context-dependent access
- ✅ Complex business rules
- ✅ Dynamic permissions

**💡 Hybrid Approach:** Use RBAC for base permissions, ABAC for exceptions.

</div>

---

## 🎨 Design Considerations

<div align="center">

### Role Design

| Consideration | Description | Guideline |
|:---:|:---:|:---:|
| **Too Many Roles** | Hard to manage, confusing | 5-15 roles for most applications |
| **Too Few Roles** | Over-privileged users | Balance granularity |
| **Role Naming** | Clear, descriptive names | Use job function names |
| **Role Scope** | Organization-wide vs resource-specific | Start broad, narrow as needed |

**Role Design Checklist:**
- [ ] Roles align with job functions
- [ ] Clear naming conventions
- [ ] Appropriate granularity
- [ ] Documented permissions

---

### Permission Granularity

| Level | Description | Example |
|:---:|:---:|:---:|
| **Too Coarse** | Over-privileged users | Single "admin" permission |
| **Too Fine** | Complex to manage | Separate permission per field |
| **Balanced** | Match business needs | Resource:action format |

**Best Practice:** Start with coarse permissions, refine as needed.

---

### Dynamic Roles

**Context-Dependent Roles:**

| Scenario | Solution |
|:---:|:---:|
| **Project-specific roles** | Resource-specific roles |
| **Time-limited access** | Temporary roles with expiration |
| **Department-specific** | Hybrid RBAC + ABAC |

**Example:**
```python
# Project-specific role
role = f"project_{project_id}_editor"

# Temporary role
role = {
    "name": "contractor",
    "expires_at": "2024-12-31"
}
```

</div>

---

## 🔄 Common Patterns

<div align="center">

### 1. Default Roles

**New users get default role**

| Pattern | Description | Example |
|:---:|:---:|:---:|
| **Default Role** | New users get Viewer role | Auto-assign on signup |
| **Explicit Promotion** | Admin must promote | Manual role assignment |
| **Self-Service** | Users request roles | Approval workflow |

**Implementation:**
```python
def create_user(email):
    user = User.create(email=email)
    default_role = Role.get(name="viewer")
    user.assign_role(default_role)
    return user
```

---

### 2. Role Inheritance

**Hierarchical roles reduce duplication**

```
Admin (all permissions)
  └── Editor (read, write)
      └── Viewer (read)
```

**Benefits:**
- ✅ Reduces permission duplication
- ✅ Natural hierarchy
- ✅ Easier maintenance

---

### 3. Temporary Roles

**Time-limited access**

| Use Case | Description |
|:---:|:---:|
| **Contractors** | Temporary access for contractors |
| **Projects** | Project-specific temporary access |
| **Emergency Access** | Time-limited elevated access |

**Example:**
```python
role = Role.create(
    name="contractor",
    expires_at=datetime.now() + timedelta(days=30)
)
```

---

### 4. Role Templates

**Predefined role sets**

| Template | Roles Included |
|:---:|:---:|
| **Developer** | Code:read, Code:write, Deploy:execute |
| **QA** | Code:read, Test:execute |
| **DevOps** | Deploy:execute, Monitor:read |

**Benefits:**
- ✅ Faster onboarding
- ✅ Consistent permissions
- ✅ Easy to update

</div>

---

## 🛡️ Security Best Practices

<div align="center">

### Core Principles

| Practice | Description | Implementation |
|:---:|:---:|:---:|
| **Principle of Least Privilege** | Minimum permissions needed | Start with minimal roles |
| **Regular Audits** | Review roles and permissions periodically | Quarterly access reviews |
| **Separation of Duties** | Critical operations require multiple roles | Constrained RBAC |
| **Role Expiration** | Roles expire if not used | Automatic expiration |
| **Audit Logging** | Track all permission changes | Log all role assignments |

### Implementation Checklist

- [ ] Implement principle of least privilege
- [ ] Set up regular access reviews
- [ ] Enable audit logging
- [ ] Implement role expiration
- [ ] Document all roles and permissions
- [ ] Test permission checks thoroughly
- [ ] Monitor for privilege escalation

</div>

---

## 🚧 Challenges & Solutions

<div align="center">

### 1. Role Explosion

**Problem:** Too many roles to manage.

**Solutions:**

- **Use Role Hierarchies:** Inherit permissions from parent roles
- **Role Templates:** Predefined role sets
- **Combine Roles:** Allow users to have multiple roles
- **Regular Cleanup:** Remove unused roles

**Example:**
```
Instead of:
- Project1_Editor
- Project2_Editor
- Project3_Editor

Use:
- Editor (base role)
- Project-specific permissions (ABAC or resource-specific)
```

---

### 2. Context-Dependent Permissions

**Problem:** Permissions depend on context (project, department).

**Solutions:**

- **Hybrid RBAC + ABAC:** RBAC for base, ABAC for context
- **Resource-Specific Roles:** Project-specific roles
- **Dynamic Role Assignment:** Assign roles based on context

**Example:**
```python
# RBAC base
role = "editor"

# ABAC context
if user.department == resource.department:
    allow()
```

---

### 3. Permission Inheritance

**Problem:** Complex inheritance rules.

**Solutions:**

- **Keep Hierarchy Simple:** Limit depth to 2-3 levels
- **Document Clearly:** Document all inheritance rules
- **Test Thoroughly:** Test inheritance paths
- **Use Tools:** RBAC management tools

---

### 4. Cross-Resource Permissions

**Problem:** Permissions span multiple resources.

**Solutions:**

- **Composite Permissions:** Combine resource permissions
- **Wildcard Permissions:** Use wildcards for related resources
- **Permission Groups:** Group related permissions

**Example:**
```python
# Composite permission
permission = "content:manage"  # Includes articles, comments, media

# Wildcard
permission = "articles:*"  # All article actions
```

</div>

---

## 🎓 Interview Tips

<div align="center">

### Key Points to Cover

When discussing RBAC in interviews:

1. **Identify Roles:** Based on user types and job functions
2. **Define Permissions:** Per role, match business needs
3. **Consider Hierarchy:** Hierarchical roles if needed
4. **Discuss Implementation:** Database schema, API design
5. **Address Edge Cases:** Temporary access, context-dependent permissions
6. **Security Considerations:** Least privilege, audits, separation of duties

### Common Interview Questions

| Question | Key Points |
|:---:|:---:|
| **How would you implement RBAC?** | Database schema, API design, middleware |
| **How do you handle role explosion?** | Hierarchies, templates, regular cleanup |
| **What about context-dependent permissions?** | Hybrid RBAC + ABAC, resource-specific roles |
| **How do you ensure security?** | Least privilege, audits, logging |
| **RBAC vs ABAC?** | RBAC for simple, ABAC for complex |

</div>

---

## 💡 Real-World Implementation

<div align="center">

### Example: Blog Platform

**Roles:**

| Role | Description | Permissions |
|:---:|:---:|:---:|
| **Admin** | Full system access | All permissions |
| **Editor** | Content management | Create, edit, publish articles |
| **Author** | Content creation | Create, edit own articles |
| **Viewer** | Read-only access | Read articles |

**Permissions:**

```
articles:create      # Create new articles
articles:edit:own    # Edit own articles
articles:edit:all    # Edit any article
articles:publish     # Publish articles
articles:read        # Read articles
comments:create      # Create comments
comments:moderate    # Moderate comments
users:manage         # Manage users
```

**Role-Permission Mapping:**

```
Admin:
  - articles:*
  - comments:*
  - users:*

Editor:
  - articles:create
  - articles:edit:all
  - articles:publish
  - articles:read
  - comments:moderate

Author:
  - articles:create
  - articles:edit:own
  - articles:read
  - comments:create

Viewer:
  - articles:read
  - comments:create
```

</div>

---

## 📊 Best Practices Summary

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Keep roles simple** | 5-15 roles typical, easy to manage |
| **Use hierarchical roles** | When appropriate, reduces duplication |
| **Regular access reviews** | Ensure permissions are still needed |
| **Document role permissions** | Clear documentation essential |
| **Start with least privilege** | Security best practice |
| **Implement audit logging** | Track all permission changes |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Too many roles** | Hard to manage | Use hierarchies, templates |
| **Over-privileged users** | Security risk | Principle of least privilege |
| **No access reviews** | Stale permissions | Regular audits |
| **Complex inheritance** | Hard to reason about | Keep hierarchy simple |
| **No documentation** | Confusion | Document all roles |

</div>

---

## 🔗 Related Topics

<div align="center">

| Topic | Description | Link |
|:---:|:---:|:---:|
| **[ABAC](./02-abac.md)** | More flexible than RBAC | [Explore →](./02-abac.md) |
| **[Least Privilege](./03-least-privilege.md)** | Security principle | [Explore →](./03-least-privilege.md) |
| **[Fine-Grained Permissions](./04-fine-grained-permissions.md)** | Granular access control | [Explore →](./04-fine-grained-permissions.md) |

</div>

---

## 🎯 Summary

<div align="center">

### Key Takeaways

| Concept | Key Point |
|:---:|:---:|
| **RBAC Model** | User → Role → Permissions → Resources |
| **Core Benefit** | Scalable permission management |
| **Role Design** | 5-15 roles typical, align with job functions |
| **Permission Models** | Resource-based, action-based, attribute-based |
| **Implementation** | Database schema, API design, middleware |
| **Security** | Least privilege, audits, logging |

**💡 Remember:** RBAC is the most common authorization model. Keep it simple, document clearly, and review regularly.

</div>

---

<div align="center">

**Master RBAC for scalable, secure access control! 🚀**

*RBAC simplifies permission management by grouping users into roles, making access control scalable and maintainable.*

</div>
