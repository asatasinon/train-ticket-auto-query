# Docker部署说明

本文档介绍如何使用Docker容器部署和运行Train-Ticket自动查询工具的Web应用。

## 1. 前提条件

确保您的系统已安装：

- Docker (20.10.0+)
- Docker Compose (v2.0.0+) (可选，但推荐)

## 2. 快速部署（推荐）

我们提供了一个一键部署脚本，可以自动处理构建和运行过程：

```bash
# 赋予脚本执行权限
chmod +x build-and-run.sh

# 运行部署脚本
./build-and-run.sh
```

脚本会自动：
1. 创建日志目录
2. 确保入口脚本有执行权限
3. 停止并删除旧容器（如果存在）
4. 构建新镜像
5. 启动容器

部署完成后，访问：`http://localhost:5001`

## 3. 使用Docker Compose部署

如果您希望手动控制部署过程，也可以直接使用Docker Compose：

### 3.1 准备工作

```bash
# 创建日志目录
mkdir -p logs

# 确保脚本有执行权限
chmod +x docker-entrypoint.sh
```

### 3.2 构建并启动容器

```bash
# 构建镜像
docker-compose build

# 构建并在后台启动容器
docker-compose up -d

# 查看容器日志
docker-compose logs -f
```

### 3.3 访问Web应用

在浏览器中访问：`http://localhost:5001`

### 3.4 停止和删除容器

```bash
docker-compose down
```

## 4. 使用Docker命令部署

如果您不想使用Docker Compose，也可以直接使用Docker命令：

### 4.1 构建镜像

```bash
docker build -t train-ticket-auto-query .
```

### 4.2 启动容器

```bash
docker run -d --name train-ticket-auto-query -p 5001:5001 -v $(pwd)/logs:/app/logs train-ticket-auto-query
```

### 4.3 访问Web应用

在浏览器中访问：`http://localhost:5001`

### 4.4 查看容器日志

```bash
docker logs -f train-ticket-auto-query
```

### 4.5 停止和删除容器

```bash
docker stop train-ticket-auto-query
docker rm train-ticket-auto-query
```

## 5. 自定义配置

### 5.1 使用环境变量

您可以通过环境变量覆盖默认配置：

```bash
# 使用Docker Compose
# 编辑docker-compose.yml文件中的environment部分

# 使用Docker命令
docker run -d --name train-ticket-auto-query \
  -p 5001:5001 \
  -v $(pwd)/logs:/app/logs \
  -e TS_BASE_URL="http://你的服务器地址:端口" \
  -e TS_USERNAME="你的用户名" \
  -e TS_PASSWORD="你的密码" \
  train-ticket-auto-query
```

### 5.2 可用的环境变量

| 环境变量 | 说明 | 默认值 |
|---------|------|-------|
| TS_BASE_URL | Train-Ticket系统地址 | http://101.47.134.73:32677 |
| TS_USERNAME | 登录用户名 | fdse_microservice |
| TS_PASSWORD | 登录密码 | 111111 |
| TS_LOG_LEVEL | 日志级别 | INFO |
| ... | 更多配置见.env.example | ... |

## 6. 故障排除

### 6.1 容器无法启动

检查日志：
```bash
docker logs train-ticket-auto-query
```

如果遇到权限问题，确保执行了以下操作：
```bash
chmod +x docker-entrypoint.sh
```

### 6.2 无法连接到Train-Ticket服务器

确保您的Train-Ticket服务器地址正确：
- 检查TS_BASE_URL环境变量
- 确认服务器可以正常访问
- 如果使用的是局域网地址，确保Docker容器能够访问该地址

### 6.3 Web界面无法加载

- 确认容器正在运行：`docker ps`
- 检查端口映射是否正确：`docker port train-ticket-auto-query`
- 检查防火墙设置，确保5001端口未被阻止 