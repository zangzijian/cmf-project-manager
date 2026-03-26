"""
CMF 供应链项目管理系统 - Pydantic Schemas
用于 API 请求/响应验证和序列化
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================
# 枚举 Schema
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
# 用户 Schema
# ============================================

class UserBase(BaseModel):
    email: str = Field(..., description="邮箱地址")
    name: str = Field(..., description="姓名")
    avatar_initial: Optional[str] = Field(None, description="头像首字母")
    role: UserRole = Field(default=UserRole.PM, description="角色")


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_initial: Optional[str] = None
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# 供应商 Schema
# ============================================

class SupplierBase(BaseModel):
    name: str = Field(..., description="供应商名称")
    type: SupplierType = Field(default=SupplierType.PRIMARY, description="供应商类型")
    contact_person: Optional[str] = Field(None, description="联系人")
    contact_email: Optional[str] = Field(None, description="联系邮箱")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    performance_score: Optional[float] = Field(None, description="绩效评分", ge=0, le=100)
    is_approved: bool = Field(default=True, description="是否认证供应商")


class SupplierCreate(SupplierBase):
    part_id: str


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[SupplierType] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    performance_score: Optional[float] = Field(None, ge=0, le=100)
    is_approved: Optional[bool] = None


class SupplierResponse(SupplierBase):
    id: str
    part_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# 部件 Schema
# ============================================

class PartBase(BaseModel):
    name: str = Field(..., description="部件名称")
    structure: Optional[str] = Field(None, description="结构描述")
    process: Optional[str] = Field(None, description="工艺说明")
    risk_level: RiskLevel = Field(default=RiskLevel.LOW, description="风险等级")
    risk_type: Optional[RiskType] = Field(None, description="风险类型")
    progress_note: Optional[str] = Field(None, description="进度备注")
    is_critical: bool = Field(default=False, description="是否关键部件")


class PartCreate(PartBase):
    project_id: str


class PartUpdate(BaseModel):
    name: Optional[str] = None
    structure: Optional[str] = None
    process: Optional[str] = None
    risk_level: Optional[RiskLevel] = None
    risk_type: Optional[RiskType] = None
    progress_note: Optional[str] = None
    actual_date: Optional[datetime] = None
    is_critical: Optional[bool] = None


class PartResponse(PartBase):
    id: str
    project_id: str
    actual_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    suppliers: List[SupplierResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# 里程碑 Schema
# ============================================

class MilestoneBase(BaseModel):
    stage: ProjectStage = Field(..., description="阶段类型")
    planned_date: datetime = Field(..., description="计划日期")
    actual_date: Optional[datetime] = Field(None, description="实际日期")
    status: str = Field(default="pending", description="状态")
    notes: Optional[str] = Field(None, description="备注")


class MilestoneCreate(MilestoneBase):
    project_id: str


class MilestoneUpdate(BaseModel):
    planned_date: Optional[datetime] = None
    actual_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class MilestoneResponse(MilestoneBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# 任务 Schema
# ============================================

class TaskBase(BaseModel):
    title: str = Field(..., description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    priority: TaskPriority = Field(default=TaskPriority.P2, description="优先级")
    due_date: datetime = Field(..., description="截止时间")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="状态")


class TaskCreate(TaskBase):
    project_id: Optional[str] = Field(None, description="关联项目 ID")
    assignee_ids: List[str] = Field(default=[], description="指派人 ID 列表")


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    status: Optional[TaskStatus] = None
    assignee_ids: Optional[List[str]] = None
    completed_at: Optional[datetime] = None


class TaskAssigneeResponse(BaseModel):
    id: str
    name: str
    avatar_initial: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)


class TaskResponse(TaskBase):
    id: str
    project_id: Optional[str]
    assignees: List[TaskAssigneeResponse] = []
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# 项目 Schema
# ============================================

class ProjectBase(BaseModel):
    code: str = Field(..., description="项目代号", pattern=r"^PJ-\d{4}-\w+$")
    name: str = Field(..., description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    current_stage: ProjectStage = Field(default=ProjectStage.PROTOTYPE, description="当前阶段")
    overall_status: RiskLevel = Field(default=RiskLevel.LOW, description="整体风险状态")
    pm_id: str = Field(..., description="项目经理 ID")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    current_stage: Optional[ProjectStage] = None
    overall_status: Optional[RiskLevel] = None
    pm_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ProjectResponse(ProjectBase):
    id: str
    pm: UserResponse
    parts: List[PartResponse] = []
    milestones: List[MilestoneResponse] = []
    tasks: List[TaskResponse] = []
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# 风险日志 Schema
# ============================================

class RiskLogBase(BaseModel):
    entity_type: str = Field(..., description="实体类型：project/part")
    entity_id: str = Field(..., description="实体 ID")
    previous_level: Optional[RiskLevel] = Field(None, description="原风险等级")
    new_level: RiskLevel = Field(..., description="新风险等级")
    risk_type: Optional[RiskType] = Field(None, description="风险类型")
    reason: Optional[str] = Field(None, description="变更原因")
    triggered_by: Optional[str] = Field(None, description="触发来源：manual/auto")


class RiskLogCreate(RiskLogBase):
    user_id: Optional[str] = None


class RiskLogResponse(RiskLogBase):
    id: str
    user_id: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# 仪表盘概览 Schema
# ============================================

class DashboardOverview(BaseModel):
    total_projects: int
    ongoing_projects: int
    high_risk_parts: int
    today_tasks: int
    pending_tasks: int
    projects: List[ProjectResponse]
    tasks: List[TaskResponse]


# ============================================
# 系统时间 Schema
# ============================================

class SystemTimeResponse(BaseModel):
    server_time: datetime
    timezone: str = "Asia/Shanghai"


# ============================================
# 通用响应 Schema
# ============================================

class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    message: str
    detail: Optional[str] = None
    success: bool = False
