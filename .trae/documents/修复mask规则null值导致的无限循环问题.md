## 问题分析

当切换到新型号时，mask规则中的 `cover_x` 和 `cover_y` 为 `null`，导致 `SymmetryCalculator` 类的 `calculateAxisSteps` 方法进入无限循环，最终引发浏览器内存不足崩溃。

## 根本原因

在 `calculateMaskPositions` 函数中，当前代码使用 `const { cover_x = 5, cover_y = 6 } = glassConfig.maskRule` 来设置默认值。**但当 `cover_x` 或 `cover_y` 为 `null` 时，解构赋值的默认值不会生效**，因为 `null` 是一个有效的值，不是 `undefined`。

当 `maskSize`（即 `cover_x` 或 `cover_y`）为 `null` 时，`calculateAxisSteps` 方法中的 `while` 循环条件 `cursor + maskSize <= totalUnits` 会变成 `NaN <= totalUnits`，结果永远为 `false`，导致循环无法正常终止。

## 修复方案

1. **修改 `calculateMaskPositions` 函数**：在解构赋值时，确保 `cover_x` 和 `cover_y` 始终是有效数值，即使它们为 `null`，并将默认值设置为99。

2. **增强 `SymmetryCalculator` 构造函数**：添加参数有效性检查，确保传入的 `maskCols` 和 `maskRows` 是有效的正整数，默认值为99。

3. **优化 `calculateAxisSteps` 方法**：添加对 `maskSize` 的有效性检查，防止无效值导致的无限循环。

## 具体修改点

### 1. 修改前端 `calculateMaskPositions` 函数
文件：`d:\DEV\Code\JamesRepo\mac-insp\mac-inspection\frontend\src\components\CanvasStage.vue`

将默认值处理逻辑从简单的解构赋值改为使用 `||` 运算符，确保 `null` 值也能触发默认值，并将默认值设置为99：

```javascript
// 修改前
const { cover_x = 5, cover_y = 6, full_shot = 1 } = glassConfig.maskRule;

// 修改后
const { cover_x, cover_y, full_shot } = glassConfig.maskRule;
const maskCols = cover_x || 99;
const maskRows = cover_y || 99;
const fullShot = full_shot || 1;
```

### 2. 增强 `SymmetryCalculator` 构造函数
文件：`d:\DEV\Code\JamesRepo\mac-insp\mac-inspection\frontend\src\components\CanvasStage.vue`

在构造函数中添加参数有效性检查，并将默认值设置为99：

```javascript
constructor(glassCols, glassRows, maskCols, maskRows, fullShot = 1) {
  this.gCols = glassCols;
  this.gRows = glassRows;
  // 确保 maskCols 和 maskRows 是有效的正整数，默认值为99
  this.mCols = Math.max(1, parseInt(maskCols) || 99);
  this.mRows = Math.max(1, parseInt(maskRows) || 99);
  this.fullShot = fullShot;
  
  this.shots = this.calculateShots();
}
```

### 3. 优化 `calculateAxisSteps` 方法
文件：`d:\DEV\Code\JamesRepo\mac-insp\mac-inspection\frontend\src\components\CanvasStage.vue`

在方法开头添加参数有效性检查，确保 `maskSize` 是有效的正整数：

```javascript
calculateAxisSteps(totalUnits, maskSize, isReverseAxis) {
  const steps = [];
  
  // 确保 maskSize 是有效的正整数，防止无限循环
  const validMaskSize = Math.max(1, parseInt(maskSize) || 99);
  
  if (!isReverseAxis) {
    // --- 正向模式 (0 -> Total) ---
    let cursor = 0;
    while (cursor < totalUnits) {
      // ... 使用 validMaskSize 替代 maskSize ...
    }
  } else {
    // --- 逆向模式 (Total -> 0) ---
    let cursor = totalUnits;
    while (cursor > 0) {
      // ... 使用 validMaskSize 替代 maskSize ...
    }
  }
  return steps;
}
```

## 预期效果

通过以上修改，当 `cover_x` 或 `cover_y` 为 `null` 时，系统会自动使用默认值99，避免了无限循环，确保了程序的稳定性和可靠性。