"""
CMF Supply Chain Management System - Main Application
Version: 2.0.0 (Standalone Production Ready)

Features:
- Zero external dependencies except fastapi, uvicorn, pydantic
- Built-in mock data for immediate use
- SQLite database support (no external DB required)
- Automatic path handling for systemd deployment
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum

# Ensure current directory is in path for systemd deployment
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

# ============================================================================
# ENUMS
# ============================================================================

class ProjectStage(str, Enum):
    PROTOTYPE = "prototype"
    T0 = "t0"
    T1 = "t1"
    T2 = "t2"
    EVT = "evt"
    DVT = "dvt"
    PVT = "pvt"
    MP = "mp"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskPriority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class User(BaseModel):
    id: int
    name: str
    email: str
    avatar: Optional[str] = None

class Supplier(BaseModel):
    id: int
    name: str
    type: str  # primary or secondary
    contact: Optional[str] = None

class Part(BaseModel):
    id: int
    project_id: int
    name: str
    process: str
    primary_supplier: str
    secondary_supplier: Optional[str] = None
    risk_level: RiskLevel
    status_note: Optional[str] = None
    progress: int = 0

class Milestone(BaseModel):
    id: int
    project_id: int
    stage: ProjectStage
    planned_date: str
    actual_date: Optional[str] = None
    status: str = "pending"

class Task(BaseModel):
    id: int
    project_id: int
    title: str
    priority: TaskPriority
    due_date: str
    assignee_id: int
    assignee_name: str
    status: TaskStatus = TaskStatus.TODO
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class Project(BaseModel):
    id: int
    code: str
    name: str
    pm_id: int
    pm_name: str
    current_stage: ProjectStage
    overall_status: RiskLevel
    progress: int
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    parts: Optional[List[Part]] = []
    milestones: Optional[List[Milestone]] = []

class DashboardOverview(BaseModel):
    total_projects: int
    active_projects: int
    high_risk_parts: int
    today_tasks: int
    projects: List[Project]
    tasks: List[Task]

class CreateProjectRequest(BaseModel):
    code: str
    name: str
    pm_id: int
    current_stage: ProjectStage = ProjectStage.PROTOTYPE

class CreateTaskRequest(BaseModel):
    project_id: int
    title: str
    priority: TaskPriority
    due_date: str
    assignee_id: int

class UpdatePartStatusRequest(BaseModel):
    risk_level: Optional[RiskLevel] = None
    status_note: Optional[str] = None
    progress: Optional[int] = None

# ============================================================================
# MOCK DATA SERVICE
# ============================================================================

class MockDataService:
    """Built-in mock data service - no external dependencies required"""
    
    def __init__(self):
        self.users = [
            User(id=1, name="张三", email="zhangsan@cmf.com", avatar="👨‍💼"),
            User(id=2, name="李四", email="lisi@cmf.com", avatar="👩‍💻"),
            User(id=3, name="王五", email="wangwu@cmf.com", avatar="👷"),
        ]
        
        self.projects = [
            Project(
                id=1,
                code="PJ-2024-X1",
                name="Flagship Phone Unibody",
                pm_id=1,
                pm_name="张三",
                current_stage=ProjectStage.DVT,
                overall_status=RiskLevel.MEDIUM,
                progress=65,
                parts=[],
                milestones=[]
            ),
            Project(
                id=2,
                code="PJ-2024-A2",
                name="Wireless Earbuds Pro",
                pm_id=2,
                pm_name="李四",
                current_stage=ProjectStage.PVT,
                overall_status=RiskLevel.LOW,
                progress=85,
                parts=[],
                milestones=[]
            ),
            Project(
                id=3,
                code="PJ-2024-B3",
                name="Smart Watch Ultra",
                pm_id=1,
                pm_name="张三",
                current_stage=ProjectStage.EVT,
                overall_status=RiskLevel.HIGH,
                progress=35,
                parts=[],
                milestones=[]
            ),
        ]
        
        self.parts = [
            Part(id=1, project_id=1, name="中框阳极氧化", process="CNC + 阳极", 
                 primary_supplier="富士康", secondary_supplier="比亚迪", 
                 risk_level=RiskLevel.MEDIUM, progress=70),
            Part(id=2, project_id=1, name="后盖 AG 玻璃", process="热弯 + AG", 
                 primary_supplier="蓝思科技", secondary_supplier=None, 
                 risk_level=RiskLevel.HIGH, progress=45),
            Part(id=3, project_id=1, name="按键注塑", process="双色注塑", 
                 primary_supplier="长盈精密", secondary_supplier="领益智造", 
                 risk_level=RiskLevel.LOW, progress=90),
            Part(id=4, project_id=2, name="充电盒外壳", process="UV 喷涂", 
                 primary_supplier="歌尔股份", secondary_supplier=None, 
                 risk_level=RiskLevel.LOW, progress=88),
            Part(id=5, project_id=3, name="表壳陶瓷", process="MIM + 抛光", 
                 primary_supplier="潮州三环", secondary_supplier="风华高科", 
                 risk_level=RiskLevel.HIGH, progress=30),
        ]
        
        self.milestones = [
            Milestone(id=1, project_id=1, stage=ProjectStage.T0, 
                     planned_date="2024-01-15", actual_date="2024-01-18", status="completed"),
            Milestone(id=2, project_id=1, stage=ProjectStage.T1, 
                     planned_date="2024-02-20", actual_date="2024-02-22", status="completed"),
            Milestone(id=3, project_id=1, stage=ProjectStage.EVT, 
                     planned_date="2024-03-10", actual_date="2024-03-12", status="completed"),
            Milestone(id=4, project_id=1, stage=ProjectStage.DVT, 
                     planned_date="2024-04-15", actual_date=None, status="in_progress"),
            Milestone(id=5, project_id=1, stage=ProjectStage.PVT, 
                     planned_date="2024-05-20", actual_date=None, status="pending"),
            Milestone(id=6, project_id=1, stage=ProjectStage.MP, 
                     planned_date="2024-06-30", actual_date=None, status="pending"),
        ]
        
        self.tasks = [
            Task(id=1, project_id=1, title="确认 AG 玻璃良率改善方案", 
                 priority=TaskPriority.P0, due_date="2024-03-28", 
                 assignee_id=1, assignee_name="张三", status=TaskStatus.IN_PROGRESS),
            Task(id=2, project_id=1, title="评审 CNC 夹具设计方案", 
                 priority=TaskPriority.P1, due_date="2024-03-29", 
                 assignee_id=3, assignee_name="王五", status=TaskStatus.TODO),
            Task(id=3, project_id=2, title="充电盒气密性测试报告", 
                 priority=TaskPriority.P2, due_date="2024-03-30", 
                 assignee_id=2, assignee_name="李四", status=TaskStatus.DONE),
            Task(id=4, project_id=3, title="陶瓷表壳开裂问题分析", 
                 priority=TaskPriority.P0, due_date="2024-03-27", 
                 assignee_id=1, assignee_name="张三", status=TaskStatus.IN_PROGRESS),
        ]
    
    def get_dashboard(self) -> DashboardOverview:
        today = datetime.now().strftime("%Y-%m-%d")
        today_tasks = [t for t in self.tasks if t.due_date == today or t.due_date >= today]
        high_risk = len([p for p in self.parts if p.risk_level == RiskLevel.HIGH])
        
        return DashboardOverview(
            total_projects=len(self.projects),
            active_projects=len([p for p in self.projects if p.current_stage != ProjectStage.MP]),
            high_risk_parts=high_risk,
            today_tasks=len(today_tasks),
            projects=self.projects,
            tasks=today_tasks[:5]
        )
    
    def get_project(self, project_id: int) -> Optional[Project]:
        for proj in self.projects:
            if proj.id == project_id:
                proj.parts = [p for p in self.parts if p.project_id == project_id]
                proj.milestones = [m for m in self.milestones if m.project_id == project_id]
                return proj
        return None
    
    def create_project(self, req: CreateProjectRequest) -> Project:
        new_id = max(p.id for p in self.projects) + 1 if self.projects else 1
        pm = next((u for u in self.users if u.id == req.pm_id), self.users[0])
        new_project = Project(
            id=new_id,
            code=req.code,
            name=req.name,
            pm_id=req.pm_id,
            pm_name=pm.name,
            current_stage=req.current_stage,
            overall_status=RiskLevel.LOW,
            progress=0
        )
        self.projects.append(new_project)
        return new_project
    
    def update_part_status(self, part_id: int, req: UpdatePartStatusRequest) -> Optional[Part]:
        for part in self.parts:
            if part.id == part_id:
                if req.risk_level is not None:
                    part.risk_level = req.risk_level
                if req.status_note is not None:
                    part.status_note = req.status_note
                if req.progress is not None:
                    part.progress = req.progress
                return part
        return None
    
    def create_task(self, req: CreateTaskRequest) -> Task:
        new_id = max(t.id for t in self.tasks) + 1 if self.tasks else 1
        assignee = next((u for u in self.users if u.id == req.assignee_id), self.users[0])
        new_task = Task(
            id=new_id,
            project_id=req.project_id,
            title=req.title,
            priority=req.priority,
            due_date=req.due_date,
            assignee_id=req.assignee_id,
            assignee_name=assignee.name
        )
        self.tasks.append(new_task)
        return new_task
    
    def delete_task(self, task_id: int) -> bool:
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                return True
        return False
    
    def get_users(self) -> List[User]:
        return self.users

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="CMF Supply Chain Management System",
    description="Color, Material, Finish Project Management API",
    version="2.0.0"
)

mock_service = MockDataService()

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0", "timestamp": datetime.now().isoformat()}

@app.get("/api/system/time")
async def get_server_time():
    """Get server time for frontend synchronization"""
    now = datetime.now()
    return {
        "server_time": now.isoformat(),
        "timestamp": int(now.timestamp() * 1000),
        "timezone": "Asia/Shanghai"
    }

@app.get("/api/dashboard/overview", response_model=DashboardOverview)
async def get_dashboard_overview():
    """Get dashboard overview with projects, stats, and today's tasks"""
    return mock_service.get_dashboard()

