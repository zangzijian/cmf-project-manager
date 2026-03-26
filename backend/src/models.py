# CMF 供应链项目管理系统 - SQLAlchemy 数据库模型
# 数据库：PostgreSQL

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Boolean, Float, Text, UniqueConstraint, Index, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from enum import Enum as PyEnum
import uuid

Base = declarative_base()

# ============================================
# 枚举定义
# ============================================

class ProjectStage(str, PyEnum):
    """项目生命周期阶段（硬件行业标准的线性状态机）"""
    KV = "KV"           # 关键验证
    EVT = "EVT"         # 工程验证测试
    DVT = "DVT"         # 设计验证测试
    PVT = "PVT"         # 生产验证测试
    MP = "MP"           # 量产
    PROTOTYPE = "PROTOTYPE"  # 手板/原型
    T0 = "T0"           # 第一次试模
    T1 = "T1"           # 第二次试模
    T2 = "T2"           # 第三次试模


class RiskLevel(str, PyEnum):
    """风险等级"""
    LOW = "LOW"         # 低风险 - 绿色
    MEDIUM = "MEDIUM"   # 中风险 - 黄色
    HIGH = "HIGH"       # 高风险 - 红色
    CRITICAL = "CRITICAL"  # 严重风险


class RiskType(str, PyEnum):
    """风险类型（支持扩展）"""
    DELAY = "DELAY"     # 延期风险
    PROCESS = "PROCESS" # 工艺风险
    YIELD = "YIELD"     # 良率风险
    COST = "COST"       # 成本风险
    QUALITY = "QUALITY" # 质量风险
    SUPPLY = "SUPPLY"   # 供应风险


class TaskPriority(str, PyEnum):
    """任务优先级"""
    P0 = "P0"  # 紧急 - 立即处理
    P1 = "P1"  # 重要 - 今天处理
    P2 = "P2"  # 常规 - 本周处理
    P3 = "P3"  # 低优 - 可延后


class TaskStatus(str, PyEnum):
    """任务状态"""
    PENDING = "PENDING"     # 待处理
    IN_PROGRESS = "IN_PROGRESS"  # 进行中
    COMPLETED = "COMPLETED"      # 已完成
    CANCELLED = "CANCELLED"      # 已取消


class SupplierType(str, PyEnum):
    """供应商类型"""
    PRIMARY = "PRIMARY"     # 主供应商
    SECONDARY = "SECONDARY" # 二供/备选


class UserRole(str, PyEnum):
    """用户角色"""
    ADMIN = "ADMIN"     # 管理员
    PM = "PM"           # 项目经理
    ENGINEER = "ENGINEER"  # 工程师
    SUPPLIER = "SUPPLIER"  # 供应商代表


# ============================================
# 核心数据模型
# ============================================

