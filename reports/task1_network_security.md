# Task 1 — Network Security Hardening Report

**Tester:** Perikala Anusha  
**Organisation:** Redynox (Internship)  
**Date:** February 2026  
**Environment:** Windows Home Lab + Kali Linux WSL2

---

## 1. Objectives

- Configure Windows Defender Firewall with advanced rules
- Harden home router (credentials, encryption, firmware)
- Disable legacy SMBv1 protocol (EternalBlue mitigation)
- Verify clean traffic baseline with Wireshark

---

## 2. Firewall Configuration (wf.msc)

```
Profiles configured:  Domain, Private, Public — ALL ON
Logging enabled:      Dropped packets logged
Custom rule created:  Inbound block rule for unauthorised ports
```

**Steps taken:**
- Opened Windows Defender Firewall with Advanced Security (wf.msc)
- Enabled firewall on all three network profiles
- Enabled dropped-packet logging for audit trail
- Created custom inbound block rule to demonstrate granular access control

---

## 3. Router Hardening

```
Action                          Before              After
──────────────────────────────────────────────────────────
Admin credentials               Default (admin/admin) Strong unique password
Wireless encryption             WPA2-TKIP           WPA3-Personal + AES-CCMP
Firmware                        Outdated            Updated to latest
UPnP                            Enabled             Disabled
Remote Management               Enabled             Disabled
```

---

## 4. SMBv1 Disabling (EternalBlue / WannaCry Mitigation)

**Why:** SMBv1 is exploited by EternalBlue (CVE-2017-0144) — the vulnerability used by WannaCry ransomware.

**Command run (PowerShell as Administrator):**
```powershell
# Disable SMBv1
Set-SmbServerConfiguration -EnableSMB1Protocol $false -Force

# Verify
Get-SmbServerConfiguration | Select EnableSMB1Protocol
# Expected: EnableSMB1Protocol : False

# Also disable File and Printer Sharing
netsh advfirewall firewall set rule group="File and Printer Sharing" new enable=No
```

---

## 5. Wireshark Traffic Verification

**Capture duration:** 10 minutes post-hardening  
**Filters applied:**

```
tcp.flags.syn == 1          # SYN packets — new connections
http.request                # HTTP requests
dns                         # DNS queries
```

**Result:** Clean baseline confirmed — no malicious or unexpected connections detected.

---

## 6. Security Controls Summary

| Control | Implementation | Outcome |
|---------|---------------|---------|
| Windows Firewall | All profiles ON + logging | Audit trail active |
| Router credentials | Default → Strong password | Brute force mitigated |
| Wireless encryption | WPA2 → WPA3 + AES-CCMP | Modern encryption |
| SMBv1 | Disabled via PowerShell | EternalBlue blocked |
| UPnP | Disabled | Remote exploit surface reduced |
| Traffic baseline | Wireshark 10min capture | Clean — no anomalies |

---

## 7. Documentation

- 9 implementation screenshots captured
- Written analysis produced for each control
- Professional security report format followed
