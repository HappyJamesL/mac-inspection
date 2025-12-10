## 需求分析

用户希望在CST和LOT下拉列表展开后，当在文本框中输入值时，能对下拉列表的内容进行过滤。当前的实现是点击下拉箭头时会清空文本框，这个功能需要保留，同时添加输入过滤功能。

## 实现方案

1. **添加完整数据存储**：在`selectOptions`中添加`cstFull`和`lotFull`字段，用于存储完整的原始数据
2. **添加过滤逻辑**：
   - 在`loadDropdownData`函数中，将完整数据保存到`cstFull`和`lotFull`
   - 添加计算属性或方法，根据当前输入值过滤数据
3. **修改UI模板**：
   - 修改下拉列表的v-for循环，使用过滤后的列表
   - 添加输入事件监听器，当文本框内容变化时更新过滤结果
4. **添加输入事件**：在CST和LOT输入框上添加`@input`事件监听器

## 具体实现步骤

1. **修改`selectOptions`对象**：添加`cstFull`和`lotFull`字段
2. **修改`loadDropdownData`函数**：
   - 将完整数据保存到`selectOptions.cstFull`或`selectOptions.lotFull`
   - 保持清空文本框的功能不变
3. **添加过滤方法**：创建`filterDropdownOptions`方法，根据输入值过滤数据
4. **修改UI模板**：
   - 在CST和LOT输入框上添加`@input`事件监听器，调用过滤方法
   - 修改下拉列表的v-for循环，使用过滤后的列表
5. **调整相关函数**：确保`selectOption`等函数正常工作

## 预期效果

- 点击下拉箭头时，清空文本框并显示完整的下拉列表
- 在文本框中输入值时，下拉列表会根据输入值进行过滤
- 选择下拉列表中的选项后，文本框显示选中值，下拉列表隐藏

## 修改文件

- `frontend/src/views/InspectionView.vue`