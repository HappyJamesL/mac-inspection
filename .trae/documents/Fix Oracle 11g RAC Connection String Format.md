## 问题分析
当前 `config.py` 中的Oracle连接字符串格式将service_name作为路径的一部分，这在Oracle 11g RAC环境中无法正常工作。

## 根本原因
对于Oracle 11g RAC，service_name必须作为查询参数（`?service_name=...`）指定，而不是包含在数据库路径中。当使用路径格式时，Oracle驱动会将其解释为SID（实例名），而不是服务名。

## 解决方案
更新 `/d:/DEV/Code/mac-inspection/backend/app/core/config.py` 中的 `DATABASE_URL` 方法，使用Oracle 11g RAC兼容的连接字符串格式：

```python
def DATABASE_URL(self) -> str:
    """根据数据库类型动态生成连接URL"""
    if self.DATABASE_TYPE == "oracle":
        # 使用service_name查询参数以兼容Oracle 11g RAC
        return f"oracle+cx_oracle://{self.ORACLE_USER}:{self.ORACLE_PASSWORD}@{self.ORACLE_HOST}:{self.ORACLE_PORT}/?service_name={self.ORACLE_SERVICE_NAME}&encoding=UTF-8&nencoding=UTF-8"
    else:  # sqlite
        return self.SQLITE_URL
```

## 预期结果
- 应用程序将能够使用服务名成功连接到Oracle 11g RAC数据库
- 连接字符串格式将同时兼容单实例和RAC Oracle环境
- 现有的编码参数将被保留

## 额外说明
- 此修改仅影响Oracle连接，不影响SQLite连接
- 该格式符合SQLAlchemy和cx_Oracle对Oracle 11g RAC的最佳实践
- 保持了原有的环境变量配置方式，无需修改`.env`文件