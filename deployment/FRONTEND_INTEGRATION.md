# CMF 供应链项目管理系统 - 前端对接指南

## 概述

本文档说明如何将现有的静态 HTML 前端 (`mainweb.html`) 与后端 API 进行对接，实现数据动态化。

---

## 1. 需要修改的 HTML 部分

### 1.1 添加 data-id 属性

为了让 JavaScript 能够识别和操作 DOM 元素，需要为关键元素添加 `data-id` 属性：

#### 项目卡片
```html
<!-- 修改前 -->
<div class="glass-card rounded-2xl p-5 relative overflow-hidden group">

<!-- 修改后 -->
<div class="glass-card rounded-2xl p-5 relative overflow-hidden group" data-project-id="proj-x1-001">
```

#### 部件行
```html
<!-- 修改前 -->
<tr class="group/row hover:bg-white/5 transition-colors border-b border-white/5 last:border-0">

<!-- 修改后 -->
<tr class="group/row hover:bg-white/5 transition-colors border-b border-white/5 last:border-0" data-part-id="part-x1-001">
```

#### 任务卡片
```html
<!-- 修改前 -->
<div class="glass-card p-4 rounded-xl border-l-4 border-l-red-500 cursor-pointer hover:bg-white/5 transition-colors relative group">

<!-- 修改后 -->
<div class="glass-card p-4 rounded-xl border-l-4 border-l-red-500 cursor-pointer hover:bg-white/5 transition-colors relative group" data-task-id="task-001">
```

#### 删除按钮
```html
<!-- 修改前 -->
<button class="delete-btn w-6 h-6 rounded-lg bg-white/5 hover:bg-red-500/20 flex items-center justify-center transition-colors" title="删除任务">

<!-- 修改后 -->
<button class="delete-btn w-6 h-6 rounded-lg bg-white/5 hover:bg-red-500/20 flex items-center justify-center transition-colors" 
        data-task-id="task-001" 
        title="删除任务">
```

---

## 2. JavaScript Fetch 逻辑修改

### 2.1 创建 API 服务模块

在 HTML 底部或单独的 JS 文件中添加以下代码：

```javascript
// API 配置
const API_BASE_URL = 'http://localhost:8000/api';

// API 服务类
class ApiService {
    // 获取仪表盘概览数据
    static async getDashboardOverview() {
        try {
            const response = await fetch(`${API_BASE_URL}/dashboard/overview`);
            if (!response.ok) throw new Error('Failed to fetch dashboard');
            return await response.json();
        } catch (error) {
            console.error('Error fetching dashboard:', error);
            return null;
        }
    }

    // 获取服务器时间（用于校准）
    static async getServerTime() {
        try {
            const response = await fetch(`${API_BASE_URL}/system/time`);
            if (!response.ok) throw new Error('Failed to fetch time');
            return await response.json();
        } catch (error) {
            console.error('Error fetching server time:', error);
            return null;
        }
    }

    // 删除任务
    static async deleteTask(taskId) {
        try {
            const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
                method: 'DELETE'
            });
            if (!response.ok) throw new Error('Failed to delete task');
            return await response.json();
        } catch (error) {
            console.error('Error deleting task:', error);
            return null;
        }
    }

    // 创建新项目
    static async createProject(projectData) {
        try {
            const response = await fetch(`${API_BASE_URL}/projects`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(projectData)
            });
            if (!response.ok) throw new Error('Failed to create project');
            return await response.json();
        } catch (error) {
            console.error('Error creating project:', error);
            return null;
        }
    }

    // 更新部件状态
    static async updatePartStatus(partId, statusData) {
        try {
            const response = await fetch(`${API_BASE_URL}/parts/${partId}/status`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(statusData)
            });
            if (!response.ok) throw new Error('Failed to update part');
            return await response.json();
        } catch (error) {
            console.error('Error updating part:', error);
            return null;
        }
    }
}
```

### 2.2 风险等级到颜色的映射

