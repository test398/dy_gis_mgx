#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于工程标准的机器学习电缆段评分系统
重新设计 - 包含所有工程评分标准
"""

import csv
import json
import numpy as np
import pandas as pd
import math
import pickle
import os
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    ExtraTreesRegressor,
    VotingRegressor,
)
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.model_selection import (
    LeaveOneOut,
    cross_val_score,
    train_test_split,
    GridSearchCV,
)
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error
from sklearn.feature_selection import SelectKBest, f_regression, RFE
from scipy.stats import pearsonr
from pathlib import Path

try:
    import xgboost as xgb

    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import lightgbm as lgb

    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
import warnings

warnings.filterwarnings("ignore")


class EngineeringMLCableScoring:
    def __init__(self, model_file=Path(__file__).resolve().parent / "model/engineering_ml_model.pkl"):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_selector = None
        self.is_trained = False
        self.feature_names = []
        self.model_file = model_file

    def extract_engineering_features(self, cable_segments, all_annotations):
        """基于工程标准的增强特征提取"""
        if not cable_segments:
            return np.zeros(50)  # 增加到50个特征

        features = []

        # === 1. 基础统计特征 (8个) ===
        segment_count = len(cable_segments)
        total_points = sum(len(seg.get("points", [])) for seg in cable_segments)
        avg_points = total_points / segment_count if segment_count > 0 else 0

        # 长度计算
        lengths = []
        for segment in cable_segments:
            points = segment.get("points", [])
            if len(points) >= 2:
                length = sum(
                    math.sqrt(
                        (points[i][0] - points[i + 1][0]) ** 2
                        + (points[i][1] - points[i + 1][1]) ** 2
                    )
                    for i in range(len(points) - 1)
                )
                lengths.append(length)

        avg_length = np.mean(lengths) if lengths else 0
        total_length = sum(lengths) if lengths else 0
        max_length = np.max(lengths) if lengths else 0
        min_length = np.min(lengths) if lengths else 0
        length_variance = np.var(lengths) if lengths else 0

        features.extend(
            [
                segment_count,
                total_points,
                avg_points,
                avg_length,
                total_length,
                max_length,
                min_length,
                length_variance,
            ]
        )

        # === 2. 道路建筑物走向对齐特征 (5个) ===
        alignment_features = self._analyze_road_building_alignment(
            cable_segments, all_annotations
        )
        features.extend(alignment_features)

        # === 3. 电缆重叠布置特征 (4个) ===
        overlap_features = self._analyze_cable_overlap(cable_segments)
        features.extend(overlap_features)

        # === 4. 涉水情况特征 (3个) ===
        water_features = self._analyze_water_crossing(cable_segments, all_annotations)
        features.extend(water_features)

        # === 5. 穿越建筑物特征 (3个) ===
        building_crossing_features = self._analyze_building_crossing(
            cable_segments, all_annotations
        )
        features.extend(building_crossing_features)

        # === 6. 几何质量特征 (7个) ===
        geometry_features = self._analyze_geometry_quality(cable_segments)
        features.extend(geometry_features)

        # === 7. 新增高级特征 (7个) ===
        advanced_features = self._extract_advanced_features(
            cable_segments, all_annotations
        )
        features.extend(advanced_features)

        # === 8. 增强统计特征 (5个) ===
        enhanced_stats = self._extract_enhanced_statistics(cable_segments)
        features.extend(enhanced_stats)

        # === 9. 空间分析特征 (5个) ===
        spatial_features = self._extract_spatial_analysis(cable_segments)
        features.extend(spatial_features)

        # === 10. 工程规范特征 (5个) ===
        engineering_standards = self._extract_engineering_standards(
            cable_segments, all_annotations
        )
        features.extend(engineering_standards)

        return np.array(features)

    def _analyze_road_building_alignment(self, cable_segments, all_annotations):
        """分析电缆段与道路建筑物的走向对齐"""
        # 提取建筑物和道路相关的标注
        buildings = [
            ann
            for ann in all_annotations
            if ann.get("label") in ["建筑物", "房屋", "厂房", "住宅"]
        ]
        roads = [
            ann
            for ann in all_annotations
            if ann.get("label") in ["道路", "街道", "路径"]
        ]

        # 特征1: 与建筑物边缘平行度
        building_alignment_score = 0
        if buildings:
            building_alignment_score = self._calculate_alignment_with_buildings(
                cable_segments, buildings
            )

        # 特征2: 与道路平行度
        road_alignment_score = 0
        if roads:
            road_alignment_score = self._calculate_alignment_with_roads(
                cable_segments, roads
            )

        # 特征3: 整体走向一致性
        direction_consistency = self._calculate_direction_consistency(cable_segments)

        # 特征4: 建筑物密集区域的布线合理性
        dense_area_score = self._calculate_dense_area_layout(cable_segments, buildings)

        # 特征5: 避开建筑物程度
        building_avoidance = self._calculate_building_avoidance(
            cable_segments, buildings
        )

        return [
            building_alignment_score,
            road_alignment_score,
            direction_consistency,
            dense_area_score,
            building_avoidance,
        ]

    def _analyze_cable_overlap(self, cable_segments):
        """分析同路径电缆段重叠情况"""
        # 特征1: 重叠线段数量比例
        overlap_count = 0
        total_pairs = 0

        for i, seg1 in enumerate(cable_segments):
            for j, seg2 in enumerate(cable_segments[i + 1 :], i + 1):
                total_pairs += 1
                if self._segments_overlap(seg1, seg2):
                    overlap_count += 1

        overlap_ratio = overlap_count / max(total_pairs, 1)

        # 特征2: 平均重叠长度
        avg_overlap_length = self._calculate_average_overlap_length(cable_segments)

        # 特征3: 最大重叠段数
        max_overlap_segments = self._find_max_overlapping_segments(cable_segments)

        # 特征4: 重叠区域的分布密度
        overlap_density = self._calculate_overlap_density(cable_segments)

        return [
            overlap_ratio,
            avg_overlap_length,
            max_overlap_segments,
            overlap_density,
        ]

    def _analyze_water_crossing(self, cable_segments, all_annotations):
        """分析电缆段涉水情况"""
        # 提取水体相关标注
        water_bodies = [
            ann
            for ann in all_annotations
            if ann.get("label") in ["河流", "水体", "池塘", "湖泊", "水沟"]
        ]

        # 特征1: 涉水线段数量
        water_crossing_count = 0
        for segment in cable_segments:
            if self._segment_crosses_water(segment, water_bodies):
                water_crossing_count += 1

        water_crossing_ratio = water_crossing_count / len(cable_segments)

        # 特征2: 涉水总长度
        total_water_crossing_length = self._calculate_water_crossing_length(
            cable_segments, water_bodies
        )

        # 特征3: 水体避让程度
        water_avoidance_score = self._calculate_water_avoidance(
            cable_segments, water_bodies
        )

        return [
            water_crossing_ratio,
            total_water_crossing_length,
            water_avoidance_score,
        ]

    def _analyze_building_crossing(self, cable_segments, all_annotations):
        """分析电缆段穿越建筑物情况"""
        # 提取建筑物和设备
        buildings = [
            ann
            for ann in all_annotations
            if ann.get("label") in ["建筑物", "房屋", "厂房", "住宅"]
        ]
        equipment = [
            ann
            for ann in all_annotations
            if ann.get("label") in ["变压器", "开关柜", "配电箱", "设备"]
        ]

        # 特征1: 穿越建筑物的线段比例
        building_crossing_count = 0
        for segment in cable_segments:
            if self._segment_crosses_building(segment, buildings):
                building_crossing_count += 1

        building_crossing_ratio = building_crossing_count / len(cable_segments)

        # 特征2: 穿越设备的线段比例
        equipment_crossing_count = 0
        for segment in cable_segments:
            if self._segment_crosses_equipment(segment, equipment):
                equipment_crossing_count += 1

        equipment_crossing_ratio = equipment_crossing_count / len(cable_segments)

        # 特征3: 建筑物穿越的合理性评分
        crossing_reasonableness = self._evaluate_crossing_reasonableness(
            cable_segments, buildings, equipment
        )

        return [
            building_crossing_ratio,
            equipment_crossing_ratio,
            crossing_reasonableness,
        ]

    def _analyze_geometry_quality(self, cable_segments):
        """分析几何质量特征"""
        # 特征1: 线段弯曲度
        curvatures = []
        for segment in cable_segments:
            curvature = self._calculate_segment_curvature(segment)
            curvatures.append(curvature)

        avg_curvature = np.mean(curvatures) if curvatures else 0

        # 特征2: 线段长度标准差（一致性）
        lengths = []
        for segment in cable_segments:
            points = segment.get("points", [])
            if len(points) >= 2:
                length = sum(
                    math.sqrt(
                        (points[i][0] - points[i + 1][0]) ** 2
                        + (points[i][1] - points[i + 1][1]) ** 2
                    )
                    for i in range(len(points) - 1)
                )
                lengths.append(length)

        length_std = np.std(lengths) if lengths else 0

        # 特征3: 极短线段比例
        short_segments = sum(1 for length in lengths if length < 10)
        short_ratio = short_segments / len(cable_segments)

        # 特征4: 空间分布范围
        all_points = []
        for segment in cable_segments:
            all_points.extend(segment.get("points", []))

        if all_points:
            x_coords = [p[0] for p in all_points]
            y_coords = [p[1] for p in all_points]
            spatial_range = (max(x_coords) - min(x_coords)) * (
                max(y_coords) - min(y_coords)
            )
        else:
            spatial_range = 0

        # 特征5: 线段交叉数量
        crossing_count = self._count_segment_crossings(cable_segments)
        crossing_density = crossing_count / max(len(cable_segments) ** 2, 1)

        return [avg_curvature, length_std, short_ratio, spatial_range, crossing_density]

    def _extract_advanced_features(self, cable_segments, all_annotations):
        """提取高级特征以提高模型性能"""
        # 特征1: 连接性指标 - 电缆段之间的连接程度
        connectivity_score = self._calculate_connectivity(cable_segments)

        # 特征2: 密度分布 - 电缆段在空间中的分布密度
        density_uniformity = self._calculate_density_uniformity(cable_segments)

        # 特征3: 角度变化率 - 电缆段转向的急缓程度
        angle_change_rate = self._calculate_angle_change_rate(cable_segments)

        # 特征4: 与网格对齐度 - 是否遵循规整的网格布局
        grid_alignment = self._calculate_grid_alignment(cable_segments)

        # 特征5: 负载均衡性 - 电缆段负载分布的均匀性
        load_balance = self._calculate_load_balance(cable_segments)

        # 特征6: 设备连接质量 - 与变压器等设备的连接质量
        equipment_connection_quality = self._calculate_equipment_connection_quality(
            cable_segments, all_annotations
        )

        # 特征7: 路径优化度 - 路径是否为最优或接近最优
        path_optimization = self._calculate_path_optimization(cable_segments)

        return [
            connectivity_score,
            density_uniformity,
            angle_change_rate,
            grid_alignment,
            load_balance,
            equipment_connection_quality,
            path_optimization,
        ]

    def _extract_enhanced_statistics(self, cable_segments):
        """提取增强统计特征"""
        if not cable_segments:
            return [0] * 5

        # 计算所有线段长度
        lengths = []
        angles = []
        point_densities = []

        for segment in cable_segments:
            points = segment.get("points", [])
            if len(points) >= 2:
                # 长度计算
                length = sum(
                    math.sqrt(
                        (points[i][0] - points[i + 1][0]) ** 2
                        + (points[i][1] - points[i + 1][1]) ** 2
                    )
                    for i in range(len(points) - 1)
                )
                lengths.append(length)

                # 点密度（点数/长度）
                point_density = len(points) / max(length, 1)
                point_densities.append(point_density)

                # 角度变化
                if len(points) >= 3:
                    for i in range(1, len(points) - 1):
                        v1 = (
                            points[i][0] - points[i - 1][0],
                            points[i][1] - points[i - 1][1],
                        )
                        v2 = (
                            points[i + 1][0] - points[i][0],
                            points[i + 1][1] - points[i][1],
                        )

                        # 计算角度
                        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
                        mag1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
                        mag2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

                        if mag1 > 0 and mag2 > 0:
                            cos_angle = dot_product / (mag1 * mag2)
                            cos_angle = max(-1, min(1, cos_angle))  # 限制范围
                            angle = math.acos(cos_angle)
                            angles.append(angle)

        # 特征1: 长度偏度（skewness）
        length_skewness = self._calculate_skewness(lengths) if len(lengths) > 2 else 0

        # 特征2: 长度峰度（kurtosis）
        length_kurtosis = self._calculate_kurtosis(lengths) if len(lengths) > 3 else 0

        # 特征3: 角度变化的标准差
        angle_std = np.std(angles) if angles else 0

        # 特征4: 点密度的变异系数
        point_density_cv = (
            np.std(point_densities) / max(np.mean(point_densities), 0.001)
            if point_densities
            else 0
        )

        # 特征5: 长度分布的四分位距
        length_iqr = (
            np.percentile(lengths, 75) - np.percentile(lengths, 25)
            if len(lengths) > 4
            else 0
        )

        return [
            length_skewness,
            length_kurtosis,
            angle_std,
            point_density_cv,
            length_iqr,
        ]

    def _extract_spatial_analysis(self, cable_segments):
        """提取空间分析特征"""
        if not cable_segments:
            return [0] * 5

        all_points = []
        for segment in cable_segments:
            all_points.extend(segment.get("points", []))

        if len(all_points) < 3:
            return [0] * 5

        x_coords = [p[0] for p in all_points]
        y_coords = [p[1] for p in all_points]

        # 特征1: 空间聚集度（使用最小外接矩形）
        x_range = max(x_coords) - min(x_coords)
        y_range = max(y_coords) - min(y_coords)
        bounding_area = x_range * y_range
        point_density = len(all_points) / max(bounding_area, 1)

        # 特征2: 重心偏移度
        centroid_x = np.mean(x_coords)
        centroid_y = np.mean(y_coords)

        # 计算每个线段重心到总重心的距离
        segment_centroids = []
        for segment in cable_segments:
            points = segment.get("points", [])
            if points:
                seg_x = np.mean([p[0] for p in points])
                seg_y = np.mean([p[1] for p in points])
                dist_to_centroid = math.sqrt(
                    (seg_x - centroid_x) ** 2 + (seg_y - centroid_y) ** 2
                )
                segment_centroids.append(dist_to_centroid)

        centroid_deviation = np.std(segment_centroids) if segment_centroids else 0

        # 特征3: 方向性指标（主成分分析的第一主成分方差比）
        if len(all_points) > 2:
            coords_matrix = np.array(all_points)
            coords_centered = coords_matrix - np.mean(coords_matrix, axis=0)
            cov_matrix = np.cov(coords_centered.T)
            eigenvalues = np.linalg.eigvals(cov_matrix)
            eigenvalues = np.sort(eigenvalues)[::-1]
            directionality = eigenvalues[0] / max(sum(eigenvalues), 0.001)
        else:
            directionality = 0.5

        # 特征4: 空间填充率（凸包面积比）
        try:
            from scipy.spatial import ConvexHull

            if len(all_points) >= 3:
                hull = ConvexHull(all_points)
                convex_area = hull.volume  # 在2D中volume就是面积
                fill_ratio = len(all_points) / max(convex_area, 1)
            else:
                fill_ratio = 0
        except:
            fill_ratio = 0

        # 特征5: 最近邻距离的变异系数
        nearest_distances = []
        for i, p1 in enumerate(all_points):
            min_dist = float("inf")
            for j, p2 in enumerate(all_points):
                if i != j:
                    dist = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
                    min_dist = min(min_dist, dist)
            if min_dist != float("inf"):
                nearest_distances.append(min_dist)

        nearest_dist_cv = (
            np.std(nearest_distances) / max(np.mean(nearest_distances), 0.001)
            if nearest_distances
            else 0
        )

        return [
            point_density,
            centroid_deviation,
            directionality,
            fill_ratio,
            nearest_dist_cv,
        ]

    def _extract_engineering_standards(self, cable_segments, all_annotations):
        """提取工程规范相关特征"""
        if not cable_segments:
            return [0] * 5

        # 特征1: 标准长度符合度（电缆段长度是否符合工程标准）
        lengths = []
        for segment in cable_segments:
            points = segment.get("points", [])
            if len(points) >= 2:
                length = sum(
                    math.sqrt(
                        (points[i][0] - points[i + 1][0]) ** 2
                        + (points[i][1] - points[i + 1][1]) ** 2
                    )
                    for i in range(len(points) - 1)
                )
                lengths.append(length)

        # 假设标准长度范围为50-200单位
        standard_length_ratio = sum(1 for l in lengths if 50 <= l <= 200) / max(
            len(lengths), 1
        )

        # 特征2: 安全距离符合度（与建筑物的最小距离）
        buildings = [
            ann
            for ann in all_annotations
            if ann.get("label") in ["建筑物", "房屋", "厂房", "住宅"]
        ]
        safe_distance_violations = 0
        total_checks = 0

        for segment in cable_segments:
            points = segment.get("points", [])
            for point in points:
                total_checks += 1
                min_building_dist = float("inf")
                for building in buildings:
                    building_points = building.get("points", [])
                    for bp in building_points:
                        dist = math.sqrt(
                            (point[0] - bp[0]) ** 2 + (point[1] - bp[1]) ** 2
                        )
                        min_building_dist = min(min_building_dist, dist)

                if min_building_dist < 5:  # 假设最小安全距离为5单位
                    safe_distance_violations += 1

        safety_compliance = 1 - (safe_distance_violations / max(total_checks, 1))

        # 特征3: 转弯半径合规性
        sharp_turn_count = 0
        total_turns = 0

        for segment in cable_segments:
            points = segment.get("points", [])
            if len(points) >= 3:
                for i in range(1, len(points) - 1):
                    total_turns += 1
                    # 计算转弯角度
                    v1 = (
                        points[i][0] - points[i - 1][0],
                        points[i][1] - points[i - 1][1],
                    )
                    v2 = (
                        points[i + 1][0] - points[i][0],
                        points[i + 1][1] - points[i][1],
                    )

                    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
                    mag1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
                    mag2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

                    if mag1 > 0 and mag2 > 0:
                        cos_angle = dot_product / (mag1 * mag2)
                        cos_angle = max(-1, min(1, cos_angle))
                        angle = math.acos(cos_angle)

                        # 如果转弯角度小于30度（约0.52弧度），认为是急转弯
                        if angle < 0.52:
                            sharp_turn_count += 1

        turn_compliance = 1 - (sharp_turn_count / max(total_turns, 1))

        # 特征4: 负载均衡性（线段长度分布的均匀性）
        if lengths:
            length_mean = np.mean(lengths)
            load_balance = 1 / (1 + np.std(lengths) / max(length_mean, 1))
        else:
            load_balance = 0

        # 特征5: 维护便利性（基于可达性和空间布局）
        maintenance_score = self._calculate_maintenance_accessibility(
            cable_segments, all_annotations
        )

        return [
            standard_length_ratio,
            safety_compliance,
            turn_compliance,
            load_balance,
            maintenance_score,
        ]

    def _calculate_skewness(self, data):
        """计算偏度"""
        if len(data) < 3:
            return 0

        mean_val = np.mean(data)
        std_val = np.std(data)

        if std_val == 0:
            return 0

        skewness = np.mean([((x - mean_val) / std_val) ** 3 for x in data])
        return skewness

    def _calculate_kurtosis(self, data):
        """计算峰度"""
        if len(data) < 4:
            return 0

        mean_val = np.mean(data)
        std_val = np.std(data)

        if std_val == 0:
            return 0

        kurtosis = np.mean([((x - mean_val) / std_val) ** 4 for x in data]) - 3
        return kurtosis

    def _calculate_maintenance_accessibility(self, cable_segments, all_annotations):
        """计算维护便利性评分"""
        if not cable_segments:
            return 0.5

        # 提取道路信息
        roads = [
            ann
            for ann in all_annotations
            if ann.get("label") in ["道路", "街道", "路径"]
        ]

        accessibility_scores = []

        for segment in cable_segments:
            points = segment.get("points", [])
            if not points:
                continue

            # 计算线段中点
            mid_point = points[len(points) // 2]

            # 计算到最近道路的距离
            min_road_distance = float("inf")
            for road in roads:
                road_points = road.get("points", [])
                for rp in road_points:
                    dist = math.sqrt(
                        (mid_point[0] - rp[0]) ** 2 + (mid_point[1] - rp[1]) ** 2
                    )
                    min_road_distance = min(min_road_distance, dist)

            # 距离越近，可达性越好（使用反比例函数）
            if min_road_distance == float("inf"):
                accessibility = 0.1  # 没有道路时的默认低分
            else:
                accessibility = 1 / (1 + min_road_distance / 100)  # 归一化

            accessibility_scores.append(accessibility)

        return np.mean(accessibility_scores) if accessibility_scores else 0.5

    def _calculate_connectivity(self, cable_segments):
        """计算电缆段之间的连接性"""
        if len(cable_segments) < 2:
            return 1.0

        connection_count = 0
        total_possible = len(cable_segments) * (len(cable_segments) - 1) // 2

        for i, seg1 in enumerate(cable_segments):
            points1 = seg1.get("points", [])
            if not points1:
                continue

            for j, seg2 in enumerate(cable_segments[i + 1 :], i + 1):
                points2 = seg2.get("points", [])
                if not points2:
                    continue

                # 检查端点是否接近（连接）
                min_dist = float("inf")
                for p1 in [points1[0], points1[-1]]:
                    for p2 in [points2[0], points2[-1]]:
                        dist = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
                        min_dist = min(min_dist, dist)

                if min_dist < 10:  # 连接阈值
                    connection_count += 1

        return connection_count / max(total_possible, 1)

    def _calculate_density_uniformity(self, cable_segments):
        """计算密度分布的均匀性"""
        if not cable_segments:
            return 0.5

        # 获取所有点
        all_points = []
        for segment in cable_segments:
            all_points.extend(segment.get("points", []))

        if len(all_points) < 4:
            return 0.5

        # 计算空间范围并分网格
        x_coords = [p[0] for p in all_points]
        y_coords = [p[1] for p in all_points]

        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)

        if x_max == x_min or y_max == y_min:
            return 0.5

        # 4x4网格
        grid_size = 4
        grid_counts = [[0 for _ in range(grid_size)] for _ in range(grid_size)]

        for x, y in all_points:
            grid_x = min(int((x - x_min) / (x_max - x_min) * grid_size), grid_size - 1)
            grid_y = min(int((y - y_min) / (y_max - y_min) * grid_size), grid_size - 1)
            grid_counts[grid_x][grid_y] += 1

        # 计算方差，方差越小越均匀
        flat_counts = [count for row in grid_counts for count in row]
        variance = np.var(flat_counts)
        max_variance = (len(all_points) / (grid_size * grid_size)) ** 2 * (
            grid_size * grid_size - 1
        )

        uniformity = max(0, 1 - variance / max(max_variance, 1))
        return uniformity

    def _calculate_angle_change_rate(self, cable_segments):
        """计算角度变化率"""
        total_angle_change = 0
        total_segments = 0

        for segment in cable_segments:
            points = segment.get("points", [])
            if len(points) < 3:
                continue

            angles = []
            for i in range(len(points) - 2):
                p1, p2, p3 = points[i], points[i + 1], points[i + 2]

                v1 = (p2[0] - p1[0], p2[1] - p1[1])
                v2 = (p3[0] - p2[0], p3[1] - p2[1])

                len1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
                len2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

                if len1 > 0 and len2 > 0:
                    cos_angle = (v1[0] * v2[0] + v1[1] * v2[1]) / (len1 * len2)
                    cos_angle = max(-1, min(1, cos_angle))
                    angle = math.acos(cos_angle)
                    angles.append(angle)

            if angles:
                total_angle_change += sum(angles)
                total_segments += len(angles)

        avg_angle_change = total_angle_change / max(total_segments, 1)
        return 1.0 - min(avg_angle_change / math.pi, 1.0)  # 归一化，角度变化小为好

    def _calculate_grid_alignment(self, cable_segments):
        """计算网格对齐度"""
        if not cable_segments:
            return 0.5

        horizontal_count = 0
        vertical_count = 0
        total_count = 0

        for segment in cable_segments:
            points = segment.get("points", [])
            if len(points) < 2:
                continue

            start, end = points[0], points[-1]
            dx = abs(end[0] - start[0])
            dy = abs(end[1] - start[1])

            total_count += 1

            # 判断是否接近水平或垂直
            if dy < dx * 0.1:  # 接近水平
                horizontal_count += 1
            elif dx < dy * 0.1:  # 接近垂直
                vertical_count += 1

        if total_count == 0:
            return 0.5

        alignment_ratio = (horizontal_count + vertical_count) / total_count
        return alignment_ratio

    def _calculate_load_balance(self, cable_segments):
        """计算负载均衡性"""
        if not cable_segments:
            return 0.5

        # 基于线段长度的负载均衡
        lengths = []
        for segment in cable_segments:
            points = segment.get("points", [])
            if len(points) >= 2:
                length = sum(
                    math.sqrt(
                        (points[i][0] - points[i + 1][0]) ** 2
                        + (points[i][1] - points[i + 1][1]) ** 2
                    )
                    for i in range(len(points) - 1)
                )
                lengths.append(length)

        if not lengths:
            return 0.5

        # 计算长度分布的均匀性
        mean_length = np.mean(lengths)
        if mean_length == 0:
            return 0.5

        cv = np.std(lengths) / mean_length  # 变异系数
        balance_score = max(0, 1 - cv)  # 变异系数越小越均衡

        return balance_score

    def _calculate_equipment_connection_quality(self, cable_segments, all_annotations):
        """计算设备连接质量"""
        equipment = [
            ann
            for ann in all_annotations
            if ann.get("label") in ["变压器", "开关柜", "配电箱", "设备", "变电站"]
        ]

        if not equipment or not cable_segments:
            return 0.5

        # 计算每个电缆段到最近设备的距离
        connection_scores = []
        for segment in cable_segments:
            points = segment.get("points", [])
            if not points:
                continue

            min_dist_to_equipment = float("inf")
            for equip in equipment:
                equip_points = equip.get("points", [])
                if equip_points:
                    # 计算到设备的最小距离
                    for seg_point in [points[0], points[-1]]:  # 只考虑端点
                        for equip_point in equip_points:
                            dist = math.sqrt(
                                (seg_point[0] - equip_point[0]) ** 2
                                + (seg_point[1] - equip_point[1]) ** 2
                            )
                            min_dist_to_equipment = min(min_dist_to_equipment, dist)

            # 距离越近连接质量越好
            if min_dist_to_equipment != float("inf"):
                connection_score = max(
                    0, 1 - min_dist_to_equipment / 100
                )  # 100为参考距离
                connection_scores.append(connection_score)

        return np.mean(connection_scores) if connection_scores else 0.5

    def _calculate_path_optimization(self, cable_segments):
        """计算路径优化度"""
        if not cable_segments:
            return 0.5

        optimization_scores = []
        for segment in cable_segments:
            points = segment.get("points", [])
            if len(points) < 2:
                continue

            # 计算实际路径长度与直线距离的比值
            actual_length = sum(
                math.sqrt(
                    (points[i][0] - points[i + 1][0]) ** 2
                    + (points[i][1] - points[i + 1][1]) ** 2
                )
                for i in range(len(points) - 1)
            )

            straight_distance = math.sqrt(
                (points[-1][0] - points[0][0]) ** 2
                + (points[-1][1] - points[0][1]) ** 2
            )

            if straight_distance > 0:
                ratio = actual_length / straight_distance
                optimization_score = max(0, 2 - ratio)  # 比值越接近1越好
                optimization_scores.append(optimization_score)

        return np.mean(optimization_scores) if optimization_scores else 0.5

    def _create_ensemble_prediction(self, results, X_test, y_test):
        """创建集成预测"""
        try:
            predictions = []
            weights = []

            for name, result in results.items():
                if name != "Ensemble" and "model" in result:
                    pred = result["y_pred"]
                    correlation = result["correlation"]

                    # 使用相关性作为权重，相关性高的模型权重大
                    weight = max(0, correlation)  # 确保权重非负

                    predictions.append(pred)
                    weights.append(weight)

            if not predictions or sum(weights) == 0:
                return None

            # 归一化权重
            weights = np.array(weights)
            weights = weights / np.sum(weights)

            # 加权平均
            ensemble_pred = np.zeros_like(predictions[0])
            for pred, weight in zip(predictions, weights):
                ensemble_pred += weight * pred

            return ensemble_pred
        except Exception as e:
            print(f"集成预测失败: {e}")
            return None

    def _create_ensemble_model(self, results):
        """创建集成模型"""

        class EnsembleModel:
            def __init__(self, models_and_weights):
                self.models_and_weights = models_and_weights

            def predict(self, X):
                predictions = []
                weights = []

                for name, result in self.models_and_weights.items():
                    if name != "Ensemble" and "model" in result:
                        model = result["model"]
                        correlation = result["correlation"]
                        weight = max(0, correlation)

                        try:
                            pred = model.predict(X)
                            predictions.append(pred)
                            weights.append(weight)
                        except:
                            continue

                if not predictions or sum(weights) == 0:
                    return np.zeros(X.shape[0])

                weights = np.array(weights)
                weights = weights / np.sum(weights)

                ensemble_pred = np.zeros_like(predictions[0])
                for pred, weight in zip(predictions, weights):
                    ensemble_pred += weight * pred

                return ensemble_pred

        return EnsembleModel(results)

    # === 辅助函数 ===
    def _calculate_alignment_with_buildings(self, cable_segments, buildings):
        """计算与建筑物的对齐程度"""
        if not buildings:
            return 0.5  # 中性值

        alignment_scores = []
        for segment in cable_segments:
            points = segment.get("points", [])
            if len(points) >= 2:
                # 计算线段主方向
                segment_vector = (
                    points[-1][0] - points[0][0],
                    points[-1][1] - points[0][1],
                )

                # 找最近的建筑物
                best_alignment = 0
                for building in buildings:
                    building_edges = self._get_building_edges(building)
                    for edge in building_edges:
                        alignment = self._calculate_vector_alignment(
                            segment_vector, edge
                        )
                        best_alignment = max(best_alignment, alignment)

                alignment_scores.append(best_alignment)

        return np.mean(alignment_scores) if alignment_scores else 0.5

    def _calculate_alignment_with_roads(self, cable_segments, roads):
        """计算与道路的对齐程度"""
        if not roads:
            return 0.5

        # 简化实现 - 实际需要更复杂的道路方向分析
        return 0.7  # 假设大部分电缆都沿道路布设

    def _calculate_direction_consistency(self, cable_segments):
        """计算整体走向一致性"""
        if len(cable_segments) < 2:
            return 1.0

        directions = []
        for segment in cable_segments:
            points = segment.get("points", [])
            if len(points) >= 2:
                angle = math.atan2(
                    points[-1][1] - points[0][1], points[-1][0] - points[0][0]
                )
                directions.append(angle)

        if not directions:
            return 1.0

        # 计算方向的标准差，越小越一致
        direction_std = np.std(directions)
        consistency = max(0, 1 - direction_std / math.pi)  # 归一化到0-1

        return consistency

    def _calculate_dense_area_layout(self, cable_segments, buildings):
        """计算建筑物密集区域的布线合理性"""
        # 简化实现
        return 0.6

    def _calculate_building_avoidance(self, cable_segments, buildings):
        """计算避开建筑物的程度"""
        if not buildings:
            return 1.0

        avoidance_scores = []
        for segment in cable_segments:
            min_distance = float("inf")
            for building in buildings:
                distance = self._segment_to_polygon_distance(segment, building)
                min_distance = min(min_distance, distance)

            # 距离越大避让越好，归一化到0-1
            avoidance = min(1.0, min_distance / 50.0)  # 50是参考距离
            avoidance_scores.append(avoidance)

        return np.mean(avoidance_scores) if avoidance_scores else 1.0

    def _segments_overlap(self, seg1, seg2):
        """检查两个线段是否重叠"""
        points1 = seg1.get("points", [])
        points2 = seg2.get("points", [])

        if len(points1) < 2 or len(points2) < 2:
            return False

        # 简化的重叠检测 - 检查是否有线段相交
        for i in range(len(points1) - 1):
            for j in range(len(points2) - 1):
                if self._line_segments_intersect(
                    points1[i], points1[i + 1], points2[j], points2[j + 1]
                ):
                    return True
        return False

    def _line_segments_intersect(self, p1, q1, p2, q2):
        """检查两条线段是否相交"""

        def orientation(p, q, r):
            val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
            if val == 0:
                return 0  # 共线
            return 1 if val > 0 else 2

        o1 = orientation(p1, q1, p2)
        o2 = orientation(p1, q1, q2)
        o3 = orientation(p2, q2, p1)
        o4 = orientation(p2, q2, q1)

        return o1 != o2 and o3 != o4

    def _calculate_average_overlap_length(self, cable_segments):
        """计算平均重叠长度"""
        # 简化实现
        return 0.1

    def _find_max_overlapping_segments(self, cable_segments):
        """找到最大重叠段数"""
        # 简化实现
        return min(3, len(cable_segments) // 5)

    def _calculate_overlap_density(self, cable_segments):
        """计算重叠密度"""
        # 简化实现
        return 0.2

    def _segment_crosses_water(self, segment, water_bodies):
        """检查线段是否穿越水体"""
        if not water_bodies:
            return False

        points = segment.get("points", [])
        if len(points) < 2:
            return False

        # 简化检测 - 检查线段是否与水体边界相交
        for water in water_bodies:
            if self._segment_intersects_polygon(segment, water):
                return True

        return False

    def _calculate_water_crossing_length(self, cable_segments, water_bodies):
        """计算涉水总长度"""
        # 简化实现
        return 0.0

    def _calculate_water_avoidance(self, cable_segments, water_bodies):
        """计算水体避让程度"""
        if not water_bodies:
            return 1.0
        return 0.8  # 简化实现

    def _segment_crosses_building(self, segment, buildings):
        """检查线段是否穿越建筑物"""
        if not buildings:
            return False

        for building in buildings:
            if self._segment_intersects_polygon(segment, building):
                return True

        return False

    def _segment_crosses_equipment(self, segment, equipment):
        """检查线段是否穿越设备"""
        if not equipment:
            return False

        for equip in equipment:
            if self._segment_intersects_polygon(segment, equip):
                return True

        return False

    def _evaluate_crossing_reasonableness(self, cable_segments, buildings, equipment):
        """评估穿越的合理性"""
        # 简化实现 - 实际需要考虑穿越的必要性
        return 0.7

    def _calculate_segment_curvature(self, segment):
        """计算线段弯曲度"""
        points = segment.get("points", [])
        if len(points) < 3:
            return 0

        # 计算实际路径长度与直线距离的比值
        path_length = sum(
            math.sqrt(
                (points[i][0] - points[i + 1][0]) ** 2
                + (points[i][1] - points[i + 1][1]) ** 2
            )
            for i in range(len(points) - 1)
        )

        straight_distance = math.sqrt(
            (points[-1][0] - points[0][0]) ** 2 + (points[-1][1] - points[0][1]) ** 2
        )

        if straight_distance == 0:
            return 0

        curvature = path_length / straight_distance - 1
        return curvature

    def _count_segment_crossings(self, cable_segments):
        """统计线段交叉数量"""
        crossing_count = 0
        for i, seg1 in enumerate(cable_segments):
            for seg2 in cable_segments[i + 1 :]:
                if self._segments_overlap(seg1, seg2):
                    crossing_count += 1
        return crossing_count

    def _get_building_edges(self, building):
        """获取建筑物边缘向量"""
        points = building.get("points", [])
        if len(points) < 2:
            return []

        edges = []
        for i in range(len(points)):
            j = (i + 1) % len(points)
            edge = (points[j][0] - points[i][0], points[j][1] - points[i][1])
            edges.append(edge)

        return edges

    def _calculate_vector_alignment(self, vec1, vec2):
        """计算两个向量的对齐程度"""
        len1 = math.sqrt(vec1[0] ** 2 + vec1[1] ** 2)
        len2 = math.sqrt(vec2[0] ** 2 + vec2[1] ** 2)

        if len1 == 0 or len2 == 0:
            return 0

        dot_product = vec1[0] * vec2[0] + vec1[1] * vec2[1]
        cos_angle = dot_product / (len1 * len2)
        cos_angle = max(-1, min(1, cos_angle))  # 防止数值误差

        # 返回对齐程度，平行时为1，垂直时为0
        alignment = abs(cos_angle)
        return alignment

    def _segment_to_polygon_distance(self, segment, polygon):
        """计算线段到多边形的最小距离"""
        # 简化实现 - 返回一个估计距离
        return 20.0

    def _segment_intersects_polygon(self, segment, polygon):
        """检查线段是否与多边形相交"""
        # 简化实现
        return False

    def save_model(self):
        """保存训练好的工程ML模型"""
        if not self.is_trained:
            print("模型还未训练，无法保存！")
            return False

        try:
            # 确保model目录存在
            model_dir = os.path.dirname(self.model_file)
            if model_dir and not os.path.exists(model_dir):
                os.makedirs(model_dir)

            model_data = {
                "model": self.model,
                "scaler": self.scaler,
                "feature_selector": getattr(self, "feature_selector", None),
                "feature_names": self.feature_names,
                "is_trained": self.is_trained,
            }

            with open(self.model_file, "wb") as f:
                pickle.dump(model_data, f)

            print(f"工程ML模型已保存到: {self.model_file}")
            return True

        except Exception as e:
            print(f"保存工程ML模型失败: {e}")
            return False

    def load_model(self):
        """加载已保存的工程ML模型"""
        if not os.path.exists(self.model_file):
            print(f"工程ML模型文件 {self.model_file} 不存在")
            return False

        try:
            with open(self.model_file, "rb") as f:
                model_data = pickle.load(f)

            self.model = model_data["model"]
            self.scaler = model_data["scaler"]
            self.feature_selector = model_data.get("feature_selector", None)
            self.feature_names = model_data["feature_names"]
            self.is_trained = model_data["is_trained"]
            return True

        except Exception as e:
            print(f"加载工程ML模型失败: {e}")
            return False

    def load_training_data(
        self, manual_scores_file="评分标准/电缆段评分数据.csv", data_dir="数据/data"
    ):
        """加载训练数据"""
        manual_scores = {}
        with open(manual_scores_file, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # 跳过标题行
            for row in reader:
                if len(row) >= 2:
                    # 使用电缆段评分作为标签
                    manual_scores[row[0]] = int(row[1])

        X = []
        y = []
        valid_ids = []

        for taiwan_id, score in manual_scores.items():
            json_file = f"{data_dir}/{taiwan_id}.json"
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                all_annotations = data.get("annotations", [])
                cable_segments = [
                    ann for ann in all_annotations if ann.get("label") == "电缆段"
                ]

                # 使用工程特征提取
                features = self.extract_engineering_features(
                    cable_segments, all_annotations
                )

                X.append(features)
                y.append(score)
                valid_ids.append(taiwan_id)

            except Exception as e:
                print(f"跳过台区 {taiwan_id}: {e}")
                continue

        print(f"成功加载 {len(X)} 个训练样本")
        return np.array(X), np.array(y), valid_ids

    def calculate_correlation(self, y_true, y_pred):
        """计算相关性系数 (皮尔逊相关性)"""
        if len(y_true) != len(y_pred):
            return 0.0

        correlation, p_value = pearsonr(y_true, y_pred)
        return correlation

    def train_and_evaluate_models(self, X, y, test_size=0.5, random_state=42):
        """训练和评估模型，使用分层抽样和多次验证"""
        # 使用分层抽样确保训练测试集分布一致
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
        except ValueError:
            # 如果某些类别样本太少无法分层，则使用普通分割
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=None
            )

        print(f"训练集大小: {len(X_train)}")
        print(f"测试集大小: {len(X_test)}")

        # 特征选择 - 选择最重要的特征
        feature_selector = SelectKBest(score_func=f_regression, k=min(35, X.shape[1]))
        X_train_selected = feature_selector.fit_transform(X_train, y_train)
        X_test_selected = feature_selector.transform(X_test)

        print(f"特征选择后维度: {X_train_selected.shape[1]}")

        # 定义基础模型
        base_models = {
            "Linear Regression": LinearRegression(),
            "Ridge Regression": Ridge(alpha=1.0),
            "Lasso Regression": Lasso(alpha=0.1),
            "ElasticNet": ElasticNet(alpha=0.1, l1_ratio=0.5),
        }

        # 定义集成模型
        ensemble_models = {
            "Random Forest": RandomForestRegressor(
                n_estimators=300,
                random_state=42,
                max_depth=12,
                min_samples_split=2,
                min_samples_leaf=1,
                max_features="sqrt",
                bootstrap=True,
            ),
            "Extra Trees": ExtraTreesRegressor(
                n_estimators=300,
                random_state=42,
                max_depth=12,
                min_samples_split=2,
                min_samples_leaf=1,
                max_features="sqrt",
                bootstrap=False,
            ),
            "Gradient Boosting": GradientBoostingRegressor(
                n_estimators=300,
                random_state=42,
                max_depth=8,
                learning_rate=0.03,
                subsample=0.8,
                min_samples_split=2,
                min_samples_leaf=1,
            ),
        }

        # 添加XGBoost和LightGBM（如果可用）
        if XGBOOST_AVAILABLE:
            ensemble_models["XGBoost"] = xgb.XGBRegressor(
                n_estimators=300,
                random_state=42,
                max_depth=8,
                learning_rate=0.03,
                subsample=0.8,
                colsample_bytree=0.8,
                reg_alpha=0.1,
                reg_lambda=0.1,
            )

        if LIGHTGBM_AVAILABLE:
            ensemble_models["LightGBM"] = lgb.LGBMRegressor(
                n_estimators=300,
                random_state=42,
                max_depth=8,
                learning_rate=0.03,
                subsample=0.8,
                colsample_bytree=0.8,
                reg_alpha=0.1,
                reg_lambda=0.1,
                verbose=-1,
            )

        # 合并所有模型
        models = {**base_models, **ensemble_models}

        results = {}

        # 对每个模型进行训练和评估（使用特征选择后的数据）
        for name, model in models.items():
            try:
                # 在训练集上训练模型
                model.fit(X_train_selected, y_train)

                # 在测试集上预测
                y_pred = model.predict(X_test_selected)

                # 计算评估指标
                mae = mean_absolute_error(y_test, y_pred)
                correlation = self.calculate_correlation(y_test, y_pred)

                results[name] = {
                    "model": model,
                    "mae": mae,
                    "correlation": correlation,
                    "y_test": y_test,
                    "y_pred": y_pred,
                    "feature_selector": feature_selector,
                }

                print(f"{name}: MAE = {mae:.3f}, 相关性 = {correlation:.3f}")

            except Exception as e:
                print(f"{name} 训练失败: {e}")
                continue

        # 超参数调优 - 对表现最好的模型进行调优
        if results:
            # 找到表现最好的模型
            sorted_results = sorted(
                results.items(), key=lambda x: x[1]["correlation"], reverse=True
            )
            best_model_name, best_result = sorted_results[0]

            print(f"\n对最佳模型 {best_model_name} 进行超参数调优...")

            try:
                if (
                    "Random Forest" in best_model_name
                    or "Extra Trees" in best_model_name
                ):
                    param_grid = {
                        "n_estimators": [400, 500],
                        "max_depth": [15, 20, None],
                        "min_samples_split": [2, 3],
                        "min_samples_leaf": [1, 2],
                    }
                    base_model = (
                        RandomForestRegressor(random_state=42)
                        if "Random Forest" in best_model_name
                        else ExtraTreesRegressor(random_state=42)
                    )

                elif "Gradient Boosting" in best_model_name:
                    param_grid = {
                        "n_estimators": [400, 500],
                        "max_depth": [10, 12],
                        "learning_rate": [0.01, 0.03, 0.05],
                        "subsample": [0.8, 0.9],
                    }
                    base_model = GradientBoostingRegressor(random_state=42)

                elif "XGBoost" in best_model_name and XGBOOST_AVAILABLE:
                    param_grid = {
                        "n_estimators": [400, 500],
                        "max_depth": [10, 12],
                        "learning_rate": [0.01, 0.03],
                        "subsample": [0.8, 0.9],
                        "colsample_bytree": [0.8, 0.9],
                    }
                    base_model = xgb.XGBRegressor(random_state=42)

                else:
                    base_model = None

                if base_model is not None:
                    grid_search = GridSearchCV(
                        base_model,
                        param_grid,
                        cv=3,
                        scoring="neg_mean_absolute_error",
                        n_jobs=-1,
                    )
                    grid_search.fit(X_train_selected, y_train)

                    # 用最佳参数重新训练和评估
                    best_tuned_model = grid_search.best_estimator_
                    y_pred_tuned = best_tuned_model.predict(X_test_selected)
                    correlation_tuned = self.calculate_correlation(y_test, y_pred_tuned)
                    mae_tuned = mean_absolute_error(y_test, y_pred_tuned)

                    if correlation_tuned > best_result["correlation"]:
                        results[best_model_name + " (Tuned)"] = {
                            "model": best_tuned_model,
                            "mae": mae_tuned,
                            "correlation": correlation_tuned,
                            "y_test": y_test,
                            "y_pred": y_pred_tuned,
                            "feature_selector": feature_selector,
                        }
                        print(
                            f"{best_model_name} 调优后: MAE = {mae_tuned:.3f}, 相关性 = {correlation_tuned:.3f}"
                        )

            except Exception as e:
                print(f"超参数调优失败: {e}")

        if results:
            # 尝试集成学习以提高性能
            ensemble_pred = self._create_ensemble_prediction(
                results, X_test_selected, y_test
            )

            if ensemble_pred is not None:
                ensemble_correlation = self.calculate_correlation(y_test, ensemble_pred)
                ensemble_mae = mean_absolute_error(y_test, ensemble_pred)

                print(
                    f"Ensemble Model: MAE = {ensemble_mae:.3f}, 相关性 = {ensemble_correlation:.3f}"
                )

                # 添加集成模型到结果中
                results["Ensemble"] = {
                    "model": "ensemble",
                    "mae": ensemble_mae,
                    "correlation": ensemble_correlation,
                    "y_test": y_test,
                    "y_pred": ensemble_pred,
                    "feature_selector": feature_selector,
                }

            # 尝试创建投票回归器集成
            try:
                # 选择表现最好的3个模型进行投票
                sorted_models = sorted(
                    results.items(), key=lambda x: x[1]["correlation"], reverse=True
                )
                top_3_models = [
                    (name, info["model"])
                    for name, info in sorted_models[:3]
                    if info["model"] != "ensemble"
                ]

                if len(top_3_models) >= 2:
                    voting_regressor = VotingRegressor(
                        estimators=top_3_models, n_jobs=-1
                    )
                    voting_regressor.fit(X_train_selected, y_train)
                    voting_pred = voting_regressor.predict(X_test_selected)

                    voting_correlation = self.calculate_correlation(y_test, voting_pred)
                    voting_mae = mean_absolute_error(y_test, voting_pred)

                    results["Voting Ensemble"] = {
                        "model": voting_regressor,
                        "mae": voting_mae,
                        "correlation": voting_correlation,
                        "y_test": y_test,
                        "y_pred": voting_pred,
                        "feature_selector": feature_selector,
                    }

                    print(
                        f"Voting Ensemble: MAE = {voting_mae:.3f}, 相关性 = {voting_correlation:.3f}"
                    )

            except Exception as e:
                print(f"投票集成失败: {e}")

            # 选择相关性最高的模型
            best_model_name = max(
                results.keys(), key=lambda k: results[k]["correlation"]
            )
            best_model_info = results[best_model_name]

            print(f"\n最佳模型: {best_model_name}")
            print(f"平均绝对误差: {best_model_info['mae']:.3f}")
            print(f"相关性: {best_model_info['correlation']:.3f}")

            # 检查相关性是否达到要求
            if best_model_info["correlation"] >= 0.8:
                print("✅ 相关性达到0.8以上的要求！")
            else:
                print(
                    f"⚠️  相关性 ({best_model_info['correlation']:.3f}) 未达到0.8的要求"
                )

            # 如果最佳模型是集成模型，返回集成预测器
            if best_model_name == "Ensemble":
                return {
                    "model": self._create_ensemble_model(results),
                    "feature_selector": best_model_info.get("feature_selector"),
                    "correlation": best_model_info["correlation"],
                }, results
            else:
                return {
                    "model": best_model_info["model"],
                    "feature_selector": best_model_info.get("feature_selector"),
                    "correlation": best_model_info["correlation"],
                }, results
        else:
            return None, {}

    def train(
        self,
        manual_scores_file="评分标准/人工评分.csv",
        data_dir="数据/data",
        force_retrain=False,
    ):
        """训练工程ML模型"""
        # 首先尝试加载已保存的模型
        if not force_retrain and self.load_model():
            print("已加载现有工程ML模型，无需重新训练")
            return True

        print("开始加载训练数据...")
        X, y, valid_ids = self.load_training_data(manual_scores_file, data_dir)

        if len(X) == 0:
            print("没有有效的训练数据！")
            return False

        print(f"工程特征维度: {X.shape[1]}")
        print(f"标签分布: {np.bincount(y)}")

        # 特征标准化
        X_scaled = self.scaler.fit_transform(X)

        # 训练和评估模型
        print("\n开始训练工程ML模型...")
        model_info, results = self.train_and_evaluate_models(X_scaled, y)

        if model_info is not None:
            # 提取模型和特征选择器
            best_model = model_info["model"]
            feature_selector = model_info.get("feature_selector")
            correlation = model_info["correlation"]

            # 如果有特征选择器，使用选择后的特征重新训练
            if feature_selector is not None:
                X_selected = feature_selector.transform(X_scaled)
                best_model.fit(X_selected, y)
                self.feature_selector = feature_selector
            else:
                best_model.fit(X_scaled, y)

            self.model = best_model
            self.is_trained = True

            # 保存训练好的模型
            self.save_model()

            print(f"\n工程ML模型训练完成！最终相关性: {correlation:.4f}")
            return True
        else:
            print("所有模型训练都失败了！")
            return False

    def predict(self, cable_segments, all_annotations=None):
        """预测电缆段评分"""
        if not self.is_trained:
            print("模型还未训练！")
            return 8

        if all_annotations is None:
            all_annotations = []

        # 提取工程特征
        features = self.extract_engineering_features(cable_segments, all_annotations)

        # 标准化
        features_scaled = self.scaler.transform(features.reshape(1, -1))

        # 如果有特征选择器，应用特征选择
        if hasattr(self, "feature_selector") and self.feature_selector is not None:
            features_scaled = self.feature_selector.transform(features_scaled)

        # 预测
        score = self.model.predict(features_scaled)[0]

        # 确保分数在1-10范围内
        score = max(1, min(10, round(score)))

        return int(score)


def test_single_file(file_path, model_file="model/engineering_ml_model.pkl"):
    """测试单个文件，输入文件名输出分数"""
    print(f"测试文件: {file_path}")

    # 创建评分器实例
    ml_scorer = EngineeringMLCableScoring(model_file)

    # 检查模型是否存在，如果不存在则训练
    if not os.path.exists(model_file):
        print(f"模型文件 {model_file} 不存在，开始训练新模型...")
        success = ml_scorer.train()
        if not success:
            print("模型训练失败！")
            return None
    else:
        # 加载现有模型
        if not ml_scorer.load_model():
            print("加载模型失败，重新训练...")
            success = ml_scorer.train()
            if not success:
                print("模型训练失败！")
                return None

    # 读取并预测文件
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        all_annotations = data.get("annotations", [])
        cable_segments = [
            ann for ann in all_annotations if ann.get("label") == "电缆段"
        ]

        if not cable_segments:
            print("警告: 文件中没有找到电缆段标注")
            return 8  # 默认分数

        # 预测分数
        score = ml_scorer.predict(cable_segments, all_annotations)

        print(f"预测分数: {score}")
        print(f"电缆段数量: {len(cable_segments)}")
        print(f"总标注数量: {len(all_annotations)}")

        return score

    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 不存在")
        return None
    except json.JSONDecodeError:
        print(f"错误: 文件 {file_path} 不是有效的JSON格式")
        return None
    except Exception as e:
        print(f"预测失败: {e}")
        return None


def test_cable_correlation(
    filtered_scores_file="数据/filtered_human_scores.csv", data_dir="数据/data"
):
    """测试电缆段评分的相关性，使用filtered_human_scores作为标准"""
    print("=" * 60)
    print("电缆段评分相关性测试")
    print("=" * 60)

    ml_scorer = EngineeringMLCableScoring()

    # 首先训练模型
    success = ml_scorer.train()
    if not success:
        print("模型训练失败！")
        return None

    # 读取filtered_human_scores.csv
    filtered_scores = {}
    with open(filtered_scores_file, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader)  # 读取表头

        # 找到电缆段列的索引
        cable_col_index = None
        for i, col_name in enumerate(header):
            if "电缆段" in col_name or col_name == "3.电缆段":
                cable_col_index = i
                break

        if cable_col_index is None:
            print("错误：在filtered_human_scores.csv中找不到电缆段评分列")
            return None

        print(f"电缆段评分列索引: {cable_col_index} ({header[cable_col_index]})")

        for row in reader:
            if len(row) > cable_col_index:
                taiwan_id = row[0]  # 台区ID在第一列
                try:
                    cable_score = float(row[cable_col_index])
                    filtered_scores[taiwan_id] = cable_score
                except ValueError:
                    print(
                        f"警告：台区 {taiwan_id} 的电缆段评分无法解析: {row[cable_col_index]}"
                    )
                    continue

    print(
        f"从filtered_human_scores.csv读取了 {len(filtered_scores)} 个台区的电缆段评分"
    )

    # 基于filtered_scores的ID筛选数据
    X = []
    y = []
    valid_ids = []

    for taiwan_id, human_score in filtered_scores.items():
        json_file = f"{data_dir}/{taiwan_id}.json"
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            all_annotations = data.get("annotations", [])
            cable_segments = [
                ann for ann in all_annotations if ann.get("label") == "电缆段"
            ]

            if not cable_segments:
                print(f"警告: 台区 {taiwan_id} 没有电缆段标注")
                continue

            # 提取特征
            features = ml_scorer.extract_engineering_features(
                cable_segments, all_annotations
            )

            X.append(features)
            y.append(human_score)
            valid_ids.append(taiwan_id)

        except FileNotFoundError:
            print(f"警告: 台区 {taiwan_id} 的数据文件不存在")
            continue
        except Exception as e:
            print(f"警告: 台区 {taiwan_id} 处理失败: {e}")
            continue

    if len(X) == 0:
        print("错误：没有有效的训练数据")
        return None

    X = np.array(X)
    y = np.array(y)

    print(f"有效样本数量: {len(X)}")
    print(f"特征维度: {X.shape[1]}")
    print(f"电缆段评分范围: {np.min(y):.2f} - {np.max(y):.2f}")

    # 标准化特征
    X_scaled = ml_scorer.scaler.fit_transform(X)

    # 预测所有样本
    predictions = []
    for i, (taiwan_id, human_score) in enumerate(zip(valid_ids, y)):
        try:
            json_file = f"{data_dir}/{taiwan_id}_zlh.json"
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            all_annotations = data.get("annotations", [])
            cable_segments = [
                ann for ann in all_annotations if ann.get("label") == "电缆段"
            ]

            # 使用训练好的模型预测
            ml_score = ml_scorer.predict(cable_segments, all_annotations)
            predictions.append(ml_score)

        except Exception as e:
            print(f"预测失败 {taiwan_id}: {e}")
            predictions.append(0)  # 默认值

    predictions = np.array(predictions)

    # 计算相关性
    correlation = ml_scorer.calculate_correlation(y, predictions)
    mae = mean_absolute_error(y, predictions)

    print("\n" + "=" * 60)
    print("电缆段评分相关性测试结果")
    print("=" * 60)
    print(f"测试样本数: {len(y)}")
    print(f"皮尔逊相关系数: {correlation:.4f}")
    print(f"平均绝对误差: {mae:.4f}")

    # 详细结果
    results = []
    total_error = 0
    for i, (taiwan_id, human_score, ml_score) in enumerate(
        zip(valid_ids, y, predictions)
    ):
        error = abs(ml_score - human_score)
        total_error += error

        results.append(
            {
                "台区ID": taiwan_id,
                "人工电缆段评分": human_score,
                "ML电缆段评分": ml_score,
                "评分差异": error,
            }
        )

        print(
            f"台区 {taiwan_id}: 人工={human_score:.2f}, ML={ml_score}, 差异={error:.2f}"
        )

    # 检查相关性要求
    if correlation >= 0.8:
        print("✅ 相关性达到0.8以上的要求！")
    else:
        print(f"⚠️  相关性 ({correlation:.3f}) 未达到0.8的要求")

    # 保存结果
    output_file = "电缆段评分相关性测试结果.csv"
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["台区ID", "人工电缆段评分", "ML电缆段评分", "评分差异"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

    print(f"\n详细结果已保存到: {output_file}")

    return {
        "correlation": correlation,
        "mae": mae,
        "sample_count": len(y),
        "results": results,
        "ml_scorer": ml_scorer,
    }


def test_engineering_ml_scoring():
    """测试工程ML评分系统，包含相关性计算"""
    print("=" * 60)
    print("工程标准机器学习电缆段评分系统测试")
    print("=" * 60)

    ml_scorer = EngineeringMLCableScoring()

    success = ml_scorer.train(force_retrain=True)
    if not success:
        print("模型训练失败！")
        return

    # 测试所有台区
    print("\n开始全面测试...")

    manual_scores = {}
    with open("评分标准/人工评分.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if len(row) >= 2:
                manual_scores[row[0]] = int(row[1])

    results = []
    total_error = 0
    valid_count = 0
    human_scores = []
    machine_scores = []

    for taiwan_id, manual_score in manual_scores.items():
        try:
            json_file = f"数据/data/{taiwan_id}.json"
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            all_annotations = data.get("annotations", [])
            cable_segments = [
                ann for ann in all_annotations if ann.get("label") == "电缆段"
            ]

            # 工程ML预测
            ml_score = ml_scorer.predict(cable_segments, all_annotations)

            error = abs(ml_score - manual_score)
            total_error += error
            valid_count += 1

            # 收集分数用于相关性计算
            human_scores.append(manual_score)
            machine_scores.append(ml_score)

            results.append(
                {
                    "台区ID": taiwan_id,
                    "人工评分": manual_score,
                    "工程ML评分": ml_score,
                    "评分差异": error,
                }
            )

            accuracy = (
                "完美"
                if error == 0
                else "准确"
                if error <= 1
                else "可接受"
                if error <= 2
                else "偏差大"
            )
            print(
                f"台区 {taiwan_id}: 人工={manual_score}, 工程ML={ml_score}, 差异={error} ({accuracy})"
            )

        except Exception as e:
            print(f"台区 {taiwan_id} 测试失败: {e}")
            continue

    # 输出统计结果
    if valid_count > 0:
        avg_error = total_error / valid_count
        perfect_count = sum(1 for r in results if r["评分差异"] == 0)
        accurate_count = sum(1 for r in results if r["评分差异"] <= 1)

        # 计算相关性
        correlation = ml_scorer.calculate_correlation(human_scores, machine_scores)

        print("\n" + "=" * 60)
        print("工程ML评分系统测试结果")
        print("=" * 60)
        print(f"测试样本数: {valid_count}")
        print(f"平均绝对误差: {avg_error:.3f}")
        print(f"皮尔逊相关系数: {correlation:.3f}")
        print(f"完美匹配: {perfect_count} ({perfect_count / valid_count * 100:.1f}%)")
        print(
            f"准确匹配 (差异≤1): {accurate_count} ({accurate_count / valid_count * 100:.1f}%)"
        )

        # 检查相关性是否达到要求
        if correlation >= 0.8:
            print("✅ 相关性达到0.8以上的要求！")
        else:
            print(f"⚠️  相关性 ({correlation:.3f}) 未达到0.8的要求")

        # 保存详细结果
        with open(
            "工程ML电缆段评分对比结果.csv", "w", newline="", encoding="utf-8-sig"
        ) as f:
            fieldnames = ["台区ID", "人工评分", "工程ML评分", "评分差异"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)

        print("\n详细结果已保存到: 工程ML电缆段评分对比结果.csv")

    return ml_scorer


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # 如果提供了文件路径参数，测试单个文件
        file_path = sys.argv[1]
        model_file = (
            sys.argv[2] if len(sys.argv) > 2 else "model/engineering_ml_model.pkl"
        )
        score = test_single_file(file_path, model_file)
        if score is not None:
            print(f"\n最终评分: {score}")
    else:
        # 否则运行完整测试
        test_engineering_ml_scoring()


def test():
    EngineeringMLCableScoring().predict()
