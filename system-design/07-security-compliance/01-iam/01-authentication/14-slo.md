# SLO (Single Logout)

**What it is:** When a user logs out from one application, they are logged out from all applications that were accessed using the same SSO session.

**One-line:** Logout once → sessions invalidated everywhere

## Why SLO Is Hard (Reality First)

**Important truth:** SSO is reliable. SLO is best-effort.

### Reasons SLO Fails

- ❌ **Browser restrictions** - 3rd-party cookies blocked
- ❌ **Network failures** - Apps unreachable
- ❌ **Apps not responding** - Logout callbacks fail
- ❌ **Stateless tokens** - JWTs remain valid until expiry
- ❌ **Multiple protocols** - SAML + OIDC mixed usage

### Practical Industry Truth

Many systems:
- ✅ Support SSO
- ❌ Do not fully support SLO
- ✅ Rely on short session TTLs instead

## SLO in SAML

SAML has explicit protocol support for logout.

### SAML Logout Types

1. **SP-Initiated Logout** - User clicks Logout in your app
2. **IdP-Initiated Logout** - User logs out from IdP portal

### SP-Initiated SAML Logout Flow

```
1. User clicks Logout in App A (SP)
   ↓
2. SP sends LogoutRequest to IdP
   ↓
3. IdP:
   - Terminates its session
   - Sends LogoutRequest to all other SPs
   ↓
4. SPs invalidate local sessions
   ↓
5. LogoutResponse returned
```

### SAML SLO Configuration

**SP Configuration:**
- SLO URL - Endpoint to receive logout
- Session index - Track IdP session
- Certificate - Sign logout requests
- Binding - Redirect or POST

**IdP Configuration:**
- SLO endpoint - Receive logout
- SP SLO URL - Where to send callbacks
- Certificate - Verify requests

⚠️ **Both sides must support SLO or it fails.**

## SLO in OIDC

OIDC logout is weaker and fragmented.

### OIDC Logout Types

1. **Front-Channel Logout** - Browser redirects, uses iframes
2. **Back-Channel Logout** - Server-to-server HTTP call (better)

### Front-Channel Logout Flow

```
1. App redirects user to IdP logout endpoint
   ↓
2. IdP clears its session
   ↓
3. IdP loads logout URLs of all clients (hidden iframes)
   ↓
4. Each app clears local session
```

**Problem:** Browser blocks 3rd-party cookies, iframes may fail silently

### Back-Channel Logout Flow (Better)

```
1. IdP sends logout token (JWT) to app
   ↓
2. App invalidates sessions tied to user
   ↓
3. No browser dependency
```

**Sample Back-Channel Logout Token:**
```json
{
  "iss": "https://idp.example.com",
  "aud": "client_abc123",
  "iat": 1766238000,
  "jti": "logout-xyz",
  "events": {
    "http://schemas.openid.net/event/backchannel-logout": {}
  },
  "sub": "109876543210"
}
```

### OIDC Logout Configuration

**SP (Client) Configuration:**
- `post_logout_redirect_uri` - Redirect after logout
- Back-channel URL - Receive logout token
- Session mapping - Map user → sessions

**IdP Configuration:**
- Logout endpoint - Initiate logout
- Client logout URLs - Front/back-channel
- Token signing keys - JWT validation

## What Actually Gets Logged Out?

| Layer | Logout Effect |
|-------|---------------|
| **App session** | ✅ Cleared |
| **IdP session** | ✅ Cleared |
| **Access tokens** | ❌ Still valid |
| **Refresh tokens** | ❌ Unless revoked |

**JWTs remain valid until expiry unless explicitly revoked.**

## Why SLO Commonly Fails in Production

| Issue | Reason |
|-------|--------|
| **Partial logout** | App unreachable |
| **Silent failures** | Browser blocks iframe |
| **Zombie sessions** | JWT statelessness |
| **Multi-device users** | Logout from one device only |

## Best Practices (What Real SaaS Teams Do)

- ✅ Implement SP-initiated logout
- ✅ Support back-channel logout if using OIDC
- ✅ Use short session TTLs
- ✅ Use short access token expiry
- ✅ Revoke refresh tokens on logout
- ✅ Treat SLO as best-effort
- ✅ Log logout failures for debugging

## Common Interview Questions

**Q: Is SLO guaranteed?**
→ No. It is best-effort.

**Q: Why is SLO easier in SAML than OIDC?**
→ SAML is session-based and browser-centric.

**Q: Can logout invalidate JWTs?**
→ Only if you track them (token blacklist).

**Q: What's the most reliable logout approach?**
→ Short-lived tokens + back-channel logout.

**Q: Does logging out of one device log out all devices?**
→ Not unless IdP tracks global sessions.

**Q: What breaks SLO in practice?**
→ Browser blocking 3rd-party cookies, network failures, app crashes during logout, mixed protocol usage

## One-Line Summary

**SSO centralizes authentication; SLO attempts to centralize session termination—but is inherently unreliable due to stateless tokens and browser constraints.**

## Related Topics

- **[SSO](./10-sso.md)** - Single Sign-On
- **[SAML](./13-saml.md)** - SAML logout implementation
- **[OIDC](./09-openid-connect.md)** - OIDC logout implementation

