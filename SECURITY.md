# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## Reporting a Vulnerability

We take the security of **CareerRadar** seriously. If you discover a security vulnerability, please report it responsibly instead of opening a public issue.

### Reporting Process
1. **Email**: Send details of the vulnerability to `security@careerradar.io`.
2. **Details to Include**:
   - Description of the vulnerability and its potential impact.
   - Steps to reproduce or proof-of-concept code.
   - Environment details (OS, Python/Node versions, browser).
3. **Response Window**: You will receive an acknowledgment within **48 hours** and regular updates on mitigation progress.

---

## Security Best Practices in CareerRadar

- **Rate Limiting**: Sliding window rate limiting across authentication, analysis triggers, and automated scan endpoints.
- **OWASP Security Headers**: `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Strict-Transport-Security`, and strict `Referrer-Policy`.
- **Candidate Data Isolation**: Multi-tenant data isolation guaranteeing candidate analyses, profiles, and alert settings are strictly bounded to authenticated JWT subjects.
- **Deterministic Math Engine**: LLMs only generate qualitative explanatory advice and never modify readiness percentages, match scores, or database rankings.
