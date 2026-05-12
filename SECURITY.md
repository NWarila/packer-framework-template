# Security Policy

## Reporting a vulnerability

**Do not file public issues for security vulnerabilities.**

### Preferred: GitHub private vulnerability reporting

Use [GitHub's private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) to report vulnerabilities directly through the affected repository's Security tab.

### Fallback contact

If private vulnerability reporting is not available on the affected repository, contact the maintainer through their [GitHub profile](https://github.com/NWarila).

## What to include

- Description of the vulnerability
- Steps to reproduce or proof of concept
- Affected repository and version (or "latest default branch" if unsure)
- Potential impact

## Response timeline

| Stage | Target |
|-------|--------|
| Initial acknowledgement | 7 business days |
| Validation | 14 days |
| Remediation or mitigation | 90 days when reasonable |

These are targets, not guarantees. Complex issues may take longer. You will be kept informed of progress.

## Supported versions

Unless a repository documents otherwise, only the latest version on the default branch is supported.

## Scope

### In scope

- Vulnerabilities in code, dependencies, or configurations maintained in repositories under [NWarila](https://github.com/NWarila)
- Misconfigurations in GitHub Actions workflows that could lead to secret exposure or privilege escalation

### Out of scope

- Vulnerabilities in third-party dependencies that should be reported upstream
- Social engineering attacks
- Denial of service attacks
- Issues in archived repositories

## Coordinated disclosure

We follow coordinated disclosure practices. We ask that you:

- Give us reasonable time to investigate and address the issue before public disclosure
- Act in good faith and avoid accessing or modifying data that does not belong to you
- Do not exploit the vulnerability beyond what is necessary to demonstrate it

We will credit researchers who report valid vulnerabilities unless they prefer to remain anonymous.
