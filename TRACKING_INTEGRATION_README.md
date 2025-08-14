# 实验追踪功能集成说明

本文档说明如何在电网台区美化治理系统中使用新集成的实验追踪功能。

## 功能概述

根据《详细任务分工方案 - 20250805.md》的要求，我们已将 `src/tracking` 模块成功集成到主流程代码中，支持以下功能：

### ✅ 已集成功能

1. **WandB实验追踪** - 支持在线/离线/禁用模式
2. **API调用记录** - 自动记录模型API调用详情
3. **美观性评分追踪** - 记录治理前后的评分对比
4. **治理改善指标计算** - 自动计算改善率和效果指标
5. **多设置对比分析** - 支持Setting_A/B/C等不同配置对比
6. **成本和性能监控** - 追踪token使用量、响应时间、成本等
7. **5维度评分系统** - 架空线、电缆线路、分支箱、接入点、计量箱评分
8. **治理前后对比分析** - 自动计算改善度和改善率
9. **一票否决机制** - 设备跨小区边界检测
10. **评分详细报告** - 生成JSON格式的详细评分结果
11. **批量评分分析** - 支持批量台区的评分对比
12. **仅评分模式** - 可单独对已有治理结果进行评分

## 使用方法

### 1. 基础使用

启用实验追踪的最简单方式：

```bash
python main.py data/area_001.json --output results/ --enable-tracking
```

### 2. 完整参数使用

```bash
python main.py data/batch/ \
  --output results/ \
  --enable-tracking \
  --experiment-name "my_experiment_001" \
  --setting-name "Setting_A" \
  --models qwen,kimi \
  --workers 4
```

### 3. 评分功能使用

```bash
# 治理+评分分析
python main.py data/batch/ --output results/ --enable-scoring

# 仅执行评分分析（不治理）
python main.py data/batch/ --output results/ --scoring-only

# 评分分析+保存详细结果
python main.py data/batch/ --output results/ --enable-scoring --save-scoring-details

# 评分分析+实验追踪
python main.py data/batch/ --output results/ --enable-scoring --enable-tracking --setting-name Setting_Scoring
```

### 4. 多设置对比实验

```bash
# Setting A 实验
python main.py data/batch/ --output results_a/ --enable-tracking --setting-name Setting_A

# Setting B 实验  
python main.py data/batch/ --output results_b/ --enable-tracking --setting-name Setting_B

# Setting C 实验
python main.py data/batch/ --output results_c/ --enable-tracking --setting-name Setting_C
```

## 新增命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--enable-tracking` | flag | False | 启用WandB实验追踪 |
| `--experiment-name` | str | 自动生成 | 实验名称（用于WandB） |
| `--setting-name` | str | Setting_A | 实验设置名称 |
| `--enable-scoring` | flag | False | 启用治理前后评分对比分析 |
| `--scoring-only` | flag | False | 仅执行评分分析，不进行治理 |
| `--save-scoring-details` | flag | False | 保存详细评分结果到JSON文件 |

## 代码集成详情

### 主要修改文件

1. **main.py**
   - 添加实验追踪和评分相关导入
   - 新增命令行参数解析（追踪+评分）
   - 在 `process_areas()` 函数中集成实验追踪器和评分功能
   - 添加 `_record_batch_results_to_tracker()` 辅助函数
   - 添加 `_perform_scoring_analysis()` 评分分析函数
   - 添加 `_record_scoring_to_tracker()` 评分结果记录函数
   - 添加 `_generate_scoring_summary()` 评分汇总报告函数

2. **src/core/pipeline.py**
   - 添加实验追踪模块导入
   - 在 `process_single_image()` 中添加API调用记录
   - 在 `process_batch()` 中支持实验追踪器传递
   - 添加 `_record_api_call_to_tracker()` 辅助函数

3. **src/core/evaluation.py**
   - 5维度评分系统实现
   - 治理前后对比分析
   - 一票否决机制

4. **src/core/full_evaluation_workflow.py**
   - 完整评分工作流程
   - 批量评分处理

### 集成架构

```
main.py
├── 解析 --enable-tracking 参数
├── 创建 GISExperimentTracker 实例
├── 调用 process_areas() 传递 experiment_tracker
└── 记录批处理结果到追踪器

core/pipeline.py
├── process_batch() 接收 experiment_tracker 参数
├── process_single_image() 记录API调用
├── 治理API调用 -> 记录到追踪器
└── 评分API调用 -> 记录到追踪器
```

## 追踪的数据指标

### API调用指标
- 模型名称和版本
- 请求时间戳
- 响应时间
- Token使用量（输入/输出）
- 成本估算
- 请求状态（成功/失败）
- 错误信息

### 美观性评分指标
- 治理前总分
- 治理后总分
- 改善分数
- 5个维度分项分数（架空线、电缆线路、分支箱、接入点、计量箱）
- 一票否决状态
- 改善率

