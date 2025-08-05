"""
指标计算模块

提供改善指标和成本指标的计算功能，用于评估治理效果和成本分析
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import wandb


@dataclass
class ImprovementMetrics:
    """改善指标数据类"""
    total_score_improvement: float
    average_score_improvement: float
    improvement_rate: float
    dimension_improvements: Dict[str, float]
    consistency_score: float
    overall_quality_score: float


@dataclass
class CostMetrics:
    """成本指标数据类"""
    total_cost: float
    average_cost_per_call: float
    cost_per_improvement_point: float
    cost_efficiency_ratio: float
    model_cost_comparison: Dict[str, float]


def calculate_improvement_metrics(before_scores: List[Dict[str, float]], 
                                after_scores: List[Dict[str, float]],
                                human_scores: Optional[List[Dict[str, float]]] = None) -> ImprovementMetrics:
    """
    计算改善指标
    
    Args:
        before_scores: 治理前评分列表
        after_scores: 治理后评分列表
        human_scores: 人工评分列表（可选）
        
    Returns:
        ImprovementMetrics: 改善指标
    """
    if len(before_scores) != len(after_scores):
        raise ValueError("治理前后评分数量不匹配")
    
    # 计算总体改善
    before_totals = [sum(scores.values()) for scores in before_scores]
    after_totals = [sum(scores.values()) for scores in after_scores]
    
    mean_before = np.mean(before_totals)
    mean_after = np.mean(after_totals)
    total_score_improvement = mean_after - mean_before
    average_score_improvement = total_score_improvement / len(before_scores) if len(before_scores) > 0 else 0
    improvement_rate = ((mean_after - mean_before) / mean_before * 100) if mean_before != 0 else 0
    
    # 计算各维度改善
    all_dimensions = set()
    for scores in before_scores + after_scores:
        all_dimensions.update(scores.keys())
    
    dimension_improvements = {}
    for dimension in all_dimensions:
        before_dim_scores = [scores.get(dimension, 0) for scores in before_scores]
        after_dim_scores = [scores.get(dimension, 0) for scores in after_scores]
        mean_before_dim = np.mean(before_dim_scores)
        mean_after_dim = np.mean(after_dim_scores)
        dimension_improvements[dimension] = mean_after_dim - mean_before_dim
    
    # 计算一致性评分
    consistency_score = _calculate_consistency_score(after_scores)
    
    # 计算整体质量评分
    overall_quality_score = _calculate_overall_quality_score(after_scores, human_scores)
    
    return ImprovementMetrics(
        total_score_improvement=total_score_improvement,
        average_score_improvement=average_score_improvement,
        improvement_rate=improvement_rate,
        dimension_improvements=dimension_improvements,
        consistency_score=consistency_score,
        overall_quality_score=overall_quality_score
    )


def calculate_cost_metrics(api_calls: List[Dict], 
                          improvement_metrics: ImprovementMetrics) -> CostMetrics:
    """
    计算成本指标
    
    Args:
        api_calls: API调用记录列表
        improvement_metrics: 改善指标
        
    Returns:
        CostMetrics: 成本指标
    """
    # 计算总成本
    total_cost = sum(call.get('cost', 0) for call in api_calls)
    average_cost_per_call = total_cost / len(api_calls) if api_calls else 0
    
    # 计算每改善点的成本
    cost_per_improvement_point = (total_cost / improvement_metrics.total_score_improvement 
                                 if improvement_metrics.total_score_improvement > 0 else float('inf'))
    
    # 计算成本效率比
    cost_efficiency_ratio = improvement_metrics.total_score_improvement / total_cost if total_cost > 0 else 0
    
    # 按模型分组计算成本
    model_costs = {}
    for call in api_calls:
        model_name = call.get('model_name', 'unknown')
        if model_name not in model_costs:
            model_costs[model_name] = 0
        model_costs[model_name] += call.get('cost', 0)
    
    return CostMetrics(
        total_cost=total_cost,
        average_cost_per_call=average_cost_per_call,
        cost_per_improvement_point=cost_per_improvement_point,
        cost_efficiency_ratio=cost_efficiency_ratio,
        model_cost_comparison=model_costs
    )


def calculate_model_performance_metrics(model_results: Dict[str, List[Dict[str, float]]]) -> Dict[str, Any]:
    """
    计算模型性能指标
    
    Args:
        model_results: 各模型的评分结果 {model_name: [scores]}
        
    Returns:
        Dict: 模型性能指标
    """
    performance_metrics = {}
    
    for model_name, scores_list in model_results.items():
        if not scores_list:
            continue
            
        # 计算各维度统计
        all_dimensions = set()
        for scores in scores_list:
            all_dimensions.update(scores.keys())
        
        dimension_stats = {}
        for dimension in all_dimensions:
            dimension_scores = [scores.get(dimension, 0) for scores in scores_list]
            dimension_stats[dimension] = {
                'mean': np.mean(dimension_scores),
                'std': np.std(dimension_scores),
                'min': np.min(dimension_scores),
                'max': np.max(dimension_scores),
                'median': np.median(dimension_scores)
            }
        
        # 计算总体评分统计
        total_scores = [sum(scores.values()) for scores in scores_list]
        total_stats = {
            'mean': np.mean(total_scores),
            'std': np.std(total_scores),
            'min': np.min(total_scores),
            'max': np.max(total_scores),
            'median': np.median(total_scores)
        }
        
        performance_metrics[model_name] = {
            'total_records': len(scores_list),
            'dimension_statistics': dimension_stats,
            'total_score_statistics': total_stats,
            'consistency_score': _calculate_consistency_score(scores_list)
        }
    
    return performance_metrics


def calculate_comparison_metrics(model_a_scores: List[Dict[str, float]], 
                               model_b_scores: List[Dict[str, float]]) -> Dict[str, Any]:
    """
    计算两个模型的对比指标
    
    Args:
        model_a_scores: 模型A的评分结果
        model_b_scores: 模型B的评分结果
        
    Returns:
        Dict: 对比指标
    """
    if len(model_a_scores) != len(model_b_scores):
        raise ValueError("两个模型的评分数量不匹配")
    
    # 计算总体评分对比
    model_a_totals = [sum(scores.values()) for scores in model_a_scores]
    model_b_totals = [sum(scores.values()) for scores in model_b_scores]
    
    total_difference = np.mean(model_b_totals) - np.mean(model_a_totals)
    relative_difference = total_difference / np.mean(model_a_totals) * 100 if np.mean(model_a_totals) > 0 else 0
    
    # 计算各维度对比
    all_dimensions = set()
    for scores in model_a_scores + model_b_scores:
        all_dimensions.update(scores.keys())
    
    dimension_comparisons = {}
    for dimension in all_dimensions:
        model_a_dim_scores = [scores.get(dimension, 0) for scores in model_a_scores]
        model_b_dim_scores = [scores.get(dimension, 0) for scores in model_b_scores]
        
        dim_difference = np.mean(model_b_dim_scores) - np.mean(model_a_dim_scores)
        dim_relative = dim_difference / np.mean(model_a_dim_scores) * 100 if np.mean(model_a_dim_scores) > 0 else 0
        
        dimension_comparisons[dimension] = {
            'difference': dim_difference,
            'relative_difference': dim_relative,
            'model_a_mean': np.mean(model_a_dim_scores),
            'model_b_mean': np.mean(model_b_dim_scores)
        }
    
    # 计算一致性对比
    consistency_a = _calculate_consistency_score(model_a_scores)
    consistency_b = _calculate_consistency_score(model_b_scores)
    
    return {
        'total_difference': total_difference,
        'relative_difference': relative_difference,
        'dimension_comparisons': dimension_comparisons,
        'consistency_comparison': {
            'model_a_consistency': consistency_a,
            'model_b_consistency': consistency_b,
            'consistency_difference': consistency_b - consistency_a
        }
    }


def _calculate_consistency_score(scores_list: List[Dict[str, float]]) -> float:
    """
    计算评分一致性
    
    Args:
        scores_list: 评分列表
        
    Returns:
        float: 一致性评分 (0-1)
    """
    if not scores_list:
        return 0.0
    
    # 计算各维度评分的标准差，标准差越小表示一致性越高
    all_dimensions = set()
    for scores in scores_list:
        all_dimensions.update(scores.keys())
    
    dimension_stds = []
    for dimension in all_dimensions:
        dimension_scores = [scores.get(dimension, 0) for scores in scores_list]
        if len(dimension_scores) > 1:
            std = np.std(dimension_scores)
            mean = np.mean(dimension_scores)
            # 使用变异系数 (CV = std/mean) 来衡量一致性
            cv = std / mean if mean > 0 else 0
            dimension_stds.append(1 - min(cv, 1))  # 转换为一致性评分
    
    return np.mean(dimension_stds) if dimension_stds else 0.0


def _calculate_overall_quality_score(ai_scores: List[Dict[str, float]], 
                                   human_scores: Optional[List[Dict[str, float]]] = None) -> float:
    """
    计算整体质量评分
    
    Args:
        ai_scores: AI评分结果
        human_scores: 人工评分结果（可选）
        
    Returns:
        float: 整体质量评分 (0-100)
    """
    if not ai_scores:
        return 0.0
    
    # 计算AI评分的平均总分
    ai_totals = [sum(scores.values()) for scores in ai_scores]
    ai_average = np.mean(ai_totals)
    
    # 如果有人工评分，计算与人工评分的一致性
    if human_scores and len(human_scores) == len(ai_scores):
        human_totals = [sum(scores.values()) for scores in human_scores]
        human_average = np.mean(human_totals)
        
        # 计算相关性
        correlation = np.corrcoef(ai_totals, human_totals)[0, 1] if len(ai_totals) > 1 else 0
        
        # 计算平均绝对误差
        mae = np.mean(np.abs(np.array(ai_totals) - np.array(human_totals)))
        mae_normalized = 1 - min(mae / 100, 1)  # 归一化到0-1
        
        # 综合质量评分
        quality_score = (ai_average * 0.4 + correlation * 100 * 0.3 + mae_normalized * 100 * 0.3)
    else:
        # 仅基于AI评分计算质量
        quality_score = ai_average
    
    return min(max(quality_score, 0), 100)  # 确保在0-100范围内


def generate_metrics_report(improvement_metrics: ImprovementMetrics,
                          cost_metrics: CostMetrics,
                          model_performance: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成综合指标报告
    
    Args:
        improvement_metrics: 改善指标
        cost_metrics: 成本指标
        model_performance: 模型性能指标
        
    Returns:
        Dict: 综合指标报告
    """
    report = {
        "summary": {
            "total_improvement": improvement_metrics.total_score_improvement,
            "improvement_rate": improvement_metrics.improvement_rate,
            "total_cost": cost_metrics.total_cost,
            "cost_efficiency": cost_metrics.cost_efficiency_ratio,
            "overall_quality": improvement_metrics.overall_quality_score
        },
        "improvement_analysis": {
            "dimension_improvements": improvement_metrics.dimension_improvements,
            "consistency_score": improvement_metrics.consistency_score,
            "average_improvement": improvement_metrics.average_score_improvement
        },
        "cost_analysis": {
            "total_cost": cost_metrics.total_cost,
            "average_cost_per_call": cost_metrics.average_cost_per_call,
            "cost_per_improvement_point": cost_metrics.cost_per_improvement_point,
            "model_cost_comparison": cost_metrics.model_cost_comparison
        },
        "model_performance": model_performance,
        "recommendations": _generate_metrics_recommendations(improvement_metrics, cost_metrics, model_performance)
    }
    # 自动上传summary到wandb
    try:
        wandb.log({"metrics_report": report["summary"]})
        wandb.summary.update(report["summary"])
    except Exception:
        pass
    return report


