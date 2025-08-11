"""
实验追踪模块

提供WandB集成和指标计算功能，用于追踪治理过程和成本分析
"""

from .wandb_tracker import ExperimentTracker, create_experiment_tracker
from .gis_experiment_tracker import GISExperimentTracker, create_gis_experiment_tracker, GISExperimentConfig, GISExperimentResult
from .metrics import (
    calculate_improvement_metrics, 
    calculate_cost_metrics, 
    calculate_model_performance_metrics,
    calculate_comparison_metrics,
    generate_metrics_report,
    ImprovementMetrics,
    CostMetrics,
    # GIS相关指标
    calculate_gis_performance_metrics,
    calculate_setting_comparison_metrics,
    calculate_gis_improvement_metrics,
    generate_gis_metrics_report,
    GISPerformanceMetrics
)
from .example_usage import WandBExperimentRunner, create_sample_test_data
from .gis_example_usage import GISExperimentRunner

__all__ = [
    # 原有功能
    "ExperimentTracker",
    "create_experiment_tracker",
    "calculate_improvement_metrics",
    "calculate_cost_metrics", 
    "calculate_model_performance_metrics",
    "calculate_comparison_metrics",
    "generate_metrics_report",
    "ImprovementMetrics",
    "CostMetrics",
    "WandBExperimentRunner",
    "create_sample_test_data",
    # GIS新功能
    "GISExperimentTracker",
    "create_gis_experiment_tracker",
    "GISExperimentConfig",
    "GISExperimentResult",
    "calculate_gis_performance_metrics",
    "calculate_setting_comparison_metrics",
    "calculate_gis_improvement_metrics",
    "generate_gis_metrics_report",
    "GISPerformanceMetrics",
    "GISExperimentRunner"
]