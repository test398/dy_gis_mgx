"""
多模型集成客户端

实现多模型并行调用、结果对比和性能分析

注意：此文件是一个模块，不能直接运行。
要使用此模块，请：
1. 导入到其他脚本中
2. 运行 demo.py 或 example_usage.py 查看演示
3. 运行 test_imports.py 测试导入
"""

import time
import asyncio
import concurrent.futures
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
import json
from pathlib import Path

from .base_model import BaseModel
from . import get_model, list_available_models
from ..core.data_types import GISData, TreatmentResponse, EvaluationResponse


@dataclass
class ModelCallResult:
    """单次模型调用结果"""
    model_name: str
    model_type: str
    success: bool
    response: Optional[Any] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    timestamp: float = 0.0


@dataclass
class ModelComparisonResult:
    """模型对比结果"""
    task_type: str  # 'beautify' 或 'evaluate'
    input_data: Dict[str, Any]
    results: Dict[str, ModelCallResult]
    comparison_metrics: Dict[str, Any]
    recommendations: List[str]
    timestamp: float = 0.0


class MultiModelClient:
    """多模型集成客户端"""
    
    def __init__(self, config: Dict[str, Dict[str, str]]):
        """
        初始化多模型客户端
        
        Args:
            config: 模型配置字典
                {
                    'qwen': {'api_key': 'sk-xxx', 'model_name': 'qwen-vl-max'},
                    'glm': {'api_key': 'sk-xxx', 'model_name': 'glm-4v'},
                    'kimi': {'api_key': 'sk-xxx', 'model_name': 'kimi-k2'}
                }
        """
        self.config = config
        self.models: Dict[str, BaseModel] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 初始化所有模型
        self._initialize_models()
        
        # 性能统计
        self.performance_stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_cost': 0.0,
            'total_processing_time': 0.0
        }
    
    def _initialize_models(self):
        """初始化所有配置的模型"""
        for model_type, model_config in self.config.items():
            try:
                if model_type in list_available_models():
                    model = get_model(model_type, **model_config)
                    self.models[model_type] = model
                    self.logger.info(f"模型 {model_type} 初始化成功")
                else:
                    self.logger.warning(f"不支持的模型类型: {model_type}")
            except Exception as e:
                self.logger.error(f"模型 {model_type} 初始化失败: {e}")
    
    def call_all_models(self, 
                       task_type: str, 
                       input_data: Dict[str, Any], 
                       prompt: Optional[str] = None,
                       image_path: Optional[str] = None,
                       timeout: int = 300) -> Dict[str, ModelCallResult]:
        """
        并行调用所有模型
        
        Args:
            task_type: 任务类型 ('beautify' 或 'evaluate')
            input_data: 输入数据
            prompt: 治理提示词（仅用于beautify任务）
            image_path: 图片路径（可选）
            timeout: 超时时间（秒）
            
        Returns:
            Dict[str, ModelCallResult]: 各模型的结果
        """
        self.logger.info(f"开始并行调用所有模型，任务类型: {task_type}")
        start_time = time.perf_counter()
        
        # 使用线程池并行执行
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.models)) as executor:
            # 提交所有任务
            future_to_model = {}
            for model_type, model in self.models.items():
                if task_type == 'beautify':
                    future = executor.submit(
                        self._call_model_beautify, 
                        model_type, 
                        model, 
                        input_data, 
                        prompt, 
                        image_path
                    )
                elif task_type == 'evaluate':
                    future = executor.submit(
                        self._call_model_evaluate, 
                        model_type, 
                        model, 
                        input_data
                    )
                else:
                    self.logger.error(f"不支持的任务类型: {task_type}")
                    continue
                
                future_to_model[future] = model_type
            
            # 收集结果
            results = {}
            for future in concurrent.futures.as_completed(future_to_model, timeout=timeout):
                model_type = future_to_model[future]
                try:
                    result = future.result()
                    results[model_type] = result
                    self.logger.info(f"模型 {model_type} 调用完成")
                except concurrent.futures.TimeoutError:
                    self.logger.error(f"模型 {model_type} 调用超时")
                    results[model_type] = ModelCallResult(
                        model_name=model_type,
                        model_type=model_type,
                        success=False,
                        error="调用超时",
                        processing_time=timeout,
                        timestamp=time.time()
                    )
                except Exception as e:
                    self.logger.error(f"模型 {model_type} 调用失败: {e}")
                    results[model_type] = ModelCallResult(
                        model_name=model_type,
                        model_type=model_type,
                        success=False,
                        error=str(e),
                        timestamp=time.time()
                    )
        
        # 更新性能统计
        total_time = time.perf_counter() - start_time
        self._update_performance_stats(results, total_time)
        
        self.logger.info(f"所有模型调用完成，总耗时: {total_time:.2f}s")
        return results
    
    def _call_model_beautify(self, 
                            model_type: str, 
                            model: BaseModel, 
                            input_data: Dict[str, Any], 
                            prompt: str, 
                            image_path: Optional[str] = None) -> ModelCallResult:
        """调用单个模型的beautify方法"""
        start_time = time.perf_counter()
        timestamp = time.time()
        
        try:
            # 调用模型
            response = model.beautify(input_data, prompt, image_path)
            
            # 计算成本
            cost = model.calculate_cost(response.input_tokens, response.output_tokens)
            
            return ModelCallResult(
                model_name=model.model_name,
                model_type=model_type,
                success=True,
                response=response,
                processing_time=response.processing_time,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cost=cost,
                timestamp=timestamp
            )
            
        except Exception as e:
            return ModelCallResult(
                model_name=model.model_name,
                model_type=model_type,
                success=False,
                error=str(e),
                processing_time=time.perf_counter() - start_time,
                timestamp=timestamp
            )
    
    def _call_model_evaluate(self, 
                           model_type: str, 
                           model: BaseModel, 
                           input_data: Dict[str, Any]) -> ModelCallResult:
        """调用单个模型的evaluate方法"""
        start_time = time.perf_counter()
        timestamp = time.time()
        
        try:
            # 提取原始和治理后的数据
            original_data = input_data.get('original_gis_data')
            treated_data = input_data.get('treated_gis_data')
            
            if not original_data or not treated_data:
                raise ValueError("evaluate任务需要original_gis_data和treated_gis_data")
            
            # 调用模型
            response = model.evaluate(original_data, treated_data)
            
            # 计算成本
            cost = model.calculate_cost(response.input_tokens, response.output_tokens)
            
            return ModelCallResult(
                model_name=model.model_name,
                model_type=model_type,
                success=True,
                response=response,
                processing_time=time.perf_counter() - start_time,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cost=cost,
                timestamp=timestamp
            )
            
        except Exception as e:
            return ModelCallResult(
                model_name=model.model_name,
                model_type=model_type,
                success=False,
                error=str(e),
                processing_time=time.perf_counter() - start_time,
                timestamp=timestamp
            )
    
    def compare_model_outputs(self, 
                            results: Dict[str, ModelCallResult], 
                            task_type: str) -> ModelComparisonResult:
        """
        对比不同模型的输出结果
        
        Args:
            results: 各模型的结果
            task_type: 任务类型
            
        Returns:
            ModelComparisonResult: 对比结果
        """
        self.logger.info("开始对比模型输出结果")
        
        # 计算对比指标
        comparison_metrics = self._calculate_comparison_metrics(results)
        
        # 生成建议
        recommendations = self._generate_recommendations(results, comparison_metrics, task_type)
        
        # 构建对比结果
        comparison_result = ModelComparisonResult(
            task_type=task_type,
            input_data={},  # 这里可以添加输入数据的摘要
            results=results,
            comparison_metrics=comparison_metrics,
            recommendations=recommendations,
            timestamp=time.time()
        )
        
        self.logger.info("模型输出对比完成")
        return comparison_result
    
    def _calculate_comparison_metrics(self, results: Dict[str, ModelCallResult]) -> Dict[str, Any]:
        """计算对比指标"""
        successful_results = {k: v for k, v in results.items() if v.success}
        
        if not successful_results:
            return {
                'success_rate': 0.0,
                'avg_processing_time': 0.0,
                'avg_cost': 0.0,
                'best_performance_model': None,
                'cost_efficiency_model': None
            }
        
        # 成功率
        success_rate = len(successful_results) / len(results)
        
        # 平均处理时间
        avg_processing_time = sum(r.processing_time for r in successful_results.values()) / len(successful_results)
        
        # 平均成本
        avg_cost = sum(r.cost for r in successful_results.values()) / len(successful_results)
        
        # 性能最佳模型（处理时间最短）
        best_performance_model = min(successful_results.items(), 
                                   key=lambda x: x[1].processing_time)[0]
        
        # 成本效益最佳模型（成本最低）
        cost_efficiency_model = min(successful_results.items(), 
                                  key=lambda x: x[1].cost)[0]
        
        return {
            'success_rate': success_rate,
            'avg_processing_time': avg_processing_time,
            'avg_cost': avg_cost,
            'best_performance_model': best_performance_model,
            'cost_efficiency_model': cost_efficiency_model,
            'total_successful_calls': len(successful_results),
            'total_failed_calls': len(results) - len(successful_results)
        }
    
    def _generate_recommendations(self, 
                                results: Dict[str, ModelCallResult], 
                                metrics: Dict[str, Any], 
                                task_type: str) -> List[str]:
        """生成模型选择建议"""
        recommendations = []
        
        # 成功率建议
        if metrics['success_rate'] < 0.5:
            recommendations.append("多个模型调用失败率较高，建议检查API配置和网络连接")
        elif metrics['success_rate'] < 0.8:
            recommendations.append("部分模型调用失败，建议优化API参数或检查模型状态")
        
        # 性能建议
        if metrics['best_performance_model']:
            recommendations.append(f"性能最佳模型: {metrics['best_performance_model']} "
                               f"(处理时间: {metrics['avg_processing_time']:.2f}s)")
        
        # 成本建议
        if metrics['cost_efficiency_model']:
            recommendations.append(f"成本效益最佳模型: {metrics['cost_efficiency_model']} "
                               f"(平均成本: ${metrics['avg_cost']:.4f})")
        
        # 任务特定建议
        if task_type == 'beautify':
            recommendations.append("对于GIS美化任务，建议优先选择支持多模态的模型")
        elif task_type == 'evaluate':
            recommendations.append("对于评估任务，建议选择响应稳定的模型以确保一致性")
        
        return recommendations
    
    def _update_performance_stats(self, results: Dict[str, ModelCallResult], total_time: float):
        """更新性能统计"""
        self.performance_stats['total_calls'] += len(results)
        self.performance_stats['total_processing_time'] += total_time
        
        for result in results.values():
            if result.success:
                self.performance_stats['successful_calls'] += 1
                self.performance_stats['total_cost'] += result.cost
            else:
                self.performance_stats['failed_calls'] += 1
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能统计摘要"""
        total_calls = self.performance_stats['total_calls']
        if total_calls == 0:
            return self.performance_stats
        
        return {
            **self.performance_stats,
            'success_rate': self.performance_stats['successful_calls'] / total_calls,
            'avg_cost_per_call': self.performance_stats['total_cost'] / total_calls,
            'avg_processing_time': self.performance_stats['total_processing_time'] / total_calls
        }
    
    def export_comparison_report(self, 
                               comparison_result: ModelComparisonResult, 
                               output_path: str):
        """导出对比报告"""
        try:
            # 准备导出数据
            export_data = {
                'task_type': comparison_result.task_type,
                'timestamp': comparison_result.timestamp,
                'comparison_metrics': comparison_result.comparison_metrics,
                'recommendations': comparison_result.recommendations,
                'model_results': {}
            }
            
            # 添加各模型结果（排除不可序列化的对象）
            for model_type, result in comparison_result.results.items():
                export_data['model_results'][model_type] = {
                    'model_name': result.model_name,
                    'success': result.success,
                    'processing_time': result.processing_time,
                    'input_tokens': result.input_tokens,
                    'output_tokens': result.output_tokens,
                    'cost': result.cost,
                    'error': result.error,
                    'timestamp': result.timestamp
                }
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"对比报告已导出到: {output_path}")
            
        except Exception as e:
            self.logger.error(f"导出对比报告失败: {e}")
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        return list(self.models.keys())
    
    def get_model_info(self, model_type: str) -> Optional[Dict[str, Any]]:
        """获取指定模型的信息"""
        if model_type in self.models:
            return self.models[model_type].get_model_info()
        return None 