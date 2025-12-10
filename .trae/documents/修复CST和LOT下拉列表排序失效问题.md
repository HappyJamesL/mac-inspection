## 问题分析

用户反馈CST和LOT点击下拉展开的列表递增排序失效。通过代码检查，发现问题出在`loadDropdownData`函数中：

- 当用户点击下拉箭头时，会触发`loadDropdownData`函数
- 该函数直接从API获取最新的初始化数据
- 更新`selectOptions.cst`或`selectOptions.lots`后，没有调用排序函数
- 导致下拉列表显示的是API返回的原始顺序，而不是排序后的顺序

## 解决方案

修改`loadDropdownData`函数，在更新CST和LOT列表后添加排序逻辑：

1. 在`loadDropdownData`函数中，当更新`selectOptions.cst`后，添加`selectOptions.cst.sort()`
2. 在`loadDropdownData`函数中，当更新`selectOptions.lots`后，添加`selectOptions.lots.sort()`

## 具体实现步骤

1. 打开`InspectionView.vue`文件
2. 找到`loadDropdownData`函数
3. 在更新`selectOptions.cst`后添加排序逻辑
4. 在更新`selectOptions.lots`后添加排序逻辑

## 预期效果

- 当用户点击CST下拉箭头时，展开的列表会按递增顺序排序
- 当用户点击LOT下拉箭头时，展开的列表会按递增顺序排序
- 与之前在`loadInitData`和`onOperChange`函数中添加的排序逻辑保持一致