"""
CMF Supply Chain Management System - Main Application
Version: 2.0.0 (Fixed for Production Deployment)
"""
import sys
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn

# Ensure current directory is in path for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# ============================================================================
# ENUMS (No external dependencies)
# ============================================================================

class ProjectStage(str, Enum):
    PROTOTYPE = "PROTOTYPE"
    T0 = "T0"
    T1 = "T1"
    T2 = "T2"
    EVT = "EVT"
    DVT = "DVT"
    PVT = "PVT"
    MP = "MP"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskPriority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"

# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class UserSchema(BaseModel):
    id: int
    name: str
    email: str
    avatar: Optional[str] = None
    role: str = "member"

class SupplierSchema(BaseModel):
    id: int
    name: str
    type: str = "primary"  # primary or secondary
    contact: Optional[str] = None
    rating: float = 5.0

class PartSchema(BaseModel):
    id: int
    project_id: int
    name: str
    process: str
    risk_level: RiskLevel = RiskLevel.LOW
    status_note: Optional[str] = None
    suppliers: List[SupplierSchema] = []

class MilestoneSchema(BaseModel):
    id: int
    project_id: int
    stage: ProjectStage
    planned_date: str
    actual_date: Optional[str] = None
    status: str = "planned"  # planned, completed, delayed

