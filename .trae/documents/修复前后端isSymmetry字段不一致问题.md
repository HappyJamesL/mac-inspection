## 问题分析
前端本地缓存时isSymmetry: false，但数据库中IS_SYMMETRY却是Y，原因是前端在转换is_symmetry字段时，没有正确处理字符串类型的is_symmetry值。

## 问题定位
在前端`api.js`文件中，第146行的转换逻辑存在问题：
```javascript
is_symmetry: (defectRecord.isSymmetry !== undefined ? defectRecord.isSymmetry : defectRecord.is_symmetry) ? 'Y' : 'N',
```
当`defectRecord.isSymmetry`未定义，而`defectRecord.is_symmetry`是字符串'N'时，'N'会被JavaScript转换为true，导致最终结果为'Y'。

## 修复方案
修改前端`api.js`文件中的转换逻辑，正确处理字符串类型的is_symmetry值：

1. **修改`api.js`文件**：
   - 第146行的转换逻辑需要正确处理字符串类型的is_symmetry值
   - 当值为字符串时，直接比较是否为'Y'，否则使用布尔值判断

2. **检查`InspectionView.vue`文件**：
   - 确保第881行的转换逻辑也正确处理字符串类型

## 预期效果
修复后，前端isSymmetry: false会正确转换为后端is_symmetry: 'N'，前后端保持一致。