#!/bin/bash

# =============================================================================
# CMF 供应链管理系统 - Linux 云服务器一键部署脚本
# =============================================================================
# 使用方法:
#   1. 上传整个 backend 文件夹到服务器
#   2. chmod +x deploy.sh
#   3. ./deploy.sh
# =============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}CMF 供应链管理系统 - 开始部署${NC}"
echo -e "${GREEN}========================================${NC}"

# -----------------------------------------------------------------------------
# 步骤 1: 检查系统依赖
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[1/6] 检查系统依赖...${NC}"

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误：未找到 Python3，请先安装 (Ubuntu: apt install python3 python3-pip)${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python 版本：$PYTHON_VERSION"

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}错误：未找到 pip3，请先安装 (Ubuntu: apt install python3-pip)${NC}"
    exit 1
fi
echo "✓ pip3 已安装"

# 检查 git (可选，用于拉取代码)
if command -v git &> /dev/null; then
    echo "✓ git 已安装"
else
    echo "⚠ git 未安装 (可选)"
fi

# -----------------------------------------------------------------------------
# 步骤 2: 创建虚拟环境
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[2/6] 创建 Python 虚拟环境...${NC}"

cd "$(dirname "$0")"
PROJECT_ROOT="$(pwd)"
VENV_PATH="$PROJECT_ROOT/venv"

if [ -d "$VENV_PATH" ]; then
    echo "⚠ 虚拟环境已存在，将重新创建"
    rm -rf "$VENV_PATH"
fi

python3 -m venv "$VENV_PATH"
echo "✓ 虚拟环境创建完成：$VENV_PATH"

# -----------------------------------------------------------------------------
# 步骤 3: 激活虚拟环境并安装依赖
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[3/6] 安装 Python 依赖包...${NC}"

source "$VENV_PATH/bin/activate"

# 升级 pip
pip install --upgrade pip -q

# 创建 requirements.txt (如果不存在)
REQ_FILE="$PROJECT_ROOT/requirements.txt"
if [ ! -f "$REQ_FILE" ]; then
    cat > "$REQ_FILE" << EOF
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
pydantic==2.5.3
pydantic-settings==2.1.0
psycopg2-binary==2.9.9
python-multipart==0.0.6
aiosqlite==0.19.0  # SQLite 异步支持 (开发环境用)
EOF
    echo "✓ 已生成 requirements.txt"
fi

# 安装依赖
pip install -r "$REQ_FILE" -q
echo "✓ 依赖包安装完成"

# -----------------------------------------------------------------------------
# 步骤 4: 配置环境变量
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[4/6] 配置环境变量...${NC}"

ENV_FILE="$PROJECT_ROOT/.env"
if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << EOF
# CMF 供应链管理系统 - 环境配置

# 服务配置
HOST=0.0.0.0
PORT=8000
WORKERS=2

# 数据库配置 (生产环境建议使用 PostgreSQL)
# 模式选择: sqlite (开发/演示) 或 postgresql (生产)
DATABASE_MODE=sqlite
DATABASE_URL=sqlite:///./cmf_database.db

# PostgreSQL 配置示例 (取消注释并使用)
# DATABASE_MODE=postgresql
# DATABASE_URL=postgresql://user:password@localhost:5432/cmf_db

# Redis 配置 (可选，用于缓存)
REDIS_URL=redis://localhost:6379/0
USE_REDIS=false

# 安全配置
SECRET_KEY=your-secret-key-change-in-production
API_PREFIX=/api

# 日志配置
LOG_LEVEL=info
EOF
    echo "✓ 已生成 .env 配置文件"
    echo -e "${YELLOW}提示：请编辑 .env 文件修改数据库配置和安全密钥${NC}"
else
    echo "✓ .env 文件已存在"
fi

# -----------------------------------------------------------------------------
# 步骤 5: 初始化数据库 (仅首次)
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[5/6] 初始化数据库...${NC}"

# 运行初始化脚本
if [ -f "$PROJECT_ROOT/src/init_db.py" ]; then
    source "$VENV_PATH/bin/activate"
    cd "$PROJECT_ROOT/src"
    python init_db.py
    echo "✓ 数据库初始化完成"
else
    echo "⚠ 未找到 init_db.py，将在首次启动时自动创建"
fi

# -----------------------------------------------------------------------------
# 步骤 6: 创建系统服务 (systemd)
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[6/6] 配置 systemd 服务...${NC}"

SERVICE_FILE="/etc/systemd/system/cmf-scm.service"

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}提示：非 root 用户，跳过 systemd 服务配置${NC}"
    echo -e "${YELLOW}如需开机自启，请以 sudo 运行此脚本或使用以下命令手动配置:${NC}"
    echo -e "  sudo cp cmf-scm.service /etc/systemd/system/"
    echo -e "  sudo systemctl daemon-reload"
    echo -e "  sudo systemctl enable cmf-scm"
    echo -e "  sudo systemctl start cmf-scm"
else
    cat > /tmp/cmf-scm.service << EOF
[Unit]
Description=CMF Supply Chain Management System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_ROOT
Environment="PATH=$VENV_PATH/bin"
ExecStart=$VENV_PATH/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

# 日志
StandardOutput=journal
StandardError=journal
SyslogIdentifier=cmf-scm

[Install]
WantedBy=multi-user.target
EOF

    cp /tmp/cmf-scm.service "$SERVICE_FILE"
    systemctl daemon-reload
    systemctl enable cmf-scm
    systemctl start cmf-scm
    
    echo "✓ systemd 服务配置完成"
    echo "✓ 服务状态：$(systemctl is-active cmf-scm)"
fi

# -----------------------------------------------------------------------------
# 部署完成
# -----------------------------------------------------------------------------
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"

# 获取本机 IP
IP_ADDR=$(hostname -I | awk '{print $1}')
if [ -z "$IP_ADDR" ]; then
    IP_ADDR="YOUR_SERVER_IP"
fi

echo -e "\n${YELLOW}访问方式:${NC}"
echo -e "  本地访问：http://localhost:8000"
echo -e "  远程访问：http://${IP_ADDR}:8000"
echo -e "  API 文档：http://${IP_ADDR}:8000/api/docs"
echo -e "\n${YELLOW}管理命令:${NC}"
if [ "$EUID" -eq 0 ]; then
    echo -e "  启动服务：sudo systemctl start cmf-scm"
    echo -e "  停止服务：sudo systemctl stop cmf-scm"
    echo -e "  重启服务：sudo systemctl restart cmf-scm"
    echo -e "  查看日志：sudo journalctl -u cmf-scm -f"
    echo -e "  禁用自启：sudo systemctl disable cmf-scm"
else
    echo -e "  手动启动：cd $PROJECT_ROOT && source venv/bin/activate && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000"
fi

echo -e "\n${YELLOW}防火墙配置提示:${NC}"
echo -e "  Ubuntu: sudo ufw allow 8000/tcp"
echo -e "  CentOS: sudo firewall-cmd --permanent --add-port=8000/tcp && sudo firewall-cmd --reload"
echo -e "  阿里云/腾讯云：在安全组中开放 8000 端口"

echo -e "\n${GREEN}祝使用愉快！${NC}\n"
