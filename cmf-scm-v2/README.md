# CMF Supply Chain Management System v2.0

## 📦 部署包说明

本版本为**修复后的生产就绪版本**，解决了之前部署中的所有问题：

### ✅ 核心修复
1. **移除外部依赖**: 不再需要 `pytz` 模块，使用 Python 标准库处理时间
2. **单文件架构**: 所有代码合并到 `main.py`，避免导入路径问题
3. **自动路径配置**: 启动时自动将当前目录加入 `sys.path`
4. **精简依赖**: `requirements.txt` 仅包含必需的 4 个包
5. **增强的 systemd 配置**: 明确设置 `PYTHONPATH` 环境变量

### 📁 文件结构
```
cmf-scm-v2/
├── src/
│   └── main.py              # 主应用（包含所有业务逻辑）
├── install.sh               # 一键安装脚本
├── requirements.txt         # Python 依赖
├── README.md                # 本文件
└── deploy/
    ├── cmf-scm.service      # systemd 服务模板
    └── nginx.conf           # Nginx 配置（可选）
```

---

## 🚀 快速部署（推荐）

### 方式一：一键脚本部署

```bash
# 1. 上传部署包到服务器
scp -r cmf-scm-v2 root@你的服务器IP:/tmp/

# 2. SSH 登录服务器
ssh root@你的服务器IP

# 3. 执行安装脚本
cd /tmp/cmf-scm-v2
chmod +x install.sh
./install.sh
```

安装完成后，服务会自动启动并设置为开机自启。

### 方式二：手动部署

```bash
# 1. 创建安装目录
sudo mkdir -p /opt/cmf-scm
cd /opt/cmf-scm

# 2. 复制文件
cp /tmp/cmf-scm-v2/src/main.py .
cp /tmp/cmf-scm-v2/requirements.txt .

# 3. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 4. 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 5. 测试运行
python -m uvicorn main:app --host 0.0.0.0 --port 8000
# 按 Ctrl+C 停止测试

# 6. 配置 systemd 服务（见下方）
```

---

## 🔧 systemd 服务配置

创建 `/etc/systemd/system/cmf-scm.service` 文件：

```ini
[Unit]
Description=CMF Supply Chain Management System
After=network.target

[Service]
Type=notify
User=root
WorkingDirectory=/opt/cmf-scm
Environment="PATH=/opt/cmf-scm/venv/bin"
Environment="PYTHONPATH=/opt/cmf-scm"
ExecStart=/opt/cmf-scm/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=cmf-scm

[Install]
WantedBy=multi-user.target
```

然后执行：
```bash
sudo systemctl daemon-reload
sudo systemctl enable cmf-scm
sudo systemctl start cmf-scm
sudo systemctl status cmf-scm
```

---

## 🌐 访问地址

部署成功后，通过以下地址访问：

| 功能 | URL |
|------|-----|
| Web 界面 | `http://服务器IP:8000/` |
| API 文档 | `http://服务器IP:8000/api/docs` |
| 健康检查 | `http://服务器IP:8000/api/health` |
| 系统时间 | `http://服务器IP:8000/api/system/time` |

---

## ⚠️ 重要提示

### 云服务器安全组配置

**必须**在云服务商控制台开放 8000 端口：

- **阿里云**: 控制台 → 安全组 → 添加规则 → TCP 8000
- **腾讯云**: 控制台 → 安全组 → 入站规则 → TCP 8000
- **AWS**: EC2 → Security Groups → Inbound Rules → Custom TCP 8000
- **Azure**: NSG → Inbound Security Rules → TCP 8000

### 防火墙配置

如果服务器启用了防火墙：

```bash
# Ubuntu (UFW)
sudo ufw allow 8000/tcp
sudo ufw reload

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

---

## 🛠️ 运维命令

```bash
# 查看服务状态
sudo systemctl status cmf-scm

# 查看实时日志
sudo journalctl -u cmf-scm -f

# 重启服务
sudo systemctl restart cmf-scm

# 停止服务
sudo systemctl stop cmf-scm

# 启动服务
sudo systemctl start cmf-scm

# 禁用开机自启
sudo systemctl disable cmf-scm
```

---

## 📊 API 接口概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/dashboard/overview` | 仪表盘聚合数据 |
| GET | `/api/projects` | 获取项目列表 |
| GET | `/api/projects/{id}` | 获取项目详情 |
| POST | `/api/projects` | 创建新项目 |
| GET | `/api/tasks` | 获取任务列表 |
| POST | `/api/tasks` | 创建新任务 |
| DELETE | `/api/tasks/{id}` | 删除任务 |
| PATCH | `/api/parts/{id}/status` | 更新部件状态 |
| GET | `/api/users` | 获取用户列表 |

详细 API 文档请访问 `/api/docs`。

---

## ❓ 故障排查

### 问题 1: 服务无法启动

```bash
# 查看详细错误日志
sudo journalctl -u cmf-scm --no-pager -n 50

# 手动测试启动
cd /opt/cmf-scm
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 问题 2: 页面无法访问但服务正常

1. 检查防火墙：`sudo ufw status` 或 `sudo firewall-cmd --list-all`
2. 检查云安全组是否开放 8000 端口
3. 检查端口监听：`sudo ss -tlnp | grep 8000`

### 问题 3: 需要更换端口

修改 systemd 服务文件中的 `--port 8000` 为其他端口，然后：
```bash
sudo systemctl daemon-reload
sudo systemctl restart cmf-scm
```

---

## 📝 版本历史

### v2.0.0 (2024-01)
- ✅ 修复 `ModuleNotFoundError: No module named 'pytz'`
- ✅ 修复 `ModuleNotFoundError: No module named 'models'`
- ✅ 合并所有代码到单文件，消除导入问题
- ✅ 精简依赖，仅需 4 个包
- ✅ 增强 systemd 配置，自动设置 PYTHONPATH
- ✅ 提供一键安装脚本

### v1.0.0 (初始版本)
- 初始发布，存在多文件导入问题

---

## 📞 技术支持

如遇问题，请提供以下信息：
1. 操作系统版本：`cat /etc/os-release`
2. Python 版本：`python3 --version`
3. 服务状态：`sudo systemctl status cmf-scm`
4. 错误日志：`sudo journalctl -u cmf-scm --no-pager -n 100`
