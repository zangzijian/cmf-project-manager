"""
CMF 供应链项目管理系统 - FastAPI 单文件应用 (v2.0)
所有逻辑合并至此文件，消除模块导入问题
零外部依赖（仅 FastAPI/Uvicorn），内存+JSON Mock 数据持久化
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
import copy
import uuid
import json
import os

# ============================================
# 枚举定义
# ============================================

class ProjectStage(str, Enum):
    KV = "KV"
    EVT = "EVT"
    DVT = "DVT"
    PVT = "PVT"
    MP = "MP"
    PROTOTYPE = "PROTOTYPE"
    T0 = "T0"
    T1 = "T1"
    T2 = "T2"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskType(str, Enum):
    DELAY = "DELAY"
    PROCESS = "PROCESS"
    YIELD = "YIELD"
    COST = "COST"
    QUALITY = "QUALITY"
    SUPPLY = "SUPPLY"


class TaskPriority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class SupplierType(str, Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    PM = "PM"
    ENGINEER = "ENGINEER"
    SUPPLIER = "SUPPLIER"


# ============================================
# Pydantic Schemas (请求/响应模型)
# ============================================

class UserBase(BaseModel):
    email: str = Field(..., description="邮箱地址")
    name: str = Field(..., description="姓名")
    avatar_initial: Optional[str] = Field(None, description="头像首字母")
    role: UserRole = Field(default=UserRole.PM, description="角色")


class UserResponse(UserBase):
    id: str
    created_at: str
    updated_at: str
    model_config = ConfigDict(from_attributes=True)


class SupplierBase(BaseModel):
    name: str = Field(..., description="供应商名称")
    type: SupplierType = Field(default=SupplierType.PRIMARY, description="供应商类型")


class SupplierResponse(SupplierBase):
    id: str
    part_id: str
    created_at: str
    updated_at: str
    model_config = ConfigDict(from_attributes=True)


class PartBase(BaseModel):
    name: str = Field(..., description="部件名称")
    structure: Optional[str] = Field(None, description="结构描述")
    process: Optional[str] = Field(None, description="工艺说明")
    risk_level: RiskLevel = Field(default=RiskLevel.LOW, description="风险等级")
    risk_type: Optional[RiskType] = Field(None, description="风险类型")
    progress_note: Optional[str] = Field(None, description="进度备注")
    is_critical: bool = Field(default=False, description="是否关键部件")


class PartUpdate(BaseModel):
    risk_level: Optional[RiskLevel] = None
    progress_note: Optional[str] = None
    actual_date: Optional[str] = None


class PartResponse(PartBase):
    id: str
    project_id: str
    actual_date: Optional[str] = None
    created_at: str
    updated_at: str
    suppliers: List[SupplierResponse] = []
    model_config = ConfigDict(from_attributes=True)


class MilestoneBase(BaseModel):
    stage: ProjectStage = Field(..., description="阶段类型")
    planned_date: str = Field(..., description="计划日期")
    actual_date: Optional[str] = Field(None, description="实际日期")
    status: str = Field(default="pending", description="状态")
    notes: Optional[str] = Field(None, description="备注")


class MilestoneResponse(MilestoneBase):
    id: str
    project_id: str
    created_at: str
    updated_at: str
    model_config = ConfigDict(from_attributes=True)


class TaskAssigneeResponse(BaseModel):
    id: str
    name: str
    avatar_initial: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    title: str = Field(..., description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    priority: TaskPriority = Field(default=TaskPriority.P2, description="优先级")
    due_date: str = Field(..., description="截止时间")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="状态")


class TaskCreate(TaskBase):
    project_id: Optional[str] = Field(None, description="关联项目 ID")
    assignee_ids: List[str] = Field(default=[], description="指派人 ID 列表")


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[str] = None
    status: Optional[TaskStatus] = None
    assignee_ids: Optional[List[str]] = None


class TaskResponse(TaskBase):
    id: str
    project_id: Optional[str]
    assignees: List[TaskAssigneeResponse] = []
    completed_at: Optional[str] = None
    created_at: str
    updated_at: str
    model_config = ConfigDict(from_attributes=True)


class ProjectBase(BaseModel):
    code: str = Field(..., description="项目代号")
    name: str = Field(..., description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    current_stage: ProjectStage = Field(default=ProjectStage.PROTOTYPE, description="当前阶段")
    overall_status: RiskLevel = Field(default=RiskLevel.LOW, description="整体风险状态")
    pm_id: str = Field(..., description="项目经理 ID")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    current_stage: Optional[ProjectStage] = None
    overall_status: Optional[RiskLevel] = None
    pm_id: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: str
    pm: UserResponse
    parts: List[PartResponse] = []
    milestones: List[MilestoneResponse] = []
    tasks: List[TaskResponse] = []
    created_at: str
    updated_at: str
    model_config = ConfigDict(from_attributes=True)


class DashboardOverview(BaseModel):
    total_projects: int
    ongoing_projects: int
    high_risk_parts: int
    today_tasks: int
    pending_tasks: int
    projects: List[ProjectResponse]
    tasks: List[TaskResponse]


class SystemTimeResponse(BaseModel):
    server_time: str
    timezone: str = "Asia/Shanghai"


class MessageResponse(BaseModel):
    message: str
    success: bool = True


# ============================================
# Mock 数据服务 (内存持久化)
# ============================================

def get_mock_data():
    """获取内置 Mock 数据"""
    now = datetime.now()
    today_14 = now.replace(hour=14, minute=0, second=0, microsecond=0)
    today_17 = now.replace(hour=17, minute=0, second=0, microsecond=0)
    tomorrow_10 = (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    
    return {
        "users": [
            {"id": "user-alex-001", "email": "alex.chen@cmf.com", "name": "Alex Chen", "avatar_initial": "A", "role": "PM", "created_at": "2023-01-01T00:00:00Z", "updated_at": "2023-01-01T00:00:00Z"},
            {"id": "user-sarah-002", "email": "sarah.li@cmf.com", "name": "Sarah Li", "avatar_initial": "S", "role": "PM", "created_at": "2023-01-01T00:00:00Z", "updated_at": "2023-01-01T00:00:00Z"}
        ],
        "projects": [
            {"id": "proj-x1-001", "code": "PJ-2023-X1", "name": "Flagship Phone Unibody", "description": "旗舰手机一体化机身项目", "current_stage": "T1", "overall_status": "HIGH", "pm_id": "user-alex-001", "start_date": "2023-09-01T00:00:00Z", "end_date": "2024-02-01T00:00:00Z", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-10-24T00:00:00Z"},
            {"id": "proj-w2-002", "code": "PJ-2023-W2", "name": "Smart Watch Band - Leather", "description": "智能手表真皮表带项目", "current_stage": "DVT", "overall_status": "LOW", "pm_id": "user-sarah-002", "start_date": "2023-08-01T00:00:00Z", "end_date": "2024-01-15T00:00:00Z", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-10-24T00:00:00Z"}
        ],
        "parts": [
            {"id": "part-x1-001", "project_id": "proj-x1-001", "name": "A 面铝合金中框", "structure": "CNC + 阳极氧化", "process": "CNC 精密加工 + 阳极氧化表面处理", "risk_level": "HIGH", "risk_type": "DELAY", "progress_note": "模具修改中，预计延期 3 天", "is_critical": True, "actual_date": None, "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-10-24T00:00:00Z"},
            {"id": "part-x1-002", "project_id": "proj-x1-001", "name": "摄像头装饰圈", "structure": "PVD 镀膜", "process": "物理气相沉积镀膜工艺", "risk_level": "MEDIUM", "risk_type": "PROCESS", "progress_note": "新颜色样板确认中", "is_critical": False, "actual_date": None, "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-10-24T00:00:00Z"},
            {"id": "part-x1-003", "project_id": "proj-x1-001", "name": "玻璃后盖 (AG)", "structure": "热弯 + 丝印", "process": "热弯成型 + 丝网印刷", "risk_level": "LOW", "risk_type": None, "progress_note": "首批样品已签收", "is_critical": True, "actual_date": None, "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-10-24T00:00:00Z"},
            {"id": "part-w2-001", "project_id": "proj-w2-002", "name": "真皮表带 (小牛皮)", "structure": "缝制 + 油边", "process": "手工缝制 + 精细油边", "risk_level": "LOW", "risk_type": None, "progress_note": "大货生产进行中", "is_critical": True, "actual_date": None, "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-10-24T00:00:00Z"},
            {"id": "part-w2-002", "project_id": "proj-w2-002", "name": "不锈钢扣具", "structure": "316L 精铸 + 抛光", "process": "精密铸造 + 镜面抛光", "risk_level": "LOW", "risk_type": None, "progress_note": "等待表面处理确认", "is_critical": False, "actual_date": None, "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-10-24T00:00:00Z"}
        ],
        "suppliers": [
            {"id": "sup-001", "part_id": "part-x1-001", "name": "Foxconn", "type": "PRIMARY", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
            {"id": "sup-002", "part_id": "part-x1-001", "name": "Luxshare", "type": "SECONDARY", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
            {"id": "sup-003", "part_id": "part-x1-002", "name": "BYD", "type": "PRIMARY", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
            {"id": "sup-004", "part_id": "part-x1-003", "name": "Lens Tech", "type": "PRIMARY", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
            {"id": "sup-005", "part_id": "part-x1-003", "name": "Biel", "type": "SECONDARY", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
            {"id": "sup-006", "part_id": "part-w2-001", "name": "Hermès Supplier A", "type": "PRIMARY", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-08-01T00:00:00Z"},
            {"id": "sup-007", "part_id": "part-w2-001", "name": "Local Leather Co.", "type": "SECONDARY", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-08-01T00:00:00Z"},
            {"id": "sup-008", "part_id": "part-w2-002", "name": "Shenzhen Metal", "type": "PRIMARY", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-08-01T00:00:00Z"}
        ],
        "milestones": [
            {"id": "ms-x1-001", "project_id": "proj-x1-001", "stage": "PROTOTYPE", "planned_date": "2023-09-01T00:00:00Z", "actual_date": "2023-09-01T00:00:00Z", "status": "completed", "notes": "", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
            {"id": "ms-x1-002", "project_id": "proj-x1-001", "stage": "T0", "planned_date": "2023-10-01T00:00:00Z", "actual_date": "2023-10-01T00:00:00Z", "status": "completed", "notes": "", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-10-01T00:00:00Z"},
            {"id": "ms-x1-003", "project_id": "proj-x1-001", "stage": "T1", "planned_date": "2023-10-20T00:00:00Z", "actual_date": "2023-10-20T00:00:00Z", "status": "completed", "notes": "", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-10-20T00:00:00Z"},
            {"id": "ms-x1-004", "project_id": "proj-x1-001", "stage": "T2", "planned_date": "2023-11-15T00:00:00Z", "actual_date": None, "status": "pending", "notes": "", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
            {"id": "ms-x1-005", "project_id": "proj-x1-001", "stage": "DVT", "planned_date": "2023-12-01T00:00:00Z", "actual_date": None, "status": "pending", "notes": "", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
            {"id": "ms-x1-006", "project_id": "proj-x1-001", "stage": "PVT", "planned_date": "2024-01-10T00:00:00Z", "actual_date": None, "status": "pending", "notes": "", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
            {"id": "ms-x1-007", "project_id": "proj-x1-001", "stage": "MP", "planned_date": "2024-02-01T00:00:00Z", "actual_date": None, "status": "pending", "notes": "", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
            {"id": "ms-w2-001", "project_id": "proj-w2-002", "stage": "PROTOTYPE", "planned_date": "2023-08-01T00:00:00Z", "actual_date": "2023-08-01T00:00:00Z", "status": "completed", "notes": "", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-08-01T00:00:00Z"},
            {"id": "ms-w2-002", "project_id": "proj-w2-002", "stage": "T0", "planned_date": "2023-09-01T00:00:00Z", "actual_date": "2023-09-01T00:00:00Z", "status": "completed", "notes": "", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
            {"id": "ms-w2-003", "project_id": "proj-w2-002", "stage": "T1", "planned_date": "2023-10-01T00:00:00Z", "actual_date": "2023-10-01T00:00:00Z", "status": "completed", "notes": "", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-10-01T00:00:00Z"},
            {"id": "ms-w2-004", "project_id": "proj-w2-002", "stage": "DVT", "planned_date": "2023-11-01T00:00:00Z", "actual_date": "2023-11-01T00:00:00Z", "status": "completed", "notes": "", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-11-01T00:00:00Z"},
            {"id": "ms-w2-005", "project_id": "proj-w2-002", "stage": "PVT", "planned_date": "2023-12-15T00:00:00Z", "actual_date": None, "status": "pending", "notes": "", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-08-01T00:00:00Z"},
            {"id": "ms-w2-006", "project_id": "proj-w2-002", "stage": "MP", "planned_date": "2024-01-15T00:00:00Z", "actual_date": None, "status": "pending", "notes": "", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-08-01T00:00:00Z"}
        ],
        "tasks": [
            {"id": "task-001", "project_id": "proj-x1-001", "title": "确认 A 面中框阳极色差限度样", "description": "需要与供应商确认阳极氧化色差的可接受范围", "priority": "P0", "due_date": today_14.isoformat(), "status": "PENDING", "assignee_ids": ["user-alex-001"], "completed_at": None, "created_at": "2023-10-20T00:00:00Z", "updated_at": "2023-10-20T00:00:00Z"},
            {"id": "task-002", "project_id": "proj-x1-001", "title": "审核摄像头圈 PVD 新工艺报告", "description": "审核新 PVD 工艺的可行性报告", "priority": "P1", "due_date": today_17.isoformat(), "status": "PENDING", "assignee_ids": ["user-alex-001", "user-sarah-002"], "completed_at": None, "created_at": "2023-10-20T00:00:00Z", "updated_at": "2023-10-20T00:00:00Z"},
            {"id": "task-003", "project_id": "proj-w2-002", "title": "签署表带大货生产同意书 (PPAP)", "description": "签署 PPAP 文件，批准大货生产", "priority": "P2", "due_date": tomorrow_10.isoformat(), "status": "PENDING", "assignee_ids": ["user-sarah-002"], "completed_at": None, "created_at": "2023-10-20T00:00:00Z", "updated_at": "2023-10-20T00:00:00Z"},
            {"id": "task-004", "project_id": None, "title": "更新供应商联络人列表", "description": "季度供应商联络人信息更新", "priority": "P3", "due_date": "2023-10-20T00:00:00Z", "status": "COMPLETED", "assignee_ids": ["user-sarah-002"], "completed_at": "2023-10-20T00:00:00Z", "created_at": "2023-10-15T00:00:00Z", "updated_at": "2023-10-20T00:00:00Z"}
        ]
    }


class MockDataService:
    """Mock 数据服务类 - 内存中的数据管理"""
    
    def __init__(self):
        self.data = get_mock_data()
    
    def _build_project_response(self, proj: Dict) -> Dict:
        """构建包含关联数据的项目响应"""
        pm = next((u for u in self.data["users"] if u["id"] == proj["pm_id"]), None)
        parts = [p for p in self.data["parts"] if p["project_id"] == proj["id"]]
        parts_with_suppliers = []
        for part in parts:
            suppliers = [s for s in self.data["suppliers"] if s["part_id"] == part["id"]]
            parts_with_suppliers.append({**part, "suppliers": suppliers})
        
        milestones = [m for m in self.data["milestones"] if m["project_id"] == proj["id"]]
        tasks = [t for t in self.data["tasks"] if t.get("project_id") == proj["id"]]
        tasks_with_assignees = []
        for task in tasks:
            assignees = [u for u in self.data["users"] if u["id"] in task.get("assignee_ids", [])]
            tasks_with_assignees.append({**task, "assignees": assignees})
        
        return {
            **proj,
            "pm": pm,
            "parts": parts_with_suppliers,
            "milestones": milestones,
            "tasks": tasks_with_assignees
        }
    
    def get_dashboard_overview(self) -> Dict[str, Any]:
        """获取仪表盘概览数据"""
        total_projects = len(self.data["projects"])
        ongoing_projects = sum(1 for p in self.data["projects"] if p["current_stage"] != "MP")
        high_risk_parts = sum(1 for p in self.data["parts"] if p["risk_level"] in ["HIGH", "CRITICAL"])
        
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        today_tasks = []
        for t in self.data["tasks"]:
            try:
                due = datetime.fromisoformat(t["due_date"].replace("Z", "+00:00")).replace(tzinfo=None)
                if today_start <= due < today_end and t["status"] != "COMPLETED":
                    today_tasks.append(t)
            except:
                pass
        
        pending_tasks = sum(1 for t in self.data["tasks"] if t["status"] == "PENDING")
        
        projects_with_relations = [self._build_project_response(p) for p in self.data["projects"]]
        
        tasks_with_assignees = []
        for task in today_tasks:
            assignees = [u for u in self.data["users"] if u["id"] in task.get("assignee_ids", [])]
            tasks_with_assignees.append({**task, "assignees": assignees})
        
        return {
            "total_projects": total_projects,
            "ongoing_projects": ongoing_projects,
            "high_risk_parts": high_risk_parts,
            "today_tasks": len(today_tasks),
            "pending_tasks": pending_tasks,
            "projects": projects_with_relations,
            "tasks": tasks_with_assignees
        }
    
    def get_all_projects(self) -> List[Dict]:
        """获取所有项目"""
        return [self._build_project_response(p) for p in self.data["projects"]]
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """获取单个项目"""
        proj = next((p for p in self.data["projects"] if p["id"] == project_id), None)
        return self._build_project_response(proj) if proj else None
    
    def create_project(self, project_data: Dict) -> Dict:
        """创建新项目"""
        # 检查项目代号是否已存在
        if any(p["code"] == project_data["code"] for p in self.data["projects"]):
            raise HTTPException(status_code=400, detail="项目代号已存在")
        
        # 验证项目经理是否存在
        if not any(u["id"] == project_data["pm_id"] for u in self.data["users"]):
            raise HTTPException(status_code=404, detail="项目经理不存在")
        
        new_project = {
            "id": f"proj-{uuid.uuid4().hex[:8]}",
            **project_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.data["projects"].append(new_project)
        return self._build_project_response(new_project)
    
    def update_project(self, project_id: str, update_data: Dict) -> Optional[Dict]:
        """更新项目"""
        proj = next((p for p in self.data["projects"] if p["id"] == project_id), None)
        if not proj:
            return None
        
        for key, value in update_data.items():
            if value is not None and key in proj:
                proj[key] = value
        proj["updated_at"] = datetime.now().isoformat()
        
        return self._build_project_response(proj)
    
    def update_part_status(self, part_id: str, update_data: Dict) -> Optional[Dict]:
        """更新部件状态"""
        part = next((p for p in self.data["parts"] if p["id"] == part_id), None)
        if not part:
            return None
        
        for key, value in update_data.items():
            if value is not None and key in part:
                part[key] = value
        part["updated_at"] = datetime.now().isoformat()
        
        # 构建响应
        suppliers = [s for s in self.data["suppliers"] if s["part_id"] == part_id]
        return {**part, "suppliers": suppliers}
    
    def get_tasks(self, project_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        """获取任务列表"""
        tasks = self.data["tasks"]
        if project_id:
            tasks = [t for t in tasks if t.get("project_id") == project_id]
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        
        result = []
        for task in tasks:
            assignees = [u for u in self.data["users"] if u["id"] in task.get("assignee_ids", [])]
            result.append({**task, "assignees": assignees})
        return result
    
    def create_task(self, task_data: Dict) -> Dict:
        """创建新任务"""
        assignee_ids = task_data.pop("assignee_ids", [])
        
        # 验证指派人
        if assignee_ids:
            valid_ids = {u["id"] for u in self.data["users"]}
            if not all(aid in valid_ids for aid in assignee_ids):
                raise HTTPException(status_code=404, detail="部分指派人不存在")
        
        new_task = {
            "id": f"task-{uuid.uuid4().hex[:8]}",
            **task_data,
            "assignee_ids": assignee_ids,
            "completed_at": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.data["tasks"].append(new_task)
        
        assignees = [u for u in self.data["users"] if u["id"] in assignee_ids]
        return {**new_task, "assignees": assignees}
    
    def update_task(self, task_id: str, update_data: Dict) -> Optional[Dict]:
        """更新任务"""
        task = next((t for t in self.data["tasks"] if t["id"] == task_id), None)
        if not task:
            return None
        
        assignee_ids = update_data.pop("assignee_ids", None)
        for key, value in update_data.items():
            if value is not None and key in task:
                task[key] = value
        
        if assignee_ids is not None:
            task["assignee_ids"] = assignee_ids
        task["updated_at"] = datetime.now().isoformat()
        
        assignees = [u for u in self.data["users"] if u["id"] in task.get("assignee_ids", [])]
        return {**task, "assignees": assignees}
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        task = next((t for t in self.data["tasks"] if t["id"] == task_id), None)
        if not task:
            return False
        self.data["tasks"].remove(task)
        return True
    
    def get_users(self) -> List[Dict]:
        """获取所有用户"""
        return self.data["users"]


# 全局数据服务实例
data_service = MockDataService()


# ============================================
# FastAPI 应用初始化
# ============================================

app = FastAPI(
    title="CMF 供应链项目管理系统 API",
    description="""
