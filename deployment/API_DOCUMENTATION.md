# CMF 供应链项目管理系统 - API 接口文档

## 概述

本文档描述了 CMF 供应链管理系统的 RESTful API 接口。所有接口返回 JSON 格式数据。

**基础 URL**: `http://localhost:8000/api`

---

## 1. 系统接口

### 1.1 获取服务器时间

**GET** `/system/time`

获取服务器标准时间，用于前端校准时间指示器。

**响应示例**:
```json
{
  "server_time": "2023-10-24T14:30:00+08:00",
  "timezone": "Asia/Shanghai"
}
```

---

## 2. 仪表盘接口

### 2.1 获取看板首页数据

**GET** `/dashboard/overview`

聚合项目列表、统计数字、今日任务。

**响应示例**:
```json
{
  "total_projects": 2,
  "ongoing_projects": 2,
  "high_risk_parts": 1,
  "today_tasks": 2,
  "pending_tasks": 3,
  "projects": [
    {
      "id": "proj-x1-001",
      "code": "PJ-2023-X1",
      "name": "Flagship Phone Unibody",
      "current_stage": "T1",
      "overall_status": "HIGH",
      "pm": {
        "id": "user-alex-001",
        "name": "Alex Chen",
        "avatar_initial": "A"
      },
      "parts": [
        {
          "id": "part-x1-001",
          "name": "A 面铝合金中框",
          "structure": "CNC + 阳极氧化",
          "risk_level": "HIGH",
          "risk_type": "DELAY",
          "progress_note": "模具修改中，预计延期 3 天",
          "suppliers": [
            {"id": "sup-001", "name": "Foxconn", "type": "PRIMARY"},
            {"id": "sup-002", "name": "Luxshare", "type": "SECONDARY"}
          ]
        }
      ],
      "milestones": [
        {
          "id": "ms-x1-003",
          "stage": "T1",
          "planned_date": "2023-10-20T00:00:00Z",
          "status": "completed"
        }
      ]
    }
  ],
  "tasks": [
    {
      "id": "task-001",
      "title": "确认 A 面中框阳极色差限度样",
      "priority": "P0",
      "due_date": "2023-10-24T14:00:00Z",
      "status": "PENDING",
      "assignees": [
        {"id": "user-alex-001", "name": "Alex Chen", "avatar_initial": "A"}
      ]
    }
  ]
}
```

---

## 3. 项目管理接口

### 3.1 获取所有项目

**GET** `/projects`

**响应示例**:
```json
[
  {
    "id": "proj-x1-001",
    "code": "PJ-2023-X1",
    "name": "Flagship Phone Unibody",
    "current_stage": "T1",
    "overall_status": "HIGH",
    "pm_id": "user-alex-001"
  }
]
```

### 3.2 获取单个项目详情

**GET** `/projects/{project_id}`

包含部件列表、时间轴（里程碑）。

**响应示例**:
```json
{
  "id": "proj-x1-001",
  "code": "PJ-2023-X1",
  "name": "Flagship Phone Unibody",
  "description": "旗舰手机一体化机身项目",
  "current_stage": "T1",
  "overall_status": "HIGH",
  "pm": {
    "id": "user-alex-001",
    "email": "alex.chen@cmf.com",
    "name": "Alex Chen",
    "avatar_initial": "A"
  },
  "parts": [
    {
      "id": "part-x1-001",
      "name": "A 面铝合金中框",
      "structure": "CNC + 阳极氧化",
      "risk_level": "HIGH",
      "risk_type": "DELAY",
      "progress_note": "模具修改中，预计延期 3 天",
      "suppliers": [
        {"id": "sup-001", "name": "Foxconn", "type": "PRIMARY"},
        {"id": "sup-002", "name": "Luxshare", "type": "SECONDARY"}
      ]
    }
  ],
  "milestones": [
    {"stage": "PROTOTYPE", "planned_date": "2023-09-01", "status": "completed"},
    {"stage": "T1", "planned_date": "2023-10-20", "status": "completed"},
    {"stage": "T2", "planned_date": "2023-11-15", "status": "pending"},
    {"stage": "DVT", "planned_date": "2023-12-01", "status": "pending"},
    {"stage": "PVT", "planned_date": "2024-01-10", "status": "pending"},
    {"stage": "MP", "planned_date": "2024-02-01", "status": "pending"}
  ],
  "tasks": []
}
```

### 3.3 创建新项目

**POST** `/projects`

对应前端悬浮按钮 (+) 功能。

**请求体**:
```json
{
  "code": "PJ-2024-A1",
  "name": "New Product Development",
  "description": "新产品开发项目",
  "current_stage": "PROTOTYPE",
  "overall_status": "LOW",
  "pm_id": "user-alex-001",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-06-01T00:00:00Z"
}
```

