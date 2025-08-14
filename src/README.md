# 电网台区美化治理与打分系统 - Phase 1 基础框架

## 🎯 项目概述

这是一个基于大模型的端到端自动化台区治理系统，能够自动优化电网台区设备布局并进行美观性评分。

### 核心功能
- **输入**: 结构化GIS数据（设备坐标、地形要素等）+ 可视化图片
- **处理**: 大模型基于数据进行自动化治理 + 美观性打分
- **输出**: 治理后的结构化数据 + 新生成的可视化图片 + 详细评分报告
- **追踪**: WandB实验记录 + 成本分析
- **并行**: Multiprocessing批量处理

## 🏗️ 架构设计

```
project/
├── main.py                       # 主入口程序
├── run_demo.py                   # 演示运行脚本
└── src/
    ├── core/                     # 核心业务逻辑
    │   ├── data_types.py         # 数据类型定义
    │   ├── pipeline.py           # 主处理流程
    │   ├── beautification.py     # 美化治理引擎
    │   └── evaluation.py         # 评分引擎
    ├── models/                   # 大模型接口
    │   ├── base_model.py         # 模型基类
    │   └── qwen_model.py         # 千问模型实现
    ├── utils/                    # 工具模块 (待实现)
    ├── tracking/                 # 实验追踪 (待实现)
    └── data/                     # 数据接口 (待实现)
```

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

### 2. 环境变量配置

```bash
# 可选：设置千问API密钥（不设置将使用模拟模式）
# Windows PowerShell
$env:QWEN_API_KEY="your-qwen-api-key"

# Linux/macOS
export QWEN_API_KEY="your-qwen-api-key"
```

### 3. 运行演示

```bash
# 方式1: 使用封装的运行脚本（推荐）
python run_demo.py

# 方式2: 直接运行主程序
python main.py
```

### 4. 演示内容

演示程序包含三个部分：

1. **模型信息演示**: 显示可用模型和定价信息
2. **单图处理演示**: 处理单个台区图像的完整流程
3. **批量处理演示**: 并行处理多个台区图像

## 💡 使用示例

### 基本用法

```python
from src import GISData, ImageInput, process_single_image

# 创建GIS数据
gis_data = GISData(
    devices=[
        {"id": "device_1", "x": 100, "y": 200, "type": "变压器"},
        {"id": "device_2", "x": 150, "y": 180, "type": "表箱"},
    ],
    buildings=[...],
    roads=[...],
    # ...
)

# 创建输入
image_input = ImageInput(
    gis_data=gis_data,
    visual_image_path="path/to/image.png"  # 可选
)

# 处理
results = process_single_image(
    image_input=image_input,
    models=['qwen'],
    prompt="请优化台区设备布局"
)

# 查看结果
for result in results:
    print(f"美观性评分: {result.beauty_score}")
    print(f"处理成本: ${result.cost:.4f}")
```

### 批量处理

```python
from src import BatchInput, process_batch

# 创建批量输入
batch_input = BatchInput(inputs=[input1, input2, input3])

# 批量处理
batch_result = process_batch(
    batch_input=batch_input,
    models=['qwen'],
    max_workers=4,
    enable_wandb=True
)

# 查看汇总
print(f"成功率: {batch_result.summary.success_rate}%")
print(f"总成本: ${batch_result.summary.total_cost}")
```

## 📊 数据格式

### GIS数据格式

```python
gis_data = GISData(
    devices=[
        {
            "id": "device_001",
            "x": 100.5,
            "y": 200.3,
            "type": "变压器",
            "points": [[95, 195], [105, 195], [105, 205], [95, 205]]
        }
    ],
    buildings=[
        {
            "id": "building_001", 
            "coords": [[x1,y1], [x2,y2], ...],
            "type": "residential"
        }
    ],
    roads=[...],
    rivers=[...],
    boundaries={"coords": [[x1,y1], [x2,y2], ...]},
    metadata={"region_id": "area_001", ...}
)
```

### 治理结果格式

```python
result = TreatmentResult(
    original_input=image_input,           # 原始输入
    treated_gis_data=optimized_gis_data,  # 治理后数据
    beauty_score=85.5,                    # 美观性评分 (0-100)
    improvement_metrics={                 # 改善指标
        "devices_moved": 3,
        "spacing_improved": True
    },
    processing_time=2.34,                 # 处理时间
    cost=0.0042                          # 处理成本
)
```

## 🎛️ 配置选项

### 模型配置

```python
# 支持的模型类型
models = ['qwen', 'openai', 'kimi', 'glm']  # 目前只实现了qwen

#### 千问模型配置
qwen_model = get_model('qwen', 
    api_key='your-api-key',
    model_name='qwen-vl-max-2025-04-08',
    max_retries=3,
    timeout=300,
    # 自动分批处理配置
    enable_auto_batch=True,        # 启用自动分批处理
    max_input_length=15000,        # 单次处理最大字符数
    batch_overlap=500              # 批次间重叠字符数
)
```

## 🚀 自动分批处理功能

当输入数据过大导致模型输出不全时，系统会自动将数据分批处理并合并结果。

### 功能特性

- **智能分割**: 根据输入长度自动计算最优批次大小
- **无缝合并**: 自动合并多个批次的处理结果
- **错误恢复**: 单个批次失败不影响整体处理
- **详细日志**: 完整的分批处理过程记录

