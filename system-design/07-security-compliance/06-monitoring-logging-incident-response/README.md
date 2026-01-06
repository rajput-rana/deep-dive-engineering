# Monitoring, Logging & Incident Response

Detection, logging, and incident response: SIEM, IDS/IPS, audit logs, and breach handling.

## Overview

**📌 Compliance loves evidence, not promises.**

Security monitoring and incident response are critical for detecting threats, investigating incidents, and maintaining compliance.

## Table of Contents

### Detection
- **[01. Security Detection](./01-security-detection.md)** - SIEM, IDS/IPS, Anomaly Detection

### Logging
- **[02. Security Logging](./02-security-logging.md)** - Audit Logs, Immutable Logs, Access Trails

### Incident Response
- **[03. Incident Response](./03-incident-response.md)** - Playbooks, Breach Handling, Root Cause Analysis

## Detection

### SIEM (Security Information and Event Management)
- Centralized log collection
- Correlation and analysis
- Threat detection
- **Tools:** Splunk, ELK Stack, Datadog Security

### IDS / IPS
- **IDS (Intrusion Detection System)** - Detect threats
- **IPS (Intrusion Prevention System)** - Detect and block threats
- Network-based and host-based
- Signature-based and anomaly-based

### Anomaly Detection
- Behavioral analysis
- Machine learning models
- Unusual pattern detection
- **Use Cases:** Fraud detection, insider threats

## Logging

### Audit Logs
- Record all security events
- User actions
- System changes
- Access attempts

**What to Log:**
- Authentication events
- Authorization decisions
- Data access
- Configuration changes
- Administrative actions

### Immutable Logs
- Write-once, read-many (WORM)
- Cannot be modified or deleted
- **Compliance:** Required for many regulations
- **Implementation:** Append-only storage

### Access Trails
- Who accessed what
- When access occurred
- From where (IP address)
- What action was taken

**Use Cases:**
- Forensic analysis
- Compliance audits
- Security investigations

## Incident Response

### Playbooks
- Documented response procedures
- Step-by-step guides
- Role assignments
- **Types:** Data breach, malware, DDoS, insider threat

### Breach Handling
1. **Containment** - Stop the breach
2. **Investigation** - Determine scope
3. **Eradication** - Remove threat
4. **Recovery** - Restore services
5. **Post-Incident** - Lessons learned

### Root Cause Analysis
- Identify root cause
- Not just symptoms
- **5 Whys Technique** - Ask why 5 times
- **Fishbone Diagram** - Categorize causes

### Postmortems
- Document incident
- Timeline of events
- What went wrong
- What went right
- Improvements needed

## Incident Response Phases

### 1. Preparation
- Incident response plan
- Team training
- Tools and access
- Communication plan

### 2. Detection & Analysis
- Identify incident
- Classify severity
- Initial assessment
- Escalation

### 3. Containment
- Short-term containment
- Long-term containment
- Evidence preservation
- Communication

### 4. Eradication
- Remove threat
- Patch vulnerabilities
- Clean infected systems
- Verify removal

### 5. Recovery
- Restore services
- Monitor for re-infection
- Validate security
- Return to normal operations

### 6. Post-Incident
- Documentation
- Lessons learned
- Process improvements
- Training updates

## Compliance Requirements

### Log Retention
- **SOC 2:** 90 days minimum
- **HIPAA:** 6 years
- **PCI DSS:** 1 year minimum
- **GDPR:** As required by law

### Evidence Collection
- Chain of custody
- Timestamp accuracy
- Immutable logs
- Forensic readiness

## Best Practices

### Monitoring
- ✅ Monitor all critical systems
- ✅ Real-time alerting
- ✅ Baseline normal behavior
- ✅ Review alerts regularly
- ✅ Tune detection rules

### Logging
- ✅ Log all security events
- ✅ Use structured logging
- ✅ Centralize logs
- ✅ Protect log integrity
- ✅ Regular log reviews

### Incident Response
- ✅ Have a plan
- ✅ Practice regularly (tabletop exercises)
- ✅ Document everything
- ✅ Learn from incidents
- ✅ Update playbooks

## Related Topics

- **[Application Security](../04-application-security/)** - Application security monitoring
- **[Compliance](../07-compliance-governance-risk/)** - Compliance requirements
- **[Infrastructure Security](../05-infrastructure-network-security/)** - Infrastructure monitoring

