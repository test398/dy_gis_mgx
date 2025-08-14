#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
千问模型自动分批处理示例

演示如何使用QwenModel的自动分批处理功能来处理大量GIS数据
"""

import os
import sys
import json
import logging
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.qwen_model import QwenModel
from models.batch_config import BatchConfig, BatchConfigPresets
from core.data_types import GISData

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_large_test_data(device_count: int = 100) -> Dict[str, Any]:
    """
    创建大量测试数据
    
    Args:
        device_count: 设备数量
        
    Returns:
        Dict: 包含大量设备的GIS数据
    """
    devices = []
    for i in range(device_count):
        device = {
            "id": f"device_{i:04d}",
            "x": 100 + (i % 20) * 50,
            "y": 100 + (i // 20) * 50,
            "type": ["transformer", "meter_box", "switch_box", "cable_joint"][i % 4],
            "points": [
                [100 + (i % 20) * 50, 100 + (i // 20) * 50],
                [110 + (i % 20) * 50, 100 + (i // 20) * 50],
                [110 + (i % 20) * 50, 110 + (i // 20) * 50],
                [100 + (i % 20) * 50, 110 + (i // 20) * 50]
            ],
            "properties": {
                "voltage": "10kV" if i % 4 == 0 else "0.4kV",
                "capacity": f"{(i % 10 + 1) * 100}kVA" if i % 4 == 0 else None,
                "status": "active",
                "installation_date": f"2020-{(i % 12) + 1:02d}-01"
            }
        }
        devices.append(device)
    
    return {
        "devices": devices,
        "buildings": [
            {
                "id": "building_001",
                "points": [[50, 50], [150, 50], [150, 150], [50, 150]],
                "type": "residential",
                "height": 20
            }
        ],
        "roads": [
            {
                "id": "road_001",
                "points": [[0, 200], [1000, 200]],
                "type": "main_road",
                "width": 8
            }
        ],
        "rivers": [],
        "boundaries": {
            "area": [[0, 0], [1000, 0], [1000, 1000], [0, 1000]]
        },
        "metadata": {
            "region": "test_area",
            "scale": "1:1000",
            "device_count": device_count,
            "created_for": "batch_processing_test"
        }
    }

def test_auto_batch_processing():
    """
    测试自动分批处理功能
    """
    logger.info("开始测试千问模型自动分批处理功能")
    
    # 检查API密钥
    api_key = os.getenv('QWEN_API_KEY')
    if not api_key:
        logger.error("请设置环境变量 QWEN_API_KEY")
        return
    
    # 创建测试数据（大量设备）
    logger.info("创建大量测试数据...")
    large_data = create_large_test_data(device_count=150)  # 150个设备
    logger.info(f"创建了包含 {len(large_data['devices'])} 个设备的测试数据")
    
    # 初始化千问模型（启用自动分批）
    logger.info("初始化千问模型...")
    qwen_model = QwenModel(
        api_key=api_key,
        model_name="qwen-vl-max-2025-04-08",
        enable_auto_batch=True,
        max_input_length=10000,  # 设置较小的限制以触发分批处理
        batch_overlap=200
    )
    
    # 测试治理提示词
    prompt = """
    请对台区设备布局进行美观性优化：
    1. 调整设备位置，使其排列更加整齐
    2. 优化设备间距，避免过于密集或稀疏
    3. 考虑设备类型的合理分组
    4. 确保设备布局符合电网安全规范
    5. 提升整体视觉美观性
    """
    
    try:
        # 执行自动分批处理
        logger.info("开始执行自动分批处理...")
        result = qwen_model.beautify(large_data, prompt)
        
        if result["success"]:
            logger.info("✅ 自动分批处理成功完成！")
            logger.info(f"处理结果: {result['message']}")
            logger.info(f"元数据: {json.dumps(result['metadata'], ensure_ascii=False, indent=2)}")
            
            # 输出处理统计
            treated_data = result["data"]
            logger.info(f"输入设备数: {len(large_data['devices'])}")
            logger.info(f"输出设备数: {len(treated_data.devices)}")
            
            # 保存结果（可选）
            output_file = "batch_processing_result.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                # 将GISData转换为字典格式保存
                result_dict = {
                    "devices": [device.__dict__ if hasattr(device, '__dict__') else device for device in treated_data.devices],
                    "buildings": treated_data.buildings,
                    "roads": treated_data.roads,
                    "rivers": treated_data.rivers,
                    "boundaries": treated_data.boundaries,
                    "metadata": treated_data.metadata
                }
                json.dump(result_dict, f, ensure_ascii=False, indent=2)
            logger.info(f"结果已保存到: {output_file}")
            
        else:
            logger.error(f"❌ 自动分批处理失败: {result['message']}")
            if 'error' in result:
                logger.error(f"错误详情: {result['error']}")
                
    except Exception as e:
        logger.error(f"❌ 测试过程中发生异常: {e}")
        raise

def test_manual_vs_auto_batch():
    """
    对比手动处理和自动分批处理的效果
    """
    logger.info("开始对比测试：手动处理 vs 自动分批处理")
    
    api_key = os.getenv('QWEN_API_KEY')
    if not api_key:
        logger.error("请设置环境变量 QWEN_API_KEY")
        return
    
    # 创建中等规模的测试数据
    test_data = create_large_test_data(device_count=50)
    prompt = "请优化设备布局，提升美观性。"
    
    # 测试1: 禁用自动分批
    logger.info("\n=== 测试1: 禁用自动分批 ===")
    model_manual = QwenModel(
        api_key=api_key,
        enable_auto_batch=False
    )
    
    try:
        result_manual = model_manual.beautify(test_data, prompt)
        logger.info(f"手动处理结果: {result_manual['success']}")
        if result_manual['success']:
            logger.info(f"输出设备数: {len(result_manual['data'].devices)}")
    except Exception as e:
        logger.error(f"手动处理失败: {e}")
    
    # 测试2: 启用自动分批
    logger.info("\n=== 测试2: 启用自动分批 ===")
    model_auto = QwenModel(
        api_key=api_key,
        enable_auto_batch=True,
        max_input_length=8000
    )
    
    try:
        result_auto = model_auto.beautify(test_data, prompt)
        logger.info(f"自动分批处理结果: {result_auto['success']}")
        if result_auto['success']:
            logger.info(f"输出设备数: {len(result_auto['data'].devices)}")
            logger.info(f"是否使用了分批: {result_auto['metadata']['auto_batch_used']}")
    except Exception as e:
        logger.error(f"自动分批处理失败: {e}")

def main():
    """主函数：演示自动分批处理功能"""
    
    # 配置API密钥
    api_key = os.getenv('QWEN_API_KEY')
    if not api_key:
        print("❌ 请先设置环境变量 QWEN_API_KEY")
        print("   例如: export QWEN_API_KEY='your_api_key_here'")
        return
    
    print("=== 千问模型自动分批处理演示 ===")
    
    # 创建大型测试数据
    print("\n1. 创建大型测试数据...")
    large_gis_data = create_large_test_data()
    print(f"创建了包含 {len(large_gis_data['devices'])} 个设备的测试数据")
    
    # 治理提示词
    prompt = """
    请对以下GIS设备数据进行治理和优化：
    1. 检查设备名称的规范性
    2. 验证坐标的合理性
    3. 补充缺失的属性信息
    4. 优化设备分类
    
    请返回治理后的完整数据。
    """
    
    # 演示1: 使用预设配置
    print("\n2. 演示1: 使用预设配置...")
    
    # 保守配置 - 适合稳定性要求高的场景
    print("\n2.1 使用保守配置")
    conservative_config = BatchConfigPresets.conservative()
    model_conservative = QwenModel(api_key=api_key, batch_config=conservative_config)
    
    try:
        result1 = model_conservative.beautify(large_gis_data, prompt)
        print(f"保守配置处理完成，设备数量: {len(result1.devices)}")
        if hasattr(result1, 'metadata') and 'batch_metadata' in result1.metadata:
            meta = result1.metadata['batch_metadata']
            print(f"  - 总批次: {meta['total_batches']}, 成功: {meta['successful_batches']}, 失败: {meta['failed_batches']}")
    except Exception as e:
        print(f"保守配置处理失败: {e}")
    
    # 激进配置 - 适合快速处理的场景
    print("\n2.2 使用激进配置")
    aggressive_config = BatchConfigPresets.aggressive()
    model_aggressive = QwenModel(api_key=api_key, batch_config=aggressive_config)
    
    try:
        result2 = model_aggressive.beautify(large_gis_data, prompt)
        print(f"激进配置处理完成，设备数量: {len(result2.devices)}")
        if hasattr(result2, 'metadata') and 'batch_metadata' in result2.metadata:
            meta = result2.metadata['batch_metadata']
            print(f"  - 总批次: {meta['total_batches']}, 成功: {meta['successful_batches']}, 失败: {meta['failed_batches']}")
    except Exception as e:
        print(f"激进配置处理失败: {e}")
    
    # 演示2: 自定义配置
    print("\n3. 演示2: 自定义配置...")
    custom_config = BatchConfig(
        enable_auto_batch=True,
        max_input_length=8000,
        batch_overlap=400,
        max_devices_per_batch=20,
        safety_margin=0.9,
        retry_failed_batches=True,
        max_batch_retries=3
    )
    
    model_custom = QwenModel(api_key=api_key, batch_config=custom_config)
    
    try:
        result3 = model_custom.beautify(large_gis_data, prompt)
        print(f"自定义配置处理完成，设备数量: {len(result3.devices)}")
        if hasattr(result3, 'metadata') and 'batch_metadata' in result3.metadata:
            meta = result3.metadata['batch_metadata']
            print(f"  - 总批次: {meta['total_batches']}, 成功: {meta['successful_batches']}, 失败: {meta['failed_batches']}")
            print(f"  - 配置详情: {meta['batch_config']}")
        
        # 保存结果
        output_file = "batch_processing_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            # 将GISData转换为字典格式保存
            result_dict = {
                "devices": [device.__dict__ if hasattr(device, '__dict__') else device for device in result3.devices],
                "buildings": result3.buildings,
                "roads": result3.roads,
                "rivers": result3.rivers,
                "boundaries": result3.boundaries,
                "metadata": result3.metadata
            }
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"自定义配置处理失败: {e}")
    
    # 演示3: 智能配置推荐
    print("\n4. 演示3: 智能配置推荐...")
    
    # 根据数据量推荐配置
    recommended_config = BatchConfigPresets.recommend_for_data_size(len(large_gis_data['devices']))
    print(f"根据 {len(large_gis_data['devices'])} 个设备推荐的配置: {recommended_config}")
    
    model_recommended = QwenModel(api_key=api_key, batch_config=recommended_config)
    
    try:
        result4 = model_recommended.beautify(large_gis_data, prompt)
        print(f"推荐配置处理完成，设备数量: {len(result4.devices)}")
        if hasattr(result4, 'metadata') and 'batch_metadata' in result4.metadata:
            meta = result4.metadata['batch_metadata']
            print(f"  - 总批次: {meta['total_batches']}, 成功: {meta['successful_batches']}, 失败: {meta['failed_batches']}")
    except Exception as e:
        print(f"推荐配置处理失败: {e}")
    
    # 演示4: 禁用分批处理（对比）
    print("\n5. 演示4: 禁用分批处理（对比）...")
    disabled_config = BatchConfigPresets.disabled()
    model_disabled = QwenModel(api_key=api_key, batch_config=disabled_config)
    
    # 只处理小批量数据以避免超限
    small_data = {
        "devices": large_gis_data['devices'][:5],
        "buildings": large_gis_data['buildings'],
        "roads": large_gis_data['roads'],
        "rivers": large_gis_data['rivers'],
        "boundaries": large_gis_data['boundaries'],
        "metadata": large_gis_data['metadata']
    }
    
    try:
        result5 = model_disabled.beautify(small_data, prompt)
        print(f"禁用分批处理完成，设备数量: {len(result5.devices)}")
    except Exception as e:
        print(f"禁用分批处理失败: {e}")
    
    print("\n✅ 所有演示完成！")

if __name__ == "__main__":
    main()