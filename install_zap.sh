#!/bin/bash
# ============================================================
# install_zap.sh — OWASP ZAP Installer for Kali Linux WSL
# Author: Anuhack | GitHub: github.com/anuhack
# ============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}"
echo "  ╔═══════════════════════════════════════╗"
echo "  ║   OWASP ZAP Installer — Kali WSL      ║"
echo "  ╚═══════════════════════════════════════╝"
echo -e "${NC}"

# Check we're in Linux home, not Windows path
if [[ "$PWD" == /mnt/c/* ]]; then
  echo -e "${RED}[!] ERROR: You're in the Windows filesystem (/mnt/c/)${NC}"
  echo -e "${YELLOW}[*] Run: cd ~ && bash setup/install_zap.sh${NC}"
  exit 1
fi

cd ~
echo -e "${GREEN}[+] Working directory: $(pwd)${NC}"

# Install Java
echo -e "${YELLOW}[*] Installing Java 17...${NC}"
sudo apt update -qq
sudo apt install -y openjdk-17-jdk wget curl git python3 python3-pip docker.io
java -version

# Download ZAP
ZAP_VERSION="2.16.1"
ZAP_FILE="ZAP_${ZAP_VERSION}_Linux.tar.gz"
ZAP_URL="https://github.com/zaproxy/zaproxy/releases/download/v${ZAP_VERSION}/${ZAP_FILE}"

echo -e "${YELLOW}[*] Downloading OWASP ZAP v${ZAP_VERSION}...${NC}"
wget -q --show-progress "$ZAP_URL"

echo -e "${YELLOW}[*] Extracting...${NC}"
tar -xzf "$ZAP_FILE"
sudo mv "ZAP_${ZAP_VERSION}" /opt/zaproxy
sudo ln -sf /opt/zaproxy/zap.sh /usr/local/bin/zap.sh
sudo chmod +x /opt/zaproxy/zap.sh

# Verify
echo -e "${GREEN}[+] ZAP installed at /opt/zaproxy${NC}"
zap.sh -version

# Python deps
echo -e "${YELLOW}[*] Installing Python dependencies...${NC}"
pip3 install requests python-owasp-zap-v2.4 --quiet

echo -e "${GREEN}"
echo "  ╔═══════════════════════════════════════╗"
echo "  ║   ✅ Installation Complete!            ║"
echo "  ║   Run: zap.sh -version to verify       ║"
echo "  ╚═══════════════════════════════════════╝"
echo -e "${NC}"
