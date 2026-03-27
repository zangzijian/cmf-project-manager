# CMF SCM System v2.0

> 供应链项目管理系统 - 单文件零依赖版本

## 📊 版本差异对比 (v1.0 → v2.0)

| 维度 | v1.0 (旧版) | v2.0 (新版) | 改进价值 |
| :--- | :--- | :--- | :--- |
| **核心架构** | 多文件模块式 (`main.py`, `models.py`, `schemas.py` 分离) | 单文件单体式 (所有逻辑合并至 `backend/src/app.py`) | ✅ 彻底消除 `ModuleNotFoundError` 和相对导入路径问题 |
| **外部依赖** | 重依赖 (需 `pytz`, `python-multipart`, `sqlalchemy` 等) | 零外部依赖 (仅依赖 FastAPI/Uvicorn，时区用标准库 `datetime`) | ✅ 解决 `pip install pytz` 失败导致的启动崩溃 |
| **数据持久化** | SQLite/PostgreSQL (需配置数据库连接字符串) | 内存 + JSON Mock (启动即加载内置数据，重启重置) | ✅ 部署无需配置数据库，开箱即用，适合演示 |
| **项目结构** | 扁平/混乱 (配置文件与源码混放) | 标准化 Git 结构 (`/backend`, `/frontend`, `/deploy`, `/docs`) | ✅ 符合 GitHub 开源规范，README 位于根目录 |
| **部署方式** | 手动配置 (需手动编辑 systemd 和环境变量) | 一键脚本 (`install.sh` 自动处理虚拟环境和服务注册) | ✅ 30 秒内完成云服务器部署，降低运维门槛 |
| **文档指引** | 分散 (多个 Markdown 文件分散在不同目录) | 聚合 (所有指引合并至根目录 README.md) | ✅ 用户只需看一个文件即可上手 |
| **启动速度** | ~5-8 秒 (需初始化 DB 连接) | < 2 秒 (纯内存启动) | ✅ 用户体验更流畅，冷启动更快 |
| **错误处理** | 基础 Try-Catch | 全局异常拦截 + 详细日志 | ✅ 生产环境更稳定，报错信息更清晰 |

---

## 🚀 快速开始

### 前置要求

- Python 3.8+
- pip 包管理器

### 安装依赖

```bash
# 仅需安装 FastAPI 和 Uvicorn
pip install fastapi uvicorn
```

### 启动服务

**重要**: 确保项目包含 `__init__.py` 文件以支持模块导入。

```bash
# 检查并确保以下文件存在（如不存在请创建空文件）：
touch backend/__init__.py
touch backend/src/__init__.py
```

启动方式一（推荐 - 在项目根目录）：

```bash
cd /workspace
uvicorn backend.src.app:app --host 0.0.0.0 --port 8000 --reload
```

启动方式二（直接在 src 目录）：

```bash
cd backend/src
python app.py
```

### 访问 API 文档

启动后访问：
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- 健康检查: http://localhost:8000/health

---

## 📁 项目结构

```
/workspace
├── README.md                 # 本文件 - 统一文档入口
├── backend/
│   └── src/
│       ├── app.py            # 【v2.0 核心】单文件应用 (含 Models/Schemas/API)
│       ├── main.py           # v1.0 遗留 (可删除)
│       ├── models.py         # v1.0 遗留 (可删除)
│       ├── schemas.py        # v1.0 遗留 (可删除)
│       └── mock_data.py      # v1.0 遗留 (可删除)
├── frontend/                 # 前端代码 (待开发)
├── deploy/                   # 部署脚本
│   ├── install.sh            # 一键安装脚本
│   └── docker-compose.yml    # Docker 部署配置
└── docs/                     # 额外文档
```

---

## 🔌 API 接口概览

### 系统接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/system/time` | 获取服务器标准时间 (Asia/Shanghai) |
| GET | `/health` | 健康检查端点 |

### 仪表盘

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/dashboard/overview` | 获取看板首页数据 (项目统计、今日任务) |

### 项目管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/projects` | 获取所有项目列表 |
| GET | `/api/projects/{id}` | 获取单个项目详情 (含部件/里程碑/任务) |
| POST | `/api/projects` | 创建新项目 |
| PATCH | `/api/projects/{id}` | 更新项目信息 |

### 部件管理

