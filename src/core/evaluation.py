"""
评分引擎

集成overhead_line_scorer.py的架空线评分功能，并扩展阶段4其他维度
"""
from typing import Dict, Any, List, Tuple
from .overhead_line_scorer import OverheadLineScorer
from .cable_line_scorer import CableLineScorer
from .branch_box_scorer import BranchBoxScorer
from .access_point_scorer import AccessPointScorer
from .meter_box_scorer import MeterBoxScorer
import logging

logger = logging.getLogger(__name__)


def evaluation_pipeline(treatment_result: Dict[str, Any]) -> Dict:
    """
    评分流水线：调用阶段1与阶段4评分器，返回详细评分结果。
    Args:
        treatment_result: 治理结果数据，需包含'gis_data'字段（dict，含'devices'）
    Returns:
        Dict: 评分详细结果
    """
    gis_data = treatment_result.get('gis_data', {})

    overhead = OverheadLineScorer().score_overhead_lines(gis_data)
    cable = CableLineScorer().score_cable_lines(gis_data)
    branch = BranchBoxScorer().score_branch_boxes(gis_data)
    accessp = AccessPointScorer().score_access_points(gis_data)
    meter = MeterBoxScorer().score_meter_boxes(gis_data)

    def _safe_total(d: Dict[str, Any], default: float = 0.0) -> float:
        if not isinstance(d, dict):
            return default
        v = d.get('total_score')
        return float(v) if isinstance(v, (int, float)) else default

    total = _safe_total(overhead) + _safe_total(cable) + _safe_total(branch) + _safe_total(accessp) + _safe_total(meter)
    level = _level_from_100(total)
    basis: List[str] = [
        '本次评分聚合：架空线20分 + 低压电缆线路20分 + 分支箱20分 + 接入点20分 + 计量箱20分，总计100分'
    ]

    # 一票否决：设备跨小区沿布（若存在边界多边形）
    veto_applied = False
    veto_reasons: List[str] = []
    try:
        boundary = _extract_boundary_polygon(gis_data)
        if boundary:
            if _has_outside_devices_or_lines(gis_data, boundary):
                veto_applied = True
                veto_reasons.append('触发一票否决：存在设备/线路跨小区边界沿布')
    except Exception as e:
        logger.debug(f"一票否决检测异常：{e}")

    if veto_applied:
        basis.extend(veto_reasons)
        return {
            'total_score': 0.0,
            'level': '较差',
            'basis': basis,
            'veto': True,
            'veto_reasons': veto_reasons,
            'overhead': overhead,
            'cable_lines': cable,
            'branch_boxes': branch,
            'access_points': accessp,
            'meter_boxes': meter,
        }

    return {
        'total_score': round(total, 2),
        'overhead': overhead,
        'cable_lines': cable,
        'branch_boxes': branch,
        'access_points': accessp,
        'meter_boxes': meter,
        'basis': basis,
        'level': level,
        'veto': False
    }


def calculate_beauty_score(original_data: Dict, treated_data: Dict) -> Dict[str, Any]:
    """
    计算美观性评分（对治理前后各自调用完整评分器集，返回详细评分结果对比）
    Args:
        original_data: 原始GIS数据（dict，含'devices'）
        treated_data: 治理后GIS数据（dict，含'devices'）
    Returns:
        Dict[str, Any]: 详细评分对比结果
    """
    original_score = evaluation_pipeline({'gis_data': original_data})
    treated_score = evaluation_pipeline({'gis_data': treated_data})
    return {
        'original_score': original_score,
        'treated_score': treated_score
    }


def _level_from_100(score: float) -> str:
    if score >= 95:
        return '优秀'
    if score >= 75:
        return '良好'
    if score >= 50:
        return '一般'
    return '较差'


# ------------------ 一票否决工具 ------------------

def _extract_boundary_polygon(gis_data: Dict[str, Any]) -> List[Tuple[float, float]]:
    b = gis_data.get('boundaries') or {}
    poly = b.get('coords') or b.get('coors') or b.get('points') or []
    if isinstance(poly, list) and len(poly) >= 3 and isinstance(poly[0], (list, tuple)):
        return [(float(p[0]), float(p[1])) for p in poly]
    return []


def _point_in_polygon(p: Tuple[float, float], poly: List[Tuple[float, float]]) -> bool:
    # 射线法
    x, y = p
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        cond = ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1)
        if cond:
            inside = not inside
    return inside


def _has_outside_devices_or_lines(gis_data: Dict[str, Any], poly: List[Tuple[float, float]]) -> bool:
    devices = gis_data.get('devices', []) or []
    # 点类设备
    for d in devices:
        pts = d.get('points') or []
        if not pts or len(pts) == 1:
            x = float(d.get('x', pts[0][0] if pts else 0.0))
            y = float(d.get('y', pts[0][1] if pts else 0.0))
            if not _point_in_polygon((x, y), poly):
                return True
    # 线/面类设备
    for d in devices:
        pts = d.get('points') or []
        if len(pts) >= 2:
            for i in range(len(pts)):
                px, py = float(pts[i][0]), float(pts[i][1])
                if not _point_in_polygon((px, py), poly):
                    return True
    return False

