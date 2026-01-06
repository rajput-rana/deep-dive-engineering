# Secure SDLC (Shift Left)

DevSecOps, threat modeling, secure CI/CD, secrets scanning, SAST/DAST, and change management for secure software development.

## Shift Left Security

**Shift Left:** Move security earlier in the development lifecycle.

**Traditional:** Security at the end (testing, production)
**Shift Left:** Security from the start (requirements, design, development)

## Table of Contents

### DevSecOps
- **[01. DevSecOps](./01-devsecops.md)** - Integrating security into DevOps

### Threat Modeling
- **[02. Threat Modeling](./02-threat-modeling.md)** - Identify and mitigate threats early

### Secure CI/CD
- **[03. Secure CI/CD](./03-secure-cicd.md)** - Security in continuous integration/deployment

### Security Scanning
- **[04. Secrets Scanning](./04-secrets-scanning.md)** - Detect secrets in code
- **[05. SAST / DAST](./05-sast-dast.md)** - Static and Dynamic Application Security Testing

### Change Management
- **[06. Code Reviews](./06-code-reviews.md)** - Security-focused code reviews
- **[07. Approvals](./07-approvals.md)** - Change approval process
- **[08. Rollback Plans](./08-rollback-plans.md)** - Safe deployment rollback

## DevSecOps

### Integration Points
- **Requirements** - Security requirements
- **Design** - Threat modeling, secure design
- **Development** - Secure coding, SAST
- **Build** - Dependency scanning, secrets scanning
- **Test** - DAST, security testing
- **Deploy** - Secure configuration, scanning
- **Monitor** - Security monitoring, vulnerability management

### Tools & Practices
- **SAST** - Static analysis in CI/CD
- **DAST** - Dynamic testing in pipeline
- **Dependency Scanning** - Check for vulnerabilities
- **Secrets Scanning** - Detect exposed secrets
- **Container Scanning** - Scan container images
- **Infrastructure as Code Scanning** - Scan IaC for misconfigurations

## Threat Modeling

### Process
1. **Identify Assets** - What to protect
2. **Identify Threats** - What could go wrong
3. **Assess Risks** - Impact and likelihood
4. **Mitigate** - Implement controls
5. **Validate** - Test mitigations

### Methodologies
- **STRIDE** - Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege
- **DREAD** - Damage, Reproducibility, Exploitability, Affected Users, Discoverability
- **Attack Trees** - Visualize attack paths

## Secure CI/CD

### Pipeline Security
- **Secure Build Environment** - Isolated, clean builds
- **Secrets Management** - Secure secret injection
- **Artifact Signing** - Sign artifacts
- **Immutable Deployments** - Versioned, reproducible

### Security Gates
- **SAST Gate** - Block on critical findings
- **Dependency Gate** - Block on high-severity vulnerabilities
- **Secrets Gate** - Block on exposed secrets
- **Compliance Gate** - Verify compliance checks

## Security Scanning

### Secrets Scanning
- **Pre-commit Hooks** - Scan before commit
- **CI/CD Integration** - Scan in pipeline
- **Repository Scanning** - Scan entire repo history
- **Tools:** GitGuardian, TruffleHog, detect-secrets

### SAST (Static Application Security Testing)
- **Code Analysis** - Analyze source code
- **Find Vulnerabilities** - Before runtime
- **Fast Feedback** - Quick results
- **Tools:** SonarQube, Checkmarx, Veracode

### DAST (Dynamic Application Security Testing)
- **Runtime Testing** - Test running application
- **Find Runtime Issues** - Configuration, runtime vulnerabilities
- **Tools:** OWASP ZAP, Burp Suite

## Change Management

### Code Reviews
- **Security Focus** - Review for security issues
- **Checklist** - Security review checklist
- **Automated Checks** - Automated security checks
- **Peer Review** - Multiple reviewers

### Approvals
- **Security Approval** - Security team approval for sensitive changes
- **Compliance Approval** - Compliance review for regulatory changes
- **Documentation** - Document approval decisions

### Rollback Plans
- **Automated Rollback** - Quick rollback capability
- **Blue-Green Deployment** - Zero-downtime rollback
- **Canary Deployments** - Gradual rollout with rollback
- **Documentation** - Rollback procedures

## Best Practices

### Shift Left
- ✅ Security from requirements phase
- ✅ Threat modeling in design
- ✅ Secure coding practices
- ✅ Security testing in CI/CD
- ✅ Security reviews before merge

### Automation
- ✅ Automate security scanning
- ✅ Automate vulnerability detection
- ✅ Automate compliance checks
- ✅ Automate security testing

### Culture
- ✅ Security training for developers
- ✅ Security champions program
- ✅ Security awareness
- ✅ Reward secure practices

## Related Topics

- **[Application Security](../04-application-security/)** - Secure coding practices
- **[Secrets Management](../02-secrets-management/)** - Secure secret handling
- **[Compliance](../07-compliance-governance-risk/)** - Compliance in SDLC

