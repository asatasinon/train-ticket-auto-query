#!/bin/bash
set -e

# 配置信息
echo "启动 Train-Ticket 自动查询工具定时任务..."
echo "Python 版本: $(python --version)"
echo "当前目录: $(pwd)"
echo "当前时间: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "系统时区: $(cat /etc/timezone) ($(date +%z))"
echo "环境变量:"
echo "- TS_BASE_URL: $TS_BASE_URL"
echo "- TS_LOG_LEVEL: $TS_LOG_LEVEL"
echo "- TS_TIMED_TASK_INTERVAL: $TS_TIMED_TASK_INTERVAL"

# 检查目录结构
if [ ! -d "src" ]; then
    echo "错误: 找不到src目录，请确保容器正确构建"
    exit 1
fi

if [ ! -f "src/timed_task.py" ]; then
    echo "错误: 找不到定时任务入口文件 src/timed_task.py"
    exit 1
fi

# 测试连接
echo "测试与Train-Ticket服务器的连接..."
python -c "import requests; r = requests.get('$TS_BASE_URL', timeout=5); print(f'连接状态: {r.status_code}')" || {
    echo "警告: 无法连接到Train-Ticket服务器 ($TS_BASE_URL)，请检查网络或配置"
    echo "应用将继续启动，但可能无法正常工作"
}

# 设置默认的间隔时间（如果未指定）
if [ -z "$TS_TIMED_TASK_INTERVAL" ]; then
    export TS_TIMED_TASK_INTERVAL=60
    echo "未设置TS_TIMED_TASK_INTERVAL，使用默认值: 60秒"
fi

# 启动定时任务
echo "正在启动定时任务，间隔时间: ${TS_TIMED_TASK_INTERVAL}秒..."
echo "每次完成所有场景后将退出登录，下次循环开始时重新登录"

# 启动定时任务
exec python -m src.timed_task \
  --server "$TS_BASE_URL" \
  --username "$TS_USERNAME" \
  --password "$TS_PASSWORD" \
  --interval "$TS_TIMED_TASK_INTERVAL" \
  --health-file "/tmp/health_check" \
  --log-level "$TS_LOG_LEVEL" 