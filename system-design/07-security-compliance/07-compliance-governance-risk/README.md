# Compliance, Governance & Risk (GRC)

Compliance frameworks, governance controls, and risk management: SOC 2, ISO 27001, PCI DSS, HIPAA, GDPR.

## Table of Contents

### Compliance Frameworks
- **[01. SOC 2](./01-soc2.md)** - Service Organization Control 2
- **[02. ISO 27001](./02-iso27001.md)** - Information Security Management
- **[03. PCI DSS](./03-pci-dss.md)** - Payment Card Industry Data Security Standard
- **[04. HIPAA](./04-hipaa.md)** - Health Insurance Portability and Accountability Act
- **[05. GDPR](./05-gdpr.md)** - General Data Protection Regulation

### Governance & Controls
- **[06. Access Reviews](./06-access-reviews.md)** - Regular access audits
- **[07. Change Management](./07-change-management.md)** - Controlled changes
- **[08. Vendor Risk](./08-vendor-risk.md)** - Third-party risk management
- **[09. Segregation of Duties](./09-segregation-of-duties.md)** - Separation of responsibilities

### Audits & Risk
- **[10. Audit Management](./10-audit-management.md)** - Evidence collection, control mapping
- **[11. Risk Management](./11-risk-management.md)** - Risk registers, risk assessment

## Common Compliance Frameworks

### SOC 2 (Service Organization Control 2)
**Focus:** Security, availability, processing integrity, confidentiality, privacy

**Trust Service Criteria:**
- **CC1:** Control Environment
- **CC2:** Communication and Information
- **CC3:** Risk Assessment
- **CC4:** Monitoring Activities
- **CC5:** Control Activities

**Types:**
- **Type I:** Design of controls at a point in time
- **Type II:** Operating effectiveness over time (6-12 months)

### ISO 27001
**Focus:** Information Security Management System (ISMS)

**Key Domains:**
- Information security policies
- Organization of information security
- Human resource security
- Asset management
- Access control
- Cryptography
- Physical and environmental security
- Operations security
- Communications security
- System acquisition, development, and maintenance
- Supplier relationships
- Information security incident management
- Business continuity management
- Compliance

### PCI DSS (Payment Card Industry Data Security Standard)
**Focus:** Payment card data protection

**Requirements:**
1. Build and maintain secure network
2. Protect cardholder data
3. Maintain vulnerability management program
4. Implement strong access control
5. Monitor and test networks
6. Maintain information security policy

**Levels:** Based on transaction volume

### HIPAA (Health Insurance Portability and Accountability Act)
**Focus:** Protected Health Information (PHI)

**Rules:**
- **Privacy Rule** - PHI use and disclosure
- **Security Rule** - Administrative, physical, technical safeguards
- **Breach Notification Rule** - Breach reporting

**Requirements:**
- Access controls
- Audit controls
- Integrity controls
- Transmission security

### GDPR (General Data Protection Regulation)
**Focus:** Personal data protection (EU)

**Key Principles:**
- Lawfulness, fairness, transparency
- Purpose limitation
- Data minimization
- Accuracy
- Storage limitation
- Integrity and confidentiality
- Accountability

**Rights:**
- Right to access
- Right to rectification
- Right to erasure (right to be forgotten)
- Right to data portability
- Right to object

## Governance Controls

### Access Reviews
- Regular review of user access
- Remove unnecessary access
- **Frequency:** Quarterly or annually
- **Documentation:** Review evidence

### Change Management
- Controlled changes
- Approval process
- Testing before production
- Rollback plans
- **Documentation:** Change logs

### Vendor Risk
- Assess third-party vendors
- Security questionnaires
- Contract requirements
- Regular reviews
- **Due Diligence:** Before engagement

### Segregation of Duties
- Separate conflicting duties
- **Example:** Developer ≠ Deployer
- **Example:** Requester ≠ Approver
- **Principle:** Prevent fraud and errors

## Audits

### Evidence Collection
- Document controls
- Collect evidence
- **Types:** Policies, logs, screenshots, interviews
- **Chain of Custody:** Maintain integrity

### Control Mapping
- Map controls to requirements
- Demonstrate compliance
- **Gap Analysis:** Identify missing controls

### Risk Registers
- Document risks
- Assess impact and likelihood
- Mitigation strategies
- **Regular Review:** Update risk register

## Best Practices

### Compliance
- ✅ Understand requirements
- ✅ Implement controls
- ✅ Document everything
- ✅ Regular assessments
- ✅ Continuous improvement

### Governance
- ✅ Clear policies and procedures
- ✅ Regular reviews
- ✅ Accountability
- ✅ Training and awareness

### Risk Management
- ✅ Identify risks
- ✅ Assess risks
- ✅ Mitigate risks
- ✅ Monitor risks
- ✅ Document risk decisions

## Related Topics

- **[Data Security](../03-data-security-privacy/)** - Data protection requirements
- **[Monitoring](../06-monitoring-logging-incident-response/)** - Audit logging
- **[IAM](../01-iam/)** - Access control compliance

