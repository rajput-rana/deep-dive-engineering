# JSON Web Tokens (JWT)

**Reference:** [AlgoMaster - JWT](https://algomaster.io/learn/system-design/jwt)

## Summary

JWT is a compact, URL-safe token format for securely transmitting information between parties. It's commonly used for authentication and authorization in stateless systems, eliminating the need for server-side session storage.

## Key Concepts

### JWT Structure

A JWT has three parts separated by dots:

```
header.payload.signature
```

1. **Header:** Algorithm and token type
   ```json
   {
     "alg": "HS256",
     "typ": "JWT"
   }
   ```

2. **Payload:** Claims (data)
   ```json
   {
     "sub": "user123",
     "name": "John Doe",
     "exp": 1609459200
   }
   ```

3. **Signature:** Verifies token integrity
   ```
   HMACSHA256(
     base64UrlEncode(header) + "." + base64UrlEncode(payload),
     secret
   )
   ```

### JWT Flow

```
1. User logs in → Server validates credentials
2. Server creates JWT → Signs with secret
3. Server returns JWT → Client stores (localStorage/cookie)
4. Client sends JWT → In Authorization header
5. Server validates signature → Grants access
```

## Why It Matters

**Stateless:** No server-side session storage needed. Perfect for microservices and distributed systems.

**Scalability:** Any server can validate tokens without shared state.

**Portable:** Token contains user info, reducing database lookups.

**Standard:** Widely supported across languages and frameworks.

## Real-World Examples

**Auth0:** Uses JWT for authentication tokens.

**Google OAuth:** Returns JWT tokens for API access.

**AWS Cognito:** Issues JWTs for authenticated users.

**Spring Security:** JWT support for stateless authentication.

## Tradeoffs

### Advantages
- ✅ Stateless (no server storage)
- ✅ Scalable (no shared session store)
- ✅ Portable (works across services)
- ✅ Self-contained (user info in token)

### Disadvantages
- ❌ Can't revoke easily (until expiration)
- ❌ Size limit (can't store too much data)
- ❌ Security risk if secret leaked
- ❌ No built-in refresh mechanism

## Security Considerations

### Best Practices

1. **Use HTTPS:** Always transmit JWTs over HTTPS
2. **Short Expiration:** Set reasonable expiration times
3. **Secure Storage:** Don't store in localStorage (XSS risk)
4. **Secret Management:** Use strong, rotated secrets
5. **Validate Signature:** Always verify signature

### Common Vulnerabilities

1. **Algorithm Confusion:** Attacker uses "none" algorithm
   - Solution: Explicitly verify algorithm

2. **Weak Secrets:** Predictable signing keys
   - Solution: Use strong, random secrets

3. **XSS Attacks:** Stealing tokens from localStorage
   - Solution: Use httpOnly cookies

4. **Token Replay:** Using expired tokens
   - Solution: Check expiration, use refresh tokens

## Design Considerations

### When to Use JWT

**Good for:**
- Stateless APIs
- Microservices
- Mobile apps
- Single-page applications
- Cross-domain authentication

**Not ideal for:**
- Systems requiring immediate revocation
- Large payloads
- Highly sensitive data in token

### Token Storage

**Options:**
1. **localStorage:** Easy, but XSS vulnerable
2. **httpOnly Cookies:** More secure, CSRF risk
3. **Memory:** Most secure, lost on refresh

**Recommendation:** httpOnly cookies for web, memory for mobile.

### Refresh Tokens

Use refresh tokens for long-lived sessions:
- Short-lived access token (15 min)
- Long-lived refresh token (7 days)
- Refresh endpoint to get new access token

## Interview Hints

When discussing JWT:
1. Explain structure (header, payload, signature)
2. Describe stateless authentication flow
3. Discuss security considerations
4. Address revocation challenges
5. Compare with session-based auth

## Reference

[AlgoMaster - JWT](https://algomaster.io/learn/system-design/jwt)

