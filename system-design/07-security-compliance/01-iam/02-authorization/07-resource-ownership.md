# Resource-Based Authorization (Ownership Checks)

**What it is:** Access depends on who owns the resource.

**Example:** User can edit order only if `order.userId == user.id`

## How It Works

### Ownership Check
```python
def can_edit_order(user_id, order_id):
    order = get_order(order_id)
    return order.user_id == user_id
```

### API Implementation
```python
if resource.owner_id == user.id:
    allow()
else:
    deny()
```

## Common Patterns

### User-Owned Resources
- Posts, comments, orders
- Check: `resource.user_id == user.id`

### Organization-Owned Resources
- Company data, team resources
- Check: `resource.org_id == user.org_id`

### Project-Owned Resources
- Project-specific resources
- Check: `user in resource.project.members`

## Pros

- ✅ Simple
- ✅ Intuitive
- ✅ Natural access control
- ✅ Easy to understand

## Cons

- ❌ Requires DB lookup
- ❌ Logic spread across services
- ❌ Performance overhead

## When to Use

- ✅ User-generated content
- ✅ Multi-tenant apps
- ✅ Personal data
- ✅ User-owned resources

## Best Practices

- ✅ Cache ownership checks
- ✅ Index owner_id columns
- ✅ Combine with RBAC for admin override
- ✅ Document ownership rules

## Related Topics

- **[RBAC](./01-rbac.md)** - Baseline permissions
- **[Fine-Grained Permissions](./04-fine-grained-permissions.md)** - Granular access

