## 添加layout检查，拦截没有layout时的点击操作

### 问题分析

当前代码中，当没有layout返回时，`panels`数组为空，但点击处理逻辑中没有检查这个情况，导致：

1. 用户可以点击并尝试保存缺陷
2. 线缺和面缺在碰撞检测时遍历空数组
3. 最终在保存时出错

需要优化：当没有layout返回时，所有缺陷都应该在前端被拦截，不能点击和保存。

### 解决方案

修改`d:\DEV\Code\JamesRepo\mac-insp\mac-inspection\frontend\src\components\CanvasStage.vue`文件，在点击处理逻辑中添加`panels`数组检查，拦截没有layout时的所有绘制操作。

### 具体修改点

**在`handleStageDown`函数中添加检查**：

* 检查`panels`数组是否为空

* 为空时，直接返回，不处理点击

* 添加调试日志

- **在`handleStageUp`函数中添加检查**：

  * 检查`panels`数组是否为空

  * 为空时，直接返回，不保存缺陷

  * 清除临时绘制
- **在`calculateMaskPositions`函数中确保panels更新**：

  * 当有layout时，更新`panels`数组

  * 当没有layout时，确保`panels`数组为空
- **调试信息**：

  * 添加`panels`数组长度的调试日志

  * 输出是否允许点击的结果

  * 便于调试和验证

### 修改策略

* 在点击处理的入口添加检查

* 确保所有绘制操作都被拦截

* 保持代码简洁和高效

* 不影响现有功能

### 预期效果

* 当没有layout返回时，panels数组为空

* 所有点击操作被拦截，不产生任何效果

* 绘制操作被忽略，不保存缺陷

* 保持原有功能不变

* 便于调试和维护

### 关键代码实现

```javascript
// 在handleStageDown函数中添加检查
const handleStageDown = (e) => {
  // ... 现有代码 ...
  
  // 检查是否有有效的layout（panels数组不为空）
  if (panels.length === 0) {
    console.log('没有有效的layout数据，无法绘制缺陷');
    return;
  }
  
  // ... 继续处理点击 ...
};

// 在handleStageUp函数中添加检查
const handleStageUp = () => {
  // ... 现有代码 ...
  
  // 检查是否有有效的layout
  if (panels.length === 0) {
    console.log('没有有效的layout数据，无法保存缺陷');
    drawingState.points = [];
    if (drawingState.tempLine) {
      drawingState.tempLine.destroy();
      drawingState.tempLine = null;
    }
    return;
  }
  
  // ... 继续处理绘制 ...
};

// 确保calculateMaskPositions函数正确更新panels
const calculateMaskPositions = () => {
  maskPositions = [];
  const layout = analyzePanelLayout(glassConfig.panels);
  
  // 更新全局panels引用
  panels = layout ? layout.panelsWithId : [];
  
  if (!layout) return;
  
  // ... 现有代码 ...
};
```

