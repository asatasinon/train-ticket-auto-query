#!/bin/bash
# 定时任务启动脚本

# 检查当前工作目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 设置默认参数
INTERVAL=${1:-60}
LOG_LEVEL=${2:-INFO}

# 激活虚拟环境（如果存在）
if [ -d ".venv" ]; then
  echo "激活虚拟环境..."
  source .venv/bin/activate
elif [ -d "venv" ]; then
  echo "激活虚拟环境..."
  source venv/bin/activate
fi

# 输出启动信息
echo "===== 启动 Train-Ticket 定时任务 ====="
echo "间隔时间: ${INTERVAL}秒"
echo "日志级别: ${LOG_LEVEL}"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "======================================="

# 启动定时任务
python -m src.timed_task --interval $INTERVAL --log-level $LOG_LEVEL

# 如果命令异常退出，输出错误信息
if [ $? -ne 0 ]; then
  echo "定时任务异常退出，请检查日志获取详细信息"
  exit 1
fi

# 退出虚拟环境
if [ -n "$VIRTUAL_ENV" ]; then
  deactivate
fi 