# ABAC (Attribute-Based Access Control) ⭐ POWERFUL

**What it is:** Decisions based on attributes, not roles.

**Attributes can be:**
- User attributes (department, location, clearance)
- Resource attributes (owner, classification, project)
- Environment attributes (time, IP address, device)

## Example Rule

```
Allow if:
  user.department == "finance"
  AND resource.owner == user.id
  AND request.time < 6pm
  AND user.clearance >= resource.classification
```

## How It Works

- Policy engine evaluates rules dynamically
- Rules can be complex and context-aware
- Decisions made at request time

## Pros

- ✅ Very flexible
- ✅ Fine-grained control
- ✅ Context-aware permissions
- ✅ Handles complex scenarios

## Cons

- ❌ Complex to implement
- ❌ Hard to debug
- ❌ Needs policy engine
- ❌ Performance overhead

## When to Use

- ✅ Enterprises
- ✅ Compliance-heavy systems
- ✅ Complex access rules
- ✅ Multi-tenant applications
- ❌ Simple systems (overkill)

## ABAC vs RBAC

| Aspect | RBAC | ABAC |
|--------|------|------|
| **Granularity** | Medium | Very High |
| **Complexity** | Low | High |
| **Flexibility** | Low | Very High |
| **Use Case** | Most apps | Enterprise |

## Best Practices

- ✅ Use policy engine (OPA, XACML)
- ✅ Document policies clearly
- ✅ Test policies thoroughly
- ✅ Monitor policy performance

## Related Topics

- **[RBAC](./01-rbac.md)** - Simpler alternative
- **[Policy-Based Authorization](./05-policy-based-authorization.md)** - Implementation approach

