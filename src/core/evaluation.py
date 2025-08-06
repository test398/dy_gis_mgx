"""
评分引擎

提供美观性评分功能（目前是placeholder）
"""

from typing import Dict, Any, List, Optional
from .data_types import GISData
import logging
import math
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ScoreLevel(Enum):
    """评分等级枚举"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


@dataclass
class ScoringConfig:
    """评分配置类"""
    # 电杆塔间距评分配置
    pole_distance_excellent_range: tuple = (40, 45)  # 优秀范围
    pole_distance_good_range: tuple = (30, 50)      # 良好范围
    pole_distance_fair_range: tuple = (20, 60)      # 一般范围
    pole_distance_max_score: float = 12.0            # 最大分值
    
    # 墙支架安装评分配置
    bracket_height_excellent_range: tuple = (2.5, 3.5)  # 优秀高度范围
    bracket_height_good_range: tuple = (2.0, 4.0)      # 良好高度范围
    bracket_tilt_excellent_threshold: float = 5.0       # 优秀倾斜度阈值
    bracket_tilt_good_threshold: float = 10.0           # 良好倾斜度阈值
    bracket_max_score: float = 8.0                      # 最大分值
    
    # 权重配置
    pole_distance_weight: float = 0.6                  # 电杆塔间距权重
    wall_bracket_weight: float = 0.4                   # 墙支架安装权重


class OverheadLineScorer:
    """
    架空线评分器
    
    专门用于评估架空线路的美观性和规范性
    支持可配置的评分标准和详细的评分分析
    """
    
    def __init__(self, config: Optional[ScoringConfig] = None):
        """
        初始化评分器
        
        Args:
            config: 评分配置，如果为None则使用默认配置
        """
        self.config = config or ScoringConfig()
        self.logger = logging.getLogger(__name__)
    
    def score_overhead_lines(self, gis_data: Dict) -> Dict:
        """
        评分架空线路
        
        Args:
            gis_data: GIS数据字典，包含设备信息
            
        Returns:
            Dict: 评分结果，包含总分、分项评分和详细分析
        """
        self.logger.info("开始评分架空线路")
        
        # 提取架空线相关设备
        overhead_devices = self._extract_overhead_devices(gis_data)
        
        # 计算各项评分
        pole_tower_result = self._score_pole_tower_span(overhead_devices.get('poles', []))
        wall_bracket_result = self._score_wall_bracket(overhead_devices.get('brackets', []))
        
        # 计算加权总分
        total_score = (
            pole_tower_result['score'] * self.config.pole_distance_weight +
            wall_bracket_result['score'] * self.config.wall_bracket_weight
        )
        
        # 生成评分等级
        score_level = self._calculate_score_level(total_score)
        
        return {
            'total_score': round(total_score, 2),
            'score_level': score_level.value,
            'score_level_name': self._get_score_level_name(score_level),
            'pole_tower_score': pole_tower_result,
            'wall_bracket_score': wall_bracket_result,
            'details': {
                'pole_tower_details': self._get_pole_tower_details(overhead_devices.get('poles', [])),
                'wall_bracket_details': self._get_wall_bracket_details(overhead_devices.get('brackets', [])),
                'overall_analysis': self._generate_overall_analysis(pole_tower_result, wall_bracket_result)
            },
            'recommendations': self._generate_recommendations(pole_tower_result, wall_bracket_result)
        }
    
    def _score_pole_tower_span(self, pole_data: List) -> Dict:
        """
        评分电杆塔间距（12分）
        
        Args:
            pole_data: 电杆塔数据列表
            
        Returns:
            Dict: 评分结果，包含分数、等级和详细分析
        """
        if not pole_data:
            return {
                'score': 0.0,
                'level': ScoreLevel.POOR.value,
                'details': '无电杆塔数据',
                'improvements': ['需要添加电杆塔数据']
            }
        
        # 计算电杆塔间距
        distances = self._calculate_pole_distances(pole_data)
        
        if not distances:
            return {
                'score': 0.0,
                'level': ScoreLevel.POOR.value,
                'details': '电杆塔数量不足，无法计算间距',
                'improvements': ['需要至少2个电杆塔才能计算间距']
            }
        
        # 评分计算
        score = 0.0
        distance_scores = []
        distance_analysis = []
        
        for i, distance in enumerate(distances):
            distance_score = self._calculate_distance_score(distance)
            distance_scores.append(distance_score)
            score += distance_score
            
            # 分析每个间距
            analysis = self._analyze_distance(distance, i + 1)
            distance_analysis.append(analysis)
        
        # 计算平均分
        avg_score = score / len(distances)
        
        # 确定等级
        level = self._get_distance_level(avg_score)
        
        # 生成改进建议
        improvements = self._generate_distance_improvements(distances, distance_analysis)
        
        return {
            'score': round(avg_score, 2),
            'level': level.value,
            'details': f'平均间距: {sum(distances)/len(distances):.1f}米',
            'distance_analysis': distance_analysis,
            'improvements': improvements,
            'raw_data': {
                'distances': distances,
                'distance_scores': distance_scores
            }
        }
    
    def _score_wall_bracket(self, bracket_data: List) -> Dict:
        """
        评分墙支架安装（8分）
        
        Args:
            bracket_data: 墙支架数据列表
            
        Returns:
            Dict: 评分结果，包含分数、等级和详细分析
        """
        if not bracket_data:
            return {
                'score': 0.0,
                'level': ScoreLevel.POOR.value,
                'details': '无墙支架数据',
                'improvements': ['需要添加墙支架数据']
            }
        
        total_score = 0.0
        bracket_analyses = []
        
        for i, bracket in enumerate(bracket_data):
            bracket_score = 0.0
            bracket_analysis = {
                'id': bracket.get('id', f'bracket_{i+1}'),
                'height_score': 0.0,
                'tilt_score': 0.0,
                'secure_score': 0.0,
                'clean_score': 0.0,
                'total_score': 0.0,
                'issues': []
            }
            
            # 检查安装高度
            height = bracket.get('height', 0)
            height_score = self._calculate_height_score(height)
            bracket_score += height_score
            bracket_analysis['height_score'] = height_score
            
            if height_score < 2.0:
                bracket_analysis['issues'].append(f'安装高度{height}米不符合标准(2.5-3.5米)')
            
            # 检查水平度
            tilt = bracket.get('tilt', 0)
            tilt_score = self._calculate_tilt_score(tilt)
            bracket_score += tilt_score
            bracket_analysis['tilt_score'] = tilt_score
            
            if tilt_score < 2.0:
                bracket_analysis['issues'].append(f'倾斜度{abs(tilt)}度超过标准(应<5度)')
            
            # 检查牢固度
            secure = bracket.get('secure', True)
            secure_score = 2.0 if secure else 0.5
            bracket_score += secure_score
            bracket_analysis['secure_score'] = secure_score
            
            if not secure:
                bracket_analysis['issues'].append('固定不牢固')
            
            # 检查外观
            clean = bracket.get('clean', True)
            clean_score = 2.0 if clean else 0.5
            bracket_score += clean_score
            bracket_analysis['clean_score'] = clean_score
            
            if not clean:
                bracket_analysis['issues'].append('外观不整洁')
            
            bracket_analysis['total_score'] = bracket_score
            bracket_analyses.append(bracket_analysis)
            total_score += bracket_score
        
        # 计算平均分
        avg_score = total_score / len(bracket_data)
        
        # 确定等级
        level = self._get_bracket_level(avg_score)
        
        # 生成改进建议
        improvements = self._generate_bracket_improvements(bracket_analyses)
        
        return {
            'score': round(avg_score, 2),
            'level': level.value,
            'details': f'平均评分: {avg_score:.1f}/8',
            'bracket_analyses': bracket_analyses,
            'improvements': improvements,
            'raw_data': {
                'bracket_count': len(bracket_data),
                'avg_height': sum(b.get('height', 0) for b in bracket_data) / len(bracket_data),
                'secure_count': sum(1 for b in bracket_data if b.get('secure', True)),
                'clean_count': sum(1 for b in bracket_data if b.get('clean', True))
            }
        }
    
    def _calculate_distance_score(self, distance: float) -> float:
        """计算单个间距的评分"""
        if self.config.pole_distance_excellent_range[0] <= distance <= self.config.pole_distance_excellent_range[1]:
            return self.config.pole_distance_max_score
        elif self.config.pole_distance_good_range[0] <= distance <= self.config.pole_distance_good_range[1]:
            return self.config.pole_distance_max_score * 0.83  # 10/12
        elif self.config.pole_distance_fair_range[0] <= distance <= self.config.pole_distance_fair_range[1]:
            return self.config.pole_distance_max_score * 0.58  # 7/12
        else:
            return self.config.pole_distance_max_score * 0.25  # 3/12
    
    def _calculate_height_score(self, height: float) -> float:
        """计算高度评分"""
        if self.config.bracket_height_excellent_range[0] <= height <= self.config.bracket_height_excellent_range[1]:
            return 2.0
        elif self.config.bracket_height_good_range[0] <= height <= self.config.bracket_height_good_range[1]:
            return 1.5
        else:
            return 0.5
    
    def _calculate_tilt_score(self, tilt: float) -> float:
        """计算倾斜度评分"""
        abs_tilt = abs(tilt)
        if abs_tilt < self.config.bracket_tilt_excellent_threshold:
            return 2.0
        elif abs_tilt < self.config.bracket_tilt_good_threshold:
            return 1.5
        else:
            return 0.5
    
    def _analyze_distance(self, distance: float, index: int) -> Dict:
        """分析单个间距"""
        level = self._get_distance_level(self._calculate_distance_score(distance))
        
        return {
            'index': index,
            'distance': distance,
            'level': level.value,
            'level_name': self._get_score_level_name(level),
            'recommendation': self._get_distance_recommendation(distance)
        }
    
    def _get_distance_level(self, score: float) -> ScoreLevel:
        """根据分数确定间距等级"""
        if score >= self.config.pole_distance_max_score * 0.83:
            return ScoreLevel.EXCELLENT
        elif score >= self.config.pole_distance_max_score * 0.58:
            return ScoreLevel.GOOD
        elif score >= self.config.pole_distance_max_score * 0.25:
            return ScoreLevel.FAIR
        else:
            return ScoreLevel.POOR
    
    def _get_bracket_level(self, score: float) -> ScoreLevel:
        """根据分数确定墙支架等级"""
        if score >= self.config.bracket_max_score * 0.875:  # 7/8
            return ScoreLevel.EXCELLENT
        elif score >= self.config.bracket_max_score * 0.75:   # 6/8
            return ScoreLevel.GOOD
        elif score >= self.config.bracket_max_score * 0.5:     # 4/8
            return ScoreLevel.FAIR
        else:
            return ScoreLevel.POOR
    
    def _calculate_score_level(self, total_score: float) -> ScoreLevel:
        """计算总体评分等级"""
        if total_score >= 16:
            return ScoreLevel.EXCELLENT
        elif total_score >= 12:
            return ScoreLevel.GOOD
        elif total_score >= 8:
            return ScoreLevel.FAIR
        else:
            return ScoreLevel.POOR
    
    def _get_score_level_name(self, level: ScoreLevel) -> str:
        """获取评分等级中文名称"""
        level_names = {
            ScoreLevel.EXCELLENT: "优秀",
            ScoreLevel.GOOD: "良好",
            ScoreLevel.FAIR: "一般",
            ScoreLevel.POOR: "差"
        }
        return level_names.get(level, "未知")
    
    def _get_distance_recommendation(self, distance: float) -> str:
        """获取间距改进建议"""
        if distance < 30:
            return f"间距{distance}米过小，建议增加到30-50米"
        elif distance > 50:
            return f"间距{distance}米过大，建议减少到30-50米"
        else:
            return f"间距{distance}米符合标准"
    
    def _generate_distance_improvements(self, distances: List[float], analyses: List[Dict]) -> List[str]:
        """生成间距改进建议"""
        improvements = []
        
        if not distances:
            improvements.append("需要添加电杆塔数据")
            return improvements
        
        avg_distance = sum(distances) / len(distances)
        
        if avg_distance < 35:
            improvements.append(f"平均间距{avg_distance:.1f}米偏小，建议优化到40-45米")
        elif avg_distance > 45:
            improvements.append(f"平均间距{avg_distance:.1f}米偏大，建议优化到40-45米")
        
        # 检查间距一致性
        distance_variance = sum((d - avg_distance) ** 2 for d in distances) / len(distances)
        if distance_variance > 25:  # 方差大于25
            improvements.append("电杆塔间距不均匀，建议统一间距")
        
        return improvements
    
    def _generate_bracket_improvements(self, bracket_analyses: List[Dict]) -> List[str]:
        """生成墙支架改进建议"""
        improvements = []
        
        if not bracket_analyses:
            improvements.append("需要添加墙支架数据")
            return improvements
        
        # 统计问题
        height_issues = sum(1 for a in bracket_analyses if a['height_score'] < 2.0)
        tilt_issues = sum(1 for a in bracket_analyses if a['tilt_score'] < 2.0)
        secure_issues = sum(1 for a in bracket_analyses if a['secure_score'] < 2.0)
        clean_issues = sum(1 for a in bracket_analyses if a['clean_score'] < 2.0)
        
        if height_issues > 0:
            improvements.append(f"{height_issues}个墙支架安装高度不符合标准")
        if tilt_issues > 0:
            improvements.append(f"{tilt_issues}个墙支架倾斜度超过标准")
        if secure_issues > 0:
            improvements.append(f"{secure_issues}个墙支架固定不牢固")
        if clean_issues > 0:
            improvements.append(f"{clean_issues}个墙支架外观不整洁")
        
        return improvements
    
    def _generate_overall_analysis(self, pole_result: Dict, bracket_result: Dict) -> Dict:
        """生成总体分析"""
        return {
            'summary': f"架空线总体评分{pole_result['score'] + bracket_result['score']:.1f}分",
            'strengths': self._identify_strengths(pole_result, bracket_result),
            'weaknesses': self._identify_weaknesses(pole_result, bracket_result),
            'priority_actions': self._get_priority_actions(pole_result, bracket_result)
        }
    
    def _identify_strengths(self, pole_result: Dict, bracket_result: Dict) -> List[str]:
        """识别优势"""
        strengths = []
        
        if pole_result['level'] in ['excellent', 'good']:
            strengths.append("电杆塔间距设置合理")
        if bracket_result['level'] in ['excellent', 'good']:
            strengths.append("墙支架安装规范")
        
        return strengths
    
    def _identify_weaknesses(self, pole_result: Dict, bracket_result: Dict) -> List[str]:
        """识别不足"""
        weaknesses = []
        
        if pole_result['level'] in ['fair', 'poor']:
            weaknesses.append("电杆塔间距需要优化")
        if bracket_result['level'] in ['fair', 'poor']:
            weaknesses.append("墙支架安装需要改进")
        
        return weaknesses
    
    def _get_priority_actions(self, pole_result: Dict, bracket_result: Dict) -> List[str]:
        """获取优先行动"""
        actions = []
        
        # 根据评分确定优先级
        if pole_result['score'] < bracket_result['score']:
            actions.extend(pole_result['improvements'][:2])  # 取前2个建议
        else:
            actions.extend(bracket_result['improvements'][:2])
        
        return actions
    
    def _generate_recommendations(self, pole_result: Dict, bracket_result: Dict) -> List[str]:
        """生成总体建议"""
        recommendations = []
        
        total_score = pole_result['score'] + bracket_result['score']
        
        if total_score >= 16:
            recommendations.append("架空线布局优秀，继续保持")
        elif total_score >= 12:
            recommendations.append("架空线布局良好，可进行小幅优化")
        elif total_score >= 8:
            recommendations.append("架空线布局需要改进，建议重点优化")
        else:
            recommendations.append("架空线布局问题较多，需要全面整改")
        
        # 添加具体建议
        recommendations.extend(pole_result['improvements'][:1])
        recommendations.extend(bracket_result['improvements'][:1])
        
        return recommendations

    def _extract_overhead_devices(self, gis_data: Dict) -> Dict:
        """
        提取架空线相关设备
        
        Args:
            gis_data: GIS数据
            
        Returns:
            Dict: 分类后的设备数据
        """
        devices = gis_data.get('devices', [])
        
        overhead_devices = {
            'poles': [],
            'brackets': []
        }
        
        for device in devices:
            device_type = device.get('type', '').lower()
            
            if '电杆' in device_type or '杆塔' in device_type or 'pole' in device_type:
                overhead_devices['poles'].append(device)
            elif '墙支架' in device_type or 'bracket' in device_type:
                overhead_devices['brackets'].append(device)
        
        return overhead_devices
    
    def _calculate_pole_distances(self, pole_data: List) -> List[float]:
        """
        计算电杆塔间距
        
        Args:
            pole_data: 电杆塔数据
            
        Returns:
            List[float]: 间距列表
        """
        if len(pole_data) < 2:
            return []
        
        # 按坐标排序
        sorted_poles = sorted(pole_data, key=lambda x: (x.get('x', 0), x.get('y', 0)))
        
        distances = []
        for i in range(len(sorted_poles) - 1):
            pole1 = sorted_poles[i]
            pole2 = sorted_poles[i + 1]
            
            x1, y1 = pole1.get('x', 0), pole1.get('y', 0)
            x2, y2 = pole2.get('x', 0), pole2.get('y', 0)
            
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            distances.append(distance)
        
        return distances
    
    def _get_pole_tower_details(self, pole_data: List) -> Dict:
        """
        获取电杆塔评分详情
        
        Args:
            pole_data: 电杆塔数据
            
        Returns:
            Dict: 评分详情
        """
        distances = self._calculate_pole_distances(pole_data)
        
        return {
            'pole_count': len(pole_data),
            'distance_count': len(distances),
            'avg_distance': sum(distances) / len(distances) if distances else 0,
            'min_distance': min(distances) if distances else 0,
            'max_distance': max(distances) if distances else 0,
            'distances': distances
        }
    
    def _get_wall_bracket_details(self, bracket_data: List) -> Dict:
        """
        获取墙支架评分详情
        
        Args:
            bracket_data: 墙支架数据
            
        Returns:
            Dict: 评分详情
        """
        return {
            'bracket_count': len(bracket_data),
            'avg_height': sum(b.get('height', 0) for b in bracket_data) / len(bracket_data) if bracket_data else 0,
            'secure_count': sum(1 for b in bracket_data if b.get('secure', True)),
            'clean_count': sum(1 for b in bracket_data if b.get('clean', True))
        }


def evaluation_pipeline(treatment_result: Dict[str, Any]) -> float:
    """
    评分流水线
    
    Args:
        treatment_result: 治理结果数据
    
    Returns:
        float: 美观性评分 (0-100)
    """
    logger.info("执行评分流水线（placeholder）")
    
    # TODO: 实现具体的评分逻辑
    # 这里可能包括：
    # 1. 布局规整性评分
    # 2. 设备间距评分
    # 3. 视觉和谐性评分
    # 4. 可达性评分
    # 5. 综合评分计算
    
    # placeholder: 返回随机评分
    return 85.5


def calculate_beauty_score(original_data: GISData, treated_data: GISData) -> Dict[str, Any]:
    """
    计算美观性评分
    
    Args:
        original_data: 原始GIS数据
        treated_data: 治理后GIS数据
    
    Returns:
        Dict[str, Any]: 详细评分结果
    """
    logger.info("计算美观性评分（placeholder）")
    
    # TODO: 实现详细的评分算法
    
    return {
        'beauty_score': 85.5,
        'dimension_scores': {
            'layout': 88,
            'spacing': 85, 
            'harmony': 87,
            'accessibility': 82
        },
        'improvement_analysis': {
            'devices_moved': 3,
            'spacing_improved': True,
            'layout_optimized': True
        },
        'reasoning': '治理后设备布局更加整齐，间距更加合理，整体美观性得到显著提升。'
    }