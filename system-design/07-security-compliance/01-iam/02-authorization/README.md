# Authorization

**Authorization answers: "What can you do?"**

Authorization determines what actions a user or service can perform after authentication. It's about permissions and access control.

## Auth vs Authorization (1-Line Clarity)

- **Authentication** → Who are you?
- **Authorization** → What are you allowed to do?

**You must authenticate first, then authorize.**

## Table of Contents

- **[01. RBAC (Role-Based Access Control)](./01-rbac.md)** ⭐ - Role-based permissions (most common)
- **[02. ABAC (Attribute-Based Access Control)](./02-abac.md)** ⭐ - Attribute-based permissions (powerful)
- **[03. Least Privilege](./03-least-privilege.md)** - Principle of least privilege
- **[04. Fine-Grained Permissions](./04-fine-grained-permissions.md)** - Granular access control
- **[05. Policy-Based Authorization](./05-policy-based-authorization.md)** - Centralized policy evaluation
- **[06. OAuth Scopes](./06-oauth-scopes.md)** - Scope-based permissions
- **[07. Resource Ownership](./07-resource-ownership.md)** - Ownership-based access
- **[08. Authorization Comparison](./08-authorization-comparison.md)** - Comparison of all methods

## How Authorization Works

Once the API knows who you are (via JWT, OAuth, etc.), it checks:

- **Role** - User's role
- **Permission** - Explicit permissions
- **Resource ownership** - Who owns the resource
- **Policy rules** - Policy engine evaluation

**Authorization answers:** Can this identity perform THIS action on THIS resource?

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

## Real-World Combinations

Most systems combine methods:

**Example:**
```
OAuth → authenticate
  ↓
JWT → carry identity
  ↓
RBAC → baseline access
  ↓
Ownership → resource check
  ↓
ABAC → edge cases
```

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
