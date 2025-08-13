#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片上传功能使用示例

展示如何使用WandB追踪器的图片上传功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.tracking.wandb_tracker import ExperimentTracker, ExperimentConfig

def demo_image_upload():
    """
    演示图片上传功能
    """
    # 创建实验配置
    config = ExperimentConfig(
        experiment_name="image_upload_demo",
        project_name="grid-beautification",
        tags=["demo", "image_upload"],
        notes="演示图片上传功能"
    )
    
    # 创建追踪器
    tracker = ExperimentTracker(config)
    
    try:
        # 初始化实验
        tracker.init_experiment()
        print("实验已初始化")
        
        # 示例图片路径（请根据实际情况修改）
        # 这里使用项目中可能存在的图片路径作为示例
        example_images = [
            "codespace/kk3.png",
            "codespace/设备位置对比_20250803_132122.png"
        ]
        
        # 检查并使用存在的图片
        existing_images = []
        for img_path in example_images:
            full_path = project_root / img_path
            if full_path.exists():
                existing_images.append(str(full_path))
                print(f"找到示例图片: {img_path}")
        
        if not existing_images:
            print("未找到示例图片，创建虚拟图片路径进行演示")
            # 如果没有真实图片，我们仍然可以演示API的使用方式
            demo_image_paths(tracker)
        else:
            # 使用真实图片进行演示
            demo_real_images(tracker, existing_images)
            
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
    finally:
        # 结束实验
        tracker.finish_experiment()
        print("实验已结束")

def demo_image_paths(tracker):
    """
    演示图片上传API的使用方式（使用虚拟路径）
    """
    print("\n=== 演示图片上传API使用方式 ===")
    
    # 1. 单张图片上传
    print("\n1. 单张图片上传示例:")
    print("tracker.log_image(\n    image_path='path/to/result.jpg',\n    caption='处理结果图片',\n    image_type='result'\n)")
    
    # 2. 对比图片上传
    print("\n2. 对比图片上传示例:")
    print("tracker.log_image_comparison(\n    before_image_path='path/to/before.jpg',\n    after_image_path='path/to/after.jpg',\n    image_id='IMG_001',\n    model_name='GLM-4V'\n)")
    
    # 3. 批量图片上传
    print("\n3. 批量图片上传示例:")
    print("tracker.log_batch_images(\n    image_paths=['img1.jpg', 'img2.jpg', 'img3.jpg'],\n    captions=['图片1', '图片2', '图片3'],\n    image_type='batch_results'\n)")
    
    # 4. 评分结果与图片一起记录
    print("\n4. 评分结果与图片一起记录示例:")
    print("tracker.log_scoring_result(\n    image_id='IMG_001',\n    model_name='GLM-4V',\n    scores={'美观性': 8.5, '合理性': 9.0},\n    before_image_path='path/to/before.jpg',\n    after_image_path='path/to/after.jpg'\n)")

def demo_real_images(tracker, image_paths):
    """
    使用真实图片进行演示
    """
    print("\n=== 使用真实图片进行演示 ===")
    
    # 1. 单张图片上传
    if len(image_paths) >= 1:
        print(f"\n1. 上传单张图片: {os.path.basename(image_paths[0])}")
        tracker.log_image(
            image_path=image_paths[0],
            caption=f"示例图片 - {os.path.basename(image_paths[0])}",
            image_type="demo"
        )
    
    # 2. 批量图片上传
    if len(image_paths) >= 2:
        print(f"\n2. 批量上传图片")
        captions = [f"示例图片 {i+1}" for i in range(len(image_paths))]
        tracker.log_batch_images(
            image_paths=image_paths,
            captions=captions,
            image_type="demo_batch"
        )
    
    # 3. 模拟评分结果记录（带图片）
    if len(image_paths) >= 1:
        print(f"\n3. 记录评分结果（带图片）")
        tracker.log_scoring_result(
            image_id="DEMO_001",
            model_name="GLM-4V",
            scores={
                "美观性": 8.5,
                "合理性": 9.0,
                "安全性": 8.8,
                "经济性": 7.5
            },
            result_image_path=image_paths[0]
        )
    
    # 4. 模拟对比图片（如果有两张图片）
    if len(image_paths) >= 2:
        print(f"\n4. 上传对比图片")
        tracker.log_image_comparison(
            before_image_path=image_paths[0],
            after_image_path=image_paths[1],
            image_id="DEMO_COMPARISON",
            model_name="GLM-4V"
        )

def main():
    """
    主函数
    """
    print("WandB图片上传功能演示")
    print("=" * 50)
    
    # 检查是否设置了WandB API密钥
    if not os.getenv('WANDB_API_KEY'):
        print("\n注意: 未设置WANDB_API_KEY环境变量")
        print("可以通过以下方式设置:")
        print("1. export WANDB_API_KEY=your_api_key")
        print("2. 或者在运行时会提示登录")
        print()
    
    # 运行演示
    demo_image_upload()
    
    print("\n=== 功能说明 ===")
    print("新增的图片上传功能包括:")
    print("1. log_image() - 上传单张图片")
    print("2. log_image_comparison() - 上传对比图片（治理前后）")
    print("3. log_batch_images() - 批量上传图片")
    print("4. log_scoring_result() - 增强版，支持同时上传图片")
    print("\n所有图片都会自动上传到WandB，并可在Web界面中查看")

if __name__ == "__main__":
    main()