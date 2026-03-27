#!/bin/bash

# =============================================================================
# CMF SCM System v2.0 - 一键安装部署脚本
# =============================================================================
# 使用方法:
#   chmod +x install.sh
#   ./install.sh
# =============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}CMF SCM System v2.0 - 开始部署${NC}"
echo -e "${GREEN}========================================${NC}"

# -----------------------------------------------------------------------------
# 步骤 1: 检查系统依赖
# -----------------------------------------------------------------------------
echo -e "\n${BLUE}[1/7] 检查系统依赖...${NC}"

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误：未找到 Python3，请先安装 (Ubuntu: apt install python3 python3-pip)${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "  ✓ Python 版本：$PYTHON_VERSION"

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}错误：未找到 pip3，请先安装 (Ubuntu: apt install python3-pip)${NC}"
    exit 1
fi
echo -e "  ✓ pip3 已安装"

# 检查 git (可选)
if command -v git &> /dev/null; then
    echo -e "  ✓ git 已安装"
else
    echo -e "  ⚠ git 未安装 (可选)"
fi

# -----------------------------------------------------------------------------
# 步骤 2: 创建 Python 包初始化文件
# -----------------------------------------------------------------------------
echo -e "\n${BLUE}[2/7] 创建 Python 包结构...${NC}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# 创建 __init__.py 文件
touch "$PROJECT_ROOT/backend/__init__.py"
touch "$PROJECT_ROOT/backend/src/__init__.py"
echo -e "  ✓ 已创建 backend/__init__.py"
echo -e "  ✓ 已创建 backend/src/__init__.py"

# -----------------------------------------------------------------------------
# 步骤 3: 创建虚拟环境
# -----------------------------------------------------------------------------
echo -e "\n${BLUE}[3/7] 创建 Python 虚拟环境...${NC}"

VENV_PATH="$PROJECT_ROOT/venv"

if [ -d "$VENV_PATH" ]; then
    echo -e "  ⚠ 虚拟环境已存在，将重新创建"
    rm -rf "$VENV_PATH"
fi

python3 -m venv "$VENV_PATH"
echo -e "  ✓ 虚拟环境创建完成：$VENV_PATH"

# -----------------------------------------------------------------------------
# 步骤 4: 激活虚拟环境并安装依赖
# -----------------------------------------------------------------------------
echo -e "\n${BLUE}[4/7] 安装 Python 依赖包...${NC}"

source "$VENV_PATH/bin/activate"

# 升级 pip
pip install --upgrade pip -q

# 创建 requirements.txt (v2.0 仅需 FastAPI 和 Uvicorn)
REQ_FILE="$PROJECT_ROOT/backend/requirements.txt"
cat > "$REQ_FILE" << EOF
# CMF SCM System v2.0 - 零外部依赖版本
# 仅需 FastAPI 和 Uvicorn
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
EOF

pip install -r "$REQ_FILE" -q
echo -e "  ✓ 依赖包安装完成 (FastAPI + Uvicorn + Pydantic)"

# -----------------------------------------------------------------------------
# 步骤 5: 配置环境变量
# -----------------------------------------------------------------------------
echo -e "\n${BLUE}[5/7] 配置环境变量...${NC}"

ENV_FILE="$PROJECT_ROOT/.env"
if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << EOF
# CMF SCM System v2.0 - 环境配置

# 服务配置
HOST=0.0.0.0
PORT=8000

# v2.0 特性：无需数据库配置，使用内存数据
# DATABASE_MODE=memory (内置)

# 日志配置
LOG_LEVEL=info
EOF
    echo -e "  ✓ 已生成 .env 配置文件"
else
    echo -e "  ✓ .env 文件已存在"
fi

# -----------------------------------------------------------------------------
# 步骤 6: 验证安装
# -----------------------------------------------------------------------------
echo -e "\n${BLUE}[6/7] 验证安装...${NC}"

cd "$PROJECT_ROOT"
source "$VENV_PATH/bin/activate"

# 测试导入
python3 -c "from backend.src import app; print('  ✓ 模块导入成功')" 2>/dev/null || {
    echo -e "${RED}错误：模块导入失败，请检查项目结构${NC}"
    exit 1
}