## CMF 项目管理后端服务 (v2.0)

### 核心特性
- **零外部依赖**: 仅依赖 FastAPI/Uvicorn，时区用标准库 datetime
- **内存+JSON Mock**: 启动即加载内置数据，重启重置
- **单文件架构**: 所有逻辑合并至 app.py，消除导入问题

### 核心功能
- **项目管理**: 创建、更新、查询硬件项目（EVT/DVT/PVT/MP 生命周期）
- **部件管理**: 管理 CMF 部件及其风险状态
- **供应商管理**: 主供/二供关系管理
- **里程碑跟踪**: 项目时间节点管理
- **任务系统**: 待办事项管理（P0-P3 优先级）
    """,
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# 全局异常处理
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常拦截"""
    import traceback
    error_trace = traceback.format_exc()
    print(f"[ERROR] {error_trace}")
    return {"message": "Internal Server Error", "success": False}


# ============================================
# API 接口实现
# ============================================

@app.get("/api/system/time", response_model=SystemTimeResponse, tags=["系统"])
async def get_system_time():
    """获取服务器标准时间（使用标准库 datetime，无需 pytz）"""
    tz = timezone(timedelta(hours=8))  # Asia/Shanghai = UTC+8
    server_time = datetime.now(tz)
    return SystemTimeResponse(
        server_time=server_time.isoformat(),
        timezone="Asia/Shanghai"
    )


