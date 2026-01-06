# Infrastructure & Network Security

Protecting infrastructure and network layers: VPCs, firewalls, security groups, zero trust, host security, and container/K8s security.

## Table of Contents

### Network Security
- **[01. Network Security](./01-network-security.md)** - VPCs, Firewalls, Security Groups, Zero Trust

### Host Security
- **[02. Host Security](./02-host-security.md)** - OS Hardening, Patch Management, Malware Protection

### Container & Kubernetes Security
- **[03. Container Security](./03-container-security.md)** - Image Scanning, Pod Security Policies, Secrets Injection

## Network Security

### VPCs (Virtual Private Clouds)
- Isolated network environments
- Subnet segmentation
- Network ACLs
- **Best Practice:** Private subnets for databases

### Firewalls
- **Network Firewalls** - Perimeter defense
- **Application Firewalls** - WAF (Web Application Firewall)
- **Stateful Inspection** - Track connection state
- **Rules:** Allow/deny based on rules

### Security Groups
- Virtual firewalls for instances
- Inbound and outbound rules
- Stateful filtering
- **Principle:** Deny by default, allow explicitly

### Zero Trust
- **Never trust, always verify**
- Verify every request
- No implicit trust
- Continuous verification

**Zero Trust Principles:**
- Verify explicitly
- Use least privilege access
- Assume breach

## Host Security

### OS Hardening
- Remove unnecessary services
- Disable default accounts
- Configure security settings
- **CIS Benchmarks** - Security configuration guidelines

### Patch Management
- Regular security updates
- Automated patching
- Test patches before production
- **Critical:** Patch known vulnerabilities quickly

### Malware Protection
- Antivirus/antimalware
- Endpoint detection and response (EDR)
- Behavioral analysis
- Real-time scanning

## Container & Kubernetes Security

### Image Scanning
- Scan container images for vulnerabilities
- Check for known CVEs
- **Tools:** Trivy, Clair, Snyk
- **Best Practice:** Scan in CI/CD pipeline

### Pod Security Policies
- Restrict pod capabilities
- Prevent privilege escalation
- Limit host access
- **Kubernetes:** Pod Security Standards

### Secrets Injection
- Inject secrets at runtime
- Never bake secrets into images
- Use Kubernetes Secrets or external vaults
- **Best Practice:** Use init containers for secret retrieval

## Security Best Practices

### Network Segmentation
- Separate networks by trust level
- DMZ for public-facing services
- Private networks for internal services
- **Principle:** Least privilege networking

### Defense in Depth
- Multiple security layers
- Network + Host + Application security
- Fail-secure defaults
- **No single point of failure**

### Monitoring
- Network traffic monitoring
- Intrusion detection (IDS)
- Intrusion prevention (IPS)
- Anomaly detection

## Related Topics

- **[Application Security](../04-application-security/)** - Secure application layer
- **[Monitoring](../06-monitoring-logging-incident-response/)** - Security monitoring
- **[Compliance](../07-compliance-governance-risk/)** - Infrastructure compliance

