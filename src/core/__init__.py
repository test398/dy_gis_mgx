"""
核心业务逻辑模块

包含主处理流程、美化治理引擎、评分引擎等核心功能
"""

# 导出核心数据类型
from .data_types import (
    GISData, ImageInput, TreatmentResult, BatchInput, BatchResult,
    TreatmentResponse, EvaluationResponse, ModelInfo, TokenUsage,
    BatchSummary, GISDataDict, CoordinatesList, DeviceDict
)

# 导出评分器（阶段1 + 阶段4）
from .overhead_line_scorer import OverheadLineScorer
from .cable_line_scorer import CableLineScorer
from .branch_box_scorer import BranchBoxScorer
from .access_point_scorer import AccessPointScorer
from .meter_box_scorer import MeterBoxScorer

# 导出核心处理流程 - 使用简单导入
def get_core_functions():
    """延迟导入核心功能，避免循环导入"""
    try:
        from . import pipeline
        from . import beautification
        from . import evaluation
        return pipeline, beautification, evaluation
    except ImportError as e:
        print(f"Warning: Could not import core functions: {e}")
        return None, None, None