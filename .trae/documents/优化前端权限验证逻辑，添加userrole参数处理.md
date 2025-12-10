# 实现前端userrole参数验证功能

## 1. 后端修改

### 1.1 添加userrole验证API端点
- **文件**：`backend/app/api/routes/auth.py`
- **功能**：添加一个API端点，用于验证URL中的userrole参数
- **实现逻辑**：
  - 接收userrole查询参数
  - 检查userrole是否与配置的ROLE_ADMIN匹配
  - 返回验证结果

### 1.2 代码实现
```python
@router.get("/check-permission")
async def check_permission(
    userrole: str,
    db: Session = Depends(get_db)
):
    """验证userrole权限"""
    # 验证userrole是否与配置的ROLE_ADMIN匹配
    allowed = userrole == settings.ROLE_ADMIN
    return {"allowed": allowed}
```

## 2. 前端修改

### 2.1 修改API服务
- **文件**：`frontend/src/services/api.js`
- **功能**：添加调用后端权限验证API的函数
- **代码实现**：
```javascript
// 验证userrole权限
export const checkPermission = async (userrole) => {
  try {
    return await api.get('/api/v1/auth/check-permission', { params: { userrole } });
  } catch (error) {
    console.error('权限验证失败:', error);
    return { allowed: false };
  }
};
```

### 2.2 修改路由守卫
- **文件**：`frontend/src/router/index.js`
- **功能**：在访问需要权限的路由前，验证URL中的userrole参数
- **代码实现**：
```javascript
import { checkPermission } from '../services/api';

// 权限控制 - 简化版，仅做基本路由保护
const checkPermission = async (to, from, next) => {
  // 以下页面不需要权限检查
  const noPermissionRequired = ['forbidden', 'query'];
  if (noPermissionRequired.includes(to.name)) {
    next();
    return;
  }
  
  // 开发环境中，允许所有访问，方便开发和测试
  if (import.meta.env.DEV) {
    next();
    return;
  }
  
  // 生产环境中，验证URL中的userrole参数
  const userrole = to.query.userrole;
  if (userrole) {
    try {
      // 调用后端API验证userrole
      const response = await checkPermission(userrole);
      if (response.allowed) {
        next();
        return;
      }
    } catch (error) {
      console.error('权限验证失败:', error);
    }
  }
  
  // 没有userrole参数或验证失败，重定向到403页面
  next({ name: 'forbidden' });
};
```

## 3. 实现细节

### 3.1 验证逻辑
- 前端路由守卫获取URL中的userrole参数
- 调用后端`/api/v1/auth/check-permission?userrole=xxx` API
- 后端检查userrole是否与配置的ROLE_ADMIN匹配
- 返回`{"allowed": true/false}`
- 前端根据返回结果决定是否允许访问

### 3.2 配置说明
- 后端`ROLE_ADMIN`配置在`backend/.env`文件中
- 前端通过`import.meta.env.DEV`区分开发环境和生产环境

## 4. 测试验证

1. 启动后端服务
2. 启动前端服务
3. 访问 `http://localhost:5173/inspection?userrole=9a2722e6-023f-472b-95a8-304a22ba43e4`
   - 预期：正常访问inspection页面
4. 访问 `http://localhost:5173/inspection?userrole=invalid`
   - 预期：重定向到forbidden页面
5. 访问 `http://localhost:5173/inspection`（无userrole参数）
   - 预期：重定向到forbidden页面

## 5. 注意事项

1. **安全性**：userrole参数是明文传递的，生产环境建议使用更安全的认证方式
2. **错误处理**：添加了错误处理，确保验证失败时能够正确重定向
3. **开发环境支持**：开发环境下跳过验证，方便开发测试
4. **代码兼容**：修改后的代码与现有代码兼容，不影响其他功能

通过以上实现，当用户访问 `http://172.20.180.81/inspection?userrole=9a2722e6-023f-472b-95a8-304a22ba43e4` 时，前端会验证URL中的userrole参数，与后端配置的ROLE_ADMIN匹配，从而允许访问inspection页面。