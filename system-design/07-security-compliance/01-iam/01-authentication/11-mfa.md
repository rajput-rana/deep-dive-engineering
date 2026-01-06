# MFA (Multi-Factor Authentication)

**What it is:** Authentication using multiple factors.

**Factors:**
1. **Something you know** - Password
2. **Something you have** - Phone, hardware key
3. **Something you are** - Biometrics

## MFA Types

### TOTP (Time-Based One-Time Password)
- **Apps:** Google Authenticator, Authy
- **How:** 6-digit code, changes every 30 seconds
- **Pros:** Works offline, no SMS needed
- **Cons:** Phone required

### SMS-Based MFA
- **How:** Code sent via SMS
- **Pros:** Easy to use
- **Cons:** Vulnerable to SIM swapping

### Hardware Keys (FIDO2/WebAuthn)
- **Examples:** YubiKey, Titan Security Key
- **Pros:** Most secure, phishing-resistant
- **Cons:** Requires hardware

### Push Notifications
- **How:** Approval via mobile app
- **Pros:** User-friendly
- **Cons:** Requires app installation

## Why MFA Matters

- ✅ **Prevents password-only attacks** - Even if password stolen
- ✅ **Reduces account takeover** - Requires physical device
- ✅ **Compliance requirement** - Many regulations require MFA
- ✅ **Better security** - Multiple factors harder to compromise

## Best Practices

- ✅ Require MFA for admin accounts
- ✅ Require MFA for sensitive operations
- ✅ Prefer TOTP or hardware keys over SMS
- ✅ Implement backup codes
- ✅ Allow multiple MFA methods

## When to Use

- ✅ High-security accounts
- ✅ Admin access
- ✅ Financial operations
- ✅ Sensitive data access
- ✅ Compliance requirements

## Related Topics

- **[Passwords](./02-username-password.md)** - First factor
- **[Passwordless](./12-passwordless.md)** - Advanced authentication

