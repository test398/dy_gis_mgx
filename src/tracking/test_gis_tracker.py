"""
GIS实验追踪器测试

测试GISExperimentTracker的各项功能
"""

import time
import logging
import random
from typing import Dict, List, Any
from datetime import datetime


# 导入GIS实验追踪器
from gis_experiment_tracker import create_gis_experiment_tracker, GISExperimentTracker
from metrics import calculate_gis_performance_metrics, calculate_setting_comparison_metrics

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


import wandb
from wandb import Settings

def test_gis_experiment_tracker():
    """
    测试GIS实验追踪器基本功能
    """
    logger.info("开始测试GIS实验追踪器")
    # 在创建追踪器前添加代理配置
    import os
    os.environ["HTTP_PROXY"] = "http://127.0.0.1:10792"
    os.environ["HTTPS_PROXY"] = "https://127.0.0.1:10792"
    
    # 创建实验追踪器
    # tracker = create_gis_experiment_tracker(
    #     experiment_id="test_exp_001",
    #     setting_name="Setting_A",
    #     data_version="标注数据v1",
    #     evaluation_criteria="5项评分标准",
    #     model_name="qwen-vl-max",
    #     algorithm_version="v2.1",
    #     prompt_version="optimized_v3"
    # )

    # 创建实验追踪器（增加wandb超时设置）
    tracker = create_gis_experiment_tracker(
        experiment_id="test_exp_001",
        setting_name="Setting_A",
        data_version="标注数据v1",
        evaluation_criteria="5项评分标准",
        model_name="qwen-vl-max",
        algorithm_version="v2.1",
        prompt_version="optimized_v3",
        # 传递wandb设置：延长超时时间到120秒
        # wandb_settings=Settings(init_timeout=120)
    )
    
    # 测试API调用记录
    logger.info("测试API调用记录")
    for i in range(3):
        api_result = {
            "success": True,
            "beauty_score": random.uniform(70, 90),
            "improvement_score": random.uniform(10, 20),
            "dimension_scores": {
                "overhead_lines": random.uniform(15, 20),
                "cable_lines": random.uniform(12, 20),
                "branch_boxes": random.uniform(15, 20),
                "access_points": random.uniform(12, 20),
                "meter_boxes": random.uniform(12, 20)
            },
            "tokens_used": random.randint(800, 1200),
            "cost": random.uniform(0.05, 0.15)
        }
        
        tracker.log_api_call(
            model_name="qwen-vl-max",
            input_data={"sample_id": f"test_sample_{i+1}"},
            output=api_result,
            metrics={
                "response_time": random.uniform(0.5, 2.0),
                "success": True,
                "error_message": None
            },
            cost=api_result["cost"],
            tokens_used=api_result["tokens_used"]
        )
        
        # 记录实验结果
        tracker.log_experiment_result(
            beauty_score=api_result["beauty_score"],
            improvement_score=api_result["improvement_score"],
            dimension_scores=api_result["dimension_scores"],
            api_success_rate=1.0,
            json_parse_success_rate=1.0,
            processing_time=random.uniform(0.5, 2.0),
            total_tokens=api_result["tokens_used"],
            total_cost=api_result["cost"],
            is_best_attempt=(api_result["beauty_score"] > 80)
        )
    
    # 生成实验报告
    logger.info("生成实验报告")
    report = tracker.generate_experiment_report()
    logger.info(f"实验报告: {report}")
    
    # 保存实验数据
    logger.info("保存实验数据")
    tracker.save_experiment_data("test_gis_experiment_data")
    
    # 完成实验
    tracker.finish_experiment()
    
    logger.info("GIS实验追踪器测试完成")
    return tracker


