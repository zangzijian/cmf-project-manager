#!/bin/bash
# CMF SCM System v2.0 - One-Click Installation Script
# This script installs all dependencies and prepares the system for deployment

set -e

echo "=========================================="
echo "  CMF SCM System v2.0 - Installation"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${GREEN}✓${NC} Working directory: $SCRIPT_DIR"

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python3 is not installed. Please install Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓${NC} Python version: $PYTHON_VERSION"

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip --quiet

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet --break-system-packages 2>/dev/null || pip install -r requirements.txt --quiet
    echo -e "${GREEN}✓${NC} Dependencies installed successfully"
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    exit 1
fi

# Verify installation
echo -e "${YELLOW}Verifying installation...${NC}"
python -c "import fastapi; import uvicorn; import pydantic" && echo -e "${GREEN}✓${NC} All packages verified"

# Create static directory if not exists
if [ ! -d "src/static" ]; then
    mkdir -p src/static
    echo -e "${GREEN}✓${NC} Static directory created"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  Installation Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy your mainweb.html to src/static/"
echo "2. Run: ./scripts/deploy.sh (for systemd deployment)"
echo "   OR"
echo "   Run: source venv/bin/activate && cd src && python -m uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""
echo "Access the application at: http://YOUR_SERVER_IP:8000"
echo "API Documentation: http://YOUR_SERVER_IP:8000/api/docs"
echo ""
