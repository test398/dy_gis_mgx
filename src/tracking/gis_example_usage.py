"""
电网台区美化系统 - WandB实验追踪示例

基于WandB实验追踪方案 - 20250807.md的要求实现
演示如何使用GISExperimentTracker进行实验追踪
"""

import time
import logging
import random
from typing import Dict, List, Any
from datetime import datetime

# 导入GIS实验追踪器
from gis_experiment_tracker import create_gis_experiment_tracker, GISExperimentTracker

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GISExperimentRunner:
    """
    GIS实验运行器
    
    用于运行不同类型的GIS实验并记录结果
    """
    
    def __init__(self):
        self.trackers: Dict[str, GISExperimentTracker] = {}
        self.experiment_results: Dict[str, List[Dict]] = {}
    
    def run_setting_experiment(self, 
                              setting_name: str,
                              data_version: str,
                              evaluation_criteria: str,
                              num_samples: int = 5) -> Dict[str, Any]:
        """
        运行指定Setting的实验
        
        Args:
            setting_name: Setting名称 (Setting_A, Setting_B, Setting_C等)
            data_version: 数据集版本
            evaluation_criteria: 评价标准
            num_samples: 样本数量
            
        Returns:
            Dict: 实验结果
        """
        experiment_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{setting_name}"
        
        logger.info(f"开始运行 {setting_name} 实验 (数据集: {data_version}, 评价标准: {evaluation_criteria})")
        
        # 创建实验追踪器
        tracker = create_gis_experiment_tracker(
            experiment_id=experiment_id,
            setting_name=setting_name,
            data_version=data_version,
            evaluation_criteria=evaluation_criteria,
            model_name="qwen-vl-max",
            algorithm_version="v2.1",
            prompt_version="optimized_v3"
        )
        
        self.trackers[experiment_id] = tracker
        self.experiment_results[experiment_id] = []
        
        total_beauty_score = 0
        total_improvement_score = 0
        total_processing_time = 0
        total_tokens = 0
        total_cost = 0
        successful_calls = 0
        
        # 运行实验样本
        for i in range(num_samples):
            logger.info(f"处理样本 {i+1}/{num_samples}")
            
            # 模拟API调用
            start_time = time.time()
            api_result = self._simulate_api_call(f"sample_{i+1:03d}")
            processing_time = time.time() - start_time
            
            # 记录API调用
            tracker.log_api_call(
                model_name="qwen-vl-max",
                input_data={"sample_id": f"sample_{i+1:03d}", "setting": setting_name},
                output=api_result,
                metrics={
                    "response_time": processing_time,
                    "success": api_result.get("success", True),
                    "error_message": api_result.get("error_message")
                },
                cost=api_result.get("cost", 0.1),
                tokens_used=api_result.get("tokens_used", 1000)
            )
            
            # 计算评分
            beauty_score = api_result.get("beauty_score", 0)
            improvement_score = api_result.get("improvement_score", 0)
            dimension_scores = api_result.get("dimension_scores", {})
            
            # 记录实验结果
            tracker.log_experiment_result(
                beauty_score=beauty_score,
                improvement_score=improvement_score,
                dimension_scores=dimension_scores,
                api_success_rate=1.0 if api_result.get("success", True) else 0.0,
                json_parse_success_rate=1.0,
                processing_time=processing_time,
                total_tokens=api_result.get("tokens_used", 1000),
                total_cost=api_result.get("cost", 0.1),
                is_best_attempt=(beauty_score > 80)  # 简单的最佳尝试判断
            )
            
            # 累计统计
            total_beauty_score += beauty_score
            total_improvement_score += improvement_score
            total_processing_time += processing_time
            total_tokens += api_result.get("tokens_used", 1000)
            total_cost += api_result.get("cost", 0.1)
            if api_result.get("success", True):
                successful_calls += 1
            
            # 保存结果
            self.experiment_results[experiment_id].append({
                "sample_id": f"sample_{i+1:03d}",
                "beauty_score": beauty_score,
                "improvement_score": improvement_score,
                "dimension_scores": dimension_scores,
                "processing_time": processing_time,
                "tokens_used": api_result.get("tokens_used", 1000),
                "cost": api_result.get("cost", 0.1)
            })
            
            logger.info(f"样本 {i+1} 处理完成，美观性评分: {beauty_score:.1f}")
        
        # 计算平均指标
        avg_beauty_score = total_beauty_score / num_samples
        avg_improvement_score = total_improvement_score / num_samples
        avg_processing_time = total_processing_time / num_samples
        api_success_rate = successful_calls / num_samples
        
        logger.info(f"{setting_name} 实验完成")
        logger.info(f"  平均美观性评分: {avg_beauty_score:.1f}")
        logger.info(f"  平均治理提升分数: {avg_improvement_score:.1f}")
        logger.info(f"  平均处理时间: {avg_processing_time:.2f}s")
        logger.info(f"  API成功率: {api_success_rate:.1%}")
        
        return {
            "experiment_id": experiment_id,
            "setting_name": setting_name,
            "data_version": data_version,
            "evaluation_criteria": evaluation_criteria,
            "avg_beauty_score": avg_beauty_score,
            "avg_improvement_score": avg_improvement_score,
            "avg_processing_time": avg_processing_time,
            "api_success_rate": api_success_rate,
            "total_tokens": total_tokens,
            "total_cost": total_cost
        }
    
    def run_all_settings(self) -> Dict[str, Any]:
        """
        运行所有Setting的实验
        
        Returns:
            Dict: 所有实验结果
        """
        logger.info("开始运行所有Setting的实验")
        
        # 定义所有Setting
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
        
        results = {}
        
        for setting in settings:
            result = self.run_setting_experiment(
                setting_name=setting["setting_name"],
                data_version=setting["data_version"],
                evaluation_criteria=setting["evaluation_criteria"],
                num_samples=3  # 每个Setting运行3个样本
            )
            results[setting["setting_name"]] = result
        
        return results
    
    def save_all_results(self, output_dir: str = "gis_experiment_results") -> None:
        """
        保存所有实验结果
        
        Args:
            output_dir: 输出目录
        """
        logger.info(f"保存所有实验结果到: {output_dir}")
        
        for experiment_id, tracker in self.trackers.items():
            try:
                tracker.save_experiment_data(output_dir)
            except Exception as e:
                logger.error(f"保存实验 {experiment_id} 结果时出错: {e}")
    
    def finish_all_experiments(self) -> None:
        """
        完成所有实验
        """
        logger.info("完成所有实验")
        
        for experiment_id, tracker in self.trackers.items():
            try:
                tracker.finish_experiment()
            except Exception as e:
                logger.error(f"完成实验 {experiment_id} 时出错: {e}")
    
    def _simulate_api_call(self, sample_id: str) -> Dict[str, Any]:
        """
        模拟API调用
        
        Args:
            sample_id: 样本ID
            
        Returns:
            Dict: 模拟的API调用结果
        """
        # 模拟处理时间
        time.sleep(random.uniform(0.1, 0.5))
        
        # 模拟评分结果
        beauty_score = random.uniform(60, 95)
        improvement_score = random.uniform(5, 25)
        
        # 模拟5维度分项分数
        dimension_scores = {
            "overhead_lines": random.uniform(15, 20),
            "cable_lines": random.uniform(12, 20),
            "branch_boxes": random.uniform(15, 20),
            "access_points": random.uniform(12, 20),
            "meter_boxes": random.uniform(12, 20)
        }
        
        # 确保总分不超过100
        total_dimension_score = sum(dimension_scores.values())
        if total_dimension_score > 100:
            scale_factor = 100 / total_dimension_score
            dimension_scores = {k: v * scale_factor for k, v in dimension_scores.items()}
        
        return {
            "success": True,
            "beauty_score": beauty_score,
            "improvement_score": improvement_score,
            "dimension_scores": dimension_scores,
            "tokens_used": random.randint(800, 1200),
            "cost": random.uniform(0.05, 0.15),
            "error_message": None
        }


def main():
    """
    主函数 - 演示GIS实验追踪系统的使用
    """
    logger.info("开始GIS实验追踪系统演示")
    
    # 创建实验运行器
    runner = GISExperimentRunner()
    
    try:
        # 运行所有Setting的实验
        results = runner.run_all_settings()
        
        # 打印结果摘要
        logger.info("\n=== 实验结果摘要 ===")
        for setting_name, result in results.items():
            logger.info(f"{setting_name}:")
            logger.info(f"  数据集版本: {result['data_version']}")
            logger.info(f"  评价标准: {result['evaluation_criteria']}")
            logger.info(f"  平均美观性评分: {result['avg_beauty_score']:.1f}")
            logger.info(f"  平均治理提升分数: {result['avg_improvement_score']:.1f}")
            logger.info(f"  API成功率: {result['api_success_rate']:.1%}")
            logger.info("")
        
        # 保存实验结果
        runner.save_all_results()
        
        logger.info("GIS实验追踪系统演示完成")
        
    except Exception as e:
        logger.error(f"实验运行出错: {e}")
    finally:
        # 完成所有实验
        runner.finish_all_experiments()


if __name__ == "__main__":
    main() 