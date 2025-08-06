"""
架空线评分器

专门用于评估架空线路的美观性和规范性
支持可配置的评分标准和详细的评分分析
支持标注数据格式和GIS数据格式
"""

from typing import Dict, List

class OverheadLineScorer:
    """
    阶段1：架空线路部分评分器
    只实现电杆塔和墙支架的评分
    """
    def score_overhead_lines(self, gis_data: Dict) -> Dict:
        """
        对输入的GIS数据进行架空线路评分，只考虑电杆塔和墙支架。
        Args:
            gis_data: 包含'devices'字段的字典，每个device需有'type'字段。
        Returns:
            Dict: 包含总分、分项分、数量和评分依据的结果。
        """
        pole_data = [d for d in gis_data.get('devices', []) if d.get('type') in ['电杆', '杆塔', 'pole']]
        bracket_data = [d for d in gis_data.get('devices', []) if d.get('type') in ['墙支架', '墙担', 'bracket']]
        pole_score = self._score_pole_tower_span(pole_data)
        bracket_score = self._score_wall_bracket(bracket_data)
        total_score = pole_score + bracket_score
        return {
            "total_score": total_score,
            "pole_score": pole_score,
            "bracket_score": bracket_score,
            "details": {
                "pole_count": len(pole_data),
                "bracket_count": len(bracket_data),
                "pole_score_basis": "杆塔数量和间距评分（示例）",
                "bracket_score_basis": "墙支架数量评分（示例）"
            }
        }
    
    def _score_pole_tower_span(self, pole_data: List) -> Dict:
        """
        严格按照附件2标准细化电杆塔与档距段评分（12分），返回详细评分依据。
        """
        if len(pole_data) < 2:
            return {
                "score": 0.0,
                "level": "较差",
                "basis": "杆塔数量不足，无法形成档距段。"
            }

        coords = [(p.get('x', 0), p.get('y', 0)) for p in pole_data]
        # 顺序合理性检查
        is_ordered_reasonable = self._check_pole_order_reasonable(coords)
        coords = self._sort_poles_by_nearest_neighbor(coords)
        has_overlap = len(coords) != len(set(coords))
        xs = [c[0] for c in coords]
        is_ordered = all(xs[i] <= xs[i+1] for i in range(len(xs)-1))

        # 检查档距段交叉
        def segments_cross(a, b, c, d):
            def ccw(p1, p2, p3):
                return (p3[1]-p1[1])*(p2[0]-p1[0]) > (p2[1]-p1[1])*(p3[0]-p1[0])
            return (ccw(a, c, d) != ccw(b, c, d)) and (ccw(a, b, c) != ccw(a, b, d))
        has_cross = False
        for i in range(len(coords)-1):
            for j in range(i+2, len(coords)-1):
                if segments_cross(coords[i], coords[i+1], coords[j], coords[j+1]):
                    has_cross = True
                    break

        # 检查导线反折
        is_reverse = False
        for i in range(1, len(xs)-1):
            if (xs[i] - xs[i-1]) * (xs[i+1] - xs[i]) < 0:
                is_reverse = True
                break

        # 评分与依据
        basis = []
        if not is_ordered_reasonable:
            basis.append("杆塔顺序与空间布局不符，顺序不合理")
        if has_overlap:
            basis.append("存在杆塔重叠")
        if not is_ordered:
            basis.append("杆塔顺序不合理")
        if has_cross:
            basis.append("档距段存在交叉")
        if is_reverse:
            basis.append("导线存在反折")
        if not basis:
            score = 12.0
            level = "优秀"
            basis.append("杆塔顺道路沿布，无重叠，顺序合理，档距段无交叉，导线无反折，完全符合标准")
        elif len(basis) == 1:
            score = 9.0
            level = "良好"
        elif len(basis) == 2:
            score = 7.0
            level = "一般"
        else:
            score = 4.0
            level = "较差"
        return {
            "score": score,
            "level": level,
            "basis": basis
        }

    def _check_pole_order_reasonable(self, coords: List[tuple]) -> bool:
        """
        判断原始杆塔顺序是否与空间最近邻顺序基本一致。
        允许1个错位。
        """
        if len(coords) < 2:
            return True
        sorted_coords = self._sort_poles_by_nearest_neighbor(coords)
        match_count = sum(1 for a, b in zip(coords, sorted_coords) if a == b)
        return match_count >= len(coords) - 1  # 允许1个错位

    def _score_wall_bracket(self, bracket_data: List) -> Dict:
        """
        严格按照附件2标准细化墙支架评分（8分），返回详细评分依据。
        """
        if not bracket_data:
            return {
                "score": 0.0,
                "level": "较差",
                "basis": "无墙支架数据。"
            }

        # 假设每个支架有x/y和楼栋x/y（如有），否则只按顺序和分布判断
        coords = [(b.get('x', 0), b.get('y', 0)) for b in bracket_data]
        is_ordered = all(coords[i][0] <= coords[i+1][0] for i in range(len(coords)-1))
        # 检查是否都在“正面”——这里假设y值接近某一常数为正面（如有楼栋y坐标可更精确）
        y_vals = [c[1] for c in coords]
        y_mean = sum(y_vals) / len(y_vals)
        deviation = [abs(y - y_mean) for y in y_vals]
        max_dev = max(deviation) if deviation else 0
        # 设定阈值，偏离正面则为脱离
        threshold = 10  # 可根据实际数据调整
        has_off_front = max_dev > threshold
        # 检查顺序混乱
        is_messy = not is_ordered

        # 评分与依据
        basis = []
        if has_off_front:
            basis.append("存在支架脱离楼栋正面布置")
        if is_messy:
            basis.append("支架顺序混乱")
        if not basis:
            score = 8.0
            level = "优秀"
            basis.append("墙支架沿楼栋顺序布置，位置准确且位于楼栋正面，无脱离楼栋放置，完全符合治理标准")
        elif len(basis) == 1:
            score = 6.0
            level = "良好"
        else:
            score = 3.0
            level = "较差"
        return {
            "score": score,
            "level": level,
            "basis": basis
        } 

    def _sort_poles_by_nearest_neighbor(self, coords: List[tuple]) -> List[tuple]:
        if not coords:
            return []
        unvisited = set(coords)
        path = []
        current = coords[0]
        path.append(current)
        unvisited.remove(current)
        while unvisited:
            next_pole = min(unvisited, key=lambda p: (current[0]-p[0])**2 + (current[1]-p[1])**2)
            path.append(next_pole)
            unvisited.remove(next_pole)
            current = next_pole
        return path 