# 修复layout显示问题

## 问题分析
1. **try块作用域错误**：在`loadPanelData`函数中，第1093行的`const data = await getProductLayout(props.selectedProductId);`后面缺少了一个大括号闭合，导致try块的作用域错误，`data`变量无法被后续代码访问。
2. **异步操作问题**：由于try块作用域错误，`glassConfig`无法被正确赋值，导致layout无法显示。

## 解决方案
1. 修复`loadPanelData`函数中的try块作用域问题
2. 调整清除对称点提示的代码，确保在合适的时机调用
3. 添加错误处理，确保代码的健壮性

## 实现步骤

### 1. 修复loadPanelData函数中的try块作用域
```javascript
const loadPanelData = async () => {
  if (!props.selectedProductId) return;
  loading.value = true;
  try {
    const data = await getProductLayout(props.selectedProductId);
    // 添加默认值，确保玻璃尺寸始终有效
    glassConfig.size = data.glass_size || { w: 920000, h: 730000 };
    glassConfig.panels = data.panels || [];
    glassConfig.maskRule = data.mask_rule || { cover_x: 5, cover_y: 6, full_shot: 1 };
    
    nextTick(() => {
      initStage();
      calculateMaskPositions();
      drawBackground();
      // 发射layout状态变化事件
      emit('layout-status-change', glassConfig.panels.length > 0);
    });
  } catch(e) {
    console.error('Failed to load panel data:', e);
  } finally {
    loading.value = false;
  }
};
```

### 2. 调整initStage函数中的清除对称点提示代码
- 移除`initStage`函数中添加的清除对称点提示代码，因为此时还没有绘制任何内容
- 保留`loadPanelData`函数中的清除对称点提示代码，但确保在try块内部调用

### 3. 保留selectedCode的watch监听
- 保留对`selectedCode`的watch监听，确保切换缺陷类型时清除对称点提示
- 添加错误处理，确保在`hintLayer`不存在时不会出错

## 预期效果
- layout能够正确显示
- 切换glassid时，对称点提示会被清除
- 切换缺陷类型时，对称点提示会被清除
- 点击新缺陷时，旧的对称点提示会被清除

## 代码修改点

1. **CanvasStage.vue**：
   - 修复`loadPanelData`函数中的try块作用域问题
   - 移除`initStage`函数中添加的清除对称点提示代码
   - 在`selectedCode`的watch监听中添加错误处理

## 验证步骤
1. 运行`npm run dev`启动开发服务器
2. 检查layout是否能够正确显示
3. 测试切换glassid时对称点提示是否被清除
4. 测试切换缺陷类型时对称点提示是否被清除
5. 测试点击新缺陷时旧的对称点提示是否被清除