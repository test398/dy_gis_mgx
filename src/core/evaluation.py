"""
评分引擎

集成overhead_line_scorer.py的架空线评分功能
"""
from typing import Dict, Any
from .overhead_line_scorer import OverheadLineScorer
import logging

logger = logging.getLogger(__name__)

def evaluation_pipeline(treatment_result: Dict[str, Any]) -> Dict:
    """
    评分流水线：只调用OverheadLineScorer，返回详细评分结果。
    Args:
        treatment_result: 治理结果数据，需包含'gis_data'字段（dict，含'devices'）
    Returns:
        Dict: 架空线评分详细结果
    """
    gis_data = treatment_result.get('gis_data', {})
    scorer = OverheadLineScorer()
    result = scorer.score_overhead_lines(gis_data)
    return result


def calculate_beauty_score(original_data: Dict, treated_data: Dict) -> Dict[str, Any]:
    """
    计算美观性评分（只对治理前后各自调用OverheadLineScorer，返回详细评分结果对比）
    Args:
        original_data: 原始GIS数据（dict，含'devices'）
        treated_data: 治理后GIS数据（dict，含'devices'）
    Returns:
        Dict[str, Any]: 详细评分对比结果
    """
    scorer = OverheadLineScorer()
    original_score = scorer.score_overhead_lines(original_data)
    treated_score = scorer.score_overhead_lines(treated_data)
    return {
        'original_score': original_score,
        'treated_score': treated_score
    }

