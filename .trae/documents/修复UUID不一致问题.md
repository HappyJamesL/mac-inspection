## 问题分析

通过代码分析，发现UUID相关问题包括：

1. **字段名称不统一**：前端代码中同时使用了uid和uuid，导致混淆
2. **字段名称不匹配**：`triggerAutoSave`使用uuid字段，`saveDefectRecord`却从uid字段获取值
3. **UUID生成逻辑重复**：前端已生成uid，`saveDefectRecord`又重新生成，导致不一致

## 修复方案

### 1. 统一字段名称
- 将前端代码中所有uid字段统一改为uuid
- 确保所有组件和函数使用一致的字段名

### 2. 修复saveDefectRecord函数
- 修改`saveDefectRecord`函数，优先使用`defectRecord.uuid`字段
- 简化UUID生成逻辑，避免重复生成

### 3. 统一UUID生成格式
- 所有UUID生成时统一格式，包含"defect-"前缀
- 确保前端本地UUID与数据库中存储的UUID完全一致

## 具体修改点

1. **修改CanvasStage组件**（`src/components/CanvasStage.vue`）：
   - 将`addDefect`函数中的`uid`改为`uuid`
   - 将`handleStageUp`函数中的`uid`改为`uuid`
   - 生成UUID时添加"defect-"前缀

2. **修改InspectionView.vue**：
   - 将`removeDefect`函数中的参数`uid`改为`uuid`
   - 将`addDefect`函数中接收的缺陷对象的`uid`改为`uuid`
   - 将`copyDefectsFromGlass`函数中的`uid`改为`uuid`
   - 将`triggerAutoSave`函数中的`uuid`字段保持不变
   - 将`toggleEdit`和`saveRemark`函数中的`uid`改为`uuid`

3. **修改saveDefectRecord函数**（`src/services/api.js`）：
   - 将UUID生成逻辑改为：`uuid: defectRecord.uuid || defectRecord.uid || `defect-${Date.now()}`

4. **修改getDefects函数返回数据处理**：
   - 确保从后端获取的缺陷数据中，将uuid字段正确映射到前端的uuid字段

## 预期效果

- 前端代码中统一使用uuid字段，不再有uid和uuid混用
- 数据库中存储的UUID与前端本地UUID完全一致
- 简化了UUID生成和使用逻辑
- 确保删除缺陷时能正确匹配数据库中的UUID
- 提高了代码的可读性和可维护性