# Train-Ticket 自动查询工具

这是一个用于与 Train-Ticket 系统进行交互的自动化查询工具，支持多种查询场景的批量执行和性能压测。本工具使用现代Python项目结构和uv包管理器，提供高效的依赖管理和开发体验。

## 项目结构

```
train-ticket-auto-query/
├── pyproject.toml        # 项目配置和依赖管理
├── .env                  # 环境变量配置文件（需要自行创建）
├── src/                  # 源代码目录
│   ├── __init__.py       # 包初始化
│   ├── main.py           # 主入口
│   ├── core/             # 核心模块
│   │   ├── __init__.py
│   │   ├── queries.py    # 查询类
│   │   └── atomic_queries.py # 原子级别查询
│   ├── utils/            # 工具模块
│   │   ├── __init__.py
│   │   ├── config.py     # 配置管理
│   │   └── helpers.py    # 辅助函数
│   ├── scenarios/        # 场景模块
│   │   ├── __init__.py
│   │   ├── scenarios.py  # 场景定义
│   │   └── runners.py    # 场景执行器
│   └── timed_task.py     # 定时任务工具
├── tests/                # 测试目录
│   ├── test_connection.py # 连接测试
│   └── test_login.py     # 登录测试
├── examples/             # 示例目录
│   └── example.py        # 使用示例
├── start_timed_task.sh   # 定时任务启动脚本 (Linux/macOS)
├── start_timed_task.bat  # 定时任务启动脚本 (Windows)
└── archive/              # 归档文件夹
    ├── README.md         # 归档说明
    └── old_scripts/      # 旧版脚本
```

## 环境要求

- Python 3.8 或更高版本
- requests 库
- python-dotenv 库
- schedule 库
- 有效的 Train-Ticket 微服务系统实例

## 安装 uv 包管理器

[uv](https://github.com/astral-sh/uv) 是一个快速、可靠的Python包安装和管理工具，比传统的pip速度更快。推荐使用它来管理依赖。

### 安装 uv

#### 方法 1: 通过安装脚本（推荐）

**Linux/macOS**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell)**:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 方法 2: 通过 pip 安装
```bash
pip install uv
```

#### 方法 3: 通过 Homebrew (macOS)
```bash
brew install uv
```

#### 方法 4: 通过 Conda
```bash
conda install -c conda-forge uv
```

## 配置

在项目根目录创建 `.env` 文件，配置以下环境变量（或者复制 `.env.example` 并修改）：

```
# 服务器配置
TS_BASE_URL=http://train-ticket-server-address:port
TS_USERNAME=your_username
TS_PASSWORD=your_password

# 日期配置（如果不设置则使用当前日期）
TS_DEFAULT_DATE=2023-08-01

# 查询配置
TS_HIGHSPEED_WEIGHT=60
TS_NORMAL_WEIGHT=40

# 批量执行配置
TS_BATCH_COUNT=100
TS_BATCH_INTERVAL=1

# 日志级别
TS_LOG_LEVEL=INFO

# 压测配置
TS_STRESS_CONCURRENT=10     # 压测并发数
TS_STRESS_COUNT=100         # 压测总请求数
TS_STRESS_SCENARIO=high_speed  # 压测场景
TS_STRESS_TIMEOUT=30        # 请求超时时间(秒)
TS_STRESS_INTERVAL=0.1      # 并发线程启动间隔(秒)
TS_STRESS_ERROR_RATE_THRESHOLD=0.1  # 可接受的错误率阈值
```

## 安装依赖

### 使用 uv 安装（推荐）

创建并激活虚拟环境：
```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境 (Linux/macOS)
source .venv/bin/activate
# 或者 Windows
.venv\Scripts\activate
```

安装项目依赖：
```bash
# 开发模式安装
uv pip install -e .

# 或者从requirements.txt安装
uv pip install -r requirements.txt
```

### 使用传统 pip 安装
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Linux/macOS)
source venv/bin/activate
# 或者 Windows
venv\Scripts\activate

# 安装依赖
pip install -e .
```

## 使用方法

### 测试连接和登录

```bash
python -m src.main --test-connection
```

### 执行特定场景

```bash
python -m src.main --scenario query_high_speed
```

可用的场景：
- `book`: 预订车票
- `cancel`: 查询并取消订单
- `collect_ticket`: 查询并取票
- `consign`: 查询并添加托运信息
- `food`: 查询食品
- `high_speed`: 查询高铁票
- `normal`: 查询普通列车票
- `parallel`: 并行查询车票
- `pay`: 查询并支付订单
- `rebook`: 查询并改签车票

### 批量执行随机场景

```bash
python -m src.main --batch 50
```

### 执行定时任务

定时任务工具会按照场景的实际使用顺序依次执行所有场景，并在执行完所有场景后重新开始循环。

#### 使用启动脚本

**Linux/macOS**:
```bash
# 启动定时任务（默认60秒间隔）
./start_timed_task.sh

# 指定间隔时间和日志级别
./start_timed_task.sh -i 120 -l DEBUG

# 指定token刷新间隔（默认1800秒，即30分钟）
./start_timed_task.sh -r 3600

# 显示帮助信息
./start_timed_task.sh -h
```

**Windows**:
```cmd
# 启动定时任务（默认60秒间隔）
start_timed_task.bat

