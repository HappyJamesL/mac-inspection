# 内网Redhat服务器部署方案

## 1. 环境准备

### 1.1 服务器要求
- Redhat 7.x/8.x/9.x
- Python 3.10+
- Node.js 18+
- 至少 4GB 内存
- 至少 50GB 磁盘空间

### 1.2 软件安装
- **Python 3.10+**：如果服务器没有安装，需要从离线源安装
- **Node.js 18+**：从离线包安装
- **Nginx**：用于反向代理和静态文件服务

## 2. 依赖安装

### 2.1 前端依赖
1. 在联网环境下，下载前端依赖包：
   ```bash
   cd frontend
   npm install --legacy-peer-deps
   npm run build
   ```
2. 将 `node_modules` 和 `dist` 目录打包，上传到内网服务器

### 2.2 后端依赖
1. 在联网环境下，下载后端依赖包：
   ```bash
   cd backend
   pip install -r requirements.txt -t ./vendor
   ```
2. 将 `vendor` 目录打包，上传到内网服务器

## 3. 配置调整

### 3.1 后端配置
1. 修改 `.env` 文件，配置数据库连接和其他参数
2. 确保 `settings.py` 中的配置正确
3. 调整 CORS 配置，允许前端域名访问

### 3.2 前端配置
1. 修改 `vite.config.js`，配置后端 API 代理
2. 修改 `src/services/api.js`，调整 API 基础 URL
3. 确保构建后的静态文件能正确访问后端 API

### 3.3 Nginx 配置
创建 Nginx 配置文件，配置反向代理和静态文件服务：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 静态文件服务
    location / {
        root /path/to/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 反向代理到后端 API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 4. 构建和部署

### 4.1 前端构建
1. 在联网环境下完成构建后，将 `dist` 目录上传到服务器
2. 或者在服务器上使用离线 `node_modules` 进行构建

### 4.2 后端部署
1. 将后端代码和 `vendor` 目录上传到服务器
2. 安装依赖：
   ```bash
   pip install -e ./vendor
   ```
3. 初始化数据库（如果需要）：
   ```bash
   python -m app.db.init_db
   ```

## 5. 运行和维护

### 5.1 启动后端服务
使用 `nohup` 或 `systemd` 启动后端服务：
```bash
cd backend
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > backend.log 2>&1 &
```

### 5.2 启动前端服务
配置 Nginx 后，启动 Nginx 服务：
```bash
systemctl start nginx
systemctl enable nginx
```

### 5.3 监控和日志
- 后端日志：`backend.log`
- 前端日志：Nginx 访问日志和错误日志
- 可以使用 `tail -f` 实时查看日志

## 6. 常见问题处理

### 6.1 依赖安装问题
- 确保使用正确的 Python 版本
- 确保依赖包版本兼容
- 可以使用离线依赖包管理工具，如 `pip wheel`

### 6.2 数据库连接问题
- 确保数据库服务正常运行
- 确保数据库连接字符串正确
- 确保用户有足够的权限

### 6.3 CORS 问题
- 确保后端 CORS 配置正确
- 确保 Nginx 配置了正确的跨域头

### 6.4 静态文件访问问题
- 确保 Nginx 配置了正确的根目录
- 确保静态文件权限正确
- 确保 Nginx 服务正常运行

## 7. 安全考虑

### 7.1 网络安全
- 配置防火墙，只允许必要的端口访问
- 使用 HTTPS（如果需要）
- 配置合适的 CORS 策略

### 7.2 数据安全
- 定期备份数据库
- 配置合适的数据库权限
- 敏感数据加密存储

### 7.3 应用安全
- 定期更新依赖包
- 配置合适的日志级别
- 实现访问控制和认证

## 8. 部署脚本

### 8.1 后端启动脚本
```bash
#!/bin/bash
cd /path/to/backend
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 > backend.log 2>&1 &
echo $! > backend.pid
```

### 8.2 后端停止脚本
```bash
#!/bin/bash
if [ -f /path/to/backend/backend.pid ]; then
    kill $(cat /path/to/backend/backend.pid)
    rm /path/to/backend/backend.pid
fi
```

## 9. 自动化部署

### 9.1 使用 Ansible 自动化部署
- 编写 Ansible playbook，实现自动化部署
- 包括环境检查、依赖安装、配置调整、服务启动等步骤
- 支持回滚和版本管理

### 9.2 使用 Docker 容器化部署（可选）
- 构建 Docker 镜像（在联网环境下）
- 上传镜像到内网 Docker 仓库
- 在服务器上运行容器
- 使用 Docker Compose 管理多容器应用

## 10. 监控和告警

### 10.1 系统监控
- 使用 Prometheus 和 Grafana 监控系统资源
- 配置告警规则，当资源使用率超过阈值时发送告警

### 10.2 应用监控
- 实现应用健康检查 API
- 监控 API 响应时间和错误率
- 配置应用日志收集和分析

# 部署流程图

1. **环境准备** → 2. **依赖安装** → 3. **配置调整** → 4. **构建和部署** → 5. **运行和维护**

# 注意事项

1. 确保服务器时间同步
2. 定期更新系统和软件
3. 定期备份数据
4. 监控系统资源使用情况
5. 实现访问控制和认证
6. 配置合适的日志级别
7. 确保网络安全
8. 定期检查应用健康状态

# 部署检查清单

- [ ] 服务器环境准备完成
- [ ] 依赖包下载和上传完成
- [ ] 配置文件调整完成
- [ ] 数据库初始化完成
- [ ] 后端服务启动成功
- [ ] 前端服务部署完成
- [ ] Nginx 配置完成
- [ ] 系统监控配置完成
- [ ] 安全配置完成
- [ ] 备份策略制定完成

# 后续维护计划

1. **日常维护**：检查日志、监控系统状态
2. **定期维护**：更新依赖、备份数据、优化性能
3. **应急处理**：制定应急预案，处理突发情况
4. **版本更新**：制定版本更新计划，确保平滑过渡

# 总结

本方案详细描述了在内部Redhat服务器上部署前后端分离项目的完整流程，包括环境准备、依赖安装、配置调整、构建和部署、运行和维护等步骤。由于是内网环境，需要在联网环境下提前下载依赖包，然后上传到服务器。同时，还需要考虑安全、监控、备份等方面的问题，确保系统稳定运行。