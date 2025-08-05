"""
WandB实验追踪系统使用示例

展示如何将WandB实验追踪集成到电网台区美化治理系统中
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

# 导入追踪模块
from wandb_tracker import ExperimentTracker, create_experiment_tracker
from metrics import calculate_improvement_metrics, calculate_cost_metrics, generate_metrics_report


import weave
# 导入模型模块
from models import get_model
import wandb
wandb.login(key="1d7931063f483ab522c3a5fbbded1557fb842d6d")
# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WandBExperimentRunner:
    """
    WandB实验运行器
    
    提供完整的实验流程管理
    """
    
    def __init__(self, experiment_name: str, project_name: str = "grid-beautification", entity: str = "luozhengwei2022-"):
        """
        初始化实验运行器
        
        Args:
            experiment_name: 实验名称
            project_name: 项目名称
            entity: WandB实体
        """
        self.tracker = create_experiment_tracker(
            experiment_name,
            project_name,
            entity=entity
        )
        self.api_calls = []
        self.scoring_results = {}
        
    def run_single_model_experiment(self, 
                                   model_type: str,
                                   test_data: List[Dict],
                                   model_config: Dict) -> Dict[str, Any]:
        """
        运行单模型实验
        
        Args:
            model_type: 模型类型 ('qwen', 'glm', 'kimi')
            test_data: 测试数据列表
            model_config: 模型配置
            
        Returns:
            Dict: 实验结果
        """
        logger.info(f"开始运行 {model_type} 模型实验")
        
        # 初始化模型（模拟模式）
        # model = get_model(model_type, **model_config)
        
        results = {
            'model_type': model_type,
            'api_calls': [],
            'scoring_results': [],
            'performance_metrics': {}
        }
        
        # 处理每个测试样本
        for i, data in enumerate(test_data):
            logger.info(f"处理样本 {i+1}/{len(test_data)}")
            
            try:
                # 记录开始时间
                start_time = time.time()
                
                # 模拟模型调用（避免实际API调用）
                result = {
                    'scores': {
                        'overhead_lines': 15.0 + i,
                        'cable_lines': 12.0 + i,
                        'branch_boxes': 18.0 + i,
                        'access_points': 16.0 + i,
                        'meter_boxes': 14.0 + i
                    },
                    'improved_gis_data': data['gis_data'],
                    'status': 'success'
                }
                
                # 计算响应时间
                response_time = time.time() - start_time
                
                # 记录API调用
                self.tracker.log_api_call(
                    model_name=model_type,
                    input_data=data,
                    output=result,
                    metrics={
                        'response_time': response_time,
                        'success': True,
                        'error_message': None
                    },
                    cost=self._estimate_cost(model_type, result)
                )
                results['api_calls'].append({
                    'model_name': model_type,
                    'input_data': data,
                    'output': result,
                    'metrics': {
                        'response_time': response_time,
                        'success': True,
                        'error_message': None
                    },
                    'cost': self._estimate_cost(model_type, result)
                })
                
                # 如果有评分结果，记录评分
                if 'scores' in result:
                    self.tracker.log_scoring_result(
                        image_id=data.get('image_id', f'sample_{i}'),
                        model_name=model_type,
                        scores=result['scores'],
                        human_scores=data.get('human_scores')
                    )
                    
                    results['scoring_results'].append({
                        'image_id': data.get('image_id', f'sample_{i}'),
                        'scores': result['scores'],
                        'human_scores': data.get('human_scores')
                    })
                
                logger.info(f"样本 {i+1} 处理完成，响应时间: {response_time:.2f}s")
                
            except Exception as e:
                logger.error(f"处理样本 {i+1} 时出错: {e}")
                
                # 记录失败的API调用
                self.tracker.log_api_call(
                    model_name=model_type,
                    input_data=data,
                    output={},
                    metrics={
                        'response_time': time.time() - start_time,
                        'success': False,
                        'error_message': str(e)
                    },
                    cost=0
                )
                results['api_calls'].append({
                    'model_name': model_type,
                    'input_data': data,
                    'output': {},
                    'metrics': {
                        'response_time': time.time() - start_time,
                        'success': False,
                        'error_message': str(e)
                    },
                    'cost': 0
                })
        
        # 计算性能指标
        results['performance_metrics'] = self._calculate_performance_metrics(results)
        
        logger.info(f"{model_type} 模型实验完成")
        return results
    
    def run_multi_model_comparison(self, 
                                  model_configs: Dict[str, Dict],
                                  test_data: List[Dict]) -> Dict[str, Any]:
        """
        运行多模型对比实验
        
        Args:
            model_configs: 模型配置字典 {model_type: config}
            test_data: 测试数据列表
            
        Returns:
            Dict: 对比实验结果
        """
        logger.info("开始运行多模型对比实验")
        
        comparison_results = {
            'model_results': {},
            'comparison_metrics': {},
            'recommendations': []
        }
        
        # 运行每个模型的实验
        for model_type, config in model_configs.items():
            logger.info(f"运行 {model_type} 模型")
            model_results = self.run_single_model_experiment(model_type, test_data, config)
            comparison_results['model_results'][model_type] = model_results
        
        # 生成对比报告
        comparison_report = self.tracker.generate_comparison_report()
        comparison_results['comparison_metrics'] = comparison_report
        
        # 记录模型对比结果
        self.tracker.log_model_comparison(comparison_results['model_results'])
        
        logger.info("多模型对比实验完成")
        return comparison_results
    
    def run_improvement_analysis(self, 
                               before_data: List[Dict],
                               after_data: List[Dict],
                               human_scores: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        运行改善分析实验
        
        Args:
            before_data: 治理前数据
            after_data: 治理后数据
            human_scores: 人工评分（可选）
            
        Returns:
            Dict: 改善分析结果
        """
        logger.info("开始运行改善分析实验")
        
        # 提取评分数据
        before_scores = [data.get('scores', {}) for data in before_data]
        after_scores = [data.get('scores', {}) for data in after_data]
        
        # 计算改善指标
        improvement_metrics = calculate_improvement_metrics(
            before_scores, after_scores, human_scores
        )
        
        # 计算成本指标
        cost_metrics = calculate_cost_metrics(self.api_calls, improvement_metrics)
        
        # 生成综合报告
        analysis_report = generate_metrics_report(
            improvement_metrics, cost_metrics, {}
        )
        
        # 记录到WandB
        if self.tracker.wandb_run:
            self.tracker.wandb_run.log({
                "improvement_metrics": improvement_metrics.__dict__,
                "cost_metrics": cost_metrics.__dict__,
                "analysis_report": analysis_report
            })
        
        logger.info("改善分析实验完成")
        return analysis_report
    
    def save_experiment_results(self, output_dir: str = "experiment_results") -> None:
        """
        保存实验结果
        
        Args:
            output_dir: 输出目录
        """
        # 保存实验数据
        self.tracker.save_experiment_data(output_dir)
        
        # 生成实验总结
        summary = {
            "experiment_name": self.tracker.config.experiment_name,
            "total_api_calls": len(self.tracker.api_calls),
            "total_scoring_records": len(self.tracker.scoring_records),
            "experiment_duration": time.time() - self.tracker.experiment_start_time if self.tracker.experiment_start_time else 0
        }
        
        output_path = Path(output_dir)
        with open(output_path / "experiment_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"实验结果已保存到: {output_path}")
    
    def finish_experiment(self) -> None:
        """完成实验"""
        self.tracker.finish_experiment()
        logger.info("实验已完成")
    
    def _estimate_cost(self, model_type: str, result: Dict) -> float:
        """
        估算API调用成本
        
        Args:
            model_type: 模型类型
            result: API调用结果
            
        Returns:
            float: 估算成本
        """
        # 这里可以根据实际的API定价来计算成本
        # 目前使用简化的估算方法
        cost_estimates = {
            'qwen': 0.01,  # 每次调用约0.01元
            'glm': 0.008,  # 每次调用约0.008元
            'kimi': 0.012  # 每次调用约0.012元
        }
        
        base_cost = cost_estimates.get(model_type, 0.01)
        
        # 根据输出复杂度调整成本
        if 'scores' in result:
            complexity_factor = len(result['scores']) * 0.1
            return base_cost * (1 + complexity_factor)
        
        return base_cost
    
    def _calculate_performance_metrics(self, results: Dict) -> Dict[str, Any]:
        """
        计算性能指标
        
        Args:
            results: 实验结果
            
        Returns:
            Dict: 性能指标
        """
        api_calls = results['api_calls']
        scoring_results = results['scoring_results']
        
        # 计算API性能指标
        successful_calls = [call for call in api_calls if call['metrics']['success']]
        response_times = [call['metrics']['response_time'] for call in successful_calls]
        
        api_metrics = {
            'total_calls': len(api_calls),
            'successful_calls': len(successful_calls),
            'success_rate': len(successful_calls) / len(api_calls) if api_calls else 0,
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'total_cost': sum(call['cost'] for call in api_calls)
        }
        
        # 计算评分性能指标
        if scoring_results:
            all_scores = [result['scores'] for result in scoring_results]
            total_scores = [sum(scores.values()) for scores in all_scores]
            
            scoring_metrics = {
                'total_records': len(scoring_results),
                'avg_total_score': sum(total_scores) / len(total_scores),
                'score_range': {
                    'min': min(total_scores),
                    'max': max(total_scores),
                    'std': sum((score - sum(total_scores) / len(total_scores)) ** 2 for score in total_scores) / len(total_scores)
                }
            }
        else:
            scoring_metrics = {}
        
        return {
            'api_metrics': api_metrics,
            'scoring_metrics': scoring_metrics
        }


def create_sample_test_data() -> List[Dict]:
    """
    创建示例测试数据
    
    Returns:
        List[Dict]: 测试数据列表
    """
    sample_data = [
        {
            'image_id': 'sample_001',
            'gis_data': {
                'overhead_lines': [
                    {'pole_id': 'P001', 'position': [120.1, 30.1], 'height': 12.5},
                    {'pole_id': 'P002', 'position': [120.2, 30.2], 'height': 12.8}
                ],
                'cable_lines': [
                    {'cable_id': 'C001', 'start_point': [120.1, 30.1], 'end_point': [120.2, 30.2]}
                ],
                'branch_boxes': [
                    {'box_id': 'B001', 'position': [120.15, 30.15], 'type': 'distribution'}
                ]
            },
            'human_scores': {
                'overhead_lines': 15.0,
                'cable_lines': 12.0,
                'branch_boxes': 18.0,
                'access_points': 16.0,
                'meter_boxes': 14.0
            },
            'prompt': '请对电网台区进行美观性治理，重点关注架空线路的布局优化。'
        },
        {
            'image_id': 'sample_002',
            'gis_data': {
                'overhead_lines': [
                    {'pole_id': 'P003', 'position': [120.3, 30.3], 'height': 11.8},
                    {'pole_id': 'P004', 'position': [120.4, 30.4], 'height': 12.2}
                ],
                'cable_lines': [
                    {'cable_id': 'C002', 'start_point': [120.3, 30.3], 'end_point': [120.4, 30.4]}
                ],
                'branch_boxes': [
                    {'box_id': 'B002', 'position': [120.35, 30.35], 'type': 'distribution'}
                ]
            },
            'human_scores': {
                'overhead_lines': 16.0,
                'cable_lines': 14.0,
                'branch_boxes': 17.0,
                'access_points': 15.0,
                'meter_boxes': 16.0
            },
            'prompt': '优化电网台区的整体布局，提升美观性和安全性。'
        }
    ]
    
    return sample_data

@weave.op()
def main():
    """
    主函数 - 演示WandB实验追踪系统的使用
    """
    logger.info("开始WandB实验追踪系统演示")
    # 自动登录wandb
    # wandb.login(key="1d7931063f483ab522c3a5fbbded1557fb842d6d")
    
    # 创建实验运行器
    runner = WandBExperimentRunner(
        experiment_name="grid-beautification-experiment-001",
        project_name="grid-beautification",
        entity="luozhengwei2022-"
    )
    
    try:
        # 创建示例测试数据
        test_data = create_sample_test_data()
        
        # 定义模型配置
        model_configs = {
            'qwen': {
                'api_key': 'your-qwen-api-key',
                'model_name': 'qwen-vl-max-latest'
            },
            'glm': {
                'api_key': 'your-glm-api-key',
                'model_name': 'glm-4v'
            }
        }
        
        # 运行单模型实验
        logger.info("运行单模型实验")
        qwen_results = runner.run_single_model_experiment(
            model_type='qwen',
            test_data=test_data,
            model_config=model_configs['qwen']
        )
        
        # 运行多模型对比实验
        logger.info("运行多模型对比实验")
        comparison_results = runner.run_multi_model_comparison(
            model_configs=model_configs,
            test_data=test_data
        )
        
        # 运行改善分析
        logger.info("运行改善分析")
        improvement_results = runner.run_improvement_analysis(
            before_data=test_data,
            after_data=test_data,  # 这里应该使用治理后的数据
            human_scores=[data.get('human_scores') for data in test_data]
        )
        
        # 保存实验结果
        runner.save_experiment_results("experiment_results")
        
        logger.info("实验演示完成")
        
    except Exception as e:
        logger.error(f"实验运行出错: {e}")
        raise
    finally:
        # 完成实验
        runner.finish_experiment()


if __name__ == "__main__":
    weave.init('quickstart_play')
    main() 