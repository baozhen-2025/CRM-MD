# 主数据集成管理平台

一级公司与三级公司主数据同步管理系统原型

## 项目结构

```
CRM-MD/
├── frontend/          # Vue3 前端项目
└── backend/           # FastAPI 后端项目
```

## 快速启动

### 1. 启动后端服务

```bash
cd backend
pip install -r requirements.txt
python init_data.py          # 初始化示例数据（首次运行）
uvicorn app.main:app --reload --port 8000
```

后端服务地址: http://localhost:8000
API 文档地址: http://localhost:8000/docs

### 2. 启动前端服务

```bash
cd frontend
npm install                  # 安装依赖（首次运行）
npm run dev
```

前端访问地址: http://localhost:5173

## 功能模块

| 模块 | 路径 | 功能说明 |
|------|------|----------|
| 数据源管理 | /datasource | 配置一级公司 API 连接信息 |
| 字段映射配置 | /mapping | 配置一级字段与三级字段的对应关系 |
| 匹配规则配置 | /rule | 定义数据匹配条件 |
| 同步任务管理 | /sync | 查看任务执行情况，手动触发同步 |
| 人工审核 | /audit | 处理无法自动匹配的数据 |
| 变更日志 | /log | 查看数据变更历史 |

## 技术栈

### 前端
- Vue 3 + TypeScript
- Vite
- Ant Design Vue 4.x
- Vue Router 4
- Pinia
- Axios

### 后端
- Python FastAPI
- SQLAlchemy
- SQLite
- Pydantic

## 示例数据

系统初始化后包含以下示例数据：
- 3 个数据源（组织架构、客商、人员）
- 7 条字段映射配置
- 3 条匹配规则
- 3 个同步任务
- 3 条同步记录
- 3 条待审核记录
- 4 条变更日志
