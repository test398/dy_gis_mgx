"""
电网台区美化治理与打分系统 - 主入口程序

演示端到端的治理和评分流程
"""

import os
import sys
import time
import logging
from typing import List, Optional
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent.absolute()
src_dir = current_dir / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# 导入src下的模块
from core.data_types import GISData, ImageInput, TreatmentResult, BatchInput, BatchResult
from core.pipeline import process_single_image, process_batch
from models import get_model, list_available_models

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def create_demo_gis_data() -> GISData:
    """创建演示用的GIS数据"""
    demo_devices = [
        {"id": "transformer_01", "x": 100, "y": 200, "type": "变压器", 
         "points": [[95, 195], [105, 195], [105, 205], [95, 205]]},
        {"id": "meter_box_01", "x": 150, "y": 180, "type": "表箱", 
         "points": [[145, 175], [155, 175], [155, 185], [145, 185]]},
        {"id": "cable_head_01", "x": 80, "y": 250, "type": "电缆头", 
         "points": [[75, 245], [85, 245], [85, 255], [75, 255]]},
        {"id": "branch_box_01", "x": 200, "y": 160, "type": "分支箱", 
         "points": [[195, 155], [205, 155], [205, 165], [195, 165]]},
    ]
    
    demo_buildings = [
        {"id": "residential_01", "coords": [[50, 150], [120, 150], [120, 220], [50, 220]], "type": "住宅"},
        {"id": "commercial_01", "coords": [[170, 130], [230, 130], [230, 190], [170, 190]], "type": "商业"}
    ]
    
    demo_roads = [
        {"id": "main_road", "coords": [[0, 100], [300, 100]], "width": 8, "type": "主干道"},
        {"id": "branch_road", "coords": [[140, 0], [140, 300]], "width": 6, "type": "支路"}
    ]
    
    return GISData(
        devices=demo_devices,
        buildings=demo_buildings,
        roads=demo_roads,
        rivers=[],
        boundaries={"coords": [[0, 0], [300, 0], [300, 300], [0, 300]]},
        metadata={
            "region_id": "demo_area_001",
            "area_name": "演示台区",
            "coordinate_system": "local",
            "creation_time": time.strftime('%Y-%m-%d %H:%M:%S')
        }
    )


def process_single_image_demo(image_input: ImageInput, model_name: str = 'qwen') -> TreatmentResult:
    """
    演示单图处理流程 - 模拟模式（跳过API调用）
    
    Args:
        image_input: 输入数据
        model_name: 使用的模型名称
        
    Returns:
        TreatmentResult: 模拟处理结果
    """
    logger.info(f"🎭 [DEMO模式] 开始处理台区: {image_input.input_id}")
    logger.info(f"⚠️  [DEMO模式] 跳过{model_name}实际API调用，使用模拟结果展示流程")
    
    # 模拟处理时间
    processing_start = time.perf_counter()
    time.sleep(0.5)  # 模拟API调用时间
    processing_time = time.perf_counter() - processing_start
    
    # 创建模拟的治理后GIS数据（稍微调整设备位置来模拟治理效果）
    treated_gis = create_demo_gis_data()
    for i, device in enumerate(treated_gis.devices):
        # 模拟设备位置优化：稍微调整坐标
        device['x'] += 5 * (i % 2)  # 轻微偏移
        device['y'] += 3 * (i % 3)
        device['id'] = f"treated_{device['id']}"
        # 更新多边形坐标
        for point in device['points']:
            point[0] += 5 * (i % 2)
            point[1] += 3 * (i % 3)
    
    # 创建模拟结果
    result = TreatmentResult(
        original_input=image_input,
        treated_gis_data=treated_gis,
        beauty_score=78.5,  # 模拟美观性评分
        improvement_metrics={
            "layout_optimization": "设备间距优化",
            "visual_harmony": "视觉协调性提升",
            "safety_compliance": "安全规范符合度",
            "simulated": True  # 标记这是模拟结果
        },
        model_info={
            "model_name": model_name,
            "provider": "qwen_simulated",
            "version": "demo_mode"
        },
        processing_time=processing_time,
        cost=0.0123  # 模拟成本
    )
    
    logger.info(f"🎭 [DEMO模式] 处理完成: 评分{result.beauty_score}, 成本${result.cost:.6f}")
    return result