class TaskSchema(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    priority: TaskPriority
    due_date: str
    assignee_id: Optional[int] = None
    assignee_name: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    created_at: str

class ProjectSchema(BaseModel):
    id: int
    code: str
    name: str
    pm_id: int
    pm_name: str
    current_stage: ProjectStage
    overall_status: RiskLevel = RiskLevel.LOW
    parts_count: int = 0
    tasks_count: int = 0
    created_at: str
    updated_at: str

class DashboardOverviewSchema(BaseModel):
    total_projects: int
    active_projects: int
    high_risk_parts: int
    pending_tasks: int
    today_tasks: List[TaskSchema] = []
    recent_projects: List[ProjectSchema] = []

class CreateProjectSchema(BaseModel):
    code: str
    name: str
    pm_id: int
    current_stage: ProjectStage = ProjectStage.PROTOTYPE

class UpdatePartStatusSchema(BaseModel):
    risk_level: Optional[RiskLevel] = None
    status_note: Optional[str] = None

class CreateTaskSchema(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.P2
    due_date: str
    assignee_id: Optional[int] = None

# ============================================================================
# MOCK DATA SERVICE (No database dependency for quick start)
# ============================================================================

class MockDataService:
    """In-memory mock data service for immediate deployment"""
    
    def __init__(self):
        self.users = [
            {"id": 1, "name": "张三", "email": "zhangsan@cmf.com", "avatar": "👨‍💼", "role": "pm"},
            {"id": 2, "name": "李四", "email": "lisi@cmf.com", "avatar": "👩‍🔬", "role": "engineer"},
            {"id": 3, "name": "王五", "email": "wangwu@cmf.com", "avatar": "👨‍🔧", "role": "supplier_mgr"},
            {"id": 4, "name": "赵六", "email": "zhaoliu@cmf.com", "avatar": "👩‍💻", "role": "member"},
        ]
        
        self.projects = [
            {
                "id": 1,
                "code": "PJ-2023-X1",
                "name": "Flagship Phone Unibody",
                "pm_id": 1,
                "pm_name": "张三",
                "current_stage": ProjectStage.DVT,
                "overall_status": RiskLevel.MEDIUM,
                "created_at": "2023-06-15T00:00:00Z",
                "updated_at": "2024-01-10T08:30:00Z"
            },
            {
                "id": 2,
                "code": "PJ-2023-A5",
                "name": "Wireless Earbuds Pro",
                "pm_id": 2,
                "pm_name": "李四",
                "current_stage": ProjectStage.PVT,
                "overall_status": RiskLevel.LOW,
                "created_at": "2023-08-20T00:00:00Z",
                "updated_at": "2024-01-09T14:20:00Z"
            },
            {
                "id": 3,
                "code": "PJ-2024-M2",
                "name": "Smart Watch Ceramic Bezel",
                "pm_id": 1,
                "pm_name": "张三",
                "current_stage": ProjectStage.EVT,
                "overall_status": RiskLevel.HIGH,
                "created_at": "2024-01-05T00:00:00Z",
                "updated_at": "2024-01-10T09:15:00Z"
            },
            {
                "id": 4,
                "code": "PJ-2024-T7",
                "name": "Tablet Glass Back Panel",
                "pm_id": 3,
                "pm_name": "王五",
                "current_stage": ProjectStage.T1,
                "overall_status": RiskLevel.LOW,
                "created_at": "2024-01-08T00:00:00Z",
                "updated_at": "2024-01-10T07:45:00Z"
            }
        ]
        
        self.parts = [
            {
                "id": 1,
                "project_id": 1,
                "name": "Unibody Shell",
                "process": "CNC + Anodizing",
                "risk_level": RiskLevel.MEDIUM,
                "status_note": "Color consistency needs improvement",
                "suppliers": [
                    {"id": 1, "name": "Foxconn", "type": "primary", "contact": "sz@foxconn.com", "rating": 4.8},
                    {"id": 2, "name": "Luxshare", "type": "secondary", "contact": "dg@luxshare.com", "rating": 4.5}
                ]
            },
            {
                "id": 2,
                "project_id": 1,
                "name": "Camera Lens Ring",
                "process": "Diamond Cutting + PVD",
                "risk_level": RiskLevel.HIGH,
                "status_note": "Tooling delay, risk of schedule slip",
                "suppliers": [
                    {"id": 3, "name": "Goertek", "type": "primary", "contact": "qd@goertek.com", "rating": 4.6}
                ]
            },
            {
                "id": 3,
                "project_id": 1,
                "name": "Button Components",
                "process": "MIM + Brushing",
                "risk_level": RiskLevel.LOW,
                "status_note": "Mass production ready",
                "suppliers": [
                    {"id": 4, "name": "AAC Technologies", "type": "primary", "contact": "sz@aactech.com", "rating": 4.9},
                    {"id": 5, "name": "Lengyi", "type": "secondary", "contact": "dg@lengyi.com", "rating": 4.3}
                ]
            },
            {
                "id": 4,
                "project_id": 2,
                "name": "Earbud Housing",
                "process": "Injection Molding + UV Coating",
                "risk_level": RiskLevel.LOW,
                "status_note": "Verified",
                "suppliers": [
                    {"id": 6, "name": "Amkor", "type": "primary", "contact": "ph@amkor.com", "rating": 4.7}
                ]
            },
            {
                "id": 5,
                "project_id": 3,
                "name": "Ceramic Bezel",
                "process": "Powder Metallurgy + Polishing",
                "risk_level": RiskLevel.CRITICAL,
                "status_note": "Yield rate only 65%, critical risk",
                "suppliers": [
                    {"id": 7, "name": "Kyocera", "type": "primary", "contact": "jp@kyocera.com", "rating": 4.9}
                ]
            }
        ]
        
        self.milestones = [
            {"id": 1, "project_id": 1, "stage": ProjectStage.PROTOTYPE, "planned_date": "2023-07-01", "actual_date": "2023-07-03", "status": "completed"},
            {"id": 2, "project_id": 1, "stage": ProjectStage.T0, "planned_date": "2023-08-15", "actual_date": "2023-08-14", "status": "completed"},
            {"id": 3, "project_id": 1, "stage": ProjectStage.T1, "planned_date": "2023-09-30", "actual_date": "2023-10-05", "status": "completed"},
            {"id": 4, "project_id": 1, "stage": ProjectStage.EVT, "planned_date": "2023-11-15", "actual_date": "2023-11-20", "status": "completed"},
            {"id": 5, "project_id": 1, "stage": ProjectStage.DVT, "planned_date": "2024-01-10", "actual_date": None, "status": "in_progress"},
            {"id": 6, "project_id": 1, "stage": ProjectStage.PVT, "planned_date": "2024-03-01", "actual_date": None, "status": "planned"},
            {"id": 7, "project_id": 1, "stage": ProjectStage.MP, "planned_date": "2024-05-15", "actual_date": None, "status": "planned"},
            {"id": 8, "project_id": 2, "stage": ProjectStage.DVT, "planned_date": "2023-12-20", "actual_date": "2023-12-18", "status": "completed"},
            {"id": 9, "project_id": 2, "stage": ProjectStage.PVT, "planned_date": "2024-01-15", "actual_date": None, "status": "in_progress"},
            {"id": 10, "project_id": 3, "stage": ProjectStage.T0, "planned_date": "2024-01-20", "actual_date": None, "status": "delayed"},
        ]
        
        self.tasks = [
            {
                "id": 1,
                "project_id": 1,
                "title": "Review DVT sample quality",
                "description": "Check color consistency and surface finish",
                "priority": TaskPriority.P0,
                "due_date": "2024-01-12",
                "assignee_id": 2,
                "assignee_name": "李四",
                "status": TaskStatus.IN_PROGRESS,
                "created_at": "2024-01-08T09:00:00Z"
            },
            {
                "id": 2,
                "project_id": 1,
                "title": "Follow up with camera ring supplier",
                "description": "Expedite tooling completion",
                "priority": TaskPriority.P0,
                "due_date": "2024-01-11",
                "assignee_id": 3,
                "assignee_name": "王五",
                "status": TaskStatus.TODO,
                "created_at": "2024-01-09T10:30:00Z"
            },
            {
                "id": 3,
                "project_id": 3,
                "title": "Analyze ceramic bezel yield issue",
                "description": "Root cause analysis for low yield rate",
                "priority": TaskPriority.P0,
                "due_date": "2024-01-13",
                "assignee_id": 2,
                "assignee_name": "李四",
                "status": TaskStatus.TODO,
                "created_at": "2024-01-10T08:00:00Z"
            },
            {
                "id": 4,
                "project_id": 2,
                "title": "Prepare PVT report",
                "description": "Compile test results and quality metrics",
                "priority": TaskPriority.P1,
                "due_date": "2024-01-15",
                "assignee_id": 4,
                "assignee_name": "赵六",
                "status": TaskStatus.IN_PROGRESS,
                "created_at": "2024-01-07T14:00:00Z"
            },
            {
                "id": 5,
                "project_id": 4,
                "title": "Review T1 sample feedback",
                "description": "Collect and analyze customer feedback",
                "priority": TaskPriority.P2,
                "due_date": "2024-01-18",
                "assignee_id": 1,
                "assignee_name": "张三",
                "status": TaskStatus.TODO,
                "created_at": "2024-01-10T09:30:00Z"
            }
        ]
        
        self.next_ids = {
            "projects": 5,
            "parts": 6,
            "milestones": 11,
            "tasks": 6
        }
    
    def get_users(self) -> List[UserSchema]:
        return [UserSchema(**u) for u in self.users]
    
    def get_user(self, user_id: int) -> Optional[UserSchema]:
        for u in self.users:
            if u["id"] == user_id:
                return UserSchema(**u)
        return None
    
    def get_projects(self) -> List[ProjectSchema]:
        result = []
        for p in self.projects:
            parts_count = sum(1 for part in self.parts if part["project_id"] == p["id"])
            tasks_count = sum(1 for t in self.tasks if t["project_id"] == p["id"] and t["status"] != TaskStatus.DONE)
            proj = p.copy()
            proj["parts_count"] = parts_count
            proj["tasks_count"] = tasks_count
            result.append(ProjectSchema(**proj))
        return result
    
    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        for p in self.projects:
            if p["id"] == project_id:
                parts = [part for part in self.parts if part["project_id"] == project_id]
                milestones = [m for m in self.milestones if m["project_id"] == project_id]
                tasks = [t for t in self.tasks if t["project_id"] == project_id]
                return {
                    **p,
                    "parts": parts,
                    "milestones": milestones,
                    "tasks": tasks
                }
        return None
    
    def create_project(self, data: CreateProjectSchema) -> ProjectSchema:
        new_id = self.next_ids["projects"]
        self.next_ids["projects"] += 1
        
        pm = self.get_user(data.pm_id)
        new_project = {
            "id": new_id,
            "code": data.code,
            "name": data.name,
            "pm_id": data.pm_id,
            "pm_name": pm.name if pm else "Unknown",
            "current_stage": data.current_stage,
            "overall_status": RiskLevel.LOW,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        self.projects.append(new_project)
        
        return ProjectSchema(
            **new_project,
            parts_count=0,
            tasks_count=0
        )
    
    def update_part_status(self, part_id: int, data: UpdatePartStatusSchema) -> Optional[Dict]:
        for part in self.parts:
            if part["id"] == part_id:
                if data.risk_level is not None:
                    part["risk_level"] = data.risk_level
                if data.status_note is not None:
                    part["status_note"] = data.status_note
                return part
        return None
    
    def get_tasks(self, project_id: Optional[int] = None, status: Optional[TaskStatus] = None) -> List[TaskSchema]:
        result = self.tasks
        if project_id is not None:
            result = [t for t in result if t["project_id"] == project_id]
        if status is not None:
            result = [t for t in result if t["status"] == status]
        return [TaskSchema(**t) for t in result]
    
    def get_task(self, task_id: int) -> Optional[TaskSchema]:
        for t in self.tasks:
            if t["id"] == task_id:
                return TaskSchema(**t)
        return None
    
    def create_task(self, data: CreateTaskSchema) -> TaskSchema:
        new_id = self.next_ids["tasks"]
        self.next_ids["tasks"] += 1
        
        assignee = self.get_user(data.assignee_id) if data.assignee_id else None
        
        new_task = {
            "id": new_id,
            "project_id": data.project_id,
            "title": data.title,
            "description": data.description,
            "priority": data.priority,
            "due_date": data.due_date,
            "assignee_id": data.assignee_id,
            "assignee_name": assignee.name if assignee else None,
            "status": TaskStatus.TODO,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        self.tasks.append(new_task)
        return TaskSchema(**new_task)
    
    def delete_task(self, task_id: int) -> bool:
        for i, t in enumerate(self.tasks):
            if t["id"] == task_id:
                self.tasks.pop(i)
                return True
        return False
    
    def update_task_status(self, task_id: int, status: TaskStatus) -> Optional[TaskSchema]:
        for t in self.tasks:
            if t["id"] == task_id:
                t["status"] = status
                return TaskSchema(**t)
        return None
    
    def get_dashboard_overview(self) -> DashboardOverviewSchema:
        today = datetime.utcnow().date()
        today_str = today.isoformat()
        
        today_tasks = [
            TaskSchema(**t) for t in self.tasks 
            if t["due_date"] == today_str and t["status"] != TaskStatus.DONE
        ]
        
        recent_projects = self.get_projects()[:4]
        
        high_risk_parts = sum(
            1 for p in self.parts 
            if p["risk_level"] in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
        
        pending_tasks = sum(
            1 for t in self.tasks 
            if t["status"] in [TaskStatus.TODO, TaskStatus.IN_PROGRESS]
        )
        
        return DashboardOverviewSchema(
            total_projects=len(self.projects),
            active_projects=sum(1 for p in self.projects if p["current_stage"] != ProjectStage.MP),
            high_risk_parts=high_risk_parts,
            pending_tasks=pending_tasks,
            today_tasks=today_tasks,
            recent_projects=recent_projects
        )

# Initialize mock data service
mock_data = MockDataService()

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="CMF Supply Chain Management System",
    description="Backend API for CMF Project and Supply Chain Management",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - serves the frontend HTML"""
    return FileResponse(
        path=os.path.join(os.path.dirname(__file__), "index.html"),
        media_type="text/html"
    )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "2.0.0"
    }

@app.get("/api/system/time")
async def get_system_time():
    """Get server time for frontend synchronization"""
    now = datetime.utcnow()
    return {
        "server_time": now.isoformat() + "Z",
        "timestamp": int(now.timestamp() * 1000),
        "timezone": "UTC"
    }

@app.get("/api/dashboard/overview", response_model=DashboardOverviewSchema)
async def get_dashboard_overview():
    """Get dashboard overview with aggregated data"""
    return mock_data.get_dashboard_overview()

@app.get("/api/users", response_model=List[UserSchema])
async def get_users():
    """Get all users"""
    return mock_data.get_users()

@app.get("/api/users/{user_id}", response_model=UserSchema)
async def get_user(user_id: int):
    """Get user by ID"""
    user = mock_data.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/api/projects", response_model=List[ProjectSchema])
async def get_projects():
    """Get all projects"""
    return mock_data.get_projects()

@app.get("/api/projects/{project_id}")
async def get_project(project_id: int):
    """Get project details with parts, milestones, and tasks"""
    project = mock_data.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.post("/api/projects", response_model=ProjectSchema)
async def create_project(data: CreateProjectSchema):
    """Create a new project"""
    return mock_data.create_project(data)

@app.patch("/api/parts/{part_id}/status")
async def update_part_status(part_id: int, data: UpdatePartStatusSchema):
    """Update part risk level and status note"""
    part = mock_data.update_part_status(part_id, data)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    return part

@app.get("/api/tasks", response_model=List[TaskSchema])
async def get_tasks(
    project_id: Optional[int] = None,
    status: Optional[TaskStatus] = None
):
    """Get tasks with optional filters"""
    return mock_data.get_tasks(project_id, status)

@app.post("/api/tasks", response_model=TaskSchema)
async def create_task(data: CreateTaskSchema):
    """Create a new task"""
    return mock_data.create_task(data)

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int):
    """Delete a task"""
    success = mock_data.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully", "task_id": task_id}

@app.patch("/api/tasks/{task_id}/status")
async def update_task_status(task_id: int, status: TaskStatus):
    """Update task status"""
    task = mock_data.update_task_status(task_id, status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=2,
        reload=False
    )
