from __future__ import annotations

from typing import Dict, Any, List, Tuple
import math


class CableLineScorer:
    """
    低压电缆线路评分器（20分）
    - 电缆头（8分）
    - 电缆段（12分）
    
    返回JSON包含: total_score, level, basis(list), sub-scores
    """

    FULL_SCORE_HEAD = 8.0
    FULL_SCORE_SEG = 12.0

    def score_cable_lines(self, gis_data: Dict[str, Any]) -> Dict[str, Any]:
        devices = gis_data.get('devices', []) or []
        buildings = gis_data.get('buildings', []) or []
        roads = gis_data.get('roads', []) or []
        rivers = gis_data.get('rivers', []) or []

        cable_segments = self._extract_cable_segments(devices)
        cable_heads = self._extract_cable_heads(devices)

        seg_res = self._score_cable_segment(cable_segments, rivers=rivers, buildings=buildings, devices=devices)
        head_res = self._score_cable_head(cable_heads, cable_segments, roads=roads, buildings=buildings)

        total = float(seg_res['score']) + float(head_res['score'])
        level = self._level_from_score(total, 20.0)
        basis = []
        basis.extend(head_res.get('basis', []))
        basis.extend(seg_res.get('basis', []))

        return {
            'total_score': round(total, 2),
            'level': level,
            'basis': basis,
            'head_score': head_res,
            'segment_score': seg_res
        }

    # ------------------- 细项评分 -------------------
    def _score_cable_head(
        self,
        cable_head_data: List[Dict[str, Any]],
        cable_segments: List[Dict[str, Any]],
        roads: List[Dict[str, Any]] | None = None,
        buildings: List[Dict[str, Any]] | None = None
    ) -> Dict[str, Any]:
        basis: List[str] = []
        if not cable_head_data:
            basis.append('未检测到电缆头设备')
            return {'score': 0.0, 'level': '较差', 'basis': basis}

        # 规则1：电缆头应靠近站房/建筑出线点（近似为建筑边缘）或电缆段端点
        matched = 0
        distances: List[float] = []
        for head in cable_head_data:
            hx, hy = head.get('x', 0.0), head.get('y', 0.0)
            dmin = math.inf
            for seg in cable_segments:
                pts = seg.get('points') or []
                if len(pts) >= 2:
                    d1 = self._distance((hx, hy), tuple(pts[0]))
                    d2 = self._distance((hx, hy), tuple(pts[-1]))
                    dmin = min(dmin, d1, d2)
            if dmin < math.inf:
                distances.append(dmin)
                if dmin <= 20.0:
                    matched += 1
            # 贴近建筑外立面
            if buildings:
                for b in buildings:
                    poly = b.get('coords') or b.get('coors') or b.get('points') or []
                    if len(poly) >= 3 and self._distance_point_to_polygon_edge((hx, hy), poly) <= 20.0:
                        matched += 0.2  # 小幅加分权重
                        break
        if matched < len(cable_head_data):
            basis.append(f"有{max(0, len(cable_head_data) - int(matched))}个电缆头未靠近电缆端点/建筑出线点(>20像素)")
        if distances:
            mean_d = sum(distances) / len(distances)
            if mean_d > 20:
                basis.append(f"电缆头整体与端点平均距离偏大(均值≈{mean_d:.1f})")

        # 计分
        endpoint_ratio = min(matched / max(len(cable_head_data), 1), 1.0)
        score = self.FULL_SCORE_HEAD * endpoint_ratio
        level = self._level_from_score(score, self.FULL_SCORE_HEAD)
        return {'score': round(score, 2), 'level': level, 'basis': basis}

    def _score_cable_segment(
        self,
        cable_data: List[Dict[str, Any]],
        *,
        rivers: List[Dict[str, Any]] | None = None,
        buildings: List[Dict[str, Any]] | None = None,
        devices: List[Dict[str, Any]] | None = None
    ) -> Dict[str, Any]:
        basis: List[str] = []
        if not cable_data:
            basis.append('未检测到电缆段')
            return {'score': 0.0, 'level': '较差', 'basis': basis}

        # 拼装所有线段
        segments: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []
        for seg in cable_data:
            pts = seg.get('points') or []
            if len(pts) >= 2:
                for i in range(len(pts) - 1):
                    segments.append((tuple(pts[i]), tuple(pts[i + 1])))

        # 规则1：线段相交
        crossings = 0
        for i in range(len(segments)):
            for j in range(i + 1, len(segments)):
                if self._segments_intersect(segments[i][0], segments[i][1], segments[j][0], segments[j][1]):
                    crossings += 1
        if crossings > 0:
            basis.append(f"检测到{crossings}处电缆段交叉")

        # 规则2：避免穿越河流/建筑/站房设备
        river_cross_cnt = 0
        if rivers:
            polys = [r.get('coords') or r.get('coors') or [] for r in rivers]
            polys = [p for p in polys if len(p) >= 3]
            for (a, b) in segments:
                for poly in polys:
                    if self._segment_intersects_polygon(a, b, poly):
                        river_cross_cnt += 1
                        break
        if river_cross_cnt > 0:
            basis.append(f"有{river_cross_cnt}段电缆穿越河流区域")

        building_cross_cnt = 0
        if buildings:
            polys_b = [b.get('coords') or b.get('coors') or b.get('points') or [] for b in buildings]
            polys_b = [p for p in polys_b if len(p) >= 3]
            for (a, b) in segments:
                for poly in polys_b:
                    if self._segment_intersects_polygon(a, b, poly):
                        building_cross_cnt += 1
                        break
        if building_cross_cnt > 0:
            basis.append(f"有{building_cross_cnt}段电缆穿越建筑/站房设备区域")

        # 规则3：横平竖直/正交折线（检测折角是否接近90度或180度）
        non_orth_cnt = 0
        for seg in cable_data:
            pts = seg.get('points') or []
            for i in range(1, len(pts) - 1):
                ang = self._angle(pts[i - 1], pts[i], pts[i + 1])
                # 接近直线或正交：角度在[170, 190]或[85, 95]
                if not (85 <= ang <= 95 or 170 <= ang <= 190):
                    non_orth_cnt += 1
        if non_orth_cnt > 0:
            basis.append(f"存在{non_orth_cnt}处非直线/非正交折线")

        # 计分：从满分扣分
        score = self.FULL_SCORE_SEG
        score -= min(crossings * 2.0, 6.0)
        score -= min(river_cross_cnt * 1.5, 3.0)
        score -= min(building_cross_cnt * 2.0, 4.0)
        score -= min(non_orth_cnt * 0.5, 3.0)
        score = max(score, 0.0)
        level = self._level_from_score(score, self.FULL_SCORE_SEG)
        return {'score': round(score, 2), 'level': level, 'basis': basis}

    # ------------------- 提取器 -------------------
    def _extract_cable_segments(self, devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for d in devices:
            t = str(d.get('type', '')).lower()
            label = (d.get('label') or d.get('name') or '').lower()
            pts = d.get('points') or []
            if ((any(k in t for k in ['cable', 'segment']) or any(k in label for k in ['电缆', '线路'])) and len(pts) >= 2):
                results.append(d)
        return results

    def _extract_cable_heads(self, devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for d in devices:
            t = str(d.get('type', '')).lower()
            label = (d.get('label') or d.get('name') or '').lower()
            if any(k in t for k in ['head']) or any(k in label for k in ['电缆头']):
                results.append(d)
        return results

    # ------------------- 几何工具 -------------------
    @staticmethod
    def _distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    @staticmethod
    def _cross(o: Tuple[float, float], a: Tuple[float, float], b: Tuple[float, float]) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def _segments_intersect(self, p1: Tuple[float, float], p2: Tuple[float, float], q1: Tuple[float, float], q2: Tuple[float, float]) -> bool:
        def on_seg(a, b, c):
            return min(a[0], b[0]) - 1e-6 <= c[0] <= max(a[0], b[0]) + 1e-6 and \
                   min(a[1], b[1]) - 1e-6 <= c[1] <= max(a[1], b[1]) + 1e-6

        d1 = self._cross(p1, p2, q1)
        d2 = self._cross(p1, p2, q2)
        d3 = self._cross(q1, q2, p1)
        d4 = self._cross(q1, q2, p2)
        if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
            return True
        if abs(d1) < 1e-6 and on_seg(p1, p2, q1):
            return True
        if abs(d2) < 1e-6 and on_seg(p1, p2, q2):
            return True
        if abs(d3) < 1e-6 and on_seg(q1, q2, p1):
            return True
        if abs(d4) < 1e-6 and on_seg(q1, q2, p2):
            return True
        return False

    def _distance_point_to_segment(self, p: Tuple[float, float], a: Tuple[float, float], b: Tuple[float, float]) -> float:
        ax, ay = a
        bx, by = b
        px, py = p
        abx, aby = bx - ax, by - ay
        apx, apy = px - ax, py - ay
        denom = abx * abx + aby * aby
        if denom == 0:
            return self._distance(p, a)
        t = max(0.0, min(1.0, (apx * abx + apy * aby) / denom))
        cx, cy = ax + t * abx, ay + t * aby
        return self._distance(p, (cx, cy))

    def _distance_point_to_polyline(self, p: Tuple[float, float], line: List[List[float]]) -> float:
        best = math.inf
        for i in range(len(line) - 1):
            d = self._distance_point_to_segment(p, tuple(line[i]), tuple(line[i + 1]))
            best = min(best, d)
        return best

    def _distance_point_to_polygon_edge(self, p: Tuple[float, float], poly: List[List[float]]) -> float:
        best = math.inf
        for i in range(len(poly)):
            a = tuple(poly[i])
            b = tuple(poly[(i + 1) % len(poly)])
            d = self._distance_point_to_segment(p, a, b)
            best = min(best, d)
        return best

    def _segment_intersects_polygon(self, a: Tuple[float, float], b: Tuple[float, float], poly: List[List[float]]) -> bool:
        for i in range(len(poly)):
            c = tuple(poly[i])
            d = tuple(poly[(i + 1) % len(poly)])
            if self._segments_intersect(a, b, c, d):
                return True
        return False

    @staticmethod
    def _angle(a: List[float], b: List[float], c: List[float]) -> float:
        bax = a[0] - b[0]
        bay = a[1] - b[1]
        bcx = c[0] - b[0]
        bcy = c[1] - b[1]
        dot = bax * bcx + bay * bcy
        na = math.hypot(bax, bay)
        nb = math.hypot(bcx, bcy)
        if na * nb == 0:
            return 180.0
        cosv = max(-1.0, min(1.0, dot / (na * nb)))
        return math.degrees(math.acos(cosv))

    @staticmethod
    def _level_from_score(score: float, full: float) -> str:
        ratio = score / max(full, 1e-6)
        if ratio >= 0.95:
            return '优秀'
        if ratio >= 0.75:
            return '良好'
        if ratio >= 0.5:
            return '一般'
        return '较差' 