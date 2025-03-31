#!/bin/bash
# 构建并运行Train-Ticket自动查询工具Docker容器

# 确保脚本在出错时退出
set -e

echo "===== Train-Ticket 自动查询工具Docker部署脚本 ====="

# 创建日志目录
mkdir -p logs
echo "已创建logs目录"

# 确保docker-entrypoint.sh有执行权限
echo "确保docker-entrypoint.sh有执行权限..."
chmod +x docker-entrypoint.sh
echo "权限已设置"

# 停止并删除旧容器（如果存在）
echo "停止并删除旧容器（如果存在）..."
docker-compose down 2>/dev/null || true
echo "旧容器已清理"

# 构建新镜像
echo "构建Docker镜像..."
docker-compose build --no-cache
echo "镜像构建完成"

# 启动容器
echo "启动容器..."
docker-compose up -d
echo "容器已启动"

# 显示容器状态
echo "容器状态:"
docker-compose ps

echo ""
echo "Web应用已启动！请访问: http://localhost:5001"
echo "查看日志: docker-compose logs -f"
echo "===== 部署完成 =====" 