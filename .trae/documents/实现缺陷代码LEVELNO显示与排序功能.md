## 实现计划

### 1. reasoncode接口增加LEVELNO字段及前端排序显示

**后端修改**：
- 修改`/api/v1/reasoncode`接口，在返回结果中添加`LEVELNO`字段
- 文件：`backend/app/api/routes/init.py`

**前端修改**：
- 修改`loadDefectCodes`函数，在处理reasoncode数据时添加`levelno`字段
- 在`InspectionView.vue`中，按`levelno`对缺陷代码进行排序
- 在UI中，在颜色图标左侧显示LEVELNO序号
- 文件：`frontend/src/views/InspectionView.vue`

### 2. glass列表按递增排序显示

**前端修改**：
- 在获取glass列表后，添加排序逻辑，按glass_id递增排序
- 文件：`frontend/src/views/InspectionView.vue`

### 3. CST, LOT的下拉列表递增排序

**前端修改**：
- 在`loadInitData`函数中，对获取到的`selectOptions.lots`和`selectOptions.cst`进行递增排序
- 文件：`frontend/src/views/InspectionView.vue`

## 具体实现步骤

1. 首先修改后端`init.py`文件，在reasoncode接口中添加LEVELNO字段
2. 然后修改前端`InspectionView.vue`文件：
   - 更新`loadDefectCodes`函数，添加levelno字段并按其排序
   - 修改UI模板，在颜色图标左侧显示LEVELNO
   - 添加glass列表排序逻辑
   - 添加CST和LOT下拉列表排序逻辑

## 预期效果

- 缺陷代码列表按LEVELNO序号递增排序
- 每个缺陷代码前显示LEVELNO序号，位于颜色图标左侧
- Glass列表按ID递增排序
- CST和LOT下拉列表按值递增排序