@app.get("/api/dashboard/overview", response_model=DashboardOverview, tags=["仪表盘"])
async def get_dashboard_overview():
    """获取看板首页数据"""
    return data_service.get_dashboard_overview()


@app.get("/api/projects", response_model=List[ProjectResponse], tags=["项目"])
async def list_projects():
    """获取所有项目列表"""
    return data_service.get_all_projects()


@app.get("/api/projects/{project_id}", response_model=ProjectResponse, tags=["项目"])
async def get_project(project_id: str):
    """获取单个项目详情"""
    project = data_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@app.post("/api/projects", response_model=ProjectResponse, tags=["项目"])
async def create_project(project_data: ProjectCreate):
    """创建新项目"""
    return data_service.create_project(project_data.model_dump())


@app.patch("/api/projects/{project_id}", response_model=ProjectResponse, tags=["项目"])
async def update_project(project_id: str, project_data: ProjectUpdate):
    """更新项目信息"""
    update_data = {k: v for k, v in project_data.model_dump().items() if v is not None}
    project = data_service.update_project(project_id, update_data)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@app.patch("/api/parts/{part_id}/status", response_model=PartResponse, tags=["部件"])
async def update_part_status(part_id: str, status_data: PartUpdate):
    """更新部件风险状态或进度备注"""
    update_data = {k: v for k, v in status_data.model_dump().items() if v is not None}
    part = data_service.update_part_status(part_id, update_data)
    if not part:
        raise HTTPException(status_code=404, detail="部件不存在")
    return part


