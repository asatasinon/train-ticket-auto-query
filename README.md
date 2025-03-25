# Train-Ticket 自动查询工具

用于自动化测试和模拟用户操作的火车票系统查询工具集。该项目提供了一套全面的Python脚本，用于与Train-Ticket微服务系统交互，模拟真实用户的各种操作场景。

## 项目介绍

Train-Ticket自动查询工具是一个功能完整的测试框架，可以模拟用户在火车票系统中的各种操作，包括查询车票、预订车票、支付订单、取消订单、改签等。该工具采用模块化设计，具有良好的扩展性和可配置性，适用于微服务测试、性能测试和用户行为模拟。项目使用uv进行依赖管理，确保更快速、可靠的包安装和环境管理。

## 功能特点

- **支持多种用户操作场景**：
  - 查询并预订车票
  - 取消订单
  - 付款操作
  - 改签操作
  - 验票进站
  - 托运行李
  - 订餐服务
  - 路线查询
  - 行程查询（高铁和普通列车）
  - 高级查询（最便宜、最快、最少站点）

- **模拟真实用户行为**：
  - 随机选择出发地和目的地
  - 随机选择是否购买食物
  - 随机选择是否需要保险
  - 随机选择是否托运行李
  - 支持高铁和普通列车查询

- **可配置性高**：
  - 所有配置项通过.env文件集中管理
  - 支持设置服务器地址、用户凭据、查询参数等
  - 易于在不同环境中部署和使用
  - 使用uv进行版本控制和依赖管理，确保环境一致性

## 项目结构

```
train-ticket-auto-query/
├── config.py                   # 配置管理模块，从.env加载配置
├── queries.py                  # 核心查询类，封装所有API操作
├── utils.py                    # 工具函数，如随机选择、生成随机数据等
├── atomic_queries.py           # 原子级别的API操作实现
├── scenarios.py                # 定义各种用户场景的模拟流程
├── example.py                  # 示例脚本，演示配置使用和场景执行
├── test_connection.py          # 测试连接和登录的脚本
├── test_login.py               # 专门用于测试登录功能的脚本
├── .env                        # 实际配置文件（需要自行创建）
├── .env.example                # 配置文件模板
├── requirements.txt            # 项目依赖
└── setup.py                    # 安装脚本
```

## 安装说明

### 环境要求

- Python 3.8 或更高版本（支持 3.8、3.9、3.10、3.11、3.12、3.13）
- requests 库
- python-dotenv 库
- 有效的Train-Ticket微服务系统实例

### 安装步骤

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/train-ticket-auto-query.git
cd train-ticket-auto-query
```

2. 安装uv（如果尚未安装）：

Linux/macOS:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows (PowerShell):
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

使用pip:
```bash
pip install uv
```

3. 创建并激活虚拟环境：

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
# Linux/macOS:
. .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

4. 安装依赖：

```bash
# 安装requirements.txt中的依赖
uv pip install -r requirements.txt

# 或者使用开发者模式安装
uv pip install -e .
```

## 配置说明

本项目使用.env文件进行配置管理，支持以下配置项：

```
# Train-Ticket系统URL配置
TS_BASE_URL=http://your-train-ticket-server:port

# 用户登录凭据
TS_USERNAME=fdse_microservice
TS_PASSWORD=111111

# 查询配置
TS_DEFAULT_DATE=    # 为空时使用当前日期

# 地点配置
TS_PLACE_SHANG_HAI=Shang Hai
TS_PLACE_SU_ZHOU=Su Zhou
TS_PLACE_NAN_JING=Nan Jing

# 权重配置
TS_HIGHSPEED_WEIGHT=60  # 高铁的权重比例
TS_NORMAL_WEIGHT=40     # 普通列车的权重比例

# 批量执行配置
TS_BATCH_COUNT=100      # 批量执行的次数
TS_BATCH_INTERVAL=1     # 执行间隔(秒)

# 日志配置
TS_LOG_LEVEL=INFO       # 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### 配置使用方法

1. 复制项目根目录下的`.env.example`文件为`.env`：
   ```bash
   cp .env.example .env
   ```

2. 编辑`.env`文件，根据实际情况修改配置项：
   ```ini
   # 修改为实际的Train-Ticket系统地址
   TS_BASE_URL=http://your-train-ticket-address:port
   
   # 修改为实际的登录凭据
   TS_USERNAME=your_username
   TS_PASSWORD=your_password
   ```

3. 安装所需依赖：
   ```bash
   pip install -r requirements.txt
   ```
   
   或者使用uv（速度更快）：
   ```bash
   uv pip install -r requirements.txt
   ```

## 使用方法

### 测试连接和登录

在开始使用前，建议先测试连接和登录功能，确保服务器可访问并且凭据有效：

```bash
python test_login.py
# 或者
python test_connection.py
```

### 基本使用示例

可以使用提供的example.py脚本快速体验功能：

```bash
# 直接运行
python example.py

# 或使用uv运行（可自动选择正确的Python版本）
uv run example.py
```

这将随机执行多个场景，模拟真实用户操作。

### 在代码中使用

