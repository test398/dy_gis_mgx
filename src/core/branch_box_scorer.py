from __future__ import annotations

from typing import Dict, Any, List, Tuple
import math

from src.core.base_scorer import BaseScorer


class BranchBoxScorer(BaseScorer):
    """
    分支箱评分器（20分）
    - 位置（12分）
    - 连接（8分）
    """

    FULL_SCORE_POS = 12.0
    FULL_SCORE_CONN = 8.0

    def score_branch_boxes(self, gis_data: Dict[str, Any]) -> Dict[str, Any]:
        devices = gis_data.get('devices', []) or []
        roads = gis_data.get('roads', []) or []
        buildings = gis_data.get('buildings', []) or []

        boxes = self._extract_boxes(devices)
        cables = self._extract_cables(devices)

        pos_res = self._score_box_position(boxes, roads=roads, buildings=buildings)
        conn_res = self._score_box_connection(boxes, cables)

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
    def _score_box_position(
        self,
        box_data: List[Dict[str, Any]],
        *,
        roads: List[Dict[str, Any]] | None = None,
        buildings: List[Dict[str, Any]] | None = None
    ) -> Dict[str, Any]:
        basis: List[str] = []
        if not box_data:
            basis.append('未检测到分支箱')
            return {'score': 0.0, 'level': '较差', 'basis': basis}

        # 规则1：靠近道路边或建筑外立面
        near_cnt = 0
        for box in box_data:
            p = (box.get('x', 0.0), box.get('y', 0.0))
            ok = False
            if roads:
                for r in roads:
                    line = r.get('coords') or r.get('coors') or []
                    if len(line) >= 2 and self._distance_point_to_polyline(p, line) <= 25.0:
                        ok = True
                        break
            if not ok and buildings:
                for b in buildings:
                    poly = b.get('coords') or b.get('coors') or []
                    if len(poly) >= 3 and self._distance_point_to_polygon_edge(p, poly) <= 25.0:
                        ok = True
                        break
            if ok:
                near_cnt += 1
        ratio = near_cnt / max(len(box_data), 1)
        if ratio < 0.6:
            basis.append('分支箱未充分靠近道路或建筑外立面(比例<60%)')

        # 规则2：分支箱彼此间距适中(避免聚簇)
        cluster_cnt = self._count_clusters([(b.get('x', 0.0), b.get('y', 0.0)) for b in box_data], radius=30.0, min_size=3)
        if cluster_cnt > 0:
            basis.append(f'存在{cluster_cnt}处分支箱聚簇(半径30像素,>=3)')

        # 规则3：避免占用主要通道（近似：距离道路中心线过近且处于路肩内侧）
        occupy_cnt = 0
        for box in box_data:
            p = (box.get('x', 0.0), box.get('y', 0.0))
            too_close = False
            for r in roads or []:
                line = r.get('coords') or r.get('coors') or []
                if len(line) >= 2 and self._distance_point_to_polyline(p, line) < 10.0:
                    too_close = True
                    break
            if too_close:
                occupy_cnt += 1
        if occupy_cnt > 0:
            basis.append(f'有{occupy_cnt}处分支箱疑似占用通道(与道路中心线<10像素)')

        score = self.FULL_SCORE_POS * (0.7 * ratio + 0.2 * (1.0 / (1.0 + cluster_cnt)) + 0.1 * (1.0 / (1.0 + occupy_cnt)))
        level = self._level_from_score(score, self.FULL_SCORE_POS)
        return {'score': round(score, 2), 'level': level, 'basis': basis}

    def _score_box_connection(self, box_data: List[Dict[str, Any]], cables: List[Dict[str, Any]]) -> Dict[str, Any]:
        basis: List[str] = []
        if not box_data:
            basis.append('未检测到分支箱，无法评估连接')
            return {'score': 0.0, 'level': '较差', 'basis': basis}

        if not cables:
            basis.append('未检测到电缆线路，连接关系未知')
            return {'score': 2.0, 'level': '较差', 'basis': basis}

        # 规则：每个分支箱应有至少一条电缆段端点连接，且路径尽量直线或正交折线
        ok_cnt = 0
        non_orth_cnt = 0
        for box in box_data:
            bx, by = box.get('x', 0.0), box.get('y', 0.0)
            linked = False
            best_path_ok = True
            for seg in cables:
                pts = seg.get('points') or []
                if len(pts) >= 2:
                    if self._distance((bx, by), tuple(pts[0])) <= 20.0 or self._distance((bx, by), tuple(pts[-1])) <= 20.0:
                        linked = True
                        # 检测端点附近折线是否正交/直线
                        if len(pts) >= 3:
                            a, b, c = pts[-3], pts[-2], pts[-1]
                            ang = self._angle(a, b, c)
                            if not (85 <= ang <= 95 or 170 <= ang <= 190):
                                best_path_ok = False
                        break
            if linked:
                ok_cnt += 1
                if not best_path_ok:
                    non_orth_cnt += 1
        ratio = ok_cnt / max(len(box_data), 1)
        if ratio < 0.8:
            basis.append('分支箱连接到电缆端点的比例不足80%')
        if non_orth_cnt > 0:
            basis.append(f'分支箱连接处存在{non_orth_cnt}处非直线/非正交折线')

        score = self.FULL_SCORE_CONN * (ratio - min(non_orth_cnt * 0.05, 0.3))
        score = max(score, 0.0)
        level = self._level_from_score(score, self.FULL_SCORE_CONN)
        return {'score': round(score, 2), 'level': level, 'basis': basis}

    # ----------------- 提取器/工具 -----------------
    def _extract_boxes(self, devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取分支箱设备
        
        根据设备类型和标签提取分支箱设备
        """
        results = []
        for d in devices:
            t = str(d.get('type', '')).lower()
            label = (d.get('label') or d.get('name') or '').lower()
            if any(k in t for k in ['branch', 'box']) or any(k in label for k in ['分支箱', '开关箱', '箱']) and len(d.get('points') or []) <= 1:
                results.append(d)
        return results

    # 这些方法已移至基类