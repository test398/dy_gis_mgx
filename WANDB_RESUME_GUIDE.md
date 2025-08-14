# WandB运行恢复使用指南

## 概述

现在GIS实验追踪器支持恢复现有的WandB运行，这意味着您可以将新的实验结果记录到之前的运行ID下，实现数据的连续追踪。

## 功能特性

✅ **恢复现有运行**: 将新数据添加到已存在的WandB运行中 <mcreference link="https://docs.wandb.ai/guides/runs/resuming/" index="1">1</mcreference>
✅ **多种恢复模式**: 支持`allow`、`must`、`never`三种模式 <mcreference link="https://docs.wandb.ai/ref/python/init/" index="2">2</mcreference>
✅ **自动降级**: 在线/离线/禁用模式都支持恢复功能
✅ **数据连续性**: 新数据会追加到现有运行的历史记录中

## 使用方法

### 1. 命令行参数使用（推荐）

#### 创建新实验
```bash
python main.py --enable-tracking --experiment-name "my_experiment" data/
```

#### 恢复现有实验
```bash
# 尝试恢复，失败则创建新实验（推荐）
python main.py --enable-tracking --resume-run-id "abc123def" --resume-mode "allow" data/

# 必须恢复现有实验，失败则报错
python main.py --enable-tracking --resume-run-id "abc123def" --resume-mode "must" data/

# 总是创建新实验，忽略运行ID
python main.py --enable-tracking --resume-mode "never" data/
```

#### 命令行参数说明
- `--resume-run-id RUN_ID`: 要恢复的WandB运行ID
- `--resume-mode MODE`: 恢复模式，可选值：
  - `allow`: 允许恢复或创建新运行（默认，推荐）
  - `must`: 必须恢复现有运行，如果ID不存在则失败
  - `never`: 总是创建新运行，忽略resume-run-id

### 2. 编程接口使用

```python
from tracking.gis_experiment_tracker import create_gis_experiment_tracker

# 恢复现有运行
tracker = create_gis_experiment_tracker(
    experiment_id="continued_experiment",
    setting_name="Setting_A",
    data_version="标注数据v1",
    evaluation_criteria="5项评分标准",
    resume_run_id="91c9r789",  # 要恢复的运行ID
    resume_mode="allow"        # 恢复模式
)

# 继续记录新数据
tracker.log_api_call(...)
tracker.log_experiment_result(...)
```

### 2. 恢复模式说明

#### `resume_mode="allow"` (推荐)
- 如果指定的运行ID存在，则恢复该运行
- 如果运行ID不存在，则创建新运行
- 最安全的选择，不会因为运行不存在而报错

```python
tracker = create_gis_experiment_tracker(
    experiment_id="flexible_resume",
    setting_name="Setting_A",
    data_version="标注数据v1",
    evaluation_criteria="5项评分标准",
    resume_run_id="some_run_id",
    resume_mode="allow"  # 灵活恢复
)
```

#### `resume_mode="must"`
- 必须恢复指定的运行ID
- 如果运行ID不存在，会抛出错误
- 适用于确定运行ID存在的场景

```python
tracker = create_gis_experiment_tracker(
    experiment_id="strict_resume",
    setting_name="Setting_A",
    data_version="标注数据v1",
    evaluation_criteria="5项评分标准",
    resume_run_id="91c9r789",
    resume_mode="must"  # 严格恢复
)
```

#### `resume_mode="never"`
- 永不恢复，总是创建新运行
- 即使提供了`resume_run_id`也会被忽略
- 适用于确保创建全新运行的场景

```python
tracker = create_gis_experiment_tracker(
    experiment_id="always_new",
    setting_name="Setting_A",
    data_version="标注数据v1",
    evaluation_criteria="5项评分标准",
    resume_run_id="91c9r789",  # 会被忽略
    resume_mode="never"       # 总是新建
)
```

### 3. 获取现有运行ID

#### 方法1: 从WandB Web界面获取
1. 访问 https://wandb.ai/dy_gis_mgx_/gis-beautification
2. 找到要恢复的运行
3. 复制运行ID（通常在URL中或运行详情页面）

#### 方法2: 通过API查询
```python
import wandb

# 获取最近的运行
api = wandb.Api()
runs = list(api.runs('dy_gis_mgx_/gis-beautification', per_page=5))

for run in runs:
    print(f"运行ID: {run.id}, 名称: {run.name}, 状态: {run.state}")
```

#### 方法3: 从日志文件获取
查看之前运行的日志输出，通常会显示运行ID：
```
🌐 WandB实验ID: 91c9r789
📈 请访问 https://wandb.ai 查看实验结果
```

### 4. 实际应用场景

#### 典型工作流程

##### 第一次运行（创建新实验）
```bash
# 首次运行，创建新实验
python main.py --enable-tracking --experiment-name "area_beautification_v1" data/batch1/

# 运行完成后，记录输出的运行ID，例如: abc123def
```

##### 后续运行（恢复现有实验）
```bash
# 使用相同的运行ID继续实验
python main.py --enable-tracking --resume-run-id "abc123def" --resume-mode "allow" data/batch2/

# 或者处理更多数据
python main.py --enable-tracking --resume-run-id "abc123def" --resume-mode "allow" data/batch3/
```