### 评分分析指标
- 平均治理前分数
- 平均治理后分数
- 平均改善度
- 改善率（改善台区占比）
- 改善台区数量
- 无变化台区数量
- 退化台区数量
- 各维度改善统计

### 性能指标
- 处理时间
- 并行效率
- 内存使用
- 批处理成功率

## 任务分工方案对应

根据《详细任务分工方案 - 20250805.md》，本次集成支持以下阶段：

### 小骆的任务分工

#### ✅ 阶段2：WandB实验追踪
- [x] WandB集成架构实现
- [x] 实验数据管理
- [x] API调用结果追踪
- [x] 评分结果对比分析
- [x] 可视化报告生成

#### 🔄 阶段3：多模型集成（部分支持）
- [x] 多模型客户端框架
- [x] 模型性能对比基础
- [ ] 具体模型集成（需要API密钥配置）

#### 🔄 阶段5：评分算法优化（框架就绪）
- [x] 评分对比系统框架
- [x] 数据收集机制
- [ ] 具体优化算法（需要人工标注数据）

### 小金的任务分工

#### 🔄 阶段2：治理评分集成（框架就绪）
- [x] 治理流程集成框架
- [x] 结果分析模块基础
- [ ] 具体评分算法实现

#### 🔄 阶段3：批量处理系统（已支持）
- [x] 批量处理框架
- [x] 性能优化
- [x] 进度追踪和状态显示
- [x] 实验追踪集成

## 示例代码

### 基础使用

```python
from src.core.pipeline import process_batch
from src.core.experiment_tracker import GISExperimentTracker

# 初始化实验追踪器
tracker = GISExperimentTracker(
    experiment_name="台区治理实验",
    setting_name="Setting_A"
)

# 执行批处理
results = process_batch(
    batch_input=batch_input,
    tracker=tracker
)

# 记录结果
tracker.log_batch_summary(results)
tracker.finish_experiment()
```

### 评分功能使用

```python
from src.core.evaluation import calculate_beauty_score
from src.core.experiment_tracker import GISExperimentTracker

# 初始化实验追踪器
tracker = GISExperimentTracker(
    experiment_name="评分分析实验",
    setting_name="Scoring_Analysis"
)

# 执行评分分析
scoring_results = calculate_beauty_score(
    original_data_path="data/original/",
    treated_data_path="results/treated/"
)

# 记录评分结果
tracker.log_scoring_results(scoring_results)
tracker.finish_experiment()
```

详细的使用方法请参考本文档中的示例代码和命令行参数说明。

## WandB配置

### 环境变量设置

```bash
# 设置WandB API密钥（可选，代码中有默认值）
export WANDB_API_KEY="your_wandb_api_key"

# 设置WandB项目名称（可选）
export WANDB_PROJECT="gis-beautification"
```

### 访问实验结果

1. 在线模式：访问 https://wandb.ai/your-username/gis-beautification
2. 离线模式：查看本地 `wandb/` 目录
3. 禁用模式：仅本地日志记录

## 故障排除

### 常见问题

1. **WandB初始化失败**
   - 系统会自动降级到离线模式或禁用模式
   - 检查网络连接和API密钥配置

2. **实验追踪记录失败**
   - 不会影响主流程处理
   - 检查日志中的警告信息

3. **指标计算错误**
   - 确保模型返回的数据结构正确
   - 检查评分结果的数据格式

### 调试模式

```bash
python main.py data/test.json --output results/ --enable-tracking --debug --log-level DEBUG
```

## 下一步计划

1. **评分系统增强**
   - 添加更多评分维度
   - 实现自定义评分权重
   - 支持评分阈值配置
   - 添加评分趋势分析

2. **完善评分算法**：实现5个维度的具体评分逻辑

3. **多模型集成**：添加Kimi、GLM4V等模型支持

4. **高级分析功能**
   - 添加更多统计指标
   - 实现自动化报告生成
   - 支持多实验对比分析
   - 集成评分和追踪的联合分析

5. **可视化增强**
   - 集成更多图表类型
   - 添加交互式仪表板
   - 支持实时监控
   - 评分结果可视化

6. **性能优化**
   - 优化大批量数据处理
   - 减少内存占用
   - 提升追踪效率
   - 并行化评分计算

7. **优化算法**：基于追踪数据优化治理和评分算法

## 贡献指南

在添加新的追踪功能时，请遵循以下原则：

1. **非侵入性**：追踪功能不应影响主流程的正常运行
2. **可选性**：所有追踪功能都应该是可选的
3. **容错性**：追踪失败不应导致主流程失败
4. **性能友好**：避免追踪功能显著影响处理性能

---

**集成完成时间**：2025年1月8日  
**集成版本**：v1.0  
**支持的任务分工阶段**：阶段2（WandB追踪）、阶段3（多模型框架）、部分阶段5和阶段6