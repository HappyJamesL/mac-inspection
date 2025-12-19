# Mac Insp 玻璃缺陷检测系统

## 项目简介
Mac Insp 是一个用于玻璃缺陷检测的Web应用系统，提供缺陷标注、查询和管理功能。

## 技术栈

### 前端
- Vue 3
- Vite
- Vue Router
- Konva (Canvas绘图)
- Tailwind CSS

### 后端
- FastAPI
- Python 3.9+
- SQLAlchemy
- SQLite / Oracle
- JWT认证

## 项目结构

```
mac-inspection/
├── backend/              # 后端代码
│   ├── app/              # 应用核心代码
│   │   ├── api/          # API路由和模式
│   │   ├── core/         # 配置管理
│   │   ├── db/           # 数据库模型和连接
│   │   └── utils/        # 工具函数
│   ├── packages/         # Python依赖包
│   ├── main.py           # 后端入口文件
│   └── requirements.txt  # 依赖列表
├── frontend/             # 前端代码
│   ├── src/              # 源代码
│   │   ├── components/   # Vue组件
│   │   ├── router/       # 路由配置
│   │   ├── services/     # API服务
│   │   └── views/        # 页面视图
│   ├── package.json      # 前端依赖
│   └── vite.config.js    # Vite配置
└── macinsp.db            # SQLite数据库文件
```

## 快速开始

### 环境要求
- Node.js 16+ (前端)
- Python 3.9+ (后端)

### 前端启动

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm run dev
```

4. 访问前端应用
```
http://localhost:5173/mac/
```

### 后端启动

1. 进入后端目录
```bash
cd backend
```

2. 安装依赖
```bash
# 使用虚拟环境
python -m venv venv39
# 激活虚拟环境
# Windows: venv39\Scripts\activate
# Linux/Mac: source venv39/bin/activate
# 安装依赖
pip install -r requirements.txt
```

3. 启动后端服务
```bash
python main.py
```

4. 访问后端API
```
http://localhost:8000
```

5. 查看API文档
```
http://localhost:8000/docs
```

## 主要功能

### 缺陷检测
- 在画布上标注玻璃缺陷
- 支持多种缺陷类型
- 实时显示坐标和缺陷信息
- 支持缺陷对称性标记

### 缺陷查询
- 按条件查询缺陷记录
- 支持多种过滤条件
- 查看缺陷详情

### 权限管理
- 支持不同角色权限控制
- JWT认证机制

## API文档

后端提供完整的RESTful API，可通过以下地址访问Swagger文档：

```
http://localhost:8000/docs
```

主要API端点：
- `/api/v1/defects` - 缺陷管理
- `/api/v1/defect_types` - 缺陷类型管理
- `/api/v1/glasses` - 玻璃信息管理
- `/api/v1/lots` - 批次管理
- `/api/v1/auth` - 认证相关

## 开发说明

### 前端开发
- 开发服务器：`npm run dev`
- 构建生产版本：`npm run build`
- 预览生产构建：`npm run preview`

### 后端开发
- 开发模式：`python main.py` (自动重载)
- 使用Gunicorn部署：`gunicorn main:app -c gunicorn.conf.py`

## 配置说明

### 后端配置

后端配置文件位于 `backend/app/core/config.py`，主要配置项：

- `APP_NAME` - 应用名称
- `DEBUG` - 调试模式
- `HOST` - 服务地址
- `PORT` - 服务端口
- `DATABASE_TYPE` - 数据库类型 (sqlite/oracle)
- `SQLITE_URL` - SQLite数据库连接URL
- `ORACLE_*` - Oracle数据库配置
- `SECRET_KEY` - JWT密钥

### 前端配置

前端API地址配置位于 `frontend/src/services/api.js`

## 数据库迁移

对于Oracle数据库，需要确保数据库服务已启动，并配置正确的连接信息。

## 部署说明

### 生产环境部署

1. **前端部署**
   - 构建生产版本：`npm run build`
   - 将 `dist` 目录部署到Web服务器 (如Nginx)

2. **后端部署**
   - 使用Gunicorn作为WSGI服务器：
     ```bash
     gunicorn main:app -c gunicorn.conf.py
     ```
   - 可以使用systemd或supervisor管理进程
   - 配置反向代理 (如Nginx) 处理HTTPS和静态文件

### 环境变量
通过 backend 目录下的 `.env` 文件配置环境变量。

### 应用启停
1. 启动应用：
- 进入backend目录：`cd backend`
- 启动应用：`./restart.sh start`
- 重启应用：`./restart.sh restart`
- 停止应用：`./restart.sh stop`
- 应用日志：`tail -f logs/app.log`


