from __future__ import annotations

from typing import Dict, Any, List, Tuple
import math


class MeterBoxScorer:
    """
    计量箱评分器（20分）
    - 位置（10分）
    - 协调性（10分）
    """

    FULL_SCORE_POS = 10.0
    FULL_SCORE_COO = 10.0

    def score_meter_boxes(self, gis_data: Dict[str, Any]) -> Dict[str, Any]:
        devices = gis_data.get('devices', []) or []
        roads = gis_data.get('roads', []) or []
        buildings = gis_data.get('buildings', []) or []

        meters = self._extract_meters(devices)
        access_points = [d for d in devices if (str(d.get('type', '')).lower().find('access') >= 0 or (d.get('label') or '').find('接入点') >= 0)]

        pos_res = self._score_meter_position(meters, roads=roads, buildings=buildings, access_points=access_points)
        coo_res = self._score_meter_coordination(meters, access_points=access_points)

        total = float(pos_res['score']) + float(coo_res['score'])
        level = self._level_from_score(total, 20.0)
        basis = []
        basis.extend(pos_res.get('basis', []))
        basis.extend(coo_res.get('basis', []))

        return {
            'total_score': round(total, 2),
            'level': level,
            'basis': basis,
            'position_score': pos_res,
            'coordination_score': coo_res
        }

    # ----------------- 细项 -----------------
    def _score_meter_position(
        self,
        meter_data: List[Dict[str, Any]],
        *,
        roads: List[Dict[str, Any]] | None = None,
        buildings: List[Dict[str, Any]] | None = None,
        access_points: List[Dict[str, Any]] | None = None
    ) -> Dict[str, Any]:
        basis: List[str] = []
        if not meter_data:
            basis.append('未检测到计量箱')
            return {'score': 0.0, 'level': '较差', 'basis': basis}

        # 规则1：靠近建筑墙面或道路边
        near_cnt = 0
        for m in meter_data:
            p = (m.get('x', 0.0), m.get('y', 0.0))
            ok = False
            if buildings:
                for b in buildings:
                    poly = b.get('coords') or b.get('coors') or []
                    if len(poly) >= 3 and self._distance_point_to_polygon_edge(p, poly) <= 20.0:
                        ok = True
                        break
            if not ok and roads:
                for r in roads:
                    line = r.get('coords') or r.get('coors') or []
                    if len(line) >= 2 and self._distance_point_to_polyline(p, line) <= 20.0:
                        ok = True
                        break
            if ok:
                near_cnt += 1
        ratio_near = near_cnt / max(len(meter_data), 1)
        if ratio_near < 0.7:
            basis.append('计量箱未充分靠近墙面/道路(比例<70%)')

        # 规则2：与接入点的距离（<=10m近似阈值，像素阈值取20像素可调整）
        if access_points:
            far_cnt = 0
            for m in meter_data:
                mp = (m.get('x', 0.0), m.get('y', 0.0))
                dmin = min((self._distance(mp, (a.get('x', 0.0), a.get('y', 0.0))) for a in access_points), default=1e9)
                if dmin > 20.0:
                    far_cnt += 1
            if far_cnt > 0:
                basis.append(f'有{far_cnt}个计量箱距离最近接入点超过阈值(>20像素)')

        score = self.FULL_SCORE_POS * (0.8 * ratio_near + 0.2 * (1.0 / (1.0 + (far_cnt if access_points else 0))))
        level = self._level_from_score(score, self.FULL_SCORE_POS)
        return {'score': round(score, 2), 'level': level, 'basis': basis}

    def _score_meter_coordination(self, meter_data: List[Dict[str, Any]], *, access_points: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
        basis: List[str] = []
        if not meter_data:
            basis.append('未检测到计量箱，无法评估协调性')
            return {'score': 0.0, 'level': '较差', 'basis': basis}

        # 规则：成排对齐、间距均匀；与接入点无冲突遮挡
        pts = [(m.get('x', 0.0), m.get('y', 0.0)) for m in meter_data]
        if len(pts) < 2:
            return {'score': self.FULL_SCORE_COO, 'level': '优秀', 'basis': basis}

        # 判断主排列方向
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        var_x = self._variance(xs)
        var_y = self._variance(ys)
        horizontal = var_y < var_x

        # 对齐与间距
        if horizontal:
            mean_y = sum(ys) / len(ys)
            align_err = sum(abs(y - mean_y) for y in ys) / len(ys)
            sorted_pts = sorted(pts, key=lambda v: v[0])
            gaps = [sorted_pts[i + 1][0] - sorted_pts[i][0] for i in range(len(sorted_pts) - 1)]
        else:
            mean_x = sum(xs) / len(xs)
            align_err = sum(abs(x - mean_x) for x in xs) / len(xs)
            sorted_pts = sorted(pts, key=lambda v: v[1])
            gaps = [sorted_pts[i + 1][1] - sorted_pts[i][1] for i in range(len(sorted_pts) - 1)]

        gap_var = self._variance(gaps) if gaps else 0.0
        if align_err > 10.0:
            basis.append(f'计量箱排布不整齐(平均偏离≈{align_err:.1f}像素)')
        if gap_var > 50.0:
            basis.append('计量箱间距差异较大')

        # 与接入点冲突（同一位置重叠近似判断）
        conflict_cnt = 0
        if access_points:
            ap_pts = [(a.get('x', 0.0), a.get('y', 0.0)) for a in access_points]
            for p in pts:
                for ap in ap_pts:
                    if self._distance(p, ap) < 8.0:
                        conflict_cnt += 1
                        break
        if conflict_cnt > 0:
            basis.append(f'计量箱与接入点存在{conflict_cnt}处空间冲突/遮挡(<8像素)')

        # 计分：从满分扣分
        score = self.FULL_SCORE_COO
        score -= min(max(align_err - 5.0, 0.0) * 0.2, 5.0)
        score -= min(gap_var * 0.02, 5.0)
        score -= min(conflict_cnt * 1.0, 5.0)
        score = max(score, 0.0)
        level = self._level_from_score(score, self.FULL_SCORE_COO)
        return {'score': round(score, 2), 'level': level, 'basis': basis}

    # ----------------- 提取器/工具 -----------------
    def _extract_meters(self, devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for d in devices:
            t = str(d.get('type', '')).lower()
            label = (d.get('label') or d.get('name') or '').lower()
            if any(k in t for k in ['meter']) or any(k in label for k in ['计量箱', '电表箱']):
                if len(d.get('points') or []) <= 1:
                    results.append(d)
        return results

    @staticmethod
    def _variance(vals: List[float]) -> float:
        if not vals:
            return 0.0
        mean = sum(vals) / len(vals)
        return sum((v - mean) ** 2 for v in vals) / len(vals)

    @staticmethod
    def _distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

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
        best = 1e9
        for i in range(len(line) - 1):
            d = self._distance_point_to_segment(p, tuple(line[i]), tuple(line[i + 1]))
            best = min(best, d)
        return best

    def _distance_point_to_polygon_edge(self, p: Tuple[float, float], poly: List[List[float]]) -> float:
        best = 1e9
        for i in range(len(poly)):
            a = tuple(poly[i])
            b = tuple(poly[(i + 1) % len(poly)])
            d = self._distance_point_to_segment(p, a, b)
            best = min(best, d)
        return best

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