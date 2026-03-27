#!/bin/bash
# CMF SCM System v2.0 - Systemd Deployment Script
# This script configures and starts the service with systemd

set -e

echo "=========================================="
echo "  CMF SCM System v2.0 - Deploy to Systemd"
echo "=========================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get absolute path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

INSTALL_DIR="/opt/cmf-scm-v2"
SERVICE_NAME="cmf-scm-v2"

echo -e "${YELLOW}Installing to $INSTALL_DIR...${NC}"

# Create installation directory
sudo mkdir -p "$INSTALL_DIR"

# Copy files
sudo cp -r ./* "$INSTALL_DIR/"

# Set ownership
sudo chown -R $USER:$USER "$INSTALL_DIR"

echo -e "${GREEN}✓${NC} Files copied to $INSTALL_DIR"

# Create systemd service file
echo -e "${YELLOW}Creating systemd service...${NC}"

sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=CMF Supply Chain Management System v2.0
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR/src
Environment="PATH=$INSTALL_DIR/venv/bin"
Environment="PYTHONPATH=$INSTALL_DIR/src"
ExecStart=$INSTALL_DIR/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=${SERVICE_NAME}

# Security hardening
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓${NC} Systemd service created"

# Reload systemd
echo -e "${YELLOW}Reloading systemd daemon...${NC}"
sudo systemctl daemon-reload

# Enable service
echo -e "${YELLOW}Enabling service...${NC}"
sudo systemctl enable ${SERVICE_NAME}

# Start service
echo -e "${YELLOW}Starting service...${NC}"
sudo systemctl start ${SERVICE_NAME}

# Wait for service to start
sleep 3

# Check status
echo ""
echo -e "${YELLOW}Service Status:${NC}"
sudo systemctl status ${SERVICE_NAME} --no-pager -l

echo ""
echo "=========================================="
if sudo systemctl is-active --quiet ${SERVICE_NAME}; then
    echo -e "${GREEN}  Deployment Successful!${NC}"
    echo "=========================================="
    echo ""
    echo "Application is running at:"
    echo "  http://YOUR_SERVER_IP:8000"
    echo ""
    echo "API Documentation:"
    echo "  http://YOUR_SERVER_IP:8000/api/docs"
    echo ""
    echo "Useful commands:"
    echo "  sudo systemctl status ${SERVICE_NAME}   - Check status"
    echo "  sudo systemctl restart ${SERVICE_NAME}  - Restart service"
    echo "  sudo journalctl -u ${SERVICE_NAME} -f   - View logs"
    echo "  sudo systemctl stop ${SERVICE_NAME}     - Stop service"
else
    echo -e "${RED}  Deployment Failed!${NC}"
    echo "=========================================="
    echo ""
    echo "Check logs with:"
    echo "  sudo journalctl -u ${SERVICE_NAME} -n 50"
fi
echo ""
