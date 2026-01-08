# 🔐 IAM - Identity and Access Management

<div align="center">

**Control access to AWS resources: users, roles, and policies**

[![IAM](https://img.shields.io/badge/IAM-Security-blue?style=for-the-badge)](./)
[![Access](https://img.shields.io/badge/Access-Control-green?style=for-the-badge)](./)
[![Security](https://img.shields.io/badge/Security-Permissions-orange?style=for-the-badge)](./)

*Master IAM: secure access control, least privilege, and identity management*

</div>

---

## 🎯 What is IAM?

<div align="center">

**IAM (Identity and Access Management) controls who can access AWS resources and what they can do.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **👤 User** | Person or application identity |
| **🎭 Role** | Temporary credentials |
| **📋 Policy** | Permission document |
| **👥 Group** | Collection of users |
| **🔑 Access Key** | Programmatic access |
| **🔒 MFA** | Multi-factor authentication |

**Mental Model:** Think of IAM like a security guard with a rulebook - they check who you are (authentication) and what you're allowed to do (authorization) before letting you access AWS resources.

</div>

---

## 👤 Users

<div align="center">

### What are IAM Users?

**Identity for people or applications**

| Type | Description | Use Case |
|:---:|:---:|:---:|
| **Root User** | Account owner | Initial setup only |
| **IAM User** | Individual user | Team members |
| **Service User** | Application user | Programmatic access |

---

### User Best Practices

| Practice | Why |
|:---:|:---:|
| **Don't use root** | Security risk |
| **Enable MFA** | Additional security |
| **Use groups** | Manage permissions |
| **Rotate access keys** | Security |
| **Least privilege** | Minimum permissions needed |

</div>

---

## 🎭 Roles

<div align="center">

### What are IAM Roles?

**Temporary credentials assumed by users or services**

| Characteristic | Description |
|:---:|:---:|
| **Temporary** | Credentials expire |
| **Assumable** | Can be assumed by users/services |
| **No Access Keys** | No long-term credentials |
| **Cross-Account** | Assume roles in other accounts |

---

### Common Role Types

| Role Type | Description | Use Case |
|:---:|:---:|:---:|
| **Service Role** | Assumed by AWS service | EC2, Lambda |
| **User Role** | Assumed by users | Cross-account access |
| **Cross-Account Role** | Access other accounts | Multi-account |

**💡 Use roles instead of access keys when possible.**

</div>

---

## 📋 Policies

<div align="center">

### What are Policies?

**JSON documents that define permissions**

### Policy Structure

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

---

### Policy Types

| Type | Description | Attached To |
|:---:|:---:|:---:|
| **Identity-Based** | User/role/group policies | Users, roles, groups |
| **Resource-Based** | Resource policies | S3 buckets, etc. |
| **Inline** | Embedded in resource | Specific resource |
| **Managed** | AWS or custom managed | Reusable |

---

### Policy Elements

| Element | Description | Example |
|:---:|:---:|:---:|
| **Effect** | Allow or Deny | Allow |
| **Action** | What action | s3:GetObject |
| **Resource** | Which resource | arn:aws:s3:::bucket/* |
| **Condition** | When policy applies | IP address, time |

</div>

---

## 🔐 Security Best Practices

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Least Privilege** | Minimum permissions |
| **Use Roles** | Temporary credentials |
| **Enable MFA** | Additional security |
| **Rotate Credentials** | Security |
| **Use Groups** | Manage permissions |
| **Regular Audits** | Review permissions |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Use root account** | Security risk | Use IAM users |
| **Wildcard permissions** | Too permissive | Specific permissions |
| **Hardcode credentials** | Security risk | Use roles, secrets manager |
| **No MFA** | Weak security | Enable MFA |

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **IAM Purpose** | Access control for AWS |
| **Users** | Long-term identities |
| **Roles** | Temporary credentials |
| **Policies** | Define permissions |
| **Best Practice** | Least privilege, use roles |

**💡 Remember:** IAM is the foundation of AWS security. Use roles, enable MFA, and follow least privilege principle.

</div>

---

<div align="center">

**Master IAM for secure AWS access! 🚀**

*Control access to AWS resources with IAM - users, roles, policies, and security best practices.*

</div>

