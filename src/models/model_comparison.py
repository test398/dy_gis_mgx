"""
模型性能对比分析模块

提供详细的模型性能评估、对比分析和可视化功能
"""

import time
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

from .multi_model_client import ModelCallResult, ModelComparisonResult
from ..core.data_types import GISData


@dataclass
class PerformanceMetrics:
    """性能指标"""
    model_type: str
    success_rate: float
    avg_processing_time: float
    avg_cost: float
    avg_input_tokens: float
    avg_output_tokens: float
    total_calls: int
    successful_calls: int
    failed_calls: int
    total_cost: float
    total_processing_time: float


@dataclass
class QualityMetrics:
    """质量指标"""
    model_type: str
    consistency_score: float  # 输出一致性
    accuracy_score: float     # 准确性评分
    completeness_score: float # 完整性评分
    confidence_score: float   # 置信度


class ModelComparisonAnalyzer:
    """模型对比分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.analysis_history: List[ModelComparisonResult] = []
        
    def analyze_performance(self, results: Dict[str, ModelCallResult]) -> Dict[str, PerformanceMetrics]:
        """
        分析各模型的性能指标
        
        Args:
            results: 各模型的结果
            
        Returns:
            Dict[str, PerformanceMetrics]: 各模型的性能指标
        """
        self.logger.info("开始分析模型性能指标")
        
        performance_metrics = {}
        
        for model_type, result in results.items():
            # 收集该模型的所有调用结果（如果有多次调用）
            if hasattr(result, 'response') and result.response:
                # 单次调用结果
                metrics = self._calculate_single_performance(model_type, [result])
            else:
                # 多次调用结果
                metrics = self._calculate_single_performance(model_type, [result])
            
            performance_metrics[model_type] = metrics
        
        self.logger.info("性能指标分析完成")
        return performance_metrics
    
    def _calculate_single_performance(self, model_type: str, results: List[ModelCallResult]) -> PerformanceMetrics:
        """计算单个模型的性能指标"""
        if not results:
            return PerformanceMetrics(
                model_type=model_type,
                success_rate=0.0,
                avg_processing_time=0.0,
                avg_cost=0.0,
                avg_input_tokens=0.0,
                avg_output_tokens=0.0,
                total_calls=0,
                successful_calls=0,
                failed_calls=0,
                total_cost=0.0,
                total_processing_time=0.0
            )
        
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        total_calls = len(results)
        successful_calls = len(successful_results)
        failed_calls = len(failed_results)
        
        if successful_calls == 0:
            return PerformanceMetrics(
                model_type=model_type,
                success_rate=0.0,
                avg_processing_time=0.0,
                avg_cost=0.0,
                avg_input_tokens=0.0,
                avg_output_tokens=0.0,
                total_calls=total_calls,
                successful_calls=successful_calls,
                failed_calls=failed_calls,
                total_cost=0.0,
                total_processing_time=0.0
            )
        
        # 计算平均值
        avg_processing_time = sum(r.processing_time for r in successful_results) / successful_calls
        avg_cost = sum(r.cost for r in successful_results) / successful_calls
        avg_input_tokens = sum(r.input_tokens for r in successful_results) / successful_calls
        avg_output_tokens = sum(r.output_tokens for r in successful_results) / successful_calls
        
        total_cost = sum(r.cost for r in successful_results)
        total_processing_time = sum(r.processing_time for r in successful_results)
        
        success_rate = successful_calls / total_calls
        
        return PerformanceMetrics(
            model_type=model_type,
            success_rate=success_rate,
            avg_processing_time=avg_processing_time,
            avg_cost=avg_cost,
            avg_input_tokens=avg_input_tokens,
            avg_output_tokens=avg_output_tokens,
            total_calls=total_calls,
            successful_calls=successful_calls,
            failed_calls=failed_calls,
            total_cost=total_cost,
            total_processing_time=total_processing_time
        )
    
    def analyze_quality(self, results: Dict[str, ModelCallResult], task_type: str) -> Dict[str, QualityMetrics]:
        """
        分析各模型的质量指标
        
        Args:
            results: 各模型的结果
            task_type: 任务类型
            
        Returns:
            Dict[str, QualityMetrics]: 各模型的质量指标
        """
        self.logger.info("开始分析模型质量指标")
        
        quality_metrics = {}
        
        for model_type, result in results.items():
            if result.success and result.response:
                metrics = self._calculate_quality_metrics(model_type, result, task_type)
                quality_metrics[model_type] = metrics
            else:
                # 如果调用失败，设置默认质量指标
                quality_metrics[model_type] = QualityMetrics(
                    model_type=model_type,
                    consistency_score=0.0,
                    accuracy_score=0.0,
                    completeness_score=0.0,
                    confidence_score=0.0
                )
        
        self.logger.info("质量指标分析完成")
        return quality_metrics
    
    def _calculate_quality_metrics(self, model_type: str, result: ModelCallResult, task_type: str) -> QualityMetrics:
        """计算单个模型的质量指标"""
        if task_type == 'beautify':
            return self._calculate_beautify_quality(model_type, result)
        elif task_type == 'evaluate':
            return self._calculate_evaluate_quality(model_type, result)
        else:
            # 默认质量指标
            return QualityMetrics(
                model_type=model_type,
                consistency_score=0.8,
                accuracy_score=0.8,
                completeness_score=0.8,
                confidence_score=getattr(result.response, 'confidence_score', 0.8)
            )
    
    def _calculate_beautify_quality(self, model_type: str, result: ModelCallResult) -> QualityMetrics:
        """计算美化任务的质量指标"""
        response = result.response
        
        # 完整性评分：检查是否包含所有必要字段
        required_fields = ['devices', 'buildings', 'roads', 'rivers', 'boundaries', 'metadata']
        completeness_score = 0.0
        
        if hasattr(response, 'treated_gis_data'):
            gis_data = response.treated_gis_data
            present_fields = sum(1 for field in required_fields if hasattr(gis_data, field) and getattr(gis_data, field))
            completeness_score = present_fields / len(required_fields)
        
        # 置信度评分
        confidence_score = getattr(response, 'confidence_score', 0.8)
        
        # 一致性评分（基于输出格式的一致性）
        consistency_score = 0.8  # 可以基于历史数据计算
        
        # 准确性评分（基于输出合理性）
        accuracy_score = 0.8  # 可以基于规则或人工评估计算
        
        return QualityMetrics(
            model_type=model_type,
            consistency_score=consistency_score,
            accuracy_score=accuracy_score,
            completeness_score=completeness_score,
            confidence_score=confidence_score
        )
    
    def _calculate_evaluate_quality(self, model_type: str, result: ModelCallResult) -> QualityMetrics:
        """计算评估任务的质量指标"""
        response = result.response
        
        # 完整性评分：检查评分维度是否完整
        completeness_score = 0.0
        if hasattr(response, 'dimension_scores'):
            dimension_scores = response.dimension_scores
            required_dimensions = ['layout', 'spacing', 'harmony', 'accessibility']
            present_dimensions = sum(1 for dim in required_dimensions if dim in dimension_scores)
            completeness_score = present_dimensions / len(required_dimensions)
        
        # 置信度评分
        confidence_score = getattr(response, 'confidence_score', 0.8)
        
        # 一致性评分
        consistency_score = 0.8
        
        # 准确性评分
        accuracy_score = 0.8
        
        return QualityMetrics(
            model_type=model_type,
            consistency_score=consistency_score,
            accuracy_score=accuracy_score,
            completeness_score=completeness_score,
            confidence_score=confidence_score
        )
    
    def generate_comparison_report(self, 
                                 comparison_result: ModelComparisonResult,
                                 performance_metrics: Dict[str, PerformanceMetrics],
                                 quality_metrics: Dict[str, QualityMetrics]) -> Dict[str, Any]:
        """
        生成详细的对比报告
        
        Args:
            comparison_result: 模型对比结果
            performance_metrics: 性能指标
            quality_metrics: 质量指标
            
        Returns:
            Dict[str, Any]: 详细对比报告
        """
        self.logger.info("生成详细对比报告")
        
        # 保存到分析历史
        self.analysis_history.append(comparison_result)
        
        # 构建报告
        report = {
            'task_type': comparison_result.task_type,
            'timestamp': comparison_result.timestamp,
            'summary': {
                'total_models': len(comparison_result.results),
                'successful_models': sum(1 for r in comparison_result.results.values() if r.success),
                'failed_models': sum(1 for r in comparison_result.results.values() if not r.success),
                'overall_success_rate': comparison_result.comparison_metrics['success_rate']
            },
            'performance_analysis': {
                model_type: asdict(metrics) for model_type, metrics in performance_metrics.items()
            },
            'quality_analysis': {
                model_type: asdict(metrics) for model_type, metrics in quality_metrics.items()
            },
            'comparison_metrics': comparison_result.comparison_metrics,
            'recommendations': comparison_result.recommendations,
            'model_rankings': self._generate_model_rankings(performance_metrics, quality_metrics)
        }
        
        self.logger.info("详细对比报告生成完成")
        return report
    
    def _generate_model_rankings(self, 
                               performance_metrics: Dict[str, PerformanceMetrics],
                               quality_metrics: Dict[str, QualityMetrics]) -> Dict[str, List[str]]:
        """生成模型排名"""
        rankings = {}
        
        # 性能排名（按处理时间）
        performance_ranking = sorted(
            performance_metrics.items(),
            key=lambda x: x[1].avg_processing_time
        )
        rankings['performance'] = [item[0] for item in performance_ranking]
        
        # 成本效益排名（按成本）
        cost_ranking = sorted(
            performance_metrics.items(),
            key=lambda x: x[1].avg_cost
        )
        rankings['cost_efficiency'] = [item[0] for item in cost_ranking]
        
        # 质量排名（按综合质量分数）
        quality_ranking = sorted(
            quality_metrics.items(),
            key=lambda x: (x[1].accuracy_score + x[1].completeness_score + x[1].consistency_score) / 3,
            reverse=True
        )
        rankings['quality'] = [item[0] for item in quality_ranking]
        
        # 综合排名（加权评分）
        combined_scores = {}
        for model_type in performance_metrics.keys():
            if model_type in quality_metrics:
                perf_score = 1.0 / (1.0 + performance_metrics[model_type].avg_processing_time)
                cost_score = 1.0 / (1.0 + performance_metrics[model_type].avg_cost)
                quality_score = (quality_metrics[model_type].accuracy_score + 
                               quality_metrics[model_type].completeness_score + 
                               quality_metrics[model_type].consistency_score) / 3
                
                # 加权计算（性能30%，成本20%，质量50%）
                combined_score = 0.3 * perf_score + 0.2 * cost_score + 0.5 * quality_score
                combined_scores[model_type] = combined_score
        
        combined_ranking = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        rankings['combined'] = [item[0] for item in combined_ranking]
        
        return rankings
    
    def create_visualization(self, 
                           performance_metrics: Dict[str, PerformanceMetrics],
                           quality_metrics: Dict[str, QualityMetrics],
                           output_dir: str = "reports"):
        """
        创建可视化图表
        
        Args:
            performance_metrics: 性能指标
            quality_metrics: 质量指标
            output_dir: 输出目录
        """
        self.logger.info("开始创建可视化图表")
        
        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 1. 性能对比图
        self._create_performance_charts(performance_metrics, output_dir)
        
        # 2. 质量对比图
        self._create_quality_charts(quality_metrics, output_dir)
        
        # 3. 综合对比图
        self._create_comprehensive_charts(performance_metrics, quality_metrics, output_dir)
        
        self.logger.info(f"可视化图表已保存到: {output_dir}")
    
    def _create_performance_charts(self, performance_metrics: Dict[str, PerformanceMetrics], output_dir: str):
        """创建性能对比图表"""
        models = list(performance_metrics.keys())
        
        # 处理时间对比
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        processing_times = [performance_metrics[m].avg_processing_time for m in models]
        plt.bar(models, processing_times, color='skyblue')
        plt.title('平均处理时间对比')
        plt.ylabel('时间 (秒)')
        plt.xticks(rotation=45)
        
        # 成本对比
        plt.subplot(2, 2, 2)
        costs = [performance_metrics[m].avg_cost for m in models]
        plt.bar(models, costs, color='lightcoral')
        plt.title('平均调用成本对比')
        plt.ylabel('成本 (美元)')
        plt.xticks(rotation=45)
        
        # 成功率对比
        plt.subplot(2, 2, 3)
        success_rates = [performance_metrics[m].success_rate for m in models]
        plt.bar(models, success_rates, color='lightgreen')
        plt.title('成功率对比')
        plt.ylabel('成功率')
        plt.xticks(rotation=45)
        
        # Token使用对比
        plt.subplot(2, 2, 4)
        input_tokens = [performance_metrics[m].avg_input_tokens for m in models]
        output_tokens = [performance_metrics[m].avg_output_tokens for m in models]
        
        x = np.arange(len(models))
        width = 0.35
        
        plt.bar(x - width/2, input_tokens, width, label='输入Tokens', color='lightblue')
        plt.bar(x + width/2, output_tokens, width, label='输出Tokens', color='orange')
        plt.title('Token使用量对比')
        plt.ylabel('Token数量')
        plt.xticks(x, models, rotation=45)
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/performance_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_quality_charts(self, quality_metrics: Dict[str, QualityMetrics], output_dir: str):
        """创建质量对比图表"""
        models = list(quality_metrics.keys())
        
        # 质量维度对比
        plt.figure(figsize=(12, 8))
        
        # 雷达图
        categories = ['一致性', '准确性', '完整性', '置信度']
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # 闭合
        
        ax = plt.subplot(111, projection='polar')
        
        for model_type in models:
            metrics = quality_metrics[model_type]
            values = [
                metrics.consistency_score,
                metrics.accuracy_score,
                metrics.completeness_score,
                metrics.confidence_score
            ]
            values += values[:1]  # 闭合
            
            ax.plot(angles, values, 'o-', linewidth=2, label=model_type)
            ax.fill(angles, values, alpha=0.25)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 1)
        ax.set_title('模型质量维度对比', size=16, pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/quality_radar.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_comprehensive_charts(self, 
                                  performance_metrics: Dict[str, PerformanceMetrics],
                                  quality_metrics: Dict[str, QualityMetrics], 
                                  output_dir: str):
        """创建综合对比图表"""
        models = list(performance_metrics.keys())
        
        # 综合评分对比
        plt.figure(figsize=(14, 10))
        
        # 计算综合评分
        comprehensive_scores = {}
        for model_type in models:
            if model_type in quality_metrics:
                perf_score = 1.0 / (1.0 + performance_metrics[model_type].avg_processing_time)
                cost_score = 1.0 / (1.0 + performance_metrics[model_type].avg_cost)
                quality_score = (quality_metrics[model_type].accuracy_score + 
                               quality_metrics[model_type].completeness_score + 
                               quality_metrics[model_type].consistency_score) / 3
                
                # 加权计算
                comprehensive_score = 0.3 * perf_score + 0.2 * cost_score + 0.5 * quality_score
                comprehensive_scores[model_type] = comprehensive_score
        
        # 综合评分柱状图
        plt.subplot(2, 2, 1)
        scores = [comprehensive_scores.get(m, 0) for m in models]
        colors = ['gold' if i == 0 else 'silver' if i == 1 else 'bronze' if i == 2 else 'lightgray' 
                 for i in range(len(models))]
        plt.bar(models, scores, color=colors)
        plt.title('综合评分对比')
        plt.ylabel('综合评分')
        plt.xticks(rotation=45)
        
        # 性能-质量散点图
        plt.subplot(2, 2, 2)
        perf_scores = [1.0 / (1.0 + performance_metrics[m].avg_processing_time) for m in models]
        quality_scores = [(quality_metrics[m].accuracy_score + 
                          quality_metrics[m].completeness_score + 
                          quality_metrics[m].consistency_score) / 3 
                         for m in models if m in quality_metrics]
        
        plt.scatter(perf_scores, quality_scores, s=100, alpha=0.7)
        for i, model in enumerate([m for m in models if m in quality_metrics]):
            plt.annotate(model, (perf_scores[i], quality_scores[i]), 
                        xytext=(5, 5), textcoords='offset points')
        plt.xlabel('性能评分')
        plt.ylabel('质量评分')
        plt.title('性能-质量散点图')
        
        # 成本-质量散点图
        plt.subplot(2, 2, 3)
        cost_scores = [1.0 / (1.0 + performance_metrics[m].avg_cost) for m in models]
        plt.scatter(cost_scores, quality_scores, s=100, alpha=0.7)
        for i, model in enumerate([m for m in models if m in quality_metrics]):
            plt.annotate(model, (cost_scores[i], quality_scores[i]), 
                        xytext=(5, 5), textcoords='offset points')
        plt.xlabel('成本效益评分')
        plt.ylabel('质量评分')
        plt.title('成本-质量散点图')
        
        # 三维散点图（性能-成本-质量）
        ax = plt.subplot(2, 2, 4, projection='3d')
        ax.scatter(perf_scores, cost_scores, quality_scores, s=100, alpha=0.7)
        for i, model in enumerate([m for m in models if m in quality_metrics]):
            ax.text(perf_scores[i], cost_scores[i], quality_scores[i], model)
        ax.set_xlabel('性能评分')
        ax.set_ylabel('成本效益评分')
        ax.set_zlabel('质量评分')
        ax.set_title('三维综合对比')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/comprehensive_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def export_analysis_data(self, 
                           report: Dict[str, Any], 
                           output_path: str):
        """导出分析数据"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"分析数据已导出到: {output_path}")
            
        except Exception as e:
            self.logger.error(f"导出分析数据失败: {e}")
    
    def get_analysis_history(self) -> List[ModelComparisonResult]:
        """获取分析历史"""
        return self.analysis_history
    
    def get_model_recommendations(self, 
                                task_type: str,
                                priority: str = 'balanced') -> Dict[str, str]:
        """
        获取模型选择建议
        
        Args:
            task_type: 任务类型
            priority: 优先级 ('performance', 'cost', 'quality', 'balanced')
            
        Returns:
            Dict[str, str]: 建议信息
        """
        if not self.analysis_history:
            return {"message": "暂无分析历史数据"}
        
        # 基于最新分析结果生成建议
        latest_analysis = self.analysis_history[-1]
        
        recommendations = {
            'task_type': task_type,
            'priority': priority,
            'recommendations': {}
        }
        
        if priority == 'performance':
            best_model = latest_analysis.comparison_metrics.get('best_performance_model')
            if best_model:
                recommendations['recommendations']['performance'] = f"推荐使用 {best_model} 以获得最佳性能"
        
        elif priority == 'cost':
            cost_efficient_model = latest_analysis.comparison_metrics.get('cost_efficiency_model')
            if cost_efficient_model:
                recommendations['recommendations']['cost'] = f"推荐使用 {cost_efficient_model} 以获得最佳成本效益"
        
        elif priority == 'quality':
            # 基于质量指标推荐
            pass
        
        else:  # balanced
            recommendations['recommendations']['balanced'] = "建议根据具体需求平衡性能、成本和质量"
        
        return recommendations 