# /app/mac-inspection/backend/gunicorn.conf.py
import multiprocessing
import os

# 基础配置
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 2

# 注释掉用户和组设置
# user = "www-data"  # 不指定
# group = "www-data"  # 不指定

# 日志输出到控制台
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Worker 管理
max_requests = 1000
max_requests_jitter = 50