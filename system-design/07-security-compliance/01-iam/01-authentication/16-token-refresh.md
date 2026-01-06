# Token Refresh

**What it is:** Mechanism to obtain new access tokens without re-authenticating.

**Purpose:** Maintain long-lived sessions while keeping access tokens short-lived.

## Why Token Refresh?

### Problem with Long-Lived Tokens

- ❌ If stolen, valid for long time
- ❌ Hard to revoke
- ❌ Security risk

### Solution: Short Access + Long Refresh

- ✅ Short-lived access tokens (15 minutes)
- ✅ Long-lived refresh tokens (7-30 days)
- ✅ Refresh token gets new access token

## Token Refresh Flow

```
1. User authenticates
   ↓
2. Server issues:
   - Access Token (short-lived)
   - Refresh Token (long-lived)
   ↓
3. Client uses Access Token for API calls
   ↓
4. Access Token expires
   ↓
5. Client uses Refresh Token to get new Access Token
   ↓
6. Process repeats
```

## Refresh Token Characteristics

### Security Properties

- ✅ **Long-lived** - Days to weeks
- ✅ **Single-use** - Ideally rotated on each use
- ✅ **Stored securely** - Not in localStorage
- ✅ **Revocable** - Can be invalidated

### Storage

**Server-Side (Recommended):**
- Stored in database
- Associated with user
- Can be revoked

**Client-Side:**
- Secure storage (httpOnly cookie)
- Not in localStorage (XSS risk)

## Refresh Token Rotation

**What it is:** Issue new refresh token on each refresh

**Flow:**
```
1. Client sends refresh token
   ↓
2. Server validates refresh token
   ↓
3. Server issues:
   - New access token
   - New refresh token
   ↓
4. Old refresh token invalidated
```

**Benefits:**
- ✅ Limits exposure window
- ✅ Detects token theft
- ✅ Better security

## Refresh Token Revocation

### When to Revoke

- User logs out
- Password change
- Suspicious activity
- Token compromise

### Implementation

- Store refresh tokens in database
- Mark as revoked
- Check revocation on refresh

## Best Practices

- ✅ Use short-lived access tokens (15-30 min)
- ✅ Use longer refresh tokens (7-30 days)
- ✅ Implement token rotation
- ✅ Store refresh tokens securely
- ✅ Revoke on logout
- ✅ Monitor refresh patterns
- ❌ Don't store refresh tokens in localStorage
- ❌ Don't use same token for access and refresh

## Common Interview Questions

**Q: Why not just use long-lived access tokens?**
- If stolen, valid for long time
- Hard to revoke
- Security risk

**Q: How do you handle refresh token theft?**
- Token rotation
- Detect multiple refresh attempts
- Revoke compromised tokens

**Q: Where should refresh tokens be stored?**
- Server-side (database) - preferred
- Client-side (httpOnly cookie) - acceptable
- Never localStorage

## Related Topics

- **[JWT](./05-jwt.md)** - Token format
- **[OAuth 2.0](./06-oauth2.md)** - Token framework
- **[Session Management](./15-session-management.md)** - Session handling

