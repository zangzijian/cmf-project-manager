# 🚀 CMF SCM 系统 v2.0 - 3 分钟快速部署指南

## 前提条件
- Linux 服务器（Ubuntu/CentOS/Debian）
- Python 3.8+
-  root 权限
- 开放 8000 端口（在云控制台安全组配置）

---

## ⚡ 一键部署（推荐）

```bash
# 步骤 1: 上传部署包
scp -r cmf-scm-v2 root@8.134.33.206:/tmp/

# 步骤 2: SSH 登录服务器
ssh root@8.134.33.206

# 步骤 3: 执行安装脚本
cd /tmp/cmf-scm-v2
chmod +x install.sh
./install.sh
```

**完成！** 服务将自动启动。

---

## ✅ 验证部署

```bash
# 检查服务状态
sudo systemctl status cmf-scm

# 测试健康检查接口
curl http://localhost:8000/api/health

# 查看实时日志
sudo journalctl -u cmf-scm -f
```

---

## 🌐 访问服务

在浏览器中打开：
- **Web 界面**: `http://8.134.33.206:8000/`
- **API 文档**: `http://8.134.33.206:8000/api/docs`

---

## ⚠️ 如果无法访问

### 1. 检查云安全组
登录阿里云控制台 → ECS → 安全组 → 添加入站规则：
- 协议：TCP
- 端口：8000
- 授权对象：0.0.0.0/0

### 2. 检查防火墙
```bash
# Ubuntu
sudo ufw allow 8000/tcp

# CentOS
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 3. 检查端口监听
```bash
sudo ss -tlnp | grep 8000
```
应该看到 uvicorn 在监听 0.0.0.0:8000

### 4. 查看错误日志
```bash
sudo journalctl -u cmf-scm --no-pager -n 50
```

---

## 🔄 常用运维命令

```bash
# 重启服务
sudo systemctl restart cmf-scm

# 停止服务
sudo systemctl stop cmf-scm

# 更新应用
cd /opt/cmf-scm
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart cmf-scm

# 查看日志
sudo journalctl -u cmf-scm -f --since "10 minutes ago"
```

---

## 📦 卸载

```bash
sudo systemctl stop cmf-scm
sudo systemctl disable cmf-scm
sudo rm /etc/systemd/system/cmf-scm.service
sudo systemctl daemon-reload
sudo rm -rf /opt/cmf-scm
```

---

## 💡 提示

- 数据存储在内存中，重启服务会重置数据
- 生产环境建议使用 Nginx 反向代理（见 deploy/nginx.conf）
- 如需持久化数据，可集成 PostgreSQL 数据库