class User(Base):
    """用户表 - 对应头像/负责人"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    avatar_initial = Column(String, nullable=True)  # 头像首字母（如前端显示的"A", "S"）
    role = Column(Enum(UserRole), default=UserRole.PM)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    assigned_tasks = relationship("Task", secondary="task_assignees", back_populates="assignees")
    created_projects = relationship("Project", back_populates="pm")
    risk_logs = relationship("RiskLog", back_populates="user")
    
    __table_args__ = (
        Index('ix_users_email', 'email'),
    )


class Project(Base):
    """项目主表"""
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String, unique=True, nullable=False)  # 项目代号，如 PJ-2023-X1
    name = Column(String, nullable=False)  # 项目名称
    description = Column(Text, nullable=True)
    current_stage = Column(Enum(ProjectStage), default=ProjectStage.PROTOTYPE)
    overall_status = Column(Enum(RiskLevel), default=RiskLevel.LOW)  # 整体风险状态
    pm_id = Column(String, ForeignKey("users.id"), nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    pm = relationship("User", back_populates="created_projects")
    parts = relationship("Part", back_populates="project", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project")
    risk_logs = relationship("RiskLog", back_populates="project")
    
    __table_args__ = (
        Index('ix_projects_current_stage', 'current_stage'),
        Index('ix_projects_overall_status', 'overall_status'),
    )


class Part(Base):
    """部件表 - CMF 核心管理对象"""
    __tablename__ = "parts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)  # 部件名称
    structure = Column(String, nullable=True)  # 结构描述
    process = Column(String, nullable=True)  # 工艺说明
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.LOW)
    risk_type = Column(Enum(RiskType), nullable=True)
    progress_note = Column(Text, nullable=True)  # 进度备注
    actual_date = Column(DateTime, nullable=True)  # 实际完成日期
    is_critical = Column(Boolean, default=False)  # 是否关键部件
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    project = relationship("Project", back_populates="parts")
    suppliers = relationship("Supplier", back_populates="part", cascade="all, delete-orphan")
    risk_logs = relationship("RiskLog", back_populates="part")
    
    __table_args__ = (
        Index('ix_parts_project_id', 'project_id'),
        Index('ix_parts_risk_level', 'risk_level'),
    )


class Supplier(Base):
    """供应商表 - 支持多对多关系（一个部件多个供应商）"""
    __tablename__ = "suppliers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    part_id = Column(String, ForeignKey("parts.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)  # 供应商名称
    type = Column(Enum(SupplierType), default=SupplierType.PRIMARY)
    contact_person = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    performance_score = Column(Float, nullable=True)  # 绩效评分 (0-100)
    is_approved = Column(Boolean, default=True)  # 是否认证供应商
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    part = relationship("Part", back_populates="suppliers")
    
    __table_args__ = (
        Index('ix_suppliers_part_id', 'part_id'),
        Index('ix_suppliers_type', 'type'),
    )


class Milestone(Base):
    """里程碑表 - 项目时间节点"""
    __tablename__ = "milestones"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    stage = Column(Enum(ProjectStage), nullable=False)  # 阶段类型
    planned_date = Column(DateTime, nullable=False)  # 计划日期
    actual_date = Column(DateTime, nullable=True)  # 实际日期
    status = Column(String, default="pending")  # pending/completed/delayed
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    project = relationship("Project", back_populates="milestones")
    
    __table_args__ = (
        Index('ix_milestones_project_id', 'project_id'),
        Index('ix_milestones_stage', 'stage'),
        UniqueConstraint('project_id', 'stage', name='uq_project_stage'),
    )


# 任务分配关联表（多对多）
task_assignees = Table(
    'task_assignees',
    Base.metadata,
    Column('task_id', String, ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
)


class Task(Base):
    """任务表 - 待办事项"""
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.P2)
    due_date = Column(DateTime, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    project = relationship("Project", back_populates="tasks")
    assignees = relationship("User", secondary=task_assignees, back_populates="assigned_tasks")
    
    __table_args__ = (
        Index('ix_tasks_project_id', 'project_id'),
        Index('ix_tasks_priority', 'priority'),
        Index('ix_tasks_status', 'status'),
        Index('ix_tasks_due_date', 'due_date'),
    )


class RiskLog(Base):
    """风险日志表 - 审计追踪"""
    __tablename__ = "risk_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = Column(String, nullable=False)  # entity type: project/part
    entity_id = Column(String, nullable=False)  # entity id
    previous_level = Column(Enum(RiskLevel), nullable=True)
    new_level = Column(Enum(RiskLevel), nullable=False)
    risk_type = Column(Enum(RiskType), nullable=True)
    reason = Column(Text, nullable=True)  # 变更原因
    triggered_by = Column(String, nullable=True)  # manual/auto
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="risk_logs")
    project = relationship("Project", back_populates="risk_logs", primaryjoin="and_(RiskLog.entity_type=='project', RiskLog.entity_id==foreign(Project.id))")
    part = relationship("Part", back_populates="risk_logs", primaryjoin="and_(RiskLog.entity_type=='part', RiskLog.entity_id==foreign(Part.id))")
    
    __table_args__ = (
        Index('ix_risk_logs_entity', 'entity_type', 'entity_id'),
        Index('ix_risk_logs_created_at', 'created_at'),
    )


class SystemSetting(Base):
    """系统设置表"""
    __tablename__ = "system_settings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

