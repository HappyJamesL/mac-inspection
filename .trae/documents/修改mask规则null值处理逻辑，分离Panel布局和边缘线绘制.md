## 问题分析

用户希望当 `cover_x` 和 `cover_y` 为 `null` 时，**不要计算shot（即不显示边缘线），但要正常绘制Panel的layout**。

## 现有逻辑

当前 `calculateMaskPositions` 函数的执行流程：
1. 调用 `analyzePanelLayout` 分析panel布局
2. 实例化 `SymmetryCalculator` 计算shots
3. 将计算结果存储在 `maskPositions` 数组中
4. `drawBackground` 函数使用 `maskPositions` 绘制边缘线

## 修复方案

修改 `calculateMaskPositions` 函数，实现 **Panel布局绘制** 和 **边缘线计算** 的分离：

1. 当 `cover_x` 或 `cover_y` 为 `null` 时：
   - 仍然调用 `analyzePanelLayout` 分析panel布局，确保panel正常显示
   - **跳过** `SymmetryCalculator` 实例化和shot计算
   - 清空 `maskPositions` 数组，确保不绘制边缘线

2. 当 `cover_x` 和 `cover_y` 都有有效值时：
   - 按照现有逻辑执行完整的计算

## 具体修改点

### 修改前端 `calculateMaskPositions` 函数
文件：`d:\DEV\Code\JamesRepo\mac-insp\mac-inspection\frontend\src\components\CanvasStage.vue`

在 `calculateMaskPositions` 函数中添加条件判断，当 `cover_x` 或 `cover_y` 为 `null` 时，跳过shot计算：

```javascript
const calculateMaskPositions = () => {
  // 清空当前mask位置
  maskPositions = [];
  
  // 分析panel布局
  const layout = analyzePanelLayout(glassConfig.panels);
  
  // 更新全局panels引用
  panels = layout ? layout.panelsWithId : [];
  
  // 发射layout状态变化事件
  emit('layout-status-change', panels.length > 0);
  
  if (!layout) return;

  // 获取规则参数
  const { cover_x, cover_y, full_shot } = glassConfig.maskRule;
  
  // 当cover_x或cover_y为null时，只绘制panel布局，不计算shot
  if (cover_x === null || cover_y === null) {
    return;
  }
  
  // 否则，按照现有逻辑计算shot
  const maskCols = cover_x || 99;
  const maskRows = cover_y || 99;
  const fullShot = full_shot || 1;

  // 实例化计算器
  const calculator = new SymmetryCalculator(
    layout.columns, layout.rows, 
    maskCols, maskRows, 
    fullShot
  );

  // 将逻辑Shot转换为物理Mask区域 (用于绘图)
  calculator.shots.forEach(shot => {
    // 现有代码...
    maskPositions.push({ /* ... */ });
  });
}
```

## 预期效果

通过以上修改，当 `cover_x` 或 `cover_y` 为 `null` 时：
- Panel布局会正常绘制
- 不会计算shot，也不会显示边缘线
- 避免了之前的无限循环问题
- 实现了Panel布局和边缘线绘制的分离

## 额外优化

1. 移除 `SymmetryCalculator` 构造函数和 `calculateAxisSteps` 方法中针对null值的防护逻辑，因为现在在调用前已经进行了null值检查
2. 简化代码，提高性能

## 具体修改点（额外优化）

1. **简化 `SymmetryCalculator` 构造函数**：
   ```javascript
   constructor(glassCols, glassRows, maskCols, maskRows, fullShot = 1) {
     this.gCols = glassCols;
     this.gRows = glassRows;
     this.mCols = maskCols;
     this.mRows = maskRows;
     this.fullShot = fullShot;
     
     this.shots = this.calculateShots();
   }
   ```

2. **简化 `calculateAxisSteps` 方法**：
   ```javascript
   calculateAxisSteps(totalUnits, maskSize, isReverseAxis) {
     const steps = [];
     
     if (!isReverseAxis) {
       // --- 正向模式 (0 -> Total) ---
       let cursor = 0;
       while (cursor < totalUnits) {
         // 现有逻辑...
       }
     } else {
       // --- 逆向模式 (Total -> 0) ---
       let cursor = totalUnits;
       while (cursor > 0) {
         // 现有逻辑...
       }
     }
     return steps;
   }
   ```

## 预期效果

通过这些优化，代码结构更加清晰，性能也会有所提升。同时，实现了用户要求的功能：当 `cover_x` 和 `cover_y` 为 `null` 时，只绘制Panel布局，不显示边缘线。