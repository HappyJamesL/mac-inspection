#!/bin/bash
# /app/mac-inspection/backend/start.sh
set -e

# 配置变量
APP_NAME="mac-inspection"
APP_DIR="/app/mac-inspection/backend"
VENV_PATH="$APP_DIR/venv3"
CONFIG_FILE="$APP_DIR/gunicorn.conf.py"
LOG_DIR="/tmp/gunicorn_logs"
PID_DIR="/tmp/gunicorn_pids"
USER=$(whoami)  # 使用当前用户
GROUP=$(id -gn)  # 使用当前用户的组

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    local level=$1
    local message=$2
    case $level in
        "info") echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $message" ;;
        "warn") echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $message" ;;
        "error") echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $message" ;;
    esac
}

# 创建必要目录
create_dirs() {
    log "info" "创建日志和PID目录..."
    mkdir -p "$LOG_DIR"
    mkdir -p "$PID_DIR"
    chmod 755 "$LOG_DIR" "$PID_DIR"
    log "info" "目录创建完成: $LOG_DIR, $PID_DIR"
}

# 检查环境
check_environment() {
    log "info" "检查环境..."
    
    # 检查Python和pip
    local python_cmds=("python3.9" "/usr/local/bin/python3.9/bin/python3.9" "python3.9.x" "python" "python3")
    
    for cmd in "${python_cmds[@]}"; do
        if command -v "$cmd" &> /dev/null; then
            # 检查版本是否为3.9.x
            version=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
            if [[ "$version" == "3.9" ]]; then
                log "info" "找到 Python 3.9 (命令: $cmd)"
                PYTHON_CMD="$cmd"
                return 0
            fi
        fi
    done
    
    log "error" "未找到 Python 3.9"
    return 1
    
    # 检查虚拟环境
    if [ ! -f "$VENV_PATH/bin/activate" ]; then
        log "warn" "虚拟环境不存在: $VENV_PATH"
        return 1
    fi
    
    # 检查应用目录
    if [ ! -f "$APP_DIR/main.py" ]; then
        log "error" "主文件不存在: $APP_DIR/main.py"
        return 1
    fi
    
    log "info" "环境检查通过"
    log "info" "当前用户: $USER, 组: $GROUP"
    return 0
}

# 激活虚拟环境
activate_venv() {
    log "info" "激活虚拟环境..."
    source "$VENV_PATH/bin/activate"
    log "info" "Python路径: $(which python)"
    log "info" "Python版本: $(python --version 2>&1)"
}

# 检查端口占用
check_port() {
    local port=${1:-8000}
    log "info" "检查端口 $port 占用情况..."
    
    if netstat -tln 2>/dev/null | grep -q ":$port "; then
        local pid=$(lsof -ti:$port 2>/dev/null | head -1)
        local process=$(ps -p $pid -o cmd= 2>/dev/null || echo "未知进程")
        log "warn" "端口 $port 已被占用 (PID: $pid, 进程: $process)"
        return 1
    fi
    
    log "info" "端口 $port 可用"
    return 0
}

# 启动Gunicorn
start_gunicorn() {
    log "info" "启动 $APP_NAME..."
    
    cd "$APP_DIR"
    
    # 检查是否已在运行
    if [ -f "$PID_DIR/$APP_NAME.pid" ]; then
        local pid=$(cat "$PID_DIR/$APP_NAME.pid" 2>/dev/null)
        if [ -n "$pid" ] && ps -p $pid > /dev/null 2>&1; then
            log "warn" "应用已在运行 (PID: $pid)"
            return 0
        fi
    fi
    
    # 清理旧的PID文件
    rm -f "$PID_DIR/$APP_NAME.pid"
    
    # 启动命令 - 不指定user/group
    nohup gunicorn main:app \
        -c "$CONFIG_FILE" \
        --daemon \
        --pid "$PID_DIR/$APP_NAME.pid" \
        --access-logfile "$LOG_DIR/access.log" \
        --error-logfile "$LOG_DIR/error.log" \
        > "$LOG_DIR/startup.log" 2>&1 &
    
    # 等待进程启动
    local timeout=10
    while [ $timeout -gt 0 ]; do
        if [ -f "$PID_DIR/$APP_NAME.pid" ]; then
            local pid=$(cat "$PID_DIR/$APP_NAME.pid" 2>/dev/null)
            if [ -n "$pid" ] && ps -p $pid > /dev/null 2>&1; then
                log "info" "$APP_NAME 启动成功 (PID: $pid)"
                return 0
            fi
        fi
        sleep 1
        ((timeout--))
    done
    
    log "error" "$APP_NAME 启动失败，查看日志: $LOG_DIR/startup.log"
    tail -20 "$LOG_DIR/startup.log"
    return 1
}

# 监控进程状态
monitor_process() {
    if [ -f "$PID_DIR/$APP_NAME.pid" ]; then
        local pid=$(cat "$PID_DIR/$APP_NAME.pid" 2>/dev/null)
        if [ -n "$pid" ] && ps -p $pid > /dev/null 2>&1; then
            # 获取进程信息
            local cmd=$(ps -p $pid -o cmd= 2>/dev/null | head -1)
            local start_time=$(ps -p $pid -o lstart= 2>/dev/null | head -1)
            local cpu=$(ps -p $pid -o %cpu= 2>/dev/null | head -1)
            local mem=$(ps -p $pid -o rss= 2>/dev/null | awk '{printf "%.2f MB", $1/1024}')
            
            # 获取worker数量
            local workers=$(ps aux | grep -c "[g]unicorn.*worker")
            
            echo -e "${GREEN}✓ 应用运行正常${NC}"
            echo "主进程PID: $pid"
            echo "启动时间: $start_time"
            echo "CPU使用率: $cpu%"
            echo "内存使用: $mem"
            echo "Worker数量: $workers"
            echo "PID文件: $PID_DIR/$APP_NAME.pid"
            echo "访问日志: $LOG_DIR/access.log"
            echo "错误日志: $LOG_DIR/error.log"
            
            # 检查端口
            if netstat -tln 2>/dev/null | grep -q ":8000 "; then
                echo -e "${GREEN}✓ 端口8000监听正常${NC}"
            else
                echo -e "${RED}✗ 端口8000未监听${NC}"
            fi
            
            return 0
        fi
    fi
    
    echo -e "${RED}✗ 应用未运行${NC}"
    return 1
}

