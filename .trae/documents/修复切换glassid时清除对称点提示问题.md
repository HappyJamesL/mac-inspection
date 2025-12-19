# 修复切换glassid时清除对称点提示问题

## 问题分析
1. **切换缺陷类型时**：通过watch监听`selectedCode`的变化，能够正确清除对称点提示
2. **切换glassid时**：虽然会更新`currentDefects`并重新绘制缺陷，但没有清除对称点提示
3. **代码流程**：切换glassid时，会调用`loadGlassDefects`加载新的缺陷数据，更新`currentDefects`，然后触发`redrawVisibleDefects`重新绘制缺陷，但这个过程中没有清除`hintLayer`上的对称点提示

## 解决方案
在`redrawVisibleDefects`函数中添加清除对称点提示的代码，因为该函数在切换glassid时会被调用，这样可以确保每次切换glassid或更新缺陷数据时，对称点提示都会被清除

## 实现步骤

### 1. 修改redrawVisibleDefects函数
在`redrawVisibleDefects`函数中添加清除对称点提示的代码：
```javascript
const redrawVisibleDefects = () => {
  if (!defectLayer) return;
  defectLayer.destroyChildren();
  
  // 清除对称点提示
  if (hintLayer) {
    hintLayer.destroyChildren();
    hintLayer.draw();
  }
  
  // 原有代码...
};
```

### 2. 验证修改
运行构建命令和开发服务器，确保修改后的代码能够正确工作

## 代码修改点

1. **CanvasStage.vue**：
   - 在`redrawVisibleDefects`函数中添加清除对称点提示的代码

## 预期效果
- 切换glassid时，当前glass上的对称点提示会被清除
- 切换缺陷类型时，当前显示的对称点提示会被清除
- 点击新缺陷时，旧的对称点提示会被清除
- 更新缺陷数据时，对称点提示会被清除

## 验证步骤
1. 运行`npm run build`命令，确保构建成功
2. 运行`npm run dev`命令，确保开发服务器成功启动
3. 测试切换glassid时，对称点提示是否被清除
4. 测试切换缺陷类型时，对称点提示是否被清除
5. 测试点击新缺陷时，旧的对称点提示是否被清除