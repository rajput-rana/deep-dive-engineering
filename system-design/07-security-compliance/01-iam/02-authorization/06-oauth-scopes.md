# OAuth Scopes

**What scopes are:** Permissions that define what a token can do.

**Example:** `read:orders`, `write:orders`

## How Scopes Work

### Token with Scopes
```json
{
  "scope": "read:orders write:orders",
  "sub": "user123"
}
```

### API Checks Scope
```python
if "write:orders" in token.scope:
    allow()
else:
    deny()
```

## Scope Format

### Standard Format
```
read:orders
write:orders
admin:users
```

### Scope Structure
- **Action:** `read`, `write`, `admin`
- **Resource:** `orders`, `users`, `posts`

## Scope Best Practices

- ✅ Use descriptive scope names
- ✅ Follow naming conventions
- ✅ Document scope permissions
- ✅ Request minimum scopes needed
- ✅ Validate scopes on every request

## Pros

- ✅ Standardized
- ✅ Works well for APIs
- ✅ Fine-grained permissions
- ✅ User consent

## Cons

- ❌ Coarse-grained (not resource-specific)
- ❌ Scope explosion possible
- ❌ User may not understand scopes

## When to Use

- ✅ External APIs
- ✅ OAuth-based systems
- ✅ Third-party integrations
- ✅ User-delegated access

## Related Topics

- **[OAuth 2.0](../01-authentication/06-oauth2.md)** - Token framework
- **[Fine-Grained Permissions](./04-fine-grained-permissions.md)** - More granular access

