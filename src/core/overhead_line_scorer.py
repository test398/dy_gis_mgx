"""
架空线评分器

专门用于评估架空线路的美观性和规范性
支持可配置的评分标准和详细的评分分析
支持标注数据格式和GIS数据格式
"""

from typing import Dict, List, Tuple


class OverheadLineScorer:
    """
    阶段1：架空线路部分评分器（总分20分）
    - 杆塔/档距段（12分）
    - 墙支架（8分）
    """

    FULL_SCORE_POLE = 12.0
    FULL_SCORE_BRACKET = 8.0

    def score_overhead_lines(self, gis_data: Dict) -> Dict:
        """
        对输入的GIS数据进行架空线路评分，只考虑电杆塔和墙支架。
        Args:
            gis_data: 包含'devices'字段的字典，每个device需有'type'字段。
        Returns:
            Dict: 包含总分、分项分、数量和评分依据的结果。
        """
        devices = gis_data.get('devices', []) or []
        pole_data = [d for d in devices if d.get('type') in ['电杆', '杆塔', 'pole']]
        bracket_data = [d for d in devices if d.get('type') in ['墙支架', '墙担', 'bracket']]

        pole_res = self._score_pole_tower_span(pole_data)
        bracket_res = self._score_wall_bracket(bracket_data)

        total = float(pole_res.get('score', 0.0)) + float(bracket_res.get('score', 0.0))
        result = {
            'total_score': round(total, 2),
            'level': self._level_from_20(total),
            'basis': [
                *([b for b in (pole_res.get('basis') or [])]),
                *([b for b in (bracket_res.get('basis') or [])])
            ],
            'details': {
                'pole_count': len(pole_data),
                'bracket_count': len(bracket_data)
            },
            'pole_score': pole_res,
            'bracket_score': bracket_res,
        }

        # 兼容需求：提供墙支架分析字段（包含 position / level_name / recommendations）
        bracket_position = 'front' if not any('脱离楼栋正面' in s for s in (bracket_res.get('basis') or [])) else 'off_front'
        result['bracket_analysis'] = {
            'position': bracket_position,
            'level_name': bracket_res.get('level', ''),
            'recommendations': self._build_bracket_recommendations(bracket_res)
        }
        return result

    # ----------------------- 杆塔与档距段（12分） -----------------------
    def _score_pole_tower_span(self, pole_data: List[Dict]) -> Dict:
        """
        严格按照附件2标准细化电杆塔与档距段评分（12分），返回详细评分依据。
        """
        if len(pole_data) < 2:
            return {
                'score': 0.0,
                'level': '较差',
                'basis': ['杆塔数量不足，无法形成档距段。']
            }

        coords = [(p.get('x', 0), p.get('y', 0)) for p in pole_data]
        # 顺序合理性检查
        is_ordered_reasonable = self._check_pole_order_reasonable(coords)
        coords_sorted = self._sort_poles_by_nearest_neighbor(coords)
        has_overlap = len(coords_sorted) != len(set(coords_sorted))
        xs = [c[0] for c in coords_sorted]
        is_monotonic = all(xs[i] <= xs[i + 1] for i in range(len(xs) - 1))

        # 检查档距段交叉
        def segments_cross(a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float], d: Tuple[float, float]) -> bool:
            def ccw(p1, p2, p3):
                return (p3[1] - p1[1]) * (p2[0] - p1[0]) > (p2[1] - p1[1]) * (p3[0] - p1[0])
            return (ccw(a, c, d) != ccw(b, c, d)) and (ccw(a, b, c) != ccw(a, b, d))

        has_cross = False
        for i in range(len(coords_sorted) - 1):
            for j in range(i + 2, len(coords_sorted) - 1):
                if segments_cross(coords_sorted[i], coords_sorted[i + 1], coords_sorted[j], coords_sorted[j + 1]):
                    has_cross = True
                    break
            if has_cross:
                break

        # 检查导线反折
        is_reverse = False
        for i in range(1, len(xs) - 1):
            if (xs[i] - xs[i - 1]) * (xs[i + 1] - xs[i]) < 0:
                is_reverse = True
                break

        # 评分与依据
        basis = []
        if not is_ordered_reasonable:
            basis.append('杆塔顺序与空间布局不符，顺序不合理')
        if has_overlap:
            basis.append('存在杆塔重叠')
        if not is_monotonic:
            basis.append('杆塔顺序不合理')
        if has_cross:
            basis.append('档距段存在交叉')
        if is_reverse:
            basis.append('导线存在反折')

        if not basis:
            score = self.FULL_SCORE_POLE
            level = '优秀'
            basis.append('杆塔顺道路沿布，无重叠，顺序合理，档距段无交叉，导线无反折，完全符合标准')
        elif len(basis) == 1:
            score = 9.0
            level = '良好'
        elif len(basis) == 2:
            score = 7.0
            level = '一般'
        else:
            score = 4.0
            level = '较差'
        
        return {
            'score': score,
            'level': level,
            'basis': basis
        }

    def _check_pole_order_reasonable(self, coords: List[Tuple[float, float]]) -> bool:
        """
        判断原始杆塔顺序是否与空间最近邻顺序基本一致。允许1个错位。
        """
        if len(coords) < 2:
            return True
        sorted_coords = self._sort_poles_by_nearest_neighbor(coords)
        match_count = sum(1 for a, b in zip(coords, sorted_coords) if a == b)
        return match_count >= len(coords) - 1  # 允许1个错位

    def _sort_poles_by_nearest_neighbor(self, coords: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        if not coords:
            return []
        unvisited = set(coords)
        path = []
        current = coords[0]
        path.append(current)
        unvisited.remove(current)
        while unvisited:
            next_pole = min(unvisited, key=lambda p: (current[0] - p[0]) ** 2 + (current[1] - p[1]) ** 2)
            path.append(next_pole)
            unvisited.remove(next_pole)
            current = next_pole
        return path

    # ----------------------- 墙支架（8分） -----------------------
    def _score_wall_bracket(self, bracket_data: List[Dict]) -> Dict:
        """
        严格按照附件2标准细化墙支架评分（8分），返回详细评分依据。
        """
        if not bracket_data:
            return {
                'score': 0.0,
                'level': '较差',
                'basis': ['无墙支架数据。']
            }

        coords = [(b.get('x', 0), b.get('y', 0)) for b in bracket_data]
        is_ordered = all(coords[i][0] <= coords[i + 1][0] for i in range(len(coords) - 1))
        y_vals = [c[1] for c in coords]
        y_mean = sum(y_vals) / len(y_vals)
        deviation = [abs(y - y_mean) for y in y_vals]
        max_dev = max(deviation) if deviation else 0
        threshold = 10  # 偏离阈值，可按实际数据调优
        has_off_front = max_dev > threshold

        basis = []
        if has_off_front:
            basis.append('存在支架脱离楼栋正面布置')
        if not is_ordered:
            basis.append('支架顺序混乱')

        if not basis:
            score = self.FULL_SCORE_BRACKET
            level = '优秀'
            basis.append('墙支架沿楼栋顺序布置，位置准确且位于楼栋正面，无脱离楼栋放置，完全符合治理标准')
        elif len(basis) == 1:
            score = 6.0
            level = '良好'
        else:
            score = 3.0
            level = '较差'
        
        return {
            'score': score,
            'level': level,
            'basis': basis
        }

    @staticmethod
    def _level_from_20(score: float) -> str:
        if score >= 19:
            return '优秀'
        if score >= 15:
            return '良好'
        if score >= 10:
            return '一般'
        return '较差'

    def _build_bracket_recommendations(self, bracket_res: Dict) -> List[str]:
        basis_list = bracket_res.get('basis') or []
        recs: List[str] = []
        for item in basis_list:
            if '脱离楼栋正面' in item:
                recs.append('将墙支架调整至楼栋正面统一布置，保持与门窗边线平行')
            if '顺序混乱' in item or '顺序' in item:
                recs.append('按沿街方向由左至右重新编号与布置，保持等间距对齐')
        if not recs and bracket_res.get('level') == '优秀':
            recs.append('保持现状，定期巡检与维护')
        return recs 