# RBAC (Role-Based Access Control) ⭐ MOST COMMON

**What it is:** Permissions assigned to roles, users get roles.

**Model:** `User → Role → Permissions`

## How RBAC Works

### Example Roles
```
Admin  → create_user, delete_user, manage_system
Editor → edit_post, publish_post
Viewer → read_post
```

### How It Works in APIs

**JWT contains role:**
```json
{
  "userId": 123,
  "role": "admin"
}
```

**API checks:**
```python
if role == "admin":
    allow()
else:
    deny()
```

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

## Pros

- ✅ Simple
- ✅ Easy to reason about
- ✅ Easy to implement
- ✅ Scales well

## Cons

- ❌ Role explosion (too many roles)
- ❌ Not flexible for complex rules
- ❌ Context-dependent permissions hard

## When to Use

- ✅ Most backend systems
- ✅ Internal tools
- ✅ Simple to medium complexity
- ❌ Fine-grained, context-dependent access

## Best Practices

- ✅ Keep roles simple (5-15 roles typical)
- ✅ Use hierarchical roles when appropriate
- ✅ Regular access reviews
- ✅ Document role permissions clearly

## Related Topics

- **[ABAC](./02-abac.md)** - More flexible than RBAC
- **[Least Privilege](./03-least-privilege.md)** - Principle to follow

