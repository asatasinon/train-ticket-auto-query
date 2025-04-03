FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# # 安装必要的系统依赖
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# 设置Python环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 从.env文件中提取的默认环境变量
ENV TS_BASE_URL="http://101.47.134.73:32677" \
    TS_USERNAME="fdse_microservice" \
    TS_PASSWORD="111111" \
    TS_DEFAULT_DATE="" \
    TS_PLACE_SHANG_HAI="Shang Hai" \
    TS_PLACE_SU_ZHOU="Su Zhou" \
    TS_PLACE_NAN_JING="Nan Jing" \
    TS_HIGHSPEED_WEIGHT="60" \
    TS_NORMAL_WEIGHT="40" \
    TS_BATCH_COUNT="100" \
    TS_BATCH_INTERVAL="1" \
    TS_STRESS_CONCURRENT="10" \
    TS_STRESS_COUNT="100" \
    TS_STRESS_SCENARIO="high_speed" \
    TS_STRESS_TIMEOUT="30" \
    TS_STRESS_INTERVAL="0.1" \
    TS_STRESS_ERROR_RATE_THRESHOLD="0.1" \
    TS_LOG_LEVEL="INFO"

# 复制requirements.txt并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制入口脚本
COPY docker-entrypoint.sh .
# 确保脚本有执行权限 (添加多种方式确保权限正确设置)
RUN chmod +x /app/docker-entrypoint.sh && \
    chmod 755 /app/docker-entrypoint.sh && \
    ls -la /app/docker-entrypoint.sh

# 复制项目文件
COPY . .

# 再次确保脚本有执行权限 (针对COPY操作可能覆盖文件的情况)
RUN chmod +x /app/docker-entrypoint.sh && \
    chmod 755 /app/docker-entrypoint.sh && \
    ls -la /app/docker-entrypoint.sh

# 暴露端口
EXPOSE 5001

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/ || exit 1

# 设置入口点 (使用shell形式，可以绕过权限问题)
CMD ["/bin/bash", "/app/docker-entrypoint.sh"] 