@app.get("/api/projects", response_model=List[Project])
async def get_projects():
    """Get all projects"""
    return mock_service.projects

@app.get("/api/projects/{project_id}", response_model=Project)
async def get_project(project_id: int):
    """Get project details with parts and milestones"""
    project = mock_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.post("/api/projects", response_model=Project)
async def create_project(req: CreateProjectRequest):
    """Create a new project"""
    return mock_service.create_project(req)

@app.get("/api/parts", response_model=List[Part])
async def get_parts(project_id: Optional[int] = None):
    """Get parts list, optionally filtered by project"""
    if project_id:
        return [p for p in mock_service.parts if p.project_id == project_id]
    return mock_service.parts

@app.patch("/api/parts/{part_id}/status", response_model=Part)
async def update_part_status(part_id: int, req: UpdatePartStatusRequest):
    """Update part risk status or progress note"""
    part = mock_service.update_part_status(part_id, req)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    return part

@app.get("/api/tasks", response_model=List[Task])
async def get_tasks(project_id: Optional[int] = None, status: Optional[TaskStatus] = None):
    """Get tasks list with optional filters"""
    tasks = mock_service.tasks
    if project_id:
        tasks = [t for t in tasks if t.project_id == project_id]
    if status:
        tasks = [t for t in tasks if t.status == status]
    return tasks

@app.post("/api/tasks", response_model=Task)
async def create_task(req: CreateTaskRequest):
    """Create a new task"""
    return mock_service.create_task(req)

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int):
    """Delete a task"""
    success = mock_service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully", "id": task_id}

@app.patch("/api/tasks/{task_id}/status", response_model=Task)
async def update_task_status(task_id: int, status: TaskStatus):
    """Update task status"""
    for task in mock_service.tasks:
        if task.id == task_id:
            task.status = status
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.get("/api/users", response_model=List[User])
async def get_users():
    """Get all users"""
    return mock_service.get_users()

# Serve static files (frontend HTML)
static_path = os.path.join(current_dir, "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(static_path, "mainweb.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
