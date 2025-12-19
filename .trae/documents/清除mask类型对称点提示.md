# 清除mask类型对称点提示

## 问题分析
当用户点击mask类型缺陷时，系统会显示对称点提示。但目前这些提示点只会在用户点击新缺陷时被清除，而在切换glassid或切换其他缺陷类型时不会被清除，导致提示点残留，影响用户体验。

## 解决方案
需要在以下两种情况下清除对称点提示：
1. 切换glassid时
2. 切换缺陷类型时

## 实现步骤

### 1. 分析当前清除逻辑
查看CanvasStage.vue代码，发现当前在`handleStageDown`函数中，每次点击画布时都会调用`hintLayer.destroyChildren()`清除旧的对称点提示。这个逻辑可以复用。

### 2. 监听selectedCode变化
在CanvasStage.vue中添加对`selectedCode`的watch监听，当缺陷类型变化时清除提示点：
```javascript
watch(() => props.selectedCode, () => {
  hintLayer.destroyChildren();
  hintLayer.draw();
}, { immediate: false });
```

### 3. 监听glassConfig和panel数据变化
在CanvasStage.vue中，当glassConfig或panel数据变化时（通常发生在切换glassid时），会调用`loadPanelData`和`initStage`函数。需要在这些函数中添加清除提示点的逻辑：
- 在`loadPanelData`函数中，添加清除提示点的代码
- 在`initStage`函数中，添加清除提示点的代码

## 代码修改点

1. **CanvasStage.vue**：
   - 添加对`selectedCode`的watch监听，清除对称点提示
   - 在`loadPanelData`函数中添加清除对称点提示的代码
   - 在`initStage`函数中添加清除对称点提示的代码

## 预期效果
- 切换glassid时，当前glass上的对称点提示会被清除
- 切换缺陷类型时，当前显示的对称点提示会被清除
- 只有在用户选择mask类型缺陷并点击画布时，才会显示对称点提示
- 无需添加新方法，直接复用现有清除逻辑