#### 场景1: 继续中断的实验
```python
# 如果实验因为网络问题或其他原因中断
tracker = create_gis_experiment_tracker(
    experiment_id="interrupted_experiment",
    setting_name="Setting_B",
    data_version="标注数据v2",
    evaluation_criteria="改进评价标准",
    resume_run_id="previous_run_id",
    resume_mode="must"
)
```

#### 场景2: 分阶段实验
```python
# 第一阶段：基础实验
tracker_phase1 = create_gis_experiment_tracker(
    experiment_id="multi_phase_experiment",
    setting_name="Setting_C",
    data_version="扩展数据集",
    evaluation_criteria="完整评价体系"
)
# ... 进行第一阶段实验
phase1_run_id = tracker_phase1.wandb_run.id
tracker_phase1.finish_experiment()

# 第二阶段：继续实验
tracker_phase2 = create_gis_experiment_tracker(
    experiment_id="multi_phase_experiment_phase2",
    setting_name="Setting_C",
    data_version="扩展数据集",
    evaluation_criteria="完整评价体系",
    resume_run_id=phase1_run_id,
    resume_mode="allow"
)
```

#### 场景3: 补充实验数据
```python
# 为已完成的实验补充新的测试数据
tracker = create_gis_experiment_tracker(
    experiment_id="supplementary_data",
    setting_name="Setting_A",
    data_version="标注数据v1",
    evaluation_criteria="5项评分标准",
    resume_run_id="91c9r789",
    resume_mode="allow",
    notes="补充实验数据"
)
```

#### 场景4: 批量数据处理
```python
# 分批处理大量数据，所有结果记录在同一个实验中
for batch_num, batch_data in enumerate(data_batches):
    tracker = create_gis_experiment_tracker(
        experiment_id=f"large_dataset_batch_{batch_num}",
        setting_name="Setting_Production",
        data_version="大规模数据集",
        evaluation_criteria="生产环境评价",
        resume_run_id="shared_run_id" if batch_num > 0 else None,
        resume_mode="allow"
    )
    # 处理当前批次数据
    process_batch(batch_data, tracker)
```

## 注意事项

### ⚠️ 重要提醒

1. **运行ID格式**: WandB运行ID通常是8位字符的随机字符串（如`91c9r789`）

2. **权限检查**: 确保您有权限访问要恢复的运行（必须是同一个项目和实体）

3. **数据一致性**: 恢复的运行会继承原有的配置，新的配置参数会更新到运行中

4. **步数连续性**: WandB会自动处理步数，新数据会从上次的步数继续

5. **运行状态**: 可以恢复已完成（finished）的运行，WandB会重新激活它

### 🔧 故障排除

#### 问题1: "run doesn't exist" 错误
```
wandb.errors.UsageError: resume='must' but run (xxx) doesn't exist
```
**解决方案**:
- 检查运行ID是否正确
- 确认运行属于当前项目和实体
- 改用`resume_mode="allow"`

#### 问题2: 权限错误
**解决方案**:
- 确认WandB API密钥正确
- 检查项目和实体名称
- 确认有访问该运行的权限

#### 问题3: 网络连接问题
**解决方案**:
- 系统会自动降级到离线模式
- 离线数据稍后会自动同步

## 最佳实践

### 1. 运行ID管理
```python
# 保存运行ID供后续使用
tracker = create_gis_experiment_tracker(...)
run_id = tracker.wandb_run.id

# 将运行ID保存到文件
with open('current_run_id.txt', 'w') as f:
    f.write(run_id)

# 后续恢复时读取
with open('current_run_id.txt', 'r') as f:
    saved_run_id = f.read().strip()

tracker = create_gis_experiment_tracker(
    ...,
    resume_run_id=saved_run_id,
    resume_mode="allow"
)
```

### 2. 条件恢复
```python
import os

# 从环境变量获取运行ID
resume_id = os.getenv('WANDB_RESUME_ID')

tracker = create_gis_experiment_tracker(
    experiment_id="conditional_resume",
    setting_name="Setting_A",
    data_version="标注数据v1",
    evaluation_criteria="5项评分标准",
    resume_run_id=resume_id,  # 如果为None则创建新运行
    resume_mode="allow"
)
```

### 3. 批量处理中的恢复
```python
# 在批量处理脚本中使用恢复功能
def process_batch_with_resume(batch_data, resume_run_id=None):
    tracker = create_gis_experiment_tracker(
        experiment_id=f"batch_{len(batch_data)}_items",
        setting_name="Setting_Batch",
        data_version="批量数据",
        evaluation_criteria="批量评价",
        resume_run_id=resume_run_id,
        resume_mode="allow"
    )
    
    for item in batch_data:
        # 处理每个项目
        result = process_item(item)
        tracker.log_api_call(...)
    
    return tracker.wandb_run.id  # 返回运行ID供下次使用
```

## 示例代码

完整的使用示例请参考：
- `demo_resume_gis_tracker.py` - 完整演示脚本
- `resume_wandb_example.py` - 基础WandB恢复示例

## 相关文档

- [WandB官方恢复文档](https://docs.wandb.ai/guides/runs/resuming/)
- [WandB Init API参考](https://docs.wandb.ai/ref/python/init/)
- `TRACKING_INTEGRATION_README.md` - 实验追踪集成文档