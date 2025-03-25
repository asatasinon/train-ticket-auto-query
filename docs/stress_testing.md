# Train-Ticket 压测工具使用说明

## 简介

Train-Ticket压测工具是一个用于测试系统性能的工具，可以模拟多用户并发访问场景，帮助评估系统在高负载下的表现。

## 配置方式

压测参数可以通过两种方式配置：

### 1. 环境变量配置

在`.env`文件中配置以下参数：

```ini
# 压测配置
TS_STRESS_CONCURRENT=10     # 压测并发数
TS_STRESS_COUNT=100         # 压测请求总数
TS_STRESS_SCENARIO=high_speed  # 压测场景
TS_STRESS_TIMEOUT=30        # 请求超时时间(秒)
TS_STRESS_INTERVAL=0.1      # 并发线程启动间隔(秒)
TS_STRESS_ERROR_RATE_THRESHOLD=0.1  # 可接受的错误率阈值
```

### 2. 命令行参数配置

命令行参数优先级高于环境变量配置：

```bash
--scenario      # 场景名称
--concurrent    # 并发数
--count         # 请求总数
--interval      # 线程启动间隔
--timeout       # 请求超时时间
--error-threshold  # 错误率阈值
```

## 支持场景

压测工具支持以下场景：

- `high_speed`: 高铁票查询场景
- `normal`: 普通列车票查询场景
- `food`: 餐食查询场景
- `parallel`: 并行查询场景
- `pay`: 购票场景
- `cancel`: 退票场景
- `consign`: 托运场景

## 使用方法

### 1. 使用默认配置执行压测

```bash
python -m src.stress
```

### 2. 指定场景进行压测

```bash
python -m src.stress --scenario high_speed
```

### 3. 自定义并发数和请求数

```bash
python -m src.stress --concurrent 20 --count 200
```

### 4. 完整参数示例

```bash
python -m src.stress \
    --scenario normal \
    --concurrent 20 \
    --count 200 \
    --interval 0.2 \
    --timeout 60 \
    --error-threshold 0.05
```

## 压测结果说明

压测完成后，工具会输出详细的测试结果，包括：

- 总请求数
- 成功/失败请求数
- 错误率
- 总耗时
- QPS（每秒查询数）
- 响应时间统计（平均、最小、最大、P90、P95、P99）
- 响应时间标准差
- 错误信息列表（如果有）

## 注意事项

1. 压测前请确保系统处于稳定状态
2. 建议从小规模并发开始测试，逐步增加并发数
3. 注意观察系统资源使用情况（CPU、内存、网络等）
4. 如果出现大量错误，请检查系统日志和网络连接
5. 可以通过Ctrl+C随时中断压测

## 最佳实践

1. **循序渐进**：
   - 从较小的并发数开始（如5-10）
   - 逐步增加并发数，观察系统表现
   - 记录每次测试的结果，便于对比分析

2. **场景选择**：
   - 根据实际业务场景选择合适的测试场景
   - 可以组合多个场景进行测试
   - 注意场景之间的依赖关系

3. **监控指标**：
   - 关注QPS和响应时间的变化
   - 观察错误率是否在可接受范围内
   - 分析响应时间的分布情况

4. **结果分析**：
   - 对比不同并发数下的系统表现
   - 识别性能瓶颈
   - 根据测试结果优化系统配置 