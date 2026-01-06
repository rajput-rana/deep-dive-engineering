# Role-Based Access Control (RBAC)

**Reference:** [AlgoMaster - RBAC](https://algomaster.io/learn/system-design/rbac)

## Problem / Concept Overview

RBAC manages permissions by assigning roles to users. Instead of granting permissions directly, users get roles, and roles have permissions. This simplifies access control in large systems.

## Key Ideas

### Core Components

1. **Users:** People or systems accessing resources
2. **Roles:** Job functions or responsibilities (Admin, Editor, Viewer)
3. **Permissions:** Actions on resources (read, write, delete)
4. **Resources:** Objects being protected (files, databases, APIs)

### RBAC Model

```
User → Role → Permissions → Resources
```

**Example:**
- User: Alice
- Role: Editor
- Permissions: read, write
- Resources: Articles, Comments

## Why It Matters

**Scalability:** Managing permissions per user doesn't scale. Roles group users with similar needs.

**Maintainability:** Change permissions in one place (role) affects all users with that role.

**Security:** Principle of least privilege—users get minimum permissions needed.

**Compliance:** Easier to audit who has access to what.

## Real-World Examples

**AWS IAM:** Roles for EC2 instances, Lambda functions, users.

**GitHub:** Repository roles (Owner, Admin, Write, Read).

**Google Workspace:** Roles for team members (Admin, User, Viewer).

**Kubernetes:** RBAC for cluster access control.

## RBAC Models

### 1. Flat RBAC
- Users assigned to roles
- Roles have permissions
- Simple, common model

### 2. Hierarchical RBAC
```
Admin (all permissions)
  └── Editor (read, write)
      └── Viewer (read)
```
- Roles inherit permissions from parent roles
- Reduces duplication

### 3. Constrained RBAC
- Adds constraints (separation of duties)
- Example: User can't be both Accountant and Auditor

### 4. Symmetric RBAC
- Roles and permissions can be assigned to each other
- More flexible, more complex

## Permission Models

### 1. Resource-Based
```
Role: Editor
Permissions: 
  - articles:read
  - articles:write
  - comments:read
```

### 2. Action-Based
```
Role: Editor
Permissions:
  - read
  - write
  - delete
```

### 3. Attribute-Based (ABAC)
```
User.department == "Engineering" AND Resource.type == "Code"
```
- More flexible, more complex
- Context-aware permissions

## Implementation Patterns

### Database Schema

```sql
Users (id, name, email)
Roles (id, name)
Permissions (id, name, resource, action)
UserRoles (user_id, role_id)
RolePermissions (role_id, permission_id)
```

### API Design

```
GET  /users/{id}/roles
POST /users/{id}/roles
GET  /roles/{id}/permissions
POST /roles/{id}/permissions
```

## Tradeoffs

### RBAC vs ACL (Access Control Lists)
- **RBAC:** Role-based, easier to manage at scale
- **ACL:** Fine-grained, per-resource control

### RBAC vs ABAC (Attribute-Based)
- **RBAC:** Simple, role-based decisions
- **ABAC:** Context-aware, more flexible, complex

## Design Considerations

### Role Design
- **Too Many Roles:** Hard to manage, confusing
- **Too Few Roles:** Over-privileged users
- **Guideline:** 5-15 roles for most applications

### Permission Granularity
- **Too Coarse:** Over-privileged users
- **Too Fine:** Complex to manage
- **Balance:** Match business needs

### Dynamic Roles
- Some systems need context-dependent roles
- Example: Project-specific roles
- Consider hybrid approach

## Common Patterns

### 1. Default Roles
- New users get default role (Viewer)
- Explicit promotion required

### 2. Role Inheritance
- Hierarchical roles reduce duplication
- Admin inherits Editor permissions

### 3. Temporary Roles
- Time-limited access
- Useful for contractors, temporary access

### 4. Role Templates
- Predefined role sets
- Faster onboarding

## Security Best Practices

1. **Principle of Least Privilege:** Minimum permissions needed
2. **Regular Audits:** Review roles and permissions periodically
3. **Separation of Duties:** Critical operations require multiple roles
4. **Role Expiration:** Roles expire if not used
5. **Audit Logging:** Track all permission changes

## Challenges

### 1. Role Explosion
**Problem:** Too many roles to manage.

**Solution:** Use role hierarchies, role templates.

### 2. Context-Dependent Permissions
**Problem:** Permissions depend on context (project, department).

**Solution:** Hybrid RBAC + ABAC, or resource-specific roles.

### 3. Permission Inheritance
**Problem:** Complex inheritance rules.

**Solution:** Keep hierarchy simple, document clearly.

## Interview Tips

When discussing RBAC:
1. Identify roles based on user types
2. Define permissions per role
3. Consider hierarchical roles if needed
4. Discuss implementation (database schema, API)
5. Address edge cases (temporary access, context-dependent)

## Real-World Implementation

**Example: Blog Platform**

Roles:
- **Admin:** All permissions
- **Editor:** Create, edit, publish articles
- **Author:** Create, edit own articles
- **Viewer:** Read articles

Permissions:
- `articles:create`
- `articles:edit:own`
- `articles:edit:all`
- `articles:publish`
- `articles:read`

