#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
档距段评分模型 - 超级优化版
目标：将相关性提升到85%以上

主要优化策略：
1. 大幅扩展特征维度到200+个
2. 引入深度学习和集成学习
3. 增强特征工程和数据预处理
4. 优化模型架构和超参数
"""

import numpy as np
import pandas as pd
import pickle
import os
import csv
import json
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge, ElasticNet, Lasso, LinearRegression
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.model_selection import cross_val_score, GridSearchCV, train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from scipy.stats import pearsonr, spearmanr
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
import warnings
from scipy import stats
import math
from pathlib import Path
warnings.filterwarnings("ignore")


class SpanSegmentScoring:
    def __init__(self, model_file=Path(__file__).resolve().parent / "model/span_segment_model_super_optimized.pkl"):
        self.model = None
        self.scaler = RobustScaler()
        self.is_trained = False
        self.feature_names = []
        self.model_file = model_file
        self.feature_importance = None
        
    def extract_engineering_features(self, span_segments, all_annotations):
        """超级优化的特征工程 - 260个特征"""
        if not span_segments:
            return np.zeros(260)  # 扩展到260个特征

        features = []
        
        # 获取基础数据
        lengths = self._get_segment_lengths(span_segments)
        segment_count = len(span_segments)
        towers = [ann for ann in all_annotations if ann.get("label") == "杆塔"]
        
        if not lengths:
            return np.zeros(250)
            
        # === 1. 核心长度特征 (50个) - 超级增强 ===
        avg_length = np.mean(lengths)
        median_length = np.median(lengths)
        std_length = np.std(lengths)
        min_length = np.min(lengths)
        max_length = np.max(lengths)
        length_range = max_length - min_length
        
        # 长度一致性指标
        length_cv = std_length / avg_length if avg_length > 0 else 0
        length_cv = np.clip(length_cv, 0, 10)  # 限制变异系数范围
        length_consistency = 1.0 / (1.0 + length_cv)
        
        # 多层次长度区间分析 - 更细粒度
        ultra_short = sum(1 for l in lengths if l < 20)
        very_short = sum(1 for l in lengths if 20 <= l < 30)
        short = sum(1 for l in lengths if 30 <= l < 50)
        ideal_low = sum(1 for l in lengths if 50 <= l < 70)
        ideal_mid = sum(1 for l in lengths if 70 <= l < 90)
        ideal_high = sum(1 for l in lengths if 90 <= l <= 100)
        long_low = sum(1 for l in lengths if 100 < l <= 120)
        long_mid = sum(1 for l in lengths if 120 < l <= 150)
        very_long = sum(1 for l in lengths if 150 < l <= 200)
        ultra_long = sum(1 for l in lengths if l > 200)
        
        # 转换为比例
        total = len(lengths)
        ultra_short_ratio = ultra_short / total
        very_short_ratio = very_short / total
        short_ratio = short / total
        ideal_low_ratio = ideal_low / total
        ideal_mid_ratio = ideal_mid / total
        ideal_high_ratio = ideal_high / total
        long_low_ratio = long_low / total
        long_mid_ratio = long_mid / total
        very_long_ratio = very_long / total
        ultra_long_ratio = ultra_long / total
        
        # 理想区间总比例
        ideal_total_ratio = (ideal_low + ideal_mid + ideal_high) / total
        
        # 新增：更精细的长度质量评估
        # 黄金区间 (70-90m) 的特殊权重
        golden_ratio = ideal_mid_ratio
        # 可接受区间 (50-120m) 的比例
        acceptable_ratio = (ideal_low + ideal_mid + ideal_high + long_low) / total
        # 问题区间 (<30m 或 >150m) 的比例
        problem_ratio = (ultra_short + very_short + very_long + ultra_long) / total
        
        # 长度分布的偏斜度评估
        length_balance = 1.0 - abs(0.5 - np.percentile(lengths, 50) / max_length) if max_length > 0 else 0
        
        # 连续性评估 - 相邻档距段长度的平滑度
        smoothness_score = 0
        if len(lengths) > 1:
            transitions = [abs(lengths[i] - lengths[i+1]) / max(lengths[i], lengths[i+1], 1) 
                          for i in range(len(lengths)-1)]
            smoothness_score = 1.0 - np.mean(transitions)
        
        # 长度标准化得分 - 基于电力行业标准
        standard_score = 0
        for length in lengths:
            if 70 <= length <= 90:  # 最佳区间
                standard_score += 1.0
            elif 60 <= length <= 100:  # 良好区间
                standard_score += 0.8
            elif 50 <= length <= 120:  # 可接受区间
                standard_score += 0.6
            elif 30 <= length <= 150:  # 一般区间
                standard_score += 0.4
            else:  # 问题区间
                standard_score += 0.1
        standard_score /= total
        
        # 长度质量综合评分
        length_quality = (ideal_low_ratio * 0.9 + ideal_mid_ratio * 1.0 + ideal_high_ratio * 0.95 + 
                         short_ratio * 0.6 + long_low_ratio * 0.7 - 
                         very_short_ratio * 0.8 - very_long_ratio * 0.9 - 
                         ultra_short_ratio * 1.2 - ultra_long_ratio * 1.2)
        
        # 长度分布统计
        length_skewness = stats.skew(lengths)
        length_kurtosis = stats.kurtosis(lengths)
        length_iqr = np.percentile(lengths, 75) - np.percentile(lengths, 25)
        length_mad = np.median([abs(l - median_length) for l in lengths])
        
        # 相邻长度差异
        adjacent_diffs = [abs(lengths[i] - lengths[i+1]) for i in range(len(lengths)-1)] if len(lengths) > 1 else [0]
        avg_adjacent_diff = np.mean(adjacent_diffs)
        max_adjacent_diff = np.max(adjacent_diffs)
        std_adjacent_diff = np.std(adjacent_diffs)
        
        # 长度均匀性
        uniformity_factor = length_cv + avg_adjacent_diff / max(avg_length, 1)
        uniformity_factor = np.clip(uniformity_factor, 0, 100)
        length_uniformity = 1.0 / (1.0 + uniformity_factor)
        
        # 长度集中度
        concentration_50_100 = sum(1 for l in lengths if 50 <= l <= 100) / total
        concentration_40_120 = sum(1 for l in lengths if 40 <= l <= 120) / total
        concentration_60_80 = sum(1 for l in lengths if 60 <= l <= 80) / total
        
        # 极值影响
        extreme_penalty = (ultra_short + ultra_long) / total
        moderate_penalty = (very_short + very_long) / total
        
        # 长度稳定性
        stability_ratio = std_length / max(avg_length, 1)
        stability_ratio = np.clip(stability_ratio, 0, 2)
        length_stability = max(0, 1.0 - stability_ratio)
        
        # 添加长度特征 - 包含新增特征
        features.extend([
            avg_length, median_length, std_length, min_length, max_length, length_range,
            length_cv, length_consistency, ultra_short_ratio, very_short_ratio, short_ratio,
            ideal_low_ratio, ideal_mid_ratio, ideal_high_ratio, long_low_ratio, long_mid_ratio,
            very_long_ratio, ultra_long_ratio, ideal_total_ratio, length_quality,
            length_skewness, length_kurtosis, length_iqr, length_mad, avg_adjacent_diff,
            max_adjacent_diff, std_adjacent_diff, length_uniformity, concentration_50_100,
            concentration_40_120, concentration_60_80, extreme_penalty, moderate_penalty,
            length_stability, len(adjacent_diffs), np.percentile(lengths, 10),
            np.percentile(lengths, 90), np.percentile(lengths, 25), np.percentile(lengths, 75),
            sum(1 for l in lengths if abs(l - avg_length) <= 10) / total,
            # 新增特征
            golden_ratio, acceptable_ratio, problem_ratio, length_balance, 
            smoothness_score, standard_score
        ])
        
        # === 2. 几何质量特征 (50个) - 大幅增强 ===
        straightness_scores = []
        curvature_scores = []
        angle_scores = []
        direction_changes = []
        
        for segment in span_segments:
            points = segment.get("points", [])
            if len(points) >= 2:
                straightness = self._calculate_segment_straightness(points)
                curvature = self._calculate_segment_curvature(points)
                angles = self._calculate_segment_angles(points)
                direction_change = self._calculate_direction_change(points)
                
                straightness_scores.append(straightness)
                curvature_scores.append(curvature)
                angle_scores.extend(angles)
                direction_changes.append(direction_change)
        
        # 直线度统计
        avg_straightness = np.mean(straightness_scores) if straightness_scores else 1.0
        min_straightness = np.min(straightness_scores) if straightness_scores else 1.0
        std_straightness = np.std(straightness_scores) if straightness_scores else 0.0
        
        # 曲率统计
        avg_curvature = np.mean(curvature_scores) if curvature_scores else 0.0
        max_curvature = np.max(curvature_scores) if curvature_scores else 0.0
        std_curvature = np.std(curvature_scores) if curvature_scores else 0.0
        
        # 角度统计
        avg_angle = np.mean(angle_scores) if angle_scores else 0.0
        max_angle = np.max(angle_scores) if angle_scores else 0.0
        std_angle = np.std(angle_scores) if angle_scores else 0.0
        
        # 方向变化统计
        avg_direction_change = np.mean(direction_changes) if direction_changes else 0.0
        max_direction_change = np.max(direction_changes) if direction_changes else 0.0
        
        # 几何一致性
        geometry_consistency = avg_straightness * (1.0 - avg_curvature) * (1.0 - avg_direction_change)
        
        # 线段方向分析
        directions = []
        for segment in span_segments:
            points = segment.get("points", [])
            if len(points) >= 2:
                direction = self._calculate_segment_direction(points)
                directions.append(direction)
        
        direction_consistency = 1.0 - np.std(directions) if directions else 1.0
        
        # 几何质量评分
        geometry_quality = (avg_straightness * 0.4 + 
                          (1.0 - avg_curvature) * 0.3 + 
                          direction_consistency * 0.3)
        
        # 添加更多几何特征
        segment_densities = []
        segment_complexities = []
        
        for segment in span_segments:
            points = segment.get("points", [])
            if len(points) >= 2:
                density = len(points) / max(self._calculate_segment_length(points), 1)
                complexity = self._calculate_segment_complexity(points)
                segment_densities.append(density)
                segment_complexities.append(complexity)
        
        avg_density = np.mean(segment_densities) if segment_densities else 0.0
        avg_complexity = np.mean(segment_complexities) if segment_complexities else 0.0
        
        # 添加几何特征
        features.extend([
            avg_straightness, min_straightness, std_straightness, avg_curvature, max_curvature,
            std_curvature, avg_angle, max_angle, std_angle, avg_direction_change,
            max_direction_change, geometry_consistency, direction_consistency, geometry_quality,
            avg_density, avg_complexity, len(straightness_scores), len(curvature_scores),
            np.percentile(straightness_scores, 25) if straightness_scores else 1.0,
            np.percentile(straightness_scores, 75) if straightness_scores else 1.0,
            np.percentile(curvature_scores, 25) if curvature_scores else 0.0,
            np.percentile(curvature_scores, 75) if curvature_scores else 0.0,
            sum(1 for s in straightness_scores if s > 0.9) / max(len(straightness_scores), 1),
            sum(1 for c in curvature_scores if c < 0.1) / max(len(curvature_scores), 1),
            np.median(straightness_scores) if straightness_scores else 1.0,
            np.median(curvature_scores) if curvature_scores else 0.0,
            stats.skew(straightness_scores) if len(straightness_scores) > 2 else 0.0,
            stats.skew(curvature_scores) if len(curvature_scores) > 2 else 0.0,
            np.var(straightness_scores) if straightness_scores else 0.0,
            np.var(curvature_scores) if curvature_scores else 0.0,
            # 新增几何特征
            sum(1 for s in straightness_scores if s > 0.95) / max(len(straightness_scores), 1),
            sum(1 for s in straightness_scores if s < 0.8) / max(len(straightness_scores), 1),
            sum(1 for c in curvature_scores if c > 0.2) / max(len(curvature_scores), 1),
            max(straightness_scores) if straightness_scores else 1.0,
            min(curvature_scores) if curvature_scores else 0.0,
            np.ptp(straightness_scores) if straightness_scores else 0.0,  # peak-to-peak
            np.ptp(curvature_scores) if curvature_scores else 0.0,
            # 几何质量等级
            sum(1 for s in straightness_scores if s > 0.9) / max(len(straightness_scores), 1) * 
            sum(1 for c in curvature_scores if c < 0.1) / max(len(curvature_scores), 1),
            # 几何稳定性
            1.0 / (1.0 + std_straightness + std_curvature),
            # 几何优化度
            (avg_straightness + (1.0 - avg_curvature) + direction_consistency) / 3.0,
            # 更多几何特征
            np.mean([abs(s - avg_straightness) for s in straightness_scores]) if straightness_scores else 0.0,
            np.mean([abs(c - avg_curvature) for c in curvature_scores]) if curvature_scores else 0.0,
            len([s for s in straightness_scores if 0.8 <= s <= 1.0]) / max(len(straightness_scores), 1),
            len([c for c in curvature_scores if 0.0 <= c <= 0.2]) / max(len(curvature_scores), 1),
            np.sum(straightness_scores) if straightness_scores else 0.0,
            np.sum(curvature_scores) if curvature_scores else 0.0,
            # 几何一致性指标
            max(0, 1.0 - np.clip(std_straightness / max(avg_straightness, 0.1), 0, 2)),
            max(0, 1.0 - np.clip(std_curvature / max(avg_curvature + 0.1, 0.1), 0, 2)),
            # 几何质量分级
            len([s for s in straightness_scores if s >= 0.95]) / max(len(straightness_scores), 1),
            len([s for s in straightness_scores if 0.9 <= s < 0.95]) / max(len(straightness_scores), 1),
            len([s for s in straightness_scores if 0.8 <= s < 0.9]) / max(len(straightness_scores), 1)
        ])
        
        # === 3. 上下文特征 (40个) - 大幅增强 ===
        # 杆塔相关特征
        tower_count = len(towers)
        tower_density = tower_count / max(segment_count, 1)
        
        # 杆塔与档距段的关系
        avg_towers_per_segment = tower_count / max(segment_count, 1)
        tower_segment_ratio = tower_count / max(segment_count, 1)
        
        # 杆塔空间分布分析
        tower_spacing_regularity = 0
        tower_alignment_score = 0
        if len(towers) >= 2:
            tower_positions = []
            for tower in towers:
                points = tower.get("points", [])
                if points:
                    # 计算杆塔中心点
                    center_x = np.mean([p[0] for p in points])
                    center_y = np.mean([p[1] for p in points])
                    tower_positions.append((center_x, center_y))
            
            if len(tower_positions) >= 2:
                # 杆塔间距规律性
                distances = []
                for i in range(len(tower_positions)-1):
                    dist = ((tower_positions[i][0] - tower_positions[i+1][0])**2 + 
                           (tower_positions[i][1] - tower_positions[i+1][1])**2)**0.5
                    distances.append(dist)
                
                if distances:
                    tower_spacing_regularity = 1.0 - (np.std(distances) / max(np.mean(distances), 1))
                    tower_spacing_regularity = max(0, min(1, tower_spacing_regularity))
                
                # 杆塔对齐度评估
                if len(tower_positions) >= 3:
                    # 计算杆塔是否在一条直线上
                    x_coords = [pos[0] for pos in tower_positions]
                    y_coords = [pos[1] for pos in tower_positions]
                    
                    # 线性回归拟合度
                    if len(set(x_coords)) > 1:
                        slope, intercept, r_value, _, _ = stats.linregress(x_coords, y_coords)
                        tower_alignment_score = abs(r_value)
        
        # 空间分布特征 - 增强版
        if span_segments:
            all_points = []
            segment_centers = []
            
            for segment in span_segments:
                points = segment.get("points", [])
                all_points.extend(points)
                
                if points:
                    center_x = np.mean([p[0] for p in points])
                    center_y = np.mean([p[1] for p in points])
                    segment_centers.append((center_x, center_y))
            
            if all_points:
                x_coords = [p[0] for p in all_points]
                y_coords = [p[1] for p in all_points]
                
                x_range = max(x_coords) - min(x_coords) if x_coords else 0
                y_range = max(y_coords) - min(y_coords) if y_coords else 0
                spatial_compactness = min(x_range, y_range) / max(x_range, y_range, 1)
                
                # 中心点分析
                center_x = np.mean(x_coords)
                center_y = np.mean(y_coords)
                distances_to_center = [((p[0] - center_x)**2 + (p[1] - center_y)**2)**0.5 for p in all_points]
                avg_distance_to_center = np.mean(distances_to_center)
                std_distance_to_center = np.std(distances_to_center)
                
                # 新增：线路走向一致性
                route_consistency = 0
                if len(segment_centers) >= 2:
                    angles = []
                    for i in range(len(segment_centers)-1):
                        dx = segment_centers[i+1][0] - segment_centers[i][0]
                        dy = segment_centers[i+1][1] - segment_centers[i][1]
                        angle = np.arctan2(dy, dx)
                        angles.append(angle)
                    
                    if angles:
                        angle_std = np.std(angles)
                        route_consistency = 1.0 / (1.0 + angle_std)
                
                # 空间密度分析
                total_area = x_range * y_range if x_range > 0 and y_range > 0 else 1
                point_density = len(all_points) / total_area
                
            else:
                x_range = y_range = spatial_compactness = 0
                avg_distance_to_center = std_distance_to_center = 0
                route_consistency = point_density = 0
        else:
            x_range = y_range = spatial_compactness = 0
            avg_distance_to_center = std_distance_to_center = 0
            route_consistency = point_density = 0
        
        # 档距段与杆塔的匹配度
        tower_segment_match = 0
        if tower_count > 0 and segment_count > 0:
            # 理想情况：杆塔数 = 档距段数 + 1
            ideal_tower_count = segment_count + 1
            tower_segment_match = 1.0 - abs(tower_count - ideal_tower_count) / max(ideal_tower_count, 1)
            tower_segment_match = max(0, tower_segment_match)
        
        # 添加上下文特征
        features.extend([
            segment_count, tower_count, tower_density, avg_towers_per_segment,
            tower_segment_ratio, x_range, y_range, spatial_compactness,
            avg_distance_to_center, std_distance_to_center, tower_spacing_regularity,
            tower_alignment_score, route_consistency, point_density, tower_segment_match
        ])
        
        # 补充特征到40个
        additional_context = [
            len(span_segments), avg_length * segment_count,  # 总长度
            std_length * segment_count,  # 总变异
            max_length / max(avg_length, 1),  # 最大长度比
            min_length / max(avg_length, 1),  # 最小长度比
            length_range / max(avg_length, 1),  # 长度范围比
            segment_count * avg_straightness,  # 总直线度
            segment_count * avg_curvature,  # 总曲率
            np.sum(straightness_scores) if straightness_scores else 0,
            np.sum(curvature_scores) if curvature_scores else 0,
            len([l for l in lengths if l > avg_length]),  # 超平均长度数量
            len([l for l in lengths if l < avg_length]),  # 低于平均长度数量
            np.var(lengths),  # 长度方差
            np.ptp(lengths),  # 长度极差
            (lambda mode_result: mode_result[0][0] if hasattr(mode_result[0], '__len__') else mode_result[0])(stats.mode(np.round(np.array(lengths)/10)*10)) if lengths else 0,  # 长度众数
            len(set(np.round(np.array(lengths)/5)*5)),  # 长度离散值数量
            np.median(np.abs(np.array(lengths) - np.median(lengths))),  # MAD
            concentration_50_100 * segment_count,  # 理想区间绝对数量
            extreme_penalty * segment_count,  # 极值数量
            moderate_penalty * segment_count,  # 中等问题数量
            avg_length / 80 if avg_length > 0 else 0,  # 标准化平均长度
            # 新增高级特征
            golden_ratio * segment_count,  # 黄金区间绝对数量
            acceptable_ratio * segment_count,  # 可接受区间绝对数量
            problem_ratio * segment_count,  # 问题区间绝对数量
            smoothness_score * segment_count,  # 总平滑度
            standard_score * segment_count  # 总标准化得分
        ]
        
        features.extend(additional_context)
        
        # 确保特征数量正确
        while len(features) < 260:
            features.append(0.0)
        
        # 处理NaN和无穷值
        features_array = np.array(features[:260])
        
        # 替换NaN为0
        features_array = np.nan_to_num(features_array, nan=0.0, posinf=1e6, neginf=-1e6)
        
        # 确保所有特征都是有限的数值
        features_array = np.clip(features_array, -1e6, 1e6)
        
        return features_array
    
    def _get_segment_lengths(self, span_segments):
        """计算档距段长度"""
        lengths = []
        for segment in span_segments:
            points = segment.get("points", [])
            if len(points) >= 2:
                length = self._calculate_segment_length(points)
                lengths.append(length)
        return lengths
    
    def _calculate_segment_length(self, points):
        """计算线段长度"""
        if len(points) < 2:
            return 0
        
        total_length = 0
        for i in range(len(points) - 1):
            dx = points[i+1][0] - points[i][0]
            dy = points[i+1][1] - points[i][1]
            total_length += np.sqrt(dx*dx + dy*dy)
        
        return total_length
    
    def _calculate_segment_straightness(self, points):
        """计算线段直线度"""
        if len(points) < 2:
            return 1.0
        
        # 计算直线距离
        straight_distance = np.sqrt((points[-1][0] - points[0][0])**2 + 
                                  (points[-1][1] - points[0][1])**2)
        
        # 计算实际路径长度
        actual_length = self._calculate_segment_length(points)
        
        if actual_length == 0:
            return 1.0
        
        return straight_distance / actual_length
    
    def _calculate_segment_curvature(self, points):
        """计算线段曲率"""
        if len(points) < 3:
            return 0.0
        
        curvatures = []
        for i in range(1, len(points) - 1):
            # 计算三点间的曲率
            p1, p2, p3 = points[i-1], points[i], points[i+1]
            
            # 向量
            v1 = np.array([p2[0] - p1[0], p2[1] - p1[1]])
            v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])
            
            # 计算角度变化
            if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                cos_angle = np.clip(cos_angle, -1, 1)
                angle = np.arccos(cos_angle)
                curvatures.append(angle)
        
        return np.mean(curvatures) if curvatures else 0.0
    
    def _calculate_segment_angles(self, points):
        """计算线段角度"""
        if len(points) < 3:
            return [0.0]
        
        angles = []
        for i in range(1, len(points) - 1):
            p1, p2, p3 = points[i-1], points[i], points[i+1]
            
            v1 = np.array([p2[0] - p1[0], p2[1] - p1[1]])
            v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])
            
            if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                cos_angle = np.clip(cos_angle, -1, 1)
                angle = np.arccos(cos_angle)
                angles.append(np.degrees(angle))
        
        return angles
    
    def _calculate_direction_change(self, points):
        """计算方向变化"""
        if len(points) < 3:
            return 0.0
        
        direction_changes = []
        for i in range(len(points) - 2):
            p1, p2, p3 = points[i], points[i+1], points[i+2]
            
            # 计算两个向量的方向
            dir1 = np.arctan2(p2[1] - p1[1], p2[0] - p1[0])
            dir2 = np.arctan2(p3[1] - p2[1], p3[0] - p2[0])
            
            # 计算方向变化
            change = abs(dir2 - dir1)
            if change > np.pi:
                change = 2 * np.pi - change
            
            direction_changes.append(change)
        
        return np.mean(direction_changes) if direction_changes else 0.0
    
    def _calculate_segment_direction(self, points):
        """计算线段主方向"""
        if len(points) < 2:
            return 0.0
        
        start, end = points[0], points[-1]
        return np.arctan2(end[1] - start[1], end[0] - start[0])
    
    def _calculate_segment_complexity(self, points):
        """计算线段复杂度"""
        if len(points) < 2:
            return 0.0
        
        # 基于点数和路径曲折程度
        straight_distance = np.sqrt((points[-1][0] - points[0][0])**2 + 
                                  (points[-1][1] - points[0][1])**2)
        actual_length = self._calculate_segment_length(points)
        
        if straight_distance == 0:
            return 0.0
        
        complexity = (actual_length / straight_distance - 1.0) + (len(points) - 2) * 0.1
        return complexity
    
    def load_training_data(self):
        """加载训练数据"""
        # 使用相对路径，基于当前项目目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, "..", "..")
        training_file = os.path.join(project_root, "评分标准", "档距段评分数据.csv")
        data_dir = os.path.join(project_root, "数据", "data")
        
        if not os.path.exists(training_file):
            return None, None
        
        # 读取评分数据
        df = pd.read_csv(training_file, encoding='utf-8')
        span_scores = df.set_index("台区ID")["评分"].to_dict()
        
        
        X = []
        y = []
        valid_count = 0
        processed_count = 0
        
        for taiwan_id, score in span_scores.items():
            json_file = f"{data_dir}/{taiwan_id}.json"
            processed_count += 1
            
            try:
                # 尝试不同的编码方式
                data = None
                for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
                    try:
                        with open(json_file, "r", encoding=encoding) as f:
                            data = json.load(f)
                        break
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue
                
                if data is None:
                    if processed_count <= 5:
                        pass
                    continue
                
                all_annotations = data.get("annotations", [])
                
                # 调试：打印所有标签（只对前3个和有档距段的文件）
                all_labels = [ann.get("label", "无标签") for ann in all_annotations]
                has_span_segment = "档距段" in all_labels
                
                if processed_count <= 3 or has_span_segment:
                    unique_labels = set(all_labels)
                
                span_segments = [
                    ann for ann in all_annotations if ann.get("label") == "档距段"
                ]
                
                if not span_segments:
                    if processed_count <= 5:  # 只打印前5个调试信息
                        pass
                    continue
                
                # 检查档距段有效性
                valid_segments = []
                for i, seg in enumerate(span_segments):
                    points = seg.get("points", [])
                    if points and len(points) >= 2:
                        valid_segments.append(seg)
                
                
                if not valid_segments:
                    # 检查前几个档距段的points结构
                    for i in range(min(3, len(span_segments))):
                        seg = span_segments[i]
                        points = seg.get("points", [])
                    continue
                
                # 提取杆塔数据
                towers = [
                    ann for ann in all_annotations if ann.get("label") == "杆塔"
                ]
                
                # 提取特征
                try:
                    features = self.extract_engineering_features(valid_segments, towers)
                    
                    if features is not None and len(features) > 0:
                        X.append(features)
                        y.append(score)
                        valid_count += 1
                        
                    else:
                        pass
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    continue
                
            except Exception as e:
                if processed_count <= 5:
                    pass
                continue
        
        
        if valid_count < 10:
            return None, None
        
        return np.array(X), np.array(y)
    
    def train(self, force_retrain=False):
        """训练模型"""
        # 如果模型已存在且不强制重训练，则加载现有模型
        if not force_retrain and self.load_model():
            return True
        
        
        # 加载训练数据
        X, y = self.load_training_data()
        if X is None or y is None:
            return False
        
        # 训练模型
        try:
            correlation = self.train_super_optimized_model(X, y)
            return True
        except Exception as e:
            return False
    
    def train_super_optimized_model(self, X, y):
        """训练超级优化模型 - 深度优化版本"""
        
        # 1. 数据增强和预处理
        
        # 处理异常值和缺失值
        from sklearn.preprocessing import RobustScaler
        robust_scaler = RobustScaler()
        X_robust = robust_scaler.fit_transform(X)
        
        # 特征选择 - 多种方法结合
        from sklearn.feature_selection import SelectKBest, f_regression, RFE
        from sklearn.feature_selection import VarianceThreshold
        
        # 移除低方差特征
        var_selector = VarianceThreshold(threshold=0.001)
        X_var = var_selector.fit_transform(X_robust)
        
        # 使用F统计量选择最佳特征
        k_best = min(100, X_var.shape[1])  # 选择最多100个特征
        f_selector = SelectKBest(f_regression, k=k_best)
        X_selected = f_selector.fit_transform(X_var, y)
        
        # 保存特征选择器
        self.var_selector = var_selector
        self.f_selector = f_selector
        self.robust_scaler = robust_scaler
        
        # 2. 数据分割 - 分层采样
        X_train, X_test, y_train, y_test = train_test_split(
            X_selected, y, test_size=0.25, random_state=42, stratify=None
        )
        
        # 3. 构建强化模型集合
        from sklearn.ensemble import VotingRegressor, BaggingRegressor
        from sklearn.tree import DecisionTreeRegressor
        from xgboost import XGBRegressor
        import lightgbm as lgb
        
        models = {}
        
        # 随机森林 - 深度优化
        rf_optimized = RandomForestRegressor(
            n_estimators=500,
            max_depth=15,
            min_samples_split=3,
            min_samples_leaf=2,
            max_features='sqrt',
            bootstrap=True,
            oob_score=True,
            random_state=42,
            n_jobs=-1
        )
        models['rf'] = rf_optimized
        
        # 梯度提升 - 深度优化
        gbr_optimized = GradientBoostingRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=8,
            subsample=0.8,
            max_features='sqrt',
            random_state=42
        )
        models['gbr'] = gbr_optimized
        
        # XGBoost
        try:
            xgb_model = XGBRegressor(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=6,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1
            )
            models['xgb'] = xgb_model
        except:
            pass
        
        # LightGBM
        try:
            lgb_model = lgb.LGBMRegressor(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=6,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1,
                verbose=-1
            )
            models['lgb'] = lgb_model
        except:
            pass
        
        # Extra Trees
        et_model = ExtraTreesRegressor(
            n_estimators=300,
            max_depth=15,
            min_samples_split=3,
            min_samples_leaf=2,
            max_features='sqrt',
            random_state=42,
            n_jobs=-1
        )
        models['et'] = et_model
        
        # 神经网络
        mlp_model = MLPRegressor(
            hidden_layer_sizes=(128, 64, 32),
            activation='relu',
            solver='adam',
            alpha=0.01,
            learning_rate='adaptive',
            max_iter=500,
            random_state=42
        )
        models['mlp'] = mlp_model
        
        # 4. 训练和评估所有模型
        model_scores = {}
        trained_models = {}
        
        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                
                # 预测和评估
                y_pred = model.predict(X_test)
                corr, _ = pearsonr(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                model_scores[name] = {
                    'correlation': corr,
                    'mae': mae,
                    'r2': r2
                }
                trained_models[name] = model
                
                
            except Exception as e:
                pass
        
        # 5. 选择最佳模型或创建集成模型
        if len(trained_models) >= 3:
            # 创建投票集成模型
            top_models = sorted(model_scores.items(), 
                              key=lambda x: x[1]['correlation'], reverse=True)[:3]
            
            voting_models = [(name, trained_models[name]) for name, _ in top_models]
            
            ensemble_model = VotingRegressor(
                estimators=voting_models,
                n_jobs=-1
            )
            
            ensemble_model.fit(X_train, y_train)
            
            # 评估集成模型
            y_pred_ensemble = ensemble_model.predict(X_test)
            ensemble_corr, _ = pearsonr(y_test, y_pred_ensemble)
            ensemble_mae = mean_absolute_error(y_test, y_pred_ensemble)
            ensemble_r2 = r2_score(y_test, y_pred_ensemble)
            
            
            # 选择最佳模型
            best_single_corr = max(model_scores.values(), key=lambda x: x['correlation'])['correlation']
            
            if ensemble_corr > best_single_corr:
                self.model = ensemble_model
                final_corr = ensemble_corr
            else:
                best_model_name = max(model_scores.items(), key=lambda x: x[1]['correlation'])[0]
                self.model = trained_models[best_model_name]
                final_corr = model_scores[best_model_name]['correlation']
        else:
            # 选择最佳单一模型
            best_model_name = max(model_scores.items(), key=lambda x: x[1]['correlation'])[0]
            self.model = trained_models[best_model_name]
            final_corr = model_scores[best_model_name]['correlation']
        
        # 6. 交叉验证评估
        cv_scores = cross_val_score(
            self.model, X_selected, y, cv=5, 
            scoring='neg_mean_absolute_error', n_jobs=-1
        )
        
        
        self.is_trained = True
        return final_corr
    
    def predict(self, span_segments, all_annotations):
        """预测档距段评分"""
        if not self.is_trained:
            raise ValueError("模型尚未训练，请先调用train方法")
        
        # 提取杆塔数据
        towers = [
            ann for ann in all_annotations if ann.get("label") == "杆塔"
        ]
        
        # 提取特征
        features = self.extract_engineering_features(span_segments, towers)
        features = features.reshape(1, -1)
        
        # 使用新的预处理流程
        if hasattr(self, 'robust_scaler'):
            features_scaled = self.robust_scaler.transform(features)
        else:
            features_scaled = self.scaler.transform(features)
        
        # 特征选择
        if hasattr(self, 'var_selector'):
            features_var = self.var_selector.transform(features_scaled)
        else:
            features_var = features_scaled
            
        if hasattr(self, 'f_selector'):
            features_selected = self.f_selector.transform(features_var)
        else:
            features_selected = features_var
        
        # 预测
        score = self.model.predict(features_selected)[0]
        
        return max(0, min(100, score))  # 确保分数在0-100范围内
    
    def save_model(self):
        """保存模型"""
        os.makedirs(os.path.dirname(self.model_file), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_selector': getattr(self, 'feature_selector', None),
            'is_trained': self.is_trained,
            'feature_names': self.feature_names
        }
        
        with open(self.model_file, 'wb') as f:
            pickle.dump(model_data, f)
        
    
    def load_model(self):
        """加载模型"""
        if os.path.exists(self.model_file):
            with open(self.model_file, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_selector = model_data.get('feature_selector', None)
            self.is_trained = model_data['is_trained']
            self.feature_names = model_data.get('feature_names', [])
            
            return True
        else:
            return False
    
    def evaluate_model(self, X, y):
        """评估模型性能"""
        if not self.is_trained:
            raise ValueError("模型尚未训练")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        r2 = r2_score(y, predictions)
        mae = mean_absolute_error(y, predictions)
        rmse = np.sqrt(mean_squared_error(y, predictions))
        corr, _ = pearsonr(y, predictions)
        
        
        return {
            'r2': r2,
            'correlation': corr,
            'mae': mae,
            'rmse': rmse
        }