### 使用示例

```python
from models.qwen_model import QwenModel

# 创建支持自动分批的模型实例
model = QwenModel(
    api_key='your-api-key',
    enable_auto_batch=True,
    max_input_length=10000,  # 较小的限制以触发分批
    batch_overlap=200
)

# 处理大量设备数据
large_gis_data = {
    "devices": [device1, device2, ..., device150],  # 150个设备
    "buildings": [...],
    "roads": [...]
}

# 自动分批处理
result = model.beautify(large_gis_data, "请优化设备布局")

if result["success"]:
    print(f"处理完成！输入设备: {result['metadata']['input_devices']}")
    print(f"输出设备: {result['metadata']['output_devices']}")
    print(f"使用分批: {result['metadata']['auto_batch_used']}")
else:
    print(f"处理失败: {result['message']}")
```

### 配置参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enable_auto_batch` | bool | True | 是否启用自动分批处理 |
| `max_input_length` | int | 15000 | 单次处理的最大字符数 |
| `batch_overlap` | int | 500 | 批次间重叠字符数（预留） |

### 处理流程

1. **输入评估**: 估算输入数据的字符长度
2. **分批决策**: 超过限制时自动启用分批处理
3. **智能分割**: 根据设备数量和输入长度计算最优批次
4. **并行处理**: 逐个处理每个批次
5. **结果合并**: 将所有批次结果合并为完整输出

### 运行测试

```bash
# 设置API密钥
export QWEN_API_KEY='your-api-key'

# 运行分批处理测试
python src/models/qwen_batch_example.py
```

### 处理配置

```

```python
config = {
    'max_workers': 4,           # 并行进程数
    'enable_wandb': True,       # 启用WandB追踪
    'batch_size': 10,          # 批处理大小
    'retry_count': 3           # 失败重试次数
}
```

## 📊 WandB实验追踪与图片上传

系统集成了完整的WandB实验追踪功能，支持自动上传图片、记录评分结果和API调用指标。

### 图片上传功能

```python
from src.tracking.wandb_tracker import ExperimentTracker, ExperimentConfig

# 创建追踪器
config = ExperimentConfig(
    experiment_name="grid_beautification_exp",
    project_name="grid-beautification",
    tags=["beautification", "scoring"]
)
tracker = ExperimentTracker(config)
tracker.init_experiment()

# 1. 上传单张图片
tracker.log_image(
    image_path="path/to/result.jpg",
    caption="处理结果图片",
    image_type="result"
)

# 2. 上传对比图片（治理前后）
tracker.log_image_comparison(
    before_image_path="path/to/before.jpg",
    after_image_path="path/to/after.jpg",
    image_id="IMG_001",
    model_name="GLM-4V"
)

# 3. 批量上传图片
tracker.log_batch_images(
    image_paths=["img1.jpg", "img2.jpg", "img3.jpg"],
    captions=["图片1", "图片2", "图片3"],
    image_type="batch_results"
)

# 4. 记录评分结果（同时上传图片）
tracker.log_scoring_result(
    image_id="IMG_001",
    model_name="GLM-4V",
    scores={"美观性": 8.5, "合理性": 9.0},
    before_image_path="path/to/before.jpg",
    after_image_path="path/to/after.jpg"
)

# 结束实验
tracker.finish_experiment()
```

### 支持的图片类型

- **original**: 原始图片
- **processed**: 处理后图片
- **result**: 结果图片
- **comparison**: 对比图片
- **scoring_result**: 评分结果图片
- **batch**: 批量图片

### 运行演示

```bash
# 运行图片上传功能演示
python src/tracking/image_upload_example.py
```

## 🔧 开发状态

### ✅ 已完成功能

- [x] 完整的数据结构定义 (`GISData`, `ImageInput`, `TreatmentResult`等)
- [x] BaseModel抽象基类和统一接口
- [x] QwenModel实现（基于现有API）
- [x] 单图和批量处理Pipeline
- [x] 基础的可扩展架构
- [x] 演示程序和使用示例

### 🚧 待实现功能

- [ ] 完整的utils模块（可视化、GIS处理）
- [x] WandB实验追踪集成（包含图片上传功能）
- [x] GLM模型实现（支持GLM-4.5V）
- [ ] 其他大模型（OpenAI、Kimi）
- [ ] 高级美化算法
- [ ] 完整的错误处理和日志
- [ ] 配置文件管理
- [ ] Web界面集成

## 🤝 开发指南

### 添加新模型

1. 继承`BaseModel`类
2. 实现必要的抽象方法
3. 在`models/__init__.py`中注册

```python
class NewModel(BaseModel):
    def _make_api_call(self, messages, **kwargs):
        # 实现API调用
        pass
    
    def get_pricing(self):
        # 返回定价信息
        pass
        
    def _add_image_to_messages(self, messages, image_path):
        # 实现图片添加逻辑
        pass
```

### 扩展功能模块

在相应目录下添加新文件，并在`__init__.py`中导出：

```python
# src/utils/new_feature.py
def new_function():
    pass

# src/utils/__init__.py  
from .new_feature import new_function
```

## 📄 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 👥 贡献者

- **DY-GIS Team** - 项目开发团队

---

💡 **提示**: 这是Phase 1基础框架，为后续功能扩展提供了坚实的架构基础。如有问题或建议，欢迎提出！