def test_setting_comparison():
    """
    测试Setting对比功能
    """
    logger.info("开始测试Setting对比功能")
    
    # 创建多个Setting的实验追踪器
    settings = [
        {
            "setting_name": "Setting_A",
            "data_version": "标注数据v1",
            "evaluation_criteria": "5项评分标准"
        },
        {
            "setting_name": "Setting_B",
            "data_version": "标注数据v2", 
            "evaluation_criteria": "改进评价标准"
        },
        {
            "setting_name": "Setting_C",
            "data_version": "扩展数据集",
            "evaluation_criteria": "完整评价体系"
        }
    ]
    
    trackers = {}
    setting_results = {}
    
    for setting in settings:
        # 创建追踪器
        tracker = create_gis_experiment_tracker(
            experiment_id=f"test_{setting['setting_name']}_{datetime.now().strftime('%H%M%S')}",
            setting_name=setting["setting_name"],
            data_version=setting["data_version"],
            evaluation_criteria=setting["evaluation_criteria"]
        )
        
        trackers[setting["setting_name"]] = tracker
        setting_results[setting["setting_name"]] = []
        
        # 运行实验
        for i in range(2):
            api_result = {
                "success": True,
                "beauty_score": random.uniform(60, 95),
                "improvement_score": random.uniform(5, 25),
                "dimension_scores": {
                    "overhead_lines": random.uniform(12, 20),
                    "cable_lines": random.uniform(10, 20),
                    "branch_boxes": random.uniform(12, 20),
                    "access_points": random.uniform(10, 20),
                    "meter_boxes": random.uniform(10, 20)
                },
                "tokens_used": random.randint(800, 1200),
                "cost": random.uniform(0.05, 0.15)
            }
            
            # 记录API调用
            tracker.log_api_call(
                model_name="qwen-vl-max",
                input_data={"sample_id": f"{setting['setting_name']}_sample_{i+1}"},
                output=api_result,
                metrics={
                    "response_time": random.uniform(0.5, 2.0),
                    "success": True,
                    "error_message": None
                },
                cost=api_result["cost"],
                tokens_used=api_result["tokens_used"]
            )
            
            # 记录实验结果
            tracker.log_experiment_result(
                beauty_score=api_result["beauty_score"],
                improvement_score=api_result["improvement_score"],
                dimension_scores=api_result["dimension_scores"],
                api_success_rate=1.0,
                json_parse_success_rate=1.0,
                processing_time=random.uniform(0.5, 2.0),
                total_tokens=api_result["tokens_used"],
                total_cost=api_result["cost"],
                is_best_attempt=(api_result["beauty_score"] > 80)
            )
            
            # 保存结果
            setting_results[setting["setting_name"]].append({
                "beauty_score": api_result["beauty_score"],
                "improvement_score": api_result["improvement_score"],
                "processing_time": random.uniform(0.5, 2.0),
                "api_success_rate": 1.0,
                "total_cost": api_result["cost"]
            })
    
    # 计算Setting对比指标
    logger.info("计算Setting对比指标")
    comparison_metrics = calculate_setting_comparison_metrics(setting_results)
    logger.info(f"Setting对比指标: {comparison_metrics}")
    
    # 完成所有实验
    for tracker in trackers.values():
        tracker.finish_experiment()
    
    logger.info("Setting对比测试完成")
    return comparison_metrics


def test_gis_metrics():
    """
    测试GIS指标计算功能
    """
    logger.info("开始测试GIS指标计算功能")
    
    # 模拟实验结果
    experiment_results = []
    for i in range(5):
        result = {
            "beauty_score": random.uniform(70, 90),
            "improvement_score": random.uniform(10, 20),
            "dimension_scores": {
                "overhead_lines": random.uniform(15, 20),
                "cable_lines": random.uniform(12, 20),
                "branch_boxes": random.uniform(15, 20),
                "access_points": random.uniform(12, 20),
                "meter_boxes": random.uniform(12, 20)
            },
            "api_success_rate": 1.0,
            "json_parse_success_rate": 1.0,
            "processing_time": random.uniform(0.5, 2.0),
            "total_tokens": random.randint(800, 1200),
            "total_cost": random.uniform(0.05, 0.15)
        }
        experiment_results.append(result)
    
    # 计算性能指标
    performance_metrics = calculate_gis_performance_metrics(experiment_results)
    logger.info(f"性能指标: {performance_metrics}")
    
    logger.info("GIS指标计算测试完成")
    return performance_metrics


def main():
    """
    主测试函数
    """
    logger.info("开始GIS实验追踪系统测试")
    
    try:
        # 测试基本功能
        test_gis_experiment_tracker()
        
        # 测试Setting对比
        test_setting_comparison()
        
        # 测试指标计算
        test_gis_metrics()
        
        logger.info("所有测试完成")
        
    except Exception as e:
        logger.error(f"测试过程中出错: {e}")


if __name__ == "__main__":
    main() 