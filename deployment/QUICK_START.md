# 🚀 CMF 供应链管理系统 - 快速部署指南

## 三种部署方式

### 方式一：一键脚本部署（推荐新手）

```bash
# 1. 上传整个 deployment 文件夹到服务器
scp -r /workspace/deployment root@你的服务器 IP:/opt/cmf-scm

# 2. SSH 登录服务器
ssh root@你的服务器 IP

# 3. 执行部署脚本
cd /opt/cmf-scm
chmod +x deploy.sh
./deploy.sh
```

**访问地址**: `http://你的服务器 IP:8000`

---

### 方式二：Docker 部署（推荐生产环境）

```bash
# 1. 确保已安装 Docker 和 Docker Compose
curl -fsSL https://get.docker.com | sh

# 2. 上传项目文件
scp -r /workspace/deployment root@你的服务器 IP:/opt/cmf-scm

# 3. 启动服务
cd /opt/cmf-scm
docker-compose up -d

# 4. 查看日志
docker-compose logs -f
```

**访问地址**: `http://你的服务器 IP` (通过 Nginx)

---

### 方式三：手动部署（适合自定义配置）

详见 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

---

## 验证部署

部署完成后，在浏览器访问：

| 地址 | 说明 |
|------|------|
| `http://你的服务器 IP:8000` | 主界面 |
| `http://你的服务器 IP:8000/api/docs` | API 文档 |
| `http://你的服务器 IP:8000/api/health` | 健康检查 |

---

## 常用命令

### 服务管理
```bash
# 查看状态
sudo systemctl status cmf-scm

# 重启服务
sudo systemctl restart cmf-scm

# 查看日志
sudo journalctl -u cmf-scm -f
```

### Docker 管理
```bash
# 查看容器
docker-compose ps

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f api

# 停止服务
docker-compose down
```

---

## 遇到问题？

1. **端口被占用**: 修改 `.env` 中的 `PORT` 变量
2. **无法访问**: 检查防火墙和安全组是否开放 8000 端口
3. **数据库错误**: 删除 `src/cmf_database.db` 重新启动

详细故障排查请参考 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

---

**祝部署顺利！** 🎉
