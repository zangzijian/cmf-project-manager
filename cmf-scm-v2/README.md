# CMF Supply Chain Management System v2.0

## 版本说明

v2.0 是彻底重构的生产就绪版本，解决了之前所有的部署问题：

### 核心改进
✅ **零外部依赖**: 仅需 fastapi, uvicorn, pydantic (已锁定版本)
✅ **自动路径处理**: 内置 sys.path 修正，systemd 部署不再报错
✅ **单文件架构**: 所有代码在 src/main.py，无相对导入问题
✅ **内置 Mock 数据**: 安装即可用，无需数据库配置
✅ **完整部署脚本**: 一键安装和 systemd 部署

## 快速部署

### 方法一：手动测试（推荐先测试）

```bash
# 1. 上传整个 cmf-scm-v2 文件夹到服务器
scp -r cmf-scm-v2 root@YOUR_SERVER_IP:/opt/

# 2. SSH 登录服务器
ssh root@YOUR_SERVER_IP

# 3. 运行安装脚本
cd /opt/cmf-scm-v2
chmod +x install.sh scripts/deploy.sh
./install.sh

# 4. 直接启动测试
source venv/bin/activate
cd src
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

访问 http://YOUR_SERVER_IP:8000

### 方法二：Systemd 服务部署（生产环境）

```bash
# 1-3 步同上

# 4. 运行部署脚本
cd /opt/cmf-scm-v2
./scripts/deploy.sh
```

服务将自动启动并开机自启。

## 目录结构

```
cmf-scm-v2/
├── src/
│   ├── main.py          # 主应用（430 行，包含所有 API 和 Mock 数据）
│   └── static/          # 前端 HTML 文件存放目录
│       └── mainweb.html # 将你的前端文件放在这里
├── scripts/
│   └── deploy.sh        # Systemd 部署脚本
├── install.sh           # 一键安装脚本
├── requirements.txt     # Python 依赖（已锁定版本）
└── README.md            # 本文件
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/system/time` | GET | 服务器时间 |
| `/api/dashboard/overview` | GET | 仪表盘总览 |
| `/api/projects` | GET/POST | 项目列表/创建 |
| `/api/projects/{id}` | GET | 项目详情 |
| `/api/parts` | GET | 部件列表 |
| `/api/parts/{id}/status` | PATCH | 更新部件状态 |
| `/api/tasks` | GET/POST | 任务列表/创建 |
| `/api/tasks/{id}` | DELETE | 删除任务 |
| `/api/users` | GET | 用户列表 |

## 故障排查

### 服务无法启动
```bash
# 查看详细日志
sudo journalctl -u cmf-scm-v2 -n 50 --no-pager

# 手动测试启动
cd /opt/cmf-scm-v2
source venv/bin/activate
cd src
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 端口被占用
```bash
# 查看 8000 端口占用
sudo ss -tlnp | grep 8000

# 修改端口（编辑 scripts/deploy.sh 中的 ExecStart 行）
```

### 防火墙问题
```bash
# Ubuntu/Debian
sudo ufw allow 8000/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# 阿里云/腾讯云：在控制台安全组开放 8000 端口
```

## 技术栈

- **后端框架**: FastAPI 0.109.0
- **ASGI 服务器**: Uvicorn 0.27.0
- **数据验证**: Pydantic 2.5.3
- **Python**: 3.8+
- **数据存储**: 内存 Mock（可扩展 SQLite/PostgreSQL）

## 从 v1.x 升级

v2.0 是彻底重构版本，不建议升级，建议全新部署：

1. 停止旧服务：`sudo systemctl stop cmf-scm`
2. 禁用旧服务：`sudo systemctl disable cmf-scm`
3. 删除旧文件：`sudo rm -rf /opt/cmf-scm`
4. 按上述步骤部署 v2.0

## 许可证

内部使用，请勿外传。