**成功响应 (201)**:
```json
{
  "id": "proj-new-001",
  "code": "PJ-2024-A1",
  "name": "New Product Development",
  "current_stage": "PROTOTYPE",
  "overall_status": "LOW",
  "pm_id": "user-alex-001"
}
```

**错误响应 (400)**:
```json
{
  "message": "项目代号已存在",
  "success": false
}
```

---

## 4. 部件管理接口

### 4.1 更新部件风险状态

**PATCH** `/parts/{part_id}/status`

更新部件风险状态或进度备注，同时记录风险变更日志。

**请求体**:
```json
{
  "risk_level": "MEDIUM",
  "risk_type": "PROCESS",
  "progress_note": "新工艺验证中"
}
```

**响应示例**:
```json
{
  "id": "part-x1-001",
  "name": "A 面铝合金中框",
  "risk_level": "MEDIUM",
  "risk_type": "PROCESS",
  "progress_note": "新工艺验证中",
  "suppliers": [...]
}
```

---

## 5. 任务管理接口

### 5.1 获取任务列表

**GET** `/tasks?project_id={id}&status={status}`

支持按项目和状态筛选。

**查询参数**:
- `project_id` (可选): 项目 ID
- `status` (可选): PENDING, IN_PROGRESS, COMPLETED, CANCELLED

**响应示例**:
```json
[
  {
    "id": "task-001",
    "title": "确认 A 面中框阳极色差限度样",
    "priority": "P0",
    "due_date": "2023-10-24T14:00:00Z",
    "status": "PENDING",
    "assignees": [
      {"id": "user-alex-001", "name": "Alex Chen", "avatar_initial": "A"}
    ]
  }
]
```

### 5.2 创建新任务

**POST** `/tasks`

**请求体**:
```json
{
  "title": "审核新工艺报告",
  "description": "审核供应商提交的新工艺可行性报告",
  "priority": "P1",
  "due_date": "2023-10-25T17:00:00Z",
  "project_id": "proj-x1-001",
  "assignee_ids": ["user-alex-001", "user-sarah-002"]
}
```

**响应示例**:
```json
{
  "id": "task-new-001",
  "title": "审核新工艺报告",
  "priority": "P1",
  "status": "PENDING",
  "assignees": [...]
}
```

### 5.3 删除任务

**DELETE** `/tasks/{task_id}`

对应前端垃圾桶按钮 (.delete-btn) 功能。

**成功响应 (200)**:
```json
{
  "message": "任务已删除",
  "success": true
}
```

**错误响应 (404)**:
```json
{
  "message": "任务不存在",
  "success": false
}
```

### 5.4 更新任务

**PATCH** `/tasks/{task_id}`

**请求体**:
```json
{
  "status": "COMPLETED",
  "completed_at": "2023-10-24T15:00:00Z"
}
```

---

## 6. 用户管理接口

### 6.1 获取所有用户

**GET** `/users`

**响应示例**:
```json
[
  {
    "id": "user-alex-001",
    "email": "alex.chen@cmf.com",
    "name": "Alex Chen",
    "avatar_initial": "A",
    "role": "PM"
  }
]
```

---

## 7. 枚举值说明

### 项目阶段 (ProjectStage)
| 值 | 说明 |
|---|---|
| PROTOTYPE | 手板/原型 |
| T0 | 第一次试模 |
| T1 | 第二次试模 |
| T2 | 第三次试模 |
| EVT | 工程验证测试 |
| DVT | 设计验证测试 |
| PVT | 生产验证测试 |
| MP | 量产 |

### 风险等级 (RiskLevel)
| 值 | 前端颜色 | 说明 |
|---|---|---|
| LOW | 绿色 (#10b981) | 低风险 |
| MEDIUM | 黄色 (#f59e0b) | 中风险 |
| HIGH | 红色 (#ef4444) | 高风险 |
| CRITICAL | 深红色 | 严重风险 |

### 风险类型 (RiskType)
| 值 | 说明 |
|---|---|
| DELAY | 延期风险 |
| PROCESS | 工艺风险 |
| YIELD | 良率风险 |
| COST | 成本风险 |
| QUALITY | 质量风险 |
| SUPPLY | 供应风险 |

### 任务优先级 (TaskPriority)
| 值 | 说明 | 前端边框颜色 |
|---|---|---|
| P0 | 紧急 - 立即处理 | 红色 |
| P1 | 重要 - 今天处理 | 黄色 |
| P2 | 常规 - 本周处理 | 青色 |
| P3 | 低优 - 可延后 | 灰色 |

---

## 8. 错误码说明

| HTTP 状态码 | 说明 |
|---|---|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 9. Swagger/OpenAPI 文档

启动服务后访问：
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
