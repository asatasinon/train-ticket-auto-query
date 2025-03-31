#!/bin/bash
set -e

# 确保脚本使用LF而非CRLF行尾
# 打印环境信息
echo "启动 Train-Ticket 自动查询工具 Web 应用..."
echo "Python 版本: $(python --version)"
echo "当前目录: $(pwd)"
echo "文件权限检查:"
ls -la /app/docker-entrypoint.sh
echo "环境变量:"
echo "- TS_BASE_URL: $TS_BASE_URL"
echo "- TS_LOG_LEVEL: $TS_LOG_LEVEL"

# 检查目录结构
if [ ! -d "src" ]; then
    echo "错误: 找不到src目录，请确保容器正确构建"
    exit 1
fi

if [ ! -f "src/web/app.py" ]; then
    echo "错误: 找不到Web应用入口文件 src/web/app.py"
    exit 1
fi

# 测试连接
echo "测试与Train-Ticket服务器的连接..."
python -c "import requests; r = requests.get('$TS_BASE_URL', timeout=5); print(f'连接状态: {r.status_code}')" || {
    echo "警告: 无法连接到Train-Ticket服务器 ($TS_BASE_URL)，请检查网络或配置"
    echo "应用将继续启动，但可能无法正常工作"
}

# 启动Web应用
echo "正在启动Web应用..."
python -m src.web.app 