def demo_single_image_processing():
    """演示单图处理流程 - DEMO模式"""
    print("\n" + "="*60)
    print("🎯 演示：单图处理流程")
    print("="*60)
    print("⚠️  [DEMO模式] 跳过实际API调用，使用模拟数据展示流程")
    
    # 创建演示数据
    demo_gis = create_demo_gis_data()
    demo_input = ImageInput(
        gis_data=demo_gis,
        visual_image_path=None,
        input_id="demo_single_image"
    )
    
    print(f"\n📊 输入设备数量: {demo_gis.get_device_count()}")
    print(f"📍 台区区域: {demo_gis.metadata['area_name']}")
    
    # 处理单图
    start_time = time.perf_counter()
    result = process_single_image_demo(demo_input)
    processing_time = time.perf_counter() - start_time
    
    # 显示结果
    print(f"\n📈 [DEMO模式] 处理结果:")
    print(f"  美观性评分: {result.beauty_score:.1f}/100 🎭")
    print(f"  处理时间: {result.processing_time:.2f}s")
    print(f"  处理成本: ${result.cost:.6f}")
    print(f"  治理后设备数: {result.treated_gis_data.get_device_count()}")
    
    if result.beauty_score > 0:
        print(f"  改善指标: {result.improvement_metrics}")
        print(f"  结果ID: {result.result_id}")
        print(f"  🎭 注意: 以上为模拟结果，展示系统处理能力")
    else:
        print(f"  处理状态: 失败")
    
    print(f"\n⏱️  总处理时间: {processing_time:.2f}秒")


def demo_batch_processing():
    """演示批量处理流程 - DEMO模式"""
    print("\n" + "="*60)
    print("🎯 演示：批量处理流程")
    print("="*60)
    
    # 创建多个演示输入
    batch_inputs = []
    for i in range(3):
        demo_gis = create_demo_gis_data()
        # 稍微修改数据以模拟不同台区
        for device in demo_gis.devices:
            device['x'] += i * 20
            device['y'] += i * 15
            device['id'] = f"{device['id']}_batch_{i}"
        
        demo_gis.metadata['region_id'] = f"batch_area_{i+1:03d}"
        demo_gis.metadata['area_name'] = f"批量演示台区{i+1}"
        
        demo_input = ImageInput(
            gis_data=demo_gis,
            input_id=f"demo_batch_{i+1}"
        )
        batch_inputs.append(demo_input)
    
    batch_data = BatchInput(
        inputs=batch_inputs,
        config={"max_workers": 2},
        batch_id="demo_batch_001"
    )
    
    print(f"📊 批量处理图片数: {batch_data.get_total_images()}")
    
    # 🎭 DEMO模式：跳过实际API调用，使用模拟处理
    logger.info("🎭 [DEMO模式] 批量处理：跳过API调用，使用模拟结果")
    print(f"\n⚠️  [DEMO模式] 跳过实际qwen API调用，使用模拟结果展示批量处理流程")
    
    start_time = time.perf_counter()
    
    # 模拟批量处理：逐个处理每个输入
    all_results = []
    for i, batch_input in enumerate(batch_inputs):
        print(f"  🎭 [模拟处理] 台区 {i+1}/{len(batch_inputs)}: {batch_input.input_id}")
        result = process_single_image_demo(batch_input)
        all_results.append(result)
    
    # 创建批量结果
    batch_result = BatchResult(
        results=all_results,
        batch_id=batch_data.batch_id
    )
    
    processing_time = time.perf_counter() - start_time
    
    # 显示批量结果
    print(f"\n📈 [DEMO模式] 批量处理结果:")
    if batch_result.summary:
        print(f"  成功处理: {batch_result.summary.successful_images}/{batch_result.summary.total_images}")
        print(f"  成功率: {batch_result.summary.success_rate:.1f}%")
        print(f"  平均评分: {batch_result.summary.average_beauty_score:.1f}")
        print(f"  总成本: ${batch_result.summary.total_cost:.6f}")
        print(f"  平均处理时间: {batch_result.summary.average_processing_time:.2f}s")
        print(f"  🎭 注意: 以上为模拟数据，用于演示流程")
    
    print(f"\n⏱️  总处理时间: {processing_time:.2f}秒")


