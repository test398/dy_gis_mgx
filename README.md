# 思极地图坐标转换工具

## 项目介绍
这是一个用于思极地图坐标转换的工具，提供了多种获取API token的方式，并支持坐标转换功能。

## ⚡ 快速开始

### 1. 配置环境

```bash
# 克隆项目到本地
git clone <your-repo-url>
cd dy_gis_mgx

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境（macOS/Linux）
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API Token

有三种方式获取和配置API token：

#### 方式1：手动配置（推荐）
1. 打开浏览器，访问 [思极地图](https://map.sgcc.com.cn/)
2. 登录您的账号
3. 打开开发者工具 (F12 或 Command+Option+I)
4. 切换到 Application 标签页
5. 在左侧 Storage 下找到 Session Storage
6. 查找并复制 accessToken 的值
7. 设置环境变量:
   ```bash
   export SGCC_MAP_TOKEN=your_token_here
   ```
   可用的环境变量名称: SGCC_MAP_TOKEN, AUTH_TOKEN, SGCC_TOKEN
8. 为了持久化环境变量，建议将其添加到 ~/.bashrc 或 ~/.zshrc 文件中:
   ```bash
   echo 'export SGCC_MAP_TOKEN=your_token_here' >> ~/.bashrc
   source ~/.bashrc
   ```
9. 或者在代码中手动设置token:
   ```python
   from src.data.内网代码.token_manager import set_manual_token
   set_manual_token('your_token_here')
   ```

   }
   ```

#### 方式2：使用备用token
在 `token_manager.py` 中设置备用token：
```python
self.backup_tokens = [
    "your_backup_token_1",
    "your_backup_token_2",
    # 更多备用token...
]
```

#### 方式3：浏览器自动化获取
工具会尝试自动通过浏览器获取token（需要Chrome驱动）

### 3. 运行程序

```bash
# 确保已激活虚拟环境
source venv/bin/activate

# 运行主脚本
python temp_code/main_coordinate_pipeline.py
```

## 🎯 核心功能

- **坐标转换**: 支持多种坐标系统之间的转换
- **Token管理**: 提供多种API token获取方式
- **错误处理**: 完善的错误处理和日志记录
- **离线支持**: 备用token机制支持离线环境

## 🏗️ 架构特点

- **模块化设计**: 清晰的模块划分，易于维护
- **多种token获取方式**: 支持手动配置、备用token和浏览器自动化
- **完善的错误处理**: 详细的错误信息和解决方案提示
- **类型安全**: 使用类型提示提高代码可读性和可维护性

## 📁 项目结构

```
project/
├── temp_code/
│   ├── main_coordinate_pipeline.py  # 主入口程序
│   ├── token_manager.py             # Token管理模块
│   └── test_chrome_driver.py        # Chrome驱动测试脚本
├── requirements.txt                 # 依赖配置
└── README.md                        # 项目说明
```

## 🔧 工具与依赖

- Python 3.8+
- Selenium (浏览器自动化)
- Webdriver-manager (Chrome驱动管理)
- Requests (HTTP请求)
- Python-dotenv (环境变量管理)

## 📋 当前状态

| 模块 | 完成度 | 状态 |
|------|--------|------|
| 🟢 坐标转换核心 | 100% | ✅ 完成 |
| 🟢 Token管理模块 | 95% | ✅ 完成 |
| 🟢 错误处理系统 | 100% | ✅ 完成 |
| 🟡 Chrome驱动自动配置 | 70% | 🚧 部分实现 |
| 🟢 备用token机制 | 100% | ✅ 完成 |

## ❓ 常见问题

### 1. Chrome驱动问题
- 错误: `Could not reach host. Are you offline?`
  解决方法: 检查网络连接，或手动安装Chrome驱动

- 错误: `Unable to obtain driver for chrome`
  解决方法: 确认Chrome驱动已正确安装并添加到系统PATH

### 2. Token获取问题
- 错误: `无法获取有效的API token，包括备用token`
  解决方法: 按照手动获取token的指南操作，确保配置文件格式正确

### 3. 网络连接问题
- 如遇网络限制，建议使用手动获取token的方式

## 📚 资源

- [ChromeDriver下载](https://chromedriver.chromium.org/downloads)
- [Selenium文档](https://www.selenium.dev/documentation/)
- [思极地图官网](https://map.sgcc.com.cn/)
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
