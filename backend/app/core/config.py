"""应用配置管理"""
import os
from typing import List, Optional
from pydantic import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类"""
    # 应用基本配置
    APP_NAME: str = "Mac Insp API"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_TYPE: str = "sqlite"  # 支持: sqlite, oracle
    
    # SQLite配置
    SQLITE_URL: str = "sqlite:///macinsp.db"
    
    # Oracle配置
    ORACLE_USER: Optional[str] = "D1FAMADM"
    ORACLE_PASSWORD: Optional[str] = "fab#test"
    ORACLE_HOST: Optional[str] = "127.0.0.1"
    ORACLE_PORT: Optional[int] = 7013
    ORACLE_SERVICE_NAME: Optional[str] = "DEVUX03"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here-please-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # 权限配置
    ROLE_ADMIN: str = ""  # 固定角色字符串
    
    @property
    def DATABASE_URL(self) -> str:
        """根据数据库类型动态生成连接URL"""
        if self.DATABASE_TYPE == "oracle":
            return f"oracle+cx_oracle://{self.ORACLE_USER}:{self.ORACLE_PASSWORD}@{self.ORACLE_HOST}:{self.ORACLE_PORT}/?service_name={self.ORACLE_SERVICE_NAME}&encoding=UTF-8&nencoding=UTF-8"
        else:  # sqlite
            return self.SQLITE_URL
   
    class Config:
        env_file = ".env"
        case_sensitive = True
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            """解析环境变量"""
            if field_name == "BACKEND_CORS_ORIGINS":
                return [origin.strip() for origin in raw_val.split(",")]
            return raw_val


@lru_cache()
def get_settings():
    """获取配置实例（单例模式）"""
    return Settings()


# 导出配置实例
settings = get_settings()