# Authorization

**Authorization answers: "What can you do?"**

Authorization determines what actions a user or service can perform after authentication. It's about permissions and access control.

## Table of Contents

- **[01. RBAC (Role-Based Access Control)](./01-rbac.md)** - Role-based permissions
- **[02. ABAC (Attribute-Based Access Control)](./02-abac.md)** - Attribute-based permissions
- **[03. Least Privilege](./03-least-privilege.md)** - Principle of least privilege
- **[04. Fine-Grained Permissions](./04-fine-grained-permissions.md)** - Granular access control

## Authorization Models

### RBAC (Role-Based Access Control)
- Users assigned to roles
- Roles have permissions
- Simple and scalable
- **Use Cases:** Most applications, enterprise systems

### ABAC (Attribute-Based Access Control)
- Context-aware permissions
- Based on attributes (user, resource, environment)
- More flexible than RBAC
- **Use Cases:** Complex access control, dynamic permissions

### ACL (Access Control Lists)
- Per-resource permissions
- Fine-grained control
- **Use Cases:** File systems, specific resources

## Authorization Patterns

### Policy-Based Authorization
- Centralized policies
- Policy engine evaluates requests
- **Examples:** AWS IAM Policies, OPA (Open Policy Agent)

### Permission-Based Authorization
- Explicit permissions
- Check permissions directly
- **Examples:** Database permissions, API permissions

## Best Practices

- ✅ Follow least privilege principle
- ✅ Regular access reviews
- ✅ Audit all authorization decisions
- ✅ Use appropriate model (RBAC vs ABAC)
- ✅ Implement fine-grained permissions when needed

## Related Topics

- **[Authentication](../01-authentication/)** - Identity verification
- **[Service Identity](../03-service-identity/)** - Service authorization
- **[Data Security](../../03-data-security-privacy/)** - Data access control

