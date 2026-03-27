# CMF SCM 供应链管理系统 v2.0 - 部署指引

## 📦 发布说明

**版本号**: v2.0.0  
**发布日期**: 2024-03-27  
**版本类型**: 生产就绪版 (Production Ready)

### 核心修复
本版本彻底重构解决了 v1.x 的所有部署问题：

| 问题 | v1.x | v2.0 |
|------|------|------|
| pytz 模块缺失 | ❌ 需要手动安装 | ✅ 完全移除依赖 |
| 相对导入错误 | ❌ ModuleNotFoundError | ✅ 绝对路径 + sys.path 自动修正 |
| 目录结构混乱 | ❌ src/deployment 混用 | ✅ 清晰的 src/ scripts/ 分离 |
| systemd 配置复杂 | ❌ 多文件配置 | ✅ 一键部署脚本 |
| 需要外部数据库 | ❌ PostgreSQL 配置 | ✅ 内置 Mock 数据，开箱即用 |

---

## 🚀 快速部署（3 分钟上线）

### 步骤 1：上传到服务器

在本地执行：
```bash
# 方式 A: scp 上传压缩包
scp cmf-scm-v2.tar.gz root@8.134.33.206:/opt/

# 方式 B: 直接上传整个文件夹
scp -r cmf-scm-v2 root@8.134.33.206:/opt/
```

### 步骤 2：SSH 登录服务器

```bash
ssh root@8.134.33.206
cd /opt
```

### 步骤 3：解压并安装

```bash
# 如果使用压缩包
tar -xzf cmf-scm-v2.tar.gz
cd cmf-scm-v2

# 赋予执行权限
chmod +x install.sh scripts/deploy.sh

# 运行安装脚本（安装 Python 依赖）
./install.sh
```

### 步骤 4A：测试运行（推荐先测试）

```bash
# 激活虚拟环境
source venv/bin/activate

# 进入源码目录
cd src

# 启动服务（单进程模式，便于调试）
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

此时访问 `http://8.134.33.206:8000` 应该能看到界面。

按 `Ctrl+C` 停止测试服务。

### 步骤 4B：正式部署（systemd 服务）

```bash
# 返回项目根目录
cd /opt/cmf-scm-v2

# 运行部署脚本
./scripts/deploy.sh
```

部署成功后，服务将：
- ✅ 自动启动
- ✅ 开机自启
- ✅ 崩溃自动重启
- ✅ 日志记录到 journalctl

---

## 🔍 验证部署

### 检查服务状态
```bash
sudo systemctl status cmf-scm-v2
```

期望输出包含 `active (running)`

### 检查端口监听
```bash
sudo ss -tlnp | grep 8000
```

期望看到 python 进程监听 0.0.0.0:8000

### 健康检查
```bash
curl http://localhost:8000/api/health
```

期望返回：
```json
{"status":"healthy","version":"2.0.0","timestamp":"..."}
```

### 浏览器访问
- 主界面：`http://8.134.33.206:8000`
- API 文档：`http://8.134.33.206:8000/api/docs`

---

## 🔧 故障排查

### 问题 1：服务启动失败

```bash
# 查看详细错误日志
sudo journalctl -u cmf-scm-v2 -n 50 --no-pager
```

常见错误及解决：

**ModuleNotFoundError**: 
```bash
cd /opt/cmf-scm-v2
source venv/bin/activate
pip install -r requirements.txt --break-system-packages
sudo systemctl restart cmf-scm-v2
```

**Port already in use**:
```bash
# 查看占用端口的进程
sudo ss -tlnp | grep 8000
# 停止冲突进程或修改端口
```

### 问题 2：无法访问（连接被拒绝）

**检查防火墙**:
```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow 8000/tcp

# CentOS/RHEL
sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

**检查云安全组**（重要！）:
登录阿里云控制台 → 云服务器 ECS → 安全组 → 添加规则：
- 端口范围：8000/8000
- 授权对象：0.0.0.0/0
- 协议：TCP

### 问题 3：502 Bad Gateway

这通常表示后端服务未正常启动：

```bash
# 1. 检查服务状态
sudo systemctl status cmf-scm-v2

# 2. 如果 inactive，查看日志
sudo journalctl -u cmf-scm-v2 -f

# 3. 手动测试启动
cd /opt/cmf-scm-v2/src
../venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📋 常用运维命令

```bash
# 查看服务状态
sudo systemctl status cmf-scm-v2

# 重启服务
sudo systemctl restart cmf-scm-v2

# 停止服务
sudo systemctl stop cmf-scm-v2

# 启动服务
sudo systemctl start cmf-scm-v2

# 查看实时日志
sudo journalctl -u cmf-scm-v2 -f

# 查看最近 100 行日志
sudo journalctl -u cmf-scm-v2 -n 100 --no-pager

# 禁用开机自启
sudo systemctl disable cmf-scm-v2

# 卸载服务
sudo systemctl stop cmf-scm-v2
sudo systemctl disable cmf-scm-v2
sudo rm /etc/systemd/system/cmf-scm-v2.service
sudo systemctl daemon-reload
sudo rm -rf /opt/cmf-scm-v2
```

---

## 📁 目录结构说明

```
/opt/cmf-scm-v2/
├── src/
│   ├── main.py          # 主应用（433 行，包含所有 API 和 Mock 数据）
│   └── static/          # 前端 HTML 目录
│       └── mainweb.html # 将你的前端文件放在这里
├── scripts/
│   └── deploy.sh        # systemd 部署脚本
├── venv/                # Python 虚拟环境（自动生成）
├── install.sh           # 一键安装脚本
├── requirements.txt     # Python 依赖列表
└── README.md            # 项目说明
```

---

## 🔐 安全建议

1. **生产环境不要使用 root 用户运行服务**
   ```bash
   # 创建专用用户
   sudo useradd -r -s /bin/false cmf-scm
   sudo chown -R cmf-scm:cmf-scm /opt/cmf-scm-v2
   
   # 修改 systemd 服务文件中的 User=cmf-scm
   ```

2. **配置 Nginx 反向代理**（可选，用于 HTTPS 和域名访问）
   
3. **定期备份数据**（如果扩展了数据库）

4. **限制 API 访问**（未来版本将添加认证功能）

---

## 📞 技术支持

如遇到其他问题，请提供以下信息：

1. 操作系统版本：`cat /etc/os-release`
2. Python 版本：`python3 --version`
3. 服务状态：`sudo systemctl status cmf-scm-v2`
4. 错误日志：`sudo journalctl -u cmf-scm-v2 -n 100`

---

## 📝 版本历史

### v2.0.0 (2024-03-27)
- ✅ 彻底重构，单文件架构
- ✅ 移除 pytz 等外部依赖
- ✅ 内置 sys.path 自动修正
- ✅ 内置 Mock 数据，无需数据库
- ✅ 一键安装和部署脚本
- ✅ 完整的故障排查文档

### v1.x (已废弃)
- ❌ 存在多个部署问题
- ❌ 需要手动修复依赖
- ❌ 不推荐使用

---

**祝你部署顺利！** 🎉