```javascript
// 风险等级映射配置
const RISK_CONFIG = {
    'LOW': {
        bgClass: 'bg-emerald-500/10',
        textClass: 'text-emerald-400',
        borderClass: 'border-emerald-500/20',
        icon: 'fa-check-circle',
        label: '正常'
    },
    'MEDIUM': {
        bgClass: 'bg-amber-500/10',
        textClass: 'text-amber-400',
        borderClass: 'border-amber-500/20',
        icon: 'fa-flask',
        label: '工艺风险'
    },
    'HIGH': {
        bgClass: 'bg-red-500/10',
        textClass: 'text-red-400',
        borderClass: 'border-red-500/20',
        icon: 'fa-exclamation-triangle',
        label: '延期风险'
    },
    'CRITICAL': {
        bgClass: 'bg-red-700/20',
        textClass: 'text-red-300',
        borderClass: 'border-red-700/30',
        icon: 'fa-radiation',
        label: '严重风险'
    }
};

// 获取风险样式
function getRiskStyle(riskLevel) {
    return RISK_CONFIG[riskLevel] || RISK_CONFIG['LOW'];
}
```

### 2.3 渲染项目卡片

```javascript
// 渲染单个项目卡片
function renderProjectCard(project) {
    const riskConfig = getRiskStyle(project.overall_status);
    const pmInitial = project.pm?.avatar_initial || '?';
    
    // 生成部件表格行
    const partsRows = project.parts.map(part => {
        const partRisk = getRiskStyle(part.risk_level);
        const primarySupplier = part.suppliers?.find(s => s.type === 'PRIMARY')?.name || '-';
        const secondarySupplier = part.suppliers?.find(s => s.type === 'SECONDARY')?.name || '-';
        
        return `
            <tr class="group/row hover:bg-white/5 transition-colors border-b border-white/5 last:border-0" data-part-id="${part.id}">
                <td class="py-3 pl-2">
                    <div class="font-medium text-slate-200">${part.name}</div>
                    <div class="text-xs text-slate-500 mt-0.5">${part.structure || ''}</div>
                </td>
                <td class="py-3">
                    <span class="text-slate-300">${primarySupplier}</span>
                </td>
                <td class="py-3 text-slate-500">${secondarySupplier}</td>
                <td class="py-3">
                    <span class="text-xs ${part.risk_level === 'HIGH' ? 'text-amber-400' : 'text-cyan-400'}">
                        <i class="fas ${part.risk_level === 'HIGH' ? 'fa-exclamation-circle' : 'fa-info-circle'} mr-1"></i>${part.progress_note || ''}
                    </span>
                </td>
                <td class="py-3 text-right pr-2">
                    <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium ${partRisk.bgClass} ${partRisk.textClass} ${partRisk.borderClass}">
                        <i class="fas ${partRisk.icon}"></i> ${partRisk.label}
                    </span>
                </td>
            </tr>
        `;
    }).join('');
    
    // 生成里程碑
    const milestonesHtml = project.milestones.map((ms, index) => {
        const isActive = ms.status === 'completed' ? 'active' : '';
        const isCompleted = ms.status === 'completed';
        const colorClass = isCompleted ? 'bg-cyan-500' : 'bg-slate-700';
        const textColor = isCompleted ? 'text-cyan-400' : '';
        
        return `
            <div class="timeline-dot ${isActive} flex flex-col items-center gap-1 cursor-pointer group/tl">
                <div class="w-3 h-3 rounded-full ${colorClass} border-2 border-slate-900 ${isActive ? 'shadow-[0_0_10px_rgba(34,211,238,0.5)]' : ''}"></div>
                <span class="text-[10px] ${textColor} font-bold">${ms.stage}</span>
                <span class="text-[9px] text-slate-600">${new Date(ms.planned_date).toLocaleDateString('zh-CN', {month: '2-digit', day: '2-digit'})}</span>
            </div>
        `;
    }).join('');
    
    return `
        <div class="glass-card rounded-2xl p-5 relative overflow-hidden group" data-project-id="${project.id}">
            <div class="absolute top-0 left-0 w-full h-1 ${project.overall_status === 'HIGH' ? 'bg-gradient-to-r from-red-500 via-orange-500' : 'bg-gradient-to-r from-emerald-500 to-teal-500'} opacity-80"></div>
            
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-4 gap-4">
                <div class="flex items-center gap-3">
                    <span class="px-2 py-1 rounded bg-slate-800 text-xs font-mono text-slate-400 border border-slate-700">${project.code}</span>
                    <h2 class="text-lg font-bold text-white group-hover:text-cyan-400 transition-colors">${project.name}</h2>
                    ${project.overall_status === 'HIGH' ? `
                        <span class="px-2 py-0.5 rounded-full text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20 flex items-center gap-1">
                            <span class="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span> 高风险
                        </span>
                    ` : `
                        <span class="px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            进度正常
                        </span>
                    `}
                </div>
                <div class="flex items-center gap-4 text-sm">
                    <div class="flex items-center gap-2">
                        <span class="text-slate-400">PM:</span>
                        <span class="text-white font-medium">${project.pm?.name || '-'}</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-slate-400">当前阶段:</span>
                        <span class="${project.overall_status === 'HIGH' ? 'text-cyan-400' : 'text-emerald-400'} font-bold">${project.current_stage}</span>
                    </div>
                </div>
            </div>
            
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="text-xs text-slate-500 border-b border-white/5">
                            <th class="pb-3 font-medium pl-2">部件名称 / 结构</th>
                            <th class="pb-3 font-medium">主供应商</th>
                            <th class="pb-3 font-medium">二供 / 备选</th>
                            <th class="pb-3 font-medium">进度备注</th>
                            <th class="pb-3 font-medium text-right pr-2">风险状态</th>
                        </tr>
                    </thead>
                    <tbody class="text-sm">
                        ${partsRows}
                    </tbody>
                </table>
            </div>
            
            <div class="mt-5 pt-4 border-t border-white/5">
                <div class="flex justify-between items-center text-xs text-slate-500 mb-2">
                    <span>项目时间轴</span>
                    <span class="text-cyan-400">Next: ${project.milestones.find(m => m.status === 'pending')?.stage || 'MP'}</span>
                </div>
                <div class="relative flex items-center justify-between">
                    <div class="absolute left-0 top-1/2 w-full h-0.5 bg-slate-800 -z-10 rounded"></div>
                    <div class="absolute left-0 top-1/2 w-[45%] h-0.5 bg-gradient-to-r from-cyan-600 to-cyan-400 -z-10 rounded"></div>
                    ${milestonesHtml}
                </div>
            </div>
        </div>
    `;
}
```

