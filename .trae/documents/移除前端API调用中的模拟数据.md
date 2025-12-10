## 移除前端API调用中的模拟数据

### 问题分析
前端`api.js`文件中所有API调用都包含`catch`块，当真实API请求失败时会返回模拟数据。现在需要移除这些模拟数据，让前端在没有数据时显示为空。

### 解决方案
修改`d:\DEV\Code\JamesRepo\mac-insp\mac-inspection\frontend\src\services\api.js`文件，移除所有`catch`块中的模拟数据返回，让API请求在失败时返回空数据或抛出错误。

### 具体修改点

1. **getDeviceInfo**：移除模拟数据，返回空对象或抛出错误
2. **getLotList**：移除模拟数据，返回空数组
3. **getProductList**：移除模拟数据，返回空数组
4. **getReasonCodeList**：移除模拟数据，返回空数组
5. **getInitData**：移除模拟数据，返回空对象
6. **getProductLayout**：移除模拟数据，返回空对象
7. **getGlassList**：移除模拟数据，返回空数组
8. **getDefects**：移除模拟数据，返回空数组
9. **getDefectsByLot**：移除模拟数据，返回空数组
10. **queryDefectRecords**：移除模拟数据，返回空对象
11. **getRelatedInfoByCstOrLot**：移除模拟数据，返回空对象
12. **filterOptionsByOper**：移除模拟数据，返回空对象
13. **getMachineByIp**：移除模拟数据，返回空对象
14. **getCurrentOperator**：移除模拟数据，返回空对象

### 修改策略
- 对于返回数组的API，在catch块中返回`[]`
- 对于返回对象的API，在catch块中返回`{}`
- 保留错误日志，方便调试

### 预期效果
- 前端在API请求失败时显示为空，不再显示模拟数据
- 部署环境中使用真实API数据
- 保持代码的可读性和可维护性