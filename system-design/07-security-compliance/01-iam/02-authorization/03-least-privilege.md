# Least Privilege

**Principle:** Grant minimum permissions necessary.

**One-line:** Users and services should only have access to what they need, nothing more.

## Why Least Privilege?

- ✅ **Reduces attack surface** - Less access = less risk
- ✅ **Limits damage** - Compromised account has limited access
- ✅ **Compliance** - Required by many regulations
- ✅ **Best practice** - Security fundamental

## How to Implement

### 1. Start with No Access
- Default: Deny all
- Grant only what's needed

### 2. Regular Reviews
- Review access quarterly/annually
- Remove unnecessary access
- Document access decisions

### 3. Time-Limited Access
- Temporary access for specific tasks
- Auto-revoke after time period
- Just-in-time access

### 4. Scope Permissions
- Limit to specific resources
- Limit to specific actions
- Limit to specific time periods

## Examples

### ❌ Bad: Over-Privileged
```
User: Developer
Permissions: admin, delete_all_data, access_production_db
```

### ✅ Good: Least Privilege
```
User: Developer
Permissions: read_dev_db, write_dev_db, deploy_dev
```

## Best Practices

- ✅ Default deny
- ✅ Grant minimum needed
- ✅ Regular access reviews
- ✅ Document access decisions
- ✅ Use temporary access when possible
- ❌ Don't grant "just in case"
- ❌ Don't share admin accounts

## Related Topics

- **[RBAC](./01-rbac.md)** - Role-based access control
- **[Fine-Grained Permissions](./04-fine-grained-permissions.md)** - Granular access

