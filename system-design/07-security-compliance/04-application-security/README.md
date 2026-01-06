# Application Security (AppSec)

Secure coding practices, OWASP Top 10, and dependency security to protect applications from vulnerabilities.

## OWASP Top 10 (2021)

### A01 – Broken Access Control
**Problem:** Users can do what they shouldn't.

**Examples:**
- Unauthorized access to admin functions
- Privilege escalation
- Insecure direct object references

**Prevention:**
- Implement proper authorization checks
- Use RBAC/ABAC
- Validate user permissions

### A02 – Cryptographic Failures
**Problem:** Data not properly encrypted.

**Examples:**
- Weak encryption algorithms
- Exposed encryption keys
- Unencrypted sensitive data

**Prevention:**
- Use strong encryption (AES-256)
- Secure key management
- Encrypt sensitive data at rest and in transit

### A03 – Injection
**Problem:** Input executed as code (SQL, NoSQL, OS).

**Types:**
- SQL Injection
- NoSQL Injection
- Command Injection
- LDAP Injection

**Prevention:**
- Parameterized queries
- Input validation
- Output encoding
- Use ORMs

### A04 – Insecure Design
**Problem:** Security flaws in architecture.

**Examples:**
- Missing security controls
- Weak threat modeling
- Insecure defaults

**Prevention:**
- Threat modeling
- Security by design
- Secure architecture patterns

### A05 – Security Misconfiguration
**Problem:** Unsafe defaults, open configs.

**Examples:**
- Default credentials
- Exposed error messages
- Unnecessary features enabled

**Prevention:**
- Secure defaults
- Regular security reviews
- Minimal attack surface

### A06 – Vulnerable & Outdated Components
**Problem:** Using insecure libraries.

**Examples:**
- Outdated dependencies
- Known vulnerabilities
- Unmaintained libraries

**Prevention:**
- Dependency scanning
- Regular updates
- SBOM (Software Bill of Materials)

### A07 – Identification & Authentication Failures
**Problem:** Weak login/session management.

**Examples:**
- Weak passwords
- Session fixation
- Credential stuffing

**Prevention:**
- Strong password policies
- MFA
- Secure session management

### A08 – Software & Data Integrity Failures
**Problem:** Tampered code/data.

**Examples:**
- Supply chain attacks
- Unsigned updates
- CI/CD compromise

**Prevention:**
- Code signing
- Integrity checks
- Secure CI/CD pipelines

### A09 – Logging & Monitoring Failures
**Problem:** Attacks not detected.

**Examples:**
- Insufficient logging
- No monitoring
- Delayed detection

**Prevention:**
- Comprehensive logging
- Security monitoring
- Alerting systems

### A10 – Server-Side Request Forgery (SSRF)
**Problem:** Server abused to call internal services.

**Examples:**
- Internal network access
- Cloud metadata access
- Local file access

**Prevention:**
- Input validation
- Network segmentation
- Whitelist allowed URLs

## Secure Coding Practices

### Input Validation
- Validate all input
- Whitelist validation (preferred)
- Sanitize user input
- Reject invalid input

### Output Encoding
- Encode output to prevent XSS
- Context-aware encoding
- Use framework encoding functions

### Error Handling
- Don't expose sensitive information
- Generic error messages for users
- Detailed errors in logs only
- Don't leak stack traces

### Authentication & Session Management
- Strong password policies
- Secure password storage
- Session timeout
- Secure session cookies

## Dependency Security

### Vulnerability Scanning
- Regular dependency scans
- Automated scanning in CI/CD
- Track known vulnerabilities (CVE)

### SBOM (Software Bill of Materials)
- List all dependencies
- Track versions
- License compliance
- Vulnerability tracking

### Dependency Management
- Keep dependencies updated
- Remove unused dependencies
- Use dependency pinning
- Review dependency changes

## Security Testing

### SAST (Static Application Security Testing)
- Code analysis
- Find vulnerabilities in source code
- **Tools:** SonarQube, Checkmarx, Veracode

### DAST (Dynamic Application Security Testing)
- Runtime testing
- Find vulnerabilities in running application
- **Tools:** OWASP ZAP, Burp Suite

### IAST (Interactive Application Security Testing)
- Runtime analysis
- Combines SAST and DAST
- Real-time vulnerability detection

## Secure Development Lifecycle

1. **Requirements** - Security requirements
2. **Design** - Threat modeling, secure design
3. **Development** - Secure coding, code reviews
4. **Testing** - Security testing, penetration testing
5. **Deployment** - Secure configuration
6. **Maintenance** - Vulnerability management, updates

## Best Practices

- ✅ Follow OWASP Top 10 guidelines
- ✅ Implement secure coding practices
- ✅ Regular security testing
- ✅ Keep dependencies updated
- ✅ Code reviews with security focus
- ✅ Threat modeling
- ✅ Security training for developers

## Related Topics

- **[IAM](../01-iam/)** - Authentication and authorization
- **[Secure SDLC](../08-secure-sdlc/)** - Secure development lifecycle
- **[Monitoring](../06-monitoring-logging-incident-response/)** - Security monitoring