### 2.4 渲染任务列表

```javascript
// 渲染任务卡片
function renderTaskCard(task) {
    const priorityConfig = {
        'P0': { border: 'border-l-red-500', text: 'text-red-400', label: 'P0 紧急' },
        'P1': { border: 'border-l-amber-500', text: 'text-amber-400', label: 'P1 重要' },
        'P2': { border: 'border-l-cyan-500', text: 'text-cyan-400', label: 'P2 常规' },
        'P3': { border: 'border-l-slate-600', text: 'text-slate-400', label: 'P3 低优' }
    };
    
    const config = priorityConfig[task.priority] || priorityConfig['P2'];
    const isCompleted = task.status === 'COMPLETED';
    const assigneesHtml = task.assignees?.map(a => `
        <div class="w-5 h-5 rounded-full bg-slate-700 border border-slate-900 flex items-center justify-center text-[8px]">${a.avatar_initial || '?'}</div>
    `).join('') || '';
    
    const dueDate = new Date(task.due_date);
    const isToday = dueDate.toDateString() === new Date().toDateString();
    const isTomorrow = dueDate.toDateString() === new Date(Date.now() + 86400000).toDateString();
    let dueText = isToday ? '今日' : (isTomorrow ? '明日' : dueDate.toLocaleDateString('zh-CN'));
    dueText += ` ${dueDate.getHours().toString().padStart(2, '0')}:${dueDate.getMinutes().toString().padStart(2, '0')}前`;
    
    return `
        <div class="glass-card p-4 rounded-xl ${config.border} cursor-pointer hover:bg-white/5 transition-colors relative group ${isCompleted ? 'opacity-70' : ''}" data-task-id="${task.id}">
            <div class="flex justify-between items-start mb-2">
                <span class="text-[10px] font-mono text-slate-500 bg-slate-800 px-1.5 rounded">${task.project_id || 'General'}</span>
                <span class="text-[10px] ${config.text} font-bold">${config.label}</span>
            </div>
            <p class="text-sm text-slate-200 font-medium mb-2 ${isCompleted ? 'line-through' : ''}">${task.title}</p>
            <div class="flex items-center justify-between text-xs text-slate-500">
                <div class="flex items-center gap-1">
                    <i class="far fa-clock"></i>
                    <span>${isCompleted ? '已完成' : dueText}</span>
                </div>
                <div class="flex items-center gap-2">
                    <div class="flex -space-x-2">
                        ${assigneesHtml}
                    </div>
                    <button class="delete-btn w-6 h-6 rounded-lg bg-white/5 hover:bg-red-500/20 flex items-center justify-center transition-colors" 
                            data-task-id="${task.id}" 
                            title="删除任务">
                        <i class="far fa-trash-alt text-xs"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
}
```

### 2.5 初始化数据加载

```javascript
// 页面加载时获取数据
async function initializeDashboard() {
    // 获取仪表盘数据
    const dashboard = await ApiService.getDashboardOverview();
    
    if (dashboard) {
        // 更新统计数字
        document.querySelector('.glass-card.p-3.rounded-xl.text-center:first-child .text-2xl').textContent = dashboard.ongoing_projects;
        document.querySelector('.glass-card.p-3.rounded-xl.text-center:last-child .text-2xl').textContent = dashboard.high_risk_parts;
        
        // 渲染项目列表
        const mainElement = document.querySelector('main.lg\\:col-span-9');
        const projectsHtml = dashboard.projects.map(renderProjectCard).join('');
        // 保留原有的 aside，只替换项目卡片部分
        // ... (具体实现根据实际 DOM 结构调整)
        
        // 渲染任务列表
        const asideElement = document.querySelector('aside.lg\\:col-span-3');
        const tasksContainer = asideElement?.querySelector('.space-y-3');
        if (tasksContainer) {
            tasksContainer.innerHTML = dashboard.tasks.map(renderTaskCard).join('');
            
            // 重新绑定删除事件
            bindDeleteEvents();
        }
    }
    
    // 获取服务器时间并校准
    const serverTime = await ApiService.getServerTime();
    if (serverTime) {
        updateTimeIndicator(new Date(serverTime.server_time));
    }
}

