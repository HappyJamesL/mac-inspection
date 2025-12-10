# 调整前端配置以支持二级域名/mac/

## 1. 修改Vite配置

### 1.1 设置base路径
- **文件**：`frontend/vite.config.js`
- **修改内容**：添加`base: '/mac/'`配置
- **作用**：确保构建后的资源路径以/mac/开头

### 1.2 调整代理配置
- **文件**：`frontend/vite.config.js`
- **修改内容**：确保代理配置能正确处理/mac/api请求
- **作用**：开发环境下正确代理API请求

## 2. 修改路由配置

### 2.1 确认路由base路径
- **文件**：`frontend/src/router/index.js`
- **检查内容**：路由已经使用`import.meta.env.BASE_URL`作为base路径，无需修改
- **作用**：确保路由能正确处理/mac/前缀

## 3. 构建前端项目

### 3.1 安装依赖
```bash
npm install
```

### 3.2 构建项目
```bash
npm run build
```

### 3.3 验证构建结果
- 检查`dist`目录下的`index.html`文件
- 确保所有资源引用路径都以`/mac/`开头

## 4. 配置Nginx

### 4.1 调整Nginx配置
- **配置文件**：Nginx配置文件（如`nginx.conf`或`/etc/nginx/conf.d/default.conf`）
- **修改内容**：添加/mac/的反向代理配置
- **作用**：确保访问/mac/时能正确代理到前端和后端

### 4.2 示例Nginx配置
```nginx
server {
    listen 80;
    server_name 172.20.180.81;

    location /mac/ {
        root /path/to/frontend/dist;
        index index.html;
        try_files $uri $uri/ /mac/index.html; # 处理单页应用路由
    }

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

## 5. 验证访问

### 5.1 重启Nginx
```bash
nginx -s reload
```

### 5.2 访问测试
- 访问`http://172.20.180.81/mac/`，确认能正常加载首页
- 访问`http://172.20.180.81/mac/inspection?userrole=xxx`，确认能正常访问检测页面
- 确认API请求能正常代理到后端

## 6. 开发环境配置

### 6.1 调整开发服务器配置
- **文件**：`frontend/vite.config.js`
- **修改内容**：添加server配置，支持/mac/前缀
- **作用**：开发环境下也能通过/mac/访问

## 注意事项

1. 确保所有资源路径都使用相对路径或正确的base路径
2. 确保单页应用路由能正确处理404情况
3. 确保API请求路径正确
4. 构建前清除之前的构建缓存
5. 测试不同浏览器的兼容性