# Policy-Based Authorization

**What it is:** Centralized policy evaluation system.

**Tools:** Open Policy Agent (OPA), AWS IAM policies, XACML

## How It Works

### Policy Engine
- Centralized policy evaluation
- Policies written in declarative language
- Evaluated at request time

### Example Policy (OPA)
```rego
allow {
    user.role == "admin"
}

allow {
    user.id == resource.owner_id
    resource.type == "post"
}
```

## Policy Types

### 1. Allow/Deny Policies
- Explicit allow or deny rules
- First match wins or all must pass

### 2. Attribute-Based Policies
- Decisions based on attributes
- Dynamic evaluation

### 3. Time-Based Policies
- Policies valid at certain times
- Temporal access control

## Pros

- ✅ Centralized logic
- ✅ Highly scalable
- ✅ Auditable
- ✅ Version controlled
- ✅ Testable

## Cons

- ❌ Learning curve
- ❌ Extra infrastructure
- ❌ Performance overhead
- ❌ Debugging complexity

## When to Use

- ✅ Large distributed systems
- ✅ Multi-team platforms
- ✅ Complex authorization rules
- ✅ Compliance requirements
- ❌ Simple systems (overkill)

## Best Practices

- ✅ Version control policies
- ✅ Test policies thoroughly
- ✅ Monitor policy performance
- ✅ Document policy decisions
- ✅ Use policy as code

## Related Topics

- **[ABAC](./02-abac.md)** - Attribute-based access control
- **[Fine-Grained Permissions](./04-fine-grained-permissions.md)** - Granular access

