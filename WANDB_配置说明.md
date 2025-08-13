# WandB 配置说明

## 问题描述

如果您发现程序仍然使用原来的WandB账号登录，这是因为之前代码中硬编码了API密钥。现在已经修改为支持自定义配置。

## 解决方案

### 方法1：使用环境变量（推荐）

1. 获取您的WandB API密钥：
   - 访问 https://wandb.ai/settings
   - 复制您的API密钥

2. 设置环境变量：
   
   **Windows (PowerShell):**
   ```powershell
   $env:WANDB_API_KEY="your_api_key_here"
   ```
   
   **Windows (命令提示符):**
   ```cmd
   set WANDB_API_KEY=your_api_key_here
   ```
   
   **永久设置（Windows）:**
   ```powershell
   [Environment]::SetEnvironmentVariable("WANDB_API_KEY", "your_api_key_here", "User")
   ```

3. 重新运行程序

### 方法2：使用WandB命令行登录

1. 在终端中运行：
   ```bash
   wandb login
   ```

2. 输入您的API密钥

3. 重新运行程序

### 方法3：清除现有登录信息后重新登录

1. 清除现有登录信息：
   ```bash
   wandb logout
   ```

2. 重新登录：
   ```bash
   wandb login
   ```

3. 输入您的新API密钥

## 验证配置

运行程序后，查看日志输出，应该看到类似以下信息：

```
使用环境变量WANDB_API_KEY登录WandB
```
或
```
使用已保存的登录信息登录WandB
```

## 注意事项

1. **API密钥安全**：请不要将API密钥提交到代码仓库中
2. **团队协作**：每个团队成员应使用自己的WandB账号
3. **项目权限**：确保您的账号有权限访问目标项目

## 故障排除

如果仍然遇到问题：

1. 检查网络连接
2. 确认API密钥正确
3. 查看程序日志中的详细错误信息
4. 尝试使用离线模式（程序会自动降级）

## 相关文件

修改的文件：
- `src/tracking/gis_experiment_tracker.py`
- `src/tracking/wandb_tracker.py`

这些文件现在支持：
- 环境变量 `WANDB_API_KEY`
- 已保存的登录信息
- 自动降级到离线模式