# 指定间隔时间和日志级别
start_timed_task.bat -i 120 -l DEBUG

# 指定token刷新间隔（默认1800秒，即30分钟）
start_timed_task.bat -r 3600

# 显示帮助信息
start_timed_task.bat -h
```

可用参数：
- `-i, --interval`: 设置定时任务的执行间隔，单位为秒，默认60秒
- `-r, --token-refresh`: 设置token刷新间隔，单位为秒，默认1800秒（30分钟）
- `-l, --log-level`: 设置日志级别 (DEBUG, INFO, WARNING, ERROR)，默认INFO
- `-s, --server`: 设置服务器地址
- `-u, --username`: 设置用户名
- `-p, --password`: 设置密码
- `-h, --help`: 显示帮助信息

#### 直接使用Python

```bash
# 使用默认间隔（60秒）
python -m src.timed_task

# 使用自定义间隔（30秒）
python -m src.timed_task --interval 30

# 使用自定义日志级别
python -m src.timed_task --log-level DEBUG
```

#### 使用Docker

也可以通过Docker来运行定时任务：

```bash
# 构建并启动定时任务容器
docker-compose up -d train-ticket-timed-task

# 查看定时任务容器日志
docker logs -f train-ticket-timed-task

# 停止定时任务容器
docker-compose stop train-ticket-timed-task
```

定时任务容器的配置参数可在docker-compose.yml文件中修改：

```yaml
environment:
  TS_BASE_URL: "http://train-ticket-server-address:port"
  TS_USERNAME: "your_username"
  TS_PASSWORD: "your_password"
  TS_TIMED_TASK_INTERVAL: "60"  # 定时任务执行间隔（秒）
  TS_TOKEN_REFRESH_INTERVAL: "1800"  # token刷新间隔（秒，默认30分钟）
  TS_LOG_LEVEL: "INFO"  # 日志级别
  TZ: "Asia/Shanghai"  # 设置容器时区为东八区（北京/上海时间）
```

### 执行压测

详细的压测使用说明请参考[压测工具使用说明](docs/stress_testing.md)。

基本用法：
```bash
# 使用默认配置执行压测
python -m src.stress

# 指定场景进行压测
python -m src.stress --scenario high_speed

# 指定并发数和总请求数
python -m src.stress --concurrent 20 --count 200

# 更多选项
python -m src.stress --help
```

### 查看当前配置

```bash
python -m src.main --config
```

### 运行示例

使用 python 运行：
```bash
python examples/example.py
```

使用 uv 运行（自动选择正确的Python版本）：
```bash
uv run examples/example.py
```

## 开发

### 使用 uv 进行开发

#### 安装开发依赖
```bash
uv pip install -e ".[dev]"
```

#### 运行测试
```bash
# 使用 Python 运行
python tests/test_connection.py
python tests/test_login.py

# 或使用 uv 运行
uv run tests/test_connection.py
uv run tests/test_login.py
```

#### uv 的其他实用命令

**管理依赖**:
```bash
# 添加新依赖
uv pip install -r requirements.txt requests
uv pip freeze > requirements.txt  # 更新依赖列表

# 更新特定包
uv pip install -U requests
uv pip freeze > requirements.txt  # 更新依赖列表

# 查看依赖树
uv pip list -v

# 显示可更新的包
uv pip list --outdated
```

**使用特定的Python版本**:
```bash
# 安装Python 3.10和3.11
uv python install 3.10 3.11

# 为当前项目指定Python版本
uv python pin 3.11

# 创建使用特定Python版本的虚拟环境
uv venv --python 3.11

# 使用特定Python版本运行脚本
uv run --python 3.11 examples/example.py
```

## 故障排除

### 1. 登录失败

如果登录失败，可能有以下原因：
- 服务器地址不正确：检查.env文件中的TS_BASE_URL配置
- 用户名或密码错误：检查.env文件中的TS_USERNAME和TS_PASSWORD配置
- 服务器未运行或不可访问：确保Train-Ticket系统正常运行
- 网络问题：检查防火墙或网络连接

运行连接测试脚本诊断问题：
```bash
python tests/test_connection.py
```

### 2. 导入错误

如果遇到相对导入错误，可能是因为Python的导入机制问题，可以：
- 安装项目包：`uv pip install -e .`
- 使用模块方式运行：`python -m src.main` 而不是 `python src/main.py`

## 了解更多

- [uv 官方文档](https://docs.astral.sh/uv/)
- [python-dotenv 文档](https://github.com/theskumar/python-dotenv)
- [Train-Ticket 系统](https://github.com/FudanSELab/train-ticket)

## 文档

- [压测工具使用说明](docs/stress_testing.md) - 详细的压测配置和使用指南

### 时区设置

本项目默认使用中国标准时间（CST，即UTC+8，Asia/Shanghai时区）。在Docker容器中，时区通过以下方式设置：

1. Dockerfile中设置了TZ环境变量并配置了系统时区
2. docker-compose.yml中通过环境变量TZ="Asia/Shanghai"设置
3. Python代码中使用os.environ['TZ']和time.tzset()设置当前进程的时区

如需使用其他时区，可修改docker-compose.yml中的TZ环境变量。
