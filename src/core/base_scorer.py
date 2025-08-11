from __future__ import annotations

from typing import Dict, Any, List, Tuple
import math


class BaseScorer:
    """
    评分器基类，提供共享的几何计算和评分工具方法
    """

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
        best = float('inf')
        for i in range(len(line) - 1):
            d = self._distance_point_to_segment(p, tuple(line[i]), tuple(line[i + 1]))
            best = min(best, d)
        return best

    def _distance_point_to_polygon_edge(self, p: Tuple[float, float], poly: List[List[float]]) -> float:
        best = float('inf')
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
    def _point_in_polygon(p: Tuple[float, float], poly: List[Tuple[float, float]]) -> bool:
        """检查点是否在多边形内部
        
        使用射线法（Ray Casting Algorithm）判断点是否在多边形内部
        """
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

    # ------------------- 通用提取器 -------------------
    def _extract_cables(self, devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取电缆线路设备
        
        根据设备类型和标签提取电缆线路设备，要求点数大于等于2
        """
        results = []
        for d in devices:
            pts = d.get('points') or []
            t = str(d.get('type', '')).lower()
            label = (d.get('label') or d.get('name') or '').lower()
            if (any(k in t for k in ['cable', 'segment']) or any(k in label for k in ['电缆', '线路'])) and len(pts) >= 2:
                results.append(d)
        return results

    # ------------------- 聚类工具 -------------------
    def _count_clusters(self, points: List[Tuple[float, float]], radius: float = 30.0, min_size: int = 3) -> int:
        used = [False] * len(points)
        clusters = 0
        for i in range(len(points)):
            if used[i]:
                continue
            group = [i]
            for j in range(i + 1, len(points)):
                if self._distance(points[i], points[j]) <= radius:
                    group.append(j)
            if len(group) >= min_size:
                for idx in group:
                    used[idx] = True
                clusters += 1
        return clusters