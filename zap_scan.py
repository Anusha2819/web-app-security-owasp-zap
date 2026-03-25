#!/usr/bin/env python3
"""
zap_scan.py — Full Automated OWASP ZAP Web Scanner
Author: Anuhack | github.com/anuhack
"""

import time
import json
import sys
import requests
from datetime import datetime

# ─── Configuration ───────────────────────────────────────────
ZAP_URL  = "http://127.0.0.1:8080"
API_KEY  = "mysecretkey"
TARGET   = "http://localhost:3000"   # Change to your target
REPORTS  = "./reports"
# ─────────────────────────────────────────────────────────────

BANNER = """
╔══════════════════════════════════════════════════════╗
║        OWASP ZAP — Automated Web App Scanner         ║
║              github.com/anuhack                      ║
╚══════════════════════════════════════════════════════╝
"""

def zap_get(endpoint, params={}):
    params["apikey"] = API_KEY
    try:
        r = requests.get(f"{ZAP_URL}/JSON/{endpoint}", params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        print("  [!] Cannot connect to ZAP. Is it running on port 8080?")
        sys.exit(1)

def check_zap_running():
    try:
        v = zap_get("core/view/version")
        print(f"  [+] ZAP connected — version {v['version']}")
        return True
    except:
        return False

def wait_for(check_fn, label, interval=5):
    print(f"  [*] {label}...")
    while True:
        try:
            progress = int(check_fn())
            bar = "█" * (progress // 5) + "░" * (20 - progress // 5)
            print(f"\r      [{bar}] {progress}%", end="", flush=True)
            if progress >= 100:
                print()
                break
        except:
            pass
        time.sleep(interval)
    print(f"  [+] {label} — Done!")

def run_spider(target):
    print("\n[PHASE 1] 🕷️  Spider Crawl")
    scan = zap_get("spider/action/scan", {"url": target, "recurse": "true", "maxChildren": "10"})
    sid = scan.get("scan", "0")
    wait_for(lambda: zap_get("spider/view/status", {"scanId": sid})["status"], "Spider crawl")
    urls = zap_get("spider/view/results", {"scanId": sid})
    print(f"  [+] URLs discovered: {len(urls.get('results', []))}")

def run_ajax_spider(target):
    print("\n[PHASE 2] 🔄  AJAX Spider (JS-rendered pages)")
    zap_get("ajaxSpider/action/scan", {"url": target})
    time.sleep(5)
    for _ in range(30):
        status = zap_get("ajaxSpider/view/status")
        if status.get("status") == "stopped":
            break
        time.sleep(3)
    print("  [+] AJAX Spider — Done!")

def wait_passive_scan():
    print("\n[PHASE 3] 🔍  Passive Scan")
    while True:
        remaining = int(zap_get("pscan/view/recordsToScan")["recordsToScan"])
        print(f"\r      Records remaining: {remaining}   ", end="", flush=True)
        if remaining == 0:
            break
        time.sleep(3)
    print("\n  [+] Passive Scan — Done!")

def run_active_scan(target):
    print("\n[PHASE 4] ⚔️   Active Scan (Attack Simulation)")
    scan = zap_get("ascan/action/scan", {"url": target, "recurse": "true", "inScopeOnly": "false"})
    sid = scan.get("scan", "0")
    wait_for(lambda: zap_get("ascan/view/status", {"scanId": sid})["status"], "Active scan", interval=10)

def collect_alerts(target):
    print("\n[PHASE 5] 📊  Collecting Results")
    alerts = zap_get("core/view/alerts", {"baseurl": target})["alerts"]
    risks = {"High": [], "Medium": [], "Low": [], "Informational": []}
    for a in alerts:
        risks.get(a.get("risk", "Informational"), risks["Informational"]).append(a)
    return alerts, risks

def save_reports(alerts, risks):
    import os
    os.makedirs(REPORTS, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # JSON
    json_path = f"{REPORTS}/zap_report_{ts}.json"
    with open(json_path, "w") as f:
        json.dump(alerts, f, indent=2)

    # Summary TXT
    txt_path = f"{REPORTS}/summary_{ts}.txt"
    with open(txt_path, "w") as f:
        f.write(f"ZAP Scan Summary — {datetime.now()}\n")
        f.write(f"Target: {TARGET}\n")
        f.write("=" * 50 + "\n")
        for level, items in risks.items():
            f.write(f"[{level}] {len(items)} findings\n")
        f.write("=" * 50 + "\n\n")
        for a in alerts:
            f.write(f"[{a.get('risk')}] {a.get('name')}\n")
            f.write(f"  URL: {a.get('url')}\n")
            f.write(f"  Desc: {a.get('description', '')[:120]}\n\n")

    print(f"  [+] JSON  → {json_path}")
    print(f"  [+] Summary → {txt_path}")

    # HTML via ZAP API
    try:
        html = requests.get(
            f"{ZAP_URL}/OTHER/core/other/htmlreport/",
            params={"apikey": API_KEY}
        ).text
        html_path = f"{REPORTS}/zap_report_{ts}.html"
        with open(html_path, "w") as f:
            f.write(html)
        print(f"  [+] HTML  → {html_path}")
    except:
        pass

def print_summary(risks):
    print("\n" + "═" * 52)
    print("  📋  SCAN SUMMARY")
    print("═" * 52)
    total = sum(len(v) for v in risks.values())
    print(f"  Total Vulnerabilities : {total}")
    colors = {"High": "🔴", "Medium": "🟠", "Low": "🟡", "Informational": "🔵"}
    for level, items in risks.items():
        print(f"  {colors[level]} {level:<15} : {len(items)}")
    print("═" * 52)

# ─── Main ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print(BANNER)
    print(f"  Target  : {TARGET}")
    print(f"  ZAP API : {ZAP_URL}")
    print(f"  Time    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    if not check_zap_running():
        print("  [!] Start ZAP first: zap.sh -daemon -host 127.0.0.1 -port 8080 -config api.key=mysecretkey")
        sys.exit(1)

    run_spider(TARGET)
    run_ajax_spider(TARGET)
    wait_passive_scan()
    run_active_scan(TARGET)
    alerts, risks = collect_alerts(TARGET)
    save_reports(alerts, risks)
    print_summary(risks)
    print("\n  ✅  Scan complete!\n")
