# Authorization Methods Comparison

**Quick reference for choosing the right authorization method.**

## Comparison Table

| Method | Granularity | Complexity | Typical Use | Performance |
|--------|------------|------------|-------------|-------------|
| **RBAC** | Medium | Low | Most apps | Fast |
| **Permissions** | Medium-High | Medium | Feature gating | Fast |
| **ABAC** | Very High | High | Enterprise | Medium |
| **Ownership** | High | Low | User content | Medium |
| **Policy-Based** | Very High | High | Large platforms | Medium |
| **OAuth Scopes** | Medium | Low | External APIs | Fast |
| **Claims-Based** | Medium | Low | Microservices | Fast |

## Real-World Combinations

Most systems combine methods:

**Example Architecture:**
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

## Common Interview Questions

**Q: Why not only RBAC?**
- RBAC breaks when rules depend on context or data
- Need ownership checks for user content
- Need ABAC for complex enterprise rules

**Q: Why put auth logic in JWT?**
- Performance - no DB lookup
- Scalability - stateless
- Speed - fast validation

**Q: When to avoid putting permissions in JWT?**
- When permissions change frequently
- When revocation needed immediately
- When token size matters

## Decision Tree

```
Need user context?
├─ Yes → Ownership checks
└─ No → Continue

Simple permissions?
├─ Yes → RBAC
└─ No → Continue

Complex rules?
├─ Yes → ABAC or Policy-Based
└─ No → Permissions-based

External API?
├─ Yes → OAuth Scopes
└─ No → Continue

Microservices?
├─ Yes → Claims-Based (JWT)
└─ No → RBAC
```

## Best Practices

- ✅ Start simple (RBAC)
- ✅ Add complexity only when needed
- ✅ Combine methods appropriately
- ✅ Document authorization logic
- ✅ Regular access reviews