// 绑定删除事件
function bindDeleteEvents() {
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.stopPropagation();
            const taskId = this.dataset.taskId;
            
            if (await ApiService.deleteTask(taskId)) {
                const card = this.closest('.glass-card');
                card.style.opacity = '0';
                card.style.transform = 'translateX(20px)';
                setTimeout(() => {
                    card.style.display = 'none';
                    // 可选：刷新任务列表
                    initializeDashboard();
                }, 300);
            }
        });
    });
}

// 悬浮按钮添加项目
function bindFabButton() {
    document.querySelector('.fab-button')?.addEventListener('click', async function() {
        // 这里可以打开模态框或跳转到新项目页面
        const projectName = prompt('请输入项目名称:');
        const projectCode = prompt('请输入项目代号 (格式：PJ-2024-XX):');
        
        if (projectName && projectCode) {
            const newProject = await ApiService.createProject({
                code: projectCode,
                name: projectName,
                current_stage: 'PROTOTYPE',
                overall_status: 'LOW',
                pm_id: 'user-alex-001' // 实际应从用户选择中获取
            });
            
            if (newProject) {
                alert('项目创建成功!');
                initializeDashboard(); // 刷新看板
            } else {
                alert('项目创建失败，请检查项目代号是否已存在');
            }
        }
    });
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    initializeDashboard();
    bindDeleteEvents();
    bindFabButton();
});
```

---

## 3. 完整示例文件

创建一个新文件 `mainweb_dynamic.html`，包含上述所有修改。

---

## 4. 开发环境运行

1. **启动后端服务**:
   ```bash
   cd backend
   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **访问 Swagger 文档**: http://localhost:8000/api/docs

3. **打开前端页面**: 直接在浏览器中打开 `mainweb.html` 或修改后的 `mainweb_dynamic.html`

---

## 5. 注意事项

1. **CORS 配置**: 后端已配置允许所有来源，生产环境应限制具体域名
2. **错误处理**: 所有 API 调用都应包含错误处理和重试机制
3. **加载状态**: 数据加载时应显示 loading 状态
4. **缓存策略**: 考虑使用 localStorage 缓存数据，减少 API 调用
5. **认证授权**: 当前未实现认证，生产环境需添加 JWT 或其他认证机制
