"""历史数据库基础配置"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 根据数据库类型动态创建历史数据库引擎
if settings.HISTORICAL_DATABASE_TYPE == "oracle":
    # 历史Oracle数据库配置
    historical_engine = create_engine(
        settings.HISTORICAL_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,  # Oracle连接超时设置
        echo=settings.DEBUG
    )
elif settings.HISTORICAL_DATABASE_TYPE == "sqlite":
    # 历史SQLite数据库配置
    historical_engine = create_engine(
        settings.HISTORICAL_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        connect_args={"check_same_thread": False}
    )
else:
    raise ValueError(f"不支持的历史数据库类型: {settings.HISTORICAL_DATABASE_TYPE}")

# 创建历史数据库会话工厂
HistoricalSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=historical_engine)

# 创建历史数据库基类
HistoricalBase = declarative_base()


def get_historical_db():
    """获取历史数据库会话的依赖函数"""
    db = HistoricalSessionLocal()
    try:
        yield db
    finally:
        db.close()