# 检查 app.py 是否存在
if [ -f "$PROJECT_ROOT/backend/src/app.py" ]; then
    echo -e "  ✓ app.py 存在"
else
    echo -e "${RED}错误：未找到 backend/src/app.py${NC}"
    exit 1
fi

echo -e "  ✓ 安装验证通过"

# -----------------------------------------------------------------------------
# 步骤 7: 创建系统服务 (systemd) - 仅 root 用户
# -----------------------------------------------------------------------------
echo -e "\n${BLUE}[7/7] 配置 systemd 服务...${NC}"

SERVICE_FILE="/etc/systemd/system/cmf-scm-v2.service"

if [ "$EUID" -ne 0 ]; then
    echo -e "  ${YELLOW}提示：非 root 用户，跳过 systemd 服务配置${NC}"
    echo -e "  ${YELLOW}如需开机自启，请以 sudo 运行此脚本或手动配置:${NC}"
    echo -e "    sudo cp cmf-scm-v2.service /etc/systemd/system/"
    echo -e "    sudo systemctl daemon-reload"
    echo -e "    sudo systemctl enable cmf-scm-v2"
    echo -e "    sudo systemctl start cmf-scm-v2"
else
    cat > /tmp/cmf-scm-v2.service << EOF
[Unit]
Description=CMF SCM System v2.0
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_ROOT
Environment="PATH=$VENV_PATH/bin"
ExecStart=$VENV_PATH/bin/python -m uvicorn backend.src.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

# 日志
StandardOutput=journal
StandardError=journal
SyslogIdentifier=cmf-scm-v2

[Install]
WantedBy=multi-user.target
EOF

    cp /tmp/cmf-scm-v2.service "$SERVICE_FILE"
    systemctl daemon-reload
    systemctl enable cmf-scm-v2
    systemctl start cmf-scm-v2

    echo -e "  ✓ systemd 服务配置完成"
    
    # 等待服务启动
    sleep 2
    SERVICE_STATUS=$(systemctl is-active cmf-scm-v2 2>/dev/null || echo "unknown")
    echo -e "  ✓ 服务状态：$SERVICE_STATUS"
fi

# -----------------------------------------------------------------------------
# 部署完成
# -----------------------------------------------------------------------------
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"

# 获取本机 IP
IP_ADDR=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "YOUR_SERVER_IP")

echo -e "\n${YELLOW}访问方式:${NC}"
echo -e "  本地访问：http://localhost:8000"
echo -e "  远程访问：http://${IP_ADDR}:8000"
echo -e "  API 文档：http://${IP_ADDR}:8000/api/docs"
echo -e "  健康检查：http://${IP_ADDR}:8000/health"

echo -e "\n${YELLOW}管理命令:${NC}"
if [ "$EUID" -eq 0 ]; then
    echo -e "  启动服务：sudo systemctl start cmf-scm-v2"
    echo -e "  停止服务：sudo systemctl stop cmf-scm-v2"
    echo -e "  重启服务：sudo systemctl restart cmf-scm-v2"
    echo -e "  查看日志：sudo journalctl -u cmf-scm-v2 -f"
    echo -e "  禁用自启：sudo systemctl disable cmf-scm-v2"
else
    echo -e "  手动启动：cd $PROJECT_ROOT && source venv/bin/activate && python -m uvicorn backend.src.app:app --host 0.0.0.0 --port 8000"
fi

echo -e "\n${YELLOW}防火墙配置提示:${NC}"
echo -e "  Ubuntu: sudo ufw allow 8000/tcp"
echo -e "  CentOS: sudo firewall-cmd --permanent --add-port=8000/tcp && sudo firewall-cmd --reload"
echo -e "  阿里云/腾讯云：在安全组中开放 8000 端口"

echo -e "\n${BLUE}v2.0 新特性:${NC}"
echo -e "  ✅ 单文件架构 - 无模块导入错误"
echo -e "  ✅ 零外部依赖 - 仅需 FastAPI/Uvicorn"
echo -e "  ✅ 内存数据 - 开箱即用，无需数据库"
echo -e "  ✅ < 2 秒启动 - 极速冷启动"

echo -e "\n${GREEN}祝使用愉快！${NC}\n"
