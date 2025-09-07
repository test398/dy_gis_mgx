# 台区评分系统

这是一个用于台区评分和相关性分析的 Python 工具集。

## 功能模块

### 1. 自动评分系统 (auto_scoring_system.py)

- 提供台区自动评分功能
- 包含多个评分维度和规则
- 支持 JSON 格式的台区数据输入

### 2. 单台区评分助手 (single_scoring_helper.py)

- 对单个台区进行评分
- 生成详细的评分报告
- 支持 CSV 格式输出

### 3. 散点图生成器 (generate_scatter_plots.py)

- 生成各维度的散点图
- 支持中文字体显示
- 提供数据分布分析

## 安装依赖

```bash
pip install -r requirements.txt
```

## 项目结构

```
newCode/
├── README.md                    # 项目说明文档
├── config.py                    # 配置文件
├── auto_scoring_system.py       # 自动评分系统核心模块
├── single_scoring_helper.py     # 单台区评分助手
├── generate_scatter_plots.py    # 散点图生成器
├── requirements.txt             # 依赖包列表
├── data/                        # 数据目录
│   ├── *.csv                   # 评分数据文件
│   └── *.json                  # 台区JSON数据文件
├── fonts/                       # 字体目录
│   └── SimHei.ttf              # 中文字体文件
└── output/                      # 输出目录
    ├── charts/                 # 图表输出
    │   └── scatter_plots/      # 散点图
    └── single_results/         # 单台区评分结果
```

## 配置说明

在使用前，请根据您的实际情况修改 `config.py` 文件中的路径配置：

1. **数据目录**: 设置机器评分、人工评分和台区 JSON 数据的文件路径
2. **输出目录**: 设置各种分析结果的输出目录
3. **字体配置**: 设置中文字体路径（用于图表显示）

## 使用方法

### 单台区评分

```bash
# 直接运行脚本进行单台区评分
python single_scoring_helper.py
```

或在 Python 代码中调用：

```python
from single_scoring_helper import score_single_taiqu

# 对单个台区进行评分
results = score_single_taiqu('path/to/taiqu.json')
```

### 批量自动评分

```bash
# 运行自动评分系统，对所有台区进行评分
python auto_scoring_system.py
```

### 生成散点图

```bash
# 生成机器评分与人工评分的散点图对比
python generate_scatter_plots.py
```

## 数据格式要求

### 台区 JSON 数据

- 包含台区基本信息和各项指标数据
- 格式需符合 AutoScoringSystem 的要求

### 机器评分 CSV

- 必须包含'台区 ID'列
- 包含各评分维度的数值列

### 人工评分 CSV

- 必须包含'台区 ID'列
- 包含对应的人工评分数据

## 输出结果

- **单台区评分**: CSV 格式的详细评分结果，保存在 `output/single_results/` 目录
- **散点图**: 各维度的机器评分 vs 人工评分散点图，保存在 `output/charts/scatter_plots/` 目录

## 注意事项

1. 确保所有数据文件路径在 config.py 中正确配置
2. 首次运行时会自动下载中文字体文件到 `fonts/` 目录
3. 所有输出目录会自动创建
4. 建议在运行前检查数据文件的编码格式（推荐 UTF-8）
5. 项目已配置中文输出，所有日志和结果均为中文显示
