#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动分批处理配置文件

用于配置千问模型的自动分批处理参数
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class BatchConfig:
    """自动分批处理配置类"""
    
    # 基础配置
    enable_auto_batch: bool = True
    """是否启用自动分批处理"""
    
    max_input_length: int = 15000
    """单次处理的最大字符数"""
    
    batch_overlap: int = 500
    """批次间重叠字符数，用于保持上下文连续性"""
    
    # 高级配置
    max_devices_per_batch: Optional[int] = None
    """每批次最大设备数，None表示自动计算"""
    
    min_batch_size: int = 1
    """最小批次大小，防止批次过小"""
    
    safety_margin: float = 0.8
    """安全边际，实际批次大小为计算值的80%"""
    
    retry_failed_batches: bool = True
    """是否重试失败的批次"""
    
    max_batch_retries: int = 2
    """批次最大重试次数"""
    
    def validate(self) -> bool:
        """验证配置参数的有效性"""
        if self.max_input_length <= 0:
            raise ValueError("max_input_length 必须大于 0")
        
        if self.batch_overlap < 0:
            raise ValueError("batch_overlap 不能为负数")
        
        if self.batch_overlap >= self.max_input_length:
            raise ValueError("batch_overlap 不能大于等于 max_input_length")
        
        if self.safety_margin <= 0 or self.safety_margin > 1:
            raise ValueError("safety_margin 必须在 (0, 1] 范围内")
        
        if self.min_batch_size <= 0:
            raise ValueError("min_batch_size 必须大于 0")
        
        if self.max_batch_retries < 0:
            raise ValueError("max_batch_retries 不能为负数")
        
        return True
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'enable_auto_batch': self.enable_auto_batch,
            'max_input_length': self.max_input_length,
            'batch_overlap': self.batch_overlap,
            'max_devices_per_batch': self.max_devices_per_batch,
            'min_batch_size': self.min_batch_size,
            'safety_margin': self.safety_margin,
            'retry_failed_batches': self.retry_failed_batches,
            'max_batch_retries': self.max_batch_retries
        }
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'BatchConfig':
        """从字典创建配置对象"""
        return cls(**config_dict)


# 预定义配置模板
class BatchConfigPresets:
    """预定义的批处理配置模板"""
    
    @staticmethod
    def conservative() -> BatchConfig:
        """保守配置：较小的批次，更安全"""
        return BatchConfig(
            enable_auto_batch=True,
            max_input_length=8000,
            batch_overlap=800,
            safety_margin=0.7,
            max_batch_retries=3
        )
    
    @staticmethod
    def balanced() -> BatchConfig:
        """平衡配置：默认推荐配置"""
        return BatchConfig(
            enable_auto_batch=True,
            max_input_length=15000,
            batch_overlap=500,
            safety_margin=0.8,
            max_batch_retries=2
        )
    
    @staticmethod
    def aggressive() -> BatchConfig:
        """激进配置：较大的批次，更高效"""
        return BatchConfig(
            enable_auto_batch=True,
            max_input_length=25000,
            batch_overlap=300,
            safety_margin=0.9,
            max_batch_retries=1
        )
    
    @staticmethod
    def disabled() -> BatchConfig:
        """禁用自动分批"""
        return BatchConfig(
            enable_auto_batch=False,
            max_input_length=50000,  # 设置很大的值
            batch_overlap=0,
            safety_margin=1.0,
            max_batch_retries=0
        )
    
    @staticmethod
    def small_data() -> BatchConfig:
        """小数据配置：适用于设备数量较少的场景"""
        return BatchConfig(
            enable_auto_batch=True,
            max_input_length=5000,
            batch_overlap=200,
            max_devices_per_batch=20,
            safety_margin=0.8,
            max_batch_retries=2
        )
    
    @staticmethod
    def large_data() -> BatchConfig:
        """大数据配置：适用于设备数量很多的场景"""
        return BatchConfig(
            enable_auto_batch=True,
            max_input_length=20000,
            batch_overlap=1000,
            max_devices_per_batch=100,
            safety_margin=0.8,
            max_batch_retries=3
        )
    
    @staticmethod
    def recommend_for_data_size(device_count: int) -> BatchConfig:
        """根据设备数量推荐配置"""
        return get_config_for_device_count(device_count)
    
    @staticmethod
    def recommend_for_input_size(estimated_size: int) -> BatchConfig:
        """根据估算输入大小推荐配置"""
        return get_config_for_input_size(estimated_size)


def get_config_for_device_count(device_count: int) -> BatchConfig:
    """根据设备数量推荐配置"""
    if device_count <= 20:
        return BatchConfigPresets.small_data()
    elif device_count <= 50:
        return BatchConfigPresets.conservative()
    elif device_count <= 100:
        return BatchConfigPresets.balanced()
    elif device_count <= 200:
        return BatchConfigPresets.aggressive()
    else:
        return BatchConfigPresets.large_data()


def get_config_for_input_size(estimated_size: int) -> BatchConfig:
    """根据估算的输入大小推荐配置"""
    if estimated_size <= 5000:
        return BatchConfigPresets.disabled()
    elif estimated_size <= 15000:
        return BatchConfigPresets.conservative()
    elif estimated_size <= 30000:
        return BatchConfigPresets.balanced()
    else:
        return BatchConfigPresets.aggressive()


# 示例用法
if __name__ == "__main__":
    # 创建配置
    config = BatchConfigPresets.balanced()
    print("平衡配置:")
    print(config)
    
    # 验证配置
    try:
        config.validate()
        print("✅ 配置验证通过")
    except ValueError as e:
        print(f"❌ 配置验证失败: {e}")
    
    # 根据设备数量推荐配置
    device_count = 150
    recommended_config = get_config_for_device_count(device_count)
    print(f"\n针对 {device_count} 个设备的推荐配置:")
    print(recommended_config)
    
    # 转换为字典
    config_dict = recommended_config.to_dict()
    print("\n配置字典:")
    for key, value in config_dict.items():
        print(f"  {key}: {value}")