"""
数据接口模块

提供输入数据加载和结果保存功能
"""

from .input_loader import load_gis_data, load_batch_data
from .output_saver import save_treatment_results, save_batch_results