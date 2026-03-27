# CMF 供应链管理系统 - Linux 云服务器部署指南

## 📋 目录

1. [系统要求](#系统要求)
2. [快速部署（推荐）](#快速部署推荐)
3. [手动部署](#手动部署)
4. [配置说明](#配置说明)
5. [服务管理](#服务管理)
6. [故障排查](#故障排查)
7. [安全加固](#安全加固)

---

## 系统要求

### 最低配置
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **CPU**: 1 核
- **内存**: 512MB
- **磁盘**: 2GB 可用空间
- **网络**: 开放端口 8000

### 推荐配置
- **操作系统**: Ubuntu 22.04 LTS
- **CPU**: 2 核
- **内存**: 2GB
- **磁盘**: 10GB SSD
- **网络**: 开放端口 80 (Nginx 反向代理) + 8000

---

## 快速部署（推荐）

### 步骤 1: 上传项目文件

**方式 A: 使用 SCP**
```bash
# 在本地电脑执行
scp -r /workspace/deployment root@你的服务器IP:/opt/cmf-scm
```

**方式 B: 使用 Git**
```bash
# 在服务器上执行
git clone <你的代码仓库地址> /opt/cmf-scm
cd /opt/cmf-scm
```

**方式 C: 使用 FTP/SFTP 工具**
- 使用 FileZilla、WinSCP 等工具上传整个 `deployment` 文件夹到 `/opt/cmf-scm`

### 步骤 2: 执行一键部署脚本

```bash
# SSH 登录服务器
ssh root@你的服务器IP

# 进入项目目录
cd /opt/cmf-scm

# 赋予执行权限
chmod +x deploy.sh

# 执行部署脚本
./deploy.sh
```

### 步骤 3: 验证部署

部署完成后，脚本会显示访问地址：
```
========================================
🎉 部署完成！
========================================

访问方式:
  本地访问：http://localhost:8000
  远程访问：http://YOUR_SERVER_IP:8000
  API 文档：http://YOUR_SERVER_IP:8000/api/docs
```

在浏览器中访问：`http://你的服务器 IP:8000`

---

## 手动部署

如果自动脚本无法运行，请按以下步骤手动部署：

### 1. 安装系统依赖

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl
```

**CentOS/RHEL:**
```bash
sudo yum install -y python3 python3-pip git curl
# 如果 python3-venv 不可用
sudo yum install -y python3-devel
```

### 2. 创建应用目录和虚拟环境

```bash
# 创建目录
sudo mkdir -p /opt/cmf-scm
sudo chown $USER:$USER /opt/cmf-scm
cd /opt/cmf-scm

# 复制项目文件（如果还没复制）
cp -r /path/to/deployment/* .

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

### 3. 安装 Python 依赖

```bash
# 升级 pip
pip install --upgrade pip

# 安装依赖包
pip install fastapi uvicorn[standard] sqlalchemy pydantic \
    pydantic-settings psycopg2-binary python-multipart aiosqlite
```

### 4. 配置环境变量

```bash
# 创建 .env 文件
cat > .env << EOF
HOST=0.0.0.0
PORT=8000
WORKERS=2
DATABASE_MODE=sqlite
DATABASE_URL=sqlite:///./cmf_database.db
SECRET_KEY=change-this-to-a-random-secret-key
LOG_LEVEL=info
EOF
```

### 5. 初始化数据库

```bash
cd src
python -c "from models import Base, engine; Base.metadata.create_all(bind=engine)"
python -c "from mock_data import seed_database; seed_database()"
cd ..
```

### 6. 启动服务

**开发模式（前台运行）:**
```bash
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**生产模式（后台运行）:**
```bash
nohup bash -c 'source venv/bin/activate && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 2' > app.log 2>&1 &
```

---

## 配置说明

### 环境变量 (.env 文件)

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| HOST | 监听地址 | 0.0.0.0 | 0.0.0.0 |
| PORT | 监听端口 | 8000 | 8000 |
| WORKERS | 工作进程数 | 2 | 4 |
| DATABASE_MODE | 数据库模式 | sqlite | postgresql |
| DATABASE_URL | 数据库连接串 | sqlite:///./cmf_database.db | postgresql://user:pass@localhost/cmf_db |
| SECRET_KEY | 安全密钥 | (必须修改) | your-secret-key-here |
| LOG_LEVEL | 日志级别 | info | debug/error |
| USE_REDIS | 是否启用 Redis | false | true |
| REDIS_URL | Redis 连接串 | redis://localhost:6379/0 | redis://redis-server:6379/1 |

### 数据库配置

**SQLite (开发/演示):**
```env
DATABASE_MODE=sqlite
DATABASE_URL=sqlite:///./cmf_database.db
```

**PostgreSQL (生产环境):**
```env
DATABASE_MODE=postgresql
DATABASE_URL=postgresql://cmf_user:your_password@localhost:5432/cmf_db
```

安装 PostgreSQL:
```bash
# Ubuntu
sudo apt install postgresql postgresql-contrib

# 创建数据库和用户
sudo -u postgres psql
CREATE DATABASE cmf_db;
CREATE USER cmf_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE cmf_db TO cmf_user;
\q
```

---

## 服务管理

### 使用 systemd 管理（推荐）

如果部署脚本已配置 systemd 服务：

```bash
# 查看服务状态
sudo systemctl status cmf-scm

# 启动服务
sudo systemctl start cmf-scm

# 停止服务
sudo systemctl stop cmf-scm

# 重启服务
sudo systemctl restart cmf-scm

# 开机自启
sudo systemctl enable cmf-scm

# 禁用自启
sudo systemctl disable cmf-scm

# 查看实时日志
sudo journalctl -u cmf-scm -f
```

### 使用 PM2 管理（可选）

```bash
# 安装 PM2
npm install -g pm2

# 启动应用
pm2 start "python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 2" --name cmf-scm

# 查看状态
pm2 status

# 查看日志
pm2 logs cmf-scm

# 重启
pm2 restart cmf-scm

# 开机自启
pm2 startup
pm2 save
```

---

## 防火墙配置

### Ubuntu (UFW)
```bash
sudo ufw allow 8000/tcp
sudo ufw reload
sudo ufw status
```

### CentOS (firewalld)
```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports
```

### 云服务器安全组

**阿里云/腾讯云/华为云:**
1. 登录云服务器控制台
2. 找到实例 → 安全组
3. 添加入站规则：
   - 协议：TCP
   - 端口：8000
   - 授权对象：0.0.0.0/0 (或指定 IP)

---

## 故障排查

### 1. 服务无法启动

**检查端口占用:**
```bash
sudo lsof -i :8000
sudo netstat -tlnp | grep 8000
```

**解决:**
```bash
# 杀死占用端口的进程
sudo kill -9 <PID>

# 或修改端口
echo "PORT=8001" >> .env
```

### 2. 数据库错误

**检查数据库文件权限:**
```bash
ls -la src/cmf_database.db
chmod 644 src/cmf_database.db
```

**重新初始化数据库:**
```bash
cd src
rm -f cmf_database.db
python -c "from models import Base, engine; Base.metadata.create_all(bind=engine)"
python -c "from mock_data import seed_database; seed_database()"
```

### 3. 依赖安装失败

**更新 pip:**
```bash
source venv/bin/activate
pip install --upgrade pip setuptools wheel
```

**使用国内镜像:**
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 查看应用日志

```bash
# systemd 日志
sudo journalctl -u cmf-scm -n 100 --no-pager

# 应用日志 (如果使用 nohup)
tail -f app.log

# FastAPI 日志
sudo journalctl -u cmf-scm -f | grep -i error
```

### 5. 内存不足

**添加 Swap 分区:**
```bash
# 创建 2GB swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久生效
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 安全加固

### 1. 修改默认端口

```env
# .env 文件
PORT=8443
```

### 2. 使用 Nginx 反向代理

安装 Nginx:
```bash
sudo apt install nginx
```

配置 Nginx:
```nginx
# /etc/nginx/sites-available/cmf-scm
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持 (如果需要)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 静态文件缓存
    location /static {
        alias /opt/cmf-scm/static;
        expires 30d;
    }
}
```

启用配置:
```bash
sudo ln -s /etc/nginx/sites-available/cmf-scm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. 配置 HTTPS (Let's Encrypt)

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

### 4. 限制 API 访问

在 `.env` 中配置 API Key:
```env
API_KEY_REQUIRED=true
API_KEY=your-secret-api-key
```

### 5. 定期备份

创建备份脚本 `/opt/cmf-scm/backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/cmf-scm"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp /opt/cmf-scm/src/cmf_database.db $BACKUP_DIR/cmf_db_$DATE.db
tar -czf $BACKUP_DIR/cmf_backup_$DATE.tar.gz /opt/cmf-scm/src/*.db

# 保留最近 7 天的备份
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

设置定时任务:
```bash
crontab -e
# 每天凌晨 2 点备份
0 2 * * * /opt/cmf-scm/backup.sh
```

---

## 性能优化

### 1. 调整 Worker 数量

根据 CPU 核心数调整:
```env
WORKERS=4  # 建议：CPU 核心数 * 2 + 1
```

### 2. 启用 Gzip 压缩

Nginx 配置:
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml;
```

### 3. 配置 Redis 缓存

```bash
# 安装 Redis
sudo apt install redis-server

# 配置 .env
USE_REDIS=true
REDIS_URL=redis://localhost:6379/0
```

---

## 常见问题 FAQ

**Q: 访问时出现 403 Forbidden?**
A: 检查防火墙和安全组是否开放了 8000 端口。

**Q: 数据库锁定错误？**
A: SQLite 不支持高并发写入，生产环境请切换到 PostgreSQL。

**Q: 如何更新代码？**
A: 
```bash
cd /opt/cmf-scm
git pull  # 如果使用 Git
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart cmf-scm
```

**Q: 如何重置数据库？**
A:
```bash
cd /opt/cmf-scm/src
rm -f cmf_database.db
python -c "from models import Base, engine; Base.metadata.create_all(bind=engine)"
python -c "from mock_data import seed_database; seed_database()"
sudo systemctl restart cmf-scm
```

---

## 技术支持

如有问题，请提供以下信息：
1. 操作系统版本：`cat /etc/os-release`
2. Python 版本：`python3 --version`
3. 错误日志：`sudo journalctl -u cmf-scm -n 50`
4. 服务状态：`sudo systemctl status cmf-scm`

---

**祝您部署顺利！** 🚀
