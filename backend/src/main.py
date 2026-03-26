"""
CMF 供应链项目管理系统 - FastAPI 主应用
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from typing import List, Optional
import pytz

from models import (
    Base, Project, Part, Supplier, Milestone, Task, User, RiskLog, SystemSetting,
    ProjectStage, RiskLevel, RiskType, TaskPriority, TaskStatus, SupplierType
)
from schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    PartUpdate, PartResponse,
    TaskCreate, TaskUpdate, TaskResponse,
    MilestoneResponse,
    UserResponse,
    DashboardOverview,
    SystemTimeResponse,
    MessageResponse
)

# ============================================
# 数据库配置
# ============================================

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/cmf_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """数据库会话依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================
# FastAPI 应用初始化
# ============================================

app = FastAPI(
    title="CMF 供应链项目管理系统 API",
    description="""
## CMF 项目管理后端服务
    
提供项目、部件、供应商、里程碑和任务的完整管理功能。

### 核心功能
- **项目管理**: 创建、更新、查询硬件项目（EVT/DVT/PVT/MP 生命周期）
- **部件管理**: 管理 CMF 部件及其风险状态
- **供应商管理**: 主供/二供关系管理
- **里程碑跟踪**: 项目时间节点管理
- **任务系统**: 待办事项管理（P0-P3 优先级）
- **风险审计**: 风险变更日志追踪
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS 配置（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# 辅助函数
# ============================================

def calculate_dynamic_risk(part: Part, milestones: List[Milestone]) -> RiskLevel:
    """
    动态风险计算服务
    根据部件的实际日期 vs 计划日期自动计算风险等级
    """
    if not milestones:
        return part.risk_level
    
    now = datetime.now()
    
    # 查找当前或下一个里程碑
    upcoming_milestones = [m for m in milestones if m.planned_date >= now]
    if not upcoming_milestones:
        return part.risk_level
    
    next_milestone = min(upcoming_milestones, key=lambda m: m.planned_date)
    days_until_deadline = (next_milestone.planned_date - now).days
    
    # 根据剩余天数判断风险
    if days_until_deadline < 0:
        return RiskLevel.HIGH  # 已延期
    elif days_until_deadline <= 3:
        return RiskLevel.HIGH  # 3 天内到期，高风险
    elif days_until_deadline <= 7:
        return RiskLevel.MEDIUM  # 7 天内到期，中风险
    
    return part.risk_level


# ============================================
# API 接口实现
# ============================================

@app.get("/api/system/time", response_model=SystemTimeResponse, tags=["系统"])
async def get_system_time():
    """
    获取服务器标准时间
    用于前端校准时间指示器
    """
    tz = pytz.timezone("Asia/Shanghai")
    server_time = datetime.now(tz)
    return SystemTimeResponse(
        server_time=server_time,
        timezone="Asia/Shanghai"
    )


@app.get("/api/dashboard/overview", response_model=DashboardOverview, tags=["仪表盘"])
async def get_dashboard_overview(db: Session = Depends(get_db)):
    """
    获取看板首页数据
    聚合项目列表、统计数字、今日任务
    """
    # 查询所有项目（带关联数据）
    projects = db.query(Project).options(
        joinedload(Project.pm),
        joinedload(Project.parts).joinedload(Part.suppliers),
        joinedload(Project.milestones),
        joinedload(Project.tasks).joinedload(Task.assignees)
    ).all()
    
    # 统计数字
    total_projects = len(projects)
    ongoing_projects = sum(1 for p in projects if p.current_stage != ProjectStage.MP)
    
    # 高风险部件统计
    high_risk_parts = db.query(Part).filter(
        or_(Part.risk_level == RiskLevel.HIGH, Part.risk_level == RiskLevel.CRITICAL)
    ).count()
    
    # 今日任务
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    today_tasks = db.query(Task).filter(
        Task.due_date >= today_start,
        Task.due_date < today_end,
        Task.status != TaskStatus.COMPLETED
    ).all()
    
    pending_tasks = db.query(Task).filter(
        Task.status == TaskStatus.PENDING
    ).count()
    
    # 转换为响应格式
    def project_to_dict(p: Project) -> dict:
        return {
            "id": p.id,
            "code": p.code,
            "name": p.name,
            "description": p.description,
            "current_stage": p.current_stage.value,
            "overall_status": p.overall_status.value,
            "pm_id": p.pm_id,
            "start_date": p.start_date.isoformat() if p.start_date else None,
            "end_date": p.end_date.isoformat() if p.end_date else None,
            "pm": {
                "id": p.pm.id,
                "email": p.pm.email,
                "name": p.pm.name,
                "avatar_initial": p.pm.avatar_initial,
                "role": p.pm.role.value,
                "created_at": p.pm.created_at.isoformat(),
                "updated_at": p.pm.updated_at.isoformat()
            },
            "parts": [{
                "id": part.id,
                "name": part.name,
                "structure": part.structure,
                "process": part.process,
                "risk_level": part.risk_level.value,
                "risk_type": part.risk_type.value if part.risk_type else None,
                "progress_note": part.progress_note,
                "is_critical": part.is_critical,
                "actual_date": part.actual_date.isoformat() if part.actual_date else None,
                "created_at": part.created_at.isoformat(),
                "updated_at": part.updated_at.isoformat(),
                "suppliers": [{
                    "id": s.id,
                    "name": s.name,
                    "type": s.type.value,
                    "created_at": s.created_at.isoformat(),
                    "updated_at": s.updated_at.isoformat(),
                    "part_id": s.part_id
                } for s in part.suppliers]
            } for part in p.parts],
            "milestones": [{
                "id": m.id,
                "stage": m.stage.value,
                "planned_date": m.planned_date.isoformat(),
                "actual_date": m.actual_date.isoformat() if m.actual_date else None,
                "status": m.status,
                "notes": m.notes,
                "created_at": m.created_at.isoformat(),
                "updated_at": m.updated_at.isoformat(),
                "project_id": m.project_id
            } for m in p.milestones],
            "tasks": [],  # 项目详情中不包含任务列表，避免数据过大
            "created_at": p.created_at.isoformat(),
            "updated_at": p.updated_at.isoformat()
        }
    
    def task_to_dict(t: Task) -> dict:
        return {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "priority": t.priority.value,
            "due_date": t.due_date.isoformat(),
            "status": t.status.value,
            "project_id": t.project_id,
            "assignees": [{
                "id": a.id,
                "name": a.name,
                "avatar_initial": a.avatar_initial
            } for a in t.assignees],
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            "created_at": t.created_at.isoformat(),
            "updated_at": t.updated_at.isoformat()
        }
    
    return DashboardOverview(
        total_projects=total_projects,
        ongoing_projects=ongoing_projects,
        high_risk_parts=high_risk_parts,
        today_tasks=len(today_tasks),
        pending_tasks=pending_tasks,
        projects=[project_to_dict(p) for p in projects],
        tasks=[task_to_dict(t) for t in today_tasks]
    )


@app.get("/api/projects", response_model=List[ProjectResponse], tags=["项目"])
async def list_projects(db: Session = Depends(get_db)):
    """获取所有项目列表"""
    projects = db.query(Project).options(
        joinedload(Project.pm),
        joinedload(Project.parts).joinedload(Part.suppliers),
        joinedload(Project.milestones)
    ).all()
    return projects


@app.get("/api/projects/{project_id}", response_model=ProjectResponse, tags=["项目"])
async def get_project(project_id: str, db: Session = Depends(get_db)):
    """
    获取单个项目详情
    包含部件列表、时间轴（里程碑）
    """
    project = db.query(Project).options(
        joinedload(Project.pm),
        joinedload(Project.parts).joinedload(Part.suppliers),
        joinedload(Project.milestones),
        joinedload(Project.tasks).joinedload(Task.assignees)
    ).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    return project


@app.post("/api/projects", response_model=ProjectResponse, tags=["项目"])
async def create_project(project_data: ProjectCreate, db: Session = Depends(get_db)):
    """
    创建新项目
    对应前端悬浮按钮 (+) 功能
    """
    # 验证项目经理是否存在
    pm = db.query(User).filter(User.id == project_data.pm_id).first()
    if not pm:
        raise HTTPException(status_code=404, detail="项目经理不存在")
    
    # 检查项目代号是否已存在
    existing = db.query(Project).filter(Project.code == project_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="项目代号已存在")
    
    # 创建项目
    project = Project(**project_data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # 加载关联数据
    db.refresh(project, attribute_names=['pm'])
    
    return project


@app.patch("/api/projects/{project_id}", response_model=ProjectResponse, tags=["项目"])
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """更新项目信息"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    update_data = project_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    
    db.commit()
    db.refresh(project)
    
    return project


@app.patch("/api/parts/{part_id}/status", response_model=PartResponse, tags=["部件"])
async def update_part_status(
    part_id: str,
    status_data: PartUpdate,
    db: Session = Depends(get_db)
):
    """
    更新部件风险状态或进度备注
    同时记录风险变更日志
    """
    part = db.query(Part).options(joinedload(Part.suppliers)).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="部件不存在")
    
    # 记录风险变更前状态
    previous_level = part.risk_level
    
    update_data = status_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(part, key, value)
    
    # 如果风险等级发生变化，记录日志
    if previous_level != part.risk_level:
        risk_log = RiskLog(
            entity_type="part",
            entity_id=part.id,
            previous_level=previous_level,
            new_level=part.risk_level,
            risk_type=part.risk_type,
            reason=status_data.progress_note,
            triggered_by="manual"
        )
        db.add(risk_log)
    
    db.commit()
    db.refresh(part)
    
    return part