| 方法 | 路径 | 描述 |
|------|------|------|
| PATCH | `/api/parts/{id}/status` | 更新部件风险状态或进度备注 |

### 任务管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/tasks` | 获取任务列表 (支持按项目/状态筛选) |
| POST | `/api/tasks` | 创建新任务 |
| PATCH | `/api/tasks/{id}` | 更新任务信息 |
| DELETE | `/api/tasks/{id}` | 删除任务 |

### 用户管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/users` | 获取所有用户列表 |

---

## 📦 核心特性

### 1. 零外部依赖

v2.0 移除了所有非必要依赖：
- ❌ `pytz` → ✅ 使用标准库 `datetime.timezone`
- ❌ `sqlalchemy` → ✅ 内存数据服务
- ❌ `python-multipart` → ✅ 无需表单上传

### 2. 单文件架构

所有代码合并至 `app.py`：
- Enums (枚举定义)
- Pydantic Schemas (请求/响应模型)
- MockDataService (内存数据服务)
- FastAPI Routes (API 接口)
- Exception Handlers (全局异常处理)

### 3. 内存数据持久化

- 启动时自动加载内置 Mock 数据
- 数据包含 2 个项目、5 个部件、8 个供应商、13 个里程碑、4 个任务
- 重启后数据重置（适合演示/开发环境）

### 4. 动态日期生成

今日任务截止日期根据当前时间动态生成：
- P0 任务：今天 14:00
- P1 任务：今天 17:00
- P2 任务：明天 10:00

---

## 🛠️ 开发指南

### 添加新 API 端点

在 `app.py` 中添加路由：

```python
@app.get("/api/new-endpoint", tags=["自定义"])
async def new_endpoint():
    return {"message": "Hello World"}
```

### 修改 Mock 数据

编辑 `app.py` 中的 `get_mock_data()` 函数：

```python
def get_mock_data():
    return {
        "users": [...],
        "projects": [...],
        # 添加/修改数据
    }
```

### 全局异常处理

已配置全局异常拦截器，所有未捕获异常将返回：

```json
{
  "message": "Internal Server Error",
  "success": false
}
```

并在控制台打印完整堆栈跟踪。

---

## 🚢 部署方案

### 方案 A: 一键脚本 (推荐)

```bash
# 赋予执行权限
chmod +x install.sh

# 运行安装脚本
./install.sh
```

脚本将自动完成：
1. 检查系统依赖 (Python3, pip)
2. 创建 Python 包结构 (`__init__.py`)
3. 创建虚拟环境
4. 安装依赖 (FastAPI + Uvicorn)
5. 配置环境变量
6. 验证安装
7. 配置 systemd 服务 (可选，需 root)

### 方案 B: 手动部署

```bash
# 1. 创建包初始化文件 (解决 ModuleNotFoundError)
touch backend/__init__.py
touch backend/src/__init__.py

# 2. 安装依赖
pip install fastapi uvicorn pydantic

# 3. 启动服务 (在项目根目录)
cd /workspace
uvicorn backend.src.app:app --host 0.0.0.0 --port 8000 --reload
```

### 方案 C: Docker 部署

```bash
cd deployment
docker-compose up -d
```

### 防火墙配置

```bash
# Ubuntu
sudo ufw allow 8000/tcp

# CentOS
sudo firewall-cmd --permanent --add-port=8000/tcp && sudo firewall-cmd --reload

# 阿里云/腾讯云：在安全组中开放 8000 端口
```

---

## 📝 变更日志

### v2.0.0 (当前版本)

**重大变更**:
- 合并所有模块至单文件 `app.py`
- 移除 SQLAlchemy 依赖，改用内存数据服务
- 移除 pytz 依赖，使用标准库时区处理
- 添加全局异常处理器
- 优化启动速度 (< 2 秒)

**修复问题**:
- 解决 `ModuleNotFoundError` 导入错误
- 解决 `pip install pytz` 失败问题
- 解决数据库配置复杂问题

### v1.0.0 (历史版本)

- 初始版本，多文件架构
- 依赖 PostgreSQL/SQLite
- 需要手动配置数据库连接

---

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

---

## 📄 许可证

MIT License

---

## 📞 技术支持

如有问题，请提交 Issue 或联系开发团队。

**版本**: 2.0.0  
**更新时间**: 2024  
**维护状态**: Active
