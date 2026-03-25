# Task 2 — Web Application Security Testing Report

**Tester:** Perikala Anusha  
**Organisation:** Redynox (Internship)  
**Date:** February 2026  
**Target:** WebGoat 8.2.2 (localhost:8080)  
**Tool:** OWASP ZAP 2.15  

---

## 1. Scope & Objectives

- Deploy and configure WebGoat 8.2.2 as a vulnerable test target
- Configure OWASP ZAP as intercepting proxy
- Run automated spider scan
- Manually exploit identified vulnerabilities
- Document findings with CVSS scores and code-level fixes

---

## 2. Environment Configuration

```
WebGoat URL:      http://localhost:8080/WebGoat
ZAP Proxy:        127.0.0.1:8090
Browser:          Firefox with FoxyProxy plugin
Spider Scan:      Traditional Spider + Ajax Spider
URLs Discovered:  59
Total Alerts:     19
```

---

## 3. Vulnerability Findings

### 3.1 SQL Injection — CWE-89 — CVSS 9.8 (Critical)

**Description:**  
The application constructs SQL queries using unsanitised user input, allowing an attacker to manipulate the query logic.

**Payload:** `admin'--`

**Impact:** Complete authentication bypass — admin access without valid credentials.

**Evidence:**
```
Input:    username=admin'-- | password=anything
Result:   Authentication successful — logged in as admin
SQL:      SELECT * FROM users WHERE username='admin'--' AND password='anything'
          (password check commented out by --)
```

**Remediation:**
```java
PreparedStatement stmt = connection.prepareStatement(
    "SELECT * FROM users WHERE username=? AND password=?"
);
stmt.setString(1, username);
stmt.setString(2, hashedPassword);
```

---

### 3.2 Cross-Site Scripting (Reflected XSS) — CWE-79 — CVSS 8.8 (High)

**Description:**  
User-controlled input is reflected in the response without sanitisation, enabling script injection.

**Payloads:**
```html
<script>alert('XSS')</script>
<img src=x onerror="alert(document.cookie)">
```

**Impact:** Session cookie theft, session hijacking, phishing page injection.

**Remediation:**
```java
// Output encoding
Encode.forHtml(userInput);

// HTTP headers
Content-Security-Policy: default-src 'self'
Set-Cookie: session=X; HttpOnly; Secure
```

---

### 3.3 CSRF — CWE-352 — CVSS 7.4 (High)

**Description:**  
The application does not validate that state-changing requests originate from legitimate user sessions.

**Attack:**
```html
<form action="http://localhost:8080/WebGoat/transfer" method="POST">
  <input type="hidden" name="amount" value="5000">
  <input type="hidden" name="to_account" value="attacker">
</form>
<script>document.forms[0].submit()</script>
```

**Impact:** $5,000 unauthorised fund transfer executed without victim awareness.

**Remediation:**
```java
// CSRF token per session
String token = UUID.randomUUID().toString();
session.setAttribute("csrf_token", token);

// Validate on every POST
if (!token.equals(request.getParameter("csrf_token"))) {
    response.sendError(403, "CSRF Validation Failed");
}
```

---

## 4. Risk Summary

| Vulnerability | CVSS | Risk Level | Status |
|--------------|------|-----------|--------|
| SQL Injection | 9.8 | Critical | Documented + Fixed |
| XSS Reflected | 8.8 | High | Documented + Fixed |
| CSRF | 7.4 | High | Documented + Fixed |

---

## 5. Recommendations

1. Implement parameterised queries across ALL database interactions
2. Apply output encoding on ALL user-controlled data rendered in HTML
3. Deploy CSRF tokens on ALL state-changing HTTP requests
4. Enable Content Security Policy headers site-wide
5. Set HttpOnly and SameSite=Strict on all session cookies
6. Schedule regular automated scans + manual penetration tests
