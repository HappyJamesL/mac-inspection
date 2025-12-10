# 实现方案

## 1. 后端修改

### 1.1 修改`checkPermission`接口
- **文件**: `backend/app/api/routes/auth.py`
- **修改内容**: 更新权限检查逻辑，允许`readonly`角色访问
- **具体实现**: 将`allowed = userrole == settings.ROLE_ADMIN`修改为`allowed = userrole in [settings.ROLE_ADMIN, 'readonly']`

## 2. 前端修改

### 2.1 修改路由权限检查
- **文件**: `frontend/src/router/index.js`
- **修改内容**: 保持不变，因为当前路由检查已经通过`checkPermission`接口验证，而我们已经修改了该接口允许readonly角色

### 2.2 在InspectionView.vue中添加角色控制
- **文件**: `frontend/src/views/InspectionView.vue`
- **修改内容**:
  1. 从URL获取userrole参数
  2. 添加计算属性`isReadonly`来判断是否为readonly角色
  3. 根据`isReadonly`属性控制以下功能:
     - 禁用Canvas绘图功能（缺陷记录）
     - 隐藏或禁用复制缺陷按钮
     - 禁用缺陷代码选择
     - 禁用其他可能的编辑功能

### 2.3 具体实现细节
- **获取userrole**: 在`onMounted`钩子中添加`const userrole = route.query.userrole`
- **计算属性**: `const isReadonly = computed(() => userrole === 'readonly')`
- **控制Canvas**: 在Canvas元素上添加`@click.prevent`或`pointer-events: none`样式
- **控制按钮**: 使用`v-if`或`v-disabled`指令控制复制缺陷等按钮
- **控制缺陷代码**: 禁用缺陷代码选择按钮

## 3. 预期效果
- readonly角色可以正常打开系统，输入cst,lot，查询数据
- readonly角色无法进行缺陷记录（Canvas点击无效）
- readonly角色无法复制缺陷
- readonly角色只能查看数据，不能进行任何编辑操作

## 4. 改动范围
- 仅修改2个文件，改动最小化
- 不影响现有admin角色的功能
- 不需要修改数据库或JWT令牌生成逻辑
- 不需要添加新的API接口

## 5. 实现步骤
1. 修改后端`checkPermission`接口
2. 在前端InspectionView.vue中添加角色检查逻辑
3. 控制UI元素的可用性
4. 测试readonly角色和admin角色的功能

这个方案改动最小，只需要修改少量代码，就能实现readonly角色的权限控制需求。