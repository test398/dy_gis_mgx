"""
电网台区美化治理与打分系统

一个基于大模型的端到端自动化台区治理系统
"""

__version__ = "1.0.0"
__author__ = "DY-GIS Team"

# 导出核心数据类型
from .core.data_types import (
    GISData, ImageInput, TreatmentResult, BatchInput, BatchResult,
    TreatmentResponse, EvaluationResponse, ModelInfo, TokenUsage
)

# 导出核心接口 (待实现)
from .core.pipeline import process_single_image, process_batch
from .models import get_model
from .data.input_loader import load_gis_data