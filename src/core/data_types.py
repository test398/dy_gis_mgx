"""
核心数据类型定义

简化版数据结构，避免复杂导入问题
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time


@dataclass
class GISData:
    """结构化的GIS数据 - 用来画图的原始数据"""
    devices: List[dict] = field(default_factory=list)      # 设备坐标列表 [{"x": 100, "y": 200, "type": "transformer"}, ...]
    buildings: List[dict] = field(default_factory=list)    # 建筑物坐标 [{"coords": [[x1,y1], [x2,y2], ...], "type": "residential"}, ...]
    roads: List[dict] = field(default_factory=list)        # 道路坐标 [{"coords": [[x1,y1], [x2,y2], ...], "width": 5}, ...]
    rivers: List[dict] = field(default_factory=list)       # 河流坐标 [{"coords": [[x1,y1], [x2,y2], ...], "width": 10}, ...]
    boundaries: Dict[str, Any] = field(default_factory=dict)  # 台区边界 {"coords": [[x1,y1], [x2,y2], ...]}
    metadata: Dict[str, Any] = field(default_factory=dict)    # 元数据 (台区ID、区域信息等)
    
    def __post_init__(self):
        """数据验证和初始化后处理"""
        # 确保所有设备都有必要的字段
        for device in self.devices:
            # if 'x' not in device or 'y' not in device:
            #     raise ValueError(f"设备坐标缺少x或y字段: {device}")
            if 'type' not in device:
                device['type'] = 'unknown'
    
    def get_device_count(self) -> int:
        """获取设备总数"""
        return len(self.devices)
    
    def get_bounds(self) -> Dict[str, float]:
        """获取数据边界"""
        if not self.devices:
            return {"min_x": 0, "max_x": 0, "min_y": 0, "max_y": 0}
        
        x_coords = [d['x'] for d in self.devices]
        y_coords = [d['y'] for d in self.devices]
        
        return {
            "min_x": min(x_coords),
            "max_x": max(x_coords),
            "min_y": min(y_coords),
            "max_y": max(y_coords)
        }


@dataclass 
class ImageInput:
    """输入数据格式"""
    gis_data: GISData                              # 核心：用来画图的结构化数据
    visual_image_path: Optional[str] = None        # 辅助：基于gis_data生成的可视化图片路径
    image_format: str = "png"                      # 图片格式
    input_id: Optional[str] = None                 # 输入ID（用于追踪）
    timestamp: float = field(default_factory=time.time)  # 输入时间戳
    
    def __post_init__(self):
        """后处理：生成默认ID"""
        if self.input_id is None:
            self.input_id = f"input_{int(self.timestamp)}"


@dataclass
class ModelInfo:
    """模型信息"""
    model_type: str                    # 模型类型 ('qwen', 'openai', 'kimi', 'glm')
    model_name: str                    # 具体模型名称
    api_version: Optional[str] = None  # API版本
    provider: Optional[str] = None     # 提供商


@dataclass
class TokenUsage:
    """Token使用统计"""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    
    def __post_init__(self):
        """确保total_tokens正确"""
        if self.total_tokens == 0:
            self.total_tokens = self.input_tokens + self.output_tokens


@dataclass
class TreatmentResponse:
    """治理响应格式"""
    treated_gis_data: GISData          # 治理后的完整GIS结构化数据
    input_tokens: int                  # 输入token数
    output_tokens: int                 # 输出token数
    processing_time: float             # API调用时间
    raw_response: str                  # 原始响应
    confidence_score: float = 0.8      # 模型对治理结果的置信度
    
    @property
    def token_usage(self) -> TokenUsage:
        """获取token使用情况"""
        return TokenUsage(
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            total_tokens=self.input_tokens + self.output_tokens
        )


@dataclass
class EvaluationResponse:
    """评分响应格式"""
    beauty_score: float                           # 总体美观性评分 (0-100)
    dimension_scores: Dict[str, float]            # 各维度评分 {"layout": 85, "spacing": 90, "harmony": 80}
    improvement_analysis: Dict[str, Any]          # 改善分析 {"devices_moved": 5, "spacing_improved": True}
    reasoning: str                                # 评分理由和改善建议
    input_tokens: int = 0                        # 输入token数
    output_tokens: int = 0                       # 输出token数
    
    @property
    def token_usage(self) -> TokenUsage:
        """获取token使用情况"""
        return TokenUsage(
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            total_tokens=self.input_tokens + self.output_tokens
        )


@dataclass
class TreatmentResult:
    """完整的治理结果"""
    original_input: ImageInput                    # 原始输入（包含原始GIS数据）
    treated_gis_data: GISData                    # 治理后的结构化GIS数据
    treated_image_path: Optional[str] = None     # 基于treated_gis_data生成的可视化图片
    beauty_score: float = 0.0                    # 美观性评分 (0-100)
    improvement_metrics: Dict[str, Any] = field(default_factory=dict)  # 改善指标
    model_info: Optional[ModelInfo] = None       # 使用的模型信息
    tokens_used: Optional[TokenUsage] = None     # token使用情况
    processing_time: float = 0.0                 # 处理时间
    cost: float = 0.0                           # 处理成本
    result_id: Optional[str] = None             # 结果ID
    timestamp: float = field(default_factory=time.time)  # 完成时间戳
    
    def __post_init__(self):
        """后处理：生成默认ID"""
        if self.result_id is None:
            self.result_id = f"result_{int(self.timestamp)}"
    
    def get_improvement_summary(self) -> Dict[str, Any]:
        """获取改善总结"""
        original_count = self.original_input.gis_data.get_device_count()
        treated_count = self.treated_gis_data.get_device_count()
        
        return {
            "original_device_count": original_count,
            "treated_device_count": treated_count,
            "devices_changed": abs(treated_count - original_count),
            "beauty_improvement": self.beauty_score,
            "cost_per_improvement": self.cost / max(self.beauty_score, 1),
            "processing_time": self.processing_time
        }


@dataclass
class BatchInput:
    """批量输入格式"""
    inputs: List[ImageInput] = field(default_factory=list)  # 输入列表
    config: Optional[Dict[str, Any]] = None                 # 处理配置
    batch_id: Optional[str] = None                          # 批次ID
    timestamp: float = field(default_factory=time.time)     # 批次时间戳
    
    def __post_init__(self):
        """后处理：生成默认ID和配置"""
        if self.batch_id is None:
            self.batch_id = f"batch_{int(self.timestamp)}"
        if self.config is None:
            self.config = {}
    
    def get_total_images(self) -> int:
        """获取图片总数"""
        return len(self.inputs)


@dataclass
class BatchSummary:
    """批量处理汇总"""
    total_images: int
    successful_images: int
    failed_images: int
    average_beauty_score: float
    total_cost: float
    total_processing_time: float
    average_processing_time: float
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        return self.successful_images / max(self.total_images, 1) * 100


@dataclass
class BatchResult:
    """批量处理结果"""
    results: List[TreatmentResult] = field(default_factory=list)  # 所有结果
    summary: Optional[BatchSummary] = None                        # 批量处理汇总
    wandb_run_id: Optional[str] = None                           # WandB运行ID
    batch_id: Optional[str] = None                               # 对应的批次ID
    timestamp: float = field(default_factory=time.time)          # 完成时间戳
    
    def __post_init__(self):
        """后处理：生成汇总统计"""
        if self.summary is None and self.results:
            self.summary = self._calculate_summary()
    
    def _calculate_summary(self) -> BatchSummary:
        """计算汇总统计"""
        total_images = len(self.results)
        # 治理成功的判断：有治理后的GIS数据且设备数量大于0
        successful_results = [r for r in self.results if 
                            hasattr(r, 'treated_gis_data') and r.treated_gis_data and 
                            len(getattr(r.treated_gis_data, 'devices', []) or []) > 0]
        successful_images = len(successful_results)
        failed_images = total_images - successful_images
        
        if successful_results:
            avg_beauty_score = sum(r.beauty_score for r in successful_results) / successful_images
            total_cost = sum(r.cost for r in self.results)
            total_time = sum(r.processing_time for r in self.results)
            avg_time = total_time / total_images
        else:
            avg_beauty_score = 0.0
            total_cost = 0.0
            total_time = 0.0
            avg_time = 0.0
        
        return BatchSummary(
            total_images=total_images,
            successful_images=successful_images,
            failed_images=failed_images,
            average_beauty_score=avg_beauty_score,
            total_cost=total_cost,
            total_processing_time=total_time,
            average_processing_time=avg_time
        )
    
    def get_failed_results(self) -> List[TreatmentResult]:
        """获取失败的结果"""
        return [r for r in self.results if r.beauty_score <= 0]
    
    def get_successful_results(self) -> List[TreatmentResult]:
        """获取成功的结果"""
        return [r for r in self.results if r.beauty_score > 0]


# 类型别名
GISDataDict = Dict[str, Any]  # GIS数据的字典表示
CoordinatesList = List[List[float]]  # 坐标列表 [[x1,y1], [x2,y2], ...]
DeviceDict = Dict[str, Any]  # 设备字典 {"x": 100, "y": 200, "type": "transformer"}