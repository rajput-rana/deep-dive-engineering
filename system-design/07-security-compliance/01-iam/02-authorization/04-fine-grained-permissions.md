# Fine-Grained Permissions

**What it is:** Granular, resource-specific access control.

**Example:** User can edit their own posts, but not others' posts.

## Permission Levels

### Coarse-Grained
```
Role: Editor
Permission: edit_post (all posts)
```

### Fine-Grained
```
User: Alice
Permission: edit_post WHERE owner_id = user.id
```

## Fine-Grained Patterns

### Resource Ownership
- User can only access their own resources
- Check: `resource.owner_id == user.id`

### Attribute-Based
- Permissions based on resource attributes
- Check: `resource.department == user.department`

### Time-Based
- Permissions valid only at certain times
- Check: `current_time < permission.expires_at`

### Action-Specific
- Different permissions for different actions
- Examples: `read:invoice`, `refund:payment`, `export:data`

## Implementation Approaches

### 1. Permission-Based
```json
{
  "permissions": [
    "read:orders",
    "write:own_orders",
    "refund:own_payments"
  ]
}
```

### 2. Claims-Based (JWT)
```json
{
  "userId": 123,
  "permissions": ["read", "write"],
  "resourceScope": "own"
}
```

### 3. Policy-Based
```python
if user.id == resource.owner_id:
    allow()
elif user.role == "admin":
    allow()
else:
    deny()
```

## Pros

- ✅ Precise access control
- ✅ Better security
- ✅ Flexible permissions
- ✅ Resource-specific rules

## Cons

- ❌ More complex to implement
- ❌ Performance overhead
- ❌ Harder to manage at scale

## When to Use

- ✅ Multi-tenant applications
- ✅ User-generated content
- ✅ Financial systems
- ✅ Healthcare systems
- ❌ Simple applications (overkill)

## Best Practices

- ✅ Combine with RBAC for baseline
- ✅ Use ownership checks for user content
- ✅ Cache permission decisions
- ✅ Document permission logic

## Related Topics

- **[RBAC](./01-rbac.md)** - Baseline permissions
- **[ABAC](./02-abac.md)** - Attribute-based approach
- **[Least Privilege](./03-least-privilege.md)** - Principle to follow

