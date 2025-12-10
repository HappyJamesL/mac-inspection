# 修复Machine下拉框无选项的问题

## 问题分析
1. 后端接口返回了equipments数据，但前端没有处理
2. loadInitData函数中缺少将data.equipments赋值给selectOptions.eqs的代码
3. 导致selectOptions.eqs一直是空数组，下拉框没有选项

## 解决方案
在loadInitData函数中添加一行代码，将后端返回的equipments字段赋值给selectOptions.eqs

## 实现步骤
1. 找到loadInitData函数，位置在InspectionView.vue第880-927行
2. 在处理其他初始化数据的地方添加：
   ```javascript
   selectOptions.eqs = data.equipments || [];
   ```
3. 确保代码位置在设置默认选中值之前
4. 验证修复后的效果

## 预期效果
修复后，当页面加载时，selectOptions.eqs会被赋值为后端返回的equipments数据，Machine下拉框会显示正确的选项。