@app.get("/api/tasks", response_model=List[TaskResponse], tags=["任务"])
async def list_tasks(
    project_id: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    db: Session = Depends(get_db)
):
    """获取任务列表，支持按项目和状态筛选"""
    query = db.query(Task).options(joinedload(Task.assignees))
    
    if project_id:
        query = query.filter(Task.project_id == project_id)
    if status:
        query = query.filter(Task.status == status)
    
    return query.all()


@app.post("/api/tasks", response_model=TaskResponse, tags=["任务"])
async def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    """
    创建新任务
    """
    # 验证指派人是否存在
    if task_data.assignee_ids:
        assignees = db.query(User).filter(User.id.in_(task_data.assignee_ids)).all()
        if len(assignees) != len(task_data.assignee_ids):
            raise HTTPException(status_code=404, detail="部分指派人不存在")
    
    # 创建任务
    task = Task(**task_data.model_dump(exclude={'assignee_ids'}))
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 关联指派人
    if task_data.assignee_ids:
        task.assignees = assignees
        db.commit()
        db.refresh(task)
    
    return task


@app.delete("/api/tasks/{task_id}", response_model=MessageResponse, tags=["任务"])
async def delete_task(task_id: str, db: Session = Depends(get_db)):
    """
    删除任务
    对应前端垃圾桶按钮 (.delete-btn) 功能
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    db.delete(task)
    db.commit()
    
    return MessageResponse(message="任务已删除", success=True)


@app.patch("/api/tasks/{task_id}", response_model=TaskResponse, tags=["任务"])
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    db: Session = Depends(get_db)
):
    """更新任务信息"""
    task = db.query(Task).options(joinedload(Task.assignees)).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == 'assignee_ids' and value is not None:
            assignees = db.query(User).filter(User.id.in_(value)).all()
            task.assignees = assignees
        else:
            setattr(task, key, value)
    
    db.commit()
    db.refresh(task)
    
    return task


@app.get("/api/users", response_model=List[UserResponse], tags=["用户"])
async def list_users(db: Session = Depends(get_db)):
    """获取所有用户列表"""
    return db.query(User).all()


# ============================================
# 健康检查
# ============================================

@app.get("/health", tags=["健康检查"])
async def health_check():
    """API 健康检查端点"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