def _generate_metrics_recommendations(improvement_metrics: ImprovementMetrics,
                                    cost_metrics: CostMetrics,
                                    model_performance: Dict[str, Any]) -> List[str]:
    """
    基于指标生成建议
    
    Args:
        improvement_metrics: 改善指标
        cost_metrics: 成本指标
        model_performance: 模型性能指标
        
    Returns:
        List[str]: 建议列表
    """
    recommendations = []
    
    # 基于改善指标的建议
    if improvement_metrics.improvement_rate < 10:
        recommendations.append("改善率较低，建议优化治理算法")
    
    if improvement_metrics.consistency_score < 0.7:
        recommendations.append("评分一致性较低，建议改进评分标准")
    
    # 基于成本指标的建议
    if cost_metrics.cost_efficiency_ratio < 0.1:
        recommendations.append("成本效率较低，建议优化API调用策略")
    
    if cost_metrics.total_cost > 1000:
        recommendations.append("总成本较高，建议考虑成本优化方案")
    
    # 基于模型性能的建议
    for model_name, performance in model_performance.items():
        total_mean = performance.get('total_score_statistics', {}).get('mean', 0)
        if total_mean < 60:
            recommendations.append(f"{model_name}的平均评分较低，建议优化模型或提示词")
    
    return recommendations 