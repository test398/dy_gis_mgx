# 电网台区美化治理与打分系统

**Phase 1 基础框架** - 基于大模型的端到端自动化台区治理系统

## ⚡ 快速开始

### 1. 使用uv配置环境

```bash
# 克隆项目到本地
git clone <your-repo-url>
cd dy_gis_mgx

# 使用uv安装依赖
uv sync

# 可选：安装开发依赖（包含wandb）
uv sync --extra dev
```

### 2. 环境变量配置（可选）

```bash
# 可选：设置千问API密钥（不设置将使用模拟模式）
# Windows PowerShell
$env:QWEN_API_KEY="your-qwen-api-key"

# Linux/macOS
export QWEN_API_KEY="your-qwen-api-key"
```

### 3. 运行演示

```bash
# 推荐：使用封装的运行脚本
python run_demo.py

# 或者：直接运行主程序
python main.py
```

## 🎯 核心功能

- **输入**: 结构化GIS数据（设备坐标、地形要素等）
- **处理**: 大模型基于数据进行自动化治理 + 美观性打分  
- **输出**: 治理后的结构化数据 + 详细评分报告
- **追踪**: 成本分析 + 完整日志
- **并行**: 支持批量处理

## 📊 演示结果

运行演示后你将看到：

1. **模型信息**: 可用模型列表和定价信息
2. **单图处理**: 
   - 美观性评分: 85.5/100
   - 处理时间: ~0.20秒  
   - 处理成本: ~$0.002360
3. **批量处理**: 
   - 3台区并行处理
   - 100%成功率
   - 总耗时: ~0.61秒

## 🏗️ 架构特点

- **数据驱动**: 处理结构化GIS坐标数据，而非像素级图像
- **模型无关**: 统一接口支持多种大模型（当前支持千问）
- **成本透明**: 完整的token使用和费用追踪
- **类型安全**: 使用dataclass和类型提示
- **可扩展**: 新增模型只需继承BaseModel

## 📁 项目结构

```
project/
├── main.py                 # 主入口程序
├── run_demo.py             # 演示运行脚本
├── src/
│   ├── core/               # 核心业务逻辑
│   │   ├── data_types.py   # 数据类型定义
│   │   └── ...
│   ├── models/             # 大模型接口
│   │   ├── base_model.py   # 模型基类
│   │   ├── qwen_model.py   # 千问模型实现
│   │   └── ...
│   └── utils/              # 工具模块
├── pyproject.toml          # 依赖配置
└── README.md               # 项目说明
```

## 📋 当前状态

| 模块 | 完成度 | 状态 |
|------|--------|------|
| 🟢 核心数据结构 | 100% | ✅ 完成 |
| 🟢 千问模型集成 | 100% | ✅ 完成 |
| 🟢 处理流程框架 | 95% | ✅ 完成 |
| 🟢 成本计算系统 | 100% | ✅ 完成 |
| 🟡 可视化工具 | 0% | 🚧 待实现 |
| 🟡 WandB追踪 | 10% | 🚧 待实现 |
| 🟡 其他模型 | 20% | 🚧 待实现 |

## 🔧 自动分批处理功能

当输入数据过大时，千问模型支持自动分批处理，避免因输入长度限制导致的输出不完整问题。

### 功能特性

- **智能分割**: 自动将大量GIS数据分割成多个批次
- **灵活配置**: 支持多种预设配置和自定义配置
- **重叠处理**: 批次间包含重叠数据，确保处理连续性
- **重试机制**: 失败批次自动重试，提高成功率
- **结果合并**: 自动合并多个批次的处理结果
- **智能推荐**: 根据数据量自动推荐最佳配置
- **进度跟踪**: 详细的处理进度和状态日志

### BatchConfig配置类

新版本引入了`BatchConfig`配置类，提供更灵活的分批处理配置：

```python
from models.batch_config import BatchConfig, BatchConfigPresets

# 方式1: 使用预设配置
conservative_config = BatchConfigPresets.conservative()  # 保守配置
balanced_config = BatchConfigPresets.balanced()         # 平衡配置
aggressive_config = BatchConfigPresets.aggressive()     # 激进配置

# 方式2: 自定义配置
custom_config = BatchConfig(
    enable_auto_batch=True,
    max_input_length=12000,
    batch_overlap=400,
    max_devices_per_batch=25,
    safety_margin=0.85,
    retry_failed_batches=True,
    max_batch_retries=3
)

# 方式3: 智能推荐配置
recommended_config = BatchConfigPresets.recommend_for_data_size(100)
```

### 使用示例

```python
from models.qwen_model import QwenModel
from models.batch_config import BatchConfigPresets

# 使用预设配置
model = QwenModel(
    api_key="your_api_key",
    batch_config=BatchConfigPresets.balanced()
)

# 或者使用自定义配置
custom_config = BatchConfig(
    enable_auto_batch=True,
    max_input_length=15000,
    batch_overlap=500,
    max_devices_per_batch=30
)
model = QwenModel(
    api_key="your_api_key",
    batch_config=custom_config
)

# 处理大量数据
result = model.beautify(large_gis_data, prompt)

# 查看处理元数据
if 'batch_metadata' in result:
    meta = result['batch_metadata']
    print(f"总批次: {meta['total_batches']}")
    print(f"成功批次: {meta['successful_batches']}")
    print(f"失败批次: {meta['failed_batches']}")
```

### 配置参数详解

**基础配置**:
- `enable_auto_batch`: 是否启用自动分批（默认: True）
- `max_input_length`: 单次处理的最大字符数（默认: 15000）
- `batch_overlap`: 批次间重叠字符数（默认: 500）
- `max_devices_per_batch`: 每批次最大设备数（默认: None，无限制）

**高级配置**:
- `safety_margin`: 安全边际系数（默认: 0.8）
- `retry_failed_batches`: 是否重试失败的批次（默认: True）
- `max_batch_retries`: 最大重试次数（默认: 2）

### 预设配置说明

- **保守配置**: 小批次、多重试，适合稳定性要求高的场景
- **平衡配置**: 中等批次、适度重试，适合大多数场景
- **激进配置**: 大批次、少重试，适合快速处理的场景
- **小数据配置**: 针对小数据量优化
- **大数据配置**: 针对大数据量优化

### 处理流程

1. **配置验证**: 验证BatchConfig配置的有效性
2. **输入评估**: 估算输入数据的总长度
3. **智能分割**: 根据配置参数分割数据
4. **批次处理**: 逐个处理每个批次，支持重试
5. **结果合并**: 合并所有成功批次的结果
6. **元数据记录**: 记录处理统计信息

### 运行测试

```bash
# 设置API密钥
export QWEN_API_KEY="your_api_key_here"

# 运行分批处理示例
python src/models/qwen_batch_example.py
```

## 📖 详细文档

更多详细信息请查看 [src/README.md](src/README.md)

---

**Version**: Phase 1 Complete  
**Date**: 2025-08-04
