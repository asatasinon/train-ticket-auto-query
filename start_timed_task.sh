#!/bin/bash
# 定时任务启动脚本

# 检查当前工作目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 默认设置
INTERVAL=60
LOG_LEVEL="INFO"
SERVER=""
USERNAME=""
PASSWORD=""

# 解析参数
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -i|--interval)
      INTERVAL="$2"
      shift
      shift
      ;;
    -l|--log-level)
      LOG_LEVEL="$2"
      shift
      shift
      ;;
    -s|--server)
      SERVER="$2"
      shift
      shift
      ;;
    -u|--username)
      USERNAME="$2"
      shift
      shift
      ;;
    -p|--password)
      PASSWORD="$2"
      shift
      shift
      ;;
    -h|--help)
      echo "使用方法: $0 [选项]"
      echo "选项:"
      echo "  -i, --interval 秒数     设置定时任务的执行间隔，默认60秒"
      echo "  -l, --log-level 级别     设置日志级别 (DEBUG, INFO, WARNING, ERROR)，默认INFO"
      echo "  -s, --server 地址        设置服务器地址"
      echo "  -u, --username 用户名    设置用户名"
      echo "  -p, --password 密码      设置密码"
      echo "  -h, --help               显示此帮助信息"
      exit 0
      ;;
    *)
      echo "未知参数: $1"
      exit 1
      ;;
  esac
done

# 检查服务器地址、用户名和密码
SERVER_ARGS=""
if [ -n "$SERVER" ] && [ -n "$USERNAME" ] && [ -n "$PASSWORD" ]; then
  SERVER_ARGS="--server $SERVER --username $USERNAME --password $PASSWORD"
fi

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
nohup python -m src.timed_task --interval "$INTERVAL" --log-level "$LOG_LEVEL" $SERVER_ARGS > timed_task.log 2>&1 &

# 保存进程ID
echo $! > timed_task.pid
echo "定时任务已启动，进程ID: $(cat timed_task.pid)"
echo "日志保存在 timed_task.log"

# 如果命令异常退出，输出错误信息
if [ $? -ne 0 ]; then
  echo "定时任务异常退出，请检查日志获取详细信息"
  exit 1
fi

# 退出虚拟环境
if [ -n "$VIRTUAL_ENV" ]; then
  deactivate
fi 