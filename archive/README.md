# 归档文件

本目录包含项目重构前的原始文件，仅供参考和比对之用。

## 目录结构

- `old_scripts/`: 包含原始的Python脚本文件
  - `atomic_queries.py`: 原始的原子查询操作实现
  - `config.py`: 旧版配置管理模块
  - `queries.py`: 旧版查询类
  - `setup.py`: 旧版安装脚本
  - `utils.py`: 旧版辅助函数
  - `scenarios.py`: 旧版场景定义
  - `main.py`: 旧版主入口
  - `example.py`: 旧版示例文件
  - `test_*.py`: 旧版测试文件
  - `query_*.py`: 各种查询场景的独立脚本

## 注意事项

这些文件已被新的模块化结构取代，不应再用于开发或运行。新的实现位于`src/`目录下，遵循更好的项目结构和Python最佳实践。

- 原先的查询功能被整合到了`src/core/`模块
- 辅助函数和配置管理被移至`src/utils/`模块
- 场景定义被重构到`src/scenarios/`模块
- 测试文件被移至`tests/`目录
- 示例被移至`examples/`目录

如需了解更多信息，请参阅项目根目录中的README.md文件。 