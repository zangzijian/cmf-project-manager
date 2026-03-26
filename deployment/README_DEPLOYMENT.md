# 📦 CMF 供应链管理系统 - 部署包说明

本目录包含完整的后端服务和部署配置，可直接部署到 Linux 云服务器。

---

## 📁 目录结构

```
deployment/
├── README_DEPLOYMENT.md      # 本文件 - 部署包说明
├── QUICK_START.md            # ⚡ 快速开始指南（3 分钟上手）
├── DEPLOYMENT_GUIDE.md       # 📖 完整部署文档（详细教程）
├── deploy.sh                 # 🔧 一键部署脚本
├── requirements.txt          # Python 依赖列表
├── Dockerfile                # Docker 镜像构建文件
├── docker-compose.yml        # Docker Compose 配置
├── nginx.conf                # Nginx 反向代理配置
│
├── src/                      # 后端源代码
│   ├── main.py              # FastAPI 主应用
│   ├── models.py            # 数据库模型
│   ├── schemas.py           # 数据验证 Schema
│   └── mock_data.py         # Mock 数据服务
│
├── static/                   # 静态文件
│   └── mainweb.html         # 前端界面
│
└── prisma/                   # Prisma ORM 配置 (可选)
```

---

## 🚀 三种部署方式

### 方式一：一键脚本（推荐新手）

```bash
# 上传到服务器
scp -r deployment root@服务器IP:/opt/cmf-scm

# 登录并执行
ssh root@服务器IP
cd /opt/cmf-scm && ./deploy.sh
```

**优点**: 全自动配置，适合 Ubuntu/CentOS  
**时间**: 5-10 分钟

---

### 方式二：Docker（推荐生产）

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 启动服务
docker-compose up -d
```

**优点**: 环境隔离，易于维护  
**时间**: 3-5 分钟

---

### 方式三：手动部署（高级用户）

参考 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

**优点**: 完全自定义配置  
**时间**: 15-30 分钟

---

## ✅ 部署后验证

访问以下地址确认服务正常：

| URL | 说明 |
|-----|------|
| `http://服务器 IP:8000` | 主界面 |
| `http://服务器 IP:8000/api/docs` | API 文档 |
| `http://服务器 IP:8000/api/health` | 健康检查 |

---

## 🔑 核心功能

- ✅ **项目管理**: 硬件产品全生命周期管理 (EVT/DVT/PVT/MP)
- ✅ **部件追踪**: CMF 部件与供应商关联
- ✅ **风险评估**: 自动计算延期/工艺/良率风险
- ✅ **任务系统**: P0-P3 优先级任务管理
- ✅ **仪表盘**: 实时统计和项目概览
- ✅ **API 文档**: Swagger 自动生成

---

## 🛠️ 技术栈

- **后端**: FastAPI (Python 3.11+)
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **部署**: Docker / systemd
- **前端**: 原生 HTML/JS (深色毛玻璃风格)

---

## 📞 常见问题

### 1. 无法访问服务？
```bash
# 检查防火墙
sudo ufw allow 8000/tcp  # Ubuntu
sudo firewall-cmd --permanent --add-port=8000/tcp  # CentOS

# 检查服务状态
sudo systemctl status cmf-scm
```

### 2. 如何重置数据库？
```bash
cd /opt/cmf-scm/src
rm -f cmf_database.db
python -c "from mock_data import seed_database; seed_database()"
sudo systemctl restart cmf-scm
```

### 3. 如何查看日志？
```bash
# systemd 方式
sudo journalctl -u cmf-scm -f

# Docker 方式
docker-compose logs -f api
```

---

## 📚 文档索引

| 文档 | 用途 |
|------|------|
| [QUICK_START.md](./QUICK_START.md) | 快速上手，3 分钟部署 |
| [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) | 完整部署教程，故障排查 |
| [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) | API 接口详细说明 |
| [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md) | 前后端对接指南 |

---

## 📄 许可证

本项目仅供学习和内部使用。

---

**祝您部署顺利！** 🎉

如有问题，请参考 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) 或查看服务日志。
