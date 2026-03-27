#!/bin/bash
# CMF SCM System - One-Click Installation Script
# Version: 2.0.0

set -e

echo "=========================================="
echo "CMF Supply Chain Management System v2.0"
echo "Installation Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/cmf-scm"
SERVICE_NAME="cmf-scm"
PORT=8000

echo -e "${YELLOW}Step 1: Checking prerequisites...${NC}"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python version: $PYTHON_VERSION"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed${NC}"
    exit 1
fi
echo "✓ pip3 is available"

echo -e "${YELLOW}Step 2: Creating installation directory...${NC}"
mkdir -p $INSTALL_DIR
echo "✓ Created directory: $INSTALL_DIR"

echo -e "${YELLOW}Step 3: Copying application files...${NC}"
# Copy src directory
cp -r $(dirname "$0")/src/* $INSTALL_DIR/
echo "✓ Application files copied"

echo -e "${YELLOW}Step 4: Creating virtual environment...${NC}"
cd $INSTALL_DIR
python3 -m venv venv
echo "✓ Virtual environment created"

echo -e "${YELLOW}Step 5: Installing dependencies...${NC}"
source $INSTALL_DIR/venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r $INSTALL_DIR/requirements.txt
echo "✓ Dependencies installed"

echo -e "${YELLOW}Step 6: Creating systemd service...${NC}"
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=CMF Supply Chain Management System
After=network.target

[Service]
Type=notify
User=root
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
Environment="PYTHONPATH=$INSTALL_DIR"
ExecStart=$INSTALL_DIR/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF
echo "✓ Systemd service file created"

echo -e "${YELLOW}Step 7: Reloading systemd and enabling service...${NC}"
systemctl daemon-reload
systemctl enable $SERVICE_NAME
echo "✓ Service enabled"

echo -e "${YELLOW}Step 8: Configuring firewall...${NC}"
if command -v ufw &> /dev/null; then
    ufw allow $PORT/tcp comment "CMF SCM Web Service" > /dev/null 2>&1 || true
    echo "✓ UFW rule added (if UFW is active)"
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-port=$PORT/tcp > /dev/null 2>&1 || true
    firewall-cmd --reload > /dev/null 2>&1 || true
    echo "✓ firewalld rule added (if firewalld is active)"
else
    echo "⚠ No firewall manager detected, skipping"
fi

echo -e "${YELLOW}Step 9: Starting service...${NC}"
systemctl start $SERVICE_NAME
sleep 3
echo "✓ Service started"

echo ""
echo -e "${GREEN}=========================================="
echo "Installation Complete!"
echo "==========================================${NC}"
echo ""
echo "Service Status:"
systemctl status $SERVICE_NAME --no-pager -l
echo ""
echo "Access URLs:"
echo "  - Web Interface: http://$(hostname -I | awk '{print $1}'):$PORT"
echo "  - API Docs:      http://$(hostname -I | awk '{print $1}'):$PORT/api/docs"
echo "  - Health Check:  http://$(hostname -I | awk '{print $1}'):$PORT/api/health"
echo ""
echo "Management Commands:"
echo "  - Start:   systemctl start $SERVICE_NAME"
echo "  - Stop:    systemctl stop $SERVICE_NAME"
echo "  - Restart: systemctl restart $SERVICE_NAME"
echo "  - Logs:    journalctl -u $SERVICE_NAME -f"
echo ""
echo -e "${YELLOW}Note: Make sure port $PORT is open in your cloud provider's security group!${NC}"
echo ""
