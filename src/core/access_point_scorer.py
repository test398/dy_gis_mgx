from __future__ import annotations

from typing import Dict, Any, List, Tuple
import math

from src.core.base_scorer import BaseScorer


class AccessPointScorer(BaseScorer):
    """
    接入点评分器（20分）
    - 位置（12分）
    - 连接（8分）
    """

    FULL_SCORE_POS = 12.0
    FULL_SCORE_CONN = 8.0

    def score_access_points(self, gis_data: Dict[str, Any]) -> Dict[str, Any]:
        devices = gis_data.get('devices', []) or []
        roads = gis_data.get('roads', []) or []
        buildings = gis_data.get('buildings', []) or []

        points = self._extract_access_points(devices)
        cables = self._extract_cables(devices)

        pos_res = self._score_point_position(points, roads=roads, buildings=buildings)
        conn_res = self._score_point_connection(points, cables)

        total = float(pos_res['score']) + float(conn_res['score'])
        level = self._level_from_score(total, 20.0)
        basis = []
        basis.extend(pos_res.get('basis', []))
        basis.extend(conn_res.get('basis', []))

        return {
            'total_score': round(total, 2),
            'level': level,
            'basis': basis,
            'position_score': pos_res,
            'connection_score': conn_res
        }

    # ----------------- 细项 -----------------
    def _score_point_position(
        self,
        point_data: List[Dict[str, Any]],
        *,
        roads: List[Dict[str, Any]] | None = None,
        buildings: List[Dict[str, Any]] | None = None
    ) -> Dict[str, Any]:
        basis: List[str] = []
        if not point_data:
            basis.append('未检测到接入点')
            return {'score': 0.0, 'level': '较差', 'basis': basis}

        # 规则1：位于建筑内且靠近建筑外墙
        inside_or_near = 0.0
        for pt in point_data:
            p = (pt.get('x', 0.0), pt.get('y', 0.0))
            inside = False
            near_wall = False
            for b in buildings or []:
                poly = b.get('coords') or b.get('coors') or []
                if len(poly) >= 3:
                    inside = inside or self._point_in_polygon(p, [(pp[0], pp[1]) for pp in poly])
                    if self._distance_point_to_polygon_edge(p, poly) <= 20.0:
                        near_wall = True
            # 计数：在建筑内计1，靠近外墙额外+0.2
            inside_or_near += (1.0 if inside else 0.0) + (0.2 if near_wall else 0.0)
        ratio_inside = min(inside_or_near / max(len(point_data), 1), 1.0)
        if ratio_inside < 0.7:
            basis.append('接入点不在建筑内或未贴近外墙(比例不足70%)')

        # 规则2：接入点间的最小间距
        min_dist_violation = 0
        pts = [(p.get('x', 0.0), p.get('y', 0.0)) for p in point_data]
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                if self._distance(pts[i], pts[j]) < 15.0:
                    min_dist_violation += 1
        if min_dist_violation > 0:
            basis.append(f'接入点之间存在过近的布局(共{min_dist_violation}对<15像素)')

        score = self.FULL_SCORE_POS * (0.85 * ratio_inside + 0.15 * (1.0 / (1.0 + min_dist_violation)))
        level = self._level_from_score(score, self.FULL_SCORE_POS)
        return {'score': round(score, 2), 'level': level, 'basis': basis}

    def _score_point_connection(self, point_data: List[Dict[str, Any]], cables: List[Dict[str, Any]]) -> Dict[str, Any]:
        basis: List[str] = []
        if not point_data:
            basis.append('未检测到接入点，无法评估连接')
            return {'score': 0.0, 'level': '较差', 'basis': basis}
        if not cables:
            basis.append('未检测到电缆线路，连接关系未知')
            return {'score': 2.0, 'level': '较差', 'basis': basis}

        # 规则：接入点连接应为直线或正交折线
        ok_cnt = 0
        non_orth_cnt = 0
        for pt in point_data:
            p = (pt.get('x', 0.0), pt.get('y', 0.0))
            ok = False
            best_path_ok = True
            for seg in cables:
                pts = seg.get('points') or []
                if len(pts) >= 2:
                    d0 = self._distance(p, tuple(pts[0]))
                    d1 = self._distance(p, tuple(pts[-1]))
                    if d0 <= 15.0 or d1 <= 15.0:
                        ok = True
                        # 检查端点附近折线
                        if len(pts) >= 3:
                            a, b, c = pts[-3], pts[-2], pts[-1]
                            ang = self._angle(a, b, c)
                            if not (85 <= ang <= 95 or 170 <= ang <= 190):
                                best_path_ok = False
                        break
                    # 最近线段距离
                    for i in range(len(pts) - 1):
                        if self._distance_point_to_segment(p, tuple(pts[i]), tuple(pts[i + 1])) <= 10.0:
                            ok = True
                            break
                if ok:
                    break
            if ok:
                ok_cnt += 1
                if not best_path_ok:
                    non_orth_cnt += 1
        ratio = ok_cnt / max(len(point_data), 1)
        if ratio < 0.85:
            basis.append('接入点与电缆的连接/贴近比例不足85%')
        if non_orth_cnt > 0:
            basis.append(f'接入点连接处存在{non_orth_cnt}处非直线/非正交折线')

        score = self.FULL_SCORE_CONN * (ratio - min(non_orth_cnt * 0.05, 0.3))
        score = max(score, 0.0)
        level = self._level_from_score(score, self.FULL_SCORE_CONN)
        return {'score': round(score, 2), 'level': level, 'basis': basis}

    # ----------------- 提取器/工具 -----------------
    def _extract_access_points(self, devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取接入点设备
        
        根据设备类型和标签提取接入点设备
        """
        results = []
        for d in devices:
            t = str(d.get('type', '')).lower()
            label = (d.get('label') or d.get('name') or '').lower()
            if any(k in t for k in ['access', '接入点']) or any(k in label for k in ['接入', '接入点']):
                if len(d.get('points') or []) <= 1:
                    results.append(d)
        return results

    # 这些方法已移至基类