@app.get("/api/tasks", response_model=List[TaskResponse], tags=["任务"])
async def list_tasks(project_id: Optional[str] = None, status: Optional[TaskStatus] = None):
    """获取任务列表，支持按项目和状态筛选"""
    return data_service.get_tasks(project_id, status.value if status else None)


@app.post("/api/tasks", response_model=TaskResponse, tags=["任务"])
async def create_task(task_data: TaskCreate):
    """创建新任务"""
    return data_service.create_task(task_data.model_dump())


@app.delete("/api/tasks/{task_id}", response_model=MessageResponse, tags=["任务"])
async def delete_task(task_id: str):
    """删除任务"""
    if not data_service.delete_task(task_id):
        raise HTTPException(status_code=404, detail="任务不存在")
    return MessageResponse(message="任务已删除", success=True)


@app.patch("/api/tasks/{task_id}", response_model=TaskResponse, tags=["任务"])
async def update_task(task_id: str, task_data: TaskUpdate):
    """更新任务信息"""
    update_data = {k: v for k, v in task_data.model_dump().items() if v is not None}
    task = data_service.update_task(task_id, update_data)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@app.get("/api/users", response_model=List[UserResponse], tags=["用户"])
async def list_users():
    """获取所有用户列表"""
    return data_service.get_users()


@app.get("/health", tags=["健康检查"])
async def health_check():
    """API 健康检查端点"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ============================================
# 前端静态文件服务
# ============================================

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# 如果 static 目录存在，则挂载静态文件服务
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    
    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        """提供前端看板页面"""
        mainweb_path = os.path.join(STATIC_DIR, "mainweb.html")
        if os.path.exists(mainweb_path):
            return FileResponse(mainweb_path)
        return {"message": "前端页面未找到，请查看 /api/docs 使用 API"}
else:
    # 尝试从根目录查找 mainweb.html
    root_mainweb = os.path.join(BASE_DIR, "mainweb.html")
    if os.path.exists(root_mainweb):
        @app.get("/", include_in_schema=False)
        async def serve_frontend():
            """提供前端看板页面"""
            return FileResponse(root_mainweb)


# ============================================
# 主入口
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
