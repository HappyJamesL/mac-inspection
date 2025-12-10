"""数据库基础配置"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 根据数据库类型动态创建数据库引擎
if settings.DATABASE_TYPE == "oracle":
    # Oracle数据库配置
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,  # Oracle连接超时设置
        echo=settings.DEBUG
    )
elif settings.DATABASE_TYPE == "sqlite":
    # SQLite数据库配置
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        connect_args={"check_same_thread": False}
    )
else:
    raise ValueError(f"不支持的数据库类型: {settings.DATABASE_TYPE}")

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """获取数据库会话的依赖函数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()