```python
import logging
from queries import Query
from scenarios import query_and_preserve

# 设置日志
logging.basicConfig(level=logging.INFO)

# 初始化查询对象（会自动从配置读取服务器地址）
q = Query()

# 登录（会自动从配置读取用户名和密码）
if not q.login():
    logging.fatal('登录失败')
    exit(1)

# 执行特定场景
query_and_preserve(q)  # 查询并预订车票

# 或者直接执行特定查询
trip_ids = q.query_high_speed_ticket()  # 查询高铁票
```

### 批量执行场景

可以像下面这样执行批量操作来模拟持续的用户活动：

```python
import time
import random
from queries import Query
from scenarios import query_and_preserve, query_and_cancel, query_and_pay

q = Query()
if not q.login():
    exit(1)

scenarios = [query_and_preserve, query_and_cancel, query_and_pay]

# 执行100次随机场景
for i in range(100):
    scenario = random.choice(scenarios)
    try:
        scenario(q)
        print(f"完成场景 {scenario.__name__}, 索引: {i}")
        time.sleep(1)  # 避免请求过于频繁
    except Exception as e:
        print(f"场景执行失败: {e}")
```

## 常见问题

### 1. 导入错误

如果遇到类似以下的导入错误：
```
ImportError: attempted relative import with no known parent package
```

这是因为Python的相对导入规则问题。解决方法有以下几种：

1. **使用pip安装（推荐）**：
   ```bash
   pip install -e .
   # 或者使用uv
   uv pip install -e .
   ```
   这将以开发模式安装该项目，使Python能够正确识别包结构。

2. **使用PYTHONPATH**：
   ```bash
   export PYTHONPATH=$PYTHONPATH:/path/to/train-ticket-auto-query
   ```
   
3. **将项目作为模块运行**：
   ```bash
   python -m example
   ```

### 2. 登录失败

如果登录失败，可能有以下原因：

- 服务器地址不正确：检查.env文件中的TS_BASE_URL配置
- 用户名或密码错误：检查.env文件中的TS_USERNAME和TS_PASSWORD配置
- 服务器未运行或不可访问：确保Train-Ticket系统正常运行
- 网络问题：检查防火墙或网络连接

可以运行专门的登录测试脚本来诊断问题：

```bash
python test_login.py
```

如果需要更详细的日志，可以在.env文件中设置：
```
TS_LOG_LEVEL=DEBUG
```

### 3. uv相关问题

如果您在使用uv时遇到问题：

- **uv安装失败**：尝试其他安装方法
  ```bash
  # 使用pip安装
  pip install uv
  
  # 或者使用下载安装脚本
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- **权限不足**：在某些系统上可能需要管理员权限
  ```bash
  # Linux/Mac
  sudo curl -LsSf https://astral.sh/uv/install.sh | sh
  
  # Windows (以管理员身份运行PowerShell)
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

- **虚拟环境激活失败**：检查虚拟环境路径并使用正确的激活命令
  ```bash
  # Linux/Mac
  . .venv/bin/activate  # 注意前面的点
  
  # Windows
  .venv\Scripts\activate
  ```

- **运行特定Python版本**：直接指定Python解释器
  ```bash
  uv run --python=python3.10 script.py
  ```

## 开发指南

### 添加新的查询功能

如需添加新的查询功能，请按以下步骤操作：

1. 在`queries.py`中的`Query`类中添加新方法
2. 在`scenarios.py`中添加新的场景函数
3. 如果需要，更新配置项

### 依赖管理

本项目使用uv进行依赖管理，它比传统的pip更快、更安全：

1. **添加新依赖**：
   ```bash
   # 安装并添加到requirements.txt
   uv pip install -r requirements.txt requests
   uv pip freeze > requirements.txt  # 更新依赖列表
   ```

2. **更新依赖**：
   ```bash
   # 更新特定包
   uv pip install -U requests
   uv pip freeze > requirements.txt  # 更新依赖列表
   ```

3. **定位依赖问题**：
   ```bash
   # 查看依赖树
   uv pip list -v
   ```

4. **检查过时依赖**：
   ```bash
   # 显示可更新的包
   uv pip list --outdated
   ```

5. **使用缓存提高速度**：
   uv 会自动缓存安装过的包，显著提高重复安装的速度。

6. **安装和运行开发工具**：
   ```bash
   # 安装工具并立即运行
   uv pip install black
   uv run black .
   ```

### 贡献代码

欢迎提交Pull Request或Issues，一起改进这个项目！

## 注意事项

- 请确保Train-Ticket系统正常运行并可访问
- 默认的用户名/密码是 `fdse_microservice/111111`
- 该工具主要用于模拟测试，请勿用于生产环境或实际业务
- 为避免对服务器造成过大压力，请合理设置执行间隔和批量数量

### 使用特定Python版本

uv可以轻松管理和使用不同版本的Python：

1. **安装特定Python版本**:
   ```bash
   # 安装Python 3.10和3.11
   uv python install 3.10 3.11
   ```

2. **为当前项目指定Python版本**:
   ```bash
   uv python pin 3.11
   # 这会创建.python-version文件
   ```

3. **创建使用特定Python版本的虚拟环境**:
   ```bash
   uv venv --python 3.11
   ```

4. **使用特定Python版本运行脚本**:
   ```bash
   uv run --python 3.11 example.py
   ```

更多信息请参阅[uv官方文档](https://docs.astral.sh/uv/)。