def demo_model_info():
    """演示模型信息 - 模拟模式"""
    print("\n" + "="*60)
    print("🎯 演示：模型信息")
    print("="*60)
    
    # 🎭 DEMO模式：跳过实际模型初始化
    print("⚠️  [DEMO模式] 跳过实际模型初始化，展示模拟模型信息")
    
    # 显示可用模型（模拟）
    available_models = ['qwen', 'openai', 'kimi', 'glm']  # 模拟可用模型列表
    print(f"📋 可用模型: {available_models}")
    print(f"🎭 注意: qwen已实现，其他模型为待实现状态")
    
    # 显示千问模型信息（模拟）
    print(f"\n🤖 千问模型信息 (模拟):")
    print(f"  模型名称: qwen-vl-max-2025-04-08")
    print(f"  提供商: 阿里云-通义千问")
    print(f"  状态: 🎭 DEMO模式 - 跳过实际API调用")
    
    print(f"  定价信息 (实际):")
    print(f"    输入: $7.00/1M tokens")
    print(f"    输出: $14.00/1M tokens")
    
    # 检查API密钥状态
    qwen_key = os.getenv('QWEN_API_KEY')
    if qwen_key:
        print(f"  API密钥: ✅ 已配置 (但在DEMO模式下不使用)")
    else:
        print(f"  API密钥: ❌ 未配置 (DEMO模式下无影响)")
    
    print(f"\n📝 其他模型状态:")
    print(f"  OpenAI GPT-4V: 🚧 待实现")
    print(f"  Kimi: 🚧 待实现") 
    print(f"  GLM: 🚧 待实现")


def main():
    """主函数 - 运行完整演示"""
    print("🚀 电网台区美化治理与打分系统")
    print("⚡ Phase 1 基础框架演示")
    print(f"📅 运行时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查环境
    print(f"\n🔧 环境检查:")
    qwen_key = os.getenv('QWEN_API_KEY')
    print(f"  千问API密钥: {'✅ 已配置' if qwen_key else '❌ 未配置'}")
    print(f"  🎭 运行模式: DEMO模式 - 跳过所有API调用")
    
    # 运行演示
    try:
        demo_model_info()
        demo_single_image_processing()
        demo_batch_processing()
        
        print("\n" + "="*60)
        print("✅ 所有演示完成！")
        print("\n🎭 重要说明: 本次演示为DEMO模式")
        print("   - 所有API调用已跳过，使用模拟数据")
        print("   - 展示了完整的系统流程和架构")
        print("   - 实际使用时需配置有效的API密钥")
        
        print("\n📖 Phase 1基础框架已实现:")
        print("   - ✅ 完整的数据结构定义")
        print("   - ✅ BaseModel抽象基类")
        print("   - ✅ QwenModel实现（基于现有API）")
        print("   - ✅ 单图和批量处理Pipeline")
        print("   - ✅ 基础的可扩展架构")
        print("   - ✅ 统一的main.py入口程序")
        
        print("\n🚧 下一步开发计划:")
        print("   - 🔥 优先级1: 融合之前的治理代码（例如openaiApi_clean.py）")
        print("   - 🔥 优先级1: 实现正式的6项打分标准的其中1-2项")
        print("   - 📊 优先级2: WandB实验追踪集成")
        print("   - 🔧 优先级2: 统一配置管理系统")
        print("   - 🤖 优先级3: 其他大模型（OpenAI、Kimi、GLM）")
        print("   - 🎨 优先级3: 打分系统优化")
        print("   - 🎨 优先级3: 美化算法优化")
        print("="*60)
        
    except Exception as e:
        logger.error(f"演示运行失败: {e}")
        print(f"\n❌ 演示失败: {e}")


if __name__ == "__main__":
    main()