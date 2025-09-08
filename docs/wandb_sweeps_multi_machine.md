# 使用 W&B Sweeps 跨多机并行运行（不同输入数据）

> 参考官方文档：<https://docs.wandb.ai/guides/sweeps/>  
> 适用环境：Windows PowerShell / Linux bash，均已验证可行。

---

## 1. 场景简介

在机器评分或模型训练中，我们常需要 **同一套脚本** 但 **不同输入数据** 来并行运行实验。例如：

* 同一模型结构，需要在多机并行完成 12 个训练 / 推理任务；
* 希望统一在 Weights & Biases（W&B） 上追踪超参数、指标与日志。

W&B Sweeps 提供了跨机器（multi-node）并行能力：

1. **创建** Sweep（一次即可）；
2. **在每台机器启动 `wandb agent`**，自动分配任务；
3. 根据 Sweep 配置控制输入数据路径、超参数等。

---

## 2. 前置条件

| 组件 | 版本/要求 |
|------|-----------|
| Python | ≥ 3.8 |
| wandb | ≥ 0.16.0（`pip install wandb -U`） |
| 代码仓库 | 已包含可执行脚本 `main.py`，接受 `--data_path` 等参数 |
| 网络 | 可访问 `api.wandb.ai`，或自建 W&B Server |

> **PowerShell 包管理**：本项目使用 `uv`，示例：
> ```powershell
> uv pip install -r requirements.txt
> ```

---

## 3. 代码改造示例

`main.py` 需能够读取命令行参数，并将必要信息记录到 W&B：

```python
import argparse, time, wandb

parser = argparse.ArgumentParser()
parser.add_argument("--data_path", type=str, required=True)
args = parser.parse_args()

wandb.init(project="beauty-score", config=args)
start = time.perf_counter()
# ====== 核心逻辑 ======
# 例如：加载数据、推理、保存结果
# ...
# ======================
wandb.log({"run_time_s": time.perf_counter() - start})
```

---

## 4. 创建 Sweep

1. **编写 Sweep 配置** `sweep.yaml`：

```yaml
program: main.py
method: grid  # 也可 random / bayes
parameters:
  data_path:
    values:
      - "datasets/part1.csv"
      - "datasets/part2.csv"
      - "datasets/part3.csv"
      # ... 可写 12 个条目
```

2. **初始化 Sweep（任意一台机器执行一次）**：

```powershell
# 在 PowerShell 中
wandb sweep --project beauty-score sweep.yaml
```

执行后会打印 `Sweep ID: <entity/project>/<sweep_id>`。

---

## 5. 在多机启动 Agent

将代码仓库同步到每台机器，确保 `wandb` 已登录同一账号（或设置 `WANDB_API_KEY` 环境变量）。

### 5.1 PowerShell 启动示例（Windows）
```powershell
$env:WANDB_API_KEY = "your_api_key"
wandb agent <entity/project>/<sweep_id>
```

### 5.2 Bash 启动示例（Linux）
```bash
export WANDB_API_KEY=your_api_key
wandb agent <entity/project>/<sweep_id>
```

> *每启动一次 `wandb agent`，就相当于向调度器申请一个任务。*  
> 多台机器、多进程均可同时启动，W&B 会自动为每个 Agent 分配尚未运行的 `data_path`。

---

## 6. 监控与中止

* **Web UI**：`https://wandb.ai/<entity>/<project>/sweeps/<sweep_id>`
* **命令行暂停/恢复**：
  ```powershell
  wandb sweep --stop <sweep_id>
  wandb sweep --resume <sweep_id>
  ```

---

## 7. 常见问题

| 现象 | 解决方案 |
|------|-----------|
| Agent 日志 `Waiting for runs to be assigned` | Sweep 中的参数已全部分配完；确认是否还需新增 `values` |
| 无法联网 | 配置 HTTP(S) 代理，或部署自托管 W&B Server |
| 需要 GPU | 在 `sweep.yaml` 中添加自定义参数 `cuda_visible_devices`，脚本内解析后 `os.environ` 设置 |

---

## 8. 结论：跨机器并行可行性确认

* 只要各机器 **使用同一个 Sweep ID**，即可自动负载均衡；无需额外编排工具。
* 如果使用本地部署的W&B，则需要个机器能访问同一个地址，由`WANDB_BASE_URL`给出，具体的方式之后再讨论。但默认是使用官方的公有云，不需要担心。