# 停止应用
stop_gunicorn() {
    log "info" "停止 $APP_NAME..."
    
    if [ -f "$PID_DIR/$APP_NAME.pid" ]; then
        local pid=$(cat "$PID_DIR/$APP_NAME.pid" 2>/dev/null)
        
        if [ -n "$pid" ] && ps -p $pid > /dev/null 2>&1; then
            # 优雅关闭
            log "info" "优雅停止进程 $pid..."
            kill -TERM $pid
            
            # 等待进程退出
            local timeout=30
            while ps -p $pid > /dev/null 2>&1 && [ $timeout -gt 0 ]; do
                sleep 1
                ((timeout--))
            done
            
            if ps -p $pid > /dev/null 2>&1; then
                log "warn" "强制终止进程 $pid..."
                kill -9 $pid
            fi
        fi
        
        rm -f "$PID_DIR/$APP_NAME.pid"
        log "info" "进程已停止"
    else
        log "warn" "PID文件不存在，尝试查找进程..."
        
        # 尝试通过名称查找进程
        local pids=$(pgrep -f "gunicorn.*main:app" 2>/dev/null || echo "")
        if [ -n "$pids" ]; then
            echo $pids | xargs kill -TERM
            log "info" "已发送停止信号"
        else
            log "info" "未找到相关进程"
        fi
    fi
}

# 重载应用
reload_gunicorn() {
    if [ -f "$PID_DIR/$APP_NAME.pid" ]; then
        local pid=$(cat "$PID_DIR/$APP_NAME.pid" 2>/dev/null)
        if [ -n "$pid" ] && ps -p $pid > /dev/null 2>&1; then
            log "info" "重新加载配置 (PID: $pid)..."
            kill -HUP $pid
            log "info" "重新加载信号已发送"
        else
            log "error" "进程不存在 (PID: $pid)"
        fi
    else
        log "error" "PID文件不存在"
    fi
}

# 清理日志
clean_logs() {
    local days=${1:-7}
    log "info" "清理 $days 天前的日志..."
    
    find "$LOG_DIR" -name "*.log" -mtime +$days -delete
    log "info" "日志清理完成"
}

# 查看日志
view_logs() {
    local log_type=${1:-"error"}
    
    case $log_type in
        "access")
            echo -e "${BLUE}=== 访问日志 ===${NC}"
            tail -50 "$LOG_DIR/access.log"
            ;;
        "error")
            echo -e "${BLUE}=== 错误日志 ===${NC}"
            tail -50 "$LOG_DIR/error.log"
            ;;
        "startup")
            echo -e "${BLUE}=== 启动日志 ===${NC}"
            tail -50 "$LOG_DIR/startup.log"
            ;;
        "all")
            echo -e "${BLUE}=== 所有日志 ===${NC}"
            echo -e "${GREEN}访问日志:${NC}"
            tail -20 "$LOG_DIR/access.log"
            echo -e "\n${YELLOW}错误日志:${NC}"
            tail -20 "$LOG_DIR/error.log"
            echo -e "\n${BLUE}启动日志:${NC}"
            tail -20 "$LOG_DIR/startup.log"
            ;;
        *)
            echo "用法: $0 logs {access|error|startup|all}"
            ;;
    esac
}

# 主函数
main() {
    case "${1:-start}" in
        start)
            create_dirs
            if ! check_environment; then
                exit 1
            fi
            activate_venv
            if ! check_port 8000; then
                read -p "端口已被占用，是否继续？(y/n): " -n 1 -r
                echo
                [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
            fi
            start_gunicorn
            sleep 2
            monitor_process
            ;;
        stop)
            stop_gunicorn
            ;;
        restart)
            stop_gunicorn
            sleep 3
            create_dirs
            if ! check_environment; then
                exit 1
            fi
            activate_venv
            start_gunicorn
            sleep 2
            monitor_process
            ;;
        status)
            monitor_process
            ;;
        reload)
            reload_gunicorn
            ;;
        monitor)
            clear
            while true; do
                echo -e "${BLUE}=== $APP_NAME 监控面板 ===${NC}"
                echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
                echo "用户: $USER"
                echo
                monitor_process
                echo
                echo -e "${YELLOW}按 Ctrl+C 退出监控${NC}"
                echo
                sleep 5
                clear
            done
            ;;
        logs)
            view_logs "$2"
            ;;
        clean)
            clean_logs "$2"
            ;;
        *)
            echo -e "${BLUE}使用方法: $0 {command}${NC}"
            echo
            echo "命令:"
            echo "  start     启动应用"
            echo "  stop      停止应用"
            echo "  restart   重启应用"
            echo "  status    查看状态"
            echo "  reload    重载配置（不重启）"
            echo "  monitor   实时监控"
            echo "  logs      查看日志 {access|error|startup|all}"
            echo "  clean     清理日志 {天数，默认7}"
            echo
            echo "示例:"
            echo "  $0 start"
            echo "  $0 logs error"
            echo "  $0 clean 30"
            ;;
    esac
}

main "$@"