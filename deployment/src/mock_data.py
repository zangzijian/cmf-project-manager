"""
CMF 供应链项目管理系统 - Mock 数据服务
当数据库不可用时，提供内存中的 Mock 数据
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import copy


# ============================================
# Mock 数据 - 与前端 HTML 展示内容匹配
# ============================================

MOCK_USERS = [
    {
        "id": "user-alex-001",
        "email": "alex.chen@cmf.com",
        "name": "Alex Chen",
        "avatar_initial": "A",
        "role": "PM",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    },
    {
        "id": "user-sarah-002",
        "email": "sarah.li@cmf.com",
        "name": "Sarah Li",
        "avatar_initial": "S",
        "role": "PM",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
]

MOCK_PROJECTS = [
    {
        "id": "proj-x1-001",
        "code": "PJ-2023-X1",
        "name": "Flagship Phone Unibody",
        "description": "旗舰手机一体化机身项目",
        "current_stage": "T1",
        "overall_status": "HIGH",
        "pm_id": "user-alex-001",
        "start_date": "2023-09-01T00:00:00Z",
        "end_date": "2024-02-01T00:00:00Z",
        "created_at": "2023-09-01T00:00:00Z",
        "updated_at": "2023-10-24T00:00:00Z"
    },
    {
        "id": "proj-w2-002",
        "code": "PJ-2023-W2",
        "name": "Smart Watch Band - Leather",
        "description": "智能手表真皮表带项目",
        "current_stage": "DVT",
        "overall_status": "LOW",
        "pm_id": "user-sarah-002",
        "start_date": "2023-08-01T00:00:00Z",
        "end_date": "2024-01-15T00:00:00Z",
        "created_at": "2023-08-01T00:00:00Z",
        "updated_at": "2023-10-24T00:00:00Z"
    }
]

MOCK_PARTS = [
    # 项目 X1 的部件
    {
        "id": "part-x1-001",
        "project_id": "proj-x1-001",
        "name": "A 面铝合金中框",
        "structure": "CNC + 阳极氧化",
        "process": "CNC 精密加工 + 阳极氧化表面处理",
        "risk_level": "HIGH",
        "risk_type": "DELAY",
        "progress_note": "模具修改中，预计延期 3 天",
        "is_critical": True,
        "actual_date": None,
        "created_at": "2023-09-01T00:00:00Z",
        "updated_at": "2023-10-24T00:00:00Z"
    },
    {
        "id": "part-x1-002",
        "project_id": "proj-x1-001",
        "name": "摄像头装饰圈",
        "structure": "PVD 镀膜",
        "process": "物理气相沉积镀膜工艺",
        "risk_level": "MEDIUM",
        "risk_type": "PROCESS",
        "progress_note": "新颜色样板确认中",
        "is_critical": False,
        "actual_date": None,
        "created_at": "2023-09-01T00:00:00Z",
        "updated_at": "2023-10-24T00:00:00Z"
    },
    {
        "id": "part-x1-003",
        "project_id": "proj-x1-001",
        "name": "玻璃后盖 (AG)",
        "structure": "热弯 + 丝印",
        "process": "热弯成型 + 丝网印刷",
        "risk_level": "LOW",
        "risk_type": None,
        "progress_note": "首批样品已签收",
        "is_critical": True,
        "actual_date": None,
        "created_at": "2023-09-01T00:00:00Z",
        "updated_at": "2023-10-24T00:00:00Z"
    },
    # 项目 W2 的部件
    {
        "id": "part-w2-001",
        "project_id": "proj-w2-002",
        "name": "真皮表带 (小牛皮)",
        "structure": "缝制 + 油边",
        "process": "手工缝制 + 精细油边",
        "risk_level": "LOW",
        "risk_type": None,
        "progress_note": "大货生产进行中",
        "is_critical": True,
        "actual_date": None,
        "created_at": "2023-08-01T00:00:00Z",
        "updated_at": "2023-10-24T00:00:00Z"
    },
    {
        "id": "part-w2-002",
        "project_id": "proj-w2-002",
        "name": "不锈钢扣具",
        "structure": "316L 精铸 + 抛光",
        "process": "精密铸造 + 镜面抛光",
        "risk_level": "LOW",
        "risk_type": None,
        "progress_note": "等待表面处理确认",
        "is_critical": False,
        "actual_date": None,
        "created_at": "2023-08-01T00:00:00Z",
        "updated_at": "2023-10-24T00:00:00Z"
    }
]

MOCK_SUPPLIERS = [
    # 项目 X1 部件的供应商
    {"id": "sup-001", "part_id": "part-x1-001", "name": "Foxconn", "type": "PRIMARY", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
    {"id": "sup-002", "part_id": "part-x1-001", "name": "Luxshare", "type": "SECONDARY", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
    {"id": "sup-003", "part_id": "part-x1-002", "name": "BYD", "type": "PRIMARY", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
    {"id": "sup-004", "part_id": "part-x1-003", "name": "Lens Tech", "type": "PRIMARY", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
    {"id": "sup-005", "part_id": "part-x1-003", "name": "Biel", "type": "SECONDARY", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
    # 项目 W2 部件的供应商
    {"id": "sup-006", "part_id": "part-w2-001", "name": "Hermès Supplier A", "type": "PRIMARY", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-08-01T00:00:00Z"},
    {"id": "sup-007", "part_id": "part-w2-001", "name": "Local Leather Co.", "type": "SECONDARY", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-08-01T00:00:00Z"},
    {"id": "sup-008", "part_id": "part-w2-002", "name": "Shenzhen Metal", "type": "PRIMARY", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-08-01T00:00:00Z"}
]

MOCK_MILESTONES = [
    # 项目 X1 里程碑
    {"id": "ms-x1-001", "project_id": "proj-x1-001", "stage": "PROTOTYPE", "planned_date": "2023-09-01T00:00:00Z", "actual_date": "2023-09-01T00:00:00Z", "status": "completed", "notes": "", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
    {"id": "ms-x1-002", "project_id": "proj-x1-001", "stage": "T0", "planned_date": "2023-10-01T00:00:00Z", "actual_date": "2023-10-01T00:00:00Z", "status": "completed", "notes": "", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-10-01T00:00:00Z"},
    {"id": "ms-x1-003", "project_id": "proj-x1-001", "stage": "T1", "planned_date": "2023-10-20T00:00:00Z", "actual_date": "2023-10-20T00:00:00Z", "status": "completed", "notes": "", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-10-20T00:00:00Z"},
    {"id": "ms-x1-004", "project_id": "proj-x1-001", "stage": "T2", "planned_date": "2023-11-15T00:00:00Z", "actual_date": None, "status": "pending", "notes": "", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
    {"id": "ms-x1-005", "project_id": "proj-x1-001", "stage": "DVT", "planned_date": "2023-12-01T00:00:00Z", "actual_date": None, "status": "pending", "notes": "", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
    {"id": "ms-x1-006", "project_id": "proj-x1-001", "stage": "PVT", "planned_date": "2024-01-10T00:00:00Z", "actual_date": None, "status": "pending", "notes": "", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
    {"id": "ms-x1-007", "project_id": "proj-x1-001", "stage": "MP", "planned_date": "2024-02-01T00:00:00Z", "actual_date": None, "status": "pending", "notes": "", "created_at": "2023-09-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
    # 项目 W2 里程碑
    {"id": "ms-w2-001", "project_id": "proj-w2-002", "stage": "PROTOTYPE", "planned_date": "2023-08-01T00:00:00Z", "actual_date": "2023-08-01T00:00:00Z", "status": "completed", "notes": "", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-08-01T00:00:00Z"},
    {"id": "ms-w2-002", "project_id": "proj-w2-002", "stage": "T0", "planned_date": "2023-09-01T00:00:00Z", "actual_date": "2023-09-01T00:00:00Z", "status": "completed", "notes": "", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-09-01T00:00:00Z"},
    {"id": "ms-w2-003", "project_id": "proj-w2-002", "stage": "T1", "planned_date": "2023-10-01T00:00:00Z", "actual_date": "2023-10-01T00:00:00Z", "status": "completed", "notes": "", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-10-01T00:00:00Z"},
    {"id": "ms-w2-004", "project_id": "proj-w2-002", "stage": "DVT", "planned_date": "2023-11-01T00:00:00Z", "actual_date": "2023-11-01T00:00:00Z", "status": "completed", "notes": "", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-11-01T00:00:00Z"},
    {"id": "ms-w2-005", "project_id": "proj-w2-002", "stage": "PVT", "planned_date": "2023-12-15T00:00:00Z", "actual_date": None, "status": "pending", "notes": "", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-08-01T00:00:00Z"},
    {"id": "ms-w2-006", "project_id": "proj-w2-002", "stage": "MP", "planned_date": "2024-01-15T00:00:00Z", "actual_date": None, "status": "pending", "notes": "", "created_at": "2023-08-01T00:00:00Z", "updated_at": "2023-08-01T00:00:00Z"}
]

# 动态生成今日和明日的日期
now = datetime.now()
today_14 = now.replace(hour=14, minute=0, second=0, microsecond=0)
today_17 = now.replace(hour=17, minute=0, second=0, microsecond=0)
tomorrow_10 = (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)

MOCK_TASKS = [
    {
        "id": "task-001",
        "project_id": "proj-x1-001",
        "title": "确认 A 面中框阳极色差限度样",
        "description": "需要与供应商确认阳极氧化色差的可接受范围",
        "priority": "P0",
        "due_date": today_14.isoformat(),
        "status": "PENDING",
        "assignee_ids": ["user-alex-001"],
        "completed_at": None,
        "created_at": "2023-10-20T00:00:00Z",
        "updated_at": "2023-10-20T00:00:00Z"
    },
    {
        "id": "task-002",
        "project_id": "proj-x1-001",
        "title": "审核摄像头圈 PVD 新工艺报告",
        "description": "审核新 PVD 工艺的可行性报告",
        "priority": "P1",
        "due_date": today_17.isoformat(),
        "status": "PENDING",
        "assignee_ids": ["user-alex-001", "user-sarah-002"],
        "completed_at": None,
        "created_at": "2023-10-20T00:00:00Z",
        "updated_at": "2023-10-20T00:00:00Z"
    },
    {
        "id": "task-003",
        "project_id": "proj-w2-002",
        "title": "签署表带大货生产同意书 (PPAP)",
        "description": "签署 PPAP 文件，批准大货生产",
        "priority": "P2",
        "due_date": tomorrow_10.isoformat(),
        "status": "PENDING",
        "assignee_ids": ["user-sarah-002"],
        "completed_at": None,
        "created_at": "2023-10-20T00:00:00Z",
        "updated_at": "2023-10-20T00:00:00Z"
    },
    {
        "id": "task-004",
        "project_id": None,
        "title": "更新供应商联络人列表",
        "description": "季度供应商联络人信息更新",
        "priority": "P3",
        "due_date": "2023-10-20T00:00:00Z",
        "status": "COMPLETED",
        "assignee_ids": ["user-sarah-002"],
        "completed_at": "2023-10-20T00:00:00Z",
        "created_at": "2023-10-15T00:00:00Z",
        "updated_at": "2023-10-20T00:00:00Z"
    }
]


class MockDataService:
    """Mock 数据服务类 - 提供与真实 API 相同的数据结构"""
    
    def __init__(self):
        self.users = copy.deepcopy(MOCK_USERS)
        self.projects = copy.deepcopy(MOCK_PROJECTS)
        self.parts = copy.deepcopy(MOCK_PARTS)
        self.suppliers = copy.deepcopy(MOCK_SUPPLIERS)
        self.milestones = copy.deepcopy(MOCK_MILESTONES)
        self.tasks = copy.deepcopy(MOCK_TASKS)
    
    def get_dashboard_overview(self) -> Dict[str, Any]:
        """获取仪表盘概览数据"""
        total_projects = len(self.projects)
        ongoing_projects = sum(1 for p in self.projects if p['current_stage'] != 'MP')
        high_risk_parts = sum(1 for p in self.parts if p['risk_level'] in ['HIGH', 'CRITICAL'])
        
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        today_tasks = [
            t for t in self.tasks 
            if today_start <= datetime.fromisoformat(t['due_date'].replace('Z', '+00:00')).replace(tzinfo=None) < today_end
            and t['status'] != 'COMPLETED'
        ]
        
        pending_tasks = sum(1 for t in self.tasks if t['status'] == 'PENDING')
        
        # 构建完整的项目数据（包含关联数据）
        projects_with_relations = []
        for proj in self.projects:
            pm = next((u for u in self.users if u['id'] == proj['pm_id']), None)
            parts = [p for p in self.parts if p['project_id'] == proj['id']]
            parts_with_suppliers = []
            for part in parts:
                suppliers = [s for s in self.suppliers if s['part_id'] == part['id']]
                parts_with_suppliers.append({**part, 'suppliers': suppliers})
            
            milestones = [m for m in self.milestones if m['project_id'] == proj['id']]
            
            projects_with_relations.append({
                **proj,
                'pm': pm,
                'parts': parts_with_suppliers,
                'milestones': milestones,
                'tasks': []
            })
        
        # 构建任务数据（包含指派人）
        tasks_with_assignees = []
        for task in today_tasks:
            assignees = [u for u in self.users if u['id'] in task['assignee_ids']]
            tasks_with_assignees.append({
                **task,
                'assignees': assignees
            })
        
        return {
            "total_projects": total_projects,
            "ongoing_projects": ongoing_projects,
            "high_risk_parts": high_risk_parts,
            "today_tasks": len(today_tasks),
            "pending_tasks": pending_tasks,
            "projects": projects_with_relations,
            "tasks": tasks_with_assignees
        }
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """获取单个项目详情"""
        proj = next((p for p in self.projects if p['id'] == project_id), None)
        if not proj:
            return None
        
        pm = next((u for u in self.users if u['id'] == proj['pm_id']), None)
        parts = [p for p in self.parts if p['project_id'] == proj['id']]
        parts_with_suppliers = []
        for part in parts:
            suppliers = [s for s in self.suppliers if s['part_id'] == part['id']]
            parts_with_suppliers.append({**part, 'suppliers': suppliers})
        
        milestones = [m for m in self.milestones if m['project_id'] == proj['id']]
        tasks = [t for t in self.tasks if t['project_id'] == project_id]
        tasks_with_assignees = []
        for task in tasks:
            assignees = [u for u in self.users if u['id'] in task['assignee_ids']]
            tasks_with_assignees.append({**task, 'assignees': assignees})
        
        return {
            **proj,
            'pm': pm,
            'parts': parts_with_suppliers,
            'milestones': milestones,
            'tasks': tasks_with_assignees
        }
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        task = next((t for t in self.tasks if t['id'] == task_id), None)
        if not task:
            return False
        self.tasks.remove(task)
        return True
    
    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新任务"""
        import uuid
        new_task = {
            "id": f"task-{uuid.uuid4().hex[:8]}",
            **task_data,
            "completed_at": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.tasks.append(new_task)
        return new_task
    
    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新项目"""
        import uuid
        new_project = {
            "id": f"proj-{uuid.uuid4().hex[:8]}",
            **project_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.projects.append(new_project)
        return new_project
    
    def update_part_status(self, part_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新部件状态"""
        part = next((p for p in self.parts if p['id'] == part_id), None)
        if not part:
            return None
        
        for key, value in update_data.items():
            if key in part:
                part[key] = value
        part['updated_at'] = datetime.now().isoformat()
        
        return part
    
    def get_users(self) -> List[Dict[str, Any]]:
        """获取所有用户"""
        return self.users


# 全局 Mock 数据实例
mock_data_service = MockDataService()
